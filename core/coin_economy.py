#!/usr/bin/env python3
"""
💰 GAVATCore 2.0 - Coin Economy System
=====================================

Token bazlı mesajlaşma ekonomisi. Zehra'nın yanıt sıklığı ve kalitesi
kullanıcının token harcamasına göre değişir.

Features:
- Token bazlı yanıt sistemi
- Dinamik fiyatlandırma
- Mood-based cost modifiers  
- VIP discount sistemi
- Cooldown management
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.core.coin_economy")

class TokenTier(Enum):
    """Token seviye kategorileri"""
    FREELOADER = "freeloader"    # 0 token
    BASIC = "basic"              # 1-50 token
    REGULAR = "regular"          # 51-200 token
    PREMIUM = "premium"          # 201-500 token
    VIP = "vip"                  # 501+ token

@dataclass
class TokenTransaction:
    """Token işlem kaydı"""
    user_id: str
    amount: int
    transaction_type: str  # purchase, spend, bonus, penalty
    timestamp: datetime
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EconomyConfig:
    """Ekonomi konfigürasyonu"""
    base_message_cost: int = 5
    premium_message_cost: int = 20
    voice_message_cost: int = 50
    video_call_cost_per_minute: int = 100
    
    # Mood modifier'ları
    mood_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "happy": 0.8,      # %20 indirim
        "neutral": 1.0,    # Normal fiyat
        "testing": 1.2,    # %20 zamm
        "angry": 1.5,      # %50 zamm
        "cold": 2.0        # %100 zamm
    })
    
    # VIP indirimleri
    vip_discounts: Dict[str, float] = field(default_factory=lambda: {
        TokenTier.FREELOADER.value: 1.0,
        TokenTier.BASIC.value: 0.95,
        TokenTier.REGULAR.value: 0.9,
        TokenTier.PREMIUM.value: 0.8,
        TokenTier.VIP.value: 0.7
    })
    
    # Response delay'leri (saniye)
    response_delays: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        TokenTier.VIP.value: (1, 3),
        TokenTier.PREMIUM.value: (2, 8),
        TokenTier.REGULAR.value: (5, 15),
        TokenTier.BASIC.value: (10, 60),
        TokenTier.FREELOADER.value: (60, 300)
    })

class CoinEconomy:
    """
    💰 Token Ekonomi Sistemi
    
    Zehra'nın token bazlı yanıt sistemi. Kullanıcıların token harcamasına göre
    yanıt kalitesi, hızı ve sıklığı değişir.
    """
    
    def __init__(self, config: Optional[EconomyConfig] = None):
        self.config = config or EconomyConfig()
        self.user_balances: Dict[str, int] = {}
        self.transaction_history: Dict[str, List[TokenTransaction]] = {}
        self.user_tiers: Dict[str, TokenTier] = {}
        self.active_cooldowns: Dict[str, datetime] = {}
        
        # İstatistikler
        self.daily_stats = {
            "total_spent": 0,
            "total_earned": 0,
            "active_users": set(),
            "transactions": 0
        }
        
        logger.info("💰 Coin Economy System initialized")
    
    async def get_user_balance(self, user_id: str) -> int:
        """Kullanıcının token bakiyesini al"""
        return self.user_balances.get(user_id, 0)
    
    async def get_user_tier(self, user_id: str) -> TokenTier:
        """Kullanıcının tier seviyesini al"""
        if user_id in self.user_tiers:
            return self.user_tiers[user_id]
        
        balance = await self.get_user_balance(user_id)
        tier = self._calculate_tier(balance)
        self.user_tiers[user_id] = tier
        return tier
    
    def _calculate_tier(self, balance: int) -> TokenTier:
        """Token bakiyesine göre tier hesapla"""
        if balance == 0:
            return TokenTier.FREELOADER
        elif balance <= 50:
            return TokenTier.BASIC
        elif balance <= 200:
            return TokenTier.REGULAR
        elif balance <= 500:
            return TokenTier.PREMIUM
        else:
            return TokenTier.VIP
    
    async def calculate_message_cost(
        self, 
        user_id: str, 
        message_type: str = "basic",
        mood: str = "neutral",
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """Mesaj maliyetini hesapla"""
        try:
            # Base cost
            if message_type == "basic":
                base_cost = self.config.base_message_cost
            elif message_type == "premium":
                base_cost = self.config.premium_message_cost
            elif message_type == "voice":
                base_cost = self.config.voice_message_cost
            elif message_type == "video":
                duration = context.get("duration_minutes", 1) if context else 1
                base_cost = self.config.video_call_cost_per_minute * duration
            else:
                base_cost = self.config.base_message_cost
            
            # Mood modifier
            mood_multiplier = self.config.mood_multipliers.get(mood, 1.0)
            
            # VIP discount
            user_tier = await self.get_user_tier(user_id)
            vip_discount = self.config.vip_discounts.get(user_tier.value, 1.0)
            
            # Final cost
            final_cost = int(base_cost * mood_multiplier * vip_discount)
            
            logger.debug(f"💰 Cost calculated for {user_id}: {final_cost} tokens",
                        base=base_cost, mood=mood_multiplier, vip=vip_discount)
            
            return max(1, final_cost)  # Minimum 1 token
            
        except Exception as e:
            logger.error(f"❌ Error calculating cost: {e}")
            return self.config.base_message_cost
    
    async def can_afford_message(
        self, 
        user_id: str, 
        message_type: str = "basic",
        mood: str = "neutral"
    ) -> Tuple[bool, int, int]:
        """
        Kullanıcı mesaj için ödeme yapabilir mi?
        
        Returns:
            (can_afford, current_balance, required_cost)
        """
        balance = await self.get_user_balance(user_id)
        cost = await self.calculate_message_cost(user_id, message_type, mood)
        
        can_afford = balance >= cost
        
        return can_afford, balance, cost
    
    async def process_message_payment(
        self, 
        user_id: str, 
        message_type: str = "basic",
        mood: str = "neutral",
        force: bool = False
    ) -> Dict[str, Any]:
        """Mesaj ödemesini işle"""
        try:
            can_afford, balance, cost = await self.can_afford_message(user_id, message_type, mood)
            
            if not can_afford and not force:
                return {
                    "success": False,
                    "reason": "insufficient_tokens",
                    "balance": balance,
                    "required": cost,
                    "deficit": cost - balance
                }
            
            # Token'ları düş
            new_balance = max(0, balance - cost)
            self.user_balances[user_id] = new_balance
            
            # İşlemi kaydet
            await self._record_transaction(
                user_id, 
                cost, 
                "spend", 
                f"Message payment ({message_type})"
            )
            
            # Tier'ı güncelle
            self.user_tiers[user_id] = self._calculate_tier(new_balance)
            
            # İstatistikleri güncelle
            self.daily_stats["total_spent"] += cost
            self.daily_stats["active_users"].add(user_id)
            self.daily_stats["transactions"] += 1
            
            logger.info(f"💸 Payment processed: {user_id} spent {cost} tokens, balance: {new_balance}")
            
            return {
                "success": True,
                "cost": cost,
                "new_balance": new_balance,
                "tier": self.user_tiers[user_id].value
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing payment: {e}")
            return {
                "success": False,
                "reason": "processing_error",
                "error": str(e)
            }
    
    async def add_tokens(
        self, 
        user_id: str, 
        amount: int, 
        reason: str = "purchase"
    ) -> Dict[str, Any]:
        """Kullanıcıya token ekle"""
        try:
            current_balance = await self.get_user_balance(user_id)
            new_balance = current_balance + amount
            
            self.user_balances[user_id] = new_balance
            self.user_tiers[user_id] = self._calculate_tier(new_balance)
            
            # İşlemi kaydet
            await self._record_transaction(user_id, amount, "purchase", reason)
            
            # İstatistikleri güncelle
            self.daily_stats["total_earned"] += amount
            self.daily_stats["active_users"].add(user_id)
            self.daily_stats["transactions"] += 1
            
            logger.info(f"💰 Tokens added: {user_id} received {amount} tokens, balance: {new_balance}")
            
            return {
                "success": True,
                "added": amount,
                "new_balance": new_balance,
                "tier": self.user_tiers[user_id].value
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding tokens: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_response_delay(self, user_id: str) -> Tuple[int, int]:
        """Kullanıcı tier'ına göre yanıt gecikmesi al"""
        tier = await self.get_user_tier(user_id)
        return self.config.response_delays.get(tier.value, (10, 60))
    
    async def is_user_on_cooldown(self, user_id: str) -> Tuple[bool, Optional[int]]:
        """Kullanıcı cooldown'da mı?"""
        if user_id not in self.active_cooldowns:
            return False, None
        
        cooldown_end = self.active_cooldowns[user_id]
        now = datetime.now()
        
        if now >= cooldown_end:
            del self.active_cooldowns[user_id]
            return False, None
        
        remaining_seconds = int((cooldown_end - now).total_seconds())
        return True, remaining_seconds
    
    async def set_user_cooldown(self, user_id: str, seconds: int) -> None:
        """Kullanıcıya cooldown uygula"""
        cooldown_end = datetime.now() + timedelta(seconds=seconds)
        self.active_cooldowns[user_id] = cooldown_end
        
        logger.info(f"⏰ Cooldown set for {user_id}: {seconds} seconds")
    
    async def give_bonus_tokens(
        self, 
        user_id: str, 
        amount: int, 
        reason: str
    ) -> Dict[str, Any]:
        """Bonus token ver"""
        return await self.add_tokens(user_id, amount, f"bonus: {reason}")
    
    async def apply_penalty(
        self, 
        user_id: str, 
        amount: int, 
        reason: str
    ) -> Dict[str, Any]:
        """Token cezası uygula"""
        try:
            current_balance = await self.get_user_balance(user_id)
            penalty = min(amount, current_balance)  # Bakiyeden fazla düşme
            
            new_balance = current_balance - penalty
            self.user_balances[user_id] = new_balance
            self.user_tiers[user_id] = self._calculate_tier(new_balance)
            
            # İşlemi kaydet
            await self._record_transaction(user_id, penalty, "penalty", reason)
            
            logger.info(f"⚠️ Penalty applied: {user_id} lost {penalty} tokens, balance: {new_balance}")
            
            return {
                "success": True,
                "penalty": penalty,
                "new_balance": new_balance,
                "tier": self.user_tiers[user_id].value
            }
            
        except Exception as e:
            logger.error(f"❌ Error applying penalty: {e}")
            return {"success": False, "error": str(e)}
    
    async def _record_transaction(
        self, 
        user_id: str, 
        amount: int, 
        transaction_type: str, 
        reason: str
    ) -> None:
        """İşlemi kaydet"""
        if user_id not in self.transaction_history:
            self.transaction_history[user_id] = []
        
        transaction = TokenTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            timestamp=datetime.now(),
            reason=reason
        )
        
        self.transaction_history[user_id].append(transaction)
        
        # Son 100 işlemi sakla
        if len(self.transaction_history[user_id]) > 100:
            self.transaction_history[user_id] = self.transaction_history[user_id][-100:]
    
    async def get_user_economy_stats(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcının ekonomi istatistikleri"""
        balance = await self.get_user_balance(user_id)
        tier = await self.get_user_tier(user_id)
        
        # İşlem geçmişi
        transactions = self.transaction_history.get(user_id, [])
        total_spent = sum(t.amount for t in transactions if t.transaction_type == "spend")
        total_purchased = sum(t.amount for t in transactions if t.transaction_type == "purchase")
        
        # Cooldown durumu
        on_cooldown, cooldown_remaining = await self.is_user_on_cooldown(user_id)
        
        # Yanıt gecikmesi
        min_delay, max_delay = await self.get_response_delay(user_id)
        
        return {
            "user_id": user_id,
            "current_balance": balance,
            "tier": tier.value,
            "total_spent": total_spent,
            "total_purchased": total_purchased,
            "transaction_count": len(transactions),
            "on_cooldown": on_cooldown,
            "cooldown_remaining": cooldown_remaining,
            "response_delay_range": [min_delay, max_delay],
            "last_transaction": transactions[-1].timestamp.isoformat() if transactions else None
        }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Sistem geneli istatistikler"""
        total_users = len(self.user_balances)
        total_balance = sum(self.user_balances.values())
        
        # Tier dağılımı
        tier_distribution = {}
        for tier in TokenTier:
            tier_distribution[tier.value] = sum(
                1 for user_tier in self.user_tiers.values() 
                if user_tier == tier
            )
        
        return {
            "total_users": total_users,
            "total_token_balance": total_balance,
            "tier_distribution": tier_distribution,
            "daily_stats": {
                **self.daily_stats,
                "active_users": len(self.daily_stats["active_users"])
            },
            "active_cooldowns": len(self.active_cooldowns)
        } 