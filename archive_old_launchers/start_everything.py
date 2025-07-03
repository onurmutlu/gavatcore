#!/usr/bin/env python3
"""
GAVATCore Unified Launcher - Tek Tuşla Her Şey!
"""

import subprocess
import sys
import time
import os
import signal

class UnifiedLauncher:
    def __init__(self):
        self.processes = []
        
    def start_component(self, name, command):
        """Bileşen başlat"""
        print(f"🚀 {name} başlatılıyor...")
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            self.processes.append((name, process))
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {name} başlatıldı (PID: {process.pid})")
                return True
            else:
                print(f"❌ {name} başlatılamadı")
                return False
        except Exception as e:
            print(f"❌ {name} hatası: {e}")
            return False
            
    def run(self):
        print("🔥" + "="*50 + "🔥")
        print("🚀 GAVATCore UNIFIED SYSTEM")
        print("🔥" + "="*50 + "🔥")
        
        # Bileşenleri başlat
        components = [
            ("Flask API", "python apis/production_bot_api.py"),
            ("XP Token API", "python apis/xp_token_api_sync.py"),
            ("Bot System", "python -m services.telegram.bot_manager.bot_system")
        ]
        
        success_count = 0
        for name, command in components:
            if self.start_component(name, command):
                success_count += 1
                
        print(f"\n✅ {success_count}/{len(components)} bileşen başlatıldı!")
        
        if success_count > 0:
            print("\n🎯 Sistem çalışıyor! Ctrl+C ile durdurun.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Sistem durduruluyor...")
                for name, process in self.processes:
                    try:
                        process.terminate()
                        print(f"🔴 {name} durduruldu")
                    except:
                        pass
        else:
            print("\n❌ Sistem başlatılamadı!")
            sys.exit(1)

if __name__ == "__main__":
    launcher = UnifiedLauncher()
    launcher.run()
