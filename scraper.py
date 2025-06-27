# steam-inspect/scraper.py
import requests, urllib.parse, time, logging, sqlite3
from typing import List, Tuple, Dict
from config import STEAM_APPID, CURRENCY_ID, UA_HEADER, MAX_RETRIES, DB_PATH

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def market_hash_name(skin: str, wear: str = "Field-Tested", stattrak: bool = False) -> str:
    """Compose the exact Market Hash Name used by Steam."""
    prefix = "StatTrak\u2122 " if stattrak else ""
    return f"{prefix}{skin} ({wear})"

def fetch_market_json(hash_name: str, start: int = 0, count: int = 100) -> Dict:
    """Hit the hidden ‘render’ JSON endpoint Steam’s own site uses."""
    url_hash = urllib.parse.quote(hash_name, safe='')
    url = f"https://steamcommunity.com/market/listings/{STEAM_APPID}/{url_hash}/render"
    params = {
        "start":   start,
        "count":   count,
        "currency": CURRENCY_ID,
        "language": "english",
        "format":   "json",
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, headers=UA_HEADER, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as err:
            logging.warning("Request failed (%s) – retry %d/%d", err, attempt, MAX_RETRIES)
            time.sleep(1)
    raise RuntimeError("Steam ‘render’ endpoint failed after retries")

def extract_inspect_links(market_json: Dict, limit: int = 20) -> List[Tuple[int, str]]:
    """Return [(price_in_cents, inspect_link), …] for the cheapest N."""
    infos   = market_json.get("listinginfo", {})
    assets  = market_json.get("assets", {}).get(str(STEAM_APPID), {}).get("2", {})
    rows: List[Tuple[int, str]] = []

    for lst in infos.values():
        price_cents = lst.get("price") or lst.get("converted_price")
        asset_id    = str(lst["asset"]["id"])
        asset_blob  = assets.get(asset_id, {})
        acts        = asset_blob.get("market_actions") or asset_blob.get("actions") or []
        if acts:
            rows.append((price_cents, acts[0]["link"]))

    rows.sort(key=lambda t: t[0])      # cheapest first
    return rows[:limit]

def save_links_sqlite(rows: List[Tuple[int, str]]):
    """Persist (price, link) to a local SQLite DB if requested."""
    if DB_PATH is None:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inspect_links (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                link   TEXT UNIQUE,
                price  INTEGER
            )
        """)
        conn.executemany("INSERT OR IGNORE INTO inspect_links (link, price) VALUES (?, ?)",
                         [(lnk, price) for price, lnk in rows])
        conn.commit()

def main():
    # ==== CHANGE THESE TWO STRINGS AS NEEDED =========================
    skin = "AWP | Printstream"     # weapon & finish
    wear = "Field-Tested"          # exterior (Factory New … Battle-Scarred)
    # =================================================================
    hash_name = market_hash_name(skin, wear, stattrak=False)
    logging.info("Querying Steam listings for: %s", hash_name)

    js   = fetch_market_json(hash_name, count=100)
    rows = extract_inspect_links(js, limit=20)

    if not rows:
        logging.error("No inspect links found – Steam may have hidden the actions.")
        return

    # Store (optional) and print
    save_links_sqlite(rows)
    print("\nCheapest 20 inspect links:")
    for cents, link in rows:
        print(f"${cents/100:>6.2f}  –  {link}")

    # === Hand off to your local CSGOFloat clone ======================
    # from csfloat_local import fetch_float
    # floats = [fetch_float(link) for _, link in rows]
    # print(floats)

if __name__ == "__main__":
    main()
