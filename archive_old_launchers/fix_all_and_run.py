#!/usr/bin/env python3
"""
🚀 GAVATCore Full Otomasyon - Tek Tuşla Her Şey!
"""

import os
import sys
import subprocess
import time
import shutil
import signal
import sqlite3
from pathlib import Path

class GAVATCoreAutoFixer:
    def __init__(self):
        self.errors_fixed = 0
        self.warnings = []
        
    def print_banner(self):
        """Başlangıç banner'ı"""
        print("🔥" + "="*60 + "🔥")
        print("🚀 GAVATCore FULL OTOMASYON SİSTEMİ 🚀")
        print("💪 Tek tuşla her şey çalışacak!")
        print("🔥" + "="*60 + "🔥")
        print()
        
    def fix_database_locks(self):
        """Database lock sorunlarını çöz"""
        print("🔧 Database lock sorunları düzeltiliyor...")
        
        # Tüm .session-journal dosyalarını sil
        journal_files = list(Path("sessions").glob("*.session-journal"))
        for journal in journal_files:
            try:
                os.remove(journal)
                print(f"✅ Silindi: {journal}")
                self.errors_fixed += 1
            except:
                pass
        
        # SQLite WAL dosyalarını temizle
        wal_files = list(Path(".").glob("**/*.db-wal"))
        shm_files = list(Path(".").glob("**/*.db-shm"))
        
        for wal in wal_files + shm_files:
            try:
                os.remove(wal)
                print(f"✅ Temizlendi: {wal}")
                self.errors_fixed += 1
            except:
                pass
                
        # Session dosyalarını kontrol et ve düzelt
        session_files = list(Path("sessions").glob("*.session"))
        for session in session_files:
            try:
                # Dosyayı aç ve kapat (lock'u kaldır)
                conn = sqlite3.connect(str(session))
                conn.execute("PRAGMA journal_mode=DELETE")
                conn.close()
                print(f"✅ Session düzeltildi: {session.name}")
                self.errors_fixed += 1
            except Exception as e:
                print(f"⚠️ Session düzeltilemedi: {session.name} - {e}")
                self.warnings.append(f"Session sorunu: {session.name}")
                
    def kill_existing_processes(self):
        """Çalışan process'leri kapat"""
        print("\n🔪 Eski process'ler kapatılıyor...")
        
        # Port'ları kontrol et
        ports = [5050, 5051, 5005, 9095]
        for port in ports:
            try:
                # lsof komutu ile port'u kullanan process'i bul
                result = subprocess.run(
                    f"lsof -ti:{port}", 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            print(f"✅ Port {port} temizlendi (PID: {pid})")
                            self.errors_fixed += 1
                        except:
                            pass
            except:
                pass
                
        # Python process'lerini kontrol et
        bot_processes = ["bot_system.py", "lara_bot_launcher.py", "production_bot_api.py"]
        for proc in bot_processes:
            try:
                subprocess.run(f"pkill -f {proc}", shell=True)
                print(f"✅ {proc} process'leri kapatıldı")
            except:
                pass
                
    def create_missing_files(self):
        """Eksik dosyaları oluştur"""
        print("\n📁 Eksik dosyalar oluşturuluyor...")
        
        # __init__.py dosyaları
        init_dirs = [
            "handlers",
            "services",
            "services/telegram", 
            "services/telegram/bot_manager",
            "services/telegram/monitors",
            "utilities",
            "core",
            "modules",
            "modules/auth",
            "modules/analytics",
            "modules/payments"
        ]
        
        for dir_path in init_dirs:
            os.makedirs(dir_path, exist_ok=True)
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                Path(init_file).touch()
                print(f"✅ Oluşturuldu: {init_file}")
                self.errors_fixed += 1
                
    def move_handlers_to_services(self):
        """Handler'ları services/telegram'a taşı"""
        print("\n📦 Handler'lar taşınıyor...")
        
        if os.path.exists("handlers"):
            handlers = list(Path("handlers").glob("*.py"))
            target_dir = Path("services/telegram")
            os.makedirs(target_dir, exist_ok=True)
            
            for handler in handlers:
                if "lara" in handler.name or "bot" in handler.name:
                    target = target_dir / handler.name
                    if not target.exists():
                        shutil.copy2(handler, target)
                        print(f"✅ Taşındı: {handler.name} → services/telegram/")
                        self.errors_fixed += 1
                        
    def fix_imports_in_launchers(self):
        """Launcher'lardaki import'ları düzelt"""
        print("\n🔧 Import path'leri düzeltiliyor...")
        
        launcher_files = [
            "launchers/lara_bot_launcher.py",
            "launchers/gavatcore_ultimate_launcher.py",
            "launchers/auto_session_bot_launcher.py"
        ]
        
        for launcher in launcher_files:
            if os.path.exists(launcher):
                try:
                    with open(launcher, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Import düzeltmeleri
                    replacements = [
                        ("from handlers.", "from services.telegram."),
                        ("from utilities.", "from utilities."),
                        ("from utils.", "from utilities.")
                    ]
                    
                    modified = False
                    for old, new in replacements:
                        if old in content:
                            content = content.replace(old, new)
                            modified = True
                    
                    if modified:
                        with open(launcher, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Import'lar düzeltildi: {launcher}")
                        self.errors_fixed += 1
                        
                except Exception as e:
                    print(f"⚠️ Import düzeltme hatası: {launcher} - {e}")
                    self.warnings.append(f"Import sorunu: {launcher}")
                    
    def create_unified_launcher(self):
        """Tek tuşla çalışan unified launcher oluştur"""
        print("\n🚀 Unified launcher oluşturuluyor...")
        
        launcher_code = '''#!/usr/bin/env python3
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
                
        print(f"\\n✅ {success_count}/{len(components)} bileşen başlatıldı!")
        
        if success_count > 0:
            print("\\n🎯 Sistem çalışıyor! Ctrl+C ile durdurun.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\\n🛑 Sistem durduruluyor...")
                for name, process in self.processes:
                    try:
                        process.terminate()
                        print(f"🔴 {name} durduruldu")
                    except:
                        pass
        else:
            print("\\n❌ Sistem başlatılamadı!")
            sys.exit(1)

if __name__ == "__main__":
    launcher = UnifiedLauncher()
    launcher.run()
'''
        
        with open("start_everything.py", "w") as f:
            f.write(launcher_code)
        os.chmod("start_everything.py", 0o755)
        print("✅ start_everything.py oluşturuldu")
        self.errors_fixed += 1
        
    def run_diagnostics(self):
        """Sistem diagnostiği"""
        print("\n🔍 Sistem Diagnostiği...")
        
        checks = {
            "config.py": os.path.exists("config.py"),
            "sessions klasörü": os.path.exists("sessions"),
            "services/telegram": os.path.exists("services/telegram"),
            "APIs klasörü": os.path.exists("apis"),
            "Database dosyaları": len(list(Path(".").glob("**/*.db"))) > 0
        }
        
        all_good = True
        for check, result in checks.items():
            if result:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                all_good = False
                self.warnings.append(f"Eksik: {check}")
                
        return all_good
        
    def run_full_automation(self):
        """Full otomasyon çalıştır"""
        self.print_banner()
        
        # 1. Process'leri kapat
        self.kill_existing_processes()
        
        # 2. Database lock'larını düzelt
        self.fix_database_locks()
        
        # 3. Eksik dosyaları oluştur
        self.create_missing_files()
        
        # 4. Handler'ları taşı
        self.move_handlers_to_services()
        
        # 5. Import'ları düzelt
        self.fix_imports_in_launchers()
        
        # 6. Unified launcher oluştur
        self.create_unified_launcher()
        
        # 7. Diagnostik
        system_ok = self.run_diagnostics()
        
        # Sonuç raporu
        print("\n" + "="*60)
        print(f"✅ OTOMASYON TAMAMLANDI!")
        print(f"🔧 Düzeltilen sorun: {self.errors_fixed}")
        print(f"⚠️  Uyarı sayısı: {len(self.warnings)}")
        
        if self.warnings:
            print("\n⚠️ UYARILAR:")
            for warning in self.warnings:
                print(f"   - {warning}")
                
        print("\n🚀 SİSTEMİ BAŞLATMAK İÇİN:")
        print("   python start_everything.py")
        print("\n💡 VEYA MANUEL BAŞLATMA:")
        print("   python run.py")
        print("\n" + "="*60)
        
        # Otomatik başlat
        if system_ok:
            print("\n🎯 Sistem 3 saniye sonra otomatik başlatılacak...")
            time.sleep(3)
            subprocess.run([sys.executable, "start_everything.py"])

if __name__ == "__main__":
    fixer = GAVATCoreAutoFixer()
    fixer.run_full_automation() 