#!/usr/bin/env python3
"""
💀🔥 EXTREME MODE FINAL - NO DATABASE LOCKS! 🔥💀

CONCURRENCY-SAFE, FULL AI, MULTI-DB ARCHITECTURE

Tech Stack:
- PostgreSQL (asyncpg) - Ana veritabanı
- MongoDB (motor) - Document store
- Redis (redis-py[async]) - Cache & locks
- GPT-4o - AI engine
- Telethon - Telegram client
- AsyncIO - Full async
- Distributed Locks - Concurrency safety

💀 DATABASE LOCKED TARIH OLUYOR! 💀
"""

import asyncio
import json
import os
import sys
import time
import random
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# Async Database Drivers
import asyncpg
import motor.motor_asyncio
import redis.asyncio as redis  # New redis async
from redis.asyncio.lock import Lock as RedisLock

# AI
import openai
from openai import AsyncOpenAI

# Telegram
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import User, Chat, Channel, Message
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError

# Utils
import aiofiles
import backoff
from cachetools import TTLCache
import structlog

# Setup structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Bot Personalities
BOT_PERSONALITIES = {
    "xxxgeisha": {
        "name": "XXXGeisha",
        "session_file": "sessions/_905486306226",
        "style": "çok seksi, flörtöz, cesur, kışkırtıcı",
        "traits": ["seksi fanteziler", "cesur yaklaşımlar", "flört", "çekici"],
        "system_prompt": """Sen XXXGeisha'sın. Çok seksi, flörtöz ve cesur bir kızsın. 
Konuşmalarında samimi, çekici ve kışkırtıcı ol. Emoji kullan ama abartma.
Gerçek bir insan gibi konuş, bot olduğunu asla belli etme."""
    },
    "yayincilara": {
        "name": "YayıncıLara", 
        "session_file": "sessions/_905382617727",
        "style": "enerjik yayıncı kız, hype queen, takipçi odaklı",
        "traits": ["yayın", "stream", "donation", "takipçi", "hype"],
        "system_prompt": """Sen YayıncıLara'sın. Enerjik bir yayıncı kızsın.
Stream, takipçi, donation konularında heyecanlısın. Caps lock ve emoji kullan.
Yayıncı slangı kullan, enerjik ol."""
    },
    "babagavat": {
        "name": "BabaGAVAT",
        "session_file": "sessions/babagavat_conversation", 
        "style": "sokak lideri, para babası, dominant, alfa",
        "traits": ["para", "güç", "liderlik", "koruma", "iş"],
        "system_prompt": """Sen BabaGAVAT'sın. Sokak lideri, para babası, alfa erkeksin.
Kısa, etkili, sokak dili kullan. Para ve güç konularında dominant ol.
Patron havasında konuş."""
    }
}

@dataclass
class ConversationContext:
    """Konuşma context'i"""
    group_id: int
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_bot_message: Optional[datetime] = None
    waiting_response: bool = False
    
class DatabaseManager:
    """Concurrency-safe database manager"""
    
    def __init__(self):
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.mongo_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.redis: Optional[redis.Redis] = None
        self._initialized = False
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize all databases with proper connection pooling"""
        async with self._lock:
            if self._initialized:
                return
                
            try:
                # PostgreSQL - Connection pool ile
                logger.info("Initializing PostgreSQL...")
                self.pg_pool = await asyncpg.create_pool(
                    host=os.getenv('PG_HOST', 'localhost'),
                    port=int(os.getenv('PG_PORT', 5432)),
                    user=os.getenv('PG_USER', 'postgres'),
                    password=os.getenv('PG_PASSWORD', 'postgres'),
                    database=os.getenv('PG_DATABASE', 'extreme_mode'),
                    min_size=10,
                    max_size=20,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300,
                    command_timeout=60
                )
                
                # Create tables
                await self._create_pg_tables()
                
                # MongoDB - Async motor client
                logger.info("Initializing MongoDB...")
                self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                    os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
                    maxPoolSize=50,
                    minPoolSize=10,
                    maxIdleTimeMS=300000
                )
                self.mongo_db = self.mongo_client.extreme_mode
                
                # Create indexes
                await self._create_mongo_indexes()
                
                # Redis - New async redis
                logger.info("Initializing Redis...")
                self.redis = await redis.from_url(
                    os.getenv('REDIS_URI', 'redis://localhost:6379'),
                    encoding='utf-8',
                    decode_responses=True,
                    max_connections=20
                )
                
                self._initialized = True
                logger.info("All databases initialized successfully!")
                
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise
    
    async def _create_pg_tables(self):
        """Create PostgreSQL tables"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_sessions (
                    bot_name VARCHAR(50) PRIMARY KEY,
                    session_data TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_active TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS messages (
                    id BIGSERIAL PRIMARY KEY,
                    bot_name VARCHAR(50),
                    group_id BIGINT,
                    user_id BIGINT,
                    message_text TEXT,
                    is_bot_message BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS groups (
                    id BIGINT PRIMARY KEY,
                    name VARCHAR(255),
                    member_count INTEGER,
                    last_activity TIMESTAMP DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                );
                
                CREATE INDEX IF NOT EXISTS idx_messages_bot_group 
                ON messages(bot_name, group_id, created_at DESC);
            ''')
    
    async def _create_mongo_indexes(self):
        """Create MongoDB indexes"""
        # Conversation contexts
        await self.mongo_db.conversations.create_index([
            ("group_id", 1),
            ("bot_name", 1)
        ])
        
        # AI responses cache
        await self.mongo_db.ai_cache.create_index([
            ("hash", 1),
            ("created_at", -1)
        ])
        
        # User profiles
        await self.mongo_db.users.create_index([("user_id", 1)])
    
    @asynccontextmanager
    async def get_pg_connection(self):
        """Get PostgreSQL connection with proper handling"""
        conn = await self.pg_pool.acquire()
        try:
            yield conn
        finally:
            await self.pg_pool.release(conn)
    
    async def get_distributed_lock(self, key: str, timeout: int = 30):
        """Get distributed lock using Redis"""
        lock_key = f"lock:{key}"
        lock = self.redis.lock(lock_key, timeout=timeout)
        return lock
    
    async def close(self):
        """Close all database connections"""
        if self.pg_pool:
            await self.pg_pool.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.redis:
            await self.redis.close()

class AIEngine:
    """GPT-4o powered AI engine with caching"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.response_cache = TTLCache(maxsize=1000, ttl=3600)
        
    async def generate_response(
        self, 
        bot_personality: Dict[str, Any],
        context: ConversationContext,
        original_message: str,
        sender_name: str
    ) -> Optional[str]:
        """Generate AI response with context"""
        
        # Cache key
        cache_key = hashlib.md5(
            f"{bot_personality['name']}:{original_message}:{sender_name}".encode()
        ).hexdigest()
        
        # Check cache
        if cache_key in self.response_cache:
            logger.info(f"Using cached response for {bot_personality['name']}")
            return self.response_cache[cache_key]
        
        # Prepare context
        context_messages = context.messages[-10:] if context.messages else []
        context_text = "\n".join([
            f"{msg['sender']}: {msg['text']}" 
            for msg in context_messages
        ])
        
        # Generate response
        try:
            messages = [
                {"role": "system", "content": bot_personality['system_prompt']},
                {"role": "user", "content": f"""
Grup konuşması:
{context_text}

{sender_name} şimdi dedi ki: "{original_message}"

Sen {bot_personality['name']} olarak nasıl cevap verirsin? 
Kısa, doğal ve karakterine uygun cevap ver.
"""}
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for faster responses
                messages=messages,
                temperature=0.8,
                max_tokens=150,
                frequency_penalty=1.5,
                presence_penalty=1.0
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            # Cache response
            self.response_cache[cache_key] = generated_text
            
            # Also save to MongoDB for long-term cache
            await self.db.mongo_db.ai_cache.insert_one({
                "hash": cache_key,
                "bot_name": bot_personality['name'],
                "response": generated_text,
                "created_at": datetime.utcnow()
            })
            
            return generated_text
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return None

class ExtremeModeBot:
    """Single bot instance with concurrency safety"""
    
    def __init__(
        self, 
        bot_name: str,
        personality: Dict[str, Any],
        db_manager: DatabaseManager,
        ai_engine: AIEngine
    ):
        self.bot_name = bot_name
        self.personality = personality
        self.db = db_manager
        self.ai = ai_engine
        self.client: Optional[TelegramClient] = None
        self.contexts: Dict[int, ConversationContext] = {}
        self.is_running = False
        
    async def initialize(self):
        """Initialize bot with session"""
        try:
            session_path = self.personality['session_file']
            
            # Create client
            from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
            
            self.client = TelegramClient(
                session_path,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH
            )
            
            await self.client.start()
            me = await self.client.get_me()
            
            logger.info(f"Bot {self.bot_name} initialized: @{me.username}")
            
            # Setup handlers
            await self._setup_handlers()
            
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization error for {self.bot_name}: {e}")
            return False
    
    async def _setup_handlers(self):
        """Setup message handlers"""
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            """Handle incoming messages"""
            try:
                # Skip own messages
                if event.sender_id == (await self.client.get_me()).id:
                    return
                
                # Get or create context
                group_id = event.chat_id
                if group_id not in self.contexts:
                    self.contexts[group_id] = ConversationContext(group_id=group_id)
                
                context = self.contexts[group_id]
                
                # Rate limiting
                if context.last_bot_message:
                    time_diff = (datetime.utcnow() - context.last_bot_message).seconds
                    if time_diff < 30:  # 30 second cooldown
                        return
                
                # Random reply chance
                if random.random() > 0.3:  # 30% chance to reply
                    return
                
                # Get sender info
                sender = await event.get_sender()
                sender_name = getattr(sender, 'first_name', 'Unknown')
                
                # Add to context
                context.messages.append({
                    "sender": sender_name,
                    "text": event.text,
                    "timestamp": datetime.utcnow()
                })
                
                # Keep last 50 messages
                if len(context.messages) > 50:
                    context.messages = context.messages[-50:]
                
                # Generate AI response
                response = await self.ai.generate_response(
                    self.personality,
                    context,
                    event.text,
                    sender_name
                )
                
                if response:
                    # Send with delay
                    await asyncio.sleep(random.uniform(2, 5))
                    
                    await event.reply(response)
                    
                    # Update context
                    context.last_bot_message = datetime.utcnow()
                    context.messages.append({
                        "sender": self.personality['name'],
                        "text": response,
                        "timestamp": datetime.utcnow()
                    })
                    
                    # Log to database
                    await self._log_message(
                        group_id=group_id,
                        user_id=event.sender_id,
                        message_text=event.text,
                        bot_response=response
                    )
                    
            except Exception as e:
                logger.error(f"Message handler error for {self.bot_name}: {e}")
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _log_message(self, group_id: int, user_id: int, message_text: str, bot_response: str):
        """Log message to database with retry"""
        try:
            # Use distributed lock
            lock = await self.db.get_distributed_lock(f"log:{self.bot_name}:{group_id}")
            
            async with lock:
                # PostgreSQL logging
                async with self.db.get_pg_connection() as conn:
                    # User message
                    await conn.execute('''
                        INSERT INTO messages (bot_name, group_id, user_id, message_text, is_bot_message)
                        VALUES ($1, $2, $3, $4, $5)
                    ''', self.bot_name, group_id, user_id, message_text, False)
                    
                    # Bot response
                    await conn.execute('''
                        INSERT INTO messages (bot_name, group_id, user_id, message_text, is_bot_message)
                        VALUES ($1, $2, $3, $4, $5)
                    ''', self.bot_name, group_id, user_id, bot_response, True)
                
                # MongoDB logging
                await self.db.mongo_db.message_logs.insert_one({
                    "bot_name": self.bot_name,
                    "group_id": group_id,
                    "user_id": user_id,
                    "original_message": message_text,
                    "bot_response": bot_response,
                    "timestamp": datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"Message logging error: {e}")
    
    async def discover_groups(self) -> List[Dict[str, Any]]:
        """Discover all groups bot is in"""
        groups = []
        
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    groups.append({
                        "id": dialog.id,
                        "name": dialog.name,
                        "members": getattr(dialog.entity, 'participants_count', 0)
                    })
                    
                    # Save to database
                    async with self.db.get_pg_connection() as conn:
                        await conn.execute('''
                            INSERT INTO groups (id, name, member_count)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (id) DO UPDATE 
                            SET name = EXCLUDED.name,
                                member_count = EXCLUDED.member_count,
                                last_activity = NOW()
                        ''', dialog.id, dialog.name, getattr(dialog.entity, 'participants_count', 0))
            
            logger.info(f"Bot {self.bot_name} discovered {len(groups)} groups")
            return groups
            
        except Exception as e:
            logger.error(f"Group discovery error: {e}")
            return []
    
    async def send_strategic_message(self, group_id: int, message: str):
        """Send strategic message to group"""
        try:
            # Rate limiting check
            cache_key = f"sent:{self.bot_name}:{group_id}"
            if await self.db.redis.exists(cache_key):
                return
            
            # Send message
            await self.client.send_message(group_id, message)
            
            # Set rate limit (5 minutes)
            await self.db.redis.setex(cache_key, 300, "1")
            
            logger.info(f"Bot {self.bot_name} sent strategic message to {group_id}")
            
        except Exception as e:
            logger.error(f"Strategic message error: {e}")
    
    async def run(self):
        """Run bot main loop"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Just keep the bot alive
                await asyncio.sleep(60)
                
                # Periodic health check
                if self.client.is_connected():
                    logger.debug(f"Bot {self.bot_name} is healthy")
                else:
                    logger.warning(f"Bot {self.bot_name} disconnected, reconnecting...")
                    await self.client.connect()
                    
            except Exception as e:
                logger.error(f"Bot run loop error: {e}")
                await asyncio.sleep(10)
    
    async def shutdown(self):
        """Shutdown bot gracefully"""
        self.is_running = False
        
        if self.client:
            await self.client.disconnect()
            
        logger.info(f"Bot {self.bot_name} shutdown complete")

class ExtremeModeOrchestrator:
    """Main orchestrator for all bots"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ai_engine: Optional[AIEngine] = None
        self.bots: Dict[str, ExtremeModeBot] = {}
        self.is_running = False
        
    async def initialize(self):
        """Initialize the entire system"""
        try:
            print("""
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
💀                                                               💀
💀         🔥 EXTREME MODE FINAL - NO LOCKS! 🔥                 💀
💀                                                               💀
💀          💣 DATABASE LOCKED TARIH OLUYOR! 💣                  💀
💀                                                               💀
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀

🚀 Concurrency-Safe Architecture
🧠 GPT-4o AI Engine
📊 PostgreSQL + MongoDB + Redis
🔒 Distributed Locks
🤖 3 AI Personalities
💬 Context-Aware Conversations
            """)
            
            # Initialize databases
            logger.info("Initializing databases...")
            await self.db_manager.initialize()
            
            # Initialize AI engine
            logger.info("Initializing AI engine...")
            self.ai_engine = AIEngine(self.db_manager)
            
            # Initialize bots
            logger.info("Initializing bots...")
            for bot_name, personality in BOT_PERSONALITIES.items():
                bot = ExtremeModeBot(
                    bot_name=bot_name,
                    personality=personality,
                    db_manager=self.db_manager,
                    ai_engine=self.ai_engine
                )
                
                if await bot.initialize():
                    self.bots[bot_name] = bot
                    
                    # Discover groups
                    await bot.discover_groups()
                else:
                    logger.error(f"Failed to initialize bot: {bot_name}")
            
            logger.info(f"System initialized with {len(self.bots)} bots")
            return True
            
        except Exception as e:
            logger.error(f"System initialization error: {e}")
            traceback.print_exc()
            return False
    
    async def run_strategic_campaign(self):
        """Run strategic messaging campaign"""
        campaign_round = 0
        
        while self.is_running:
            campaign_round += 1
            logger.info(f"Starting campaign round #{campaign_round}")
            
            try:
                # Get top groups from database
                async with self.db_manager.get_pg_connection() as conn:
                    groups = await conn.fetch('''
                        SELECT DISTINCT g.id, g.name, g.member_count
                        FROM groups g
                        WHERE g.member_count > 10
                        ORDER BY g.last_activity DESC
                        LIMIT 20
                    ''')
                
                # Strategic message deployment
                for group in groups:
                    group_id = group['id']
                    
                    # Select random bot
                    bot_name = random.choice(list(self.bots.keys()))
                    bot = self.bots[bot_name]
                    
                    # Generate strategic message
                    context = ConversationContext(group_id=group_id)
                    
                    # Get recent messages from this group
                    async with self.db_manager.get_pg_connection() as conn:
                        recent_messages = await conn.fetch('''
                            SELECT message_text, created_at
                            FROM messages
                            WHERE group_id = $1
                            ORDER BY created_at DESC
                            LIMIT 10
                        ''', group_id)
                    
                    if recent_messages:
                        for msg in recent_messages:
                            context.messages.append({
                                "sender": "User",
                                "text": msg['message_text'],
                                "timestamp": msg['created_at']
                            })
                    
                    # Generate AI message
                    strategic_message = await self.ai_engine.generate_response(
                        bot.personality,
                        context,
                        "Gruba ilginç bir şey yaz",
                        "System"
                    )
                    
                    if strategic_message:
                        await bot.send_strategic_message(group_id, strategic_message)
                        
                        # Random delay between messages
                        await asyncio.sleep(random.uniform(30, 60))
                
                # Wait before next round
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Campaign error: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        """Run the entire system"""
        self.is_running = True
        
        try:
            # Start all bots
            bot_tasks = []
            for bot_name, bot in self.bots.items():
                task = asyncio.create_task(bot.run())
                bot_tasks.append(task)
                logger.info(f"Started bot: {bot_name}")
            
            # Start campaign
            campaign_task = asyncio.create_task(self.run_strategic_campaign())
            
            # Monitor health
            while self.is_running:
                await asyncio.sleep(60)
                
                # Health check
                active_bots = sum(1 for bot in self.bots.values() if bot.is_running)
                logger.info(f"System health: {active_bots}/{len(self.bots)} bots active")
                
                # Database health
                try:
                    async with self.db_manager.get_pg_connection() as conn:
                        await conn.fetchval("SELECT 1")
                    logger.debug("PostgreSQL is healthy")
                except Exception as e:
                    logger.error(f"PostgreSQL health check failed: {e}")
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"System error: {e}")
            traceback.print_exc()
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown system gracefully"""
        logger.info("Shutting down system...")
        self.is_running = False
        
        # Shutdown all bots
        shutdown_tasks = []
        for bot_name, bot in self.bots.items():
            task = asyncio.create_task(bot.shutdown())
            shutdown_tasks.append(task)
        
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # Close databases
        await self.db_manager.close()
        
        logger.info("System shutdown complete")

async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create orchestrator
    orchestrator = ExtremeModeOrchestrator()
    
    # Initialize
    if not await orchestrator.initialize():
        logger.error("Failed to initialize system")
        return
    
    # Run
    await orchestrator.run()

if __name__ == "__main__":
    # Check environment
    required_env = ['OPENAI_API_KEY', 'TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
    missing = [env for env in required_env if not os.getenv(env)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please set them in .env file")
        sys.exit(1)
    
    # Create required directories
    Path("sessions").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Run
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n💀 EXTREME MODE TERMINATED BY USER")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        traceback.print_exc() 