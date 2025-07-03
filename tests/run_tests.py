#!/usr/bin/env python3
"""
🔥 GavatCore Test Runner 🔥

Production-grade test execution script with comprehensive reporting.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """
    🚀 Run comprehensive test suite
    
    Includes:
    - Unit tests
    - Integration tests  
    - Coverage reporting
    - HTML reports
    """
    
    print("🔥 GavatCore Contact Utils Test Suite 🔥")
    print("=" * 50)
    
    # Test command with comprehensive options
    cmd = [
        "python", "-m", "pytest",
        "test_contact_utils.py",
        "-v",                           # Verbose output
        "--tb=short",                   # Short traceback
        "--asyncio-mode=auto",          # Auto async mode
        "--cov=contact_utils",          # Coverage for contact_utils
        "--cov-report=term-missing",    # Terminal coverage with missing lines
        "--cov-report=html:htmlcov",    # HTML coverage report
        "--html=test_report.html",      # HTML test report
        "--self-contained-html",        # Self-contained HTML
        "-x",                          # Stop on first failure
        "--durations=10"               # Show 10 slowest tests
    ]
    
    print("🧪 Executing test command:")
    print(" ".join(cmd))
    print("-" * 50)
    
    try:
        # Run tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        print("\n" + "=" * 50)
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("\n📊 Reports generated:")
            print("  🌐 HTML Test Report: test_report.html")
            print("  📈 Coverage Report: htmlcov/index.html")
        else:
            print("❌ Some tests failed!")
            print(f"   Exit code: {result.returncode}")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ pytest not found! Install test dependencies:")
        print("   pip install -r requirements_test.txt")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def quick_test():
    """🏃‍♂️ Quick test run without coverage"""
    
    cmd = [
        "python", "-m", "pytest",
        "test_contact_utils.py",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "-x"
    ]
    
    try:
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    # Check if quick mode requested
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("🏃‍♂️ Quick test mode")
        success = quick_test()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1) 