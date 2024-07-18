import os
import requests
import json
from datetime import datetime
from src.bungie_manifest import BungieManifest
from src.bungie_profile import BungieProfile
from src.settings import CACHE_MAX_AGE_HOURS


class BungieApi:
    def __init__(self, api_key, access_token):
        self.api_key = api_key
        self.access_token = access_token
        self.manifest = BungieManifest(self)
        self.profile = BungieProfile(self)
        self.cache = {} # {'<path>' : {'json': <json>, 'response': <response>, 'timestamp': <timestamp>, 'filename': <filename>}

    def __default_headers(self):
        return {
            'X-API-Key': self.api_key,
        }

    def request_json(self, path: str, use_cache: bool=False, bust_cache: bool=False):
        return self.request(path, use_cache, bust_cache).get('json')
    
    def request(self, path: str, use_cache: bool=False, bust_cache: bool=False):
        url = f'https://www.bungie.net{path}'
        key = self.sanitize_path_for_key(path)

        if use_cache:
            expired = self.cache_expired(key)
            if expired is None:
                if self.key_is_cached_on_disk(key):
                    if not bust_cache:
                        print(f"Key {key} not in cache but on disk, caching from disk")
                        with open(f'data/{key}', 'rb') as f:
                            data = f.read()
                        json_data = None
                        try:
                            json_data = json.loads(data)
                        except Exception:
                            print("File is not JSON")
                            pass
                        self.cache[key] = {
                            'json': json_data,
                            'text': None,
                            'content': data,
                            'response': None,
                            'timestamp': datetime.now(),
                            'filename': key,
                        }
                        return self.cache[key]
                    else:
                        print(f"Key {key} not in cache, but on disk, but busting as requested")
                        self.prune_cache(key)
                else:
                    print(f"Key {key} not in cache, fetching from network")
            elif expired is True:
                print(f"Key {key} in cache but expired, fetching from network")
                self.prune_cache(key)
            elif bust_cache:
                print(f"Key {key} in cache, but busting as requested")
                self.prune_cache(key)
            else:
                print(f"Key {key} in cache and not expired, returning cached response")
                return self.cache[key]
            

        print(f"Fetching {url} for key {key}")
        response: requests.Response = requests.get(url, headers=self.__default_headers())
        response.raise_for_status()

        response_json = None
        try:
            response_json = response.json()
        except ValueError:
            pass

        response_text = None
        try:
            response_text = response.text
        except ValueError:
            pass

        output = {
            'json': response_json,
            'text': response_text,
            'content': response.content,
            'response': response,
            'timestamp': datetime.now(),
            'filename': key,
        }

        if use_cache:
            print(f"Caching response for key {key}")
            # Write to disk
            os.makedirs('data', exist_ok=True)
            filename = f'data/{key}'
            if response_json:
                with open(filename, 'w') as f:
                    json.dump(response_json, f, indent=4)
            else:
                with open(filename, 'wb') as f:
                    f.write(response.content)

        return output
    
    def prune_cache(self, key: str):
        print("**** PRUNING KEY: ", key, " ****")
        if key in self.cache:
            del self.cache[key]
            os.remove(f'data/{key}')
    
    @staticmethod
    def sanitize_path_for_key(path: str):
        return path.replace('/', '__')

    @staticmethod
    def key_is_cached_on_disk(key: str):
        return os.path.exists(f'data/{key}')
    
    def cache_expired(self, key: str) -> bool:
        """
        Return whether the cache is expired for the given key.
        
        If the key is not in the cache, or the key is missing a timestamp, returns falsey None.
        """
        if key not in self.cache or 'timestamp' not in self.cache[key] or self.cache[key]['timestamp'] is None:
            return None
        return (datetime.now() - self.cache[key]['timestamp']) > CACHE_MAX_AGE_HOURS
