from enum import Enum
from dataclasses import dataclass


class cloudPaletteTypes(Enum):
    notYetAssigned = 'empty'
    folder = 'folder'
    tdComp = 'tdComp'
    tdTemplate = 'tdTemplate'


def _check_compatible(tdVersionString: str) -> bool:
    return tdVersionString != f'{app.version}.{app.build}'


def _type_string_to_type(typeString: str) -> cloudPaletteTypes:
    type_map = {
        cloudPaletteTypes.tdTemplate.name: cloudPaletteTypes.tdTemplate,
        cloudPaletteTypes.tdComp.name: cloudPaletteTypes.tdComp,
        cloudPaletteTypes.folder.name: cloudPaletteTypes.folder,
        cloudPaletteTypes.tdComp.name: cloudPaletteTypes.tdComp
    }
    return type_map.get(typeString, cloudPaletteTypes.notYetAssigned)


@dataclass
class cloudPaletteAsset:

    display_name: str = ''
    author: str = ''
    lister_path: str = ''
    is_tox: bool = False
    is_local: bool = False
    asset_url: str = ''
    asset_local_path: str = ''
    assetType: cloudPaletteTypes = cloudPaletteTypes.notYetAssigned
    tdVersion: str = ''
    toxVersion: str = ''
    lastSaved: str = ''
    compatible: bool = None
    opFamilies: list = []
    opTypes: list = []

    @property
    def has_COMPs(self) -> bool:
        return 'COMP' in self.opFamilies

    @property
    def has_TOPs(self) -> bool:
        return 'TOP' in self.opFamilies

    @property
    def has_CHOPs(self) -> bool:
        return 'CHOP' in self.opFamilies

    @property
    def has_SOPs(self) -> bool:
        return 'SOP' in self.opFamilies

    @property
    def has_POPs(self) -> bool:
        return 'POP' in self.opFamilies

    @property
    def has_MATs(self) -> bool:
        return 'MAT' in self.opFamilies

    @property
    def has_DATs(self) -> bool:
        return 'DAT' in self.opFamilies

    @property
    def asset_type(self) -> str:
        return self.assetType.name

    @property
    def is_tox(self) -> bool:
        True if self.assetType in [
            cloudPaletteTypes.tdComp, cloudPaletteTypes.tdTemplate] else False

    @staticmethod
    def from_api_response(data: dict):
        # create new row
        newPaletteAsset = cloudPaletteAsset()

        # pull data from incoming object
        td_version: str = data.get('asset_data').get('td_version', 'Unknown')
        tox_version: str = data.get('asset_data').get('tox_version', 'Unknown')
        author: str = data.get('author', '')
        block: str = data.get('block', '')
        asset_path: str = data.get('asset_data').get('asset_path', '')
        asset_name: str = data.get('asset_data').get('display_name', 'Unnamed')
        type_string: str = data.get('asset_data').get('type')
        last_saved: str = data.get('asset_data').get('last_updated', 'Unknown')
        op_families: list = data.get('asset_data').get('opFamilies', [])
        op_types: list = data.get('asset_data').get('opTypes', [])
        base_uri: str = data.get('base_uri', '')

        # assign attributes to newRow object
        newPaletteAsset.display_name = asset_name
        newPaletteAsset.author = author
        newPaletteAsset.lister_path = f'creator/{author}/{block}/{asset_name}'
        newPaletteAsset.is_local = False
        newPaletteAsset.asset_url = f'{base_uri}latest/{asset_path}'
        newPaletteAsset.assetType = _type_string_to_type(type_string)
        newPaletteAsset.tdVersion = td_version
        newPaletteAsset.toxVersion = tox_version
        newPaletteAsset.lastSaved = last_saved
        newPaletteAsset.compatible = _check_compatible(td_version)
        newPaletteAsset.opFamilies = op_families
        newPaletteAsset.opTypes = op_types
        return newPaletteAsset

    @staticmethod
    def from_github_response(data: dict, author: str, source: str, sourceMap: dict):
        newAsset = cloudPaletteAsset
        sub_path: str = sourceMap.get(source)

        raw_name: str = data.get("display_name", "unknown")
        asset_name: str = raw_name.replace('\n', ' ')
        lister_path: str = data.get("path", "unknown")
        asset_path: str = "" if data.get(
            "asset_path") == None else f'https://{source}/releases/latest/download/{data.get("asset_path")}'
        td_version: str = data.get("td_version", "")
        tox_version: str = data.get("tox_version", "")
        last_saved: str = data.get("last_updated", "")
        opFam: list = data.get("opFamilies", [])
        opTypes: list = data.get("opTypes", [])
        asset_type = _type_string_to_type(data.get("type"))
        isCompatible = None if asset_type == cloudPaletteTypes.folder else _check_compatible(
            td_version)

        # assign attributes to newRow object
        newAsset.display_name = asset_name
        newAsset.author = author
        newAsset.lister_path = f"creator/{author}/{sub_path}/{lister_path}"
        newAsset.is_local = False
        newAsset.asset_url = asset_path
        newAsset.assetType = asset_type
        newAsset.tdVersion = td_version
        newAsset.toxVersion = tox_version
        newAsset.lastSaved = last_saved
        newAsset.compatible = isCompatible
        newAsset.opFamilies = opFam
        newAsset.opTypes = opTypes
        return newAsset
