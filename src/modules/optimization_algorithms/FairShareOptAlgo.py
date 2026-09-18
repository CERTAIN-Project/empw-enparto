from modules.optimization_algorithms.OptAlgo import OptAlgo
from modules.data_schemas import ParticipationFactorSchedule, BaselineEnergyData
import pandas as pd
from abc import abstractmethod
from pandera.typing import DataFrame
from typing import Callable


class FairShareOptAlgo(OptAlgo):
    """This subclass of Optimization Algorithm refers to all algorithms with goal of re-distributing the energy within EEGs
    For Consumer the Communty Coverage gets re-distributed.
    For Generators the Generation consumed by the EEG gets re-distributed.
    Cause the main goal of those algorithms is a more fair energy distribution, without any costs-intensives, the sum of distributed energy should never be reduced.

    Therefore as Hard-Rule:
    - Consumers participation factors gets optimized during deficit
    - Generators participation factors gets optimized during surplus

    The enforcement of those 2 Hard-Rules is the main reason for existence of this class.
    """

    def __init__(self):
        super().__init__()
        self.__name__ = "abstract_FairShareOptAlgo"

    def calculate_pfs(
        self, baseline_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Applies participation factors for consumers during deficit and for generators during surplus.
        """
        baseline_energy_data = baseline_energy_data.copy()
        consumer_pfs = self._calculate_consumer_pfs_during_deficit(baseline_energy_data)

        generator_pfs = self._calculate_generator_pfs_during_surplus(
           baseline_energy_data
        )

        calced_pfs = pd.concat([consumer_pfs, generator_pfs], axis=0, ignore_index=True)
        #calced_pfs = pd.concat([consumer_pfs], axis=0, ignore_index=True)

        complete_pfs = pd.merge(
            left=baseline_energy_data[["organization_id", "metering_point_id", "time"]],
            right=calced_pfs,
            on=["organization_id", "metering_point_id", "time"],
            how="left",
        )

        complete_pfs["pf"] = complete_pfs["pf"].fillna(100)

        return complete_pfs

    # -------------------------
    # Protected helper methods
    # -------------------------
    def _with_per_time_sums(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merges each row with the per-timestamp column sums, prefixed 'sum_'."""
        return df.merge(
            df.groupby(by="time").sum().add_prefix("sum_").reset_index(),
            on="time",
            how="left",
        )

    def _timestamps_where(
        self, df: DataFrame[BaselineEnergyData], predicate: Callable[[pd.Series], pd.Series]
    ) -> pd.Series:
        """Computes, per timestamp, whether predicate holds for the summed surplus at that timestamp."""
        surplus_per_time = df.groupby("time")["wt_surp_gen"].sum()
        return predicate(surplus_per_time)

    def get_deficit_timestamps(self, df: DataFrame[BaselineEnergyData]) -> pd.Series:
        """
        Computes, per timestamp, whether a deficit (under-coverage) exists.
        Return: pd.Series with bool per timestamp
        """
        return self._timestamps_where(df, lambda surplus_per_time: surplus_per_time <= 0)

    def filter_deficit_rows(
        self, df: DataFrame[BaselineEnergyData]
    ) -> DataFrame[BaselineEnergyData]:
        """
        Filters all rows whose timestamp is in deficit.
        """
        deficit_timestamps = self.get_deficit_timestamps(df)
        # map onto all rows
        mask = df["time"].map(deficit_timestamps)
        return df[mask]

    def get_surplus_timestamps(
        self, df: DataFrame[BaselineEnergyData]
    ) -> pd.Series:
        """
        Computes, per timestamp, whether the sum of surplus energy > 0.
        Return: pd.Series with bool per timestamp
        """
        return self._timestamps_where(df, lambda surplus_per_time: surplus_per_time > 0)

    def filter_surplus_rows(
        self, df: DataFrame[BaselineEnergyData]
    ) -> DataFrame[BaselineEnergyData]:
        """
        Filters all rows whose timestamp has a positive surplus.
        """
        positive_timestamps = self.get_surplus_timestamps(df)
        mask = df["time"].map(positive_timestamps)
        return df[mask]

    def _apply_waterfilling(
        self,
        filtered_energy_data: DataFrame[BaselineEnergyData],
        feat_for_r0_pf_opt: str,
        feat_for_R0_pf_opt: str,
        cap: Callable[[pd.DataFrame], pd.DataFrame] = None,
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Iterative equal water-filling: at each round the available pool (R_i) is
        split equally across every still-active participant (U_i), each capped at
        its own remaining demand (r_i); the round repeats on what's left until the
        pool is exhausted or i > 20.

        cap, if given, is called with filtered_energy_data and must return a
        DataFrame with columns ["time", "cap"]; each participant's initial demand
        (r_0) is then clipped to that per-timestamp ceiling. Passing no cap (the
        default) reproduces plain equal water-filling.
        """
        work_pfo_algo = filtered_energy_data.copy()

        # INIT
        work_pfo_algo["A_0"] = 0
        work_pfo_algo["a_0"] = 0
        work_pfo_algo["r_0"] = work_pfo_algo[feat_for_r0_pf_opt]
        if cap is not None:
            cap_by_time = cap(filtered_energy_data)
            work_pfo_algo = work_pfo_algo.merge(cap_by_time, on="time", how="left")
            work_pfo_algo["r_0"] = work_pfo_algo[["r_0", "cap"]].min(axis=1, skipna=True)
            work_pfo_algo = work_pfo_algo.drop(columns="cap")
        work_pfo_algo["R_0"] = work_pfo_algo[feat_for_R0_pf_opt]
        work_pfo_algo["U_0"] = (
            True  # will this CMP still receive generation at this t?
        )
        work_pfo_algo = work_pfo_algo.merge(
            work_pfo_algo.groupby(by="time").sum()["U_0"].rename("U_count_0"),
            on="time",
            how="left",
        )

        i = 0
        while (
            work_pfo_algo.groupby(by="time")
            .sum()[f"U_{i}"]
            .rename(f"U_count_{i}")
            .max()
            > 0
        ) & (work_pfo_algo[f"R_{i}"].max() > 1e-9):

            work_pfo_algo[f"A_{i}"] = (
                work_pfo_algo[f"R_{i}"] / work_pfo_algo[f"U_count_{i}"]
            )
            work_pfo_algo[f"a_{i+1}"] = work_pfo_algo[[f"r_{i}", f"A_{i}"]].min(axis=1)
            work_pfo_algo[f"r_{i+1}"] = (
                work_pfo_algo[f"r_{i}"] - work_pfo_algo[f"a_{i+1}"]
            )

            work_pfo_algo = work_pfo_algo.merge(
                work_pfo_algo.groupby(by="time")
                .sum()[f"a_{i+1}"]
                .rename(f"sum_a_{i+1}"),
                on="time",
                how="left",
            )
            work_pfo_algo[f"R_{i+1}"] = (
                work_pfo_algo[f"R_{i}"] - work_pfo_algo[f"sum_a_{i+1}"]
            )
            work_pfo_algo[f"U_{i+1}"] = work_pfo_algo[f"r_{i+1}"] > 0
            work_pfo_algo = work_pfo_algo.merge(
                work_pfo_algo.groupby(by="time")
                .sum()[f"U_{i+1}"]
                .rename(f"U_count_{i+1}"),
                on="time",
                how="left",
            )
            i += 1
            if i > 20:
                break

        # Sum up for the final distribution
        a_cols = [col for col in work_pfo_algo.columns if col.startswith("a_")]
        work_pfo_algo["a_opt"] = work_pfo_algo[a_cols].sum(axis=1).clip(lower=0)
        work_pfo_algo["pf"] = (
            work_pfo_algo["a_opt"] / work_pfo_algo[feat_for_r0_pf_opt] * 100
        )

        pf_schedule = work_pfo_algo[["time", "organization_id", "metering_point_id", "pf"]].copy()
        pf_schedule["pf"] = pf_schedule["pf"].fillna(100).clip(upper=100)

        return pf_schedule

    # -------------------------
    # Abstract protected steps
    # -------------------------

    @abstractmethod
    def _calculate_consumer_pfs_during_deficit(
        self, baseline_cons_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize consumer participation factors during deficit.
        """
        pass

    @abstractmethod
    def _calculate_generator_pfs_during_surplus(
        self, baseline_gen_energy_data: DataFrame[BaselineEnergyData]
    ) -> DataFrame[ParticipationFactorSchedule]:
        """
        Optimize generator participation factors during surplus.
        """
        pass
