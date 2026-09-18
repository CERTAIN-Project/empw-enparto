import pandas as pd
from pandera.typing import DataFrame

from modules.data_schemas import OptimizedEnergyData
from modules.participation_factor_schedule_evaluator import PFSEvaluator


class SignedDiffOfSummedEnergyFlow(PFSEvaluator):
    """Evaluates, per timestamp, the signed absolute difference between the
    optimized and baseline sum of an energy-flow feature: sum_opt - sum.
    """

    def __init__(
        self,
        energy_flow_feature: str,
    ) -> None:
        self.energy_flow_feature: str = energy_flow_feature

    def evaluate_optimized_energy_data(
        self, optimized_energy_data: DataFrame[OptimizedEnergyData]
    ) -> pd.Series:
        """Returns sum_opt_<feature> - sum_<feature>, per timestamp."""
        sums_per_time = (
            optimized_energy_data.groupby(by="time")
            .sum(numeric_only=True)
            .add_prefix("sum_")
        )

        sum_col_name = f"sum_{self.energy_flow_feature}"
        opt_sum_col_name = f"sum_opt_{self.energy_flow_feature}"

        signed_diff = sums_per_time[opt_sum_col_name] - sums_per_time[sum_col_name]
        signed_diff.name = f"signed_diff_{self.energy_flow_feature}"

        return signed_diff
