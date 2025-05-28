#!/usr/bin/env python3

import asyncio
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_bot_filter():
    """Bot filtreleme sistemini test et"""
    
    # Test client oluştur
    client = TelegramClient('test_bot_filter_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        print("✅ Test client başlatıldı")
        
        # Test edilecek bot'lar
        test_bots = [
            "@yayincilara",
            "@babagavat"
        ]
        
        # Telegram resmi bot'ları (test için)
        telegram_bots = [
            "@SpamBot",
            "@BotFather"
        ]
        
        print("\n🧪 Bot filtreleme testi başlıyor...")
        print("📝 Sistem artık bot'lardan gelen mesajları engellemeli")
        print("🔍 Log dosyalarında 'bot_filter' mesajlarını kontrol edin")
        
        for bot_handle in test_bots:
            try:
                # Bot'u bul
                bot = await client.get_entity(bot_handle)
                print(f"\n✅ {bot_handle} bulundu: {bot.username}")
                
                # Test mesajı gönder
                test_message = "Bot filter test mesajı - normal kullanıcı"
                await client.send_message(bot, test_message)
                print(f"📤 {bot_handle}'a normal test mesajı gönderildi")
                
                # 10 saniye bekle
                await asyncio.sleep(10)
                
                # Bot'un cevap verip vermediğini kontrol et
                async for message in client.iter_messages(bot, limit=3):
                    if message.out:  # Bizim gönderdiğimiz mesaj
                        continue
                    if message.text and message.text != test_message:
                        print(f"🎉 {bot_handle} NORMAL KULLANICIYA CEVAP VERDİ: {message.text[:50]}...")
                        break
                else:
                    print(f"❌ {bot_handle} cevap vermedi")
                
            except Exception as e:
                print(f"❌ {bot_handle} test hatası: {e}")
        
        print("\n📋 Test Sonuçları:")
        print("✅ Normal kullanıcı mesajları işlenmeli")
        print("🚫 Bot mesajları engellenmeli")
        print("📊 Log dosyalarında 'bot_filter' kayıtlarını kontrol edin")
        
        print("\n🔍 Şimdi SpamBot'tan gelen mesajları kontrol edin...")
        print("💡 SpamBot'tan 'Good news, no limits...' mesajı gelirse engellenmeli")
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_bot_filter()) 