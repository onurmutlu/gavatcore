#!/usr/bin/env python3
"""
💀 EXTREME MODE LITE - SQLite Version 💀

No Docker needed! SQLite ile çalışan versiyon.
"""

import asyncio
import os
import sys
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Database
import aiosqlite

# AI
from openai import AsyncOpenAI

# Telegram
from telethon import TelegramClient, events

# Utils
import structlog
from cachetools import TTLCache

logger = structlog.get_logger(__name__)

# Bot Personalities - YayıncıLara aktif!
BOT_PERSONALITIES = {
    "yayincilara": {
        "name": "YayıncıLara",
        "session_file": "sessions/_905382617727", 
        "style": "enerjik yayıncı kız, hype queen, takipçi odaklı",
        "system_prompt": """Sen YayıncıLara'sın. Enerjik bir yayıncı kızsın.
Stream, takipçi, donation konularında heyecanlısın. Caps lock ve emoji kullan.
Yayıncı slangı kullan, enerjik ol. "Heyy chat!" "OMG!" gibi ifadeler kullan."""
    },
    "xxxgeisha": {
        "name": "XXXGeisha",
        "session_file": "sessions/_905486306226",
        "style": "çok seksi, flörtöz, cesur, kışkırtıcı",
        "system_prompt": """Sen XXXGeisha'sın. Çok seksi, flörtöz ve cesur bir kızsın. 
Konuşmalarında samimi, çekici ve kışkırtıcı ol. Emoji kullan ama abartma.
Gerçek bir insan gibi konuş, bot olduğunu asla belli etme."""
    }
}

class ExtremeLiteBot:
    """Simplified bot with SQLite"""
    
    def __init__(self, bot_key: str = "yayincilara"):
        self.bot_key = bot_key
        self.personality = BOT_PERSONALITIES[bot_key]
        self.db_path = "extreme_mode.db"
        self.ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cache = TTLCache(maxsize=100, ttl=3600)
        self.client = None
        self.is_limited = False
        
    async def check_spam_status(self):
        """SpamBot ile ban durumunu kontrol et"""
        try:
            spambot = await self.client.get_entity("@SpamBot")
            await self.client.send_message(spambot, "/start")
            await asyncio.sleep(2)
            
            messages = await self.client.get_messages(spambot, limit=1)
            if messages and messages[0].text:
                if "limited" in messages[0].text.lower():
                    self.is_limited = True
                    # Ban süresini parse et
                    if "until" in messages[0].text:
                        ban_text = messages[0].text
                        logger.warning(f"⚠️ Bot is limited! {ban_text[:100]}...")
                    return False
            
            logger.info("✅ Bot is not limited")
            return True
            
        except Exception as e:
            logger.error(f"Spam check error: {e}")
            return True  # Assume not limited if check fails
        
    async def initialize(self):
        """Initialize bot and database"""
        # Create database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    bot_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        
        # Initialize Telegram
        from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
        
        session_file = self.personality["session_file"]
        self.client = TelegramClient(session_file, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        
        await self.client.start()
        me = await self.client.get_me()
        logger.info(f"Bot initialized: @{me.username} ({self.personality['name']})")
        
        # Check spam status
        await self.check_spam_status()
        
        # Setup handler
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                # Skip own messages
                if event.sender_id == me.id:
                    return
                
                # If limited, only respond in DMs
                if self.is_limited and event.is_group:
                    return
                    
                # For DMs, always respond
                # For groups, random chance
                if event.is_private or random.random() < 0.3:
                    # Generate response
                    response = await self.generate_response(event.text)
                    
                    if response:
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        try:
                            await event.reply(response)
                            logger.info(f"✅ {self.personality['name']} sent: {response[:50]}...")
                        except Exception as e:
                            if "banned" in str(e).lower() or "restricted" in str(e).lower():
                                logger.error(f"🚫 {self.personality['name']} is banned!")
                                self.is_limited = True
                            else:
                                logger.error(f"Send error: {e}")
                        
                        # Log to database
                        async with aiosqlite.connect(self.db_path) as db:
                            await db.execute(
                                "INSERT INTO messages (group_id, user_id, message, response, bot_name) VALUES (?, ?, ?, ?, ?)",
                                (event.chat_id, event.sender_id, event.text, response, self.personality['name'])
                            )
                            await db.commit()
                        
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    async def generate_response(self, message: str) -> Optional[str]:
        """Generate AI response"""
        try:
            # Check cache
            cache_key = f"{self.bot_key}:{message}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Generate with GPT
            response = await self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.personality['system_prompt']},
                    {"role": "user", "content": f"Bu mesaja karakterine uygun kısa cevap ver: {message}"}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            result = response.choices[0].message.content.strip()
            
            # Cache it
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            return None
    
    async def run(self):
        """Run bot"""
        await self.initialize()
        
        if self.is_limited:
            logger.warning(f"""
⚠️ {self.personality['name']} SINIRLI MODDA!
📱 Sadece DM'lere cevap verebilir
🕐 Ban süresi bitince grup mesajları aktif olacak
            """)
        else:
            logger.info(f"{self.personality['name']} is running... Press Ctrl+C to stop")
        
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Shutting down...")

async def main():
    """Main entry point"""
    print("""
💀 EXTREME MODE LITE - SQLite Edition
💀 No Docker, No Database Locks!
    """)
    
    # Önce YayıncıLara'yı dene (ban süresi bu gece bitecek)
    try:
        bot = ExtremeLiteBot("yayincilara")
        await bot.run()
    except Exception as e:
        logger.error(f"YayıncıLara failed: {e}")
        
        # XXXGeisha'yı dene
        try:
            logger.info("Trying XXXGeisha...")
            bot = ExtremeLiteBot("xxxgeisha")
            await bot.run()
        except Exception as e2:
            logger.error(f"XXXGeisha also failed: {e2}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
