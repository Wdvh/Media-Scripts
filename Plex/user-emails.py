from plexapi.server import PlexServer
from dotenv import load_dotenv
import os
from helpers import get_plex, load_and_upgrade_env

import logging
from pathlib import Path
from datetime import datetime, timedelta
# current dateTime
now = datetime.now()

# convert to string
RUNTIME_STR = now.strftime("%Y-%m-%d %H:%M:%S")

SCRIPT_NAME = Path(__file__).stem

VERSION = "0.1.0"


env_file_path = Path(".env")

logging.basicConfig(
    filename=f"{SCRIPT_NAME}.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.info(f"Starting {SCRIPT_NAME}")
print(f"Starting {SCRIPT_NAME}")

status = load_and_upgrade_env(env_file_path)

print("connecting...")
plex = get_plex()
plexacc = plex.myPlexAccount()
print("getting users...")
users = plexacc.users()
user_total = len(users)
print(f"looping over {user_total} users...")
for u in users:
    print(f"{u.username} - {u.email}")
