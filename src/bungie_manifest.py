import os
from datetime import datetime
from src.settings import CACHE_MAX_AGE_HOURS
from src.manifest import COMPONENTS
from src.manifest.component_collections import ManifestComponentCollection
from src.manifest.components import ManifestComponent


def create_instance_class(name):
    return type(f'{name}Instance', (ManifestComponent,), {})


def create_collection_class(name):
    return type(f'{name}Collection', (ManifestComponentCollection,), {})


class BungieManifest:
    def __init__(self, api):
        self.api = api
        self.cached_version = None
        self.manifest_keys = {} # {'<friendly_name>': '<request_path>'}
        self.manifest = {} # Collection of deserialized Bungie manifests
        self.components = {} # { 'DestinyInventoryItemDefinition': [<cls_collection>, <cls_instance>, <obj_collection>], ... }

    def __getattr__(self, name):
        full_name = f"jsonWorldComponentContentPaths.{name}"
        if full_name in list(self.manifest_keys.keys()):
            component = self.components.get(full_name)
            # Lazy-load collection instance
            collection = component[0](self.manifest[f"jsonWorldComponentContentPaths.{name}"], component[1], self)
            component[2] = collection
            return collection
        raise AttributeError(f"'BungieManifest' object has no dynamic attribute '{name}'") 

    def _fetch_and_cache(self, key, request_path, response_key, bust_cache, manifest_data=None):
        if not manifest_data:
            response = self.api.request(request_path, use_cache=True, bust_cache=bust_cache)
            manifest_data = response[response_key]
        self.manifest_keys[key] = request_path
        self.manifest[key] = manifest_data
        # [2] is lazy-loaded in __getattr__, so omitted here
        self.components[key] = [create_collection_class(key), create_instance_class(key), None]
        return manifest_data
    
    def cache_manifests(self, bust_cache: bool=False) -> None:
        print("+bungie_manifest.BungieManifest.cache_manifests()")
        manifest = self.api.request('/Platform/Destiny2/Manifest/', use_cache=True, bust_cache=bust_cache).get('json')

        if self.cached_version or self.manifest_keys:
            print("The manifests were previously cached")
            if self.cached_version != manifest['Response']['version']:
                print("Busting cache as the core manifest version has changed")
                for key in self.manifest_keys:
                    print(f"- Pruning {key}")
                    self.api.prune_cache(key)
        if 'Response' not in manifest:
            raise Exception("Manifest fetch failed")
        mresponse = manifest['Response']
        self.cached_version = mresponse['version']

        print("Requesting manifest pieces...")
        self._fetch_and_cache('Manifest', '/Platform/Destiny2/Manifest/', 'json', bust_cache, manifest_data=manifest)

        # JSON files. You probably want these.
        # self._fetch_and_cache('jsonWorldContentPaths', mresponse['jsonWorldContentPaths']['en'], 'json', bust_cache)

        for key, value in mresponse['jsonWorldComponentContentPaths']['en'].items():
            self._fetch_and_cache(f"jsonWorldComponentContentPaths.{key}", value, 'json', bust_cache)

        # SQLite databases used by the mobile app. Some may have content not available otherwise.
        # self._fetch_and_cache('mobileAssetContentPath', mresponse['mobileAssetContentPath'], 'content', bust_cache)

        # for version in mresponse['mobileGearAssetDataBases']:
        #     self._fetch_and_cache(f"mobileGearAssetDataBases.{version['version']}", version['path'], 'content', bust_cache)

        # This database seems to contain 71 objects that mostly align with jsonWorldContentPaths.
        # self._fetch_and_cache('mobileWorldContentPaths', mresponse['mobileWorldContentPaths']['en'], 'content', bust_cache)

        # self._fetch_and_cache('mobileClanBannerDatabasePath', mresponse['mobileClanBannerDatabasePath'], 'content', bust_cache)

        # These return 403 Forbidden:
        # print("Caching mobileGearCDN")
        # for key, value in response['mobileGearCDN'].items():
        #     print(f"Caching mobileGearCDN.{key}")
        #     self.api.request(value, use_cache=True)
        #     self.manifest_keys[f"mobileGearCDN.{key}"] = value
        print("Done caching manifests")

    # def lookup_component(self, name, data=None):
    #     if data is None:
    #         # Initial call, use manifest_keys
    #         full_name = f"jsonWorldComponentContentPaths.{name}"
    #         if full_name in self.manifest_keys:
    #             component_data = self.manifest['jsonWorldComponentContentPaths'][name]
    #             # Assuming self.components[name][0] is a constructor or factory function
    #             component = self.components.get(name)
    #             return component[0](component_data, component[1], self)
    #         else:
    #             raise KeyError(f"No component named '{name}'")
    #     else:
    #         # Recursive call, 'data' is a subset of the JSON structure
    #         if name in data:
    #             # Process the data or perform further recursion as needed
    #             return data[name]
    #         else:
    #             raise KeyError(f"No component named '{name}' in provided data")
            
    # @property
    # def manifest_version(self):
    #     return self.api.request('/Platform/Destiny2/Manifest/').json()['Response']['version']

    # def __get_manifest_for_path(self, path):
    #     return self.api.request_json(path)
    # 
    # def __get_item_definitions(self, manifest):
    #     return self.__get_manifest_for_path(manifest["Response"]["jsonWorldComponentContentPaths"]["en"]["DestinyInventoryItemDefinition"])

    # def __get_stat_definitions(self, manifest):
    #     return self.__get_manifest_for_path(manifest["Response"]["jsonWorldComponentContentPaths"]["en"]["DestinyStatDefinition"])

    # @property
    # def is_cached(self) -> bool:
    #     return os.path.exists('data') and not self.cache_expired

    # @property
    # def cache_expired(self) -> bool:
    #     if self.cached_time is None:
    #         return True
    #     return (datetime.now() - self.cached_time) > CACHE_MAX_AGE_HOURS
    
    # def get_static_definitions(self):
    #     manifest = self.get_manifest()
    #     item_definitions = self.__get_item_definitions(manifest)
    #     stat_definitions = self.__get_stat_definitions(manifest)
    #     return item_definitions, stat_definitions


    """
    All Destiny manifest components are dicts of objects.

    There are usually multiple entries per component.
    Key is a large integer (referred to as a hash).

    The objects sometimes/often some common attributes:
    - blacklisted
    - redacted
    - index
    - hash
    - displayProperties
    - rootNodeHash

    The size of each component as of June 14, 2024:
        45768		DestinyUnlockDefinition 
        26486		DestinyInventoryItemDefinition 
        26486		DestinyInventoryItemLiteDefinition 
        21630		DestinyArtDyeReferenceDefinition 
        13442		DestinyUnlockExpressionMappingDefinition 
        12740		DestinyUnlockValueDefinition 
        9753		DestinyObjectiveDefinition 
        8847		DestinyCollectibleDefinition 
        7545		DestinyRewardMappingDefinition 
        6279		DestinyRecordDefinition 
        4091		DestinySandboxPerkDefinition 
        3963		DestinyPlugSetDefinition 
        3148		DestinyRewardItemListDefinition 
        2860		DestinyActivityDefinition 
        2778		DestinyLoreDefinition 
        2677		DestinyRewardSheetDefinition 
        2107		DestinySackRewardItemListDefinition 
        1937		DestinyPresentationNodeDefinition 
        1127		DestinySocketTypeDefinition 
        945			DestinyVendorDefinition 
        869			DestinySandboxPatternDefinition 
        852			DestinyLocationDefinition 
        851			DestinyEntitlementOfferDefinition 
        363			DestinyMetricDefinition 
        296			DestinyActivityModifierDefinition 
        292			DestinyTraitDefinition 
        276			DestinyMaterialRequirementSetDefinition 
        253			DestinyUnlockEventDefinition 
        216			DestinyFireteamFinderLabelDefinition 
        186			DestinyAchievementDefinition 
        178			DestinyFireteamFinderActivityGraphDefinition 
        166			DestinyFireteamFinderActivitySetDefinition 
        154			DestinyNodeStepSummaryDefinition 
        153			DestinyProgressionDefinition 
        130			DestinyItemCategoryDefinition 
        127			DestinyDestinationDefinition 
        117			DestinyActivityInteractableDefinition 
        92			DestinyStatGroupDefinition 
        73			DestinyActivityModeDefinition 
        71			DestinyStatDefinition 
        70			DestinyActivityTypeDefinition 
        63			DestinyFactionDefinition 
        61			DestinyInventoryBucketDefinition 
        60			DestinySocketCategoryDefinition 
        55			DestinyPlaceDefinition 
        54			DestinyMilestoneDefinition 
        44			DestinyProgressionMappingDefinition 
        34			DestinyUnlockCountMappingDefinition 
        30			DestinyCharacterCustomizationCategoryDefinition 
        26			DestinySeasonDefinition 
        25			DestinyRewardAdjusterPointerDefinition 
        23			DestinyActivityGraphDefinition 
        22			DestinyLoadoutColorDefinition 
        22			DestinyLoadoutNameDefinition 
        21			DestinyLoadoutIconDefinition 
        19			DestinyEquipmentSlotDefinition 
        18			DestinyArtDyeChannelDefinition 
        17			DestinyPowerCapDefinition 
        17			DestinySeasonPassDefinition 
        16			DestinySocialCommendationDefinition 
        15			DestinyChecklistDefinition 
        13			DestinyTalentGridDefinition 
        11			DestinyProgressionLevelRequirementDefinition 
        11			DestinyGuardianRankDefinition 
        10			DestinyFireteamFinderOptionDefinition 
        9			DestinyReportReasonCategoryDefinition 
        8			DestinyVendorGroupDefinition 
        8			DestinyFireteamFinderLabelGroupDefinition 
        8			DestinyFireteamFinderOptionGroupDefinition 
        7			DestinyDamageTypeDefinition 
        7			DestinyMedalTierDefinition 
        7			DestinyItemTierTypeDefinition 
        7			DestinyPlatformBucketMappingDefinition 
        7			DestinyEnergyTypeDefinition 
        6			DestinyCharacterCustomizationOptionDefinition 
        5			DestinySocialCommendationNodeDefinition 
        4			DestinyBondDefinition 
        4			DestinyEventCardDefinition 
        3			DestinyClassDefinition 
        3			DestinyRaceDefinition 
        3			DestinyBreakerTypeDefinition 
        2			DestinyGenderDefinition 
        1			DestinyRewardAdjusterProgressionMapDefinition 
        1			DestinyArtifactDefinition 
        1			DestinyGuardianRankConstantsDefinition 
        1			DestinyLoadoutConstantsDefinition 
        1			DestinyFireteamFinderConstantsDefinition 
        0			DestinyRewardSourceDefinition 
     
    """
 




class GenericNode:
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        try:
            value = self._data[name]
            if isinstance(value, (dict, list)):
                return GenericNode(value)
            return value
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __getitem__(self, key):
        try:
            value = self._data[key]
            if isinstance(value, (dict, list)):
                return GenericNode(value)
            return value
        except KeyError:
            raise KeyError(f"Key '{key}' not found in '{type(self).__name__}'")

    def __dir__(self):
        dynamic_attrs = super().__dir__()
        if isinstance(self._data, dict):
            dynamic_attrs += list(self._data.keys())
        return dynamic_attrs


