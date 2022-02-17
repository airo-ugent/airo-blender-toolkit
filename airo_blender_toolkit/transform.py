import math
import os

import bpy
from mathutils import Matrix

os.environ["INSIDE_OF_THE_INTERNAL_BLENDER_PYTHON_ENVIRONMENT"] = "1"
import blenderproc as bproc  # noqa: E402

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
    empty.matrix_world @= matrix
    empty.empty_display_size = scale

    for axis, color in zip(axes, blender_rgb):
        material = cylinders[axis].new_material("Material")
        material.set_principled_shader_value("Base Color", color)
        material.blender_obj.diffuse_color = color
