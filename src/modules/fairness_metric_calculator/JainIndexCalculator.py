import numpy as np
import pandas as pd

from modules.fairness_metric_calculator import FairnessMetricCalculator


class JainIndexCalculator(FairnessMetricCalculator):
    """Calculator for Jain's fairness index"""

    def calculate_evaluation_metric(self, values: pd.Series) -> float:
        """
        Computes Jain's fairness index for a list of values.
        """
        n = len(values)
        if n == 0:
            return 0

        x = np.asarray(values, dtype=float)
        sum_x = x.sum()
        sum_sq_x = (x**2).sum()

        # Formula: (sum x)^2 / (n * sum x^2)
        if sum_x == 0:
            fairness = 1
        else:
            fairness = (sum_x**2) / (n * sum_sq_x)

        return fairness

    def get_name(self) -> str:
        return "Jain Index"

    def get_interpretation(self) -> str:
        return f"""{self.get_name()} interpretation
        | {self.get_name()} | Interpretation            |
        | --------- | ------------------------- |
        | 1.0       | Perfectly equal distribution |
        | 0.9 - 1.0 | Very high fairness        |
        | 0.7 - 0.9 | Moderate fairness         |
        | < 0.7     | Significant inequality    |
        | 1/n       | Extremely unfair distribution |
        """
