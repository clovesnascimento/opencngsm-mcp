#!/usr/bin/env python3
"""
Test Script for OpenCngsm MCP v2.0
Tests both backend and frontend functionality
"""

import requests
import json
import time
import sys

class OpenCngsmTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:18789"
        self.token = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    def print_header(self, text):
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
        
    def print_test(self, name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"     {details}")
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
    def test_backend_health(self):
        """Test if backend is running"""
        self.print_header("Testing Backend Health")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            data = response.json()
            
            self.print_test(
                "Backend is running",
                response.status_code == 200,
                f"Status: {data.get('status')}"
            )
            
            self.print_test(
                "Correct version",
                data.get('version') == '2.0',
                f"Version: {data.get('version')}"
            )
            
            return True
        except requests.exceptions.ConnectionError:
            self.print_test("Backend is running", False, "Connection refused")
            return False
        except Exception as e:
            self.print_test("Backend is running", False, str(e))
            return False
            
    def test_authentication(self):
        """Test JWT authentication"""
        self.print_header("Testing Authentication")
        
        try:
            # Test login
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"user_id": "admin", "secret": "opencngsm_secret_2024"}
            )
            
            self.print_test(
                "Login successful",
                response.status_code == 200,
                f"Status code: {response.status_code}"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                
                self.print_test(
                    "Token received",
                    self.token is not None,
                    f"Token length: {len(self.token) if self.token else 0}"
                )
                
                return True
            return False
            
        except Exception as e:
            self.print_test("Authentication", False, str(e))
            return False
            
    def test_status_endpoint(self):
        """Test status endpoint"""
        self.print_header("Testing Status Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/api/status")
            data = response.json()
            
            self.print_test(
                "Status endpoint accessible",
                response.status_code == 200
            )
            
            self.print_test(
                "Gateway is active",
                data.get('gateway') == 'active',
                f"Gateway: {data.get('gateway')}"
            )
            
            skills = data.get('skills', [])
            self.print_test(
                "Skills loaded",
                len(skills) > 0,
                f"Skills count: {len(skills)}"
            )
            
            return True
            
        except Exception as e:
            self.print_test("Status endpoint", False, str(e))
            return False
            
    def test_message_endpoint(self):
        """Test message processing"""
        self.print_header("Testing Message Endpoint")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/message",
                json={"message": "Hello, test message", "user_id": "test_user"}
            )
            
            self.print_test(
                "Message endpoint accessible",
                response.status_code == 200,
                f"Status code: {response.status_code}"
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_test(
                    "Response received",
                    'response' in data,
                    f"Response: {data.get('response', '')[:50]}..."
                )
                
                self.print_test(
                    "Plan generated",
                    'plan' in data,
                    f"Steps: {len(data.get('plan', {}).get('steps', []))}"
                )
                
                return True
            return False
            
        except Exception as e:
            self.print_test("Message endpoint", False, str(e))
            return False
            
    def test_skills_endpoint(self):
        """Test skills endpoint"""
        self.print_header("Testing Skills Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/api/skills")
            data = response.json()
            
            self.print_test(
                "Skills endpoint accessible",
                response.status_code == 200
            )
            
            skills = data.get('skills', [])
            expected_skills = [
                "web_search", "code_analysis", "file_operations",
                "data_processing", "api_integration", "text_generation",
                "image_analysis", "task_planning", "memory_management",
                "error_handling", "report_generation"
            ]
            
            self.print_test(
                "All skills present",
                len(skills) == len(expected_skills),
                f"Found {len(skills)}/{len(expected_skills)} skills"
            )
            
            return True
            
        except Exception as e:
            self.print_test("Skills endpoint", False, str(e))
            return False
            
    def test_cors_headers(self):
        """Test CORS configuration"""
        self.print_header("Testing CORS Configuration")
        
        try:
            response = requests.options(
                f"{self.base_url}/api/status",
                headers={"Origin": "http://localhost:5173"}
            )
            
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            
            self.print_test(
                "CORS headers present",
                cors_header is not None,
                f"Allow-Origin: {cors_header}"
            )
            
            return True
            
        except Exception as e:
            self.print_test("CORS headers", False, str(e))
            return False
            
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total = self.tests_passed + self.tests_failed
        percentage = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {percentage:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! System is working correctly!")
        else:
            print("\n⚠️  Some tests failed. Please check the output above.")
            
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 OpenCngsm MCP v2.0 - Test Suite")
        print("Testing backend functionality...")
        
        # Wait a moment for server to be ready
        time.sleep(1)
        
        # Run tests
        if not self.test_backend_health():
            print("\n❌ Backend is not running!")
            print("Please start the backend first:")
            print("  python core/gateway/gateway.py")
            sys.exit(1)
            
        self.test_authentication()
        self.test_status_endpoint()
        self.test_message_endpoint()
        self.test_skills_endpoint()
        self.test_cors_headers()
        
        # Print summary
        self.print_summary()
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = OpenCngsmTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
