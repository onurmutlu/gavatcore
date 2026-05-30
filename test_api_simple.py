#!/usr/bin/env python3
"""
Simple test script to debug the API server issue
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5050"
    
    print("Testing API server connectivity...")
    
    # Test 1: System status
    try:
        response = requests.get(f"{base_url}/api/system/status", timeout=5)
        print(f"✅ System status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ System status failed: {e}")
    
    # Test 2: Available bots
    try:
        response = requests.get(f"{base_url}/api/telegram/bots", timeout=5)
        print(f"✅ Available bots: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Bots: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ Available bots failed: {e}")
    
    # Test 3: Send code
    try:
        payload = {"bot_name": "lara"}
        response = requests.post(
            f"{base_url}/api/telegram/send-code",
            json=payload,
            timeout=10
        )
        print(f"✅ Send code: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Send code failed: {e}")

if __name__ == "__main__":
    test_api()