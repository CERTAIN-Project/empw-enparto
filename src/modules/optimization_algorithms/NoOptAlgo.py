from modules.optimization_algorithms.OptAlgo import OptAlgo
from modules.data_schemas import ParticipationFactorSchedule, BaselineEnergyData
from pandera.typing import DataFrame


class NoOptAlgo(OptAlgo):
    """
    This Optimization Algorithm subclass returns an participation factor schedule with 100% for every available participation factor.
    """

    def __init__(self):
        super().__init__()
        self.__name__ = "NoOptAlgo"

    def calculate_pfs(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Applies participation factors to retain current energy flow distributions
        """
        pfs = baseline_energy_data[
            [
                "time",
                "organization_id",
                "metering_point_id",
                "energy_direction",
                "wt_meas_cons",
                "comm_cov",
                "wt_meas_gen",
                "cons_gen",
            ]
        ].copy()

        pfs["pf"] = 100

        complete_pfs = pfs[["time", "organization_id", "metering_point_id", "pf"]]

        return complete_pfs.copy()
    
    def get_params(self):
        return {}