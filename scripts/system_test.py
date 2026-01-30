"""
Smart Trading Journal - System Integration Test
Tests all components and their connections
"""

import requests
import sys
import time
from typing import Dict, List, Tuple
from colorama import init, Fore, Style

init(autoreset=True)

class SystemTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results: List[Tuple[str, bool, str]] = []
        
    def test_service(self, name: str, url: str, timeout: int = 5) -> bool:
        """Test if a service is responding"""
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                self.results.append((name, True, f"Status: {response.status_code}"))
                return True
            else:
                self.results.append((name, False, f"Status: {response.status_code}"))
                return False
        except requests.exceptions.ConnectionError:
            self.results.append((name, False, "Connection refused - service not running"))
            return False
        except requests.exceptions.Timeout:
            self.results.append((name, False, "Request timeout"))
            return False
        except Exception as e:
            self.results.append((name, False, f"Error: {str(e)}"))
            return False
    
    def test_api_endpoint(self, name: str, endpoint: str, expected_keys: List[str] = None) -> bool:
        """Test a specific API endpoint"""
        try:
            url = f"{self.backend_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                self.results.append((name, False, f"Status: {response.status_code}"))
                return False
            
            data = response.json()
            
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    self.results.append((name, False, f"Missing keys: {missing_keys}"))
                    return False
            
            self.results.append((name, True, "Endpoint working correctly"))
            return True
            
        except Exception as e:
            self.results.append((name, False, f"Error: {str(e)}"))
            return False
    
    def test_proxy(self, name: str, proxy_path: str) -> bool:
        """Test frontend proxy to backend"""
        try:
            url = f"{self.frontend_url}{proxy_path}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                self.results.append((name, True, "Proxy working"))
                return True
            else:
                self.results.append((name, False, f"Status: {response.status_code}"))
                return False
                
        except requests.exceptions.ConnectionError:
            self.results.append((name, False, "Frontend not running or proxy not configured"))
            return False
        except Exception as e:
            self.results.append((name, False, f"Error: {str(e)}"))
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        print(f"{Fore.CYAN}=" * 60)
        print(f"{Fore.CYAN}  Smart Trading Journal - System Integration Test")
        print(f"{Fore.CYAN}=" * 60)
        print()
        
        # Test 1: Backend Health
        print(f"{Fore.YELLOW}[TEST 1] Backend Health Check...")
        self.test_api_endpoint(
            "Backend Health",
            "/health",
            ["status", "demo_mode", "nlp_model"]
        )
        print()
        
        # Test 2: Backend API - NLP Keywords
        print(f"{Fore.YELLOW}[TEST 2] Backend NLP Keywords API...")
        self.test_api_endpoint(
            "NLP Keywords",
            "/api/nlp/keywords",
            ["vi", "en"]
        )
        print()
        
        # Test 3: Backend API - NLP Emotions
        print(f"{Fore.YELLOW}[TEST 3] Backend NLP Emotions API...")
        self.test_api_endpoint(
            "NLP Emotions",
            "/api/nlp/emotions",
            None
        )
        print()
        
        # Test 4: Backend API Docs
        print(f"{Fore.YELLOW}[TEST 4] Backend API Documentation...")
        self.test_service(
            "API Docs",
            f"{self.backend_url}/docs"
        )
        print()
        
        # Test 5: Frontend Server
        print(f"{Fore.YELLOW}[TEST 5] Frontend Server...")
        self.test_service(
            "Frontend",
            self.frontend_url
        )
        print()
        
        # Test 6: Frontend Proxy to Backend
        print(f"{Fore.YELLOW}[TEST 6] Frontend-to-Backend Proxy...")
        self.test_proxy(
            "Frontend Proxy",
            "/api/nlp/keywords"
        )
        print()
        
        # Test 7: CORS Configuration
        print(f"{Fore.YELLOW}[TEST 7] CORS Configuration...")
        try:
            response = requests.options(
                f"{self.backend_url}/api/nlp/keywords",
                headers={"Origin": self.frontend_url},
                timeout=5
            )
            cors_header = response.headers.get("Access-Control-Allow-Origin")
            if cors_header:
                self.results.append(("CORS Config", True, f"Allow-Origin: {cors_header}"))
            else:
                self.results.append(("CORS Config", False, "CORS headers not found"))
        except Exception as e:
            self.results.append(("CORS Config", False, f"Error: {str(e)}"))
        print()
        
        # Print Results
        self.print_results()
    
    def print_results(self):
        """Print test results"""
        print(f"{Fore.CYAN}=" * 60)
        print(f"{Fore.CYAN}  Test Results")
        print(f"{Fore.CYAN}=" * 60)
        print()
        
        passed = 0
        failed = 0
        
        for name, success, message in self.results:
            if success:
                print(f"{Fore.GREEN}✓ {name:<30} {message}")
                passed += 1
            else:
                print(f"{Fore.RED}✗ {name:<30} {message}")
                failed += 1
        
        print()
        print(f"{Fore.CYAN}=" * 60)
        print(f"Total Tests: {passed + failed}")
        print(f"{Fore.GREEN}Passed: {passed}")
        print(f"{Fore.RED}Failed: {failed}")
        print(f"{Fore.CYAN}=" * 60)
        print()
        
        if failed == 0:
            print(f"{Fore.GREEN}✓ ALL TESTS PASSED! System is healthy.")
            print()
            print(f"{Fore.CYAN}Access your application at:")
            print(f"  Frontend: {self.frontend_url}")
            print(f"  Backend:  {self.backend_url}")
            print(f"  API Docs: {self.backend_url}/docs")
            return 0
        elif failed <= 2:
            print(f"{Fore.YELLOW}⚠ SOME TESTS FAILED - System may have issues")
            print()
            print(f"{Fore.CYAN}Recommendations:")
            print("  1. Check if backend is running: uvicorn main:app --host 0.0.0.0 --port 8000")
            print("  2. Check if frontend is running: npm run dev")
            print("  3. Check if database is running: docker-compose up -d")
            return 1
        else:
            print(f"{Fore.RED}✗ CRITICAL FAILURES - System is not working properly")
            print()
            print(f"{Fore.CYAN}Please check:")
            print("  1. Database: docker-compose up -d")
            print("  2. Backend: Check logs for errors")
            print("  3. Frontend: Check console for errors")
            print("  4. Network: Ensure ports 8000, 3000, 5432 are not blocked")
            return 2


def main():
    """Main test runner"""
    print(f"{Fore.CYAN}Starting system tests...\n")
    time.sleep(1)
    
    tester = SystemTest()
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
