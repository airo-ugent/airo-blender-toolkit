import bpy
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper


class AddTowel(bpy.types.Operator, AddObjectHelper):
    """Add a towel"""

    bl_idname = "mesh.primitive_towel_add"
    bl_label = "Towel"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(
        name="width",
        description="width",
        soft_min=0.1,
        soft_max=2.0,
        step=1,
        default=0.5,
    )
    length: FloatProperty(
        name="length",
        description="length",
        soft_min=0.2,
        soft_max=3.0,
        step=1,
        default=1.0,
    )

    def execute(self, context):
        import airo_blender_toolkit as abt

        abt.Towel(
            self.width,
            self.length,
        )

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(AddTowel.bl_idname, icon="MOD_CLOTH")


# Register and add to the "add mesh" menu (required to use F3 search "Add Towel" for quick access)
def register():
    bpy.utils.register_class(AddTowel)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddTowel)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.primitive_towel_add()
