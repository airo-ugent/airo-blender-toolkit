import os

import bpy
import requests
from mathutils import Vector


def download_hdri(hdri_name, output_dir="", res="1k", format="exr"):
    """Downloads an HDRI from Poly Haven.

    Args:
        hdri_name (str): short name of the HDRI. Can be found in the url of the HDRI on polyhaven.com
        output_dir (str, optional): directory where the HDRI will be saved. Defaults to "".
        res (str, optional): HDRI resolution e.g. "1k", "2k", "4k", "8k". Defaults to "1k".
        format (str, optional): HDRI format, "hdr" or "exr". Defaults to "exr".

    Returns:
        boolean: True when the download was successful.
    """
    url = f"https://dl.polyhaven.org/file/ph-assets/HDRIs/{format}/{res}/{hdri_name}_{res}.{format}"
    # example: https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/1k/studio_small_09_1k.exr

    r = requests.get(url, allow_redirects=True)

    if r.status_code != 200:
        print(f"Bad status code {r.status_code}")
        return False

    local_filename = f"{hdri_name}_{res}.{format}"
    local_path = os.path.join(output_dir, local_filename)

    with open(local_path, "wb") as f:
        f.write(r.content)

    return True


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
    world_tree = bpy.data.worlds["World"].node_tree

    for node in world_tree.nodes:
        world_tree.nodes.remove(node)

    world_output_node = world_tree.nodes.new("ShaderNodeOutputWorld")

    environment_texture_node = world_tree.nodes.new("ShaderNodeTexEnvironment")
    place(environment_texture_node, world_output_node, "left")

    world_tree.links.new(environment_texture_node.outputs["Color"], world_output_node.inputs["Surface"])

    environment_texture_node.image = bpy.data.images.load(filepath)

    mapping_node = world_tree.nodes.new("ShaderNodeMapping")
    place(mapping_node, environment_texture_node, "left")
    world_tree.links.new(mapping_node.outputs["Vector"], environment_texture_node.inputs["Vector"])

    texture_coordinate_node = world_tree.nodes.new("ShaderNodeTexCoord")
    place(texture_coordinate_node, mapping_node, "left")
    world_tree.links.new(texture_coordinate_node.outputs["Generated"], mapping_node.inputs["Vector"])

    mapping_node.inputs["Rotation"].default_value[2] = z_rotation
