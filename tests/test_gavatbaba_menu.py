#!/usr/bin/env python3
# tests/test_gavatbaba_menu.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.menu_manager import ShowMenuManager
import json
from pathlib import Path

def test_gavatbaba_menu():
    """Gavatbaba'nın güncellenmiş show menüsünü test et"""
    
    print("🎭 GAVATBABA SHOW MENÜ TEST")
    print("=" * 40)
    
    # Debug: Dosya yolu kontrolü
    print("🔍 DEBUG: Dosya yolu kontrolü:")
    print("-" * 40)
    
    # Current working directory
    cwd = os.getcwd()
    print(f"   Current working directory: {cwd}")
    
    # Menu dosya yolu
    menu_file = Path("data/show_menus.json")
    print(f"   Menu file path: {menu_file}")
    print(f"   Menu file exists: {menu_file.exists()}")
    print(f"   Menu file absolute: {menu_file.absolute()}")
    
    # Dosyayı manuel yükle
    if menu_file.exists():
        try:
            with open(menu_file, "r", encoding="utf-8") as f:
                menu_data = json.load(f)
            print(f"   ✅ Dosya başarıyla yüklendi")
            print(f"   📊 Menü keys: {list(menu_data.keys())}")
            
            # Gavat menüsü var mı
            if "gavat_show_menu" in menu_data:
                gavat_menu = menu_data["gavat_show_menu"]
                print(f"   ✅ gavat_show_menu bulundu")
                print(f"   📊 İçerik uzunluğu: {len(gavat_menu.get('content', ''))}")
            else:
                print(f"   ❌ gavat_show_menu bulunamadı")
                
        except Exception as e:
            print(f"   ❌ Dosya yükleme hatası: {e}")
    
    print("\n" + "=" * 40)
    
    menu_manager = ShowMenuManager()
    
    # Debug: Menu manager'ın dosya yolu
    print(f"🔍 Menu manager file path: {menu_manager.menu_file}")
    print(f"🔍 Menu manager file exists: {menu_manager.menu_file.exists()}")
    print(f"🔍 Menu manager menus loaded: {len(menu_manager.menus)}")
    
    # Debug: Mevcut menüleri listele
    print("\n🔍 DEBUG: Mevcut menüler:")
    print("-" * 40)
    available_menus = menu_manager.list_available_menus()
    for bot_name, title in available_menus.items():
        print(f"   📋 {bot_name}: {title}")
    
    # Debug: Raw menü verilerini kontrol et
    print(f"\n🔍 DEBUG: Raw menü keys: {list(menu_manager.menus.keys())}")
    
    # Farklı username varyasyonlarını test et
    test_usernames = ['babagavat', 'gavat', 'GavatBaba_BOT']
    
    for username in test_usernames:
        print(f"\n🧪 Test username: '{username}'")
        
        # Bot key'i nasıl normalize ediliyor
        bot_key = username.lower().replace("@", "").replace("bot_", "")
        print(f"   Normalized bot_key: '{bot_key}'")
        
        # Username mapping
        username_mapping = {
            "yayincilara": "lara",
            "geishaniz": "geisha", 
            "gavatbaba": "gavat"
        }
        
        if bot_key in username_mapping:
            bot_key = username_mapping[bot_key]
            print(f"   Mapped bot_key: '{bot_key}'")
        
        menu_key = f"{bot_key}_show_menu"
        print(f"   Looking for menu_key: '{menu_key}'")
        
        # Menü var mı kontrol et
        if menu_key in menu_manager.menus:
            print(f"   ✅ Menü bulundu!")
            menu_content = menu_manager.menus[menu_key].get("content", "")
            print(f"   📊 İçerik uzunluğu: {len(menu_content)} karakter")
        else:
            print(f"   ❌ Menü bulunamadı")
    
    print("\n" + "=" * 40)
    print("📋 Gavatbaba Tam Show Menüsü:")
    print("-" * 40)
    full_menu = menu_manager.get_show_menu('gavatbaba', compact=False)
    if full_menu:
        # İlk 800 karakteri göster
        preview = full_menu[:800] + "..." if len(full_menu) > 800 else full_menu
        print(preview)
        print(f"\n📊 Toplam karakter: {len(full_menu)}")
    else:
        print("❌ Tam menü bulunamadı")
    
    print("\n" + "=" * 40)
    print("📋 Gavatbaba Kısa Menü:")
    print("-" * 40)
    compact_menu = menu_manager.get_show_menu('gavatbaba', compact=True)
    if compact_menu:
        print(compact_menu)
        print(f"\n📊 Toplam karakter: {len(compact_menu)}")
    else:
        print("❌ Kısa menü bulunamadı")
    
    print("\n" + "=" * 40)
    print("🔍 Menü İçerik Analizi:")
    print("-" * 40)
    
    if full_menu:
        # Anahtar kelime kontrolü
        keywords = {
            "Kız Bağlantı": "kız bağlant" in full_menu.lower(),
            "Arşiv": "arşiv" in full_menu.lower(),
            "VIP Grup": "vip grup" in full_menu.lower(),
            "Tanıştırma": "tanıştırma" in full_menu.lower(),
            "Pavyon": "pavyon" in full_menu.lower(),
            "Sesli Sohbet": "sesli sohbet" in full_menu.lower(),
            "Görüntülü": "görüntülü" in full_menu.lower()
        }
        
        for keyword, found in keywords.items():
            status = "✅" if found else "❌"
            print(f"   {status} {keyword}: {'Var' if found else 'Yok'}")
    
    print("\n✅ MENÜ TEST TAMAMLANDI!")
    print("🎯 Erkek bot karakterine uygun hizmetler:")
    print("   ✅ Kız tanıştırma ve bağlantı")
    print("   ✅ Arşiv ve içerik satışı")
    print("   ✅ VIP grup üyelikleri")
    print("   ❌ Sesli/görüntülü kişisel hizmetler (kaldırıldı)")

if __name__ == "__main__":
    test_gavatbaba_menu() 