#!/usr/bin/env python3

import importlib
import os
from src import config
from pprint import pprint


client_id, api_key, _ = config.load_config()

print(f"client_id length: {len(client_id)}")
print(f"api_key length: {len(api_key)}")

from src.bungie_oauth import BungieAuth
import datetime

# perform oauth login to get the access token used in later requests.  It is good for 1 hour
print("We're using a self-signed certificate to run an HTTPS server on localhost, you'll need to accept the certificate in your browser.")
access_token = None
OFFLINE = os.environ.get('BUNGIE_OFFLINE', None)
if not OFFLINE:
    try:
        access_token = BungieAuth(client_id).refresh_oauth_token()
        # token is good for 1 hour, print out the time that it expires
        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        print(f"Access token successfully acquired at: {datetime.datetime.now().isoformat()} and expires at: {expiration_time.isoformat()}")
    except Exception as e:
        print("Oauth refresh failed, no token available")

from src import bungie_api

api = bungie_api.BungieApi(client_id, api_key)

# it's nice to have all of the manifest files downloaded locally into the data directory for reference
# import shutil
# shutil.rmtree("data", ignore_errors=True)
api.manifest.cache_manifests()

# achievement = api.manifest.DestinyAchievementDefinition[1088488145]
# print(type(achievement))
# print(list(achievement.keys()))
