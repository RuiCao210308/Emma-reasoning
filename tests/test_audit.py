import numpy as np
import pytest

from emma_reasoning.evaluation.audit import (
    action_diagnostics,
    displacement_error_by_step,
    distribution_summary,
    worst_reconstruction_cases,
)


def test_distribution_summary_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        distribution_summary([0.0, np.nan], name="test values")


def test_displacement_error_by_step_preserves_future_index_alignment() -> None:
    diagnostics = displacement_error_by_step(
        [np.array([[1.0, 0.0], [3.0, 0.0]])],
        [np.zeros((2, 2))],
    )

    assert diagnostics["per_step"][0]["step"] == 1
    assert diagnostics["per_step"][0]["mean"] == pytest.approx(1.0)
    assert diagnostics["per_step"][1]["step"] == 2
    assert diagnostics["per_step"][1]["mean"] == pytest.approx(3.0)
    assert diagnostics["mean_error_non_decreasing"] is True


def test_action_diagnostics_separates_near_stop_curvature_singularity() -> None:
    diagnostics = action_diagnostics(
        speeds_mps=[0.001, 2.0, -0.2],
        curvatures_inv_m=[10.0, 0.1, 2.0],
        dt_seconds=[0.5, 0.6, 0.5],
        nominal_dt=0.5,
    )

    assert diagnostics["negative_speed_interval_count"] == 1
    assert diagnostics["speed_below_minus_0_1_mps_count"] == 1
    assert diagnostics["near_stop_extreme_curvature_count"] == 1
    assert diagnostics["moving_extreme_curvature_count"] == 1
    assert diagnostics["anomalous_dt_interval_count"] == 0


def test_worst_cases_rank_actual_ade_and_include_required_context() -> None:
    def record(sample_id: str, ade: float) -> dict:
        return {
            "sample_id": sample_id,
            "scene_name": "scene-test",
            "actual_timestamp_metrics": {"ade_m": ade, "fde_m": ade + 1.0},
            "nominal_dt_metrics": {"ade_m": ade + 2.0, "fde_m": ade + 3.0},
            "interval_arc_fit_residual_m": [0.01, 0.02],
            "dt_abs_deviation_from_nominal_seconds": [0.0, 0.1],
        }

    worst = worst_reconstruction_cases([record("low", 0.1), record("high", 0.5)], limit=1)

    assert worst == [
        {
            "sample_id": "high",
            "scene": "scene-test",
            "actual_ade_m": 0.5,
            "actual_fde_m": 1.5,
            "nominal_ade_m": 2.5,
            "nominal_fde_m": 3.5,
            "max_interval_arc_fit_residual_m": 0.02,
            "max_dt_abs_deviation_from_nominal_seconds": 0.1,
        }
    ]
