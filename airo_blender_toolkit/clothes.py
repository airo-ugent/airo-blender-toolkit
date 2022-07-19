import os

import numpy as np

import airo_blender_toolkit as abt
from airo_blender_toolkit.keypointed_object import KeypointedObject

os.environ["INSIDE_OF_THE_INTERNAL_BLENDER_PYTHON_ENVIRONMENT"] = "1"


class Towel(KeypointedObject):
    keypoint_ids = {"corner": [0, 1, 2, 3]}

    def __init__(self, length, width):
        self.width = width
        self.length = length

        mesh = self._create_mesh()
        blender_obj = abt.make_object(name="Towel", mesh=mesh)
        super().__init__(blender_obj, Towel.keypoint_ids)

    def _create_mesh(self):
        width, length = float(self.width), float(self.length)

        vertices = [
            np.array([-width / 2, -length / 2, 0.0]),
            np.array([-width / 2, length / 2, 0.0]),
            np.array([width / 2, length / 2, 0.0]),
            np.array([width / 2, -length / 2, 0.0]),
        ]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        faces = [(0, 1, 2, 3)]

        return vertices, edges, faces


class PolygonalShirt(KeypointedObject):
    def __init__(
        self,
        bottom_width=0.65,
        neck_width=0.32,
        neck_depth=0.08,
        shoulder_width=0.62,
        shoulder_height=0.9,
        sleeve_width_start=0.28,
        sleeve_width_end=0.18,
        sleeve_length=0.76,
        sleeve_angle=-3,
        scale=0.635,
    ):
        self.bottom_width = bottom_width
        self.neck_width = neck_width
        self.neck_depth = neck_depth
        self.shoulder_width = shoulder_width
        self.shoulder_height = shoulder_height
        self.sleeve_width_start = sleeve_width_start
        self.sleeve_width_end = sleeve_width_end
        self.sleeve_length = sleeve_length
        self.sleeve_angle = sleeve_angle
        self.scale = scale

        self.blender_object = self.make_shirt_object()

        keypoint_ids = {
            "bottom_right": [0],
            "armpit_right": [1],
            "sleeve_bottom_right": [2],
            "sleeve_top_right": [3],
            "shoulder_right": [4],
            "neck_right": [5],
            "neck_middle": [6],
            "neck_left": [7],
            "shoulder_left": [8],
            "sleeve_top_left": [9],
            "sleeve_bottom_left": [10],
            "armpit_left": [11],
            "bottom_left": [12],
        }

        super().__init__(self.blender_object, keypoint_ids)

    def make_shirt_object(self):
        # First we make the right half of the shirt
        bottom_side = np.array([self.bottom_width / 2.0, 0.0, 0.0])

        neck_offset = self.neck_width / 2.0
        neck_top = np.array([neck_offset, 1.0, 0.0])
        neck_bottom = np.array([0, 1.0 - self.neck_depth, 0.0])

        self.shoulder_width / 2.0 - neck_offset
        shoulder = np.array([self.shoulder_width / 2.0, self.shoulder_height, 0.0])

        A = np.abs(self.bottom_width - self.shoulder_width) / 2.0
        C = self.sleeve_width_start
        B = np.sqrt(C ** 2 - A ** 2)
        armpit_height = self.shoulder_height - B
        armpit = np.array([self.bottom_width / 2.0, armpit_height, 0.0])

        sleeve_middle = (shoulder + armpit) / 2.0
        sleeve_end = sleeve_middle + np.array([self.sleeve_length, 0.0, 0.0])
        sleeve_end_top = sleeve_end + np.array([0.0, self.sleeve_width_end / 2.0, 0.0])
        sleeve_end_bottom = sleeve_end - np.array([0.0, self.sleeve_width_end / 2.0, 0.0])

        a = np.deg2rad(self.sleeve_angle)
        up = np.array([0.0, 0.0, 1.0])
        sleeve_end_top = abt.rotate_point(sleeve_end_top, sleeve_middle, up, -a)
        sleeve_end_bottom = abt.rotate_point(sleeve_end_bottom, sleeve_middle, up, -a)

        vertices = [
            bottom_side,
            armpit,
            sleeve_end_bottom,
            sleeve_end_top,
            shoulder,
            neck_top,
            neck_bottom,
        ]

        for vertex in reversed(vertices[0:-1]):
            mirrored_vertex = vertex.copy()
            mirrored_vertex[0] *= -1
            vertices.append(mirrored_vertex)

        vertices = np.array(vertices)
        vertices[:, 1] -= 0.5  # move origin to center of shirt
        vertices *= self.scale

        faces = [list(range(len(vertices)))]
        mesh = vertices, [], faces
        blender_object = abt.make_object("Shirt", mesh)
        return blender_object


if __name__ == "__main__":
    PolygonalShirt()
    Towel()
