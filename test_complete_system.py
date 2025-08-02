#!/usr/bin/env python3
"""
Comprehensive system test for GavatCore Multi-Bot Authentication
"""

import requests
import json
import time
import subprocess
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.api_url = "http://localhost:5050"
        self.flutter_url = "http://localhost:3000"
        self.results = []
    
    def log_result(self, test_name, success, message):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_api_connectivity(self):
        """Test basic API server connectivity"""
        try:
            response = requests.get(f"{self.api_url}/api/system/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_result("API Connectivity", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_result("API Connectivity", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("API Connectivity", False, str(e))
            return False
    
    def test_bot_list_endpoint(self):
        """Test bot list endpoint"""
        try:
            response = requests.get(f"{self.api_url}/api/telegram/bots", timeout=5)
            if response.status_code == 200:
                data = response.json()
                bots = data.get('bots', [])
                expected_bots = ['lara', 'babagavat', 'geisha']
                found_bots = [bot['name'] for bot in bots]
                
                if all(bot in found_bots for bot in expected_bots):
                    self.log_result("Bot List Endpoint", True, f"Found all bots: {found_bots}")
                    return True
                else:
                    self.log_result("Bot List Endpoint", False, f"Missing bots. Found: {found_bots}")
                    return False
            else:
                self.log_result("Bot List Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Bot List Endpoint", False, str(e))
            return False
    
    def test_send_code_endpoint(self):
        """Test send code endpoint for each bot"""
        success_count = 0
        for bot_name in ['lara', 'babagavat', 'geisha']:
            try:
                payload = {"bot_name": bot_name}
                response = requests.post(
                    f"{self.api_url}/api/telegram/send-code",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('bot_name') == bot_name:
                        self.log_result(f"Send Code ({bot_name})", True, f"Phone: {data.get('phone')}")
                        success_count += 1
                    else:
                        self.log_result(f"Send Code ({bot_name})", False, f"Invalid response: {data}")
                else:
                    self.log_result(f"Send Code ({bot_name})", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result(f"Send Code ({bot_name})", False, str(e))
        
        return success_count == 3
    
    def test_flutter_accessibility(self):
        """Test Flutter web app accessibility"""
        try:
            response = requests.get(self.flutter_url, timeout=10)
            if response.status_code == 200:
                if "GavatCore" in response.text or "flutter" in response.text.lower():
                    self.log_result("Flutter Accessibility", True, "Web app is accessible")
                    return True
                else:
                    self.log_result("Flutter Accessibility", False, "Unexpected content")
                    return False
            else:
                self.log_result("Flutter Accessibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Flutter Accessibility", False, str(e))
            return False
    
    def test_cors_headers(self):
        """Test CORS headers for web requests"""
        try:
            response = requests.options(f"{self.api_url}/api/telegram/send-code")
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header == '*':
                self.log_result("CORS Headers", True, "CORS properly configured")
                return True
            else:
                self.log_result("CORS Headers", False, f"CORS header: {cors_header}")
                return False
        except Exception as e:
            self.log_result("CORS Headers", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting GavatCore Multi-Bot System Tests")
        print("=" * 50)
        
        # Test API
        api_ok = self.test_api_connectivity()
        if api_ok:
            self.test_bot_list_endpoint()
            self.test_send_code_endpoint() 
            self.test_cors_headers()
        
        # Test Flutter
        self.test_flutter_accessibility()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is fully operational.")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed. System needs attention.")
            print("\nFailed tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
            return False

def main():
    tester = SystemTester()
    
    print("🔍 Checking if services are running...")
    
    # Quick check if services are up
    api_running = False
    flutter_running = False
    
    try:
        requests.get("http://localhost:5050/api/system/status", timeout=2)
        api_running = True
        print("✅ API Server is running on port 5050")
    except:
        print("❌ API Server is not running on port 5050")
    
    try:
        requests.get("http://localhost:3000", timeout=2)
        flutter_running = True
        print("✅ Flutter App is running on port 3000")
    except:
        print("❌ Flutter App is not running on port 3000")
    
    if not api_running:
        print("\n⚠️  API Server is not running. Please start it with:")
        print("   python3 apis/telegram_auth_api_minimal.py")
        return False
    
    if not flutter_running:
        print("\n⚠️  Flutter Web App is not running. Please start it with:")
        print("   cd gavatcore_panel && flutter run -d chrome --web-port 3000")
        return False
    
    print("\n🧪 Running comprehensive system tests...")
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)