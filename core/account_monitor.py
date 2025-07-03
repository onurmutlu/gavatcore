#!/usr/bin/env python3
# core/account_monitor.py

import asyncio
import time
from typing import Dict, Optional
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserDeactivatedError, AuthKeyUnregisteredError
from utilities.log_utils import log_event
from utilities.anti_spam_guard import anti_spam_guard

class AccountMonitor:
    def __init__(self):
        self.monitoring_active = {}  # {username: bool}
        self.last_spambot_check = {}  # {username: timestamp}
        self.account_health = {}  # {username: {"status": "healthy|warning|banned", "last_check": timestamp}}
        
        # Check intervals
        self.SPAMBOT_CHECK_INTERVAL = 21600  # 6 saat
        self.HEALTH_CHECK_INTERVAL = 3600   # 1 saat

    async def start_monitoring(self, client: TelegramClient, username: str):
        """Hesap izlemeyi başlat"""
        self.monitoring_active[username] = True
        log_event(username, "🔍 Hesap izleme başlatıldı")
        
        # Monitoring loop'u başlat
        asyncio.create_task(self._monitoring_loop(client, username))

    async def stop_monitoring(self, username: str):
        """Hesap izlemeyi durdur"""
        self.monitoring_active[username] = False
        log_event(username, "🛑 Hesap izleme durduruldu")

    async def _monitoring_loop(self, client: TelegramClient, username: str):
        """Ana izleme döngüsü"""
        while self.monitoring_active.get(username, False):
            try:
                # SpamBot kontrolü
                await self._check_spambot_status(client, username)
                
                # Genel sağlık kontrolü
                await self._check_account_health(client, username)
                
                # 1 saat bekle
                await asyncio.sleep(self.HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                log_event(username, f"❌ Monitoring loop hatası: {e}")
                await asyncio.sleep(300)  # 5 dakika bekle ve devam et

    async def _check_spambot_status(self, client: TelegramClient, username: str):
        """@SpamBot'tan durum kontrolü"""
        current_time = time.time()
        last_check = self.last_spambot_check.get(username, 0)
        
        # 6 saatte bir kontrol et
        if current_time - last_check < self.SPAMBOT_CHECK_INTERVAL:
            return
        
        try:
            log_event(username, "🤖 @SpamBot durumu kontrol ediliyor...")
            
            # SpamBot'a mesaj gönder
            spambot = await client.get_entity("@SpamBot")
            await client.send_message(spambot, "/start")
            
            # Yanıt bekle (5 saniye)
            await asyncio.sleep(5)
            
            # Son mesajları al
            messages = await client.get_messages(spambot, limit=3)
            
            spam_detected = False
            warning_message = ""
            
            for message in messages:
                if message.text:
                    text_lower = message.text.lower()
                    
                    # Spam uyarı kelimelerini kontrol et - ama pozitif mesajları hariç tut
                    warning_keywords = [
                        "spam", "flood", "restricted", 
                        "warning", "violation", "abuse", "banned"
                    ]
                    
                    # Pozitif mesajları hariç tut
                    positive_phrases = [
                        "good news", "no limits", "free as a bird", 
                        "all clear", "no restrictions"
                    ]
                    
                    # Pozitif mesaj değilse ve uyarı kelimesi varsa spam olarak işaretle
                    is_positive = any(phrase in text_lower for phrase in positive_phrases)
                    has_warning = any(keyword in text_lower for keyword in warning_keywords)
                    
                    # Debug log ekle
                    log_event(username, f"🔍 SpamBot mesaj analizi: '{text_lower[:50]}...'")
                    log_event(username, f"🔍 Pozitif: {is_positive}, Uyarı: {has_warning}")
                    
                    if has_warning and not is_positive:
                        spam_detected = True
                        warning_message = message.text
                        log_event(username, f"🚨 Spam tespit edildi: pozitif={is_positive}, uyarı={has_warning}")
                        break
                    elif is_positive:
                        log_event(username, f"✅ Pozitif mesaj tespit edildi, spam değil")
                        break
            
            if spam_detected:
                log_event(username, f"⚠️ SPAM UYARISI TESPİT EDİLDİ: {warning_message}")
                
                # Anti-spam guard'a uyarı ekle
                anti_spam_guard.add_spam_warning(username, "spambot_warning")
                
                # Hesap durumunu güncelle
                self.account_health[username] = {
                    "status": "warning",
                    "last_check": current_time,
                    "warning_message": warning_message
                }
                
                # Acil müdahale
                await self._emergency_response(username, "spambot_warning")
                
            else:
                log_event(username, "✅ @SpamBot kontrolü temiz")
                self.account_health[username] = {
                    "status": "healthy",
                    "last_check": current_time
                }
            
            self.last_spambot_check[username] = current_time
            
        except Exception as e:
            log_event(username, f"❌ SpamBot kontrol hatası: {e}")

    async def _check_account_health(self, client: TelegramClient, username: str):
        """Genel hesap sağlığı kontrolü"""
        try:
            # Basit API çağrısı ile hesap durumunu test et
            me = await client.get_me()
            
            if me:
                log_event(username, "💚 Hesap sağlığı: Normal")
                return True
            else:
                log_event(username, "💔 Hesap sağlığı: Sorunlu")
                return False
                
        except UserDeactivatedError:
            log_event(username, "🚫 HESAP DEVRE DIŞI BIRAKILDI!")
            await self._emergency_response(username, "account_deactivated")
            return False
            
        except AuthKeyUnregisteredError:
            log_event(username, "🔑 AUTH KEY GEÇERSİZ!")
            await self._emergency_response(username, "auth_invalid")
            return False
            
        except FloodWaitError as e:
            log_event(username, f"🌊 Flood wait: {e.seconds}s")
            # Flood wait normal bir durum, uyarı verme
            return True
            
        except Exception as e:
            log_event(username, f"❌ Sağlık kontrolü hatası: {e}")
            return False

    async def _emergency_response(self, username: str, emergency_type: str):
        """Acil durum müdahalesi"""
        log_event(username, f"🚨 ACİL DURUM: {emergency_type}")
        
        if emergency_type == "spambot_warning":
            # Spam uyarısı alındı - spam'i durdur
            log_event(username, "🛑 Spam durduruldu - güvenlik modu aktif")
            
            # Bot profilini güvenli moda al
            await self._set_safe_mode(username, True)
            
        elif emergency_type == "account_deactivated":
            # Hesap devre dışı - tamamen durdur
            log_event(username, "🚫 Hesap tamamen devre dışı bırakıldı")
            await self.stop_monitoring(username)
            
        elif emergency_type == "auth_invalid":
            # Auth key geçersiz - session yenilenmeli
            log_event(username, "🔑 Session yenilenmesi gerekiyor")
            await self.stop_monitoring(username)

    async def _set_safe_mode(self, username: str, enabled: bool):
        """Güvenli mod ayarla"""
        try:
            # Bot profilini güncelle
            import json
            from pathlib import Path
            
            profile_path = Path(f"data/personas/{username}.json")
            if profile_path.exists():
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                
                if enabled:
                    profile["autospam"] = False
                    profile["reply_mode"] = "manual"  # Sadece manuel yanıt
                    profile["safe_mode"] = True
                    log_event(username, "🛡️ Güvenli mod aktifleştirildi")
                else:
                    profile["safe_mode"] = False
                    log_event(username, "🔓 Güvenli mod devre dışı bırakıldı")
                
                with open(profile_path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            log_event(username, f"❌ Güvenli mod ayarlama hatası: {e}")

    def get_account_status(self, username: str) -> Dict:
        """Hesap durumu raporu"""
        health = self.account_health.get(username, {"status": "unknown", "last_check": 0})
        anti_spam_status = anti_spam_guard.get_account_status(username)
        
        return {
            "username": username,
            "monitoring_active": self.monitoring_active.get(username, False),
            "health_status": health["status"],
            "last_health_check": health.get("last_check", 0),
            "last_spambot_check": self.last_spambot_check.get(username, 0),
            "warning_message": health.get("warning_message"),
            "anti_spam": anti_spam_status
        }

    async def manual_spambot_check(self, client: TelegramClient, username: str):
        """Manuel SpamBot kontrolü"""
        log_event(username, "🔍 Manuel SpamBot kontrolü başlatıldı")
        await self._check_spambot_status(client, username)

    async def reset_warnings(self, username: str):
        """Uyarıları sıfırla"""
        anti_spam_guard.spam_warnings[username] = []
        self.account_health[username] = {
            "status": "healthy",
            "last_check": time.time()
        }
        log_event(username, "🔄 Uyarılar sıfırlandı")

# Global instance
account_monitor = AccountMonitor() 