#!/usr/bin/env python3
# restart_system.py

import os
import time
import subprocess
import signal

def restart_system():
    """Sistemi güvenli şekilde yeniden başlatır."""
    print("🔄 GAVATCORE Sistem Yeniden Başlatılıyor...")
    
    # 1. Çalışan process'leri durdur
    print("🛑 Çalışan process'ler durduruluyor...")
    try:
        result = subprocess.run(['pgrep', '-f', 'python.*run.py'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"   ✅ PID {pid} durduruldu")
                    except:
                        print(f"   ❌ PID {pid} durdurulamadı")
        else:
            print("   ℹ️ Çalışan process bulunamadı")
    except Exception as e:
        print(f"   ⚠️ Process kontrolü hatası: {e}")
    
    # 2. Session lock'ları temizle
    print("🧹 Session lock dosyaları temizleniyor...")
    os.system("python cleanup_sessions.py")
    
    # 3. 5 saniye bekle
    print("⏳ 5 saniye bekleniyor...")
    time.sleep(5)
    
    # 4. Sistemi yeniden başlat
    print("🚀 Sistem yeniden başlatılıyor...")
    os.system("python run.py &")
    
    # 5. Durum kontrolü
    time.sleep(3)
    print("📊 Sistem durumu kontrol ediliyor...")
    os.system("python monitor_system.py")

if __name__ == "__main__":
    restart_system() 