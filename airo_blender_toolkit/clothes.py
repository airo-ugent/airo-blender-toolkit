import os

import numpy as np

import airo_blender_toolkit as abt

os.environ["INSIDE_OF_THE_INTERNAL_BLENDER_PYTHON_ENVIRONMENT"] = "1"

import blenderproc as bproc  # noqa: E402


class PolygonalShirt:
    def __init__(
        self,
        bottom_width=0.6,
        neck_width=0.2,
        neck_depth=0.1,
        shoulder_width=0.5,
        shoulder_angle=20,
        sleeve_width_start=0.3,
        sleeve_width_end=0.15,
        sleeve_length=0.5,
        sleeve_angle=10,
    ):

        # First we make the right half of the shirt

        bottom_middle = np.array([0.0, 0.0, 0.0])
        bottom_side = np.array([bottom_width / 2.0, 0.0, 0.0])

        neck_offset = neck_width / 2.0
        neck_top = np.array([neck_offset, 1.0, 0.0])
        neck_bottom = np.array([0, 1.0 - neck_depth, 0.0])

        shoulder_offset = shoulder_width / 2.0 - neck_offset
        shoulder_height = 1.0 - np.tan(np.deg2rad(shoulder_angle)) * shoulder_offset
        shoulder = np.array([shoulder_width / 2.0, shoulder_height, 0.0])

        A = np.abs(bottom_width - shoulder_width) / 2.0
        C = sleeve_width_start
        B = np.sqrt(C ** 2 - A ** 2)
        armpit_height = shoulder_height - B
        armpit = np.array([bottom_width / 2.0, armpit_height, 0.0])

        sleeve_middle = (shoulder + armpit) / 2.0
        sleeve_end = sleeve_middle + np.array([sleeve_length, 0.0, 0.0])
        sleeve_end_top = sleeve_end + np.array([0.0, sleeve_width_end / 2.0, 0.0])
        sleeve_end_bottom = sleeve_end - np.array([0.0, sleeve_width_end / 2.0, 0.0])

        a = np.deg2rad(sleeve_angle)
        up = np.array([0.0, 0.0, 1.0])
        sleeve_end_top = abt.rotate_point(sleeve_end_top, sleeve_middle, up, -a)
        sleeve_end_bottom = abt.rotate_point(sleeve_end_bottom, sleeve_middle, up, -a)

        points = [
            bottom_middle,
            bottom_side,
            neck_bottom,
            neck_top,
            shoulder,
            armpit,
            sleeve_end_top,
            sleeve_end_bottom,
        ]

        for point in points:
            bproc.object.create_primitive("SPHERE", radius=0.05, location=point)

    def mesh_outline(self):
        pass


if __name__ == "__main__":
    PolygonalShirt()
