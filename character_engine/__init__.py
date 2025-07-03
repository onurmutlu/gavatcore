"""
🧠 GAVATCore Character Engine
Modüler karakter yönetim sistemi - Her bot için özel kişilik ve GPT destekli yanıt motoru
"""

from .character_manager import CharacterManager, CharacterConfig
from .gpt_reply_generator import GPTReplyGenerator
from .personality_router import PersonalityRouter, ReplyType
from .fallback_reply_manager import FallbackReplyManager
from .memory_context_tracker import MemoryContextTracker

__version__ = "2.0.0"
__all__ = [
    "CharacterManager",
    "CharacterConfig",
    "GPTReplyGenerator", 
    "PersonalityRouter",
    "ReplyType",
    "FallbackReplyManager",
    "MemoryContextTracker"
] 