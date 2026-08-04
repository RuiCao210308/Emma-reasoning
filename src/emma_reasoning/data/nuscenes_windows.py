"""Deterministic nuScenes ego-motion window extraction.

This module intentionally keeps nuScenes imports optional so the geometry and
metric unit tests can run without the dataset devkit installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class EgoWindow:
    """One observed-plus-future ego-motion window.

    Arrays contain ``obs_len + fut_len`` keyframe states. The prediction anchor
    is ``obs_len - 1``; future targets begin at ``obs_len``.
    """

    sample_id: str
    scene_name: str
    start_index: int
    sample_tokens: tuple[str, ...]
    timestamps_seconds: FloatArray
    positions_world_xy: FloatArray
    headings_world_rad: FloatArray
    image_paths: tuple[str, ...]
    obs_len: int
    fut_len: int

    @property
    def anchor_index(self) -> int:
        return self.obs_len - 1


def quaternion_yaw(rotation_wxyz: Any) -> float:
    """Extract planar yaw from a nuScenes ``[w, x, y, z]`` quaternion."""
    quaternion = np.asarray(rotation_wxyz, dtype=np.float64)
    if quaternion.shape != (4,) or not np.all(np.isfinite(quaternion)):
        raise ValueError("rotation_wxyz must be a finite quaternion with shape (4,).")
    norm = np.linalg.norm(quaternion)
    if norm <= 0:
        raise ValueError("rotation_wxyz must have non-zero norm.")
    w, x, y, z = quaternion / norm
    return float(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))


def _load_scene_states(
    nusc: Any,
    scene: dict[str, Any],
    *,
    camera_channel: str,
) -> dict[str, Any]:
    sample_tokens: list[str] = []
    timestamps: list[float] = []
    positions: list[list[float]] = []
    headings: list[float] = []
    image_paths: list[str] = []

    sample_token = scene["first_sample_token"]
    while sample_token:
        sample = nusc.get("sample", sample_token)
        if camera_channel not in sample["data"]:
            raise KeyError(f"Sample {sample_token} has no channel {camera_channel}.")
        sample_data = nusc.get("sample_data", sample["data"][camera_channel])
        ego_pose = nusc.get("ego_pose", sample_data["ego_pose_token"])

        sample_tokens.append(sample_token)
        timestamps.append(float(sample_data["timestamp"]) * 1e-6)
        positions.append([float(ego_pose["translation"][0]), float(ego_pose["translation"][1])])
        headings.append(quaternion_yaw(ego_pose["rotation"]))
        image_paths.append(str(Path(nusc.dataroot) / sample_data["filename"]))

        sample_token = sample["next"]

    timestamps_array = np.asarray(timestamps, dtype=np.float64)
    if timestamps_array.size > 1 and np.any(np.diff(timestamps_array) <= 0):
        raise ValueError(f"Scene {scene['name']} contains non-increasing camera timestamps.")

    return {
        "sample_tokens": tuple(sample_tokens),
        "timestamps_seconds": timestamps_array,
        "positions_world_xy": np.asarray(positions, dtype=np.float64),
        "headings_world_rad": np.unwrap(np.asarray(headings, dtype=np.float64)),
        "image_paths": tuple(image_paths),
    }


def iter_ego_windows(
    nusc: Any,
    *,
    obs_len: int = 10,
    fut_len: int = 10,
    stride: int = 1,
    camera_channel: str = "CAM_FRONT",
    max_scenes: int | None = None,
    max_windows: int | None = None,
) -> Iterator[EgoWindow]:
    """Yield deterministic sliding windows in nuScenes scene order."""
    if obs_len < 2:
        raise ValueError("obs_len must be at least 2.")
    if fut_len < 1:
        raise ValueError("fut_len must be positive.")
    if stride < 1:
        raise ValueError("stride must be positive.")
    if max_scenes is not None and max_scenes < 1:
        raise ValueError("max_scenes must be positive when provided.")
    if max_windows is not None and max_windows < 1:
        raise ValueError("max_windows must be positive when provided.")

    total_len = obs_len + fut_len
    yielded = 0

    scenes = nusc.scene if max_scenes is None else nusc.scene[:max_scenes]
    for scene in scenes:
        states = _load_scene_states(nusc, scene, camera_channel=camera_channel)
        scene_length = len(states["sample_tokens"])
        if scene_length < total_len:
            continue

        for start_index in range(0, scene_length - total_len + 1, stride):
            stop_index = start_index + total_len
            sample_tokens = states["sample_tokens"][start_index:stop_index]
            sample_id = f"{scene['name']}:{start_index:04d}"
            yield EgoWindow(
                sample_id=sample_id,
                scene_name=scene["name"],
                start_index=start_index,
                sample_tokens=sample_tokens,
                timestamps_seconds=states["timestamps_seconds"][start_index:stop_index].copy(),
                positions_world_xy=states["positions_world_xy"][start_index:stop_index].copy(),
                headings_world_rad=states["headings_world_rad"][start_index:stop_index].copy(),
                image_paths=states["image_paths"][start_index:stop_index],
                obs_len=obs_len,
                fut_len=fut_len,
            )
            yielded += 1
            if max_windows is not None and yielded >= max_windows:
                return
