from src.manifest.component_parts import DisplayProperties


class ManifestComponent():
    def __init__(self, manifest, base_manifest):
        self._raw_manifest = manifest
        self.base_manifest = base_manifest

    @property
    def manifest(self):
        return self._raw_manifest

    @property
    def hash(self) -> int:
        return self.manifest.get('hash', None)
    
    @property
    def index(self) -> int:
        return self.manifest.get('index', None)
    
    @property
    def redacted(self) -> bool:
        return self.manifest.get('redacted', None)
    
    @property
    def blacklisted(self) -> bool:
        return self.manifest.get('blacklisted', None)

    @property
    def display_properties(self) -> DisplayProperties:
        if self.manifest.get('displayProperties', None) is None:
            return None
        return DisplayProperties(self.manifest.get('displayProperties', {}))

    @property
    def name(self) -> str:
        return self.display_properties.get('name', None)

    @property
    def stats(self):
        # stats.stats{}
        # investmentStats[].statTypeHash(DestinyStatDefinition)
        #   > displayProperties.name
        #   > value
        # collectibleHash(DestinyCollectibleDefinition)
        #   > stats.stats{}
        #     > __key(DestinyStatDefinition)
        #       > displayProperties.name
        #     > value
        #   also available is stats.statGroupHash(DestinyStatGroupDefinition), which gives value display interpolation ranges
        # investmentStats[].statTypeHash(DestinyStatDefinition)
        #   > displayProperties.Name
        if 'stats' not in self.manifest:
            raise NotImplementedError("Manifest object does not have key 'stats'")
        return {
            self.base_manifest.DestinyStatDefinition[k].manifest['displayProperties']['name']: self.manifest.get('stats').get('stats').get(k).get('value')
            for k
            in self.manifest.get('stats').get('stats')
        }

    @property
    def breaker_type(self) -> str:
        if 'breakerType' not in self.manifest:
            raise NotImplementedError("Manifest object does not have key 'breakerType'")

        match self.manifest.get('breakerType'):
            case 1:
                return 'Barrier'
            case 2:
                return 'Overload'
            case 3:
                return 'Unstoppable'
        return None

    @property
    def investment_stats(self):
        if 'investmentStats' not in self.manifest:
            raise NotImplementedError("Manifest object does not have key 'investmentStats'")
        return {
            self.base_manifest.DestinyStatDefinition[k.get('statTypeHash')].manifest['displayProperties']['name']: k.get('value')
            for i, k
            in enumerate(self.manifest.get('investmentStats'))
        }

    @property
    def sockets(self):
        if 'sockets' not in self.manifest:
            raise NotImplementedError("Manifest object does not have key 'sockets'")
        if 'socketEntries' not in self.manifest.get('sockets'):
            raise NotImplementedError("Manifest object does not have key 'sockets.socketEntries'")
        # Hydrate resulting dict with:
        # * socketType: socketTypeHash -> plugWhitelist -> str.join([].get('categoryIdentifier')) --OR-- build a static enum? --OR-- IGNORE
        # * socketCategory: socketTypeHash -> socketCategoryHash -> display_properties.name
        sockets = self.manifest.get('sockets').get('socketEntries').copy()
        for i, socket in enumerate(sockets):
            socket_type = api.manifest.DestinySocketTypeDefinition[socket.get('socketTypeHash')].manifest
            sockets[i]['socketType'] = socket_type
            socket_category = api.manifest.DestinySocketCategoryDefinition[socket['socketType'].get('socketCategoryHash')].manifest
            sockets[i]['socketType']['socketCategory'] = socket_category
            
            single_initial_item_hash = socket.get('singleInitialItemHash')
            if single_initial_item_hash:
                item = api.manifest.DestinyInventoryItemDefinition[single_initial_item_hash]
                item_name = item.display_properties.name
                sockets[i]['singleInitialItemName'] = item_name

            sockets[i]['randomizedPlugSet'] = {}
            randomized_plug_set_hash = socket.get('randomizedPlugSetHash')
            if randomized_plug_set_hash:
                rps = api.manifest.DestinyPlugSetDefinition[randomized_plug_set_hash]
                sockets[i]['randomizedPlugSet'] = {}
                for rpi in rps.manifest.get('reusablePlugItems'):
                    rpi_hash = rpi.get('plugItemHash')
                    sockets[i]['randomizedPlugSet'][rpi_hash] = {}
                    rpi_item_name = api.manifest.DestinyInventoryItemDefinition[rpi_hash].display_properties.name
                    sockets[i]['randomizedPlugSet'][rpi_hash]['name'] = rpi_item_name
                    can_roll = rpi.get('currentlyCanRoll')
                    sockets[i]['randomizedPlugSet'][rpi_hash]['currentlyCanRoll'] = can_roll

            sockets[i]['reusablePlugSet'] = {}
            reusable_plug_set_hash = socket.get('reusablePlugSetHash')
            if reusable_plug_set_hash:
                rps = api.manifest.DestinyPlugSetDefinition[reusable_plug_set_hash]
                sockets[i]['reusablePlugSet'] = {}
                for rpi in rps.manifest.get('reusablePlugItems'):
                    rpi_hash = rpi.get('plugItemHash')
                    sockets[i]['reusablePlugSet'][rpi_hash] = {}
                    rpi_item_name = api.manifest.DestinyInventoryItemDefinition[rpi_hash].display_properties.name
                    sockets[i]['reusablePlugSet'][rpi_hash]['name'] = rpi_item_name
                    can_roll = rpi.get('currentlyCanRoll')
                    sockets[i]['reusablePlugSet'][rpi_hash]['currentlyCanRoll'] = can_roll

        return sockets
        # socket_types = {
        #     x.get('socketTypeHash'):
        #     api.manifest.DestinySocketTypeDefinition[x.get('socketTypeHash')]
        #     for x
        #     in sockets
        # }
        # socket_categories = {
        #     socket_types[x].manifest.get('socketCategoryHash'):
        #     api.manifest.DestinySocketCategoryDefinition[socket_types[x].manifest.get('socketCategoryHash')].display_properties.name or 'Unknown'
        #     for x
        #     in socket_types.keys()
        # }
        # socket_types_by_category = {
        #     socket_categories[x]:
        #     [
        #         socket_types[y]
        #         for y
        #         in socket_types
        #         if socket_types[y].manifest.get('socketCategoryHash') == x
        #     ]
        #     for x
        #     in socket_categories.keys()
        # }

        # [
        #     (
        #         api.manifest.DestinySocketCategoryDefinition[api.manifest.DestinySocketTypeDefinition[x.get('socketTypeHash')].manifest.get('socketCategoryHash')].display_properties.name,
        #         api.manifest.DestinySocketTypeDefinition[x.get('socketTypeHash')].manifest.get('plugWhitelist'))
        #         for x
        #         in s.manifest.get('sockets').get('socketEntries')
        # ]

    @property
    def perk_pool(self):
        if 'sockets' not in self.manifest:
            raise NotImplementedEerror("Manifest object does not have key 'sockets'")
        # sockets.socketEntries(DestinySocketTypeDefinition)
        #   > randomizedPlugsetHash(DestinyPlugSetDefinition)
        #     > reusablePlugItems[].plugItemHash(DestinyInventoryItemDefinition)
        #       > displayProperties.name
        pass

    @property
    def accumulator_threshold(self) -> int:
        if 'accumulatorThreshold' not in self.manifest:
            raise NotImplementedError("Manifest object does not have key 'accumulatorThreshold'")
        return self.manifest.get('accumulatorThreshold', None)
    
    @property
    def platform_index(self) -> int:
        if 'platformIndex' not in self.manifest:
            raise NotImplementedError("Manifest object does not have key 'platformIndex'")
        return self.manifest.get('platformIndex', None)


# collectibleHash • DestinyCollectibleDefinition
# collectible > sourceString
# collectible > itemTypeDisplayName
# collectible > itemTypeAndTierDisplayName
# collectible > inventory.bucketTypeHash.displayProperties.name
# collectible > inventory.tierTypeHash.displayProperties.name
# collectible > stats.statGroupHash > ??? (maybe list of stat names from scaledStats?)
# collectible > stats.stats{}__key > displayProperties.name
# collectible > stats.stats{}.value
# collectible > stats.stats{}.minimum
# collectible > stats.stats{}.maximum
# collectible > stats.stats{}.displayMaximum
# collectible > primaryBaseStathash.displayProperties.name
# collectible > equippingBlock.equipmentSlotTypeHash.displayProperties.name
# collectible > quality.versions[] • DestinyItemTierTypeDefinitions.displayProperties.name
# collectible > sockets.socketEntries[].plugWhitelist{}.categoryIdentifier
# collectible > sockets.socketEntries[].socketTypeHash(DestinySocketTypeDefinition).plugWhitelist{}.socketCategoryHash(DestinySocketCategoryDefinition).displayProperties.name
# collectible > sockets.socketEntries[].singleInitialItemHash(DestinyInventoryItemDefinition).displayProperties.name
# collectible > sockets.socketEntries[].singleInitialItemHash(DestinyInventoryItemDefinition).displayProperties.name

# investmentStats[].statTypeHash • DestinyStatDefinition
# summaryItemHash • DestinyInventoryItemDefinition
# itemCategoryHashes[] • DestinyItemCategoryDefinition
# damageTypeHashes[] • DestinyDamageTypeDefinition
# defaultDamageTypeHash • DestinyDamageTypeDefinition
# traitHashes[] • DestinyTraitDefinition (see traitIds[] for names... this one has no names)
