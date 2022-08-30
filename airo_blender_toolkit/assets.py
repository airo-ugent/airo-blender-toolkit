from pathlib import Path

import bpy
import numpy as np
from appdirs import user_cache_dir
from diskcache import Cache

from airo_blender_toolkit.primitives import BlenderObject

# The 6 asset types in the filter dropdown in the Asset Browser
asset_types = [
    "actions",
    "collections",
    "materials",
    "node_groups",
    "objects",
    "worlds",
]


class Asset:
    def __init__(self, name, library_name, type, tags, source_file):
        self.name = name
        self.library_name = library_name
        self.type = type
        self.tags = tags
        self.source_file = source_file

    def __str__(self):
        return f"{self.name}: a {self.type[:-1]} from {self.library_name} with tags: \n {self.tags}"

    def load(self):
        with bpy.data.libraries.load(str(self.source_file), assets_only=True) as (other_file, current_file):
            if self.name not in getattr(other_file, self.type):
                raise Exception(f"No asset with name {self.name} found in {self.source_file}.")
            getattr(current_file, self.type).append(self.name)
        return getattr(bpy.data, self.type)[self.name]


def cache_directory():
    return user_cache_dir("airo-blender-toolkit", "airo")


def load_blend_file_assets(blend_file):
    assets_to_be_processed = {asset_type: [] for asset_type in asset_types}
    with bpy.data.libraries.load(blend_file, assets_only=True) as (other_file, current_file):
        for asset_type in asset_types:
            for asset_name in getattr(other_file, asset_type):
                getattr(current_file, asset_type).append(asset_name)
                assets_to_be_processed[asset_type].append(asset_name)
    return assets_to_be_processed


def process_assets(assets_to_be_processed, library_name, blend_file):
    processed_assets = []
    for asset_type, asset_names in assets_to_be_processed.items():
        for asset_name in asset_names:
            bpy_data_collection = getattr(bpy.data, asset_type)
            asset = bpy_data_collection[asset_name]
            asset_info = Asset(
                asset_name,
                library_name,
                asset_type,
                [t.name for t in asset.asset_data.tags],
                str(blend_file),
            )
            processed_assets.append(asset_info)
            bpy_data_collection.remove(asset)
    return processed_assets


def list_blend_files(asset_library):
    library_path = Path(asset_library.path)
    blend_files = [str(path) for path in library_path.glob("**/*.blend") if path.is_file()]
    return blend_files


def rebuild_asset_cache():
    with Cache(cache_directory()) as cache:
        assets = []
        processed_blend_files = set()

        # adapted from: https://blender.stackexchange.com/questions/244971
        asset_libraries = bpy.context.preferences.filepaths.asset_libraries
        for asset_library in asset_libraries:
            blend_files = list_blend_files(asset_library)
            processed_blend_files.update(blend_files)
            for blend_file in blend_files:
                assets_to_be_processed = load_blend_file_assets(blend_file)
                processed_assets = process_assets(assets_to_be_processed, asset_library.name, blend_file)
                assets.extend(processed_assets)

        cache["processed_blend_files"] = processed_blend_files
        cache["assets"] = assets
        print(f"Cached the info of {len(assets)} assets.")


def asset_cache_outdated():
    with Cache(cache_directory()) as cache:
        if "processed_blend_files" not in cache:
            return True
        processed_blend_files = cache["processed_blend_files"]  # list of paths

    asset_blend_files = set()
    asset_libraries = bpy.context.preferences.filepaths.asset_libraries
    for asset_library in asset_libraries:
        blend_files = list_blend_files(asset_library)
        asset_blend_files.update(blend_files)

    return not (processed_blend_files == asset_blend_files)


def assets():
    if asset_cache_outdated():
        print("Rebuilding asset cache, this can take a while.")
        rebuild_asset_cache()

    with Cache(cache_directory()) as cache:
        return cache["assets"]


def filtered_assets(type, required_tags=[]):
    def filter_condition(asset):
        if asset.type != type:
            return False
        required_tags_present = all((required_tag in asset.tags) for required_tag in required_tags)
        return required_tags_present

    return [a for a in assets() if filter_condition(a)]


class World(BlenderObject):
    def __init__(self, required_tags=[]):
        assets = filtered_assets("worlds", required_tags)
        index = np.random.choice(len(assets))
        asset = assets[index]
        world = asset.load()
        bpy.context.scene.world = world
        self.blender_object = world


def load_thingi10k_object():
    pass
    # thingi_folder = os.path.join(assets_path(), "thingi10k")
    # random_object_name = get_random_filename(thingi_folder)
    # print(random_object_name)
    # bpy.ops.import_mesh.stl(filepath=os.path.join(thingi_folder, random_object_name))
    # obj = bpy.context.selected_objects[0]
    # bb_vertex = obj.matrix_world @ (Vector(obj.bound_box[6]) - Vector(obj.bound_box[0]))
    # bb_vertex = [abs(x) for x in bb_vertex]
    # obj.scale = np.array([0.1 / (bb_vertex[0]), 0.1 / (bb_vertex[1]), 0.1 / (bb_vertex[2])]) * np.random.uniform(
    #     0.5, 3.0
    # )
    # obj.location = (np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5), 0)
    # material = bpy.data.materials.new(name=random_object_name)
    # material.diffuse_color = random_hsv()
    # obj.data.materials.append(material)
