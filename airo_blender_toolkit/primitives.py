from abc import ABC

import bpy
import numpy as np

import airo_blender_toolkit as abt


class BlenderObject(ABC):
    blender_obj: bpy.types.Object

    @property
    def location(self):
        return self.blender_object.location

    @location.setter
    def location(self, value):
        self.blender_object.location = value
        abt.select_only(self.blender_object)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    @property
    def rotation_euler(self):
        return self.blender_object.rotation_euler

    @rotation_euler.setter
    def rotation_euler(self, value):
        self.blender_object.rotation_euler = value
        abt.select_only(self.blender_object)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    @property
    def scale(self):
        return self.blender_object.scale

    @scale.setter
    def scale(self, value):
        if isinstance(value, float):
            value = (value, value, value)
        self.blender_object.scale = value
        abt.select_only(self.blender_object)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    def add_material(self, required_tags=[]):
        # Load a random asset with the required tags.
        assets = abt.assets()
        assets = [m for m in assets if m.type == "material"]

        assets_with_required_tags = []
        for asset in assets:
            tags = asset.tags
            if all((required_tag in tags) for required_tag in required_tags):
                assets_with_required_tags.append(asset)

        index = np.random.choice(len(assets_with_required_tags))
        asset = assets_with_required_tags[index]
        material = asset.load()

        self.blender_object.data.materials.append(material)

        # Fix texture scale
        override = bpy.context.copy()
        override["material"] = material
        with bpy.context.temp_override(**override):
            val = bpy.ops.pha.tex_scale_fix()
            print("val", val)

        return material

        # material = abt.Asset(type="material", required_tags=[])
        # abt.import_asset_materials()
        # materials = [m for m in bpy.data.materials if m.asset_data]

        # materials_with_required_tags = []
        # for material in materials:
        #     tags = material.asset_data.tags
        #     if all((required_tag in tags) for required_tag in required_tags):
        #         materials_with_required_tags.append(material)

        # index = np.random.choice(len(materials_with_required_tags))
        # material = materials_with_required_tags[index]

        # self.blender_object.data.materials.append(material)
        # return material


class Plane(BlenderObject):
    def __init__(self, size=2.0, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=1.0):
        if isinstance(scale, float):
            scale = (scale, scale, scale)

        bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation, scale=scale)
        self.blender_object = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


class Sphere(BlenderObject):
    def __init__(self, radius=1.0, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=1.0):
        if isinstance(scale, float):
            scale = (scale, scale, scale)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, rotation=rotation, scale=scale)
        self.blender_object = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


class IcoSphere(BlenderObject):
    def __init__(self, radius=1.0, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=1.0):
        if isinstance(scale, float):
            scale = (scale, scale, scale)

        bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, location=location, rotation=rotation, scale=scale)
        self.blender_object = bpy.context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
