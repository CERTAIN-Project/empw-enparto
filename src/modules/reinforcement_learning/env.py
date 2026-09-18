"""
Gymnasium reinforcement-learning environment for participation-factor
optimisation within a renewable energy community (REC).

usage: imported by the RL prototyping notebooks, not run standalone.
"""

#  pylint: disable=invalid-name

from __future__ import annotations
import gymnasium as gym
import random
import numpy as np
import pandas as pd
import datetime
from modules.optimization_algorithms.NashProductOptAlgo import NashProductOptAlgo
import cvxpy as cp
from modules.pf_calculations import gini, apply_pf_schedule_to_mps

class EEGOpt(gym.Env):
    """Gymnasium Reinforcement Environment for Optimizing the Energy Flow within Energy Communites.
    """

    def __init__(
        self, baseline_energy_data, default_episode_date: datetime.date = None
    ):
        self.n_episode =0
        self.n_steps=0
        # PARAMS
        # ed ... energy_data
        self.default_ed: pd.DataFrame = baseline_energy_data.copy()
        self.default_episode_date = default_episode_date

        # calculate varaibles
        self.metering_point_ids = self.default_ed[
            self.default_ed["energy_direction"] == "C"
        ]["metering_point_id"].unique()
        # mps_cnt ... metering points count
        self.mps_cnt = len(self.metering_point_ids)

        self.dates: np.ndarray = self.default_ed[
            "time"
        ].dt.date.drop_duplicates().values
        if self.default_episode_date is not None:
            if self.default_episode_date not in self.dates:
                raise ValueError("default_episode_date not in dates in energy data")

        # for every time step, a weighting parameter is determined for each metering
        # point, i.e. how much this metering point should be considered at this time step
        self.action_space = gym.spaces.Box(
            low=0.0,
            high=1.0,
            shape=(),
            dtype=np.float32
        )

        self.observation_space = gym.spaces.Box(
            low=0, high=np.inf, shape=(self.mps_cnt * 2 + 2,), dtype=np.float32
        )

        # populated by reset()
        self.act_episode_date = None
        self.act_episode_ed = None
        self.act_obs_ts = None


    def reset(self, seed=None, options=None, **kwargs):
        """
        Reset to new episode.
        One Episode represents one calender day with 96 timestamps in 15min freq.
        The chosen day is either random, of fixed.
        The Episode always start at 00:00 and ende at 23:45.
        """
        if self.default_episode_date is None:
            self.act_episode_date = random.choice(self.dates)
        else:
            self.act_episode_date = self.default_episode_date

        self.act_episode_ed = self.default_ed[
            self.default_ed["time"].dt.date == self.act_episode_date
        ].copy()

        self.act_episode_ed["a_opt"] = 0

        # act_obs_ts ... timestamps of observation_timestamps
        self.act_obs_ts = self.act_episode_ed["time"].min()


        act_observation = self.get_state()

        info = {}

        return act_observation, info



    def step(self, action):
        self.n_steps+=1
        self.act(action)

        obs = self.get_state()
        if self.act_obs_ts != self.act_episode_ed["time"].max():
            self.act_obs_ts += datetime.timedelta(minutes=15)
            reward = self.get_reward(verbose=False)
            terminated = False
        else:
            reward = self.get_reward(verbose=True)
            print(f"terminate episode[{self.n_episode}/{self.n_steps}]")
            self.n_episode += 1
            terminated = True

        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info

    def get_reward(self, verbose=False):
        cons_df = self.act_episode_ed[
                self.act_episode_ed["energy_direction"] == "C"
            ]

        sums_on_c_mps = cons_df.groupby(by="metering_point_id").sum(numeric_only=True)

        baseline_gini = gini(sums_on_c_mps["comm_cov"])
        opt_gini = gini(sums_on_c_mps["a_opt"])
        reward =  baseline_gini - opt_gini
        if verbose:
            print(f"terminate {self.n_steps} episode; with r. {reward}[{baseline_gini} - {opt_gini}]")

        return reward

    def act(self, action):
        """
        Distribute REC generation to all metering points based on priorities.

        action_priorities: np.array or pd.Series, length = number of metering points
        """
        # current consumption values and available REC generation
        # act observation energy data ... filtered on single timestamp
        act_obs_ed = self.act_episode_ed[
            (self.act_episode_ed["time"] == self.act_obs_ts)
        ]

        if act_obs_ed["wt_surp_gen"].sum() <= 0:
            act_obs_deficit_ed = act_obs_ed #_filter_deficit_rows(act_obs_ed_with_sums)

            algo = NashProductOptAlgo(alpha=float(action), solver=cp.SCS)
            act_obs_pfs= algo.calculate_pfs(act_obs_deficit_ed)

            act_obs_applied_pfs = apply_pf_schedule_to_mps(act_obs_deficit_ed, act_obs_pfs)

            # sort the a_opt DataFrame
            act_obs_applied_pfs["a_opt"] = act_obs_applied_pfs["opt_comm_cov"]
            act_obs_opt_comm_cov_sorted = act_obs_applied_pfs.sort_values(
                "metering_point_id"
            )[["time", "metering_point_id", "a_opt"]]

            # merge into self.act_episode_ed
            # we only want to update the rows where a_opt exists, otherwise overwrite nothing
            self.act_episode_ed = self.act_episode_ed.merge(
                act_obs_opt_comm_cov_sorted,
                on=["time", "metering_point_id"],
                how="left",
                suffixes=("", "_new"),
            )

            # write the new values into the existing "a_opt" column (reset() always creates it),
            # only overwriting the rows that are not NaN
            self.act_episode_ed["a_opt"] = self.act_episode_ed[
                "a_opt_new"
            ].combine_first(self.act_episode_ed["a_opt"])

            # drop the temporary column
            self.act_episode_ed.drop(columns=["a_opt_new"], inplace=True)
        else:
            self.act_episode_ed["a_opt"] = self.act_episode_ed["comm_cov"]

    def get_state(self):
        # computes the observation vector from the energy_data dataframe
        # the observation vector holds current_consumption, total already allocated comm_cov, current total_generation, and hour of day
        total_gen = self.act_episode_ed[self.act_episode_ed["time"] == self.act_obs_ts][
            "wt_meas_gen"
        ].sum()

        obs_df = (
            self.act_episode_ed[
                (self.act_episode_ed["time"] == self.act_obs_ts)
                & (self.act_episode_ed["energy_direction"] == "C")
            ]
            .sort_values("metering_point_id")
            .reset_index(drop=True)
        )

        cumulative_allocation = (
            self.act_episode_ed[
                (self.act_episode_ed["energy_direction"] == "C")
                & (self.act_episode_ed["time"] <= self.act_obs_ts)
            ]
            .groupby("metering_point_id")["a_opt"]
            .sum()
        )

        # map onto the current consumer metering points, missing values = 0
        obs_df["cumulative_allocation"] = (
            obs_df["metering_point_id"].map(cumulative_allocation).fillna(0)
        )

        obs_df["current_consumption"] = obs_df["wt_meas_cons"]
        obs_df["total_gen"] = total_gen
        obs_df["hour"] = obs_df["time"].dt.hour

        obs_array = np.concatenate(
            [
                obs_df["current_consumption"].values,
                obs_df["cumulative_allocation"].values,
                [total_gen],
                [obs_df["hour"].iloc[0]],
            ]
        ).astype(np.float32)

        return obs_array
