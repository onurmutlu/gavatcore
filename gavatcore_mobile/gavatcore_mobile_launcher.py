#!/usr/bin/env python3
"""
🚀 GAVATCORE V3 MOBILE APP LAUNCHER
"Delikanlı Gibi Yazılımcı" - Mobile Edition

YAŞASIN SPONSORLAR! 🔥
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class GavatCoreMobileLauncher:
    def __init__(self):
        self.project_name = "GavatCore V3 Mobile"
        self.flutter_project_path = Path(__file__).parent
        self.start_time = time.time()
        
    def print_banner(self):
        """Epic banner yazdır"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚀 GAVATCORE V3 MOBILE APP LAUNCHER 🚀                   ║
║                                                              ║
║    "Delikanlı Gibi Yazılımcı" - Mobile Edition              ║
║                                                              ║
║    📱 Flutter + Dart + GavatCore V2 API                     ║
║    🎯 iOS & Android Native Performance                      ║
║    🔥 AI-Powered Bot Management                              ║
║    💎 Premium Features & Analytics                          ║
║                                                              ║
║    YAŞASIN SPONSORLAR! 🔥                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_flutter_installation(self):
        """Flutter kurulu mu kontrol et"""
        try:
            result = subprocess.run(['flutter', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Flutter kurulu ve hazır!")
                print(f"   {result.stdout.split()[1]} {result.stdout.split()[2]}")
                return True
            else:
                print("❌ Flutter kurulu değil!")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Flutter bulunamadı!")
            return False
    
    def install_flutter_guide(self):
        """Flutter kurulum rehberi"""
        print("\n🔧 FLUTTER KURULUM REHBERİ:")
        print("=" * 50)
        print("1. Flutter SDK'yı indirin:")
        print("   https://flutter.dev/docs/get-started/install")
        print()
        print("2. macOS için:")
        print("   brew install flutter")
        print()
        print("3. PATH'e ekleyin:")
        print("   export PATH=\"$PATH:`pwd`/flutter/bin\"")
        print()
        print("4. Flutter doctor çalıştırın:")
        print("   flutter doctor")
        print()
        print("5. Bu script'i tekrar çalıştırın!")
        print("=" * 50)
    
    def check_project_structure(self):
        """Proje yapısını kontrol et"""
        required_files = [
            'pubspec.yaml',
            'lib/main.dart',
            'lib/shared/themes/app_theme.dart',
            'lib/core/storage/storage_service.dart',
            'lib/features/auth/presentation/pages/login_page.dart',
            'lib/features/dashboard/presentation/pages/dashboard_page.dart'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.flutter_project_path / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Eksik dosyalar:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        print("✅ Proje yapısı tamamlanmış!")
        return True
    
    def run_flutter_commands(self):
        """Flutter komutlarını çalıştır"""
        commands = [
            ("flutter clean", "Proje temizleniyor..."),
            ("flutter pub get", "Dependencies yükleniyor..."),
            ("flutter analyze", "Kod analizi yapılıyor..."),
        ]
        
        for command, description in commands:
            print(f"\n🔄 {description}")
            try:
                result = subprocess.run(command.split(), 
                                      cwd=self.flutter_project_path,
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✅ {description.replace('...', '')} tamamlandı!")
                else:
                    print(f"⚠️ {description.replace('...', '')} uyarıları:")
                    print(result.stderr)
            except subprocess.TimeoutExpired:
                print(f"⏰ {description.replace('...', '')} zaman aşımı!")
            except Exception as e:
                print(f"❌ {description.replace('...', '')} hatası: {e}")
    
    def show_available_devices(self):
        """Kullanılabilir cihazları göster"""
        try:
            result = subprocess.run(['flutter', 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("\n📱 KULLANILABILIR CİHAZLAR:")
                print("=" * 40)
                print(result.stdout)
            else:
                print("❌ Cihaz listesi alınamadı!")
        except Exception as e:
            print(f"❌ Cihaz listesi hatası: {e}")
    
    def run_app(self, device=None):
        """Uygulamayı çalıştır"""
        print("\n🚀 GAVATCORE V3 MOBILE APP BAŞLATILIYOR!")
        print("=" * 50)
        
        command = ['flutter', 'run']
        if device:
            command.extend(['-d', device])
        
        try:
            print("📱 Uygulama başlatılıyor...")
            print("   Hot reload için 'r' tuşuna basın")
            print("   Hot restart için 'R' tuşuna basın")
            print("   Çıkmak için 'q' tuşuna basın")
            print()
            
            subprocess.run(command, cwd=self.flutter_project_path)
            
        except KeyboardInterrupt:
            print("\n🛑 Uygulama kullanıcı tarafından durduruldu!")
        except Exception as e:
            print(f"❌ Uygulama başlatma hatası: {e}")
    
    def show_project_info(self):
        """Proje bilgilerini göster"""
        elapsed_time = time.time() - self.start_time
        
        print("\n📊 PROJE BİLGİLERİ:")
        print("=" * 40)
        print(f"📱 Proje: {self.project_name}")
        print(f"📂 Konum: {self.flutter_project_path}")
        print(f"⏰ Hazırlık süresi: {elapsed_time:.1f} saniye")
        print(f"🎯 Platform: iOS & Android")
        print(f"🔧 Framework: Flutter 3.19.0+")
        print(f"💾 State Management: Riverpod")
        print(f"🎨 UI: Material Design 3")
        print(f"🔐 Storage: Hive")
        print("=" * 40)
    
    def interactive_menu(self):
        """Interaktif menü"""
        while True:
            print("\n🎮 GAVATCORE V3 MOBILE LAUNCHER MENÜ:")
            print("=" * 40)
            print("1. 📱 Uygulamayı Çalıştır")
            print("2. 🔍 Cihazları Listele")
            print("3. 🔧 Flutter Komutları Çalıştır")
            print("4. 📊 Proje Bilgileri")
            print("5. 🚪 Çıkış")
            print("=" * 40)
            
            choice = input("Seçiminizi yapın (1-5): ").strip()
            
            if choice == '1':
                device = input("Cihaz ID (boş bırakın varsayılan için): ").strip()
                self.run_app(device if device else None)
            elif choice == '2':
                self.show_available_devices()
            elif choice == '3':
                self.run_flutter_commands()
            elif choice == '4':
                self.show_project_info()
            elif choice == '5':
                print("\n👋 Görüşürüz! YAŞASIN SPONSORLAR! 🔥")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 1-5 arası bir sayı girin.")
    
    def launch(self):
        """Ana launcher fonksiyonu"""
        self.print_banner()
        
        # Flutter kontrolü
        if not self.check_flutter_installation():
            self.install_flutter_guide()
            return
        
        # Proje yapısı kontrolü
        if not self.check_project_structure():
            print("\n❌ Proje yapısı eksik! Lütfen dosyaları kontrol edin.")
            return
        
        print("\n🎉 GavatCore V3 Mobile App hazır!")
        print("   Tüm kontroller başarılı!")
        
        # Interaktif menü
        self.interactive_menu()

def main():
    """Ana fonksiyon"""
    launcher = GavatCoreMobileLauncher()
    launcher.launch()

if __name__ == "__main__":
    main() 