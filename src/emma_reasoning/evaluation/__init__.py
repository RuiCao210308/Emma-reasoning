"""Trajectory and action evaluation utilities."""

from .audit import (
    action_diagnostics,
    displacement_error_by_step,
    distribution_summary,
    signed_range_summary,
    worst_reconstruction_cases,
)
from .metrics import (
    TrajectoryMetrics,
    action_mae,
    displacement_errors,
    evaluate_trajectory,
    horizon_index,
)

__all__ = [
    "TrajectoryMetrics",
    "action_diagnostics",
    "action_mae",
    "displacement_error_by_step",
    "displacement_errors",
    "distribution_summary",
    "evaluate_trajectory",
    "horizon_index",
    "signed_range_summary",
    "worst_reconstruction_cases",
]
