import bpy
import numpy as np
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper


class AddPants(bpy.types.Operator, AddObjectHelper):
    """Add pants"""

    bl_idname = "mesh.primitive_pants_add"
    bl_label = "Pants"
    bl_options = {"REGISTER", "UNDO"}

    waist_width: FloatProperty(
        name="waist_width",
        description="waist_width",
        soft_min=0.3,
        soft_max=0.5,
        step=1,
        default=0.4,
    )
    crotch_depth: FloatProperty(
        name="crotch_depth",
        description="crotch_depth",
        soft_min=0.1,
        soft_max=0.3,
        step=1,
        default=0.2,
    )

    pipe_angle: FloatProperty(
        name="pipe_angle",
        description="pipe_angle",
        soft_min=np.deg2rad(0),
        soft_max=np.deg2rad(20),
        step=10,
        default=np.deg2rad(10),
        subtype="ANGLE",  # noqa: F821
    )

    pipe_length: FloatProperty(
        name="pipe_length",
        description="pipe_length",
        soft_min=0.3,
        soft_max=1.5,
        step=1,
        default=0.8,
    )
    pipe_bottom_width: FloatProperty(
        name="pipe_bottom_width",
        description="pipe_bottom_width",
        soft_min=0.05,
        soft_max=0.25,
        step=1,
        default=0.1,
    )

    scale: FloatProperty(
        name="scale",
        description="scale",
        soft_min=0.2,
        soft_max=1.5,
        step=1,
        default=0.635,
    )

    def execute(self, context):
        import airo_blender_toolkit as abt

        abt.PolygonalPants(
            self.waist_width,
            self.crotch_depth,
            np.rad2deg(self.pipe_angle),
            self.pipe_length,
            self.pipe_bottom_width,
            self.scale,
        )

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(AddPants.bl_idname, icon="MOD_CLOTH")


# Register and add to the "add mesh" menu (required to use F3 search "Add Pants" for quick access)
def register():
    bpy.utils.register_class(AddPants)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddPants)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.primitive_pants_add()
