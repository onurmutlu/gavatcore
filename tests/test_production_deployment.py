#!/usr/bin/env python3
"""
🧪 GAVATCore Production Deployment Test Suite
Kapsamlı deployment testleri ve health check'ler

Usage: python3 test_production_deployment.py --environment production
"""

import asyncio
import aiohttp
import pytest
import time
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Test configuration."""
    environment: str
    base_url: str
    admin_url: str
    timeout: int = 30
    retry_count: int = 3
    load_test_duration: int = 60

@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    passed: bool
    duration: float
    message: str
    details: Optional[Dict] = None

class ProductionDeploymentTester:
    """
    🧪 Production deployment test suite
    
    Comprehensive testing for GAVATCore production deployment
    including health checks, performance tests, and integration tests.
    """
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def run_test(self, test_name: str, test_func) -> TestResult:
        """
        Run a single test with error handling and timing.
        
        Args:
            test_name: Name of the test
            test_func: Async test function to run
            
        Returns:
            TestResult object with test outcome
        """
        logger.info(f"🧪 Running test: {test_name}")
        start_time = time.time()
        
        try:
            result = await test_func()
            duration = time.time() - start_time
            
            if result.get('passed', False):
                test_result = TestResult(
                    test_name=test_name,
                    passed=True,
                    duration=duration,
                    message=result.get('message', 'Test passed'),
                    details=result.get('details')
                )
                logger.info(f"✅ {test_name} passed in {duration:.2f}s")
            else:
                test_result = TestResult(
                    test_name=test_name,
                    passed=False,
                    duration=duration,
                    message=result.get('message', 'Test failed'),
                    details=result.get('details')
                )
                logger.error(f"❌ {test_name} failed: {result.get('message')}")
                
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                message=f"Test exception: {str(e)}",
                details={'exception': str(e)}
            )
            logger.error(f"💥 {test_name} crashed: {str(e)}")
        
        self.results.append(test_result)
        return test_result
    
    async def test_health_endpoints(self) -> Dict:
        """Test application health endpoints."""
        health_endpoints = [
            ('Main API Health', f"{self.config.base_url}/api/system/status"),
            ('Admin API Health', f"{self.config.admin_url}/api/admin/system/health"),
            ('Main App Root', f"{self.config.base_url}/"),
        ]
        
        all_passed = True
        details = {}
        
        for name, url in health_endpoints:
            try:
                async with self.session.get(url) as response:
                    status_code = response.status
                    response_text = await response.text()
                    
                    if status_code == 200:
                        details[name] = {
                            'status': 'healthy',
                            'status_code': status_code,
                            'response_time': response.headers.get('x-response-time')
                        }
                        logger.info(f"✅ {name}: Healthy ({status_code})")
                    else:
                        details[name] = {
                            'status': 'unhealthy',
                            'status_code': status_code,
                            'response': response_text[:200]
                        }
                        all_passed = False
                        logger.error(f"❌ {name}: Unhealthy ({status_code})")
                        
            except Exception as e:
                details[name] = {
                    'status': 'error',
                    'error': str(e)
                }
                all_passed = False
                logger.error(f"💥 {name}: Error - {str(e)}")
        
        return {
            'passed': all_passed,
            'message': f"Health check results: {len([d for d in details.values() if d.get('status') == 'healthy'])}/{len(health_endpoints)} passed",
            'details': details
        }
    
    async def test_api_endpoints(self) -> Dict:
        """Test critical API endpoints."""
        api_tests = [
            ('System Status', 'GET', f"{self.config.base_url}/api/system/status"),
            ('Dashboard Stats', 'GET', f"{self.config.admin_url}/api/admin/dashboard/stats"),
            ('System Health', 'GET', f"{self.config.admin_url}/api/admin/system/health"),
        ]
        
        all_passed = True
        details = {}
        
        for name, method, url in api_tests:
            try:
                async with self.session.request(method, url) as response:
                    status_code = response.status
                    response_data = await response.json()
                    
                    if status_code == 200:
                        details[name] = {
                            'status': 'success',
                            'status_code': status_code,
                            'response_keys': list(response_data.keys()) if isinstance(response_data, dict) else None
                        }
                        logger.info(f"✅ {name}: API working ({status_code})")
                    else:
                        details[name] = {
                            'status': 'failed',
                            'status_code': status_code
                        }
                        all_passed = False
                        logger.error(f"❌ {name}: API failed ({status_code})")
                        
            except Exception as e:
                details[name] = {
                    'status': 'error',
                    'error': str(e)
                }
                all_passed = False
                logger.error(f"💥 {name}: Error - {str(e)}")
        
        return {
            'passed': all_passed,
            'message': f"API tests: {len([d for d in details.values() if d.get('status') == 'success'])}/{len(api_tests)} passed",
            'details': details
        }
    
    async def test_performance(self) -> Dict:
        """Test application performance."""
        performance_urls = [
            f"{self.config.base_url}/api/system/status",
            f"{self.config.admin_url}/api/admin/dashboard/stats"
        ]
        
        all_passed = True
        details = {}
        response_times = []
        
        # Test response times
        for url in performance_urls:
            times = []
            for i in range(10):  # 10 requests per endpoint
                try:
                    start = time.time()
                    async with self.session.get(url) as response:
                        await response.read()
                        duration = (time.time() - start) * 1000  # Convert to milliseconds
                        times.append(duration)
                        response_times.append(duration)
                except Exception as e:
                    logger.error(f"Performance test error: {e}")
                    all_passed = False
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                details[url] = {
                    'average_ms': round(avg_time, 2),
                    'max_ms': round(max_time, 2),
                    'min_ms': round(min_time, 2),
                    'requests': len(times)
                }
                
                # Performance thresholds
                if avg_time > 1000:  # > 1 second average
                    all_passed = False
                    logger.warning(f"⚠️ Slow response: {url} avg {avg_time:.2f}ms")
                else:
                    logger.info(f"✅ Good performance: {url} avg {avg_time:.2f}ms")
        
        # Overall performance metrics
        if response_times:
            overall_avg = sum(response_times) / len(response_times)
            details['overall'] = {
                'average_response_time_ms': round(overall_avg, 2),
                'total_requests': len(response_times),
                'performance_grade': 'good' if overall_avg < 500 else 'acceptable' if overall_avg < 1000 else 'poor'
            }
        
        return {
            'passed': all_passed,
            'message': f"Performance test completed. Average response time: {overall_avg:.2f}ms",
            'details': details
        }
    
    async def test_load_capacity(self) -> Dict:
        """Test application under load."""
        url = f"{self.config.base_url}/api/system/status"
        concurrent_requests = 50
        test_duration = 30  # seconds
        
        logger.info(f"🔥 Starting load test: {concurrent_requests} concurrent requests for {test_duration}s")
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        start_time = time.time()
        
        async def make_request(session):
            nonlocal successful_requests, failed_requests, response_times
            try:
                request_start = time.time()
                async with session.get(url) as response:
                    await response.read()
                    duration = (time.time() - request_start) * 1000
                    response_times.append(duration)
                    if response.status == 200:
                        successful_requests += 1
                    else:
                        failed_requests += 1
            except Exception:
                failed_requests += 1
        
        # Run load test
        tasks = []
        while time.time() - start_time < test_duration:
            # Create batch of concurrent requests
            batch_tasks = [
                make_request(self.session) 
                for _ in range(min(concurrent_requests, 100))
            ]
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            await asyncio.sleep(0.1)  # Small delay between batches
        
        total_requests = successful_requests + failed_requests
        success_rate = (successful_requests / max(total_requests, 1)) * 100
        
        details = {
            'duration_seconds': test_duration,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate_percent': round(success_rate, 2),
            'requests_per_second': round(total_requests / test_duration, 2),
            'average_response_time_ms': round(sum(response_times) / max(len(response_times), 1), 2),
            'max_response_time_ms': round(max(response_times), 2) if response_times else 0
        }
        
        passed = success_rate >= 95  # 95% success rate threshold
        
        logger.info(f"📊 Load test results: {success_rate:.1f}% success rate, {details['requests_per_second']:.1f} req/s")
        
        return {
            'passed': passed,
            'message': f"Load test: {success_rate:.1f}% success rate with {details['requests_per_second']:.1f} requests/second",
            'details': details
        }
    
    async def test_database_connectivity(self) -> Dict:
        """Test database connectivity through API."""
        try:
            # Test database through dashboard stats endpoint
            async with self.session.get(f"{self.config.admin_url}/api/admin/dashboard/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if stats contain database-derived data
                    has_user_count = 'total_users' in data
                    has_message_count = 'total_messages' in data
                    
                    details = {
                        'database_accessible': True,
                        'stats_available': has_user_count and has_message_count,
                        'response_data_keys': list(data.keys())
                    }
                    
                    passed = has_user_count or has_message_count
                    message = "Database connectivity verified through API"
                    
                else:
                    details = {'database_accessible': False, 'status_code': response.status}
                    passed = False
                    message = f"Database API returned status {response.status}"
                    
        except Exception as e:
            details = {'database_accessible': False, 'error': str(e)}
            passed = False
            message = f"Database connectivity test failed: {str(e)}"
        
        return {
            'passed': passed,
            'message': message,
            'details': details
        }
    
    async def test_security_headers(self) -> Dict:
        """Test security headers."""
        security_headers = [
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection',
            'strict-transport-security'
        ]
        
        try:
            async with self.session.get(self.config.base_url) as response:
                headers = {k.lower(): v for k, v in response.headers.items()}
                
                present_headers = []
                missing_headers = []
                
                for header in security_headers:
                    if header in headers:
                        present_headers.append(header)
                    else:
                        missing_headers.append(header)
                
                details = {
                    'present_headers': present_headers,
                    'missing_headers': missing_headers,
                    'security_score': len(present_headers) / len(security_headers) * 100
                }
                
                passed = len(missing_headers) <= 1  # Allow 1 missing header
                message = f"Security headers: {len(present_headers)}/{len(security_headers)} present"
                
        except Exception as e:
            details = {'error': str(e)}
            passed = False
            message = f"Security headers test failed: {str(e)}"
        
        return {
            'passed': passed,
            'message': message,
            'details': details
        }
    
    async def run_all_tests(self) -> Dict:
        """Run all deployment tests."""
        logger.info("🚀 Starting GAVATCore Production Deployment Tests")
        start_time = time.time()
        
        # Define test suite
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("API Endpoints", self.test_api_endpoints),
            ("Performance", self.test_performance),
            ("Database Connectivity", self.test_database_connectivity),
            ("Security Headers", self.test_security_headers),
            ("Load Capacity", self.test_load_capacity),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
        
        # Calculate overall results
        total_duration = time.time() - start_time
        passed_tests = len([r for r in self.results if r.passed])
        total_tests = len(self.results)
        success_rate = (passed_tests / total_tests) * 100
        
        overall_result = {
            'environment': self.config.environment,
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': round(success_rate, 2),
            'total_duration': round(total_duration, 2),
            'overall_passed': success_rate >= 80,  # 80% pass rate threshold
            'test_results': [
                {
                    'test_name': r.test_name,
                    'passed': r.passed,
                    'duration': round(r.duration, 2),
                    'message': r.message,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        return overall_result
    
    def generate_report(self, results: Dict) -> str:
        """Generate human-readable test report."""
        report = []
        report.append("=" * 60)
        report.append("🧪 GAVATCore Production Deployment Test Report")
        report.append("=" * 60)
        report.append(f"Environment: {results['environment']}")
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Total Duration: {results['total_duration']}s")
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Tests: {results['total_tests']}")
        report.append(f"Passed: {results['passed_tests']}")
        report.append(f"Failed: {results['failed_tests']}")
        report.append(f"Success Rate: {results['success_rate']}%")
        report.append(f"Overall Status: {'✅ PASS' if results['overall_passed'] else '❌ FAIL'}")
        report.append("")
        
        # Individual test results
        report.append("🔍 TEST DETAILS")
        report.append("-" * 30)
        for test in results['test_results']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            report.append(f"{status} {test['test_name']} ({test['duration']}s)")
            report.append(f"    {test['message']}")
            if test['details'] and not test['passed']:
                report.append(f"    Details: {json.dumps(test['details'], indent=6)}")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)

def get_config_for_environment(environment: str) -> TestConfig:
    """Get test configuration for specific environment."""
    configs = {
        'local': TestConfig(
            environment='local',
            base_url='http://localhost:5050',
            admin_url='http://localhost:5055'
        ),
        'staging': TestConfig(
            environment='staging',
            base_url='https://staging.gavatcore.com',
            admin_url='https://admin-staging.gavatcore.com'
        ),
        'production': TestConfig(
            environment='production',
            base_url='https://gavatcore.com',
            admin_url='https://admin.gavatcore.com'
        )
    }
    
    return configs.get(environment, configs['local'])

async def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='GAVATCore Production Deployment Tests')
    parser.add_argument('--environment', '-e', 
                       choices=['local', 'staging', 'production'],
                       default='local',
                       help='Target environment to test')
    parser.add_argument('--output', '-o',
                       help='Output file for test results')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get configuration
    config = get_config_for_environment(args.environment)
    
    # Run tests
    async with ProductionDeploymentTester(config) as tester:
        results = await tester.run_all_tests()
        
        # Generate report
        report = tester.generate_report(results)
        print(report)
        
        # Save results if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📄 Test results saved to {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_passed'] else 1)

if __name__ == "__main__":
    asyncio.run(main()) 