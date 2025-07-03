#!/usr/bin/env python3
# test_show_system.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utilities.menu_manager import show_menu_manager

def test_show_menus():
    """Show menü sistemini test et"""
    
    print("🧪 SHOW MENÜ SİSTEMİ TESTİ")
    print("=" * 50)
    
    # Test 1: Geisha menü
    print("\n1️⃣ GEİSHA MENÜ TESTİ:")
    geisha_menu = show_menu_manager.get_show_menu('geishaniz', compact=True)
    if geisha_menu:
        print("✅ Geisha menü bulundu")
        print(f"📏 Uzunluk: {len(geisha_menu)} karakter")
        print(f"📝 Önizleme: {geisha_menu[:100]}...")
    else:
        print("❌ Geisha menü bulunamadı")
    
    # Test 2: Lara menü
    print("\n2️⃣ LARA MENÜ TESTİ:")
    lara_menu = show_menu_manager.get_show_menu('yayincilara', compact=True)
    if lara_menu:
        print("✅ Lara menü bulundu")
        print(f"📏 Uzunluk: {len(lara_menu)} karakter")
        print(f"📝 Önizleme: {lara_menu[:100]}...")
    else:
        print("❌ Lara menü bulunamadı")
    
    # Test 3: Username testleri
    print("\n3️⃣ USERNAME TESTLERİ:")
    test_usernames = [
        '@geishaniz',
        'bot_geishaniz', 
        'geishaniz',
        'GEİSHANİZ',
        '@yayincilara',
        'bot_yayincilara',
        'yayincilara',
        'YAYINCILARA'
    ]
    
    for username in test_usernames:
        menu = show_menu_manager.get_show_menu(username, compact=True)
        status = "✅" if menu else "❌"
        print(f"   {username} {status}")
    
    # Test 4: Menü listesi
    print("\n4️⃣ MENÜ LİSTESİ:")
    menus = show_menu_manager.list_available_menus()
    for bot, title in menus.items():
        print(f"   🤖 {bot}: {title}")
    
    print("\n✅ Test tamamlandı!")

if __name__ == "__main__":
    test_show_menus() 