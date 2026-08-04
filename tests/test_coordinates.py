import numpy as np

from emma_reasoning.trajectory.coordinates import ego_to_world_xy, world_to_ego_xy


def test_world_to_ego_known_rotation() -> None:
    points_world = np.array([[10.0, 11.0], [9.0, 10.0]])
    origin_world = np.array([10.0, 10.0])

    points_ego = world_to_ego_xy(points_world, origin_world, yaw_world=np.pi / 2)

    np.testing.assert_allclose(points_ego, [[1.0, 0.0], [0.0, 1.0]], atol=1e-12)


def test_coordinate_round_trip() -> None:
    points_world = np.array([[3.0, -2.0], [4.5, 8.0], [-1.0, 0.25]])
    origin_world = np.array([2.0, 1.0])
    yaw_world = 0.73

    points_ego = world_to_ego_xy(points_world, origin_world, yaw_world)
    reconstructed = ego_to_world_xy(points_ego, origin_world, yaw_world)

    np.testing.assert_allclose(reconstructed, points_world, atol=1e-12)
