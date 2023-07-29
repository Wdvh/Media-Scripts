import logging
from plexapi.server import PlexServer
from plexapi.exceptions import Unauthorized
import os
from dotenv import load_dotenv
import sys
import textwrap
from tmdbapis import TMDbAPIs
import requests
import pathlib
from timeit import default_timer as timer
from helpers import get_ids, get_plex, load_and_upgrade_env

# // TODO: improved error handling
# // TODO: TV Theme tunes
# // TODO: Process Music libraries
# // TODO: Process Photo libraries

# import tvdb_v4_official

start = timer()

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
TMDB_KEY = os.getenv("TMDB_KEY")
TVDB_KEY = os.getenv("TVDB_KEY")
REMOVE_LABELS = os.getenv("REMOVE_LABELS")

if REMOVE_LABELS:
    lbl_array = REMOVE_LABELS.split(",")

# Commented out until this doesn't throw a 400
# tvdb = tvdb_v4_official.TVDB(TVDB_KEY)

tmdb = TMDbAPIs(TMDB_KEY, language="en")

tmdb_str = "tmdb://"
tvdb_str = "tvdb://"

local_dir = f"{os.getcwd()}/posters"

os.makedirs(local_dir, exist_ok=True)

show_dir = f"{local_dir}/shows"
movie_dir = f"{local_dir}/movies"

os.makedirs(show_dir, exist_ok=True)
os.makedirs(movie_dir, exist_ok=True)


def progress(count, total, status=""):
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)
    stat_str = textwrap.shorten(status, width=30)

    sys.stdout.write("[%s] %s%s ... %s\r" % (bar, percents, "%", stat_str.ljust(30)))
    sys.stdout.flush()


print("tmdb config...")

base_url = tmdb.configuration().secure_base_image_url
size_str = "original"

plex = get_plex()

logging.info("connection success")

print(f"getting items from [{LIBRARY_NAME}]...")
items = plex.library.section(LIBRARY_NAME).all()
item_total = len(items)
print(f"looping over {item_total} items...")
item_count = 1
for item in items:
    tmpDict = {}
    imdb_id, tmdb_id, tvdb_id = get_ids(item.guids, TMDB_KEY)
    item_count = item_count + 1
    try:
        progress(item_count, item_total, item.title)
        pp = None
        if item.TYPE == "show":
            try:
                pp = (
                    tmdb.tv_show(tmdb_id).poster_path
                    if tmdb_id
                    else tmdb.find_by_id(tvdb_id=tvdb_id).tv_results[0].poster_path
                )
            except:
                pp = "NONE"
            tgt_dir = show_dir
        else:
            pp = tmdb.movie(tmdb_id).poster_path
            tgt_dir = movie_dir

        if pp is not None:
            if pp == "NONE":
                posters = item.posters()
                item.setPoster(posters[0])
            else:
                ext = pathlib.Path(pp).suffix
                posterURL = f"{base_url}{size_str}{pp}"
                local_file = f"{tgt_dir}/{item.ratingKey}{ext}"
                if not os.path.exists(local_file):
                    r = requests.get(posterURL, allow_redirects=True)
                    open(f"{local_file}", "wb").write(r.content)
                item.uploadPoster(filepath=local_file)
        else:
            progress(item_count, item_total, "unknown type: " + item.title)

    except Exception as ex:
        progress(item_count, item_total, "EX: " + item.title)

end = timer()
elapsed = end - start
print(f"{os.linesep}{os.linesep}processed {item_count - 1} items in {elapsed} seconds.")
