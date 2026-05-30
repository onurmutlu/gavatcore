#!/usr/bin/env python3
"""
🔥 ULTIMATE GAVATCORE LAUNCHER v3.0 🔥
Mükemmel Bot Sistemi - Full GPT + Character + Persona Aktif

3 Ana Bot:
- 🎯 BabaGavat (Bilge lider, abi tavrı)
- 🎮 Yayıncı Lara (Enerjik streamer)
- 🌸 XXXGeisha (Gizemli, zarif)

Özellikler:
✅ GPT-4 Entegrasyonu
✅ Karakter Sistemleri
✅ Persona & Senaryolar
✅ DM Handling
✅ Grup Yönetimi
✅ Contact Management
✅ Session Management
✅ Health Monitoring
"""

import asyncio
import subprocess
import sys
import time
import os
import signal
import json
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger("gavatcore.ultimate")

class UltimateGavatCoreLauncher:
    def __init__(self):
        self.processes = []
        self.running = False
        self.start_time = datetime.now()
        
        # 3 Ana Bot Konfigürasyonu
        self.bot_configs = {
            "babagavat": {
                "name": "🎯 BabaGavat",
                "session": "sessions/babagavat_conversation.session",
                "character": {
                    "name": "Baba Gavat",
                    "personality": "Bilge, tecrübeli, komik. Gruplarda lider, herkesi yönlendirir. Bazen argo kullanır.",
                    "style": "Abi tavrı, öğüt verici, bazen ironik. 'Evlat', 'oğlum' gibi hitaplar.",
                    "mood": "wise_leader",
                    "trigger_words": ["baba", "gavat", "abi", "hocam", "tavsiye", "yardım"]
                },
                "priority": 1,
                "description": "Ana lider bot - Grup yönetimi ve DM handling"
            },
            "yayincilara": {
                "name": "🎮 Yayıncı Lara",
                "session": "sessions/yayincilara_conversation.session",
                "character": {
                    "name": "Yayıncı Lara",
                    "personality": "Enerjik, eğlenceli, yayın odaklı. Streaming kültürüne hakim, trending konularda aktif.",
                    "style": "Genç, dinamik dil. Gaming ve streaming terimleri kullanır.",
                    "mood": "streamer_energy",
                    "trigger_words": ["yayın", "stream", "game", "chat", "live", "twitch"]
                },
                "priority": 2,
                "description": "Streaming ve gaming odaklı bot"
            },
            "xxxgeisha": {
                "name": "🌸 XXXGeisha",
                "session": "sessions/xxxgeisha_conversation.session",
                "character": {
                    "name": "Geisha",
                    "personality": "Gizemli, çekici, sofistike. Derin konuşmalar yapar, sanatsal yaklaşımlar.",
                    "style": "Zarif, akıllı dil. Metaforlar ve felsefi yaklaşımlar kullanır.",
                    "mood": "mysterious_elegant",
                    "trigger_words": ["sanat", "güzellik", "felsefe", "geisha", "zen", "estetik"]
                },
                "priority": 3,
                "description": "Sofistike ve gizemli karakter bot"
            }
        }
        
        # Sistem bileşenleri
        self.system_components = {
            "main_system": {
                "name": "🏗️ Ana Sistem (GavatCore)",
                "command": "python main.py",
                "priority": 0,
                "description": "Core sistem - Contact management, DM handling"
            },
            "flask_api": {
                "name": "🌐 Flask API Server",
                "command": "python apis/production_bot_api.py",
                "priority": 4,
                "description": "REST API server (port 5050)"
            },
            "xp_token_api": {
                "name": "🪙 XP Token API",
                "command": "python apis/xp_token_api_sync.py",
                "priority": 5,
                "description": "Token economy API (port 5051)"
            }
        }
    
    def print_ultimate_banner(self):
        """Ultimate banner"""
        banner = f"""
🔥═══════════════════════════════════════════════════════════════🔥
██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗
██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   █████╗  
██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
 ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
🔥═══════════════════════════════════════════════════════════════🔥
        🚀 ULTIMATE GAVATCORE LAUNCHER v3.0 🚀
        💎 FULL GPT + CHARACTER + PERSONA SYSTEM 💎
🔥═══════════════════════════════════════════════════════════════🔥

🎯 3 ANA BOT:
   • BabaGavat (Bilge Lider)
   • Yayıncı Lara (Streamer Energy)  
   • XXXGeisha (Mysterious Elegant)

✨ ÖZELLIKLER:
   • GPT-4 Entegrasyonu
   • Karakter Sistemleri
   • Persona & Senaryolar
   • DM & Grup Yönetimi
   • Contact Management
   • Health Monitoring

🔥═══════════════════════════════════════════════════════════════🔥
        """
        print(banner)
    
    def check_dependencies(self) -> bool:
        """Sistem gereksinimlerini kontrol et"""
        log.info("🔍 Sistem kontrolleri başlıyor...")
        
        # Python version
        if sys.version_info < (3, 8):
            log.error("❌ Python 3.8+ gerekli!")
            return False
        log.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Required files
        required_files = [
            "config.py", "main.py", "multi_bot_launcher.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            log.error(f"❌ Eksik dosyalar: {missing_files}")
            return False
        
        # Session files
        for bot_key, config in self.bot_configs.items():
            session_path = Path(config["session"])
            if not session_path.exists():
                log.warning(f"⚠️ Session dosyası bulunamadı: {session_path}")
                # Create empty session file
                session_path.parent.mkdir(exist_ok=True)
                session_path.touch()
        
        # Memory check
        memory = psutil.virtual_memory()
        if memory.available < 2 * 1024**3:  # 2GB
            log.warning("⚠️ Düşük RAM! 2GB+ önerilen")
        else:
            log.info(f"✅ RAM: {memory.available // (1024**3)}GB mevcut")
        
        log.info("✅ Tüm kontroller başarılı!")
        return True
    
    def start_system_component(self, comp_key: str, config: Dict) -> bool:
        """Sistem bileşeni başlat"""
        log.info(f"🚀 {config['name']} başlatılıyor...")
        
        try:
            process = subprocess.Popen(
                config['command'].split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            
            time.sleep(3)
            
            if process.poll() is None:
                self.processes.append({
                    'key': comp_key,
                    'name': config['name'],
                    'type': 'system',
                    'process': process,
                    'pid': process.pid,
                    'start_time': datetime.now(),
                    'command': config['command']
                })
                log.info(f"✅ {config['name']} başlatıldı! (PID: {process.pid})")
                return True
            else:
                log.error(f"❌ {config['name']} başlatılamadı!")
                return False
                
        except Exception as e:
            log.error(f"❌ {config['name']} hatası: {e}")
            return False
    
    def start_character_bot(self, bot_key: str, config: Dict) -> bool:
        """Karakter botu başlat"""
        log.info(f"🤖 {config['name']} başlatılıyor...")
        
        try:
            # Multi bot launcher ile başlat
            env = os.environ.copy()
            env['GAVATCORE_BOT_MODE'] = bot_key
            env['GAVATCORE_CHARACTER'] = json.dumps(config['character'])
            
            process = subprocess.Popen(
                ['python', 'multi_bot_launcher.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                env=env
            )
            
            time.sleep(5)  # Character botlar için daha uzun bekleme
            
            if process.poll() is None:
                self.processes.append({
                    'key': bot_key,
                    'name': config['name'],
                    'type': 'character_bot',
                    'character': config['character']['name'],
                    'process': process,
                    'pid': process.pid,
                    'start_time': datetime.now(),
                    'session': config['session']
                })
                log.info(f"✅ {config['name']} aktif! (PID: {process.pid})")
                log.info(f"   🎭 Karakter: {config['character']['name']}")
                log.info(f"   💭 Kişilik: {config['character']['personality'][:50]}...")
                return True
            else:
                log.error(f"❌ {config['name']} başlatılamadı!")
                return False
                
        except Exception as e:
            log.error(f"❌ {config['name']} hatası: {e}")
            return False
    
    def start_all_systems(self) -> Dict[str, int]:
        """Tüm sistemleri başlat"""
        log.info("🔥 ULTIMATE GAVATCORE BAŞLATILIYOR! 🔥")
        
        results = {
            'system_components': 0,
            'character_bots': 0,
            'total_success': 0,
            'total_attempted': 0
        }
        
        # 1. Sistem bileşenlerini başlat
        log.info("🏗️ Sistem bileşenleri başlatılıyor...")
        sorted_components = sorted(
            self.system_components.items(),
            key=lambda x: x[1]['priority']
        )
        
        for comp_key, config in sorted_components:
            results['total_attempted'] += 1
            if self.start_system_component(comp_key, config):
                results['system_components'] += 1
                results['total_success'] += 1
            time.sleep(2)
        
        # 2. Karakter botlarını başlat
        log.info("🤖 Karakter botları başlatılıyor...")
        sorted_bots = sorted(
            self.bot_configs.items(),
            key=lambda x: x[1]['priority']
        )
        
        for bot_key, config in sorted_bots:
            results['total_attempted'] += 1
            if self.start_character_bot(bot_key, config):
                results['character_bots'] += 1
                results['total_success'] += 1
            time.sleep(3)
        
        return results
    
    def show_ultimate_status(self):
        """Ultimate durum gösterimi"""
        print("\n" + "="*80)
        print("📊 ULTIMATE GAVATCORE SYSTEM STATUS")
        print("="*80)
        
        if not self.processes:
            print("❌ Hiçbir bileşen çalışmıyor")
            return
        
        # Sistem bileşenleri
        system_procs = [p for p in self.processes if p['type'] == 'system']
        if system_procs:
            print("\n🏗️ SİSTEM BİLEŞENLERİ:")
            print("-" * 40)
            for i, proc in enumerate(system_procs, 1):
                try:
                    uptime = datetime.now() - proc['start_time']
                    status = "🟢 ÇALIŞIYOR" if proc['process'].poll() is None else "🔴 DURDU"
                    memory_mb = psutil.Process(proc['pid']).memory_info().rss / (1024 * 1024)
                    
                    print(f"{i:2d}. {proc['name']}")
                    print(f"    Status: {status}")
                    print(f"    PID: {proc['pid']}")
                    print(f"    Uptime: {str(uptime).split('.')[0]}")
                    print(f"    Memory: {memory_mb:.1f}MB")
                    print()
                except Exception as e:
                    print(f"{i:2d}. {proc['name']} - ❌ HATA: {e}")
                    print()
        
        # Karakter botları
        bot_procs = [p for p in self.processes if p['type'] == 'character_bot']
        if bot_procs:
            print("🤖 KARAKTER BOTLARI:")
            print("-" * 40)
            for i, proc in enumerate(bot_procs, 1):
                try:
                    uptime = datetime.now() - proc['start_time']
                    status = "🟢 ÇALIŞIYOR" if proc['process'].poll() is None else "🔴 DURDU"
                    memory_mb = psutil.Process(proc['pid']).memory_info().rss / (1024 * 1024)
                    
                    print(f"{i:2d}. {proc['name']}")
                    print(f"    🎭 Karakter: {proc['character']}")
                    print(f"    Status: {status}")
                    print(f"    PID: {proc['pid']}")
                    print(f"    Uptime: {str(uptime).split('.')[0]}")
                    print(f"    Memory: {memory_mb:.1f}MB")
                    print(f"    Session: {proc['session']}")
                    print()
                except Exception as e:
                    print(f"{i:2d}. {proc['name']} - ❌ HATA: {e}")
                    print()
        
        # Özet
        total_uptime = datetime.now() - self.start_time
        running_count = sum(1 for p in self.processes if p['process'].poll() is None)
        total_memory = sum(
            psutil.Process(p['pid']).memory_info().rss / (1024 * 1024)
            for p in self.processes
            if p['process'].poll() is None
        )
        
        print("📈 ÖZET:")
        print("-" * 40)
        print(f"🟢 Çalışan: {running_count}/{len(self.processes)}")
        print(f"⏱️ Sistem Uptime: {str(total_uptime).split('.')[0]}")
        print(f"💾 Toplam Memory: {total_memory:.1f}MB")
        print(f"🎭 Aktif Karakterler: {len(bot_procs)}")
        print(f"🏗️ Sistem Bileşenleri: {len(system_procs)}")
    
    def stop_all_systems(self):
        """Tüm sistemleri durdur"""
        log.info("🛑 ULTIMATE GAVATCORE DURDURULUYOR...")
        
        for proc in self.processes:
            try:
                process = psutil.Process(proc['pid'])
                if process.is_running():
                    process.terminate()
                    log.info(f"🔴 {proc['name']} durduruldu")
                    
                    # Zorla kapatma gerekirse
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        process.kill()
                        log.warning(f"💀 {proc['name']} zorla kapatıldı")
                        
            except psutil.NoSuchProcess:
                log.info(f"⚠️ {proc['name']} zaten durmuş")
            except Exception as e:
                log.error(f"❌ {proc['name']} durdurma hatası: {e}")
        
        self.processes.clear()
        log.info("✅ Tüm sistemler durduruldu!")
    
    def interactive_ultimate_menu(self):
        """Ultimate interaktif menü"""
        while True:
            print("\n" + "="*60)
            print("🎮 ULTIMATE GAVATCORE CONTROL PANEL")
            print("="*60)
            print("1. 🚀 Tüm Sistemleri Başlat")
            print("2. 📊 Ultimate Status Göster")
            print("3. 🤖 Sadece Character Botları Başlat")
            print("4. 🏗️ Sadece Sistem Bileşenlerini Başlat")
            print("5. 🛑 Tüm Sistemleri Durdur")
            print("6. 🔄 Full Sistem Restart")
            print("7. 📋 Bot Karakterlerini Göster")
            print("8. ❌ Çıkış")
            
            choice = input("\n🎯 Seçiminiz (1-8): ").strip()
            
            if choice == "1":
                results = self.start_all_systems()
                print(f"\n🎉 BAŞLATMA SONUÇLARI:")
                print(f"   🏗️ Sistem Bileşenleri: {results['system_components']}")
                print(f"   🤖 Karakter Botları: {results['character_bots']}")
                print(f"   ✅ Toplam Başarılı: {results['total_success']}/{results['total_attempted']}")
                
            elif choice == "2":
                self.show_ultimate_status()
                
            elif choice == "3":
                log.info("🤖 Sadece karakter botları başlatılıyor...")
                success = 0
                for bot_key, config in self.bot_configs.items():
                    if self.start_character_bot(bot_key, config):
                        success += 1
                    time.sleep(3)
                print(f"🎉 {success}/{len(self.bot_configs)} karakter botu başlatıldı!")
                
            elif choice == "4":
                log.info("🏗️ Sadece sistem bileşenleri başlatılıyor...")
                success = 0
                for comp_key, config in self.system_components.items():
                    if self.start_system_component(comp_key, config):
                        success += 1
                    time.sleep(2)
                print(f"🎉 {success}/{len(self.system_components)} sistem bileşeni başlatıldı!")
                
            elif choice == "5":
                self.stop_all_systems()
                
            elif choice == "6":
                self.stop_all_systems()
                time.sleep(3)
                results = self.start_all_systems()
                print(f"🔄 Sistem yeniden başlatıldı! {results['total_success']} bileşen aktif")
                
            elif choice == "7":
                self.show_character_info()
                
            elif choice == "8":
                self.stop_all_systems()
                print("👋 Ultimate GavatCore kapatılıyor!")
                break
                
            else:
                print("❌ Geçersiz seçim!")
    
    def show_character_info(self):
        """Karakter bilgilerini göster"""
        print("\n" + "="*60)
        print("🎭 GAVATCORE CHARACTER PROFILES")
        print("="*60)
        
        for i, (bot_key, config) in enumerate(self.bot_configs.items(), 1):
            char = config['character']
            print(f"\n{i}. {config['name']}")
            print(f"   🎭 Karakter: {char['name']}")
            print(f"   💭 Kişilik: {char['personality']}")
            print(f"   🗣️ Konuşma Tarzı: {char['style']}")
            print(f"   🎯 Mood: {char['mood']}")
            print(f"   🔑 Trigger Words: {', '.join(char['trigger_words'])}")
            print(f"   📁 Session: {config['session']}")
            print(f"   📝 Açıklama: {config['description']}")
    
    def run(self):
        """Ultimate launcher çalıştır"""
        self.print_ultimate_banner()
        
        if not self.check_dependencies():
            log.error("❌ Sistem kontrolleri başarısız!")
            sys.exit(1)
        
        # Signal handlers
        def signal_handler(signum, frame):
            log.info(f"🛑 Kapatma sinyali alındı: {signum}")
            self.stop_all_systems()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        log.info("🎮 Ultimate Control Panel başlatılıyor...")
        
        try:
            self.interactive_ultimate_menu()
        except KeyboardInterrupt:
            log.info("🛑 Ctrl+C ile çıkış...")
            self.stop_all_systems()

if __name__ == "__main__":
    launcher = UltimateGavatCoreLauncher()
    launcher.run()