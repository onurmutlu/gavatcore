#!/usr/bin/env python3
"""
🔥 ÇATIR ÇUTUR BOT LAUNCHER 🔥
Tüm botları aynı anda çalıştıran süper sistem!
"""

import asyncio
import subprocess
import sys
import time
import os
import signal
import json
from datetime import datetime
from typing import Dict, List, Optional
import psutil

class CatirCuturLauncher:
    def __init__(self):
        self.processes = []
        self.bot_configs = self.load_bot_configs()
        self.running = False
        
    def load_bot_configs(self) -> Dict:
        """Bot konfigürasyonlarını yükle"""
        return {
            "main_system": {
                "name": "🎯 Ana Sistem (GavatCore)",
                "command": "python main.py",
                "priority": 1,
                "description": "Ana bot sistemi - Contact ekleme, DM handling"
            },
            "multi_bot": {
                "name": "🤖 Multi Bot (3 Karakter)",
                "command": "python multi_bot_launcher.py",
                "priority": 2,
                "description": "3 farklı karakter botu - BabaGavat, Lara, Geisha"
            },
            "ultimate_bot": {
                "name": "⚡ Ultimate Bot",
                "command": "python ultimate_full_throttle_bot.py",
                "priority": 3,
                "description": "Full throttle bot sistemi"
            },
            "perfect_gpt": {
                "name": "🧠 Perfect GPT Bot",
                "command": "python perfect_gpt_bot.py",
                "priority": 4,
                "description": "GPT entegreli akıllı bot"
            },
            "grup_mesaj": {
                "name": "💬 Grup Mesaj Botu",
                "command": "python grup_mesaj_botu.py",
                "priority": 5,
                "description": "Grup mesajlaşma botu"
            },
            "temiz_grup": {
                "name": "🧹 Temiz Grup Bot",
                "command": "python temiz_grup_bot.py",
                "priority": 6,
                "description": "Grup temizlik ve moderasyon"
            },
            "simple_perfect": {
                "name": "✨ Simple Perfect Bot",
                "command": "python simple_perfect_bot.py",
                "priority": 7,
                "description": "Basit ama mükemmel bot"
            },
            "production_bot": {
                "name": "🏭 Production Bot",
                "command": "python gavatcore_ultimate_production_bot.py",
                "priority": 8,
                "description": "Production seviye bot sistemi"
            }
        }
    
    def print_banner(self):
        """Süper banner yazdır"""
        banner = """
🔥═══════════════════════════════════════════════════════════════🔥
██████╗  ██████╗ ████████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ 
██╔══██╗██╔═══██╗╚══██╔══╝    ██║     ██╔══██╗██║   ██║████╗  ██║ 
██████╔╝██║   ██║   ██║       ██║     ███████║██║   ██║██╔██╗ ██║ 
██╔══██╗██║   ██║   ██║       ██║     ██╔══██║██║   ██║██║╚██╗██║ 
██████╔╝╚██████╔╝   ██║       ███████╗██║  ██║╚██████╔╝██║ ╚████║ 
╚═════╝  ╚═════╝    ╚═╝       ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ 
🔥═══════════════════════════════════════════════════════════════🔥
        🚀 ÇATIR ÇUTUR BOT LAUNCHER v2.0 🚀
        💥 TÜM BOTLARI AYNI ANDA ÇALIŞTIR! 💥
🔥═══════════════════════════════════════════════════════════════🔥
        """
        print(banner)
        
    def check_dependencies(self) -> bool:
        """Bağımlılıkları kontrol et"""
        print("🔍 Sistem kontrolleri yapılıyor...")
        
        # Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            print("❌ Python 3.8+ gerekli!")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Required files
        required_files = [
            "config.py", "main.py", "multi_bot_launcher.py",
            "ultimate_full_throttle_bot.py", "perfect_gpt_bot.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Eksik dosyalar: {', '.join(missing_files)}")
            return False
        
        print("✅ Tüm dosyalar mevcut")
        
        # Memory check
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # 1GB
            print("⚠️ Düşük RAM! (1GB+ önerilen)")
        else:
            print(f"✅ RAM: {memory.available // (1024**3)}GB mevcut")
        
        return True
    
    def start_bot(self, bot_key: str, config: Dict) -> bool:
        """Tek bot başlat"""
        print(f"\n🚀 {config['name']} başlatılıyor...")
        
        try:
            # Process başlat
            process = subprocess.Popen(
                config['command'].split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            
            # Kısa bekleme
            time.sleep(3)
            
            # Process durumunu kontrol et
            if process.poll() is None:
                self.processes.append({
                    'key': bot_key,
                    'name': config['name'],
                    'process': process,
                    'pid': process.pid,
                    'start_time': datetime.now(),
                    'command': config['command']
                })
                print(f"✅ {config['name']} başlatıldı! (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {config['name']} başlatılamadı!")
                if stderr:
                    print(f"   Hata: {stderr.decode()[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ {config['name']} hatası: {str(e)}")
            return False
    
    def start_all_bots(self, selected_bots: Optional[List[str]] = None) -> int:
        """Tüm botları başlat"""
        print("\n🔥 BOT BAŞLATMA SÜRECI BAŞLIYOR! 🔥")
        
        # Hangi botları başlatacağımızı belirle
        bots_to_start = selected_bots or list(self.bot_configs.keys())
        
        # Priority'ye göre sırala
        sorted_bots = sorted(
            [(k, v) for k, v in self.bot_configs.items() if k in bots_to_start],
            key=lambda x: x[1]['priority']
        )
        
        successful_bots = 0
        total_bots = len(sorted_bots)
        
        print(f"📊 {total_bots} bot başlatılacak...")
        
        for bot_key, config in sorted_bots:
            if self.start_bot(bot_key, config):
                successful_bots += 1
                # Botlar arası bekleme
                time.sleep(2)
            else:
                print(f"⚠️ {config['name']} atlandı")
        
        return successful_bots
    
    def show_status(self):
        """Bot durumlarını göster"""
        print("\n📊 BOT DURUMU:")
        print("=" * 60)
        
        if not self.processes:
            print("❌ Hiçbir bot çalışmıyor")
            return
        
        for i, bot in enumerate(self.processes, 1):
            try:
                # Process durumunu kontrol et
                process = psutil.Process(bot['pid'])
                status = "🟢 ÇALIŞIYOR" if process.is_running() else "🔴 DURDU"
                uptime = datetime.now() - bot['start_time']
                memory_mb = process.memory_info().rss / (1024 * 1024)
                
                print(f"{i:2d}. {bot['name']}")
                print(f"    Status: {status}")
                print(f"    PID: {bot['pid']}")
                print(f"    Uptime: {str(uptime).split('.')[0]}")
                print(f"    Memory: {memory_mb:.1f}MB")
                print(f"    Command: {bot['command']}")
                print()
                
            except psutil.NoSuchProcess:
                print(f"{i:2d}. {bot['name']} - 🔴 PROCESS BULUNAMADI")
                print()
    
    def stop_all_bots(self):
        """Tüm botları durdur"""
        print("\n🛑 TÜM BOTLAR DURDURULUYOR...")
        
        for bot in self.processes:
            try:
                process = psutil.Process(bot['pid'])
                if process.is_running():
                    process.terminate()
                    print(f"🔴 {bot['name']} durduruldu")
                    
                    # Zorla kapatma gerekirse
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        process.kill()
                        print(f"💀 {bot['name']} zorla kapatıldı")
                        
            except psutil.NoSuchProcess:
                print(f"⚠️ {bot['name']} zaten durmuş")
            except Exception as e:
                print(f"❌ {bot['name']} durdurma hatası: {e}")
        
        self.processes.clear()
        print("✅ Tüm botlar durduruldu!")
    
    def interactive_menu(self):
        """Interaktif menü"""
        while True:
            print("\n" + "="*50)
            print("🎮 ÇATIR ÇUTUR BOT LAUNCHER MENÜ")
            print("="*50)
            print("1. 🚀 Tüm Botları Başlat")
            print("2. 🎯 Seçili Botları Başlat")
            print("3. 📊 Bot Durumunu Göster")
            print("4. 🛑 Tüm Botları Durdur")
            print("5. 📋 Bot Listesini Göster")
            print("6. 🔄 Sistem Yeniden Başlat")
            print("7. ❌ Çıkış")
            
            choice = input("\n🎯 Seçiminiz (1-7): ").strip()
            
            if choice == "1":
                successful = self.start_all_bots()
                print(f"\n🎉 {successful}/{len(self.bot_configs)} bot başlatıldı!")
                
            elif choice == "2":
                self.show_bot_list()
                selected = input("\nBot numaralarını girin (1,2,3): ").strip()
                try:
                    indices = [int(x.strip()) - 1 for x in selected.split(",")]
                    bot_keys = list(self.bot_configs.keys())
                    selected_bots = [bot_keys[i] for i in indices if 0 <= i < len(bot_keys)]
                    successful = self.start_all_bots(selected_bots)
                    print(f"\n🎉 {successful}/{len(selected_bots)} bot başlatıldı!")
                except:
                    print("❌ Geçersiz seçim!")
                    
            elif choice == "3":
                self.show_status()
                
            elif choice == "4":
                self.stop_all_bots()
                
            elif choice == "5":
                self.show_bot_list()
                
            elif choice == "6":
                self.stop_all_bots()
                time.sleep(2)
                successful = self.start_all_bots()
                print(f"\n🔄 Sistem yeniden başlatıldı! {successful} bot aktif")
                
            elif choice == "7":
                self.stop_all_bots()
                print("👋 Görüşürüz!")
                break
                
            else:
                print("❌ Geçersiz seçim!")
    
    def show_bot_list(self):
        """Bot listesini göster"""
        print("\n📋 MEVCUT BOTLAR:")
        print("="*60)
        
        for i, (key, config) in enumerate(self.bot_configs.items(), 1):
            print(f"{i:2d}. {config['name']}")
            print(f"    📝 {config['description']}")
            print(f"    🔧 {config['command']}")
            print()
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.print_banner()
        
        if not self.check_dependencies():
            print("❌ Sistem kontrolleri başarısız!")
            sys.exit(1)
        
        print("\n✅ Sistem hazır!")
        
        # Signal handler
        def signal_handler(signum, frame):
            print("\n\n🛑 Kapatma sinyali alındı...")
            self.stop_all_bots()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Interaktif menüyü başlat
        try:
            self.interactive_menu()
        except KeyboardInterrupt:
            print("\n\n🛑 Ctrl+C ile çıkış...")
            self.stop_all_bots()

if __name__ == "__main__":
    launcher = CatirCuturLauncher()
    launcher.run()