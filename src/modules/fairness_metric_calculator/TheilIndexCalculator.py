import numpy as np
import pandas as pd

from modules.fairness_metric_calculator import FairnessMetricCalculator


class TheilIndexCalculator(FairnessMetricCalculator):
    """Calculator for the Theil index"""

    def calculate_evaluation_metric(self, values: pd.Series) -> float:
        """
        Computes the Theil index of a distribution.

        Parameters
        ----------
        values : array-like
            Non-negative values (e.g. energy allocations)

        Returns
        -------
        float
            Theil index (0 = perfectly equal distribution)
        """
        x = np.array(values, dtype=float)

        if np.any(x < 0):
            raise ValueError("Theil index requires non-negative values.")

        if np.all(x == 0):
            return 0.0

        mean_x = np.mean(x)

        # only consider positive values (0 * log(0) = 0)
        ratios = x[x > 0] / mean_x
        theil = np.mean(ratios * np.log(ratios))

        return theil

    def get_name(self) -> str:
        return "Theil Index"

    def get_interpretation(self) -> str:
        return f"""{self.get_name()} interpretation
        | {self.get_name()} | Interpretation            |
        | ----------- | ------------------------- |
        | 0.0         | perfectly equal distribution |
        | < 0.1       | very low inequality       |
        | 0.1–0.3     | moderate inequality       |
        | > 0.3       | strong inequality         |
        | > 1.0       | extreme inequality        |
        """
