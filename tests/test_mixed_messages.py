#!/usr/bin/env python3
# test_mixed_messages.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
from utils.smart_reply import smart_reply

def test_mixed_message_system():
    print("🧪 Karışık Mesaj Sistemi Test Ediliyor...\n")
    
    # Test bot profili (Geisha'dan örnek)
    test_bot_profile = {
        "engaging_messages": [
            "Geceyi birlikte renklendirecek biri var mı burada? 🌃",
            "Bu gece biraz daha özel geçebilir... Kim benimle? 🔥",
            "Kendini yalnız hissedenler için buradayım... ✨"
        ],
        "reply_messages": [
            "Ağzından dökülen kelimelere bayıldım... Devam et 😍",
            "Beni biraz utandırdın ama hoşuma gitti 🙈",
            "Bu cevabınla beni etkiledin... Daha fazlasını isterim 💌"
        ]
    }
    
    print("1️⃣ Bot Engaging Mesajları:")
    for msg in test_bot_profile["engaging_messages"]:
        print(f"   📝 {msg}")
    print()
    
    print("2️⃣ Bot Reply Mesajları:")
    for msg in test_bot_profile["reply_messages"]:
        print(f"   💬 {msg}")
    print()
    
    print("3️⃣ Genel Havuz Mesajları (ilk 5):")
    for i, msg in enumerate(smart_reply.global_engaging_messages[:5]):
        print(f"   🌐 {msg}")
    print()
    
    print("4️⃣ Karışık Engaging Mesajları (10 test):")
    engaging_stats = {"bot": 0, "global": 0}
    for i in range(10):
        mixed_msg = smart_reply.get_mixed_messages(test_bot_profile["engaging_messages"], "engaging")
        
        # Hangi havuzdan geldiğini tespit et
        if mixed_msg in test_bot_profile["engaging_messages"]:
            source = "🤖 BOT"
            engaging_stats["bot"] += 1
        else:
            source = "🌐 GLOBAL"
            engaging_stats["global"] += 1
        
        print(f"   {i+1:2d}. {source}: {mixed_msg}")
    
    print(f"\n   📊 Engaging Dağılım: Bot %{engaging_stats['bot']*10}, Global %{engaging_stats['global']*10}")
    print()
    
    print("5️⃣ Karışık Reply Mesajları (10 test):")
    reply_stats = {"bot": 0, "global": 0}
    for i in range(10):
        mixed_msg = smart_reply.get_mixed_messages(test_bot_profile["reply_messages"], "reply")
        
        # Hangi havuzdan geldiğini tespit et
        if mixed_msg in test_bot_profile["reply_messages"]:
            source = "🤖 BOT"
            reply_stats["bot"] += 1
        else:
            source = "🌐 GLOBAL"
            reply_stats["global"] += 1
        
        print(f"   {i+1:2d}. {source}: {mixed_msg}")
    
    print(f"\n   📊 Reply Dağılım: Bot %{reply_stats['bot']*10}, Global %{reply_stats['global']*10}")
    print()
    
    print("6️⃣ Boş Bot Mesajları ile Test:")
    empty_bot_profile = {"engaging_messages": [], "reply_messages": []}
    
    print("   Engaging (boş bot mesajları):")
    for i in range(3):
        mixed_msg = smart_reply.get_mixed_messages(empty_bot_profile["engaging_messages"], "engaging")
        print(f"   {i+1}. 🌐 FALLBACK: {mixed_msg}")
    
    print("\n   Reply (boş bot mesajları):")
    for i in range(3):
        mixed_msg = smart_reply.get_mixed_messages(empty_bot_profile["reply_messages"], "reply")
        print(f"   {i+1}. 🌐 FALLBACK: {mixed_msg}")
    print()
    
    print("7️⃣ Smart Reply Template Test:")
    test_messages = [
        "Merhaba",
        "Nasılsın?",
        "Çok güzelsin",
        "Buluşalım mı?",
        "Fiyatların nedir?",
        "❤️💕",
        "😘😍",
        "Teşekkürler"
    ]
    
    for msg in test_messages:
        response = smart_reply.find_template_response(msg, test_bot_profile)
        if response:
            print(f"   📥 '{msg}' → 📤 '{response}'")
        else:
            print(f"   📥 '{msg}' → ❌ Template bulunamadı")

if __name__ == "__main__":
    test_mixed_message_system() 