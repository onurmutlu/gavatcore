#!/usr/bin/env python3
"""
🚀 QUICK ONLYVIPS TEST 🚀

OnlyVips Bot Conversation System için hızlı test
"""

import asyncio
import sys
from datetime import datetime

async def test_onlyvips_conversation():
    """🔧 OnlyVips conversation system test"""
    try:
        print(f"""
🔥🔥🔥 ONLYVIPS BOT CONVERSATION TEST 🔥🔥🔥
⏰ Test zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🧪 Test adımları:
1. Import kontrolü
2. System başlatma
3. Bot client bağlantıları
4. Grup bulma
5. Handler kurulumu

💪 ONUR METODU - HIZLI TEST!
        """)
        
        # 1. Import test
        print("📦 Imports kontrol ediliyor...")
        try:
            from onlyvips_bot_conversation_system import OnlyVipsBotConversationSystem
            print("   ✅ OnlyVipsBotConversationSystem import - OK")
        except Exception as e:
            print(f"   ❌ Import error: {e}")
            return False
        
        # 2. System oluşturma
        print("🏗️ System oluşturuluyor...")
        conversation_system = OnlyVipsBotConversationSystem()
        print("   ✅ System created - OK")
        
        # 3. Initialization test
        print("🚀 System initialization test...")
        try:
            initialized = await conversation_system.initialize()
            if initialized:
                print("   ✅ System initialized - OK")
                print(f"   🤖 Active bots: {len(conversation_system.clients)}")
                print(f"   📱 OnlyVips group: {conversation_system.onlyvips_group_id}")
                
                # 5 saniye çalıştır
                print("⏰ 5 saniye test çalıştırması...")
                await asyncio.sleep(5)
                
                # Shutdown
                await conversation_system.shutdown()
                print("   ✅ Shutdown - OK")
                
                return True
            else:
                print("   ❌ System initialization failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Initialization error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

async def main():
    """🚀 Ana test fonksiyonu"""
    try:
        success = await test_onlyvips_conversation()
        
        if success:
            print("""
✅✅✅ ONLYVIPS TEST BAŞARILI! ✅✅✅

🎯 SONUÇ: OnlyVips Bot Conversation System hazır!
💬 Botlar muhabbet etmeye hazır!
🚀 python onlyvips_bot_conversation_system.py ile başlatın!

💪 ONUR METODU: TEST PASSED!
            """)
        else:
            print("""
❌❌❌ ONLYVIPS TEST BAŞARISIZ! ❌❌❌

🔧 Sorunları çözün ve tekrar deneyin!
            """)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Main test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 