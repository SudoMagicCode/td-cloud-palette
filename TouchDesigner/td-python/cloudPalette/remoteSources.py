from dataclasses import dataclass
import cloudPaletteType

# Strict translation layer from web app that outputs invio files


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

# data layer useful to cloud palette


@dataclass
class RemoteSource:
    '''Remote sources represents a class objet that holds both a name
    remote address for a github repo whose releases will be available on demand.
    '''
    name: str
    remote: str
    author: str
    collection_name: str
    paletteCollection: cloudPaletteType.cloudPaletteCollection = None

    @property
    def remote_inventory(self) -> str:
        return f"https:/{self.remote}/releases/latest/download/inventory.json"

    def __repr__(self) -> str:
        return 'Class <RemoteSource>'

    @staticmethod
    def fromInvioSource(collection: str, source: InvioSource):
        name = source.name
        remote = source.link
        author = remote.split('/')[1]

        return RemoteSource(
            name=name,
            remote=remote,
            author=author,
            collection_name=collection)


@dataclass
class RemoteCollection:
    name: str
    sources: list[RemoteSource]

    def __repr__(self) -> str:
        return 'Class <RemoteCollection>'

    @staticmethod
    def fromInvioCollection(invio: InvioCollection):
        print("------------- > creating collection")
        remoteSources = []
        name: str = invio.name

        for each in invio.sources:
            newSource: RemoteSource = RemoteSource.fromInvioSource(
                name, each)
            remoteSources.append(newSource)

        newCollection = InvioCollection(
            name=name,
            sources=remoteSources)

        return newCollection
