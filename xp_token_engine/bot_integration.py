from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🎮 GavatCoin Bot Integration v1.0 🎮

Production bot'lar için XP/Token entegrasyon sistemi
Her kullanıcı etkileşiminde XP kazanır, otomatik token'a dönüşür
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .token_manager import get_token_manager
from .spend_handlers import SpendHandlers, spend_token_for_service

logger = logging.getLogger(__name__)

class XPBotIntegration:
    """Bot etkileşimleri için XP/Token sistemi"""
    
    # XP reward table
    XP_REWARDS = {
        "start_command": 10,          # /start komutu
        "first_dm": 15,              # İlk DM
        "dm_reply": 5,               # DM yanıtı
        "group_mention": 8,          # Grupta mention
        "group_reply": 6,            # Grupta reply  
        "daily_bonus": 20,           # Günlük bonus
        "invite_friend": 25,         # Arkadaş davet
        "premium_interaction": 30,   # Premium etkileşim
        "vip_activity": 50,          # VIP aktivite
    }
    
    def __init__(self):
        self.daily_rewards = {}      # user_id -> last_daily_time
        self.user_stats = {}         # user_id -> stats dict
        self.interaction_cooldowns = {}  # user_id -> {action: last_time}
    
    async def award_xp(self, user_id: int, action: str, bonus_multiplier: float = 1.0) -> Tuple[bool, int, str]:
        """
        Kullanıcıya XP ver ve otomatik token'a çevir
        
        Args:
            user_id: Telegram user ID
            action: XP kazanma nedeni
            bonus_multiplier: Bonus çarpanı (VIP için 2x vs)
        
        Returns:
            (success, tokens_earned, message)
        """
        try:
            # XP miktarını hesapla
            base_xp = self.XP_REWARDS.get(action, 5)
            xp_amount = int(base_xp * bonus_multiplier)
            
            # Cooldown kontrolü
            if not self._check_cooldown(user_id, action):
                return False, 0, "Çok sık XP kazanamaz! Biraz bekle 😊"
            
            # Token manager ile XP'yi token'a çevir
            async with get_token_manager() as tm:
                new_balance = await tm.xp_to_token(str(user_id), xp_amount)
                
                # Kullanıcı istatistiklerini güncelle
                await self._update_user_stats(user_id, action, xp_amount)
                
                # Success message
                action_emoji = self._get_action_emoji(action)
                message = f"{action_emoji} +{xp_amount} XP → {xp_amount} Token kazandın! 💰\n"
                message += f"💳 Toplam bakiye: {new_balance} token"
                
                if bonus_multiplier > 1.0:
                    message += f"\n🎉 {bonus_multiplier}x bonus aktif!"
                
                logger.info(f"🎮 XP awarded: {user_id} -> {action} -> {xp_amount} XP/tokens")
                return True, xp_amount, message
                
        except Exception as e:
            logger.error(f"❌ XP award error for {user_id}: {e}")
            return False, 0, "XP verme hatası! 😞"
    
    async def check_daily_bonus(self, user_id: int) -> Tuple[bool, str]:
        """Günlük bonus kontrolü ve verme"""
        try:
            current_time = time.time()
            last_daily = self.daily_rewards.get(user_id, 0)
            
            # 24 saat geçmiş mi?
            if current_time - last_daily < 86400:  # 24 hours
                hours_left = int((86400 - (current_time - last_daily)) / 3600)
                return False, f"⏰ Günlük bonus {hours_left} saat sonra!"
            
            # Günlük bonus ver
            success, tokens, message = await self.award_xp(
                user_id, 
                "daily_bonus", 
                bonus_multiplier=1.0
            )
            
            if success:
                self.daily_rewards[user_id] = current_time
                return True, f"🎁 Günlük bonus! {message}"
            else:
                return False, "Günlük bonus verme hatası!"
                
        except Exception as e:
            logger.error(f"❌ Daily bonus error for {user_id}: {e}")
            return False, "Günlük bonus hatası!"
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı istatistiklerini getir"""
        try:
            async with get_token_manager() as tm:
                # Token balance
                balance = await tm.get_balance(str(user_id))
                
                # Transaction history (son 3)
                logs = await tm.get_logs(str(user_id), limit=3)
                
                # User stats
                user_stats = self.user_stats.get(user_id, {
                    "total_xp_earned": 0,
                    "actions_count": {},
                    "join_date": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat()
                })
                
                # Daily bonus status
                daily_available, daily_msg = await self.check_daily_bonus(user_id)
                
                return {
                    "user_id": user_id,
                    "token_balance": balance,
                    "total_xp_earned": user_stats["total_xp_earned"],
                    "daily_bonus_available": daily_available,
                    "daily_bonus_message": daily_msg,
                    "recent_transactions": logs,
                    "actions_count": user_stats["actions_count"],
                    "join_date": user_stats["join_date"],
                    "last_activity": user_stats["last_activity"]
                }
                
        except Exception as e:
            logger.error(f"❌ Get user stats error for {user_id}: {e}")
            return {}
    
    async def handle_stats_command(self, user_id: int) -> str:
        """
        /stats komutu için formatted response
        """
        try:
            stats = await self.get_user_stats(user_id)
            
            if not stats:
                return "❌ İstatistikler alınamadı!"
            
            # Format response
            response = "📊 **Senin İstatistiklerin** 📊\n\n"
            response += f"💰 **Token Bakiye:** {stats['token_balance']} token\n"
            response += f"🎮 **Toplam XP:** {stats['total_xp_earned']} XP\n\n"
            
            # Daily bonus
            if stats['daily_bonus_available']:
                response += f"🎁 {stats['daily_bonus_message']}\n\n"
            else:
                response += f"⏰ {stats['daily_bonus_message']}\n\n"
            
            # Recent transactions
            if stats['recent_transactions']:
                response += "📜 **Son İşlemler:**\n"
                for tx in stats['recent_transactions']:
                    emoji = "💰" if tx['amount'] > 0 else "💸"
                    response += f"{emoji} {tx['amount']} - {tx['reason']}\n"
                response += "\n"
            
            # Actions count
            if stats['actions_count']:
                response += "🏆 **Aktiviteler:**\n"
                for action, count in stats['actions_count'].items():
                    emoji = self._get_action_emoji(action)
                    response += f"{emoji} {action}: {count}x\n"
            
            # Spending options teaser
            response += "\n🛒 **Token Harcama:**\n"
            response += "• 🎬 Premium içerik (10 token)\n"
            response += "• 👑 VIP statü (25 token)\n"
            response += "• ⚡ Görev boost (5 token)\n"
            response += "\n💡 Harcama için beni DM'den yaz!"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Stats command error for {user_id}: {e}")
            return "❌ İstatistik hatası!"
    
    async def handle_spend_command(self, user_id: int, service: str, content_id: Optional[str] = None) -> str:
        """Token harcama komutu"""
        try:
            # Check if user can afford
            can_afford, balance, cost = await SpendHandlers.can_afford(str(user_id), service)
            
            if not can_afford:
                return f"❌ Yetersiz bakiye! {service} için {cost} token gerekli, sen {balance} token'a sahipsin."
            
            # Execute purchase
            kwargs = {"content_id": content_id} if content_id else {}
            success, message = await spend_token_for_service(
                str(user_id), 
                service, 
                **kwargs
            )
            
            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
                
        except Exception as e:
            logger.error(f"❌ Spend command error for {user_id}: {e}")
            return "❌ Token harcama hatası!"
    
    def _check_cooldown(self, user_id: int, action: str) -> bool:
        """Action cooldown kontrolü"""
        current_time = time.time()
        
        if user_id not in self.interaction_cooldowns:
            self.interaction_cooldowns[user_id] = {}
        
        user_cooldowns = self.interaction_cooldowns[user_id]
        last_time = user_cooldowns.get(action, 0)
        
        # Cooldown sürelerine göre kontrol
        cooldown_durations = {
            "start_command": 3600,      # 1 hour
            "first_dm": 0,              # No cooldown
            "dm_reply": 300,            # 5 minutes
            "group_mention": 600,       # 10 minutes
            "group_reply": 300,         # 5 minutes
            "daily_bonus": 86400,       # 24 hours
            "invite_friend": 1800,      # 30 minutes
            "premium_interaction": 600, # 10 minutes
        }
        
        cooldown = cooldown_durations.get(action, 300)  # Default 5 min
        
        if current_time - last_time >= cooldown:
            user_cooldowns[action] = current_time
            return True
        
        return False
    
    async def _update_user_stats(self, user_id: int, action: str, xp_amount: int):
        """Kullanıcı istatistiklerini güncelle"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                "total_xp_earned": 0,
                "actions_count": {},
                "join_date": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            }
        
        stats = self.user_stats[user_id]
        stats["total_xp_earned"] += xp_amount
        stats["last_activity"] = datetime.now().isoformat()
        
        if action not in stats["actions_count"]:
            stats["actions_count"][action] = 0
        stats["actions_count"][action] += 1
    
    def _get_action_emoji(self, action: str) -> str:
        """Action için emoji döndür"""
        emoji_map = {
            "start_command": "🚀",
            "first_dm": "💌",
            "dm_reply": "💬",
            "group_mention": "📢",
            "group_reply": "💭",
            "daily_bonus": "🎁",
            "invite_friend": "👥",
            "premium_interaction": "⭐",
            "vip_activity": "👑"
        }
        return emoji_map.get(action, "🎮")

# Global instance for easy import
xp_integration = XPBotIntegration()

async def award_user_xp(user_id: int, action: str, bonus_multiplier: float = 1.0) -> Tuple[bool, int, str]:
    """
    Easy-to-use function for awarding XP in bot handlers
    """
    return await xp_integration.award_xp(user_id, action, bonus_multiplier)

async def handle_user_stats(user_id: int) -> str:
    """
    Easy-to-use function for /stats command
    """
    return await xp_integration.handle_stats_command(user_id)

async def handle_user_spend(user_id: int, service: str, content_id: Optional[str] = None) -> str:
    """
    Easy-to-use function for token spending
    """
    return await xp_integration.handle_spend_command(user_id, service, content_id) 