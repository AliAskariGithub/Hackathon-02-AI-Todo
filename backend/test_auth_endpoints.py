"""
Test script for Better Auth migration endpoints
Tests cookie-based authentication flow
"""

import requests
import json
import time
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "user_name": f"testuser_auth_{int(time.time())}",  # Unique username
    "email": f"testuser_auth_{int(time.time())}@example.com",  # Unique email
    "password": "testpassword123"
}

class AuthTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()  # Maintains cookies across requests

    def print_result(self, test_name: str, success: bool, details: str = ""):
        status = "[PASS]" if success else "[FAIL]"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   {details}")

    def test_register(self) -> bool:
        """Test user registration with cookie setting"""
        print("\n" + "="*60)
        print("TEST 1: User Registration")
        print("="*60)

        try:
            response = self.session.post(
                f"{self.base_url}/api/users/register",
                json=TEST_USER
            )

            # Check response status
            if response.status_code != 200:
                self.print_result(
                    "Registration",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}"
                )
                return False

            # Check response body
            data = response.json()
            if "user" not in data:
                self.print_result("Registration", False, "No user in response")
                return False

            # Check cookies
            cookies = self.session.cookies.get_dict()
            has_access = "access_token" in cookies
            has_refresh = "refresh_token" in cookies

            self.print_result(
                "Registration",
                has_access and has_refresh,
                f"Access token: {has_access}, Refresh token: {has_refresh}"
            )

            print(f"   User ID: {data['user'].get('id')}")
            print(f"   Email: {data['user'].get('email')}")

            return has_access and has_refresh

        except Exception as e:
            self.print_result("Registration", False, str(e))
            return False

    def test_protected_endpoint(self) -> bool:
        """Test accessing protected endpoint with cookie"""
        print("\n" + "="*60)
        print("TEST 2: Protected Endpoint Access")
        print("="*60)

        try:
            response = self.session.get(f"{self.base_url}/api/users/me")

            if response.status_code != 200:
                self.print_result(
                    "Protected Access",
                    False,
                    f"Status: {response.status_code}"
                )
                return False

            data = response.json()
            self.print_result(
                "Protected Access",
                True,
                f"User: {data.get('email')}"
            )
            return True

        except Exception as e:
            self.print_result("Protected Access", False, str(e))
            return False

    def test_logout(self) -> bool:
        """Test logout endpoint"""
        print("\n" + "="*60)
        print("TEST 3: Logout")
        print("="*60)

        try:
            response = self.session.post(f"{self.base_url}/api/auth/logout")

            if response.status_code != 200:
                self.print_result("Logout", False, f"Status: {response.status_code}")
                return False

            # Check if cookies are cleared
            cookies = self.session.cookies.get_dict()
            cookies_cleared = "access_token" not in cookies and "refresh_token" not in cookies

            self.print_result(
                "Logout",
                cookies_cleared,
                f"Cookies cleared: {cookies_cleared}"
            )
            return cookies_cleared

        except Exception as e:
            self.print_result("Logout", False, str(e))
            return False

    def test_login(self) -> bool:
        """Test login endpoint"""
        print("\n" + "="*60)
        print("TEST 4: Login")
        print("="*60)

        try:
            response = self.session.post(
                f"{self.base_url}/api/users/login",
                json=TEST_USER
            )

            if response.status_code != 200:
                self.print_result("Login", False, f"Status: {response.status_code}")
                return False

            data = response.json()
            cookies = self.session.cookies.get_dict()
            has_access = "access_token" in cookies
            has_refresh = "refresh_token" in cookies

            self.print_result(
                "Login",
                has_access and has_refresh,
                f"Access token: {has_access}, Refresh token: {has_refresh}"
            )
            return has_access and has_refresh

        except Exception as e:
            self.print_result("Login", False, str(e))
            return False

    def test_refresh_token(self) -> bool:
        """Test token refresh endpoint"""
        print("\n" + "="*60)
        print("TEST 5: Token Refresh")
        print("="*60)

        try:
            # Get current access token
            old_access = self.session.cookies.get("access_token")

            response = self.session.post(f"{self.base_url}/api/auth/refresh")

            if response.status_code != 200:
                self.print_result("Token Refresh", False, f"Status: {response.status_code}")
                return False

            # Get new access token
            new_access = self.session.cookies.get("access_token")
            token_refreshed = old_access != new_access

            self.print_result(
                "Token Refresh",
                token_refreshed,
                f"Token changed: {token_refreshed}"
            )
            return token_refreshed

        except Exception as e:
            self.print_result("Token Refresh", False, str(e))
            return False

    def test_unauthorized_access(self) -> bool:
        """Test that protected endpoints reject requests without cookies"""
        print("\n" + "="*60)
        print("TEST 6: Unauthorized Access")
        print("="*60)

        try:
            # Create new session without cookies
            new_session = requests.Session()
            response = new_session.get(f"{self.base_url}/api/users/me")

            # Should return 401
            is_unauthorized = response.status_code == 401

            self.print_result(
                "Unauthorized Access",
                is_unauthorized,
                f"Status: {response.status_code} (expected 401)"
            )
            return is_unauthorized

        except Exception as e:
            self.print_result("Unauthorized Access", False, str(e))
            return False

    def run_all_tests(self):
        """Run all authentication tests"""
        print("\n" + "="*60)
        print("BETTER AUTH MIGRATION - ENDPOINT TESTS")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {TEST_USER['email']}")

        results = []

        # Test 1: Register
        results.append(("Registration", self.test_register()))

        # Test 2: Protected endpoint access
        results.append(("Protected Access", self.test_protected_endpoint()))

        # Test 3: Logout
        results.append(("Logout", self.test_logout()))

        # Test 4: Login
        results.append(("Login", self.test_login()))

        # Test 5: Token refresh
        results.append(("Token Refresh", self.test_refresh_token()))

        # Test 6: Unauthorized access
        results.append(("Unauthorized Access", self.test_unauthorized_access()))

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} - {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n[SUCCESS] All tests passed!")
        else:
            print(f"\n[WARNING] {total - passed} test(s) failed")

        return passed == total

if __name__ == "__main__":
    tester = AuthTester(BASE_URL)
    success = tester.run_all_tests()
    exit(0 if success else 1)
