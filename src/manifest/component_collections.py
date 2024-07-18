

class ManifestComponentCollection:
    def __init__(self, collection, instance_cls, base_manifest):
        self._instance_cls = instance_cls
        self._collection = collection
        self.base_manifest = base_manifest

    def __getitem__(self, key):
        return self.instance_of(self._collection[str(key)])
    
    def __dir__(self):
        dynamic_attrs = [key for key in self._collection.keys()]
        return super().__dir__() + dynamic_attrs

    @property
    def keys(self):
        return [key for key in self._collection.keys()]

    def find_by_name(self, obj_name):
        return [
            self.instance_of(self._collection[x])
            for x
            in self._collection.keys()
            if self._collection[x].get('displayProperties').get('name') == obj_name
        ]

    def instance_of(self, manifest_element):
        return self._instance_cls(manifest_element, self.base_manifest)

    @property
    def weapons(self):
        # These bucketTypeHash entries all have "equipmentCategoryHash": 1885559401 in DestinyEquipmentSlotDefinition
        return [
            self.instance_of(self._collection[x])
            for x
            in self._collection.keys()
            if
                self._collection[x].get('inventory').get('bucketTypeHash') in (1498876634, 2465295065, 953998645)
                and self._collection[x].get('itemTypeDisplayName') not in ('', None, 'Package', 'Weapon Ornament')
        ]
