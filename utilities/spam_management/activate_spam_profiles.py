from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
# activate_spam_profiles.py - Profilleri spam için aktif hale getir

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile_manager import profile_manager
from core.session_manager import get_active_sessions
from utilities.log_utils import log_event
import structlog

logger = structlog.get_logger()

async def activate_spam_profiles():
    """Tüm profilleri spam için aktif hale getir"""
    try:
        logger.info("🚀 Profiller aktif hale getiriliyor...")
        
        # Session'ları al
        sessions = await get_active_sessions()
        
        if not sessions:
            logger.error("❌ Aktif session bulunamadı!")
            return False
        
        logger.info(f"✅ {len(sessions)} session bulundu")
        
        # Her profili güncelle
        activated_count = 0
        for username in sessions:
            try:
                # Mevcut profili al veya yeni oluştur
                profile = await profile_manager.get_profile(username)
                
                if not profile:
                    # Varsayılan profil oluştur
                    profile = {
                        "username": username,
                        "profile_type": "spambot",
                        "is_spam_active": True,
                        "is_dm_active": True,
                        "is_group_active": True,
                        "engaging_messages": [
                            "Merhaba! Nasılsınız? 😊",
                            "Selam! Ne yapıyorsunuz? 👋",
                            "Hey! Keyifler nasıl? 🌟",
                            "Merhaba arkadaşlar! 💫",
                            "Selam canlar! Nasıl gidiyor? 🎉",
                            "Günaydın! Harika bir gün dilerim! ☀️",
                            "İyi akşamlar! Keyifli sohbetler! 🌙",
                            "Herkese selam! 🙋‍♂️",
                            "Merhaba güzel insanlar! 💝",
                            "Selamlar! Bugün nasıl geçiyor? 🌈"
                        ],
                        "response_style": "friendly",
                        "tone": "warm",
                        "topics": ["genel", "sohbet", "günlük", "sosyal"],
                        "created_at": None,
                        "updated_at": None
                    }
                    
                    # Profili kaydet
                    await profile_manager.save_profile(username, profile)
                    logger.info(f"✅ Yeni profil oluşturuldu: {username}")
                else:
                    # Mevcut profili güncelle
                    profile["is_spam_active"] = True
                    profile["is_dm_active"] = True
                    profile["is_group_active"] = True
                    
                    # Mesajları kontrol et
                    if not profile.get("engaging_messages"):
                        profile["engaging_messages"] = [
                            "Merhaba! Nasılsınız? 😊",
                            "Selam! Ne yapıyorsunuz? 👋",
                            "Hey! Keyifler nasıl? 🌟"
                        ]
                    
                    await profile_manager.save_profile(username, profile)
                    logger.info(f"✅ Profil güncellendi: {username}")
                
                activated_count += 1
                log_event(username, "✅ Spam profili aktif edildi")
                
            except Exception as e:
                logger.error(f"❌ Profil güncelleme hatası ({username}): {e}")
                continue
        
        logger.info(f"✅ Toplam {activated_count} profil aktif edildi")
        return True
        
    except Exception as e:
        logger.error(f"❌ Profil aktivasyon hatası: {e}")
        return False

async def main():
    """Ana fonksiyon"""
    success = await activate_spam_profiles()
    
    if success:
        logger.info("✅ TÜM PROFİLLER AKTİF!")
        logger.info("🚀 Artık 'python run_optimized.py' ile sistemi başlatabilirsiniz")
        return 0
    else:
        logger.error("❌ Profil aktivasyonu başarısız!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 