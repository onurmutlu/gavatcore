#!/usr/bin/env python3
"""
🤖 AI-POWERED CONVERSATION LAUNCHER
==================================
Doğal sohbet açıcı mesajlar ile viral büyüme
ONUR METODU - Natural Conversation Edition
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError
from ai_conversation_optimizer import AIConversationOptimizer
import sqlite3

class AIConversationLauncher:
    def __init__(self):
        self.ai_optimizer = AIConversationOptimizer()
        self.target_group = "@arayisonlyvips"
        
        # Bot bilgileri
        self.bots = [
            {"name": "YayınCı-Lara", "session": "_905382617727", "persona": "yayincilara"},
            {"name": "Geisha", "session": "_905486306226", "persona": "xxxgeisha"},
            {"name": "BabaGAVAT", "session": "_905513272355", "persona": "babagavat"}
        ]
        
        # Rate limiting
        self.bot_limits = {}
        self.group_limits = {}
        self.last_arayisvips_mention = {}
        
        # Performance tracking
        self.performance_data = {
            'total_conversations': 0,
            'successful_replies': 0,
            'dm_conversations': 0,
            'group_engagements': 0,
            'ban_incidents': 0,
            'daily_growth': [],
            'bot_performance': {}
        }
        
    async def get_conversation_starter(self, persona: str, group_name: str) -> dict:
        """AI optimize edilmiş conversation starter al"""
        
        # Persona için en iyi kategoriyi seç
        category = self.ai_optimizer.get_best_category_for_persona(persona)
        
        # @arayisonlyvips mention kontrolü
        should_mention = self.ai_optimizer.should_mention_arayisvips(
            persona, 
            self.last_arayisvips_mention.get(persona)
        )
        
        if should_mention:
            category = "arayisvips_soft_mention"
            self.last_arayisvips_mention[persona] = datetime.now()
        
        # En optimal mesajı al
        message_data = self.ai_optimizer.get_optimal_conversation_starter(category, persona, group_name)
        
        if not message_data:
            # AI ile yeni mesaj üret
            try:
                ai_message = self.ai_optimizer.generate_ai_conversation_starter(category, persona)
                message_data = {
                    'message_id': f"ai_{category}_{persona}_{int(time.time())}",
                    'content': ai_message,
                    'engagement_score': 0.0,
                    'ban_risk_score': 0.1
                }
            except Exception as e:
                print(f"❌ AI mesaj üretim hatası: {e}")
                # Fallback
                message_data = {
                    'message_id': f"fallback_{int(time.time())}",
                    'content': "Merhaba! Bu grupta nasıl sohbetler dönüyor? 😊",
                    'engagement_score': 0.0,
                    'ban_risk_score': 0.1
                }
        
        return {
            'message_id': message_data['message_id'],
            'content': message_data['content'],
            'category': category,
            'engagement_score': message_data['engagement_score'],
            'ban_risk_score': message_data['ban_risk_score']
        }
    
    async def natural_conversation_campaign(self, client, bot_name: str, persona: str, groups: list):
        """Doğal conversation kampanyası"""
        
        sent_count = 0
        success_count = 0
        
        for group in groups:
            try:
                group_name = group.title
                
                # Rate limiting kontrolü
                if self.is_rate_limited(bot_name, group_name):
                    continue
                
                # Conversation starter al
                conversation = await self.get_conversation_starter(persona, group_name)
                
                # Mesajı gönder
                await client.send_message(group, conversation['content'])
                
                print(f"  💬 {group_name}: {conversation['content'][:60]}...")
                
                # Conversation kaydı
                self.ai_optimizer.record_conversation_sent(
                    conversation['message_id'],
                    conversation['content'],
                    conversation['category'],
                    persona,
                    group_name
                )
                
                # Grup context güncelle
                self.ai_optimizer.update_group_context(group_name, "medium")
                
                # Başarı kaydı
                sent_count += 1
                success_count += 1
                
                # Rate limit güncelle
                self.update_rate_limits(bot_name, group_name)
                
                # Doğal bekleme (conversation arası)
                await asyncio.sleep(random.uniform(45, 120))
                
            except FloodWaitError as e:
                print(f"  ❌ {group.title}: {e.seconds} saniye bekleme gerekli")
                await asyncio.sleep(e.seconds)
                
            except (UserBannedInChannelError, ChatWriteForbiddenError):
                print(f"  🚫 {group.title}: Bot banlanmış")
                # Ban riski kaydı
                self.performance_data['ban_incidents'] += 1
                
            except Exception as e:
                print(f"  ❌ {group.title}: {e}")
        
        return sent_count, success_count
    
    async def smart_dm_conversation(self, client, bot_name: str, persona: str):
        """Akıllı DM conversation sistemi"""
        
        try:
            # Hedef grubun üyelerini al
            target_entity = await client.get_entity(self.target_group)
            participants = await client.get_participants(target_entity, limit=50)
            
            dm_sent = 0
            max_dm_per_session = 3  # Conversation odaklı, az ama etkili
            
            for user in participants:
                if dm_sent >= max_dm_per_session:
                    break
                    
                if user.bot or user.deleted:
                    continue
                
                try:
                    # Samimi conversation starter
                    conversation = await self.get_conversation_starter(persona, "dm")
                    
                    await client.send_message(user, conversation['content'])
                    
                    print(f"  💌 DM conversation: {user.first_name}")
                    
                    # DM engagement kaydı
                    self.ai_optimizer.record_conversation_engagement(
                        conversation['message_id'], 
                        "dm"
                    )
                    
                    dm_sent += 1
                    
                    # DM arası uzun bekleme (doğal görünmek için)
                    await asyncio.sleep(random.uniform(180, 300))
                    
                except Exception as e:
                    print(f"  ❌ DM conversation hatası {user.first_name}: {e}")
                    continue
            
            return dm_sent
            
        except Exception as e:
            print(f"❌ {bot_name} DM conversation genel hata: {e}")
            return 0
    
    def is_rate_limited(self, bot_name: str, group_name: str) -> bool:
        """Conversation rate limiting kontrolü"""
        
        now = datetime.now()
        
        # Bot saatlik limit (5 conversation/saat - daha az ama kaliteli)
        bot_key = f"{bot_name}_hourly"
        if bot_key not in self.bot_limits:
            self.bot_limits[bot_key] = []
        
        # Son 1 saatteki conversation'ları filtrele
        self.bot_limits[bot_key] = [
            timestamp for timestamp in self.bot_limits[bot_key]
            if now - timestamp < timedelta(hours=1)
        ]
        
        if len(self.bot_limits[bot_key]) >= 5:
            print(f"  ⏭️ {group_name}: Bot saatlik conversation limiti aşıldı (5/5)")
            return True
        
        # Grup günlük limit (2 conversation/grup/gün - doğal görünmek için)
        group_key = f"{bot_name}_{group_name}_daily"
        if group_key not in self.group_limits:
            self.group_limits[group_key] = []
        
        # Son 24 saatteki conversation'ları filtrele
        self.group_limits[group_key] = [
            timestamp for timestamp in self.group_limits[group_key]
            if now - timestamp < timedelta(days=1)
        ]
        
        if len(self.group_limits[group_key]) >= 2:
            print(f"  ⏭️ {group_name}: Grup günlük conversation limiti aşıldı (2/2)")
            return True
        
        # Grup minimum ara (1 saat - doğal conversation için)
        if self.group_limits[group_key]:
            last_conversation = max(self.group_limits[group_key])
            if now - last_conversation < timedelta(hours=1):
                remaining = timedelta(hours=1) - (now - last_conversation)
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
    
    async def run_conversation_campaign(self):
        """AI-powered conversation kampanya çalıştır"""
        
        print("🤖 AI-POWERED CONVERSATION KAMPANYA BAŞLIYOR!")
        print("=" * 60)
        print("💬 Doğal sohbet açıcı mesajlar")
        print("🧠 GPT-4o optimize edilmiş conversation")
        print("🎯 Ban-proof natural engagement")
        print("📊 Real-time conversation tracking")
        print("=" * 60)
        
        # AI optimizer'ı hazırla
        print("\n🧠 AI Conversation Optimizer hazırlanıyor...")
        optimal_conversations = self.ai_optimizer.optimize_conversation_rotation()
        print(f"✅ {len(optimal_conversations)} conversation kombinasyonu optimize edildi")
        
        # Bot kampanyalarını başlat
        tasks = []
        
        for bot_info in self.bots:
            task = asyncio.create_task(self.run_bot_conversation_campaign(bot_info))
            tasks.append(task)
        
        # Tüm botları paralel çalıştır
        await asyncio.gather(*tasks)
        
        # Final rapor
        print("\n" + "=" * 60)
        print("🎯 AI-POWERED CONVERSATION KAMPANYA TAMAMLANDI!")
        print("=" * 60)
        
        # AI conversation raporu
        ai_report = self.ai_optimizer.generate_performance_report()
        print(ai_report)
        
        # Conversation rapor kaydet
        self.save_conversation_report()
    
    async def run_bot_conversation_campaign(self, bot_info: dict):
        """Tek bot conversation kampanyası"""
        
        bot_name = bot_info["name"]
        persona = bot_info["persona"]
        session_file = f"sessions/{bot_info['session']}.session"
        
        print(f"\n🤖 {bot_name} conversation kampanyası başlatılıyor...")
        
        try:
            # Telegram client oluştur
            client = TelegramClient(session_file, api_id=29943673, api_hash="c5d8076c4d6d9d6e8b8b8b8b8b8b8b8b")
            await client.start()
            
            # Bot bilgilerini al
            me = await client.get_me()
            print(f"✅ {me.first_name} ({me.username}) conversation modu aktif")
            
            # Grupları al
            dialogs = await client.get_dialogs()
            groups = [d.entity for d in dialogs if hasattr(d.entity, 'megagroup') and d.entity.megagroup]
            
            print(f"  📊 {me.first_name} toplam grup: {len(groups)}")
            
            # Natural conversation kampanyası
            sent, success = await self.natural_conversation_campaign(client, bot_name, persona, groups)
            
            # Smart DM conversation
            dm_sent = await self.smart_dm_conversation(client, bot_name, persona)
            
            # Performance kaydı
            self.performance_data['bot_performance'][me.first_name] = {
                'conversations_sent': sent,
                'dm_conversations': dm_sent,
                'engagement_score': 0,  # Henüz reply tracking yok
                'start_time': time.time()
            }
            
            print(f"✅ {me.first_name} conversation turu: {sent} grup conversation, {dm_sent} DM")
            
            await client.disconnect()
            
        except Exception as e:
            print(f"❌ {bot_name} conversation kampanya hatası: {e}")
    
    def save_conversation_report(self):
        """Conversation rapor kaydet"""
        
        # Toplam istatistikleri hesapla
        total_conversations = sum(bot['conversations_sent'] for bot in self.performance_data['bot_performance'].values())
        total_dm = sum(bot['dm_conversations'] for bot in self.performance_data['bot_performance'].values())
        
        self.performance_data.update({
            'total_conversations': total_conversations,
            'dm_conversations': total_dm,
            'group_engagements': 0,  # Henüz reply tracking yok
            'daily_growth': [{
                'day': 1,
                'conversations_sent': total_conversations,
                'dm_conversations': total_dm,
                'timestamp': datetime.now().isoformat()
            }]
        })
        
        # Raporu kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.performance_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Conversation rapor kaydedildi: {filename}")

async def main():
    """AI Conversation Launcher ana fonksiyon"""
    
    launcher = AIConversationLauncher()
    await launcher.run_conversation_campaign()

if __name__ == "__main__":
    asyncio.run(main()) 