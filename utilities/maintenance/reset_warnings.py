#!/usr/bin/env python3

import json
from pathlib import Path

def reset_all_warnings():
    """Tüm botların uyarılarını sıfırla ve spam'i aktifleştir"""
    
    personas_dir = Path("data/personas")
    
    for persona_file in personas_dir.glob("*.json"):
        if persona_file.name in [".gitkeep", "customer_bot_example.json", "test_user.json", "test_producer.json", "test_gavatbaba.json"]:
            continue
            
        try:
            with open(persona_file, "r", encoding="utf-8") as f:
                profile = json.load(f)
            
            username = profile.get("username", persona_file.stem)
            bot_type = profile.get("type", "unknown")
            
            # Sadece bot tipindeki profilleri işle
            if bot_type == "bot" and username in ["yayincilara", "babagavat"]:
                # Güvenli modu kapat
                profile["safe_mode"] = False
                profile["autospam"] = True
                profile["reply_mode"] = "hybrid"
                
                # Dosyayı güncelle
                with open(persona_file, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {username}: Uyarılar sıfırlandı, spam aktifleştirildi")
            
        except Exception as e:
            print(f"❌ {persona_file.name}: Hata - {e}")

if __name__ == "__main__":
    reset_all_warnings()
    print("\n🔄 Tüm uyarılar sıfırlandı! Sistemi yeniden başlatın.") 