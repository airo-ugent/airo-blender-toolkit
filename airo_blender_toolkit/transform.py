import math
import os

import bpy
import numpy as np
from mathutils import Matrix
from scipy.spatial.transform import Rotation

os.environ["INSIDE_OF_THE_INTERNAL_BLENDER_PYTHON_ENVIRONMENT"] = "1"
import blenderproc as bproc  # noqa: E402


class Frame(np.ndarray):
    """4x4 matrix that represents a frame/pose/homogeneous transfrom.
    See: https://numpy.org/doc/stable/user/basics.subclassing.html
    """

    def __new__(cls, matrix):
        obj = np.asarray(matrix).view(cls)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

    @classmethod
    def from_vectors(cls, x_column, y_column, z_column, translation):
        matrix = np.identity(4)
        matrix[0:3, 0] = x_column
        matrix[0:3, 1] = y_column
        matrix[0:3, 2] = z_column
        matrix[0:3, 3] = translation
        return cls(matrix)

    @classmethod
    def from_orientation_and_position(cls, orientation, position):
        matrix = np.identity(4)
        matrix[0:3, 0:3] = orientation
        matrix[0:3, 3] = position
        return cls(matrix)

    @classmethod
    def identity(cls):
        return cls(np.identity(4))

    @property
    def position(self):
        return self[0:3, 3]

    @property
    def orientation(self):
        return self[0:3, 0:3]


def rotate_point(point, rotation_origin, rotation_axis, angle):
    unit_axis = rotation_axis / np.linalg.norm(rotation_axis)
    rotation = Rotation.from_rotvec(angle * unit_axis)
    point_new = rotation.as_matrix() @ (point - rotation_origin) + rotation_origin
    return point_new


def project_point_on_line(point, point_on_line, line_direction):
    unit_direction = line_direction / np.linalg.norm(line_direction)
    point_on_line_to_point = point - point_on_line
    projection = point_on_line + np.dot(point_on_line_to_point, unit_direction) * unit_direction
    return projection


blender_rgb = [
    [0.930111, 0.036889, 0.084376, 1.000000],
    [0.205079, 0.527115, 0.006049, 1.000000],
    [0.028426, 0.226966, 0.760525, 1.000000],
]


def shorten_cylinder(cylinder, radius):
    for v in cylinder.data.vertices:
        if v.co.z < -radius:
            v.co.z = -radius


def visualize_transform(matrix: Matrix, scale: float = 1.0):
    """Creates a blender object with 3 colored axes to visualize a 4x4 matrix that represent a 3D pose/transform.

    :param matrix: the matrix that will be visualized
    :type matrix: Matrix of size 4x4
    :param scale: length in meters of an axis, defaults to 1.0
    :type scale: float, optional
    """
    depth = 2.0 * scale
    radius = 0.02 * depth

    axes = ["X", "Y", "Z"]
    cylinders = {}

    for axis in axes:
        cylinder = bproc.object.create_primitive("CYLINDER", radius=radius, depth=depth)
        cylinder.blender_obj.name = axis
        cylinders[axis] = cylinder
        shorten_cylinder(cylinder.blender_obj, radius)

    cylinders["X"].blender_obj.matrix_world @= Matrix.Rotation(math.pi / 2, 4, "Y")
    cylinders["Y"].blender_obj.matrix_world @= Matrix.Rotation(-math.pi / 2, 4, "X")

    # Create Empty object to serve as parent of the axes
    bpy.ops.object.empty_add(type="ARROWS", scale=(scale, scale, scale))
    empty = bpy.context.object
    for cylinder in cylinders.values():
        cylinder.persist_transformation_into_mesh()
        cylinder.blender_obj.parent = empty
    empty.matrix_world @= Matrix(matrix)
    empty.empty_display_size = scale

    for axis, color in zip(axes, blender_rgb):
        material = cylinders[axis].new_material("Material")
        material.set_principled_shader_value("Base Color", color)
        material.blender_obj.diffuse_color = color

    return empty
