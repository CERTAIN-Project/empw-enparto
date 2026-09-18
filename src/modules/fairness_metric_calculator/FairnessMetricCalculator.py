"""Abstract base class for calculating fairness metrics on resource distribuations."""

from abc import ABC, abstractmethod

import pandas as pd


class FairnessMetricCalculator(ABC):
    """Abstract base class for calculating fairness metrics on resource distribuations."""

    @abstractmethod
    def calculate_evaluation_metric(self, values: pd.Series) -> float:
        """Compute this fairness metric for a series of resource-share values."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the human-readable name of this metric."""

    @abstractmethod
    def get_interpretation(self) -> str:
        """Return interpreation text and tables on matric values."""
