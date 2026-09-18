from pandera.typing import DataFrame

from modules.data_schemas import (
    BaselineEnergyData,
    OptimizedEnergyData,
    ParticipationFactorSchedule,
)
from modules.pf_calculations import apply_pf_schedule_to_mps


def apply_pfs_on_energy_data(
    energy_data: DataFrame[BaselineEnergyData],
    pfs: DataFrame[ParticipationFactorSchedule],
) -> DataFrame[OptimizedEnergyData]:
    """Applies a participation-factor schedule to baseline energy data."""
    return apply_pf_schedule_to_mps(energy_data, pfs)
