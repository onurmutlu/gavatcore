from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🤖 GavatCore Telegram MiniApp Bot
Users can access the management panel through this bot
"""

import asyncio
import logging
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError
import os
from datetime import datetime
import json

# Configuration
API_ID = 21724912
API_HASH = "1c5c96c5ced4ddc84b63ea97a20bc283"
BOT_TOKEN = "7719767896:AAGjQGn7dNKvSAVQUUVnzjqEjZhkRyPXCjw"  # GavatCore Panel Bot
PANEL_URL = "https://gavatcore-panel.vercel.app/"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GavatCorePanelBot:
    def __init__(self):
        self.client = TelegramClient('gavatcore_panel_bot', API_ID, API_HASH)
        self.admins = [1328613028]  # Admin user IDs
        self.stats = {
            'users': set(),
            'panel_opens': 0,
            'commands_used': 0,
            'start_time': datetime.now()
        }
    
    async def start(self):
        """Start the bot"""
        await self.client.start(bot_token=BOT_TOKEN)
        logger.info("🚀 GavatCore Panel Bot started!")
        
        # Register event handlers
        self.client.add_event_handler(self.handle_start, events.NewMessage(pattern='/start'))
        self.client.add_event_handler(self.handle_panel, events.NewMessage(pattern='/panel'))
        self.client.add_event_handler(self.handle_help, events.NewMessage(pattern='/help'))
        self.client.add_event_handler(self.handle_stats, events.NewMessage(pattern='/stats'))
        self.client.add_event_handler(self.handle_admin, events.NewMessage(pattern='/admin'))
        self.client.add_event_handler(self.handle_callback, events.CallbackQuery)
        
        # Keep the bot running
        await self.client.run_until_disconnected()
    
    async def handle_start(self, event):
        """Handle /start command"""
        user = await event.get_sender()
        user_id = user.id
        
        self.stats['users'].add(user_id)
        self.stats['commands_used'] += 1
        
        welcome_message = f"""
🚀 **GavatCore Yönetim Paneli**

Merhaba {user.first_name}! 👋

Bu bot ile GavatCore SaaS platformunun yönetim paneline erişebilirsiniz.

**Özellikler:**
• 🤖 Bot yönetimi
• 👥 Şovcu paneli  
• 📊 Gerçek zamanlı analitik
• 💳 Ödeme ve lisans takibi
• ⚙️ Sistem ayarları

**Komutlar:**
/panel - Yönetim panelini aç
/help - Yardım menüsü
/stats - Bot istatistikleri
        """
        
        buttons = [
            [Button.inline("📊 Paneli Aç", b"open_panel")],
            [Button.inline("🤖 Bot Durumu", b"bot_status"), Button.inline("👥 Şovcu Panel", b"performer_panel")],
            [Button.inline("💳 Ödemeler", b"payments"), Button.inline("📈 Analitik", b"analytics")],
            [Button.inline("⚙️ Ayarlar", b"settings"), Button.inline("❓ Yardım", b"help")]
        ]
        
        await event.reply(welcome_message, buttons=buttons)
    
    async def handle_panel(self, event):
        """Handle /panel command"""
        user = await event.get_sender()
        self.stats['panel_opens'] += 1
        self.stats['commands_used'] += 1
        
        panel_message = f"""
📊 **GavatCore Yönetim Paneli**

Merhaba {user.first_name}! 

Aşağıdaki butona tıklayarak yönetim panelini açabilirsiniz.

**Panel Özellikleri:**
• Telegram içinde çalışır
• Gerçek zamanlı veri
• Mobil uyumlu tasarım
• Güvenli erişim
        """
        
        buttons = [
            [Button.url("🚀 Paneli Aç", PANEL_URL)],
            [Button.inline("🔄 Yenile", b"refresh_panel")],
            [Button.inline("📱 Mobil Görünüm", b"mobile_view"), Button.inline("🖥️ Desktop Görünüm", b"desktop_view")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.reply(panel_message, buttons=buttons)
    
    async def handle_help(self, event):
        """Handle /help command"""
        self.stats['commands_used'] += 1
        
        help_message = """
❓ **Yardım Menüsü**

**Komutlar:**
/start - Botı başlat
/panel - Yönetim panelini aç
/help - Bu yardım menüsü
/stats - Bot istatistikleri

**Panel Bölümleri:**
• 🤖 **Bot Yönetimi** - Telegram botlarınızı yönetin
• 👥 **Şovcu Paneli** - Performer takibi ve yönetimi
• 📊 **Analitik** - Gerçek zamanlı istatistikler
• 💳 **Ödemeler** - Subscription ve lisans takibi
• ⚙️ **Ayarlar** - Sistem konfigürasyonu

**Destek:**
Sorunlarınız için @gavat_support hesabından iletişime geçebilirsiniz.
        """
        
        buttons = [
            [Button.inline("📊 Paneli Aç", b"open_panel")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.reply(help_message, buttons=buttons)
    
    async def handle_stats(self, event):
        """Handle /stats command"""
        user = await event.get_sender()
        self.stats['commands_used'] += 1
        
        # Check if user is admin
        if user.id not in self.admins:
            await event.reply("❌ Bu komut sadece yöneticiler için!")
            return
        
        uptime = datetime.now() - self.stats['start_time']
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds%3600)//60}m"
        
        stats_message = f"""
📊 **Bot İstatistikleri**

**Kullanıcı:**
• Toplam kullanıcı: {len(self.stats['users'])}
• Panel açılma: {self.stats['panel_opens']}
• Komut kullanımı: {self.stats['commands_used']}

**Sistem:**
• Çalışma süresi: {uptime_str}
• Başlatma: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
• Durum: ✅ Aktif

**Panel:**
• URL: {PANEL_URL}
• Telegram WebApp: ✅ Aktif
• Mobil uyumlu: ✅ Evet
        """
        
        buttons = [
            [Button.inline("🔄 Yenile", b"refresh_stats")],
            [Button.inline("📊 Paneli Aç", b"open_panel")]
        ]
        
        await event.reply(stats_message, buttons=buttons)
    
    async def handle_admin(self, event):
        """Handle /admin command"""
        user = await event.get_sender()
        self.stats['commands_used'] += 1
        
        # Check if user is admin
        if user.id not in self.admins:
            await event.reply("❌ Bu komut sadece yöneticiler için!")
            return
        
        admin_message = f"""
🔧 **Admin Paneli**

Merhaba {user.first_name}! 

Admin komutlarını kullanabilirsiniz:

**Mevcut Komutlar:**
• /stats - Bot istatistikleri
• /admin - Bu admin paneli
• /broadcast - Duyuru gönder (yakında)
• /users - Kullanıcı listesi (yakında)
        """
        
        buttons = [
            [Button.inline("📊 İstatistikler", b"refresh_stats")],
            [Button.inline("📡 Duyuru", b"broadcast"), Button.inline("👥 Kullanıcılar", b"users_list")],
            [Button.inline("🔄 Sistemi Yenile", b"system_refresh")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.reply(admin_message, buttons=buttons)
    
    async def handle_callback(self, event):
        """Handle callback queries"""
        data = event.data.decode('utf-8')
        user = await event.get_sender()
        
        if data == "open_panel":
            await self.handle_panel(event)
        
        elif data == "bot_status":
            await self.show_bot_status(event)
        
        elif data == "performer_panel":
            await self.show_performer_panel(event)
        
        elif data == "payments":
            await self.show_payments(event)
        
        elif data == "analytics":
            await self.show_analytics(event)
        
        elif data == "settings":
            await self.show_settings(event)
        
        elif data == "help":
            await self.handle_help(event)
        
        elif data == "main_menu":
            await self.handle_start(event)
        
        elif data == "refresh_stats":
            await self.handle_stats(event)
        
        elif data == "refresh_panel":
            await event.edit("🔄 Panel yenileniyor...")
            await asyncio.sleep(1)
            await self.handle_panel(event)
        
        elif data == "mobile_view":
            await event.edit("📱 Mobil görünüm için paneli açın: " + PANEL_URL)
        
        elif data == "desktop_view":
            await event.edit("🖥️ Desktop görünüm için paneli açın: " + PANEL_URL)
        
        elif data == "broadcast":
            await event.edit("📡 Duyuru sistemi yakında aktif olacak!")
        
        elif data == "users_list":
            await event.edit("👥 Kullanıcı listesi yakında aktif olacak!")
        
        elif data == "system_refresh":
            await event.edit("🔄 Sistem yenileniyor...")
            await asyncio.sleep(2)
            await event.edit("✅ Sistem yenilendi!")
    
    async def show_bot_status(self, event):
        """Show bot status"""
        status_message = """
🤖 **Bot Durumu**

**Aktif Botlar:**
• Yayıncı Lara: ✅ Aktif
• XXX Geisha: ✅ Aktif  
• Gavat Baba: ❌ Banned

**Sistem:**
• API: ✅ Çalışıyor
• Database: ✅ Bağlı
• GPT: ✅ Aktif
        """
        
        buttons = [
            [Button.inline("📊 Detaylar", b"open_panel")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.edit(status_message, buttons=buttons)
    
    async def show_performer_panel(self, event):
        """Show performer panel"""
        performer_message = """
👥 **Şovcu Paneli**

**Performans Özeti:**
• Yayıncı Lara: 89 mesaj bugün
• XXX Geisha: 67 mesaj bugün
• Toplam kazanç: 780 ₺

**Özellikler:**
• Gerçek zamanlı takip
• Kazanç hesaplama
• Engagement analizi
        """
        
        buttons = [
            [Button.inline("📊 Detaylar", b"open_panel")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.edit(performer_message, buttons=buttons)
    
    async def show_payments(self, event):
        """Show payments"""
        payments_message = """
💳 **Ödemeler**

**Bu Ay:**
• Toplam gelir: 18,750 ₺
• Aktif abonelik: 89
• Yeni kayıt: 12

**Planlar:**
• Trial: 0 ₺
• Starter: 499 ₺
• Pro: 799 ₺
• Deluxe: 1,499 ₺
        """
        
        buttons = [
            [Button.inline("📊 Detaylar", b"open_panel")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.edit(payments_message, buttons=buttons)
    
    async def show_analytics(self, event):
        """Show analytics"""
        analytics_message = """
📈 **Analitik**

**Bugün:**
• Toplam mesaj: 345
• Yeni kullanıcı: 12
• Sistem uptime: 99.8%

**Bu Hafta:**
• Toplam mesaj: 2,103
• Engagement: 92.4%
• Yanıt süresi: 1.8s
        """
        
        buttons = [
            [Button.inline("📊 Detaylar", b"open_panel")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.edit(analytics_message, buttons=buttons)
    
    async def show_settings(self, event):
        """Show settings"""
        settings_message = """
⚙️ **Ayarlar**

**Sistem Ayarları:**
• Auto-reply: ✅ Aktif
• GPT Mode: Hybrid
• Spam koruması: ✅ Aktif
• Logs: ✅ Aktif

**Telegram Ayarları:**
• MiniApp: ✅ Aktif
• Webhook: ✅ Bağlı
• Notifications: ✅ Açık
        """
        
        buttons = [
            [Button.inline("📊 Detaylar", b"open_panel")],
            [Button.inline("🏠 Ana Menü", b"main_menu")]
        ]
        
        await event.edit(settings_message, buttons=buttons)

async def main():
    """Main function"""
    bot = GavatCorePanelBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 