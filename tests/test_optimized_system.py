#!/usr/bin/env python3
# test_optimized_system.py - Optimize Edilmiş Sistem Test Script'i

import asyncio
import os
import sys
from datetime import datetime
import structlog

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

async def test_system():
    """Sistemi test et"""
    logger.info("🧪 GAVATCORE TEST BAŞLATILIYOR")
    logger.info("=" * 80)
    
    try:
        # Test modunu aktif et
        os.environ["TEST_MODE"] = "true"
        os.environ["OPTIMIZATION_CONFIG"] = "development"
        
        # Core modülleri import et
        from run_optimized import OptimizedGavatcore
        from core.integrated_optimizer import get_integrated_stats
        from core.profile_manager import profile_manager
        from core.session_manager import get_active_sessions
        from core.package_manager import package_manager
        from utils.anti_spam_guard import anti_spam_guard
        
        logger.info("1️⃣ Modüller başarıyla import edildi")
        
        # Session'ları kontrol et
        logger.info("2️⃣ Session'lar kontrol ediliyor...")
        sessions = await get_active_sessions()
        
        if not sessions:
            logger.error("❌ Aktif session bulunamadı!")
            return False
        
        logger.info(f"✅ {len(sessions)} aktif session bulundu")
        for username in sessions:
            logger.info(f"   - {username}")
        
        # Profile'ları kontrol et
        logger.info("3️⃣ Profile'lar kontrol ediliyor...")
        for username in sessions:
            profile = await profile_manager.get_profile(username)
            if profile:
                logger.info(f"✅ Profile bulundu: {username}")
                logger.info(f"   - Spam aktif: {profile.get('is_spam_active', False)}")
                logger.info(f"   - DM reply aktif: {profile.get('is_dm_active', False)}")
                logger.info(f"   - Group reply aktif: {profile.get('is_group_active', False)}")
            else:
                logger.warning(f"⚠️ Profile bulunamadı: {username}")
        
        # Paket sistemini kontrol et
        logger.info("4️⃣ Paket sistemi kontrol ediliyor...")
        for username in sessions:
            try:
                # Test user ID
                test_user_id = 123456789  # Test için sabit ID
                package_info = package_manager.get_user_package(test_user_id)
                
                if package_info:
                    logger.info(f"✅ Paket bilgisi: {username}")
                    logger.info(f"   - Paket: {package_info['package_name']}")
                    logger.info(f"   - Günlük limit: {package_info['daily_messages']}")
                    logger.info(f"   - Grup limiti: {package_info['groups']}")
                else:
                    logger.info(f"ℹ️ Varsayılan paket kullanılacak: {username}")
            except Exception as e:
                logger.error(f"Paket kontrolü hatası: {e}")
        
        # Anti-spam durumunu kontrol et
        logger.info("5️⃣ Anti-spam sistemi kontrol ediliyor...")
        for username in sessions:
            status = anti_spam_guard.get_account_status(username)
            logger.info(f"Anti-spam durumu - {username}:")
            logger.info(f"   - Uyarı sayısı: {status['warning_count']}")
            logger.info(f"   - Spam güvenli: {status['is_safe']}")
            logger.info(f"   - Son spam: {status.get('last_spam_time', 'Yok')}")
        
        # Optimize edilmiş sistemi başlat
        logger.info("6️⃣ Optimize edilmiş sistem başlatılıyor...")
        gavatcore = OptimizedGavatcore()
        
        # Test modunda başlat (kısa süreliğine)
        success = await gavatcore.initialize("development")
        
        if not success:
            logger.error("❌ Sistem başlatılamadı!")
            return False
        
        logger.info("✅ Sistem başarıyla başlatıldı!")
        
        # Sistem istatistiklerini al
        await asyncio.sleep(5)  # Sistem stabilize olsun
        
        stats = await get_integrated_stats()
        logger.info("📊 Sistem İstatistikleri:")
        logger.info(f"   - Memory: {stats.get('integrated_optimizer', {}).get('avg_memory_mb', 0):.1f} MB")
        logger.info(f"   - CPU: {stats.get('integrated_optimizer', {}).get('avg_cpu_percent', 0):.1f}%")
        logger.info(f"   - Aktif bot sayısı: {len(gavatcore.clients)}")
        
        # 30 saniye çalıştır ve gözlemle
        logger.info("⏱️ Sistem 30 saniye test edilecek...")
        await asyncio.sleep(30)
        
        # Final istatistikler
        logger.info("📊 Final İstatistikler:")
        for username, bot_data in gavatcore.clients.items():
            stats = bot_data["stats"]
            logger.info(f"{username}:")
            logger.info(f"   - Gönderilen mesaj: {stats['messages_sent']}")
            logger.info(f"   - Spam gönderilen: {stats['spam_sent']}")
            logger.info(f"   - DM reply: {stats['dm_replies']}")
            logger.info(f"   - Group reply: {stats['group_replies']}")
            logger.info(f"   - Hatalar: {stats['errors']}")
        
        # Sistemi kapat
        logger.info("🛑 Sistem kapatılıyor...")
        await gavatcore.shutdown()
        
        logger.info("✅ TEST BAŞARIYLA TAMAMLANDI!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test hatası: {e}", exc_info=True)
        return False
    finally:
        # Test modunu kapat
        os.environ.pop("TEST_MODE", None)

async def main():
    """Ana test fonksiyonu"""
    start_time = datetime.now()
    
    success = await test_system()
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"⏱️ Test süresi: {duration:.1f} saniye")
    
    if success:
        logger.info("✅ TÜM TESTLER BAŞARILI!")
        return 0
    else:
        logger.error("❌ TESTLER BAŞARISIZ!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 