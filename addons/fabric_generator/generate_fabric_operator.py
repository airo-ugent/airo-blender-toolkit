import os
import sys

import bpy
import numpy as np
from bpy.types import Operator, Panel

import airo_blender_toolkit as abt

# Fragile workaround to initialize the Substance Addon from Python
home = os.path.expanduser("~")
substance_path = os.path.join(home, ".config", "blender", "3.2", "scripts", "addons", "Substance3DInBlender")
sys.path.insert(0, substance_path)
from Substance3DInBlender.api import SUBSTANCE_Api, SUBSTANCE_Utils  # noqa: E402
from Substance3DInBlender.common import RENDER_KEY  # noqa: E402

if not SUBSTANCE_Api.is_running:
    _result = SUBSTANCE_Api.initialize()

# This function of the SUBSTANCE_Api is replaced to make these update synchronous.
# When async was enabled, not all parameter changes where executed.
@classmethod  # noqa
def sbsar_parm_update_edited(cls, context, sbsar_id, graph_idx, graph_id, parm, value, output_size, callback):  # noqa
    _render_id = RENDER_KEY.format(sbsar_id, graph_idx)
    return callback(context, _render_id, sbsar_id, graph_idx, graph_id, parm, value, output_size)


SUBSTANCE_Api.sbsar_parm_update = sbsar_parm_update_edited


# Not sure where to place this:
asset_libraries = bpy.context.preferences.filepaths.asset_libraries
if "User Library" in asset_libraries:
    user_library = asset_libraries["User Library"].path
    default_sbsar_path = os.path.join(user_library, "FabricSubstance009.sbsar")
else:
    default_sbsar_path = ""


class VIEW3D_OT_generate_fabrics(Operator):
    bl_idname = "material.generate_fabrics"
    bl_label = "Generate Fabrics"

    _timer = None
    duplication_started = False

    finalized = False

    amount: bpy.props.IntProperty(
        name="amount", description="Amount of materials that will be generated.", default=1, min=1, soft_max=50  # noqa
    )

    sbsar_path: bpy.props.StringProperty(name="SBSAR Path", subtype="FILE_PATH", default=default_sbsar_path)  # noqa

    def _finalize(self, context):
        # wm = context.window_manager
        # wm.event_timer_remove(self._timer)
        self._visualize_materials()
        for material_name in self.materials:
            self._randomize_material(context, material_name)
        self._fix_projections(context)
        context.scene.render.engine = "CYCLES"
        abt.World()

        for image in bpy.data.images:
            image.reload()

    def _randomize_material(self, context, material_name):
        sbsar = context.scene.loaded_sbsars[material_name]
        graph = sbsar.graphs["Material"]
        graph.tiling.x = 1

        sbsar_index = context.scene.loaded_sbsars.find(material_name)
        print("index", sbsar_index, graph.parms_class_name)

        # print(graph.parms["enable_horizontal_1"])

        # graph.enable_horizontal_1 = "0"

        # bpy.context.scene.SUBSTANCE_SGP_C005FD51-83D6-4ABB-8E77-7854641C0C0D.enable_horizontal_1 = '0'
        graph_parameters = getattr(context.scene, graph.parms_class_name)

        # graph_parameters.callback = {"enabled": False}

        # global QUEUE_CURSOR_ACTIVE
        # QUEUE_CURSOR_ACTIVE = False

        graph_parameters.enable_horizontal_1 = "0"
        graph_parameters.enable_horizontal_2 = "0"
        graph_parameters.enable_horizontal_3 = "0"
        graph_parameters.enable_horizontal_4 = "0"
        graph_parameters.enable_horizontal_5 = "0"

        graph_parameters.enable_vertical_1 = "1"
        graph_parameters.enable_vertical_2 = "0"
        graph_parameters.enable_vertical_3 = "0"
        graph_parameters.enable_vertical_4 = "0"
        graph_parameters.enable_vertical_5 = "0"

        range = np.random.uniform(0.0, 2.0)
        position = (1 - range / 2.0) / 2.0  # emprically found to ensure symmtery of the pattern

        graph_parameters.range_vertical_1 = range
        graph_parameters.position_vertical_1 = position
        graph_parameters.color_vertical_1 = [1.000000, 0.000000, 0.000000, 1.000000]
        graph_parameters.tile_vertical_1 = np.random.randint(1, 10)

        context.scene.sbsar_index = sbsar_index

    def _visualize_materials(self):
        for i, material_name in enumerate(self.materials):
            material = bpy.data.materials[material_name]
            plane = abt.Plane(location=(2.1 * i, 0, 0))
            plane.blender_object.data.materials.append(material)

    def _fix_projections(self, context):
        print(len(context.scene.loaded_sbsars))
        for material_name in self.materials:
            sbsar = context.scene.loaded_sbsars[material_name]
            sbsar.graphs["Material"].shader_preset_list = "1"  # Projection Standard

    def duplicate_material(self, context):
        self.duplicated_materials = []
        for _ in range(self.amount - 1):
            name = SUBSTANCE_Utils.get_unique_name(self.filename, context)
            self.duplicated_materials.append(name)
            bpy.ops.substance.duplicate_sbsar()

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.cancel(context)
            return {"CANCELLED"}

        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        print("TIMER")

        if self.loaded_material in bpy.data.materials and not self.duplication_started:
            self.duplicate_material(context)
            self.duplication_started = True
            return {"PASS_THROUGH"}

        if not self.duplication_started:
            return {"PASS_THROUGH"}

        if all([m in bpy.data.materials for m in self.duplicated_materials]):
            if not self.finalized:
                self.materials = [self.loaded_material] + self.duplicated_materials
                self._finalize(context)
                self.finalized = True
            print("Finished generating fabrics!")

        # return {"FINISHED"}

        print([m.name for m in bpy.data.materials])
        # self.i +=1
        return {"RUNNING_MODAL"}

    def execute(self, context):
        abt.clear_scene()

        abspath = bpy.path.abspath(context.scene.fabric_sbsar_path)
        filename = os.path.basename(abspath)
        directory = os.path.dirname(abspath)

        self.filename = filename

        print(abspath)
        print(filename)
        print(directory)

        print(f"Generating {self.amount} new fabric materials!")
        # return {"FINISHED"}

        self.loaded_material = SUBSTANCE_Utils.get_unique_name(filename, context)

        # These calls are asynchronous.
        # for i in range(self.amount):
        # self.expected_materials.append(SUBSTANCE_Utils.get_unique_name(filename, context))
        bpy.ops.substance.load_sbsar(
            filepath=abspath,
            files=[{"name": filename, "name": filename}],
            directory=directory,
        )

        # bpy.context.scene.loaded_sbsars[0].graphs[0].shader_preset_list = '1'
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    # def invoke(self, context, event):
    #     self.i = 0
    #     context.window_manager.modal_handler_add(self)
    #     return {'RUNNING_MODAL'}


class VIEW3D_PT_generate_fabrics(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Fabrics"
    bl_label = "Generate Fabrics"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "fabric_sbsar_path")
        layout.prop(context.scene, "fabric_amount")
        props = layout.operator("material.generate_fabrics", text="Start generating", icon="MOD_CLOTH")
        props.amount = context.scene.fabric_amount
        props.sbsar_path = context.scene.fabric_sbsar_path


blender_classes = [VIEW3D_OT_generate_fabrics, VIEW3D_PT_generate_fabrics]


def register():
    bpy.types.Scene.fabric_sbsar_path = bpy.props.StringProperty(
        name="SBSAR Path", subtype="FILE_PATH", default=default_sbsar_path
    )
    bpy.types.Scene.fabric_amount = bpy.props.IntProperty(name="Amount", default=2)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    del bpy.types.Scene.fabric_sbsar_path
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
