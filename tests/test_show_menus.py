#!/usr/bin/env python3
# test_show_menus.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utilities.menu_manager import show_menu_manager

def test_show_menu_system():
    print("🧪 Show Menü Sistemi Test Ediliyor...\n")
    
    print("1️⃣ Mevcut Menüleri Listele:")
    available_menus = show_menu_manager.list_available_menus()
    for bot_name, title in available_menus.items():
        print(f"   🤖 {bot_name}: {title}")
    print()
    
    print("2️⃣ Lara'nın Tam Show Menüsü:")
    lara_full = show_menu_manager.get_show_menu("yayincilara", compact=False)
    if lara_full:
        print(f"   📏 Uzunluk: {len(lara_full)} karakter")
        print(f"   📝 İlk 100 karakter: {lara_full[:100]}...")
    else:
        print("   ❌ Menü bulunamadı")
    print()
    
    print("3️⃣ Lara'nın Kısa Show Menüsü:")
    lara_compact = show_menu_manager.get_show_menu("yayincilara", compact=True)
    if lara_compact:
        print(f"   📏 Uzunluk: {len(lara_compact)} karakter")
        print(f"   📝 İlk 100 karakter: {lara_compact[:100]}...")
    else:
        print("   ❌ Kısa menü bulunamadı")
    print()
    
    print("4️⃣ Geisha'nın Tam Show Menüsü:")
    geisha_full = show_menu_manager.get_show_menu("geishaniz", compact=False)
    if geisha_full:
        print(f"   📏 Uzunluk: {len(geisha_full)} karakter")
        print(f"   📝 İlk 100 karakter: {geisha_full[:100]}...")
    else:
        print("   ❌ Menü bulunamadı")
    print()
    
    print("5️⃣ Gavat Baba'nın Tam Show Menüsü:")
    gavat_full = show_menu_manager.get_show_menu("gavatbaba", compact=False)
    if gavat_full:
        print(f"   📏 Uzunluk: {len(gavat_full)} karakter")
        print(f"   📝 İlk 100 karakter: {gavat_full[:100]}...")
    else:
        print("   ❌ Menü bulunamadı")
    print()
    
    print("6️⃣ Rastgele Show Menüsü (Lara hariç):")
    random_menu = show_menu_manager.get_random_show_menu(exclude_bot="yayincilara", compact=True)
    if random_menu:
        print(f"   📏 Uzunluk: {len(random_menu)} karakter")
        print(f"   📝 İlk 100 karakter: {random_menu[:100]}...")
    else:
        print("   ❌ Rastgele menü bulunamadı")
    print()
    
    print("7️⃣ Bot Username Normalizasyon Testi:")
    test_usernames = [
        "@yayincilara",
        "bot_yayincilara", 
        "yayincilara",
        "YAYINCILARA",
        "@GeishaNiz",
        "bot_geishaniz",
        "geishaniz"
    ]
    
    for username in test_usernames:
        menu = show_menu_manager.get_show_menu(username, compact=True)
        status = "✅ Bulundu" if menu else "❌ Bulunamadı"
        print(f"   {username} → {status}")
    print()
    
    print("8️⃣ Menü Varyasyonları:")
    for bot in ["yayincilara", "geishaniz", "gavatbaba"]:
        variations = show_menu_manager.get_menu_variations(bot)
        print(f"   🤖 {bot}: {len(variations)} varyasyon")
        for i, var in enumerate(variations):
            print(f"      {i+1}. {len(var)} karakter")
    print()
    
    print("9️⃣ Yeni Menü Ekleme Testi:")
    test_menu = """🧪 TEST MENÜ 🧪

⚡ TEST SHOWLAR:
• 5dk Test - 100₺
• 10dk Test - 200₺

🔥 TEST EKSTRALAR:
• Test Extra - +50₺

⚠️ Bu bir test menüsüdür!"""
    
    success = show_menu_manager.update_show_menu("test_bot", test_menu, "Test Bot Menüsü")
    print(f"   Test menü ekleme: {'✅ Başarılı' if success else '❌ Başarısız'}")
    
    # Test menüsünü kontrol et
    test_retrieved = show_menu_manager.get_show_menu("test_bot", compact=False)
    if test_retrieved:
        print(f"   Test menü geri alma: ✅ Başarılı ({len(test_retrieved)} karakter)")
    else:
        print("   Test menü geri alma: ❌ Başarısız")
    print()
    
    print("🔟 Kısa Versiyon Oluşturma Testi:")
    for bot in ["yayincilara", "geishaniz", "gavatbaba"]:
        compact_created = show_menu_manager.create_compact_version("", bot)
        print(f"   🤖 {bot}: {len(compact_created)} karakter")
        print(f"      İlk satır: {compact_created.split(chr(10))[0]}")

if __name__ == "__main__":
    test_show_menu_system() 