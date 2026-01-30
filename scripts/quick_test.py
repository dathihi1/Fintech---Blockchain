"""
Quick connectivity test for Smart Trading Journal
Tests basic connectivity to all services
"""

import requests
import sys

def test_connection(name: str, url: str) -> bool:
    """Test connection to a service"""
    try:
        response = requests.get(url, timeout=3)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {name:<20} {url:<40} Status: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"✗ {name:<20} {url:<40} NOT RUNNING")
        return False
    except Exception as e:
        print(f"✗ {name:<20} {url:<40} Error: {str(e)[:30]}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  Quick Connectivity Test")
    print("="*80 + "\n")
    
    results = []
    
    # Test all services
    results.append(test_connection("Backend Health", "http://localhost:8000/health"))
    results.append(test_connection("Backend API", "http://localhost:8000/api/nlp/keywords"))
    results.append(test_connection("Frontend", "http://localhost:3000"))
    results.append(test_connection("Frontend Proxy", "http://localhost:3000/api/nlp/keywords"))
    
    print("\n" + "="*80)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("\nYour system is ready! Access at: http://localhost:3000")
        sys.exit(0)
    else:
        print(f"✗ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nPlease check:")
        print("  1. Backend: uvicorn main:app --host 0.0.0.0 --port 8000")
        print("  2. Frontend: npm run dev")
        print("  3. Database: docker-compose up -d")
        sys.exit(1)
