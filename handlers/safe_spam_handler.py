#!/usr/bin/env python3
# handlers/safe_spam_handler.py

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError
from utils.log_utils import log_event
from utils.anti_spam_guard import anti_spam_guard
from core.account_monitor import account_monitor
from core.crm_database import crm_db

class SafeSpamHandler:
    def __init__(self):
        self.active_spam_tasks = {}  # {username: task}
        self.spam_statistics = {}  # {username: {"sent": 0, "failed": 0, "groups": []}}

    async def start_safe_spam_loop(self, client: TelegramClient, username: str, profile: dict):
        """Güvenli spam döngüsünü başlat"""
        
        # Zaten aktif spam varsa durdur
        if username in self.active_spam_tasks:
            self.active_spam_tasks[username].cancel()
        
        # Yeni spam task'i başlat
        task = asyncio.create_task(self._safe_spam_loop(client, username, profile))
        self.active_spam_tasks[username] = task
        
        log_event(username, "🛡️ Güvenli spam döngüsü başlatıldı")

    async def stop_safe_spam_loop(self, username: str):
        """Güvenli spam döngüsünü durdur"""
        if username in self.active_spam_tasks:
            self.active_spam_tasks[username].cancel()
            del self.active_spam_tasks[username]
            log_event(username, "🛑 Güvenli spam döngüsü durduruldu")

    async def _safe_spam_loop(self, client: TelegramClient, username: str, profile: dict):
        """Ana güvenli spam döngüsü"""
        
        # İstatistikleri başlat
        self.spam_statistics[username] = {"sent": 0, "failed": 0, "groups": []}
        
        # Paket kontrolü
        from core.package_manager import package_manager
        try:
            me = await client.get_me()
            user_id = me.id
            daily_limit = package_manager.get_limit(user_id, "daily_messages")
            group_limit = package_manager.get_limit(user_id, "groups")
            cooldown_minutes = package_manager.get_limit(user_id, "cooldown_minutes")
            log_event(username, f"📦 Paket limitleri - Günlük: {daily_limit}, Grup: {group_limit}, Cooldown: {cooldown_minutes}dk")
        except Exception as e:
            log_event(username, f"❌ Paket bilgisi alınamadı: {e}")
            daily_limit = 100  # Varsayılan Basic limit
            group_limit = 50
            cooldown_minutes = 5
        
        while True:
            try:
                # Spam güvenlik kontrolü
                safe_to_spam, reason = anti_spam_guard.is_safe_to_spam(username, 0)  # Genel kontrol
                
                if not safe_to_spam:
                    log_event(username, f"🛡️ Spam güvenlik kontrolü: {reason}")
                    await asyncio.sleep(300)  # 5 dakika bekle (BAMGÜM!)
                    continue
                
                # Günlük limit kontrolü
                if self.spam_statistics[username]["sent"] >= daily_limit:
                    log_event(username, f"📦 Günlük mesaj limitine ulaşıldı: {daily_limit}")
                    # Gece yarısına kadar bekle
                    now = datetime.now()
                    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    wait_seconds = (tomorrow - now).total_seconds()
                    await asyncio.sleep(wait_seconds)
                    # İstatistikleri sıfırla
                    self.spam_statistics[username]["sent"] = 0
                    continue
                
                # Dialog'ları al
                dialogs = await self._get_safe_dialogs(client, username)
                
                if not dialogs:
                    log_event(username, "📭 Spam için uygun grup bulunamadı")
                    await asyncio.sleep(180)  # 3 dakika bekle
                    continue
                
                # Grup limitine göre dialog sayısını sınırla
                dialogs = dialogs[:group_limit]
                
                # Her grup için spam gönder
                sent_count = 0
                failed_count = 0
                
                for dialog in dialogs:
                    try:
                        # Grup bazlı güvenlik kontrolü
                        group_safe, group_reason = anti_spam_guard.is_safe_to_spam(username, dialog.id)
                        
                        if not group_safe:
                            log_event(username, f"🛡️ Grup güvenlik: {dialog.title} - {group_reason}")
                            continue
                        
                        # Dinamik cooldown hesapla
                        cooldown = anti_spam_guard.calculate_dynamic_cooldown(username, dialog.id)
                        
                        # Mesaj varyasyonu al
                        message = await self._get_safe_message_variant(username, profile)
                        
                        # Mesaj gönder
                        success = await self._send_safe_message(client, username, dialog, message)
                        
                        if success:
                            sent_count += 1
                            anti_spam_guard.record_message_sent(username, dialog.id)
                            
                            # CRM'e kaydet
                            await crm_db.record_message_sent(
                                username, dialog.id, 0, message, "spam"
                            )
                            
                            log_event(username, f"📤 Güvenli spam: {dialog.title}")
                        else:
                            failed_count += 1
                        
                        # Paket bazlı cooldown bekle
                        package_cooldown = cooldown_minutes * 60  # Dakikayı saniyeye çevir
                        final_cooldown = max(cooldown, package_cooldown)
                        await asyncio.sleep(final_cooldown)
                        
                    except Exception as e:
                        log_event(username, f"❌ Grup spam hatası {dialog.title}: {e}")
                        failed_count += 1
                        continue
                
                # İstatistikleri güncelle
                self.spam_statistics[username]["sent"] += sent_count
                self.spam_statistics[username]["failed"] += failed_count
                
                log_event(username, f"✅ Spam turu tamamlandı: {sent_count} başarılı, {failed_count} başarısız")
                
                # Bir sonraki tur için kısa bekleme - BAMGÜM! 🔥
                next_round_delay = random.randint(300, 600)  # 5-10 dakika arası (çok hızlı!)
                log_event(username, f"⏰ Sonraki spam turu: {next_round_delay//60} dakika sonra")
                await asyncio.sleep(next_round_delay)
                
            except asyncio.CancelledError:
                log_event(username, "🛑 Spam döngüsü iptal edildi")
                break
            except Exception as e:
                log_event(username, f"❌ Spam döngüsü hatası: {e}")
                await asyncio.sleep(1800)  # 30 dakika bekle

    async def _get_safe_dialogs(self, client: TelegramClient, username: str) -> List:
        """Güvenli dialog'ları al"""
        try:
            all_dialogs = await client.get_dialogs()
            safe_dialogs = []
            
            for dialog in all_dialogs:
                # Sadece grupları al
                if not dialog.is_group:
                    continue
                
                # Grup risk seviyesini kontrol et
                traffic_count, risk_level = anti_spam_guard.calculate_group_traffic_score(dialog.id)
                
                # Sadece çok riskli durumları atla (düşük trafik grupları dahil et)
                # Tamamen sessiz gruplar bile spam için uygun olabilir
                
                safe_dialogs.append(dialog)
            
            # Rastgele karıştır
            random.shuffle(safe_dialogs)
            
            # Maksimum 20 grup ile sınırla
            return safe_dialogs[:20]
            
        except Exception as e:
            log_event(username, f"❌ Dialog alma hatası: {e}")
            return []

    async def _get_safe_message_variant(self, username: str, profile: dict) -> str:
        """Güvenli mesaj varyasyonu al"""
        try:
            # Profil mesajlarını al
            engaging_messages = profile.get("engaging_messages", [])
            
            if not engaging_messages:
                # Fallback mesajlar
                engaging_messages = [
                    "Merhaba! Nasıl gidiyor? 😊",
                    "Selam! Ne yapıyorsunuz? 🌟",
                    "Hey! Keyifler nasıl? 💫"
                ]
            
            # Rastgele mesaj seç
            base_message = random.choice(engaging_messages)
            
            # Anti-spam guard'dan varyasyon al
            variants = anti_spam_guard.get_safe_message_variants(base_message, 3)
            
            return random.choice(variants)
            
        except Exception as e:
            log_event(username, f"❌ Mesaj varyasyonu hatası: {e}")
            return "Merhaba! 😊"

    async def _send_safe_message(self, client: TelegramClient, username: str, dialog, message: str) -> bool:
        """Güvenli mesaj gönder"""
        try:
            await client.send_message(dialog, message)
            return True
            
        except FloodWaitError as e:
            log_event(username, f"🌊 Flood wait: {e.seconds}s - {dialog.title}")
            
            # Flood wait uyarısı ekle
            anti_spam_guard.add_spam_warning(username, "flood_wait")
            
            # Flood wait süresini bekle
            await asyncio.sleep(min(e.seconds, 3600))  # Maksimum 1 saat bekle
            return False
            
        except ChatWriteForbiddenError:
            log_event(username, f"⚠️ Yazma izni yok: {dialog.title}")
            return False
            
        except UserBannedInChannelError:
            log_event(username, f"🚫 Gruptan banlandı: {dialog.title}")
            
            # Ban uyarısı ekle
            anti_spam_guard.add_spam_warning(username, "banned_from_group")
            return False
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Spam tespiti
            if any(keyword in error_str for keyword in ["spam", "flood", "limit", "too many"]):
                log_event(username, f"🚨 SPAM TESPİTİ: {dialog.title} - {e}")
                anti_spam_guard.add_spam_warning(username, "spam_detected")
                
                # Acil durum - spam'i durdur
                await account_monitor._emergency_response(username, "spambot_warning")
                return False
            
            log_event(username, f"❌ Mesaj gönderme hatası {dialog.title}: {e}")
            return False

    def get_spam_statistics(self, username: str) -> dict:
        """Spam istatistiklerini al"""
        stats = self.spam_statistics.get(username, {"sent": 0, "failed": 0, "groups": []})
        anti_spam_status = anti_spam_guard.get_account_status(username)
        
        return {
            "username": username,
            "is_active": username in self.active_spam_tasks,
            "messages_sent": stats["sent"],
            "messages_failed": stats["failed"],
            "success_rate": stats["sent"] / max(stats["sent"] + stats["failed"], 1) * 100,
            "anti_spam_status": anti_spam_status
        }

    async def emergency_stop_all(self):
        """Tüm spam döngülerini acil durdur"""
        for username in list(self.active_spam_tasks.keys()):
            await self.stop_safe_spam_loop(username)
        log_event("system", "🚨 Tüm spam döngüleri acil durduruldu")

# Global instance
safe_spam_handler = SafeSpamHandler() 