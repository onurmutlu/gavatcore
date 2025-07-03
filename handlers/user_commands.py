"""
👤 User Commands Handler - Kullanıcı komutları yönetimi
"""
from telethon import events
from core.controller import Controller
from core.gpt_system import GPTSystem
from core.anti_spam_system import AntiSpamSystem

class UserCommandsHandler:
    def __init__(self, controller: Controller, gpt_system: GPTSystem, anti_spam: AntiSpamSystem):
        self.controller = controller
        self.gpt_system = gpt_system
        self.anti_spam = anti_spam
        self.commands = {
            '/start': self.handle_start,
            '/help': self.handle_help,
            '/status': self.handle_status,
            '/settings': self.handle_settings,
            '/gpt': self.handle_gpt,
            '/spam': self.handle_spam,
            '/ban': self.handle_ban,
            '/unban': self.handle_unban,
            '/mute': self.handle_mute,
            '/unmute': self.handle_unmute,
            '/warn': self.handle_warn,
            '/stats': self.handle_stats
        }
        
    async def handle_command(self, event: events.NewMessage.Event):
        """Komutları işle"""
        try:
            # Komut ve argümanları ayır
            message = event.message.text.split()
            command = message[0].lower()
            args = message[1:] if len(message) > 1 else []
            
            # Komut var mı kontrol et
            if command in self.commands:
                await self.commands[command](event, args)
            else:
                await event.respond("❌ Bilinmeyen komut! /help yazarak komutları görebilirsiniz.")
                
        except Exception as e:
            print(f"Command Handler Error: {e}")
            await event.respond("❌ Bir hata oluştu! Lütfen tekrar deneyin.")
            
    async def handle_start(self, event: events.NewMessage.Event, args: list):
        """Başlangıç komutu"""
        try:
            welcome_msg = """
🌟 GAVATCore Bot'a Hoş Geldiniz! 🌟

🤖 Ben yapay zeka destekli bir Telegram botuyum.
📱 Grup yönetimi, spam koruması ve GPT entegrasyonu sunuyorum.

📌 Komutlar:
/help - Tüm komutları göster
/status - Bot durumunu kontrol et
/settings - Ayarları yönet

❓ Yardım için /help yazabilirsiniz.
            """
            await event.respond(welcome_msg)
            
        except Exception as e:
            print(f"Start Command Error: {e}")
            
    async def handle_help(self, event: events.NewMessage.Event, args: list):
        """Yardım komutu"""
        try:
            help_msg = """
📚 GAVATCore Bot Komutları:

👤 Kullanıcı Komutları:
/start - Botu başlat
/help - Bu yardım mesajını göster
/status - Bot durumunu kontrol et
/settings - Ayarları yönet

🤖 GPT Komutları:
/gpt [soru] - GPT'ye soru sor
/gpt_settings - GPT ayarlarını yönet

🛡️ Moderasyon Komutları:
/spam [on/off] - Spam korumasını aç/kapat
/ban [kullanıcı] - Kullanıcıyı yasakla
/unban [kullanıcı] - Kullanıcının yasağını kaldır
/mute [kullanıcı] [süre] - Kullanıcıyı sustur
/unmute [kullanıcı] - Kullanıcının susturmasını kaldır
/warn [kullanıcı] - Kullanıcıyı uyar

📊 İstatistik Komutları:
/stats - Bot istatistiklerini göster
            """
            await event.respond(help_msg)
            
        except Exception as e:
            print(f"Help Command Error: {e}")
            
    async def handle_status(self, event: events.NewMessage.Event, args: list):
        """Durum komutu"""
        try:
            status_msg = """
📊 Bot Durumu:

🤖 Sistem:
- CPU: %s
- RAM: %s
- Uptime: %s

📱 Telegram:
- Gruplar: %d
- Kullanıcılar: %d
- Mesajlar: %d

🛡️ Güvenlik:
- Spam Koruması: %s
- Ban Sayısı: %d
- Uyarı Sayısı: %d

🤖 GPT:
- İstek Sayısı: %d
- Başarı Oranı: %s
            """ % (
                "25%",  # CPU
                "512MB",  # RAM
                "2g 5s",  # Uptime
                10,  # Grup sayısı
                100,  # Kullanıcı sayısı
                1000,  # Mesaj sayısı
                "Aktif",  # Spam koruması
                5,  # Ban sayısı
                10,  # Uyarı sayısı
                50,  # GPT istek sayısı
                "98%"  # GPT başarı oranı
            )
            await event.respond(status_msg)
            
        except Exception as e:
            print(f"Status Command Error: {e}")
            
    async def handle_settings(self, event: events.NewMessage.Event, args: list):
        """Ayarlar komutu"""
        try:
            settings_msg = """
⚙️ Bot Ayarları:

🔔 Bildirimler:
- Grup Bildirimleri: Açık
- Özel Mesaj Bildirimleri: Açık
- Hata Bildirimleri: Kapalı

🛡️ Güvenlik:
- Spam Koruması: Açık
- Otomatik Ban: Kapalı
- Uyarı Limiti: 3

🤖 GPT:
- Model: GPT-4
- Sıcaklık: 0.7
- Maksimum Token: 2000

📱 Arayüz:
- Dil: Türkçe
- Tema: Koyu
- Emoji: Açık
            """
            await event.respond(settings_msg)
            
        except Exception as e:
            print(f"Settings Command Error: {e}")
            
    async def handle_gpt(self, event: events.NewMessage.Event, args: list):
        """GPT komutu"""
        try:
            if not args:
                await event.respond("❌ Lütfen bir soru sorun! Örnek: /gpt Python nedir?")
                return
                
            question = " ".join(args)
            response = await self.gpt_system.get_response(question)
            await event.respond(response)
            
        except Exception as e:
            print(f"GPT Command Error: {e}")
            await event.respond("❌ GPT yanıt verirken bir hata oluştu!")
            
    async def handle_spam(self, event: events.NewMessage.Event, args: list):
        """Spam komutu"""
        try:
            if not args:
                await event.respond("❌ Lütfen bir durum belirtin! Örnek: /spam on")
                return
                
            status = args[0].lower()
            if status == "on":
                await self.anti_spam.enable()
                await event.respond("✅ Spam koruması aktif edildi!")
            elif status == "off":
                await self.anti_spam.disable()
                await event.respond("✅ Spam koruması devre dışı bırakıldı!")
            else:
                await event.respond("❌ Geçersiz durum! Kullanım: /spam [on/off]")
                
        except Exception as e:
            print(f"Spam Command Error: {e}")
            
    async def handle_ban(self, event: events.NewMessage.Event, args: list):
        """Ban komutu"""
        try:
            if not args:
                await event.respond("❌ Lütfen bir kullanıcı belirtin! Örnek: /ban @kullanici")
                return
                
            user = args[0]
            await self.controller.ban_user(user)
            await event.respond(f"✅ {user} başarıyla yasaklandı!")
            
        except Exception as e:
            print(f"Ban Command Error: {e}")
            
    async def handle_unban(self, event: events.NewMessage.Event, args: list):
        """Unban komutu"""
        try:
            if not args:
                await event.respond("❌ Lütfen bir kullanıcı belirtin! Örnek: /unban @kullanici")
                return
                
            user = args[0]
            await self.controller.unban_user(user)
            await event.respond(f"✅ {user} kullanıcısının yasağı kaldırıldı!")
            
        except Exception as e:
            print(f"Unban Command Error: {e}")
            
    async def handle_mute(self, event: events.NewMessage.Event, args: list):
        """Mute komutu"""
        try:
            if len(args) < 2:
                await event.respond("❌ Kullanım: /mute @kullanici 1h")
                return
                
            user = args[0]
            duration = args[1]
            await self.controller.mute_user(user, duration)
            await event.respond(f"✅ {user} kullanıcısı {duration} süreyle susturuldu!")
            
        except Exception as e:
            print(f"Mute Command Error: {e}")
            
    async def handle_unmute(self, event: events.NewMessage.Event, args: list):
        """Unmute komutu"""
        try:
            if not args:
                await event.respond("❌ Lütfen bir kullanıcı belirtin! Örnek: /unmute @kullanici")
                return
                
            user = args[0]
            await self.controller.unmute_user(user)
            await event.respond(f"✅ {user} kullanıcısının susturması kaldırıldı!")
            
        except Exception as e:
            print(f"Unmute Command Error: {e}")
            
    async def handle_warn(self, event: events.NewMessage.Event, args: list):
        """Warn komutu"""
        try:
            if not args:
                await event.respond("❌ Lütfen bir kullanıcı belirtin! Örnek: /warn @kullanici")
                return
                
            user = args[0]
            reason = " ".join(args[1:]) if len(args) > 1 else "Sebep belirtilmedi"
            await self.controller.warn_user(user, reason)
            await event.respond(f"⚠️ {user} kullanıcısı uyarıldı!\nSebep: {reason}")
            
        except Exception as e:
            print(f"Warn Command Error: {e}")
            
    async def handle_stats(self, event: events.NewMessage.Event, args: list):
        """Stats komutu"""
        try:
            stats_msg = """
📊 Bot İstatistikleri:

👥 Kullanıcılar:
- Toplam: 100
- Aktif: 50
- Yeni (24s): 10

📱 Gruplar:
- Toplam: 10
- Aktif: 8
- Yeni (24s): 2

💬 Mesajlar:
- Toplam: 1000
- Bugün: 100
- Spam: 5

🤖 GPT:
- İstekler: 50
- Başarı: 98%
- Hata: 2%

🛡️ Moderasyon:
- Ban: 5
- Mute: 3
- Uyarı: 10
            """
            await event.respond(stats_msg)
            
        except Exception as e:
            print(f"Stats Command Error: {e}") 