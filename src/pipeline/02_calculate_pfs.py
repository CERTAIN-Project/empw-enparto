from pandera.typing import DataFrame

from modules.data_schemas import BaselineEnergyData, ParticipationFactorSchedule
from modules.optimization_algorithms import OptAlgo


def calculate_pfs(
    energy_data: DataFrame[BaselineEnergyData], optimization_algo: OptAlgo
) -> DataFrame[ParticipationFactorSchedule]:
    """Runs the given optimisation algorithm over the baseline energy data."""
    return optimization_algo.calculate_pfs(energy_data)
