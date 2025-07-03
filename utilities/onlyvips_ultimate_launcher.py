#!/usr/bin/env python3
"""
🔥🔥🔥 ONLYVIPS ULTIMATE LAUNCHER 🔥🔥🔥

💪 ONUR METODU - FULL ONLYVIPS POWER!

Features:
- OnlyVips Grup Monitoring
- Bot Conversation System
- Real-time mesaj takip + cevap
- Botlar arası muhabbet + laf atma
- Parallel system operation

🎯 HEDEF: ONLYVIPS TOTAL CONTROL!
"""

import asyncio
import multiprocessing
import time
import sys
from datetime import datetime
import structlog

logger = structlog.get_logger("onlyvips.ultimate")

class OnlyVipsUltimateLauncher:
    """🔥 OnlyVips Ultimate Launcher - Full Power Control"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.processes = {}
        
        print("""
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🔥                                                               🔥
🔥        🚀 ONLYVIPS ULTIMATE LAUNCHER 🚀                      🔥
🔥                                                               🔥
🔥          📡 MONITORING + 💬 CONVERSATION POWER! 📡            🔥
🔥                    💪 ONUR METODU ULTIMATE! 💪                🔥
🔥                                                               🔥
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

🎯 SISTEMLER:
   👁️ OnlyVips Group Monitor - Real-time mesaj izleme
   🤖 Bot Conversation System - Botlar arası muhabbet + laf atma
   
💰 YAŞASIN SPONSORLAR! ONLYVIPS TOTAL CONTROL! 💰
        """)
    
    async def start_monitoring_system(self):
        """👁️ Monitoring sistemini başlat"""
        try:
            print("👁️ OnlyVips Monitoring System başlatılıyor...")
            
            from onlyvips_group_monitor import OnlyVipsGroupMonitor
            
            monitor = OnlyVipsGroupMonitor()
            
            if await monitor.initialize():
                print("✅ Monitoring System başlatıldı!")
                await monitor.run_monitor()
            else:
                print("❌ Monitoring System başlatılamadı!")
                
        except Exception as e:
            logger.error(f"❌ Monitoring system error: {e}")
    
    async def start_conversation_system(self):
        """🤖 Conversation sistemini başlat"""
        try:
            print("🤖 OnlyVips Conversation System başlatılıyor...")
            
            from onlyvips_bot_conversation_system import OnlyVipsBotConversationSystem
            
            conversation = OnlyVipsBotConversationSystem()
            
            if await conversation.initialize():
                print("✅ Conversation System başlatıldı!")
                await conversation.run_conversation_system()
            else:
                print("❌ Conversation System başlatılamadı!")
                
        except Exception as e:
            logger.error(f"❌ Conversation system error: {e}")
    
    async def run_ultimate_system(self):
        """🚀 Ultimate sistemi çalıştır"""
        try:
            print("🚀 ONLYVIPS ULTIMATE SYSTEM BAŞLATIYOR...")
            
            # Her iki sistemi paralel çalıştır
            monitoring_task = asyncio.create_task(self.start_monitoring_system())
            conversation_task = asyncio.create_task(self.start_conversation_system())
            
            print("""
✅✅✅ ONLYVIPS ULTIMATE SYSTEM AKTİF! ✅✅✅

📊 ÇALIŞAN SİSTEMLER:
   👁️ Group Monitor: Real-time mesaj izleme
   🤖 Bot Conversation: Botlar arası muhabbet + laf atma

💬 ÖZELLIKLER:
   📡 OnlyVips grubundaki her mesajı göster
   🤖 Botlar birbiriyle sohbet etsin
   😄 Diğer kullanıcılara laf atsın
   🎯 Personality bazlı cevaplar
   ⚡ Real-time operation

🛑 Durdurmak için Ctrl+C kullanın
            """)
            
            # Her iki task'ı bekle
            await asyncio.gather(monitoring_task, conversation_task, return_exceptions=True)
            
        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu")
        except Exception as e:
            logger.error(f"❌ Ultimate system error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """🛑 Ultimate sistemin kapatılması"""
        try:
            print("\n🛑 ONLYVIPS ULTIMATE SYSTEM KAPATILIYOR...")
            
            uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            
            print(f"""
✅ ONLYVIPS ULTIMATE SYSTEM KAPATILDI!

📊 FINAL STATS:
   ⏱️ Total Uptime: {uptime_minutes:.1f} dakika
   📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
   📅 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   
🔥 ONLYVIPS ULTIMATE MISSION - TAMAMLANDI! 🔥
💪 ONUR METODU: BAŞARIYLA UYGULANDI! 💪
            """)
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

async def main():
    """🚀 Ana fonksiyon - Ultimate OnlyVips Launcher"""
    try:
        print("🚀 ONLYVIPS ULTIMATE LAUNCHER STARTING...")
        
        # Ultimate launcher oluştur
        launcher = OnlyVipsUltimateLauncher()
        
        # Ultimate sistemi çalıştır
        await launcher.run_ultimate_system()
        
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"❌ Main error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Enhanced logging setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'onlyvips_ultimate_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Ana döngüyü başlat
    asyncio.run(main()) 