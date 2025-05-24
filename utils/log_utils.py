# utils/log_utils.py
import os
from datetime import datetime

LOGS_DIR = "logs"

def log_event(user_id_or_username: str, text: str):
    """
    Kullanıcının log dosyasına zaman damgalı bir olay ekler.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    filename = f"{str(user_id_or_username).replace('@', '')}.log"
    path = os.path.join(LOGS_DIR, filename)

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {text}\n")

def get_logs(user_id_or_username: str, limit: int = 20) -> str:
    """
    Son X log satırını döner. Log yoksa uyarı verir.
    """
    filename = f"{str(user_id_or_username).replace('@', '')}.log"
    path = os.path.join(LOGS_DIR, filename)

    if not os.path.exists(path):
        return "📭 Log bulunamadı."

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return "📭 Log dosyası boş."

    return "".join(lines[-limit:])
