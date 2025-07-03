#!/usr/bin/env python3
"""
🏟️ Temiz Grup Bot - Patır patır mesaj, hata verenler otomatik listeden çıkar!
"""
import asyncio
import os
import sys
import random
import json
from datetime import datetime
from telethon import TelegramClient, events, errors

# Config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

# Random mesaj listesi
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

class TemizGrupBot:
    def __init__(self, session_path, bot_type):
        self.bot_type = bot_type
        self.session_path = session_path
        self.client = None
        self.mesajlar = BOT_MESAJLARI.get(bot_type, BOT_MESAJLARI["babagavat"])
        self.aktif_gruplar = []
        self.yasakli_gruplar = set()  # Hata veren grupları burada tutacağız
        self.blacklist_dosyasi = f"data/{bot_type}_blacklist.json"
        self.stats = {"gonderilen": 0, "hata": 0, "gruplar": 0}
        self.interval_min = 1  # min dakika
        self.interval_max = 5  # max dakika
        
    async def blacklist_yukle(self):
        """Yasaklı grup listesini yükle"""
        try:
            # Klasör yoksa oluştur
            os.makedirs("data", exist_ok=True)
            
            if os.path.exists(self.blacklist_dosyasi):
                with open(self.blacklist_dosyasi, "r") as f:
                    yasakli_idler = json.load(f)
                    self.yasakli_gruplar = set(yasakli_idler)
                print(f"📋 {len(self.yasakli_gruplar)} yasaklı grup yüklendi.")
        except Exception as e:
            print(f"⚠️ Blacklist yükleme hatası: {e}")
        
    async def blacklist_kaydet(self):
        """Yasaklı grup listesini kaydet"""
        try:
            with open(self.blacklist_dosyasi, "w") as f:
                json.dump(list(self.yasakli_gruplar), f)
        except Exception as e:
            print(f"⚠️ Blacklist kaydetme hatası: {e}")
        
    async def start(self):
        """Bot başlat"""
        print(f"🤖 {self.bot_type} başlatılıyor...")
        
        # Blacklist yükle
        await self.blacklist_yukle()
        
        # Client
        self.client = TelegramClient(
            self.session_path,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            print(f"✅ {self.bot_type} ({me.first_name}) aktif!")
            
            # Aktif grupları getir
            await self.gruplari_getir()
            return True
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")
            return False
    
    async def gruplari_getir(self):
        """Aktif grup listesini getir"""
        self.aktif_gruplar = []
        
        print(f"🔍 Gruplar aranıyor...")
        async for dialog in self.client.iter_dialogs():
            try:
                # Kanallar ve gruplar
                if dialog.is_group or dialog.is_channel:
                    # Blacklistte mi kontrol et
                    if dialog.id in self.yasakli_gruplar:
                        continue
                        
                    # Gruba ekle
                    self.aktif_gruplar.append({
                        "id": dialog.id,
                        "title": dialog.title,
                        "entity": dialog.entity
                    })
            except Exception as e:
                print(f"⚠️ Dialog hatası: {e}")
                
        self.stats["gruplar"] = len(self.aktif_gruplar)
        print(f"✅ {self.bot_type}: {len(self.aktif_gruplar)} aktif grup bulundu.")
    
    async def mesaj_gonderici(self):
        """Gruplara mesaj gönderen ana döngü"""
        if not self.aktif_gruplar:
            print("⚠️ Aktif grup bulunamadı!")
            return
            
        while True:
            try:
                # Random grup seç (aktif gruplar sürekli değişebilir)
                if not self.aktif_gruplar:
                    print("⚠️ Tüm gruplar yasaklandı! Gruplar yeniden aranıyor...")
                    await self.gruplari_getir()
                    if not self.aktif_gruplar:
                        print("❌ Hiç aktif grup kalmadı! Bekleniyor...")
                        await asyncio.sleep(600)  # 10 dakika bekle
                        continue
                
                # Random grup seç
                grup = random.choice(self.aktif_gruplar)
                
                # Random mesaj seç
                mesaj = random.choice(self.mesajlar)
                
                # Mesaj gönder
                try:
                    await self.client.send_message(grup["id"], mesaj)
                    self.stats["gonderilen"] += 1
                    print(f"✅ [{self.bot_type}] Grup: {grup['title']} - Mesaj: {mesaj}")
                    
                except errors.ChatAdminRequiredError:
                    print(f"🚫 [{self.bot_type}] Admin gerekli: {grup['title']}")
                    self.aktif_gruplar.remove(grup)
                    self.yasakli_gruplar.add(grup["id"])
                    self.stats["hata"] += 1
                    await self.blacklist_kaydet()
                    
                except errors.ChatWriteForbiddenError:
                    print(f"🚫 [{self.bot_type}] Yazma yasak: {grup['title']}")
                    self.aktif_gruplar.remove(grup)
                    self.yasakli_gruplar.add(grup["id"])
                    self.stats["hata"] += 1
                    await self.blacklist_kaydet()
                    
                except errors.UserBannedInChannelError:
                    print(f"🚫 [{self.bot_type}] Kanalda yasaklı: {grup['title']}")
                    self.aktif_gruplar.remove(grup)
                    self.yasakli_gruplar.add(grup["id"])
                    self.stats["hata"] += 1
                    await self.blacklist_kaydet()
                    
                except Exception as e:
                    print(f"❌ [{self.bot_type}] Mesaj hatası: {grup['title']} - {e}")
                    self.stats["hata"] += 1
                    if "Peer" in str(e) or "privileges" in str(e) or "can't" in str(e):
                        self.aktif_gruplar.remove(grup)
                        self.yasakli_gruplar.add(grup["id"])
                        await self.blacklist_kaydet()
                        print(f"👉 {grup['title']} yasaklı listeye eklendi.")
                
                # Random interval - 3-8 dakika
                dakika = random.randint(self.interval_min, self.interval_max)
                saniye = dakika * 60
                print(f"⏱️ {dakika} dakika bekleniyor...")
                print(f"📊 {self.bot_type} İstatistikler: {self.stats['gonderilen']} gönderilen, {self.stats['hata']} hata, {len(self.aktif_gruplar)}/{self.stats['gruplar']} aktif grup")
                
                await asyncio.sleep(saniye)
                
            except Exception as e:
                print(f"❌ Ana döngü hatası: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        """Bot çalıştır"""
        if not await self.start():
            return
            
        # Mesaj gönderici başlat
        print(f"🕒 {self.bot_type} mesaj gönderici başlıyor! ({self.interval_min}-{self.interval_max} dakika)")
        asyncio.create_task(self.mesaj_gonderici())
        
        # Client'ı çalışır tut
        await self.client.run_until_disconnected()
        
async def main():
    """Ana fonksiyon"""
    print("🚀 Temiz Grup Bot başlıyor...")
    print("🔥 PATIR PATIR MESAJLAR!")
    
    # Botlar
    botlar = [
        TemizGrupBot("sessions/babagavat_conversation.session", "babagavat"),
        TemizGrupBot("sessions/yayincilara_conversation.session", "yayincilara"),
        TemizGrupBot("sessions/xxxgeisha_conversation.session", "xxxgeisha")
    ]
    
    # Tüm botları başlat
    tasks = []
    for bot in botlar:
        task = asyncio.create_task(bot.run())
        tasks.append(task)
    
    # Tüm botları bekle
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        # Data klasörü oluştur
        os.makedirs("data", exist_ok=True)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Botlar durduruluyor...")
    except Exception as e:
        print(f"❌ Ana hata: {e}")
    finally:
        print("✅ Program kapatıldı") 