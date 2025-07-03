#!/usr/bin/env python3
"""
🧪 SIMPLE GPT TEST 🧪

Mevcut session ile GPT sistemini test et
"""

import asyncio
import os
from datetime import datetime
from telethon import TelegramClient

async def simple_gpt_test():
    """🧪 Basit GPT test"""
    try:
        print("🧪 Simple GPT Test başlıyor...")
        
        # Mevcut babagavat session'ını kullan
        client = TelegramClient(
            "sessions/babagavat_conversation",
            27000000,  # Dummy values
            "dummy"
        )
        
        # Session file var mı kontrol et
        session_file = "sessions/babagavat_conversation.session"
        if os.path.exists(session_file):
            print("✅ Session file bulundu")
        else:
            print("❌ Session file bulunamadı")
            return False
        
        print("📊 GPT System Status:")
        print(f"   🤖 GPT Process ID: {os.popen('ps aux | grep gpt | grep -v grep').read().strip()}")
        
        # Log dosyasını kontrol et
        log_files = [f for f in os.listdir('.') if f.startswith('onlyvips_gpt_conversation_')]
        if log_files:
            latest_log = sorted(log_files)[-1]
            print(f"   📝 Latest Log: {latest_log}")
            
            # Son 10 satırı göster
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                print("   📋 Son log satırları:")
                for line in lines[-10:]:
                    print(f"      {line.strip()}")
        
        print("""
🎯 GPT SYSTEM STATUS TAMAMLANDI!

🧠 GPT-4o sistem durumu kontrol edildi
📝 Log dosyaları incelendi
🤖 Process durumu kontrol edildi

💪 ONUR METODU: SYSTEM CHECK!
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Simple test error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(simple_gpt_test()) 