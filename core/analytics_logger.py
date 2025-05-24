# core/analytics_logger.py

import json
from datetime import datetime
from pathlib import Path

ANALYTICS_DIR = Path("data/analytics")
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

def _get_today_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return ANALYTICS_DIR / f"{today}.json"

def _load_data(path):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def _save_data(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_analytics(user_id_or_username: str, action: str, details: dict = None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_id_or_username,
        "action": action,
        "details": details or {}
    }
    file = _get_today_file()
    data = _load_data(file)
    data.append(entry)
    _save_data(file, data)
