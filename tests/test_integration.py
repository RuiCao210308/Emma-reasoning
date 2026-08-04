import numpy as np

from emma_reasoning.trajectory.integration import integrate_speed_curvature


def test_straight_motion_uses_explicit_half_second_dt() -> None:
    rollout = integrate_speed_curvature(
        speeds_mps=[2.0, 2.0, 2.0],
        curvatures_inv_m=[0.0, 0.0, 0.0],
        dt=0.5,
    )

    np.testing.assert_allclose(
        rollout.positions,
        [[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]],
        atol=1e-12,
    )
    np.testing.assert_allclose(rollout.headings, 0.0, atol=1e-12)


def test_constant_curvature_exact_quarter_circle() -> None:
    rollout = integrate_speed_curvature(
        speeds_mps=[1.0],
        curvatures_inv_m=[1.0],
        dt=np.pi / 2,
    )

    np.testing.assert_allclose(rollout.positions, [[1.0, 1.0]], atol=1e-12)
    np.testing.assert_allclose(rollout.headings, [np.pi / 2], atol=1e-12)


def test_rollout_starts_from_final_observed_anchor_not_future_target() -> None:
    rollout = integrate_speed_curvature(
        speeds_mps=[4.0],
        curvatures_inv_m=[0.0],
        dt=0.5,
        initial_position_xy=[7.0, -2.0],
    )

    np.testing.assert_allclose(rollout.positions, [[9.0, -2.0]], atol=1e-12)
