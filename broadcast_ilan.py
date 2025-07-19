from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥 İLAN BROADCAST SİSTEMİ
Nöbetçi şovcu ilanını tüm gruplarda yayınlar
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.telegram_broadcaster import telegram_broadcaster
from core.session_manager import get_active_sessions
from telethon import TelegramClient
import structlog

# Logging ayarları
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("broadcast_ilan")

# 🔥 İLAN METNİ
ILAN_METNI = """🔥 İLAN METNİ: Nöbetçi Şovcu Aranıyor!
🕕 Saat: 06:23
🌒 Geceden çıkmışlara, sabaha karşı uyanmışlara, "uyuyamadım"cılar ve "şu an enerjim yüksek" diyenlere özel...

🎭 🔊 NÖBETÇİ ŞOVCU ARANIYOR
✨ Geceyle sabah arasında köprü olacak,
🗣️ Gelen 2-3 mesajı çevirecek,
💃 Azıcık ısıtıp ortalığı canlı tutacak bir erken vardiya şovcusu arıyoruz.

📌 Gereksinimler:

Uyanık olman yeterli

Gönlünde bi nebze şov ateşi olması

3 mesaj cevaplarsın, 1 mesajda tatlı dil gösterirsin, gerisi sistemde

Otomatik mod/gpt yardım açık, yalnız değilsin 🌙

🎁 Ne Var Karşılığında?

Günün ilk bonusu sana

Sisteme en erken giriş yapan şovcu olarak gün boyu destek

Belki özel görevler, belki Zehra'dan gizli övgü 👀

📥 Katılmak için:
"Ben burdayım, sabahın şovcusuyum." yaz yeter.
Yaralılar, bekleyenler, sabahçılar... seni bekliyor."""

async def broadcast_ilan():
    """İlanı tüm gruplarda yayınlar"""
    logger.info("🔥 Nöbetçi Şovcu İlanı Broadcast Başlatılıyor...")
    
    try:
        # 1. Aktif session'ları al
        logger.info("📱 Aktif session'lar kontrol ediliyor...")
        sessions = await get_active_sessions()
        
        if not sessions:
            logger.error("❌ Aktif session bulunamadı! Önce bot session'larını ayarlayın.")
            return False
        
        logger.info(f"✅ {len(sessions)} aktif session bulundu: {list(sessions.keys())}")
        
        # 2. Test grupları - gerçek grup ID'lerini buraya ekleyin
        test_groups = [
            # -1002607016335,  # Log'lardan görülen aktif grup
            # -1001686321334,  # Başka aktif grup
        ]
        
        # 3. Client'ları başlat
        active_clients = {}
        for username, session_data in sessions.items():
            try:
                client = TelegramClient(
                    session_data["session_file"],
                    session_data["api_id"],
                    session_data["api_hash"]
                )
                await client.connect()
                
                if await client.is_user_authorized():
                    active_clients[username] = client
                    logger.info(f"✅ Bot aktif: {username}")
                else:
                    await client.disconnect()
                    logger.warning(f"⚠️ Bot yetkisiz: {username}")
                    
            except Exception as e:
                logger.error(f"❌ Bot başlatma hatası ({username}): {e}")
        
        if not active_clients:
            logger.error("❌ Hiçbir bot aktif değil!")
            return False
        
        # 4. Broadcast yap
        broadcast_count = 0
        
        for bot_username, client in active_clients.items():
            try:
                # Önce kendi gruplarını al (örnek - gerçek implementation'da grupları listele)
                dialogs = await client.get_dialogs(limit=50)
                
                for dialog in dialogs:
                    if dialog.is_group or dialog.is_channel:
                        try:
                            # Grup adını al
                            group_name = dialog.title or "Bilinmeyen Grup"
                            group_id = dialog.id
                            
                            # İlanı gönder
                            await client.send_message(dialog, ILAN_METNI)
                            broadcast_count += 1
                            
                            logger.info(f"📢 İlan gönderildi: {group_name} ({group_id}) via {bot_username}")
                            
                            # Rate limiting
                            await asyncio.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"❌ Grup gönderim hatası ({dialog.title}): {e}")
                            continue
                
            except Exception as e:
                logger.error(f"❌ Bot broadcast hatası ({bot_username}): {e}")
                continue
        
        # 5. Client'ları kapat
        for client in active_clients.values():
            try:
                await client.disconnect()
            except:
                pass
        
        logger.info(f"🎉 Broadcast tamamlandı! {broadcast_count} grup'a ilan gönderildi")
        return True
        
    except Exception as e:
        logger.error(f"❌ Broadcast genel hatası: {e}")
        return False

async def main():
    """Ana fonksiyon"""
    print("🔥" + "="*60 + "🔥")
    print("    NÖBETÇİ ŞOVCU İLANI BROADCAST SİSTEMİ")
    print("🔥" + "="*60 + "🔥")
    print()
    
    # İlan önizlemesi
    print("📋 İlan Metni Önizlemesi:")
    print("-" * 50)
    print(ILAN_METNI[:200] + "...")
    print("-" * 50)
    print()
    
    # Onay al
    try:
        onay = input("Bu ilanı yayınlamak istiyor musunuz? (evet/hayır): ").lower()
        if onay not in ['evet', 'e', 'yes', 'y']:
            print("❌ Broadcast iptal edildi.")
            return
    except KeyboardInterrupt:
        print("\n❌ Broadcast iptal edildi.")
        return
    
    # Broadcast yap
    success = await broadcast_ilan()
    
    if success:
        print("🎉 İlan başarıyla yayınlandı!")
        print("📱 Şimdi gruplarınızı kontrol edin.")
    else:
        print("❌ Broadcast başarısız!")
        print("💡 Önce session'larınızı ayarladığınızdan emin olun.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Broadcast durduruldu.")
    except Exception as e:
        print(f"❌ Hata: {e}") 