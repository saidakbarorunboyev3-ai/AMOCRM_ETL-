import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE = f"https://{os.getenv('AMO_SUBDOMAIN')}.amocrm.ru/api/v4"
HEADERS = {"Authorization": f"Bearer {os.getenv('AMO_TOKEN')}"}


def get_table(name):
    key = name.split("/")[-1]
    rows = []
    page = 1
    while True:
        r = requests.get(f"{BASE}/{name}", headers=HEADERS,
                         params={"limit": 250, "page": page}, timeout=30)
        if r.status_code == 204:
            break
        r.raise_for_status()
        data = r.json()
        rows += data["_embedded"][key]
        if "next" not in data["_links"]:
            break
        page += 1
    return pd.json_normalize(rows)