import bpy


# TODO cleanup and document
def make_object(name, mesh):
    # consider using:
    # from bpy_extras import object_utils
    # object_utils.object_data_add(context, mesh, operator=self)

    vertices, edges, faces = mesh
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    object = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(object)
    return object


def clear_scene():
    """Clear the active scene by removing objects, orphan data and custom properties"""
    remove_all_objects()
    remove_orphan_data()


def remove_all_objects():
    """Removes all objects of the current scene"""
    # Select all
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    # Delete selection
    bpy.ops.object.delete()


def remove_orphan_data():
    """Remove all data blocks which are not used anymore."""
    data_structures = [
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.textures,
        bpy.data.images,
        bpy.data.brushes,
        bpy.data.cameras,
        bpy.data.actions,
        bpy.data.lights,
        bpy.data.worlds,
    ]

    for data_structure in data_structures:
        for block in data_structure:
            # If no one uses this block => remove it
            if block.users == 0:
                data_structure.remove(block)


def select_only(blender_object):
    """Selects and actives a Blender object and deselects all others"""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = blender_object
    blender_object.select_set(True)
