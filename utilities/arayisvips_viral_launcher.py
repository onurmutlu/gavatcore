#!/usr/bin/env python3
"""
🚀 @arayisonlyvips VIRAL BÜYÜTME LAUNCHER
Hedef: 7 gün içinde 1000+ üye, viral growth!

YAŞASIN SPONSORLAR! 🔥
"""

import asyncio
import time
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from telethon import TelegramClient

# Core imports - fonksiyon bazlı
from core import session_manager
import config

class ArayisvipsViralLauncher:
    def __init__(self):
        self.target_group = "@arayisonlyvips"
        self.target_members = 1000  # Hedef üye sayısı
        self.campaign_duration = 7 * 24 * 3600  # 7 gün (saniye)
        self.start_time = time.time()
        
        # İstatistikler
        self.stats = {
            "total_invites_sent": 0,
            "successful_joins": 0,
            "spam_messages_sent": 0,
            "dm_conversations": 0,
            "conversion_rate": 0.0,
            "daily_growth": [],
            "bot_performance": {}
        }
        
        # Bot bilgileri
        self.viral_bots = [
            {"name": "YayınCı-Lara", "session": "sessions/_905382617727.session"},
            {"name": "Geisha", "session": "sessions/_905486306226.session"},
            {"name": "BabaGAVAT", "session": "sessions/_905513272355.session"}
        ]
        
        # Viral mesajlar (32 farklı varyasyon)
        self.viral_messages = [
            # Davet tarzı mesajlar
            "@arayisonlyvips grubuna katıl, harika insanlar var! 🌟",
            "@arayisonlyvips'te seni bekliyoruz, gel tanışalım! 👋",
            "@arayisonlyvips grubunda kaliteli sohbet arıyorsan doğru yerdesin! 💬",
            "@arayisonlyvips'e katılmaya ne dersin? Çok eğlenceli! 🎉",
            "@arayisonlyvips grubumuzda yeni arkadaşlar edinebilirsin! 🤝",
            
            # Topluluk vurgusu
            "@arayisonlyvips ailesi büyüyor, sen de aramıza katıl! 👨‍👩‍👧‍👦",
            "@arayisonlyvips topluluğunda herkes birbirine yardım ediyor! 🤲",
            "@arayisonlyvips grubunda pozitif enerji var, gel sen de! ⚡",
            "@arayisonlyvips'te güzel dostluklar kurabilirsin! 💕",
            "@arayisonlyvips ailesine hoş geldin demeye hazırız! 🏠",
            
            # Samimi yaklaşım
            "Merhaba! @arayisonlyvips grubumuzda güzel sohbetler var 😊",
            "Selam! @arayisonlyvips'e katılmak ister misin? 🙂",
            "Hey! @arayisonlyvips grubunda seni görmek isteriz! 👀",
            "Merhaba arkadaş! @arayisonlyvips'te buluşalım! 🤗",
            "Selam! @arayisonlyvips grubuna bir göz at derim! 👁️",
            
            # Merak uyandıran
            "@arayisonlyvips grubunda neler oluyor biliyor musun? 🤔",
            "@arayisonlyvips'te harika şeyler paylaşılıyor! 📢",
            "@arayisonlyvips grubunu henüz keşfetmedin mi? 🔍",
            "@arayisonlyvips'te sürprizler seni bekliyor! 🎁",
            "@arayisonlyvips'te harika insanlarla tanışma fırsatı! 🤝",
            "@arayisonlyvips grubunda sürprizler var, merak etme gel! 🎁",
            
            # Kısa ve etkili mesajlar
            "@arayisonlyvips 👈 Buraya gel! 🔥",
            "@arayisonlyvips grubuna katıl! 💪",
            "@arayisonlyvips'te görüşelim! 😉",
            "@arayisonlyvips 🎯 Hedef bu grup!",
            "@arayisonlyvips ✨ Kaliteli sohbet!",
            
            # Emoji ağırlıklı mesajlar
            "🚀 @arayisonlyvips 🚀 Hızla büyüyen topluluk! 📈",
            "💎 @arayisonlyvips 💎 VIP seviye sohbet! 👑",
            "🔥 @arayisonlyvips 🔥 Sıcak atmosfer! 🌡️",
            "⚡ @arayisonlyvips ⚡ Enerjik grup! 💥",
            "🌟 @arayisonlyvips 🌟 Parlayan yıldız! ✨",
            
            # Soru tarzı mesajlar
            "@arayisonlyvips grubunu duydun mu? Çok popüler oldu! 📢",
            "@arayisonlyvips'e katıldın mı? Herkesi bekliyor! 👥",
            "@arayisonlyvips grubunda kimler var biliyor musun? 🤔",
            "@arayisonlyvips'te neler konuşuluyor merak ediyor musun? 💭",
            "@arayisonlyvips grubuna neden katılmalısın? Gel gör! 👁️"
        ]
        
        # Spam koruması için kullanılan gruplar ve son gönderim zamanları
        self.group_spam_history = {}
        self.bot_message_history = {}  # Bot başına mesaj geçmişi
        
        # ===== YENİ: DM KULLANICI TAKİP SİSTEMİ =====
        self.dm_user_history = {}  # {bot_name: {user_id: last_invite_timestamp}}
        self.dm_cooldown_hours = 48  # 48 saat = 2 gün cooldown
        
        self.daily_message_limits = {
            "per_group": 3,      # Grup başına günlük max mesaj
            "per_bot": 50,       # Bot başına günlük max mesaj
            "hourly_limit": 10,  # Saatlik max mesaj (bot başına)
            "dm_per_bot_daily": 20,  # Bot başına günlük max DM davet
            "dm_per_hour": 5     # Bot başına saatlik max DM davet
        }

    async def get_bot_client(self, bot_info: dict):
        """Bot client'ını al"""
        try:
            session_path = bot_info["session"]
            bot_name = bot_info["name"]
            
            print(f"🔄 {bot_name} bağlantısı deneniyor: {session_path}")
            
            if not Path(session_path).exists():
                print(f"❌ {bot_name} session dosyası bulunamadı: {session_path}")
                return None, bot_name
            
            # Session dosyası boyutunu kontrol et
            session_size = Path(session_path).stat().st_size
            print(f"📁 {bot_name} session boyutu: {session_size} bytes")
            
            # Client oluştur
            client = TelegramClient(
                session_path,
                config.TELEGRAM_API_ID,
                config.TELEGRAM_API_HASH,
                connection_retries=3,
                retry_delay=2,
                timeout=30
            )
            
            print(f"🔗 {bot_name} client oluşturuldu, bağlanıyor...")
            await client.connect()
            
            if not await client.is_user_authorized():
                print(f"❌ {bot_name} yetkilendirilmemiş!")
                await client.disconnect()
                return None, bot_name
            
            # Bot bilgilerini al
            me = await client.get_me()
            actual_name = f"{me.first_name} (@{me.username or me.id})"
            print(f"✅ {bot_name} başarıyla bağlandı: {actual_name}")
            
            return client, actual_name
            
        except Exception as e:
            print(f"❌ {bot_name} client hatası: {e}")
            print(f"🔍 {bot_name} hata detayı: {type(e).__name__}")
            return None, bot_name

    async def initialize_campaign(self):
        """Kampanyayı başlat"""
        print("🚀 @arayisonlyvips VIRAL KAMPANYA BAŞLIYOR!")
        print("=" * 60)
        print(f"🎯 Hedef: {self.target_members} üye")
        print(f"⏰ Süre: 7 gün")
        print(f"🤖 Aktif botlar: {len(self.viral_bots)}")
        print(f"💬 Viral mesajlar: {len(self.viral_messages)}")
        print("=" * 60)
        
        # Tüm botları başlat
        tasks = []
        for bot_info in self.viral_bots:
            task = asyncio.create_task(self.run_viral_bot(bot_info))
            tasks.append(task)
        
        # Monitoring task
        monitor_task = asyncio.create_task(self.monitor_campaign())
        tasks.append(monitor_task)
        
        # Tüm task'ları çalıştır
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run_viral_bot(self, bot_info: dict):
        """Viral bot çalıştır"""
        try:
            bot_name = bot_info["name"]
            print(f"🤖 {bot_name} viral modu başlatılıyor...")
            
            # Client al
            client, actual_name = await self.get_bot_client(bot_info)
            if not client:
                return
            
            # Bot performans tracking
            self.stats["bot_performance"][actual_name] = {
                "spam_sent": 0,
                "invites_sent": 0,
                "dm_conversations": 0,
                "start_time": time.time()
            }
            
            # Ana viral döngü
            while time.time() - self.start_time < self.campaign_duration:
                try:
                    # 1. Grup spam (viral mesajlar)
                    await self.send_viral_spam(client, actual_name)
                    
                    # 2. DM davet kampanyası
                    await self.run_dm_invite_campaign(client, actual_name)
                    
                    # Bot arası bekleme (rate limiting)
                    await asyncio.sleep(random.randint(300, 600))  # 5-10 dakika
                    
                except Exception as e:
                    print(f"❌ {actual_name} viral bot hatası: {e}")
                    await asyncio.sleep(1800)  # 30 dakika bekle
            
            await client.disconnect()
            print(f"✅ {actual_name} viral kampanya tamamlandı!")
            
        except Exception as e:
            print(f"💥 {bot_name} viral bot kritik hata: {e}")

    def is_safe_to_send_message(self, bot_name: str, group_id: int) -> tuple[bool, str]:
        """Mesaj gönderimi güvenli mi kontrol et"""
        current_time = time.time()
        today = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        
        # Bot mesaj geçmişini initialize et
        if bot_name not in self.bot_message_history:
            self.bot_message_history[bot_name] = {
                "daily": {},
                "hourly": {},
                "groups": {}
            }
        
        bot_history = self.bot_message_history[bot_name]
        
        # Günlük bot limiti kontrolü
        daily_count = bot_history["daily"].get(today, 0)
        if daily_count >= self.daily_message_limits["per_bot"]:
            return False, f"Bot günlük limit aşıldı ({daily_count}/{self.daily_message_limits['per_bot']})"
        
        # Saatlik bot limiti kontrolü
        hourly_count = bot_history["hourly"].get(current_hour, 0)
        if hourly_count >= self.daily_message_limits["hourly_limit"]:
            return False, f"Bot saatlik limit aşıldı ({hourly_count}/{self.daily_message_limits['hourly_limit']})"
        
        # Grup bazlı limit kontrolü
        group_key = f"{group_id}_{today}"
        group_count = bot_history["groups"].get(group_key, 0)
        if group_count >= self.daily_message_limits["per_group"]:
            return False, f"Grup günlük limit aşıldı ({group_count}/{self.daily_message_limits['per_group']})"
        
        # Son mesaj zamanı kontrolü (minimum 30 dakika ara)
        if group_id in self.group_spam_history:
            last_sent = self.group_spam_history[group_id]
            time_diff = current_time - last_sent
            if time_diff < 1800:  # 30 dakika = 1800 saniye
                remaining = int((1800 - time_diff) / 60)
                return False, f"Grup için {remaining} dakika daha bekle"
        
        return True, "Güvenli"

    def record_message_sent(self, bot_name: str, group_id: int):
        """Gönderilen mesajı kaydet"""
        current_time = time.time()
        today = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        
        # Bot geçmişini güncelle
        bot_history = self.bot_message_history[bot_name]
        
        # Günlük sayacı
        bot_history["daily"][today] = bot_history["daily"].get(today, 0) + 1
        
        # Saatlik sayacı
        bot_history["hourly"][current_hour] = bot_history["hourly"].get(current_hour, 0) + 1
        
        # Grup sayacı
        group_key = f"{group_id}_{today}"
        bot_history["groups"][group_key] = bot_history["groups"].get(group_key, 0) + 1
        
        # Grup spam geçmişi
        self.group_spam_history[group_id] = current_time

    def get_smart_message(self, bot_name: str, group_title: str) -> str:
        """Akıllı mesaj seçimi - bot ve grup bazlı"""
        # Bot tipine göre mesaj kategorisi seç
        if "geisha" in bot_name.lower() or "xxx" in bot_name.lower():
            # Geisha için daha çekici mesajlar
            preferred_messages = [msg for msg in self.viral_messages if any(emoji in msg for emoji in ["🔥", "💋", "💎", "⚡"])]
        elif "yayinci" in bot_name.lower() or "lara" in bot_name.lower():
            # YayınCı için daha samimi mesajlar
            preferred_messages = [msg for msg in self.viral_messages if any(word in msg for word in ["Merhaba", "Selam", "Hey"])]
        elif "baba" in bot_name.lower() or "gavat" in bot_name.lower():
            # BabaGAVAT için güçlü mesajlar
            preferred_messages = [msg for msg in self.viral_messages if any(emoji in msg for emoji in ["💪", "👑", "🚀", "🎯"])]
        else:
            preferred_messages = self.viral_messages
        
        # Grup tipine göre ek filtreleme
        if "vip" in group_title.lower():
            # VIP gruplar için özel mesajlar
            vip_messages = [msg for msg in preferred_messages if any(word in msg for word in ["VIP", "özel", "kaliteli", "💎"])]
            if vip_messages:
                preferred_messages = vip_messages
        
        # Rastgele seç ama aynı mesajı tekrar etme
        if not hasattr(self, 'recent_messages'):
            self.recent_messages = {}
        
        bot_recent = self.recent_messages.get(bot_name, [])
        available_messages = [msg for msg in preferred_messages if msg not in bot_recent[-5:]]  # Son 5 mesajı hariç tut
        
        if not available_messages:
            available_messages = preferred_messages  # Tüm mesajlar kullanıldıysa reset
            self.recent_messages[bot_name] = []
        
        selected_message = random.choice(available_messages)
        
        # Mesaj geçmişini güncelle
        if bot_name not in self.recent_messages:
            self.recent_messages[bot_name] = []
        self.recent_messages[bot_name].append(selected_message)
        
        return selected_message

    async def send_viral_spam(self, client, bot_name: str):
        """Viral spam mesajları gönder - GELİŞTİRİLMİŞ SPAM KORUMASLI"""
        try:
            # Dialog'ları al
            dialogs = await client.get_dialogs()
            group_dialogs = [d for d in dialogs if d.is_group]
            
            print(f"  📊 {bot_name} toplam grup: {len(group_dialogs)}")
            
            # Grupları karıştır ve seç
            random.shuffle(group_dialogs)
            selected_groups = group_dialogs[:15]  # Max 15 grup dene
            
            sent_count = 0
            skipped_count = 0
            
            for dialog in selected_groups:
                try:
                    # Spam güvenlik kontrolü
                    is_safe, reason = self.is_safe_to_send_message(bot_name, dialog.id)
                    if not is_safe:
                        print(f"  ⏭️ {dialog.title}: {reason}")
                        skipped_count += 1
                        continue
                    
                    # Akıllı mesaj seçimi
                    message = self.get_smart_message(bot_name, dialog.title)
                    
                    # Mesaj gönder
                    await client.send_message(dialog.id, message)
                    
                    # Kayıt tut
                    self.record_message_sent(bot_name, dialog.id)
                    
                    # İstatistikleri güncelle
                    self.stats["spam_messages_sent"] += 1
                    self.stats["bot_performance"][bot_name]["spam_sent"] += 1
                    sent_count += 1
                    
                    print(f"  📤 {dialog.title}: {message[:50]}...")
                    
                    # Dinamik rate limiting (başarılı gönderim sonrası daha uzun bekle)
                    wait_time = random.uniform(5, 12)  # 5-12 saniye
                    await asyncio.sleep(wait_time)
                    
                    # Her 3 mesajda bir uzun ara
                    if sent_count % 3 == 0:
                        long_wait = random.uniform(30, 60)  # 30-60 saniye
                        print(f"  ⏸️ Güvenlik arası: {long_wait:.1f} saniye...")
                        await asyncio.sleep(long_wait)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "banned" in error_msg.lower():
                        print(f"  🚫 {dialog.title}: Bot banlanmış")
                    elif "flood" in error_msg.lower():
                        print(f"  🌊 {dialog.title}: Flood koruması, 5 dakika bekle")
                        await asyncio.sleep(300)  # 5 dakika bekle
                    elif "spam" in error_msg.lower():
                        print(f"  ⚠️ {dialog.title}: Spam algılandı, 10 dakika bekle")
                        await asyncio.sleep(600)  # 10 dakika bekle
                    else:
                        print(f"  ❌ {dialog.title}: {error_msg}")
                    continue
            
            print(f"  ✅ {bot_name} spam turu: {sent_count} gönderildi, {skipped_count} atlandı")
            
            # Başarı oranı düşükse uyarı
            if sent_count > 0:
                success_rate = (sent_count / (sent_count + skipped_count)) * 100
                if success_rate < 30:
                    print(f"  ⚠️ {bot_name} düşük başarı oranı: %{success_rate:.1f}")
            
        except Exception as e:
            print(f"❌ {bot_name} viral spam genel hata: {e}")

    async def run_dm_invite_campaign(self, client, bot_name: str):
        """DM davet kampanyası - GELİŞTİRİLMİŞ KULLANICI TAKİP SİSTEMİ"""
        try:
            print(f"  📩 {bot_name} DM davet kampanyası başlatılıyor...")
            
            # Bot için DM geçmişini initialize et
            if bot_name not in self.dm_user_history:
                self.dm_user_history[bot_name] = {}
            
            # Günlük ve saatlik DM limitlerini kontrol et
            dm_safe, dm_reason = self.is_safe_to_send_dm(bot_name)
            if not dm_safe:
                print(f"  🚫 {bot_name} DM limit: {dm_reason}")
                return
            
            # Son mesajlaşmaları al (daha fazla dialog)
            dialogs = await client.get_dialogs(limit=100)
            dm_dialogs = [d for d in dialogs if d.is_user and not d.entity.bot]
            
            print(f"  📊 {bot_name} toplam DM dialog: {len(dm_dialogs)}")
            
            # Kullanıcıları filtrele (cooldown kontrolü)
            available_users = []
            current_time = time.time()
            
            for dialog in dm_dialogs:
                user = dialog.entity
                user_id = user.id
                
                # Kullanıcı cooldown kontrolü
                if user_id in self.dm_user_history[bot_name]:
                    last_invite = self.dm_user_history[bot_name][user_id]
                    time_diff = current_time - last_invite
                    cooldown_seconds = self.dm_cooldown_hours * 3600
                    
                    if time_diff < cooldown_seconds:
                        remaining_hours = (cooldown_seconds - time_diff) / 3600
                        continue  # Bu kullanıcıyı atla
                
                available_users.append(dialog)
            
            print(f"  ✅ {bot_name} cooldown sonrası uygun kullanıcı: {len(available_users)}")
            
            if not available_users:
                print(f"  ⏰ {bot_name} tüm kullanıcılar cooldown'da")
                return
            
            # Rastgele sırala ve limit uygula
            random.shuffle(available_users)
            target_users = available_users[:10]  # Max 10 DM (güvenlik için)
            
            invite_count = 0
            skipped_count = 0
            
            for dialog in target_users:
                try:
                    user = dialog.entity
                    user_id = user.id
                    
                    # Son kontrol - DM limiti
                    dm_safe, dm_reason = self.is_safe_to_send_dm(bot_name)
                    if not dm_safe:
                        print(f"  🚫 {bot_name} DM limit aşıldı: {dm_reason}")
                        break
                    
                    # Akıllı davet mesajı seç
                    invite_msg = self.get_smart_dm_message(bot_name, user.first_name or "arkadaş")
                    
                    # Mesaj gönder
                    await client.send_message(user_id, invite_msg)
                    
                    # Kullanıcı geçmişini kaydet
                    self.dm_user_history[bot_name][user_id] = current_time
                    
                    # DM sayacını güncelle
                    self.record_dm_sent(bot_name)
                    
                    # İstatistikleri güncelle
                    self.stats["total_invites_sent"] += 1
                    self.stats["bot_performance"][bot_name]["invites_sent"] += 1
                    invite_count += 1
                    
                    user_name = user.first_name or user.username or "Anonim"
                    print(f"  📩 {bot_name} -> {user_name}: DM davet gönderildi")
                    
                    # Rate limiting (daha uzun bekleme)
                    await asyncio.sleep(random.uniform(30, 60))  # 30-60 saniye
                    
                except Exception as e:
                    error_msg = str(e)
                    if "flood" in error_msg.lower():
                        print(f"  🌊 {bot_name} DM flood: 10 dakika bekle")
                        await asyncio.sleep(600)  # 10 dakika bekle
                        break
                    elif "spam" in error_msg.lower():
                        print(f"  ⚠️ {bot_name} DM spam algılandı: 30 dakika bekle")
                        await asyncio.sleep(1800)  # 30 dakika bekle
                        break
                    else:
                        print(f"  ❌ {bot_name} DM hatası: {e}")
                        skipped_count += 1
                        continue
            
            print(f"  ✅ {bot_name} DM kampanyası: {invite_count} davet, {skipped_count} hata")
            
            # Başarı oranı kontrolü
            if invite_count > 0:
                success_rate = (invite_count / (invite_count + skipped_count)) * 100
                if success_rate < 50:
                    print(f"  ⚠️ {bot_name} düşük DM başarı oranı: %{success_rate:.1f}")
            
        except Exception as e:
            print(f"❌ {bot_name} DM kampanya genel hata: {e}")

    def is_safe_to_send_dm(self, bot_name: str) -> tuple[bool, str]:
        """DM gönderimi güvenli mi kontrol et"""
        current_time = time.time()
        today = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        
        # Bot DM geçmişini initialize et
        if bot_name not in self.bot_message_history:
            self.bot_message_history[bot_name] = {
                "daily": {},
                "hourly": {},
                "dm_daily": {},
                "dm_hourly": {}
            }
        
        bot_history = self.bot_message_history[bot_name]
        
        # Günlük DM limiti kontrolü
        daily_dm_count = bot_history["dm_daily"].get(today, 0)
        if daily_dm_count >= self.daily_message_limits["dm_per_bot_daily"]:
            return False, f"Bot günlük DM limit aşıldı ({daily_dm_count}/{self.daily_message_limits['dm_per_bot_daily']})"
        
        # Saatlik DM limiti kontrolü
        hourly_dm_count = bot_history["dm_hourly"].get(current_hour, 0)
        if hourly_dm_count >= self.daily_message_limits["dm_per_hour"]:
            return False, f"Bot saatlik DM limit aşıldı ({hourly_dm_count}/{self.daily_message_limits['dm_per_hour']})"
        
        return True, "DM güvenli"

    def record_dm_sent(self, bot_name: str):
        """DM gönderimini kaydet"""
        today = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        
        if bot_name not in self.bot_message_history:
            self.bot_message_history[bot_name] = {
                "daily": {},
                "hourly": {},
                "dm_daily": {},
                "dm_hourly": {}
            }
        
        bot_history = self.bot_message_history[bot_name]
        
        # Günlük DM sayacını artır
        bot_history["dm_daily"][today] = bot_history["dm_daily"].get(today, 0) + 1
        
        # Saatlik DM sayacını artır
        bot_history["dm_hourly"][current_hour] = bot_history["dm_hourly"].get(current_hour, 0) + 1

    def get_smart_dm_message(self, bot_name: str, user_name: str) -> str:
        """Akıllı DM mesajı seç - bot karakterine göre"""
        
        # Bot karakterine göre mesaj havuzları
        if "lara" in bot_name.lower():
            messages = [
                f"Merhaba {user_name}! 😊 @arayisonlyvips grubumuzda güzel sohbetler var, katılmak ister misin?",
                f"Selam {user_name}! 💕 @arayisonlyvips'te harika bir topluluk oluşturduk, sen de aramıza katıl!",
                f"Hey {user_name}! 🌟 @arayisonlyvips grubunda seni görmek isteriz, ne dersin?",
                f"Merhaba {user_name}! 🎉 @arayisonlyvips'te eğlenceli anlar yaşıyoruz, gel sen de!",
                f"Selam {user_name}! ✨ @arayisonlyvips grubumuzda yeni arkadaşlar edinebilirsin!"
            ]
        elif "geisha" in bot_name.lower():
            messages = [
                f"Konnichiwa {user_name}! 🎌 @arayisonlyvips grubunda kaliteli sohbetler var, katılır mısın?",
                f"Merhaba {user_name}! 💎 @arayisonlyvips'te özel bir topluluk var, sen de gel!",
                f"Selam {user_name}! 🌸 @arayisonlyvips grubumuzda güzel dostluklar kurabilirsin!",
                f"Hey {user_name}! 👑 @arayisonlyvips'te VIP seviye sohbet arıyorsan doğru yerdesin!",
                f"Merhaba {user_name}! 🔥 @arayisonlyvips grubunda sıcak atmosfer var, gel tanışalım!"
            ]
        elif "gavat" in bot_name.lower():
            messages = [
                f"Selam {user_name}! 💪 @arayisonlyvips grubuna katılmaya ne dersin? Güçlü bir topluluk!",
                f"Hey {user_name}! 🚀 @arayisonlyvips'te hızla büyüyen bir grup var, katıl bize!",
                f"Merhaba {user_name}! ⚡ @arayisonlyvips grubunda enerjik sohbetler dönüyor!",
                f"Selam {user_name}! 🎯 @arayisonlyvips hedef grup, sen de aramıza katıl!",
                f"Hey {user_name}! 🔥 @arayisonlyvips'te gücün zirvesi, gel sen de!"
            ]
        else:
            # Genel mesajlar
            messages = [
                f"Merhaba {user_name}! @arayisonlyvips grubumuzda güzel sohbetler var, katılmak ister misin? 😊",
                f"Selam {user_name}! @arayisonlyvips'te harika bir topluluk oluşturduk, sen de gel! 🌟",
                f"Hey {user_name}! @arayisonlyvips grubunda seni görmek isteriz! 👋",
                f"Merhaba {user_name}! @arayisonlyvips'te kaliteli sohbet arıyorsan doğru yerdesin! 💬",
                f"Selam {user_name}! @arayisonlyvips grubumuzda yeni arkadaşlar edinebilirsin! 🤝"
            ]
        
        return random.choice(messages)

    async def monitor_campaign(self):
        """Kampanya monitoring"""
        while time.time() - self.start_time < self.campaign_duration:
            try:
                # İstatistikleri güncelle
                await self.update_campaign_stats()
                
                # Günlük rapor
                await self.generate_daily_report()
                
                # 1 saat bekle
                await asyncio.sleep(3600)
                
            except Exception as e:
                print(f"❌ Monitoring hatası: {e}")
                await asyncio.sleep(1800)

    async def update_campaign_stats(self):
        """Kampanya istatistiklerini güncelle"""
        try:
            elapsed_time = time.time() - self.start_time
            elapsed_days = elapsed_time / (24 * 3600)
            
            # Conversion rate hesapla
            if self.stats["total_invites_sent"] > 0:
                self.stats["conversion_rate"] = (
                    self.stats["successful_joins"] / self.stats["total_invites_sent"]
                ) * 100
            
            # Günlük büyüme
            daily_growth = {
                "day": int(elapsed_days) + 1,
                "invites_sent": self.stats["total_invites_sent"],
                "spam_messages": self.stats["spam_messages_sent"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.stats["daily_growth"].append(daily_growth)
            
        except Exception as e:
            print(f"❌ Stats güncelleme hatası: {e}")

    async def generate_daily_report(self):
        """Günlük rapor oluştur"""
        try:
            elapsed_time = time.time() - self.start_time
            elapsed_days = elapsed_time / (24 * 3600)
            remaining_days = 7 - elapsed_days
            
            print("\n" + "="*60)
            print(f"📊 @arayisonlyvips VIRAL KAMPANYA RAPORU - GÜN {int(elapsed_days)+1}")
            print("="*60)
            print(f"🎯 Hedef: {self.target_members} üye")
            print(f"⏰ Kalan süre: {remaining_days:.1f} gün")
            print(f"📤 Toplam davet: {self.stats['total_invites_sent']}")
            print(f"💬 Spam mesajları: {self.stats['spam_messages_sent']}")
            print(f"📈 Conversion rate: {self.stats['conversion_rate']:.2f}%")
            print("\n🤖 Bot Performansları:")
            
            for bot, perf in self.stats["bot_performance"].items():
                runtime = (time.time() - perf["start_time"]) / 3600  # saat
                print(f"  {bot}: {perf['spam_sent']} spam, {perf['invites_sent']} davet ({runtime:.1f}h)")
            
            print("="*60)
            
            # Raporu dosyaya kaydet
            report_file = Path(f"arayisvips_viral_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Rapor kaydedildi: {report_file}")
            
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {e}")

    def get_campaign_summary(self) -> dict:
        """Kampanya özeti"""
        elapsed_time = time.time() - self.start_time
        return {
            "campaign_duration": elapsed_time,
            "target_members": self.target_members,
            "stats": self.stats,
            "viral_bots": len(self.viral_bots),
            "messages_count": len(self.viral_messages)
        }

async def main():
    """Ana fonksiyon"""
    print("🚀 @arayisonlyvips VIRAL BÜYÜTME BAŞLIYOR!")
    print("YAŞASIN SPONSORLAR! 🔥")
    print()
    
    launcher = ArayisvipsViralLauncher()
    
    try:
        await launcher.initialize_campaign()
        
    except KeyboardInterrupt:
        print("\n🛑 Kampanya kullanıcı tarafından durduruldu!")
        
    except Exception as e:
        print(f"💥 Kampanya kritik hata: {e}")
        
    finally:
        # Final rapor
        summary = launcher.get_campaign_summary()
        print("\n📋 KAMPANYA ÖZETİ:")
        print(f"⏰ Süre: {summary['campaign_duration']/3600:.1f} saat")
        print(f"📤 Toplam davet: {summary['stats']['total_invites_sent']}")
        print(f"💬 Spam mesajları: {summary['stats']['spam_messages_sent']}")
        print(f"📈 Conversion: {summary['stats']['conversion_rate']:.2f}%")
        print("\n🎉 VIRAL KAMPANYA TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(main()) 