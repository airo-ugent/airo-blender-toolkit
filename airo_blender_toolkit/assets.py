import os
import random
from pathlib import Path

import bpy
from appdirs import user_cache_dir
from diskcache import Cache

from airo_blender_toolkit.primitives import BlenderObject


def asset_identifier(asset_library_name, asset_type, asset_name):
    """A uniqie identifier for the asset. Assumes that no two assets in the same library have the same name."""
    return f"{asset_library_name} {asset_type} {asset_name}"


class Asset:
    def __init__(self, name, library_name, type, tags, source_file):
        self.name = name
        self.library_name = library_name
        self.type = type
        self.tags = tags
        self.source_file = source_file

    def __str__(self):
        return f"{self.name}: a {self.type[:-1]} from {self.library_name} with tags: \n {self.tags}"

    @property
    def id(self):
        return asset_identifier(self.library_name, self.type, self.name)

    def load(self):
        with bpy.data.libraries.load(str(self.source_file), assets_only=True) as (other_file, current_file):
            if self.name not in other_file.materials:
                raise Exception(f"No asset with name {self.name} found in {other_file}.")
            current_file.materials.append(self.name)
        return bpy.data.materials[self.name]


def cache_directory():
    return user_cache_dir("airo-blender-toolkit", "airo")


def update_asset_cache():
    with Cache(cache_directory()) as cache:
        # adapted from: https://blender.stackexchange.com/questions/244971
        asset_libraries = bpy.context.preferences.filepaths.asset_libraries

        if "assets" not in cache:
            cache["assets"] = {}

        if "blend_files" not in cache:
            cache["blend_files"] = set()

        asset_cache = cache["assets"]  # dictionary
        blend_file_cache = cache["blend_files"]  # list of paths

        # The 6 asset types in the filter dropdown in the Asset Browser
        asset_types = [
            "actions",
            "collections",
            "materials",
            "node_groups",
            "objects",
            "worlds",
        ]

        for asset_library in asset_libraries:
            library_name = asset_library.name
            library_path = Path(asset_library.path)
            blend_files = [str(path) for path in library_path.glob("**/*.blend") if path.is_file()]
            blend_file_cache.update(blend_files)
            for blend_file in blend_files:
                assets_to_be_processed = {asset_type: [] for asset_type in asset_types}
                with bpy.data.libraries.load(blend_file, assets_only=True) as (other_file, current_file):
                    for asset_type in asset_types:
                        for asset_name in getattr(other_file, asset_type):
                            asset_id = asset_identifier(library_name, asset_type, asset_name)
                            if asset_id not in asset_cache:
                                getattr(current_file, asset_type).append(asset_name)
                                assets_to_be_processed[asset_type].append(asset_name)

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
                        asset_cache[asset_info.id] = asset_info
                        bpy_data_collection.remove(asset)

        cache["blend_files"] = blend_file_cache
        cache["assets"] = asset_cache


def asset_cache_up_to_date():
    with Cache(cache_directory()) as cache:
        if "blend_files" not in cache:
            return False
        blend_file_cache = cache["blend_files"]  # list of paths

    asset_blend_files = []
    asset_libraries = bpy.context.preferences.filepaths.asset_libraries
    for asset_library in asset_libraries:
        library_path = Path(asset_library.path)
        blend_files = [str(path) for path in library_path.glob("**/*.blend") if path.is_file()]
        asset_blend_files.extend(blend_files)

    blend_files_changed = any(file not in blend_file_cache for file in asset_blend_files)
    return not blend_files_changed


def assets():
    if not asset_cache_up_to_date():
        print("Updating assets.")
        update_asset_cache()

    with Cache(cache_directory()) as cache:
        asset_cache = cache["assets"]
        assets = list(asset_cache.values())
    return assets


class World(BlenderObject):
    def __init__(self, required_tags=[]):
        pass
        # import_asset_worlds()
        # worlds = [w for w in bpy.data.worlds if w.asset_data]

        # worlds_with_required_tags = []
        # for world in worlds:
        #     tags = world.asset_data.tags
        #     if all((required_tag in tags) for required_tag in required_tags):
        #         worlds_with_required_tags.append(world)

        # index = np.random.choice(len(worlds_with_required_tags))
        # world = worlds_with_required_tags[index]

        # bpy.context.scene.world = world

        # self.blender_object = world


def get_random_filename(filedir):
    onlyfiles = [f for f in os.listdir(filedir) if os.path.isfile(os.path.join(filedir, f))]
    onlyfiles.sort()
    return random.choice(onlyfiles)


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
