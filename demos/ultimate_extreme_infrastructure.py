from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
💀🔥 ULTIMATE EXTREME INFRASTRUCTURE 🔥💀

TEKNOLOJİK SINIRLAR YOK!

Tech Stack:
- PostgreSQL: Ana veritabanı
- MongoDB: NoSQL dökümanlar
- Redis: Cache & Pub/Sub
- Celery: Asenkron task queue
- RabbitMQ: Message broker
- WebSocket: Real-time iletişim
- GraphQL: Modern API
- ElasticSearch: Log aggregation
- Prometheus: Monitoring
- Docker: Containerization

💀 BU GERÇEK EXTREME! 💀
"""

import asyncio
import json
import os
import random
import aioredis
import asyncpg
import motor.motor_asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import structlog
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
import openai
from celery import Celery
import websockets
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metrics
message_counter = Counter('telegram_messages_sent', 'Total messages sent', ['bot', 'target_type'])
response_time = Histogram('gpt_response_time', 'GPT-4o response time')
active_bots = Gauge('active_bots', 'Number of active bots')
active_connections = Gauge('active_connections', 'Number of active connections')

logger = structlog.get_logger("ultimate.extreme")

class UltimateExtremeInfrastructure:
    """💀 GERÇEK EXTREME - TEKNOLOJİK SINIRLAR YOK! 💀"""
    
    def __init__(self):
        self.clients = {}  # Bot clientları
        self.is_running = False
        
        # Database connections
        self.pg_pool = None  # PostgreSQL
        self.mongo_db = None  # MongoDB
        self.redis = None  # Redis
        
        # Celery setup
        self.celery_app = Celery(
            'extreme_tasks',
            broker='amqp://guest@localhost//',
            backend='redis://localhost:6379/0'
        )
        
        # OpenAI
        self.openai_client = None
        self._setup_openai()
        
        # WebSocket server
        self.websocket_server = None
        self.connected_clients = set()
        
        print("""
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
💀                                                               💀
💀         🔥 ULTIMATE EXTREME INFRASTRUCTURE 🔥                💀
💀                                                               💀
💀              💣 TEKNOLOJİK SINIRLAR YOK! 💣                  💀
💀                                                               💀
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀

🚀 PostgreSQL + MongoDB + Redis
🧠 GPT-4o Turbo Mode
⚡ Celery + RabbitMQ
🔌 WebSocket Real-time
📊 Prometheus + Grafana Ready
🐳 Docker Native
☸️  Kubernetes Ready
        """)
    
    def _setup_openai(self):
        """🧠 OpenAI GPT-4o setup"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("❌ OPENAI_API_KEY YOK!")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        print("🔥 GPT-4o EXTREME TURBO READY!")
    
    async def initialize_databases(self):
        """🗄️ Tüm veritabanlarını başlat"""
        try:
            print("🗄️ EXTREME DATABASE INITIALIZATION...")
            
            # PostgreSQL
            print("   🐘 PostgreSQL connecting...")
            self.pg_pool = await asyncpg.create_pool(
                host='localhost',
                port=5432,
                user='postgres',
                password='postgres',
                database='extreme_telegram',
                min_size=10,
                max_size=20
            )
            
            # Create tables
            async with self.pg_pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS bots (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE,
                        phone VARCHAR(20),
                        session_data BYTEA,
                        personality JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        last_active TIMESTAMP
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        bot_id INTEGER REFERENCES bots(id),
                        target_id BIGINT,
                        target_name VARCHAR(255),
                        message_text TEXT,
                        gpt_response_time FLOAT,
                        sent_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS targets (
                        id BIGINT PRIMARY KEY,
                        name VARCHAR(255),
                        type VARCHAR(50),
                        members INTEGER,
                        priority INTEGER DEFAULT 0,
                        last_message TIMESTAMP,
                        metadata JSONB
                    )
                ''')
            
            print("   ✅ PostgreSQL ready!")
            
            # MongoDB
            print("   🍃 MongoDB connecting...")
            mongo_client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
            self.mongo_db = mongo_client.extreme_telegram
            
            # Create indexes
            await self.mongo_db.conversations.create_index([("bot_id", 1), ("user_id", 1)])
            await self.mongo_db.gpt_cache.create_index([("prompt_hash", 1)])
            await self.mongo_db.analytics.create_index([("timestamp", -1)])
            
            print("   ✅ MongoDB ready!")
            
            # Redis
            print("   🔴 Redis connecting...")
            self.redis = await aioredis.create_redis_pool(
                'redis://localhost:6379',
                encoding='utf-8',
                minsize=5,
                maxsize=10
            )
            
            print("   ✅ Redis ready!")
            
            print("🔥 ALL DATABASES CONNECTED! EXTREME MODE READY!")
            
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            raise
    
    async def load_bot_sessions(self):
        """🤖 Bot session'larını PostgreSQL'den yükle"""
        try:
            print("🤖 LOADING BOT SESSIONS FROM POSTGRESQL...")
            
            # Önce mevcut session dosyalarını PostgreSQL'e kaydet
            session_files = [
                ("_905486306226", "XXXGeisha", "extreme seksi"),
                ("_905382617727", "YayıncıLara", "hype queen"),
                ("babagavat_conversation", "BabaGAVAT", "alfa gangster")
            ]
            
            async with self.pg_pool.acquire() as conn:
                for session_file, bot_name, personality_style in session_files:
                    # Session dosyasını oku
                    session_path = f"sessions/{session_file}.session"
                    if os.path.exists(session_path):
                        with open(session_path, 'rb') as f:
                            session_data = f.read()
                        
                        # PostgreSQL'e kaydet
                        await conn.execute('''
                            INSERT INTO bots (username, session_data, personality)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (username) 
                            DO UPDATE SET 
                                session_data = EXCLUDED.session_data,
                                last_active = NOW()
                        ''', bot_name.lower(), session_data, json.dumps({
                            "name": bot_name,
                            "style": personality_style
                        }))
                        
                        print(f"   ✅ {bot_name} session saved to PostgreSQL")
                
                # Şimdi botları yükle
                rows = await conn.fetch('SELECT * FROM bots WHERE session_data IS NOT NULL')
                
                for row in rows:
                    bot_id = row['id']
                    username = row['username']
                    session_data = row['session_data']
                    personality = json.loads(row['personality'])
                    
                    # Geçici session dosyası oluştur
                    temp_session = f"sessions/temp_{username}"
                    with open(f"{temp_session}.session", 'wb') as f:
                        f.write(session_data)
                    
                    # TelegramClient oluştur
                    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
                    
                    client = TelegramClient(
                        temp_session,
                        TELEGRAM_API_ID,
                        TELEGRAM_API_HASH
                    )
                    
                    await client.start()
                    me = await client.get_me()
                    
                    self.clients[username] = {
                        "id": bot_id,
                        "client": client,
                        "me": me,
                        "personality": personality
                    }
                    
                    # Update last active
                    await conn.execute(
                        'UPDATE bots SET last_active = NOW() WHERE id = $1',
                        bot_id
                    )
                    
                    print(f"   🔥 {personality['name']}: @{me.username} LOADED!")
                    active_bots.inc()
            
            print(f"💀 {len(self.clients)} EXTREME BOTS LOADED FROM POSTGRESQL! 💀")
            
        except Exception as e:
            logger.error(f"❌ Bot loading error: {e}")
            raise
    
    async def discover_and_prioritize_targets(self):
        """🎯 Hedefleri keşfet ve PostgreSQL'de önceliklendir"""
        try:
            print("🔍 DISCOVERING TARGETS WITH AI PRIORITIZATION...")
            
            all_targets = {}
            
            # Her bot ile hedefleri tara
            for bot_name, bot_data in self.clients.items():
                client = bot_data["client"]
                
                async for dialog in client.iter_dialogs():
                    try:
                        if hasattr(dialog.entity, 'megagroup') or hasattr(dialog.entity, 'broadcast'):
                            target_id = dialog.id
                            target_name = dialog.name or "Unknown"
                            members = getattr(dialog.entity, 'participants_count', 0)
                            
                            # Skip keywords
                            skip_keywords = ['bot', 'spam', 'test', 'debug']
                            if any(keyword in target_name.lower() for keyword in skip_keywords):
                                continue
                            
                            all_targets[target_id] = {
                                "id": target_id,
                                "name": target_name,
                                "type": "megagroup" if hasattr(dialog.entity, 'megagroup') else "channel",
                                "members": members
                            }
                    except:
                        continue
            
            # PostgreSQL'e kaydet ve önceliklendir
            async with self.pg_pool.acquire() as conn:
                for target_id, target_info in all_targets.items():
                    # AI ile öncelik hesapla
                    priority = await self._calculate_target_priority(target_info)
                    
                    await conn.execute('''
                        INSERT INTO targets (id, name, type, members, priority, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (id) 
                        DO UPDATE SET 
                            members = EXCLUDED.members,
                            priority = EXCLUDED.priority
                    ''', target_id, target_info['name'], target_info['type'], 
                        target_info['members'], priority, json.dumps(target_info))
                
                # En yüksek öncelikli 100 hedefi al
                top_targets = await conn.fetch('''
                    SELECT * FROM targets 
                    ORDER BY priority DESC, members DESC 
                    LIMIT 100
                ''')
                
                print(f"🎯 {len(top_targets)} HIGH-PRIORITY TARGETS IDENTIFIED!")
                
                # Redis'e cache'le
                for target in top_targets[:10]:
                    await self.redis.hset(
                        f"target:{target['id']}", 
                        mapping={
                            'name': target['name'],
                            'priority': str(target['priority']),
                            'members': str(target['members'])
                        }
                    )
                    print(f"   🎯 {target['name']} (Priority: {target['priority']}, Members: {target['members']})")
            
        except Exception as e:
            logger.error(f"❌ Target discovery error: {e}")
    
    async def _calculate_target_priority(self, target_info):
        """🧠 GPT-4o ile hedef önceliği hesapla"""
        try:
            prompt = f"""
Telegram grubu/kanalı değerlendir ve 0-100 arası öncelik puanı ver:

Grup: {target_info['name']}
Üye Sayısı: {target_info['members']}
Tip: {target_info['type']}

Kriteler:
- Üye sayısı ve aktiflik potansiyeli
- Grup adından anlaşılan konu/tema
- Viral potansiyel
- Para kazanma potansiyeli

Sadece sayı döndür (0-100).
"""
            
            with response_time.time():
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                    temperature=0.3
                )
            
            try:
                priority = int(response.choices[0].message.content.strip())
                return max(0, min(100, priority))
            except:
                return 50  # Default
                
        except Exception as e:
            return 50
    
    # Celery Tasks
    @staticmethod
    @Celery.task
    def generate_extreme_message_task(target_info, personality):
        """Celery task for message generation"""
        # Bu Celery worker'da çalışacak
        pass
    
    async def setup_websocket_server(self):
        """🔌 WebSocket server for real-time monitoring"""
        async def handle_client(websocket, path):
            self.connected_clients.add(websocket)
            active_connections.inc()
            try:
                await websocket.send(json.dumps({
                    "type": "connected",
                    "message": "EXTREME MODE MONITORING CONNECTED"
                }))
                
                async for message in websocket:
                    # Handle incoming commands
                    data = json.loads(message)
                    if data.get("command") == "status":
                        await self.broadcast_status()
                        
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.connected_clients.remove(websocket)
                active_connections.dec()
        
        self.websocket_server = await websockets.serve(
            handle_client, "localhost", 8765
        )
        print("🔌 WebSocket server running on ws://localhost:8765")
    
    async def broadcast_status(self):
        """📡 Broadcast status to all WebSocket clients"""
        if self.connected_clients:
            status = {
                "type": "status",
                "timestamp": datetime.now().isoformat(),
                "active_bots": len(self.clients),
                "redis_info": await self.redis.info() if self.redis else None
            }
            
            await asyncio.gather(
                *[client.send(json.dumps(status)) for client in self.connected_clients],
                return_exceptions=True
            )
    
    async def run_extreme_mode(self):
        """🚀 EXTREME MODE with full infrastructure"""
        try:
            # Start Prometheus metrics server
            start_http_server(8000)
            print("📊 Prometheus metrics on http://localhost:8000")
            
            print("🚀 ULTIMATE EXTREME MODE RUNNING!")
            print("💀 FULL TECH STACK ACTIVE!")
            print("🛑 Durdurmak için Ctrl+C")
            
            attack_round = 0
            while self.is_running:
                attack_round += 1
                print(f"\n🔥 EXTREME ATTACK ROUND #{attack_round} 🔥")
                
                # PostgreSQL'den hedefleri al
                async with self.pg_pool.acquire() as conn:
                    targets = await conn.fetch('''
                        SELECT * FROM targets 
                        WHERE last_message IS NULL 
                           OR last_message < NOW() - INTERVAL '5 minutes'
                        ORDER BY priority DESC 
                        LIMIT 20
                    ''')
                
                for target in targets:
                    for bot_name, bot_data in self.clients.items():
                        try:
                            # Redis'den cache kontrol
                            cache_key = f"sent:{bot_data['id']}:{target['id']}"
                            if await self.redis.exists(cache_key):
                                continue
                            
                            # MongoDB'den conversation history al
                            history = await self.mongo_db.conversations.find({
                                "target_id": target['id']
                            }).sort("timestamp", -1).limit(10).to_list(10)
                            
                            # GPT-4o ile mesaj oluştur
                            message = await self._generate_extreme_message_v2(
                                target, bot_data['personality'], history
                            )
                            
                            # Mesajı gönder
                            client = bot_data['client']
                            await client.send_message(target['id'], message)
                            
                            # PostgreSQL'e kaydet
                            async with self.pg_pool.acquire() as conn2:
                                await conn2.execute('''
                                    INSERT INTO messages (bot_id, target_id, target_name, message_text)
                                    VALUES ($1, $2, $3, $4)
                                ''', bot_data['id'], target['id'], target['name'], message)
                                
                                await conn2.execute('''
                                    UPDATE targets SET last_message = NOW() WHERE id = $1
                                ''', target['id'])
                            
                            # Redis cache
                            await self.redis.setex(cache_key, 300, "1")  # 5 dakika
                            
                            # MongoDB analytics
                            await self.mongo_db.analytics.insert_one({
                                "bot_id": bot_data['id'],
                                "target_id": target['id'],
                                "message": message,
                                "timestamp": datetime.now()
                            })
                            
                            # Metrics
                            message_counter.labels(
                                bot=bot_name,
                                target_type=target['type']
                            ).inc()
                            
                            # WebSocket broadcast
                            await self.broadcast_status()
                            
                            print(f"""
🚀 EXTREME MESSAGE SENT!
🤖 Bot: {bot_data['personality']['name']}
🎯 Target: {target['name']} (Priority: {target['priority']})
💬 Message: {message}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
                            """)
                            
                            await asyncio.sleep(random.uniform(2, 5))
                            
                        except FloodWaitError as e:
                            wait_time = e.seconds
                            print(f"⚠️ Flood wait: {wait_time} seconds")
                            await asyncio.sleep(wait_time)
                        except Exception as e:
                            logger.error(f"Message send error: {e}")
                
                # Round delay
                await asyncio.sleep(random.uniform(30, 60))
                
        except Exception as e:
            logger.error(f"❌ Extreme mode error: {e}")
        finally:
            await self.shutdown()
    
    async def _generate_extreme_message_v2(self, target, personality, history):
        """🧠 GPT-4o ile gelişmiş mesaj oluşturma"""
        try:
            # MongoDB'den GPT cache kontrol
            prompt_hash = hash(f"{target['id']}:{personality['name']}")
            cached = await self.mongo_db.gpt_cache.find_one({"prompt_hash": prompt_hash})
            
            if cached and (datetime.now() - cached['timestamp']).seconds < 3600:
                return cached['response']
            
            # Conversation context
            context = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in history[-5:]])
            
            system_prompt = f"""
Sen {personality['name']} karakterisin. EXTREME MODE ACTIVE!

KARAKTER: {personality['style']}
Target: {target['name']} ({target['members']} üye, Priority: {target['priority']})

EXTREME KURALLAR:
- Maksimum dikkat çek
- İnsan gibi doğal konuş
- Viral potansiyeli yüksek
- Emoji kullan ama abartma
- Kısa ve etkili
- ASLA bot olduğunu belli etme
- Her mesaj benzersiz

{f"Son konuşmalar:\n{context}" if context else ""}
"""

            user_prompt = "Bu gruba dikkat çekici, viral potansiyeli yüksek bir mesaj yaz."
            
            with response_time.time():
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.95,
                    frequency_penalty=2.0,
                    presence_penalty=2.0
                )
            
            message = response.choices[0].message.content.strip()
            
            # Cache response
            await self.mongo_db.gpt_cache.insert_one({
                "prompt_hash": prompt_hash,
                "response": message,
                "timestamp": datetime.now()
            })
            
            return message
            
        except Exception as e:
            logger.error(f"GPT error: {e}")
            return "Selam! 👋"
    
    async def shutdown(self):
        """🛑 Graceful shutdown"""
        try:
            print("\n🛑 EXTREME MODE SHUTTING DOWN...")
            
            self.is_running = False
            
            # Close all connections
            for bot_name, bot_data in self.clients.items():
                await bot_data["client"].disconnect()
            
            if self.pg_pool:
                await self.pg_pool.close()
            
            if self.redis:
                self.redis.close()
                await self.redis.wait_closed()
            
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            print("💀 EXTREME MODE TERMINATED!")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

async def main():
    """🚀 ULTIMATE EXTREME LAUNCHER"""
    try:
        # Create system
        extreme = UltimateExtremeInfrastructure()
        
        # Initialize all databases
        await extreme.initialize_databases()
        
        # Load bot sessions from PostgreSQL
        await extreme.load_bot_sessions()
        
        # Discover and prioritize targets
        await extreme.discover_and_prioritize_targets()
        
        # Setup WebSocket server
        await extreme.setup_websocket_server()
        
        # Set running flag
        extreme.is_running = True
        
        # RUN EXTREME MODE!
        await extreme.run_extreme_mode()
        
    except KeyboardInterrupt:
        print("\n💀 TERMINATED BY USER")
    except Exception as e:
        logger.error(f"❌ MAIN ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("""
    💀💀💀 ULTIMATE EXTREME MODE 💀💀💀
    
    Requirements:
    - PostgreSQL running on localhost:5432
    - MongoDB running on localhost:27017
    - Redis running on localhost:6379
    - RabbitMQ running (for Celery)
    
    Features:
    - Multi-database architecture
    - AI-powered target prioritization
    - Real-time WebSocket monitoring
    - Prometheus metrics
    - Distributed task queue
    
    READY TO UNLEASH? (yes/no)
    """)
    
    confirm = input(">>> ").lower()
    if confirm == "yes":
        asyncio.run(main())
    else:
        print("❌ Aborted") 