#!/usr/bin/env python3
# tests/test_hybrid_mode.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from utilities.smart_reply import smart_reply

async def test_hybrid_mode():
    """Hybrid mode'u test et"""
    
    print("🎭 HYBRID MODE TEST BAŞLIYOR...")
    print("=" * 50)
    
    # Test bot profili
    test_profile = {
        "username": "babagavat",
        "display_name": "Gavat Baba",
        "reply_mode": "hybrid",
        "persona": {
            "gpt_prompt": "Gavat Baba, 35 yaşında, deneyimli bir pezevenk. Ortama hakim, karizmatik, zeki espriler yapan, güven veren ve işleri tatlı dille çözen bir lider figürüdür."
        },
        "reply_messages": [
            "Beni tanıyan bilir, işim ciddidir ama eğlencelidir 😎",
            "Senin gibi zeki biriyle muhabbet etmek keyif 🌟",
            "Bu tarzı seviyorum... devam et 💬"
        ]
    }
    
    # Test mesajları
    test_messages = [
        "Merhaba",
        "Nasılsın?",
        "VIP grubun var mı?",
        "Fiyatların nedir?",
        "Çok güzelsin",
        "Buluşalım mı?",
        "Teşekkürler",
        "Ne yapıyorsun?",
        "Özel içerik var mı?",
        "Seni seviyorum ❤️"
    ]
    
    print("📊 HYBRID MODE DAĞILIM TESTİ")
    print("Beklenen: %60 GPT, %30 Bot Profili, %10 Genel Mesajlar")
    print("-" * 50)
    
    # Her mesaj için 10 test yap
    for message in test_messages:
        print(f"\n💬 Test Mesajı: '{message}'")
        print("-" * 30)
        
        gpt_count = 0
        bot_count = 0
        global_count = 0
        
        # 10 kez test et
        for i in range(10):
            try:
                response = await smart_reply.get_hybrid_reply(message, test_profile, "babagavat")
                
                # Yanıt tipini tahmin et (log mesajlarından)
                if "🤖 HYBRID GPT:" in str(response):
                    gpt_count += 1
                elif "👤 HYBRID BOT:" in str(response):
                    bot_count += 1
                elif "🌐 HYBRID GLOBAL:" in str(response):
                    global_count += 1
                
                print(f"  {i+1:2d}. {response}")
                
            except Exception as e:
                print(f"  {i+1:2d}. ❌ Hata: {e}")
        
        # İstatistikleri göster
        print(f"\n📈 Dağılım: GPT: {gpt_count}/10, Bot: {bot_count}/10, Global: {global_count}/10")
    
    print("\n" + "=" * 50)
    print("🎯 VIP SATIŞI ODAKLI TEST")
    print("=" * 50)
    
    # VIP satış odaklı test
    vip_test_messages = [
        "Merhaba canım",
        "Ne yapıyorsun?",
        "Özel bir şey var mı?",
        "VIP grubun nasıl?",
        "Fiyatların ne kadar?"
    ]
    
    for message in vip_test_messages:
        print(f"\n💎 VIP Test: '{message}'")
        try:
            response = await smart_reply.get_hybrid_reply(message, test_profile, "babagavat")
            print(f"   Yanıt: {response}")
            
            # VIP anahtar kelimelerini kontrol et
            vip_keywords = ["vip", "özel", "premium", "grup", "kanal", "exclusive"]
            has_vip = any(keyword in response.lower() for keyword in vip_keywords)
            print(f"   VIP İçerik: {'✅' if has_vip else '❌'}")
            
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    print("\n🎉 TEST TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(test_hybrid_mode()) 