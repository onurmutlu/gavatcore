#!/usr/bin/env python3
"""
🧪 GAVATCore Scalable System Test Suite
Enterprise-grade testing for async processing and load balancing

Tests:
- Async task processing
- Load balancing algorithms  
- Circuit breaker functionality
- Rate limiting
- Performance benchmarks
- Stress testing
"""

import asyncio
import aiohttp
import time
import json
import random
import uuid
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scalable_system_test")

@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    success: bool
    duration: float
    message: str
    data: Dict[str, Any] = None

class ScalableSystemTester:
    """
    🧪 Comprehensive tester for GAVATCore scalable system
    """
    
    def __init__(self, base_url: str = "http://localhost:6000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
        self.test_results: List[TestResult] = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_basic_connectivity(self) -> TestResult:
        """Test basic API connectivity."""
        start_time = time.time()
        test_name = "Basic Connectivity"
        
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    duration = time.time() - start_time
                    
                    return TestResult(
                        test_name=test_name,
                        success=True,
                        duration=duration,
                        message="API is accessible and responding",
                        data={"status_code": response.status, "service": data.get("service")}
                    )
                else:
                    duration = time.time() - start_time
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        message=f"Unexpected status code: {response.status}"
                    )
                    
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Connection failed: {str(e)}"
            )
    
    async def test_health_endpoint(self) -> TestResult:
        """Test health check endpoint."""
        start_time = time.time()
        test_name = "Health Check"
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                data = await response.json()
                duration = time.time() - start_time
                
                if response.status == 200 and data.get("status") in ["healthy", "degraded"]:
                    return TestResult(
                        test_name=test_name,
                        success=True,
                        duration=duration,
                        message=f"Health check passed: {data.get('status')}",
                        data=data
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        message=f"Health check failed: {data}"
                    )
                    
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Health check error: {str(e)}"
            )
    
    async def test_async_task_submission(self) -> TestResult:
        """Test async task submission and processing."""
        start_time = time.time()
        test_name = "Async Task Submission"
        
        try:
            # Submit a task
            task_payload = {
                "task_type": "data_analysis",
                "parameters": {"data_size": 100},
                "priority": 3,
                "async_mode": True
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/tasks",
                json=task_payload
            ) as response:
                
                if response.status != 200:
                    duration = time.time() - start_time
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        message=f"Task submission failed: {response.status}"
                    )
                
                data = await response.json()
                task_id = data.get("task_id")
                
                if not task_id:
                    duration = time.time() - start_time
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        message="No task ID returned"
                    )
                
                # Wait a bit and check task result
                await asyncio.sleep(3)
                
                async with self.session.get(
                    f"{self.base_url}/api/v1/tasks/{task_id}"
                ) as result_response:
                    
                    if result_response.status == 200:
                        result_data = await result_response.json()
                        duration = time.time() - start_time
                        
                        return TestResult(
                            test_name=test_name,
                            success=True,
                            duration=duration,
                            message=f"Task processed successfully: {result_data.get('status')}",
                            data={
                                "task_id": task_id,
                                "status": result_data.get("status"),
                                "execution_time": result_data.get("execution_time")
                            }
                        )
                    else:
                        duration = time.time() - start_time
                        return TestResult(
                            test_name=test_name,
                            success=False,
                            duration=duration,
                            message=f"Task result retrieval failed: {result_response.status}"
                        )
                        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Task submission error: {str(e)}"
            )
    
    async def test_load_balancer_endpoints(self) -> TestResult:
        """Test load balancer endpoint management."""
        start_time = time.time()
        test_name = "Load Balancer Endpoints"
        
        try:
            # Get current endpoints
            async with self.session.get(
                f"{self.base_url}/api/v1/load-balancer/endpoints"
            ) as response:
                
                if response.status != 200:
                    duration = time.time() - start_time
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        message=f"Failed to get endpoints: {response.status}"
                    )
                
                endpoints = await response.json()
                endpoint_count = len(endpoints)
                
                # Test adding an endpoint
                new_endpoint = {
                    "id": f"test-endpoint-{uuid.uuid4().hex[:8]}",
                    "host": "localhost",
                    "port": 8999,
                    "weight": 1,
                    "max_connections": 50
                }
                
                async with self.session.post(
                    f"{self.base_url}/api/v1/load-balancer/endpoints",
                    json=new_endpoint
                ) as add_response:
                    
                    if add_response.status == 200:
                        # Verify endpoint was added
                        async with self.session.get(
                            f"{self.base_url}/api/v1/load-balancer/endpoints"
                        ) as verify_response:
                            
                            if verify_response.status == 200:
                                updated_endpoints = await verify_response.json()
                                
                                if len(updated_endpoints) > endpoint_count:
                                    # Clean up - remove the test endpoint
                                    await self.session.delete(
                                        f"{self.base_url}/api/v1/load-balancer/endpoints/{new_endpoint['id']}"
                                    )
                                    
                                    duration = time.time() - start_time
                                    return TestResult(
                                        test_name=test_name,
                                        success=True,
                                        duration=duration,
                                        message="Load balancer endpoint management working",
                                        data={
                                            "initial_endpoints": endpoint_count,
                                            "after_add": len(updated_endpoints)
                                        }
                                    )
                
                duration = time.time() - start_time
                return TestResult(
                    test_name=test_name,
                    success=False,
                    duration=duration,
                    message="Load balancer endpoint management failed"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Load balancer test error: {str(e)}"
            )
    
    async def test_system_metrics(self) -> TestResult:
        """Test system metrics collection."""
        start_time = time.time()
        test_name = "System Metrics"
        
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    duration = time.time() - start_time
                    
                    required_metrics = ["uptime_seconds", "request_metrics", "timestamp"]
                    missing_metrics = [m for m in required_metrics if m not in data]
                    
                    if not missing_metrics:
                        return TestResult(
                            test_name=test_name,
                            success=True,
                            duration=duration,
                            message="System metrics available",
                            data={
                                "uptime": data.get("uptime_seconds"),
                                "total_requests": data.get("request_metrics", {}).get("total_requests", 0)
                            }
                        )
                    else:
                        return TestResult(
                            test_name=test_name,
                            success=False,
                            duration=duration,
                            message=f"Missing metrics: {missing_metrics}"
                        )
                else:
                    duration = time.time() - start_time
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration=duration,
                        message=f"Metrics endpoint failed: {response.status}"
                    )
                    
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Metrics test error: {str(e)}"
            )
    
    async def test_concurrent_requests(self, concurrent: int = 10) -> TestResult:
        """Test handling of concurrent requests."""
        start_time = time.time()
        test_name = f"Concurrent Requests ({concurrent})"
        
        try:
            async def make_request():
                async with self.session.get(f"{self.base_url}/health") as response:
                    return response.status == 200
            
            # Make concurrent requests
            tasks = [make_request() for _ in range(concurrent)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r is True)
            duration = time.time() - start_time
            
            if successful >= concurrent * 0.9:  # 90% success rate
                return TestResult(
                    test_name=test_name,
                    success=True,
                    duration=duration,
                    message=f"Handled {successful}/{concurrent} concurrent requests",
                    data={
                        "concurrent_requests": concurrent,
                        "successful": successful,
                        "success_rate": (successful / concurrent) * 100
                    }
                )
            else:
                return TestResult(
                    test_name=test_name,
                    success=False,
                    duration=duration,
                    message=f"Poor concurrent handling: {successful}/{concurrent} successful"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Concurrent test error: {str(e)}"
            )
    
    async def test_stress_test_endpoint(self) -> TestResult:
        """Test the stress test endpoint."""
        start_time = time.time()
        test_name = "Stress Test Endpoint"
        
        try:
            stress_params = {
                "concurrent_requests": 5,
                "duration_seconds": 10
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/system/stress-test",
                params=stress_params
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    stress_test_id = data.get("stress_test_id")
                    
                    if stress_test_id:
                        # Wait for stress test to complete
                        await asyncio.sleep(15)
                        
                        # Try to get stress test result
                        async with self.session.get(
                            f"{self.base_url}/api/v1/tasks/{stress_test_id}"
                        ) as result_response:
                            
                            duration = time.time() - start_time
                            
                            if result_response.status == 200:
                                result_data = await result_response.json()
                                
                                return TestResult(
                                    test_name=test_name,
                                    success=True,
                                    duration=duration,
                                    message="Stress test endpoint working",
                                    data={
                                        "stress_test_id": stress_test_id,
                                        "status": result_data.get("status")
                                    }
                                )
                
                duration = time.time() - start_time
                return TestResult(
                    test_name=test_name,
                    success=False,
                    duration=duration,
                    message=f"Stress test failed: {response.status}"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                message=f"Stress test error: {str(e)}"
            )
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        logger.info("🧪 Starting GAVATCore Scalable System Tests...")
        
        test_methods = [
            self.test_basic_connectivity,
            self.test_health_endpoint,
            self.test_system_metrics,
            self.test_async_task_submission,
            self.test_load_balancer_endpoints,
            lambda: self.test_concurrent_requests(10),
            lambda: self.test_concurrent_requests(25),
            self.test_stress_test_endpoint
        ]
        
        for test_method in test_methods:
            try:
                result = await test_method()
                self.test_results.append(result)
                
                status = "✅" if result.success else "❌"
                logger.info(f"{status} {result.test_name}: {result.message} ({result.duration:.2f}s)")
                
                # Small delay between tests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                error_result = TestResult(
                    test_name=getattr(test_method, '__name__', 'Unknown Test'),
                    success=False,
                    duration=0.0,
                    message=f"Test execution error: {str(e)}"
                )
                self.test_results.append(error_result)
                logger.error(f"❌ Test error: {str(e)}")
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        total_duration = sum(r.duration for r in self.test_results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_test_duration": total_duration / total_tests if total_tests > 0 else 0,
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "message": r.message,
                    "data": r.data
                }
                for r in self.test_results
            ]
        }
        
        logger.info(f"🏁 Tests completed: {passed_tests}/{total_tests} passed ({summary['success_rate']:.1f}%)")
        
        return summary

async def main():
    """Run the scalable system test suite."""
    print("🧪 GAVATCore Scalable System Test Suite")
    print("="*60)
    print("🔧 Testing enterprise async processing and load balancing")
    print("="*60)
    
    async with ScalableSystemTester() as tester:
        # Run all tests
        results = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "📊" + "="*50 + "📊")
        print("🧪 TEST SUMMARY")
        print("📊" + "="*50 + "📊")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Total Duration: {results['total_duration']:.2f}s")
        print(f"Average Test Duration: {results['average_test_duration']:.2f}s")
        
        # Print failed tests
        failed_tests = [r for r in results['results'] if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['message']}")
        
        # Save results to file
        with open(f"scalable_system_test_results_{int(time.time())}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Results saved to: scalable_system_test_results_{int(time.time())}.json")
        
        # Overall status
        if results['success_rate'] >= 80:
            print("\n🎉 SYSTEM STATUS: HEALTHY ✅")
            return 0
        else:
            print("\n⚠️ SYSTEM STATUS: DEGRADED ❌")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())