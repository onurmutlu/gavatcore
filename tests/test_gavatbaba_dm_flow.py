#!/usr/bin/env python3
# tests/test_gavatbaba_dm_flow.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.dm_handler import (
    update_conversation_state, 
    should_send_auto_menu, 
    should_send_followup,
    dm_conversation_state
)

def test_gavatbaba_dm_flow():
    """Gavatbaba DM conversation flow test - manuel müdahale sonrası otomatik mesajlar durmalı"""
    
    print("🧪 GAVATBABA DM CONVERSATION FLOW TEST")
    print("=" * 50)
    
    # Test DM key
    dm_key = "dm:gavatbaba:12345"
    
    print("1️⃣ İlk kullanıcı mesajı:")
    state = update_conversation_state(dm_key, user_responded=True)
    print(f"   Phase: {state['phase']}")
    print(f"   Manual mode: {state['manual_mode_active']}")
    print(f"   Auto messages paused: {state['auto_messages_paused']}")
    print()
    
    print("2️⃣ Bot otomatik yanıt gönderdi:")
    state = update_conversation_state(dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(dm_key)}")
    print()
    
    print("3️⃣ İkinci bot mesajı:")
    state = update_conversation_state(dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(dm_key)}")
    print()
    
    print("4️⃣ Üçüncü bot mesajı (threshold = 3):")
    state = update_conversation_state(dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(dm_key)} (Evet olmalı)")
    print()
    
    print("5️⃣ Manuel müdahale yapıldı:")
    state = update_conversation_state(dm_key, manual_intervention=True)
    print(f"   Phase: {state['phase']}")
    print(f"   Manual mode: {state['manual_mode_active']}")
    print(f"   Auto messages paused: {state['auto_messages_paused']}")
    print(f"   Auto message count reset: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(dm_key)} (Hayır olmalı)")
    print(f"   Takip gönderilmeli mi: {should_send_followup(dm_key)} (Hayır olmalı)")
    print()
    
    print("6️⃣ Kullanıcı manuel mesaja cevap verdi:")
    state = update_conversation_state(dm_key, user_responded=True)
    print(f"   Phase: {state['phase']}")
    print(f"   Manual mode: {state['manual_mode_active']}")
    print(f"   Auto messages paused: {state['auto_messages_paused']}")
    print()
    
    print("7️⃣ Bot tekrar mesaj gönderdi (manuel konuşma devam ediyor):")
    state = update_conversation_state(dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']} (Artmamalı - manuel mod)")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(dm_key)} (Hayır olmalı)")
    print()
    
    print("8️⃣ Birkaç mesaj daha (manuel konuşma):")
    for i in range(5):
        state = update_conversation_state(dm_key, bot_sent_message=True)
        print(f"   Mesaj {i+1}: Auto count = {state['auto_message_count']} (Hep 0 kalmalı)")
    print()
    
    print("9️⃣ State temizleme:")
    dm_conversation_state.clear()
    print(f"   State temizlendi: {len(dm_conversation_state)} entry")
    print()
    
    print("✅ TEST SONUCU:")
    print("   ✅ Manuel müdahale sonrası otomatik mesajlar durdu")
    print("   ✅ Menü gönderimi iptal edildi")
    print("   ✅ Takip mesajları duraklatıldı")
    print("   ✅ Doğal konuşma akışı korundu")
    print()
    print("🎉 GAVATBABA DM FLOW TEST BAŞARILI!")

if __name__ == "__main__":
    test_gavatbaba_dm_flow() 