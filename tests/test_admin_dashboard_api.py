#!/usr/bin/env python3
"""
🧪 Admin Dashboard API Test Script
=================================

Test script for the optimized admin dashboard API.
Tests performance, caching, and database optimizations.

@version: 1.0.0
@created: 2025-01-30
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Any
import structlog

logger = structlog.get_logger("admin_dashboard_test")

class AdminDashboardAPITester:
    """
    🧪 Comprehensive API tester for admin dashboard
    """
    
    def __init__(self, base_url: str = "http://localhost:5055"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
    
    async def initialize(self):
        """Initialize HTTP session"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        logger.info("✅ HTTP session initialized")
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
        logger.info("🧹 HTTP session cleaned up")
    
    async def test_endpoint(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Test a single endpoint and measure performance"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, **kwargs) as response:
                    response_time = time.time() - start_time
                    
                    # Get response data
                    if response.content_type == 'application/json':
                        data = await response.json()
                    else:
                        data = await response.text()
                    
                    # Get performance headers
                    api_response_time = response.headers.get("X-Response-Time", "N/A")
                    memory_used = response.headers.get("X-Memory-Used", "N/A")
                    
                    result = {
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status,
                        "response_time": response_time,
                        "api_response_time": api_response_time,
                        "memory_used": memory_used,
                        "content_length": len(str(data)),
                        "success": response.status < 400,
                        "data": data if response.status < 400 else None,
                        "error": data if response.status >= 400 else None
                    }
                    
            elif method.upper() == "DELETE":
                async with self.session.delete(url, **kwargs) as response:
                    response_time = time.time() - start_time
                    
                    if response.content_type == 'application/json':
                        data = await response.json()
                    else:
                        data = await response.text()
                    
                    result = {
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status < 400,
                        "data": data if response.status < 400 else None,
                        "error": data if response.status >= 400 else None
                    }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
            self.test_results.append(error_result)
            return error_result
    
    async def test_dashboard_stats(self) -> Dict[str, Any]:
        """Test dashboard stats endpoint"""
        print("\n📊 Testing Dashboard Stats Endpoint...")
        
        # Test normal request
        result1 = await self.test_endpoint("/api/admin/dashboard/stats")
        if result1["success"]:
            print(f"✅ Dashboard stats: {result1['response_time']:.4f}s")
            print(f"   Total users: {result1['data'].get('total_users', 'N/A')}")
            print(f"   Cache hit rate: {result1['data'].get('cache_hit_rate', 'N/A'):.1f}%")
            print(f"   System health: {result1['data'].get('system_health', 'N/A')}")
        else:
            print(f"❌ Dashboard stats failed: {result1.get('error', 'Unknown error')}")
        
        return {"normal": result1}
    
    async def test_system_health(self) -> Dict[str, Any]:
        """Test system health endpoint"""
        print("\n🏥 Testing System Health Endpoint...")
        
        result = await self.test_endpoint("/api/admin/system/health")
        if result["success"]:
            print(f"✅ System health: {result['response_time']:.4f}s")
            data = result['data']
            print(f"   Overall status: {data.get('overall_status', 'N/A')}")
            print(f"   Health score: {data.get('health_score', 'N/A')}")
        else:
            print(f"❌ System health failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive API test suite"""
        print("🧪 ADMIN DASHBOARD API COMPREHENSIVE TEST")
        print("=" * 50)
        
        await self.initialize()
        
        try:
            # Test individual endpoints
            dashboard_results = await self.test_dashboard_stats()
            health_results = await self.test_system_health()
            
            # Calculate overall performance metrics
            all_successful_tests = [r for r in self.test_results if r["success"]]
            all_failed_tests = [r for r in self.test_results if not r["success"]]
            
            if all_successful_tests:
                avg_response_time = sum(r["response_time"] for r in all_successful_tests) / len(all_successful_tests)
                min_response_time = min(r["response_time"] for r in all_successful_tests)
                max_response_time = max(r["response_time"] for r in all_successful_tests)
            else:
                avg_response_time = min_response_time = max_response_time = 0
            
            # Performance summary
            print(f"\n📊 PERFORMANCE SUMMARY")
            print("=" * 30)
            print(f"Total tests executed: {len(self.test_results)}")
            print(f"Successful tests: {len(all_successful_tests)}")
            print(f"Failed tests: {len(all_failed_tests)}")
            print(f"Success rate: {len(all_successful_tests) / len(self.test_results) * 100:.1f}%")
            print()
            print(f"Response time metrics:")
            print(f"   Average: {avg_response_time:.4f}s")
            print(f"   Minimum: {min_response_time:.4f}s")
            print(f"   Maximum: {max_response_time:.4f}s")
            
            return {
                "dashboard": dashboard_results,
                "health": health_results,
                "summary": {
                    "total_tests": len(self.test_results),
                    "successful_tests": len(all_successful_tests),
                    "failed_tests": len(all_failed_tests),
                    "success_rate": len(all_successful_tests) / len(self.test_results) * 100,
                    "avg_response_time": avg_response_time,
                    "min_response_time": min_response_time,
                    "max_response_time": max_response_time
                }
            }
            
        finally:
            await self.cleanup()

async def main():
    """Main test function"""
    tester = AdminDashboardAPITester()
    
    try:
        results = await tester.run_comprehensive_test()
        
        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"admin_dashboard_api_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n📄 Test results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n❌ Test execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())