import os
import sys
import time

import bpy

import airo_blender_toolkit as abt

# Fragile workaround to initialize the Substance Addon from Python
home = os.path.expanduser("~")
substance_path = os.path.join(home, ".config", "blender", "3.2", "scripts", "addons", "Substance3DInBlender")
sys.path.insert(0, substance_path)
from Substance3DInBlender.api import SUBSTANCE_Api, SUBSTANCE_Utils  # noqa: E402
from Substance3DInBlender.sbsar.async_ops import _initialize_sbsar_data  # noqa: E402

if not SUBSTANCE_Api.is_running:
    _result = SUBSTANCE_Api.initialize()

abt.clear_scene()

context = bpy.context

asset_libraries = context.preferences.filepaths.asset_libraries
user_library = asset_libraries["User Library"].path
fabric_sbsar_path = os.path.join(user_library, "FabricSubstance009.sbsar")
abspath = bpy.path.abspath(fabric_sbsar_path)
filename = os.path.basename(abspath)
directory = os.path.dirname(abspath)

material_name = SUBSTANCE_Utils.get_unique_name(filename, context)


def load_sbsar_sync():
    _addon_prefs, _selected_shader_preset = SUBSTANCE_Utils.get_selected_shader_preset(context)
    _normal_format = _addon_prefs.normal_format
    _output_size = _addon_prefs.resolution.get()
    _shader_outputs = getattr(context.scene, _selected_shader_preset.outputs_class_name)
    _unique_name = SUBSTANCE_Utils.get_unique_name(filename, context)
    SUBSTANCE_Utils.log_data("INFO", "Loading substance from file [{}]".format(filename))
    # Load the sbsar to the SRE
    _result = SUBSTANCE_Api.sbsar_load(abspath)
    _sbsar_id = _result[1]
    _loaded_sbsar = context.scene.loaded_sbsars.add()
    _loaded_sbsar.initialize(_sbsar_id, _unique_name, filename, abspath)
    context.scene.sbsar_index = len(context.scene.loaded_sbsars) - 1
    _initialize_sbsar_data(
        context, _sbsar_id, _unique_name, filename, abspath, _normal_format, _output_size, _shader_outputs
    )
    return _sbsar_id


sbsar_id = load_sbsar_sync()
print("FINISHED LOADING")
time.sleep(5)
print("FINISHED SLEEPING")

sbsar = context.scene.loaded_sbsars[material_name]

print(sbsar)
print(len(sbsar.graphs))

for graph in sbsar.graphs:
    print([k for (k, v) in graph.parms.items()])

# _result = SUBSTANCE_Api.msg_sbsar_update_parm(sbsar_id, parm_id, value, request_type=Code_RequestType.r_sync)
