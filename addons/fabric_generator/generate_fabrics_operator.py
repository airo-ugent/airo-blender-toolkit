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

    def _randomize_material(self, context, material_name, seed=0):
        print(f"Starting randomization of {material_name} with seed {seed}")
        np.random.seed(seed)
        sbsar = context.scene.loaded_sbsars[material_name]
        graph = sbsar.graphs["Material"]
        graph.tiling.x = 1

        # sbsar_index = context.scene.loaded_sbsars.find(material_name)
        # print("index", sbsar_index, graph.parms_class_name)

        # bpy.context.scene.SUBSTANCE_SGP_C005FD51-83D6-4ABB-8E77-7854641C0C0D.enable_horizontal_1 = '0'
        graph_parameters = getattr(context.scene, graph.parms_class_name)

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
        shift = np.random.choice([0.0, 0.5])  # the second symmetric option: the stripes are at the edges then
        position = position + shift
        stripe_count = np.random.randint(1, 10)
        stripe_color = abt.random_hsv()

        graph_parameters.range_vertical_1 = range
        graph_parameters.position_vertical_1 = position
        graph_parameters.tile_vertical_1 = stripe_count
        graph_parameters.color_vertical_1 = stripe_color

        add_horizontal_stripes = np.random.choice([True, False])

        if add_horizontal_stripes:
            graph_parameters.enable_horizontal_1 = "1"
            graph_parameters.range_horizontal_1 = range
            graph_parameters.position_horizontal_1 = position
            graph_parameters.tile_horizontal_1 = stripe_count
            graph_parameters.color_horizontal_1 = stripe_color

        # context.scene.sbsar_index = sbsar_index

    def _visualize_materials(self):
        n = len(self.materials)
        columns = int(np.ceil(np.sqrt(n)))
        for i, material_name in enumerate(self.materials):
            material = bpy.data.materials[material_name]
            scale = 2.1
            x = scale * (i % columns)
            y = -scale * (i // columns)
            plane = abt.Plane(location=(x, y, 0))
            plane.blender_object.data.materials.append(material)

    def _fix_projections(self, context):
        print(len(context.scene.loaded_sbsars))
        for material_name in self.materials:
            sbsar = context.scene.loaded_sbsars[material_name]
            sbsar.graphs["Material"].shader_preset_list = "1"  # Projection Standard

    def _mark_assets(self):

        # for area in bpy.context.screen.areas:
        #     if area.type == 'PROPERTIES':
        #         area.ui_type = 'ASSETS'

        # TypeError: bpy_struct: item.attr = val: enum "ASSET_BROWSER" not found in
        # ('VIEW_3D', 'IMAGE_EDITOR', 'UV', 'CompositorNodeTree', 'TextureNodeTree', 'GeometryNodeTree',
        # 'ShaderNodeTree', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'DOPESHEET', 'TIMELINE', 'FCURVES', 'DRIVERS',
        # 'NLA_EDITOR', 'TEXT_EDITOR', 'CONSOLE', 'INFO', 'OUTLINER', 'PROPERTIES', 'FILES', 'ASSETS', 'SPREADSHEET',
        # 'PREFERENCES')

        for material_name in self.materials:
            material = bpy.data.materials[material_name]
            material.asset_mark()
            material.asset_data.description = "A randomly generated fabric texture."
            tags = ["fabric", "cloth", "textile", "towel", "randomized"]
            for tag in tags:
                material.asset_data.tags.new(tag)

            # Doesn't work, shows old preview
            # preview = f"/home/idlab185/Documents/Adobe/Substance3DInBlender/export/{material_name}_baseColor.tga"
            # bpy.ops.ed.lib_id_load_custom_preview(
            #     {"id": material},
            #     filepath=preview
            # )

            # This shows the wrong preview at this point :/
            bpy.ops.ed.lib_id_generate_preview(
                {"id": material},
            )

            # override = bpy.context.copy()

            # # bpy.context.screen.areas.new()

            # for area in bpy.context.screen.areas:
            #     #if area.type != 'IMAGE_EDITOR' or area.ui_type != 'VIEW': # Image Editor View only
            #     #if area.type != 'IMAGE_EDITOR' or area.ui_type != 'UV': # UV Editor View only
            #     if area.type != 'ASSET_BROWSER':
            #         continue

            #     # area.spaces.active.show_region_header = False

            #     override['area'] = area
            #     # bpy.ops.image.view_zoom_ratio(override, ratio=1.0)
            #     bpy.ops.ed.lib_id_generate_preview()
            #     area.tag_redraw()

            # active_asset = SpaceAssetInfo.get_active_asset(context)

            # override = bpy.context.copy()
            # override["material"] = material
            # with bpy.context.temp_override(**override):

            # bpy.ops.ed.lib_id_generate_preview()

        # for obj in bpy.data.objects:
        # obj.asset_mark()

        bpy.ops.file.pack_all()

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.cancel(context)
            return {"CANCELLED"}

        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        print("============================================================================")
        print(self.materials)
        print([m.name for m in bpy.data.materials])
        print("============================================================================")

        if not all(m in bpy.data.materials for m in self.materials):
            return {"PASS_THROUGH"}

        # Finalize
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        for i, material_name in enumerate(self.materials):
            self._randomize_material(context, material_name, seed=i)

        self._visualize_materials()
        self._fix_projections(context)
        context.scene.render.engine = "CYCLES"
        abt.World()

        self._mark_assets()

        print("Finished generating.")
        return {"FINISHED"}

    def execute(self, context):
        abt.clear_scene()

        abspath = bpy.path.abspath(context.scene.fabric_sbsar_path)
        filename = os.path.basename(abspath)
        directory = os.path.dirname(abspath)

        self.filename = filename

        self.materials = []
        for _ in range(self.amount):
            self.materials.append(SUBSTANCE_Utils.get_unique_name(filename, context))
            bpy.ops.substance.load_sbsar(
                filepath=abspath,
                files=[{"name": filename, "name": filename}],
                directory=directory,
            )
            time.sleep(3.0)  # without this sleep the substance loader quickly gives errors when loading 10+ materials

        wm = context.window_manager
        self._timer = wm.event_timer_add(2.0, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


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
    bpy.types.Scene.fabric_amount = bpy.props.IntProperty(name="Amount", default=5)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    del bpy.types.Scene.fabric_sbsar_path
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
