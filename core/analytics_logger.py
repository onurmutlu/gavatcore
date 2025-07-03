import json
from datetime import datetime
from pathlib import Path
import portalocker  # pip install portalocker

ANALYTICS_DIR = Path("data/analytics")
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
MAX_ANALYTICS_SIZE = 5 * 1024 * 1024  # 5 MB

def _get_today_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return ANALYTICS_DIR / f"{today}.json"

def _load_data(path):
    if not path.exists():
        return []
    try:
        with portalocker.Lock(str(path), timeout=2):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[analytics_logger] load error: {e}")
        return []

def _save_data(path, data):
    # Rotate if needed
    if path.exists() and path.stat().st_size > MAX_ANALYTICS_SIZE:
        rotated = path.with_suffix(f".{int(datetime.now().timestamp())}.bak")
        path.rename(rotated)
    try:
        with portalocker.Lock(str(path), timeout=2):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[analytics_logger] Save error: {e}")

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
    # print(f"[analytics_logger] {entry}")

# 🔎 Gelişmiş sorgu: filtreli okuma
def search_analytics(action=None, user=None, since=None, until=None, limit=50):
    """
    Son X analytics eventini getir, filtrele.
    """
    results = []
    files = sorted(ANALYTICS_DIR.glob("*.json"), reverse=True)
    for file in files:
        day_data = _load_data(file)
        for entry in reversed(day_data):
            if action and entry.get("action") != action:
                continue
            if user and entry.get("user") != user:
                continue
            if since and entry.get("timestamp") < since:
                continue
            if until and entry.get("timestamp") > until:
                continue
            results.append(entry)
            if len(results) >= limit:
                return list(reversed(results))
    return list(reversed(results))

# 🎯 Analiz fonksiyonu: basit istatistik döndürür
def action_stats(days=7):
    """
    Son N günde action sayımını döndürür.
    """
    from collections import Counter
    stats = Counter()
    files = sorted(ANALYTICS_DIR.glob("*.json"), reverse=True)[:days]
    for file in files:
        for entry in _load_data(file):
            stats[entry.get("action")] += 1
    return dict(stats)

# Dışa aktarma örneği (CSV)
def export_to_csv(filename="analytics_export.csv", limit=1000):
    import csv
    results = search_analytics(limit=limit)
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["timestamp", "user", "action", "details"])
        writer.writeheader()
        for entry in results:
            entry["details"] = json.dumps(entry["details"], ensure_ascii=False)
            writer.writerow(entry)
    print(f"✅ Analytics exported: {filename}")

# Kullanım:
# log_analytics("gavatbaba", "group_gpt_reply_sent", {"msg": "test"})
# print(search_analytics(action="group_gpt_reply_sent", user="gavatbaba"))
# print(action_stats())
# export_to_csv()

