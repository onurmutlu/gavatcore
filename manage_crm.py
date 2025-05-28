#!/usr/bin/env python3
# manage_crm.py - CRM Yönetim Scripti

import asyncio
import json
from datetime import datetime, timedelta
from core.crm_database import crm_db
from core.crm_analytics import crm_analytics
from core.smart_campaign_manager import smart_campaign_manager
from utils.log_utils import log_event

class CRMManager:
    """CRM yönetim arayüzü"""
    
    def __init__(self):
        self.running = False
    
    async def show_main_menu(self):
        """Ana menüyü göster"""
        while True:
            print("\n" + "="*60)
            print("🎯 GAVATCORE CRM & DİNAMİK GÖNDERİM YÖNETİCİSİ")
            print("="*60)
            print("1. 📊 Kullanıcı Analizi & Segmentasyon")
            print("2. 🎯 Segment Performans Raporu")
            print("3. 🚀 Dinamik Gönderim Durumu")
            print("4. 📈 Grup Performans Raporu")
            print("5. 🔍 CRM Veritabanı İstatistikleri")
            print("6. 📊 Bot Performans Raporu")
            print("7. 🧹 Veritabanı Temizliği")
            print("8. 🤖 Dinamik Optimizer'ı Başlat/Durdur")
            print("9. 📋 Segment Bazlı Kullanıcı Listesi")
            print("10. 🎯 Eski Kampanya Sistemi")
            print("11. 📦 Paket Yönetimi")
            print("0. 🚪 Çıkış")
            print("="*60)
            
            choice = input("Seçiminizi yapın (0-11): ").strip()
            
            try:
                if choice == "1":
                    await self.user_analysis_with_segmentation_menu()
                elif choice == "2":
                    await self.segment_performance_menu()
                elif choice == "3":
                    await self.dynamic_delivery_status_menu()
                elif choice == "4":
                    await self.group_performance_menu()
                elif choice == "5":
                    await self.database_stats_menu()
                elif choice == "6":
                    await self.bot_performance_menu()
                elif choice == "7":
                    await self.database_cleanup_menu()
                elif choice == "8":
                    await self.dynamic_optimizer_control_menu()
                elif choice == "9":
                    await self.segment_users_list_menu()
                elif choice == "10":
                    await self.old_campaign_system_menu()
                elif choice == "11":
                    await self.package_management_menu()
                elif choice == "0":
                    print("👋 Görüşürüz!")
                    break
                else:
                    print("❌ Geçersiz seçim!")
            except Exception as e:
                print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")
    
    async def user_analysis_with_segmentation_menu(self):
        """Kullanıcı analizi ve segmentasyon menüsü"""
        print("\n📊 KULLANICI ANALİZİ & SEGMENTASYON")
        print("-" * 40)
        
        user_id = input("Kullanıcı ID girin: ").strip()
        if not user_id.isdigit():
            print("❌ Geçersiz kullanıcı ID!")
            return
        
        user_id = int(user_id)
        
        # Kullanıcı profilini al
        user_profile = await crm_db.get_user_profile(user_id)
        if not user_profile:
            print(f"❌ Kullanıcı bulunamadı: {user_id}")
            return
        
        print(f"\n👤 Kullanıcı: {user_profile.username} ({user_profile.first_name})")
        print(f"📅 İlk görülme: {user_profile.first_seen.strftime('%Y-%m-%d %H:%M')}")
        print(f"🕒 Son görülme: {user_profile.last_seen.strftime('%Y-%m-%d %H:%M')}")
        print(f"💬 Toplam etkileşim: {user_profile.total_interactions}")
        print(f"📈 Engagement skoru: {user_profile.engagement_score:.1f}/100")
        print(f"🎯 Dönüşüm potansiyeli: {user_profile.conversion_potential:.2f}")
        print(f"🤖 Tercih ettiği bot'lar: {', '.join(user_profile.preferred_bots)}")
        print(f"🏷️ İlgi alanları: {', '.join(user_profile.interests)}")
        
        # Segmentasyon analizi
        print("\n🎯 SEGMENT ANALİZİ")
        print("-" * 30)
        
        from core.user_segmentation import user_segmentation
        segments = await user_segmentation.segment_user(user_profile)
        
        if segments:
            for i, seg in enumerate(segments[:3], 1):
                print(f"\n{i}. Segment: {seg.segment.value} (Güven: {seg.confidence:.2f})")
                print(f"   Özellikler: {', '.join(seg.characteristics)}")
                print(f"   Öneriler: {', '.join(seg.recommended_actions[:2])}")
                print(f"   Optimal saatler: {seg.optimal_contact_times}")
                print(f"   Mesaj sıklığı: {seg.message_frequency}")
                print(f"   Dönüşüm olasılığı: {seg.conversion_probability:.2%}")
        
        # GPT analizi
        print("\n🤖 GPT ANALİZİ")
        print("-" * 30)
        analysis = await crm_analytics.analyze_user_behavior(user_profile)
        
        if analysis:
            print(f"🔥 Engagement seviyesi: {analysis.get('engagement_level', 'Bilinmiyor')}")
            print(f"💰 Dönüşüm olasılığı: {analysis.get('conversion_probability', 0):.2f}")
            print(f"⏰ Optimal iletişim saatleri: {analysis.get('optimal_contact_hours', [])}")
            print(f"📝 Önerilen yaklaşım: {analysis.get('recommended_approach', 'Belirtilmemiş')}")
        
        input("\nDevam etmek için Enter'a basın...")
    
    async def segment_performance_menu(self):
        """Segment performans menüsü"""
        print("\n🎯 SEGMENT PERFORMANS RAPORU")
        print("-" * 40)
        
        from core.user_segmentation import user_segmentation
        performance = await user_segmentation.analyze_segment_performance()
        
        if not performance:
            print("❌ Performans verisi bulunamadı!")
            return
        
        segment_stats = performance.get("segment_stats", {})
        
        print(f"\n📊 Toplam {len(segment_stats)} segment analiz edildi:")
        print("-" * 70)
        print(f"{'Segment':<20} {'Kullanıcı':<10} {'Eng.Skor':<10} {'Yanıt':<10} {'Performans':<15}")
        print("-" * 70)
        
        for segment_name, stats in segment_stats.items():
            print(f"{segment_name:<20} {stats['user_count']:<10} "
                  f"{stats['avg_engagement']:<10.1f} {stats['avg_response_rate']:<10.2%} "
                  f"{stats['performance_score']:<15.1f}")
        
        top_segments = performance.get("top_performing_segments", [])
        if top_segments:
            print(f"\n🏆 En iyi performans gösteren segmentler: {', '.join(top_segments[:3])}")
        
        input("\nDevam etmek için Enter'a basın...")
    
    async def dynamic_delivery_status_menu(self):
        """Dinamik gönderim durumu menüsü"""
        print("\n🚀 DİNAMİK GÖNDERİM DURUMU")
        print("-" * 40)
        
        from core.dynamic_delivery_optimizer import delivery_optimizer
        
        print(f"Durum: {'🟢 Aktif' if delivery_optimizer.running else '🔴 Durmuş'}")
        print(f"Kuyrukta bekleyen mesaj: {len(delivery_optimizer.message_queue)}")
        
        # Segment bazlı stratejiler
        print("\n📋 Segment Stratejileri:")
        print("-" * 60)
        
        for segment, strategy in delivery_optimizer.delivery_strategies.items():
            metrics = strategy.success_metrics
            print(f"\n{segment.value}:")
            print(f"  Öncelik: {strategy.priority}/10")
            print(f"  Sıklık: {strategy.frequency}")
            print(f"  Günlük limit: {strategy.max_messages_per_day}")
            print(f"  Yanıt oranı: {metrics.get('response_rate', 0):.2%}")
        
        # Performans geçmişi
        if delivery_optimizer.performance_history:
            print("\n📈 Son Performans Verileri:")
            for segment, history in list(delivery_optimizer.performance_history.items())[:3]:
                if history:
                    latest_date = max(history.keys())
                    latest_data = history[latest_date]
                    print(f"{segment.value}: {latest_data['response_rate']:.2%} yanıt ({latest_date})")
        
        print("\nSeçenekler:")
        print("1. Optimizer'ı Başlat/Durdur")
        print("2. Mesaj kuyruğunu temizle")
        print("3. Geri dön")
        
        choice = input("Seçiminizi yapın (1-3): ").strip()
        
        if choice == "1":
            if delivery_optimizer.running:
                await delivery_optimizer.stop_optimizer()
                print("⏹️ Optimizer durduruldu!")
            else:
                await delivery_optimizer.start_optimizer()
                print("🚀 Optimizer başlatıldı!")
        elif choice == "2":
            delivery_optimizer.message_queue.clear()
            print("🧹 Mesaj kuyruğu temizlendi!")
    
    async def segment_users_list_menu(self):
        """Segment bazlı kullanıcı listesi"""
        print("\n📋 SEGMENT BAZLI KULLANICI LİSTESİ")
        print("-" * 40)
        
        from core.user_segmentation import UserSegment, user_segmentation
        
        print("Mevcut segmentler:")
        for i, segment in enumerate(UserSegment, 1):
            print(f"{i}. {segment.value}")
        
        choice = input(f"\nSegment seçin (1-{len(UserSegment)}): ").strip()
        
        try:
            segment_index = int(choice) - 1
            selected_segment = list(UserSegment)[segment_index]
            
            print(f"\n🎯 {selected_segment.value} segmentindeki kullanıcılar:")
            print("-" * 60)
            
            users = await user_segmentation.get_segment_users(selected_segment, limit=20)
            
            if not users:
                print("Bu segmentte kullanıcı bulunamadı!")
                return
            
            print(f"{'ID':<12} {'Username':<20} {'İsim':<15} {'Engagement':<12} {'Son Görülme':<20}")
            print("-" * 80)
            
            for user in users:
                last_seen = user.last_seen.strftime('%Y-%m-%d %H:%M')
                print(f"{user.user_id:<12} {user.username[:19]:<20} "
                      f"{user.first_name[:14]:<15} {user.engagement_score:<12.1f} "
                      f"{last_seen:<20}")
            
            print(f"\nToplam {len(users)} kullanıcı gösteriliyor.")
            
        except (ValueError, IndexError):
            print("❌ Geçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")
    
    async def old_campaign_system_menu(self):
        """Eski kampanya sistemi menüsü"""
        print("\n🎯 ESKİ KAMPANYA SİSTEMİ")
        print("-" * 40)
        print("1. Kampanya Oluştur")
        print("2. Aktif Kampanyalar")
        print("3. Kampanya Yöneticisini Başlat/Durdur")
        print("4. Geri dön")
        
        choice = input("Seçiminizi yapın (1-4): ").strip()
        
        if choice == "1":
            await self.create_campaign_menu()
        elif choice == "2":
            await self.active_campaigns_menu()
        elif choice == "3":
            if smart_campaign_manager.running:
                await smart_campaign_manager.stop_campaign_manager()
                print("⏹️ Kampanya yöneticisi durduruldu!")
            else:
                await smart_campaign_manager.start_campaign_manager()
                print("🚀 Kampanya yöneticisi başlatıldı!")
        
        input("\nDevam etmek için Enter'a basın...")
    
    async def dynamic_optimizer_control_menu(self):
        """Dinamik optimizer kontrol menüsü"""
        print("\n🤖 DİNAMİK OPTİMİZER KONTROLÜ")
        print("-" * 40)
        
        from core.dynamic_delivery_optimizer import delivery_optimizer
        
        print(f"Mevcut durum: {'🟢 Çalışıyor' if delivery_optimizer.running else '🔴 Durmuş'}")
        print("1. Başlat")
        print("2. Durdur")
        print("3. Geri dön")
        
        choice = input("Seçiminizi yapın (1-3): ").strip()
        
        if choice == "1":
            if not delivery_optimizer.running:
                await delivery_optimizer.start_optimizer()
                print("✅ Dinamik optimizer başlatıldı!")
            else:
                print("⚠️ Optimizer zaten çalışıyor!")
        elif choice == "2":
            if delivery_optimizer.running:
                await delivery_optimizer.stop_optimizer()
                print("✅ Dinamik optimizer durduruldu!")
            else:
                print("⚠️ Optimizer zaten durmuş!")
    
    async def package_management_menu(self):
        """Paket yönetimi menüsü"""
        print("\n📦 PAKET YÖNETİMİ")
        print("-" * 40)
        
        from core.package_manager import package_manager, PackageType
        from core.profile_loader import get_all_profiles
        
        print("1. Bot paketlerini görüntüle")
        print("2. Bot paketini değiştir")
        print("3. Paket özelliklerini görüntüle")
        print("4. Geri dön")
        
        choice = input("Seçiminizi yapın (1-4): ").strip()
        
        if choice == "1":
            # Tüm bot'ların paketlerini göster
            profiles = get_all_profiles()
            
            print("\n📋 Bot Paketleri:")
            print("-" * 60)
            print(f"{'Bot':<20} {'User ID':<15} {'Paket':<15}")
            print("-" * 60)
            
            for username, profile in profiles.items():
                user_id = profile.get("user_id", "N/A")
                if user_id != "N/A":
                    package = package_manager.get_user_package(user_id)
                    print(f"{username:<20} {str(user_id):<15} {package.value:<15}")
                else:
                    print(f"{username:<20} {'N/A':<15} {'Basic (varsayılan)':<15}")
        
        elif choice == "2":
            # Bot paketi değiştir
            profiles = get_all_profiles()
            
            print("\nBot'lar:")
            bot_list = list(profiles.keys())
            for i, username in enumerate(bot_list, 1):
                print(f"{i}. {username}")
            
            bot_choice = input(f"\nBot seçin (1-{len(bot_list)}): ").strip()
            
            try:
                bot_index = int(bot_choice) - 1
                selected_bot = bot_list[bot_index]
                selected_profile = profiles[selected_bot]
                
                user_id = selected_profile.get("user_id")
                if not user_id:
                    print("❌ Bu bot'un user_id'si bulunamadı!")
                    return
                
                current_package = package_manager.get_user_package(user_id)
                print(f"\nMevcut paket: {current_package.value}")
                print("1. Basic")
                print("2. Enterprise")
                
                package_choice = input("Yeni paket seçin (1-2): ").strip()
                
                if package_choice == "1":
                    package_manager.set_user_package(user_id, PackageType.BASIC)
                    print(f"✅ {selected_bot} Basic pakete geçirildi!")
                elif package_choice == "2":
                    package_manager.set_user_package(user_id, PackageType.ENTERPRISE)
                    print(f"✅ {selected_bot} Enterprise pakete geçirildi!")
                else:
                    print("❌ Geçersiz seçim!")
                    
            except (ValueError, IndexError):
                print("❌ Geçersiz seçim!")
        
        elif choice == "3":
            # Paket özelliklerini göster
            print("\n📦 BASIC PAKET ÖZELLİKLERİ:")
            print("-" * 40)
            basic_info = package_manager.get_package_info(PackageType.BASIC)
            
            print("Özellikler:")
            for feature in basic_info["features"]:
                print(f"  • {feature}")
            
            print("\nLimitler:")
            for limit_name, limit_value in basic_info["limits"].items():
                print(f"  • {limit_name}: {limit_value}")
            
            print("\n\n🏢 ENTERPRISE PAKET ÖZELLİKLERİ:")
            print("-" * 40)
            enterprise_info = package_manager.get_package_info(PackageType.ENTERPRISE)
            
            print("Özellikler:")
            for feature in enterprise_info["features"]:
                print(f"  • {feature}")
            
            print("\nLimitler:")
            for limit_name, limit_value in enterprise_info["limits"].items():
                print(f"  • {limit_name}: {limit_value}")
        
        input("\nDevam etmek için Enter'a basın...")

    async def user_analysis_menu(self):
        """Kullanıcı analizi menüsü"""
        print("\n📊 KULLANICI ANALİZİ")
        print("-" * 40)
        
        user_id = input("Kullanıcı ID girin: ").strip()
        if not user_id.isdigit():
            print("❌ Geçersiz kullanıcı ID!")
            return
        
        user_id = int(user_id)
        
        # Kullanıcı profilini al
        user_profile = await crm_db.get_user_profile(user_id)
        if not user_profile:
            print(f"❌ Kullanıcı bulunamadı: {user_id}")
            return
        
        print(f"\n👤 Kullanıcı: {user_profile.username} ({user_profile.first_name})")
        print(f"📅 İlk görülme: {user_profile.first_seen.strftime('%Y-%m-%d %H:%M')}")
        print(f"🕒 Son görülme: {user_profile.last_seen.strftime('%Y-%m-%d %H:%M')}")
        print(f"💬 Toplam etkileşim: {user_profile.total_interactions}")
        print(f"📈 Engagement skoru: {user_profile.engagement_score:.1f}/100")
        print(f"🎯 Dönüşüm potansiyeli: {user_profile.conversion_potential:.2f}")
        print(f"🤖 Tercih ettiği bot'lar: {', '.join(user_profile.preferred_bots)}")
        print(f"🏷️ İlgi alanları: {', '.join(user_profile.interests)}")
        
        # GPT analizi yap
        print("\n🤖 GPT Analizi yapılıyor...")
        analysis = await crm_analytics.analyze_user_behavior(user_profile)
        
        if analysis:
            print(f"\n📊 Analiz Sonuçları:")
            print(f"🔥 Engagement seviyesi: {analysis.get('engagement_level', 'Bilinmiyor')}")
            print(f"💰 Dönüşüm olasılığı: {analysis.get('conversion_probability', 0):.2f}")
            print(f"⏰ Optimal iletişim saatleri: {analysis.get('optimal_contact_hours', [])}")
            print(f"📝 Önerilen yaklaşım: {analysis.get('recommended_approach', 'Belirtilmemiş')}")
            
            if analysis.get('opportunities'):
                print(f"\n🎯 Fırsatlar:")
                for opp in analysis['opportunities']:
                    print(f"  • {opp}")
            
            if analysis.get('next_actions'):
                print(f"\n📋 Önerilen aksiyonlar:")
                for action in analysis['next_actions']:
                    print(f"  • {action}")
        
        input("\nDevam etmek için Enter'a basın...")
    
    async def group_performance_menu(self):
        """Grup performans menüsü"""
        print("\n📈 GRUP PERFORMANS RAPORU")
        print("-" * 40)
        
        group_id = input("Grup ID girin (boş bırakırsanız tüm gruplar): ").strip()
        
        if group_id:
            if not group_id.lstrip('-').isdigit():
                print("❌ Geçersiz grup ID!")
                return
            
            group_id = int(group_id)
            await self._show_single_group_performance(group_id)
        else:
            await self._show_all_groups_performance()
        
        input("\nDevam etmek için Enter'a basın...")
    
    async def _show_single_group_performance(self, group_id: int):
        """Tek grup performansını göster"""
        group_profile = await crm_db.get_group_profile(group_id)
        if not group_profile:
            print(f"❌ Grup bulunamadı: {group_id}")
            return
        
        print(f"\n🏢 Grup: {group_profile.title}")
        print(f"👥 Üye sayısı: {group_profile.member_count}")
        print(f"📅 Keşfedilme: {group_profile.first_discovered.strftime('%Y-%m-%d')}")
        print(f"🕒 Son aktivite: {group_profile.last_activity.strftime('%Y-%m-%d %H:%M')}")
        print(f"📤 Gönderilen mesaj: {group_profile.total_messages_sent}")
        print(f"📥 Alınan yanıt: {group_profile.total_responses_received}")
        print(f"📊 Yanıt oranı: {group_profile.response_rate:.2%}")
        print(f"🎯 Aktivite seviyesi: {group_profile.activity_level}")
        print(f"⭐ Hedef önceliği: {group_profile.target_priority}/5")
        
        # Bot performansları
        if group_profile.bot_performance:
            print(f"\n🤖 Bot Performansları:")
            for bot_name, perf in group_profile.bot_performance.items():
                response_rate = 0
                if perf["messages_sent"] > 0:
                    response_rate = perf["responses_received"] / perf["messages_sent"]
                print(f"  • {bot_name}: {perf['messages_sent']} mesaj, {perf['responses_received']} yanıt ({response_rate:.2%})")
        
        # GPT analizi
        print("\n🤖 GPT Analizi yapılıyor...")
        analysis = await crm_analytics.analyze_group_performance(group_profile)
        
        if analysis:
            print(f"\n📊 Analiz Sonuçları:")
            print(f"🏆 Performans skoru: {analysis.get('performance_score', 0):.1f}/100")
            print(f"🎯 En iyi bot: {analysis.get('best_performing_bot', 'Belirtilmemiş')}")
            print(f"📅 Optimal mesaj sıklığı: {analysis.get('optimal_message_frequency', 'Belirtilmemiş')}")
            print(f"⚠️ Spam riski: {analysis.get('spam_risk_level', 'Bilinmiyor')}")
            print(f"🚀 Kampanya hazırlığı: {analysis.get('campaign_readiness', 'Bilinmiyor')}")
            print(f"💎 Hedef değeri: {analysis.get('target_value', 'Bilinmiyor')}")
            print(f"📝 Önerilen strateji: {analysis.get('recommended_strategy', 'Belirtilmemiş')}")
    
    async def _show_all_groups_performance(self):
        """Tüm grupların performansını göster"""
        # Redis'ten tüm grup anahtarlarını al
        keys = await crm_db.redis.keys("crm:group:*")
        
        if not keys:
            print("❌ Hiç grup bulunamadı!")
            return
        
        print(f"\n📊 Toplam {len(keys)} grup bulundu:")
        print("-" * 80)
        print(f"{'Grup ID':<12} {'Başlık':<25} {'Üye':<8} {'Mesaj':<8} {'Yanıt':<8} {'Oran':<8} {'Seviye':<10}")
        print("-" * 80)
        
        for key in keys[:20]:  # İlk 20 grubu göster
            group_id = int(key.decode().split(":")[-1])
            group_profile = await crm_db.get_group_profile(group_id)
            
            if group_profile:
                title = group_profile.title[:23] + ".." if len(group_profile.title) > 25 else group_profile.title
                print(f"{group_id:<12} {title:<25} {group_profile.member_count:<8} "
                      f"{group_profile.total_messages_sent:<8} {group_profile.total_responses_received:<8} "
                      f"{group_profile.response_rate:.1%:<8} {group_profile.activity_level:<10}")
        
        if len(keys) > 20:
            print(f"\n... ve {len(keys) - 20} grup daha")
    
    async def create_campaign_menu(self):
        """Kampanya oluşturma menüsü"""
        print("\n🎯 AKıLLı KAMPANYA OLUŞTUR")
        print("-" * 40)
        
        # Mevcut bot'ları listele
        from core.profile_loader import get_all_profiles
        profiles = get_all_profiles()
        
        if not profiles:
            print("❌ Hiç bot profili bulunamadı!")
            return
        
        print("Mevcut bot'lar:")
        for i, (username, profile) in enumerate(profiles.items(), 1):
            print(f"{i}. {username} - {profile.get('display_name', username)}")
        
        choice = input(f"\nBot seçin (1-{len(profiles)}): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(profiles)):
            print("❌ Geçersiz seçim!")
            return
        
        bot_username = list(profiles.keys())[int(choice) - 1]
        
        print(f"\n🤖 Seçilen bot: {bot_username}")
        print("Kampanya türleri:")
        print("1. Engagement (Etkileşim artırma)")
        print("2. VIP Sales (VIP satış)")
        print("3. Reactivation (Yeniden aktivasyon)")
        
        campaign_type_choice = input("Kampanya türü seçin (1-3): ").strip()
        campaign_types = {"1": "engagement", "2": "vip_sales", "3": "reactivation"}
        
        if campaign_type_choice not in campaign_types:
            print("❌ Geçersiz kampanya türü!")
            return
        
        campaign_type = campaign_types[campaign_type_choice]
        
        print(f"\n🚀 {bot_username} için {campaign_type} kampanyası oluşturuluyor...")
        
        campaign_id = await smart_campaign_manager.create_smart_campaign(bot_username, campaign_type)
        
        if campaign_id:
            print(f"✅ Kampanya başarıyla oluşturuldu!")
            print(f"🆔 Kampanya ID: {campaign_id}")
            
            # Kampanya detaylarını göster
            status = await smart_campaign_manager.get_campaign_status(campaign_id)
            if status and "error" not in status:
                print(f"📊 Hedef grup sayısı: {status['target_groups']}")
                print(f"📝 Toplam mesaj: {status['total_messages']}")
                print(f"📅 Başlangıç: {status['start_time']}")
                print(f"📅 Bitiş: {status['end_time']}")
        else:
            print("❌ Kampanya oluşturulamadı!")
    
    async def active_campaigns_menu(self):
        """Aktif kampanyalar menüsü"""
        print("\n📋 AKTİF KAMPANYALAR")
        print("-" * 40)
        
        campaigns = smart_campaign_manager.active_campaigns
        
        if not campaigns:
            print("❌ Aktif kampanya bulunamadı!")
            return
        
        print(f"Toplam {len(campaigns)} kampanya:")
        print("-" * 80)
        
        for campaign_id, campaign in campaigns.items():
            status = await smart_campaign_manager.get_campaign_status(campaign_id)
            if status and "error" not in status:
                print(f"\n🆔 {campaign_id}")
                print(f"🤖 Bot: {status['bot_username']}")
                print(f"📊 Durum: {status['status']}")
                print(f"📝 Mesajlar: {status['sent_messages']}/{status['total_messages']}")
                print(f"🎯 Hedef gruplar: {status['target_groups']}")
        
        # Kampanya yönetimi
        print("\nKampanya yönetimi:")
        print("1. Kampanya duraklat")
        print("2. Kampanya devam ettir")
        print("3. Geri dön")
        
        choice = input("Seçiminizi yapın (1-3): ").strip()
        
        if choice == "1":
            campaign_id = input("Duraklatılacak kampanya ID: ").strip()
            if await smart_campaign_manager.pause_campaign(campaign_id):
                print("✅ Kampanya duraklatıldı!")
            else:
                print("❌ Kampanya duraklatılamadı!")
        
        elif choice == "2":
            campaign_id = input("Devam ettirilecek kampanya ID: ").strip()
            if await smart_campaign_manager.resume_campaign(campaign_id):
                print("✅ Kampanya devam ettirildi!")
            else:
                print("❌ Kampanya devam ettirilemedi!")
    
    async def database_stats_menu(self):
        """Veritabanı istatistikleri"""
        print("\n🔍 CRM VERİTABANI İSTATİSTİKLERİ")
        print("-" * 40)
        
        # Redis istatistikleri
        try:
            # Kullanıcı sayısı
            user_keys = await crm_db.redis.keys("crm:user:*")
            user_count = len(user_keys)
            
            # Grup sayısı
            group_keys = await crm_db.redis.keys("crm:group:*")
            group_count = len(group_keys)
            
            # Mesaj sayısı
            message_keys = await crm_db.redis.keys("crm:message:*")
            message_count = len(message_keys)
            
            print(f"👥 Toplam kullanıcı: {user_count}")
            print(f"🏢 Toplam grup: {group_count}")
            print(f"💬 Toplam mesaj kaydı: {message_count}")
            
            # Son 24 saatteki aktivite
            yesterday = datetime.now() - timedelta(days=1)
            recent_users = 0
            recent_groups = 0
            
            # Son 24 saatte aktif kullanıcıları say
            for key in user_keys[:100]:  # İlk 100 kullanıcıyı kontrol et
                user_id = int(key.decode().split(":")[-1])
                user_profile = await crm_db.get_user_profile(user_id)
                if user_profile and user_profile.last_seen > yesterday:
                    recent_users += 1
            
            # Son 24 saatte aktif grupları say
            for key in group_keys[:100]:  # İlk 100 grubu kontrol et
                group_id = int(key.decode().split(":")[-1])
                group_profile = await crm_db.get_group_profile(group_id)
                if group_profile and group_profile.last_activity > yesterday:
                    recent_groups += 1
            
            print(f"\n📊 Son 24 saat:")
            print(f"👥 Aktif kullanıcı: {recent_users}")
            print(f"🏢 Aktif grup: {recent_groups}")
            
            # Redis bellek kullanımı
            info = await crm_db.redis.info("memory")
            used_memory = info.get("used_memory_human", "Bilinmiyor")
            print(f"\n💾 Redis bellek kullanımı: {used_memory}")
            
        except Exception as e:
            print(f"❌ İstatistik alma hatası: {e}")
    
    async def bot_performance_menu(self):
        """Bot performans raporu"""
        print("\n📊 BOT PERFORMANS RAPORU")
        print("-" * 40)
        
        # Mevcut bot'ları listele
        from core.profile_loader import get_all_profiles
        profiles = get_all_profiles()
        
        if not profiles:
            print("❌ Hiç bot profili bulunamadı!")
            return
        
        print("Mevcut bot'lar:")
        for i, (username, profile) in enumerate(profiles.items(), 1):
            print(f"{i}. {username} - {profile.get('display_name', username)}")
        
        choice = input(f"\nBot seçin (1-{len(profiles)}) veya 0 (tümü): ").strip()
        
        if choice == "0":
            # Tüm bot'lar için rapor
            for username in profiles.keys():
                await self._show_bot_performance(username)
                print("-" * 40)
        else:
            if not choice.isdigit() or not (1 <= int(choice) <= len(profiles)):
                print("❌ Geçersiz seçim!")
                return
            
            bot_username = list(profiles.keys())[int(choice) - 1]
            await self._show_bot_performance(bot_username)
    
    async def _show_bot_performance(self, bot_username: str):
        """Bot performansını göster"""
        print(f"\n🤖 Bot: {bot_username}")
        
        # 7 günlük rapor oluştur
        report = await crm_analytics.generate_performance_report(bot_username, 7)
        
        if report and "error" not in report:
            stats = report.get("stats", {})
            print(f"📤 Gönderilen mesaj: {stats.get('total_messages_sent', 0)}")
            print(f"📥 Alınan yanıt: {stats.get('total_responses_received', 0)}")
            print(f"🏢 Ulaşılan grup: {stats.get('unique_groups_reached', 0)}")
            print(f"👥 Etkileşim kurulan kullanıcı: {stats.get('unique_users_engaged', 0)}")
            print(f"📊 Ortalama yanıt oranı: {stats.get('average_response_rate', 0):.2%}")
            
            # GPT analizi
            analysis = report.get("analysis", "")
            if analysis:
                print(f"\n📝 GPT Analizi:")
                print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
        else:
            print("❌ Performans raporu oluşturulamadı!")
    
    async def database_cleanup_menu(self):
        """Veritabanı temizliği"""
        print("\n🧹 VERİTABANI TEMİZLİĞİ")
        print("-" * 40)
        print("⚠️  Bu işlem eski verileri silecektir!")
        print("1. 30 günden eski mesaj kayıtlarını sil")
        print("2. 90 günden eski kullanıcı verilerini sil")
        print("3. Kullanılmayan grup kayıtlarını sil")
        print("4. Geri dön")
        
        choice = input("Seçiminizi yapın (1-4): ").strip()
        
        if choice == "1":
            confirm = input("30 günden eski mesajları silmek istediğinizden emin misiniz? (evet/hayır): ")
            if confirm.lower() == "evet":
                await self._cleanup_old_messages(30)
        
        elif choice == "2":
            confirm = input("90 günden eski kullanıcı verilerini silmek istediğinizden emin misiniz? (evet/hayır): ")
            if confirm.lower() == "evet":
                await self._cleanup_old_users(90)
        
        elif choice == "3":
            confirm = input("Kullanılmayan grup kayıtlarını silmek istediğinizden emin misiniz? (evet/hayır): ")
            if confirm.lower() == "evet":
                await self._cleanup_unused_groups()
    
    async def _cleanup_old_messages(self, days: int):
        """Eski mesajları temizle"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            message_keys = await crm_db.redis.keys("crm:message:*")
            
            deleted_count = 0
            for key in message_keys:
                # Timestamp'i key'den çıkar
                try:
                    timestamp = int(key.decode().split(":")[-1])
                    message_date = datetime.fromtimestamp(timestamp)
                    
                    if message_date < cutoff_date:
                        await crm_db.redis.delete(key)
                        deleted_count += 1
                except:
                    continue
            
            print(f"✅ {deleted_count} eski mesaj kaydı silindi!")
            
        except Exception as e:
            print(f"❌ Mesaj temizleme hatası: {e}")
    
    async def _cleanup_old_users(self, days: int):
        """Eski kullanıcıları temizle"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            user_keys = await crm_db.redis.keys("crm:user:*")
            
            deleted_count = 0
            for key in user_keys:
                user_id = int(key.decode().split(":")[-1])
                user_profile = await crm_db.get_user_profile(user_id)
                
                if user_profile and user_profile.last_seen < cutoff_date:
                    await crm_db.redis.delete(key)
                    deleted_count += 1
            
            print(f"✅ {deleted_count} eski kullanıcı kaydı silindi!")
            
        except Exception as e:
            print(f"❌ Kullanıcı temizleme hatası: {e}")
    
    async def _cleanup_unused_groups(self):
        """Kullanılmayan grupları temizle"""
        try:
            group_keys = await crm_db.redis.keys("crm:group:*")
            cutoff_date = datetime.now() - timedelta(days=60)  # 60 gün aktivite yok
            
            deleted_count = 0
            for key in group_keys:
                group_id = int(key.decode().split(":")[-1])
                group_profile = await crm_db.get_group_profile(group_id)
                
                if (group_profile and 
                    group_profile.last_activity < cutoff_date and 
                    group_profile.total_messages_sent == 0):
                    await crm_db.redis.delete(key)
                    deleted_count += 1
            
            print(f"✅ {deleted_count} kullanılmayan grup kaydı silindi!")
            
        except Exception as e:
            print(f"❌ Grup temizleme hatası: {e}")
    
    async def start_campaign_manager(self):
        """Kampanya yöneticisini başlat"""
        try:
            if smart_campaign_manager.running:
                print("⚠️ Kampanya yöneticisi zaten çalışıyor!")
                return
            
            await smart_campaign_manager.start_campaign_manager()
            print("✅ Kampanya yöneticisi başlatıldı!")
            
        except Exception as e:
            print(f"❌ Kampanya yöneticisi başlatma hatası: {e}")
    
    async def stop_campaign_manager(self):
        """Kampanya yöneticisini durdur"""
        try:
            if not smart_campaign_manager.running:
                print("⚠️ Kampanya yöneticisi zaten durmuş!")
                return
            
            await smart_campaign_manager.stop_campaign_manager()
            print("✅ Kampanya yöneticisi durduruldu!")
            
        except Exception as e:
            print(f"❌ Kampanya yöneticisi durdurma hatası: {e}")

async def main():
    """Ana fonksiyon"""
    crm_manager = CRMManager()
    await crm_manager.show_main_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Çıkılıyor...")
    except Exception as e:
        print(f"❌ Fatal hata: {e}") 