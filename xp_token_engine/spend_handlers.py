from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🔥 GavatCoin Spend Handlers v1.0 🔥

Token harcama noktaları - İçerik, VIP, Boost, NFT sistemi
OnlyVips v6.0 Token Economy Spending Engine
"""

import asyncio
import logging
from typing import Dict, Any, Tuple
from .token_manager import token_manager

logger = logging.getLogger(__name__)

class SpendHandlers:
    """Token spending handlers for various services"""
    
    # Token costs for different services
    COSTS = {
        "content": 10,
        "vip": 25,
        "boost": 5,
        "nft": 50,
        "priority_dm": 15
    }
    
    @staticmethod
    async def buy_content(user_id: str, content_id: str) -> Tuple[bool, str]:
        """
        Buy premium content with tokens
        Cost: 10 tokens
        """
        cost = SpendHandlers.COSTS["content"]
        reason = f"Premium content purchase: {content_id}"
        
        try:
            await token_manager.spend_token(user_id, cost, reason)
            
            # Here you would grant access to the content
            # For now, we'll just log it
            logger.info(f"🎬 {user_id}: Bought content '{content_id}' for {cost} tokens")
            
            return True, f"Successfully purchased content '{content_id}' for {cost} tokens"
            
        except ValueError as e:
            error_msg = f"Failed to buy content: {str(e)}"
            logger.warning(f"❌ {user_id}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error buying content: {str(e)}"
            logger.error(f"💥 {user_id}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    async def upgrade_to_vip(user_id: str) -> Tuple[bool, str]:
        """
        Upgrade user to VIP status
        Cost: 25 tokens
        """
        cost = SpendHandlers.COSTS["vip"]
        reason = "VIP status upgrade"
        
        try:
            await token_manager.spend_token(user_id, cost, reason)
            
            # Here you would update user's VIP status in your user database
            # For now, we'll just log it
            logger.info(f"👑 {user_id}: Upgraded to VIP for {cost} tokens")
            
            return True, f"Successfully upgraded to VIP status for {cost} tokens"
            
        except ValueError as e:
            error_msg = f"Failed to upgrade to VIP: {str(e)}"
            logger.warning(f"❌ {user_id}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error upgrading to VIP: {str(e)}"
            logger.error(f"💥 {user_id}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    async def boost_daily_quest(user_id: str) -> Tuple[bool, str]:
        """
        Boost daily quest rewards
        Cost: 5 tokens
        """
        cost = SpendHandlers.COSTS["boost"]
        reason = "Daily quest boost"
        
        try:
            await token_manager.spend_token(user_id, cost, reason)
            
            # Here you would apply quest boost multiplier
            # For now, we'll just log it
            logger.info(f"⚡ {user_id}: Boosted daily quest for {cost} tokens")
            
            return True, f"Successfully boosted daily quest for {cost} tokens"
            
        except ValueError as e:
            error_msg = f"Failed to boost quest: {str(e)}"
            logger.warning(f"❌ {user_id}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error boosting quest: {str(e)}"
            logger.error(f"💥 {user_id}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    async def unlock_nft_badge(user_id: str) -> Tuple[bool, str]:
        """
        Unlock exclusive NFT badge
        Cost: 50 tokens
        """
        cost = SpendHandlers.COSTS["nft"]
        reason = "NFT badge unlock"
        
        try:
            await token_manager.spend_token(user_id, cost, reason)
            
            # Here you would mint or assign NFT badge to user
            # For now, we'll just log it
            logger.info(f"🎨 {user_id}: Unlocked NFT badge for {cost} tokens")
            
            return True, f"Successfully unlocked exclusive NFT badge for {cost} tokens"
            
        except ValueError as e:
            error_msg = f"Failed to unlock NFT: {str(e)}"
            logger.warning(f"❌ {user_id}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error unlocking NFT: {str(e)}"
            logger.error(f"💥 {user_id}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    async def priority_dm_access(user_id: str) -> Tuple[bool, str]:
        """
        Get priority DM access with bots
        Cost: 15 tokens
        """
        cost = SpendHandlers.COSTS["priority_dm"]
        reason = "Priority DM access (24h)"
        
        try:
            await token_manager.spend_token(user_id, cost, reason)
            
            # Here you would set priority flag for 24 hours
            # For now, we'll just log it
            logger.info(f"📨 {user_id}: Activated priority DM for {cost} tokens")
            
            return True, f"Successfully activated priority DM access for {cost} tokens (24h)"
            
        except ValueError as e:
            error_msg = f"Failed to activate priority DM: {str(e)}"
            logger.warning(f"❌ {user_id}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error activating priority DM: {str(e)}"
            logger.error(f"💥 {user_id}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    async def get_service_costs() -> Dict[str, int]:
        """Get all service costs"""
        return SpendHandlers.COSTS.copy()
    
    @staticmethod
    async def can_afford(user_id: str, service: str) -> Tuple[bool, int, int]:
        """
        Check if user can afford a service
        Returns: (can_afford, current_balance, required_cost)
        """
        if service not in SpendHandlers.COSTS:
            raise ValueError(f"Unknown service: {service}")
        
        cost = SpendHandlers.COSTS[service]
        balance = await token_manager.get_balance(user_id)
        
        return balance >= cost, balance, cost
    
    @staticmethod
    async def get_affordable_services(user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get list of services user can afford"""
        balance = await token_manager.get_balance(user_id)
        
        affordable_services = {}
        for service, cost in SpendHandlers.COSTS.items():
            affordable_services[service] = {
                "cost": cost,
                "affordable": balance >= cost,
                "balance_needed": max(0, cost - balance)
            }
        
        return affordable_services

# Service mappings for easy access
SERVICE_HANDLERS = {
    "content": SpendHandlers.buy_content,
    "vip": SpendHandlers.upgrade_to_vip,
    "boost": SpendHandlers.boost_daily_quest,
    "nft": SpendHandlers.unlock_nft_badge,
    "priority_dm": SpendHandlers.priority_dm_access
}

async def spend_token_for_service(user_id: str, service: str, **kwargs) -> Tuple[bool, str]:
    """
    Generic spending function
    
    Args:
        user_id: User ID
        service: Service name (content, vip, boost, nft, priority_dm)
        **kwargs: Additional arguments for specific services
    
    Returns:
        (success, message)
    """
    if service not in SERVICE_HANDLERS:
        return False, f"Unknown service: {service}"
    
    handler = SERVICE_HANDLERS[service]
    
    # Call appropriate handler based on service
    if service == "content":
        content_id = kwargs.get("content_id", "premium_content")
        return await handler(user_id, content_id)
    else:
        return await handler(user_id) 