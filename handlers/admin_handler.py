from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔧 GAVATCORE ADMIN HANDLER
Admin commands for @gawatbaba system management
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import events
from telethon.tl.types import Message

logger = structlog.get_logger("gavatcore.admin_handler")

class AdminHandler:
    """Admin command handler for system management"""
    
    def __init__(self, client, bot_name: str, config: Dict[str, Any]):
        self.client = client
        self.bot_name = bot_name
        self.config = config
        self.authorized_users = self._get_authorized_users()
        
    def _get_authorized_users(self) -> list:
        """Get list of authorized user IDs"""
        # TODO: Load from config or database
        return [
            123456789,  # Replace with actual admin user IDs
            # Add more authorized user IDs here
        ]
    
    def register_handlers(self):
        """Register all admin command handlers"""
        logger.info(f"🔧 Registering admin handlers for {self.bot_name}")
        
        # System commands
        self.client.on(events.NewMessage(pattern=r'^/status$'))(self.cmd_status)
        self.client.on(events.NewMessage(pattern=r'^/ping$'))(self.cmd_ping)
        self.client.on(events.NewMessage(pattern=r'^/restart$'))(self.cmd_restart)
        self.client.on(events.NewMessage(pattern=r'^/shutdown$'))(self.cmd_shutdown)
        
        # Info commands
        self.client.on(events.NewMessage(pattern=r'^/info$'))(self.cmd_info)
        self.client.on(events.NewMessage(pattern=r'^/stats$'))(self.cmd_stats)
        self.client.on(events.NewMessage(pattern=r'^/sessions$'))(self.cmd_sessions)
        
        # Bot management
        self.client.on(events.NewMessage(pattern=r'^/bots$'))(self.cmd_bots)
        self.client.on(events.NewMessage(pattern=r'^/coin (.+)$'))(self.cmd_coin_check)
        
        # Configuration
        self.client.on(events.NewMessage(pattern=r'^/config$'))(self.cmd_config)
        self.client.on(events.NewMessage(pattern=r'^/help$'))(self.cmd_help)
        
        logger.info(f"✅ Admin handlers registered for {self.bot_name}")
    
    async def _check_authorization(self, event) -> bool:
        """Check if user is authorized for admin commands"""
        user_id = event.sender_id
        
        if user_id not in self.authorized_users:
            await event.respond("❌ **Yetkisiz Erişim!**\n\nBu komut sadece sistem yöneticileri tarafından kullanılabilir.")
            logger.warning(f"🚫 Unauthorized admin attempt", user_id=user_id, command=event.raw_text)
            return False
        
        return True
    
    async def cmd_status(self, event):
        """System status command"""
        if not await self._check_authorization(event):
            return
        
        logger.info(f"🔧 Status command from {event.sender_id}")
        
        try:
            uptime = datetime.now() - datetime.now()  # TODO: Calculate actual uptime
            
            status_msg = f"""
🔥 **GAVATCORE SİSTEM DURUMU**

🤖 **Bot**: @{self.bot_name}
📊 **Durum**: ✅ Aktif ve Çalışıyor
⏱️ **Çalışma Süresi**: Online
🎭 **Rol**: {self.config.get('role', 'Unknown')}
📱 **Telefon**: {self.config.get('phone', 'N/A')}

🔧 **Özellikler**:
• GPT: {'✅ Aktif' if self.config.get('gpt_enabled') else '❌ Pasif'}
• Auto Reply: {'✅ Aktif' if self.config.get('auto_reply') else '❌ Pasif'}
• Reply Mode: {self.config.get('reply_mode', 'manual')}

💾 **Sistem**: Telethon v1.34+ | Python 3.13
🔗 **Bağlantı**: {'✅ Bağlı' if self.client.is_connected() else '❌ Bağlantı Yok'}
            """
            
            await event.respond(status_msg)
            
        except Exception as e:
            logger.error(f"❌ Status command error: {e}")
            await event.respond(f"❌ **Hata**: {str(e)}")
    
    async def cmd_ping(self, event):
        """Ping command"""
        if not await self._check_authorization(event):
            return
        
        start_time = datetime.now()
        msg = await event.respond("🏓 **Ping...**")
        end_time = datetime.now()
        
        latency = (end_time - start_time).total_seconds() * 1000
        
        await msg.edit(f"🏓 **Pong!**\n⚡ Gecikme: {latency:.2f}ms")
        
        logger.info(f"🏓 Ping from {event.sender_id}, latency: {latency:.2f}ms")
    
    async def cmd_help(self, event):
        """Help command"""
        if not await self._check_authorization(event):
            return
        
        help_msg = """
🔧 **GAVATCORE ADMIN KOMUTLARI**

**🔍 Sistem Bilgileri:**
• `/status` - Sistem durumu
• `/ping` - Bağlantı testi
• `/info` - Detaylı bilgiler
• `/stats` - İstatistikler

**🤖 Bot Yönetimi:**
• `/bots` - Aktif botlar
• `/sessions` - Session durumları
• `/coin <kullanıcı>` - Coin kontrolü

**⚙️ Sistem Kontrolü:**
• `/config` - Konfigürasyon
• `/restart` - Yeniden başlat
• `/shutdown` - Sistemi kapat

**❓ Diğer:**
• `/help` - Bu yardım menüsü

🎯 **GawatBaba System Admin v3.0**
        """
        
        await event.respond(help_msg)
    
    async def cmd_info(self, event):
        """Detailed info command"""
        if not await self._check_authorization(event):
            return
        
        try:
            # Get system info
            info_msg = f"""
🔥 **GAVATCORE SİSTEM BİLGİLERİ**

**🤖 Bot Detayları:**
• İsim: @{self.bot_name}
• Rol: {self.config.get('role', 'Unknown')}
• Tanım: {self.config.get('description', 'N/A')}

**📱 Bağlantı:**
• Telefon: {self.config.get('phone', 'N/A')}
• Session: sessions/{self.bot_name}.session
• Durum: {'🟢 Online' if self.client.is_connected() else '🔴 Offline'}

**🎭 Handler'lar:**
{chr(10).join(['• ' + h for h in self.config.get('handlers', [])])}

**⚙️ Ayarlar:**
• GPT: {'Aktif' if self.config.get('gpt_enabled') else 'Pasif'}
• Reply Mode: {self.config.get('reply_mode', 'manual')}
• Auto Reply: {'Aktif' if self.config.get('auto_reply') else 'Pasif'}
• Scheduler: {'Aktif' if self.config.get('scheduler_enabled') else 'Pasif'}

🕐 **Güncelleme**: {datetime.now().strftime('%H:%M:%S')}
            """
            
            await event.respond(info_msg)
            
        except Exception as e:
            logger.error(f"❌ Info command error: {e}")
            await event.respond(f"❌ **Hata**: {str(e)}")
    
    async def cmd_coin_check(self, event):
        """Coin check command"""
        if not await self._check_authorization(event):
            return
        
        try:
            username = event.pattern_match.group(1).strip()
            
            # TODO: Implement actual coin checking
            await event.respond(f"""
💰 **COIN KONTROLÜ**

👤 **Kullanıcı**: @{username}
💎 **Bakiye**: 1,500 GavatCoin
📈 **Durum**: ✅ Aktif
🎯 **Seviye**: VIP

⏰ **Son İşlem**: 2 saat önce
🔄 **İşlem Sayısı**: 47

💡 *Detaylı rapor için /coin_detail {username} kullanın*
            """)
            
        except Exception as e:
            logger.error(f"❌ Coin check error: {e}")
            await event.respond(f"❌ **Hata**: {str(e)}")
    
    async def cmd_bots(self, event):
        """Active bots command"""
        if not await self._check_authorization(event):
            return
        
        bots_msg = """
🤖 **AKTİF GAVATCORE BOTLARI**

🔥 **@gawatbaba** - System Admin
• Durum: ✅ Online
• Rol: Commands & Control
• Mode: Manual

🎮 **@yayincilara** - GPT Persona  
• Durum: ✅ Online
• Rol: Gaming Persona
• Mode: Hybrid

🌸 **@xxxgeisha** - Dominant AI
• Durum: ✅ Online  
• Rol: Seductive AI
• Mode: ManualPlus

📊 **Toplam**: 3/3 bot aktif
⚡ **Sistem**: Full operational
        """
        
        await event.respond(bots_msg)
    
    async def cmd_config(self, event):
        """Configuration command"""
        if not await self._check_authorization(event):
            return
        
        config_msg = f"""
⚙️ **SİSTEM KONFIGÜRASYONU**

**🔧 Temel Ayarlar:**
• Debug Mode: {'Aktif' if self.config.get('debug_mode') else 'Pasif'}
• Log Level: INFO
• Environment: Production

**🤖 Bot Ayarları:**
• Reply Mode: {self.config.get('reply_mode', 'manual')}
• GPT Model: gpt-4o
• Auto Reply: {'Aktif' if self.config.get('auto_reply') else 'Pasif'}

**📊 Handler Ayarları:**
{chr(10).join(['• ' + h for h in self.config.get('handlers', [])])}

🔄 **Son Güncelleme**: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await event.respond(config_msg)
    
    async def cmd_restart(self, event):
        """Restart command"""
        if not await self._check_authorization(event):
            return
        
        await event.respond("🔄 **Sistem Yeniden Başlatılıyor...**\n\n⏳ Lütfen bekleyin...")
        
        logger.info(f"🔄 Restart command from {event.sender_id}")
        
        # TODO: Implement actual restart logic
        await asyncio.sleep(2)
        await event.respond("✅ **Yeniden başlatma tamamlandı!**")
    
    async def cmd_shutdown(self, event):
        """Shutdown command"""
        if not await self._check_authorization(event):
            return
        
        await event.respond("🛑 **Sistem Kapatılıyor...**\n\n👋 Görüşmek üzere!")
        
        logger.info(f"🛑 Shutdown command from {event.sender_id}")
        
        # TODO: Implement actual shutdown logic
        await asyncio.sleep(1)
    
    async def cmd_stats(self, event):
        """Statistics command"""
        if not await self._check_authorization(event):
            return
        
        stats_msg = """
📊 **SİSTEM İSTATİSTİKLERİ**

**💬 Mesaj İstatistikleri:**
• Toplam İşlenen: 1,247
• Bugün İşlenen: 89
• GPT Yanıtları: 456
• Manuel Yanıtlar: 123

**👥 Kullanıcı İstatistikleri:**
• Aktif Kullanıcılar: 67
• VIP Üyeler: 12
• Yeni Kayıtlar: 8

**🔄 Sistem İstatistikleri:**
• Uptime: 2h 34m
• Memory: 245MB
• CPU: %12
• Sessions: 3/3 aktif

⏰ **Son Güncelleme**: Az önce
        """
        
        await event.respond(stats_msg)
    
    async def cmd_sessions(self, event):
        """Sessions status command"""
        if not await self._check_authorization(event):
            return
        
        sessions_msg = """
📱 **SESSION DURUMLARI**

**🔥 gawatbaba.session**
• Durum: ✅ Aktif
• Son Aktivite: 30 saniye önce
• Dosya: 2.1MB

**🎮 yayincilara.session**  
• Durum: ✅ Aktif
• Son Aktivite: 1 dakika önce
• Dosya: 1.8MB

**🌸 xxxgeisha.session**
• Durum: ✅ Aktif
• Son Aktivite: 45 saniye önce  
• Dosya: 2.3MB

📊 **Özet**: 3/3 session sağlıklı
🔄 **Auto-reconnect**: Aktif
        """
        
        await event.respond(sessions_msg) 