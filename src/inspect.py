#!/usr/bin/env python3

import datetime
from src import config
from src.bungie_oauth import BungieAuth
from src.bungie_api import BungieApi


client_id, api_key, _ = config.load_config()
print(f"client_id length: {len(client_id)}")
print(f"api_key length: {len(api_key)}")

# perform oauth login to get the access token used in later requests.  It is good for 1 hour
print("We're using a self-signed certificate to run an HTTPS server on localhost, you'll need to accept the certificate in your browser.")
access_token = BungieAuth(client_id).refresh_oauth_token()

# token is good for 1 hour, print out the time that it expires
expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
print(f"Access token successfully acquired at: {datetime.datetime.now().isoformat()} and expires at: {expiration_time.isoformat()}")

api = BungieApi(client_id, api_key)

# it's nice to have all of the manifest files downloaded locally into the data directory for reference
# import shutil
# shutil.rmtree("data", ignore_errors=True)
api.manifest.cache_manifests()

print(len(api.manifest.destiny_achievement_definition.manifest))