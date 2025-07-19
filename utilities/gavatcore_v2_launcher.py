from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 GavatCore V2 - Next Generation AI Social Gaming Platform
AI Voice, Real-time Interaction, Quest System, Social Gaming

Bu launcher tüm yeni sistemleri entegre eder:
- MCP API System (Modüler karakter ve görev yönetimi)
- AI Voice Engine (GPT-4o + Whisper)
- Social Gaming Engine (Topluluk etkinlikleri)
- Real-time Voice Chat
- Quest & XP System
- Leaderboards & Badges
"""

import asyncio
import os
import sys
import signal
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import structlog

# Core V2 imports
from core.mcp_api_system import mcp_api
from core.ai_voice_engine import initialize_voice_engine, voice_engine
from core.social_gaming_engine import social_gaming
from core.telegram_broadcaster import telegram_broadcaster

# Legacy imports (mevcut sistem ile uyumluluk)
from handlers.dm_handler import setup_dm_handlers
from handlers.group_handler import setup_group_handlers
from core.session_manager import get_active_sessions
from core.integrated_optimizer import start_integrated_optimization, BAMGUM_CONFIG

logger = structlog.get_logger("gavatcore.v2_launcher")

class GavatCoreV2:
    """GavatCore V2 - Next Generation Platform"""
    
    def __init__(self):
        self.is_running = False
        self.startup_time = None
        self.clients = {}
        
        # V2 Systems
        self.mcp_api = mcp_api
        self.voice_engine = None
        self.social_gaming = social_gaming
        
        # Performance metrics
        self.v2_metrics = {
            "startup_time": 0,
            "voice_sessions": 0,
            "social_events": 0,
            "quests_completed": 0,
            "xp_distributed": 0,
            "tokens_distributed": 0,
            "active_users": 0,
            "character_interactions": 0
        }
        
        logger.info("🚀 GavatCore V2 başlatılıyor...")
    
    async def initialize(self) -> bool:
        """Tüm sistemleri başlat"""
        startup_start = time.time()
        
        try:
            logger.info("🎮 GavatCore V2 - Next Generation Platform")
            logger.info("=" * 60)
            
            # 1. MCP API System başlat
            logger.info("🔧 MCP API Sistemi başlatılıyor...")
            await self.mcp_api.initialize()
            
            # 2. AI Voice Engine başlat
            logger.info("🎤 AI Voice Engine başlatılıyor...")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.warning("⚠️ OPENAI_API_KEY bulunamadı, voice özellikler devre dışı")
                self.voice_engine = None
            else:
                self.voice_engine = await initialize_voice_engine(openai_api_key)
            
            # 3. Social Gaming Engine başlat
            logger.info("🎯 Social Gaming Engine başlatılıyor...")
            await self.social_gaming.initialize()
            
            # 4. Legacy bot sistemini başlat (mevcut kullanıcılar için)
            logger.info("🤖 Legacy bot sistemi başlatılıyor...")
            await self._initialize_legacy_bots()
            
            # 5. Telegram Broadcaster başlat
            logger.info("📢 Telegram Broadcaster başlatılıyor...")
            await self._initialize_telegram_broadcaster()
            
            # 6. Event handlers kurulumu
            logger.info("⚙️ Event handlers kurulumu...")
            await self._setup_event_handlers()
            
            # 7. Background tasks başlat
            logger.info("🔄 Background tasks başlatılıyor...")
            await self._start_background_tasks()
            
            # 8. Shutdown handlers
            self._register_shutdown_handlers()
            
            # Startup metrics
            self.startup_time = time.time() - startup_start
            self.v2_metrics["startup_time"] = self.startup_time
            self.is_running = True
            
            logger.info("=" * 60)
            logger.info("✅ GavatCore V2 başarıyla başlatıldı!")
            logger.info(f"⏱️ Başlatma süresi: {self.startup_time:.2f} saniye")
            logger.info(f"🎤 Voice Engine: {'✅ Aktif' if self.voice_engine else '❌ Devre dışı'}")
            logger.info(f"🎮 Social Gaming: ✅ Aktif")
            logger.info(f"🎯 Quest System: ✅ Aktif")
            logger.info(f"🤖 Bot Count: {len(self.clients)}")
            logger.info("=" * 60)
            
            # Başlangıç bildirimi
            await self._send_startup_notification()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ GavatCore V2 başlatma hatası: {e}")
            await self.shutdown()
            return False
    
    async def run(self) -> None:
        """Ana çalışma döngüsü"""
        try:
            logger.info("🚀 GavatCore V2 çalışıyor...")
            
            # Ana monitoring döngüsü
            while self.is_running:
                await self._update_metrics()
                await self._health_check()
                await asyncio.sleep(30)  # 30 saniyede bir kontrol
                
        except KeyboardInterrupt:
            logger.info("🛑 Kullanıcı tarafından durduruldu")
        except Exception as e:
            logger.error(f"❌ Ana döngü hatası: {e}")
        finally:
            await self.shutdown()
    
    # ==================== VOICE FEATURES ====================
    
    async def start_voice_session(self, user_id: str, character_id: str) -> Optional[str]:
        """Sesli sohbet oturumu başlat"""
        if not self.voice_engine:
            logger.warning("Voice engine aktif değil")
            return None
        
        try:
            session_id = await self.voice_engine.start_voice_session(user_id, character_id)
            self.v2_metrics["voice_sessions"] += 1
            
            logger.info(f"🎤 Sesli oturum başlatıldı: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Sesli oturum başlatma hatası: {e}")
            return None
    
    async def process_voice_message(self, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Sesli mesaj işle"""
        if not self.voice_engine:
            return {"success": False, "error": "Voice engine aktif değil"}
        
        try:
            result = await self.voice_engine.process_voice_interaction(audio_data, session_id)
            if result.get("success"):
                self.v2_metrics["character_interactions"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Sesli mesaj işleme hatası: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== SOCIAL FEATURES ====================
    
    async def create_social_event(self, title: str, description: str, character_id: str, event_type: str = "voice_party") -> str:
        """Sosyal etkinlik oluştur"""
        try:
            from core.social_gaming_engine import SocialEvent, EventType
            
            event = SocialEvent(
                event_id=f"event_{int(time.time())}",
                title=title,
                description=description,
                event_type=EventType(event_type),
                host_character_id=character_id,
                max_participants=20,
                rewards=[
                    {"type": "xp", "amount": 100},
                    {"type": "token", "amount": 50}
                ]
            )
            
            await self.social_gaming.create_social_event(event)
            self.v2_metrics["social_events"] += 1
            
            logger.info(f"🎉 Sosyal etkinlik oluşturuldu: {title}")
            return event.event_id
            
        except Exception as e:
            logger.error(f"❌ Sosyal etkinlik oluşturma hatası: {e}")
            raise
    
    async def join_social_event(self, event_id: str, user_id: str) -> Dict[str, Any]:
        """Sosyal etkinliğe katıl"""
        try:
            result = await self.social_gaming.join_event(event_id, user_id)
            return result
            
        except Exception as e:
            logger.error(f"❌ Sosyal etkinliğe katılma hatası: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== QUEST FEATURES ====================
    
    async def assign_daily_quests(self, user_id: str) -> List[str]:
        """Günlük görevleri ata"""
        try:
            assigned_quests = []
            
            # Günlük sohbet görevi
            if await self.mcp_api.assign_quest_to_user("daily_chat", user_id):
                assigned_quests.append("daily_chat")
            
            # Sesli etkileşim görevi (voice engine aktifse)
            if self.voice_engine and await self.mcp_api.assign_quest_to_user("voice_interaction", user_id):
                assigned_quests.append("voice_interaction")
            
            logger.info(f"📋 Günlük görevler atandı: {user_id} -> {assigned_quests}")
            return assigned_quests
            
        except Exception as e:
            logger.error(f"❌ Günlük görev atama hatası: {e}")
            return []
    
    async def complete_quest(self, quest_id: str, user_id: str) -> Dict[str, Any]:
        """Görevi tamamla"""
        try:
            result = await self.mcp_api.complete_quest(quest_id, user_id)
            if result.get("success"):
                self.v2_metrics["quests_completed"] += 1
                self.v2_metrics["xp_distributed"] += result.get("total_xp", 0)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Görev tamamlama hatası: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== USER MANAGEMENT ====================
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcı dashboard bilgilerini al"""
        try:
            # User progress
            user_progress = await self.mcp_api.get_user_progress(user_id)
            if not user_progress:
                # Yeni kullanıcı oluştur
                await self.mcp_api.add_xp(user_id, 0)  # Bu otomatik user oluşturur
                user_progress = await self.mcp_api.get_user_progress(user_id)
            
            # Active quests
            active_quests = await self.mcp_api.get_active_quests_for_user(user_id)
            
            # Leaderboard position
            leaderboard = await self.mcp_api.get_leaderboard(100)
            user_rank = None
            for i, entry in enumerate(leaderboard):
                if entry["user_id"] == user_id:
                    user_rank = i + 1
                    break
            
            # Voice stats (eğer voice engine aktifse)
            voice_stats = {}
            if self.voice_engine:
                voice_stats = await self.voice_engine.get_user_voice_stats(user_id)
            
            dashboard = {
                "user_progress": {
                    "level": user_progress.level,
                    "total_xp": user_progress.total_xp,
                    "tokens": user_progress.tokens,
                    "badges": user_progress.badges,
                    "completed_quests_count": len(user_progress.completed_quests)
                },
                "active_quests": [
                    {
                        "id": quest.id,
                        "title": quest.title,
                        "description": quest.description,
                        "quest_type": quest.quest_type.value
                    } for quest in active_quests
                ],
                "leaderboard_rank": user_rank,
                "voice_stats": voice_stats,
                "character_relationships": user_progress.character_relationships
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ User dashboard hatası: {e}")
            return {}
    
    # ==================== PRIVATE METHODS ====================
    
    async def _initialize_legacy_bots(self) -> None:
        """Legacy bot sistemini başlat"""
        try:
            # Mevcut session'ları al
            sessions = await get_active_sessions()
            
            if not sessions:
                logger.warning("⚠️ Aktif session bulunamadı")
                return
            
            # Bot client'larını başlat (basitleştirilmiş)
            from telethon import TelegramClient
            
            for username, session_data in sessions.items():
                try:
                    client = TelegramClient(
                        session_data["session_file"],
                        session_data["api_id"],
                        session_data["api_hash"]
                    )
                    
                    await client.connect()
                    
                    if await client.is_user_authorized():
                        self.clients[username] = {
                            "client": client,
                            "session_data": session_data
                        }
                        
                        # V2 handlers setup
                        await self._setup_v2_handlers(client, username)
                        
                        logger.info(f"✅ Legacy bot başlatıldı: {username}")
                    else:
                        await client.disconnect()
                        
                except Exception as e:
                    logger.error(f"❌ Legacy bot başlatma hatası ({username}): {e}")
            
        except Exception as e:
            logger.error(f"❌ Legacy bot sistemi başlatma hatası: {e}")
    
    async def _initialize_telegram_broadcaster(self) -> None:
        """Telegram Broadcaster'ı başlat"""
        try:
            # Client'ları broadcaster'a ver
            client_dict = {}
            for username, bot_data in self.clients.items():
                client_dict[username] = bot_data["client"]
            
            # Hedef grupları belirle (config'den alınacak)
            target_groups = []
            # Örnek: Aktif grupları otomatik tespit et
            for username, bot_data in self.clients.items():
                try:
                    client = bot_data["client"]
                    # Bu kısım gerçek grup ID'leri ile güncellenecek
                    # Test için manuel grup ekleme (gerçek grup ID'si gerekli)
                    # Şimdilik boş liste ile test ediyoruz
                    # Log'lardan aktif grup ID'lerini kullanabiliriz
                    # test_group_ids = [
                    #     -1002607016335,  # Log'lardan görülen aktif grup
                    #     # -1001686321334,  # Başka bir aktif grup
                    # ]
                    # target_groups.extend(test_group_ids)
                    
                    pass
                except Exception as e:
                    logger.warning(f"⚠️ Grup tespiti hatası ({username}): {e}")
            
            # Şimdilik broadcast'i devre dışı bırakıyoruz (grup erişim sorunu)
            logger.info(f"📢 Hedef grup sayısı: {len(target_groups)} (broadcast devre dışı)")
            
            # Broadcaster'ı başlat
            await telegram_broadcaster.initialize(client_dict, target_groups)
            
            logger.info("✅ Telegram Broadcaster hazır")
            
        except Exception as e:
            logger.error(f"❌ Telegram Broadcaster başlatma hatası: {e}")
    
    async def _setup_v2_handlers(self, client, username: str) -> None:
        """V2 event handlers kurulumu"""
        try:
            # Legacy handlers
            await setup_dm_handlers(client, username)
            await setup_group_handlers(client, username)
            
            # V2 specific handlers burada eklenecek
            # Örnek: voice command handlers, quest handlers, etc.
            
        except Exception as e:
            logger.error(f"❌ V2 handlers kurulum hatası ({username}): {e}")
    
    async def _setup_event_handlers(self) -> None:
        """Event handlers kurulumu"""
        try:
            # MCP API events
            self.mcp_api.on("quest_completed", self._on_quest_completed)
            self.mcp_api.on("level_up", self._on_level_up)
            self.mcp_api.on("badge_earned", self._on_badge_earned)
            
            # Voice engine events (eğer aktifse)
            if self.voice_engine:
                self.voice_engine.on("voice_session_started", self._on_voice_session_started)
                self.voice_engine.on("voice_interaction_processed", self._on_voice_interaction)
            
            # Social gaming events
            self.social_gaming.on("event_created", self._on_social_event_created)
            
            logger.info("✅ Event handlers kuruldu")
            
        except Exception as e:
            logger.error(f"❌ Event handlers kurulum hatası: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Background tasks başlat"""
        try:
            # Metrics güncelleme
            asyncio.create_task(self._metrics_update_loop())
            
            # Daily quest assignment
            asyncio.create_task(self._daily_quest_loop())
            
            # System health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            logger.info("✅ Background tasks başlatıldı")
            
        except Exception as e:
            logger.error(f"❌ Background tasks başlatma hatası: {e}")
    
    async def _metrics_update_loop(self) -> None:
        """Metrics güncelleme döngüsü"""
        while self.is_running:
            try:
                await self._update_metrics()
                await asyncio.sleep(60)  # 1 dakikada bir
            except Exception as e:
                logger.error(f"❌ Metrics güncelleme hatası: {e}")
                await asyncio.sleep(60)
    
    async def _daily_quest_loop(self) -> None:
        """Günlük görev atama döngüsü"""
        while self.is_running:
            try:
                # Her gün saat 00:00'da çalışacak şekilde ayarlanacak
                # Şimdilik basit implementation
                await asyncio.sleep(3600)  # 1 saatte bir kontrol
            except Exception as e:
                logger.error(f"❌ Daily quest loop hatası: {e}")
                await asyncio.sleep(3600)
    
    async def _health_monitoring_loop(self) -> None:
        """Sistem sağlık izleme döngüsü"""
        while self.is_running:
            try:
                await self._health_check()
                await asyncio.sleep(300)  # 5 dakikada bir
            except Exception as e:
                logger.error(f"❌ Health monitoring hatası: {e}")
                await asyncio.sleep(300)
    
    async def _update_metrics(self) -> None:
        """Metrics güncelle"""
        try:
            # MCP API stats
            mcp_stats = self.mcp_api.system_stats
            self.v2_metrics.update({
                "active_users": mcp_stats.get("total_users", 0),
                "quests_completed": mcp_stats.get("completed_quests", 0),
                "xp_distributed": mcp_stats.get("total_xp_distributed", 0),
                "tokens_distributed": mcp_stats.get("total_tokens_distributed", 0)
            })
            
            # Voice engine stats
            if self.voice_engine:
                self.v2_metrics["voice_sessions"] = len(self.voice_engine.active_sessions)
            
        except Exception as e:
            logger.error(f"❌ Metrics güncelleme hatası: {e}")
    
    async def _health_check(self) -> None:
        """Sistem sağlık kontrolü"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - (self.startup_time or time.time()),
                "mcp_api_healthy": bool(self.mcp_api),
                "voice_engine_healthy": bool(self.voice_engine),
                "social_gaming_healthy": bool(self.social_gaming),
                "active_bots": len(self.clients),
                "metrics": self.v2_metrics
            }
            
            # Log health status
            if health_status["uptime_seconds"] % 3600 < 60:  # Her saatte bir log
                logger.info(f"💚 Sistem sağlık durumu: {health_status}")
            
        except Exception as e:
            logger.error(f"❌ Health check hatası: {e}")
    
    # ==================== EVENT HANDLERS ====================
    
    async def _on_quest_completed(self, data: Dict[str, Any]) -> None:
        """Quest tamamlandığında"""
        logger.info(f"🎯 Quest tamamlandı: {data}")
        # Telegram broadcast
        await telegram_broadcaster.broadcast_quest_completed(data)
    
    async def _on_level_up(self, data: Dict[str, Any]) -> None:
        """Level atlandığında"""
        logger.info(f"⬆️ Level up: {data}")
        # Telegram broadcast
        await telegram_broadcaster.broadcast_level_up(data)
    
    async def _on_badge_earned(self, data: Dict[str, Any]) -> None:
        """Badge kazanıldığında"""
        logger.info(f"🏆 Badge kazanıldı: {data}")
        # Telegram broadcast
        await telegram_broadcaster.broadcast_badge_earned(data)
    
    async def _on_voice_session_started(self, data: Dict[str, Any]) -> None:
        """Voice session başladığında"""
        logger.info(f"🎤 Voice session başladı: {data}")
        # Telegram broadcast
        await telegram_broadcaster.broadcast_voice_session(data)
    
    async def _on_voice_interaction(self, data: Dict[str, Any]) -> None:
        """Voice interaction işlendiğinde"""
        logger.info(f"🗣️ Voice interaction: {data}")
    
    async def _on_social_event_created(self, data: Dict[str, Any]) -> None:
        """Sosyal etkinlik oluşturulduğunda"""
        logger.info(f"🎉 Sosyal etkinlik oluşturuldu: {data}")
        # Telegram broadcast
        await telegram_broadcaster.broadcast_social_event(data)
    
    async def _send_startup_notification(self) -> None:
        """Başlangıç bildirimi gönder"""
        try:
            # Telegram gruplarına bildirim gönderilecek
            startup_message = f"""
🚀 **GavatCore V2 Başlatıldı!**

✅ Yeni özellikler aktif:
🎤 AI Voice Chat (GPT-4o + Whisper)
🎮 Social Gaming & Events
🎯 Quest & XP System
🏆 Leaderboards & Badges
💬 Real-time Community

⏱️ Başlatma süresi: {self.startup_time:.2f}s
🤖 Aktif bot sayısı: {len(self.clients)}

Yeni deneyimi keşfetmeye hazır mısınız? 🔥
            """
            
            logger.info("📢 Startup notification hazırlandı")
            
        except Exception as e:
            logger.error(f"❌ Startup notification hatası: {e}")
    
    def _register_shutdown_handlers(self) -> None:
        """Shutdown handlers kaydet"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Signal alındı: {signum}")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self) -> None:
        """Sistemi kapat"""
        try:
            logger.info("🛑 GavatCore V2 kapatılıyor...")
            
            self.is_running = False
            
            # Voice sessions kapat
            if self.voice_engine:
                for session_id in list(self.voice_engine.active_sessions.keys()):
                    await self.voice_engine.end_voice_session(session_id)
            
            # Bot clients kapat
            for username, bot_data in self.clients.items():
                try:
                    await bot_data["client"].disconnect()
                    logger.info(f"✅ Bot kapatıldı: {username}")
                except Exception as e:
                    logger.error(f"❌ Bot kapatma hatası ({username}): {e}")
            
            # Final metrics
            await self._update_metrics()
            
            logger.info("✅ GavatCore V2 başarıyla kapatıldı")
            
        except Exception as e:
            logger.error(f"❌ Shutdown hatası: {e}")

async def main():
    """Ana fonksiyon"""
    try:
        # GavatCore V2 başlat
        gavatcore_v2 = GavatCoreV2()
        
        if await gavatcore_v2.initialize():
            await gavatcore_v2.run()
        else:
            logger.error("❌ GavatCore V2 başlatılamadı")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Ana fonksiyon hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # ASCII Art Banner
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗  █████╗ ██╗   ██╗ █████╗ ████████╗ ██████╗ ██████╗ ║
    ║  ██╔════╝ ██╔══██╗██║   ██║██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗║
    ║  ██║  ███╗███████║██║   ██║███████║   ██║   ██║     ██║   ██║║
    ║  ██║   ██║██╔══██║╚██╗ ██╔╝██╔══██║   ██║   ██║     ██║   ██║║
    ║  ╚██████╔╝██║  ██║ ╚████╔╝ ██║  ██║   ██║   ╚██████╗╚██████╔╝║
    ║   ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ║
    ║                                                               ║
    ║                        VERSION 2.0                           ║
    ║              Next Generation AI Social Gaming                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    🚀 AI Voice Chat | 🎮 Social Gaming | 🎯 Quest System | 🏆 Leaderboards
    """)
    
    # Ana döngüyü başlat
    asyncio.run(main()) 