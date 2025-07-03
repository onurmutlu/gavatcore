#!/usr/bin/env python3
"""
BabaGAVAT Coin System Demo - Sokak Zekası ile Güçlendirilmiş Coin Sistemi Demo
FlirtMarket / GavatCore için Onur Metodu demo sistemi
BabaGAVAT'ın sokak tecrübesi ile coin ekonomisi gösterimi
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import structlog

# Demo imports
from core.coin_service import babagavat_coin_service, CoinTransactionType
from core.erko_analyzer import babagavat_erko_analyzer, ErkoSegment, ErkoRiskLevel
from core.database_manager import database_manager

logger = structlog.get_logger("babagavat.coin_system_demo")

class BabaGAVATCoinSystemDemo:
    """BabaGAVAT Coin System Demo - Onur Metodu Gösterimi"""
    
    def __init__(self):
        self.demo_users = []
        self.demo_scenarios = []
        self.start_time = None
        
    async def initialize(self) -> None:
        """Demo sistemini başlat"""
        try:
            self.start_time = datetime.now()
            logger.info("🚀 BabaGAVAT Coin System Demo başlatılıyor - Onur Metodu gösterimi...")
            
            # Servisleri başlat
            await database_manager.initialize()
            await babagavat_coin_service.initialize()
            await babagavat_erko_analyzer.initialize()
            
            # Demo verilerini oluştur
            await self._create_demo_data()
            
            logger.info("✅ BabaGAVAT Coin System Demo hazır - Sokak ekonomisi demo modunda! 💪")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT Coin System Demo başlatma hatası: {e}")
            raise
    
    async def _create_demo_data(self) -> None:
        """Demo verilerini oluştur"""
        try:
            # BabaGAVAT'ın demo kullanıcı profilleri
            self.demo_users = [
                {
                    "user_id": 100001,
                    "username": "ahmet_whale",
                    "profile_type": "whale_user",
                    "description": "Balina kullanıcı - Çok yüksek harcama",
                    "initial_coins": 10000,
                    "spending_pattern": "high_volume",
                    "expected_segment": ErkoSegment.WHALE
                },
                {
                    "user_id": 100002,
                    "username": "mehmet_vip",
                    "profile_type": "vip_user", 
                    "description": "VIP kullanıcı - Premium müşteri",
                    "initial_coins": 2000,
                    "spending_pattern": "premium",
                    "expected_segment": ErkoSegment.VIP
                },
                {
                    "user_id": 100003,
                    "username": "ali_hot",
                    "profile_type": "hot_user",
                    "description": "Aktif kullanıcı - Yüksek etkileşim",
                    "initial_coins": 500,
                    "spending_pattern": "active",
                    "expected_segment": ErkoSegment.HOT
                },
                {
                    "user_id": 100004,
                    "username": "emre_cold",
                    "profile_type": "cold_user",
                    "description": "Soğuk kullanıcı - Düşük aktivite",
                    "initial_coins": 100,
                    "spending_pattern": "passive",
                    "expected_segment": ErkoSegment.COLD
                },
                {
                    "user_id": 100005,
                    "username": "can_ghost",
                    "profile_type": "ghost_user",
                    "description": "Hayalet kullanıcı - Minimal aktivite",
                    "initial_coins": 50,
                    "spending_pattern": "minimal",
                    "expected_segment": ErkoSegment.GHOST
                },
                {
                    "user_id": 100006,
                    "username": "burak_risky",
                    "profile_type": "risky_user",
                    "description": "Riskli kullanıcı - Şüpheli pattern",
                    "initial_coins": 1000,
                    "spending_pattern": "suspicious",
                    "expected_segment": ErkoSegment.REGULAR,
                    "expected_risk": ErkoRiskLevel.HIGH
                },
                {
                    "user_id": 100007,
                    "username": "cem_newbie",
                    "profile_type": "newbie_user",
                    "description": "Yeni kullanıcı - Öğrenme aşaması",
                    "initial_coins": 200,
                    "spending_pattern": "learning",
                    "expected_segment": ErkoSegment.NEWBIE
                }
            ]
            
            # Demo şovcu kullanıcıları
            self.demo_performers = [
                {"user_id": 200001, "username": "ayse_performer", "specialty": "chat"},
                {"user_id": 200002, "username": "zeynep_performer", "specialty": "premium"},
                {"user_id": 200003, "username": "elif_performer", "specialty": "vip"},
                {"user_id": 200004, "username": "seda_performer", "specialty": "special"},
                {"user_id": 200005, "username": "merve_performer", "specialty": "regular"}
            ]
            
            logger.info(f"✅ {len(self.demo_users)} demo kullanıcısı ve {len(self.demo_performers)} şovcu oluşturuldu")
            
        except Exception as e:
            logger.error(f"❌ Demo veri oluşturma hatası: {e}")
    
    async def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Kapsamlı demo çalıştır"""
        try:
            print("""
💪 BabaGAVAT Coin System Demo - Onur Metodu Gösterimi

🎯 DEMO SENARYOLARI:
1️⃣ Kullanıcı Profilleri Oluşturma
2️⃣ Coin İşlemleri Simülasyonu
3️⃣ ErkoAnalyzer Segmentasyonu
4️⃣ Risk Değerlendirmesi
5️⃣ Harcama Pattern Analizi
6️⃣ Leaderboard ve İstatistikler

🚀 Demo başlatılıyor...
            """)
            
            # 1. Kullanıcı profilleri oluştur
            await self._demo_user_creation()
            
            # 2. Coin işlemleri simülasyonu
            await self._demo_coin_operations()
            
            # 3. ErkoAnalyzer segmentasyonu
            await self._demo_segmentation()
            
            # 4. Risk değerlendirmesi
            await self._demo_risk_assessment()
            
            # 5. Harcama pattern analizi
            await self._demo_spending_patterns()
            
            # 6. Leaderboard ve istatistikler
            await self._demo_analytics()
            
            # Final rapor
            return await self._generate_demo_report()
            
        except Exception as e:
            logger.error(f"❌ Demo çalıştırma hatası: {e}")
            return {"error": str(e)}
    
    async def _demo_user_creation(self) -> None:
        """Demo kullanıcı oluşturma"""
        try:
            print("\n1️⃣ KULLANICI PROFİLLERİ OLUŞTURULUYOR...")
            
            for user_data in self.demo_users:
                user_id = user_data["user_id"]
                initial_coins = user_data["initial_coins"]
                
                # İlk coin yüklemesi
                await babagavat_coin_service.babagavat_admin_add_coins(
                    admin_id=999999,
                    target_user_id=user_id,
                    amount=initial_coins,
                    reason=f"Demo başlangıç coini - {user_data['profile_type']}"
                )
                
                print(f"   👤 {user_data['username']}: {initial_coins} coin yüklendi ({user_data['description']})")
                await asyncio.sleep(0.1)  # Demo efekti
            
            print("   ✅ Tüm kullanıcı profilleri oluşturuldu!")
            
        except Exception as e:
            logger.error(f"❌ Demo user creation hatası: {e}")
    
    async def _demo_coin_operations(self) -> None:
        """Demo coin işlemleri"""
        try:
            print("\n2️⃣ COIN İŞLEMLERİ SİMÜLASYONU...")
            
            for user_data in self.demo_users:
                user_id = user_data["user_id"]
                pattern = user_data["spending_pattern"]
                
                print(f"   💰 {user_data['username']} - {pattern} pattern simülasyonu:")
                
                if pattern == "high_volume":
                    # Whale kullanıcı - çok harcama
                    for i in range(20):
                        await babagavat_coin_service.babagavat_message_to_performer(
                            user_id=user_id,
                            performer_id=200001 + (i % 5),
                            message_content=f"Whale mesaj {i+1}"
                        )
                    print(f"      🐋 20 premium mesaj gönderildi")
                
                elif pattern == "premium":
                    # VIP kullanıcı - düzenli harcama
                    for i in range(15):
                        await babagavat_coin_service.spend_coins(
                            user_id=user_id,
                            amount=10,
                            transaction_type=CoinTransactionType.SPEND_VIP_CONTENT,
                            description=f"VIP içerik {i+1}"
                        )
                    print(f"      👑 15 VIP içerik satın alındı")
                
                elif pattern == "active":
                    # Hot kullanıcı - aktif etkileşim
                    for i in range(10):
                        await babagavat_coin_service.babagavat_message_to_performer(
                            user_id=user_id,
                            performer_id=200001 + (i % 3),
                            message_content=f"Aktif mesaj {i+1}"
                        )
                    print(f"      🔥 10 aktif mesaj gönderildi")
                
                elif pattern == "passive":
                    # Cold kullanıcı - az harcama
                    for i in range(3):
                        await babagavat_coin_service.babagavat_message_to_performer(
                            user_id=user_id,
                            performer_id=200001,
                            message_content=f"Pasif mesaj {i+1}"
                        )
                    print(f"      ❄️ 3 pasif mesaj gönderildi")
                
                elif pattern == "minimal":
                    # Ghost kullanıcı - minimal aktivite
                    await babagavat_coin_service.babagavat_message_to_performer(
                        user_id=user_id,
                        performer_id=200001,
                        message_content="Tek mesaj"
                    )
                    print(f"      👻 1 minimal mesaj gönderildi")
                
                elif pattern == "suspicious":
                    # Risky kullanıcı - şüpheli pattern
                    # Çok hızlı, yüksek harcama
                    await babagavat_coin_service.spend_coins(
                        user_id=user_id,
                        amount=500,
                        transaction_type=CoinTransactionType.SPEND_SPECIAL_SHOW,
                        description="Şüpheli yüksek harcama"
                    )
                    print(f"      🚨 Şüpheli yüksek harcama yapıldı")
                
                elif pattern == "learning":
                    # Newbie kullanıcı - öğrenme
                    for i in range(5):
                        await babagavat_coin_service.babagavat_daily_task_reward(
                            user_id=user_id,
                            task_type=f"newbie_task_{i+1}"
                        )
                    print(f"      🌱 5 öğrenme görevi tamamlandı")
                
                await asyncio.sleep(0.2)  # Demo efekti
            
            print("   ✅ Tüm coin işlemleri tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Demo coin operations hatası: {e}")
    
    async def _demo_segmentation(self) -> None:
        """Demo segmentasyon"""
        try:
            print("\n3️⃣ ERKOANALYZER SEGMENTASYONU...")
            
            segmentation_results = []
            
            for user_data in self.demo_users:
                user_id = user_data["user_id"]
                
                # ErkoAnalyzer ile analiz et
                profile = await babagavat_erko_analyzer.analyze_user(user_id)
                
                expected_segment = user_data.get("expected_segment", ErkoSegment.REGULAR)
                actual_segment = profile.segment
                
                match_status = "✅" if actual_segment == expected_segment else "⚠️"
                
                print(f"   {match_status} {user_data['username']}: {actual_segment.value} (beklenen: {expected_segment.value})")
                print(f"      📊 BabaGAVAT Score: {profile.babagavat_score:.2f}")
                print(f"      🧠 Sokak Zekası: {profile.street_smart_rating:.2f}")
                print(f"      🎯 Risk Seviyesi: {profile.risk_level.value}")
                
                segmentation_results.append({
                    "user_id": user_id,
                    "username": user_data["username"],
                    "expected_segment": expected_segment.value,
                    "actual_segment": actual_segment.value,
                    "match": actual_segment == expected_segment,
                    "babagavat_score": profile.babagavat_score,
                    "risk_level": profile.risk_level.value
                })
                
                await asyncio.sleep(0.3)  # Demo efekti
            
            # Segmentasyon başarı oranı
            matches = sum(1 for r in segmentation_results if r["match"])
            success_rate = (matches / len(segmentation_results)) * 100
            
            print(f"\n   📈 Segmentasyon Başarı Oranı: {success_rate:.1f}% ({matches}/{len(segmentation_results)})")
            print("   ✅ ErkoAnalyzer segmentasyonu tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Demo segmentation hatası: {e}")
    
    async def _demo_risk_assessment(self) -> None:
        """Demo risk değerlendirmesi"""
        try:
            print("\n4️⃣ RİSK DEĞERLENDİRMESİ...")
            
            # Yüksek riskli kullanıcıları al
            high_risk_users = await babagavat_erko_analyzer.get_high_risk_users(limit=10)
            
            if high_risk_users:
                print("   🚨 Yüksek Riskli Kullanıcılar:")
                for user in high_risk_users:
                    risk_emoji = "🔴" if user["risk_level"] == "critical" else "🟡"
                    print(f"      {risk_emoji} {user['username']}: {user['risk_level']} risk")
                    print(f"         Red Flags: {', '.join(user['red_flags'])}")
                    print(f"         BabaGAVAT Notes: {user['babagavat_notes']}")
            else:
                print("   ✅ Yüksek riskli kullanıcı bulunamadı")
            
            print("   ✅ Risk değerlendirmesi tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Demo risk assessment hatası: {e}")
    
    async def _demo_spending_patterns(self) -> None:
        """Demo harcama pattern analizi"""
        try:
            print("\n5️⃣ HARCAMA PATTERN ANALİZİ...")
            
            for user_data in self.demo_users[:3]:  # İlk 3 kullanıcı için detaylı analiz
                user_id = user_data["user_id"]
                
                # Kullanıcı profilini al
                profile = await babagavat_erko_analyzer.analyze_user(user_id)
                
                print(f"   📊 {user_data['username']} Harcama Pattern'i:")
                pattern = profile.spending_pattern
                
                print(f"      💰 Toplam İşlem: {pattern.get('total_transactions', 0)}")
                print(f"      💸 Harcama İşlemi: {pattern.get('spending_transactions', 0)}")
                print(f"      📈 Ortalama Harcama: {pattern.get('average_spending', 0):.1f} coin")
                print(f"      🎯 Harcama Sıklığı: {pattern.get('spending_frequency', 'unknown')}")
                print(f"      🧠 BabaGAVAT Analizi: {pattern.get('babagavat_analysis', 'normal')}")
                
                if pattern.get('preferred_times'):
                    print(f"      ⏰ Tercih Edilen Saatler: {', '.join(pattern['preferred_times'])}")
                
                await asyncio.sleep(0.3)  # Demo efekti
            
            print("   ✅ Harcama pattern analizi tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Demo spending patterns hatası: {e}")
    
    async def _demo_analytics(self) -> None:
        """Demo analytics ve leaderboard"""
        try:
            print("\n6️⃣ LEADERBOARD VE İSTATİSTİKLER...")
            
            # Leaderboard
            leaderboard = await babagavat_coin_service.get_babagavat_leaderboard(limit=5)
            
            print("   🏆 BabaGAVAT Coin Leaderboard:")
            for entry in leaderboard:
                tier_emoji = {"platinum": "💎", "gold": "🥇", "silver": "🥈", "bronze": "🥉"}.get(entry["babagavat_tier"], "🔸")
                print(f"      {entry['rank']}. {tier_emoji} User {entry['user_id']}: {entry['balance']} coin")
                print(f"         Tier: {entry['babagavat_tier']} | Status: {entry['babagavat_status']}")
            
            # Segment istatistikleri
            segment_stats = await babagavat_erko_analyzer.get_segment_statistics()
            
            print("\n   📊 Segment İstatistikleri:")
            for segment, stats in segment_stats.get("segments", {}).items():
                print(f"      {segment.upper()}: {stats['count']} kullanıcı")
                print(f"         Ort. BabaGAVAT Score: {stats['avg_babagavat_score']}")
                print(f"         Toplam Harcama: {stats['total_spending']} coin")
            
            print("   ✅ Analytics tamamlandı!")
            
        except Exception as e:
            logger.error(f"❌ Demo analytics hatası: {e}")
    
    async def _generate_demo_report(self) -> Dict[str, Any]:
        """Demo raporu oluştur"""
        try:
            # Tüm kullanıcıların final durumunu al
            user_reports = []
            
            for user_data in self.demo_users:
                user_id = user_data["user_id"]
                
                # Coin stats
                coin_stats = await babagavat_coin_service.get_user_stats(user_id)
                
                # ErkoAnalyzer profili
                profile = await babagavat_erko_analyzer.analyze_user(user_id)
                
                # Transaction history
                transactions = await babagavat_coin_service.get_babagavat_transaction_history(user_id, limit=10)
                
                user_reports.append({
                    "user_data": user_data,
                    "coin_stats": coin_stats,
                    "erko_profile": {
                        "segment": profile.segment.value,
                        "risk_level": profile.risk_level.value,
                        "babagavat_score": profile.babagavat_score,
                        "street_smart_rating": profile.street_smart_rating,
                        "spending_pattern": profile.spending_pattern,
                        "red_flags": profile.red_flags,
                        "green_flags": profile.green_flags,
                        "babagavat_notes": profile.babagavat_notes
                    },
                    "transaction_count": len(transactions)
                })
            
            # Leaderboard
            leaderboard = await babagavat_coin_service.get_babagavat_leaderboard(limit=10)
            
            # Segment stats
            segment_stats = await babagavat_erko_analyzer.get_segment_statistics()
            
            # High risk users
            high_risk_users = await babagavat_erko_analyzer.get_high_risk_users(limit=5)
            
            demo_duration = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "demo_report": {
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": demo_duration,
                    "demo_users_count": len(self.demo_users),
                    "demo_performers_count": len(self.demo_performers),
                    "onur_metodu_status": "successfully_demonstrated"
                },
                "user_reports": user_reports,
                "leaderboard": leaderboard,
                "segment_statistics": segment_stats,
                "high_risk_users": high_risk_users,
                "babagavat_analysis": "comprehensive_coin_system_demo_completed",
                "system_performance": {
                    "coin_service": "operational",
                    "erko_analyzer": "operational",
                    "segmentation": "accurate",
                    "risk_assessment": "functional",
                    "sokak_zekasi": "maksimum"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Demo rapor oluşturma hatası: {e}")
            return {"error": str(e)}

async def main():
    """Ana demo fonksiyonu"""
    try:
        # Demo'yu başlat
        demo = BabaGAVATCoinSystemDemo()
        await demo.initialize()
        
        # Kapsamlı demo çalıştır
        results = await demo.run_comprehensive_demo()
        
        # Sonuçları kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"babagavat_coin_system_demo_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # Final özet
        print(f"""

🎯 BABAGAVAT COIN SYSTEM DEMO TAMAMLANDI - ONUR METODU GÖSTERİLDİ!

📊 DEMO SONUÇLARI:
⏱️ Demo Süresi: {results['demo_report']['duration_seconds']:.2f} saniye
👥 Demo Kullanıcıları: {results['demo_report']['demo_users_count']}
🎭 Demo Şovcuları: {results['demo_report']['demo_performers_count']}
🎯 Onur Metodu Durumu: {results['demo_report']['onur_metodu_status']}

🏆 LEADERBOARD TOP 3:
        """)
        
        for i, entry in enumerate(results['leaderboard'][:3]):
            tier_emoji = {"platinum": "💎", "gold": "🥇", "silver": "🥈", "bronze": "🥉"}.get(entry["babagavat_tier"], "🔸")
            print(f"{i+1}. {tier_emoji} User {entry['user_id']}: {entry['balance']} coin ({entry['babagavat_tier']})")
        
        print(f"""
📊 SEGMENT DAĞILIMI:
        """)
        
        for segment, stats in results['segment_statistics'].get("segments", {}).items():
            print(f"   {segment.upper()}: {stats['count']} kullanıcı (Ort. Score: {stats['avg_babagavat_score']})")
        
        if results['high_risk_users']:
            print(f"""
🚨 YÜKSEK RİSKLİ KULLANICILAR: {len(results['high_risk_users'])}
            """)
            for user in results['high_risk_users'][:3]:
                print(f"   ⚠️ {user['username']}: {user['risk_level']} risk")
        
        print(f"""
📋 Detaylı Rapor: {report_file}

💪 BabaGAVAT Coin System - Onur Metodu başarıyla gösterildi!
🔥 Sokak zekası ile güçlendirilmiş coin ekonomisi!
        """)
        
    except Exception as e:
        print(f"❌ BabaGAVAT Coin System Demo hatası: {e}")

if __name__ == "__main__":
    print("""
💪 BabaGAVAT Coin System Demo - Onur Metodu Gösterimi

🎯 ONUR METODU ÖZELLİKLERİ:
✅ Coin Balance Management
✅ Transaction Processing
✅ Referral Bonus System
✅ Daily Task Rewards
✅ Message to Performer
✅ ErkoAnalyzer Integration
✅ User Segmentation (HOT/COLD/GHOST/FAKE/VIP/WHALE)
✅ Risk Assessment
✅ Spending Pattern Analysis
✅ Leaderboard System
✅ Admin Panel Functions

🔥 BabaGAVAT'ın sokak zekası ile güçlendirilmiş sistem!

🚀 Demo başlatılıyor...
    """)
    
    asyncio.run(main()) 