#!/usr/bin/env python3
"""
🔍 ONLYVIPS DEBUG MONITOR 🔍

OnlyVips grubundaki mesajları izleyip botların neden cevap vermediğini anlayalım
"""

import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

class OnlyVipsDebugMonitor:
    """🔍 Debug Monitor"""
    
    def __init__(self):
        self.client = None
        self.onlyvips_group_id = None
        
    async def initialize(self):
        """🚀 Debug monitörü başlat"""
        try:
            print("🔍 OnlyVips Debug Monitor başlatılıyor...")
            
            self.client = TelegramClient(
                "sessions/debug_monitor",
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH
            )
            
            await self.client.start()
            me = await self.client.get_me()
            print(f"✅ Debug Monitor bağlandı: @{me.username}")
            
            # OnlyVips grubunu bul
            await self._find_onlyvips_group()
            
            # Message listener kur
            await self._setup_debug_listener()
            
            return True
            
        except Exception as e:
            print(f"❌ Debug monitor error: {e}")
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
            print("\n📋 Mevcut gruplar:")
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    print(f"   📱 {dialog.name} (ID: {dialog.id})")
            
        except Exception as e:
            print(f"❌ Group search error: {e}")
    
    async def _setup_debug_listener(self):
        """👂 Debug message listener"""
        try:
            @self.client.on(events.NewMessage)
            async def debug_message_handler(event):
                """💬 Debug mesaj handler'ı"""
                try:
                    if self.onlyvips_group_id and event.chat_id == self.onlyvips_group_id:
                        sender = await event.get_sender()
                        message_text = event.text or ""
                        
                        sender_info = "Unknown"
                        if sender:
                            if hasattr(sender, 'username') and sender.username:
                                sender_info = f"@{sender.username}"
                            elif hasattr(sender, 'first_name'):
                                sender_info = sender.first_name or "Unknown"
                        
                        print(f"""
🔍 DEBUG: ONLYVIPS MESAJ GELDİ!
⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}
👤 Gönderen: {sender_info}
💬 Mesaj: {message_text}
📊 Event ID: {event.id}
📍 Chat ID: {event.chat_id}
═══════════════════════════════════════════════════════════
                        """)
                        
                        # Bot mu kontrol et
                        if sender and hasattr(sender, 'username'):
                            username = sender.username or ""
                            if any(bot_name in username.lower() for bot_name in ["babagavat", "geishaniz", "yayincilara"]):
                                print(f"🤖 BOT MESAJI DETECTED: {username}")
                        
                except Exception as e:
                    print(f"❌ Debug handler error: {e}")
            
            print("✅ Debug listener kuruldu!")
            
        except Exception as e:
            print(f"❌ Debug listener setup error: {e}")
    
    async def run_debug_monitor(self):
        """🔍 Debug monitörü çalıştır"""
        try:
            print("""
🔍 ONLYVIPS DEBUG MONITOR AKTİF!

📡 OnlyVips grubundaki TÜM mesajları izliyorum...
🤖 Bot mesajlarını tespit ediyorum...
🔧 Sorunları analiz ediyorum...

💬 Şimdi Lara'dan mesaj yazın ve ne olduğunu görelim!
🛑 Durdurmak için Ctrl+C kullanın
            """)
            
            # Sürekli dinle
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Debug monitor durduruldu")
        except Exception as e:
            print(f"❌ Debug monitor error: {e}")
        finally:
            if self.client:
                await self.client.disconnect()

async def main():
    """🚀 Debug ana fonksiyon"""
    try:
        monitor = OnlyVipsDebugMonitor()
        
        if await monitor.initialize():
            await monitor.run_debug_monitor()
        else:
            print("❌ Debug monitor başlatılamadı")
            
    except Exception as e:
        print(f"❌ Debug main error: {e}")

if __name__ == "__main__":
    import os
    os.makedirs("sessions", exist_ok=True)
    asyncio.run(main()) 