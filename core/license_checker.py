import os
import json
import datetime
from utils.log_utils import log_event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(BASE_DIR, "../data/licenses.json")
DEFAULT_DEMO_MINUTES = int(os.getenv("DEMO_DURATION_MINUTES", 180))

class LicenseChecker:
    def __init__(self):
        if not os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, 'w') as f:
                json.dump({}, f)

    def load_licenses(self):
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)

    def save_licenses(self, data):
        with open(LICENSE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def get_license_status(self, user_id: int) -> str:
        data = self.load_licenses()
        user_id_str = str(user_id)

        if user_id_str in data:
            license_data = data[user_id_str]
            if license_data.get("is_active"):
                return "active"
            return "inactive"

        return "demo"

    def is_license_valid(self, user_id: int, session_created_at: datetime.datetime, profile: dict = None) -> bool:
        if profile:
            if profile.get("type") == "bot" and profile.get("owner_id") in [None, "system"]:
                return True
            owner_id = profile.get("owner_id", user_id)
        else:
            owner_id = user_id

        status = self.get_license_status(owner_id)

        if status == "active":
            return True
        elif status == "demo":
            elapsed = datetime.datetime.now() - session_created_at
            return elapsed.total_seconds() < (DEFAULT_DEMO_MINUTES * 60)
        return False

    def activate_license(self, user_id: int):
        data = self.load_licenses()
        uid = str(user_id)
        data[uid] = {
            "is_active": True,
            "activated_at": datetime.datetime.now().isoformat()
        }
        self.save_licenses(data)
        log_event(uid, "✅ Lisans AKTİF edildi (admin veya sistem tarafından)")

    def deactivate_license(self, user_id: int):
        data = self.load_licenses()
        uid = str(user_id)
        if uid in data:
            data[uid]["is_active"] = False
            self.save_licenses(data)
            log_event(uid, "❌ Lisans DEAKTİF edildi")

    def get_session_creation_time(self, user_id: int) -> datetime.datetime:
        data = self.load_licenses()
        user_id_str = str(user_id)
        if user_id_str in data and "activated_at" in data[user_id_str]:
            return datetime.datetime.fromisoformat(data[user_id_str]["activated_at"])
        return datetime.datetime.now()  # fallback
