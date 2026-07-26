#!/usr/bin/env python3
"""
🔥 MASTER BOT AUTOMATION - TAM OTOMATİK SİSTEM 🔥
================================================

Her şey otomatik çalışır:
- Persona JSON'lardan telefon numaraları otomatik alınır
- Session dosyaları otomatik kullanılır  
- Telefon numarası sormaz
- 3 bot birlikte çalışır
- Monitoring API otomatik başlar
- Flutter dashboard otomatik açılır

SEN HİÇ BİR ŞEY YAPMA - HER ŞEY OTOMATİK!
"""

import asyncio
import subprocess
import time
import json
import os
import signal
import sys
from datetime import datetime
from typing import Dict, List
import multiprocessing
from pathlib import Path

class MasterBotAutomation:
    """Master Bot Otomasyon Sistemi - Her şey otomatik"""
    
    def __init__(self):
        self.processes = {}
        self.api_process = None
        self.flutter_process = None
        self.running = False
        
        # Bot konfigürasyonları (persona JSON'lardan otomatik)
        self.bot_configs = {
            "lara": {
                "persona_file": "data/personas/yayincilara.json",
                "launcher_script": "lara_bot_launcher.py",
                "expected_phone": "+905382617727",
                "display_name": "Lara - Flörtöz Yayıncı"
            },
            "babagavat": {
                "persona_file": "data/personas/babagavat.json", 
                "launcher_script": "babagavat_simple_launcher.py",  # Basit launcher oluşturacağız
                "expected_phone": "+905513272355",
                "display_name": "BabaGavat - Pavyon Lideri"
            },
            "baron": {
                "persona_file": "data/personas/baron.json",
                "launcher_script": "baron_simple_launcher.py",
                "expected_phone": "+905325566496",
                "display_name": "BaronBaba - Sokak Lideri"
            },
            "geisha": {
                "persona_file": "data/personas/xxxgeisha.json",
                "launcher_script": "geisha_simple_launcher.py",  # Basit launcher oluşturacağız
                "expected_phone": "+905486306226", 
                "display_name": "Geisha - Vamp Moderatör"
            }
        }
    
    def load_persona_data(self, bot_name: str) -> Dict:
        """Persona JSON dosyasından bot bilgilerini otomatik yükle"""
        config = self.bot_configs[bot_name]
        persona_file = config["persona_file"]
        
        if not os.path.exists(persona_file):
            print(f"❌ {bot_name} persona dosyası bulunamadı: {persona_file}")
            return {}
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
            
            phone = persona_data.get('phone', config["expected_phone"])
            clean_phone = phone.replace('+', '')
            session_path = f"sessions/_{clean_phone}.session"
            
            print(f"✅ {bot_name.upper()} persona yüklendi:")
            print(f"   📱 Telefon: {phone}")
            print(f"   💾 Session: {session_path}")
            print(f"   👤 Username: @{persona_data.get('username', bot_name)}")
            
            return {
                "phone": phone,
                "session_path": session_path,
                "username": persona_data.get('username', bot_name),
                "display_name": persona_data.get('display_name', bot_name),
                "persona_data": persona_data
            }
            
        except Exception as e:
            print(f"❌ {bot_name} persona yükleme hatası: {e}")
            return {}
    
    def verify_session_files(self) -> bool:
        """Tüm session dosyalarını kontrol et"""
        print("\n🔍 SESSION DOSYALARI KONTROL EDİLİYOR:")
        print("=" * 50)
        
        all_valid = True
        
        for bot_name, config in self.bot_configs.items():
            persona = self.load_persona_data(bot_name)
            if not persona:
                all_valid = False
                continue
            
            session_path = persona["session_path"]
            
            if not os.path.exists(session_path):
                print(f"❌ {bot_name}: Session dosyası bulunamadı!")
                all_valid = False
                continue
            
            size_kb = os.path.getsize(session_path) / 1024
            
            if size_kb < 10:
                print(f"⚠️ {bot_name}: Session dosyası çok küçük ({size_kb:.1f}KB)")
            else:
                print(f"✅ {bot_name}: Session hazır ({size_kb:.1f}KB)")
        
        print("=" * 50)
        return all_valid
    
    def create_simple_bot_launchers(self):
        """BabaGavat ve Geisha için basit launcher'lar oluştur"""
        
        # BabaGavat Simple Launcher
        babagavat_launcher = '''#!/usr/bin/env python3
import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import User
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from datetime import datetime

class BabaGavatSimpleLauncher:
    def __init__(self):
        self.client = None
        
    async def start(self):
        print("🔥 BabaGavat Bot başlatılıyor...")
        
        # Persona dosyasından telefon al
        with open('data/personas/babagavat.json', 'r', encoding='utf-8') as f:
            persona = json.load(f)
        
        phone = persona.get('phone', '+905513272355')
        clean_phone = phone.replace('+', '')
        session_path = f'sessions/_{clean_phone}'
        
        print(f"📱 Telefon: {phone}")
        print(f"💾 Session: {session_path}")
        
        self.client = TelegramClient(
            session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH,
            device_model="BabaGavat Bot", system_version="GAVATCore v2.0"
        )
        
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ BabaGavat aktif: @{me.username} (ID: {me.id})")
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, 'bot', False):
                    print(f"💬 BabaGavat DM: {sender.first_name} -> {event.raw_text[:30]}...")
        
        print("🔥 BabaGavat hazır - mesajları dinliyor!")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    launcher = BabaGavatSimpleLauncher()
    asyncio.run(launcher.start())
'''
        
        # Baron Simple Launcher
        baron_launcher = '''#!/usr/bin/env python3
import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import User
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from datetime import datetime

class BaronSimpleLauncher:
    def __init__(self):
        self.client = None
        
    async def start(self):
        print("🔥 BaronBaba Bot başlatılıyor...")
        
        # Persona dosyasından telefon al
        with open('data/personas/baron.json', 'r', encoding='utf-8') as f:
            persona = json.load(f)
        
        phone = persona.get('phone', '+905325566496')
        clean_phone = phone.replace('+', '')
        session_path = f'sessions/_{clean_phone}'
        
        print(f"📱 Telefon: {phone}")
        print(f"💾 Session: {session_path}")
        
        self.client = TelegramClient(
            session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH,
            device_model="BaronBaba Bot", system_version="GAVATCore v2.0"
        )
        
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ BaronBaba aktif: @{me.username} (ID: {me.id})")
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, 'bot', False):
                    print(f"💬 BaronBaba DM: {sender.first_name} -> {event.raw_text[:30]}...")
        
        print("🔥 BaronBaba hazır - mesajları dinliyor!")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    launcher = BaronSimpleLauncher()
    asyncio.run(launcher.start())
'''

        # Geisha Simple Launcher  
        geisha_launcher = '''#!/usr/bin/env python3
import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import User
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from datetime import datetime

class GeishaSimpleLauncher:
    def __init__(self):
        self.client = None
        
    async def start(self):
        print("💋 Geisha Bot başlatılıyor...")
        
        # Persona dosyasından telefon al
        with open('data/personas/xxxgeisha.json', 'r', encoding='utf-8') as f:
            persona = json.load(f)
        
        phone = persona.get('phone', '+905486306226')
        clean_phone = phone.replace('+', '')
        session_path = f'sessions/_{clean_phone}'
        
        print(f"📱 Telefon: {phone}")
        print(f"💾 Session: {session_path}")
        
        self.client = TelegramClient(
            session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH,
            device_model="Geisha Bot", system_version="GAVATCore v2.0"
        )
        
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ Geisha aktif: @{me.username} (ID: {me.id})")
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                sender = await event.get_sender()
                if sender and not getattr(sender, 'bot', False):
                    print(f"💬 Geisha DM: {sender.first_name} -> {event.raw_text[:30]}...")
        
        print("🔥 Geisha hazır - mesajları dinliyor!")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    launcher = GeishaSimpleLauncher()
    asyncio.run(launcher.start())
'''
        
        # Dosyaları oluştur
        with open('babagavat_simple_launcher.py', 'w', encoding='utf-8') as f:
            f.write(babagavat_launcher)
        
        with open('baron_simple_launcher.py', 'w', encoding='utf-8') as f:
            f.write(baron_launcher)
        
        with open('geisha_simple_launcher.py', 'w', encoding='utf-8') as f:
            f.write(geisha_launcher)
        
        # Executable yap
        os.chmod('babagavat_simple_launcher.py', 0o755)
        os.chmod('baron_simple_launcher.py', 0o755)
        os.chmod('geisha_simple_launcher.py', 0o755)
        
        print("✅ Basit bot launcher'ları oluşturuldu!")
    
    def start_monitoring_api(self) -> bool:
        """Monitoring API'sini başlat"""
        print("\n🚀 MONİTORİNG API BAŞLATILIYOR...")
        
        try:
            # Port 5005'i kullan (gerçek API)
            # Önce doğru API dosyasını bul
            api_files = [
                "apis/real_bot_api_no_mock.py",
                "apis/real_bot_management_api.py",
                "apis/production_bot_api.py"
            ]
            
            api_script = None
            for api_file in api_files:
                if os.path.exists(api_file):
                    api_script = api_file
                    break
            
            if not api_script:
                print("❌ Monitoring API script bulunamadı")
                return False
            
            self.api_process = subprocess.Popen(
                ["python3", api_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 3 saniye bekle
            time.sleep(3)
            
            # API'nin çalışıp çalışmadığını kontrol et
            if self.api_process.poll() is None:
                print(f"✅ Monitoring API başlatıldı (Script: {api_script})")
                return True
            else:
                print("❌ Monitoring API başlatılamadı")
                return False
                
        except Exception as e:
            print(f"❌ API başlatma hatası: {e}")
            return False
    
    def start_bot(self, bot_name: str) -> bool:
        """Tek bot başlat"""
        config = self.bot_configs[bot_name]
        launcher_script = config["launcher_script"]
        display_name = config["display_name"]
        
        print(f"\n🤖 {display_name.upper()} BAŞLATILIYOR...")
        
        try:
            process = subprocess.Popen(
                ["python3", launcher_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes[bot_name] = process
            
            # 2 saniye bekle
            time.sleep(2)
            
            # Process çalışıyor mu kontrol et
            if process.poll() is None:
                print(f"✅ {display_name} başlatıldı (PID: {process.pid})")
                return True
            else:
                print(f"❌ {display_name} başlatılamadı")
                return False
                
        except Exception as e:
            print(f"❌ {display_name} başlatma hatası: {e}")
            return False
    
    def start_all_bots(self) -> Dict[str, bool]:
        """Tüm bot'ları başlat"""
        print("\n🚀 TÜM BOT'LAR BAŞLATILIYOR...")
        print("=" * 50)
        
        results = {}
        
        for bot_name in self.bot_configs.keys():
            success = self.start_bot(bot_name)
            results[bot_name] = success
            time.sleep(1)  # Bot'lar arası 1 saniye bekle
        
        return results
    
    def start_flutter_dashboard(self) -> bool:
        """Flutter admin panel'i başlat"""
        print("\n📱 FLUTTER DASHBOARD BAŞLATILIYOR...")
        
        try:
            # Yeni flutter panel dizini
            flutter_dir = "gavatcore_panel"
            if not os.path.exists(flutter_dir):
                # Eski dizini de kontrol et
                flutter_dir = "gavatcore_mobile"
                if not os.path.exists(flutter_dir):
                    print("❌ Flutter dizini bulunamadı (gavatcore_panel veya gavatcore_mobile)")
                    return False
            
            self.flutter_process = subprocess.Popen(
                ["flutter", "run", "-d", "web-server", "--web-port", "9095"],
                cwd=flutter_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print("✅ Flutter dashboard başlatıldı (Port 9095)")
            print("🌐 Dashboard: http://localhost:9095")
            return True
            
        except Exception as e:
            print(f"❌ Flutter başlatma hatası: {e}")
            return False
    
    def show_status(self):
        """Sistem durumunu göster"""
        print("\n📊 SİSTEM DURUMU:")
        print("=" * 50)
        
        # API durumu
        if self.api_process and self.api_process.poll() is None:
            print("✅ Monitoring API: Çalışıyor (Port 5005)")
        else:
            print("❌ Monitoring API: Çalışmıyor")
        
        # Bot durumları
        for bot_name, process in self.processes.items():
            display_name = self.bot_configs[bot_name]["display_name"]
            if process and process.poll() is None:
                print(f"✅ {display_name}: Çalışıyor (PID: {process.pid})")
            else:
                print(f"❌ {display_name}: Çalışmıyor")
        
        # Flutter durumu
        if self.flutter_process and self.flutter_process.poll() is None:
            print("✅ Flutter Dashboard: Çalışıyor (Port 9095)")
        else:
            print("❌ Flutter Dashboard: Çalışmıyor")
        
        print("=" * 50)
    
    def stop_all(self):
        """Tüm servisleri durdur"""
        print("\n🔴 TÜM SERVİSLER DURDURULUYOR...")
        
        # Bot'ları durdur
        for bot_name, process in self.processes.items():
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"🔴 {bot_name} durduruldu")
                except:
                    process.kill()
        
        # API'yi durdur
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("🔴 Monitoring API durduruldu")
            except:
                self.api_process.kill()
        
        # Flutter'ı durdur
        if self.flutter_process:
            try:
                self.flutter_process.terminate()
                self.flutter_process.wait(timeout=5)
                print("🔴 Flutter Dashboard durduruldu")
            except:
                self.flutter_process.kill()
        
        print("✅ Tüm servisler durduruldu")
    
    def run_full_automation(self):
        """TAM OTOMATİK SİSTEM - Her şeyi başlat"""
        print(f"""
🔥🔥🔥 MASTER BOT AUTOMATION 🔥🔥🔥
=====================================
🤖 {len(self.bot_configs)} Bot Otomatik Başlatılacak
📊 Monitoring API Otomatik
📱 Flutter Dashboard Otomatik  
❌ HİÇ BİR MANUEL İŞLEM YOK!
=====================================
Başlatma zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        try:
            # 1. Session dosyalarını kontrol et
            if not self.verify_session_files():
                print("❌ Session dosyaları eksik, devam edilemiyor!")
                return False
            
            # 2. Basit launcher'ları oluştur
            self.create_simple_bot_launchers()
            
            # 3. Monitoring API'sini başlat
            if not self.start_monitoring_api():
                print("⚠️ API başlatılamadı ama devam ediliyor...")
            
            # 4. Tüm bot'ları başlat
            bot_results = self.start_all_bots()
            success_count = sum(bot_results.values())
            
            print(f"\n🎯 BOT BAŞLATMA SONUCU: {success_count}/{len(self.bot_configs)} başarılı")
            
            # 5. Flutter dashboard'u başlat
            if not self.start_flutter_dashboard():
                print("⚠️ Flutter başlatılamadı ama devam ediliyor...")
            
            # 6. Final durum raporu
            time.sleep(3)
            self.show_status()
            
            print(f"""
🔥 MASTER AUTOMATION TAMAMLANDI! 🔥
==================================
📊 Monitoring: http://localhost:5005
📱 Dashboard: http://localhost:9095
🤖 {success_count}/{len(self.bot_configs)} bot aktif
==================================
🎯 Ctrl+C ile tüm sistemi durdur
            """)
            
            # 7. Sürekli çalışma
            self.running = True
            
            def signal_handler(sig, frame):
                print("\n⏹️ Sistem durdurma sinyali alındı...")
                self.running = False
                self.stop_all()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Ana loop
            while self.running:
                time.sleep(10)
                # Durumu kontrol et (isteğe bağlı)
            
            return True
            
        except Exception as e:
            print(f"❌ Master automation hatası: {e}")
            self.stop_all()
            return False

# Global instance
master_automation = MasterBotAutomation()

if __name__ == "__main__":
    print("🚀 MASTER BOT AUTOMATION BAŞLATILIYOR...")
    
    try:
        success = master_automation.run_full_automation()
        if not success:
            print("❌ Sistem başlatılamadı!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Kullanıcı tarafından durduruldu")
        master_automation.stop_all()
    except Exception as e:
        print(f"❌ Kritik hata: {e}")
        master_automation.stop_all()
        sys.exit(1) 