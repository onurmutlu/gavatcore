#!/usr/bin/env python3
"""
🧪 Test Universal Character System
==================================

Quick test script to verify all components work correctly.
"""

import sys
import asyncio
from datetime import datetime

def test_character_system():
    """Test the universal character system."""
    print("🧬 Testing Universal Character System...")
    print()

    try:
        # Test character manager
        from gpt.universal_character_manager import character_manager, ConversationContext
        print("✅ Universal Character Manager imported successfully")
        
        characters = character_manager.list_characters()
        print(f"✅ Found {len(characters)} characters: {characters}")
        
        if characters:
            char_id = characters[0]
            char = character_manager.get_character(char_id)
            print(f"✅ Character {char_id}: {char.display_name}")
            print(f"   Style: {char.style}")
            print(f"   Role: {char.role}")
            print(f"   Reply Mode: {char.reply_mode}")
            
            stats = character_manager.get_character_stats(char_id)
            print(f"✅ Character stats loaded: {len(stats)} fields")
        
        print()
        print("🎭 Testing Tone Adapter...")
        from gpt.traits.tone_adapter import ToneAdapter
        tone_adapter = ToneAdapter()
        print("✅ Tone Adapter initialized")
        
        if characters:
            suggestions = tone_adapter.get_tone_suggestions(char.style, char.role)
            print(f"✅ Tone suggestions: {suggestions['primary_tones']}")
        
        print()
        print("🎯 Testing Behavior Mapper...")
        from gpt.traits.behavior_mapper import BehaviorMapper
        behavior_mapper = BehaviorMapper()
        print("✅ Behavior Mapper initialized")
        
        if characters:
            analysis = behavior_mapper.get_behavior_analysis(char.role)
            print(f"✅ Behavior analysis: {analysis['detected_roles']}")
        
        print()
        print("🔄 Testing Reply Mode Engine...")
        from gpt.modes.reply_mode_engine import ReplyModeEngine
        reply_engine = ReplyModeEngine()
        print("✅ Reply Mode Engine initialized")
        
        print()
        print("🧠 Testing System Prompt Manager...")
        from gpt.system_prompt_manager import SystemPromptManager
        prompt_manager = SystemPromptManager()
        print("✅ System Prompt Manager initialized")
        
        print()
        print("🎉 ALL COMPONENTS LOADED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_response_generation():
    """Test response generation."""
    print("\n🤖 Testing Response Generation...")
    
    try:
        from gpt.universal_character_manager import character_manager, ConversationContext
        
        characters = character_manager.list_characters()
        if not characters:
            print("⚠️ No characters loaded, skipping response test")
            return
        
        char_id = characters[0]
        
        # Create test context
        context = ConversationContext(
            user_id="test_user",
            username="TestUser",
            sentiment_score=0.8,
            interaction_count=1
        )
        
        # Test engaging message
        message, metadata = await character_manager.get_engaging_message(char_id, context)
        print(f"✅ Engaging message: {message}")
        
        # Test reply message
        reply, metadata = await character_manager.get_reply_message(char_id, context)
        print(f"✅ Reply message: {reply}")
        
        print("✅ Response generation working!")
        
    except Exception as e:
        print(f"❌ Response generation error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    success = test_character_system()
    
    if success:
        print("\n" + "="*50)
        print("🚀 Running async response test...")
        asyncio.run(test_response_generation())
        
        print("\n" + "="*50)
        print("✅ UNIVERSAL CHARACTER SYSTEM READY!")
        print("🔌 You can now start the API server with:")
        print("   python api/universal_character_api.py")
    else:
        print("\n❌ SYSTEM NOT READY - Please fix errors first")

if __name__ == "__main__":
    main() 