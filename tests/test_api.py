#!/usr/bin/env python3
"""
🧪 XP Token API Test Suite 🧪

xp_token_api.py'nin tüm endpoint'lerini test eder
Production test data ile realistic scenarios
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:5051"
TEST_USER_ID = "999888777"  # Test user

def print_header(title):
    """Test section header"""
    print("\n" + "🎯" + "="*50 + "🎯")
    print(f"🧪 {title}")
    print("🎯" + "="*50 + "🎯")

def print_result(endpoint, response, expected_success=True):
    """Print test result"""
    status = "✅" if response.status_code == 200 else "❌"
    print(f"{status} {endpoint} -> {response.status_code}")
    
    try:
        data = response.json()
        if data.get('success') == expected_success:
            print(f"   📊 Response: {data.get('message', 'OK')}")
            if 'data' in data:
                print(f"   📈 Data: {json.dumps(data['data'], indent=2)[:200]}...")
        else:
            print(f"   ❌ Unexpected success state: {data}")
    except:
        print(f"   ⚠️ Non-JSON response: {response.text[:100]}")
    
    print()

def test_health_check():
    """Test basic health check"""
    print_header("Health Check")
    
    response = requests.get(f"{API_BASE}/health")
    print_result("GET /health", response)

def test_api_docs():
    """Test API documentation"""
    print_header("API Documentation")
    
    response = requests.get(f"{API_BASE}/api/docs")
    print_result("GET /api/docs", response)

def test_award_xp():
    """Test XP awarding"""
    print_header("XP Award System")
    
    # Award start command XP
    payload = {
        "action": "start_command",
        "bonus_multiplier": 1.0
    }
    response = requests.post(f"{API_BASE}/api/award/{TEST_USER_ID}", json=payload)
    print_result(f"POST /api/award/{TEST_USER_ID} (start_command)", response)
    
    # Award DM reply XP
    payload = {
        "action": "dm_reply",
        "bonus_multiplier": 1.5  # VIP bonus
    }
    response = requests.post(f"{API_BASE}/api/award/{TEST_USER_ID}", json=payload)
    print_result(f"POST /api/award/{TEST_USER_ID} (dm_reply with bonus)", response)
    
    # Award daily bonus
    payload = {
        "action": "daily_bonus"
    }
    response = requests.post(f"{API_BASE}/api/award/{TEST_USER_ID}", json=payload)
    print_result(f"POST /api/award/{TEST_USER_ID} (daily_bonus)", response)

def test_user_stats():
    """Test user statistics"""
    print_header("User Statistics")
    
    response = requests.get(f"{API_BASE}/api/stats/{TEST_USER_ID}")
    print_result(f"GET /api/stats/{TEST_USER_ID}", response)
    
    # Extract balance for spending tests
    try:
        data = response.json()
        if data.get('success'):
            balance = data['data']['token_balance']
            print(f"💰 Current balance: {balance} tokens")
            return balance
    except:
        pass
    
    return 0

def test_token_spending(current_balance):
    """Test token spending"""
    print_header("Token Spending")
    
    if current_balance >= 10:
        # Spend on content
        payload = {
            "service": "content",
            "content_id": "test_premium_video_123"
        }
        response = requests.post(f"{API_BASE}/api/spend/{TEST_USER_ID}", json=payload)
        print_result(f"POST /api/spend/{TEST_USER_ID} (content)", response)
        
        if current_balance >= 30:  # If we have enough for VIP
            # Spend on VIP
            payload = {
                "service": "vip"
            }
            response = requests.post(f"{API_BASE}/api/spend/{TEST_USER_ID}", json=payload)
            print_result(f"POST /api/spend/{TEST_USER_ID} (vip)", response)
    
    else:
        print("⚠️ Insufficient balance for spending tests")
        
        # Test insufficient balance error
        payload = {
            "service": "nft"  # 50 tokens
        }
        response = requests.post(f"{API_BASE}/api/spend/{TEST_USER_ID}", json=payload)
        print_result(f"POST /api/spend/{TEST_USER_ID} (insufficient balance)", response, expected_success=False)

def test_system_status():
    """Test system status"""
    print_header("System Status")
    
    response = requests.get(f"{API_BASE}/api/system/status")
    print_result("GET /api/system/status", response)

def test_recent_logs():
    """Test recent logs"""
    print_header("Recent Transaction Logs")
    
    response = requests.get(f"{API_BASE}/api/logs/recent?limit=5")
    print_result("GET /api/logs/recent", response)

def test_campaign_stats():
    """Test campaign statistics"""
    print_header("VIP Campaign Stats")
    
    response = requests.get(f"{API_BASE}/api/campaign/stats")
    print_result("GET /api/campaign/stats", response)

def test_leaderboard():
    """Test leaderboard"""
    print_header("Token Leaderboard")
    
    response = requests.get(f"{API_BASE}/api/leaderboard?limit=5")
    print_result("GET /api/leaderboard", response)

def test_error_handling():
    """Test error cases"""
    print_header("Error Handling")
    
    # Invalid user ID
    response = requests.get(f"{API_BASE}/api/stats/invalid_user")
    print_result("GET /api/stats/invalid_user", response, expected_success=False)
    
    # Missing service in spend
    response = requests.post(f"{API_BASE}/api/spend/{TEST_USER_ID}", json={})
    print_result("POST /api/spend (missing service)", response, expected_success=False)
    
    # Invalid action in award
    payload = {"action": "invalid_action"}
    response = requests.post(f"{API_BASE}/api/award/{TEST_USER_ID}", json=payload)
    print_result("POST /api/award (invalid action)", response, expected_success=False)

def test_comprehensive_user_flow():
    """Test complete user journey"""
    print_header("Comprehensive User Flow Test")
    
    # Create a new test user
    flow_user = "flow_test_user_123"
    print(f"🎮 Testing complete flow for user: {flow_user}")
    
    # 1. Check initial stats (should be empty)
    response = requests.get(f"{API_BASE}/api/stats/{flow_user}")
    print_result("1. Initial stats check", response)
    
    # 2. Award start command
    payload = {"action": "start_command"}
    response = requests.post(f"{API_BASE}/api/award/{flow_user}", json=payload)
    print_result("2. Start command XP", response)
    
    # 3. Award first DM
    payload = {"action": "first_dm"}
    response = requests.post(f"{API_BASE}/api/award/{flow_user}", json=payload)
    print_result("3. First DM XP", response)
    
    # 4. Award group mention
    payload = {"action": "group_mention"}
    response = requests.post(f"{API_BASE}/api/award/{flow_user}", json=payload)
    print_result("4. Group mention XP", response)
    
    # 5. Check updated stats
    response = requests.get(f"{API_BASE}/api/stats/{flow_user}")
    print_result("5. Updated stats", response)
    
    # 6. Spend on content
    payload = {"service": "content", "content_id": "flow_test_video"}
    response = requests.post(f"{API_BASE}/api/spend/{flow_user}", json=payload)
    print_result("6. Content purchase", response)
    
    # 7. Final stats
    response = requests.get(f"{API_BASE}/api/stats/{flow_user}")
    print_result("7. Final stats", response)

def main():
    """Main test runner"""
    print("🚀" + "="*60 + "🚀")
    print("🧪 XP Token API Test Suite")
    print("💰 OnlyVips v6.0 Token Economy API Testing")
    print("🌐 Target: http://localhost:5051")
    print("🚀" + "="*60 + "🚀")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running!")
        else:
            print("❌ API health check failed!")
            return
    except:
        print("❌ Cannot connect to API. Is xp_token_api.py running?")
        print("💡 Start with: python3 xp_token_api.py")
        return
    
    # Run test suite
    start_time = time.time()
    
    test_health_check()
    test_api_docs()
    test_award_xp()
    balance = test_user_stats()
    test_token_spending(balance)
    test_system_status()
    test_recent_logs()
    test_campaign_stats()
    test_leaderboard()
    test_error_handling()
    test_comprehensive_user_flow()
    
    # Summary
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    
    print("\n" + "🎊" + "="*50 + "🎊")
    print("🎉 Test Suite Completed!")
    print(f"⏱️ Duration: {duration} seconds")
    print(f"📊 Test User: {TEST_USER_ID}")
    print("💡 Check API logs for detailed information")
    print("🎊" + "="*50 + "🎊")
    
    # Final API status
    try:
        response = requests.get(f"{API_BASE}/api/system/status")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"\n📈 Final System Stats:")
                print(f"   👥 Total Users: {stats.get('total_users', 0)}")
                print(f"   💰 Total Tokens: {stats.get('total_tokens', 0)}")
                print(f"   📊 Total Transactions: {stats.get('total_transactions', 0)}")
                print(f"   🔄 API Requests: {stats.get('api_requests', 0)}")
    except:
        pass

if __name__ == "__main__":
    main() 