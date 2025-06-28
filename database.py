import sqlite3
from typing import List, Dict

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS cheapest_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    wear TEXT NOT NULL,
    stattrak INTEGER NOT NULL,
    price INTEGER NOT NULL,
    float_value REAL,
    inspect_link TEXT UNIQUE NOT NULL
);
"""

class FloatDB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.executescript(DB_SCHEMA)

    def get_known_inspect_links(self) -> set:
        cursor = self.conn.execute("SELECT inspect_link FROM cheapest_listings")
        return set(row[0] for row in cursor.fetchall())

    def replace_variant(self, name: str, wear: str, stattrak: bool, listings: List[Dict]):
        """
        Replace all listings for a specific (name, wear, stattrak) with new top 20.
        Each listing: {price, float_value, inspect_link}
        """
        with self.conn:
            self.conn.execute(
                "DELETE FROM cheapest_listings WHERE name = ? AND wear = ? AND stattrak = ?",
                (name, wear, int(stattrak))
            )
            for entry in listings:
                self.conn.execute(
                    """INSERT OR IGNORE INTO cheapest_listings 
                       (name, wear, stattrak, price, float_value, inspect_link) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (name, wear, int(stattrak), entry["price"], entry.get("float_value"), entry["inspect_link"])
                )

    def update_float(self, inspect_link: str, float_value: float):
        with self.conn:
            self.conn.execute(
                "UPDATE cheapest_listings SET float_value = ? WHERE inspect_link = ?",
                (float_value, inspect_link)
            )

    def close(self):
        self.conn.close()
