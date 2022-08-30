import os
import random
from pathlib import Path

import bpy
from appdirs import user_cache_dir
from diskcache import Cache

from airo_blender_toolkit.primitives import BlenderObject


def asset_identifier(asset_library_name, asset_name):
    """A uniqie identifier for the asset. Assumes that no two assets in the same library have the same name."""
    return f"{asset_library_name} {asset_name}"


class Asset:
    def __init__(self, name, library_name, type, tags, source_file):
        self.name = name
        self.library_name = library_name
        self.type = type
        self.tags = tags
        self.source_file = source_file

    def __str__(self):
        return f"{self.name}: a {self.type} asset from {self.library_name} with tags: \n {self.tags}"

    @property
    def id(self):
        return asset_identifier(self.library_name, self.name)

    def load(self):
        with bpy.data.libraries.load(str(self.source_file), assets_only=True) as (other_file, current_file):
            if self.name not in other_file.materials:
                raise Exception(f"No asset with name {self.name} found in {other_file}.")
            current_file.materials.append(self.name)
        return bpy.data.materials[self.name]


def cache_directory():
    return user_cache_dir("airo-blender-toolkit", "airo")


def update_asset_cache():
    with Cache(cache_directory()) as asset_cache:
        # adapted from: https://blender.stackexchange.com/questions/244971
        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        # These are the result of printing dir(other_file) in the loop below.
        # ['Hair Curves', 'actions', 'armatures', 'brushes', 'cache_files', 'cameras', 'collections', 'curves',
        # 'fonts', 'grease_pencils', 'images', 'lattices', 'lightprobes', 'lights', 'linestyles', 'masks', 'materials',
        # 'meshes', 'metaballs', 'movieclips', 'node_groups', 'objects', 'paint_curves', 'palettes', 'particles',
        # 'pointclouds', 'scenes', 'screens', 'simulations', 'sounds', 'speakers', 'texts', 'textures', 'volumes',
        # 'workspaces', 'worlds']

        # The 6 asset types in the filter dropdown in the Asset Browser
        asset_types = [
            "action",
            "collections",
            "materials",
            "node_groups",
            "objects",
            "worlds",
        ]
        print(asset_types)

        for asset_library in asset_libraries:
            library_name = asset_library.name
            library_path = Path(asset_library.path)
            blend_files = [fp for fp in library_path.glob("**/*.blend") if fp.is_file()]
            print(f"Checking the content of library '{library_name}' :")
            for blend_file in blend_files:
                materials_to_be_processed = []
                with bpy.data.libraries.load(str(blend_file), assets_only=True) as (other_file, current_file):
                    for material_name in other_file.materials:
                        asset_id = asset_identifier(library_name, material_name)
                        if asset_id not in asset_cache:
                            current_file.materials.append(material_name)
                            materials_to_be_processed.append(material_name)

                for material_name in materials_to_be_processed:
                    material = bpy.data.materials[material_name]
                    asset = Asset(
                        material_name,
                        library_name,
                        "material",
                        [t.name for t in material.asset_data.tags],
                        str(blend_file),
                    )
                    asset_cache[asset.id] = asset
                    bpy.data.materials.remove(material)


def get_assets():
    update_asset_cache()
    with Cache(cache_directory()) as asset_cache:
        assets = [asset_cache[key] for key in list(asset_cache)]
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
