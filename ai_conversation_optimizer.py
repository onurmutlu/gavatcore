#!/usr/bin/env python3
"""
🤖 AI CONVERSATION STARTER OPTIMIZER
===================================
Doğal sohbet açıcı mesajlar ile viral büyüme
ONUR METODU - Conversation Edition
"""

import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class AIConversationOptimizer:
    def __init__(self):
        self.db_path = "conversation_optimizer.db"
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_data = self.load_conversation_starters()
        self.init_database()
        
    def load_conversation_starters(self) -> dict:
        """Conversation starter verilerini yükle"""
        try:
            with open('data/conversation_starters.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ conversation_starters.json bulunamadı!")
            return {}
    
    def init_database(self):
        """Conversation tracking database'i başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation performance tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                content TEXT,
                category TEXT,
                persona TEXT,
                group_name TEXT,
                sent_time TIMESTAMP,
                reply_count INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0.0,
                dm_conversions INTEGER DEFAULT 0,
                ban_risk_score REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Group context tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                last_conversation_time TIMESTAMP,
                conversation_count INTEGER DEFAULT 0,
                engagement_level TEXT DEFAULT 'medium',
                preferred_categories TEXT,
                ban_risk_level TEXT DEFAULT 'low'
            )
        ''')
        
        # AI generated messages tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_generated_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                persona TEXT,
                content TEXT,
                generation_time TIMESTAMP,
                performance_score REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_optimal_conversation_starter(self, category: str, persona: str, group_name: str = None) -> Optional[Dict]:
        """En optimal conversation starter mesajını al"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # En iyi performans gösteren mesajları al
        cursor.execute('''
            SELECT message_id, content, engagement_score, ban_risk_score
            FROM conversation_performance 
            WHERE category = ? AND persona = ?
            AND ban_risk_score < 0.3
            ORDER BY engagement_score DESC, usage_count ASC
            LIMIT 5
        ''', (category, persona))
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            # En iyi mesajı seç (düşük kullanım + yüksek engagement)
            best_message = results[0]
            return {
                'message_id': best_message[0],
                'content': best_message[1],
                'engagement_score': best_message[2],
                'ban_risk_score': best_message[3]
            }
        
        # Eğer DB'de yoksa, JSON'dan al
        return self.get_conversation_from_json(category, persona)
    
    def get_conversation_from_json(self, category: str, persona: str) -> Optional[Dict]:
        """JSON'dan conversation starter al"""
        
        if category not in self.conversation_data.get('conversation_starters', {}):
            return None
        
        messages = self.conversation_data['conversation_starters'][category]
        if not messages:
            return None
        
        # Rastgele mesaj seç
        message = random.choice(messages)
        message_id = f"json_{category}_{persona}_{int(time.time())}"
        
        return {
            'message_id': message_id,
            'content': message,
            'engagement_score': 0.0,
            'ban_risk_score': 0.1  # JSON mesajları düşük risk
        }
    
    def generate_ai_conversation_starter(self, category: str, persona: str, context: str = "") -> str:
        """GPT-4o ile conversation starter üret"""
        
        persona_prompts = {
            "yayincilara": "Samimi, arkadaş canlısı, pozitif enerji yayan",
            "xxxgeisha": "Çekici, gizemli, zarif ve ilgi çekici",
            "babagavat": "Güçlü, otoriter, lider karakterli"
        }
        
        category_prompts = {
            "samimi_sohbet": "samimi ve doğal sohbet açıcı",
            "merak_uyandiran": "merak uyandıran ve ilgi çekici",
            "grup_aktivitesi": "grup aktivitesi ve katılım odaklı",
            "pozitif_enerji": "pozitif enerji ve motivasyon verici",
            "arayisvips_soft_mention": "@arayisonlyvips grubunu doğal şekilde bahseden"
        }
        
        prompt = f"""
Sen {persona_prompts.get(persona, 'samimi')} bir Telegram kullanıcısısın.
Telegram gruplarında {category_prompts.get(category, 'doğal sohbet açıcı')} mesaj yazacaksın.

KURALLAR:
1. Doğal ve samimi ol
2. Spam gibi görünme
3. Grup üyelerini sohbete dahil et
4. Ban riski yaratma
5. Maksimum 100 karakter
6. Uygun emoji kullan (fazla değil)
7. Soru sorarak engagement artır

{context}

Tek bir mesaj yaz:
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            
            message = response.choices[0].message.content.strip()
            
            # AI mesajını kaydet
            self.save_ai_generated_message(category, persona, message)
            
            return message
            
        except Exception as e:
            print(f"❌ AI mesaj üretim hatası: {e}")
            # Fallback olarak JSON'dan al
            fallback = self.get_conversation_from_json(category, persona)
            return fallback['content'] if fallback else "Merhaba! Nasılsınız? 😊"
    
    def save_ai_generated_message(self, category: str, persona: str, content: str):
        """AI üretilen mesajı kaydet"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_generated_messages 
            (category, persona, content, generation_time)
            VALUES (?, ?, ?, ?)
        ''', (category, persona, content, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def record_conversation_sent(self, message_id: str, content: str, category: str, 
                               persona: str, group_name: str):
        """Gönderilen conversation'ı kaydet"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO conversation_performance 
            (message_id, content, category, persona, group_name, sent_time, last_used, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT usage_count FROM conversation_performance WHERE message_id = ?), 0) + 1)
        ''', (message_id, content, category, persona, group_name, 
              datetime.now(), datetime.now(), message_id))
        
        conn.commit()
        conn.close()
    
    def record_conversation_engagement(self, message_id: str, engagement_type: str, value: int = 1):
        """Conversation engagement'ını kaydet"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if engagement_type == "reply":
            cursor.execute('''
                UPDATE conversation_performance 
                SET reply_count = reply_count + ?, 
                    engagement_score = engagement_score + ?
                WHERE message_id = ?
            ''', (value, value * 0.5, message_id))
            
        elif engagement_type == "dm":
            cursor.execute('''
                UPDATE conversation_performance 
                SET dm_conversions = dm_conversions + ?, 
                    engagement_score = engagement_score + ?
                WHERE message_id = ?
            ''', (value, value * 2.0, message_id))
            
        elif engagement_type == "ban_risk":
            cursor.execute('''
                UPDATE conversation_performance 
                SET ban_risk_score = ban_risk_score + ?
                WHERE message_id = ?
            ''', (value * 0.1, message_id))
        
        conn.commit()
        conn.close()
    
    def update_group_context(self, group_name: str, engagement_level: str = "medium"):
        """Grup context'ini güncelle"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO group_context 
            (group_name, last_conversation_time, conversation_count, engagement_level)
            VALUES (?, ?, 
                    COALESCE((SELECT conversation_count FROM group_context WHERE group_name = ?), 0) + 1,
                    ?)
        ''', (group_name, datetime.now(), group_name, engagement_level))
        
        conn.commit()
        conn.close()
    
    def get_best_category_for_persona(self, persona: str) -> str:
        """Persona için en iyi kategoriyi al"""
        
        persona_mapping = self.conversation_data.get('persona_mapping', {})
        
        if persona in persona_mapping:
            primary_categories = persona_mapping[persona]['primary_categories']
            return random.choice(primary_categories)
        
        # Default kategoriler
        return random.choice(['samimi_sohbet', 'pozitif_enerji'])
    
    def should_mention_arayisvips(self, persona: str, last_mention_time: datetime = None) -> bool:
        """@arayisonlyvips mention edilmeli mi?"""
        
        # 2 saatte bir mention
        if last_mention_time and datetime.now() - last_mention_time < timedelta(hours=2):
            return False
        
        # %30 şans ile mention
        return random.random() < 0.3
    
    def generate_performance_report(self) -> str:
        """Conversation performance raporu üret"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Toplam istatistikler
        cursor.execute('''
            SELECT 
                COUNT(*) as total_conversations,
                AVG(engagement_score) as avg_engagement,
                AVG(ban_risk_score) as avg_ban_risk,
                SUM(reply_count) as total_replies,
                SUM(dm_conversions) as total_dm_conversions
            FROM conversation_performance
        ''')
        
        stats = cursor.fetchone()
        
        # Kategori performansları
        cursor.execute('''
            SELECT 
                category,
                COUNT(*) as count,
                AVG(engagement_score) as avg_engagement,
                AVG(ban_risk_score) as avg_ban_risk
            FROM conversation_performance
            GROUP BY category
            ORDER BY avg_engagement DESC
        ''')
        
        category_stats = cursor.fetchall()
        
        conn.close()
        
        # Safe formatting
        total_conversations = stats[0] if stats[0] else 0
        avg_engagement = stats[1] if stats[1] else 0.0
        avg_ban_risk = stats[2] if stats[2] else 0.0
        total_replies = stats[3] if stats[3] else 0
        total_dm_conversions = stats[4] if stats[4] else 0
        
        report = f"""
🤖 AI CONVERSATION STARTER PERFORMANCE RAPORU
============================================

📊 GENEL İSTATİSTİKLER:
• Toplam Conversation: {total_conversations}
• Ortalama Engagement: {avg_engagement:.2f}
• Ortalama Ban Risk: {avg_ban_risk:.2f}
• Toplam Reply: {total_replies}
• Toplam DM Conversion: {total_dm_conversions}

📈 KATEGORİ PERFORMANSLARI:
"""
        
        for cat_stat in category_stats:
            cat_engagement = cat_stat[2] if cat_stat[2] else 0.0
            cat_ban_risk = cat_stat[3] if cat_stat[3] else 0.0
            report += f"• {cat_stat[0]}: {cat_stat[1]} mesaj, {cat_engagement:.2f} engagement, {cat_ban_risk:.2f} ban risk\n"
        
        return report
    
    def optimize_conversation_rotation(self) -> Dict[str, List[str]]:
        """Conversation rotation'ını optimize et"""
        
        optimized_messages = {}
        
        categories = self.conversation_data.get('ai_optimization_config', {}).get('categories', [])
        personas = ['yayincilara', 'xxxgeisha', 'babagavat']
        
        for category in categories:
            for persona in personas:
                # Her kategori-persona kombinasyonu için 3 optimize edilmiş mesaj üret
                messages = []
                for i in range(3):
                    try:
                        ai_message = self.generate_ai_conversation_starter(category, persona)
                        messages.append(ai_message)
                    except Exception as e:
                        print(f"❌ {category}-{persona} AI mesaj hatası: {e}")
                        # Fallback
                        fallback = self.get_conversation_from_json(category, persona)
                        if fallback:
                            messages.append(fallback['content'])
                
                key = f"{category}_{persona}"
                optimized_messages[key] = messages
        
        print(f"✅ {len(optimized_messages)} kategori-persona kombinasyonu optimize edildi")
        return optimized_messages

# Test fonksiyonu
def test_conversation_optimizer():
    """Conversation optimizer test"""
    
    optimizer = AIConversationOptimizer()
    
    print("🤖 AI Conversation Optimizer Test Başlıyor...")
    
    # Optimal mesaj al
    message = optimizer.get_optimal_conversation_starter("samimi_sohbet", "yayincilara", "test_group")
    print(f"📝 Optimal mesaj: {message}")
    
    # AI mesaj üret
    ai_message = optimizer.generate_ai_conversation_starter("merak_uyandiran", "xxxgeisha")
    print(f"🤖 AI mesaj: {ai_message}")
    
    # Performance raporu
    report = optimizer.generate_performance_report()
    print(report)

if __name__ == "__main__":
    test_conversation_optimizer() 