"""Physically explicit integration of speed-curvature action chunks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Rollout2D:
    """Discrete rollout sampled after each action interval.

    ``positions[t]`` and ``headings[t]`` represent the state after executing
    action ``t`` for its corresponding duration. The initial anchor is not
    included in either output array.
    """

    positions: FloatArray
    headings: FloatArray


def _as_1d(values: ArrayLike, *, name: str) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional; got {array.shape}.")
    if array.size == 0:
        raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")
    return array


def _expand_dt(dt: float | ArrayLike, *, length: int) -> FloatArray:
    values = np.asarray(dt, dtype=np.float64)
    if values.ndim == 0:
        values = np.full(length, float(values), dtype=np.float64)
    elif values.ndim == 1 and values.shape == (length,):
        values = values.copy()
    else:
        raise ValueError(f"dt must be a scalar or have shape ({length},); got {values.shape}.")
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("All dt values must be positive and finite.")
    return values


def integrate_speed_curvature(
    speeds_mps: ArrayLike,
    curvatures_inv_m: ArrayLike,
    *,
    dt: float | ArrayLike,
    initial_position_xy: ArrayLike = (0.0, 0.0),
    initial_heading_rad: float = 0.0,
    straight_threshold: float = 1e-9,
) -> Rollout2D:
    """Integrate a speed-curvature sequence with piecewise-constant arcs.

    Curvature is defined as ``d(heading) / d(distance)`` in ``1 / m``. During
    each interval, yaw rate is ``speed * curvature``. The implementation uses
    the exact circular-arc displacement for each constant action, avoiding the
    hidden one-second spacing present in the legacy OpenEMMA prototype.

    Args:
        speeds_mps: Speed at each future step, in metres per second.
        curvatures_inv_m: Signed curvature at each future step, in ``1 / m``.
        dt: A positive scalar duration shared by all steps, or one duration per
            step. nuScenes keyframes are nominally spaced by ``0.5`` seconds,
            while the reconstruction audit can use the recorded timestamps.
        initial_position_xy: Final observed ego position. In ego-local
            evaluation this should normally be ``(0, 0)``.
        initial_heading_rad: Heading at the final observed state. In ego-local
            coordinates this should normally be ``0``.
        straight_threshold: Curvature magnitude below which straight-line
            integration is used.

    Returns:
        A :class:`Rollout2D` containing states after each future action interval.
    """
    speeds = _as_1d(speeds_mps, name="speeds_mps")
    curvatures = _as_1d(curvatures_inv_m, name="curvatures_inv_m")
    if speeds.shape != curvatures.shape:
        raise ValueError(
            "speeds_mps and curvatures_inv_m must have identical shape; "
            f"got {speeds.shape} and {curvatures.shape}."
        )
    durations = _expand_dt(dt, length=speeds.size)
    if not np.isfinite(initial_heading_rad):
        raise ValueError("initial_heading_rad must be finite.")
    if straight_threshold < 0 or not np.isfinite(straight_threshold):
        raise ValueError("straight_threshold must be finite and non-negative.")

    initial_position = np.asarray(initial_position_xy, dtype=np.float64)
    if initial_position.shape != (2,) or not np.all(np.isfinite(initial_position)):
        raise ValueError("initial_position_xy must be a finite array with shape (2,).")

    positions = np.empty((speeds.size, 2), dtype=np.float64)
    headings = np.empty(speeds.size, dtype=np.float64)

    position = initial_position.copy()
    heading = float(initial_heading_rad)

    for index, (speed, curvature, duration) in enumerate(
        zip(speeds, curvatures, durations, strict=True)
    ):
        if abs(curvature) <= straight_threshold:
            delta_body_x = speed * duration
            delta_body_y = 0.0
            delta_heading = 0.0
        else:
            delta_heading = speed * curvature * duration
            delta_body_x = np.sin(delta_heading) / curvature
            delta_body_y = (1.0 - np.cos(delta_heading)) / curvature

        cosine = np.cos(heading)
        sine = np.sin(heading)
        delta_world = np.array(
            [
                cosine * delta_body_x - sine * delta_body_y,
                sine * delta_body_x + cosine * delta_body_y,
            ],
            dtype=np.float64,
        )
        position = position + delta_world
        heading = heading + delta_heading

        positions[index] = position
        headings[index] = heading

    return Rollout2D(positions=positions, headings=headings)
