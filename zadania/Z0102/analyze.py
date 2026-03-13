
from pathlib import Path
import sys
import csv, json, io
import requests

# ensure sibling package Z0101 can be imported (adds the `zadania` dir to sys.path)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from Z0101.output import output

# read API key from local .config file
cfg_path = Path(__file__).resolve().parent / '.config'
APIKEY = None
if cfg_path.exists():
    for line in cfg_path.read_text(encoding='utf-8').splitlines():
        if line.strip().startswith('APIKEY'):
            _, val = line.split('=', 1)
            APIKEY = val.strip().strip('"').strip("'")
            break
if not APIKEY:
    raise SystemExit('APIKEY not found in .config')

tutajtwojklucz = APIKEY
url_people = f'https://hub.ag3nts.org/data/{tutajtwojklucz}/people.csv'
resp = requests.get(url_people)
resp.raise_for_status()
reader = csv.DictReader(io.StringIO(resp.text))
rows = list(reader)

# print('total', len(rows))

url_plants = f'https://hub.ag3nts.org/data/{tutajtwojklucz}/findhim_locations.json'
with requests.get(url_plants) as r:
    r.raise_for_status()
    plants = r.json()


url_locations = f'https://hub.ag3nts.org/api/locations'
body = {
    "apikey": tutajtwojklucz,
    "name": f'{}'
    "surname": f"{}"
}
