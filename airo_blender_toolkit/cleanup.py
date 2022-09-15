import bpy


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
