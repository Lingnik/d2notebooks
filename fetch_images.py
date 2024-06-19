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
    def traverse_and_download(self, data, root_node=None, key_path=''):
        # print(key_path)
        if isinstance(data, dict):
            for key, value in data.items():
                new_key_path = f"{key_path}.{key}" if key_path else key
                if root_node:
                    self.traverse_and_download(value, root_node, new_key_path)
                else:
                    self.traverse_and_download(value, new_key_path, new_key_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_key_path = f"{key_path}[{index}]"
                self.traverse_and_download(item, root_node, new_key_path)
        elif isinstance(data, str) and (data.endswith('.png') or data.endswith('jpg')):
            if key_path == self.target_path:
                self.reached_last_path = True
            if not self.reached_last_path:
                return
            if 'missing_icon_d2.png' in data:
                return
            
            # Prepare the local path
            sanitized_path = self.sanitize_path(data)
            # filename = f"{key_path}__{sanitized_path}"
            filename = f"{sanitized_path}"
            os.makedirs('content', exist_ok=True)
            # os.makedirs(f'content/{root_node}', exist_ok=True)

            # Skip download if already downloaded
            # if os.path.exists(os.path.join('content', root_node, filename)):
            if os.path.exists(os.path.join('content', filename)):
                print(f"Skipped: {key_path} -> {filename}")
                return

            # Download the image
            url = 'http://www.bungie.net' + data  # Replace with the correct base URL
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # with open(os.path.join('content', root_node, filename), 'wb') as f:
                with open(os.path.join('content', filename), 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded: {key_path} -> {filename}")
            else:
                print(f"Failed to download: {key_path} -> {filename} ({url})")

with open('data/__common__destiny2_content__json__en__aggregate-f946ef41-1dd2-49fb-bd7e-a3c45b9d20e5.json', 'r') as file:
    data = json.load(file)

# if it crashes again, here's where we left off on items:
# downloader = ImageDownloader('DestinyInventoryItemDefinition.3874578566.quality.displayVersionWatermarkIcons[0]')
# downloader = ImageDownloader('DestinySandboxPerkDefinition.3004405320.displayProperties.icon')
downloader = ImageDownloader('DestinySandboxPerkDefinition.1552233872.displayProperties.iconSequences[0].frames[0]')
downloader.traverse_and_download(data)
