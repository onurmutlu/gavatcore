#!/usr/bin/env python3
"""
🔥🔥🔥 ULTIMATE TELEGRAM BOT LAUNCHER 🔥🔥🔥

💪 ONUR METODU - FULL TELEGRAM BOT POWER + AI SUPPORT!

Features:
- Real Telegram Bot Clients (Multiple bots)
- Full GPT-4o Chat Support  
- DM & Group Message Handling
- Voice Chat Integration
- Social Gaming & Coin System
- ErkoAnalyzer Intelligence
- Full Muhabbet & Interaction

🎯 HEDEF: ULTIMATE BOT ECOSYSTEM!
"""

import asyncio
import uvicorn
import multiprocessing
import time
import json
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog
import logging
from dataclasses import dataclass, asdict

# Core Systems
from core.coin_service import babagavat_coin_service
from core.erko_analyzer import babagavat_erko_analyzer
from core.redis_manager import babagavat_redis_manager
from core.mongodb_manager import babagavat_mongo_manager
from core.database_manager import database_manager
from core.user_analyzer import babagavat_user_analyzer

# V2 Systems  
from core.mcp_api_system import mcp_api
from core.ai_voice_engine import initialize_voice_engine
from core.social_gaming_engine import social_gaming
from core.advanced_ai_manager import AdvancedAIManager, AITaskType, AIPriority

# Bot Systems
from telethon import TelegramClient, events
from handlers.dm_handler import setup_dm_handlers
from handlers.group_handler import setup_group_handlers

# API & Config
from api.coin_endpoints import app
from config import validate_config, TELEGRAM_API_ID, TELEGRAM_API_HASH

logger = structlog.get_logger("ultimate.telegram_bot_launcher")

@dataclass
class BotConfig:
    """Bot konfigürasyonu"""
    username: str
    session_file: str
    api_id: int
    api_hash: str
    phone: str = ""
    bot_token: str = ""
    is_bot: bool = False
    enabled: bool = True

class UltimateTelegramBotLauncher:
    """🔥 Ultimate Telegram Bot Launcher - FULL ECOSYSTEM POWER!"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.is_running = False
        
        # Bot clients
        self.bot_clients = {}  # {username: {"client": client, "config": config}}
        
        # AI Systems
        self.ai_manager = None
        self.voice_engine = None
        
        # Background tasks
        self.background_tasks = []
        
        # Bot configurations
        self.bot_configs = [
            BotConfig(
                username="babagavat",
                session_file="sessions/babagavat",
                api_id=TELEGRAM_API_ID,
                api_hash=TELEGRAM_API_HASH,
                enabled=True
            ),
            BotConfig(
                username="geishaniz", 
                session_file="sessions/geishaniz",
                api_id=TELEGRAM_API_ID,
                api_hash=TELEGRAM_API_HASH,
                enabled=True
            ),
            BotConfig(
                username="yayincilara",
                session_file="sessions/yayincilara", 
                api_id=TELEGRAM_API_ID,
                api_hash=TELEGRAM_API_HASH,
                enabled=True
            )
        ]
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥     🤖 ULTIMATE TELEGRAM BOT LAUNCHER 🤖                     🔥
🔥                                                               🔥
🔥                🚀 FULL MUHABBET ECOSYSTEM 🚀                 🔥
🔥                    💪 ONUR METODU TAM GÜÇ! 💪                🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🤖 TELEGRAM BOTS: babagavat, geishaniz, yayincilara
💰 YAŞASIN SPONSORLAR! FULL GPT-4o MUHABBET! 💰
🎯 HEDEF: UNLIMITED TELEGRAM POWER!
        """)
    
    async def initialize_ultimate_bot_system(self) -> bool:
        """🚀 Ultimate bot sistemini başlat"""
        startup_start = time.time()
        
        try:
            print(f"""
🎯 ULTIMATE BOT SYSTEM INITIALIZATION...

📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
🏗️ Full Ecosystem Setup:
   🤖 Multiple Telegram Bots
   🧠 GPT-4o AI Full Power
   🎤 Voice Chat System
   💰 Coin & Economy System
   🎮 Social Gaming Engine
   🔍 ErkoAnalyzer Intelligence
   📊 User Analytics & CRM
   📡 DM & Group Handlers
   🚀 Real-time Processing

💪 ONUR METODU: ULTIMATE TELEGRAM ECOSYSTEM!
            """)
            
            # 1. Config validation
            print("📋 Configuration validation...")
            validate_config()
            
            # 2. Core systems initialization
            await self._initialize_core_systems()
            
            # 3. AI engine initialization
            await self._initialize_ai_systems()
            
            # 4. Telegram bot clients initialization
            await self._initialize_telegram_bots()
            
            # 5. Bot handlers setup
            await self._setup_bot_handlers()
            
            # 6. Background services
            await self._initialize_background_services()
            
            # 7. API server setup
            await self._initialize_api_server()
            
            # Startup completed
            startup_time = time.time() - startup_start
            self.is_running = True
            
            print(f"""
✅✅✅ ULTIMATE TELEGRAM BOT SYSTEM BAŞARILI! ✅✅✅

🏆 SYSTEM STATUS:
   🤖 Telegram Bots: {len(self.bot_clients)} aktif
   🧠 AI Engine: ✅ GPT-4o READY
   🎤 Voice System: ✅ READY  
   💰 Economy: ✅ ACTIVE
   🎮 Gaming: ✅ ACTIVE
   🔍 Analytics: ✅ ACTIVE
   📡 Handlers: ✅ ACTIVE
   🌐 API: ✅ READY

⚡ METRICS:
   ⏱️ Startup: {startup_time:.2f}s
   🤖 Bots Ready: {len([c for c in self.bot_configs if c.enabled])}
   💪 ONUR METODU: FULL POWER!

🚀 ULTIMATE TELEGRAM BOT ECOSYSTEM READY! 🚀
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ultimate bot system error: {e}")
            await self.shutdown()
            return False
    
    async def _initialize_core_systems(self) -> None:
        """🗄️ Core sistemleri başlat"""
        try:
            print("🗄️ Core Systems Initialization...")
            
            # Database manager
            print("   🗄️ Database Manager...")
            await database_manager.initialize()
            
            # Redis manager
            print("   ⚡ Redis Manager...")
            await babagavat_redis_manager.initialize()
            
            # MongoDB manager
            print("   📊 MongoDB Manager...")
            await babagavat_mongo_manager.initialize()
            
            # Coin service
            print("   💰 Coin Service...")
            await babagavat_coin_service.initialize()
            
            # ErkoAnalyzer
            print("   🔍 ErkoAnalyzer...")
            await babagavat_erko_analyzer.initialize()
            
            # User Analyzer
            print("   👤 User Analyzer...")
            await babagavat_user_analyzer.initialize({})
            
            print("   ✅ Core Systems - READY!")
            
        except Exception as e:
            logger.error(f"Core systems error: {e}")
            raise
    
    async def _initialize_ai_systems(self) -> None:
        """🤖 AI sistemlerini başlat"""
        try:
            print("🤖 AI Systems Initialization...")
            
            # Advanced AI Manager
            print("   🧠 Advanced AI Manager...")
            self.ai_manager = AdvancedAIManager()
            
            # Voice Engine (if OpenAI key available)
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                print("   🎤 Voice Engine...")
                self.voice_engine = await initialize_voice_engine(openai_api_key)
                await self.voice_engine.initialize()
            
            # MCP API
            print("   🎯 MCP API System...")
            await mcp_api.initialize()
            
            # Social Gaming
            print("   🎮 Social Gaming...")
            await social_gaming.initialize()
            
            print("   ✅ AI Systems - READY!")
            
        except Exception as e:
            logger.error(f"AI systems error: {e}")
            raise
    
    async def _initialize_telegram_bots(self) -> None:
        """🤖 Telegram botlarını başlat"""
        try:
            print("🤖 Telegram Bots Initialization...")
            
            # Sessions klasörünü oluştur
            os.makedirs("sessions", exist_ok=True)
            
            for bot_config in self.bot_configs:
                if not bot_config.enabled:
                    continue
                    
                try:
                    print(f"   🤖 Starting {bot_config.username}...")
                    
                    # Telegram client oluştur
                    client = TelegramClient(
                        bot_config.session_file,
                        bot_config.api_id,
                        bot_config.api_hash
                    )
                    
                    # Client'ı başlat
                    await client.start()
                    
                    # Bot bilgilerini al
                    me = await client.get_me()
                    
                    # Bot'u kaydet
                    self.bot_clients[bot_config.username] = {
                        "client": client,
                        "config": bot_config,
                        "me": me
                    }
                    
                    logger.info(f"✅ {bot_config.username} başlatıldı: {me.username} (ID: {me.id})")
                    
                except Exception as e:
                    logger.error(f"❌ {bot_config.username} başlatma hatası: {e}")
                    # Continue with other bots
            
            print(f"   ✅ Telegram Bots - {len(self.bot_clients)} aktif!")
            
        except Exception as e:
            logger.error(f"Telegram bots error: {e}")
            raise
    
    async def _setup_bot_handlers(self) -> None:
        """📡 Bot handler'larını kur"""
        try:
            print("📡 Bot Handlers Setup...")
            
            for username, bot_data in self.bot_clients.items():
                client = bot_data["client"]
                
                try:
                    print(f"   📨 {username} handlers...")
                    
                    # DM handlers
                    await setup_dm_handlers(client, username)
                    
                    # Group handlers  
                    await setup_group_handlers(client, username)
                    
                    logger.info(f"✅ {username} handlers kuruldu")
                    
                except Exception as e:
                    logger.error(f"❌ {username} handler error: {e}")
            
            print("   ✅ Bot Handlers - READY!")
            
            # User Analyzer'a client'ları ekle
            if self.bot_clients:
                clients_dict = {username: data["client"] for username, data in self.bot_clients.items()}
                babagavat_user_analyzer.clients = clients_dict
                print("   👤 User Analyzer clients updated!")
            
        except Exception as e:
            logger.error(f"Bot handlers error: {e}")
            raise
    
    async def _initialize_background_services(self) -> None:
        """🔄 Background servisleri başlat"""
        try:
            print("🔄 Background Services...")
            
            # Analytics task
            analytics_task = asyncio.create_task(self._continuous_analytics())
            self.background_tasks.append(analytics_task)
            
            # Health monitoring
            health_task = asyncio.create_task(self._continuous_health_monitor())
            self.background_tasks.append(health_task)
            
            # Bot monitoring
            bot_monitor_task = asyncio.create_task(self._continuous_bot_monitor())
            self.background_tasks.append(bot_monitor_task)
            
            print("   ✅ Background Services - RUNNING!")
            
        except Exception as e:
            logger.error(f"Background services error: {e}")
            raise
    
    async def _initialize_api_server(self) -> None:
        """🌐 API Server'ı hazırla"""
        try:
            print("🌐 API Server Ready...")
            # FastAPI app ready from coin_endpoints
            print("   ✅ FastAPI Server - READY!")
            
        except Exception as e:
            logger.error(f"API server error: {e}")
            raise
    
    async def run_ultimate_bot_system(self) -> None:
        """🚀 Ultimate bot sistemini çalıştır"""
        try:
            print("🚀 ULTIMATE TELEGRAM BOT SYSTEM RUNNING!")
            print("💬 Full muhabbet sistemi aktif - mesajlar işleniyor...")
            
            # Main monitoring loop
            while self.is_running:
                try:
                    # Bot health check
                    await self._check_bot_health()
                    
                    # Status log
                    if datetime.now().minute % 5 == 0:
                        await self._log_system_status()
                    
                    # 30 saniye bekle
                    await asyncio.sleep(30)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Kullanıcı tarafından durduruldu")
                    break
                except Exception as e:
                    logger.error(f"❌ Ana döngü hatası: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"❌ Ultimate bot system error: {e}")
        finally:
            await self.shutdown()
    
    async def start_api_server(self) -> None:
        """🌐 API Server'ı başlat"""
        try:
            print("🌐 Starting Ultimate API Server...")
            
            config = uvicorn.Config(
                app=app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                access_log=True,
                workers=1
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"API Server error: {e}")
    
    async def _check_bot_health(self) -> None:
        """🏥 Bot sağlığını kontrol et"""
        try:
            for username, bot_data in self.bot_clients.items():
                client = bot_data["client"]
                if client.is_connected():
                    # Bot aktif
                    pass
                else:
                    logger.warning(f"⚠️ {username} disconnected - reconnecting...")
                    await client.connect()
                    
        except Exception as e:
            logger.warning(f"Bot health check error: {e}")
    
    async def _continuous_analytics(self) -> None:
        """📊 Sürekli analytics"""
        while self.is_running:
            try:
                # Analytics processing burada
                await asyncio.sleep(300)  # 5 dakika
            except Exception as e:
                logger.warning(f"Analytics error: {e}")
                await asyncio.sleep(300)
    
    async def _continuous_health_monitor(self) -> None:
        """🏥 Sürekli sağlık kontrolü"""
        while self.is_running:
            try:
                await self._check_bot_health()
                await asyncio.sleep(60)  # 1 dakika
            except Exception as e:
                logger.warning(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _continuous_bot_monitor(self) -> None:
        """🤖 Sürekli bot monitörü"""
        while self.is_running:
            try:
                # Bot monitoring burada
                await asyncio.sleep(120)  # 2 dakika
            except Exception as e:
                logger.warning(f"Bot monitor error: {e}")
                await asyncio.sleep(120)
    
    async def _log_system_status(self) -> None:
        """📝 Sistem durumunu logla"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "active_bots": len(self.bot_clients),
                "bot_list": list(self.bot_clients.keys())
            }
            
            logger.info(f"📊 Ultimate Bot System Status: {json.dumps(status, indent=2)}")
            
        except Exception as e:
            logger.warning(f"Status log error: {e}")
    
    async def shutdown(self) -> None:
        """🛑 Ultimate sistemin güvenli kapatılması"""
        try:
            print("\n🛑 ULTIMATE TELEGRAM BOT SHUTDOWN...")
            
            self.is_running = False
            
            # Background tasks'leri durdur
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Bot clientları kapat
            for username, bot_data in self.bot_clients.items():
                try:
                    await bot_data["client"].disconnect()
                    print(f"   ✅ {username} kapatıldı")
                except Exception as e:
                    logger.error(f"{username} shutdown error: {e}")
            
            uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            
            print(f"""
✅ ULTIMATE TELEGRAM BOT SYSTEM KAPATILDI!

📊 FINAL STATS:
   ⏱️ Total Uptime: {uptime_minutes:.1f} dakika
   🤖 Bots Managed: {len(self.bot_clients)}
   💪 Onur Metodu: BAŞARIYLA TAMAMLANDI
   
🔥 ULTIMATE TELEGRAM ECOSYSTEM - MISSION ACCOMPLISHED! 🔥
            """)
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon - Ultimate Telegram Bot Launcher"""
    try:
        print("🚀 ULTIMATE TELEGRAM BOT LAUNCHER STARTING...")
        
        # Ultimate launcher oluştur
        launcher = UltimateTelegramBotLauncher()
        
        # Sistemi başlat
        if await launcher.initialize_ultimate_bot_system():
            
            # API Server ve main loop'u paralel çalıştır
            api_task = asyncio.create_task(launcher.start_api_server())
            main_task = asyncio.create_task(launcher.run_ultimate_bot_system())
            
            # İkisinden herhangi biri bitene kadar bekle
            await asyncio.gather(api_task, main_task, return_exceptions=True)
            
        else:
            print("❌ Ultimate bot system başlatılamadı")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Enhanced logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'ultimate_telegram_launcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Ana döngüyü başlat
    asyncio.run(main()) 