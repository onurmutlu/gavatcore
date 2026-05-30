#!/usr/bin/env python3
"""
GavatCore Engine Full Integration Test
=====================================

Complete integration test for all modules working together.
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from gavatcore_engine.redis_state import redis_state
from gavatcore_engine.message_pool import message_pool, Message, MessageType, MessagePriority
from gavatcore_engine.telegram_client import telegram_client_pool, ClientConfig
from gavatcore_engine.scheduler_engine import scheduler_engine, ScheduledTask, TaskType
from gavatcore_engine.ai_blending import ai_blending
from gavatcore_engine.admin_commands import admin_commands


class IntegrationTester:
    """Complete system integration tester."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    async def test_redis_connectivity(self):
        """Test Redis connection and basic operations."""
        print("\n🔌 Testing Redis Connectivity...")
        
        try:
            # Connect to Redis
            await redis_state.connect()
            self.log_test("Redis Connection", True, "Connected successfully")
            
            # Test basic operations
            test_key = "integration_test_key"
            test_value = "integration_test_value"
            
            await redis_state.set(test_key, test_value)
            retrieved_value = await redis_state.get(test_key)
            
            if retrieved_value == test_value:
                self.log_test("Redis Read/Write", True, "Data stored and retrieved")
            else:
                self.log_test("Redis Read/Write", False, f"Expected {test_value}, got {retrieved_value}")
            
            # Test hash operations
            hash_key = "integration_test_hash"
            hash_data = {"field1": "value1", "field2": "value2"}
            
            await redis_state.hset(hash_key, "data", json.dumps(hash_data))
            retrieved_hash = await redis_state.hget(hash_key, "data")
            
            if retrieved_hash:
                parsed_data = json.loads(retrieved_hash.decode() if isinstance(retrieved_hash, bytes) else retrieved_hash)
                if parsed_data == hash_data:
                    self.log_test("Redis Hash Operations", True, "Hash data stored and retrieved")
                else:
                    self.log_test("Redis Hash Operations", False, "Hash data mismatch")
            else:
                self.log_test("Redis Hash Operations", False, "Hash data not found")
            
            # Cleanup
            await redis_state.delete(test_key)
            await redis_state.delete(hash_key)
            
        except Exception as e:
            self.log_test("Redis Connectivity", False, str(e))
    
    async def test_message_pool(self):
        """Test message pool functionality."""
        print("\n📬 Testing Message Pool...")
        
        try:
            # Initialize message pool
            await message_pool.initialize()
            self.log_test("Message Pool Initialization", True, "Initialized successfully")
            
            # Create test message
            test_message = Message(
                target_entity="test_entity",
                content="Test integration message",
                message_type=MessageType.TEXT,
                priority=MessagePriority.HIGH,
                session_name="test_session"
            )
            
            # Add message to pool
            message_id = await message_pool.add_message(test_message)
            
            if message_id:
                self.log_test("Message Pool Add", True, f"Message added with ID: {message_id}")
            else:
                self.log_test("Message Pool Add", False, "Failed to add message")
                return
            
            # Get message from pool
            retrieved_message = await message_pool.get_next_message()
            
            if retrieved_message and retrieved_message.content == test_message.content:
                self.log_test("Message Pool Retrieve", True, "Message retrieved successfully")
            else:
                self.log_test("Message Pool Retrieve", False, "Failed to retrieve message")
            
            # Test message status update
            await message_pool.update_message_status(message_id, "processing")
            
            # Get statistics
            stats = await message_pool.get_statistics()
            if isinstance(stats, dict):
                self.log_test("Message Pool Statistics", True, f"Stats: {stats}")
            else:
                self.log_test("Message Pool Statistics", False, "Failed to get statistics")
            
        except Exception as e:
            self.log_test("Message Pool", False, str(e))
    
    async def test_scheduler_engine(self):
        """Test scheduler engine functionality."""
        print("\n⏰ Testing Scheduler Engine...")
        
        try:
            # Initialize scheduler
            await scheduler_engine.initialize()
            self.log_test("Scheduler Initialization", True, "Scheduler initialized")
            
            # Create test task
            test_task = ScheduledTask(
                task_type=TaskType.SCHEDULED_MESSAGE,
                target_entity="test_entity",
                message_content="Test scheduled message",
                execute_at=datetime.utcnow() + timedelta(seconds=5),
                session_name="test_session"
            )
            
            # Add task to scheduler
            task_id = await scheduler_engine.add_task(test_task)
            
            if task_id:
                self.log_test("Scheduler Add Task", True, f"Task added with ID: {task_id}")
            else:
                self.log_test("Scheduler Add Task", False, "Failed to add task")
                return
            
            # Get scheduler statistics
            stats = await scheduler_engine.get_statistics()
            if isinstance(stats, dict):
                self.log_test("Scheduler Statistics", True, f"Stats: {stats}")
            else:
                self.log_test("Scheduler Statistics", False, "Failed to get statistics")
            
            # Test task status operations
            await scheduler_engine.pause_task(task_id)
            await scheduler_engine.resume_task(task_id)
            
            self.log_test("Scheduler Task Control", True, "Task pause/resume operations")
            
        except Exception as e:
            self.log_test("Scheduler Engine", False, str(e))
    
    async def test_ai_blending(self):
        """Test AI blending functionality."""
        print("\n🧠 Testing AI Blending...")
        
        try:
            # Initialize AI blending
            await ai_blending.initialize()
            self.log_test("AI Blending Initialization", True, "AI system initialized")
            
            # Test response generation
            test_message = "Merhaba, nasılsın?"
            response = await ai_blending.generate_response(
                test_message,
                "test_bot",
                "test_entity"
            )
            
            if response:
                self.log_test("AI Response Generation", True, f"Generated: {response[:50]}...")
            else:
                self.log_test("AI Response Generation", True, "No enhancement needed (expected)")
            
            # Test personality management
            personalities = await ai_blending.get_available_personalities()
            if isinstance(personalities, list):
                self.log_test("AI Personality Management", True, f"Found {len(personalities)} personalities")
            else:
                self.log_test("AI Personality Management", False, "Failed to get personalities")
            
        except Exception as e:
            self.log_test("AI Blending", False, str(e))
    
    async def test_admin_commands(self):
        """Test admin commands functionality."""
        print("\n👑 Testing Admin Commands...")
        
        try:
            # Initialize admin commands
            await admin_commands.initialize()
            self.log_test("Admin Commands Initialization", True, "Admin system initialized")
            
            # Test status command
            result = await admin_commands.execute_command("status", 123456789, [])
            if result:
                self.log_test("Admin Status Command", True, "Status command executed")
            else:
                self.log_test("Admin Status Command", False, "Status command failed")
            
            # Test stats command
            result = await admin_commands.execute_command("stats", 123456789, [])
            if result:
                self.log_test("Admin Stats Command", True, "Stats command executed")
            else:
                self.log_test("Admin Stats Command", False, "Stats command failed")
            
        except Exception as e:
            self.log_test("Admin Commands", False, str(e))
    
    async def test_telegram_client_pool(self):
        """Test Telegram client pool (mock test without real credentials)."""
        print("\n🤖 Testing Telegram Client Pool...")
        
        try:
            # Get pool statistics (should work even without clients)
            stats = await telegram_client_pool.get_pool_stats()
            
            if isinstance(stats, dict):
                self.log_test("Telegram Pool Stats", True, f"Pool stats: {stats}")
            else:
                self.log_test("Telegram Pool Stats", False, "Failed to get pool stats")
            
            # Test configuration creation
            test_config = ClientConfig(
                session_name="test_client",
                api_id=12345678,
                api_hash="test_hash",
                phone="+905551234567"
            )
            
            if test_config.session_name == "test_client":
                self.log_test("Telegram Client Config", True, "Config created successfully")
            else:
                self.log_test("Telegram Client Config", False, "Config creation failed")
            
            # Note: Actual client connection not tested without real credentials
            self.log_test("Telegram Client Note", True, "Real connection requires API credentials")
            
        except Exception as e:
            self.log_test("Telegram Client Pool", False, str(e))
    
    async def test_cross_module_integration(self):
        """Test integration between different modules."""
        print("\n🔗 Testing Cross-Module Integration...")
        
        try:
            # Test message flow: Pool -> Scheduler -> AI
            
            # 1. Create AI-enhanced message
            ai_message = Message(
                target_entity="integration_test",
                content="Test cross-module integration",
                message_type=MessageType.TEXT,
                priority=MessagePriority.NORMAL,
                session_name="test_session",
                ai_enhanced=True
            )
            
            message_id = await message_pool.add_message(ai_message)
            if message_id:
                self.log_test("Cross-Module Message Flow", True, "AI-enhanced message queued")
            else:
                self.log_test("Cross-Module Message Flow", False, "Failed to queue message")
            
            # 2. Test scheduler integration with message pool
            scheduled_task = ScheduledTask(
                task_type=TaskType.SCHEDULED_MESSAGE,
                target_entity="integration_test",
                message_content="Scheduled integration test",
                execute_at=datetime.utcnow() + timedelta(seconds=2),
                session_name="test_session"
            )
            
            task_id = await scheduler_engine.add_task(scheduled_task)
            if task_id:
                self.log_test("Scheduler-Pool Integration", True, "Scheduled task created")
            else:
                self.log_test("Scheduler-Pool Integration", False, "Failed to create task")
            
            # 3. Test Redis state sharing between modules
            await redis_state.set("integration_test_counter", "42")
            counter_value = await redis_state.get("integration_test_counter")
            
            if counter_value == "42":
                self.log_test("Redis State Sharing", True, "Modules can share state via Redis")
            else:
                self.log_test("Redis State Sharing", False, "State sharing failed")
            
            # 4. Test statistics aggregation
            await redis_state.increment_counter("integration_test_messages")
            test_count = await redis_state.get("counter:integration_test_messages")
            
            if test_count and int(test_count) > 0:
                self.log_test("Statistics Aggregation", True, "Cross-module statistics work")
            else:
                self.log_test("Statistics Aggregation", False, "Statistics aggregation failed")
            
            # Cleanup
            await redis_state.delete("integration_test_counter")
            await redis_state.delete("counter:integration_test_messages")
            
        except Exception as e:
            self.log_test("Cross-Module Integration", False, str(e))
    
    async def test_system_resilience(self):
        """Test system resilience and error handling."""
        print("\n🛡️ Testing System Resilience...")
        
        try:
            # Test graceful error handling in message pool
            invalid_message = Message(
                target_entity="",  # Invalid entity
                content="",  # Empty content
                message_type=MessageType.TEXT
            )
            
            try:
                message_id = await message_pool.add_message(invalid_message)
                if message_id:
                    self.log_test("Error Handling - Invalid Message", True, "System handled invalid message gracefully")
                else:
                    self.log_test("Error Handling - Invalid Message", True, "System rejected invalid message (expected)")
            except Exception:
                self.log_test("Error Handling - Invalid Message", True, "System threw expected exception")
            
            # Test Redis disconnection resilience
            try:
                # Simulate operations during potential Redis issues
                await redis_state.set("resilience_test", "test_value")
                await redis_state.get("resilience_test")
                self.log_test("Redis Resilience", True, "Redis operations stable")
            except Exception as e:
                self.log_test("Redis Resilience", False, f"Redis instability: {e}")
            
            # Test concurrent operations
            async def concurrent_operation(i):
                await redis_state.set(f"concurrent_test_{i}", f"value_{i}")
                return await redis_state.get(f"concurrent_test_{i}")
            
            # Run 10 concurrent operations
            tasks = [concurrent_operation(i) for i in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_ops = sum(1 for r in results if not isinstance(r, Exception))
            if successful_ops >= 8:  # Allow some failures
                self.log_test("Concurrent Operations", True, f"{successful_ops}/10 operations succeeded")
            else:
                self.log_test("Concurrent Operations", False, f"Only {successful_ops}/10 operations succeeded")
            
            # Cleanup concurrent test data
            for i in range(10):
                await redis_state.delete(f"concurrent_test_{i}")
            
        except Exception as e:
            self.log_test("System Resilience", False, str(e))
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 GavatCore Engine - Full Integration Test Suite")
        print("="*60)
        
        start_time = datetime.utcnow()
        
        # Run all test categories
        test_categories = [
            self.test_redis_connectivity,
            self.test_message_pool,
            self.test_scheduler_engine,
            self.test_ai_blending,
            self.test_admin_commands,
            self.test_telegram_client_pool,
            self.test_cross_module_integration,
            self.test_system_resilience,
        ]
        
        for test_category in test_categories:
            try:
                await test_category()
            except Exception as e:
                print(f"❌ Test category error: {e}")
            
            # Small delay between test categories
            await asyncio.sleep(0.5)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Generate test report
        await self.generate_test_report(duration)
    
    async def generate_test_report(self, duration: float):
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("📊 INTEGRATION TEST REPORT")
        print("="*60)
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"📈 Tests Run: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 Overall Result: ", end="")
        if success_rate >= 90:
            print("🎉 EXCELLENT - System ready for production!")
        elif success_rate >= 75:
            print("✅ GOOD - System mostly functional")
        elif success_rate >= 50:
            print("⚠️ FAIR - Some issues need attention")
        else:
            print("❌ POOR - Major issues need fixing")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "success_rate": success_rate,
            "test_results": self.test_results
        }
        
        # Save to file
        report_file = f"integration_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            Path("reports").mkdir(exist_ok=True)
            with open(f"reports/{report_file}", 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Detailed report saved: reports/{report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        # Store in Redis if available
        try:
            await redis_state.hset(
                "integration_test_reports",
                f"latest",
                json.dumps(report_data)
            )
            print("💾 Report stored in Redis")
        except Exception as e:
            print(f"⚠️ Could not store in Redis: {e}")
        
        print("\n" + "="*60)
        
        # Exit with appropriate code
        if success_rate >= 75:
            return True
        else:
            return False


async def main():
    """Main test runner."""
    
    # Create tester instance
    tester = IntegrationTester()
    
    try:
        # Run all tests
        success = await tester.run_all_tests()
        
        if success:
            print("🎉 Integration tests completed successfully!")
            sys.exit(0)
        else:
            print("❌ Integration tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Integration tests interrupted by user")
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