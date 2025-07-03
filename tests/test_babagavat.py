#!/usr/bin/env python3
"""
BabaGAVAT Test Suite
Sokak Zekası ile Güçlendirilmiş AI Kullanıcı Analiz ve Davet Botu Test Sistemi
BabaGAVAT'ın tüm özelliklerini test eden kapsamlı test suite
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import structlog

# Test imports - BabaGAVAT modülleri
from core.user_analyzer import babagavat_user_analyzer, UserTrustLevel
from core.database_manager import database_manager

logger = structlog.get_logger("test.babagavat")

class BabaGAVATTestSuite:
    """BabaGAVAT Test Suite - Sokak Zekası Test Sistemi"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        
    async def run_all_babagavat_tests(self) -> Dict[str, Any]:
        """Tüm BabaGAVAT testlerini çalıştır"""
        try:
            self.start_time = datetime.now()
            logger.info("🧪 BabaGAVAT Test Suite başlatılıyor - Sokak zekası test ediliyor...")
            
            # Database'i başlat
            await database_manager.initialize()
            
            # BabaGAVAT test senaryoları
            test_scenarios = [
                ("BabaGAVAT Database Tables", self.test_babagavat_database_tables),
                ("BabaGAVAT Spam Score Calculation", self.test_babagavat_spam_score_calculation),
                ("BabaGAVAT Transaction Score Calculation", self.test_babagavat_transaction_score_calculation),
                ("BabaGAVAT Engagement Score Calculation", self.test_babagavat_engagement_score_calculation),
                ("BabaGAVAT Street Smart Score Calculation", self.test_babagavat_street_smart_score_calculation),
                ("BabaGAVAT Pattern Detection", self.test_babagavat_pattern_detection),
                ("BabaGAVAT Trust Score Updates", self.test_babagavat_trust_score_updates),
                ("BabaGAVAT Female User Detection", self.test_babagavat_female_user_detection),
                ("BabaGAVAT Invite Candidate System", self.test_babagavat_invite_candidate_system),
                ("BabaGAVAT Message Analysis Flow", self.test_babagavat_message_analysis_flow),
                ("BabaGAVAT Verdict System", self.test_babagavat_verdict_system),
                ("BabaGAVAT Intelligence System", self.test_babagavat_intelligence_system),
                ("BabaGAVAT Admin Reports", self.test_babagavat_admin_reports)
            ]
            
            # BabaGAVAT testlerini çalıştır
            for test_name, test_func in test_scenarios:
                try:
                    logger.info(f"🔍 BabaGAVAT Test: {test_name}")
                    result = await test_func()
                    self.test_results.append({
                        "test_name": test_name,
                        "status": "PASS" if result else "FAIL",
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    status_emoji = "✅" if result else "❌"
                    logger.info(f"{status_emoji} {test_name}: {'PASS' if result else 'FAIL'}")
                except Exception as e:
                    self.test_results.append({
                        "test_name": test_name,
                        "status": "ERROR",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    logger.error(f"❌ {test_name}: ERROR - {e}")
            
            # BabaGAVAT test sonuçlarını derle
            return await self._compile_babagavat_test_results()
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Test suite hatası: {e}")
            return {"error": str(e)}
    
    async def test_babagavat_database_tables(self) -> bool:
        """BabaGAVAT Database tablolarını test et"""
        try:
            # BabaGAVAT tablolarını oluştur
            await babagavat_user_analyzer._create_babagavat_tables()
            
            # BabaGAVAT tablolarının varlığını kontrol et
            async with database_manager._get_connection() as db:
                babagavat_tables = [
                    "babagavat_user_profiles",
                    "babagavat_message_analysis", 
                    "babagavat_invite_candidates",
                    "babagavat_group_monitoring",
                    "babagavat_intelligence_log"
                ]
                
                for table in babagavat_tables:
                    cursor = await db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table,)
                    )
                    result = await cursor.fetchone()
                    if not result:
                        logger.error(f"❌ BabaGAVAT tablosu bulunamadı: {table}")
                        return False
            
            logger.info("✅ Tüm BabaGAVAT tabloları başarıyla oluşturuldu")
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Database tables test hatası: {e}")
            return False
    
    async def test_babagavat_spam_score_calculation(self) -> bool:
        """BabaGAVAT Spam puanı hesaplama testleri"""
        try:
            test_cases = [
                ("Merhaba nasılsın? Güzel bir gün 😊", 0.0),  # Normal mesaj
                ("IBAN hesap ödeme para TL", 0.15),  # Spam göstergeleri
                ("100 TL fiyat, whatsapp yazın dolandırıcı", 0.25),  # Yüksek spam
                ("ACIL PARA ÖDEME HESAP IBAN SAHTE SCAM", 0.35),  # Çok yüksek spam
            ]
            
            for message, expected_min in test_cases:
                score = await babagavat_user_analyzer._calculate_spam_score(message)
                
                logger.info(f"BabaGAVAT Spam test - Message: '{message}' | Score: {score:.2f} | Expected min: {expected_min}")
                
                # BabaGAVAT'ın spam tespiti daha hassas olmalı
                if expected_min == 0.0 and score > 0.05:
                    logger.warning(f"BabaGAVAT normal mesajı spam olarak işaretledi: {score}")
                    return False
                elif expected_min > 0.0 and score < expected_min:
                    logger.warning(f"BabaGAVAT spam puanı çok düşük: {score} (beklenen min: {expected_min})")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Spam score test hatası: {e}")
            return False
    
    async def test_babagavat_transaction_score_calculation(self) -> bool:
        """BabaGAVAT Transaksiyon puanı hesaplama testleri"""
        try:
            test_cases = [
                ("Merhaba nasılsın?", 0.0),
                ("Saat 14:30'da buluşalım", 0.2),
                ("100 TL ödeme yapın transfer", 0.4),
                ("TR12 3456 7890 hesap numarası, 200 TL kart", 0.6),
            ]
            
            for message, expected_min in test_cases:
                score = await babagavat_user_analyzer._calculate_transaction_score(message)
                
                logger.info(f"BabaGAVAT Transaction test - Message: '{message}' | Score: {score:.2f} | Expected min: {expected_min}")
                
                if expected_min == 0.0 and score > 0.1:
                    logger.warning(f"BabaGAVAT normal mesajı transaction olarak işaretledi: {score}")
                    return False
                elif expected_min > 0.0 and score < expected_min:
                    logger.warning(f"BabaGAVAT transaction puanı çok düşük: {score} (beklenen min: {expected_min})")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Transaction score test hatası: {e}")
            return False
    
    async def test_babagavat_engagement_score_calculation(self) -> bool:
        """BabaGAVAT Etkileşim puanı hesaplama testleri"""
        try:
            test_cases = [
                ("hi", 0.3),  # Çok kısa
                ("Merhaba! Nasılsın? Çok güzel bir gün 😊", 0.7),  # Pozitif
                ("teşekkürler harika profesyonel kaliteli ❤️", 0.8),  # Çok pozitif
                ("güvenilir samimi mükemmel süper", 0.9),  # BabaGAVAT'ın sevdiği kelimeler
            ]
            
            for message, expected_min in test_cases:
                score = await babagavat_user_analyzer._calculate_engagement_score(message)
                
                logger.info(f"BabaGAVAT Engagement test - Message: '{message}' | Score: {score:.2f} | Expected min: {expected_min}")
                
                if score < expected_min - 0.2:
                    logger.warning(f"BabaGAVAT engagement puanı çok düşük: {score} (beklenen min: {expected_min})")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Engagement score test hatası: {e}")
            return False
    
    async def test_babagavat_street_smart_score_calculation(self) -> bool:
        """BabaGAVAT Sokak Zekası puanı hesaplama testleri"""
        try:
            test_cases = [
                ("anlıyorum mantıklı tecrübe dikkatli", 0.8),  # Yüksek sokak zekası
                ("biliyorum gördüm yaşadım güvenli", 0.7),  # İyi sokak zekası
                ("bilmiyorum emin değilim kandırıldım", 0.3),  # Düşük sokak zekası
                ("ne yapacağım yardım edin dolandırıldım", 0.2),  # Çok düşük sokak zekası
            ]
            
            for message, expected_min in test_cases:
                score = await babagavat_user_analyzer._calculate_street_smart_score(message)
                
                logger.info(f"BabaGAVAT Street Smart test - Message: '{message}' | Score: {score:.2f} | Expected min: {expected_min}")
                
                if score < expected_min - 0.2:
                    logger.warning(f"BabaGAVAT street smart puanı çok düşük: {score} (beklenen min: {expected_min})")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Street Smart score test hatası: {e}")
            return False
    
    async def test_babagavat_pattern_detection(self) -> bool:
        """BabaGAVAT Pattern tespit testleri"""
        try:
            test_cases = [
                ("TR12 3456 7890 1234 5678 9012 34", ["iban_detected"]),
                ("100 TL fiyat", ["price_mentioned"]),
                ("Saat 14:30", ["time_mentioned"]),
                ("WhatsApp'tan yazın", ["contact_redirect"]),
                ("Acil bugün", ["urgency_signal"]),
                ("güvenilir profesyonel kaliteli", ["quality_signal"]),  # BabaGAVAT'ın özel pattern'i
            ]
            
            for message, expected_patterns in test_cases:
                patterns = await babagavat_user_analyzer._detect_patterns(message)
                
                logger.info(f"BabaGAVAT Pattern test - Message: '{message}' | Patterns: {patterns}")
                
                for expected in expected_patterns:
                    if expected not in patterns:
                        logger.warning(f"BabaGAVAT beklenen pattern'i tespit edemedi: {expected}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Pattern detection test hatası: {e}")
            return False
    
    async def test_babagavat_trust_score_updates(self) -> bool:
        """BabaGAVAT Güven puanı güncelleme testleri"""
        try:
            # Test kullanıcısı oluştur
            test_user_id = "babagavat_test_user_123"
            
            # İlk profil oluştur
            async with database_manager._get_connection() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO babagavat_user_profiles 
                    (user_id, username, display_name, has_photo, bio, first_seen, 
                     last_activity, message_count, trust_score, trust_level, street_smart_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_user_id, "babagavat_test", "BabaGAVAT Test User", True, "",
                    datetime.now(), datetime.now(), 1, 0.5, "neutral", 0.5
                ))
                await db.commit()
            
            # Pozitif mesaj ile güven puanını artır (BabaGAVAT'ın pozitif değerlendirmesi)
            await babagavat_user_analyzer._update_trust_score(test_user_id, 0.1, 0.1, 0.8, 0.8)
            
            # Güven puanını kontrol et
            async with database_manager._get_connection() as db:
                cursor = await db.execute(
                    "SELECT trust_score, street_smart_score FROM babagavat_user_profiles WHERE user_id = ?",
                    (test_user_id,)
                )
                result = await cursor.fetchone()
                
                if not result or result[0] <= 0.5:
                    logger.warning(f"BabaGAVAT pozitif mesaj sonrası güven puanı artmadı: {result}")
                    return False
            
            # Negatif mesaj ile güven puanını düşür (BabaGAVAT'ın negatif değerlendirmesi)
            await babagavat_user_analyzer._update_trust_score(test_user_id, 0.8, 0.7, 0.2, 0.2)
            
            # Güven puanının düştüğünü kontrol et
            async with database_manager._get_connection() as db:
                cursor = await db.execute(
                    "SELECT trust_score FROM babagavat_user_profiles WHERE user_id = ?",
                    (test_user_id,)
                )
                result = await cursor.fetchone()
                
                if not result or result[0] >= 0.6:
                    logger.warning(f"BabaGAVAT negatif mesaj sonrası güven puanı düşmedi: {result}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Trust score update test hatası: {e}")
            return False
    
    async def test_babagavat_female_user_detection(self) -> bool:
        """BabaGAVAT Kadın kullanıcı tespit testleri"""
        try:
            # Mock User objesi oluştur
            class MockUser:
                def __init__(self, first_name, username, photo):
                    self.first_name = first_name
                    self.username = username
                    self.photo = photo
            
            test_cases = [
                (MockUser("Ayşe", "ayse_guzel", True), True),
                (MockUser("Zeynep", "zeynep_princess", True), True),
                (MockUser("Elif", "elif_angel", True), True),
                (MockUser("Mehmet", "mehmet123", False), False),
                (MockUser("Ali", "ali_boy", False), False),
                (MockUser("Ahmet", "ahmet_king", False), False),
            ]
            
            for user, expected in test_cases:
                result = await babagavat_user_analyzer._is_female_user(user)
                
                logger.info(f"BabaGAVAT Female detection - User: {user.first_name}/@{user.username} | Result: {result} | Expected: {expected}")
                
                if result != expected:
                    logger.warning(f"BabaGAVAT cinsiyet tespiti yanlış: {user.first_name} - {result} (beklenen: {expected})")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Female user detection test hatası: {e}")
            return False
    
    async def test_babagavat_invite_candidate_system(self) -> bool:
        """BabaGAVAT Davet adayı sistemi testleri"""
        try:
            # Test kullanıcısı oluştur
            test_user_id = "babagavat_invite_test_user"
            
            # Yüksek güven puanlı kullanıcı oluştur (BabaGAVAT'ın beğeneceği profil)
            async with database_manager._get_connection() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO babagavat_user_profiles 
                    (user_id, username, display_name, has_photo, bio, first_seen, 
                     last_activity, message_count, trust_score, trust_level, street_smart_score, babagavat_approval)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_user_id, "babagavat_invite_test", "BabaGAVAT Invite Test", True, "",
                    datetime.now(), datetime.now(), 10, 0.8, "trusted", 0.7, False
                ))
                await db.commit()
            
            # BabaGAVAT davet adayı kontrolü
            await babagavat_user_analyzer._check_invite_candidate(test_user_id)
            
            # Davet adayı listesinde olup olmadığını kontrol et
            async with database_manager._get_connection() as db:
                cursor = await db.execute(
                    "SELECT id, babagavat_approval FROM babagavat_invite_candidates WHERE user_id = ?",
                    (test_user_id,)
                )
                result = await cursor.fetchone()
                
                if not result:
                    logger.warning(f"BabaGAVAT davet adayı listesine eklemedi: {test_user_id}")
                    return False
                
                logger.info(f"BabaGAVAT davet adayı başarıyla eklendi: {test_user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Invite candidate test hatası: {e}")
            return False
    
    async def test_babagavat_message_analysis_flow(self) -> bool:
        """BabaGAVAT Mesaj analiz akışı testleri"""
        try:
            # Mock User objesi
            class MockUser:
                def __init__(self):
                    self.id = 999888777
                    self.first_name = "BabaGAVAT"
                    self.last_name = "Test"
                    self.username = "babagavat_testuser"
                    self.photo = True
            
            # BabaGAVAT test mesajı analiz et
            test_user = MockUser()
            await babagavat_user_analyzer._analyze_message_with_street_smarts(
                user_id=str(test_user.id),
                username=test_user.username,
                display_name=f"{test_user.first_name} {test_user.last_name}",
                group_id="babagavat_test_group_123",
                message_id=12345,
                message_text="Merhaba! Anlıyorum durumu, tecrübem var bu konularda. Güvenilir yaklaşım 😊",
                sender_info=test_user
            )
            
            # BabaGAVAT mesaj analizinin kaydedildiğini kontrol et
            async with database_manager._get_connection() as db:
                cursor = await db.execute(
                    "SELECT id, babagavat_verdict, street_smart_score FROM babagavat_message_analysis WHERE user_id = ?",
                    (str(test_user.id),)
                )
                result = await cursor.fetchone()
                
                if not result:
                    logger.warning(f"BabaGAVAT mesaj analizi kaydedilmedi: {test_user.id}")
                    return False
                
                logger.info(f"BabaGAVAT mesaj analizi başarılı: verdict={result[1]}, street_smart={result[2]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Message analysis flow test hatası: {e}")
            return False
    
    async def test_babagavat_verdict_system(self) -> bool:
        """BabaGAVAT Karar sistemi testleri"""
        try:
            test_cases = [
                (0.8, 0.9, 0.2, 0.1, "ŞÜPHELI"),  # Yüksek spam/transaction
                (0.1, 0.1, 0.8, 0.8, "ONAYLANMIŞ"),  # Yüksek engagement/street smart
                (0.1, 0.1, 0.2, 0.9, "SOKAK ZEKASI"),  # Çok yüksek street smart
                (0.3, 0.3, 0.7, 0.5, "POTANSİYEL"),  # Orta seviye
                (0.2, 0.2, 0.3, 0.3, "NÖTR"),  # Düşük seviye
            ]
            
            for spam_score, transaction_score, engagement_score, street_smart_score, expected_keyword in test_cases:
                verdict = await babagavat_user_analyzer._get_babagavat_verdict(
                    spam_score, transaction_score, engagement_score, street_smart_score
                )
                
                logger.info(f"BabaGAVAT Verdict test - Scores: {spam_score:.1f}/{transaction_score:.1f}/{engagement_score:.1f}/{street_smart_score:.1f} | Verdict: {verdict}")
                
                if expected_keyword not in verdict:
                    logger.warning(f"BabaGAVAT verdict beklenen kelimeyi içermiyor: '{expected_keyword}' in '{verdict}'")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Verdict system test hatası: {e}")
            return False
    
    async def test_babagavat_intelligence_system(self) -> bool:
        """BabaGAVAT İstihbarat sistemi testleri"""
        try:
            # Test kullanıcısı oluştur (BabaGAVAT'ın özel onayı için)
            test_user_id = "babagavat_intelligence_test"
            
            async with database_manager._get_connection() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO babagavat_user_profiles 
                    (user_id, username, display_name, trust_score, street_smart_score, babagavat_approval)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (test_user_id, "intelligence_test", "Intelligence Test", 0.85, 0.75, False))
                await db.commit()
            
            # BabaGAVAT'ın özel onay sistemi test et
            await babagavat_user_analyzer._babagavat_special_approval(test_user_id, "intelligence_test", 0.85, 0.75)
            
            # Intelligence log'da kayıt olup olmadığını kontrol et
            async with database_manager._get_connection() as db:
                cursor = await db.execute(
                    "SELECT id, babagavat_decision FROM babagavat_intelligence_log WHERE target_id = ?",
                    (test_user_id,)
                )
                result = await cursor.fetchone()
                
                if not result:
                    logger.warning(f"BabaGAVAT intelligence log kaydı bulunamadı: {test_user_id}")
                    return False
                
                logger.info(f"BabaGAVAT intelligence sistemi başarılı: decision={result[1]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Intelligence system test hatası: {e}")
            return False
    
    async def test_babagavat_admin_reports(self) -> bool:
        """BabaGAVAT Admin rapor testleri"""
        try:
            # BabaGAVAT kullanıcı analiz raporu
            user_report = await babagavat_user_analyzer.get_user_analysis_report()
            if "statistics" not in user_report:
                logger.warning("BabaGAVAT user report 'statistics' içermiyor")
                return False
            
            # BabaGAVAT davet adayları raporu
            invite_report = await babagavat_user_analyzer.get_invite_candidates_report()
            if "statistics" not in invite_report:
                logger.warning("BabaGAVAT invite report 'statistics' içermiyor")
                return False
            
            # BabaGAVAT şüpheli kullanıcılar raporu
            suspicious_report = await babagavat_user_analyzer.get_suspicious_users_report()
            if "suspicious_users" not in suspicious_report:
                logger.warning("BabaGAVAT suspicious report 'suspicious_users' içermiyor")
                return False
            
            logger.info("BabaGAVAT tüm admin raporları başarılı")
            return True
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Admin reports test hatası: {e}")
            return False
    
    async def _compile_babagavat_test_results(self) -> Dict[str, Any]:
        """BabaGAVAT test sonuçlarını derle"""
        try:
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
            failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
            error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
            
            duration = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "test_suite": "BabaGAVAT Test Suite - Sokak Zekası Test Sistemi",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "babagavat_summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "errors": error_tests,
                    "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                    "street_smart_analysis": "completed"
                },
                "babagavat_test_results": self.test_results,
                "status": "SUCCESS" if failed_tests == 0 and error_tests == 0 else "FAILED"
            }
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Test sonuçları derleme hatası: {e}")
            return {"error": str(e)}

async def main():
    """BabaGAVAT Ana test fonksiyonu"""
    try:
        # BabaGAVAT Test suite'i çalıştır
        test_suite = BabaGAVATTestSuite()
        results = await test_suite.run_all_babagavat_tests()
        
        # BabaGAVAT sonuçlarını kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"babagavat_test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # BabaGAVAT sonuçlarını yazdır
        print(f"""
🧪 BabaGAVAT Test Suite Tamamlandı - Sokak Zekası Test Edildi!

📊 BABAGAVAT TEST SONUÇLARI:
✅ Başarılı: {results['babagavat_summary']['passed']}
❌ Başarısız: {results['babagavat_summary']['failed']}
🔥 Hata: {results['babagavat_summary']['errors']}
📈 Başarı Oranı: {results['babagavat_summary']['success_rate']:.1f}%

⏱️ Süre: {results['duration_seconds']:.2f} saniye
📋 Rapor: {report_file}

🎯 BabaGAVAT Genel Durum: {results['status']}
💪 Sokak Zekası Analizi: {results['babagavat_summary']['street_smart_analysis']}

🔥 BabaGAVAT - Sokak zekası ile güçlendirilmiş sistem test edildi!
        """)
        
        return results['status'] == "SUCCESS"
        
    except Exception as e:
        print(f"❌ BabaGAVAT Test hatası: {e}")
        return False

if __name__ == "__main__":
    print("""
💪 BabaGAVAT Test Suite - Sokak Zekası Test Sistemi

🔥 BabaGAVAT'ın tüm özelliklerini test eden kapsamlı test suite
🧠 Sokak zekası algoritmaları ve güvenilirlik testleri
🎯 Spam tespiti, davet sistemi ve intelligence monitoring testleri

🚀 BabaGAVAT testleri başlatılıyor...
    """)
    
    success = asyncio.run(main())
    exit(0 if success else 1) 