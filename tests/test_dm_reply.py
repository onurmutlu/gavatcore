#!/usr/bin/env python3

import asyncio
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_dm_reply():
    """DM reply sistemini test et"""
    
    # Test client oluştur
    client = TelegramClient('test_dm_reply_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        print("✅ Test client başlatıldı")
        
        # Test edilecek bot'lar
        bots = [
            "@yayincilara",
            "@babagavat"
        ]
        
        for bot_handle in bots:
            try:
                # Bot'u bul
                bot = await client.get_entity(bot_handle)
                print(f"✅ {bot_handle} bulundu: {bot.username}")
                
                # Test mesajı gönder
                test_message = "Merhaba! DM reply test mesajı 😊"
                await client.send_message(bot, test_message)
                print(f"📤 {bot_handle}'a test mesajı gönderildi: {test_message}")
                
                # 20 saniye bekle (hybrid mode timeout için)
                print("⏰ 20 saniye bekleniyor (hybrid mode test)...")
                await asyncio.sleep(20)
                
                # Bot'un cevap verip vermediğini kontrol et
                async for message in client.iter_messages(bot, limit=3):
                    if message.out:  # Bizim gönderdiğimiz mesaj
                        continue
                    if message.text and message.text != test_message:
                        print(f"🎉 {bot_handle} CEVAP VERDİ: {message.text}")
                        
                        # İkinci test mesajı gönder
                        second_message = "Teşekkürler! İkinci test mesajı"
                        await client.send_message(bot, second_message)
                        print(f"📤 İkinci test mesajı: {second_message}")
                        
                        # 15 saniye daha bekle
                        await asyncio.sleep(15)
                        
                        # İkinci cevabı kontrol et
                        async for msg in client.iter_messages(bot, limit=2):
                            if not msg.out and msg.text != message.text:
                                print(f"🎉 İKİNCİ CEVAP: {msg.text}")
                                break
                        break
                else:
                    print(f"❌ {bot_handle} cevap vermedi")
                
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ {bot_handle} test hatası: {e}")
        
        print("\n🧪 DM reply test tamamlandı!")
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_dm_reply()) 