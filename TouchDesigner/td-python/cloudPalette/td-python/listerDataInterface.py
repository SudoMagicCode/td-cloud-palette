from enum import Enum

header_row = [
    'name',
    'path',
    'isTOX',
    'isLocal',
    'local_asset_path',
    'asset_url',
    'assetType',
    'TDVersion',
    'TOXVersion',
    'lastSaved',
    'warn',
    'hasCOMPs',
    'hasTOPs',
    'hasCHOPs',
    'hasSOPs',
    'hasPOPs',
    'hasMATs',
    'hasDATs'
]


class cloudPaletteType(Enum):
    notYetAssigned = 'empty'
    folder = 'folder'
    tdComp = 'tdComp'
    tdTemplate = 'tdTemplate'


class TreeListerRow:
    def __init__(self):
        self.display_name: str = ''
        self.lister_path: str = ''
        self.is_tox: bool = False
        self.is_local: bool = False
        self.asset_url: str = ''
        self.asset_local_path: str = ''
        self.assetType: cloudPaletteType = cloudPaletteType.notYetAssigned
        self.tdVersion: str = ''
        self.toxVersion: str = ''
        self.lastSaved: str = ''
        self.compatible: bool = None
        self.opFamilies: list = []
        self.opTypes: list = []

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
    def as_list(self) -> list:
        row_list = [
            self.display_name,
            self.lister_path,
            self.is_tox,
            self.is_local,
            self.asset_local_path,
            self.asset_url,
            self.assetType.value,
            self.tdVersion,
            self.toxVersion,
            self.lastSaved,
            self.compatible,
            self.has_COMPs,
            self.has_TOPs,
            self.has_CHOPs,
            self.has_SOPs,
            self.has_POPs,
            self.has_MATs,
            self.has_DATs
        ]
        return row_list


class RowBuilderFactory:
    def __init__(self):
        pass

    def _type_string_to_type(self, typeString: str) -> cloudPaletteType:
        type_map = {
            'template': cloudPaletteType.tdTemplate,
            'tdComp': cloudPaletteType.tdComp,
            'File folder': cloudPaletteType.folder,
            'TouchDesigner Component': cloudPaletteType.tdComp
        }
        return type_map.get(typeString, cloudPaletteType.notYetAssigned)

    def _check_compatible(self, tdVersionString: str) -> bool:
        return tdVersionString != f'{app.version}.{app.build}'

    def Build_folder_row(self, data: dict) -> TreeListerRow:
        newRow = TreeListerRow()
        author: str = data.get('author')
        block: str = data.get('block')

        newRow.display_name = block if block != '' else author
        newRow.lister_path = f'creator/{author}/{block}' if block != '' else f'creator/{author}'
        newRow.assetType = cloudPaletteType.folder

        return newRow

    def Build_row_from_api_response(self, data: dict) -> TreeListerRow:
        # create new row
        newRow = TreeListerRow()

        # pull data from incoming object
        td_version: str = data.get('asset_data').get('td_version', 'Unknown')
        tox_version: str = data.get(
            'asset_data').get('tox_version', 'Unknown')
        author: str = data.get('author')
        block: str = data.get('block')
        asset_path: str = data.get('asset_data').get('asset_path', '')
        asset_name: str = data.get(
            'asset_data').get('display_name', 'Unnamed')
        type_string: str = data.get('asset_data').get('type')
        last_saved: str = data.get('asset_data').get(
            'last_updated', 'Unknown')
        op_families: list = data.get('asset_data').get('opFamilies', [])
        op_types: list = data.get('asset_data').get('opTypes', [])
        base_uri: str = data.get('base_uri', '')

        # assign attributes to newRow object
        newRow.display_name = asset_name
        newRow.lister_path = f'creator/{author}/{block}/{asset_name}'
        newRow.is_tox = True
        newRow.is_local = False
        newRow.asset_url = f'{base_uri}latest/{asset_path}'
        newRow.assetType = self._type_string_to_type(type_string)
        newRow.tdVersion = td_version
        newRow.toxVersion = tox_version
        newRow.lastSaved = last_saved
        newRow.compatible = self._check_compatible(td_version)
        newRow.opFamilies = op_families
        newRow.opTypes = op_types
        return newRow

    def Build_row_from_folder_dat(self, headerLookupMap: dict, data: dict) -> TreeListerRow:
        source_data = data.get('source_data')
        author: str = data.get('author')
        display_name: str = source_data[headerLookupMap.get('basename')].val
        type_from_folder: str = source_data[headerLookupMap.get('type')].val
        rel_path: str = source_data[headerLookupMap.get('relpath')].val
        local_path: str = source_data[headerLookupMap.get('path')].val

        split_rel_path = rel_path.split('/')

        asset_type: cloudPaletteType = self._type_string_to_type(
            type_from_folder)

        if asset_type == cloudPaletteType.folder:
            # create a folder row
            folder_row_data: dict = {
                'author': author,
                'block': rel_path
            }

            # create a new folder row
            newRow = self.Build_folder_row(folder_row_data)
            newRow.is_local = True

        else:
            # create a new asset row
            newRow = TreeListerRow()

            block_element = '.'.join(split_rel_path[:-1])

            newRow.is_tox = True if newRow.assetType.value != 'folder' else False
            newRow.display_name = display_name
            newRow.is_local = True
            newRow.asset_local_path = local_path
            newRow.assetType = asset_type

            newRow.lister_path = f'creator/{author}/{rel_path}/{display_name}'

        return newRow
