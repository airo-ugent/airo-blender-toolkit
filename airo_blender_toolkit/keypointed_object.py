from typing import List

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Color

import airo_blender_toolkit as abt


class KeypointedObject:
    """Base class for custom object with keypoints.
    Trying this for now but not sure if it's worth it.
    """

    def __init__(self, bpy_object: bpy.types.Object, keypoint_ids: dict[str, list[int]]):
        self.keypoint_ids = keypoint_ids

    @property
    def keypoints_3D(self):
        vertices = self.blender_object.data.vertices
        keypoints = {}

        for key, vertex_id in self.keypoint_ids.items():
            keypoints[key] = vertices[vertex_id].co
        return keypoints

    @property
    def keypoints_3D_visible(self):
        keypoints_3D_visible = {}
        for key, coord in self.keypoints_3D.items():
            keypoints_3D_visible[key] = abt.is_visible(coord)
        return keypoints_3D_visible

    @property
    def keypoints_2D(self):
        return KeypointedObject.project_to_camera(self.keypoints_3D)

    @property
    def keypoints_2D_visible(self):
        return KeypointedObject.project_to_camera(self.keypoints_3D_visible)

    @staticmethod
    def project_to_camera(keypoints):
        # TODO support multiview, add camera arg to keypoints_2D
        scene = bpy.context.scene

        if scene.camera is None:
            scene.camera = scene.objects["Camera"]

        camera = scene.camera
        keypoints_2D = {}

        for key, coord in keypoints.items():
            keypoints_2D[key] = world_to_camera_view(scene, camera, coord)
        return keypoints_2D

    @property
    def coco_keypoints(self) -> List[float]:
        # Because coco wants coords in pixel space, we need the image dimensions here
        scene = bpy.context.scene
        image_width = scene.render.resolution_x
        image_height = scene.render.resolution_y

        coco_keypoints_list = []

        for name, coord in self.keypoints_2D.items():
            u, v, _ = coord
            px = image_width * u
            py = image_height * (1.0 - v)
            visible_flag = 2

            if px < 0 or py < 0 or px > image_width or py > image_height:
                visible_flag = 0
                px = 0.0
                py = 0.0

            coco_keypoints_list += [px, py, visible_flag]

        return coco_keypoints_list

    def json_ready_keypoints(self, dimension=2, only_visible=True):
        if dimension == 2 and only_visible:
            keypoints = self.keypoints_2D_visible
            suffix = "_keypoints_visible"
        elif dimension == 2 and not only_visible:
            keypoints = self.keypoints_2D
            suffix = "_keypoints"
        elif dimension == 3 and only_visible:
            keypoints = self.keypoints_3D_visible
            suffix = "_keypoints_3D_visible"
        else:
            keypoints = self.keypoints_3D
            suffix = "_keypoints_3D"

        keypoints_json = {}
        for key, coord in keypoints.items():
            keypoints_json[key + suffix] = list(coord)
        return keypoints_json

    def visualize_keypoints(self, radius=0.02, keypoints_color=None):
        n = len(self.keypoints_3D.keys())

        hues = [float(i) / n for i in range(n)]

        colors = []
        for hue in hues:
            color = Color()
            color.hsv = hue, 1.0, 1.0
            colors.append(color)

        for color, (category, keypoint) in zip(colors, self.keypoints_3D.items()):
            if keypoints_color:
                color = keypoints_color

            sphere = abt.Sphere(location=keypoint, radius=radius)
            sphere.blender_object.name = category

            sphere.blender_object.parent = self.blender_object

            # TODO bring back the color
            # material = sphere.new_material("Material")
            # material.set_principled_shader_value("Base Color", tuple(color) + (1,))
            # material.blender_object.diffuse_color = tuple(color) + (1,)
