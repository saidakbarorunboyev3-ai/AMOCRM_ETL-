import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SUBDOMAIN = os.getenv("AMO_SUBDOMAIN")
TOKEN = os.getenv("AMO_TOKEN")

# O'zgaruvchilar yo'q bo'lsa, tushunarli xato bilan to'xtaydi
if not SUBDOMAIN or not TOKEN:
    raise RuntimeError(
        "AMO_SUBDOMAIN yoki AMO_TOKEN topilmadi. .env faylni "
        "(va Docker uchun docker-compose.yaml dagi environment: ni) tekshiring."
    )

BASE = f"https://{SUBDOMAIN}.amocrm.ru/api/v4"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

MAX_LIMIT = 250   # amoCRM bir so'rovda ko'pi bilan 250 ta yozuv beradi


def _get(url, query, retries):
    """So'rov yuboradi. Tarmoq xatosi, 429 (limit) va 5xx bo'lsa, qayta urinadi."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, params=query, timeout=30)
        except (requests.ConnectionError, requests.Timeout):
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
            continue

        if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
            time.sleep(2 * attempt)
            continue
        return r


def get_table(name, limit=MAX_LIMIT, params=None, pause=0.2, retries=5):
    """
    name   : endpoint nomi, masalan 'leads', 'contacts', 'leads/pipelines'
    limit  : bir sahifadagi yozuvlar soni (eng ko'pi 250)
    params : qo'shimcha parametrlar, masalan {"with": "contacts"}
    pause  : sahifalar orasidagi kutish (amoCRM so'rov limiti uchun)
    Barcha sahifalarni o'zi aylanib, hammasini bitta DataFrame qilib qaytaradi.
    """
    key = name.split("/")[-1]
    rows = []
    page = 1

    while True:
        query = {"limit": limit, "page": page, **(params or {})}
        r = _get(f"{BASE}/{name}", query, retries)

        if r.status_code == 204:          # ma'lumot yo'q yoki tugagan
            break
        if not r.ok:
            print(f"{name}: HTTP {r.status_code}: {r.text[:300]}")
            r.raise_for_status()

        data = r.json()
        items = data.get("_embedded", {}).get(key, [])
        if not items:                     # bo'sh sahifa, to'xtaymiz
            break

        rows += items
        print(f"{name}: {page}-sahifa olindi, jami {len(rows)} ta")

        if "next" not in data.get("_links", {}):
            break
        page += 1
        time.sleep(pause)

    return pd.json_normalize(rows)
