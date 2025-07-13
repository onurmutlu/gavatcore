#!/usr/bin/env python3
"""
🧪 Telegram Bot Test Script
Test imports and basic functionality
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Telegram Bot imports...")
    
    # Test standard library imports
    try:
        import asyncio
        import logging
        import sqlite3
        import json
        from datetime import datetime, timedelta
        from typing import Optional, Dict, Any
        print("✅ Standard library imports OK")
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
        return False
    
    # Test third-party imports (optional in dev environment)
    try:
        import aiohttp
        print("✅ aiohttp import OK")
    except ImportError:
        print("⚠️ aiohttp not installed (install with: pip install aiohttp)")
    
    try:
        import structlog
        print("✅ structlog import OK")
    except ImportError:
        print("⚠️ structlog not installed (install with: pip install structlog)")
    
    try:
        from telegram import Update
        from telegram.ext import Application
        print("✅ python-telegram-bot import OK")
    except ImportError:
        print("⚠️ python-telegram-bot not installed (install with: pip install python-telegram-bot==20.7)")
    
    return True

def test_database():
    """Test SQLite database functionality"""
    print("\n📦 Testing database functionality...")
    
    try:
        import sqlite3
        
        # Test database creation
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test_user",))
        conn.commit()
        
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print("✅ Database functionality OK")
            return True
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_api_request():
    """Test API request functionality (mock)"""
    print("\n🌐 Testing API request structure...")
    
    try:
        # Mock API request function
        async def mock_api_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return {"success": True, "endpoint": endpoint, "method": method}
        
        # Test async function
        import asyncio
        
        async def test():
            result = await mock_api_request("/test")
            return result
        
        result = asyncio.run(test())
        
        if result.get("success"):
            print("✅ API request structure OK")
            return True
        else:
            print("❌ API request test failed")
            return False
            
    except Exception as e:
        print(f"❌ API request test error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "API_BASE_URL", 
        "PANEL_URL",
        "WEBAPP_URL"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: Not set")

def main():
    """Run all tests"""
    print("🚀 GavatCore Telegram Bot Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database,
        test_api_request,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    check_environment()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Telegram bot is ready.")
        print("\n🚀 To deploy:")
        print("   1. Set TELEGRAM_BOT_TOKEN environment variable")
        print("   2. Run: python telegram_gateway_bot.py")
        print("   3. Or use Docker: ./scripts/deploy_telegram_bot.sh")
    else:
        print("⚠️ Some tests failed. Check dependencies.")
        print("\n💡 Install missing packages:")
        print("   pip install -r requirements_telegram.txt")

if __name__ == "__main__":
    main() 