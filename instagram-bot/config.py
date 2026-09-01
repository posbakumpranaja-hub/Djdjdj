"""
config.py - Konfigurasi global Instagram Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file jika ada
load_dotenv()

# =============================================================
# Path Configuration
# =============================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
SESSION_DIR = BASE_DIR / "sessions"

# Buat direktori jika belum ada
for _dir in (DATA_DIR, LOG_DIR, SESSION_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# =============================================================
# Instagram Credentials (dari .env atau environment)
# =============================================================
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")

# =============================================================
# Rate Limiting (detik)
# =============================================================
DELAY_BETWEEN_ACTIONS = float(os.getenv("DELAY_BETWEEN_ACTIONS", "3"))
DELAY_BETWEEN_REQUESTS = float(os.getenv("DELAY_BETWEEN_REQUESTS", "1.5"))
MAX_ACTIONS_PER_HOUR = int(os.getenv("MAX_ACTIONS_PER_HOUR", "60"))
MAX_FOLLOWS_PER_DAY = int(os.getenv("MAX_FOLLOWS_PER_DAY", "150"))
MAX_LIKES_PER_DAY = int(os.getenv("MAX_LIKES_PER_DAY", "300"))
MAX_COMMENTS_PER_DAY = int(os.getenv("MAX_COMMENTS_PER_DAY", "100"))

# =============================================================
# Database
# =============================================================
DB_PATH = str(DATA_DIR / "bot_data.db")

# =============================================================
# Logging
# =============================================================
LOG_FILE = str(LOG_DIR / "bot.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =============================================================
# Session
# =============================================================
SESSION_FILE = str(SESSION_DIR / "session.json")

# =============================================================
# Proxy
# =============================================================
PROXY_FILE = str(DATA_DIR / "proxies.txt")
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"
PROXY_ROTATION_INTERVAL = int(os.getenv("PROXY_ROTATION_INTERVAL", "10"))

# =============================================================
# Default Comments
# =============================================================
DEFAULT_COMMENTS = [
    "Nice post! 🔥",
    "Great content! 👏",
    "Amazing! ❤️",
    "Love this! 😍",
    "Keep it up! 💪",
    "Awesome! 🌟",
    "Beautiful! 😊",
    "Wow, incredible! 🙌",
]

# =============================================================
# App Info
# =============================================================
APP_NAME = "Instagram Bot"
APP_VERSION = "1.0.0"
