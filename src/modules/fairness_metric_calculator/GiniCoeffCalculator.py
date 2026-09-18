import numpy as np
import pandas as pd

from modules.fairness_metric_calculator import FairnessMetricCalculator


class GiniCoeffCalculator(FairnessMetricCalculator):
    """Calculator for the Gini coefficient"""

    def calculate_evaluation_metric(self, values: pd.Series) -> float:
        """
        Calculates the Gini coefficient for any series of values.
        """
        x = np.asarray(values, dtype=float)
        if len(x) == 0 or np.mean(x) == 0:
            return 0.0

        # mean absolute pairwise difference, vectorized: sum_{i,j} |xi - xj| = 2 * sum_{i<j} |xi - xj|
        abs_pairwise_diff_sum = np.abs(x[:, None] - x[None, :]).sum()
        return abs_pairwise_diff_sum / (2 * len(x) ** 2 * np.mean(x))

    def get_name(self) -> str:
        return "Gini coefficient"

    def get_interpretation(self) -> str:
        return f"""{self.get_name()} interpretation
        | {self.get_name()} | Interpretation        |
        | --------- | --------------------- |
        | 0.0–0.1   | Very fair             |
        | 0.1–0.3   | Low inequality        |
        | 0.3–0.5   | Moderate inequality   |
        | > 0.5     | Strong inequality     |
        """
