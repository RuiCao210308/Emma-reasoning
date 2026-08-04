"""Estimate speed-curvature actions from timestamped planar ego poses."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class IntervalActions:
    """Piecewise-constant actions fitted between consecutive poses."""

    speeds_mps: FloatArray
    curvatures_inv_m: FloatArray
    dt_seconds: FloatArray
    fit_residual_m: FloatArray


def _as_xy(points: ArrayLike) -> FloatArray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 2 or array.shape[0] < 2:
        raise ValueError(f"positions_xy must have shape (N, 2), N>=2; got {array.shape}.")
    if not np.all(np.isfinite(array)):
        raise ValueError("positions_xy contains non-finite values.")
    return array


def _as_state_vector(values: ArrayLike, *, name: str, length: int) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (length,):
        raise ValueError(f"{name} must have shape ({length},); got {array.shape}.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")
    return array


def estimate_interval_actions(
    positions_xy: ArrayLike,
    headings_rad: ArrayLike,
    timestamps_seconds: ArrayLike,
    *,
    angle_threshold: float = 1e-6,
    distance_threshold: float = 1e-9,
) -> IntervalActions:
    """Fit one constant speed-curvature action per pose interval.

    Each relative SE(2) transform is approximated by a circular arc in the
    starting ego frame. For non-zero heading change, radius is obtained by a
    least-squares fit to

    ``[dx, dy] = radius * [sin(dtheta), 1 - cos(dtheta)]``.

    This formulation exposes the residual when recorded poses are not exactly
    representable by one constant-curvature action. Straight intervals use the
    signed chord length and report any lateral component as fit residual.
    """
    positions = _as_xy(positions_xy)
    count = positions.shape[0]
    headings = np.unwrap(_as_state_vector(headings_rad, name="headings_rad", length=count))
    timestamps = _as_state_vector(
        timestamps_seconds,
        name="timestamps_seconds",
        length=count,
    )
    durations = np.diff(timestamps)
    if np.any(durations <= 0):
        raise ValueError("timestamps_seconds must be strictly increasing.")
    if angle_threshold < 0 or not np.isfinite(angle_threshold):
        raise ValueError("angle_threshold must be finite and non-negative.")
    if distance_threshold < 0 or not np.isfinite(distance_threshold):
        raise ValueError("distance_threshold must be finite and non-negative.")

    speeds = np.empty(count - 1, dtype=np.float64)
    curvatures = np.empty(count - 1, dtype=np.float64)
    residuals = np.empty(count - 1, dtype=np.float64)

    for index in range(count - 1):
        delta_world = positions[index + 1] - positions[index]
        cosine = np.cos(headings[index])
        sine = np.sin(headings[index])
        # World row vector rotated by -heading into the interval-start body frame.
        delta_body = delta_world @ np.array(
            [[cosine, -sine], [sine, cosine]],
            dtype=np.float64,
        )
        delta_heading = headings[index + 1] - headings[index]
        duration = durations[index]

        if abs(delta_heading) <= angle_threshold:
            signed_distance = np.copysign(np.linalg.norm(delta_body), delta_body[0])
            if abs(signed_distance) <= distance_threshold:
                signed_distance = 0.0
            reconstructed = np.array([signed_distance, 0.0], dtype=np.float64)
            speed = signed_distance / duration
            curvature = 0.0
        else:
            arc_basis = np.array(
                [np.sin(delta_heading), 1.0 - np.cos(delta_heading)],
                dtype=np.float64,
            )
            basis_energy = float(arc_basis @ arc_basis)
            radius = float((arc_basis @ delta_body) / basis_energy)
            arc_length = radius * delta_heading

            if abs(arc_length) <= distance_threshold or abs(radius) <= distance_threshold:
                speed = 0.0
                curvature = 0.0
                reconstructed = np.zeros(2, dtype=np.float64)
            else:
                speed = arc_length / duration
                curvature = 1.0 / radius
                reconstructed = radius * arc_basis

        speeds[index] = speed
        curvatures[index] = curvature
        residuals[index] = np.linalg.norm(delta_body - reconstructed)

    return IntervalActions(
        speeds_mps=speeds,
        curvatures_inv_m=curvatures,
        dt_seconds=durations,
        fit_residual_m=residuals,
    )
