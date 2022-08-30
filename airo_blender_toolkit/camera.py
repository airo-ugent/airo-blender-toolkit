import bpy
from mathutils import Vector

from airo_blender_toolkit.primitives import BlenderObject


class Camera(BlenderObject):
    def __init__(self, location=(0.0, 0.0, 1.0), rotation=(0, 0, 0), scale=1.0):
        if isinstance(scale, float):
            scale = (scale, scale, scale)

        bpy.ops.object.camera_add(location=location, rotation=rotation, scale=scale)
        self.blender_object = bpy.context.active_object

        # Set this camera as the scene camera if there is none yet.
        scene = bpy.context.scene
        if scene.camera is None:
            scene.camera = self.blender_object

    def look_at(self, point):
        camera = self.blender_object
        direction = Vector(point) - camera.location
        rot_quat = direction.to_track_quat("-Z", "Y")
        camera.rotation_euler = rot_quat.to_euler()

    @property
    def focal_length(self):
        return self.blender_object.data.lens

    @focal_length.setter
    def focal_length(self, value):
        self.blender_object.data.lens = value
