#!/usr/bin/env python3

import asyncio
import redis
import json

async def reset_dm_states():
    """Tüm DM conversation state'lerini sıfırla"""
    
    try:
        # Redis bağlantısı
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # DM state key'lerini bul
        dm_keys = r.keys("dm:*:conversation_state")
        
        print(f"🔍 {len(dm_keys)} DM state bulundu")
        
        for key in dm_keys:
            try:
                # State'i al
                state_json = r.get(key)
                if state_json:
                    state = json.loads(state_json)
                    
                    # Manuel mod durumunu sıfırla
                    state["manual_mode_active"] = False
                    state["auto_messages_paused"] = False
                    state["phase"] = "initial_contact"
                    
                    # State'i geri kaydet
                    r.set(key, json.dumps(state), ex=86400)  # 24 saat TTL
                    
                    print(f"✅ {key} sıfırlandı")
                
            except Exception as e:
                print(f"❌ {key} sıfırlama hatası: {e}")
        
        print(f"\n🔄 {len(dm_keys)} DM state sıfırlandı!")
        print("📝 Manuel mod durumları temizlendi")
        print("🚀 Otomatik mesajlar yeniden aktifleştirildi")
        
    except Exception as e:
        print(f"💥 Redis bağlantı hatası: {e}")
        print("⚠️  Redis çalışmıyor olabilir")

if __name__ == "__main__":
    asyncio.run(reset_dm_states()) 