import numpy as np
import pytest

from emma_reasoning.evaluation.metrics import (
    action_mae,
    evaluate_trajectory,
    horizon_index,
)


def test_horizon_index_for_nuscenes_keyframes() -> None:
    assert horizon_index(1.0, dt=0.5, length=10) == 1
    assert horizon_index(2.0, dt=0.5, length=10) == 3
    assert horizon_index(3.0, dt=0.5, length=10) == 5
    assert horizon_index(5.0, dt=0.5, length=10) == 9


def test_unaligned_horizon_is_rejected() -> None:
    with pytest.raises(ValueError, match="not aligned"):
        horizon_index(1.2, dt=0.5, length=10)


def test_trajectory_metrics_use_same_horizon_for_ade_and_fde() -> None:
    target = np.zeros((4, 2), dtype=np.float64)
    predicted = np.array(
        [[1.0, 0.0], [2.0, 0.0], [100.0, 0.0], [100.0, 0.0]],
        dtype=np.float64,
    )

    metrics = evaluate_trajectory(predicted, target, horizon_seconds=1.0, dt=0.5)

    assert metrics.ade_m == pytest.approx(1.5)
    assert metrics.fde_m == pytest.approx(2.0)
    assert metrics.longitudinal_mae_m == pytest.approx(1.5)
    assert metrics.lateral_mae_m == pytest.approx(0.0)


def test_action_mae_has_explicit_units_outside_function() -> None:
    assert action_mae([1.0, 2.0], [2.0, 4.0], name="speed_mps") == pytest.approx(1.5)
