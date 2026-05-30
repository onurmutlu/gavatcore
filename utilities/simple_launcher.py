from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 Simple GavatCore Launcher (No Flutter) 🚀

API + Bots sistemi:
• Flask API Server (localhost:5050) 
• XP-enabled Production Bots
• GavatCoin Token Economy

Kullanım: python3 simple_launcher.py
"""

import subprocess
import sys
import time
import signal
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleGavatCoreLauncher:
    """Sadece API + Bots launcher"""
    
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_flask_api(self):
        """Flask API server'ı başlat"""
        try:
            logger.info("🌐 Flask API Server başlatılıyor (localhost:5050)...")
            
            process = subprocess.Popen([
                sys.executable, "apis/production_bot_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("Flask API", process))
            logger.info("✅ Flask API Server başlatıldı!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Flask API başlatma hatası: {e}")
            return False
    
    def start_production_bots(self):
        """XP-enabled production botları başlat"""
        try:
            logger.info("🤖 XP-enabled Production Bots başlatılıyor...")
            
            process = subprocess.Popen([
                sys.executable, "launchers/production_bot_launcher_xp.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("Production Bots", process))
            logger.info("✅ Production Bots başlatıldı!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Production bots başlatma hatası: {e}")
            return False
    
    def show_startup_info(self):
        """Başlangıç bilgilerini göster"""
        print("\n" + "🎮" + "="*50 + "🎮")
        print("🚀 Simple GavatCore Launcher")
        print("💰 API + XP-enabled Bots")
        print("🎮" + "="*50 + "🎮")
        print()
        print("📊 ACTIVE COMPONENTS:")
        print("   🌐 Flask API Server  → localhost:5050")
        print("   🤖 Production Bots (3) → Telegram")
        print("   💰 GavatCoin Token Engine → SQLite")
        print()
        print("🎯 ACTIVE BOTS:")
        print("   🌟 @yayincilara (Lara)")
        print("   🦁 @babagavat (Gavat Baba)")
        print("   🌸 @xxxgeisha (Geisha)")
        print()
        print("⚡ QUICK ACCESS:")
        print("   • API Status: http://localhost:5050/api/system/status")
        print("   • Bot Stats: /stats (Telegram DM)")
        print("   • Token spending: /spend service_name")
        print()
    
    def setup_signal_handlers(self):
        """Signal handler'ları kur"""
        def signal_handler(signum, frame):
            logger.info("🛑 Çıkış sinyali alındı, sistem kapatılıyor...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def shutdown(self):
        """Tüm bileşenleri kapat"""
        logger.info("🔄 Sistem kapatılıyor...")
        self.running = False
        
        for name, process in self.processes:
            try:
                logger.info(f"🛑 {name} kapatılıyor...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} kapatıldı")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ {name} zorla kapatılıyor...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ {name} kapatma hatası: {e}")
    
    def run(self):
        """Ana launcher"""
        self.show_startup_info()
        
        # Signal handlers
        self.setup_signal_handlers()
        
        logger.info("🚀 Sistem başlatılıyor...")
        
        # 1. Flask API başlat (zaten çalışıyor olabilir, kontrol et)
        try:
            import requests
            response = requests.get("http://localhost:5050/api/system/status", timeout=2)
            if response.status_code == 200:
                logger.info("✅ Flask API zaten çalışıyor!")
                api_success = True
            else:
                api_success = self.start_flask_api()
        except:
            api_success = self.start_flask_api()
        
        if api_success:
            time.sleep(2)
        
        # 2. Production bots başlat
        bots_success = self.start_production_bots()
        if bots_success:
            time.sleep(5)
        
        # Başarı raporu
        total_components = 2
        successful_components = sum([api_success, bots_success])
        
        print("\n" + "🎉" + "="*40 + "🎉")
        print(f"🚀 Sistem başlatıldı! {successful_components}/{total_components} bileşen aktif")
        print("🎉" + "="*40 + "🎉")
        
        if successful_components > 0:
            print("\n📊 SYSTEM STATUS:")
            if api_success:
                print("   ✅ Flask API Server - http://localhost:5050")
            if bots_success:
                print("   ✅ Production Bots - Telegram'da aktif")
            
            print("\n💡 NEXT STEPS:")
            print("   1. API test: curl http://localhost:5050/api/system/status")
            print("   2. Bot'lara Telegram'dan /stats yazın")
            print("   3. Token harcama: /spend content")
            print("   4. Çıkış için Ctrl+C")
        
        # Sonsuz döngü - sistem çalışır durumda tut
        try:
            while self.running:
                time.sleep(30)
                
                # Process'leri kontrol et
                for name, process in self.processes:
                    if process.poll() is not None:
                        logger.warning(f"⚠️ {name} durdu! Exit code: {process.returncode}")
        
        except KeyboardInterrupt:
            logger.info("🛑 Kullanıcı çıkış yaptı")
        finally:
            self.shutdown()

def main():
    """Ana entry point"""
    try:
        launcher = SimpleGavatCoreLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 GavatCore sistem kapatıldı!")
    except Exception as e:
        logger.error(f"❌ Sistem hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 