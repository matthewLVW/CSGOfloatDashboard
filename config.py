# steam-inspect/config.py
STEAM_APPID     = 730       # CS2
CURRENCY_ID     = 1         # 1 = USD (see Steam docs for others)
UA_HEADER       = {"User-Agent": "Mozilla/5.0 (cs2-inspect/1.0)"}
MAX_RETRIES     = 3
DB_PATH         = "inspect_links.db"   # optional – set to None to skip SQLite
