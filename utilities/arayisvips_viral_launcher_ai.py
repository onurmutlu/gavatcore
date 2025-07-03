#!/usr/bin/env python3
"""
🤖 AI-POWERED VIRAL LAUNCHER
============================
GPT-4o optimize edilmiş mesajlar ile viral büyüme
ONUR METODU - AI Edition
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError
from ai_message_optimizer import AIMessageOptimizer
import sqlite3

class AIViralLauncher:
    def __init__(self):
        self.ai_optimizer = AIMessageOptimizer()
        self.target_group = "@arayisonlyvips"
        
        # Bot bilgileri
        self.bots = [
            {"name": "YayınCı-Lara", "session": "_905382617727", "character": "Samimi ve arkadaş canlısı"},
            {"name": "Geisha", "session": "_905486306226", "character": "Çekici ve gizemli"},
            {"name": "BabaGAVAT", "session": "_905513272355", "character": "Güçlü ve otoriter"}
        ]
        
        # AI-powered mesaj kategorileri
        self.message_categories = ["davet", "topluluk", "samimi", "merak", "kisa", "emoji", "soru"]
        
        # Rate limiting
        self.bot_limits = {}
        self.group_limits = {}
        self.dm_limits = {}
        
        # Performance tracking
        self.performance_data = {
            'total_invites_sent': 0,
            'successful_joins': 0,
            'spam_messages_sent': 0,
            'dm_conversations': 0,
            'conversion_rate': 0.0,
            'daily_growth': [],
            'bot_performance': {}
        }
        
    async def get_optimized_message(self, category: str, bot_name: str) -> str:
        """AI optimize edilmiş mesaj al"""
        
        # En optimal mesajı seç
        optimal_message = self.ai_optimizer.get_optimal_message(category)
        
        if optimal_message:
            # Mesaj kullanımını kaydet
            self.ai_optimizer.record_message_sent(
                optimal_message.message_id, 
                optimal_message.content, 
                category
            )
            return optimal_message.content
        else:
            # Yeni mesaj üret
            new_messages = await self.ai_optimizer.generate_optimized_messages(category, 1)
            if new_messages:
                message = new_messages[0]
                # Yeni mesajı kaydet
                msg_id = f"ai_{category}_{bot_name}_{int(time.time())}"
                self.ai_optimizer.record_message_sent(msg_id, message, category)
                return message
            else:
                # Fallback mesaj
                return f"Merhaba! {self.target_group} grubuna katılmak ister misin? 🙂"
    
    def record_message_engagement(self, message_content: str, engagement_type: str):
        """Mesaj engagement'ını kaydet"""
        
        # Mesaj ID'sini bul
        conn = self.ai_optimizer._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_id FROM message_performance 
            WHERE content = ? 
            ORDER BY last_used DESC 
            LIMIT 1
        ''', (message_content,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            self.ai_optimizer.record_engagement(result[0], engagement_type)
    
    async def smart_spam_campaign(self, client, bot_name: str, groups: list):
        """AI-powered akıllı spam kampanyası"""
        
        sent_count = 0
        success_count = 0
        
        for group in groups:
            try:
                group_name = group.title
                
                # Rate limiting kontrolü
                if self.is_rate_limited(bot_name, group_name):
                    continue
                
                # AI'dan kategori seç (bot karakterine göre)
                if "Lara" in bot_name:
                    category = random.choice(["samimi", "topluluk", "davet"])
                elif "Geisha" in bot_name:
                    category = random.choice(["merak", "emoji", "kisa"])
                else:  # BabaGAVAT
                    category = random.choice(["davet", "soru", "topluluk"])
                
                # AI optimize edilmiş mesaj al
                message = await self.get_optimized_message(category, bot_name)
                
                # Mesajı gönder
                await client.send_message(group, message)
                
                print(f"  📤 {group_name}: {message[:50]}...")
                
                # Başarı kaydı
                sent_count += 1
                success_count += 1
                
                # Rate limit güncelle
                self.update_rate_limits(bot_name, group_name)
                
                # Güvenlik arası
                await asyncio.sleep(random.uniform(30, 90))
                
            except FloodWaitError as e:
                print(f"  ❌ {group.title}: A wait of {e.seconds} seconds is required")
                await asyncio.sleep(e.seconds)
                
            except (UserBannedInChannelError, ChatWriteForbiddenError):
                print(f"  🚫 {group.title}: Bot banlanmış")
                
            except Exception as e:
                print(f"  ❌ {group.title}: {e}")
        
        return sent_count, success_count
    
    async def ai_dm_campaign(self, client, bot_name: str):
        """AI-powered DM kampanyası"""
        
        try:
            # DM günlük limit kontrolü
            now = datetime.now()
            dm_daily_key = f"{bot_name}_dm_daily"
            
            if dm_daily_key not in self.dm_limits:
                self.dm_limits[dm_daily_key] = []
            
            # Son 24 saatteki DM'leri filtrele
            self.dm_limits[dm_daily_key] = [
                timestamp for timestamp in self.dm_limits[dm_daily_key]
                if now - timestamp < timedelta(days=1)
            ]
            
            # Günlük DM limiti kontrolü (20 DM/gün)
            if len(self.dm_limits[dm_daily_key]) >= 20:
                print(f"  ⏭️ {bot_name}: Günlük DM limiti aşıldı (20/20)")
                return 0
            
            # Hedef grubun üyelerini al
            target_entity = await client.get_entity(self.target_group)
            participants = await client.get_participants(target_entity, limit=100)
            
            dm_sent = 0
            max_dm_per_session = min(5, 20 - len(self.dm_limits[dm_daily_key]))  # Kalan limit
            
            for user in participants:
                if dm_sent >= max_dm_per_session:  # Session DM limiti
                    break
                    
                if user.bot or user.deleted:
                    continue
                
                try:
                    # AI optimize edilmiş DM mesajı
                    dm_message = await self.get_optimized_message("samimi", bot_name)
                    
                    await client.send_message(user, dm_message)
                    
                    print(f"  📩 DM gönderildi: {user.first_name}")
                    
                    # Engagement kaydı
                    self.record_message_engagement(dm_message, "dm")
                    
                    # DM limit güncelle
                    self.dm_limits[dm_daily_key].append(now)
                    
                    dm_sent += 1
                    
                    # DM arası bekleme
                    await asyncio.sleep(random.uniform(60, 120))
                    
                except Exception as e:
                    print(f"  ❌ DM hatası {user.first_name}: {e}")
                    continue
            
            return dm_sent
            
        except Exception as e:
            print(f"❌ {bot_name} DM kampanya genel hata: {e}")
            return 0
    
    def is_rate_limited(self, bot_name: str, group_name: str) -> bool:
        """Rate limiting kontrolü"""
        
        now = datetime.now()
        
        # Bot saatlik limit (10 mesaj/saat)
        bot_key = f"{bot_name}_hourly"
        if bot_key not in self.bot_limits:
            self.bot_limits[bot_key] = []
        
        # Son 1 saatteki mesajları filtrele
        self.bot_limits[bot_key] = [
            timestamp for timestamp in self.bot_limits[bot_key]
            if now - timestamp < timedelta(hours=1)
        ]
        
        if len(self.bot_limits[bot_key]) >= 10:
            print(f"  ⏭️ {group_name}: Bot saatlik limit aşıldı (10/10)")
            return True
        
        # Grup günlük limit (3 mesaj/grup/gün)
        group_key = f"{bot_name}_{group_name}_daily"
        if group_key not in self.group_limits:
            self.group_limits[group_key] = []
        
        # Son 24 saatteki mesajları filtrele
        self.group_limits[group_key] = [
            timestamp for timestamp in self.group_limits[group_key]
            if now - timestamp < timedelta(days=1)
        ]
        
        if len(self.group_limits[group_key]) >= 3:
            print(f"  ⏭️ {group_name}: Grup günlük limit aşıldı (3/3)")
            return True
        
        # Grup minimum ara (30 dakika)
        if self.group_limits[group_key]:
            last_message = max(self.group_limits[group_key])
            if now - last_message < timedelta(minutes=30):
                remaining = timedelta(minutes=30) - (now - last_message)
                remaining_minutes = int(remaining.total_seconds() / 60)
                print(f"  ⏭️ {group_name}: Grup için {remaining_minutes} dakika daha bekle")
                return True
        
        return False
    
    def update_rate_limits(self, bot_name: str, group_name: str):
        """Rate limit güncelle"""
        
        now = datetime.now()
        
        # Bot saatlik limit güncelle
        bot_key = f"{bot_name}_hourly"
        if bot_key not in self.bot_limits:
            self.bot_limits[bot_key] = []
        self.bot_limits[bot_key].append(now)
        
        # Grup günlük limit güncelle
        group_key = f"{bot_name}_{group_name}_daily"
        if group_key not in self.group_limits:
            self.group_limits[group_key] = []
        self.group_limits[group_key].append(now)
    
    async def run_ai_viral_campaign(self):
        """AI-powered viral kampanya çalıştır"""
        
        print("🤖 AI-POWERED VIRAL KAMPANYA BAŞLIYOR!")
        print("=" * 60)
        print("🧠 GPT-4o optimize edilmiş mesajlar")
        print("📊 Real-time performance tracking")
        print("🎯 Smart rate limiting")
        print("=" * 60)
        
        # AI optimizer'ı hazırla
        print("\n🧠 AI Message Optimizer hazırlanıyor...")
        optimal_messages = await self.ai_optimizer.optimize_message_rotation()
        print(f"✅ {len(optimal_messages)} kategori için optimize edilmiş mesajlar hazır")
        
        # Bot kampanyalarını başlat
        tasks = []
        
        for bot_info in self.bots:
            task = asyncio.create_task(self.run_bot_campaign(bot_info))
            tasks.append(task)
        
        # Tüm botları paralel çalıştır
        await asyncio.gather(*tasks)
        
        # Final rapor
        print("\n" + "=" * 60)
        print("🎯 AI-POWERED VIRAL KAMPANYA TAMAMLANDI!")
        print("=" * 60)
        
        # AI performance raporu
        ai_report = self.ai_optimizer.generate_performance_report()
        print(ai_report)
        
        # Viral rapor kaydet
        self.save_viral_report()
    
    async def run_bot_campaign(self, bot_info: dict):
        """Tek bot kampanyası"""
        
        bot_name = bot_info["name"]
        session_file = f"sessions/{bot_info['session']}.session"
        
        print(f"\n🤖 {bot_name} AI kampanyası başlatılıyor...")
        
        try:
            # Telegram client oluştur
            client = TelegramClient(session_file, api_id=29943673, api_hash="c5d8076c4d6d9d6e8b8b8b8b8b8b8b8b")
            await client.start()
            
            # Bot bilgilerini al
            me = await client.get_me()
            print(f"✅ {me.first_name} ({me.username}) AI modu aktif")
            
            # Grupları al
            dialogs = await client.get_dialogs()
            groups = [d.entity for d in dialogs if hasattr(d.entity, 'megagroup') and d.entity.megagroup]
            
            print(f"  📊 {me.first_name} toplam grup: {len(groups)}")
            
            # AI spam kampanyası
            sent, success = await self.smart_spam_campaign(client, bot_name, groups)
            
            # AI DM kampanyası
            dm_sent = await self.ai_dm_campaign(client, bot_name)
            
            # Performance kaydı
            self.performance_data['bot_performance'][me.first_name] = {
                'spam_sent': sent,
                'invites_sent': dm_sent,
                'dm_conversations': 0,
                'start_time': time.time()
            }
            
            print(f"✅ {me.first_name} AI kampanya turu: {sent} spam, {dm_sent} DM")
            
            await client.disconnect()
            
        except Exception as e:
            print(f"❌ {bot_name} AI kampanya hatası: {e}")
    
    def save_viral_report(self):
        """Viral rapor kaydet"""
        
        # Toplam istatistikleri hesapla
        total_spam = sum(bot['spam_sent'] for bot in self.performance_data['bot_performance'].values())
        total_dm = sum(bot['invites_sent'] for bot in self.performance_data['bot_performance'].values())
        
        self.performance_data.update({
            'spam_messages_sent': total_spam,
            'total_invites_sent': total_dm,
            'conversion_rate': 0.0,  # Henüz join tracking yok
            'daily_growth': [{
                'day': 1,
                'invites_sent': total_dm,
                'spam_messages': total_spam,
                'timestamp': datetime.now().isoformat()
            }]
        })
        
        # Raporu kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_viral_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.performance_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 AI Viral rapor kaydedildi: {filename}")

async def main():
    """AI Viral Launcher ana fonksiyon"""
    
    launcher = AIViralLauncher()
    await launcher.run_ai_viral_campaign()

if __name__ == "__main__":
    asyncio.run(main()) 