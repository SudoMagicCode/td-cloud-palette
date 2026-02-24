from cloudPaletteType import cloudPaletteTypes


class remoteTox:
    '''A Remote TOX object - data struct for moving around remote objects
    '''

    def __init__(self):
        self.path: str = ""
        self.summary: str = ""
        self.type_tag: cloudPaletteTypes = cloudPaletteTypes.notYetAssigned
        self.display_name: str = ""
        self.tox_version: str = ""
        self.td_version: str = ""
        self.last_updated: str = ""
        self.asset_path: str = ""
        self.opFamilies: list = []
        self.opTypes: list = []

    def to_dict(self) -> dict:
        '''Dictionary representation of remoteTox object
        '''
        info: dict = {
            "path": self.path,
            "summary": self.summary,
            'type': self.type_tag.name,
            'display_name': self.display_name,
            'tox_version': self.tox_version,
            'last_updated': self.last_updated,
            'td_version': self.td_version,
            'asset_path': self.asset_path,
            'opFamilies': self.opFamilies,
            'opTypes': self.opTypes,
        }
        return info
