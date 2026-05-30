#!/usr/bin/env python3
"""
🧪 GAVATCORE SaaS API TESTS
Basic functionality tests
"""

import asyncio
import httpx
import json
from pathlib import Path


async def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing GavatCore SaaS API endpoints...")
        
        # Test health check
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data['status']} - {data['service']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test root endpoint
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint: {data['message']}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test pricing plans
        try:
            response = await client.get(f"{base_url}/api/payment/plans")
            if response.status_code == 200:
                data = response.json()
                plans = data['plans']
                print(f"✅ Pricing plans: {len(plans)} plans available")
                for plan_name, plan_data in plans.items():
                    print(f"   • {plan_data['name']}: {plan_data['price']} {plan_data['currency']}")
            else:
                print(f"❌ Pricing plans failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Pricing plans error: {e}")
        
        # Test auth endpoints
        endpoints = [
            "/api/auth/register",
            "/api/auth/login", 
            "/api/bots/",
            "/api/users/profile"
        ]
        
        for endpoint in endpoints:
            try:
                if "register" in endpoint or "login" in endpoint:
                    response = await client.post(f"{base_url}{endpoint}")
                else:
                    response = await client.get(f"{base_url}{endpoint}")
                
                if response.status_code in [200, 422]:  # 422 is expected for missing data
                    print(f"✅ {endpoint}: Endpoint accessible")
                else:
                    print(f"⚠️  {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Error {e}")


def test_imports():
    """Test Python imports"""
    print("🐍 Testing Python module imports...")
    
    try:
        from app.core.config import settings
        print(f"✅ Config loaded - Environment: {settings.ENVIRONMENT}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
    
    try:
        from app.core.exceptions import APIException, PaymentError
        print("✅ Exception classes imported")
    except Exception as e:
        print(f"❌ Exception import failed: {e}")
    
    try:
        from app.routes import auth, payment, bots, users
        print("✅ Route modules imported")
    except Exception as e:
        print(f"❌ Route import failed: {e}")


def test_environment():
    """Test environment setup"""
    print("⚙️ Testing environment setup...")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found")
    
    # Check directories
    dirs = ["sessions", "logs"]
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️  {dir_name}/ directory not found")
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created {dir_name}/ directory")


async def main():
    """Main test function"""
    print("🚀 GAVATCORE SaaS API TEST SUITE")
    print("=" * 50)
    
    # Test imports first
    test_imports()
    print()
    
    # Test environment
    test_environment()
    print()
    
    # Test API endpoints
    await test_api_endpoints()
    
    print("=" * 50)
    print("🎯 Test suite completed!")
    print("💡 If API tests failed, make sure the server is running:")
    print("   uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main()) 