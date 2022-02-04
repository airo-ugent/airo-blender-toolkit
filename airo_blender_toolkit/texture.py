import glob
import os
import random


def random_texture_name(textures_dir: str) -> str:
    glob_str = os.path.join(textures_dir, "*", "")
    texture_dirs = glob.glob(glob_str)
    texture_names = [os.path.basename(os.path.normpath(d)) for d in texture_dirs]
    texture_names.sort()
    return random.choice(texture_names)
