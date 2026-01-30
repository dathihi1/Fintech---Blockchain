"""
Run All Tests Script
Script để chạy tất cả tests
"""

import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Run all test files"""
    print("\n" + "="*70)
    print("🚀 SMART TRADING JOURNAL - TEST SUITE")
    print("="*70)
    
    test_files = [
        ("tests/test_nlp.py", "NLP Engine Tests"),
        ("tests/test_analyzers.py", "Active Analyzer Tests"),
        ("tests/test_api.py", "API Endpoint Tests"),
    ]
    
    results = []
    
    for test_file, name in test_files:
        print(f"\n\n{'='*70}")
        print(f"📋 Running: {name}")
        print('='*70)
        
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False
        )
        
        results.append((name, result.returncode == 0))
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status} - {name}")
    
    total_passed = sum(1 for _, p in results if p)
    total_failed = len(results) - total_passed
    
    print(f"\n  Total: {total_passed}/{len(results)} test suites passed")
    print("="*70 + "\n")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
