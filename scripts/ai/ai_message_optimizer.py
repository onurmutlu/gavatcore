#!/usr/bin/env python3
"""
🤖 AI-POWERED MESSAGE OPTIMIZER
===============================
GPT-4o ile viral mesaj optimizasyonu, CTR tracking, A/B testing
ONUR METODU - Telegram Growth Bible Edition
"""

import json
import time
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import openai
from dataclasses import dataclass
import statistics
import random

@dataclass
class MessagePerformance:
    message_id: str
    content: str
    category: str
    sent_count: int
    reply_count: int
    dm_count: int
    join_count: int
    ctr: float
    engagement_score: float
    last_used: datetime
    
class AIMessageOptimizer:
    def __init__(self):
        self.db_path = "ai_optimizer.db"
        self.openai_client = openai.OpenAI()
        self.init_database()
        
        # Viral mesaj kategorileri
        self.message_categories = {
            "davet": "Doğrudan davet odaklı",
            "topluluk": "Topluluk vurgusu",
            "samimi": "Samimi ve arkadaşça",
            "merak": "Merak uyandıran",
            "kisa": "Kısa ve etkili",
            "emoji": "Emoji ağırlıklı",
            "soru": "Soru tarzı"
        }
        
    def init_database(self):
        """AI optimizer veritabanını başlat"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=10000')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_performance (
                message_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                sent_count INTEGER DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                dm_count INTEGER DEFAULT 0,
                join_count INTEGER DEFAULT 0,
                ctr REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                test_id TEXT PRIMARY KEY,
                message_a_id TEXT,
                message_b_id TEXT,
                category TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                winner TEXT,
                confidence REAL,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _get_connection(self):
        """Güvenli database connection"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn
        
    async def generate_optimized_messages(self, category: str, count: int = 5) -> List[str]:
        """GPT-4o ile optimize edilmiş mesajlar üret"""
        
        # Mevcut performans verilerini al
        top_performers = self.get_top_performing_messages(category, limit=3)
        
        prompt = f"""
        Sen bir viral büyüme uzmanısın. @arayisonlyvips Telegram grubu için {category} kategorisinde 
        yüksek CTR'li viral mesajlar üret.
        
        Kategori: {self.message_categories.get(category, category)}
        
        En iyi performans gösteren mesajlar:
        {chr(10).join([f"- {msg.content} (CTR: {msg.ctr:.2%})" for msg in top_performers])}
        
        Kurallar:
        1. Spam filtresinden geçmeli
        2. Doğal ve samimi olmalı
        3. Call-to-action net olmalı
        4. Emoji kullanımı dengeli olmalı
        5. 150 karakter altında olmalı
        
        {count} adet optimize edilmiş mesaj üret:
        """
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Sen viral büyüme ve Telegram marketing uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            messages = [line.strip().lstrip('- ').lstrip('1234567890. ') 
                       for line in content.split('\n') 
                       if line.strip() and not line.startswith('#')]
            
            return messages[:count]
            
        except Exception as e:
            print(f"❌ GPT-4o mesaj üretme hatası: {e}")
            return []
    
    def record_message_sent(self, message_id: str, content: str, category: str):
        """Mesaj gönderildiğinde kaydet"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO message_performance 
            (message_id, content, category, sent_count, last_used)
            VALUES (?, ?, ?, 
                    COALESCE((SELECT sent_count FROM message_performance WHERE message_id = ?), 0) + 1,
                    CURRENT_TIMESTAMP)
        ''', (message_id, content, category, message_id))
        
        conn.commit()
        conn.close()
        
    def record_engagement(self, message_id: str, engagement_type: str):
        """Engagement kaydı (reply, dm, join)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        column_map = {
            'reply': 'reply_count',
            'dm': 'dm_count', 
            'join': 'join_count'
        }
        
        if engagement_type in column_map:
            column = column_map[engagement_type]
            cursor.execute(f'''
                UPDATE message_performance 
                SET {column} = {column} + 1
                WHERE message_id = ?
            ''', (message_id,))
            
            conn.commit()
            conn.close()
            
            # CTR ve engagement score güncelle
            self.update_performance_metrics(message_id)
        else:
            conn.close()
        
    def update_performance_metrics(self, message_id: str):
        """CTR ve engagement score hesapla"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sent_count, reply_count, dm_count, join_count
            FROM message_performance WHERE message_id = ?
        ''', (message_id,))
        
        result = cursor.fetchone()
        if result:
            sent, replies, dms, joins = result
            
            if sent > 0:
                # CTR = (replies + dms) / sent
                ctr = (replies + dms) / sent
                
                # Engagement Score = weighted sum
                engagement_score = (replies * 1.0 + dms * 2.0 + joins * 5.0) / sent
                
                cursor.execute('''
                    UPDATE message_performance 
                    SET ctr = ?, engagement_score = ?
                    WHERE message_id = ?
                ''', (ctr, engagement_score, message_id))
        
        conn.commit()
        conn.close()
        
    def get_top_performing_messages(self, category: str = None, limit: int = 10) -> List[MessagePerformance]:
        """En iyi performans gösteren mesajları getir"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT message_id, content, category, sent_count, reply_count, 
                   dm_count, join_count, ctr, engagement_score, last_used
            FROM message_performance
        '''
        params = []
        
        if category:
            query += ' WHERE category = ?'
            params.append(category)
            
        query += ' ORDER BY engagement_score DESC, ctr DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        messages = []
        for row in results:
            messages.append(MessagePerformance(
                message_id=row[0],
                content=row[1],
                category=row[2],
                sent_count=row[3],
                reply_count=row[4],
                dm_count=row[5],
                join_count=row[6],
                ctr=row[7],
                engagement_score=row[8],
                last_used=datetime.fromisoformat(row[9])
            ))
        
        conn.close()
        return messages
        
    async def start_ab_test(self, category: str) -> str:
        """A/B test başlat"""
        
        # Yeni mesajlar üret
        new_messages = await self.generate_optimized_messages(category, 2)
        
        if len(new_messages) < 2:
            return "❌ A/B test için yeterli mesaj üretilemedi"
            
        test_id = f"ab_{category}_{int(time.time())}"
        message_a_id = f"msg_{test_id}_a"
        message_b_id = f"msg_{test_id}_b"
        
        # Mesajları kaydet
        self.record_message_sent(message_a_id, new_messages[0], category)
        self.record_message_sent(message_b_id, new_messages[1], category)
        
        # A/B test kaydı
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ab_tests (test_id, message_a_id, message_b_id, category, start_time)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (test_id, message_a_id, message_b_id, category))
        
        conn.commit()
        conn.close()
        
        return f"🧪 A/B Test başlatıldı: {test_id}\nA: {new_messages[0]}\nB: {new_messages[1]}"
        
    def get_optimal_message(self, category: str, exclude_recent_hours: int = 2) -> Optional[MessagePerformance]:
        """En optimal mesajı seç (son kullanılanları hariç tut)"""
        
        cutoff_time = datetime.now() - timedelta(hours=exclude_recent_hours)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_id, content, category, sent_count, reply_count, 
                   dm_count, join_count, ctr, engagement_score, last_used
            FROM message_performance
            WHERE category = ? AND last_used < ?
            ORDER BY engagement_score DESC, ctr DESC
            LIMIT 1
        ''', (category, cutoff_time.isoformat()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return MessagePerformance(
                message_id=result[0],
                content=result[1],
                category=result[2],
                sent_count=result[3],
                reply_count=result[4],
                dm_count=result[5],
                join_count=result[6],
                ctr=result[7],
                engagement_score=result[8],
                last_used=datetime.fromisoformat(result[9])
            )
        
        return None
        
    async def optimize_message_rotation(self) -> Dict[str, str]:
        """Her kategori için en optimal mesajları seç"""
        
        optimized_messages = {}
        
        for category in self.message_categories.keys():
            # En iyi performans gösteren mesajı al
            best_message = self.get_optimal_message(category)
            
            if best_message:
                optimized_messages[category] = best_message.content
            else:
                # Yeni mesaj üret
                new_messages = await self.generate_optimized_messages(category, 1)
                if new_messages:
                    optimized_messages[category] = new_messages[0]
                    # Yeni mesajı kaydet
                    msg_id = f"opt_{category}_{int(time.time())}"
                    self.record_message_sent(msg_id, new_messages[0], category)
        
        return optimized_messages
        
    def generate_performance_report(self) -> str:
        """Performans raporu üret"""
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Genel istatistikler
        cursor.execute('''
            SELECT 
                COUNT(*) as total_messages,
                SUM(sent_count) as total_sent,
                SUM(reply_count) as total_replies,
                SUM(dm_count) as total_dms,
                SUM(join_count) as total_joins,
                AVG(ctr) as avg_ctr,
                AVG(engagement_score) as avg_engagement
            FROM message_performance
        ''')
        
        stats = cursor.fetchone()
        
        # Kategori bazlı performans
        cursor.execute('''
            SELECT 
                category,
                COUNT(*) as message_count,
                AVG(ctr) as avg_ctr,
                AVG(engagement_score) as avg_engagement,
                MAX(engagement_score) as best_engagement
            FROM message_performance
            GROUP BY category
            ORDER BY avg_engagement DESC
        ''')
        
        category_stats = cursor.fetchall()
        
        # En iyi performans gösteren mesajlar
        cursor.execute('''
            SELECT content, category, ctr, engagement_score
            FROM message_performance
            ORDER BY engagement_score DESC
            LIMIT 5
        ''')
        
        top_messages = cursor.fetchall()
        
        conn.close()
        
        # Null check for stats
        if not stats or stats[0] == 0:
            return """
🤖 AI MESSAGE OPTIMIZER RAPORU
===============================
📊 Henüz veri yok - ilk mesajları gönderin!
"""
        
        report = f"""
🤖 AI MESSAGE OPTIMIZER RAPORU
===============================
📊 Genel İstatistikler:
  • Toplam mesaj: {stats[0] or 0}
  • Toplam gönderim: {stats[1] or 0}
  • Toplam yanıt: {stats[2] or 0}
  • Toplam DM: {stats[3] or 0}
  • Toplam katılım: {stats[4] or 0}
  • Ortalama CTR: {(stats[5] or 0):.2%}
  • Ortalama Engagement: {stats[6] or 0:.2f}

📈 Kategori Performansları:
"""
        
        for cat_stat in category_stats:
            report += f"  • {cat_stat[0]}: {(cat_stat[2] or 0):.2%} CTR, {cat_stat[3] or 0:.2f} engagement\n"
            
        report += "\n🏆 En İyi Mesajlar:\n"
        for i, msg in enumerate(top_messages, 1):
            report += f"  {i}. [{msg[1]}] {msg[0][:50]}... (CTR: {(msg[2] or 0):.2%})\n"
            
        return report

async def main():
    """AI Message Optimizer test"""
    
    print("🤖 AI-POWERED MESSAGE OPTIMIZER BAŞLATIYOR...")
    print("=" * 50)
    
    optimizer = AIMessageOptimizer()
    
    # Test mesajları ekle
    test_messages = [
        ("Merhaba! @arayisonlyvips grubuna katılmak ister misin? 🙂", "samimi"),
        ("🚀 @arayisonlyvips 🚀 Hızla büyüyen topluluk! 📈", "emoji"),
        ("@arayisonlyvips grubunda neler oluyor biliyor musun? 🤔", "soru"),
    ]
    
    for content, category in test_messages:
        msg_id = f"test_{category}_{int(time.time())}"
        optimizer.record_message_sent(msg_id, content, category)
        
        # Fake engagement ekle
        for _ in range(random.randint(0, 3)):
            optimizer.record_engagement(msg_id, random.choice(['reply', 'dm', 'join']))
    
    # Yeni optimize edilmiş mesajlar üret
    print("\n🧠 GPT-4o ile yeni mesajlar üretiliyor...")
    for category in ["davet", "topluluk", "samimi"]:
        new_messages = await optimizer.generate_optimized_messages(category, 2)
        print(f"\n📝 {category.upper()} kategorisi:")
        for i, msg in enumerate(new_messages, 1):
            print(f"  {i}. {msg}")
    
    # A/B test başlat
    print("\n🧪 A/B Test başlatılıyor...")
    ab_result = await optimizer.start_ab_test("samimi")
    print(ab_result)
    
    # Optimal mesaj rotasyonu
    print("\n⚡ Optimal mesaj rotasyonu...")
    optimal_messages = await optimizer.optimize_message_rotation()
    for category, message in optimal_messages.items():
        print(f"  • {category}: {message}")
    
    # Performans raporu
    print("\n📊 PERFORMANS RAPORU:")
    print(optimizer.generate_performance_report())
    
    print("\n🎯 AI MESSAGE OPTIMIZER HAZIR!")
    print("Viral büyüme artık AI destekli! 🚀")

if __name__ == "__main__":
    asyncio.run(main()) 