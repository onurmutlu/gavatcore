from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
OnlyVipsBotConversationSystem - VIP kullanıcılar için özel sohbet sistemi
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger("gavatcore.onlyvips_bot")

@dataclass
class Conversation:
    id: str
    user_id: str
    messages: List[Dict[str, Any]]
    created_at: str

class OnlyVipsBotConversationSystem:
    def __init__(self, data_dir: str = "data/conversations"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.conversations: Dict[str, Conversation] = {}
        self.load_conversations()

    def load_conversations(self) -> None:
        """Konuşmaları yükle"""
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        conv = Conversation(**data)
                        self.conversations[conv.id] = conv
            logger.info(f"✅ {len(self.conversations)} konuşma yüklendi")
        except Exception as e:
            logger.error(f"❌ Konuşma yükleme hatası: {e}")

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Konuşmayı getir"""
        return self.conversations.get(conv_id)

    def list_conversations(self) -> List[Dict[str, Any]]:
        """Tüm konuşmaları listele"""
        return [asdict(conv) for conv in self.conversations.values()]

# Global instance
onlyvips_bot_conversation_system = OnlyVipsBotConversationSystem() 