from modules.optimization_algorithms.OptAlgo import OptAlgo
from modules.data_schemas import ParticipationFactorSchedule, BaselineEnergyData
import numpy as np
from pandera.typing import DataFrame


class DefaultOptAlgo(OptAlgo):
    """
    This Optimization Algorithm subclass calculates the participation factor to make no changes to the distribution of energy.
    - Consumers should receive the same amount of Community Coverege
    - Generatos should receive the same amount of Consumed Generation
    - The resulting participation factor should be the same as from NashProductOptAlgo(alpha=1.0), but with much less computation time

    This participation factor works the intended way only when the participation factos of all participating metering points can be changed.
    If a least one metering points participation factor per category ("C"-Consumers or "G"-Generators) cannot be changed, the desired result of unchanged distribution cannot be achived.

    This subclass exists especially for multi-EEG optimization, where the surplus from one EEG is used to reduce the deficit of another EEG.
    - Therefore this subclass calculates the participation factor for unchaged distribution, to know how much can moved to the third EEG, where the combination of both EEGs tales place
    - So each metering points should be part with (1 - pf in source EEG) in the third combined EEG.
    """

    def __init__(self):
        super().__init__()
        self.__name__ = "DefaultOptAlgo"

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

        pfs["pf"] = np.nan

        # filter: Consumption (C)
        pfs.loc[pfs["energy_direction"] == "C", "pf"] = (
            pfs.loc[pfs["energy_direction"] == "C", "comm_cov"]
            / pfs.loc[pfs["energy_direction"] == "C", "wt_meas_cons"]
            * 100
        )

        # filter: Generation (G)
        pfs.loc[pfs["energy_direction"] == "G", "pf"] = (
            pfs.loc[pfs["energy_direction"] == "G", "cons_gen"]
            / pfs.loc[pfs["energy_direction"] == "G", "wt_meas_gen"]
            * 100
        )

        pfs["pf"] = pfs["pf"].fillna(100).clip(upper=100)

        complete_pfs = pfs[["time", "organization_id", "metering_point_id", "pf"]]

        return complete_pfs.copy()
    
    def get_params(self):
        return {}