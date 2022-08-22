import os
import random

import bpy
import numpy as np
from mathutils import Vector

from airo_blender_toolkit.colors import random_hsv


def assets_path():
    """Return the path to the top-level folder where Blender assets (textures, HDRIs, models, etc.) are located.
    This function also makes sure this folder is made if it does not exist yet.

    For now this function constructs the same path as Blender uses for the default User Library.
    However in the future we could also read from a config file/environment variable/Blender user preferences
    to allow customization.
    """
    home = os.path.expanduser("~")
    default_path = os.path.join(home, "Documents", "Blender", "Assets")
    os.makedirs(default_path, exist_ok=True)
    return default_path


def get_random_filename(filedir):
    onlyfiles = [f for f in os.listdir(filedir) if os.path.isfile(os.path.join(filedir, f))]
    onlyfiles.sort()
    return random.choice(onlyfiles)


def load_thingi10k_object():
    thingi_folder = os.path.join(assets_path(), "thingi10k")
    random_object_name = get_random_filename(thingi_folder)
    print(random_object_name)
    bpy.ops.import_mesh.stl(filepath=os.path.join(thingi_folder, random_object_name))
    obj = bpy.context.selected_objects[0]
    bb_vertex = obj.matrix_world @ (Vector(obj.bound_box[6]) - Vector(obj.bound_box[0]))
    bb_vertex = [abs(x) for x in bb_vertex]
    obj.scale = np.array([0.1 / (bb_vertex[0]), 0.1 / (bb_vertex[1]), 0.1 / (bb_vertex[2])]) * np.random.uniform(
        0.5, 3.0
    )
    obj.location = (np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5), 0)
    material = bpy.data.materials.new(name=random_object_name)
    material.diffuse_color = random_hsv()
    obj.data.materials.append(material)
