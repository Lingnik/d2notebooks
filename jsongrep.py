import os
import re
import json
import sys

gray_code = "\033[90m"  # ANSI escape code for gray (bright black) foreground
reset_code = "\033[0m"  # ANSI reset code to return to default color

def search_in_json(data, search_term, key_path=''):
    matches = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key_path = f"{key_path}.{key}" if key_path else key
            matches.extend(search_in_json(value, search_term, new_key_path))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key_path = f"{key_path}[{index}]"
            matches.extend(search_in_json(item, search_term, new_key_path))
    elif isinstance(data, str) and re.search(search_term, data, re.IGNORECASE):
        matches.append((key_path, data))
    return matches

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <search_term> <json_file>")
        sys.exit(1)

    search_term = sys.argv[1]
    json_file = sys.argv[2]

    with open(json_file, 'r') as file:
        data = json.load(file)

    matches = search_in_json(data, search_term)

    for key_path, value in matches:
        print(f"{key_path}: {gray_code}{value}{reset_code}")

if __name__ == "__main__":
    main()