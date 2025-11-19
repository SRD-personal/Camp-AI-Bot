#!/usr/bin/env python3
"""
Test Render.com deployment
Tests the deployed backend API endpoints
"""
import requests
import sys
import json
from typing import Dict, Any

# Default Render URL - update this with your actual URL
RENDER_URL = "https://kit-campusai-backend.onrender.com"

def test_endpoint(url: str, endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> bool:
    """Test a single endpoint"""
    full_url = f"{url}{endpoint}"
    print(f"\n🔍 Testing: {method} {full_url}")

    try:
        if method == "GET":
            response = requests.get(full_url, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, json=data, timeout=10)
        else:
            print(f"  ❌ Unsupported method: {method}")
            return False

        print(f"  📊 Status Code: {response.status_code}")

        if response.status_code < 500:
            try:
                json_data = response.json()
                print(f"  📄 Response: {json.dumps(json_data, indent=2)[:200]}...")
            except:
                print(f"  📄 Response: {response.text[:200]}...")
        else:
            print(f"  ❌ Server Error: {response.text[:200]}")
            return False

        if response.status_code == 200:
            print(f"  ✅ SUCCESS")
            return True
        elif response.status_code in [401, 403, 422]:
            print(f"  ⚠️  Expected error (endpoint requires auth or specific input)")
            return True
        else:
            print(f"  ⚠️  Unexpected status code")
            return False

    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT - Server took too long to respond")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ CONNECTION ERROR - Cannot reach server")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 KIT CampusAI - Render.com Deployment Test")
    print("=" * 70)

    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1].rstrip('/')
        print(f"📍 Testing URL: {url}")
    else:
        url = RENDER_URL
        print(f"📍 Testing default URL: {url}")
        print(f"   (You can provide a custom URL as argument)")

    print()

    # Test endpoints
    tests = [
        ("Health Check", "/health", "GET", None),
        ("Root Endpoint", "/", "GET", None),
        ("API Documentation", "/docs", "GET", None),
        ("OpenAPI Schema", "/openapi.json", "GET", None),
        ("Auth - Google OAuth", "/api/v1/auth/google", "GET", None),
        ("Auth - Get Current User", "/api/v1/auth/me", "GET", None),
    ]

    results = []

    for name, endpoint, method, data in tests:
        print(f"\n{'─' * 70}")
        print(f"Test: {name}")
        result = test_endpoint(url, endpoint, method, data)
        results.append((name, result))

    # Summary
    print(f"\n{'═' * 70}")
    print("📊 TEST SUMMARY")
    print(f"{'═' * 70}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n{'─' * 70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'═' * 70}")

    if passed == total:
        print("\n🎉 All tests passed! Backend is deployed and working!")
        print(f"\n📚 API Documentation: {url}/docs")
        print(f"🔍 Health Check: {url}/health")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Check the errors above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
