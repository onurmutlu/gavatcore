#!/usr/bin/env python3
# monitor_system.py

import time
import os
import subprocess
from gpt.openai_utils import get_cache_stats

def monitor_system():
    """Sistem durumunu izler ve raporlar."""
    print("🔍 GAVATCORE Sistem Durumu")
    print("=" * 50)
    
    # Basit sistem bilgileri
    try:
        # macOS için memory bilgisi
        result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        if result.returncode == 0:
            print("💻 Sistem: macOS")
        else:
            print("💻 Sistem: Bilinmiyor")
    except:
        print("💻 Sistem: Bilinmiyor")
    
    # Session dosyaları
    sessions_dir = "sessions"
    if os.path.exists(sessions_dir):
        session_files = [f for f in os.listdir(sessions_dir) if f.endswith(".session")]
        lock_files = [f for f in os.listdir(sessions_dir) if "-journal" in f or ".lock" in f]
        
        print(f"📁 Session Dosyaları: {len(session_files)}")
        print(f"🔒 Lock Dosyaları: {len(lock_files)}")
        
        if lock_files:
            print("⚠️ Aktif lock dosyaları:")
            for lock_file in lock_files:
                print(f"   - {lock_file}")
    
    # GPT Cache durumu
    try:
        cache_stats = get_cache_stats()
        print(f"🤖 GPT Cache: {cache_stats['valid_entries']}/{cache_stats['total_entries']} entry")
        print(f"📊 Cache Hit Ratio: {cache_stats['cache_hit_ratio']:.2%}")
    except Exception as e:
        print(f"❌ GPT Cache durumu alınamadı: {e}")
    
    # Log dosyaları
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        log_files = []
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                if file.endswith('.log'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path) // 1024  # KB
                    log_files.append((file, file_size))
        
        print(f"📝 Log Dosyaları: {len(log_files)}")
        for log_file, size in log_files:
            print(f"   - {log_file}: {size}KB")
    
    # Process kontrolü (basit)
    try:
        result = subprocess.run(['pgrep', '-f', 'python.*run.py'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"🐍 Python Processes: {len(pids)}")
            for pid in pids:
                if pid:
                    print(f"   - PID {pid}: python run.py")
        else:
            print("🐍 Python Processes: 0")
    except:
        print("🐍 Python Processes: Kontrol edilemedi")

if __name__ == "__main__":
    monitor_system() 