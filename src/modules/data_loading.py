"""Module for data loading of energy-community data from the production database"""

import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


def get_postgres_engine() -> str:
    """Returns postgres database connection string based on ENVs"""
    server_ip = os.getenv("POSTGRES_SERVER_IP")
    postgres_username = os.getenv("POSTGRES_USERNAME")
    postgres_pw = os.getenv("POSTGRES_PASSWORD")
    postgres_database = os.getenv("POSTGRES_DATABASE")
    postgres_port = os.getenv("POSTGRES_PORT")

    postgres_connection_string = f"postgresql+psycopg2://{postgres_username}:{postgres_pw}@{server_ip}:{postgres_port}/{postgres_database}"

    return postgres_connection_string


def load_energy_community_data(
    org_id: int,
    time_start: datetime,
    time_end: datetime,
    sql_engine: str,
    limit=1_000_000,
) -> pd.DataFrame:
    """Loads energy data from production DB summed up on whole org_id"""
    sql_query = """SELECT
        organization_id,
        period_begin AS time,
        COUNT(organization_id) AS metering_points_cnt,
        COUNT(organization_id) FILTER (WHERE energy_direction = 'C') AS consumer_count,
        COUNT(organization_id) FILTER (WHERE energy_direction = 'G') AS generator_count,
        ROUND(SUM(wt_meas_cons)::numeric, 3) AS sum_wt_meas_cons,
        ROUND(SUM(comm_pot)::numeric, 3) AS sum_comm_pot,
        ROUND(SUM(comm_cov)::numeric, 3) AS sum_comm_cov,
        ROUND(SUM(wt_meas_gen)::numeric, 3) AS sum_wt_meas_gen,
        ROUND(SUM(wt_surp_gen)::numeric, 3) AS sum_wt_surp_gen
    FROM (
        SELECT
            ed.organization_id,
            ed.period_begin,
            mp.energy_direction,
            MIN(CASE WHEN measurement_type::text = 'WMC' THEN energy_value END) AS wt_meas_cons,
            MIN(CASE WHEN measurement_type::text = 'CP'  THEN energy_value END) AS comm_pot,
            MIN(CASE WHEN measurement_type::text = 'CC'  THEN energy_value END) AS comm_cov,
            MIN(CASE WHEN measurement_type::text = 'WMG' THEN energy_value END) AS wt_meas_gen,
            MIN(CASE WHEN measurement_type::text = 'WSG' THEN energy_value END) AS wt_surp_gen
        FROM v_energy_data ed
        JOIN v_metering_point mp
            ON ed.metering_point_id = mp.metering_point_id
        GROUP BY ed.organization_id, ed.metering_point_id, mp.energy_direction, ed.period_begin, ed.period_interval
    ) AS sub
    WHERE
        organization_id = %s
        AND period_begin >= %s
        AND period_begin <= %s
    GROUP BY organization_id, period_begin
    LIMIT %s;"""

    df_raw = pd.read_sql(
        sql_query, sql_engine, params=(org_id, time_start, time_end, limit)
    )
    df_raw["time"] = pd.to_datetime(df_raw["time"], utc=True)
    if len(df_raw) != 0:
        df_raw["time"] = df_raw["time"].dt.tz_convert("UTC")

    log_missing_timestamps(
        time_start, time_end, df_raw.time, freq="15min", dataset_name="energy_data"
    )

    df_sorted = df_raw.sort_values(by="time").reset_index(drop=True)

    return df_sorted.copy()


def validate_loaded_timeperiod_completeness(
    request_start: datetime,
    request_end: datetime,
    loaded_timeperiod: pd.Series,
    freq: str = "1h",
) -> pd.DatetimeIndex:
    """Calculates all missing datetimes within 'request_start' - 'request_end' based on target 'freq'"""
    expected = pd.date_range(request_start, request_end, freq=freq)

    if len(loaded_timeperiod) == 0:
        return expected

    loaded = pd.to_datetime(loaded_timeperiod.sort_values().unique()).tz_convert(
        request_start.tzinfo
    )
    missing = expected.difference(loaded)

    return missing


def get_timeperiods_from_timestamps(
    missing_timestamps: pd.DatetimeIndex, freq: str = "1h"
) -> list[tuple[int, datetime, datetime]]:
    """Groups several timestamps to closed timeperiods together"""
    diffs = missing_timestamps.to_series().diff() != pd.to_timedelta(freq)
    group_ids = diffs.cumsum()
    grouped = missing_timestamps.to_series().groupby(group_ids)

    return [(len(group), group.iloc[0], group.iloc[-1]) for _, group in grouped]


def format_timeperiods(timeperiods: list[tuple[int, datetime, datetime]]) -> list[str]:
    """Formats tuple representing timeperiod:[length of timeperiod; period start; period end] as human readable text"""
    return [
        f"{tp[0]} -> {tp[1].isoformat()} - {tp[2].isoformat()}" for tp in timeperiods
    ]


def log_missing_timestamps(
    request_start: datetime,
    request_end: datetime,
    loaded_timeperiod: pd.Series,
    freq: str = "1h",
    dataset_name: str = "data",
) -> None:
    """Logs if all requested timestamps in certain period are in target pd.Series.
    If not, all missing timestamps are logged as closed timeperiods
    """
    missing_timestamps = validate_loaded_timeperiod_completeness(
        request_start, request_end, loaded_timeperiod.sort_values(), freq=freq
    )

    if len(missing_timestamps) != 0:
        missing_timeperiods = get_timeperiods_from_timestamps(missing_timestamps, freq)
        formated_timeperiods = format_timeperiods(missing_timeperiods)

        logger.warning(
            "Unable to load requested '%s', missing %d records in %d periods: [%s]",
            dataset_name,
            len(missing_timestamps),
            len(formated_timeperiods),
            "; ".join(formated_timeperiods),
        )
    else:
        logger.info(
            "Successfully loaded all requested '%s' -> %s - %s",
            dataset_name,
            loaded_timeperiod.min(),
            loaded_timeperiod.max(),
        )


def load_all_metering_points_in_energy_community_data(
    org_id: int, time_start: datetime, time_end: datetime, sql_engine: str
) -> pd.DataFrame:
    """Loads energy data from production DB summed up on single metering point"""
    sql_query = """SELECT
        ed.organization_id,
        ed.metering_point_id,
        ed.time,
        ed.period_interval,
        mp.energy_direction,
        ROUND(ed.wt_meas_cons::numeric, 3) AS wt_meas_cons,
        ROUND(ed.comm_pot::numeric, 3)     AS comm_pot,
        ROUND(ed.comm_cov::numeric, 3)     AS comm_cov,
        ROUND(ed.wt_meas_gen::numeric, 3)  AS wt_meas_gen,
        ROUND(ed.wt_surp_gen::numeric, 3)  AS wt_surp_gen
    FROM (
        SELECT
            organization_id,
            ed.metering_point_id,
            period_begin AS time,
            period_interval,
            MIN(CASE WHEN measurement_type::text = 'WMC' THEN energy_value END) AS wt_meas_cons,
            MIN(CASE WHEN measurement_type::text = 'CP'  THEN energy_value END) AS comm_pot,
            MIN(CASE WHEN measurement_type::text = 'CC'  THEN energy_value END) AS comm_cov,
            MIN(CASE WHEN measurement_type::text = 'WMG' THEN energy_value END) AS wt_meas_gen,
            MIN(CASE WHEN measurement_type::text = 'WSG' THEN energy_value END) AS wt_surp_gen
        FROM v_energy_data ed
        WHERE organization_id = %s
        AND period_begin >= %s
        AND period_begin <= %s
        GROUP BY organization_id, ed.metering_point_id, period_begin, period_interval
    ) AS ed
    JOIN v_metering_point mp
        ON ed.metering_point_id = mp.metering_point_id
    """

    df_raw = pd.read_sql(sql_query, sql_engine, params=(org_id, time_start, time_end))
    df_raw["time"] = pd.to_datetime(df_raw["time"], utc=True)

    if len(df_raw) != 0:
        df_raw["time"] = df_raw["time"].dt.tz_convert("UTC")

    log_missing_timestamps(
        time_start, time_end, df_raw.time, freq="15min", dataset_name="energy_data"
    )

    df_sorted = df_raw.sort_values(by=["metering_point_id", "time"]).reset_index(
        drop=True
    )

    return df_sorted.copy()
