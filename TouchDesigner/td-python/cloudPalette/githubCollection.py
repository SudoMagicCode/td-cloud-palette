
class githubCollection:
    def __init__(self):
        self.author: str = None
        self.source: str = None
        self.collection: list = []

    def to_dict(self) -> dict:
        '''returns a dictionary shaped object of the collection
        '''
        collection_dict: dict = {}
        collection_dict["author"] = self.author
        collection_dict["source"] = self.source
        collection_dict["collection"] = self.collection

        return collection_dict
