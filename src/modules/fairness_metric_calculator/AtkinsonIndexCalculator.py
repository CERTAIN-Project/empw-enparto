import numpy as np
import pandas as pd

from modules.fairness_metric_calculator import FairnessMetricCalculator


class AtkinsonIndexCalculator(FairnessMetricCalculator):
    """Calculator for the Atkinson index"""

    def __init__(self, epsilon: float=0.5):
        super().__init__()
        self.epsilon = epsilon

    def calculate_evaluation_metric(self, values: pd.Series) -> float:
        """
        Computes the Atkinson index of a distribution.

        Parameters
        ----------
        x : array-like
            Non-negative values (e.g. energy allocations)
        epsilon : float
            Inequality aversion (epsilon > 0)

        Returns
        -------
        float
            Atkinson index (0 = perfectly equal, 1 = maximum inequality)
        """
        x = np.array(values, dtype=float)

        if np.any(x < 0):
            raise ValueError("Atkinson index requires non-negative values.")

        if np.all(x == 0):
            return 0.0

        n = len(x)
        mean_x = np.mean(x)

        if self.epsilon == 1:
            # geometric mean
            if np.any(x == 0):
                return 1.0
            geo_mean = np.exp(np.mean(np.log(x)))
            return 1 - geo_mean / mean_x

        else:
            mean_power = np.mean(x ** (1 - self.epsilon))
            equally_distributed_equivalent = mean_power ** (1 / (1 - self.epsilon))
            return 1 - equally_distributed_equivalent / mean_x

    def get_name(self) -> str:
        return "Atkinson Index"

    def get_interpretation(self) -> str:
        return f"""{self.get_name()} interpretation
        | ε (epsilon) | Meaning                          |
        | ----------- | -------------------------------- |
        | 0.1         | low inequality aversion          |
        | 0.5         | moderately social                |
        | 1.0         | strongly social                  |
        | >1.0        | focus on the most disadvantaged  |
        """
