import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

from modules.data_schemas._shared_checks import rows_have_columns_set_xor_unset

CONSUMPTION_COLS = [
    "wt_meas_cons",
    "comm_cov",
    "comm_pot",
    "opt_wt_meas_cons",
    "opt_comm_cov",
    "opt_comm_pot",
]
GENERATION_COLS = [
    "wt_meas_gen",
    "wt_surp_gen",
    "cons_gen",
    "opt_wt_meas_gen",
    "opt_wt_surp_gen",
    "opt_cons_gen",
]


class OptimizedEnergyData(pa.DataFrameModel):
    """Schema Definition for optimized energy data for single metering points within one or more EEGs.

    This schema represents the preprocessed and via. participation factor scheduled optimized/simulated energy data.
    """

    organization_id: Series[int] = pa.Field(ge=0)
    metering_point_id: Series[int] = pa.Field(ge=0)

    energy_direction: Series[str] = pa.Field(isin=["C", "G"], nullable=False)

    time: Series[pa.DateTime] = pa.Field(nullable=False)

    # Consumption-related
    wt_meas_cons: Series[float] = pa.Field(nullable=True, ge=0)
    comm_cov: Series[float] = pa.Field(nullable=True, ge=0)
    comm_pot: Series[float] = pa.Field(nullable=True, ge=0)

    # Optimized Consumption-related
    opt_wt_meas_cons: Series[float] = pa.Field(nullable=True, ge=0)
    opt_comm_cov: Series[float] = pa.Field(nullable=True, ge=0)
    opt_comm_pot: Series[float] = pa.Field(nullable=True, ge=0)

    # Generation-related
    wt_meas_gen: Series[float] = pa.Field(nullable=True, ge=0)
    wt_surp_gen: Series[float] = pa.Field(nullable=True, ge=0)
    cons_gen: Series[float] = pa.Field(nullable=True, ge=0)

    # Optimized Generation-related
    opt_wt_meas_gen: Series[float] = pa.Field(nullable=True, ge=0)
    opt_wt_surp_gen: Series[float] = pa.Field(nullable=True, ge=0)
    opt_cons_gen: Series[float] = pa.Field(nullable=True, ge=0)

    # -------------------------
    # Conditional checks
    # -------------------------

    @pa.check(None)
    def check_consumption_rows(self, df: pd.DataFrame) -> Series[bool]:
        """Consumer metering points should have all consumption related fields set, and all generation related fields unset."""
        return rows_have_columns_set_xor_unset(
            df, df["energy_direction"] == "C", CONSUMPTION_COLS, GENERATION_COLS
        )

    @pa.check(None)
    def check_generation_rows(self, df: pd.DataFrame) -> Series[bool]:
        """Generator metering points should have all generation related fields set, and all consumption related fields unset."""
        return rows_have_columns_set_xor_unset(
            df, df["energy_direction"] == "G", GENERATION_COLS, CONSUMPTION_COLS
        )

    class Config:
        strict = True
