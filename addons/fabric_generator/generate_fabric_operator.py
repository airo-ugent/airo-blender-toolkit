import os
import sys
import time

import bpy
import numpy as np
from bpy.types import Operator, Panel

import airo_blender_toolkit as abt

# Fragile workaround to initialize the Substance Addon from Python
home = os.path.expanduser("~")
substance_path = os.path.join(home, ".config", "blender", "3.2", "scripts", "addons", "Substance3DInBlender")
sys.path.insert(0, substance_path)
from Substance3DInBlender.api import SUBSTANCE_Api, SUBSTANCE_Utils  # noqa: E402
from Substance3DInBlender.common import RENDER_KEY, Code_RequestType  # noqa: E402

if not SUBSTANCE_Api.is_running:
    _result = SUBSTANCE_Api.initialize()


class VIEW3D_OT_generate_fabric(Operator):
    bl_idname = "material.generate_fabric"
    bl_label = "Generate Fabric"

    def execute(self, context):
        self.start_time = time.time()
        self.initialize(context)
        self.state = "INITIALIZED"
        self.start_modal(context)
        return {"RUNNING_MODAL"}

    def initialize(self, context):
        abt.clear_scene()

    def start_modal(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {"FINISHED"}

    def modal(self, context, event):
        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        if self.state == "INITIALIZED":
            self.state = "LOADING_SBSAR"
            self.material_name = self._start_loading_sbsar(context)

        if self.state == "LOADING_SBSAR":
            if self.material_name not in bpy.data.materials:
                return {"PASS_THROUGH"}
            print("SBSAR LOADED")
            self.state = "RANDOMIZING_SBSAR"
            self._randomize_material(context, self.material_name)
            self.state = "FINISHED"

        if self.state == "RANDOMIZING_SBSAR":
            return {"PASS_THROUGH"}

        # Finalize
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print(f"Generating fabric done! [{time.time() - self.start_time} s]")
        return {"FINISHED"}

    def _start_loading_sbsar(self, context):
        asset_libraries = bpy.context.preferences.filepaths.asset_libraries
        user_library = asset_libraries["User Library"].path
        fabric_sbsar_path = os.path.join(user_library, "FabricSubstance009.sbsar")

        abspath = bpy.path.abspath(fabric_sbsar_path)
        filename = os.path.basename(abspath)
        directory = os.path.dirname(abspath)

        material_name = SUBSTANCE_Utils.get_unique_name(filename, context)
        bpy.ops.substance.load_sbsar(
            filepath=abspath,
            files=[{"name": filename, "name": filename}],
            directory=directory,
        )
        return material_name

    def _randomize_material(self, context, material_name, seed=0):
        print(f"Starting randomization of {material_name} with seed {seed}")
        np.random.seed(seed)
        sbsar = bpy.context.scene.loaded_sbsars[self.material_name]
        parameter_ids_by_name = {}

        for graph in sbsar.graphs:
            graph_parameters = getattr(context.scene, graph.parms_class_name)
            for k, v in graph_parameters.default.parms.items():
                parameter_ids_by_name[k] = v.id

        def update_parameter(parameter_name, value):
            parameter_id = parameter_ids_by_name[parameter_name]
            SUBSTANCE_Api.msg_sbsar_update_parm(sbsar.id, parameter_id, value, request_type=Code_RequestType.r_sync)

        # Disable all stripes except the first horizontal and vertical one.s
        for i in range(2, 6):
            update_parameter(f"enable_horizontal_{i}", 0)
            update_parameter(f"enable_vertical_{i}", 0)

        horizontal_stripes = np.random.choice([True, False])
        if not horizontal_stripes:
            update_parameter("enable_horizontal_1", 0)

        stripe_width = np.random.uniform(0.0, 2.0)
        position = (1 - stripe_width / 2.0) / 2.0  # emprically found to ensure symmtery of the pattern
        shift = np.random.choice([0.0, 0.5])  # the second symmetric option: the stripes are at the edges then
        position = position + shift
        stripe_count = np.random.randint(1, 10)

        for orientation in ["horizontal", "vertical"]:
            update_parameter(f"range_{orientation}_1", stripe_width)
            update_parameter(f"position_{orientation}_1", position)
            update_parameter(f"tile_{orientation}_1", stripe_count)

        stripe_color = abt.random_hsv()
        update_parameter("color_vertical_1", stripe_color)
        differently_colored_stripes = np.random.choice([True, False])
        if differently_colored_stripes:
            stripe_color = abt.random_hsv()
        update_parameter("color_horizontal_1", stripe_color)

        render_id = RENDER_KEY.format(sbsar.id, graph.index)
        SUBSTANCE_Api.sbsar_render(render_id, sbsar.id, graph.index, Code_RequestType.r_sync)


class VIEW3D_PT_generate_fabric(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Fabric"
    bl_label = "Generate Fabric"

    def draw(self, context):
        layout = self.layout
        layout.operator("material.generate_fabric", text="Generate", icon="MOD_CLOTH")


blender_classes = [VIEW3D_OT_generate_fabric, VIEW3D_PT_generate_fabric]


def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
