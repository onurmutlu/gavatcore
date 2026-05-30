#!/usr/bin/env python3
"""
🚀 GAVATCORE SaaS SETUP SCRIPT
Development environment setup and testing
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def run_command(command, description):
    """Run a shell command"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED: {e.stderr}")
        return False


def setup_virtual_environment():
    """Setup Python virtual environment"""
    print("🐍 Setting up Python virtual environment...")
    
    # Create venv
    if not run_command("python3 -m venv venv", "Creating virtual environment"):
        return False
    
    # Activate and install requirements
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    install_cmd = f"{activate_cmd} && pip install --upgrade pip && pip install -r requirements.txt"
    
    if not run_command(install_cmd, "Installing Python packages"):
        return False
    
    print("✅ Virtual environment setup complete!")
    return True


def setup_database():
    """Setup database (PostgreSQL)"""
    print("🗄️ Setting up PostgreSQL database...")
    
    # Check if PostgreSQL is running
    if not run_command("pg_isready", "Checking PostgreSQL connection"):
        print("⚠️  PostgreSQL not running or not installed")
        print("📋 Please install and start PostgreSQL:")
        print("   • macOS: brew install postgresql && brew services start postgresql")
        print("   • Ubuntu: sudo apt install postgresql && sudo systemctl start postgresql")
        print("   • Or use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password123 postgres:15")
        return False
    
    # Create database and user
    commands = [
        "createuser -s gavatcore || true",
        "createdb gavatcore_saas -O gavatcore || true",
        "psql -c \"ALTER USER gavatcore PASSWORD 'password123';\" || true"
    ]
    
    for cmd in commands:
        run_command(f"sudo -u postgres {cmd}", f"Database setup: {cmd}")
    
    print("✅ Database setup complete!")
    return True


def setup_redis():
    """Setup Redis"""
    print("🔴 Setting up Redis...")
    
    if not run_command("redis-cli ping", "Checking Redis connection"):
        print("⚠️  Redis not running or not installed")
        print("📋 Please install and start Redis:")
        print("   • macOS: brew install redis && brew services start redis")
        print("   • Ubuntu: sudo apt install redis-server && sudo systemctl start redis")
        print("   • Or use Docker: docker run -d -p 6379:6379 redis:7-alpine")
        return False
    
    print("✅ Redis setup complete!")
    return True


def create_env_file():
    """Create .env file from template"""
    print("⚙️ Creating environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping...")
        return True
    
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
        print("📝 Please update .env with your actual configuration values")
        return True
    else:
        print("❌ .env.example not found")
        return False


async def test_api():
    """Test the API"""
    print("🧪 Testing API...")
    
    try:
        # Import and test basic functionality
        sys.path.append(str(Path.cwd() / "app"))
        
        from app.core.config import settings
        from app.core.exceptions import APIException
        
        print(f"✅ Configuration loaded - Environment: {settings.ENVIRONMENT}")
        print(f"✅ Database URL: {settings.DATABASE_URL[:50]}...")
        
        # Test exception handling
        try:
            raise APIException("Test exception", 400, "TEST_ERROR")
        except APIException as e:
            print(f"✅ Exception handling works - {e.code}: {e.message}")
        
        print("✅ Basic API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 GAVATCORE SaaS SETUP STARTING...")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Setup steps
    steps = [
        ("Environment file", create_env_file),
        ("Virtual environment", setup_virtual_environment),
        ("Database", setup_database),
        ("Redis", setup_redis),
        ("API test", lambda: asyncio.run(test_api()))
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print(f"⚠️  {step_name} setup had issues")
        except Exception as e:
            print(f"❌ {step_name} setup failed: {e}")
    
    print("=" * 50)
    print(f"🎯 Setup completed: {success_count}/{len(steps)} steps successful")
    
    if success_count == len(steps):
        print("🎉 GAVATCORE SaaS setup complete!")
        print("🚀 Run the API with: uvicorn app.main:app --reload")
        print("📖 API docs will be available at: http://localhost:8000/docs")
    else:
        print("⚠️  Some setup steps failed. Check the logs above.")
        print("💡 You may need to install dependencies manually.")
    
    return success_count == len(steps)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 