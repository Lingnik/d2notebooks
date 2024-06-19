

class ComponentCollection:
    def __init__(self, collection):
        self._collection = collection

    def __getitem__(self, key):
        print(f"Getting key: {key}")
        return self._collection[str(key)]
    
    def __dir__(self):
        dynamic_attrs = [key for key in self._collection.keys()]
        return super().__dir__() + dynamic_attrs
    

class DestinyAchievementDefinitionCollection(ComponentCollection):
    def __init__(self, collection):
        super().__init__(collection)
