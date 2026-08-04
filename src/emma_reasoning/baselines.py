"""Strictly history-only frozen ego-motion baselines."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from emma_reasoning.data.nuscenes_windows import EgoWindow
from emma_reasoning.trajectory.action_policy import PolicyActions, apply_action_policy
from emma_reasoning.trajectory.kinematics import estimate_interval_actions

FloatArray = NDArray[np.float64]


def _finite(values: ArrayLike, *, name: str, ndim: int) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != ndim or array.size == 0:
        raise ValueError(f"{name} must be a non-empty {ndim}-dimensional array.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")
    return array.copy()


@dataclass(frozen=True)
class ObservedMotion:
    """Motion information at or before the prediction anchor only."""

    positions_xy: FloatArray
    headings_rad: FloatArray
    timestamps_seconds: FloatArray
    history_actions: PolicyActions

    def __post_init__(self) -> None:
        positions = _finite(self.positions_xy, name="positions_xy", ndim=2)
        headings = _finite(self.headings_rad, name="headings_rad", ndim=1)
        timestamps = _finite(self.timestamps_seconds, name="timestamps_seconds", ndim=1)
        if positions.shape[1] != 2:
            raise ValueError("positions_xy must have shape (N, 2).")
        if positions.shape[0] != headings.size or headings.size != timestamps.size:
            raise ValueError("Observed pose, heading, and timestamp arrays must align.")
        if positions.shape[0] < 2 or np.any(np.diff(timestamps) <= 0):
            raise ValueError("Observed motion needs >=2 states and increasing timestamps.")
        if self.history_actions.speeds_mps.shape != (positions.shape[0] - 1,):
            raise ValueError("history_actions must contain one action per observed interval.")
        object.__setattr__(self, "positions_xy", positions)
        object.__setattr__(self, "headings_rad", headings)
        object.__setattr__(self, "timestamps_seconds", timestamps)


@dataclass(frozen=True)
class PredictionSchedule:
    """Permitted future timing only; deliberately excludes future motion state."""

    step_count: int
    future_dt_seconds: FloatArray

    def __post_init__(self) -> None:
        durations = _finite(self.future_dt_seconds, name="future_dt_seconds", ndim=1)
        if self.step_count <= 0 or durations.shape != (self.step_count,):
            raise ValueError("future_dt_seconds must have shape (step_count,).")
        if np.any(durations <= 0):
            raise ValueError("future_dt_seconds must be strictly positive.")
        object.__setattr__(self, "future_dt_seconds", durations)


def build_baseline_inputs(window: EgoWindow) -> tuple[ObservedMotion, PredictionSchedule]:
    """Split a full evaluation window at the leakage boundary before prediction."""
    anchor = window.anchor_index
    observed_stop = anchor + 1
    history_fit = estimate_interval_actions(
        window.positions_world_xy[:observed_stop],
        window.headings_world_rad[:observed_stop],
        window.timestamps_seconds[:observed_stop],
    )
    observed = ObservedMotion(
        positions_xy=window.positions_world_xy[:observed_stop],
        headings_rad=window.headings_world_rad[:observed_stop],
        timestamps_seconds=window.timestamps_seconds[:observed_stop],
        history_actions=apply_action_policy(history_fit.speeds_mps, history_fit.curvatures_inv_m),
    )
    future_timestamps = window.timestamps_seconds[anchor : anchor + window.fut_len + 1]
    schedule = PredictionSchedule(window.fut_len, np.diff(future_timestamps))
    return observed, schedule


def _constant(speed: float, curvature: float, schedule: PredictionSchedule) -> PolicyActions:
    return apply_action_policy(
        np.full(schedule.step_count, speed), np.full(schedule.step_count, curvature)
    )


def stationary(observed: ObservedMotion, schedule: PredictionSchedule) -> PolicyActions:
    del observed
    return _constant(0.0, 0.0, schedule)


def last_speed_straight(observed: ObservedMotion, schedule: PredictionSchedule) -> PolicyActions:
    return _constant(float(observed.history_actions.speeds_mps[-1]), 0.0, schedule)


def constant_last(observed: ObservedMotion, schedule: PredictionSchedule) -> PolicyActions:
    actions = observed.history_actions
    return _constant(
        float(actions.speeds_mps[-1]),
        float(actions.sanitized_curvatures_inv_m[-1]),
        schedule,
    )


def median3(observed: ObservedMotion, schedule: PredictionSchedule) -> PolicyActions:
    actions = observed.history_actions
    count = min(3, actions.speeds_mps.size)
    speed = float(np.median(actions.speeds_mps[-count:]))
    yaw_rate = float(np.median(actions.yaw_rates_rad_s[-count:]))
    curvature = 0.0 if abs(speed) < 0.1 else yaw_rate / speed
    return _constant(speed, curvature, schedule)


Baseline = Callable[[ObservedMotion, PredictionSchedule], PolicyActions]
FROZEN_BASELINES: dict[str, Baseline] = {
    "stationary": stationary,
    "last_speed_straight": last_speed_straight,
    "constant_last": constant_last,
    "median3": median3,
}
