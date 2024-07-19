

class ManifestComponentCollection:
    def __init__(self, collection, instance_cls, base_manifest):
        self._instance_cls = instance_cls
        self._collection = collection
        self._cache = {}
        self.base_manifest = base_manifest
        self.api = base_manifest.api

    def __getitem__(self, key):
        return self.instance_of(self._collection[str(key)])
    
    # This isn't actually useful, because the keys are numeric, making them an invalid attribute name:
    # def __dir__(self):
    #     dynamic_attrs = [key for key in self._collection.keys()]
    #     return super().__dir__() + dynamic_attrs

    @property
    def keys(self):
        if 'keys' not in self._cache.keys():
            self._cache['keys'] = [key for key in self._collection.keys()]
        return self._cache.get('keys')

    def find(self, obj_name = None, types=None, trait=None, item_type=None, tier=None, frame=None):
        inventory_bucket_type_hashes = None
        not_item_types = None
        not_item_category = None
        if types:
            if not inventory_bucket_type_hashes:
                inventory_bucket_type_hashes = list()
            if isinstance(types, str):
                types = [types]
            if 'weapon' in types:
                # These bucketTypeHashes have "equipmentCategoryHash": 1885559401 in DestinyEquipmentSlotDefinition:
                # Power: 953998645
                # Energy: 2465295065
                # Kinetic: 1498876634
                inventory_bucket_type_hashes.extend([1498876634, 2465295065, 953998645])
                # Some things that look like weapons, aren't. Rather than a "we want Linear Fusion Rifles, Hand
                # Cannons, [...]" filter, we exclude the ones that shouldn't be here. (In case a new type of weapon is
                # introduced someday.
                not_item_types = ['', None, 'Package', 'Weapon Ornament']
                # There's at least one item (an ornament) that looks like a weapon; its categories include "Dummies"
                not_item_category = 3109687656 # Dummies
                # There also seem to be three instances of each weapon, but the real one has equippable: true
                # But for now, the above filters seem to catch real weapons.
            # TODO: what other bucket types are there that would be interesting to provide?

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
            ) and (
                frame is None or
                self.instance_of(self._collection[x]).weapon_frame == frame
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
        if 'weapons' not in self._cache.keys():
            self._cache['weapons'] = self.find(types='weapon')
        return self._cache['weapons']

    @property
    def weapon_traits(self):
        if 'weapon_traits' not in self._cache.keys():
            self._cache['weapon_traits'] = {trait_id for x in self.weapons for trait_id in x.manifest.get('traitIds', [])}
        return self._cache['weapon_traits']

    def weapons_with_trait(self, trait: str):
        return self.find(types='weapon', trait=trait)

    def weapon_frames_for_type(self, weapon_type: str, **find_params):
        # TODO: caching here, but **find_params makes this tricky
        return {
            item.weapon_frame
            for item in self.find(types='weapon', **find_params)
            if item.item_type == weapon_type
        }

    @property
    def weapon_types(self):
        if 'weapon_types' not in self._cache.keys():
            self._cache['weapon_types'] = {w.manifest.get('itemTypeDisplayName') for w in self.weapons}
        return self._cache.get('weapon_types')

    @property
    def weapon_types_and_frames(self):
        if 'weapon_types_and_frames' not in self._cache.keys():
            self._cache['weapon_types_and_frames'] = {weapon_type: self.weapon_frames_for_type(weapon_type, tier='Legendary') for weapon_type in self.weapon_types}
        return self._cache['weapon_types_and_frames']
