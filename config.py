import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "csgo_floats.db")
LOCAL_FLOAT_API = os.getenv("LOCAL_FLOAT_API", "http://localhost:8000/float")  # if using HTTP fallback

def load_bots_from_env():
    bots = []
    i = 1
    while True:
        user = os.getenv(f"BOT{i}_USER")
        pwd = os.getenv(f"BOT{i}_PASS")
        shared_secret = os.getenv(f"BOT{i}_SHARED_SECRET", None)
        if user and pwd:
            bots.append({
                "username": user,
                "password": pwd,
                "shared_secret": shared_secret
            })
            i += 1
        else:
            break
    return bots
