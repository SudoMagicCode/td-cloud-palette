class RemoteSources:
    def __init__(self, name: str, remote: str) -> None:
        self.__repr__ = 'Class <RemoteSources>'
        self.name: str = name
        self.remote: str = remote

    @staticmethod
    def sourceFromBlock(block: callable):
        name: str = block.par.Name.eval()
        remote: str = block.par.Github.eval()
        return RemoteSources(name=name, remote=remote)
