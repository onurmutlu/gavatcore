#!/usr/bin/env python3

import asyncio
import sys
import os
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test_group_conversation():
    """Grup conversation response sistemini test et"""
    
    # Test client oluştur
    client = TelegramClient('test_conversation_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        print("✅ Test client başlatıldı")
        
        # Test edilecek bot'lar ve gruplar
        bots = [
            "@yayincilara",
            "@babagavat"
        ]
        
        # Test grupları (botların katıldığı gruplar)
        test_groups = [
            "ARAYIŞIN ADRESİ TÜRKİYE 🔥🔥",
            "ARAYIŞLAR SOHBET GRUBU"
        ]
        
        for bot_handle in bots:
            try:
                # Bot'u bul
                bot = await client.get_entity(bot_handle)
                print(f"✅ {bot_handle} bulundu: {bot.username}")
                
                # Bot'un katıldığı grupları bul
                async for dialog in client.iter_dialogs():
                    if dialog.is_group and any(test_group in dialog.name for test_group in test_groups):
                        print(f"📍 Test grubu bulundu: {dialog.name}")
                        
                        # Gruba test mesajı gönder (bot'a mention)
                        test_message = f"{bot_handle} merhaba! Nasılsın?"
                        await client.send_message(dialog, test_message)
                        print(f"📤 {dialog.name}'a test mesajı gönderildi: {test_message}")
                        
                        # 10 saniye bekle (bot'un cevap vermesi için)
                        await asyncio.sleep(10)
                        
                        # Bot'un cevap verip vermediğini kontrol et
                        async for message in client.iter_messages(dialog, limit=5):
                            if message.sender_id == bot.id:
                                print(f"✅ {bot_handle} cevap verdi: {message.text}")
                                
                                # Şimdi bot'un mesajına normal cevap gönder (mention olmadan)
                                response_message = "Teşekkürler! Ben de iyiyim 😊"
                                await client.send_message(dialog, response_message)
                                print(f"📤 Bot'a cevap gönderildi: {response_message}")
                                
                                # 15 saniye bekle (conversation response için)
                                print("⏰ 15 saniye bekleniyor (conversation response test)...")
                                await asyncio.sleep(15)
                                
                                # Bot'un conversation response verip vermediğini kontrol et
                                async for msg in client.iter_messages(dialog, limit=3):
                                    if msg.sender_id == bot.id and msg.text != message.text:
                                        print(f"🎉 CONVERSATION RESPONSE BAŞARILI: {msg.text}")
                                        break
                                else:
                                    print(f"❌ Conversation response gelmedi")
                                
                                break
                        break
                
            except Exception as e:
                print(f"❌ {bot_handle} test hatası: {e}")
        
        print("\n🧪 Grup conversation test tamamlandı!")
        
    except Exception as e:
        print(f"💥 Test hatası: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_group_conversation()) 