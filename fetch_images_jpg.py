import os
import requests
import re
import json


class ImageDownloader:
    def __init__(self, target_path):
        self.reached_last_path = False
        self.target_path = target_path

    # Function to sanitize file paths
    def sanitize_path(self, path):
        return re.sub(r'[\\/]', '__', path)

    # Function to recursively traverse the dictionary
    def traverse_and_download(self, data, key_path=''):
        # print(key_path)
        if isinstance(data, dict):
            for key, value in data.items():
                new_key_path = f"{key_path}.{key}" if key_path else key
                self.traverse_and_download(value, new_key_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_key_path = f"{key_path}[{index}]"
                self.traverse_and_download(item, new_key_path)
        elif isinstance(data, str) and data.endswith('.jpg'):
            if key_path == self.target_path:
                self.reached_last_path = True
            if not self.reached_last_path:
                return
            if not key_path.startswith('DestinyInventoryItem'):
                return
            print(f"Downloading: {key_path} - {data}")
            # Download the image
            url = 'http://www.bungie.net' + data  # Replace with the correct base URL
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                sanitized_path = self.sanitize_path(data)
                filename = f"{key_path}__{sanitized_path}"
                os.makedirs('content', exist_ok=True)
                with open(os.path.join('content', filename), 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download: {url}")

with open('data/__common__destiny2_content__json__en__aggregate-f946ef41-1dd2-49fb-bd7e-a3c45b9d20e5.json', 'r') as file:
    data = json.load(file)

# If it crashes again, here's where we left off for item stuff: downloader = ImageDownloader('DestinyInventoryItemDefinition.1178901683.screenshot')
downloader = ImageDownloader('DestinyInventoryItemDefinition.1178901683.screenshot')
downloader.traverse_and_download(data)
