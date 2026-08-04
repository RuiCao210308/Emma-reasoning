"""Coordinate transforms for 2D ego-motion evaluation.

The local ego frame follows the common autonomous-driving convention:

- +x: forward along the ego heading at the prediction anchor;
- +y: left of the ego vehicle;
- origin: final observed ego position.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def _as_xy(points: ArrayLike, *, name: str) -> FloatArray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim == 1:
        if array.shape[0] != 2:
            raise ValueError(f"{name} must have shape (2,) or (N, 2); got {array.shape}.")
        array = array[None, :]
    elif array.ndim != 2 or array.shape[1] != 2:
        raise ValueError(f"{name} must have shape (2,) or (N, 2); got {array.shape}.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")
    return array


def _rotation(yaw: float) -> FloatArray:
    if not np.isfinite(yaw):
        raise ValueError("yaw must be finite.")
    cosine = np.cos(yaw)
    sine = np.sin(yaw)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=np.float64)


def world_to_ego_xy(
    points_world: ArrayLike,
    origin_world: ArrayLike,
    yaw_world: float,
) -> FloatArray:
    """Transform world-frame points into the prediction-anchor ego frame.

    Args:
        points_world: One point ``(2,)`` or multiple points ``(N, 2)``.
        origin_world: Final observed ego position in world coordinates.
        yaw_world: Final observed ego yaw in radians.

    Returns:
        Array of shape ``(N, 2)`` in the ego frame.
    """
    points = _as_xy(points_world, name="points_world")
    origin = _as_xy(origin_world, name="origin_world")
    if origin.shape[0] != 1:
        raise ValueError("origin_world must contain exactly one point.")

    translated = points - origin[0]
    # Row vectors are multiplied by R(yaw), equivalent to rotating by -yaw.
    return translated @ _rotation(yaw_world)


def ego_to_world_xy(
    points_ego: ArrayLike,
    origin_world: ArrayLike,
    yaw_world: float,
) -> FloatArray:
    """Transform ego-frame points back into world coordinates."""
    points = _as_xy(points_ego, name="points_ego")
    origin = _as_xy(origin_world, name="origin_world")
    if origin.shape[0] != 1:
        raise ValueError("origin_world must contain exactly one point.")

    return points @ _rotation(yaw_world).T + origin[0]
