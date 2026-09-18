import pandera.pandas as pa
from pandera.typing import Series


class ParticipationFactorSchedule(pa.DataFrameModel):
    """Schema Definition for participation factor schedules for single metering points within one or more EEGs."""

    organization_id: Series[int] = pa.Field(ge=0)
    metering_point_id: Series[int] = pa.Field(ge=0)
    time: Series[pa.DateTime]
    pf: Series[float] = pa.Field(ge=0, le=100)

    class Config:
        strict = True
