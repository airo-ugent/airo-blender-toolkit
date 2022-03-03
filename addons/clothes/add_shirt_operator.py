import bpy
import numpy as np
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper


class AddShirt(bpy.types.Operator, AddObjectHelper):
    """Add a shirt"""

    bl_idname = "mesh.primitive_shirt_add"
    bl_label = "Shirt"
    bl_options = {"REGISTER", "UNDO"}

    bottom_width: FloatProperty(
        name="bottom_width",
        description="bottom_width",
        soft_min=0.6,
        soft_max=0.75,
        step=1,
        default=0.65,
    )
    neck_width: FloatProperty(
        name="neck_width",
        description="neck_width",
        soft_min=0.2,
        soft_max=0.4,
        step=1,
        default=0.32,
    )
    neck_depth: FloatProperty(
        name="neck_depth",
        description="neck_depth",
        soft_min=0.0,
        soft_max=0.2,
        step=1,
        default=0.08,
    )

    shoulder_width: FloatProperty(
        name="shoulder_width",
        description="shoulder_width",
        soft_min=0.4,
        soft_max=0.8,
        step=1,
        default=0.62,
    )
    shoulder_height: FloatProperty(
        name="shoulder_height",
        description="shoulder_height",
        soft_min=1.0,
        soft_max=0.9,
        step=1,
        default=0.95,
    )
    sleeve_width_start: FloatProperty(
        name="sleeve_width_start",
        description="sleeve_width_start",
        soft_min=0.22,
        soft_max=0.34,
        step=1,
        default=0.28,
    )
    sleeve_width_end: FloatProperty(
        name="sleeve_width_end",
        description="sleeve_width_end",
        soft_min=0.14,
        soft_max=0.22,
        step=1,
        default=0.18,
    )
    sleeve_length: FloatProperty(
        name="sleeve_length",
        description="sleeve_length",
        soft_min=0.05,
        soft_max=1.0,
        step=1,
        default=0.76,
    )
    sleeve_angle: FloatProperty(
        name="sleeve_angle",
        description="sleeve_angle",
        soft_min=np.deg2rad(-10),
        soft_max=np.deg2rad(60),
        step=10,
        default=np.deg2rad(-3),
        subtype="ANGLE",  # noqa: F821
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

        abt.PolygonalShirt(
            self.bottom_width,
            self.neck_width,
            self.neck_depth,
            self.shoulder_width,
            self.shoulder_height,
            self.sleeve_width_start,
            self.sleeve_width_end,
            self.sleeve_length,
            np.rad2deg(self.sleeve_angle),
            self.scale,
        )

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(AddShirt.bl_idname, icon="MOD_CLOTH")


# Register and add to the "add mesh" menu (required to use F3 search "Add Shirt" for quick access)
def register():
    bpy.utils.register_class(AddShirt)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddShirt)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.primitive_shirt_add()
