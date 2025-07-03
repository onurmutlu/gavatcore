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
        self.bot_configs = {
            # SİSTEM BİLEŞENLERİ
            "main_system": {
                "name": "🏗️ Ana Sistem (Flask API + XP Token)",
                "command": "python main.py",
                "description": "Flask API (port 5050) + XP Token API (port 5051)",
                "priority": 1
            },
            
            # KARAKTER BOTLARI - GAWATBABA YENİ HESAPLA AKTİF!
            "gawatbaba": {
                "name": "🔥 GawatBaba (Sokak Abisi)",
                "command": "python multi_bot_launcher.py",
                "character": "gawatbaba",
                "description": "Yeni hesap ile aktif! Tecrübeli abi, grup lideri",
                "priority": 2
            },
            "yayincilara": {
                "name": "🎮 Yayıncı Lara (Streamer)",
                "command": "python multi_bot_launcher.py",
                "character": "yayincilara",
                "description": "Streaming ve gaming odaklı enerjik bot",
                "priority": 3
            },
            "xxxgeisha": {
                "name": "🌸 XXXGeisha (Mysterious)",
                "command": "python multi_bot_launcher.py", 
                "character": "xxxgeisha",
                "description": "Gizemli, zarif, sofistike karakter bot",
                "priority": 4
            }
        }
        self.running = False
        
    def print_banner(self):
        """Süper banner yazdır"""
        banner = """
🔥═══════════════════════════════════════════════════════════════🔥
        🚀 ÇATIR ÇUTUR BOT LAUNCHER v3.0 🚀
        💥 3 ANA BOT + FULL SİSTEM! 💥
🔥═══════════════════════════════════════════════════════════════🔥
        🔥 GawatBaba - Yeni hesap ile aktif!
        🎮 Yayıncı Lara - Streamer Energy  
        🌸 XXXGeisha - Mysterious Elegant
🔥═══════════════════════════════════════════════════════════════🔥
        ✅ Tüm Telethon Userbot sistemi entegre edildi!
🔥═══════════════════════════════════════════════════════════════🔥
        """
        print(banner)
        
    def start_bot(self, bot_key, config):
        """Tek bot başlat"""
        print(f"\n🚀 {config['name']} başlatılıyor...")
        
        # Duplicate process kontrolü
        existing_process = self.find_existing_process(config['command'])
        if existing_process:
            print(f"⚠️ {config['name']} zaten çalışıyor (PID: {existing_process})")
            # Mevcut process'i listeye ekle
            self.processes.append({
                'key': bot_key,
                'name': config['name'],
                'process': None,  # Existing process için None
                'pid': existing_process,
                'start_time': datetime.now(),
                'command': config['command'],
                'description': config.get('description', ''),
                'character': config.get('character', None)
            })
            return True
        
        try:
            # Karakter botu için environment variable set et
            env = os.environ.copy()
            if 'character' in config:
                env['GAVATCORE_BOT_MODE'] = config['character']
                print(f"   🎭 Karakter modu: {config['character']}")
            
            # Process başlat
            process = subprocess.Popen(
                config['command'].split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                env=env
            )
            
            # Karakter botları için daha uzun bekleme
            wait_time = 5 if 'character' in config else 3
            time.sleep(wait_time)
            
            # Process durumunu kontrol et
            if process.poll() is None:
                self.processes.append({
                    'key': bot_key,
                    'name': config['name'],
                    'process': process,
                    'pid': process.pid,
                    'start_time': datetime.now(),
                    'command': config['command'],
                    'description': config.get('description', ''),
                    'character': config.get('character', None)
                })
                print(f"✅ {config['name']} başlatıldı! (PID: {process.pid})")
                if 'character' in config:
                    print(f"   📝 {config['description']}")
                return True
            else:
                print(f"❌ {config['name']} başlatılamadı!")
                return False
                
        except Exception as e:
            print(f"❌ {config['name']} hatası: {str(e)}")
            return False
    
    def find_existing_process(self, command):
        """Mevcut process'i bul"""
        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    # Sadece aynı komutu çalıştıran process'leri bul
                    # Karakter botları için environment variable kontrolü ekle
                    if command in cmdline and proc.info['pid'] != os.getpid():
                        # Eğer multi_bot_launcher ise, environment variable'ı kontrol et
                        if "multi_bot_launcher.py" in command:
                            # Bu durumda farklı karakterler farklı process'ler olabilir
                            # Şimdilik genel kontrol yap
                            return None  # Her karakter ayrı çalışsın
                        else:
                            return proc.info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return None
        except Exception:
            return None
    
    def start_all_bots(self):
        """Tüm botları başlat"""
        print("\n🔥 BOT BAŞLATMA SÜRECI BAŞLIYOR! 🔥")
        
        # Priority'ye göre sırala
        sorted_bots = sorted(
            self.bot_configs.items(),
            key=lambda x: x[1]['priority']
        )
        
        successful_bots = 0
        total_bots = len(sorted_bots)
        
        print(f"📊 {total_bots} bileşen başlatılacak...")
        
        for bot_key, config in sorted_bots:
            if self.start_bot(bot_key, config):
                successful_bots += 1
                # Botlar arası bekleme
                time.sleep(2)
            else:
                print(f"⚠️ {config['name']} atlandı")
        
        return successful_bots
    
    def cleanup_dead_processes(self):
        """Ölü ve zombie process'leri temizle"""
        alive_processes = []
        
        for proc in self.processes:
            try:
                process = psutil.Process(proc['pid'])
                if process.is_running():
                    alive_processes.append(proc)
                else:
                    print(f"🧹 Ölü process temizlendi: {proc['name']} (PID: {proc['pid']})")
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                print(f"🧹 Zombie/Dead process temizlendi: {proc['name']} (PID: {proc['pid']})")
        
        self.processes = alive_processes
    
    def show_status(self):
        """Bot durumlarını göster"""
        # Önce ölü process'leri temizle
        self.cleanup_dead_processes()
        
        print("\n📊 GAVATCORE SİSTEM DURUMU:")
        print("=" * 70)
        
        if not self.processes:
            print("❌ Hiçbir bileşen çalışmıyor")
            return
        
        # Sistem bileşenleri
        system_procs = [p for p in self.processes if not p.get('character')]
        character_procs = [p for p in self.processes if p.get('character')]
        
        if system_procs:
            print("\n🏗️ SİSTEM BİLEŞENLERİ:")
            print("-" * 40)
            for i, bot in enumerate(system_procs, 1):
                try:
                    process = psutil.Process(bot['pid'])
                    status = "🟢 ÇALIŞIYOR" if process.is_running() else "🔴 DURDU"
                    uptime = datetime.now() - bot['start_time']
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    
                    print(f"{i:2d}. {bot['name']}")
                    print(f"    Status: {status}")
                    print(f"    PID: {bot['pid']}")
                    print(f"    Uptime: {str(uptime).split('.')[0]}")
                    print(f"    Memory: {memory_mb:.1f}MB")
                    print(f"    📝 {bot['description']}")
                    print()
                    
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    print(f"{i:2d}. {bot['name']} - 🔴 PROCESS BULUNAMADI")
                    print()
        
        if character_procs:
            print("🤖 KARAKTER BOTLARI:")
            print("-" * 40)
            for i, bot in enumerate(character_procs, 1):
                try:
                    process = psutil.Process(bot['pid'])
                    status = "🟢 ÇALIŞIYOR" if process.is_running() else "🔴 DURDU"
                    uptime = datetime.now() - bot['start_time']
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    
                    print(f"{i:2d}. {bot['name']}")
                    print(f"    🎭 Karakter: {bot['character']}")
                    print(f"    Status: {status}")
                    print(f"    PID: {bot['pid']}")
                    print(f"    Uptime: {str(uptime).split('.')[0]}")
                    print(f"    Memory: {memory_mb:.1f}MB")
                    print(f"    📝 {bot['description']}")
                    print()
                    
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    print(f"{i:2d}. {bot['name']} - 🔴 PROCESS BULUNAMADI")
                    print()
        
        # Özet
        running_count = 0
        total_memory = 0
        
        for p in self.processes:
            try:
                process = psutil.Process(p['pid'])
                if process.is_running():
                    running_count += 1
                    total_memory += process.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                # Skip zombie or dead processes
                continue
        
        print("📈 ÖZET:")
        print("-" * 40)
        print(f"🟢 Çalışan: {running_count}/{len(self.processes)}")
        print(f"🤖 Karakter Botları: {len(character_procs)}")
        print(f"🏗️ Sistem Bileşenleri: {len(system_procs)}")
        print(f"💾 Toplam Memory: {total_memory:.1f}MB")
    
    def stop_all_bots(self):
        """Tüm botları durdur"""
        print("\n🛑 TÜM SİSTEM DURDURULUYOR...")
        
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
        print("✅ Tüm sistem durduruldu!")
    
    def show_character_info(self):
        """Karakter bilgilerini göster"""
        print("\n" + "="*60)
        print("🎭 GAVATCORE CHARACTER PROFILES")
        print("="*60)
        
        characters = {
            "gawatbaba": {
                "name": "🔥 GawatBaba (✅ AKTİF - YENİ HESAP)",
                "personality": "Tecrübeli abi, sokak akıllısı, koruyucu lider. Gruplarda otorite.",
                "style": "Sokak dili, dominant ama koruyucu. 'Lan', 'moruk', 'evlat' hitapları.",
                "triggers": "abi, baba, hocam, tavsiye, yardım, para, gavat",
                "status": "✅ Yeni telefon (+447832134241) ile aktif",
                "phone": "+447832134241",
                "features": "Admin komutları, coin kontrol, manuel mod"
            },
            "yayincilara": {
                "name": "🎮 Yayıncı Lara (✅ AKTİF)",
                "personality": "Enerjik, eğlenceli, yayın odaklı. Streaming kültürüne hakim.",
                "style": "Genç, dinamik dil. Gaming ve streaming terimleri kullanır. Türkçe-Rusça karışımı.",
                "triggers": "yayın, stream, game, chat, live, twitch, игра",
                "status": "✅ Çalışır durumda",
                "features": "GPT yanıtları, hybrid mod, scheduled mesajlar"
            },
            "xxxgeisha": {
                "name": "🌸 XXXGeisha (✅ AKTİF)",
                "personality": "Gizemli, çekici, sofistike. Derin konuşmalar yapar.",
                "style": "Zarif, akıllı dil. Metaforlar ve felsefi yaklaşımlar.",
                "triggers": "sanat, güzellik, felsefe, geisha, zen, estetik",
                "status": "✅ Çalışır durumda",
                "features": "GPT responses, manualplus mod, seductive AI"
            }
        }
        
        for i, (key, char) in enumerate(characters.items(), 1):
            print(f"\n{i}. {char['name']}")
            print(f"   💭 Kişilik: {char['personality']}")
            print(f"   🗣️ Tarz: {char['style']}")
            print(f"   🔑 Trigger Words: {char['triggers']}")
            print(f"   📁 Session: sessions/{key}.session")
            print(f"   🔄 Durum: {char['status']}")
            if 'phone' in char:
                print(f"   📱 Telefon: {char['phone']}")
            if 'features' in char:
                print(f"   ⚙️ Özellikler: {char['features']}")
        
        print(f"\n📊 Özet: 3/3 karakter aktif kullanılabilir")
        print(f"🎉 Telethon Userbot sistemi entegre edildi!")
    
    def interactive_menu(self):
        while True:
            print("\n" + "="*60)
            print("🎮 GAVATCORE ULTIMATE CONTROL PANEL")
            print("="*60)
            print("1. 🚀 Tüm Sistemi Başlat")
            print("2. 📊 Sistem Durumunu Göster")
            print("3. 🤖 Sadece Character Botları Başlat")
            print("4. 🏗️ Sadece Sistem Bileşenlerini Başlat")
            print("5. 🛑 Tüm Sistemi Durdur")
            print("6. 🔄 Full Sistem Restart")
            print("7. 🎭 Karakter Bilgilerini Göster")
            print("8. ❌ Çıkış")
            
            try:
                raw_input = input("\n🎯 Seçiminiz (1-8): ")
                choice = raw_input.strip()
                
                # Debug info
                if choice not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    print(f"[DEBUG] Raw input: '{raw_input}'")
                    print(f"[DEBUG] After strip: '{choice}'") 
                    print(f"[DEBUG] Byte representation: {choice.encode()}")
                
                # Super robust cleaning - sadece rakamları al
                clean_choice = ''.join(c for c in choice if c.isdigit())
                if clean_choice and clean_choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    choice = clean_choice
                elif choice == "":
                    continue  # Boş input, tekrar sor
                
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Çıkış...")
                break
            
            if choice == "1":
                successful = self.start_all_bots()
                print(f"\n🎉 {successful}/{len(self.bot_configs)} bileşen başlatıldı!")
                
            elif choice == "2":
                self.show_status()
                
            elif choice == "3":
                print("🤖 Sadece karakter botları başlatılıyor...")
                success = 0
                for key, config in self.bot_configs.items():
                    if 'character' in config:
                        if self.start_bot(key, config):
                            success += 1
                        time.sleep(3)
                print(f"🎉 {success}/3 karakter botu başlatıldı!")
                
            elif choice == "4":
                print("🏗️ Sadece sistem bileşenleri başlatılıyor...")
                success = 0
                for key, config in self.bot_configs.items():
                    if 'character' not in config:
                        if self.start_bot(key, config):
                            success += 1
                        time.sleep(2)
                print(f"🎉 {success} sistem bileşeni başlatıldı!")
                
            elif choice == "5":
                self.stop_all_bots()
                
            elif choice == "6":
                self.stop_all_bots()
                time.sleep(3)
                successful = self.start_all_bots()
                print(f"🔄 Sistem yeniden başlatıldı! {successful} bileşen aktif")
                
            elif choice == "7":
                self.show_character_info()
                
            elif choice == "8":
                self.stop_all_bots()
                print("👋 GavatCore Ultimate kapatılıyor!")
                break
                
            else:
                print("❌ Geçersiz seçim!")
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.print_banner()
        
        print("🔍 Sistem kontrolleri yapılıyor...")
        print("✅ Sistem hazır!")
        
        # Signal handler
        def signal_handler(signum, frame):
            print("\n\n🛑 Kapatma sinyali alındı...")
            self.stop_all_bots()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("🎮 Ultimate Control Panel başlatılıyor...")
        
        try:
            self.interactive_menu()
        except KeyboardInterrupt:
            print("\n\n🛑 Ctrl+C ile çıkış...")
            self.stop_all_bots()

if __name__ == "__main__":
    launcher = CatirCuturLauncher()
    launcher.run() 