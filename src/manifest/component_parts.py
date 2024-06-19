

class DisplayProperties():
    def __init__(self, manifest_part):
        self.manifest_part: dict = manifest_part

    def to_dict(self):
        return self.manifest_part
    
    def __str__(self):
        return str(self.manifest_part)
    
    def __repr__(self):
        return str(self.manifest_part)
    
    @property
    def description(self) -> str:
        return self.manifest_part.get('description', None)
    
    @property
    def name(self) -> str:
        return self.manifest_part.get('name', None)
    
    @property
    def icon(self) -> str:
        return self.manifest_part.get('icon', None)
    
    @property
    def has_icon(self) -> bool:
        return self.manifest_part.get('hasIcon', None)