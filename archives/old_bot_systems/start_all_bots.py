#!/usr/bin/env python3
"""
🤖 TÜMÜ BOT BAŞLATICI v1.0
Sistemdeki tüm botları başlatır: BabaGavat, Lara, Geisha
"""

import subprocess
import time
import os

def start_bot(bot_name, script_path):
    """Bot başlat"""
    print(f"🚀 {bot_name} başlatılıyor...")
    
    if not os.path.exists(script_path):
        print(f"⚠️ {bot_name} script bulunamadı: {script_path}")
        print(f"💡 Demo mode aktif olacak")
        return None
    
    try:
        process = subprocess.Popen(
            ["python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ {bot_name} başlatıldı (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ {bot_name} başlatma hatası: {e}")
        return None

def main():
    print("=" * 50)
    print("🤖 GAVATCORE BOT ORDUSU BAŞLATIYOR")
    print("=" * 50)
    
    # Bot tanımları
    bots = {
        "BabaGavat": "utils/babagavat_production_launcher.py",
        "Lara": "lara_bot_launcher.py", 
        "Geisha": "utils/babagavat_production_launcher.py"
    }
    
    processes = {}
    
    for bot_name, script_path in bots.items():
        processes[bot_name] = start_bot(bot_name, script_path)
        time.sleep(2)  # Botlar arası gecikme
    
    print("\n" + "=" * 50)
    print("🎯 BOT DURUMU:")
    print("=" * 50)
    
    for bot_name, process in processes.items():
        if process and process.poll() is None:
            print(f"✅ {bot_name}: Çalışıyor (PID: {process.pid})")
        else:
            print(f"❌ {bot_name}: Durduruldu/Hata")
    
    print("\n🔥 Sistem aktif! Botlar çalışmaya başladı.")
    print("🛑 Durdurmak için: Ctrl+C")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Sistem durduruluyor...")
        for bot_name, process in processes.items():
            if process and process.poll() is None:
                process.terminate()
                print(f"🔴 {bot_name} durduruldu")

if __name__ == "__main__":
    main() 