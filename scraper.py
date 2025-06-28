import requests
import urllib.parse
from typing import List, Tuple

UA = {"User-Agent": "Mozilla/5.0"}

def market_hash_name(skin: str, wear: str, stattrak: bool = False) -> str:
    prefix = "StatTrak™ " if stattrak else ""
    return f"{prefix}{skin} ({wear})"

def fetch_listing_data(hash_name: str, count: int = 100, currency: int = 1) -> List[Tuple[int, str]]:
    url_name = urllib.parse.quote(hash_name)
    url = f"https://steamcommunity.com/market/listings/730/{url_name}/render?count={count}&currency={currency}"
    r = requests.get(url, headers=UA)
    if not r.ok:
        return []
    try:
        data = r.json()
    except Exception:
        return []

    results = []
    for listing in data.get("listinginfo", {}).values():
        actions = listing.get("asset", {}).get("market_actions", [])
        if actions:
            link = actions[0]["link"].replace("%listingid%", listing["listingid"]).replace("%assetid%", listing["asset"]["id"])
            price_cents = int(listing.get("converted_price_per_unit", 0))
            results.append((price_cents, link))
    return sorted(results, key=lambda x: x[0])[:20]

def get_cheapest_links(skin: str, wear: str, stattrak: bool) -> List[dict]:
    name = market_hash_name(skin, wear, stattrak)
    pairs = fetch_listing_data(name)
    return [{"price": price, "inspect_link": link} for price, link in pairs]

def is_gold_item(skin: str) -> bool:
    return "★" in skin
