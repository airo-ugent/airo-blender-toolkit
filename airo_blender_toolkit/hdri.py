import os

import bpy
import numpy as np
import requests
from mathutils import Vector


def download_hdri(hdri_name, output_dir="", res="1k", format="exr"):
    """Downloads an HDRI from Poly Haven. Does not redownload if the HDRI already exists.

    Args:
        hdri_name (str): short name of the HDRI. Can be found in the url of the HDRI on polyhaven.com
        output_dir (str, optional): directory where the HDRI will be saved. Defaults to "".
        res (str, optional): HDRI resolution e.g. "1k", "2k", "4k", "8k". Defaults to "1k".
        format (str, optional): HDRI format, "hdr" or "exr". Defaults to "exr".

    Returns:
        str: Path to the downloaded HDRI file.
    """

    local_filename = f"{hdri_name}_{res}.{format}"
    local_path = os.path.join(output_dir, local_filename)

    if os.path.exists(local_path):
        print("HDRI exists, not redownloading")
        return local_path

    url = f"https://dl.polyhaven.org/file/ph-assets/HDRIs/{format}/{res}/{hdri_name}_{res}.{format}"
    # example: https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/1k/studio_small_09_1k.exr

    r = requests.get(url, allow_redirects=True)

    if r.status_code != 200:
        print(f"Bad status code {r.status_code}")
        return

    with open(local_path, "wb") as f:
        f.write(r.content)

    return local_path


# TODO clean up
def place(node, reference_node, direction, margin=50):
    if direction in ["left", "right"]:
        displacement = Vector([node.width + margin, 0])
    if direction in ["above", "below"]:
        displacement = Vector([0, node.height + margin])
    if direction in ["left", "below"]:
        displacement *= -1
    node.location = reference_node.location + displacement


# TODO clean up and document
def load_hdri(filepath, z_rotation=0.0):
    """Loads an HDRI file from disk into blender and sets up a basic node tree for it.

    texture_coord -> mapping -> env_texture -> output

    The Texture Coordinate and Mapping nodes allow us to easily rotate the HDRI.

    Args:
        filepath (str): Path to the HDRI file to be loaded.
        z_rotation (float, optional): The rotation of the HDRI around the vertical axis in degrees. Defaults to 0.0.
    """
    # Clearing the world tree
    world_tree = bpy.data.worlds["World"].node_tree
    for node in world_tree.nodes:
        world_tree.nodes.remove(node)

    # Output node
    output_node = world_tree.nodes.new("ShaderNodeOutputWorld")

    # Environment texture node
    env_texture_node = world_tree.nodes.new("ShaderNodeTexEnvironment")
    place(env_texture_node, output_node, "left")
    env_texture_node.image = bpy.data.images.load(filepath)
    world_tree.links.new(env_texture_node.outputs["Color"], output_node.inputs["Surface"])

    # Mapping node
    mapping_node = world_tree.nodes.new("ShaderNodeMapping")
    place(mapping_node, env_texture_node, "left")
    world_tree.links.new(mapping_node.outputs["Vector"], env_texture_node.inputs["Vector"])

    # Texture Coordinate node
    texture_coord_node = world_tree.nodes.new("ShaderNodeTexCoord")
    place(texture_coord_node, mapping_node, "left")
    world_tree.links.new(texture_coord_node.outputs["Generated"], mapping_node.inputs["Vector"])

    mapping_node.inputs["Rotation"].default_value[2] = np.deg2rad(z_rotation)
