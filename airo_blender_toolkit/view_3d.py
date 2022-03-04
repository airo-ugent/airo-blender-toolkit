import bpy


def show_wireframes(visible=True):
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.overlay.show_wireframes = visible
