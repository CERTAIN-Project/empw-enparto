"""Shared pandera row-checks reused across the energy-data schemas."""

import pandas as pd
from pandera.typing import Series


def rows_have_columns_set_xor_unset(
    df: pd.DataFrame,
    direction_mask: pd.Series,
    present_cols: list,
    absent_cols: list,
) -> Series[bool]:
    """For rows matching direction_mask, checks that present_cols are all set and
    absent_cols are all unset. Used to enforce that a metering point's
    energy_direction ('C' consumer or 'G' generator) has exactly the matching set
    of fields populated.
    """
    return (
        df.loc[direction_mask, present_cols].notna().all(axis=1)
        & df.loc[direction_mask, absent_cols].isna().all(axis=1)
    )
