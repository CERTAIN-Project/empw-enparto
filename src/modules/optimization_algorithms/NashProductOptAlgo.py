import pandas as pd
from pandera.typing import DataFrame

from modules.data_schemas import BaselineEnergyData, ParticipationFactorSchedule
from modules.optimization_algorithms.FairShareOptAlgo import FairShareOptAlgo

import cvxpy as cp

import numpy as np


class NashProductOptAlgo(FairShareOptAlgo):
    def __init__(self, alpha: float = 1, solver: str = cp.SCS):
        super().__init__()
        self.alpha = alpha
        self.solver = solver
        self.__name__ = "NashProductOptAlgo"

    def _calculate_consumer_pfs_during_deficit(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize consumer participation factors during deficit.
        """
        baseline_energy_data_with_sums = self._with_per_time_sums(baseline_energy_data)
        deficit_energy_data = self.filter_deficit_rows(baseline_energy_data_with_sums)
        consumer_energy_data = deficit_energy_data[
            deficit_energy_data["energy_direction"] == "C"
        ]
        generators_pfs = self._apply_nash_product(
            consumer_energy_data,
            feature_for_demand="wt_meas_cons",
            feature_for_available_pool="sum_wt_meas_gen",
        )

        return generators_pfs

    def _calculate_generator_pfs_during_surplus(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize generator participation factors during surplus.
        """
        baseline_energy_data_with_sums = self._with_per_time_sums(baseline_energy_data)
        surplus_energy_data = self.filter_surplus_rows(baseline_energy_data_with_sums)

        generatos_energy_data = surplus_energy_data[
            surplus_energy_data["energy_direction"] == "G"
        ]

        generators_pfs = self._apply_nash_product(
            generatos_energy_data,
            feature_for_demand="wt_meas_gen",
            feature_for_available_pool="sum_wt_meas_cons",
        )

        return generators_pfs

    def _calc_nash_product_for_single_timestamp(
        self, demands: pd.Series, total_available_pool: float
    ) -> pd.Series:
        demands_idx = demands.index
        demands = demands.values

        if demands.sum() == 0 or total_available_pool <= 0:
            return pd.Series(0.0, index=demands_idx)

        n = len(demands)

        # decision variables
        # how much energy/comm_cov should each participant receive?
        A = cp.Variable(n)

        # weighting
        w = demands**self.alpha
        w = w / w.sum()

        # objective function (classic weighted Nash product)
        # variant 1: weighted Nash
        objective = cp.Maximize(cp.sum(cp.multiply(w, cp.log(A + 1e-6))))
        # variant 2: pure Nash fairness (without weights)
        # objective = cp.Maximize(cp.sum(cp.log(A + 1e-6))) # -> result same as waterfilling

        # 1. no consumer may receive more than they need/consume
        # 2. no more may be distributed than is available
        constraints = [A <= demands, cp.sum(A) <= total_available_pool]

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=self.solver or cp.SCS, verbose=False)

        return A.value

    def _apply_nash_product(
        self,
        filtered_energy_data: pd.DataFrame,
        feature_for_demand: str,
        feature_for_available_pool: str,
    ) -> pd.DataFrame:

        def solve_one_timestamp(group: pd.DataFrame) -> pd.DataFrame:
            group = group.copy()

            # Freeze row order explicitly
            group = group.sort_values("metering_point_id")

            demands = group[feature_for_demand]
            index = group.index

            total_available_pool = group[feature_for_available_pool].mean()

            a_opt = self._calc_nash_product_for_single_timestamp(
                demands, total_available_pool
            )

            # Restore via positional alignment
            group["a_opt"] = a_opt

            return group

        result = filtered_energy_data.groupby("time", group_keys=False)[
            filtered_energy_data.columns
        ].apply(solve_one_timestamp, include_groups=False)

        if "a_opt" in result.columns and feature_for_demand in result.columns:
            result["pf"] = np.where(
                result[feature_for_demand] == 0,
                1,
                result["a_opt"] / result[feature_for_demand] * 100,
            )
        else:
            result["pf"] = 100

        pf_schedule = result[
            ["time", "organization_id", "metering_point_id", "pf"]
        ].copy()
        pf_schedule["pf"] = pf_schedule["pf"].fillna(100).clip(upper=100)

        return pf_schedule

    def get_params(self):
        return {"alpha": str(self.alpha), "solver": self.solver}
