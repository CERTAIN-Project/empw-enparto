import pandas as pd
import numpy as np

from modules.fairness_metric_calculator import GiniCoeffCalculator
from modules.visualisations import plot_stacked_gain_loss_sortable  # noqa: F401  (kept for backward compatibility)


def apply_pf_schedule_to_mps(all_mps: pd.DataFrame, pf_schedule: pd.DataFrame):
    # NOTE: all calculations are only tested when cons pf are changed during deficit and only gens pf are changed during surplus
    # NOTE: we guess all calculations should be correct during other szenarios, but those calculations arent tested

    # calculate count of consumption and generation metering points for every single timestamp
    mp_counts_on_time = (
        all_mps
        .groupby("time")["energy_direction"]
        .value_counts()
        .unstack(fill_value=0)
        .rename(columns={"C": "count_C_mps", "G": "count_G_mps"})
    )

    # calculate sums of within whole EEG of all six relevant energy values for every single timestamp
    sums_on_time = all_mps.groupby(by="time").sum().reset_index().drop(columns=["organization_id", "metering_point_id", "energy_direction"]).rename(columns={"wt_meas_cons":"sum_wt_meas_cons", "comm_pot":"sum_comm_pot", "comm_cov":"sum_comm_cov", "wt_meas_gen":"sum_wt_meas_gen", "wt_surp_gen":"sum_wt_surp_gen", "cons_gen":"sum_cons_gen"})
    agg_on_time = pd.merge(left=sums_on_time, right=mp_counts_on_time, on="time", how="outer")
    applied_pfs = pd.merge(left = all_mps, right=pf_schedule, on=["time", "organization_id", "metering_point_id"], how="outer").merge(right=agg_on_time, on="time", how="left")

    # default pf schedule value is 100
    applied_pfs["pf"] = applied_pfs["pf"].fillna(100)
    applied_pfs["pf"] /= 100
    applied_pfs["surp_ratio"] = (applied_pfs["sum_wt_meas_gen"] / applied_pfs["sum_wt_meas_cons"]).replace(np.nan, 1).clip(upper=1)


    # applying pf to wt_meas consumption and generation direction via participation factor
    applied_pfs["opt_wt_meas_cons"] = applied_pfs["wt_meas_cons"] * applied_pfs["pf"]
    applied_pfs["opt_wt_meas_gen"] = applied_pfs["wt_meas_gen"] * applied_pfs["pf"]

    new_calced_agg_on_time = applied_pfs.groupby(by="time").sum().reset_index()[["time", "opt_wt_meas_cons", "opt_wt_meas_gen"]].rename(columns={"opt_wt_meas_cons":"sum_opt_wt_meas_cons", "opt_wt_meas_gen":"sum_opt_wt_meas_gen"})
    applied_pfs = applied_pfs.merge(new_calced_agg_on_time, on=["time"], how="left")

    # calculating new ratios of pf applied wt_meas consumption and generation
    applied_pfs["opt_wt_meas_gen_to_wt_meas_cons_ratio"] = (applied_pfs["sum_opt_wt_meas_gen"] / applied_pfs["sum_opt_wt_meas_cons"]).replace(np.nan, 1)
    applied_pfs["opt_wt_meas_gen_to_wt_meas_cons_ratio_clipped"] = applied_pfs["opt_wt_meas_gen_to_wt_meas_cons_ratio"].clip(upper=1)
    applied_pfs["opt_wt_meas_surp_to_wt_meas_gen_ratio_clipped"] = ((applied_pfs["sum_opt_wt_meas_gen"] - applied_pfs["sum_opt_wt_meas_cons"])/applied_pfs["sum_opt_wt_meas_gen"]).clip(lower=0)

    # applying new rations to calculate new comm_cov, comm_pot and wt_meas_surp after pf schedule application
    applied_pfs["opt_comm_cov"] = applied_pfs["opt_wt_meas_gen_to_wt_meas_cons_ratio_clipped"] * applied_pfs["opt_wt_meas_cons"]
    applied_pfs["opt_comm_pot"] = applied_pfs["opt_wt_meas_gen_to_wt_meas_cons_ratio"] * applied_pfs["opt_wt_meas_cons"]
    applied_pfs["opt_wt_surp_gen"] = applied_pfs["opt_wt_meas_surp_to_wt_meas_gen_ratio_clipped"] * applied_pfs["opt_wt_meas_gen"]
    applied_pfs["opt_cons_gen"] = applied_pfs["opt_wt_meas_gen"] - applied_pfs["opt_wt_surp_gen"]


    applied_pfs["comm_cov_delta"] = applied_pfs["opt_comm_cov"] - applied_pfs["comm_cov"]
    applied_pfs["cons_gen_delta"] = applied_pfs["opt_cons_gen"] - applied_pfs["cons_gen"]

    return applied_pfs.copy()


def gini(x):
    """Gini coefficient of a 1-D array of non-negative values."""
    return GiniCoeffCalculator().calculate_evaluation_metric(pd.Series(x))

def print_baseline_energy_data(df: pd.DataFrame) -> None:
    """
    Output of baseline (original) energy values before participation factor schedule application.
    Formatted to match the optimized output style.
    """
    baseline_energy_data = df

    # baseline residual grid draw
    baseline_residual_grid_draw = baseline_energy_data["wt_meas_cons"].sum() - baseline_energy_data["comm_cov"].sum()

    print("\nOriginal (Baseline) Sums:")

    print(f"\twt_meas_cons (c): {baseline_energy_data['wt_meas_cons'].sum():.3f}")
    print(f"\tcomm_cov (cc): {baseline_energy_data['comm_cov'].sum():.3f}")
    print(f"\t-> residual grid draw (c - cc): {baseline_residual_grid_draw:.3f}")
    print(f"\tcomm_pot (cp): {baseline_energy_data['comm_pot'].sum():.3f}")
    print(f"\twt_meas_gen (g): {baseline_energy_data['wt_meas_gen'].sum():.3f}")
    print(f"\twt_surp_gen (s): {baseline_energy_data['wt_surp_gen'].sum():.3f}")
    print(f"\tcons_gen (cg): {baseline_energy_data['cons_gen'].sum():.3f}")


def print_gini_on_smp_energy_flow(df) -> None:
    applied_pfs = df
    sums_on_c_mps = applied_pfs[applied_pfs["energy_direction"] == "C"].groupby(by="metering_point_id").sum(numeric_only=True)
    sums_on_g_mps = applied_pfs[applied_pfs["energy_direction"] == "G"].groupby(by="metering_point_id").sum(numeric_only=True)
    print("\nGini Coeff on optimized values:")
    print(f"\tGini-Coeff of SUMS of Community Coverage per single metering point\n\t[baseline]: {gini(sums_on_c_mps['comm_cov']):.3f}")
    print(f"\t[optimized]: {gini(sums_on_c_mps['opt_comm_cov']):.3f} [should be lower than original]")
    print()
    print(f"\tGini-Coeff of SUMS of Consumed Energy per single metering point\n\t[baseline]: {gini(sums_on_g_mps['cons_gen']):.3f}")
    print(f"\t[optimized]: {gini(sums_on_g_mps['opt_cons_gen']):.3f} [should be lower than original]")

def print_opt_energy_data(applied_pfs: pd.DataFrame, title:str="Optimized Sums") -> None:
    """
    Output of optimized values after participation factor schedule apply.
    Dynamically prints all relevant energy features with sums and comparisons.
    """

    # baseline & optimized residual grid draw
    baseline_residual_grid_draw = (
        applied_pfs["wt_meas_cons"].sum() - applied_pfs["comm_cov"].sum()
    )
    opt_residual_grid_draw = (
        applied_pfs["opt_wt_meas_cons"].sum() - applied_pfs["comm_cov"].sum()
    )

    print(f"\n{title}:")

    # Features to report: dynamically handle all columns starting with 'opt_'
    cons_feature_map = {
        "opt_wt_meas_cons": ("opt_meas_cons (c*)", "wt_meas_cons"),
        "opt_comm_cov": ("opt_comm_cov (cc*)", "comm_cov"),
        "opt_comm_pot": ("opt_comm_pot (cp*)", "comm_pot"),
    }

    gen_feature_map = {
        "opt_wt_meas_gen": ("opt_wt_meas_gen (g*)", "wt_meas_gen"),
        "opt_wt_surp_gen": ("opt_wt_surp_gen (s*)", "wt_surp_gen"),
        "opt_cons_gen": ("opt_cons_gen (cg*)", "cons_gen"),
    }

    def _print_feature_changes(feature_map:dict, category:str) -> None:
        """Prints the changes from baseline energy flow features to optimized energy flow features."""
        print(f"\t{category}")
        for opt_col, (label, base_col) in feature_map.items():
            opt_sum = applied_pfs[opt_col].sum()
            base_sum = applied_pfs[base_col].sum()
            diff = base_sum - opt_sum
            print(
                f"\t\t{label}: {opt_sum:.3f} [base {base_col}: {base_sum:.3f}, difference: {diff:.3f}]"
            )

    _print_feature_changes(cons_feature_map, "Consumers:")

    print(f"\t-> opt_residual_grid_draw (c* - cc*): {opt_residual_grid_draw:.3f}")
    print(f"\t-> real residual_grid_draw: {baseline_residual_grid_draw:.3f}")
    print(
        f"\t-> real residual_grid_draw + opt_comm_cov = {baseline_residual_grid_draw:.3f} + {applied_pfs['opt_comm_cov'].sum():.3f} = {applied_pfs['wt_meas_cons'].sum():.3f}"
    )

    _print_feature_changes(gen_feature_map, "Generators:")

def tf_to_int(tf_schedule:pd.DataFrame, mode:str="ceil")->pd.DataFrame:
    # valid string for: mode = "ceil"  # "floor" # "round"
    tf_schedule_int = tf_schedule.copy()
    tf_schedule_int["pf"] = {
        "floor": np.floor,
        "ceil": np.ceil,
        "round": np.round,
    }[mode](tf_schedule_int["pf"]).astype(int)

    return tf_schedule_int

def tf_to_hourly(tf_schedule:pd.DataFrame, mode:str="max")->pd.DataFrame:
    # valid string for: mode = "max"  # "min" # "mean" # "median" # "first" # "last"
    # bring the quarter-hourly PF schedule to hourly, to obtain a valid final OUTPUT for the first time
    tf_schedule_hourly = tf_schedule.copy()

    tf_schedule_hourly['hour'] = tf_schedule_hourly['time'].dt.floor('h')

    # compute the aggregated pf per mp_id and hour
    max_pf = (
        tf_schedule_hourly
        .groupby(['metering_point_id', 'hour'])['pf']
        .transform(mode)
    )

    # overwrite pf
    tf_schedule_hourly['pf'] = max_pf

    # drop the helper column again once no longer needed
    tf_schedule_hourly.drop(columns='hour', inplace=True)

    return tf_schedule_hourly

def tf_to_daily(tf_schedule: pd.DataFrame, mode: str = "max") -> pd.DataFrame:
    """
    Valid modes:
    - "max", "min", "mean", "median", "first", "last"
    - "q75" (75th percentile)
    """
    valid_modes = {"max", "min", "mean", "median", "first", "last", "q75"}
    if mode not in valid_modes:
        raise ValueError(f"Unknown mode: {mode}. Valid modes: {sorted(valid_modes)}")

    tf_schedule_daily = tf_schedule.copy()
    tf_schedule_daily["day"] = tf_schedule_daily["time"].dt.floor("d")

    agg_func = (lambda x: x.quantile(0.75)) if mode == "q75" else mode

    tf_schedule_daily["pf"] = (
        tf_schedule_daily
        .groupby(["metering_point_id", "day"])["pf"]
        .transform(agg_func)
    )

    tf_schedule_daily.drop(columns="day", inplace=True)

    return tf_schedule_daily
