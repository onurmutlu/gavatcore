#!/usr/bin/env python3
"""
🪙 GavatCoin Token Engine v1.1 🪙

OnlyVips v6.0 Token Economy System
Kapalı döngü token ekonomisi - XP → Token ↔ Harcama sistemi
Bot Integration ile production-ready!
"""

from .token_manager import TokenManager, get_token_manager, token_manager
from .spend_handlers import SpendHandlers, spend_token_for_service
from .bot_integration import XPBotIntegration, award_user_xp, handle_user_stats, handle_user_spend

__version__ = "1.1.0"
__author__ = "OnlyVips Team"
__description__ = "Closed-loop token economy system for OnlyVips v6.0 with bot integration"

# Export main classes and functions
__all__ = [
    "TokenManager",
    "get_token_manager", 
    "token_manager",
    "SpendHandlers",
    "spend_token_for_service",
    "XPBotIntegration",
    "award_user_xp",
    "handle_user_stats", 
    "handle_user_spend"
]

# Token system info
TOKEN_COSTS = {
    "content": 10,
    "vip": 25, 
    "boost": 5,
    "nft": 50,
    "priority_dm": 15
}

XP_TO_TOKEN_RATE = 1  # 1 XP = 1 Token

# XP reward table for bot interactions
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