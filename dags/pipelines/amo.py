import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SUBDOMAIN = os.getenv("AMO_SUBDOMAIN")
TOKEN = os.getenv("AMO_TOKEN")

if not SUBDOMAIN or not TOKEN:
    raise RuntimeError("AMO_SUBDOMAIN yoki AMO_TOKEN topilmadi!")

# Soddalashtirish: Session yaratib, bazaviy URL va headerlarni bir marta ulab qo'yamiz
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TOKEN}"})
BASE_URL = f"https://{SUBDOMAIN}.amocrm.ru/api/v4"

def get_table(name, limit=250, params=None, pause=0.2):
    """
    amoCRM-dan ma'lumotlarni sahifalab olib, Pandas DataFrame qaytaruvchi sodda funksiya.
    """
    key = name.split("/")[-1]
    rows = []
    page = 1

    while True:
        query = {"limit": limit, "page": page, **(params or {})}
        
        # requests.Session() yordamida so'rov yuborish
        r = session.get(f"{BASE_URL}/{name}", params=query, timeout=30)

        # Xatoliklar yoki tugash holatini tekshirish
        if r.status_code == 204 or not r.ok:
            break

        data = r.json()
        items = data.get("_embedded", {}).get(key, [])
        
        if not items:
            break

        rows.extend(items)
        print(f"{name}: {page}-sahifa olindi, jami {len(rows)} ta")

        # Keyingi sahifa bor-yo'qligini tekshirish
        if "next" not in data.get("_links", {}):
            break
            
        page += 1
        time.sleep(pause)

    return pd.json_normalize(rows)
