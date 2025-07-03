#!/usr/bin/env python3
"""
Dynamic Spam Scheduler - Grup Trafiğine Göre Dinamik Spam Sistemi
Bu modül grup trafiğini analiz ederek spam frequency'sini optimize eder.
"""

import asyncio
import time
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from utilities.log_utils import log_event
from telethon.errors import ChatWriteForbiddenError

# ===== GRUP TRAFİK ANALİZİ =====
group_traffic_stats = {}  # {group_id: {'messages': [timestamps], 'last_spam': timestamp, 'activity_level': str}}
TRAFFIC_WINDOW = 3600  # 1 saat pencere
ANALYSIS_INTERVAL = 300  # 5 dakika analiz interval

# ===== SPAM FREQUENCY AYARLARI =====
SPAM_FREQUENCIES = {
    'very_high': {'interval': (300, 420), 'description': '5-7 dakika (çok yoğun gruplar)'},
    'high': {'interval': (420, 600), 'description': '7-10 dakika (yoğun gruplar)'},
    'medium': {'interval': (600, 900), 'description': '10-15 dakika (orta gruplar)'},
    'low': {'interval': (900, 1800), 'description': '15-30 dakika (sakin gruplar)'},
    'very_low': {'interval': (1800, 3600), 'description': '30-60 dakika (çok sakin gruplar)'}
}

# ===== TRAFİK SEVİYE KRİTERLERİ =====
TRAFFIC_THRESHOLDS = {
    'very_high': 100,  # 1 saatte 100+ mesaj
    'high': 50,        # 1 saatte 50+ mesaj
    'medium': 20,      # 1 saatte 20+ mesaj
    'low': 5,          # 1 saatte 5+ mesaj
    'very_low': 0      # 1 saatte 5'ten az mesaj
}

class DynamicSpamScheduler:
    def __init__(self):
        self.group_stats = {}
        self.banned_groups = set()
        self.last_analysis = 0
        
    def update_group_activity(self, group_id: int, message_count: int = 1):
        """Grup aktivitesini günceller"""
        current_time = time.time()
        
        if group_id not in self.group_stats:
            self.group_stats[group_id] = {
                'messages': [],
                'last_spam': 0,
                'activity_level': 'unknown',
                'total_messages': 0
            }
        
        # Yeni mesajları ekle
        for _ in range(message_count):
            self.group_stats[group_id]['messages'].append(current_time)
        
        self.group_stats[group_id]['total_messages'] += message_count
        
        # Eski mesajları temizle (1 saatten eski)
        self.group_stats[group_id]['messages'] = [
            timestamp for timestamp in self.group_stats[group_id]['messages']
            if current_time - timestamp < TRAFFIC_WINDOW
        ]
    
    def analyze_group_activity(self, group_id: int) -> str:
        """Grup aktivite seviyesini analiz eder"""
        if group_id not in self.group_stats:
            return 'unknown'
        
        current_time = time.time()
        recent_messages = len(self.group_stats[group_id]['messages'])
        
        # Aktivite seviyesini belirle
        for level, threshold in TRAFFIC_THRESHOLDS.items():
            if recent_messages >= threshold:
                self.group_stats[group_id]['activity_level'] = level
                return level
        
        return 'very_low'
    
    def get_spam_interval(self, group_id: int) -> Tuple[int, int]:
        """Grup için optimal spam interval'ını döner"""
        activity_level = self.analyze_group_activity(group_id)
        
        if activity_level in SPAM_FREQUENCIES:
            return SPAM_FREQUENCIES[activity_level]['interval']
        
        # Default: medium activity
        return SPAM_FREQUENCIES['medium']['interval']
    
    def should_spam_group(self, group_id: int) -> bool:
        """Gruba spam atılıp atılmayacağını belirler"""
        if group_id in self.banned_groups:
            return False
        
        if group_id not in self.group_stats:
            return True  # Yeni grup, spam at
        
        current_time = time.time()
        last_spam = self.group_stats[group_id]['last_spam']
        
        # Minimum interval kontrolü
        min_interval, max_interval = self.get_spam_interval(group_id)
        
        if current_time - last_spam < min_interval:
            return False
        
        return True
    
    def mark_spam_sent(self, group_id: int):
        """Spam gönderildiğini işaretle"""
        current_time = time.time()
        
        if group_id not in self.group_stats:
            self.group_stats[group_id] = {
                'messages': [],
                'last_spam': current_time,
                'activity_level': 'unknown',
                'total_messages': 0
            }
        else:
            self.group_stats[group_id]['last_spam'] = current_time
    
    def get_group_stats_summary(self) -> Dict:
        """Grup istatistiklerinin özetini döner"""
        summary = {
            'total_groups': len(self.group_stats),
            'banned_groups': len(self.banned_groups),
            'activity_levels': {},
            'top_active_groups': []
        }
        
        # Aktivite seviyelerine göre grupla
        for group_id, stats in self.group_stats.items():
            level = stats['activity_level']
            if level not in summary['activity_levels']:
                summary['activity_levels'][level] = 0
            summary['activity_levels'][level] += 1
        
        # En aktif grupları bul
        sorted_groups = sorted(
            self.group_stats.items(),
            key=lambda x: len(x[1]['messages']),
            reverse=True
        )[:10]
        
        summary['top_active_groups'] = [
            {
                'group_id': group_id,
                'recent_messages': len(stats['messages']),
                'activity_level': stats['activity_level'],
                'total_messages': stats['total_messages']
            }
            for group_id, stats in sorted_groups
        ]
        
        return summary
    
    async def analyze_all_groups(self, client, username: str):
        """Tüm grupları analiz eder ve istatistikleri günceller"""
        try:
            dialogs = await client.get_dialogs()
            analyzed_count = 0
            
            for dialog in dialogs:
                if not dialog.is_group:
                    continue
                
                try:
                    # Son 50 mesajı analiz et
                    message_count = 0
                    current_time = time.time()
                    
                    async for message in client.iter_messages(dialog.id, limit=50):
                        # Son 1 saat içindeki mesajları say
                        if message.date and (current_time - message.date.timestamp()) < TRAFFIC_WINDOW:
                            message_count += 1
                        else:
                            break
                    
                    # Grup aktivitesini güncelle
                    if message_count > 0:
                        self.update_group_activity(dialog.id, message_count)
                    
                    analyzed_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    log_event(username, f"❌ Grup analiz hatası [{dialog.name}]: {e}")
            
            log_event(username, f"📊 {analyzed_count} grup analiz edildi")
            
        except Exception as e:
            log_event(username, f"❌ Grup analizi genel hatası: {e}")

# Global scheduler instance
dynamic_scheduler = DynamicSpamScheduler()

async def dynamic_spam_loop(client, username: str, profile: dict):
    """
    Dinamik spam döngüsü - grup trafiğine göre optimize edilmiş
    """
    log_event(username, "🚀 Dinamik spam scheduler başlatılıyor...")
    
    # İlk analizi yap
    await dynamic_scheduler.analyze_all_groups(client, username)
    
    # Mesaj havuzunu hazırla
    bot_engaging_messages = profile.get("engaging_messages", [])
    if not bot_engaging_messages:
        bot_engaging_messages = profile.get("group_spam_templates", [])
    
    if not bot_engaging_messages:
        log_event(username, "⚠️ Spam mesajları bulunamadı")
        return
    
    spam_round = 0
    
    while True:
        spam_round += 1
        log_event(username, f"🔄 Dinamik spam turu #{spam_round} başlıyor...")
        
        # Periyodik grup analizi (her 5 dakikada bir)
        current_time = time.time()
        if current_time - dynamic_scheduler.last_analysis > ANALYSIS_INTERVAL:
            await dynamic_scheduler.analyze_all_groups(client, username)
            dynamic_scheduler.last_analysis = current_time
        
        sent_count = 0
        skipped_count = 0
        total_groups = 0
        
        try:
            dialogs = await client.get_dialogs()
            
            # Grupları aktivite seviyesine göre sırala (en aktif önce)
            group_dialogs = [d for d in dialogs if d.is_group]
            group_dialogs.sort(
                key=lambda d: len(dynamic_scheduler.group_stats.get(d.id, {}).get('messages', [])),
                reverse=True
            )
            
            for dialog in group_dialogs:
                total_groups += 1
                
                # Spam kontrolü
                if not dynamic_scheduler.should_spam_group(dialog.id):
                    skipped_count += 1
                    continue
                
                try:
                    # Aktivite seviyesine göre mesaj seç
                    activity_level = dynamic_scheduler.analyze_group_activity(dialog.id)
                    message = random.choice(bot_engaging_messages)
                    
                    # Mesajı gönder
                    await client.send_message(dialog.id, message)
                    
                    # İstatistikleri güncelle
                    dynamic_scheduler.mark_spam_sent(dialog.id)
                    sent_count += 1
                    
                    # Aktivite seviyesi bilgisi
                    interval_info = SPAM_FREQUENCIES.get(activity_level, {}).get('description', 'bilinmiyor')
                    
                    log_event(username, f"📤 [{dialog.name}] spam gönderildi (aktivite: {activity_level}, interval: {interval_info})")
                    
                    # Mesajlar arası bekleme (rate limiting)
                    await asyncio.sleep(random.uniform(2, 5))
                    
                except ChatWriteForbiddenError:
                    dynamic_scheduler.banned_groups.add(dialog.id)
                    log_event(username, f"🚫 [{dialog.name}] yazma engeli - banlandı")
                    
                except Exception as e:
                    log_event(username, f"❌ [{dialog.name}] spam hatası: {e}")
            
            # Tur özeti
            log_event(username, f"✅ Spam turu #{spam_round} tamamlandı: {sent_count} başarılı, {skipped_count} atlandı, {total_groups} toplam grup")
            
            # İstatistik özeti
            stats = dynamic_scheduler.get_group_stats_summary()
            log_event(username, f"📊 Grup istatistikleri: {stats['activity_levels']}")
            
        except Exception as e:
            log_event(username, f"❌ Dinamik spam turu hatası: {e}")
        
        # Sonraki tur için bekleme (minimum 5 dakika)
        next_round_wait = random.uniform(300, 420)  # 5-7 dakika
        log_event(username, f"⏰ Sonraki dinamik spam turu: {next_round_wait/60:.1f} dakika sonra")
        await asyncio.sleep(next_round_wait)

async def start_dynamic_spam_system(client, username: str, profile: dict):
    """Dinamik spam sistemini başlatır"""
    if not profile.get("autospam"):
        log_event(username, "ℹ️ Otomatik spam aktif değil - dinamik sistem başlatılmadı")
        return
    
    log_event(username, "🎯 Dinamik spam sistemi başlatılıyor...")
    
    # Background task olarak başlat
    asyncio.create_task(dynamic_spam_loop(client, username, profile))
    
    log_event(username, "✅ Dinamik spam sistemi aktif - grup trafiğine göre optimize edilmiş spam")

def get_dynamic_stats() -> dict:
    """Dinamik spam istatistiklerini döner"""
    return dynamic_scheduler.get_group_stats_summary()

def reset_dynamic_stats():
    """Dinamik spam istatistiklerini sıfırlar"""
    dynamic_scheduler.group_stats.clear()
    dynamic_scheduler.banned_groups.clear()
    dynamic_scheduler.last_analysis = 0 