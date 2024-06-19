from src.manifest.component_parts import DisplayProperties


class BaseManifestComponent():
    def __init__(self, manifest_obj):
        print("+base_component.BaseManifestComponent.__init__()")
        print(f"Initializing {self.__class__.__name__} with manifest_obj: {manifest_obj}")
        print(f"Manifest: {manifest_obj.manifest}")
        self.manifest = manifest_obj.manifest
        self.manifest_obj = manifest_obj
        print("-base_component.BaseManifestComponent.__init__()")

    # def get(self, key):
    #     return self.manifest.get(key, None)

    # def get_all(self):
    #     return self.manifest

    # def __str__(self):
    #     return f"{self.__class__.__name__}({self.manifest})"

    # def __repr__(self):
    #     return self.__str__()

    # def __getitem__(self, key):
    #     return self.manifest[key]

    # def __contains__(self, key):
    #     return key in self.manifest

    # def __iter__(self):
    #     return iter(self.manifest)
    
    # def __len__(self):
    #     return len(self.manifest)
    
    # def __eq__(self, other):
    #     return self.manifest == other.manifest
    
    # def __ne__(self, other):
    #     return self.manifest != other.manifest
    
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


class DestinyAchievementDefinition(BaseManifestComponent):
    def __init__(self, manifest_obj):
        print("+destiny_achievement_definition.DestinyAchievementDefinition.__init__()")
        super().__init__(manifest_obj)
        print("-destiny_achievement_definition.DestinyAchievementDefinition.__init__()")

    @property
    def display_properties(self) -> DisplayProperties:
        if self.manifest.get('displayProperties', None) is None:
            return None
        return DisplayProperties(self.manifest.get('displayProperties', {}))
    
    @property
    def accumulator_threshold(self) -> int:
        return self.manifest.get('accumulatorThreshold', None)
    
    @property
    def platform_index(self) -> int:
        return self.manifest.get('platformIndex', None)
