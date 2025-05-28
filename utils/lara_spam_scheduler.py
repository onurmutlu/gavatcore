#!/usr/bin/env python3
"""
Lara Özel Spam Scheduler - Grup Frekansına Göre Akıllı Mesajlaşma
Bu modül Lara için grup aktivitesine uyum sağlayan akıllı spam sistemi sağlar.
"""

import asyncio
import time
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from utils.log_utils import log_event
from telethon.errors import ChatWriteForbiddenError

class LaraSpamScheduler:
    def __init__(self):
        self.group_stats = {}
        self.banned_groups = set()
        self.last_spam_times = {}  # {group_id: timestamp}
        self.group_message_history = {}  # {group_id: [(timestamp, sender_id), ...]}
        self.last_message_senders = {}  # {group_id: last_sender_id}
        
        # Lara için akıllı ayarlar
        self.MIN_INTERVAL = 120  # 2 dakika minimum
        self.MAX_INTERVAL = 240  # 4 dakika maksimum
        self.ACTIVE_HOURS = [(9, 12), (14, 18), (20, 24)]  # Aktif saatler
        self.MESSAGE_HISTORY_WINDOW = 3600  # 1 saat pencere
        
    def is_active_hour(self) -> bool:
        """Aktif saat kontrolü"""
        current_hour = datetime.now().hour
        for start, end in self.ACTIVE_HOURS:
            if start <= current_hour < end:
                return True
        return False
    
    def update_group_activity(self, group_id: int, sender_id: int):
        """Grup aktivitesini güncelle"""
        current_time = time.time()
        
        # Grup mesaj geçmişini güncelle
        if group_id not in self.group_message_history:
            self.group_message_history[group_id] = []
        
        # Yeni mesajı ekle
        self.group_message_history[group_id].append((current_time, sender_id))
        
        # Son mesaj göndereni kaydet
        self.last_message_senders[group_id] = sender_id
        
        # Eski mesajları temizle (1 saatten eski)
        self.group_message_history[group_id] = [
            (timestamp, sender) for timestamp, sender in self.group_message_history[group_id]
            if current_time - timestamp < self.MESSAGE_HISTORY_WINDOW
        ]
    
    def get_group_frequency(self, group_id: int) -> float:
        """Grubun mesaj frekansını hesapla (mesaj/dakika)"""
        if group_id not in self.group_message_history:
            return 0.1  # Varsayılan düşük frekans
        
        current_time = time.time()
        messages = self.group_message_history[group_id]
        
        if len(messages) < 2:
            return 0.1
        
        # Son 30 dakikadaki mesajları say
        recent_messages = [
            timestamp for timestamp, _ in messages
            if current_time - timestamp < 1800  # 30 dakika
        ]
        
        if len(recent_messages) == 0:
            return 0.1
        
        # Mesaj/dakika hesapla
        frequency = len(recent_messages) / 30.0
        return max(0.1, min(frequency, 10.0))  # 0.1-10 mesaj/dakika arası
    
    def can_send_after_others(self, group_id: int, bot_user_id: int) -> bool:
        """Bot'tan sonra başka biri mesaj attı mı kontrol et"""
        if group_id not in self.group_message_history:
            return True
        
        messages = self.group_message_history[group_id]
        if len(messages) == 0:
            return True
        
        # Son mesajı kontrol et
        last_sender = self.last_message_senders.get(group_id)
        
        # Eğer son mesaj bot'tan değilse, mesaj atabilir
        return last_sender != bot_user_id
    
    def get_adaptive_interval(self, group_id: int) -> int:
        """Grup frekansına göre adaptif interval hesapla"""
        frequency = self.get_group_frequency(group_id)
        
        # Frekansa göre interval hesapla
        if frequency > 5:  # Çok aktif grup (5+ mesaj/dakika)
            base_interval = random.randint(300, 600)  # 5-10 dakika
        elif frequency > 2:  # Aktif grup (2-5 mesaj/dakika)
            base_interval = random.randint(180, 360)  # 3-6 dakika
        elif frequency > 0.5:  # Orta grup (0.5-2 mesaj/dakika)
            base_interval = random.randint(120, 300)  # 2-5 dakika
        else:  # Sakin grup (0.5> mesaj/dakika)
            base_interval = random.randint(600, 1200)  # 10-20 dakika
        
        # Aktif saatlerde %30 daha hızlı
        if self.is_active_hour():
            base_interval = int(base_interval * 0.7)
        
        # Gece saatlerinde %50 daha yavaş
        current_hour = datetime.now().hour
        if 1 <= current_hour <= 7:
            base_interval = int(base_interval * 1.5)
        
        return max(base_interval, 60)  # Minimum 1 dakika
    
    def can_spam_group(self, group_id: int, bot_user_id: int) -> tuple[bool, str]:
        """Gruba spam atılabilir mi kontrol et"""
        if group_id in self.banned_groups:
            return False, "Grup banlandı"
        
        # Üst üste mesaj kontrolü
        if not self.can_send_after_others(group_id, bot_user_id):
            return False, "Son mesaj bot'tan, başkası mesaj atmalı"
        
        current_time = time.time()
        last_spam = self.last_spam_times.get(group_id, 0)
        interval = self.get_adaptive_interval(group_id)
        
        if current_time - last_spam < interval:
            remaining = interval - (current_time - last_spam)
            return False, f"Interval: {remaining:.0f}s kaldı"
        
        return True, "OK"
    
    def mark_spam_sent(self, group_id: int, bot_user_id: int):
        """Spam gönderildiğini işaretle"""
        current_time = time.time()
        self.last_spam_times[group_id] = current_time
        
        # Bot'un mesajını da grup aktivitesine ekle
        self.update_group_activity(group_id, bot_user_id)
    
    def ban_group(self, group_id: int):
        """Grubu banla"""
        self.banned_groups.add(group_id)
    
    def get_group_stats(self, group_id: int) -> dict:
        """Grup istatistiklerini getir"""
        frequency = self.get_group_frequency(group_id)
        interval = self.get_adaptive_interval(group_id)
        last_sender = self.last_message_senders.get(group_id, "unknown")
        message_count = len(self.group_message_history.get(group_id, []))
        
        return {
            "frequency": frequency,
            "interval": interval,
            "last_sender": last_sender,
            "message_count": message_count
        }

async def lara_adaptive_spam_loop(client, username: str, profile: dict):
    """
    Lara için adaptif spam döngüsü - grup frekansına göre
    """
    if username != "yayincilara":
        log_event(username, "⚠️ Bu scheduler sadece Lara için tasarlandı")
        return
    
    log_event(username, "🧠 Lara adaptif spam scheduler başlatılıyor...")
    
    scheduler = LaraSpamScheduler()
    
    # Bot user ID'sini al
    try:
        me = await client.get_me()
        bot_user_id = me.id
    except Exception as e:
        log_event(username, f"❌ Bot user ID alınamadı: {e}")
        return
    
    # Mesaj havuzunu hazırla
    spam_messages = profile.get("engaging_messages", [])
    if not spam_messages:
        log_event(username, "❌ Spam mesajları bulunamadı")
        return
    
    round_count = 0
    
    while True:
        round_count += 1
        log_event(username, f"🧠 Lara adaptif spam turu #{round_count} başlıyor...")
        
        sent_count = 0
        skipped_count = 0
        total_groups = 0
        
        try:
            dialogs = await client.get_dialogs()
            group_dialogs = [d for d in dialogs if d.is_group]
            total_groups = len(group_dialogs)
            
            # Grupları rastgele karıştır
            random.shuffle(group_dialogs)
            
            for dialog in group_dialogs:
                # Spam kontrolü
                can_spam, reason = scheduler.can_spam_group(dialog.id, bot_user_id)
                if not can_spam:
                    skipped_count += 1
                    if "son mesaj bot'tan" in reason.lower():
                        log_event(username, f"⏭️ [{dialog.name}] atlandı: {reason}")
                    continue
                
                try:
                    # Grup istatistiklerini al
                    stats = scheduler.get_group_stats(dialog.id)
                    
                    # Rastgele mesaj seç
                    message = random.choice(spam_messages)
                    
                    # Mesajı gönder
                    await client.send_message(dialog.id, message)
                    
                    # İstatistikleri güncelle
                    scheduler.mark_spam_sent(dialog.id, bot_user_id)
                    sent_count += 1
                    
                    log_event(username, f"📤 [{dialog.name}] adaptif spam: {message[:50]}... (freq: {stats['frequency']:.1f}/dk, interval: {stats['interval']}s)")
                    
                    # Kısa bekleme (rate limiting)
                    await asyncio.sleep(random.uniform(2, 5))
                    
                except ChatWriteForbiddenError:
                    scheduler.ban_group(dialog.id)
                    log_event(username, f"🚫 [{dialog.name}] yazma engeli - banlandı")
                    
                except Exception as e:
                    log_event(username, f"❌ [{dialog.name}] spam hatası: {e}")
            
            # Tur özeti
            success_rate = (sent_count / total_groups * 100) if total_groups > 0 else 0
            log_event(username, f"✅ Adaptif spam turu #{round_count}: {sent_count} başarılı, {skipped_count} atlandı ({success_rate:.1f}% başarı)")
            
        except Exception as e:
            log_event(username, f"❌ Adaptif spam turu hatası: {e}")
        
        # Sonraki tur için bekleme
        if scheduler.is_active_hour():
            next_wait = random.uniform(300, 600)  # 5-10 dakika (aktif saatler)
        else:
            next_wait = random.uniform(600, 1200)  # 10-20 dakika (pasif saatler)
        
        log_event(username, f"⏰ Sonraki adaptif spam turu: {next_wait/60:.1f} dakika sonra")
        await asyncio.sleep(next_wait)

# Grup mesaj listener'ı - gerçek zamanlı aktivite takibi
async def setup_group_activity_listener(client, username: str, scheduler: LaraSpamScheduler):
    """Grup aktivitesini gerçek zamanlı takip et"""
    from telethon import events
    
    try:
        me = await client.get_me()
        bot_user_id = me.id
    except:
        return
    
    @client.on(events.NewMessage(chats=None))
    async def group_activity_handler(event):
        if not event.is_group:
            return
        
        try:
            sender = await event.get_sender()
            if sender and sender.id != bot_user_id:
                # Sadece bot olmayan mesajları takip et
                scheduler.update_group_activity(event.chat_id, sender.id)
        except:
            pass
    
    log_event(username, "👂 Grup aktivite listener başlatıldı")

async def start_lara_adaptive_spam(client, username: str, profile: dict):
    """Lara adaptif spam sistemini başlatır"""
    if username != "yayincilara":
        return
    
    if not profile.get("group_spam_aggressive"):
        log_event(username, "ℹ️ Adaptif spam aktif değil")
        return
    
    log_event(username, "🧠 Lara adaptif spam sistemi başlatılıyor...")
    
    # Global scheduler instance
    global lara_scheduler
    
    # Grup aktivite listener'ını başlat
    await setup_group_activity_listener(client, username, lara_scheduler)
    
    # Background task olarak başlat
    asyncio.create_task(lara_adaptive_spam_loop(client, username, profile))
    
    log_event(username, "✅ Lara adaptif spam sistemi aktif - grup frekansına uyumlu mesajlaşma!")

# Global instance
lara_scheduler = LaraSpamScheduler() 