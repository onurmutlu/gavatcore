from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
💰 GAVATCORE COIN CHECKER
Coin balance and transaction checking system
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

logger = structlog.get_logger("gavatcore.coin_checker")

class CoinChecker:
    """Coin balance and transaction management"""
    
    def __init__(self, api_url: str = "http://localhost:5051", api_key: Optional[str] = None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
        
    async def check_user_balance(self, user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
        """Check user's coin balance"""
        try:
            # Check cache first
            cache_key = f"balance_{user_id}"
            if self._check_cache(cache_key):
                logger.debug(f"💰 Returning cached balance for {user_id}")
                return self.cache[cache_key]['data']
            
            # Mock API call for testing
            # In production, implement actual API call
            balance_data = await self._mock_balance_check(user_id, username)
            
            # Cache the result
            self._cache_data(cache_key, balance_data)
            
            logger.info(f"💰 Balance checked for user {user_id}")
            return balance_data
            
        except Exception as e:
            logger.error(f"❌ Balance check error for {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'balance': 0,
                'status': 'error'
            }
    
    async def check_transaction_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's transaction history"""
        try:
            # Mock transaction history
            transactions = await self._mock_transaction_history(user_id, limit)
            
            logger.info(f"💳 Transaction history retrieved for {user_id}")
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Transaction history error for {user_id}: {e}")
            return []
    
    async def validate_payment(self, user_id: int, amount: float, transaction_id: Optional[str] = None) -> Dict[str, Any]:
        """Validate a payment/transaction"""
        try:
            # Mock payment validation
            validation_result = await self._mock_payment_validation(user_id, amount, transaction_id)
            
            logger.info(f"💸 Payment validation for {user_id}: {validation_result['status']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Payment validation error: {e}")
            return {
                'success': False,
                'status': 'error',
                'error': str(e)
            }
    
    async def add_coins(self, user_id: int, amount: float, reason: str = "admin_add") -> Dict[str, Any]:
        """Add coins to user's balance"""
        try:
            # Mock coin addition
            result = await self._mock_add_coins(user_id, amount, reason)
            
            # Clear cache for this user
            cache_key = f"balance_{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            logger.info(f"💰 Added {amount} coins to user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Add coins error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def spend_coins(self, user_id: int, amount: float, reason: str = "purchase") -> Dict[str, Any]:
        """Spend coins from user's balance"""
        try:
            # Check balance first
            balance_data = await self.check_user_balance(user_id)
            
            if not balance_data.get('success', False):
                return {
                    'success': False,
                    'error': 'Cannot check balance'
                }
            
            current_balance = balance_data.get('balance', 0)
            
            if current_balance < amount:
                return {
                    'success': False,
                    'error': 'Insufficient balance',
                    'current_balance': current_balance,
                    'required': amount
                }
            
            # Mock spending
            result = await self._mock_spend_coins(user_id, amount, reason)
            
            # Clear cache
            cache_key = f"balance_{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            logger.info(f"💸 User {user_id} spent {amount} coins for {reason}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Spend coins error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_cache(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        if (datetime.now() - cached_time).total_seconds() > self.cache_ttl:
            del self.cache[key]
            return False
        
        return True
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def _mock_balance_check(self, user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
        """Mock balance check for testing"""
        # Simulate some randomness for testing
        import random
        
        base_balance = 1000 + (user_id % 1000)
        random_modifier = random.randint(-200, 500)
        final_balance = max(0, base_balance + random_modifier)
        
        return {
            'success': True,
            'user_id': user_id,
            'username': username,
            'balance': final_balance,
            'currency': 'GavatCoin',
            'last_update': datetime.now().isoformat(),
            'status': 'active',
            'tier': 'vip' if final_balance > 1000 else 'standard'
        }
    
    async def _mock_transaction_history(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """Mock transaction history for testing"""
        transactions = []
        
        for i in range(min(limit, 5)):  # Max 5 mock transactions
            transaction = {
                'id': f"tx_{user_id}_{i}",
                'user_id': user_id,
                'amount': 50 + (i * 25),
                'type': 'credit' if i % 2 == 0 else 'debit',
                'reason': 'vip_purchase' if i % 2 == 1 else 'daily_bonus',
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            }
            transactions.append(transaction)
        
        return transactions
    
    async def _mock_payment_validation(self, user_id: int, amount: float, transaction_id: Optional[str] = None) -> Dict[str, Any]:
        """Mock payment validation for testing"""
        # Simulate validation process
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return {
            'success': True,
            'user_id': user_id,
            'amount': amount,
            'transaction_id': transaction_id or f"tx_{user_id}_{datetime.now().timestamp()}",
            'status': 'verified',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _mock_add_coins(self, user_id: int, amount: float, reason: str) -> Dict[str, Any]:
        """Mock adding coins for testing"""
        return {
            'success': True,
            'user_id': user_id,
            'amount_added': amount,
            'reason': reason,
            'new_balance': 1500 + amount,  # Mock new balance
            'timestamp': datetime.now().isoformat()
        }
    
    async def _mock_spend_coins(self, user_id: int, amount: float, reason: str) -> Dict[str, Any]:
        """Mock spending coins for testing"""
        return {
            'success': True,
            'user_id': user_id,
            'amount_spent': amount,
            'reason': reason,
            'new_balance': max(0, 1500 - amount),  # Mock new balance
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_coin_stats(self) -> Dict[str, Any]:
        """Get overall coin system statistics"""
        return {
            'total_users': 1247,
            'total_coins_in_circulation': 2_500_000,
            'total_transactions_today': 89,
            'average_balance': 1_500,
            'top_balance': 50_000,
            'system_status': 'operational',
            'last_update': datetime.now().isoformat()
        } 