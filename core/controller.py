# core/controller.py

import asyncio
import os
import logging
from telethon import TelegramClient, events
from core.gavat_client import GavatClient
from handlers.dm_handler import handle_message, handle_inline_bank_choice
from core.smart_campaign_manager import smart_campaign_manager
from core.crm_database import crm_db
from core.onboarding_flow import (
    start_onboarding,
    handle_onboarding_callback,
    handle_onboarding_text
)
from core.license_checker import LicenseChecker
from core.profile_loader import load_profile
from utils.scheduler_utils import spam_loop

SESSIONS_DIR = "sessions"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gavatcore.controller")

# Global client registry
active_clients = {}  # {username: client}

def get_client_by_username(username: str):
    """Username'e göre client'ı getir"""
    return active_clients.get(username)

async def launch_all_sessions():
    # SQLite session dosyalarını kullan
    session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    clients = []
    spam_tasks = []  # Spam task'lerini sakla

    for session_file in session_files:
        session_path = os.path.join(SESSIONS_DIR, session_file)
        username = session_file.replace(".session", "")
        try:
            # SQLite session ile GavatClient kullan
            from core.gavat_client import SafeSQLiteSession
            from telethon import TelegramClient
            from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
            
            safe_session = SafeSQLiteSession(session_path)
            client_obj = TelegramClient(
                safe_session,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                connection_retries=3,
                retry_delay=10,
                timeout=30,
                request_retries=2,
                flood_sleep_threshold=60*60,
                auto_reconnect=True,
                sequential_updates=True
            )
            
            # Wrapper object oluştur
            class ClientWrapper:
                def __init__(self, client, username):
                    self.client = client
                    self.username = username
                
                async def start(self):
                    try:
                        await self.client.connect()
                        if not await self.client.is_user_authorized():
                            logger.error(f"Client yetkilendirilmemiş: {self.username}")
                            return False
                        me = await self.client.get_me()
                        self.username = me.username or f"user_{me.id}"
                        logger.info(f"[{self.username}] başarıyla başlatıldı - User: {me.first_name}")
                        return True
                    except Exception as e:
                        logger.error(f"Client başlatma hatası: {e}")
                        return False
                
                async def run(self):
                    try:
                        if not await self.start():
                            return
                        logger.info(f"[{self.username}] çalışıyor...")
                        await self.client.run_until_disconnected()
                    except Exception as e:
                        logger.error(f"Client çalışma hatası: {e}")
                    finally:
                        if self.client and self.client.is_connected():
                            await self.client.disconnect()
                
                async def disconnect(self):
                    try:
                        if self.client and self.client.is_connected():
                            await self.client.disconnect()
                            logger.info(f"[{self.username}] bağlantı kapatıldı")
                    except Exception as e:
                        logger.warning(f"Disconnect hatası: {e}")
            
            client = ClientWrapper(client_obj, username)
            
            # Client'ı başlat
            if not await client.start():
                logger.error(f"[controller] {session_file} başlatılamadı")
                continue
                
            logger.info(f"[controller] {session_file} bağlı.")
            
            # Client'ı registry'ye ekle
            active_clients[client.username] = client.client

            # DM ve onboarding event handler
            @client.client.on(events.NewMessage(incoming=True))
            async def unified_message_handler(event):
                try:
                    # Client username'i al
                    client_username = username  # Bu scope'tan username'i al
                    
                    if event.is_private:
                        logger.info(f"🔍 PRIVATE MESSAGE YAKALANDI: '{event.raw_text}'")
                        # Sender cache'den al, yoksa çek
                        sender = event.sender
                        if sender is None:
                            try:
                                sender = await event.get_sender()
                            except Exception as e:
                                logger.warning(f"[handler] Sender alınamadı: {e}")
                                return
                        if sender is None:
                            logger.warning(f"[handler] Private message sender None geldi")
                            return
                        user_id = sender.id
                        # Bot profilinden created_at bilgisini al
                        try:
                            me = await client.client.get_me()
                            bot_user_id = me.id
                            # Bot profilini yükle
                            import json
                            from pathlib import Path
                            profile_path = Path(f"data/personas/{username}.json")
                            session_created_at = None
                            if profile_path.exists():
                                with open(profile_path, "r", encoding="utf-8") as f:
                                    profile = json.load(f)
                                    created_at_str = profile.get("created_at")
                                    if created_at_str:
                                        from datetime import datetime
                                        session_created_at = datetime.fromisoformat(created_at_str)
                            if session_created_at is None:
                                from datetime import datetime
                                session_created_at = datetime.now()
                        except Exception:
                            from datetime import datetime
                            session_created_at = datetime.now()
                        
                        await handle_onboarding_text(event)
                        await handle_message(client.client, sender, event.raw_text, session_created_at)
                    elif event.is_group:
                        # Grup mesajları için handler
                        from handlers.group_handler import handle_group_message
                        await handle_group_message(event, client.client)
                except Exception as e:
                    logger.error(f"[handler] Event hatası: {e}")

            @client.client.on(events.CallbackQuery)
            async def unified_callback_handler(event):
                try:
                    await handle_inline_bank_choice(event)
                    await handle_onboarding_callback(event)
                except Exception as e:
                    logger.error(f"[handler] CallbackQuery hatası: {e}")

            # Manuel müdahale tespiti için outgoing message handler (DEVRE DIŞI)
            # NOT: Bu handler her otomatik mesajı manuel olarak algıladığı için devre dışı bırakıldı
            # Manuel müdahale tespiti şimdilik DM handler içinde yapılıyor
            
            # @client.client.on(events.NewMessage(outgoing=True))
            # async def manual_intervention_handler(event):
            #     # Bu handler geçici olarak devre dışı - otomatik mesajları manuel olarak algılıyor
            #     pass

            # Spam task'i sadece autospam aktifse başlat
            try:
                # Direkt JSON dosyasından yükle
                import json
                from pathlib import Path
                profile_path = Path(f"data/personas/{username}.json")
                logger.info(f"🔍 {username} için profil yükleniyor: {profile_path}")
                profile = None
                if profile_path.exists():
                    with open(profile_path, "r", encoding="utf-8") as f:
                        profile = json.load(f)
                    logger.info(f"📄 {username} profil yüklendi, autospam: {profile.get('autospam')}")
                else:
                    logger.warning(f"❌ {username} profil dosyası bulunamadı: {profile_path}")
                
                # Spam loop'u aktif et
                if profile and profile.get('autospam', False):
                    spam_task = asyncio.create_task(spam_loop(client.client))
                    spam_tasks.append(spam_task)
                    logger.info(f"🔥 {username} için spam loop başlatıldı")
                else:
                    logger.info(f"[controller] {username} için spam loop devre dışı (autospam: False)")
            except Exception as e:
                logger.error(f"[controller] {username} profil yükleme hatası: {e}")
                print(f"💥 {username} profil yükleme hatası: {e}")

            logger.info(f"[controller] {session_file} başlatıldı.")
            clients.append(client)
        except Exception as e:
            logger.error(f"[controller] {session_file} başlatılamadı: {e}")

    if not clients:
        logger.error("[controller] Hiçbir client başlatılamadı. Çıkılıyor.")
        return

    # Cleanup task'larını başlat
    cleanup_tasks = []
    
    # DM handler cleanup task'ını başlat
    try:
        from handlers.dm_handler import dm_cooldown_cleanup_task
        dm_cleanup_task = asyncio.create_task(dm_cooldown_cleanup_task())
        cleanup_tasks.append(dm_cleanup_task)
        logger.info("🧹 DM handler cooldown cleanup task başlatıldı")
    except Exception as e:
        logger.warning(f"DM cleanup task başlatılamadı: {e}")
    
    # Grup handler cleanup task'ını başlat (eğer varsa)
    try:
        from handlers.group_handler import cooldown_cleanup_task
        group_cleanup_task = asyncio.create_task(cooldown_cleanup_task())
        cleanup_tasks.append(group_cleanup_task)
        logger.info("🧹 Grup handler cooldown cleanup task başlatıldı")
    except Exception as e:
        logger.warning(f"Grup cleanup task başlatılamadı: {e}")
    
    # Paket yöneticisini başlat
    from core.package_manager import package_manager
    logger.info("📦 Paket yönetim sistemi hazır")
    
    # CRM, Segmentasyon ve Dinamik Gönderim sistemlerini başlat (sadece Enterprise paketler için)
    enterprise_clients = []
    for client in clients:
        try:
            me = await client.client.get_me()
            user_id = me.id
            
            # Paket kontrolü
            from core.package_manager import PackageType
            user_package = package_manager.get_user_package(user_id)
            
            if user_package == PackageType.ENTERPRISE:
                enterprise_clients.append({
                    "client": client,
                    "username": client.username,
                    "user_id": user_id
                })
                logger.info(f"🏢 {client.username} Enterprise pakette")
            else:
                logger.info(f"📦 {client.username} Basic pakette")
        except Exception as e:
            logger.error(f"❌ Paket kontrolü hatası {client.username}: {e}")
    
    if enterprise_clients:
        try:
            # Enterprise özelliklerini başlat
            from core.dynamic_delivery_optimizer import delivery_optimizer
            await delivery_optimizer.start_optimizer()
            logger.info("🚀 Dinamik gönderim optimizer başlatıldı (Enterprise)")
            
            # Segmentasyon sistemini başlat
            from core.user_segmentation import user_segmentation
            logger.info("🎯 Kullanıcı segmentasyon sistemi hazır (Enterprise)")
            
            # İlk segmentasyon analizi
            segment_performance = await user_segmentation.analyze_segment_performance()
            logger.info(f"📊 İlk segment analizi tamamlandı: {len(segment_performance.get('segment_stats', {}))} segment")
            
            # Smart campaign manager
            await smart_campaign_manager.start_campaign_manager()
            logger.info("🎯 Akıllı kampanya yöneticisi başlatıldı (Enterprise)")
            
            logger.info(f"✅ Enterprise özellikler {len(enterprise_clients)} kullanıcı için aktif")
        except Exception as e:
            logger.error(f"❌ Enterprise sistemleri başlatma hatası: {e}")
    else:
        logger.info("ℹ️ Enterprise kullanıcı yok, CRM sistemleri başlatılmadı")
    
    # Tüm client'lar ve spam task'leri paralel çalışsın
    try:
        # Client run() fonksiyonları, spam task'leri ve cleanup task'larını birleştir
        all_tasks = [c.run() for c in clients] + spam_tasks + cleanup_tasks
        logger.info(f"🚀 Toplam {len(clients)} client, {len(spam_tasks)} spam task ve {len(cleanup_tasks)} cleanup task başlatılıyor...")
        logger.info(f"🎯 CRM & Kampanya yöneticisi aktif")
        await asyncio.gather(*all_tasks)
    except Exception as e:
        logger.error(f"[controller] Client çalıştırma toplu hatası: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(launch_all_sessions())
    except Exception as e:
        logger.critical(f"[controller] Fatal error: {e}")
        print(f"[controller] Fatal error: {e}")
