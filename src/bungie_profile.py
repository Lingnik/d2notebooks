import requests
from urllib.parse import quote


class BungieProfile:
    def __init__(self, api):
        self.api = api
        self.cached_time = None
        self.cached_version = None
        self.cached_manifest = None
        self.cached_manifests = {}
    
    def get_primary_membership_id_and_type(self, username):
        username = quote(username)
        url = f"https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/-1/{username}/"
        response = requests.get(url, headers=self.api.__default_headers())
        data = response.json()

        for player in data['Response']:
            membership_id = player['membershipId']
            membership_type = player['membershipType']
            print(f"Checking membership ID {membership_id} with membership type {membership_type}")
            profile_url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/?components=100"
            profile_response = requests.get(profile_url, headers=self.api.__default_headers())
            profile_data = profile_response.json()
            if 'profile' in profile_data['Response'] and profile_data['Response']['profile']['data']['userInfo']['crossSaveOverride'] == membership_type:
                print(f"Crosave override found for {membership_id}")
                return membership_id, membership_type

        return None
    
    def get_character_ids_and_classes(self, membership_id, membership_type):
        url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/?components=200"
        response = requests.get(url, headers=self.api.__default_headers())
        data = response.json()

        character_data = data['Response']['characters']['data']
        character_ids_and_classes = {}
        for character_id, character_info in character_data.items():
            class_type = character_info['classType']
            if class_type == 0:
                class_name = 'Titan'
            elif class_type == 1:
                class_name = 'Hunter'
            elif class_type == 2:
                class_name = 'Warlock'
            else:
                class_name = 'Unknown'
            character_ids_and_classes[character_id] = class_name

        return character_ids_and_classes

    # full description of components are on the bungie API documentation: https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html
    def get_profile(self, access_token, membership_type, membership_id, components):
        headers = self.__default_headers() 
        headers['Authorization'] = f'Bearer {access_token}'

        joined_components = ','.join(str(c) for c in components)

        url = f'https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/?components={joined_components}'

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()['Response']
        return data