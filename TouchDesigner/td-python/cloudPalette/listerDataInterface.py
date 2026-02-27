from enum import Enum

from cloudPaletteType import cloudPaletteTypes, cloudPaletteAsset

header_map: dict[str, str] = {
    'name': 'display_name',
    'path': 'lister_path',
    'author': 'author',
    'isTOX': 'is_tox',
    'isLocal': 'is_local',
    'asset_url': 'asset_url',
    'local_asset_path': 'asset_local_path',
    'assetType': 'asset_type',
    'TDVersion': 'tdVersion',
    'TOXVersion': 'toxVersion',
    'lastSaved': 'lastSaved',
    'warn': 'compatible',
    'hasCOMPs': 'has_COMPs',
    'hasTOPs': 'has_TOPs',
    'hasCHOPs': 'has_CHOPs',
    'hasSOPs': 'has_SOPs',
    'hasPOPs': 'has_POPs',
    'hasMATs': 'has_MATs',
    'hasDATs': 'has_DATs',
}


class TreeListerRow:
    def __init__(self):
        self.cloudAsset: cloudPaletteAsset

    @property
    def as_list(self) -> list:
        output_list = []
        for each in header_map.values():
            output_list.append(getattr(self.cloudAsset, each))
        return output_list

    @staticmethod
    def folder_row(data: dict):
        newRow = TreeListerRow()
        author: str = data.get('author')
        block: str = data.get('block')

        newRow.display_name = block if block != '' else author
        newRow.lister_path = f'creator/{author}/{block}' if block != '' else f'creator/{author}'
        newRow.assetType = cloudPaletteTypes.folder

        return newRow

    @staticmethod
    def from_github_response_folder_row(*args):
        newRow = TreeListerRow()
        newRow.author = args[0]
        newRow.display_name = args[-1]
        newRow.lister_path = f"creator/{'/'.join([each for each in args])}"
        newRow.assetType = cloudPaletteTypes.folder
        return newRow
