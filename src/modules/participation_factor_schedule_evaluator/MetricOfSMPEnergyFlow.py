import pandas as pd
from pandera.typing import DataFrame

from modules.data_schemas import OptimizedEnergyData
from modules.fairness_metric_calculator import FairnessMetricCalculator
from modules.participation_factor_schedule_evaluator.PFSEvaluator import PFSEvaluator


class MetricOnAbsoluteSMPEnergyFlow(PFSEvaluator):
    """Application of a fairness metric to the distribution
    of the absolute energy flow within the REC.

    A value is computed for each individual quarter-hour time step.

    Fairness metrics: Gini coeff, Jain index, Theil index, ...
    Energy flows:
       - comm_cov for consumers
       - cons_gen for producers

    """

    def __init__(
        self, metric_calculator: FairnessMetricCalculator, energy_flow_feature: str
    ) -> None:
        self.metric_calculator: FairnessMetricCalculator = metric_calculator
        self.energy_flow_feature: str = energy_flow_feature

    def evaluate_optimized_energy_data(
        self, optimized_energy_data: DataFrame[OptimizedEnergyData]
    ) -> pd.Series:

        def _evaluate_one_time(single_timestap_ed: pd.DataFrame) -> float:
            values = single_timestap_ed[self.energy_flow_feature]
            return self.metric_calculator.calculate_evaluation_metric(values)

        metric_per_time = optimized_energy_data.groupby("time", sort=True).apply(
            _evaluate_one_time
        )

        metric_per_time.name = self.metric_calculator.__class__.__name__
        return metric_per_time
