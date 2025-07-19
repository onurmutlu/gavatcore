from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
BabaGAVAT Demo - Sokak Zekası ile Güçlendirilmiş AI Kullanıcı Analiz Sistemi Demo
Telegram bağlantısı olmadan çalışan demo versiyonu
BabaGAVAT'ın sokak tecrübesi ile güçlendirilmiş analiz motoru
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import structlog

# Core imports - BabaGAVAT'ın modülleri
from core.user_analyzer import babagavat_user_analyzer
from core.database_manager import database_manager

logger = structlog.get_logger("babagavat.demo")

class BabaGAVATDemo:
    """BabaGAVAT Demo Sistemi - Sokak Zekası Gösterimi"""
    
    def __init__(self):
        self.is_running = False
        self.demo_users = []
        self.demo_messages = []
        self.start_time = None
        
        logger.info("💪 BabaGAVAT Demo başlatıldı - Sokak zekası test modunda!")
    
    async def initialize(self) -> None:
        """BabaGAVAT Demo'yu başlat"""
        try:
            self.start_time = datetime.now()
            logger.info("🚀 BabaGAVAT Demo sistemi başlatılıyor - Sokak analizi hazırlanıyor...")
            
            # Database'i başlat
            await database_manager.initialize()
            await babagavat_user_analyzer._create_babagavat_tables()
            
            # Demo verilerini oluştur
            await self._create_babagavat_demo_data()
            
            self.is_running = True
            logger.info("✅ BabaGAVAT Demo hazır - Sokak zekası test edilmeye hazır! 💪")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Demo başlatma hatası: {e}")
            raise
    
    async def _create_babagavat_demo_data(self) -> None:
        """BabaGAVAT demo verileri oluştur"""
        try:
            # BabaGAVAT'ın sokak zekası test senaryoları
            self.demo_users = [
                {
                    "user_id": "babagavat_demo_user_1",
                    "username": "ayse_sokak_zekasi",
                    "display_name": "Ayşe Sokak Zekası",
                    "profile_type": "street_smart_trusted",
                    "messages": [
                        "Merhaba! Bu konuda tecrübem var, dikkatli olmak lazım 😊",
                        "Anlıyorum durumu, mantıklı yaklaşım bu",
                        "Güvenilir kaynaklardan araştırmak önemli",
                        "Teşekkürler, harika bilgi paylaşımı ❤️",
                        "Profesyonel yaklaşım, kaliteli içerik"
                    ]
                },
                {
                    "user_id": "babagavat_demo_user_2", 
                    "username": "zeynep_suspicious",
                    "display_name": "Zeynep Şüpheli",
                    "profile_type": "suspicious_scammer",
                    "messages": [
                        "ACIL! 100 TL ödeme yapın hemen!",
                        "IBAN: TR12 3456 7890 1234 5678 9012 34 - Para gönderin!",
                        "WhatsApp'tan yazın, özelden konuşalım para için",
                        "Bugün son gün! Hemen transfer yapın!",
                        "Dolandırıcı değilim, güvenin bana para verin!"
                    ]
                },
                {
                    "user_id": "babagavat_demo_user_3",
                    "username": "merve_neutral",
                    "display_name": "Merve Nötr", 
                    "profile_type": "neutral_average",
                    "messages": [
                        "Saat 14:30'da buluşalım",
                        "Bugün hava çok güzel",
                        "Film önerisi var mı?",
                        "Ne yapacağım bilmiyorum",
                        "Yardım edin lütfen"
                    ]
                },
                {
                    "user_id": "babagavat_demo_user_4",
                    "username": "elif_babagavat_approved",
                    "display_name": "Elif BabaGAVAT Onaylı",
                    "profile_type": "babagavat_vip",
                    "messages": [
                        "Harika bir etkinlik olmuş, organizasyon mükemmel 🎉",
                        "Katılımcılar çok memnun kalmış, tecrübeli ekip",
                        "Bir sonraki etkinliği sabırsızlıkla bekliyorum",
                        "Güvenilir ve profesyonel yaklaşım, kaliteli hizmet",
                        "Teşekkürler bu güzel deneyim için, sokak zekası var ❤️",
                        "Anlıyorum durumu, mantıklı ve dikkatli yaklaşım",
                        "Tecrübem var bu konularda, güvenli yol bu"
                    ]
                },
                {
                    "user_id": "babagavat_demo_user_5",
                    "username": "seda_naive",
                    "display_name": "Seda Naif",
                    "profile_type": "naive_vulnerable",
                    "messages": [
                        "Bilmiyorum ne yapacağım, emin değilim",
                        "Kandırıldım galiba, nasıl olur böyle şey",
                        "İnanamıyorum, dolandırıldım sanırım",
                        "Yardım edin, ne yapacağım bilmiyorum",
                        "Güvenebilir miyim acaba, emin olamıyorum"
                    ]
                }
            ]
            
            logger.info(f"✅ {len(self.demo_users)} BabaGAVAT demo kullanıcısı oluşturuldu - Sokak profilleri hazır!")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT demo veri oluşturma hatası: {e}")
    
    async def run_babagavat_demo_analysis(self) -> Dict[str, Any]:
        """BabaGAVAT demo analizi çalıştır"""
        try:
            logger.info("🔍 BabaGAVAT demo analizi başlatılıyor - Sokak zekası devreye giriyor...")
            
            # Mock User sınıfı - BabaGAVAT test için
            class MockUser:
                def __init__(self, user_id, username, display_name):
                    self.id = int(user_id.replace("babagavat_demo_user_", ""))
                    self.username = username
                    self.first_name = display_name.split()[0]
                    self.last_name = display_name.split()[1] if len(display_name.split()) > 1 else ""
                    self.photo = True
            
            # Her kullanıcı için BabaGAVAT'ın sokak zekası ile mesajları analiz et
            for user_data in self.demo_users:
                user = MockUser(user_data["user_id"], user_data["username"], user_data["display_name"])
                
                logger.info(f"🕵️ BabaGAVAT analiz ediyor: {user_data['display_name']} ({user_data['profile_type']})")
                
                for i, message in enumerate(user_data["messages"]):
                    await babagavat_user_analyzer._analyze_message_with_street_smarts(
                        user_id=user_data["user_id"],
                        username=user_data["username"],
                        display_name=user_data["display_name"],
                        group_id="babagavat_demo_group_123",
                        message_id=i + 1,
                        message_text=message,
                        sender_info=user
                    )
                    
                    # Kısa bekleme - BabaGAVAT'ın analiz süresi
                    await asyncio.sleep(0.1)
            
            logger.info("✅ BabaGAVAT demo analizi tamamlandı - Sokak zekası sonuçları hazır!")
            
            # BabaGAVAT'ın sonuçlarını topla
            return await self._generate_babagavat_demo_report()
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT demo analizi hatası: {e}")
            return {"error": str(e)}
    
    async def _generate_babagavat_demo_report(self) -> Dict[str, Any]:
        """BabaGAVAT demo raporu oluştur"""
        try:
            # BabaGAVAT'ın kullanıcı analiz raporu
            user_report = await babagavat_user_analyzer.get_user_analysis_report()
            
            # BabaGAVAT'ın davet adayları raporu
            invite_report = await babagavat_user_analyzer.get_invite_candidates_report()
            
            # BabaGAVAT'ın şüpheli kullanıcılar raporu
            suspicious_report = await babagavat_user_analyzer.get_suspicious_users_report()
            
            # BabaGAVAT'ın detaylı kullanıcı bilgileri
            user_details = []
            for user_data in self.demo_users:
                user_detail = await babagavat_user_analyzer.get_user_analysis_report(user_data["user_id"])
                if "user_profile" in user_detail:
                    user_details.append({
                        "username": user_data["username"],
                        "display_name": user_data["display_name"],
                        "profile_type": user_data["profile_type"],
                        "profile": user_detail["user_profile"],
                        "recent_messages": user_detail.get("recent_messages", [])
                    })
            
            return {
                "babagavat_demo_report": {
                    "timestamp": datetime.now().isoformat(),
                    "demo_duration": (datetime.now() - self.start_time).total_seconds(),
                    "analyzed_users": len(self.demo_users),
                    "total_messages": sum(len(u["messages"]) for u in self.demo_users),
                    "street_smart_analysis": "completed"
                },
                "babagavat_statistics": user_report.get("statistics", []),
                "babagavat_invite_candidates": invite_report,
                "babagavat_suspicious_users": suspicious_report,
                "babagavat_user_details": user_details
            }
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT demo rapor oluşturma hatası: {e}")
            return {"error": str(e)}
    
    async def demonstrate_babagavat_features(self) -> None:
        """BabaGAVAT özelliklerini göster"""
        try:
            print("""
💪 BabaGAVAT - Sokak Zekası ile Güçlendirilmiş AI Kullanıcı Analiz Sistemi Demo

🎯 BABAGAVAT'IN SOKAK ZEKASı ÖZELLİKLERİ:
✅ Spam Tespiti - BabaGAVAT'ın sokak tecrübesi ile şüpheli mesajları yakalar
✅ Transaksiyon Analizi - Para/ödeme sinyallerini sokak zekası ile tespit eder  
✅ Güven Puanı - Kullanıcıların güvenilirlik seviyesini sokak tecrübesi ile hesaplar
✅ Sokak Zekası Puanı - Kullanıcıların sokak zekası seviyesini analiz eder
✅ Davet Sistemi - BabaGAVAT'ın onayladığı güvenilir kullanıcıları otomatik davet eder
✅ Pattern Recognition - IBAN, fiyat, saat gibi kalıpları sokak radarı ile tespit eder
✅ Kadın Kullanıcı Tespiti - Hedef kitleyi BabaGAVAT'ın sokak zekası ile filtreler
✅ Intelligence Monitoring - BabaGAVAT'ın özel istihbarat sistemi
✅ Admin Raporları - Detaylı analiz ve sokak zekası istatistikleri

🔍 BABAGAVAT DEMO SENARYOLARI:
👤 Ayşe Sokak Zekası - Pozitif, sokak zekası olan, güvenilir kullanıcı
👤 Zeynep Şüpheli - Şüpheli, spam mesajları, dolandırıcı profili
👤 Merve Nötr - Orta seviye, nötr kullanıcı, sokak zekası gelişmemiş
👤 Elif BabaGAVAT Onaylı - Yüksek güven puanı, BabaGAVAT'ın VIP listesi
👤 Seda Naif - Düşük sokak zekası, kolay kandırılabilir profil

🚀 BabaGAVAT Demo başlatılıyor - Sokak zekası devreye giriyor...
            """)
            
            # BabaGAVAT demo analizi çalıştır
            results = await self.run_babagavat_demo_analysis()
            
            # BabaGAVAT sonuçlarını göster
            await self._display_babagavat_results(results)
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT demo gösterim hatası: {e}")
    
    async def _display_babagavat_results(self, results: Dict[str, Any]) -> None:
        """BabaGAVAT sonuçlarını göster"""
        try:
            print(f"""
📊 BABAGAVAT DEMO SONUÇLARI - SOKAK ZEKASı ANALİZİ:

⏱️ Analiz Süresi: {results['babagavat_demo_report']['demo_duration']:.2f} saniye
👥 Analiz Edilen Kullanıcı: {results['babagavat_demo_report']['analyzed_users']}
💬 Toplam Mesaj: {results['babagavat_demo_report']['total_messages']}
🧠 Sokak Zekası Analizi: {results['babagavat_demo_report']['street_smart_analysis']}

📈 BABAGAVAT KULLANICI İSTATİSTİKLERİ:
            """)
            
            for stat in results.get("babagavat_statistics", []):
                trust_level = stat.get("trust_level", "unknown")
                count = stat.get("count", 0)
                avg_trust = stat.get("avg_trust", 0)
                
                if trust_level == "suspicious":
                    emoji = "🔴"
                    description = "ŞÜPHELI - BabaGAVAT'ın alarm listesinde"
                elif trust_level == "neutral":
                    emoji = "🟡"
                    description = "NÖTR - BabaGAVAT izliyor"
                else:
                    emoji = "🟢"
                    description = "GÜVENİLİR - BabaGAVAT'ın onayladığı"
                
                print(f"{emoji} {description}: {count} kullanıcı (Ort. güven: {avg_trust:.2f})")
            
            # BabaGAVAT'ın davet adayları
            candidates = results.get("babagavat_invite_candidates", {}).get("recent_candidates", [])
            if candidates:
                print(f"\n✨ BABAGAVAT DAVET ADAYLARI - SOKAK ZEKASı ONAYLILAR ({len(candidates)}):")
                for candidate in candidates[:3]:  # İlk 3'ü göster
                    if isinstance(candidate, (list, tuple)) and len(candidate) >= 3:
                        print(f"   💪 {candidate[0]} - Güven: {candidate[1]:.2f} - Öncelik: {candidate[2]} - BabaGAVAT Onaylı!")
                    elif isinstance(candidate, dict):
                        username = candidate.get("username", "Unknown")
                        trust_score = candidate.get("trust_score", 0)
                        priority = candidate.get("priority", "unknown")
                        print(f"   💪 {username} - Güven: {trust_score:.2f} - Öncelik: {priority} - BabaGAVAT Onaylı!")
            
            # BabaGAVAT'ın şüpheli kullanıcıları
            suspicious = results.get("babagavat_suspicious_users", {}).get("suspicious_users", [])
            if suspicious:
                print(f"\n🚨 BABAGAVAT ŞÜPHELİ KULLANICILAR - SOKAK ALARMI ({len(suspicious)}):")
                for user in suspicious[:3]:  # İlk 3'ü göster
                    if isinstance(user, (list, tuple)) and len(user) >= 3:
                        print(f"   ⚠️ {user[1]} - Güven: {user[2]:.2f} - BabaGAVAT Alarm Veriyor!")
                    elif isinstance(user, dict):
                        username = user.get("username", "Unknown")
                        trust_score = user.get("trust_score", 0)
                        print(f"   ⚠️ {username} - Güven: {trust_score:.2f} - BabaGAVAT Alarm Veriyor!")
            
            # BabaGAVAT'ın detaylı kullanıcı analizi
            print(f"\n🔍 BABAGAVAT DETAYLI KULLANICI ANALİZİ - SOKAK ZEKASı DEĞERLENDİRMESİ:")
            for user_detail in results.get("babagavat_user_details", []):
                profile = user_detail["profile"]
                trust_score = profile.get("trust_score", 0)
                trust_level = profile.get("trust_level", "unknown")
                message_count = profile.get("message_count", 0)
                street_smart_score = profile.get("street_smart_score", 0)
                babagavat_approval = profile.get("babagavat_approval", False)
                
                if trust_level == "suspicious":
                    emoji = "🔴"
                    status = "ŞÜPHELI"
                elif trust_level == "neutral":
                    emoji = "🟡"
                    status = "NÖTR"
                else:
                    emoji = "🟢"
                    status = "GÜVENİLİR"
                
                approval_status = "✅ BabaGAVAT ONAYLANMIŞ" if babagavat_approval else "⏳ BabaGAVAT İNCELİYOR"
                
                print(f"""
{emoji} {user_detail['display_name']} (@{user_detail['username']})
   📊 Güven Puanı: {trust_score:.2f} ({status})
   🧠 Sokak Zekası: {street_smart_score:.2f}
   💬 Mesaj Sayısı: {message_count}
   📝 Son Mesajlar: {len(user_detail.get('recent_messages', []))}
   💪 BabaGAVAT Durumu: {approval_status}
   🎯 Profil Tipi: {user_detail['profile_type']}
                """)
            
            print(f"""
🎯 BABAGAVAT SONUÇ - SOKAK ZEKASı DEĞERLENDİRMESİ:
BabaGAVAT başarıyla çalışıyor! Sokak zekası ile sistem otomatik olarak:
• Spam mesajları ve dolandırıcıları tespit etti 🔴
• Güvenilir ve sokak zekası olan kullanıcıları belirledi 🟢
• Davet adaylarını BabaGAVAT'ın onayı ile listeledi ✨
• Şüpheli aktiviteleri sokak radarı ile flagledi 🚨
• Kullanıcıların sokak zekası seviyesini analiz etti 🧠
• BabaGAVAT'ın özel onay sistemi ile VIP listesi oluşturdu 💪

📋 Detaylı rapor: babagavat_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json
🔥 BabaGAVAT - Sokak zekası ile güçlendirilmiş sistem!
            """)
            
            # BabaGAVAT raporunu kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"babagavat_demo_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📋 BabaGAVAT demo raporu kaydedildi: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT sonuç gösterim hatası: {e}")

async def main():
    """BabaGAVAT Ana demo fonksiyonu"""
    try:
        # BabaGAVAT Demo'yu oluştur ve başlat
        demo = BabaGAVATDemo()
        await demo.initialize()
        
        # BabaGAVAT özelliklerini göster
        await demo.demonstrate_babagavat_features()
        
    except KeyboardInterrupt:
        logger.info("⌨️ BabaGAVAT Demo sonlandırıldı")
    except Exception as e:
        logger.error(f"❌ BabaGAVAT Demo hatası: {e}")

if __name__ == "__main__":
    print("""
💪 BabaGAVAT Demo - Sokak Zekası ile Güçlendirilmiş AI Sistem

🔥 BabaGAVAT'ın sokak tecrübesi ile güçlendirilmiş analiz motoru
🎯 Gerçek zamanlı kullanıcı analizi ve dolandırıcı tespiti
🧠 Sokak zekası algoritmaları ile güvenilirlik değerlendirmesi

🚀 Demo başlatılıyor...
    """)
    
    asyncio.run(main()) 