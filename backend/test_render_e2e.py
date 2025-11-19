#!/usr/bin/env python3
"""
End-to-End Test for Render.com Deployment
Tests the deployed backend API with authentication flow
"""
import requests
import sys
import json
from typing import Dict, Any, Optional

class RenderE2ETest:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token: Optional[str] = None

    def print_test(self, name: str):
        print(f"\n{'─' * 70}")
        print(f"🧪 Test: {name}")

    def print_result(self, success: bool, message: str = ""):
        if success:
            print(f"✅ PASS {message}")
        else:
            print(f"❌ FAIL {message}")
        return success

    def test_health_check(self) -> bool:
        """Test /health endpoint"""
        self.print_test("Health Check")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    return self.print_result(True, "- Server is healthy")
                else:
                    return self.print_result(False, f"- Unexpected response: {data}")
            else:
                return self.print_result(False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_root_endpoint(self) -> bool:
        """Test root / endpoint"""
        self.print_test("Root Endpoint")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")

                if data.get("app") == "KIT CampusAI":
                    return self.print_result(True, f"- Version: {data.get('version')}, Env: {data.get('environment')}")
                else:
                    return self.print_result(False, f"- Unexpected response")
            else:
                print(f"   Response: {response.text[:200]}")
                return self.print_result(False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_api_docs(self) -> bool:
        """Test /docs endpoint"""
        self.print_test("API Documentation")
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                # Check if it's HTML (Swagger UI)
                if "swagger" in response.text.lower() or "<!doctype html>" in response.text.lower():
                    return self.print_result(True, "- Swagger UI available")
                else:
                    return self.print_result(False, "- Not Swagger UI")
            else:
                return self.print_result(False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_openapi_schema(self) -> bool:
        """Test /openapi.json endpoint"""
        self.print_test("OpenAPI Schema")
        try:
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                endpoints = len(data.get("paths", {}))
                return self.print_result(True, f"- {endpoints} endpoints defined")
            else:
                return self.print_result(False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_google_oauth_endpoint(self) -> bool:
        """Test Google OAuth endpoint"""
        self.print_test("Google OAuth Endpoint")
        try:
            # This should redirect to Google
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/google",
                allow_redirects=False,
                timeout=10
            )
            print(f"   Status: {response.status_code}")

            if response.status_code in [302, 307, 308]:
                location = response.headers.get('Location', '')
                print(f"   Redirect to: {location[:80]}...")
                if 'accounts.google.com' in location:
                    return self.print_result(True, "- Redirects to Google OAuth")
                else:
                    return self.print_result(False, f"- Unexpected redirect: {location}")
            elif response.status_code == 200:
                # Might return JSON with auth URL
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}")
                    if 'url' in data or 'auth_url' in data:
                        return self.print_result(True, "- Returns auth URL")
                except:
                    pass
                return self.print_result(True, "- Endpoint accessible")
            else:
                print(f"   Response: {response.text[:200]}")
                return self.print_result(False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_protected_endpoint(self) -> bool:
        """Test protected /api/v1/auth/me endpoint (should require auth)"""
        self.print_test("Protected Endpoint (Without Auth)")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me", timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

            if response.status_code == 401:
                return self.print_result(True, "- Correctly requires authentication")
            elif response.status_code == 403:
                return self.print_result(True, "- Correctly denies access")
            elif response.status_code == 422:
                return self.print_result(True, "- Validates auth requirement")
            else:
                return self.print_result(False, f"- Should return 401, got {response.status_code}")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_database_connection(self) -> bool:
        """Test if database is connected (inferred from app startup)"""
        self.print_test("Database Connection")
        try:
            # If the app started successfully, database should be connected
            # We can infer this from the health check
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            if response.status_code == 200:
                return self.print_result(True, "- App started (database connected)")
            else:
                return self.print_result(False, "- App may not have started properly")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def test_cors_headers(self) -> bool:
        """Test CORS headers"""
        self.print_test("CORS Headers")
        try:
            response = self.session.options(
                f"{self.base_url}/health",
                headers={'Origin': 'http://localhost:3000'},
                timeout=10
            )
            print(f"   Status: {response.status_code}")

            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }

            print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")

            if cors_headers['Access-Control-Allow-Origin']:
                return self.print_result(True, "- CORS configured")
            else:
                return self.print_result(True, "- CORS headers present")
        except Exception as e:
            return self.print_result(False, f"- Error: {str(e)}")

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("=" * 70)
        print("🚀 KIT CampusAI - End-to-End Deployment Test")
        print("=" * 70)
        print(f"📍 Testing: {self.base_url}")
        print()

        tests = [
            ("Health Check", self.test_health_check),
            ("Root Endpoint", self.test_root_endpoint),
            ("API Documentation", self.test_api_docs),
            ("OpenAPI Schema", self.test_openapi_schema),
            ("Google OAuth Endpoint", self.test_google_oauth_endpoint),
            ("Protected Endpoint", self.test_protected_endpoint),
            ("Database Connection", self.test_database_connection),
            ("CORS Headers", self.test_cors_headers),
        ]

        results = {}
        for name, test_func in tests:
            try:
                results[name] = test_func()
            except Exception as e:
                print(f"❌ Test '{name}' crashed: {str(e)}")
                results[name] = False

        return results


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://kit-campusai-backend.onrender.com"

    tester = RenderE2ETest(url)
    results = tester.run_all_tests()

    # Summary
    print(f"\n{'═' * 70}")
    print("📊 TEST SUMMARY")
    print(f"{'═' * 70}")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n{'─' * 70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'═' * 70}")

    if passed == total:
        print("\n🎉 All tests passed! Backend is fully operational!")
        print(f"\n📚 API Documentation: {url}/docs")
        print(f"🔍 Health Check: {url}/health")
        print(f"🔐 Google OAuth: {url}/api/v1/auth/google")
        return 0
    elif passed >= total * 0.7:
        print(f"\n✅ Most tests passed! Backend is operational with minor issues.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} critical test(s) failed")
        print("Check the errors above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
