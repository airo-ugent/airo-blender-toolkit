import os
import bpy
import airo_blender_toolkit as abt
import shutil
import numpy as np

def move_texture_png(model_directory):
    texture_path = os.path.join(model_directory, "materials", "textures", "texture.png")
    texture_destination_path = os.path.join(model_directory, "meshes", "texture.png")
    if not os.path.exists(texture_destination_path):
        shutil.move(texture_path, texture_destination_path)

def gso_download_to_asset(model_directory):
    move_texture_png(model_directory)
    obj_path = os.path.join(model_directory, "meshes", "model.obj")
    bpy.ops.object.select_all(action="DESELECT")
    # bpy.ops.import_scene.obj(filepath=obj_path, up_axis="Z") #, split_mode="OFF")
    bpy.ops.wm.obj_import(filepath=obj_path, up_axis='Z')
    object = bpy.context.selected_objects[0]
    object.asset_mark()
    # object.rotation_euler = 0, 0, 0
    # bpy.context.view_layer.objects.active = object
    # bpy.ops.object.transform_apply()
    return object


def all_gso_downloads_to_assets(gso_directory):
    model_directories = [f.path for f in os.scandir(gso_directory) if f.is_dir()]

    print(len(model_directories))

    n = len(model_directories)
    columns = int(np.ceil(np.sqrt(n)))
    spacing = 0.55


    print(f"Found {n} models, using {columns} columns.")

    for i, model_directory in enumerate(model_directories):
        print(i, model_directory)
        x = spacing * (i % columns)
        y = -spacing * (i // columns)
        object = gso_download_to_asset(model_directory)
        object.location= (x, y, 0)
        # abt.Plane(location=(x,y,0), size=0.25)



#"2_of_Jenga_Classic_Game"
abt.clear_scene()

home = os.path.expanduser("~")
gso_directory = os.path.join(home, "Documents", "Blender", "GSO")
gso_model_path = os.path.join(gso_directory, "adistar_boost_m")
# gso_download_to_asset(gso_model_path)

all_gso_downloads_to_assets(gso_directory)