"""
🧬 GAVATCore Universal Character System
======================================

Universal character management and response generation system for GAVATCore.

Modules:
- universal_character_manager: Core character management
- system_prompt_manager: Dynamic prompt generation
- modes/: Reply mode engines (manual, gpt, hybrid, manualplus)
- traits/: Character trait adapters (tone, behavior)
"""

from .universal_character_manager import (
    character_manager,
    get_character_response,
    list_available_characters,
    get_character_info
)

__version__ = "1.0.0"
__all__ = [
    "character_manager",
    "get_character_response", 
    "list_available_characters",
    "get_character_info"
] 