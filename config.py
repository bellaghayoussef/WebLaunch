import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MOCKUP_DIR = STATIC_DIR / "mockups"
TEMPLATES_DIR = BASE_DIR / "templates"
SETTINGS_FILE = BASE_DIR / "settings.json"
LEADS_DB_FILE = BASE_DIR / "leads_db.json"

# Ensure required directories exist
MOCKUP_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SETTINGS = {
    "port": 5055,
    "theme": "dark",
    "default_language": "fr",  # "fr", "ar", or "en"
    "agency_name": "WebLaunch Agency",
    "agency_phone": "+974 5000 0000",
    "agency_email": "[EMAIL_ADDRESS]",
    "smtp": {
        "host": "smtp.gmail.com",
        "port": 587,
        "user": "bellaghayoussef20@gmail.com",
        "password": "bbtx qzwm ncws bnya",
        "from_email": "[EMAIL_ADDRESS]",
        "use_tls": True
    },
    "google_places_api_key": ""
}

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # merge with defaults
                merged = DEFAULT_SETTINGS.copy()
                merged.update(data)
                return merged
        except Exception as e:
            print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()

def save_settings(new_settings):
    current = load_settings()
    current.update(new_settings)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    return current
