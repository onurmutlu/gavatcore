#!/usr/bin/env python3
"""
BEHAVIORAL & PSYCHOLOGICAL ENGINE TEST
=====================================

Behavioral engine'i test etmek ve örnek çıktıları görmek için test scripti.

Kullanım:
    python test_behavioral_engine.py
"""

import asyncio
import json
from typing import List

# Core import
from core.behavioral_psychological_engine import BehavioralPsychologicalEngine

async def test_behavioral_engine():
    """Behavioral engine test fonksiyonu"""
    
    print("🧠" + "="*60 + "🧠")
    print("🚀 BEHAVIORAL & PSYCHOLOGICAL ENGINE TEST")
    print("🧠" + "="*60 + "🧠")
    print()
    
    # Engine'i başlat
    engine = BehavioralPsychologicalEngine()
    
    # Test mesajları (farklı kullanıcı tipleri)
    test_cases = [
        {
            "user_id": 123456,
            "name": "Sosyal Ali",
            "messages": [
                "Merhaba! Bu grup çok eğlenceli 😊",
                "Arkadaşlarımla birlikte gelmeyi planlıyoruz",
                "Grubumuz var, siz de katılmak ister misiniz?",
                "Beraber bir şeyler yapalım, çok eğlenceli olur!",
                "Takım halinde çalışmayı seviyorum"
            ]
        },
        {
            "user_id": 789012,
            "name": "Analitik Ayşe", 
            "messages": [
                "Bu sistem nasıl çalışıyor? Detayları öğrenmek istiyorum",
                "Neden bu yöntemi tercih ettiniz?",
                "Başka alternatifler var mı? Karşılaştırma yapmak istiyorum",
                "Bu konuda daha fazla bilgi alabilir miyim?",
                "Verileri analiz etmek için hangi araçları kullanıyorsunuz?"
            ]
        },
        {
            "user_id": 345678,
            "name": "Yaratıcı Mehmet",
            "messages": [
                "Harika bir tasarım! 🎨✨",
                "Çok yaratıcı bir yaklaşım 💡",
                "Ben de müzik yapıyorum, sanat çok önemli",
                "Görsel olarak çok etkileyici! 🌈",
                "Yeni fikirler üretmeyi seviyorum 🚀"
            ]
        },
        {
            "user_id": 901234,
            "name": "Direkt Fatma",
            "messages": [
                "Hemen başlayalım, zaman kaybetmeyelim!",
                "Net bir cevap istiyorum, açık konuşalım",
                "Sonuç odaklı çalışmayı tercih ederim",
                "Hızlı ve etkili çözümler lazım!",
                "Boş laf istemiyorum, direkt konuya girelim"
            ]
        },
        {
            "user_id": 567890,
            "name": "Flörtöz Emre",
            "messages": [
                "Merhaba güzelim 😘💋",
                "Seninle tanışmak çok güzel! 🔥",
                "Bu akşam müsait misin? ✨",
                "Çok tatlısın, seni beğendim 💎",
                "Özelde konuşalım mı tatlım? 🌹"
            ]
        }
    ]
    
    # Her test case'i analiz et
    for i, test_case in enumerate(test_cases, 1):
        print(f"📊 TEST CASE {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Behavioral analiz
            analysis = await engine.analyze_user_behavior(
                test_case["messages"], 
                test_case["user_id"]
            )
            
            if analysis.get("error"):
                print(f"❌ Hata: {analysis['error']}")
                continue
            
            # Sonuçları göster
            print(f"👤 Kullanıcı ID: {analysis['user_id']}")
            print(f"🧠 Kişilik Tipi: {analysis['personality_type']}")
            print(f"📈 Etkileşim Seviyesi: {analysis['engagement_level']}")
            print(f"💬 İletişim Tarzı: {analysis['communication_style']}")
            print(f"🎯 İlgi Alanları: {', '.join(analysis['interests']) if analysis['interests'] else 'Belirlenmedi'}")
            print(f"📊 Davranışsal Skor: {analysis['behavioral_score']:.2f}")
            
            # Text analysis detayları
            text_analysis = analysis['text_analysis']
            print(f"\n📝 Metin Analizi:")
            print(f"   • Ortalama mesaj uzunluğu: {text_analysis['avg_message_length']:.1f}")
            print(f"   • Emoji kullanımı: {text_analysis['emoji_usage']:.2f}")
            print(f"   • Soru oranı: {text_analysis['question_ratio']:.2f}")
            print(f"   • Ünlem oranı: {text_analysis['exclamation_ratio']:.2f}")
            print(f"   • Duygu skoru: {text_analysis['sentiment_score']:.2f}")
            
            # GPT insights
            if analysis['gpt_insights']:
                print(f"\n🤖 GPT Analizi:")
                gpt_insights = analysis['gpt_insights']
                if 'personality_traits' in gpt_insights:
                    print(f"   • Kişilik özellikleri: {', '.join(gpt_insights['personality_traits'])}")
                if 'emotional_state' in gpt_insights:
                    print(f"   • Duygusal durum: {gpt_insights['emotional_state']}")
                if 'social_behavior' in gpt_insights:
                    print(f"   • Sosyal davranış: {gpt_insights['social_behavior']}")
            
            # Kişiselleştirilmiş strateji oluştur
            print(f"\n🎯 Kişiselleştirilmiş strateji oluşturuluyor...")
            strategy = await engine.create_personalized_strategy(analysis)
            
            print(f"\n📋 STRATEJİ ÖNERİSİ:")
            print(strategy)
            
            # Engagement methods
            print(f"\n💡 ETKİLEŞİM YÖNTEMLERİ:")
            engagement_methods = engine.suggest_user_engagement_methods(analysis)
            for j, method in enumerate(engagement_methods[:5], 1):  # İlk 5 metod
                print(f"   {j}. {method}")
                
        except Exception as e:
            print(f"❌ Test hatası: {e}")
        
        print("\n" + "="*60 + "\n")
    
    # Engine istatistikleri
    print("📊 ENGINE İSTATİSTİKLERİ:")
    stats = engine.get_engine_stats()
    print(f"   • Toplam profil: {stats['total_profiles']}")
    print(f"   • GPT mevcut: {stats['gpt_available']}")
    print(f"   • Gelişmiş analitik: {stats['advanced_analytics']}")
    print(f"   • Kişilik dağılımı: {stats['personality_distribution']}")
    print(f"   • Etkileşim dağılımı: {stats['engagement_distribution']}")
    
    print("\n✅ Test tamamlandı!")

async def test_user_consent_and_privacy():
    """Kullanıcı rızası ve gizlilik testleri"""
    
    print("\n🔒 ETİK VE GİZLİLİK TESTLERİ")
    print("-" * 40)
    
    engine = BehavioralPsychologicalEngine()
    test_user_id = 999999
    
    # Fake profil oluştur
    await engine.analyze_user_behavior(
        ["Test mesajı", "İkinci test", "Üçüncü test"], 
        test_user_id
    )
    
    # Consent güncelleme testi
    print("🔐 Kullanıcı rızası güncelleniyor...")
    success = engine.update_user_consent(test_user_id, True, "high")
    print(f"   Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}")
    
    # Opt-out testi
    print("🚫 Opt-out talebi kaydediliyor...")
    success = engine.add_opt_out_request(test_user_id, "data_collection")
    print(f"   Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}")
    
    # Profil kontrolü
    profile = engine.get_user_profile(test_user_id)
    if profile:
        print(f"👤 Profil durumu:")
        print(f"   • Rıza verildi: {profile.consent_given}")
        print(f"   • Gizlilik seviyesi: {profile.privacy_level}")
        print(f"   • Opt-out talepleri: {profile.opt_out_requests}")

def main():
    """Ana test fonksiyonu"""
    try:
        # Asenkron testleri çalıştır
        asyncio.run(test_behavioral_engine())
        asyncio.run(test_user_consent_and_privacy())
        
    except KeyboardInterrupt:
        print("\n⌨️ Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")

if __name__ == "__main__":
    main()