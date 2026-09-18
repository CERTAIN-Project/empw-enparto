import pandas as pd
from pandera.typing import DataFrame

from modules.data_schemas import OptimizedEnergyData
from modules.participation_factor_schedule_evaluator import PFSEvaluator


class RelativeDiffOfSummedEnergyFlow(PFSEvaluator):
    """Evaluates, per timestamp, the relative difference between the optimized and
    baseline sum of an energy-flow feature: (sum_opt - sum) / sum.
    """

    def __init__(
        self,
        energy_flow_feature: str,
    ) -> None:
        self.energy_flow_feature: str = energy_flow_feature

    def evaluate_optimized_energy_data(
        self, optimized_energy_data: DataFrame[OptimizedEnergyData]
    ) -> pd.Series:
        """Returns (sum_opt_<feature> - sum_<feature>) / sum_<feature>, per timestamp."""
        sums_per_time = (
            optimized_energy_data.groupby(by="time")
            .sum(numeric_only=True)
            .add_prefix("sum_")
        )

        sum_col_name = f"sum_{self.energy_flow_feature}"
        opt_sum_col_name = f"sum_opt_{self.energy_flow_feature}"

        relative_diff = (
            sums_per_time[opt_sum_col_name] - sums_per_time[sum_col_name]
        ) / sums_per_time[sum_col_name]
        relative_diff.name = f"relative_diff_{self.energy_flow_feature}"

        return relative_diff
