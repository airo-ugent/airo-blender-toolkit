from typing import Dict, List

import requests

base_url = "https://ambientCG.com/api/v2/full_json"
included_data = "include=downloadData,tagData,dimensionsData,imageData"
headers = {"User-Agent": "Mozilla/5.0"}

download_filetype = {"Material": "zip", "HDRI": "exr", "Terrain": "zip", "3DModel": "zip"}


def ambientcg_full_json(offset, limit):
    url = f"{base_url}?{included_data}&offset={offset}&limit={limit}"  # &type=Material
    response = requests.get(url, headers=headers)
    return response.json()


def assets_exhausted(full_json):
    return "foundAssets" not in full_json or len(full_json["foundAssets"]) == 0


def accumulate_found_assets():
    offset = 0
    limit = 100  # the maximum allowed by AmbientCG
    found_assets = []
    full_json = ambientcg_full_json(offset, limit)
    while not assets_exhausted(full_json):
        found_assets.extend(full_json["foundAssets"])
        offset += limit
        full_json = ambientcg_full_json(offset, limit)
        # break  # temp for faster debugging
    return found_assets


def select_download_folder(asset):
    asset_type = asset["dataType"]
    folders = asset["downloadFolders"]

    if asset_type in ["Material", "HDRI"]:
        return folders["default"]

    raise NotImplementedError(f"{asset_type} asset type is not supported yet.")


def select_download_filetype(asset: Dict) -> str:
    asset_type = asset["dataType"]
    if asset_type == "Material":
        return "zip"
    if asset_type == "HDRI":
        return "exr"

    raise NotImplementedError(f"{asset_type} asset type is not supported yet.")


def download_url(asset: Dict) -> str:
    asset_type = asset["dataType"]

    folder = select_download_folder(asset)
    filetype = select_download_filetype(asset)
    downloads = folder["downloadFiletypeCategories"][filetype]["downloads"]

    if asset_type == "Material":
        # print([d["attribute"] for d in downloads])
        # print("1K-JPG" in [d["attribute"] for d in downloads])

        # Example attribute: ['1K-JPG', '1K-PNG', '2K-JPG', '2K-PNG', '4K-JPG', '4K-PNG', '8K-JPG', '8K-PNG']
        attritubes = [d["attribute"] for d in downloads]
        print(asset["assetId"], attritubes)
        lowest_resolution = min([int(a.split("K-")[0]) for a in attritubes])
        print(lowest_resolution)

        # return download["fullDownloadPath"]

        # TODO I'm waiting for Blender to support importing USD materials, which should
        # be quite soon. (https://developer.blender.org/T97195)


# def clean_asset(asset):
#     raw_tags = asset["tags"]
#     tags = raw_tags if type(raw_tags) is list else list(raw_tags.values())

#     asset_cleaned = {"name": asset["assetId"], "tags": tags, "download_url": download_url(asset)}
#     return asset_cleaned


def available_assets() -> List[Dict]:
    found_assets = accumulate_found_assets()
    # assets_cleaned = [clean_asset(a) for a in found_assets]
    return found_assets


def download(asset: Dict):
    download_url(asset)


def convert_to_blender_asset(path, asset):
    pass


def processable_assets(assets):
    # 3DModel currently not included because downloadFolders naming is quite complex, sometimes there is a default, but
    # most of the time the folders are something like this ['HQ (50000 faces)', 'LQ (500 faces)', 'SQ (5000 faces)'].
    # However, sometimes there is no SQ option, and two HQ options.
    processable_types = ["Material", "HDRI"]  # , "3DModel"]
    return [a for a in assets if a["dataType"] in processable_types]


assets = available_assets()
processable = processable_assets(assets)

for asset in processable:
    path = download(asset)
    convert_to_blender_asset(path, asset)
