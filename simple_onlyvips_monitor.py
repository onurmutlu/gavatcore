#!/usr/bin/env python3
"""
🔍 SIMPLE ONLYVIPS MONITOR 🔍

Sadece OnlyVips grubunu izleyen basit monitor
"""

import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def main():
    """🚀 Basit OnlyVips Monitor"""
    try:
        print("🔍 Simple OnlyVips Monitor başlatılıyor...")
        
        # Mevcut session'ı kullan
        client = TelegramClient(
            "sessions/onlyvips_monitor",  # Mevcut session
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        
        await client.start()
        me = await client.get_me()
        print(f"✅ Bağlandı: @{me.username}")
        
        # OnlyVips grubunu bul
        onlyvips_group_id = None
        print("🔍 OnlyVips grubunu arıyor...")
        
        async for dialog in client.iter_dialogs():
            group_name = dialog.name.lower() if dialog.name else ""
            
            if any(keyword in group_name for keyword in ["onlyvips", "only vips", "vip", "gavat"]):
                onlyvips_group_id = dialog.id
                print(f"✅ OnlyVips grubu bulundu: {dialog.name} (ID: {dialog.id})")
                break
        
        if not onlyvips_group_id:
            print("❌ OnlyVips grubu bulunamadı!")
            return
        
        print("""
🎯 SIMPLE ONLYVIPS MONITOR AKTİF!

📡 OnlyVips grubunu izliyorum...
💬 Lara'dan mesaj yazın ve burada göreceğiz!
🛑 Durdurmak için Ctrl+C kullanın
        """)
        
        @client.on(events.NewMessage)
        async def message_handler(event):
            """💬 Mesaj handler'ı"""
            try:
                if event.chat_id == onlyvips_group_id:
                    sender = await event.get_sender()
                    message_text = event.text or ""
                    
                    sender_info = "Unknown"
                    if sender:
                        if hasattr(sender, 'username') and sender.username:
                            sender_info = f"@{sender.username}"
                        elif hasattr(sender, 'first_name'):
                            sender_info = sender.first_name or "Unknown"
                    
                    print(f"""
💬 ONLYVIPS MESAJ!
⏰ {datetime.now().strftime('%H:%M:%S')}
👤 {sender_info}
📝 {message_text}
════════════════════════════════════════════════════
                    """)
                    
            except Exception as e:
                print(f"❌ Handler error: {e}")
        
        # Sürekli dinle
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitor durduruldu")
    except Exception as e:
        print(f"❌ Monitor error: {e}")
    finally:
        if 'client' in locals():
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 