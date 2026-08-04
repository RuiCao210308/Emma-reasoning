"""Frozen, auditable speed-curvature action representation policy."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]
SPEED_EPSILON_MPS = 0.1


@dataclass(frozen=True)
class PolicyActions:
    """Raw and sanitized actions produced by the globally frozen policy."""

    speeds_mps: FloatArray
    raw_curvatures_inv_m: FloatArray
    sanitized_curvatures_inv_m: FloatArray
    yaw_rates_rad_s: FloatArray
    curvature_valid: BoolArray


def apply_action_policy(
    speeds_mps: ArrayLike,
    raw_curvatures_inv_m: ArrayLike,
    *,
    speed_epsilon_mps: float = SPEED_EPSILON_MPS,
) -> PolicyActions:
    """Zero near-stop curvature while preserving raw values for audit."""
    speeds = np.asarray(speeds_mps, dtype=np.float64)
    curvatures = np.asarray(raw_curvatures_inv_m, dtype=np.float64)
    if speeds.ndim != 1 or speeds.size == 0:
        raise ValueError("speeds_mps must be a non-empty one-dimensional sequence.")
    if curvatures.shape != speeds.shape:
        raise ValueError("raw_curvatures_inv_m must be one-dimensional and aligned with speed.")
    if not np.all(np.isfinite(speeds)):
        raise ValueError("speeds_mps contains non-finite values.")
    if not np.all(np.isfinite(curvatures)):
        raise ValueError("raw_curvatures_inv_m contains non-finite values.")
    if not np.isfinite(speed_epsilon_mps) or speed_epsilon_mps <= 0:
        raise ValueError("speed_epsilon_mps must be positive and finite.")
    valid = np.abs(speeds) >= speed_epsilon_mps
    return PolicyActions(
        speeds_mps=speeds.copy(),
        raw_curvatures_inv_m=curvatures.copy(),
        sanitized_curvatures_inv_m=np.where(valid, curvatures, 0.0),
        yaw_rates_rad_s=speeds * curvatures,
        curvature_valid=valid,
    )


def masked_curvature_mae(
    predicted: PolicyActions, target: PolicyActions
) -> tuple[float | None, int]:
    """Curvature MAE on moving target intervals only."""
    if predicted.speeds_mps.shape != target.speeds_mps.shape:
        raise ValueError("Predicted and target actions must align.")
    count = int(np.count_nonzero(target.curvature_valid))
    if count == 0:
        return None, 0
    error = np.abs(
        predicted.sanitized_curvatures_inv_m[target.curvature_valid]
        - target.raw_curvatures_inv_m[target.curvature_valid]
    )
    return float(np.mean(error)), count


def yaw_rate_mae(predicted: PolicyActions, target: PolicyActions) -> float:
    """Yaw-rate MAE across every interval, including near-stop intervals."""
    if predicted.speeds_mps.shape != target.speeds_mps.shape:
        raise ValueError("Predicted and target actions must align.")
    return float(np.mean(np.abs(predicted.yaw_rates_rad_s - target.yaw_rates_rad_s)))
