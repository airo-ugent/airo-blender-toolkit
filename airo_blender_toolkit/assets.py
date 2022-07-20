import os


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
