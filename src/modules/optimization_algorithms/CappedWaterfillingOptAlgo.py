import pandas as pd
from pandera.typing import DataFrame
from typing import Callable

from modules.data_schemas import BaselineEnergyData, ParticipationFactorSchedule
from modules.optimization_algorithms.FairShareOptAlgo import FairShareOptAlgo


class CappedWaterfillingOptAlgo(FairShareOptAlgo):
    """Equal water-filling with a per-timestamp cap on how much surplus generation
    any single generator can be allocated: no generator may be allocated more than
    `cap`'s per-timestamp threshold (the 75th percentile of comm_cov, by default).
    Consumer participation factors during deficit are never capped.
    """

    def __init__(self, cap: Callable[[pd.DataFrame], pd.DataFrame] = None):
        super().__init__()
        self.__name__ = "CappedWaterfillingOptAlgo"

        self.cap = cap if cap is not None else (
            lambda df: (
                df
                .groupby("time", as_index=False)["comm_cov"]
                .quantile(0.75)
                .rename(columns={"comm_cov": "cap"})
            )
        )

    def _calculate_consumer_pfs_during_deficit(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize consumer participation factors during deficit. Never capped.
        """
        baseline_energy_data_with_sums = self._with_per_time_sums(baseline_energy_data)
        deficit_energy_data = self.filter_deficit_rows(baseline_energy_data_with_sums)
        consumer_energy_data = deficit_energy_data[
            deficit_energy_data["energy_direction"] == "C"
        ]

        return self._apply_waterfilling(
            consumer_energy_data,
            feat_for_r0_pf_opt="wt_meas_cons",
            feat_for_R0_pf_opt="sum_wt_meas_gen",
        )

    def _calculate_generator_pfs_during_surplus(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize generator participation factors during surplus, capped by self.cap.
        """
        baseline_energy_data_with_sums = self._with_per_time_sums(baseline_energy_data)
        surplus_energy_data = self.filter_surplus_rows(baseline_energy_data_with_sums)
        generatos_energy_data = surplus_energy_data[
            surplus_energy_data["energy_direction"] == "G"
        ]

        return self._apply_waterfilling(
            generatos_energy_data,
            feat_for_r0_pf_opt="wt_meas_gen",
            feat_for_R0_pf_opt="sum_wt_meas_cons",
            cap=self.cap,
        )

    def get_params(self):
        return {"cap": str(self.cap)}
