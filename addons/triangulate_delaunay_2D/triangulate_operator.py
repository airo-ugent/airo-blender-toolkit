import bpy
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper


class Triangulate(bpy.types.Operator, AddObjectHelper):
    """Triangulate a 2D mesh"""

    bl_idname = "mesh.triangulate"
    bl_label = "Triangulate"
    bl_options = {"REGISTER", "UNDO"}
    bl_icon = "MOD_CLOTH"

    minimum_triangle_density: FloatProperty(
        name="minimum_triangle_density",
        description="minimum_triangle_density",
        soft_min=10.0,
        soft_max=10000.0,
        step=100,
        default=100.0,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object.data

    def execute(self, context):
        import airo_blender_toolkit as abt

        abt.triangulate_blender_object(context.active_object, self.minimum_triangle_density)
        return {"FINISHED"}


# Register and add to the "add mesh" menu (required to use F3 search "Add Shirt" for quick access)
def register():
    bpy.utils.register_class(Triangulate)


def unregister():
    bpy.utils.unregister_class(Triangulate)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.triangulate()
