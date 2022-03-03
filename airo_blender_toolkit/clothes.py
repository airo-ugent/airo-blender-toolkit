import os

import numpy as np

import airo_blender_toolkit as abt

os.environ["INSIDE_OF_THE_INTERNAL_BLENDER_PYTHON_ENVIRONMENT"] = "1"


class PolygonalShirt:
    def __init__(
        self,
        bottom_width=0.65,
        neck_width=0.32,
        neck_depth=0.08,
        shoulder_width=0.62,
        shoulder_angle=18,
        sleeve_width_start=0.28,
        sleeve_width_end=0.18,
        sleeve_length=0.76,
        sleeve_angle=-3,
        scale=0.635,
        triangle_density=10000.0,
    ):
        self.bottom_width = bottom_width
        self.neck_width = neck_width
        self.neck_depth = neck_depth
        self.shoulder_width = shoulder_width
        self.shoulder_angle = shoulder_angle
        self.sleeve_width_start = sleeve_width_start
        self.sleeve_width_end = sleeve_width_end
        self.sleeve_length = sleeve_length
        self.sleeve_angle = sleeve_angle
        self.scale = scale

        self.object = self.make_object()

    def make_object(self):
        # First we make the right half of the shirt
        bottom_middle = np.array([0.0, 0.0, 0.0])
        bottom_side = np.array([self.bottom_width / 2.0, 0.0, 0.0])

        neck_offset = self.neck_width / 2.0
        neck_top = np.array([neck_offset, 1.0, 0.0])
        neck_bottom = np.array([0, 1.0 - self.neck_depth, 0.0])

        shoulder_offset = self.shoulder_width / 2.0 - neck_offset
        shoulder_height = 1.0 - np.tan(np.deg2rad(self.shoulder_angle)) * shoulder_offset
        shoulder = np.array([self.shoulder_width / 2.0, shoulder_height, 0.0])

        A = np.abs(self.bottom_width - self.shoulder_width) / 2.0
        C = self.sleeve_width_start
        B = np.sqrt(C ** 2 - A ** 2)
        armpit_height = shoulder_height - B
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
            bottom_middle,
            bottom_side,
            armpit,
            sleeve_end_bottom,
            sleeve_end_top,
            shoulder,
            neck_top,
            neck_bottom,
        ]

        for vertex in reversed(vertices[1:-1]):
            mirrored_vertex = vertex.copy()
            mirrored_vertex[0] *= -1
            vertices.append(mirrored_vertex)

        vertices = np.array(vertices)
        vertices *= self.scale

        faces = [list(range(len(vertices)))]
        mesh = vertices, [], faces
        abt.make_object("Shirt", mesh)
        return object


if __name__ == "__main__":
    PolygonalShirt()
