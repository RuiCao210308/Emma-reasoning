import numpy as np
import pytest

from emma_reasoning.trajectory.action_policy import (
    apply_action_policy,
    masked_curvature_mae,
    yaw_rate_mae,
)


def test_fixed_policy_masks_near_stop_and_preserves_moving_curvature() -> None:
    actions = apply_action_policy([0.0, 0.099, 0.1, -2.0], [99.0, -7.0, 3.0, -4.0])
    np.testing.assert_array_equal(actions.curvature_valid, [False, False, True, True])
    np.testing.assert_allclose(actions.raw_curvatures_inv_m, [99.0, -7.0, 3.0, -4.0])
    np.testing.assert_allclose(actions.sanitized_curvatures_inv_m, [0.0, 0.0, 3.0, -4.0])
    np.testing.assert_allclose(actions.yaw_rates_rad_s, [0.0, -0.693, 0.3, 8.0])


@pytest.mark.parametrize(
    ("speeds", "curvatures"),
    [([np.nan], [0.0]), ([np.inf], [0.0]), ([1.0], [np.nan]), ([1.0], [np.inf])],
)
def test_action_policy_rejects_non_finite_input(
    speeds: list[float], curvatures: list[float]
) -> None:
    with pytest.raises(ValueError, match="non-finite"):
        apply_action_policy(speeds, curvatures)


def test_action_metrics_mask_curvature_but_score_all_yaw_rates() -> None:
    target = apply_action_policy([0.0, 2.0], [100.0, 0.5])
    predicted = apply_action_policy([1.0, 2.0], [9.0, 0.25])
    curvature_mae, valid_count = masked_curvature_mae(predicted, target)
    assert valid_count == 1
    assert curvature_mae == pytest.approx(0.25)
    assert yaw_rate_mae(predicted, target) == pytest.approx(4.75)
