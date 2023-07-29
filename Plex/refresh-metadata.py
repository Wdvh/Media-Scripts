from plexapi.server import PlexServer
import os
from dotenv import load_dotenv
import sys
import textwrap
import time
import logging
import urllib3.exceptions
from urllib3.exceptions import ReadTimeoutError
from requests import ReadTimeout
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

LIBRARY_NAME = os.getenv("LIBRARY_NAME")
LIBRARY_NAMES = os.getenv("LIBRARY_NAMES")
DELAY = int(os.getenv("DELAY"))

if LIBRARY_NAMES:
    lib_array = LIBRARY_NAMES.split(",")
else:
    lib_array = [LIBRARY_NAME]

tmdb_str = "tmdb://"
tvdb_str = "tvdb://"


def progress(count, total, status=""):
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)
    stat_str = textwrap.shorten(status, width=80)

    sys.stdout.write("[%s] %s%s ... %s\r" % (bar, percents, "%", stat_str.ljust(80)))
    sys.stdout.flush()

plex = get_plex()

for lib in lib_array:
    print(f"getting items from [{lib}]...")
    logging.info(f"getting items from [{lib}]...")
    items = plex.library.section(lib).all()
    item_total = len(items)
    print(f"looping over {item_total} items...")
    logging.info(f"looping over {item_total} items...")
    item_count = 1

    plex_links = []
    external_links = []

    for item in items:
        tmpDict = {}
        item_count = item_count + 1
        attempts = 0

        progress_str = f"{item.title}"

        progress(item_count, item_total, progress_str)

        while attempts < 5:
            try:

                progress_str = f"{item.title} - attempt {attempts + 1}"
                logging.info(progress_str)

                progress(item_count, item_total, progress_str)

                item.refresh()
                time.sleep(DELAY)
                progress_str = f"{item.title} - DONE"
                progress(item_count, item_total, progress_str)

                attempts = 6
            except urllib3.exceptions.ReadTimeoutError:
                progress(item_count, item_total, "ReadTimeoutError: " + item.title)
            except urllib3.exceptions.HTTPError:
                progress(item_count, item_total, "HTTPError: " + item.title)
            except ReadTimeoutError:
                progress(item_count, item_total, "ReadTimeoutError-2: " + item.title)
            except ReadTimeout:
                progress(item_count, item_total, "ReadTimeout: " + item.title)
            except Exception as ex:
                progress(item_count, item_total, "EX: " + item.title)
                logging.error(ex)

            attempts += 1

    print(os.linesep)
