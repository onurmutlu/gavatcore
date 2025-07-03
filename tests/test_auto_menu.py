#!/usr/bin/env python3
# test_auto_menu.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.dm_handler import (
    update_conversation_state, 
    should_send_auto_menu,
    dm_conversation_state,
    handle_message,
    handle_inline_bank_choice
)

def test_auto_menu_system():
    print("🧪 Otomatik Menü Gönderme Sistemi Test Ediliyor...\n")
    
    # Test DM key'i
    test_dm_key = "dm:geishaniz:12345"
    
    print("1️⃣ İlk kullanıcı mesajı:")
    state = update_conversation_state(test_dm_key, user_responded=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menu sent: {state['menu_sent']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key)}")
    print()
    
    # Test bot profili
    test_bot_profile = {"auto_menu_enabled": True, "auto_menu_threshold": 3}
    
    print("2️⃣ 1. bot mesajı:")
    state = update_conversation_state(test_dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)}")
    print()
    
    print("3️⃣ Kullanıcı cevap verdi:")
    state = update_conversation_state(test_dm_key, user_responded=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)}")
    print()
    
    print("4️⃣ 2. bot mesajı:")
    state = update_conversation_state(test_dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)}")
    print()
    
    print("5️⃣ Kullanıcı cevap verdi:")
    state = update_conversation_state(test_dm_key, user_responded=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)}")
    print()
    
    print("6️⃣ 3. bot mesajı (threshold = 3):")
    state = update_conversation_state(test_dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)} (EVET olmalı!)")
    print()
    
    print("7️⃣ Menü gönderildi:")
    state = update_conversation_state(test_dm_key, menu_sent=True)
    print(f"   Menu sent: {state['menu_sent']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)} (Hayır olmalı - zaten gönderildi)")
    print()
    
    print("8️⃣ 4. bot mesajı (menü sonrası):")
    state = update_conversation_state(test_dm_key, bot_sent_message=True)
    print(f"   Auto message count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(test_dm_key, test_bot_profile)} (Hayır olmalı - zaten gönderildi)")
    print()
    
    print("9️⃣ Manuel müdahale testi:")
    # Yeni DM key ile test
    manual_dm_key = "dm:geishaniz:67890"
    
    # 3 otomatik mesaj gönder
    update_conversation_state(manual_dm_key, user_responded=True)
    update_conversation_state(manual_dm_key, bot_sent_message=True)
    update_conversation_state(manual_dm_key, user_responded=True)
    update_conversation_state(manual_dm_key, bot_sent_message=True)
    update_conversation_state(manual_dm_key, user_responded=True)
    state = update_conversation_state(manual_dm_key, bot_sent_message=True)
    
    print(f"   Manuel müdahale öncesi - Auto count: {state['auto_message_count']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(manual_dm_key)} (Evet olmalı)")
    
    # Manuel müdahale
    state = update_conversation_state(manual_dm_key, manual_intervention=True)
    print(f"   Manuel müdahale sonrası - Auto count: {state['auto_message_count']}")
    print(f"   Phase: {state['phase']}")
    print(f"   Menü gönderilmeli mi: {should_send_auto_menu(manual_dm_key)} (Hayır olmalı - manuel müdahale)")
    print()
    
    print("🔟 State temizleme:")
    dm_conversation_state.clear()
    print(f"   State temizlendi: {len(dm_conversation_state)} entry")

if __name__ == "__main__":
    test_auto_menu_system() 