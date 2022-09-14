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
        # Applying the transform does not work well with geometry nodes that edit the mesh positions because they
        # can override the transform.
        # abt.select_only(self.blender_object)
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    @property
    def rotation_euler(self):
        return self.blender_object.rotation_euler

    @rotation_euler.setter
    def rotation_euler(self, value):
        self.blender_object.rotation_euler = value
        # abt.select_only(self.blender_object)
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    @property
    def scale(self):
        return self.blender_object.scale

    @scale.setter
    def scale(self, value):
        if isinstance(value, float):
            value = (value, value, value)
        self.blender_object.scale = value
        # abt.select_only(self.blender_object)
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    def add_material(self, required_tags=[], displacement=False):
        # Load a random asset with the required tags.
        assets = abt.assets()
        assets = [m for m in assets if m.type == "materials"]

        assets_with_required_tags = []
        for asset in assets:
            tags = asset.tags
            if all((required_tag in tags) for required_tag in required_tags):
                assets_with_required_tags.append(asset)

        assert len(assets_with_required_tags) != 0

        index = np.random.choice(len(assets_with_required_tags))
        asset = assets_with_required_tags[index]
        material = asset.load()

        self.blender_object.data.materials.append(material)

        # Fix texture scale
        bpy.context.scene.render.engine = "CYCLES"

        try:
            override = bpy.context.copy()
            override["material"] = material
            with bpy.context.temp_override(**override):
                bpy.ops.pha.tex_scale_fix()
                bpy.ops.pha.tex_displacement_setup()
        except:  # noqa: E722
            pass

        return material

    def add_geometry_node_group(self, name):
        assets = abt.assets()
        assets = [a for a in assets if a.type == "node_groups"]
        # Currently if multiple assets with this name are found, we pick the first.
        asset = next((a for a in assets if a.name == name), None)
        if asset is None:
            print(f"Asset with name {name} not found, no geomtery node group added.")
            return

        node_group_specification = asset.load()

        # bpy.context.window.workspace = bpy.data.workspaces["Geometry Nodes"]

        # TODO we could check if the node group is already present
        # context = bpy.context
        # override = context.copy()
        # override["active_object"] = self.blender_object
        # with context.temp_override(**override):
        bpy.context.view_layer.objects.active = self.blender_object
        bpy.ops.node.new_geometry_nodes_modifier()

        # TODO check if all these inputs/outputs are avaible
        # TODO implement smarter linking of loaded node groups
        tree = self.blender_object.modifiers["GeometryNodes"].node_group
        group_instance = tree.nodes.new("GeometryNodeGroup")
        group_instance.node_tree = node_group_specification
        a = tree.nodes["Group Input"].outputs["Geometry"]
        b = group_instance.inputs["Mesh"]
        c = group_instance.outputs["Mesh"]
        d = tree.nodes["Group Output"].inputs["Geometry"]
        tree.links.new(a, b)
        tree.links.new(c, d)
        return group_instance

    def unwrap(self):
        # Can't seem to get these context overrides to work
        # context = bpy.context
        # print(context.active_object)
        # override = context.copy()
        # override["active_object"] = self.blender_object
        # with context.temp_override(**override):

        bpy.context.view_layer.objects.active = self.blender_object
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.uv.unwrap()
        bpy.ops.object.mode_set(mode="OBJECT")


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
