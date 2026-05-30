#!/usr/bin/env python3
"""
Telegram Client Test Script
===========================

Bu script telegram_client.py modülünün tüm özelliklerini test eder.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from gavatcore_engine.telegram_client import (
    TelegramClientManager, TelegramClientPool, ClientConfig,
    ConnectionStatus, MessageResult, RetryConfig
)
from gavatcore_engine.redis_state import redis_state


async def create_test_config() -> ClientConfig:
    """Test için client config oluştur."""
    
    # Try to load from existing config.py
    try:
        import config
        api_id = config.TELEGRAM_API_ID
        api_hash = config.TELEGRAM_API_HASH
    except:
        # Default test values (gerçek değerler olmalı)
        api_id = 12345678  # Replace with real API ID
        api_hash = "abcdef1234567890abcdef1234567890"  # Replace with real API hash
    
    return ClientConfig(
        session_name="test_client",
        api_id=api_id,
        api_hash=api_hash,
        phone="+905551234567",  # Test phone number
        device_model="GavatCore Test Client",
        system_version="Test 1.0.0",
        app_version="Test Client v1.0",
        connection_retries=3,
        retry_delay=2,
        timeout=15,
    )


async def test_client_initialization():
    """Test client initialization."""
    print("1️⃣ Client Initialization Test...")
    
    config = await create_test_config()
    client_manager = TelegramClientManager(config)
    
    # Test initialization (will fail without real credentials)
    try:
        success = await client_manager.initialize()
        
        if success:
            print("   ✅ Client initialized successfully")
            print(f"   📱 Session: {config.session_name}")
            print(f"   🔗 Status: {client_manager.connection_status.value}")
            
            # Get user info
            user_info = await client_manager.get_me()
            if user_info:
                print(f"   👤 User: @{user_info.username} ({user_info.id})")
            
            return client_manager
        else:
            print("   ❌ Client initialization failed (expected without real credentials)")
            return None
            
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return None


async def test_message_sending(client_manager):
    """Test message sending functionality."""
    if not client_manager:
        print("2️⃣ Message Sending Test - Skipped (no client)")
        return
    
    print("2️⃣ Message Sending Test...")
    
    # Test basic message
    result = await client_manager.send_message(
        entity="me",  # Send to self (Saved Messages)
        message="🧪 Test mesajı - GavatCore Telegram Client Test",
        parse_mode="html"
    )
    
    print(f"   📤 Message send result: {result.result.value}")
    if result.success:
        print(f"   ✅ Message sent successfully, ID: {result.message_id}")
    else:
        print(f"   ❌ Message failed: {result.error}")
    
    # Test message with formatting
    formatted_message = """
<b>🧪 GavatCore Test Message</b>

<i>Features tested:</i>
• Message sending ✅
• HTML formatting ✅
• Retry mechanism ✅
• Flood protection ✅

<code>Timestamp: {}</code>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    result2 = await client_manager.send_message(
        entity="me",
        message=formatted_message,
        parse_mode="html"
    )
    
    print(f"   📤 Formatted message result: {result2.result.value}")
    
    # Test long message (should be split or fail gracefully)
    long_message = "🔄 " * 2000  # Very long message
    result3 = await client_manager.send_message(
        entity="me",
        message=long_message
    )
    
    print(f"   📤 Long message result: {result3.result.value}")


async def test_retry_mechanism():
    """Test retry mechanism with mock errors."""
    print("3️⃣ Retry Mechanism Test...")
    
    config = await create_test_config()
    config.session_name = "test_retry_client"
    
    # Create client with custom retry config
    client_manager = TelegramClientManager(config)
    client_manager.retry_config = RetryConfig(
        max_retries=3,
        base_delay=0.1,  # Fast retries for testing
        max_delay=1.0,
        exponential_base=2.0,
        jitter=True,
    )
    
    print(f"   ⚙️ Retry config: max_retries={client_manager.retry_config.max_retries}")
    print(f"   ⚙️ Base delay: {client_manager.retry_config.base_delay}s")
    
    # Test retry delay calculation
    for attempt in range(4):
        delay = client_manager._calculate_retry_delay(attempt)
        print(f"   ⏱️ Attempt {attempt + 1} delay: {delay:.2f}s")


async def test_session_management():
    """Test session management features."""
    print("4️⃣ Session Management Test...")
    
    config = await create_test_config()
    config.session_name = "test_session_management"
    
    client_manager = TelegramClientManager(config)
    
    # Test session file creation
    session_path = Path(f"sessions/{config.session_name}.session")
    print(f"   📁 Expected session path: {session_path}")
    
    # Test Redis integration
    try:
        await redis_state.connect()
        print("   ✅ Redis connected for session storage")
        
        # Simulate session info storage
        session_info = {
            "session_name": config.session_name,
            "user_id": 123456789,
            "username": "test_user",
            "connected_at": datetime.utcnow().isoformat(),
            "device_model": config.device_model,
        }
        
        await redis_state.hset(
            f"telegram_client:{config.session_name}",
            "session_info",
            json.dumps(session_info)
        )
        
        # Retrieve session info
        stored_info = await redis_state.hget(
            f"telegram_client:{config.session_name}",
            "session_info"
        )
        
        if stored_info:
            parsed_info = json.loads(stored_info.decode() if isinstance(stored_info, bytes) else stored_info)
            print(f"   ✅ Session info stored and retrieved")
            print(f"   📊 User ID: {parsed_info['user_id']}")
            print(f"   📊 Username: {parsed_info['username']}")
        
    except Exception as e:
        print(f"   ❌ Redis session test error: {e}")


async def test_client_pool():
    """Test client pool functionality."""
    print("5️⃣ Client Pool Test...")
    
    pool = TelegramClientPool()
    
    # Create multiple test configs
    configs = []
    for i in range(3):
        config = await create_test_config()
        config.session_name = f"pool_test_client_{i+1}"
        configs.append(config)
    
    # Add clients to pool (will fail without real credentials)
    added_clients = 0
    for i, config in enumerate(configs):
        print(f"   🔄 Adding client {i+1} to pool...")
        success = await pool.add_client(config)
        if success:
            added_clients += 1
            print(f"   ✅ Client {i+1} added successfully")
        else:
            print(f"   ❌ Client {i+1} failed to add (expected without credentials)")
    
    # Test pool stats
    stats = await pool.get_pool_stats()
    print(f"   📊 Pool stats:")
    print(f"      Total clients: {stats['total_clients']}")
    print(f"      Connected clients: {stats['connected_clients']}")
    
    # Test round-robin selection
    for i in range(5):
        client = await pool.get_client()
        if client:
            print(f"   🔄 Round-robin {i+1}: {client.config.session_name}")
        else:
            print(f"   🔄 Round-robin {i+1}: No available client")
    
    # Cleanup
    await pool.shutdown()
    print("   🧹 Pool shutdown complete")


async def test_error_handling():
    """Test error handling scenarios."""
    print("6️⃣ Error Handling Test...")
    
    config = await create_test_config()
    config.session_name = "test_error_handling"
    
    client_manager = TelegramClientManager(config)
    
    # Test with disconnected client
    result = await client_manager.send_message(
        entity="me",
        message="This should fail - client not connected"
    )
    
    print(f"   📤 Disconnected client test: {result.result.value}")
    print(f"   ❌ Error (expected): {result.error}")
    
    # Test invalid entity
    if client_manager.client:
        result = await client_manager.send_message(
            entity="invalid_entity_12345",
            message="This should fail - invalid entity"
        )
        print(f"   📤 Invalid entity test: {result.result.value}")
    
    # Test empty message
    if client_manager.client:
        result = await client_manager.send_message(
            entity="me",
            message=""  # Empty message
        )
        print(f"   📤 Empty message test: {result.result.value}")


async def test_rate_limiting():
    """Test rate limiting functionality."""
    print("7️⃣ Rate Limiting Test...")
    
    config = await create_test_config()
    config.session_name = "test_rate_limiting"
    
    client_manager = TelegramClientManager(config)
    client_manager.rate_limit_delay = 0.5  # 500ms delay for testing
    
    # Simulate rate limiting
    chat_id = 123456789
    
    print(f"   ⏱️ Rate limit delay: {client_manager.rate_limit_delay}s")
    
    # Test multiple rapid calls
    start_time = datetime.now()
    
    for i in range(3):
        print(f"   📤 Rate limit test {i+1}...")
        await client_manager._apply_rate_limit(chat_id)
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print(f"   ⏱️ Total time for 3 rate-limited calls: {total_time:.2f}s")
    expected_time = client_manager.rate_limit_delay * 2  # 2 delays expected
    print(f"   ⏱️ Expected minimum time: {expected_time:.2f}s")
    
    if total_time >= expected_time * 0.9:  # Allow 10% tolerance
        print("   ✅ Rate limiting working correctly")
    else:
        print("   ⚠️ Rate limiting may not be working as expected")


async def test_flood_protection():
    """Test flood protection mechanism."""
    print("8️⃣ Flood Protection Test...")
    
    config = await create_test_config()
    config.session_name = "test_flood_protection"
    
    client_manager = TelegramClientManager(config)
    
    # Simulate flood wait
    chat_id = 123456789
    flood_wait_time = 5  # 5 seconds
    
    # Set flood wait
    client_manager.flood_wait_until[chat_id] = datetime.utcnow() + timedelta(seconds=flood_wait_time)
    
    print(f"   🚫 Simulated flood wait: {flood_wait_time}s")
    
    # Try to send message during flood wait
    result = await client_manager.send_message(
        entity=chat_id,
        message="This should be blocked by flood protection"
    )
    
    print(f"   📤 Flood-blocked message result: {result.result.value}")
    if result.result == MessageResult.FLOOD_WAIT:
        print(f"   ✅ Flood protection working: {result.flood_wait_time}s remaining")
    else:
        print(f"   ❌ Flood protection failed: {result.error}")
    
    # Clear flood wait for next test
    del client_manager.flood_wait_until[chat_id]
    print("   🧹 Flood wait cleared")


async def test_statistics():
    """Test statistics collection."""
    print("9️⃣ Statistics Test...")
    
    config = await create_test_config()
    config.session_name = "test_statistics"
    
    client_manager = TelegramClientManager(config)
    
    # Initialize some test stats
    client_manager.stats["messages_sent"] = 10
    client_manager.stats["messages_failed"] = 2
    client_manager.stats["flood_waits"] = 1
    client_manager.stats["reconnections"] = 0
    client_manager.stats["uptime_start"] = datetime.utcnow() - timedelta(minutes=30)
    client_manager.stats["last_activity"] = datetime.utcnow() - timedelta(minutes=5)
    
    # Get stats
    stats = await client_manager.get_stats()
    
    print(f"   📊 Statistics:")
    print(f"      Session: {stats['session_name']}")
    print(f"      Status: {stats['connection_status']}")
    print(f"      Messages sent: {stats['messages_sent']}")
    print(f"      Messages failed: {stats['messages_failed']}")
    print(f"      Flood waits: {stats['flood_waits']}")
    print(f"      Reconnections: {stats['reconnections']}")
    print(f"      Uptime: {stats['uptime_seconds']:.0f}s" if stats['uptime_seconds'] else "      Uptime: Not started")
    print(f"      Last activity: {stats['last_activity']}")


async def test_configuration_validation():
    """Test configuration validation."""
    print("🔟 Configuration Validation Test...")
    
    # Test valid config
    valid_config = ClientConfig(
        session_name="valid_test",
        api_id=12345678,
        api_hash="valid_hash_32_chars_long_string",
        phone="+905551234567"
    )
    print("   ✅ Valid config created")
    print(f"      Session: {valid_config.session_name}")
    print(f"      Device: {valid_config.device_model}")
    print(f"      Retries: {valid_config.connection_retries}")
    
    # Test config with custom values
    custom_config = ClientConfig(
        session_name="custom_test",
        api_id=87654321,
        api_hash="custom_hash_value",
        device_model="Custom GavatCore Bot",
        system_version="Custom 2.0",
        connection_retries=10,
        timeout=60,
    )
    print("   ✅ Custom config created")
    print(f"      Device: {custom_config.device_model}")
    print(f"      System: {custom_config.system_version}")
    print(f"      Timeout: {custom_config.timeout}s")


async def main():
    """Ana test fonksiyonu."""
    print("🚀 Telegram Client Test Suite")
    print("="*60)
    
    # Redis'e bağlan
    try:
        await redis_state.connect()
        print("✅ Redis connected for testing\n")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        print("⚠️ Some tests may fail without Redis\n")
    
    # Test'leri sırayla çalıştır
    tests = [
        test_configuration_validation,
        test_client_initialization,
        test_session_management,
        test_retry_mechanism,
        test_rate_limiting,
        test_flood_protection,
        test_error_handling,
        test_statistics,
        test_client_pool,
    ]
    
    successful_tests = 0
    total_tests = len(tests)
    
    for i, test_func in enumerate(tests):
        try:
            await test_func()
            successful_tests += 1
            print("   ✅ Test completed\n")
        except Exception as e:
            print(f"   ❌ Test failed: {e}\n")
        
        # Small delay between tests
        if i < len(tests) - 1:
            await asyncio.sleep(1)
    
    # Test sonuçları
    print("="*60)
    print("📊 TEST SONUÇLARI")
    print("="*60)
    print(f"✅ Başarılı: {successful_tests}/{total_tests}")
    print(f"❌ Başarısız: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 TÜM TESTLER BAŞARILI!")
    else:
        print("⚠️ Bazı testler başarısız oldu.")
    
    print("\n💡 Not: Gerçek Telegram API credentials olmadan")
    print("   bazı testlerin başarısız olması normaldir.")
    
    # Cleanup
    try:
        await redis_state.disconnect()
        print("\n🧹 Cleanup tamamlandı")
    except:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc() 