class RemoteSources:
    '''Remote sources represents a class objet that holds both a name
    remote address for a github repo whose releases will be available on demand.
    '''

    def __init__(self, name: str, remote: str) -> None:
        self.__repr__ = 'Class <RemoteSources>'
        self.name: str = name
        self.remote: str = remote
        self.remote_inventory: str = f"https://{remote}/releases/latest/download/inventory.json"

    @staticmethod
    def sourceFromBlock(block: callable):
        name: str = block.par.Name.eval()
        remote: str = block.par.Github.eval()
        return RemoteSources(name=name, remote=remote)
