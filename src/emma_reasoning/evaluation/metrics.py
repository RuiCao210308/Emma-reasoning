"""Evaluation metrics with explicit temporal semantics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class TrajectoryMetrics:
    """Core open-loop metrics for one prediction window."""

    ade_m: float
    fde_m: float
    longitudinal_mae_m: float
    lateral_mae_m: float


def _as_xy(points: ArrayLike, *, name: str) -> FloatArray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError(f"{name} must have shape (T, 2); got {array.shape}.")
    if array.shape[0] == 0:
        raise ValueError(f"{name} must contain at least one timestep.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")
    return array


def horizon_index(horizon_seconds: float, *, dt: float, length: int) -> int:
    """Return the zero-based index corresponding exactly to a future horizon.

    Prediction arrays are assumed to contain states *after* every interval:
    index 0 is at ``dt``, index 1 is at ``2 * dt``, and so on.
    For example, with ``dt=0.5``, the 1-second state is index 1.
    """
    if not np.isfinite(horizon_seconds) or horizon_seconds <= 0:
        raise ValueError("horizon_seconds must be positive and finite.")
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("dt must be positive and finite.")
    if length <= 0:
        raise ValueError("length must be positive.")

    steps = horizon_seconds / dt
    rounded_steps = int(round(steps))
    if not np.isclose(steps, rounded_steps, rtol=0.0, atol=1e-9):
        raise ValueError(
            f"horizon_seconds={horizon_seconds} is not aligned with dt={dt}."
        )
    index = rounded_steps - 1
    if index < 0 or index >= length:
        raise ValueError(
            f"Horizon {horizon_seconds}s requires index {index}, but length is {length}."
        )
    return index


def displacement_errors(predicted_xy: ArrayLike, target_xy: ArrayLike) -> FloatArray:
    """Euclidean displacement error at every aligned timestep."""
    predicted = _as_xy(predicted_xy, name="predicted_xy")
    target = _as_xy(target_xy, name="target_xy")
    if predicted.shape != target.shape:
        raise ValueError(
            f"predicted_xy and target_xy must match; got {predicted.shape} and {target.shape}."
        )
    return np.linalg.norm(predicted - target, axis=1)


def evaluate_trajectory(
    predicted_xy: ArrayLike,
    target_xy: ArrayLike,
    *,
    horizon_seconds: float | None = None,
    dt: float | None = None,
) -> TrajectoryMetrics:
    """Evaluate one trajectory in the initial ego-local frame.

    The x component is reported as longitudinal error and y as lateral error.
    If a horizon is provided, both trajectories are truncated through that exact
    future state, inclusive. This keeps ADE and FDE temporally consistent.
    """
    predicted = _as_xy(predicted_xy, name="predicted_xy")
    target = _as_xy(target_xy, name="target_xy")
    if predicted.shape != target.shape:
        raise ValueError(
            f"predicted_xy and target_xy must match; got {predicted.shape} and {target.shape}."
        )

    if horizon_seconds is not None:
        if dt is None:
            raise ValueError("dt is required when horizon_seconds is provided.")
        end_index = horizon_index(horizon_seconds, dt=dt, length=predicted.shape[0])
        predicted = predicted[: end_index + 1]
        target = target[: end_index + 1]
    elif dt is not None:
        raise ValueError("dt should only be supplied together with horizon_seconds.")

    error = predicted - target
    displacement = np.linalg.norm(error, axis=1)
    return TrajectoryMetrics(
        ade_m=float(np.mean(displacement)),
        fde_m=float(displacement[-1]),
        longitudinal_mae_m=float(np.mean(np.abs(error[:, 0]))),
        lateral_mae_m=float(np.mean(np.abs(error[:, 1]))),
    )


def action_mae(predicted: ArrayLike, target: ArrayLike, *, name: str = "action") -> float:
    """Mean absolute error for an aligned scalar action sequence."""
    predicted_array = np.asarray(predicted, dtype=np.float64)
    target_array = np.asarray(target, dtype=np.float64)
    if predicted_array.ndim != 1 or target_array.ndim != 1:
        raise ValueError(f"{name} sequences must be one-dimensional.")
    if predicted_array.shape != target_array.shape:
        raise ValueError(
            f"Predicted and target {name} shapes must match; "
            f"got {predicted_array.shape} and {target_array.shape}."
        )
    if predicted_array.size == 0:
        raise ValueError(f"{name} sequences must not be empty.")
    if not np.all(np.isfinite(predicted_array)) or not np.all(np.isfinite(target_array)):
        raise ValueError(f"{name} sequences contain non-finite values.")
    return float(np.mean(np.abs(predicted_array - target_array)))
