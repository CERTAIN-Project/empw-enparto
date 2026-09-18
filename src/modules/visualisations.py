import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# uniform marker/hover styling shared by the "sorted metering points" family of charts
MARKER_STYLE = dict(color='lightblue', line=dict(color='black', width=1))
MP_HOVERTEMPLATE = "<b>MP_ID:</b> %{hovertext}<br>Value: %{y}<extra></extra>"


def _prepare_sorted_mp_data(data: pd.DataFrame, feature: str):
    df = data.groupby(by="metering_point_id").sum(numeric_only=True)[feature]
    df = df.sort_values(ascending=False)

    x = np.arange(1, len(df) + 1)
    y = df.values
    mp_ids = df.index

    return df, x, y, mp_ids


def plot_sorted_mps_full(data:pd.DataFrame, feature:str, show=False) -> None:
    """Creates a interactive plotly chart with all 3 visualizations of distribution.
    1. Sorted Sums over Metering Point
    2. classical Histplot
    3. classical Boxplot"""
    start_time = data["time"].min()
    end_time = data["time"].max()
    df, x, y, mp_ids = _prepare_sorted_mp_data(data, feature)

    # subplots: 3 rows, 1 column
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.1,
        subplot_titles=(f"Sorted {df.name}-Values", f"Histogramm [{df.name}]", f"Boxplot [{df.name}]")
    )

    # bar plot on top
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        hovertext=mp_ids,
        hovertemplate=MP_HOVERTEMPLATE,
        name="Sorted values",
        marker=MARKER_STYLE,
    ), row=1, col=1)

    # histogram in the middle
    fig.add_trace(go.Histogram(
        x=y,
        nbinsx=100,  # adjust number of bins
        name="Histogram",
        marker=MARKER_STYLE,
    ), row=2, col=1)

    # horizontal boxplot at the bottom
    fig.add_trace(go.Box(
        x=y,
        orientation='h',
        boxpoints='outliers',  # show outliers
        marker=dict(color='black'),
        line=dict(color='black'),
        name="Boxplot"
    ), row=3, col=1)

    # layout adjustments
    fig.update_layout(
        title_text=f"{df.name} summed up on single metering points from {start_time.date()} - {end_time.date()} ({len(data.time.unique())} timestamps), {len(df)} mp ids, ",
        template="plotly_white",
        showlegend=False,
        height=900
    )

    # axis titles
    fig.update_xaxes(title_text="sorted Index", row=1, col=1)
    fig.update_yaxes(title_text=df.name, row=1, col=1)
    fig.update_xaxes(title_text=f"{df.name}", row=2, col=1)
    fig.update_yaxes(title_text="count", row=2, col=1)
    fig.update_xaxes(title_text=f"{df.name}", row=3, col=1)
    fig.update_yaxes(title_text="", row=3, col=1)

    if show:
        fig.show()
    return fig

def plot_profile_by_category(
    df,
    energy_col_name="sum_wt_meas_gen",
    agg_func_str="median",
    hue_col="weekday",
    extra_col=None,  # e.g. 'temp'
    logo=None,
):
    if agg_func_str not in ["mean", "median", "sum", "min", "max", "std"]:
        raise ValueError(f"Unsupported aggregation function: {agg_func_str}")

    if hue_col not in df.columns:
        raise ValueError(f"'{hue_col}' is not a column in the DataFrame!")

    df = df.copy()
    df["daytime"] = df.time.dt.strftime("%H:%M")

    # aggregate the energy data by hue_col & daytime
    temp_df = (
        df.groupby([hue_col, "daytime"])[energy_col_name]
        .agg(agg_func_str)
        .reset_index()
    )

    unique_cats = sorted(temp_df[hue_col].unique())
    color_list = px.colors.qualitative.Plotly
    colors = {cat: color_list[i % len(color_list)] for i, cat in enumerate(unique_cats)}

    fig = go.Figure()

    # plot the main data (hue_col)
    for cat in unique_cats:
        cat_df = temp_df[temp_df[hue_col] == cat]
        fig.add_trace(
            go.Scatter(
                x=cat_df["daytime"],
                y=cat_df[energy_col_name],
                mode="lines",
                name=f"{cat} ({agg_func_str})",
                line=dict(color=colors[cat], dash="solid"),
                yaxis="y",
            )
        )

    # an additional column (if given)
    if extra_col:
        if extra_col not in df.columns:
            raise ValueError(f"'{extra_col}' is not a column in the DataFrame!")

        extra_df = df.groupby("daytime")[extra_col].agg(agg_func_str).reset_index()

        # trace (hidden by default, but the axis stays visible!)
        fig.add_trace(
            go.Scatter(
                x=extra_df["daytime"],
                y=extra_df[extra_col],
                mode="lines",
                name=f"{extra_col} ({agg_func_str})",
                line=dict(color="black", dash="dot"),
                yaxis="y2",
            )
        )

        # make the y2 axis visible (with title)
        fig.update_layout(
            yaxis2=dict(
                title=extra_col,
                overlaying="y",
                side="right",
                showgrid=False,
                visible=True,  # <<< HERE: always visible!
            )
        )

    if logo is not None:
        fig.add_layout_image(logo)

    # general layout
    fig.update_layout(
        title=f"Daily profiles by category: {hue_col} ({agg_func_str})",
        xaxis=dict(
            title="Time of day", tickangle=45, automargin=True, tickfont=dict(size=12)
        ),
        yaxis=dict(title=f"{energy_col_name} ({agg_func_str})"),
        legend=dict(x=0.5, y=1.15, orientation="h", xanchor="center"),
        margin=dict(b=80, t=80, l=60, r=80),
        height=600,
    )

    fig.show()

def plot_sorted_mps_single(data: pd.DataFrame, feature: str, show=False):
    df, x, y, mp_ids = _prepare_sorted_mp_data(data, feature)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x,
        y=y,
        hovertext=mp_ids,
        hovertemplate=MP_HOVERTEMPLATE,
        marker=MARKER_STYLE,
        name="Sorted values"
    ))

    fig.update_layout(
        title=f"Sorted {df.name}-Values ({len(df)} MP IDs)",
        template="plotly_white",
        xaxis_title="sorted index",
        yaxis_title=df.name,
        height=450,
        showlegend=False
    )

    if show:
        fig.show()

    return fig

def plot_sorted_mps_comparison(
    data: pd.DataFrame,
    feature: str,
    feature_2: str,
    show=False
):
    df1, x1, y1, mp1 = _prepare_sorted_mp_data(data, feature)
    df2, x2, y2, mp2 = _prepare_sorted_mp_data(data, feature_2)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(feature, feature_2),
        shared_yaxes=True
    )

    fig.add_trace(go.Bar(
        x=x1,
        y=y1,
        hovertext=mp1,
        hovertemplate=MP_HOVERTEMPLATE,
        marker=MARKER_STYLE,
        name="Data 1"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=x2,
        y=y2,
        hovertext=mp2,
        hovertemplate=MP_HOVERTEMPLATE,
        marker=MARKER_STYLE,
        name="Data 2"
    ), row=1, col=2)

    fig.update_layout(
        title=f"Sorted {feature} vs. {feature_2} comparison",
        template="plotly_white",
        height=500,
        showlegend=False
    )

    fig.update_xaxes(title_text="sorted index")
    fig.update_yaxes(title_text=feature)

    if show:
        fig.show()

    return fig

def plot_distribution_single(data: pd.DataFrame, feature: str, show=False):
    df, _, y, _ = _prepare_sorted_mp_data(data, feature)

    fig = make_subplots(
        rows=2, cols=1,
        vertical_spacing=0.15,
        subplot_titles=(f"Histogram [{feature}]", f"Boxplot [{feature}]")
    )

    fig.add_trace(go.Histogram(
        x=y,
        nbinsx=100,
        marker=MARKER_STYLE,
        name="Histogram"
    ), row=1, col=1)

    fig.add_trace(go.Box(
        x=y,
        orientation='h',
        boxpoints='outliers',
        marker=dict(color='black'),
        line=dict(color='black'),
        name="Boxplot"
    ), row=2, col=1)

    fig.update_layout(
        title=f"Distribution of {feature}",
        template="plotly_white",
        height=600,
        showlegend=False
    )

    fig.update_xaxes(title_text=feature, row=1, col=1)
    fig.update_yaxes(title_text="count", row=1, col=1)
    fig.update_xaxes(title_text=feature, row=2, col=1)

    if show:
        fig.show()

    return fig

def plot_distribution_comparison(
    data: pd.DataFrame,
    feature: str,
    feature_2: str,
    show=False
):
    _, _, y1, _ = _prepare_sorted_mp_data(data, feature)
    _, _, y2, _ = _prepare_sorted_mp_data(data, feature_2)

    # ------------------------------------------------------------------
    # 1️⃣ Compute common x-range and binning
    # ------------------------------------------------------------------
    all_values = np.concatenate([y1, y2])

    x_min = np.nanmin(all_values)
    x_max = np.nanmax(all_values) + 5

    nbins = 100
    bin_width = (x_max - x_min) / nbins

    # ------------------------------------------------------------------
    # 2️⃣ Subplots
    # ------------------------------------------------------------------
    fig = make_subplots(
        rows=2,
        cols=2,
        vertical_spacing=0.15,
        subplot_titles=(
            f"Histogram – {feature}",
            f"Histogram – {feature_2}",
            f"Boxplot – {feature}",
            f"Boxplot – {feature_2}"
        ),
        #shared_xaxes=True
    )

    # ------------------------------------------------------------------
    # 3️⃣ Histograms with identical bins
    # ------------------------------------------------------------------
    fig.add_trace(go.Histogram(
        x=y1,
        xbins=dict(start=x_min, end=x_max, size=bin_width),
        marker=MARKER_STYLE,
        name=feature
    ), row=1, col=1)

    fig.add_trace(go.Histogram(
        x=y2,
        xbins=dict(start=x_min, end=x_max, size=bin_width),
        marker=MARKER_STYLE,
        name=feature_2
    ), row=1, col=2)

    # ------------------------------------------------------------------
    # 4️⃣ Boxplots (auto-aligned via shared x-axis)
    # ------------------------------------------------------------------
    fig.add_trace(go.Box(
        x=y1,
        orientation='h',
        boxpoints='outliers',
        marker=dict(color='black'),
        line=dict(color='black'),
        name=feature
    ), row=2, col=1)

    fig.add_trace(go.Box(
        x=y2,
        orientation='h',
        boxpoints='outliers',
        marker=dict(color='black'),
        line=dict(color='black'),
        name=feature_2
    ), row=2, col=2)

    # ------------------------------------------------------------------
    # 5️⃣ Layout & axis settings
    # ------------------------------------------------------------------
    fig.update_layout(
        title=f"Distribution comparison of {feature} vs. {feature_2}",
        template="plotly_white",
        height=700,
        showlegend=False
    )

    # Force identical x-axis range everywhere
    fig.update_xaxes(range=[x_min, x_max], title_text="Value")

    if show:
        fig.show()

    return fig


def plot_stacked_gain_loss_sortable(df, col1, col2):
    """Stacked bar chart comparing col1 vs. col2 per metering point, with buttons
    to switch which column the bars are sorted by.
    """
    df = df.reset_index()

    def compute_sorted(sort_col):
        df_sorted = df.sort_values(sort_col, ascending=False)

        base = df_sorted[col1]
        compare = df_sorted[col2]
        diff = compare - base

        return {
            "x": np.arange(1, len(df_sorted) + 1),
            "common": np.minimum(base, compare),
            "neg": (-diff).clip(lower=0),
            "pos": diff.clip(lower=0),
            "metering_point_id": df_sorted["metering_point_id"],
        }

    data_col1 = compute_sorted(col1)
    data_col2 = compute_sorted(col2)

    fig = go.Figure()

    bar_specs = [
        ("common", "blue", "Base"),
        ("neg", "red", f"Reductions: {col1} - {col2}"),
        ("pos", "green", f"Gains: {col2} - {col1}"),
    ]
    for key, color, name in bar_specs:
        fig.add_bar(
            x=data_col1["x"],
            y=data_col1[key],
            marker_color=color,
            name=name,
            hovertext=data_col1["metering_point_id"],  # MP ID in the hover
            hovertemplate="<b>metering_point_id:</b> %{hovertext}<br>Value: %{y}<extra></extra>",
        )

    def _sort_button(sort_col, data):
        return dict(
            label=f"sorted by {sort_col}",
            method="update",
            args=[
                {
                    "x": [data["x"], data["x"], data["x"]],
                    "y": [data["common"], data["neg"], data["pos"]],
                    "hovertext": [
                        data["metering_point_id"],
                        data["metering_point_id"],
                        data["metering_point_id"],
                    ],
                },
                {"title": f"Participation Factor Opt Results (sorted by {sort_col})"},
            ],
        )

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=True,
                y=-0.12,
                x=0.5,
                xanchor="center",
                direction="right",
                font=dict(size=9),
                pad=dict(l=0, r=0, t=0, b=0),
                buttons=[
                    _sort_button(col1, data_col1),
                    _sort_button(col2, data_col2),
                ],
            )
        ]
    )

    fig.update_layout(
        barmode="stack",
        title=f"Participation Factor Opt Results (sorted by {col1})",
        xaxis_title="sorted order",
        yaxis_title="kWh",
        template="plotly_white",
        legend=dict(
            orientation="h",
            x=0,
            y=1.1,
            xanchor="left",
            yanchor="top",
        ),
        xaxis_title_standoff=5,
        margin=dict(t=85, b=10)
    )

    fig.show()
