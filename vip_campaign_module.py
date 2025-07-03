#!/usr/bin/env python3
"""
🎯 VIP Campaign Module v1.0
VIP grup kampanyası ve XP sistemi yönetimi
"""

import random
import time
from typing import Dict, List, Optional

class VIPCampaignModule:
    """🎯 VIP Grup Kampanyası Yöneticisi"""
    
    def __init__(self):
        self.campaign_active = True
        self.target_group = "t.me/arayisonlyvips"
        self.campaign_admin = "@babagavat"
        
        # Kampanya istatistikleri
        self.total_members_goal = 100
        self.current_members = 47  # Mevcut üye sayısı
        self.xp_per_invite = 10
        self.special_content_threshold = 3
        
        # Kampanya mesaj varyasyonları
        self.campaign_messages = [
            {
                "title": "🎯 VIP GRUP KAMPANYASI BAŞLADI!",
                "content": [
                    "🎁 İlk 100 üye XP + token kazanıyor!",
                    "👥 Her davet: 10 XP",
                    "🎖️ 3 davet yapanlara özel içerik",
                    "",
                    "XP = Token = Para",
                    f"Kazanmaya başla şimdi → {self.target_group}",
                    "",
                    f"{self.campaign_admin} üzerinden görevleri almayı unutma!"
                ]
            },
            {
                "title": "💰 PARA KAZANMA ZAMANI!",
                "content": [
                    "🚀 VIP grubuna katıl, XP kazan!",
                    "💎 Her davet = 10 XP = Token",
                    "🏆 İlk 100 kişi özel bonuslu!",
                    "",
                    "📈 XP sistemi aktif:",
                    "• Katılım: 5 XP",
                    "• Davet: 10 XP",
                    "• Aktiflik: Bonus XP",
                    "",
                    f"Başla → {self.target_group}",
                    f"Görevler → {self.campaign_admin}"
                ]
            },
            {
                "title": "🔥 VIP ÜYELIK KAMPANYASI!",
                "content": [
                    "⚡ Sınırlı süre fırsatı!",
                    "🎁 İlk katılanlar özel avantajlı",
                    "💰 XP = Token = Gerçek para",
                    "",
                    "🎯 Hedef: 100 VIP üye",
                    f"📊 Mevcut: {self.current_members}/100",
                    "",
                    f"Katıl → {self.target_group}",
                    f"Detaylar → {self.campaign_admin}"
                ]
            }
        ]
        
        # Bot-specific kampanya mesajları
        self.bot_specific_campaigns = {
            "yayincilara": {
                "title": "💕 Lara'nın VIP Kampanyası!",
                "personal_touch": [
                    "Canım, özel bir kampanya var! 💕",
                    "Birlikte para kazanalım! 😊",
                    "VIP grubuma katıl, XP kazan! 🌸"
                ]
            },
            "babagavat": {
                "title": "😎 Gavat Baba'nın Para Kampanyası!",
                "personal_touch": [
                    "Kardeşim, büyük fırsat! 😎",
                    "Para kazanma zamanı aslanım! 🔥",
                    "VIP olmaya hazır mısın? 💪"
                ]
            },
            "xxxgeisha": {
                "title": "😘 Geisha'nın Özel Kampanyası!",
                "personal_touch": [
                    "Aşkım, sana özel fırsat! 😘",
                    "Birlikte zengin olalım canım! 💋",
                    "VIP grubuma katıl bebek! 🌹"
                ]
            }
        }
    
    def get_campaign_message(self, bot_username: str = None) -> str:
        """Kampanya mesajı oluştur"""
        if not self.campaign_active:
            return self.get_fallback_message(bot_username)
        
        # Bot-specific campaign
        if bot_username and bot_username in self.bot_specific_campaigns:
            return self.get_personalized_campaign(bot_username)
        
        # Genel kampanya mesajı
        campaign = random.choice(self.campaign_messages)
        message_parts = [campaign["title"]] + [""] + campaign["content"]
        return "\n".join(message_parts)
    
    def get_personalized_campaign(self, bot_username: str) -> str:
        """Bot'a özel kişiselleştirilmiş kampanya"""
        bot_campaign = self.bot_specific_campaigns[bot_username]
        personal_intro = random.choice(bot_campaign["personal_touch"])
        
        # Ana kampanya bilgileri
        campaign_info = [
            "",
            "🎯 VIP GRUP KAMPANYASI BAŞLADI!",
            "",
            "🎁 İlk 100 üye XP + token kazanıyor!",
            "👥 Her davet: 10 XP",
            "🎖️ 3 davet yapanlara özel içerik",
            "",
            "XP = Token = Para",
            f"Kazanmaya başla şimdi → {self.target_group}",
            "",
            f"{self.campaign_admin} üzerinden görevleri almayı unutma!"
        ]
        
        return personal_intro + "\n".join(campaign_info)
    
    def get_short_campaign_message(self, bot_username: str = None) -> str:
        """Kısa kampanya mesajı (grup için)"""
        short_messages = [
            f"💰 VIP kampanyası aktif! {self.target_group}",
            f"🎁 XP kazan, para kazan! {self.target_group}",
            f"🚀 100 üye hedefi! Katıl → {self.target_group}",
            f"⚡ Sınırlı fırsat! {self.target_group}"
        ]
        return random.choice(short_messages)
    
    def get_fallback_message(self, bot_username: str = None) -> str:
        """Kampanya kapalıyken fallback mesajı"""
        fallback_messages = {
            "yayincilara": [
                "Merhabalar! Nasılsın? 😊",
                "Selam canım! Ne haber? 💕",
                "Hey! Bugün nasıl geçiyor? 🌸"
            ],
            "babagavat": [
                "Selam kardeşim! 😎",
                "Ne haber aslanım? 🔥",
                "Hey! Nasıl gidiyor? 💪"
            ],
            "xxxgeisha": [
                "Merhaba aşkım 😘",
                "Selam bebek, nasılsın? 💕",
                "Hey canım, ne yapıyorsun? 🌹"
            ]
        }
        
        if bot_username and bot_username in fallback_messages:
            return random.choice(fallback_messages[bot_username])
        
        return "Selam! 👋"
    
    def get_campaign_stats(self) -> Dict:
        """Kampanya istatistikleri"""
        progress_percentage = (self.current_members / self.total_members_goal) * 100
        remaining_spots = self.total_members_goal - self.current_members
        
        return {
            "active": self.campaign_active,
            "current_members": self.current_members,
            "target_members": self.total_members_goal,
            "progress_percentage": round(progress_percentage, 1),
            "remaining_spots": remaining_spots,
            "xp_per_invite": self.xp_per_invite,
            "target_group": self.target_group,
            "campaign_admin": self.campaign_admin
        }
    
    def update_member_count(self, new_count: int):
        """Üye sayısını güncelle"""
        self.current_members = new_count
        
        # Hedefe ulaşıldıysa kampanyayı bitir
        if self.current_members >= self.total_members_goal:
            self.campaign_active = False
    
    def toggle_campaign(self, active: bool = None):
        """Kampanyayı başlat/durdur"""
        if active is not None:
            self.campaign_active = active
        else:
            self.campaign_active = not self.campaign_active
        
        return self.campaign_active
    
    def get_engaging_campaign_message(self, bot_username: str = None) -> str:
        """Grup'lar için engaging kampanya mesajları"""
        engaging_messages = [
            f"🔥 VIP kampanyası devam ediyor! {self.target_group}",
            f"💰 {self.total_members_goal - self.current_members} kişi kaldı! Katıl şimdi!",
            f"⚡ Son fırsat! XP kazanmaya başla → {self.target_group}",
            f"🎁 İlk katılanlar şanslı! {self.target_group}"
        ]
        return random.choice(engaging_messages)

# Global kampanya instance
vip_campaign = VIPCampaignModule()

def get_campaign_message(bot_username: str = None) -> str:
    """Kampanya mesajı al - kolay erişim fonksiyonu"""
    return vip_campaign.get_campaign_message(bot_username)

def get_short_campaign_message(bot_username: str = None) -> str:
    """Kısa kampanya mesajı al"""
    return vip_campaign.get_short_campaign_message(bot_username)

def get_campaign_stats() -> Dict:
    """Kampanya istatistiklerini al"""
    return vip_campaign.get_campaign_stats()

if __name__ == "__main__":
    # Test kampanya modülü
    print("🧪 VIP Campaign Module Test")
    print("=" * 50)
    
    for bot in ["yayincilara", "babagavat", "xxxgeisha"]:
        print(f"\n🤖 {bot.upper()} CAMPAIGN MESSAGE:")
        print("-" * 30)
        print(get_campaign_message(bot))
        print()
    
    print("📊 CAMPAIGN STATS:")
    stats = get_campaign_stats()
    for key, value in stats.items():
        print(f"• {key}: {value}") 