

class ManifestComponentCollection:
    def __init__(self, collection, instance_cls, base_manifest):
        self._instance_cls = instance_cls
        self._collection = collection
        self.base_manifest = base_manifest
        self.api = base_manifest.api

    def __getitem__(self, key):
        return self.instance_of(self._collection[str(key)])
    
    def __dir__(self):
        dynamic_attrs = [key for key in self._collection.keys()]
        return super().__dir__() + dynamic_attrs

    @property
    def keys(self):
        return [key for key in self._collection.keys()]

    def find(self, obj_name = None, types = None, trait = None, item_type = None, tier = None):
        inventory_bucket_type_hashes = None
        not_item_types = None
        not_item_category = None
        if types:
            if not inventory_bucket_type_hashes:
                inventory_bucket_type_hashes = list()
            if isinstance(types, str):
                types = [types]
            if 'weapon' in types:
                # These bucketTypeHash entries all have "equipmentCategoryHash": 1885559401 in DestinyEquipmentSlotDefinition
                # There also seem to be three instances of each weapon, but the real one has equippable: true
                # Power: 953998645
                # Energy: 2465295065
                # Kinetic: 1498876634
                inventory_bucket_type_hashes.extend([1498876634, 2465295065, 953998645])
                not_item_types = ['', None, 'Package', 'Weapon Ornament']
                not_item_category = 3109687656 # Dummies
            # TODO: what other bucket types are there?

        return [
            self.instance_of(self._collection[x])
            for x
            in self._collection.keys()
            if (
                inventory_bucket_type_hashes is None or 
                self._collection[x].get('inventory', {}).get('bucketTypeHash', []) in inventory_bucket_type_hashes
            ) and (
                not_item_types is None or
                self._collection[x].get('itemTypeDisplayName') not in not_item_types
            ) and (
                item_type is None or
                self._collection[x].get('itemTypeDisplayName') == item_type
            ) and (
                trait is None or
                trait in self._collection[x].get('traitIds', [])
            ) and (
                tier is None or
                self._collection[x].get('inventory', {}).get('tierTypeName') == tier
            ) and (
                not_item_category is None or
                not_item_category not in self._collection[x].get('itemCategoryHashes', ())
            ) and (
                obj_name is None or
                self._collection[x].get('displayProperties', {}).get('name') == obj_name
            )
        ]

    def socket_category_defaults(self, category: str, **find_params):
        return {
            item.socket_default_for_category(category)
            for item in self.find(**find_params)
        }

    def instance_of(self, manifest_element):
        return self._instance_cls(manifest_element, self.base_manifest)

    @property
    def weapons(self):
        return self.find(types='weapon')

    @property
    def weapon_traits(self):
        return {trait_id for x in self.weapons for trait_id in x.manifest.get('traitIds', [])}

    @property
    def weapons_with_trait(self, trait: str):
        return self.find(types='weapon', trait=trait)
        # return [w for w in self.weapons if trait in w.manifest.get('traitIds', [])]

    @property
    def weapon_frames(self):
        pass
        
    @property
    def frames_for_type(self, weapon_type: str):
        pass

    @property
    def weapon_types(self):
        return {w.manifest.get('itemTypeDisplayName') for w in self.weapons}
