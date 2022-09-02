import os
import sys

import bpy

import airo_blender_toolkit as abt

# Fragile workaround to initialize the Substance Addon from Python
home = os.path.expanduser("~")
substance_path = os.path.join(home, ".config", "blender", "3.2", "scripts", "addons", "Substance3DInBlender")
sys.path.insert(0, substance_path)
from Substance3DInBlender.api import SUBSTANCE_Api  # noqa: E402

if not SUBSTANCE_Api.is_running:
    _result = SUBSTANCE_Api.initialize()


class GenerateFabrics(bpy.types.Operator):
    bl_idname = "material.generate_fabrics"
    bl_label = "Generate Fabrics"

    _timer = None
    i = 0

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.cancel(context)
            return {"CANCELLED"}

        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        print([m.name for m in bpy.data.materials])
        # self.i +=1
        return {"RUNNING_MODAL"}

    def execute(self, context):
        abt.clear_scene()

        filename = "FabricSubstance009.sbsar"
        directory = os.path.join(home, "Documents", "Blender", "AmbientCG")
        filepath = os.path.join(directory, filename)

        bpy.ops.substance.load_sbsar(
            filepath=filepath,
            files=[{"name": filename, "name": filename}],
            directory=directory,
        )

        # bpy.context.scene.loaded_sbsars[0].graphs[0].shader_preset_list = '1'

        filename.split(".")[0]

        wm = context.window_manager
        self._timer = wm.event_timer_add(2.0, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    # def invoke(self, context, event):
    #     self.i = 0
    #     context.window_manager.modal_handler_add(self)
    #     return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(GenerateFabrics)


def unregister():
    bpy.utils.unregister_class(GenerateFabrics)
