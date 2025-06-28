import subprocess
import json
import time
from typing import Optional

def fetch_float(inspect_link: str) -> Optional[float]:
    """
    Uses the local inspect CLI from CSFloat repo to get float value.
    Assumes you have a Node.js wrapper or Python script named 'inspect' that takes the inspect link.
    Modify this if your command is different.
    """
    try:
        result = subprocess.run(
            ["node", "inspect", inspect_link],
            capture_output=True,
            timeout=10
        )
        if result.returncode != 0:
            return None
        output = result.stdout.decode("utf-8")
        data = json.loads(output)
        return float(data.get("floatvalue"))
    except Exception:
        return None

def safe_fetch_float(inspect_link: str, delay: float = 1.0) -> Optional[float]:
    time.sleep(delay)  # Enforce ~1s delay per bot
    return fetch_float(inspect_link)
