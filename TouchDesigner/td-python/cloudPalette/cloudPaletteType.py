from dataclasses import dataclass, field
from enum import Enum


class paletteType(Enum):
    notYetAssigned = 'empty'
    folder = 'folder'
    tdComp = 'tdComp'
    tdTemplate = 'tdTemplate'


class elementType(Enum):
    asset = 'asset'
    collection = 'collection'


def _check_compatible(tdVersionString: str) -> bool:
    return tdVersionString != f'{app.version}.{app.build}'


def _type_string_to_type(typeString: str) -> paletteType:
    type_map = {
        paletteType.tdTemplate.name: paletteType.tdTemplate,
        paletteType.tdComp.name: paletteType.tdComp,
        paletteType.folder.name: paletteType.folder,
        paletteType.tdComp.name: paletteType.tdComp
    }
    return type_map.get(typeString, paletteType.notYetAssigned)


@dataclass
class cloudPaletteElement:
    author: str
    source: str
    elementType: elementType


@dataclass
class cloudPaletteAsset(cloudPaletteElement):
    display_name: str
    lister_path: str
    asset_url: str
    asset_local_path: str
    tdVersion: str
    toxVersion: str
    lastSaved: str
    is_tox: bool
    assetType: paletteType = paletteType.notYetAssigned
    is_local: bool = False
    compatible: bool = False
    elementType = elementType.asset
    opFamilies: list = field(default_factory=list)
    opTypes: list = field(default_factory=list)

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

    @staticmethod
    def from_github_response(data: dict, author: str, source: str, root: str, subDir: str):

        raw_name: str = data.get("display_name", "unknown")
        raw_asset_path: str = data.get("asset_path")
        raw_lister_path: str = data.get("path", "unknown")

        asset_path_elements = raw_asset_path.split('/')

        asset_name: str = raw_name.replace('\n', ' ')
        lister_path: str = raw_lister_path.replace('\n', ' ')
        asset_path: str = "" if data.get(
            "asset_path") == None else f'https://{source}/releases/latest/download/{raw_asset_path}'
        td_version: str = data.get("td_version", "")
        tox_version: str = data.get("tox_version", "")
        last_saved: str = data.get("last_updated", "")
        op_fam: list = data.get("opFamilies", [])
        op_types: list = data.get("opTypes", [])
        asset_type = _type_string_to_type(data.get("type"))
        is_compatible = None if asset_type == paletteType.folder else _check_compatible(
            td_version)
        l_path = f"{root}/{subDir}/{lister_path}"
        path_on_disk = f"{'/'.join(l_path.split('/')[:-1])}/{asset_path_elements[-1]}"

        isTox = True if asset_type in [
            paletteType.tdComp, paletteType.tdTemplate] else False

        # assign attributes to newRow object
        newAsset = cloudPaletteAsset(
            source=source,
            author=author,
            elementType=elementType.asset,
            display_name=asset_name,
            lister_path=l_path,
            asset_local_path=path_on_disk,
            is_local=False,
            is_tox=isTox,
            asset_url=asset_path,
            assetType=asset_type,
            tdVersion=td_version,
            toxVersion=tox_version,
            lastSaved=last_saved,
            compatible=is_compatible,
            opFamilies=op_fam,
            opTypes=op_types
        )

        return newAsset


@dataclass
class cloudPaletteCollection(cloudPaletteElement):
    root: str
    sub_dir: str
    elementType = elementType.collection
    collection: list[cloudPaletteAsset] = field(default_factory=list)

    @staticmethod
    def from_json(info: dict, remoteSources: dict, root: str):
        author = info.get('author', 'unknown')
        source = info.get('source', 'unknown')
        elements: list[cloudPaletteAsset] = []
        sub_dir = remoteSources.get(source, '')
        for each in info.get('collection', []):
            new_cloud_palette_asset = cloudPaletteAsset.from_github_response(
                data=each,
                author=author,
                source=source,
                root=root,
                subDir=sub_dir)

            elements.append(new_cloud_palette_asset)

        new_collection = cloudPaletteCollection(
            elementType=elementType.collection,
            sub_dir=sub_dir,
            author=author,
            source=source,
            root='',
            collection=elements)

        return new_collection
