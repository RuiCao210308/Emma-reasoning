import numpy as np

from emma_reasoning.baselines import (
    FROZEN_BASELINES,
    ObservedMotion,
    PredictionSchedule,
    build_baseline_inputs,
)
from emma_reasoning.data.nuscenes_windows import EgoWindow
from emma_reasoning.trajectory import apply_action_policy


def _observed() -> ObservedMotion:
    return ObservedMotion(
        positions_xy=np.zeros((4, 2)),
        headings_rad=np.zeros(4),
        timestamps_seconds=np.arange(4, dtype=float),
        history_actions=apply_action_policy([1.0, 3.0, 2.0], [0.1, 0.2, -0.4]),
    )


def test_frozen_baselines_emit_expected_ten_step_chunks() -> None:
    schedule = PredictionSchedule(10, np.full(10, 0.5))
    outputs = {name: method(_observed(), schedule) for name, method in FROZEN_BASELINES.items()}
    assert all(actions.speeds_mps.shape == (10,) for actions in outputs.values())
    np.testing.assert_allclose(outputs["stationary"].speeds_mps, 0.0)
    np.testing.assert_allclose(outputs["last_speed_straight"].speeds_mps, 2.0)
    np.testing.assert_allclose(outputs["last_speed_straight"].sanitized_curvatures_inv_m, 0.0)
    np.testing.assert_allclose(outputs["constant_last"].sanitized_curvatures_inv_m, -0.4)
    # Median speed=2; yaw rates=[0.1, 0.6, -0.8], median=0.1, so curvature=0.05.
    np.testing.assert_allclose(outputs["median3"].raw_curvatures_inv_m, 0.05)


def test_predictions_are_identical_when_future_pose_and_heading_change() -> None:
    positions = np.zeros((20, 2))
    headings = np.zeros(20)
    modified_positions = positions.copy()
    modified_headings = headings.copy()
    modified_positions[10:] = 1e9
    modified_headings[10:] = -1e9
    common = {
        "sample_id": "leak-test",
        "scene_name": "scene",
        "start_index": 0,
        "sample_tokens": tuple(str(index) for index in range(20)),
        "timestamps_seconds": np.arange(20, dtype=float) * 0.5,
        "image_paths": tuple("unused" for _ in range(20)),
        "obs_len": 10,
        "fut_len": 10,
    }
    original = EgoWindow(positions_world_xy=positions, headings_world_rad=headings, **common)
    modified = EgoWindow(
        positions_world_xy=modified_positions,
        headings_world_rad=modified_headings,
        **common,
    )
    observed_a, schedule_a = build_baseline_inputs(original)
    observed_b, schedule_b = build_baseline_inputs(modified)
    for method in FROZEN_BASELINES.values():
        first = method(observed_a, schedule_a)
        second = method(observed_b, schedule_b)
        np.testing.assert_array_equal(first.speeds_mps, second.speeds_mps)
        np.testing.assert_array_equal(first.raw_curvatures_inv_m, second.raw_curvatures_inv_m)
        np.testing.assert_array_equal(
            first.sanitized_curvatures_inv_m, second.sanitized_curvatures_inv_m
        )
