from pathlib import Path

import numpy as np
import pytest

from emma_reasoning.data.nuscenes_windows import iter_ego_windows, quaternion_yaw


class FakeNuScenes:
    def __init__(self) -> None:
        self.dataroot = "/tmp/fake-nuscenes"
        self.scene = [{"name": "scene-test", "first_sample_token": "s0"}]
        self._records = {}

        for index in range(5):
            sample_token = f"s{index}"
            next_token = f"s{index + 1}" if index < 4 else ""
            sample_data_token = f"sd{index}"
            pose_token = f"pose{index}"
            self._records[("sample", sample_token)] = {
                "data": {"CAM_FRONT": sample_data_token},
                "next": next_token,
            }
            self._records[("sample_data", sample_data_token)] = {
                "timestamp": index * 500_000,
                "ego_pose_token": pose_token,
                "filename": f"samples/CAM_FRONT/{index}.jpg",
            }
            self._records[("ego_pose", pose_token)] = {
                "translation": [float(index), 0.0, 0.0],
                "rotation": [1.0, 0.0, 0.0, 0.0],
            }

    def get(self, table_name: str, token: str) -> dict:
        return self._records[(table_name, token)]


def test_quaternion_yaw_for_quarter_turn() -> None:
    half_angle = np.pi / 4
    quaternion = [np.cos(half_angle), 0.0, 0.0, np.sin(half_angle)]

    assert quaternion_yaw(quaternion) == pytest.approx(np.pi / 2)


def test_window_anchor_and_future_alignment() -> None:
    windows = list(
        iter_ego_windows(
            FakeNuScenes(),
            obs_len=2,
            fut_len=2,
            stride=1,
        )
    )

    assert len(windows) == 2
    first = windows[0]
    assert first.sample_id == "scene-test:0000"
    assert first.anchor_index == 1
    assert first.sample_tokens == ("s0", "s1", "s2", "s3")
    np.testing.assert_allclose(first.timestamps_seconds, [0.0, 0.5, 1.0, 1.5])
    np.testing.assert_allclose(first.positions_world_xy[:, 0], [0.0, 1.0, 2.0, 3.0])
    assert first.image_paths[0] == str(
        Path("/tmp/fake-nuscenes") / "samples/CAM_FRONT/0.jpg"
    )
