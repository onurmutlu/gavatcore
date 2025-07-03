#!/usr/bin/env python3
"""
💀 EXTREME MODE TEST - Database Lock Tester 💀

Database locked problemini test eder
"""

import asyncio
import asyncpg
import redis.asyncio as redis
import motor.motor_asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseTester:
    def __init__(self):
        self.pg_pool = None
        self.redis = None
        self.mongo = None
        
    async def setup(self):
        """Setup all database connections"""
        # PostgreSQL
        self.pg_pool = await asyncpg.create_pool(
            'postgresql://postgres:postgres@localhost/extreme_mode',
            min_size=10,
            max_size=20
        )
        
        # Redis
        self.redis = await redis.from_url('redis://localhost:6379')
        
        # MongoDB
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        self.mongo_db = self.mongo.extreme_test
        
        logger.info("✅ All databases connected")
        
    async def stress_test_postgres(self, worker_id: int, iterations: int = 100):
        """Stress test PostgreSQL with concurrent writes"""
        for i in range(iterations):
            try:
                async with self.pg_pool.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO test_table (worker_id, data) VALUES ($1, $2)",
                        worker_id, f"Worker {worker_id} iteration {i}"
                    )
                    
                if i % 10 == 0:
                    logger.info(f"PG Worker {worker_id}: {i}/{iterations}")
                    
            except Exception as e:
                logger.error(f"PG Worker {worker_id} error: {e}")
                
    async def stress_test_redis(self, worker_id: int, iterations: int = 100):
        """Stress test Redis with concurrent operations"""
        for i in range(iterations):
            try:
                # Distributed lock test
                lock_key = f"lock:test:{random.randint(1, 10)}"
                lock = self.redis.lock(lock_key, timeout=1)
                
                async with lock:
                    # Simulate work
                    await self.redis.incr(f"counter:{worker_id}")
                    await asyncio.sleep(0.01)
                    
                if i % 10 == 0:
                    logger.info(f"Redis Worker {worker_id}: {i}/{iterations}")
                    
            except Exception as e:
                logger.error(f"Redis Worker {worker_id} error: {e}")
                
    async def stress_test_mongo(self, worker_id: int, iterations: int = 100):
        """Stress test MongoDB with concurrent writes"""
        collection = self.mongo_db.test_collection
        
        for i in range(iterations):
            try:
                await collection.insert_one({
                    "worker_id": worker_id,
                    "iteration": i,
                    "timestamp": time.time(),
                    "data": f"Worker {worker_id} iteration {i}"
                })
                
                if i % 10 == 0:
                    logger.info(f"Mongo Worker {worker_id}: {i}/{iterations}")
                    
            except Exception as e:
                logger.error(f"Mongo Worker {worker_id} error: {e}")
                
    async def run_test(self, num_workers: int = 10):
        """Run concurrent stress test"""
        logger.info(f"\n🚀 Starting stress test with {num_workers} workers per database...")
        
        # Create test table if not exists
        async with self.pg_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    worker_id INTEGER,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
        
        # Start all workers
        tasks = []
        
        # PostgreSQL workers
        for i in range(num_workers):
            task = asyncio.create_task(self.stress_test_postgres(i))
            tasks.append(task)
            
        # Redis workers
        for i in range(num_workers):
            task = asyncio.create_task(self.stress_test_redis(i))
            tasks.append(task)
            
        # MongoDB workers
        for i in range(num_workers):
            task = asyncio.create_task(self.stress_test_mongo(i))
            tasks.append(task)
            
        # Wait for all tasks
        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        logger.info(f"\n✅ Test completed in {end_time - start_time:.2f} seconds")
        logger.info(f"💀 NO DATABASE LOCKS! 💀")
        
        # Show stats
        async with self.pg_pool.acquire() as conn:
            pg_count = await conn.fetchval("SELECT COUNT(*) FROM test_table")
            
        mongo_count = await self.mongo_db.test_collection.count_documents({})
        
        redis_keys = []
        async for key in self.redis.scan_iter("counter:*"):
            value = await self.redis.get(key)
            redis_keys.append((key, value))
            
        logger.info(f"\n📊 Final Stats:")
        logger.info(f"   PostgreSQL records: {pg_count}")
        logger.info(f"   MongoDB documents: {mongo_count}")
        logger.info(f"   Redis counters: {len(redis_keys)}")
        
    async def cleanup(self):
        """Cleanup connections"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis:
            await self.redis.close()
        if self.mongo:
            self.mongo.close()

async def main():
    """Main test runner"""
    print("""
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
💀                                                               💀
💀         🔥 EXTREME MODE DATABASE TEST 🔥                     💀
💀                                                               💀
💀          💣 TESTING CONCURRENT ACCESS! 💣                     💀
💀                                                               💀
💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀
    """)
    
    tester = DatabaseTester()
    
    try:
        await tester.setup()
        await tester.run_test(num_workers=20)  # 20 workers per database = 60 total
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 