"""Dataset-level diagnostics for trusted reconstruction audits."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike


def distribution_summary(values: ArrayLike, *, name: str) -> dict[str, float]:
    """Summarize a non-empty finite scalar distribution."""
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional sequence.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p95": float(np.quantile(array, 0.95)),
        "max": float(np.max(array)),
    }


def signed_range_summary(values: ArrayLike, *, name: str) -> dict[str, float]:
    """Report signed range and absolute-value tail statistics."""
    array = np.asarray(values, dtype=np.float64)
    distribution_summary(array, name=name)
    absolute = np.abs(array)
    return {
        "min": float(np.min(array)),
        "max": float(np.max(array)),
        "median": float(np.median(array)),
        "p95_abs": float(np.quantile(absolute, 0.95)),
        "max_abs": float(np.max(absolute)),
    }


def displacement_error_by_step(
    predicted_trajectories: Sequence[ArrayLike],
    target_trajectories: Sequence[ArrayLike],
) -> dict[str, Any]:
    """Summarize aligned displacement errors separately at each future step."""
    if len(predicted_trajectories) != len(target_trajectories) or not predicted_trajectories:
        raise ValueError("Predicted and target trajectory collections must be non-empty and match.")

    error_rows: list[np.ndarray] = []
    expected_shape: tuple[int, int] | None = None
    for predicted_values, target_values in zip(
        predicted_trajectories, target_trajectories, strict=True
    ):
        predicted = np.asarray(predicted_values, dtype=np.float64)
        target = np.asarray(target_values, dtype=np.float64)
        if predicted.ndim != 2 or predicted.shape[1] != 2 or predicted.shape != target.shape:
            raise ValueError("Every predicted and target trajectory must share shape (T, 2).")
        if expected_shape is None:
            expected_shape = predicted.shape
        elif predicted.shape != expected_shape:
            raise ValueError("All trajectory windows must have the same shape.")
        if not np.all(np.isfinite(predicted)) or not np.all(np.isfinite(target)):
            raise ValueError("Trajectory collections contain non-finite values.")
        error_rows.append(np.linalg.norm(predicted - target, axis=1))

    errors = np.stack(error_rows)
    per_step = [
        {"step": index + 1, **distribution_summary(errors[:, index], name="step errors")}
        for index in range(errors.shape[1])
    ]
    mean_errors = np.mean(errors, axis=0)
    return {
        "per_step": per_step,
        "mean_error_non_decreasing": bool(np.all(np.diff(mean_errors) >= -1e-12)),
        "final_to_first_mean_ratio": float(mean_errors[-1] / mean_errors[0])
        if mean_errors[0] > 0
        else None,
    }


def worst_reconstruction_cases(
    records: Sequence[dict[str, Any]], *, limit: int = 10
) -> list[dict[str, Any]]:
    """Return the largest actual-timestamp ADE windows with audit context."""
    if limit < 1:
        raise ValueError("limit must be positive.")
    ranked = sorted(
        records,
        key=lambda record: float(record["actual_timestamp_metrics"]["ade_m"]),
        reverse=True,
    )[:limit]
    return [
        {
            "sample_id": record["sample_id"],
            "scene": record["scene_name"],
            "actual_ade_m": float(record["actual_timestamp_metrics"]["ade_m"]),
            "actual_fde_m": float(record["actual_timestamp_metrics"]["fde_m"]),
            "nominal_ade_m": float(record["nominal_dt_metrics"]["ade_m"]),
            "nominal_fde_m": float(record["nominal_dt_metrics"]["fde_m"]),
            "max_interval_arc_fit_residual_m": float(
                np.max(record["interval_arc_fit_residual_m"])
            ),
            "max_dt_abs_deviation_from_nominal_seconds": float(
                np.max(record["dt_abs_deviation_from_nominal_seconds"])
            ),
        }
        for record in ranked
    ]


def action_diagnostics(
    speeds_mps: ArrayLike,
    curvatures_inv_m: ArrayLike,
    dt_seconds: ArrayLike,
    *,
    nominal_dt: float,
    moving_speed_threshold_mps: float = 0.01,
    extreme_curvature_inv_m: float = 1.0,
    anomalous_dt_deviation_seconds: float = 0.15,
) -> dict[str, Any]:
    """Separate near-stop parameter singularities from moving action outliers."""
    speeds = np.asarray(speeds_mps, dtype=np.float64)
    curvatures = np.asarray(curvatures_inv_m, dtype=np.float64)
    durations = np.asarray(dt_seconds, dtype=np.float64)
    if speeds.ndim != 1 or speeds.size == 0 or speeds.shape != curvatures.shape:
        raise ValueError("Speed and curvature sequences must be non-empty and aligned.")
    if durations.shape != speeds.shape:
        raise ValueError("dt_seconds must align with speed and curvature sequences.")
    if not np.all(np.isfinite(speeds)) or not np.all(np.isfinite(curvatures)):
        raise ValueError("Actions contain non-finite values.")
    if not np.all(np.isfinite(durations)) or np.any(durations <= 0):
        raise ValueError("dt_seconds must be positive and finite.")
    if not np.isfinite(nominal_dt) or nominal_dt <= 0:
        raise ValueError("nominal_dt must be positive and finite.")

    near_stop = np.abs(speeds) < moving_speed_threshold_mps
    extreme_curvature = np.abs(curvatures) > extreme_curvature_inv_m
    dt_deviation = np.abs(durations - nominal_dt)
    return {
        "intervals": int(speeds.size),
        "speed_mps": signed_range_summary(speeds, name="speeds_mps"),
        "curvature_inv_m": signed_range_summary(curvatures, name="curvatures_inv_m"),
        "dt_seconds": signed_range_summary(durations, name="dt_seconds"),
        "negative_speed_interval_count": int(np.count_nonzero(speeds < 0)),
        "speed_below_minus_0_1_mps_count": int(np.count_nonzero(speeds < -0.1)),
        "near_stop_interval_count": int(np.count_nonzero(near_stop)),
        "near_stop_extreme_curvature_count": int(
            np.count_nonzero(near_stop & extreme_curvature)
        ),
        "moving_extreme_curvature_count": int(
            np.count_nonzero(~near_stop & extreme_curvature)
        ),
        "anomalous_dt_interval_count": int(
            np.count_nonzero(dt_deviation > anomalous_dt_deviation_seconds)
        ),
        "thresholds": {
            "moving_speed_mps": moving_speed_threshold_mps,
            "extreme_curvature_inv_m": extreme_curvature_inv_m,
            "anomalous_dt_deviation_seconds": anomalous_dt_deviation_seconds,
        },
    }
