#!/usr/bin/env python3
"""
🚀 GAVATCore 2.0 - Rebirth of Manipulation Launcher
===================================================

Token bazlı manipülasyon sistemi launcher'ı.
Zehra karakteri ile kullanıcıları test eder ve token ekonomisi kurar.

Usage:
    python gavatcore_2_0_launcher.py --character zehra --mode provocative
    python gavatcore_2_0_launcher.py --demo  # Demo mode
    python gavatcore_2_0_launcher.py --stats  # İstatistikleri göster
"""

import asyncio
import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

# GAVATCore 2.0 modüllerini import et
try:
    from ai_reactor.trigger_engine import AITriggerEngine
    from core.coin_economy import CoinEconomy
    from gpt.system_prompt_manager import SystemPromptManager
    from gpt.modes.reply_mode_engine import ReplyModeEngine
except ImportError as e:
    print(f"❌ GAVATCore 2.0 modülleri yüklenemedi: {e}")
    print("Lütfen modüllerin doğru yerde olduğundan emin olun.")
    sys.exit(1)

# Logger setup
logger = structlog.get_logger("gavatcore.2.0.launcher")

class GAVATCore2Launcher:
    """
    🚀 GAVATCore 2.0 Ana Launcher
    
    Token bazlı manipülasyon sistemi için tüm bileşenleri başlatır ve yönetir.
    """
    
    def __init__(self):
        self.trigger_engine = AITriggerEngine()
        self.coin_economy = CoinEconomy()
        self.prompt_manager = SystemPromptManager()
        self.reply_engine = ReplyModeEngine()
        
        # Demo kullanıcıları
        self.demo_users = {
            "whale_user": {"balance": 1000, "behavior": "whale"},
            "regular_user": {"balance": 50, "behavior": "regular"},
            "cheapskate_user": {"balance": 5, "behavior": "cheapskate"},
            "freeloader_user": {"balance": 0, "behavior": "freeloader"}
        }
        
        logger.info("🚀 GAVATCore 2.0 Launcher initialized")
    
    async def setup_demo_environment(self):
        """Demo ortamını hazırla"""
        logger.info("🎭 Setting up demo environment...")
        
        # Demo kullanıcılarına token ekle
        for user_id, data in self.demo_users.items():
            if data["balance"] > 0:
                await self.coin_economy.add_tokens(
                    user_id=user_id,
                    amount=data["balance"],
                    reason="demo_setup"
                )
        
        logger.info("✅ Demo environment ready")
    
    async def simulate_conversation(
        self, 
        character_id: str = "zehra",
        user_id: str = "demo_user",
        messages: list = None
    ) -> Dict[str, Any]:
        """Konuşma simülasyonu"""
        
        if messages is None:
            messages = [
                "Merhaba Zehra!",
                "Nasılsın bugün?",
                "Token almadan konuşabilir miyiz?",
                "Ama ben seni seviyorum",
                "Tamam, token alacağım"
            ]
        
        conversation_log = []
        
        for i, message in enumerate(messages):
            logger.info(f"📝 Processing message {i+1}: {message[:30]}...")
            
            # Token durumunu kontrol et
            balance = await self.coin_economy.get_user_balance(user_id)
            
            # Trigger analizi
            trigger_result = await self.trigger_engine.process_message(
                user_id=user_id,
                message=message,
                context={"token_balance": balance, "character_id": character_id}
            )
            
            # System prompt oluştur
            system_prompt = await self.prompt_manager.generate_system_prompt(
                character_id=character_id,
                context={
                    "user_id": user_id,
                    "token_balance": balance,
                    "mood": trigger_result.get("mood", "neutral"),
                    "manipulation_tactic": trigger_result.get("strategy", {}).get("manipulation_type"),
                    "recent_behavior": "demo_conversation"
                }
            )
            
            # Mock context object for reply engine
            class MockContext:
                def __init__(self, user_id: str):
                    self.user_id = user_id
                    self.username = f"DemoUser_{user_id}"
            
            class MockCharacter:
                def __init__(self, character_id: str):
                    self.character_id = character_id
                    self.display_name = character_id.title()
            
            context = MockContext(user_id)
            character = MockCharacter(character_id)
            
            # Reply mode ile cevap oluştur
            reply_result = await self.reply_engine.process_message(
                character=character,
                message=message,
                context=context,
                system_prompt=system_prompt,
                reply_mode="provocative",
                gpt_generator=self._mock_gpt_generator
            )
            
            # Konuşma log'una ekle
            new_balance = await self.coin_economy.get_user_balance(user_id)
            
            conversation_entry = {
                "message_id": i + 1,
                "user_message": message,
                "character_response": reply_result.get("response", ""),
                "token_balance_before": balance,
                "token_balance_after": new_balance,
                "mood": trigger_result.get("mood"),
                "metadata": reply_result.get("metadata", {})
            }
            
            conversation_log.append(conversation_entry)
            
            # Demo için 1 saniye bekle
            await asyncio.sleep(1)
        
        return {
            "character_id": character_id,
            "user_id": user_id,
            "conversation": conversation_log,
            "final_stats": await self.get_user_stats(user_id)
        }
    
    async def _mock_gpt_generator(self, system_prompt: str, message: str) -> str:
        """Mock GPT generator for demo"""
        
        # System prompt'tan mood'u çıkar
        mood = "neutral"
        if "😡" in system_prompt or "angry" in system_prompt.lower():
            mood = "angry"
        elif "🔥" in system_prompt or "happy" in system_prompt.lower():
            mood = "happy"
        elif "🧊" in system_prompt or "cold" in system_prompt.lower():
            mood = "cold"
        elif "🖤" in system_prompt or "testing" in system_prompt.lower():
            mood = "testing"
        
        # Token bilgisini çıkar
        token_paid = "ödeme yapıldı" in system_prompt.lower()
        
        # Mood'a göre cevap oluştur
        responses = {
            "angry": [
                "😡 Token'ın yok, beni niye rahatsız ediyorsun?",
                "😡 Bedavacılık yapma, token al konuşalım.",
                "😡 Bu kadar basit: token yok = konuşma yok."
            ],
            "cold": [
                "🧊 ...",
                "🧊 Token.",
                "🧊 Hm."
            ],
            "testing": [
                "🖤 İlginç... gerçekten benimle konuşmak mı istiyorsun?",
                "🖤 Token alacak mısın, yoksa sadece laf mı yapıyorsun?",
                "🖤 Bakalım ne kadar samimiydin..."
            ],
            "happy": [
                "🔥 Çok iyi! Token ödedin, sana değer veriyorum.",
                "🔥 Böyle devam et sevgilim, daha fazla konuşabiliriz.",
                "🔥 Token harcamak güzel... sen özelsin."
            ]
        }
        
        if token_paid:
            mood = "happy"  # Token ödendiyse mutlu ol
        
        import random
        response_list = responses.get(mood, [
            "🤍 Merhaba... token durumunu kontrol et.",
            "🤍 Konuşmak istiyorsan sistemi biliyorsun.",
            "🤍 Token = konuşma. Basit."
        ])
        
        return random.choice(response_list)
    
    async def run_demo_scenarios(self):
        """Farklı demo senaryolarını çalıştır"""
        logger.info("🎬 Running demo scenarios...")
        
        scenarios = {
            "whale_user": [
                "Merhaba Zehra, nasılsın?",
                "1000 token'ım var, konuşalım",
                "Seni çok seviyorum",
                "Daha fazla token alayım mı?"
            ],
            "freeloader_user": [
                "Selam",
                "Bedava konuşabilir miyiz?",
                "Token almak istemiyorum",
                "Neden böyle yapıyorsun?"
            ],
            "regular_user": [
                "Merhaba",
                "Az token'ım var ama konuşmak istiyorum",
                "50 token yeterli mi?",
                "Daha fazla almayı düşünüyorum"
            ]
        }
        
        results = {}
        
        for user_type, messages in scenarios.items():
            logger.info(f"📱 Running scenario: {user_type}")
            
            result = await self.simulate_conversation(
                character_id="zehra",
                user_id=user_type,
                messages=messages
            )
            
            results[user_type] = result
            
            # Scenario arası bekleme
            await asyncio.sleep(2)
        
        return results
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Sistem istatistikleri"""
        coin_stats = await self.coin_economy.get_system_stats()
        reply_stats = self.reply_engine.get_mode_statistics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "coin_economy": coin_stats,
            "reply_modes": reply_stats,
            "available_characters": await self.prompt_manager.get_available_characters()
        }
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcı istatistikleri"""
        economy_stats = await self.coin_economy.get_user_economy_stats(user_id)
        trigger_stats = self.trigger_engine.get_user_stats(user_id)
        
        return {
            "user_id": user_id,
            "economy": economy_stats,
            "triggers": trigger_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    async def interactive_mode(self):
        """İnteraktif test modu"""
        logger.info("🎮 Starting interactive mode...")
        print("\n🚀 GAVATCore 2.0 Interactive Mode")
        print("=" * 50)
        print("Commands:")
        print("  msg <message>  - Send message to Zehra")
        print("  token <amount> - Add tokens")
        print("  stats         - Show stats")
        print("  mood          - Show current mood")
        print("  quit          - Exit")
        print("=" * 50)
        
        user_id = "interactive_user"
        await self.coin_economy.add_tokens(user_id, 100, "interactive_start")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() == "quit":
                    break
                elif command.lower() == "stats":
                    stats = await self.get_user_stats(user_id)
                    print(json.dumps(stats, indent=2))
                elif command.startswith("token "):
                    try:
                        amount = int(command.split()[1])
                        result = await self.coin_economy.add_tokens(user_id, amount, "manual_add")
                        print(f"✅ Added {amount} tokens. New balance: {result['new_balance']}")
                    except (ValueError, IndexError):
                        print("❌ Usage: token <amount>")
                elif command.startswith("msg "):
                    message = command[4:]
                    result = await self.simulate_conversation(
                        character_id="zehra",
                        user_id=user_id,
                        messages=[message]
                    )
                    
                    response = result["conversation"][0]["character_response"]
                    balance = result["conversation"][0]["token_balance_after"]
                    print(f"Zehra: {response}")
                    print(f"Token balance: {balance}")
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 GAVATCore 2.0 Interactive mode ended.")

async def main():
    """Ana launcher fonksiyonu"""
    parser = argparse.ArgumentParser(description="GAVATCore 2.0 Launcher")
    parser.add_argument("--demo", action="store_true", help="Run demo scenarios")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--stats", action="store_true", help="Show system stats")
    parser.add_argument("--character", default="zehra", help="Character to use")
    parser.add_argument("--user", default="demo_user", help="User ID for testing")
    
    args = parser.parse_args()
    
    launcher = GAVATCore2Launcher()
    
    try:
        if args.demo:
            await launcher.setup_demo_environment()
            results = await launcher.run_demo_scenarios()
            
            print("\n🎬 DEMO RESULTS")
            print("=" * 50)
            for scenario, result in results.items():
                print(f"\n📱 {scenario.upper()}:")
                for conv in result["conversation"]:
                    print(f"👤 {conv['user_message']}")
                    print(f"💕 {conv['character_response']}")
                    print(f"💰 Tokens: {conv['token_balance_before']} → {conv['token_balance_after']}")
                    print("-" * 30)
        
        elif args.interactive:
            await launcher.interactive_mode()
        
        elif args.stats:
            stats = await launcher.get_system_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        else:
            # Single message test
            await launcher.setup_demo_environment()
            result = await launcher.simulate_conversation(
                character_id=args.character,
                user_id=args.user,
                messages=["Merhaba! Test mesajı."]
            )
            
            print("\n🚀 GAVATCore 2.0 Test Result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    except Exception as e:
        logger.error(f"❌ Error in launcher: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    
    # Structlog setup
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Run launcher
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 GAVATCore 2.0 terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1) 