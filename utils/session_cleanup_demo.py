#!/usr/bin/env python3
"""
🧹 GavatCore Session Cleanup Demo 🧹

Demo script that creates test sessions in Redis and demonstrates
the cleanup functionality with real data.

Features:
- Creates test sessions with various states
- Demonstrates cleanup process
- Shows MongoDB logging
- Performance metrics
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
import redis.asyncio as redis
from contact_utils import (
    cleanup_expired_sessions,
    quick_cleanup, 
    deep_cleanup,
    get_cleanup_statistics,
    run_session_cleanup
)

class SessionCleanupDemo:
    """🚀 Session Cleanup Demo Runner"""
    
    def __init__(self):
        self.redis_url = "redis://localhost:6379"
        self.redis_client = None
        
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            print("✅ Redis connection established")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
    
    async def create_test_sessions(self, count: int = 10) -> None:
        """Create test sessions with various states and ages"""
        
        print(f"🏗️ Creating {count} test sessions...")
        
        current_time = datetime.now()
        
        test_sessions = [
            # Recent active sessions (should be preserved)
            {
                "key": "gavatcore:contact_session:testbot1:111",
                "data": {
                    "user_id": 111,
                    "bot_username": "testbot1",
                    "status": "success",
                    "created_at": current_time.isoformat(),
                    "ttl": 3600
                },
                "ttl": 3600
            },
            {
                "key": "gavatcore:contact_session:testbot1:222", 
                "data": {
                    "user_id": 222,
                    "bot_username": "testbot1",
                    "status": "initiated",
                    "created_at": current_time.isoformat(),
                    "ttl": 3600
                },
                "ttl": 3600
            },
            
            # Old sessions (should be cleaned)
            {
                "key": "gavatcore:contact_session:testbot2:333",
                "data": {
                    "user_id": 333,
                    "bot_username": "testbot2", 
                    "status": "initiated",
                    "created_at": (current_time - timedelta(hours=25)).isoformat(),
                    "ttl": 3600
                },
                "ttl": 3600
            },
            {
                "key": "gavatcore:contact_session:testbot2:444",
                "data": {
                    "user_id": 444,
                    "bot_username": "testbot2",
                    "status": "failed", 
                    "created_at": (current_time - timedelta(hours=30)).isoformat(),
                    "ttl": 3600
                },
                "ttl": 3600
            },
            
            # Expired TTL sessions (should be cleaned)
            {
                "key": "gavatcore:contact_session:testbot3:555",
                "data": {
                    "user_id": 555,
                    "bot_username": "testbot3",
                    "status": "initiated",
                    "created_at": (current_time - timedelta(hours=5)).isoformat(),
                    "ttl": 1  # Very short TTL - will expire quickly
                },
                "ttl": 1  # 1 second TTL
            },
            {
                "key": "gavatcore:contact_session:testbot3:666",
                "data": {
                    "user_id": 666,
                    "bot_username": "testbot3",
                    "status": "initiated", 
                    "created_at": (current_time - timedelta(hours=2)).isoformat(),
                    "ttl": 1
                },
                "ttl": 1
            },
            
            # Failed status sessions (should be cleaned)
            {
                "key": "gavatcore:contact_session:testbot4:777",
                "data": {
                    "user_id": 777,
                    "bot_username": "testbot4",
                    "status": "failed",
                    "created_at": current_time.isoformat(), 
                    "ttl": 3600
                },
                "ttl": 3600
            },
            
            # Invalid JSON (should be cleaned)
            {
                "key": "gavatcore:contact_session:testbot5:888",
                "data": "invalid json data{{{",
                "ttl": 3600
            },
            
            # Very large session (memory test)
            {
                "key": "gavatcore:contact_session:testbot6:999",
                "data": {
                    "user_id": 999,
                    "bot_username": "testbot6",
                    "status": "initiated",
                    "created_at": (current_time - timedelta(hours=26)).isoformat(),
                    "ttl": 3600,
                    "large_data": "x" * 5000  # 5KB of data
                },
                "ttl": 3600
            }
        ]
        
        # Create sessions in Redis
        created_count = 0
        for session in test_sessions[:count]:
            try:
                if isinstance(session["data"], dict):
                    data_str = json.dumps(session["data"])
                else:
                    data_str = session["data"]
                
                # Set with TTL
                await self.redis_client.setex(
                    session["key"],
                    session["ttl"], 
                    data_str
                )
                created_count += 1
                
            except Exception as e:
                print(f"❌ Failed to create session {session['key']}: {e}")
        
        print(f"✅ Created {created_count}/{count} test sessions")
        
        # Wait for some TTL sessions to expire
        if count > 4:  # If we created TTL sessions
            print("⏰ Waiting 2 seconds for TTL sessions to expire...")
            await asyncio.sleep(2)
    
    async def show_current_sessions(self) -> None:
        """Display current sessions in Redis"""
        
        print("\n📋 Current sessions in Redis:")
        print("-" * 80)
        
        pattern = "gavatcore:contact_session:*"
        cursor = self.redis_client.scan_iter(match=pattern)
        
        session_count = 0
        async for key in cursor:
            try:
                data = await self.redis_client.get(key)
                ttl = await self.redis_client.ttl(key)
                
                if data:
                    try:
                        session_json = json.loads(data)
                        status = session_json.get("status", "unknown")
                        user_id = session_json.get("user_id", "unknown")
                        created = session_json.get("created_at", "unknown")
                        if created != "unknown":
                            created = created[:19]  # Trim milliseconds
                    except:
                        status = "invalid_json"
                        user_id = "unknown"
                        created = "unknown"
                    
                    print(f"🔑 {key}")
                    print(f"   👤 User: {user_id} | Status: {status} | TTL: {ttl}s | Created: {created}")
                    session_count += 1
                
            except Exception as e:
                print(f"❌ Error reading {key}: {e}")
        
        print(f"\n📊 Total sessions found: {session_count}")
    
    async def run_demo(self) -> None:
        """Run complete cleanup demo"""
        
        print("🔥 GavatCore Session Cleanup Demo 🔥")
        print("=" * 60)
        
        # Initialize
        if not await self.initialize():
            return
        
        try:
            # Step 1: Clean existing test sessions
            print("\n🧹 Step 1: Cleaning existing test sessions...")
            pattern = "gavatcore:contact_session:testbot*"
            cursor = self.redis_client.scan_iter(match=pattern)
            deleted = 0
            async for key in cursor:
                await self.redis_client.delete(key)
                deleted += 1
            print(f"🗑️ Deleted {deleted} existing test sessions")
            
            # Step 2: Create test data
            print("\n🏗️ Step 2: Creating test sessions...")
            await self.create_test_sessions(9)  # Create 9 test sessions
            
            # Step 3: Show current state
            print("\n📋 Step 3: Current session state (before cleanup):")
            await self.show_current_sessions()
            
            # Step 4: Run cleanup
            print("\n🧹 Step 4: Running session cleanup...")
            print("-" * 60)
            
            start_time = time.time()
            
            # Run the actual cleanup
            result = await cleanup_expired_sessions(
                batch_size=5,
                max_age_hours=24
            )
            
            end_time = time.time()
            
            # Step 5: Show results
            print(f"\n🎉 Step 5: Cleanup Results")
            print("-" * 60)
            
            if result["success"]:
                print("✅ Cleanup completed successfully!")
                print(f"📊 Sessions found: {result['sessions_found']}")
                print(f"🗑️ Sessions deleted: {result['sessions_deleted']}")
                print(f"💾 Sessions preserved: {result['sessions_preserved']}")
                print(f"⚠️ Errors encountered: {result['errors_encountered']}")
                print(f"📦 Batches processed: {result['batch_count']}")
                print(f"⚡ Processing time: {result['processing_time_seconds']:.2f}s")
                print(f"🔗 Redis operations: {result['redis_operations']}")
                print(f"📄 MongoDB operations: {result['mongodb_operations']}")
                print(f"💾 Memory saved: {result['memory_saved_mb']:.3f} MB")
                print(f"📝 MongoDB log ID: {result.get('log_document_id', 'N/A')}")
                
                if result['sessions_found'] > 0:
                    efficiency = (result['sessions_deleted'] / result['sessions_found']) * 100
                    print(f"📈 Cleanup efficiency: {efficiency:.1f}%")
                
            else:
                print("❌ Cleanup failed!")
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            # Step 6: Show final state
            print("\n📋 Step 6: Final session state (after cleanup):")
            await self.show_current_sessions()
            
            # Step 7: Test quick functions
            print("\n🏃‍♂️ Step 7: Testing quick cleanup functions...")
            
            # Test quick_cleanup
            quick_result = await quick_cleanup(max_age_hours=1)
            print(f"⚡ Quick cleanup: {quick_result['sessions_deleted']} sessions deleted")
            
            # Test deep_cleanup  
            deep_result = await deep_cleanup(max_age_hours=1)
            print(f"🔍 Deep cleanup: {deep_result['sessions_deleted']} sessions deleted")
            
            print("\n" + "=" * 60)
            print("🎯 Demo completed successfully! 🎯")
            
        except Exception as e:
            print(f"💥 Demo failed: {e}")
            
        finally:
            if self.redis_client:
                await self.redis_client.close()
                print("🔌 Redis connection closed")


async def main():
    """Main demo runner"""
    demo = SessionCleanupDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main()) 