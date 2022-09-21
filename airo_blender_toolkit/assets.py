""" Module that provides an API for the Blender Asset Browser.
It works by first building a cache of all available assets.
This is slow (e.g. 15s for the Poly Haven Assets) because it requires opening all Blend files with assets.
However this only happens when the names of the Blend files present in the Asset Libraries change.
To force the cache to update, delete the ~/.cache/airo-blender-toolkit folder.

After the cache if built, it can be used to filter assets by type and tags.
The chosen assets can then easily be loaded with asset.load()
"""

import time
from pathlib import Path
from typing import Dict, List

import bpy
import numpy as np
from appdirs import user_cache_dir
from diskcache import Cache

from airo_blender_toolkit.cleanup import remove_orphan_data
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
    """This class contains the information needed to filter and load an Asset from disk."""

    def __init__(self, name, library_name, type, tags, source_file):
        self.name = name
        self.library_name = library_name
        self.type = type
        self.tags = tags
        self.source_file = source_file

    def __str__(self):
        return f"{self.name}: a {self.type[:-1]} from {self.library_name} with tags: \n {self.tags}"

    def load(self):
        """Load the Asset from disk into the open Blend file.

        Returns:
            The raw Blender datablock that was loaded.
        """

        datablocks_typed = getattr(bpy.data, self.type)
        names_before = set([data.name for data in datablocks_typed])

        with bpy.data.libraries.load(str(self.source_file), assets_only=True) as (
            datablocks_source,
            datablocks_destination,
        ):
            if self.name not in getattr(datablocks_source, self.type):
                raise Exception(f"No asset with name {self.name} found in {self.source_file}.")
            getattr(datablocks_destination, self.type).append(self.name)

        names_after = set([data.name for data in datablocks_typed])
        new_name = names_after - names_before
        assert len(new_name) == 1
        new_name = new_name.pop()
        datablock_new = datablocks_typed[new_name]

        if self.type == "objects":  # alternative:   for obj in datablocks_destination.objects:
            bpy.context.scene.collection.objects.link(datablock_new)

        datablock_new.asset_clear()  # Remove the asset mark for this file
        return datablock_new


def cache_directory():
    return user_cache_dir("airo-blender-toolkit", "airo")


def load_blend_file_assets(blend_file: str) -> Dict[str, List[str]]:
    """Load all the assets from a given Blend file into the current.

    Args:
        blend_file (str): Blend file from which the assets will be loaded.

    Returns:
        dict: a dictoionary with the assets that were loaded, stored in lists per asset type.
    """
    assets_to_be_processed = {asset_type: [] for asset_type in asset_types}
    with bpy.data.libraries.load(blend_file, assets_only=True) as (other_file, current_file):
        for asset_type in asset_types:
            for asset_name in getattr(other_file, asset_type):
                getattr(current_file, asset_type).append(asset_name)
                assets_to_be_processed[asset_type].append(asset_name)
    return assets_to_be_processed


def process_assets(assets_to_be_processed: Dict[str, List[str]], library_name: str, blend_file: str) -> List[Asset]:
    """Processes assets into Asset objects that can be cached. At the end the assets are removed from the current blend
    file to free up memory.

    Args:
        assets_to_be_processed (Dict[str, List[str]]): output of load_blend_file_assets(blend_file)
        library_name (str): name of the Asset Library the assets belong to
        blend_file (str): name of the Blend file where the assets come from

    Returns:
        List[Asset]: list of the extracted Assets
    """
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
            remove_orphan_data()  # this removes the default scene when the cache is updated :/
    return processed_assets


def list_blend_files(asset_library: str) -> List[str]:
    """Recursively list all blend file in a directory.

    Args:
        asset_library (str): The top-level directory of wehre to start searching.

    Returns:
        List[str]: paths to the blend files
    """
    library_path = Path(asset_library.path)
    blend_files = [str(path) for path in library_path.glob("**/*.blend") if path.is_file()]
    return blend_files


def rebuild_asset_cache():
    """Replace the old asset cache with the new one. The asset cache contains a list this the info of all found assets
    and also a list with the blend file in which these assets where found.
    """
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
    """Checks whether the cached blend files match with the blend files found in the Asset Libraries.

    Returns:
        bool: whether the cache is outdated.
    """
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


def assets() -> List[Asset]:
    """Returns a list with all the assets that where found in the Asset libraries.

    Returns:
        List[Asset]: The list of assets.
    """

    with Cache(cache_directory()) as cache:
        return cache["assets"]


def filtered_assets(type: str, required_tags: List[str] = []) -> List[Asset]:
    """Filters through all assets and returns those with required type and tags.

    Args:
        type (str): the type of asset to return, one of: actions, collections, materials, node_groups, objects, worlds.
        required_tags (List[str], optional): The tags that are required for all returned assets. Defaults to [].

    Returns:
        List[Asset]: List of the assets that match the requirements.
    """

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


def assets_with_required_tags(assets, required_tags=[]):
    results = []
    for asset in assets:
        tags = asset.tags
        if all((required_tag in tags) for required_tag in required_tags):
            results.append(asset)
    return results


# Update asses cache on module import
if asset_cache_outdated():
    start = time.time()
    print("airo-blender-toolkit: Rebuilding asset cache, this can take a while.")
    rebuild_asset_cache()
    print(f"airo-blender-toolkit: Asset cache has been rebuilt in {time.time() - start:.2f} seconds.")
