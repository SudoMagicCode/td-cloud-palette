from cloudPaletteType import paletteType
from dataclasses import dataclass


class remoteTox:
    '''A Remote TOX object - data struct for moving around remote objects
    '''

    path: str = ""
    summary: str = ""
    type_tag: paletteType = paletteType.notYetAssigned
    display_name: str = ""
    tox_version: str = ""
    td_version: str = ""
    last_updated: str = ""
    asset_path: str = ""
    opFamilies: list = []
    opTypes: list = []

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
