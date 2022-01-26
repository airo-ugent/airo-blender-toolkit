import bpy

# TODO cleanup and document
def make_object(name, mesh):
    vertices, edges, faces = mesh
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    object = bpy.data.objects.new(name, mesh)
    collection = bpy.data.collections["Collection"]
    collection.objects.link(object)
    return object


def set_location(object, location):
    select_only(object)
    object.location = location
    bpy.ops.object.transform_apply(location=True)


def rotate(object, angle, axis="Z"):
    select_only(object)
    # Ugly way to set context for transform, figure out the right way to do this.
    ov = bpy.context.copy()
    ov["area"] = [a for a in bpy.context.screen.areas if a.type == "VIEW_3D"][0]
    bpy.ops.transform.rotate(ov, value=angle, orient_axis=axis, orient_type="GLOBAL")
    bpy.ops.object.transform_apply(rotation=True)


def cleanup_scene():
    """Cleanup the scene by removing objects, orphan data and custom properties"""
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
