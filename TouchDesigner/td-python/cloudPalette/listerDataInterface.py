from dataclasses import dataclass
import cloudPaletteType

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


@dataclass
class TreeListerRow:
    root: str


@dataclass
class AssetRow(TreeListerRow):
    cloudAsset: cloudPaletteType.cloudPaletteAsset

    @property
    def as_list(self) -> list:
        output_list = []

        for each in header_map.values():
            val = getattr(self.cloudAsset, each)
            output_list.append(val)

        return output_list


class FolderRow(TreeListerRow):
    cloudAsset: cloudPaletteType.cloudPaletteCollection

    @property
    def as_list(self) -> list:
        return [
            self.cloudAsset.sub_dir,
            f'{self.cloudAsset.author}/{self.cloudAsset.sub_dir}',
            self.cloudAsset.author,
            False,
            False,
            None,
            None,
            cloudPaletteType.paletteType.folder.name,
        ]


class AuthorRow(TreeListerRow):

    @property
    def as_list(self) -> list:
        return [
            self.root,
            self.root,
            self.root,
            False,
            False,
            None,
            None,
            cloudPaletteType.paletteType.folder.name,
        ]
