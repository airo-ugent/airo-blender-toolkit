import bpy
import numpy as np

import airo_blender_toolkit as abt
from airo_blender_toolkit.coco_parser import CocoKeypointCategory
from airo_blender_toolkit.keypointed_object import KeypointedObject
from airo_blender_toolkit.primitives import BlenderObject

# Same category ids as DeepFashion2 + 14: towel
# category_ids_map = {
#     "short_sleeved_shirt": 1,
#     "long_sleeved_shirt": 2,
#     "short_sleeved_outwear": 3,
#     "long_sleeved_outwear": 4,
#     "vest": 5,
#     "sling": 6,
#     "shorts": 7,
#     "trousers": 8,
#     "skirt": 9,
#     "short_sleeved_dress": 10,
#     "long_sleeved_dress": 11,
#     "vest_dress": 12,
#     "sling_dress": 13,
#     "towel": 14,
# }

# TODO think about the redundancy here and in PolygonalShirt
shirt_keypoints = [
    "bottom_right",
    "armpit_right",
    "sleeve_bottom_right",
    "sleeve_top_right",
    "shoulder_right",
    "neck_right",
    "neck_middle",
    "neck_left",
    "shoulder_left",
    "sleeve_top_left",
    "sleeve_bottom_left",
    "armpit_left",
    "bottom_left",
]

short_sleeved_shirt = CocoKeypointCategory(
    supercategory="clothes",
    id=1,
    name="short_sleeved_shirt",
    keypoints=shirt_keypoints,
    skeleton=[],  # TODO
)

long_sleeved_shirt = CocoKeypointCategory(
    supercategory="clothes",
    id=2,
    name="long_sleeved_shirt",
    keypoints=shirt_keypoints,
    skeleton=[],  # TODO
)


class Towel(BlenderObject, KeypointedObject):
    category = "towel"
    keypoint_ids = {"corner0": 0, "corner1": 1, "corner2": 2, "corner3": 3}

    def __init__(self, length, width):
        self.width = width
        self.length = length

        mesh = self._create_mesh()
        blender_object = abt.make_object(name=self.classification_name, mesh=mesh)
        super().__init__(blender_object, self.keypoint_ids)

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


class PolygonalShirt(BlenderObject, KeypointedObject):
    keypoint_ids = {
        "bottom_right": 0,
        "armpit_right": 1,
        "sleeve_bottom_right": 2,
        "sleeve_top_right": 3,
        "shoulder_right": 4,
        "neck_right": 5,
        "neck_middle": 6,
        "neck_left": 7,
        "shoulder_left": 8,
        "sleeve_top_left": 9,
        "sleeve_bottom_left": 10,
        "armpit_left": 11,
        "bottom_left": 12,
    }

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

        self.blender_object = self.make_shirt_object()
        super().__init__(self.blender_object, self.keypoint_ids)

        self.scale = scale
        abt.select_only(self.blender_object)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    @property
    def category(self):
        if self.sleeve_length > 0.5:
            return long_sleeved_shirt
        return short_sleeved_shirt

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
        # vertices *= self.scale

        faces = [list(range(len(vertices)))]
        mesh = vertices, [], faces
        blender_object = abt.make_object(self.category.name, mesh)
        return blender_object


class PolygonalPants(KeypointedObject):
    classification_name = "pants"
    keypoint_ids = {
        "crotch": 0,
        "pipe_right_bottom_left": 1,
        "pipe_right_bottom_right": 2,
        "waist_right": 3,
        "waist_left": 4,
        "pipe_left_bottom_left": 5,
        "pipe_left_bottom_right": 6,
    }

    def __init__(
        self,
        waist_width=0.4,
        crotch_depth=0.2,
        pipe_angle=10,
        pipe_length=0.8,
        pipe_bottom_width=0.1,
        scale=0.635,
    ):
        self.waist_width = waist_width
        self.crotch_depth = crotch_depth
        self.pipe_angle = pipe_angle
        self.pipe_length = pipe_length
        self.pipe_bottom_width = pipe_bottom_width
        self.scale = scale

        self.blender_object = self.make_pants_object()
        super().__init__(self.blender_object, PolygonalPants.keypoint_ids)

    def make_pants_object(self):
        # First we make the right half of the pants
        waist_right = np.array([self.waist_width / 2.0, 0.0, 0.0])
        crotch = np.array([0.0, -self.crotch_depth, 0.0])

        angle = np.deg2rad(self.pipe_angle)

        pipe_start = np.array([self.pipe_bottom_width / 2.0, 0.0, 0.0])
        pipe_direction = np.array([np.sin(angle) * self.pipe_length, -np.cos(angle) * self.pipe_length, 0.0])

        pipe_bottom_middle = pipe_start + pipe_direction
        offset = np.cross(pipe_direction, np.array([0.0, 0.0, 1.0]))
        offset /= np.linalg.norm(offset)
        offset *= self.pipe_bottom_width / 2.0
        pipe_bottom_left = pipe_bottom_middle + offset
        pipe_bottom_right = pipe_bottom_middle - offset

        vertices = [crotch, pipe_bottom_left, pipe_bottom_right, waist_right]

        for vertex in reversed(vertices[1:]):
            mirrored_vertex = vertex.copy()
            mirrored_vertex[0] *= -1
            vertices.append(mirrored_vertex)

        vertices = np.array(vertices)
        vertices[:, 1] -= pipe_bottom_left[1] / 2.0
        vertices *= self.scale

        faces = [list(range(len(vertices)))]
        mesh = vertices, [], faces
        blender_object = abt.make_object(self.classification_name, mesh)
        return blender_object


if __name__ == "__main__":
    # PolygonalShirt()
    PolygonalPants()
    # Towel()
