from dataclasses import dataclass


@dataclass
class InvioSource:
    name: str
    link: str

    def __repr__(self) -> str:
        return 'Class <CloudPaletteSource>'

    @staticmethod
    def fromJson(json: dict):
        newSource = InvioSource(name=json.get(
            'name', 'unnamed'), link=json.get('link', ''))
        return newSource


@dataclass
class InvioCollection:
    name: str
    sources: list[InvioSource]

    def __repr__(self) -> str:
        return 'Class <CloudPaletteCollection>'

    @staticmethod
    def fromJson(json: dict):
        print("------------- > creating collection")
        remoteSources = []
        name: str = json.get('name', 'unnamed')

        for each in json.get('sources', []):
            newSource: InvioSource = InvioSource.fromJson(each)
            remoteSources.append(newSource)

        newCollection = InvioCollection(
            name=name, sources=remoteSources)

        return newCollection


@dataclass
class RemoteSource:
    '''Remote sources represents a class objet that holds both a name
    remote address for a github repo whose releases will be available on demand.
    '''
    name: str
    remote: str
    author: str

    @property
    def remote_inventory(self) -> str:
        return f"https:/{self.remote}/releases/latest/download/inventory.json"

    def __repr__(self) -> str:
        return 'Class <RemoteSource>'

    @staticmethod
    def fromInvioSource(source: InvioSource):
        name: str = source.name
        remote: str = source.link
        author: str = remote.split('/')[1]
        return RemoteSource(name=name, remote=remote, author=author)
