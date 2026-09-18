from pandera.typing import DataFrame

from modules.data_schemas import BaselineEnergyData, ParticipationFactorSchedule
from modules.optimization_algorithms.FairShareOptAlgo import FairShareOptAlgo


class EqualWaterfillingOptAlgo(FairShareOptAlgo):

    def __init__(self):
        super().__init__()
        self.__name__ = "EqualWaterfillingOptAlgo"

    def _calculate_consumer_pfs_during_deficit(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize consumer participation factors during deficit.
        """
        baseline_energy_data_with_sums = self._with_per_time_sums(baseline_energy_data)

        self._print_surp_deficit_ratio(baseline_energy_data)
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
        Optimize generator participation factors during surplus.
        """
        baseline_energy_data_with_sums = self._with_per_time_sums(baseline_energy_data)
        surplus_energy_data = self.filter_surplus_rows(baseline_energy_data_with_sums)
        self._print_surp_deficit_ratio(baseline_energy_data)
        generatos_energy_data = surplus_energy_data[
            surplus_energy_data["energy_direction"] == "G"
        ]

        return self._apply_waterfilling(
            generatos_energy_data,
            feat_for_r0_pf_opt="wt_meas_gen",
            feat_for_R0_pf_opt="sum_wt_meas_cons",
        )

    def _print_surp_deficit_ratio(self, baseline_energy_data)->None:
        sums_ed = baseline_energy_data.groupby("time").sum().add_prefix("sum_").reset_index()
        time_with_deficit = sums_ed[sums_ed["sum_wt_surp_gen"] <= 0]
        time_with_surplus = sums_ed[sums_ed["sum_wt_surp_gen"] > 0]

        print(f"{len(time_with_deficit)}/{len(sums_ed)} ({(len(time_with_deficit)/len(sums_ed))*100:.4}%) timestamps has deficit. only for consumers during deficit a pf is optimized")
        print(f"{len(time_with_surplus)}/{len(sums_ed)} ({(len(time_with_surplus)/len(sums_ed))*100:.4}%) timestamps has surplus. only for generators during surplus a pf is optimized")


    def get_params(self):
        return {}
