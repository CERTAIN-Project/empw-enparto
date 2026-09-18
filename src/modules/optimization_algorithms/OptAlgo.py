from abc import ABC, abstractmethod
from modules.data_schemas import ParticipationFactorSchedule, BaselineEnergyData
from pandera.typing import DataFrame

class OptAlgo(ABC):
    """Abstract base class for any Optimization Algorithm"""

    def __init__(self):
        super().__init__()
        self.__name__ = "abstract_OptAlgo"

    @abstractmethod
    def calculate_pfs(self, baseline_energy_data: DataFrame[BaselineEnergyData]) -> DataFrame[ParticipationFactorSchedule]:
        """Return calculate participation factor schedule(pfs) for full time horizon and all mps of passed energy data.
        The pfs is optimized by X algorithms for Y optimization target.
        """
        pass

    @abstractmethod
    def get_params(self) -> dict:
        pass
