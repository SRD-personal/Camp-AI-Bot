#!/usr/bin/env python3
"""
Simple local test - verifies configuration and basic imports work
This doesn't require a database connection
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        import fastapi
        print("  ✅ FastAPI imported")

        import uvicorn
        print("  ✅ Uvicorn imported")

        from app.core.config import settings
        print("  ✅ Config imported")
        print(f"     - App Name: {settings.APP_NAME}")
        print(f"     - Environment: {settings.ENVIRONMENT}")
        print(f"     - Debug: {settings.DEBUG}")
        print(f"     - API Version: {settings.API_VERSION}")

        import google.generativeai as genai
        print("  ✅ Google Generative AI imported")

        from sqlalchemy.ext.asyncio import create_async_engine
        print("  ✅ SQLAlchemy imported")

        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_config():
    """Test configuration is loaded correctly"""
    print("\n🔧 Testing configuration...")
    try:
        from app.core.config import settings

        # Check required settings
        required = [
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET',
            'GEMINI_API_KEY',
            'JWT_SECRET',
            'DATABASE_URL'
        ]

        missing = []
        for key in required:
            value = getattr(settings, key, None)
            if value:
                # Mask sensitive values
                if len(value) > 10:
                    masked = value[:8] + "..." + value[-4:]
                else:
                    masked = "***"
                print(f"  ✅ {key}: {masked}")
            else:
                print(f"  ❌ {key}: NOT SET")
                missing.append(key)

        if missing:
            print(f"\n❌ Missing required configuration: {', '.join(missing)}")
            return False

        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🤖 Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        from app.core.config import settings

        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Try to list models (this verifies API key is valid)
        print("  📡 Connecting to Gemini API...")
        models = genai.list_models()
        model_list = list(models)

        if model_list:
            print(f"  ✅ Gemini API connected successfully!")
            print(f"  📋 Available models: {len(model_list)}")
            for model in model_list[:3]:
                print(f"     - {model.name}")
            return True
        else:
            print("  ⚠️  API connected but no models found")
            return False

    except Exception as e:
        print(f"  ⚠️  Gemini API test failed: {e}")
        print("  ℹ️  This might be due to SSL issues in sandbox environment")
        print("  ℹ️  The API will work in production on Render.com")
        return False


def test_app_creation():
    """Test that FastAPI app can be created"""
    print("\n🎯 Testing FastAPI app creation...")
    try:
        # Import without starting the server
        from app.main import app
        print("  ✅ FastAPI app created successfully")
        print(f"     - Title: {app.title}")
        print(f"     - Version: {app.version}")
        print(f"     - Routes: {len(app.routes)}")

        # List some routes
        print("  📍 Available routes:")
        for route in list(app.routes)[:10]:
            if hasattr(route, 'path'):
                print(f"     - {route.path}")

        return True
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 KIT CampusAI - Local Environment Test")
    print("=" * 70)
    print()

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Gemini API", test_gemini_api()))
    results.append(("App Creation", test_app_creation()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print()
    print(f"Results: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! Ready to start server.")
        print("\nTo start the server, run:")
        print("  cd backend")
        print("  ./run_local.sh")
        print("\nOr manually:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("Note: Gemini API test may fail in sandbox environment but will work in production.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
