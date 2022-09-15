import numpy as np
from mathutils import Vector

import airo_blender_toolkit as abt


def test_rotate_point_2D():
    """Test correctness"""
    point = Vector([1, 0])
    point_rotated = abt.rotate_point_2D(point, 90)
    expected_result = Vector([0, 1])
    assert np.allclose(point_rotated, expected_result, atol=1e-07)


def test_rotate_point_2D_alternative_inputs():
    """Test whether function handles numpy, list and tuple inputs."""
    points = [np.array([1, 0]), [1, 0], (1, 0)]
    for point in points:
        point_rotated = abt.rotate_point_2D(point, 90)
        expected_result = Vector([0, 1])
        assert np.allclose(point_rotated, expected_result, atol=1e-07)


def test_rotate_point_3D():
    """Test correctness"""
    point = Vector([1, 0, 0])
    axis = Vector([0, 0, 1])
    expected_result = Vector([0, 1, 0])
    point_rotated = abt.rotate_point_3D(point, 90, axis=axis)
    assert np.allclose(point_rotated, expected_result, atol=1e-07)


def test_rotate_point_3D_numpy():
    """Test whether function handles numpy inputs."""
    point = np.array([1, 0, 0])
    axis = np.array([0, 0, 1])
    expected_result = np.array([0, 1, 0])
    point_rotated = abt.rotate_point_3D(point, 90, axis=axis)
    assert np.allclose(point_rotated, expected_result, atol=1e-07)
