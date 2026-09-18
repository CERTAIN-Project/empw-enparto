import pandas as pd

from modules.optimization_algorithms.NashProductOptAlgo import NashProductOptAlgo

import cvxpy as cp
import numpy as np


class XNashProductOptAlgo(NashProductOptAlgo):
    """NashProductOptAlgo variant that carries a cumulative per-day allocation
    across timestamps, so the Nash product is computed on (allocation-so-far +
    this timestamp's share) rather than on each timestamp independently.
    """

    def __init__(self, alpha: float, solver: str):
        super().__init__(alpha=alpha, solver=solver)
        self.__name__ = "XNashProductOptAlgo"

    def _calc_nash_product_for_single_timestamp(
        self,
        demands: pd.Series,
        total_available_pool: float,
        cum_alloc: np.ndarray,  # new
    ) -> np.ndarray:

        demands_np = demands.values
        n = len(demands_np)

        if demands_np.sum() == 0 or total_available_pool <= 0:
            return np.zeros(n)

        # decision variables
        A = cp.Variable(n, nonneg=True)

        # weighting
        w = (demands_np + cum_alloc) ** self.alpha
        w = w / w.sum()

        # effective "baseline" = allocation so far this day
        S_prev = cum_alloc

        # Nash product on (S_prev + A)
        objective = cp.Maximize(cp.sum(cp.multiply(w, cp.log(S_prev + A + 1e-6))))

        constraints = [A <= demands_np, cp.sum(A) <= total_available_pool]

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=self.solver or cp.SCS, verbose=False)

        return A.value

    def _apply_nash_product(
        self,
        filtered_energy_data: pd.DataFrame,
        feature_for_demand: str,
        feature_for_available_pool: str,
    ) -> pd.DataFrame:

        def solve_one_day(day_group: pd.DataFrame) -> pd.DataFrame:
            day_group = day_group.copy()

            # fixed ordering
            day_group = day_group.sort_values(["time", "metering_point_id"])

            metering_ids = day_group["metering_point_id"].unique()
            n = len(metering_ids)

            # cumulative allocation over the day
            cum_alloc = np.zeros(n)

            results = []

            for time, group in day_group.groupby("time"):
                group = group.sort_values("metering_point_id")

                demands = group[feature_for_demand]
                total_available_pool = group[feature_for_available_pool].mean()

                a_opt = self._calc_nash_product_for_single_timestamp(
                    demands=demands,
                    total_available_pool=total_available_pool,
                    cum_alloc=cum_alloc,
                )

                # advance cumulative allocation
                cum_alloc += a_opt

                group = group.copy()
                group["a_opt"] = a_opt
                results.append(group)

            return pd.concat(results)

        result = (
            filtered_energy_data.assign(date=lambda df: df["time"].dt.date)
            .groupby("date", group_keys=False)
            .apply(solve_one_day)
        )

        if "a_opt" in result.columns and feature_for_demand in result.columns:
            result["pf"] = np.where(
                result[feature_for_demand] == 0,
                1,
                result["a_opt"] / result[feature_for_demand] * 100,
            )
        else:
            result["pf"] = 100
        result["pf"] = result["pf"].fillna(100).clip(upper=100)

        pf_schedule = result[
            ["time", "organization_id", "metering_point_id", "pf"]
        ].copy()

        return pf_schedule
