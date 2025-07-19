from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
Memory Context Tracker - Bellek ve bağlam takip sistemi
"""

import structlog
from typing import Dict, List, Any

logger = structlog.get_logger("gavatcore.memory_context_tracker")

class MemoryContextTracker:
    def __init__(self):
        self.memories: Dict[str, List[Dict[str, Any]]] = {}
        self.contexts: Dict[str, Dict[str, Any]] = {}
        logger.info("🧠 MemoryContextTracker başlatıldı")

    def add_memory(self, user_id: str, memory: Dict[str, Any]):
        """Kullanıcı için bellek ekle"""
        if user_id not in self.memories:
            self.memories[user_id] = []
        self.memories[user_id].append(memory)
        logger.info(f"✅ Bellek eklendi: {user_id}")

    def get_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Kullanıcının belleğini getir"""
        return self.memories.get(user_id, [])

    def set_context(self, user_id: str, context: Dict[str, Any]):
        """Kullanıcı için bağlam ayarla"""
        self.contexts[user_id] = context
        logger.info(f"✅ Bağlam ayarlandı: {user_id}")

    def get_context(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcının bağlamını getir"""
        return self.contexts.get(user_id, {})

# Global instance
memory_context_tracker = MemoryContextTracker() 