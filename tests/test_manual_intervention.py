#!/usr/bin/env python3
# test_manual_intervention.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import time
from handlers.dm_handler import (
    update_conversation_state, 
    should_send_followup,
    dm_conversation_state
)

def test_manual_intervention_flow():
    print("🧪 Manuel Müdahale Sonrası Conversation Flow Test Ediliyor...\n")
    
    # Test DM key'i
    test_dm_key = "dm:geishaniz:12345"
    
    print("1️⃣ İlk kullanıcı mesajı (normal flow):")
    state = update_conversation_state(test_dm_key, user_responded=True)
    print(f"   Phase: {state['phase']}")
    print(f"   Takip gerekli mi: {should_send_followup(test_dm_key)}")
    print()
    
    print("2️⃣ Bot otomatik mesaj gönderdi:")
    state = update_conversation_state(test_dm_key, bot_sent_message=True)
    print(f"   Phase: {state['phase']}")
    print(f"   User responded: {state['user_responded']}")
    print()
    
    print("3️⃣ Manuel müdahale yapıldı:")
    state = update_conversation_state(test_dm_key, manual_intervention=True)
    print(f"   Phase: {state['phase']}")
    print(f"   Manuel müdahale zamanı: {state['manual_intervention_time']}")
    print(f"   Followup count reset: {state['followup_count']}")
    print()
    
    print("4️⃣ Manuel müdahale sonrası 1 saat (normal takip süresi):")
    # 1 saat önceki timestamp simüle et
    dm_conversation_state[test_dm_key]["manual_intervention_time"] = time.time() - 3700
    print(f"   Takip gerekli mi: {should_send_followup(test_dm_key)} (Hayır olmalı - çok erken)")
    print()
    
    print("5️⃣ Manuel müdahale sonrası 3 saat:")
    # 3 saat önceki timestamp simüle et
    dm_conversation_state[test_dm_key]["manual_intervention_time"] = time.time() - 10900
    dm_conversation_state[test_dm_key]["last_user_message"] = time.time() - 10900
    print(f"   Takip gerekli mi: {should_send_followup(test_dm_key)} (Hayır olmalı - henüz 4 saat olmadı)")
    print()
    
    print("6️⃣ Manuel müdahale sonrası 5 saat:")
    # 5 saat önceki timestamp simüle et
    dm_conversation_state[test_dm_key]["last_user_message"] = time.time() - 18100
    print(f"   Takip gerekli mi: {should_send_followup(test_dm_key)} (Evet olmalı - 4+ saat geçti)")
    print()
    
    print("7️⃣ Kullanıcı cevap verdi (active_conversation'a geçiş):")
    state = update_conversation_state(test_dm_key, user_responded=True)
    print(f"   Phase: {state['phase']}")
    print(f"   Last manual check: {state['last_manual_check']}")
    print()
    
    print("8️⃣ Active conversation'da 3 saat sonra:")
    # 3 saat önceki timestamp simüle et
    dm_conversation_state[test_dm_key]["last_user_message"] = time.time() - 10900
    print(f"   Takip gerekli mi: {should_send_followup(test_dm_key)} (Hayır olmalı - 6 saat beklemeli)")
    print()
    
    print("9️⃣ Active conversation'da 7 saat sonra:")
    # 7 saat önceki timestamp simüle et
    dm_conversation_state[test_dm_key]["last_user_message"] = time.time() - 25300
    print(f"   Takip gerekli mi: {should_send_followup(test_dm_key)} (Evet olmalı - 6+ saat geçti)")
    print()
    
    print("🔟 State temizleme:")
    dm_conversation_state.clear()
    print(f"   State temizlendi: {len(dm_conversation_state)} entry")

if __name__ == "__main__":
    test_manual_intervention_flow() 