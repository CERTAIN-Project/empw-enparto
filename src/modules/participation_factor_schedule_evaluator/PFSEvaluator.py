"""Abstract base class for evaluating any already calculated participation factor schedule."""

from abc import ABC, abstractmethod

import pandas as pd
from pandera.typing import DataFrame

from modules.data_schemas import OptimizedEnergyData


class PFSEvaluator(ABC):
    """Abstract base class for evaluating any already calculated participation factor schedule."""

    @abstractmethod
    def evaluate_optimized_energy_data(
        self, optimized_energy_data: DataFrame[OptimizedEnergyData]
    ) -> pd.Series:
        """Return a per-timestamp evaluation value computed from the optimized energy data."""
        pass
