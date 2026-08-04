"""Dataset access and deterministic window construction."""

from .nuscenes_windows import EgoWindow, iter_ego_windows

__all__ = ["EgoWindow", "iter_ego_windows"]
