#!/usr/bin/env python3
"""
Bot Sorunlarını Düzeltme Script'i
"""

import os
import sys
import subprocess

def check_environment():
    """Environment kontrolü"""
    print("🔍 Environment Kontrolü...")
    
    # Config dosyası
    if os.path.exists("config.py"):
        print("✅ config.py mevcut")
    else:
        print("❌ config.py bulunamadı!")
        return False
    
    # Session klasörü
    if os.path.exists("sessions"):
        sessions = [f for f in os.listdir("sessions") if f.endswith(".session")]
        print(f"✅ {len(sessions)} session dosyası bulundu")
        for session in sessions:
            size = os.path.getsize(f"sessions/{session}") / 1024
            print(f"   - {session}: {size:.1f}KB")
    else:
        print("❌ sessions klasörü bulunamadı!")
        return False
    
    # Handler'ları kontrol et
    handlers = [
        "handlers/lara_bot_handler.py",
        "handlers/lara_bot_handler_v2.py",
        "services/telegram/lara_bot_handler.py",
        "services/telegram/lara_bot_handler_v2.py"
    ]
    
    handler_found = False
    for handler in handlers:
        if os.path.exists(handler):
            print(f"✅ Handler bulundu: {handler}")
            handler_found = True
            break
    
    if not handler_found:
        print("❌ Hiçbir handler bulunamadı!")
    
    return True

def test_simple_bot():
    """Basit bot testi"""
    print("\n🧪 Basit Bot Testi...")
    
    test_code = '''
import asyncio
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

async def test():
    client = TelegramClient("test_session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start()
    me = await client.get_me()
    print(f"✅ Test başarılı: @{me.username}")
    await client.disconnect()

asyncio.run(test())
'''
    
    with open("test_connection.py", "w") as f:
        f.write(test_code)
    
    try:
        result = subprocess.run([sys.executable, "test_connection.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Telegram bağlantısı başarılı!")
            print(result.stdout)
        else:
            print("❌ Telegram bağlantısı başarısız!")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Test hatası: {e}")
    finally:
        if os.path.exists("test_connection.py"):
            os.remove("test_connection.py")
        if os.path.exists("test_session.session"):
            os.remove("test_session.session")

def fix_imports():
    """Import sorunlarını düzelt"""
    print("\n🔧 Import Düzeltmeleri...")
    
    # PYTHONPATH'e ekle
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # __init__.py dosyaları oluştur
    dirs_need_init = [
        "handlers",
        "services",
        "services/telegram",
        "utilities",
        "core"
    ]
    
    for dir_path in dirs_need_init:
        if os.path.exists(dir_path):
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
                print(f"✅ {init_file} oluşturuldu")

def main():
    print("🚀 GAVATCore Bot Sorun Düzeltme")
    print("="*40)
    
    # 1. Environment kontrolü
    if not check_environment():
        print("\n❌ Environment sorunları var!")
        return
    
    # 2. Import düzeltmeleri
    fix_imports()
    
    # 3. Basit test
    test_simple_bot()
    
    print("\n📋 ÖNERİLER:")
    print("1. Session dosyalarını yenileyin:")
    print("   python utilities/session_manager.py")
    print("\n2. Handler'ları services/telegram'a taşıyın")
    print("\n3. Basit test bot'u çalıştırın:")
    print("   python test_bot_simple.py")
    print("\n4. run.py ile sistemi başlatın:")
    print("   python run.py")

if __name__ == "__main__":
    main() 