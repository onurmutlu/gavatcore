# core/license_checker.py

import os
import json
import datetime
import threading
from utils.log_utils import log_event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data"))
LICENSE_FILE = os.path.join(DATA_DIR, "licenses.json")
DEMO_ALERTS_FILE = os.path.join(DATA_DIR, "demo_alerts.json")
DEFAULT_DEMO_MINUTES = int(os.getenv("DEMO_DURATION_MINUTES", 180))

_lock = threading.Lock()  # File lock: thread/process güvenliği için

class LicenseChecker:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        if not os.path.exists(DEMO_ALERTS_FILE):
            with open(DEMO_ALERTS_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def load_licenses(self):
        with _lock:
            try:
                with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}

    def save_licenses(self, data):
        with _lock:
            with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_demo_alerts(self):
        """Demo uyarı durumlarını yükle"""
        with _lock:
            try:
                with open(DEMO_ALERTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}

    def save_demo_alerts(self, data):
        """Demo uyarı durumlarını kaydet"""
        with _lock:
            with open(DEMO_ALERTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def get_license_status(self, user_id: int) -> str:
        data = self.load_licenses()
        user_id_str = str(user_id)

        license_data = data.get(user_id_str)
        if license_data:
            if license_data.get("is_active"):
                return "active"
            return "inactive"
        return "demo"

    def is_license_valid(self, user_id: int, session_created_at: datetime.datetime, profile: dict = None) -> bool:
        """
        - Sistem botları (owner_id = "system"): her zaman true
        - Müşteri botları: owner_id'ye göre lisans kontrolü
        - Normal kullanıcılar: user_id'ye göre lisans kontrolü
        """
        # Sistem botları için lisans kontrolü yapma
        if profile and profile.get("owner_id") == "system":
            return True
        
        # Müşteri botları için owner_id'yi kontrol et
        owner_id = user_id
        if profile and profile.get("owner_id") and profile.get("owner_id") != "system":
            owner_id = profile.get("owner_id")
        
        status = self.get_license_status(owner_id)

        if status == "active":
            return True
        elif status == "demo":
            # session_created_at None ise şu anı kullan (fallback)
            if session_created_at is None:
                session_created_at = datetime.datetime.now()
            elapsed = datetime.datetime.now() - session_created_at
            demo_valid = elapsed.total_seconds() < (DEFAULT_DEMO_MINUTES * 60)
            
            # Demo süresi dolmuşsa akıllı uyarı sistemi
            if not demo_valid:
                self._handle_demo_expired(owner_id, profile)
            
            return demo_valid
        return False

    def _handle_demo_expired(self, user_id: int, profile: dict = None):
        """Demo süresi dolduğunda akıllı işlem yap"""
        user_id_str = str(user_id)
        alerts = self.load_demo_alerts()
        
        # Bu kullanıcı için daha önce uyarı verildi mi?
        if user_id_str in alerts:
            return  # Zaten işlem yapıldı
        
        # Bot username'ini al
        bot_username = "unknown_bot"
        if profile:
            bot_username = profile.get("username", "unknown_bot")
        
        # Uyarı kaydı oluştur
        alert_data = {
            "user_id": user_id,
            "bot_username": bot_username,
            "demo_expired_at": datetime.datetime.now().isoformat(),
            "service_suspended": True,
            "admin_notified": True,
            "profile_data": {
                "type": profile.get("type", "unknown") if profile else "unknown",
                "reply_mode": profile.get("reply_mode", "unknown") if profile else "unknown",
                "autospam": profile.get("autospam", False) if profile else False
            }
        }
        
        alerts[user_id_str] = alert_data
        self.save_demo_alerts(alerts)
        
        # Admin paneline log gönder
        log_event("ADMIN_PANEL", f"🚨 DEMO SÜRESİ DOLDU: {bot_username} (ID: {user_id})")
        log_event("ADMIN_PANEL", f"   📊 Bot Tipi: {alert_data['profile_data']['type']}")
        log_event("ADMIN_PANEL", f"   🧠 Yanıt Modu: {alert_data['profile_data']['reply_mode']}")
        log_event("ADMIN_PANEL", f"   📤 Spam Aktif: {alert_data['profile_data']['autospam']}")
        log_event("ADMIN_PANEL", f"   ⏰ Süre Dolma: {alert_data['demo_expired_at']}")
        log_event("ADMIN_PANEL", f"   🛑 Hizmet Durduruldu: Evet")
        log_event("ADMIN_PANEL", f"   💡 Aksiyon: /lisans {user_id} komutu ile aktif edilebilir")
        
        # Bot profilini güvenli moda al (eğer varsa)
        if profile:
            self._suspend_bot_services(bot_username, profile)
        
        log_event(bot_username, f"⏳ Demo süresi doldu - hizmet akıllıca durduruldu")

    def _suspend_bot_services(self, bot_username: str, profile: dict):
        """Bot hizmetlerini zarif bir şekilde durdur"""
        try:
            from core.profile_loader import update_profile
            
            # Spam'i durdur
            if profile.get("autospam", False):
                update_profile(bot_username, {"autospam": False})
                log_event(bot_username, "🛑 Otomatik spam durduruldu (demo süresi)")
            
            # Reply mode'u manuel yap (daha az kaynak kullanımı)
            if profile.get("reply_mode") in ["gpt", "hybrid"]:
                update_profile(bot_username, {"reply_mode": "manual"})
                log_event(bot_username, "🔧 Yanıt modu manuel'e çevrildi (demo süresi)")
            
            # Demo durumu işaretle
            update_profile(bot_username, {
                "demo_expired": True,
                "demo_expired_at": datetime.datetime.now().isoformat(),
                "service_suspended": True
            })
            
            log_event(bot_username, "✅ Bot hizmetleri zarif şekilde durduruldu")
            
        except Exception as e:
            log_event(bot_username, f"❌ Hizmet durdurma hatası: {e}")

    def get_demo_alerts(self) -> dict:
        """Tüm demo uyarılarını getir"""
        return self.load_demo_alerts()

    def clear_demo_alert(self, user_id: int):
        """Demo uyarısını temizle (lisans aktif edildiğinde)"""
        user_id_str = str(user_id)
        alerts = self.load_demo_alerts()
        
        if user_id_str in alerts:
            del alerts[user_id_str]
            self.save_demo_alerts(alerts)
            log_event("ADMIN_PANEL", f"✅ Demo uyarısı temizlendi: {user_id}")

    def reactivate_bot_services(self, user_id: int):
        """Bot hizmetlerini yeniden aktif et"""
        try:
            alerts = self.load_demo_alerts()
            user_id_str = str(user_id)
            
            if user_id_str in alerts:
                alert_data = alerts[user_id_str]
                bot_username = alert_data.get("bot_username", "unknown_bot")
                
                from core.profile_loader import update_profile, load_profile
                
                # Demo durumunu kaldır
                update_profile(bot_username, {
                    "demo_expired": False,
                    "service_suspended": False,
                    "reactivated_at": datetime.datetime.now().isoformat()
                })
                
                # Önceki ayarları geri yükle (eğer uygunsa)
                profile_data = alert_data.get("profile_data", {})
                if profile_data.get("autospam", False):
                    update_profile(bot_username, {"autospam": True})
                    log_event(bot_username, "🚀 Otomatik spam yeniden aktif edildi")
                
                # Reply mode'u geri yükle
                original_mode = profile_data.get("reply_mode", "manualplus")
                if original_mode in ["gpt", "hybrid"]:
                    update_profile(bot_username, {"reply_mode": original_mode})
                    log_event(bot_username, f"🧠 Yanıt modu {original_mode}'e geri yüklendi")
                
                log_event(bot_username, "✅ Bot hizmetleri yeniden aktif edildi")
                log_event("ADMIN_PANEL", f"🎉 BOT REAKTİF EDİLDİ: {bot_username} (ID: {user_id})")
                
                # Uyarıyı temizle
                self.clear_demo_alert(user_id)
                
        except Exception as e:
            log_event("ADMIN_PANEL", f"❌ Bot reaktif etme hatası: {e}")

    def activate_license(self, user_id: int, days: int = 30):
        """Lisansı aktif et ve bot hizmetlerini geri yükle"""
        data = self.load_licenses()
        uid = str(user_id)
        data[uid] = {
            "is_active": True,
            "activated_at": datetime.datetime.now().isoformat(),
            "expires_at": (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat(),
            "license_days": days
        }
        self.save_licenses(data)
        log_event(uid, f"✅ Lisans AKTİF edildi ({days} gün)")
        
        # Bot hizmetlerini yeniden aktif et
        self.reactivate_bot_services(user_id)

    def deactivate_license(self, user_id: int):
        data = self.load_licenses()
        uid = str(user_id)
        if uid in data:
            data[uid]["is_active"] = False
            self.save_licenses(data)
            log_event(uid, "❌ Lisans DEAKTİF edildi")

    def get_session_creation_time(self, user_id: int) -> datetime.datetime:
        """
        Lisans verildiyse 'activated_at', yoksa fallback olarak demo için dosya modifikasyon zamanı kullan.
        """
        data = self.load_licenses()
        user_id_str = str(user_id)
        if user_id_str in data and "activated_at" in data[user_id_str]:
            try:
                return datetime.datetime.fromisoformat(data[user_id_str]["activated_at"])
            except Exception:
                pass
        # Fallback: Dosya yoksa şu anı ver
        try:
            stat = os.stat(LICENSE_FILE)
            return datetime.datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            return datetime.datetime.now()
