#!/usr/bin/env python3
"""
🚀 SPAM-AWARE FULL BOT SYSTEM LAUNCHER 🚀

💪 ONUR METODU - SPAM'e KARŞI AKILLI CONTACT MANAGEMENT!

Bu script, SPAM-aware sistemini production modunda çalıştırır.
Tüm botları aktif tutar, SPAM durumunda akıllıca DM'e geçer.
"""

import asyncio
import sys
import signal
from datetime import datetime
from spam_aware_full_bot_system import SpamAwareFullBotSystem

# Global sistem referansı
system = None

def signal_handler(signum, frame):
    """Sistem kapatma signal handler'ı"""
    print(f"\n🛑 Signal alındı ({signum}), sistem kapatılıyor...")
    if system:
        asyncio.create_task(system._cleanup())
    sys.exit(0)

async def main():
    """Ana launcher fonksiyonu"""
    global system
    
    print("🔥" * 20)
    print("🔥 SPAM-AWARE FULL BOT SYSTEM 🔥")
    print("🔥" * 20)
    print()
    print("💪 ONUR METODU - SPAM'e Karşı Akıllı Contact Management")
    print("🎯 Tüm botları aktif tut, SPAM'e karşı akıllıca davran!")
    print()
    print("🚀 Sistem özellikleri:")
    print("  🔹 Tüm botları aynı anda aktif çalıştırma")
    print("  🔹 SPAM durumunda otomatik DM moduna geçiş")
    print("  🔹 'DM' reply'i ile otomatik contact ekleme")
    print("  🔹 Telegram API ile contact management")
    print("  🔹 GPT-4o ile akıllı sohbet")
    print("  🔹 Grup içinde yönlendirme mesajları")
    print("  🔹 SQLite veritabanı ile izleme")
    print()
    
    # Signal handler'ları kur
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Sistemi oluştur
    system = SpamAwareFullBotSystem()
    
    try:
        print("🔧 Sistem başlatılıyor...")
        print("=" * 50)
        
        # Sistemi başlat
        if await system.initialize():
            print()
            print("✅ SPAM-Aware Full Bot System başarıyla başlatıldı!")
            print()
            
            # Sistem durumunu göster
            await show_system_status(system)
            
            print("📋 Kullanım talimatları:")
            print("  1️⃣ Grup'ta bir bot'a reply yapın")
            print("  2️⃣ Mesajda 'DM', 'mesaj' veya 'yaz' kelimelerini kullanın")
            print("  3️⃣ Bot sizi otomatik contact'a ekleyecek")
            print("  4️⃣ 'Ekledim, DM başlat' mesajını alacaksınız")
            print("  5️⃣ Bot'a DM atarak özel sohbet edebilirsiniz")
            print()
            
            print("🎛️ SPAM-Aware Logic:")
            print("  ✅ Bot temizse: Normal grup mesajlaşma + contact ekleme")
            print("  ⚠️ Bot SPAM'deyse: Sadece DM yönlendirme")
            print("  🔄 Her saat SPAM durumu kontrol edilir")
            print("  🧹 24 saat sonra pending contact'lar temizlenir")
            print()
            
            print("🚀 Sistem çalışıyor... (Ctrl+C ile durdurun)")
            print("=" * 50)
            print()
            
            # Ana sistem döngüsünü çalıştır
            await system.run_system()
            
        else:
            print("❌ Sistem başlatılamadı!")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Sistem kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Sistem hatası: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if system:
            await system._cleanup()
    
    print("\n✅ SPAM-Aware Full Bot System kapatıldı!")
    return True

async def show_system_status(system):
    """Sistem durumunu göster"""
    print("📊 BOT DURUMLARI:")
    print("-" * 40)
    
    for bot_name, bot_data in system.bot_clients.items():
        status = bot_data["status"]
        me = bot_data["me"]
        config = bot_data["config"]
        
        # Status emoji
        if status == "active":
            status_emoji = "🟢"
            status_text = "AKTİF"
        elif status == "spam_restricted":
            status_emoji = "🔴"
            status_text = "SPAM KISITLAMASI"
        else:
            status_emoji = "🟡"
            status_text = "BİLİNMEYEN"
        
        print(f"  {status_emoji} {bot_name.upper()}")
        print(f"     📱 Username: @{me.username}")
        print(f"     🎭 Personality: {config['personality']}")
        print(f"     🔰 Status: {status_text}")
        print()
    
    print("🛡️ SPAM DURUMLARI:")
    print("-" * 40)
    
    for bot_name, spam_status in system.spam_status.items():
        banned = spam_status.get("banned", False)
        last_check = spam_status.get("last_check")
        
        if banned:
            emoji = "🔴"
            status_text = "SPAM KISITLAMASI"
            until = spam_status.get("until", "Bilinmiyor")
        else:
            emoji = "🟢"
            status_text = "TEMİZ"
            until = "N/A"
        
        print(f"  {emoji} {bot_name.upper()}: {status_text}")
        if banned:
            print(f"     ⏰ Bitiş: {until}")
        if last_check:
            print(f"     🔍 Son kontrol: {last_check.strftime('%H:%M:%S')}")
        print()
    
    print("🎯 TARGET GROUPS:")
    print("-" * 40)
    for i, group in enumerate(system.target_groups, 1):
        print(f"  {i}. 📢 {group}")
    print()
    
    print(f"📁 Database: {system.contact_database}")
    print(f"⏰ Başlatma: {system.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

if __name__ == "__main__":
    # Komut satırı argümanları kontrolü
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🔥 SPAM-Aware Full Bot System")
            print()
            print("Kullanım:")
            print("  python run_spam_aware_system.py          # Normal çalıştırma")
            print("  python run_spam_aware_system.py --help   # Bu yardım")
            print()
            print("Özellikler:")
            print("  - Tüm botları aktif tut")
            print("  - SPAM durumunda DM moduna geç")
            print("  - Otomatik contact ekleme")
            print("  - GPT-4o ile akıllı sohbet")
            print()
            sys.exit(0)
    
    # Ana sistemi çalıştır
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program sonlandırıldı")
    except Exception as e:
        print(f"\n❌ Program hatası: {e}")
        sys.exit(1) 