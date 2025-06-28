import time
import json
from pathlib import Path

from config import DB_PATH
from scraper import get_cheapest_links, is_gold_item
from float_fetcher import safe_fetch_float
from database import FloatDB

# ──────────────────────────────────────────────────────────────
# SETTINGS
# ──────────────────────────────────────────────────────────────
SKINS_FILE = "skins.json"
WEARS = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
SLEEP_BETWEEN_VARIANTS = 2  # seconds to avoid Steam spam

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    db = FloatDB(DB_PATH)
    with open(SKINS_FILE, "r", encoding="utf-8") as f:
        skins = json.load(f)

    known_links = db.get_known_inspect_links()

    for skin in skins:
        if is_gold_item(skin):
            continue
        for wear in WEARS:
            for stattrak in [False, True]:
                print(f"\n→ Checking: {skin} | {wear} | ST: {stattrak}")
                listings = get_cheapest_links(skin, wear, stattrak)
                new_listings = []
                for item in listings:
                    link = item["inspect_link"]
                    if link not in known_links:
                        float_val = safe_fetch_float(link)
                        if float_val is not None:
                            item["float_value"] = float_val
                            print(f"  ↳ Fetched float: {float_val:.5f}")
                        else:
                            print(f"  ↳ FAILED float fetch: {link}")
                        new_listings.append(item)
                    else:
                        # Already in DB, skip float fetch
                        print(f"  ↳ Cached: {link}")
                        item["float_value"] = None
                        new_listings.append(item)
                db.replace_variant(skin, wear, stattrak, new_listings)
                time.sleep(SLEEP_BETWEEN_VARIANTS)

    db.close()
    print("\n✅ Done.")

if __name__ == "__main__":
    main()
