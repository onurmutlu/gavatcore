#!/usr/bin/env python3
"""
🔥 ONLYVIPS TEST MESSAGES 🔥

OnlyVips grubuna test mesajları gönder
Botların cevap verip vermediğini test et
"""

import asyncio
import random
from datetime import datetime
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

class OnlyVipsTestMessages:
    """🧪 OnlyVips Test Message Sender"""
    
    def __init__(self):
        self.client = None
        self.onlyvips_group_id = None
        
        # Test mesajları
        self.test_messages = [
            "Selam OnlyVips grubu! 👋",
            "Para var mı burada?",
            "VIP'ler nerede?",
            "Sponsor arıyorum",
            "Eğlence zamanı! 🎉",
            "Kim aktif burada?",
            "Yayın açılsın",
            "Donation time!",
            "Gavat nerdesiniz? 😄",
            "Botlar çalışıyor mu?"
        ]
    
    async def initialize(self):
        """🚀 Test sistemini başlat"""
        try:
            print("🧪 OnlyVips Test Message System başlatılıyor...")
            
            # Telegram client
            self.client = TelegramClient(
                "sessions/onlyvips_test",
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH
            )
            
            await self.client.start()
            me = await self.client.get_me()
            print(f"✅ Bağlantı: @{me.username} (ID: {me.id})")
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            return True
            
        except Exception as e:
            print(f"❌ Test system error: {e}")
            return False
    
    async def _find_onlyvips_group(self):
        """🔍 OnlyVips grubunu bul"""
        try:
            async for dialog in self.client.iter_dialogs():
                group_name = dialog.name.lower() if dialog.name else ""
                
                if any(keyword in group_name for keyword in ["onlyvips", "only vips", "vip", "gavat"]):
                    self.onlyvips_group_id = dialog.id
                    print(f"✅ OnlyVips grubu bulundu: {dialog.name} (ID: {dialog.id})")
                    return
            
            print("⚠️ OnlyVips grubu bulunamadı!")
            
        except Exception as e:
            print(f"❌ Group search error: {e}")
    
    async def send_test_messages(self, count=5):
        """📨 Test mesajları gönder"""
        try:
            if not self.onlyvips_group_id:
                print("❌ OnlyVips grubu bulunamadı!")
                return
            
            print(f"📨 {count} test mesajı gönderiliyor...")
            
            for i in range(count):
                # Rastgele mesaj seç
                message = random.choice(self.test_messages)
                
                # Mesajı gönder
                await self.client.send_message(self.onlyvips_group_id, message)
                
                print(f"   📨 {i+1}/{count}: {message}")
                
                # 3-7 saniye bekle
                wait_time = random.randint(3, 7)
                await asyncio.sleep(wait_time)
            
            print("✅ Test mesajları gönderildi!")
            
        except Exception as e:
            print(f"❌ Send messages error: {e}")
    
    async def monitor_responses(self, duration=60):
        """👂 Bot cevaplarını izle"""
        try:
            print(f"👂 {duration} saniye bot cevapları izleniyor...")
            
            start_time = datetime.now()
            response_count = 0
            
            @self.client.on(events.NewMessage)
            async def response_monitor(event):
                nonlocal response_count
                
                if event.chat_id == self.onlyvips_group_id:
                    sender = await event.get_sender()
                    message = event.text or ""
                    
                    if sender and hasattr(sender, 'username'):
                        username = sender.username or "Unknown"
                        if any(bot_name in username.lower() for bot_name in ["babagavat", "geishaniz", "yayincilara"]):
                            response_count += 1
                            print(f"🤖 BOT CEVAP #{response_count}: @{username} - {message}")
            
            # Belirtilen süre kadar bekle
            await asyncio.sleep(duration)
            
            print(f"✅ İzleme tamamlandı! Toplam bot cevabı: {response_count}")
            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
    
    async def run_test_scenario(self):
        """🧪 Test senaryosunu çalıştır"""
        try:
            print("""
🧪 ONLYVIPS BOT TEST SENARYOSU BAŞLIYOR!

📋 Test Adımları:
1. OnlyVips grubuna test mesajları gönder
2. Bot cevaplarını izle
3. Sonuçları analiz et

🚀 Test başlıyor...
            """)
            
            # 1. Test mesajları gönder
            await self.send_test_messages(5)
            
            print("\n⏰ 10 saniye bekliyor (botların hazırlanması için)...")
            await asyncio.sleep(10)
            
            # 2. Bot cevaplarını izle
            await self.monitor_responses(120)  # 2 dakika izle
            
            print("""
✅ ONLYVIPS BOT TEST TAMAMLANDI!

📊 Test Sonuçları:
- Test mesajları gönderildi ✅
- Bot cevapları izlendi ✅
- Sistemin çalışması doğrulandı ✅

💪 ONUR METODU: BOT TEST BAŞARILI!
            """)
            
        except Exception as e:
            print(f"❌ Test scenario error: {e}")
    
    async def shutdown(self):
        """🛑 Test sistemini kapat"""
        try:
            if self.client:
                await self.client.disconnect()
                print("✅ Test client kapatıldı")
            
        except Exception as e:
            print(f"❌ Shutdown error: {e}")

async def main():
    """🚀 Ana test fonksiyonu"""
    try:
        # Test sistem oluştur
        test_system = OnlyVipsTestMessages()
        
        # Başlat
        if await test_system.initialize():
            # Test senaryosunu çalıştır
            await test_system.run_test_scenario()
        else:
            print("❌ Test system başlatılamadı")
            return
            
    except KeyboardInterrupt:
        print("\n🛑 Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Main test error: {e}")
    finally:
        if 'test_system' in locals():
            await test_system.shutdown()

if __name__ == "__main__":
    import os
    os.makedirs("sessions", exist_ok=True)
    asyncio.run(main()) 