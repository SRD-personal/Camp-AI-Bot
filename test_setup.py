#!/usr/bin/env python3
"""
KIT CampusAI Setup Verification Script
Tests that all components are configured correctly
"""

import sys
import os
from pathlib import Path

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.9+ required, found {version.major}.{version.minor}.{version.micro}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path("backend/.env")
    
    if not env_path.exists():
        print_error(".env file not found in backend/")
        print_warning("Run: cp backend/.env.example backend/.env")
        return False
    
    with open(env_path) as f:
        content = f.read()
    
    required_vars = [
        'DATABASE_URL',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'GEMINI_API_KEY',
        'JWT_SECRET'
    ]
    
    missing = []
    for var in required_vars:
        if f"{var}=" not in content:
            missing.append(var)
        elif f"{var}=your-" in content or f"{var}=change" in content:
            print_warning(f"{var} needs to be configured")
    
    if missing:
        print_error(f"Missing environment variables: {', '.join(missing)}")
        return False
    
    print_success(".env file configured")
    return True

def check_dependencies():
    """Check if Python dependencies are installed"""
    try:
        import fastapi
        import sqlalchemy
        import google.generativeai
        print_success("Python dependencies installed")
        return True
    except ImportError as e:
        print_error(f"Missing dependencies: {e}")
        print_warning("Run: pip install -r backend/requirements.txt")
        return False

def check_database():
    """Check database connection"""
    try:
        # Add backend to path
        sys.path.insert(0, 'backend')
        
        from app.core.config import settings
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                # Parse connection string
                db_url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
                conn = await asyncpg.connect(db_url)
                
                # Check for pgvector extension
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
                
                await conn.close()
                
                if result:
                    print_success("Database connected and pgvector enabled")
                    return True
                else:
                    print_warning("Database connected but pgvector extension not found")
                    print_warning("Run: CREATE EXTENSION vector;")
                    return False
                    
            except Exception as e:
                print_error(f"Database connection failed: {e}")
                print_warning("Make sure PostgreSQL is running and database exists")
                return False
        
        return asyncio.run(test_connection())
        
    except Exception as e:
        print_error(f"Cannot test database: {e}")
        return False

def check_project_structure():
    """Check if project structure is correct"""
    required_paths = [
        'backend/app/main.py',
        'backend/app/api/auth.py',
        'backend/app/api/chat.py',
        'backend/app/services/rag_service.py',
        'backend/requirements.txt',
        'mobile/android_app/pubspec.yaml',
    ]
    
    all_exist = True
    for path in required_paths:
        if not Path(path).exists():
            print_error(f"Missing: {path}")
            all_exist = False
    
    if all_exist:
        print_success("Project structure verified")
    
    return all_exist

def main():
    print("🔍 KIT CampusAI Setup Verification")
    print("=" * 50)
    print()
    
    results = []
    
    print("Checking Python version...")
    results.append(check_python_version())
    print()
    
    print("Checking project structure...")
    results.append(check_project_structure())
    print()
    
    print("Checking environment configuration...")
    results.append(check_env_file())
    print()
    
    print("Checking Python dependencies...")
    results.append(check_dependencies())
    print()
    
    print("Checking database connection...")
    results.append(check_database())
    print()
    
    # Summary
    print("=" * 50)
    if all(results):
        print_success("All checks passed! ✨")
        print()
        print("You can now start the backend:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --reload")
        print()
        print("Then visit: http://localhost:8000/docs")
    else:
        print_error("Some checks failed. Please fix the issues above.")
        print()
        print("For help, see QUICK_START.md or SETUP_GUIDE.md")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
