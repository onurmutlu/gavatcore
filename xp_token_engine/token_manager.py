from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🪙 GavatCoin Token Manager v1.1 🪙

Core Token Motoru - XP → Token ↔ Harcama sistemi
OnlyVips v6.0 Token Economy Engine
"""

import aiosqlite
import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class TokenManager:
    """Production-ready token management system"""
    
    def __init__(self, db_path: str = "xp_token_engine/tokens.db"):
        self.db_path = db_path
        self.initialized = False
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def initialize(self):
        """Initialize database and tables"""
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None  # Autocommit mode
        ) as db:
            # Create balances table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS balances (
                    user_id TEXT PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create transactions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    reason TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
        
        self.initialized = True
        logger.info("🪙 TokenManager initialized successfully")
    
    async def _ensure_initialized(self):
        """Ensure database is initialized"""
        if not self.initialized:
            await self.initialize()
    
    async def xp_to_token(self, user_id: str, xp: int) -> int:
        """
        Converts XP to token (1 XP = 1 Token)
        Returns new token balance
        """
        await self._ensure_initialized()
        
        if xp <= 0:
            raise ValueError("XP amount must be positive")
        
        tokens = xp  # 1:1 conversion rate
        
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None
        ) as db:
            # Get current balance or create user
            async with db.execute(
                "SELECT balance FROM balances WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                current_balance = row[0] if row else 0
            
            # Update balance
            new_balance = current_balance + tokens
            await db.execute("""
                INSERT OR REPLACE INTO balances (user_id, balance, updated_at)
                VALUES (?, ?, ?)
            """, (user_id, new_balance, datetime.now().isoformat()))
            
            # Log transaction
            await db.execute("""
                INSERT INTO transactions (user_id, type, amount, reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, "EARN", tokens, f"XP conversion: {xp} XP → {tokens} tokens", datetime.now().isoformat()))
            
            await db.commit()
        
        logger.info(f"💰 {user_id}: {xp} XP → {tokens} tokens (balance: {new_balance})")
        return new_balance
    
    async def spend_token(self, user_id: str, amount: int, reason: str) -> bool:
        """
        Deducts tokens and logs reason
        Returns True if successful, raises error if insufficient balance
        """
        await self._ensure_initialized()
        
        if amount <= 0:
            raise ValueError("Spend amount must be positive")
        
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None
        ) as db:
            # Check current balance
            async with db.execute(
                "SELECT balance FROM balances WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                current_balance = row[0] if row else 0
            
            if current_balance < amount:
                raise ValueError(f"Insufficient balance: {current_balance} < {amount}")
            
            # Deduct tokens
            new_balance = current_balance - amount
            await db.execute("""
                UPDATE balances 
                SET balance = ?, updated_at = ?
                WHERE user_id = ?
            """, (new_balance, datetime.now().isoformat(), user_id))
            
            # Log transaction
            await db.execute("""
                INSERT INTO transactions (user_id, type, amount, reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, "SPEND", -amount, reason, datetime.now().isoformat()))
            
            await db.commit()
        
        logger.info(f"💸 {user_id}: Spent {amount} tokens for '{reason}' (balance: {new_balance})")
        return True
    
    async def get_balance(self, user_id: str) -> int:
        """Returns current token balance"""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None
        ) as db:
            async with db.execute(
                "SELECT balance FROM balances WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def log_transaction(self, user_id: str, type: str, amount: int, reason: str):
        """Log transaction to database"""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None
        ) as db:
            await db.execute("""
                INSERT INTO transactions (user_id, type, amount, reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, type, amount, reason, datetime.now().isoformat()))
            await db.commit()
    
    async def get_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction logs for user"""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None
        ) as db:
            async with db.execute("""
                SELECT id, type, amount, reason, timestamp
                FROM transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "type": row[1],
                        "amount": row[2],
                        "reason": row[3],
                        "timestamp": row[4]
                    }
                    for row in rows
                ]
    
    async def get_all_users_stats(self) -> Dict[str, Any]:
        """Get system-wide token statistics"""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(
            self.db_path, 
            timeout=10.0,
            isolation_level=None
        ) as db:
            # Total users
            async with db.execute("SELECT COUNT(*) FROM balances") as cursor:
                total_users = (await cursor.fetchone())[0]
            
            # Total tokens in circulation
            async with db.execute("SELECT SUM(balance) FROM balances") as cursor:
                total_tokens = (await cursor.fetchone())[0] or 0
            
            # Total transactions
            async with db.execute("SELECT COUNT(*) FROM transactions") as cursor:
                total_transactions = (await cursor.fetchone())[0]
            
            # Top users by balance
            async with db.execute("""
                SELECT user_id, balance 
                FROM balances 
                ORDER BY balance DESC 
                LIMIT 10
            """) as cursor:
                top_users = await cursor.fetchall()
            
            return {
                "total_users": total_users,
                "total_tokens": total_tokens,
                "total_transactions": total_transactions,
                "top_users": [{"user_id": row[0], "balance": row[1]} for row in top_users],
                "timestamp": datetime.now().isoformat()
            }

# Global instance for easy import
token_manager = TokenManager()

# Async context manager support
class TokenManagerContext:
    def __init__(self, manager: TokenManager):
        self.manager = manager
    
    async def __aenter__(self):
        await self.manager.initialize()
        return self.manager
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

def get_token_manager() -> TokenManagerContext:
    """Get token manager with async context support"""
    return TokenManagerContext(token_manager) 