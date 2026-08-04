import numpy as np

from emma_reasoning.trajectory.integration import integrate_speed_curvature
from emma_reasoning.trajectory.kinematics import estimate_interval_actions


def test_exact_circular_arcs_recover_original_actions() -> None:
    speeds = np.array([4.0, 3.0, 5.0])
    curvatures = np.array([0.20, -0.10, 0.05])
    durations = np.array([0.5, 0.6, 0.4])
    rollout = integrate_speed_curvature(speeds, curvatures, dt=durations)

    positions = np.vstack([[0.0, 0.0], rollout.positions])
    headings = np.concatenate([[0.0], rollout.headings])
    timestamps = np.concatenate([[0.0], np.cumsum(durations)])

    estimated = estimate_interval_actions(positions, headings, timestamps)

    np.testing.assert_allclose(estimated.speeds_mps, speeds, atol=1e-10)
    np.testing.assert_allclose(estimated.curvatures_inv_m, curvatures, atol=1e-10)
    np.testing.assert_allclose(estimated.dt_seconds, durations, atol=1e-12)
    np.testing.assert_allclose(estimated.fit_residual_m, 0.0, atol=1e-10)


def test_straight_motion_with_irregular_timestamps() -> None:
    positions = np.array([[0.0, 0.0], [1.0, 0.0], [3.0, 0.0]])
    headings = np.zeros(3)
    timestamps = np.array([0.0, 0.5, 1.5])

    estimated = estimate_interval_actions(positions, headings, timestamps)

    np.testing.assert_allclose(estimated.speeds_mps, [2.0, 2.0], atol=1e-12)
    np.testing.assert_allclose(estimated.curvatures_inv_m, 0.0, atol=1e-12)
    np.testing.assert_allclose(estimated.fit_residual_m, 0.0, atol=1e-12)


def test_non_circular_interval_exposes_fit_residual() -> None:
    positions = np.array([[0.0, 0.0], [1.0, 0.5]])
    headings = np.array([0.0, 0.0])
    timestamps = np.array([0.0, 0.5])

    estimated = estimate_interval_actions(positions, headings, timestamps)

    assert estimated.fit_residual_m[0] > 0.0
