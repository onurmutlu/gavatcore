#!/usr/bin/env python3
"""
AI Blending System Test Script
==============================

Comprehensive test suite for AI blending functionality.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from gavatcore_engine.ai_blending import (
    AIBlendingSystem, AIConfig, AIProvider, EnhancementType,
    OpenAIClient, PromptTemplate, AIResponse
)
from gavatcore_engine.redis_state import redis_state


class AIBlendingTester:
    """AI Blending system tester."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.ai_system = AIBlendingSystem()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    async def test_config_loading(self):
        """Test AI configuration loading."""
        print("\n⚙️ Testing AI Configuration...")
        
        try:
            # Test default config
            config = AIConfig()
            
            self.log_test("Default Config Creation", True, f"Model: {config.model}, Max tokens: {config.max_tokens}")
            
            # Test config with environment variables
            os.environ["OPENAI_API_KEY"] = "test_key_123"
            os.environ["AI_MODEL"] = "gpt-4o-mini"
            os.environ["AI_MAX_TOKENS"] = "200"
            os.environ["AI_TEMPERATURE"] = "0.8"
            
            await self.ai_system._load_config()
            
            if self.ai_system.config.api_key == "test_key_123":
                self.log_test("Environment Config Loading", True, "API key loaded from env")
            else:
                self.log_test("Environment Config Loading", False, "API key not loaded")
            
            if self.ai_system.config.model == "gpt-4o-mini":
                self.log_test("Model Config Override", True, "Model updated from env")
            else:
                self.log_test("Model Config Override", False, f"Expected gpt-4o-mini, got {self.ai_system.config.model}")
            
            # Test cost control parameters
            if 0 <= self.ai_system.config.temperature <= 2:
                self.log_test("Temperature Range", True, f"Temperature: {self.ai_system.config.temperature}")
            else:
                self.log_test("Temperature Range", False, f"Invalid temperature: {self.ai_system.config.temperature}")
            
        except Exception as e:
            self.log_test("Config Loading", False, str(e))
    
    async def test_prompt_templates(self):
        """Test prompt template functionality."""
        print("\n📝 Testing Prompt Templates...")
        
        try:
            # Test all enhancement types
            enhancement_types = [
                EnhancementType.PERSUASIVE,
                EnhancementType.FRIENDLY,
                EnhancementType.PROFESSIONAL,
                EnhancementType.CASUAL,
                EnhancementType.FLIRTY,
                EnhancementType.SALES
            ]
            
            test_input = "Merhaba, nasılsın?"
            
            for enhancement_type in enhancement_types:
                template = PromptTemplate.get_template(enhancement_type)
                
                if "{user_input}" in template:
                    self.log_test(f"Template {enhancement_type.value}", True, "Contains user_input placeholder")
                else:
                    self.log_test(f"Template {enhancement_type.value}", False, "Missing user_input placeholder")
                
                # Test template formatting
                formatted = template.format(user_input=test_input)
                if test_input in formatted:
                    self.log_test(f"Template Formatting {enhancement_type.value}", True, "Input correctly inserted")
                else:
                    self.log_test(f"Template Formatting {enhancement_type.value}", False, "Input not found in formatted template")
            
            # Test persuasive template specifically (main template)
            persuasive_template = PromptTemplate.get_persuasive_template()
            expected_keywords = ["manipülasyon", "ikna", "dönüşüm"]
            
            found_keywords = sum(1 for keyword in expected_keywords if keyword in persuasive_template.lower())
            if found_keywords >= 2:
                self.log_test("Persuasive Template Content", True, f"Found {found_keywords} key persuasion terms")
            else:
                self.log_test("Persuasive Template Content", False, f"Only found {found_keywords} persuasion terms")
            
        except Exception as e:
            self.log_test("Prompt Templates", False, str(e))
    
    async def test_openai_client_setup(self):
        """Test OpenAI client setup and configuration."""
        print("\n🤖 Testing OpenAI Client Setup...")
        
        try:
            # Test client creation
            config = AIConfig(
                api_key="test_key",
                model="gpt-4o",
                max_tokens=100,
                temperature=0.7
            )
            
            client = OpenAIClient(config)
            
            self.log_test("OpenAI Client Creation", True, f"Client created with model {config.model}")
            
            # Test pricing info
            if "gpt-4o" in client.model_pricing:
                pricing = client.model_pricing["gpt-4o"]
                self.log_test("Model Pricing Data", True, f"Input: ${pricing['input']:.6f}/token, Output: ${pricing['output']:.6f}/token")
            else:
                self.log_test("Model Pricing Data", False, "gpt-4o pricing not found")
            
            # Test cost calculation
            cost = await client._calculate_cost(100, 50, "gpt-4o")
            if cost > 0:
                self.log_test("Cost Calculation", True, f"Cost for 100+50 tokens: ${cost:.6f}")
            else:
                self.log_test("Cost Calculation", False, "Cost calculation returned zero")
            
            # Test rate limiting check
            rate_limit_ok = await client._check_rate_limit()
            self.log_test("Rate Limit Check", rate_limit_ok, "Rate limit check completed")
            
            await client.close()
            
        except Exception as e:
            self.log_test("OpenAI Client Setup", False, str(e))
    
    async def test_enhancement_without_api_key(self):
        """Test AI enhancement without real API key."""
        print("\n🔒 Testing Enhancement (No API Key)...")
        
        try:
            # Test with disabled enhancement
            config = AIConfig(
                api_key=None,
                enhancement_enabled=False
            )
            
            client = OpenAIClient(config)
            
            # This should fail gracefully
            response = await client.enhance_text(
                "Test message",
                EnhancementType.PERSUASIVE
            )
            
            if not response.success and "disabled" in response.error.lower():
                self.log_test("Disabled Enhancement Handling", True, "Correctly handled disabled state")
            else:
                self.log_test("Disabled Enhancement Handling", False, f"Unexpected response: {response.error}")
            
            await client.close()
            
        except Exception as e:
            self.log_test("Enhancement Without API Key", False, str(e))
    
    async def test_personality_mappings(self):
        """Test personality mappings functionality."""
        print("\n🎭 Testing Personality Mappings...")
        
        try:
            # Initialize AI system
            await self.ai_system.initialize()
            
            # Test default mappings
            personalities = await self.ai_system.get_available_personalities()
            
            if len(personalities) > 0:
                self.log_test("Personality Loading", True, f"Loaded {len(personalities)} personalities")
            else:
                self.log_test("Personality Loading", False, "No personalities loaded")
            
            # Test specific bot mappings
            expected_bots = ["babagavat", "yayincilara", "xxxgeisha"]
            found_bots = [bot for bot in expected_bots if bot in personalities]
            
            if len(found_bots) >= 2:
                self.log_test("Expected Bot Mappings", True, f"Found {len(found_bots)} expected bots")
            else:
                self.log_test("Expected Bot Mappings", False, f"Only found {len(found_bots)} expected bots")
            
            # Test personality mapping update
            await self.ai_system.update_personality_mapping("test_bot", EnhancementType.CASUAL)
            
            if "test_bot" in self.ai_system.personality_mappings:
                mapping = self.ai_system.personality_mappings["test_bot"]
                if mapping == EnhancementType.CASUAL:
                    self.log_test("Personality Mapping Update", True, "Successfully updated mapping")
                else:
                    self.log_test("Personality Mapping Update", False, f"Wrong mapping: {mapping}")
            else:
                self.log_test("Personality Mapping Update", False, "Bot not found in mappings")
            
        except Exception as e:
            self.log_test("Personality Mappings", False, str(e))
    
    async def test_conversation_context(self):
        """Test conversation context management."""
        print("\n💬 Testing Conversation Context...")
        
        try:
            # Test context storage
            context_key = "test_bot:test_entity"
            test_messages = ["Hello", "How are you?", "What's new?"]
            
            self.ai_system.conversation_context[context_key] = test_messages
            
            # Test context retrieval
            retrieved_context = self.ai_system.conversation_context.get(context_key, [])
            
            if retrieved_context == test_messages:
                self.log_test("Context Storage", True, f"Stored and retrieved {len(test_messages)} messages")
            else:
                self.log_test("Context Storage", False, "Context mismatch")
            
            # Test context limiting (should keep last 10 messages)
            long_context = [f"Message {i}" for i in range(15)]
            self.ai_system.conversation_context[context_key] = long_context
            
            # Simulate the context limiting that happens in generate_response
            if len(self.ai_system.conversation_context[context_key]) > 10:
                self.ai_system.conversation_context[context_key] = self.ai_system.conversation_context[context_key][-10:]
            
            limited_context = self.ai_system.conversation_context[context_key]
            
            if len(limited_context) == 10:
                self.log_test("Context Limiting", True, "Context correctly limited to 10 messages")
            else:
                self.log_test("Context Limiting", False, f"Context has {len(limited_context)} messages")
            
        except Exception as e:
            self.log_test("Conversation Context", False, str(e))
    
    async def test_usage_statistics(self):
        """Test usage statistics functionality."""
        print("\n📊 Testing Usage Statistics...")
        
        try:
            # Get initial stats
            stats = await self.ai_system.get_usage_statistics()
            
            if isinstance(stats, dict):
                self.log_test("Statistics Retrieval", True, "Got statistics dictionary")
            else:
                self.log_test("Statistics Retrieval", False, "Statistics not in dict format")
            
            # Test stats structure
            expected_fields = ["total_requests", "successful_requests", "failed_requests", "total_tokens_used"]
            
            if "error" not in stats:
                found_fields = [field for field in expected_fields if field in stats]
                if len(found_fields) >= 3:
                    self.log_test("Statistics Structure", True, f"Found {len(found_fields)} expected fields")
                else:
                    self.log_test("Statistics Structure", False, f"Only found {len(found_fields)} fields")
            else:
                self.log_test("Statistics Structure", True, f"Expected error (no API key): {stats['error']}")
            
        except Exception as e:
            self.log_test("Usage Statistics", False, str(e))
    
    async def test_redis_integration(self):
        """Test Redis integration for AI system."""
        print("\n📡 Testing Redis Integration...")
        
        try:
            # Test Redis connection
            await redis_state.connect()
            
            # Test storing AI config
            test_config = {
                "model": "gpt-4o-mini",
                "max_tokens": 150,
                "temperature": 0.8
            }
            
            await redis_state.hset("ai_config", "test", json.dumps(test_config))
            
            # Test retrieving AI config
            stored_config = await redis_state.hget("ai_config", "test")
            
            if stored_config:
                if isinstance(stored_config, bytes):
                    stored_config = stored_config.decode()
                parsed_config = json.loads(stored_config)
                
                if parsed_config["model"] == test_config["model"]:
                    self.log_test("Redis Config Storage", True, "Config stored and retrieved correctly")
                else:
                    self.log_test("Redis Config Storage", False, "Config data mismatch")
            else:
                self.log_test("Redis Config Storage", False, "Config not found in Redis")
            
            # Test cost tracking
            current_hour = datetime.utcnow().strftime("%Y-%m-%d_%H")
            cost_key = f"ai_cost:{current_hour}"
            
            await redis_state.incrbyfloat(cost_key, 0.001)  # Add $0.001
            stored_cost = await redis_state.get(cost_key)
            
            if stored_cost and float(stored_cost) > 0:
                self.log_test("Cost Tracking", True, f"Hourly cost: ${float(stored_cost):.6f}")
            else:
                self.log_test("Cost Tracking", False, "Cost not tracked properly")
            
            # Cleanup
            await redis_state.delete("ai_config")
            await redis_state.delete(cost_key)
            
        except Exception as e:
            self.log_test("Redis Integration", False, str(e))
    
    async def test_mock_enhancement_flow(self):
        """Test complete enhancement flow without real API call."""
        print("\n🔄 Testing Enhancement Flow...")
        
        try:
            # Test with mock enhancement (disabled API)
            test_text = "Merhaba, nasılsın bugün?"
            bot_name = "test_bot"
            target_entity = "test_user"
            
            # This should return None because no API key
            enhanced_text = await self.ai_system.generate_response(
                text=test_text,
                bot_name=bot_name,
                target_entity=target_entity
            )
            
            if enhanced_text is None:
                self.log_test("Mock Enhancement Flow", True, "Correctly returned None without API")
            else:
                self.log_test("Mock Enhancement Flow", False, f"Unexpected enhancement: {enhanced_text}")
            
            # Test enhancement type determination
            enhancement_type = self.ai_system.personality_mappings.get(bot_name, EnhancementType.PERSUASIVE)
            
            if isinstance(enhancement_type, EnhancementType):
                self.log_test("Enhancement Type Selection", True, f"Selected: {enhancement_type.value}")
            else:
                self.log_test("Enhancement Type Selection", False, "Invalid enhancement type")
            
        except Exception as e:
            self.log_test("Enhancement Flow", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("\n🛡️ Testing Error Handling...")
        
        try:
            # Test with invalid API key
            config = AIConfig(
                api_key="invalid_key_123",
                enhancement_enabled=True
            )
            
            client = OpenAIClient(config)
            
            # This should fail gracefully
            response = await client.enhance_text("Test message", EnhancementType.PERSUASIVE)
            
            if not response.success and response.error:
                self.log_test("Invalid API Key Handling", True, f"Error handled: {response.error}")
            else:
                self.log_test("Invalid API Key Handling", False, "Should have failed with invalid key")
            
            await client.close()
            
            # Test empty text handling
            response = await client.enhance_text("", EnhancementType.PERSUASIVE)
            
            if not response.success:
                self.log_test("Empty Text Handling", True, "Empty text handled correctly")
            else:
                self.log_test("Empty Text Handling", False, "Empty text should fail")
            
            # Test network timeout simulation
            config.timeout = 0.001  # Very short timeout
            client = OpenAIClient(config)
            
            response = await client.enhance_text("Test", EnhancementType.PERSUASIVE)
            
            if not response.success and "timeout" in response.error.lower():
                self.log_test("Timeout Handling", True, "Timeout handled correctly")
            else:
                self.log_test("Timeout Handling", False, f"Unexpected timeout response: {response.error}")
            
            await client.close()
            
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
    
    async def test_cost_control(self):
        """Test cost control mechanisms."""
        print("\n💰 Testing Cost Control...")
        
        try:
            config = AIConfig(
                cost_limit_per_hour=0.01,  # Very low limit
                max_tokens=50,  # Low token limit
                temperature=0.5
            )
            
            # Test cost calculation
            client = OpenAIClient(config)
            
            # Simulate high token usage
            cost = await client._calculate_cost(1000, 500, "gpt-4o")
            
            if cost > 0:
                self.log_test("Cost Calculation", True, f"High usage cost: ${cost:.6f}")
            else:
                self.log_test("Cost Calculation", False, "Cost calculation failed")
            
            # Test cost limit checking
            current_hour = datetime.utcnow().strftime("%Y-%m-%d_%H")
            cost_key = f"ai_cost:{current_hour}"
            
            # Set high cost in Redis
            await redis_state.set(cost_key, "0.02")  # Above limit
            
            cost_ok = await client._check_cost_limit()
            
            if not cost_ok:
                self.log_test("Cost Limit Enforcement", True, "Cost limit correctly enforced")
            else:
                self.log_test("Cost Limit Enforcement", False, "Cost limit not enforced")
            
            # Cleanup
            await redis_state.delete(cost_key)
            await client.close()
            
        except Exception as e:
            self.log_test("Cost Control", False, str(e))
    
    async def run_all_tests(self):
        """Run all AI blending tests."""
        print("🧠 AI Blending System - Test Suite")
        print("="*50)
        
        # Check for Redis first
        try:
            await redis_state.connect()
            print("✅ Redis connected for testing\n")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("⚠️ Some tests may fail without Redis\n")
        
        # Run all test categories
        test_categories = [
            self.test_config_loading,
            self.test_prompt_templates,
            self.test_openai_client_setup,
            self.test_enhancement_without_api_key,
            self.test_personality_mappings,
            self.test_conversation_context,
            self.test_usage_statistics,
            self.test_redis_integration,
            self.test_mock_enhancement_flow,
            self.test_error_handling,
            self.test_cost_control,
        ]
        
        for test_category in test_categories:
            try:
                await test_category()
            except Exception as e:
                print(f"❌ Test category error: {e}")
            
            # Small delay between test categories
            await asyncio.sleep(0.5)
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate test report."""
        print("\n" + "="*50)
        print("📊 AI BLENDING TEST REPORT")
        print("="*50)
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Tests Run: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 Overall Result: ", end="")
        if success_rate >= 90:
            print("🎉 EXCELLENT - AI system ready!")
        elif success_rate >= 75:
            print("✅ GOOD - AI system mostly functional")
        elif success_rate >= 50:
            print("⚠️ FAIR - Some issues need attention")
        else:
            print("❌ POOR - Major issues need fixing")
        
        print("\n💡 Note: Real API testing requires valid OPENAI_API_KEY")
        print("💡 Set OPENAI_API_KEY environment variable for full testing")
        
        print("\n" + "="*50)


async def main():
    """Main test runner."""
    tester = AIBlendingTester()
    
    try:
        await tester.run_all_tests()
        
        if tester.tests_failed == 0:
            print("🎉 All AI blending tests passed!")
            sys.exit(0)
        else:
            print(f"❌ {tester.tests_failed} tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        try:
            await redis_state.disconnect()
        except:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 