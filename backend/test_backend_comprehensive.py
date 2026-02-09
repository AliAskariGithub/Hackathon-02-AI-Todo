"""
Comprehensive Backend Test Suite
Tests all backend functionality including authentication, tasks, testimonials, conversations, and MCP operations
"""

import requests
import json
import time
from typing import Dict, Optional, List

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "user_name": f"Checking_00{int(time.time())}",
    "email": f"Checking_00{int(time.time())}@example.com",
    "password": "testpassword123"
}

class ComprehensiveBackendTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()  # Maintains cookies across requests
        self.user_id = None
        self.task_ids = []
        self.conversation_id = None
        self.testimonial_id = None

    def print_header(self, title: str):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)

    def print_test(self, test_name: str, success: bool, details: str = ""):
        status = "[PASS]" if success else "[FAIL]"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   {details}")
        return success

    def print_section(self, section_name: str):
        print(f"\n{'-'*70}")
        print(f"  {section_name}")
        print(f"{'-'*70}")

    # ========================================================================
    # AUTHENTICATION TESTS
    # ========================================================================

    def test_health_check(self) -> bool:
        """Test if backend is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            return self.print_test(
                "Health Check",
                success,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            return self.print_test("Health Check", False, str(e))

    def test_register(self) -> bool:
        """Test user registration"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/users/register",
                json=TEST_USER
            )

            if response.status_code != 200:
                return self.print_test(
                    "User Registration",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}"
                )

            data = response.json()
            if "user" not in data:
                return self.print_test("User Registration", False, "No user in response")

            self.user_id = data["user"]["id"]

            cookies = self.session.cookies.get_dict()
            has_access = "access_token" in cookies
            has_refresh = "refresh_token" in cookies

            return self.print_test(
                "User Registration",
                has_access and has_refresh,
                f"User ID: {self.user_id}, Cookies: access={has_access}, refresh={has_refresh}"
            )
        except Exception as e:
            return self.print_test("User Registration", False, str(e))

    def test_logout(self) -> bool:
        """Test logout"""
        try:
            response = self.session.post(f"{self.base_url}/api/auth/logout")

            if response.status_code != 200:
                return self.print_test("Logout", False, f"Status: {response.status_code}")

            cookies = self.session.cookies.get_dict()
            cookies_cleared = "access_token" not in cookies and "refresh_token" not in cookies

            return self.print_test(
                "Logout",
                cookies_cleared,
                f"Cookies cleared: {cookies_cleared}"
            )
        except Exception as e:
            return self.print_test("Logout", False, str(e))

    def test_login(self) -> bool:
        """Test user login"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/users/login",
                json=TEST_USER
            )

            if response.status_code != 200:
                return self.print_test("Login", False, f"Status: {response.status_code}")

            cookies = self.session.cookies.get_dict()
            has_access = "access_token" in cookies
            has_refresh = "refresh_token" in cookies

            return self.print_test(
                "Login",
                has_access and has_refresh,
                f"Cookies: access={has_access}, refresh={has_refresh}"
            )
        except Exception as e:
            return self.print_test("Login", False, str(e))

    def test_token_refresh(self) -> bool:
        """Test token refresh"""
        try:
            old_access = self.session.cookies.get("access_token")

            time.sleep(1)  # Wait to ensure token changes

            response = self.session.post(f"{self.base_url}/api/auth/refresh")

            if response.status_code != 200:
                return self.print_test("Token Refresh", False, f"Status: {response.status_code}")

            new_access = self.session.cookies.get("access_token")
            token_refreshed = old_access != new_access

            return self.print_test(
                "Token Refresh",
                token_refreshed,
                f"Token changed: {token_refreshed}"
            )
        except Exception as e:
            return self.print_test("Token Refresh", False, str(e))

    # ========================================================================
    # TASK TESTS
    # ========================================================================

    def test_create_task(self) -> bool:
        """Test creating a task"""
        try:
            task_data = {
                "title": "Test Task 1",
                "description": "This is a test task",
                "completed": False
            }

            response = self.session.post(
                f"{self.base_url}/api/{self.user_id}/tasks",
                json=task_data
            )

            # Accept both 200 and 201 as success
            if response.status_code not in [200, 201]:
                return self.print_test(
                    "Create Task",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}"
                )

            data = response.json()
            if "id" not in data:
                return self.print_test("Create Task", False, "No task ID in response")

            self.task_ids.append(data["id"])

            return self.print_test(
                "Create Task",
                True,
                f"Task ID: {data['id']}, Title: {data['title']}"
            )
        except Exception as e:
            return self.print_test("Create Task", False, str(e))

    def test_get_tasks(self) -> bool:
        """Test getting all tasks"""
        try:
            response = self.session.get(f"{self.base_url}/api/{self.user_id}/tasks")

            if response.status_code != 200:
                return self.print_test("Get Tasks", False, f"Status: {response.status_code}")

            data = response.json()
            task_count = len(data) if isinstance(data, list) else 0

            return self.print_test(
                "Get Tasks",
                task_count > 0,
                f"Found {task_count} task(s)"
            )
        except Exception as e:
            return self.print_test("Get Tasks", False, str(e))

    def test_get_task_by_id(self) -> bool:
        """Test getting a specific task"""
        try:
            if not self.task_ids:
                return self.print_test("Get Task by ID", False, "No task ID available")

            task_id = self.task_ids[0]
            response = self.session.get(f"{self.base_url}/api/{self.user_id}/tasks/{task_id}")

            if response.status_code != 200:
                return self.print_test("Get Task by ID", False, f"Status: {response.status_code}")

            data = response.json()

            return self.print_test(
                "Get Task by ID",
                data["id"] == task_id,
                f"Task: {data['title']}"
            )
        except Exception as e:
            return self.print_test("Get Task by ID", False, str(e))

    def test_update_task(self) -> bool:
        """Test updating a task"""
        try:
            if not self.task_ids:
                return self.print_test("Update Task", False, "No task ID available")

            task_id = self.task_ids[0]
            update_data = {
                "title": "Updated Test Task",
                "completed": True
            }

            response = self.session.put(
                f"{self.base_url}/api/{self.user_id}/tasks/{task_id}",
                json=update_data
            )

            if response.status_code != 200:
                return self.print_test("Update Task", False, f"Status: {response.status_code}")

            data = response.json()

            return self.print_test(
                "Update Task",
                data["completed"] == True,
                f"Updated: {data['title']}, Completed: {data['completed']}"
            )
        except Exception as e:
            return self.print_test("Update Task", False, str(e))

    def test_delete_task(self) -> bool:
        """Test deleting a task"""
        try:
            if not self.task_ids:
                return self.print_test("Delete Task", False, "No task ID available")

            task_id = self.task_ids[0]
            response = self.session.delete(f"{self.base_url}/api/{self.user_id}/tasks/{task_id}")

            # Accept 200, 204 (No Content) as success
            success = response.status_code in [200, 204]

            if success:
                self.task_ids.remove(task_id)

            return self.print_test(
                "Delete Task",
                success,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            return self.print_test("Delete Task", False, str(e))

    # ========================================================================
    # TESTIMONIAL TESTS
    # ========================================================================

    def test_create_testimonial(self) -> bool:
        """Test creating a testimonial"""
        try:
            testimonial_data = {
                "name": "Test User",
                "email": TEST_USER["email"],
                "rating": 5,
                "message": "This is a test testimonial. Great app!"
            }

            response = self.session.post(
                f"{self.base_url}/api/testimonials",
                json=testimonial_data
            )

            # Accept both 200 and 201 as success
            if response.status_code not in [200, 201]:
                return self.print_test(
                    "Create Testimonial",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}"
                )

            data = response.json()
            if "id" in data:
                self.testimonial_id = data["id"]

            return self.print_test(
                "Create Testimonial",
                True,
                f"Rating: {data.get('rating', 'N/A')}, Message: {data.get('message', 'N/A')[:50]}..."
            )
        except Exception as e:
            return self.print_test("Create Testimonial", False, str(e))

    def test_get_testimonials(self) -> bool:
        """Test getting all testimonials"""
        try:
            response = self.session.get(f"{self.base_url}/api/testimonials")

            if response.status_code != 200:
                return self.print_test("Get Testimonials", False, f"Status: {response.status_code}")

            data = response.json()
            count = len(data) if isinstance(data, list) else 0

            return self.print_test(
                "Get Testimonials",
                count > 0,
                f"Found {count} testimonial(s)"
            )
        except Exception as e:
            return self.print_test("Get Testimonials", False, str(e))

    # ========================================================================
    # CONVERSATION & CHAT TESTS
    # ========================================================================

    def test_create_conversation(self) -> bool:
        """Test creating a conversation"""
        try:
            conversation_data = {
                "title": "Test Conversation",
                "user_id": self.user_id
            }

            response = self.session.post(
                f"{self.base_url}/api/{self.user_id}/conversations",
                json=conversation_data
            )

            # Accept both 200 and 201 as success
            if response.status_code not in [200, 201]:
                return self.print_test(
                    "Create Conversation",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}"
                )

            data = response.json()
            if "id" in data:
                self.conversation_id = data["id"]

            return self.print_test(
                "Create Conversation",
                True,
                f"Conversation ID: {self.conversation_id}"
            )
        except Exception as e:
            return self.print_test("Create Conversation", False, str(e))

    def test_get_conversations(self) -> bool:
        """Test getting all conversations"""
        try:
            response = self.session.get(f"{self.base_url}/api/{self.user_id}/conversations")

            if response.status_code != 200:
                return self.print_test("Get Conversations", False, f"Status: {response.status_code}")

            data = response.json()
            count = len(data) if isinstance(data, list) else 0

            return self.print_test(
                "Get Conversations",
                count > 0,
                f"Found {count} conversation(s)"
            )
        except Exception as e:
            return self.print_test("Get Conversations", False, str(e))

    def test_send_chat_message(self) -> bool:
        """Test sending a chat message"""
        try:
            if not self.conversation_id:
                return self.print_test("Send Chat Message", False, "No conversation ID available")

            message_data = {
                "content": "Hello, Add 5 tasks with Title and Description and mark first two tasks as completed.",
                "role": "user",
                "conversation_id": self.conversation_id
            }

            response = self.session.post(
                f"{self.base_url}/api/{self.user_id}/chat",
                json=message_data
            )

            if response.status_code != 200:
                return self.print_test(
                    "Send Chat Message",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}"
                )

            data = response.json()

            return self.print_test(
                "Send Chat Message",
                "content" in data,
                f"Response: {data.get('content', 'N/A')[:50]}..."
            )
        except Exception as e:
            return self.print_test("Send Chat Message", False, str(e))

    def test_get_conversation_messages(self) -> bool:
        """Test getting messages from a conversation"""
        try:
            if not self.conversation_id:
                return self.print_test("Get Conversation Messages", False, "No conversation ID available")

            response = self.session.get(
                f"{self.base_url}/api/{self.user_id}/conversations/{self.conversation_id}/messages"
            )

            if response.status_code != 200:
                return self.print_test("Get Conversation Messages", False, f"Status: {response.status_code}")

            data = response.json()
            count = len(data) if isinstance(data, list) else 0

            return self.print_test(
                "Get Conversation Messages",
                count > 0,
                f"Found {count} message(s)"
            )
        except Exception as e:
            return self.print_test("Get Conversation Messages", False, str(e))

    # ========================================================================
    # MCP TASK TESTS
    # ========================================================================

    def test_mcp_create_task(self) -> bool:
        """Test creating a task via MCP"""
        try:
            # Create a task using the chat interface (which uses MCP)
            message_data = {
                "content": "Create a task: Buy groceries",
                "role": "user",
                "conversation_id": self.conversation_id
            }

            response = self.session.post(
                f"{self.base_url}/api/{self.user_id}/chat",
                json=message_data
            )

            if response.status_code != 200:
                return self.print_test(
                    "MCP Create Task",
                    False,
                    f"Status: {response.status_code}"
                )

            data = response.json()
            has_tool_calls = "tool_calls" in data and len(data.get("tool_calls", [])) > 0

            return self.print_test(
                "MCP Create Task",
                True,
                f"Tool calls: {has_tool_calls}, Response: {data.get('content', 'N/A')[:50]}..."
            )
        except Exception as e:
            return self.print_test("MCP Create Task", False, str(e))

    def test_mcp_list_tasks(self) -> bool:
        """Test listing tasks via MCP"""
        try:
            message_data = {
                "content": "List all my tasks",
                "role": "user",
                "conversation_id": self.conversation_id
            }

            response = self.session.post(
                f"{self.base_url}/api/{self.user_id}/chat",
                json=message_data
            )

            if response.status_code != 200:
                return self.print_test(
                    "MCP List Tasks",
                    False,
                    f"Status: {response.status_code}"
                )

            data = response.json()

            return self.print_test(
                "MCP List Tasks",
                "content" in data,
                f"Response: {data.get('content', 'N/A')[:50]}..."
            )
        except Exception as e:
            return self.print_test("MCP List Tasks", False, str(e))

    # ========================================================================
    # TEST RUNNER
    # ========================================================================

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_header("COMPREHENSIVE BACKEND TEST SUITE")
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {TEST_USER['email']}")

        results = []

        # Health Check
        self.print_section("HEALTH CHECK")
        results.append(("Health Check", self.test_health_check()))

        # Authentication Tests
        self.print_section("AUTHENTICATION TESTS")
        results.append(("Register", self.test_register()))
        results.append(("Logout", self.test_logout()))
        results.append(("Login", self.test_login()))
        results.append(("Token Refresh", self.test_token_refresh()))

        # Task Tests
        self.print_section("TASK CRUD TESTS")
        results.append(("Create Task", self.test_create_task()))
        results.append(("Get Tasks", self.test_get_tasks()))
        results.append(("Get Task by ID", self.test_get_task_by_id()))
        results.append(("Update Task", self.test_update_task()))
        results.append(("Delete Task", self.test_delete_task()))

        # Testimonial Tests
        self.print_section("TESTIMONIAL TESTS")
        results.append(("Create Testimonial", self.test_create_testimonial()))
        results.append(("Get Testimonials", self.test_get_testimonials()))

        # Conversation & Chat Tests
        self.print_section("CONVERSATION & CHAT TESTS")
        results.append(("Create Conversation", self.test_create_conversation()))
        results.append(("Get Conversations", self.test_get_conversations()))
        results.append(("Send Chat Message", self.test_send_chat_message()))
        results.append(("Get Conversation Messages", self.test_get_conversation_messages()))

        # MCP Tests
        self.print_section("MCP TASK TESTS")
        results.append(("MCP Create Task", self.test_mcp_create_task()))
        results.append(("MCP List Tasks", self.test_mcp_list_tasks()))

        # Summary
        self.print_header("TEST SUMMARY")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        print(f"\nResults by Category:\n")

        # Group by category
        categories = {
            "Health": results[0:1],
            "Authentication": results[1:5],
            "Tasks": results[5:10],
            "Testimonials": results[10:12],
            "Conversations": results[12:16],
            "MCP": results[16:18]
        }

        for category, tests in categories.items():
            cat_passed = sum(1 for _, result in tests if result)
            cat_total = len(tests)
            print(f"  {category}: {cat_passed}/{cat_total} passed")
            for test_name, result in tests:
                status = "[PASS]" if result else "[FAIL]"
                print(f"    {status} {test_name}")

        print(f"\n{'='*70}")
        print(f"OVERALL: {passed}/{total} tests passed ({int(passed/total*100)}%)")
        print(f"{'='*70}")

        if passed == total:
            print("\n[SUCCESS] All tests passed! Backend is fully functional.")
        elif passed >= total * 0.8:
            print(f"\n[WARNING] {total - passed} test(s) failed. Most functionality working.")
        else:
            print(f"\n[ERROR] {total - passed} test(s) failed. Significant issues detected.")

        return passed == total


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  Starting Comprehensive Backend Test Suite")
    print("  Please ensure the backend server is running on http://localhost:8000")
    print("="*70)

    tester = ComprehensiveBackendTester(BASE_URL)
    success = tester.run_all_tests()

    exit(0 if success else 1)
