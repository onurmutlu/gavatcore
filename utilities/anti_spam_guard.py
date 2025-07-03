#!/usr/bin/env python3
# utils/anti_spam_guard.py

import time
import random
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from utilities.log_utils import log_event

class AntiSpamGuard:
    def __init__(self):
        self.group_traffic = {}  # {group_id: [timestamp1, timestamp2, ...]}
        self.group_risk_levels = {}  # {group_id: "low"|"medium"|"high"}
        self.account_metadata = {}  # {username: {created_at, risk_score, warnings, etc}}
        self.spam_warnings = {}  # {username: [warning_timestamps]}
        
        # ===== YENİ: BOT MESAJ TARİHÇESİ =====
        self.bot_message_history = {}  # {f"{username}:{group_id}": [timestamp1, timestamp2, ...]}
        
        # Risk thresholds
        self.TRAFFIC_WINDOW = 600  # 10 dakika pencere
        self.LOW_TRAFFIC_THRESHOLD = 3  # 10 dakikada 3'ten az mesaj = düşük trafik
        self.HIGH_TRAFFIC_THRESHOLD = 20  # 10 dakikada 20'den fazla = yüksek trafik
        
        # Cooldown ayarları - BAMGÜM MOD! 🔥
        self.BASE_COOLDOWN = 30   # 30 saniye temel bekleme (çok hızlı!)
        self.MAX_COOLDOWN = 300   # 5 dakika maksimum
        
        # ===== YENİ: ENHANCED SPAM KORUMASI =====
        # Artık konfigürasyondan alınıyor
        
        self._load_metadata()

    def _load_metadata(self):
        """Hesap metadata'sını yükle"""
        try:
            metadata_file = Path("data/account_metadata.json")
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    self.account_metadata = json.load(f)
        except Exception as e:
            log_event("anti_spam", f"❌ Metadata yükleme hatası: {e}")

    def _save_metadata(self):
        """Hesap metadata'sını kaydet"""
        try:
            metadata_file = Path("data/account_metadata.json")
            metadata_file.parent.mkdir(exist_ok=True)
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.account_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_event("anti_spam", f"❌ Metadata kaydetme hatası: {e}")

    def calculate_group_traffic_score(self, group_id: int) -> Tuple[int, str]:
        """Grup trafik skorunu hesapla"""
        current_time = time.time()
        
        # Eski mesajları temizle
        if group_id in self.group_traffic:
            self.group_traffic[group_id] = [
                ts for ts in self.group_traffic[group_id]
                if current_time - ts < self.TRAFFIC_WINDOW
            ]
        else:
            self.group_traffic[group_id] = []
        
        message_count = len(self.group_traffic[group_id])
        
        # Risk seviyesi belirle
        if message_count <= self.LOW_TRAFFIC_THRESHOLD:
            risk_level = "low"
        elif message_count >= self.HIGH_TRAFFIC_THRESHOLD:
            risk_level = "high"
        else:
            risk_level = "medium"
        
        self.group_risk_levels[group_id] = risk_level
        return message_count, risk_level

    def calculate_dynamic_cooldown(self, username: str, group_id: int) -> int:
        """Dinamik cooldown hesapla"""
        
        # Hesap yaşını kontrol et
        account_age_hours = self.get_account_age_hours(username)
        
        # Grup trafik skorunu al
        traffic_count, risk_level = self.calculate_group_traffic_score(group_id)
        
        # Temel cooldown
        cooldown = self.BASE_COOLDOWN
        
        # Hesap yaşı faktörü (ilk 24 saat çok dikkatli)
        if account_age_hours < 24:
            cooldown *= 3  # 6 dakika
            log_event(username, f"🔰 Yeni hesap faktörü: cooldown x3 = {cooldown}s")
        elif account_age_hours < 72:
            cooldown *= 2  # 4 dakika
            log_event(username, f"🔰 Genç hesap faktörü: cooldown x2 = {cooldown}s")
        
        # Trafik faktörü - BAMGÜM MOD! 🔥
        if risk_level == "low":
            cooldown += 60  # +1 dakika (hızlı!)
            log_event(username, f"📉 Düşük trafik faktörü: +60s = {cooldown}s")
        elif risk_level == "high":
            cooldown = max(cooldown // 3, 15)  # Çok hızlı!
            log_event(username, f"📈 Yüksek trafik faktörü: /3 = {cooldown}s")
        
        # Uyarı faktörü
        warning_count = len(self.spam_warnings.get(username, []))
        if warning_count > 0:
            cooldown *= (1 + warning_count)  # Her uyarı için cooldown artır
            log_event(username, f"⚠️ Uyarı faktörü ({warning_count}): cooldown x{1+warning_count} = {cooldown}s")
        
        # Rastgele faktör (pattern'i boz)
        random_factor = random.uniform(0.8, 1.5)
        cooldown = int(cooldown * random_factor)
        
        # Maksimum sınır
        cooldown = min(cooldown, self.MAX_COOLDOWN)
        
        log_event(username, f"🕒 Final cooldown: {cooldown}s (trafik: {traffic_count}, risk: {risk_level})")
        return cooldown

    def get_account_age_hours(self, username: str) -> float:
        """Hesap yaşını saat cinsinden al"""
        try:
            # Önce profil dosyasından dene (daha güvenilir)
            profile_path = Path(f"data/personas/{username}.json")
            if profile_path.exists():
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    created_at_str = profile.get("created_at")
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str)
                        age = datetime.now() - created_at
                        hours = age.total_seconds() / 3600
                        log_event(username, f"📅 Profil yaşı: {hours:.1f} saat ({hours/24:.1f} gün)")
                        return hours
            
            # Profil yoksa metadata'dan dene
            if username in self.account_metadata:
                created_at_str = self.account_metadata[username].get("created_at")
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                    age = datetime.now() - created_at
                    hours = age.total_seconds() / 3600
                    log_event(username, f"📅 Metadata yaşı: {hours:.1f} saat ({hours/24:.1f} gün)")
                    return hours
            
            # Hiçbir bilgi yoksa 0 döndür (yeni hesap muamelesi)
            log_event(username, f"⚠️ Hesap yaşı bulunamadı, yeni hesap muamelesi")
            return 0
            
        except Exception as e:
            log_event(username, f"❌ Hesap yaşı hesaplama hatası: {e}")
            return 0

    def check_enhanced_spam_protection(self, username: str, group_id: int) -> tuple[bool, str]:
        """Enhanced spam koruması - konfigürasyondan ayarları al"""
        from utilities.bot_config_manager import bot_config_manager
        
        # Bot konfigürasyonunu kontrol et
        spam_protection_type = bot_config_manager.get_spam_protection_type(username)
        if spam_protection_type != "enhanced":
            return True, f"{username} için enhanced spam koruması aktif değil"
        
        current_time = time.time()
        key = f"{username}:{group_id}"
        
        # Konfigürasyondan ayarları al
        max_messages_per_minute = bot_config_manager.get_max_messages_per_minute(username)
        minute_window = 60  # 1 dakika
        
        # Bot mesaj geçmişini al
        if key not in self.bot_message_history:
            self.bot_message_history[key] = []
        
        # 1 dakikadan eski mesajları temizle
        self.bot_message_history[key] = [
            timestamp for timestamp in self.bot_message_history[key]
            if current_time - timestamp < minute_window
        ]
        
        # Son 1 dakikadaki mesaj sayısını kontrol et
        recent_message_count = len(self.bot_message_history[key])
        
        if recent_message_count >= max_messages_per_minute:
            return False, f"🚫 {username} enhanced spam koruması: Son 1 dakikada {recent_message_count} mesaj gönderildi (limit: {max_messages_per_minute})"
        
        return True, f"✅ {username} enhanced spam koruması: {recent_message_count}/{max_messages_per_minute} mesaj (son 1 dk)"

    def record_enhanced_spam_message(self, username: str, group_id: int):
        """Enhanced spam koruması olan bot mesajını kaydet"""
        from utilities.bot_config_manager import bot_config_manager
        
        # Enhanced spam koruması aktif mi kontrol et
        spam_protection_type = bot_config_manager.get_spam_protection_type(username)
        if spam_protection_type != "enhanced":
            return
        
        current_time = time.time()
        key = f"{username}:{group_id}"
        
        if key not in self.bot_message_history:
            self.bot_message_history[key] = []
        
        self.bot_message_history[key].append(current_time)
        
        log_event(username, f"📝 {username} enhanced spam mesaj kaydedildi: Grup {group_id}, Son 1 dk: {len(self.bot_message_history[key])} mesaj")

    def is_safe_to_spam(self, username: str, group_id: int) -> Tuple[bool, str]:
        """Spam göndermenin güvenli olup olmadığını kontrol et"""
        
        # ===== YENİ: ENHANCED SPAM KORUMASI KONTROL =====
        from utilities.bot_config_manager import bot_config_manager
        spam_protection_type = bot_config_manager.get_spam_protection_type(username)
        
        if spam_protection_type == "enhanced":
            enhanced_safe, enhanced_reason = self.check_enhanced_spam_protection(username, group_id)
            if not enhanced_safe:
                return False, enhanced_reason
        
        # Hesap yaşı kontrolü
        account_age_hours = self.get_account_age_hours(username)
        
        # İlk 24 saat sadece reply mode
        if account_age_hours < 24:
            return False, f"🔰 Yeni hesap (yaş: {account_age_hours:.1f}h) - sadece reply mode"
        
        # Uyarı kontrolü
        warning_count = len(self.spam_warnings.get(username, []))
        if warning_count >= 3:
            return False, f"⚠️ Çok fazla uyarı ({warning_count}) - spam devre dışı"
        
        # Risk seviyesi kontrolü
        traffic_count, risk_level = self.calculate_group_traffic_score(group_id)
        
        # Yüksek riskli gruplarda çok dikkatli ol
        if risk_level == "low" and account_age_hours < 72:
            return False, f"📉 Düşük trafik + genç hesap - güvenlik için bekleme"
        
        return True, f"✅ Spam güvenli (yaş: {account_age_hours:.1f}h, trafik: {risk_level})"

    def record_message_sent(self, username: str, group_id: int):
        """Gönderilen mesajı kaydet"""
        current_time = time.time()
        
        # ===== YENİ: ENHANCED SPAM KORUMASI MESAJ KAYDI =====
        self.record_enhanced_spam_message(username, group_id)
        
        # Grup trafiğine ekle
        if group_id not in self.group_traffic:
            self.group_traffic[group_id] = []
        self.group_traffic[group_id].append(current_time)
        
        # Hesap metadata'sını güncelle
        if username not in self.account_metadata:
            self.account_metadata[username] = {
                "created_at": datetime.now().isoformat(),
                "total_messages": 0,
                "last_message": None
            }
        
        self.account_metadata[username]["total_messages"] += 1
        self.account_metadata[username]["last_message"] = datetime.now().isoformat()
        
        self._save_metadata()

    def add_spam_warning(self, username: str, warning_type: str = "general"):
        """Spam uyarısı ekle"""
        current_time = time.time()
        
        if username not in self.spam_warnings:
            self.spam_warnings[username] = []
        
        self.spam_warnings[username].append({
            "timestamp": current_time,
            "type": warning_type,
            "date": datetime.now().isoformat()
        })
        
        # Eski uyarıları temizle (7 günden eski)
        week_ago = current_time - (7 * 24 * 3600)
        self.spam_warnings[username] = [
            w for w in self.spam_warnings[username]
            if w["timestamp"] > week_ago
        ]
        
        warning_count = len(self.spam_warnings[username])
        log_event(username, f"⚠️ Spam uyarısı eklendi: {warning_type} (toplam: {warning_count})")
        
        # Metadata'ya kaydet
        if username in self.account_metadata:
            self.account_metadata[username]["warnings"] = warning_count
            self._save_metadata()

    def get_safe_message_variants(self, base_message: str, count: int = 3) -> List[str]:
        """Mesaj varyasyonları oluştur"""
        variants = []
        
        # Emoji varyasyonları
        emoji_sets = [
            ["😊", "😘", "🥰", "💕"],
            ["🔥", "💋", "😈", "🌟"],
            ["🎭", "🎪", "🎡", "🎨"],
            ["💖", "💗", "💘", "💝"],
            ["🌙", "⭐", "✨", "🌺"]
        ]
        
        # Temel mesajdan varyasyonlar oluştur
        for i in range(count):
            variant = base_message
            
            # Rastgele emoji seti seç
            emoji_set = random.choice(emoji_sets)
            
            # Mesajın sonuna rastgele emoji ekle
            if not any(emoji in variant for emoji_set in emoji_sets for emoji in emoji_set):
                variant += f" {random.choice(emoji_set)}"
            
            # Küçük değişiklikler yap
            if i == 1:
                variant = variant.replace("...", ".")
            elif i == 2:
                variant = variant.replace("?", " 😊")
            
            variants.append(variant)
        
        return variants

    def get_account_status(self, username: str) -> Dict:
        """Hesap durumu raporu"""
        account_age_hours = self.get_account_age_hours(username)
        warning_count = len(self.spam_warnings.get(username, []))
        
        metadata = self.account_metadata.get(username, {})
        
        return {
            "username": username,
            "age_hours": account_age_hours,
            "age_status": "new" if account_age_hours < 24 else "young" if account_age_hours < 72 else "mature",
            "warning_count": warning_count,
            "risk_level": "high" if warning_count >= 2 else "medium" if warning_count >= 1 else "low",
            "total_messages": metadata.get("total_messages", 0),
            "last_message": metadata.get("last_message"),
            "spam_safe": warning_count < 3 and account_age_hours >= 24
        }

# Global instance
anti_spam_guard = AntiSpamGuard() 