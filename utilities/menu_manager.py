#!/usr/bin/env python3
# utils/menu_manager.py

import json
import random
from pathlib import Path
from typing import Optional, Dict, List
from utilities.log_utils import log_event

class ShowMenuManager:
    def __init__(self):
        self.menu_file = Path("data/show_menus.json")
        self.menus = self._load_menus()
    
    def _load_menus(self) -> Dict:
        """Show menülerini dosyadan yükler."""
        try:
            if self.menu_file.exists():
                with open(self.menu_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_event("menu_manager", f"❌ Menü dosyası yükleme hatası: {e}")
            return {}
    
    def get_show_menu(self, bot_username: str, compact: bool = False) -> Optional[str]:
        """
        Bot'a özel show menüsünü getirir.
        
        Args:
            bot_username: Bot kullanıcı adı (geishaniz, yayincilara, gavatbaba)
            compact: Kısa versiyon mu isteniyor
        
        Returns:
            Menü metni veya None
        """
        # Bot username'ini normalize et
        bot_key = bot_username.lower().replace("@", "").replace("bot_", "")
        
        # Username mapping
        username_mapping = {
            "yayincilara": "lara",
            "geishaniz": "geisha", 
            "gavatbaba": "gavat"
        }
        
        # Mapping'i kontrol et
        if bot_key in username_mapping:
            bot_key = username_mapping[bot_key]
        
        if compact:
            # Kısa versiyonları kontrol et
            compact_key = f"{bot_key}_compact"
            if "compact_versions" in self.menus:
                return self.menus["compact_versions"].get(compact_key)
        else:
            # Tam versiyonları kontrol et
            menu_key = f"{bot_key}_show_menu"
            if menu_key in self.menus:
                return self.menus[menu_key].get("content")
        
        return None
    
    def get_random_show_menu(self, exclude_bot: str = None, compact: bool = False) -> Optional[str]:
        """
        Rastgele bir show menüsü getirir.
        
        Args:
            exclude_bot: Hariç tutulacak bot
            compact: Kısa versiyon mu
        
        Returns:
            Rastgele menü metni
        """
        available_bots = ["lara", "geisha", "gavat"]
        
        if exclude_bot:
            exclude_bot = exclude_bot.lower().replace("@", "").replace("bot_", "")
            # Username mapping
            username_mapping = {
                "yayincilara": "lara",
                "geishaniz": "geisha", 
                "gavatbaba": "gavat"
            }
            if exclude_bot in username_mapping:
                exclude_bot = username_mapping[exclude_bot]
            available_bots = [bot for bot in available_bots if bot != exclude_bot]
        
        if not available_bots:
            return None
        
        selected_bot = random.choice(available_bots)
        return self.get_show_menu(selected_bot, compact)
    
    def update_show_menu(self, bot_username: str, menu_content: str, title: str = None) -> bool:
        """
        Bot'un show menüsünü günceller.
        
        Args:
            bot_username: Bot kullanıcı adı
            menu_content: Yeni menü içeriği
            title: Menü başlığı (opsiyonel)
        
        Returns:
            Başarılı mı
        """
        try:
            bot_key = bot_username.lower().replace("@", "").replace("bot_", "")
            
            # Username mapping
            username_mapping = {
                "yayincilara": "lara",
                "geishaniz": "geisha", 
                "gavatbaba": "gavat"
            }
            if bot_key in username_mapping:
                bot_key = username_mapping[bot_key]
            
            menu_key = f"{bot_key}_show_menu"
            
            if menu_key not in self.menus:
                self.menus[menu_key] = {}
            
            self.menus[menu_key]["content"] = menu_content
            if title:
                self.menus[menu_key]["title"] = title
            
            # Dosyaya kaydet
            with open(self.menu_file, "w", encoding="utf-8") as f:
                json.dump(self.menus, f, ensure_ascii=False, indent=2)
            
            log_event("menu_manager", f"✅ {bot_username} show menüsü güncellendi")
            return True
            
        except Exception as e:
            log_event("menu_manager", f"❌ Menü güncelleme hatası: {e}")
            return False
    
    def create_compact_version(self, full_menu: str, bot_username: str) -> str:
        """
        Tam menüden kısa versiyon oluşturur.
        
        Args:
            full_menu: Tam menü metni
            bot_username: Bot kullanıcı adı
        
        Returns:
            Kısa menü metni
        """
        bot_key = bot_username.lower().replace("@", "").replace("bot_", "")
        
        # Basit kısa versiyon şablonu
        if "lara" in bot_key or "yayinci" in bot_key:
            return f"""✨ @YayinciLara SHOW MENÜ ✨

⚡ SHOWLAR:
• 10dk - 500₺ | 15dk - 750₺ | 20dk - 1000₺

🔥 EKSTRALAR:
• Boşalma +350₺ | Anal +400₺ | Oyuncak +400₺

📹 VİDEO:
• Özel 10dk - 700₺ | Hazır 5dk - 400₺

💌 SEXTİNG: 15dk - 600₺
👑 VIP KANAL: 850₺

⚠️ Önce ödeme, sonra show!
✨ Fantazinin adını Lara koydular..."""

        elif "geisha" in bot_key:
            return f"""🔥 @GeishaNiz ÖZEL MENÜ 🔥

💋 SHOWLAR:
• 12dk - 600₺ | 18dk - 900₺ | 25dk - 1200₺

🌶️ EKSTRALAR:
• Orgazm +400₺ | Anal +450₺ | Ayak +350₺

📹 VİDEO:
• Özel 12dk - 800₺ | Koleksiyon - 500₺

💬 SEXTİNG: 20dk - 700₺
👑 PREMIUM: Aylık 1000₺

⚠️ Pazarlık yok, kalite var!
🔥 Tutkun, benim gücüm..."""

        elif "gavat" in bot_key:
            return f"""👑 GAVAT BABA PAVYONU 👑

🎭 KIZ BAĞLANTI:
• Tanıştırma - 300₺ | Premium - 500₺ | VIP - 800₺

📱 ARŞİV:
• Video Paketi - 400₺ | Foto Koleksiyon - 250₺

🏆 VIP GRUP:
• Aylık VIP - 800₺ | Premium Kanal - 1200₺

🎁 PAKETLER:
• Başlangıç - 650₺ | Komple - 1500₺

⚠️ Saygı şart, ödeme peşin!
👑 Pavyonun kralı hizmetinde..."""
        
        # Fallback
        return "📋 Hizmet menüsü yükleniyor..."
    
    def get_menu_variations(self, bot_username: str) -> List[str]:
        """
        Bot için farklı menü varyasyonları getirir.
        
        Returns:
            Menü varyasyonları listesi
        """
        variations = []
        
        # Tam versiyon
        full_menu = self.get_show_menu(bot_username, compact=False)
        if full_menu:
            variations.append(full_menu)
        
        # Kısa versiyon
        compact_menu = self.get_show_menu(bot_username, compact=True)
        if compact_menu:
            variations.append(compact_menu)
        
        return variations
    
    def list_available_menus(self) -> Dict[str, str]:
        """
        Mevcut tüm menüleri listeler.
        
        Returns:
            Bot adı -> menü başlığı mapping'i
        """
        available = {}
        
        for key, menu_data in self.menus.items():
            if key.endswith("_show_menu") and isinstance(menu_data, dict):
                bot_name = key.replace("_show_menu", "")
                title = menu_data.get("title", f"{bot_name} Show Menüsü")
                available[bot_name] = title
        
        return available

# Global instance
show_menu_manager = ShowMenuManager() 