

class DisplayProperties():
    def __init__(self, manifest):
        self.manifest: dict = manifest

    def to_dict(self):
        return self.manifest
    
    def __str__(self):
        return str(self.manifest)
    
    def __repr__(self):
        return str(self.manifest)
    
    @property
    def description(self) -> str:
        return self.manifest.get('description', None)
    
    @property
    def name(self) -> str:
        return self.manifest.get('name', None)
    
    @property
    def icon(self) -> str:
        return self.manifest.get('icon', None)
    
    @property
    def has_icon(self) -> bool:
        return self.manifest.get('hasIcon', None)
