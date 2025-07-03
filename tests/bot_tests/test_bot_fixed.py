#!/usr/bin/env python3
"""
Gelişmiş Test Bot - Database lock sorununu çözer
"""

import asyncio
import os
import sys
import sqlite3
import time
from telethon import TelegramClient, events
from telethon.sessions import SQLiteSession
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

class FixedSQLiteSession(SQLiteSession):
    """Database lock sorununu çözen custom session"""
    
    def _update_session_table(self):
        """Override to fix database lock issues"""
        retries = 5
        while retries > 0:
            try:
                c = self._cursor()
                # WAL mode kullan (Write-Ahead Logging)
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("PRAGMA busy_timeout=5000")  # 5 saniye timeout
                
                # Orijinal işlem
                c.execute('delete from sessions')
                c.execute('insert into sessions values (?, ?, ?, ?, ?)', (
                    self._dc_id,
                    self._server_address,
                    self._port,
                    self._auth_key.key if self._auth_key else b'',
                    self._takeout_id
                ))
                self.save()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    retries -= 1
                    print(f"⚠️ Database locked, retrying... ({retries} left)")
                    time.sleep(1)
                else:
                    raise
            except Exception as e:
                raise

async def main():
    print("🔍 GELİŞMİŞ TEST BOT BAŞLIYOR...")
    print(f"API ID: {TELEGRAM_API_ID}")
    print(f"API HASH: {TELEGRAM_API_HASH[:10]}...")
    
    # Session dosyasını kontrol et
    session_name = "sessions/_905382617727"
    session_file = f"{session_name}.session"
    
    # Eğer session varsa, lock'u temizle
    if os.path.exists(session_file):
        print(f"✅ Session dosyası mevcut: {session_file}")
        try:
            # Database'i aç ve kapat (lock'u temizle)
            conn = sqlite3.connect(session_file)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.close()
            print("✅ Session lock temizlendi")
        except Exception as e:
            print(f"⚠️ Session temizleme hatası: {e}")
    else:
        print(f"❌ Session dosyası bulunamadı: {session_file}")
        return
    
    # Client oluştur (custom session ile)
    client = TelegramClient(
        FixedSQLiteSession(session_name),
        TELEGRAM_API_ID,
        TELEGRAM_API_HASH,
        sequential_updates=True  # Sıralı güncelleme
    )
    
    try:
        # Başlat
        await client.start()
        me = await client.get_me()
        print(f"✅ Giriş yapıldı: @{me.username} (ID: {me.id})")
        
        # Basit handler
        @client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, 'bot', False):
                    print(f"💬 DM alındı: {sender.first_name} -> {event.raw_text}")
                    
                    # Basit yanıt
                    await event.respond("🌹 Merhaba! Ben Lara, test modundayım. Mesajını aldım!")
                    print("✅ Yanıt gönderildi!")
        
        print("🎯 Bot hazır! DM bekleniyor...")
        print("Ctrl+C ile durdurun")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Bot hatası: {e}")
    finally:
        await client.disconnect()
        print("👋 Bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main()) 