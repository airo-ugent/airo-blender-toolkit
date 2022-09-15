import bpy


def _blender_object_from_mesh(mesh, name="Object"):
    # consider using if faster:
    # from bpy_extras import object_utils
    # object_utils.object_data_add(context, mesh, operator=self)
    vertices, edges, faces = mesh
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    object = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(object)
    return object
