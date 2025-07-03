#!/usr/bin/env python3
"""
🏟️ Grup Mesaj Botu - 3-8 dakika aralıklarla random mesajlar!
"""
import asyncio
import os
import sys
import random
from datetime import datetime
from telethon import TelegramClient, events, types

# Config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

# Random mesaj listesi - her bot için ayrı
BOT_MESAJLARI = {
    "babagavat": [
        "Grup sessiz kalmış, neyse ki Baba Gavat burada! 😎",
        "Evlatlarım, bugün neler yapıyorsunuz? 🤔",
        "Bir hayat dersi vereyim: Asla vazgeçme! 💪",
        "Bu grupta en kral benim diyenler, bir adım öne çıksın 👑",
        "Biraz muhabbet açalım, haydi bakalım! 🍻",
        "Grup yatmış uyuyor mu yoksa? Uyanın! ⏰",
        "Hayat kısa, muhabbet uzun! 🌙",
        "Baba Gavat geldi, parti başlasın! 🎉",
        "Keşke herkes benim kadar cool olabilse 😌",
        "Naaber gençlik, bugün neler döndü? 👀"
    ],
    "yayincilara": [
        "CANLI YAYIN BAŞLIYOR DOSTLAR! 📱",
        "Kim bugün stream yapacak? 🎮",
        "Yeni içerik önerileri alayım 👾",
        "Chat çok hızlı akıyor! 📈",
        "Subscribe butonuna basmayı unutmayın! 🔔",
        "Kim oyun oynamak istiyor? 🎲",
        "Pre-order başladı haberiniz var mı? 🛒",
        "BÜYÜK DUYURU: Yeni koleksiyon çıkıyor! 💎",
        "Bugün kim kazandı turnuvayı? 🏆",
        "Yayıncılar ekibine katılmak isteyenler DM! 📨"
    ],
    "xxxgeisha": [
        "Huzur dolu bir gün diliyorum herkese 🌸",
        "Sanatın ve güzelliğin kalbi burada atıyor 🎭",
        "Ruhunuza iyi bakın, bedeniniz zaten takip eder ✨",
        "Bugün kendinize bir iyilik yapın 🧘‍♀️",
        "Geisha'nın bilgeliği: Her şeyi zamanında yapın 🕰️",
        "Güzellik detaylarda gizlidir 🌟",
        "İnsan ruhunun derinliklerini keşfetmek isteyenler? 🔮",
        "Zen felsefesi der ki: Anı yaşa ☯️",
        "Kimonom kadar zarif sözlerim var bugün 👘",
        "Mistik bir gece başlıyor... 🌙"
    ]
}

class GrupMesajBotu:
    def __init__(self, session_path, bot_type):
        self.client = None
        self.bot_type = bot_type
        self.session_path = session_path
        self.gruplar = []
        self.is_running = False
        self.random_interval = True  # 3-8 dakika arası
        self.mesajlar = BOT_MESAJLARI.get(bot_type, BOT_MESAJLARI["babagavat"])
        
    async def start(self):
        """Bot başlat"""
        print(f"🤖 {self.bot_type} başlatılıyor...")
        
        self.client = TelegramClient(
            self.session_path,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            
            print(f"✅ {self.bot_type} ({me.first_name}) aktif!")
            
            # Tüm dialog'ları tara ve grupları bul
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    self.gruplar.append({
                        "id": dialog.id,
                        "title": dialog.title,
                        "entity": dialog.entity
                    })
            
            print(f"🏟️ {len(self.gruplar)} grup bulundu!")
            return True
            
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")
            return False
    
    async def random_mesaj_gonder(self):
        """3-8 dakika aralıklarla random mesaj gönder"""
        if not self.gruplar:
            print("⚠️ Hiç grup bulunamadı!")
            return
        
        self.is_running = True
        while self.is_running:
            try:
                # Random grup seç
                grup = random.choice(self.gruplar)
                
                # Random mesaj seç
                mesaj = random.choice(self.mesajlar)
                
                # Mesaj gönder
                await self.client.send_message(grup["id"], mesaj)
                print(f"✅ [{self.bot_type}] Grup: {grup['title']} - Mesaj: {mesaj}")
                
                # 3-8 dakika arası bekle
                dakika = random.randint(3, 8)
                saniye = dakika * 60
                print(f"⏱️ {dakika} dakika bekleniyor...")
                
                await asyncio.sleep(saniye)
                
            except Exception as e:
                print(f"❌ Mesaj hatası: {e}")
                await asyncio.sleep(60)  # Hata durumunda 1 dakika bekle
    
    async def normal_mesajlari_dinle(self):
        """Normal mesajları dinle ve cevap ver"""
        @self.client.on(events.NewMessage())
        async def handler(event):
            try:
                # Kendimizin mesajlarına cevap verme
                if event.out:
                    return
                
                # Özel mesajlara cevap ver
                if event.is_private:
                    sender = await event.get_sender()
                    if not sender.bot:
                        await asyncio.sleep(random.uniform(1, 3))
                        await event.respond(f"Merhaba! Ben bir grup mesaj botuyum. Gruplarda aktifim!")
                
            except Exception as e:
                print(f"❌ Mesaj işleme hatası: {e}")
    
    async def run(self):
        """Tüm fonksiyonları çalıştır"""
        if not await self.start():
            return False
        
        # Normal mesajları dinle
        await self.normal_mesajlari_dinle()
        
        # Random mesaj task'ı başlat
        print(f"🕒 Random mesaj gönderme başlıyor! (3-8 dakika aralıklarla)")
        asyncio.create_task(self.random_mesaj_gonder())
        
        # Bot'u çalışır halde tut
        await self.client.run_until_disconnected()

async def main():
    """Ana fonksiyon"""
    # Bot listesi
    botlar = [
        GrupMesajBotu("sessions/babagavat_conversation.session", "babagavat"),
        GrupMesajBotu("sessions/yayincilara_conversation.session", "yayincilara"),
        GrupMesajBotu("sessions/xxxgeisha_conversation.session", "xxxgeisha")
    ]
    
    print("🚀 Grup Mesaj Botu başlıyor...")
    print("🔥 3-8 DAKİKA ARALIKLARLA RANDOM MESAJLAR!")
    
    # Tüm botları başlat
    tasks = []
    for bot in botlar:
        task = asyncio.create_task(bot.run())
        tasks.append(task)
    
    # Tüm botların çalışmasını bekle
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Botlar durduruluyor...")
    except Exception as e:
        print(f"❌ Ana hata: {e}")
    finally:
        print("✅ Program kapatıldı") 