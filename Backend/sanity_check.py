"""
Quick sanity check and integration tests
Run with: python sanity_check.py
"""

import requests
import sys
import json
from typing import Tuple

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str, status: bool, message: str = ""):
    """Print test result"""
    icon = f"{Colors.GREEN}✅{Colors.RESET}" if status else f"{Colors.RED}❌{Colors.RESET}"
    msg = f" - {message}" if message else ""
    print(f"{icon} {name}{msg}")

def test_api_connection() -> bool:
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def test_health_endpoint() -> Tuple[bool, str]:
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code == 200, f"Status: {response.json()['status']}"
    except Exception as e:
        return False, str(e)

def test_languages_endpoint() -> Tuple[bool, str]:
    """Test languages endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/languages")
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        count = len(data.get('languages', []))
        return count > 10, f"{count} languages supported"
    except Exception as e:
        return False, str(e)

def test_intents_endpoint() -> Tuple[bool, str]:
    """Test intents endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/intents")
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        count = len(data.get('intents', []))
        return count == 6, f"{count} intent types"
    except Exception as e:
        return False, str(e)

def test_simple_summarization() -> Tuple[bool, str]:
    """Test basic summarization"""
    try:
        payload = {
            "document": "Machine learning enables systems to learn from data.",
            "intent": "technical_overview",
            "language": "english"
        }
        response = requests.post(f"{BASE_URL}/summarize", json=payload, timeout=10)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        has_summary = bool(data.get('summary'))
        return has_summary, f"Summary length: {data.get('length', 0)} words"
    except Exception as e:
        return False, str(e)

def test_auto_summarize() -> Tuple[bool, str]:
    """Test auto model selection"""
    try:
        payload = {
            "document": "Test document for auto summarization.",
            "quality_preference": "speed"
        }
        response = requests.post(f"{BASE_URL}/summarize", json=payload, timeout=10)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        has_model = bool(data.get('model'))
        return has_model, f"Model: {data.get('model')}"
    except Exception as e:
        return False, str(e)

def test_multilingual() -> Tuple[bool, str]:
    """Test multilingual support"""
    try:
        payload = {
            "document": "El aprendizaje automático es importante.",
            "language": "spanish"
        }
        response = requests.post(f"{BASE_URL}/summarize", json=payload, timeout=10)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        is_spanish = data.get('language') == 'spanish'
        return is_spanish, f"Language: {data.get('language')}"
    except Exception as e:
        return False, str(e)

def test_batch_processing() -> Tuple[bool, str]:
    """Test batch processing"""
    try:
        payload = {
            "documents": [
                "Document 1 for testing.",
                "Document 2 for testing.",
                "Document 3 for testing."
            ]
        }
        response = requests.post(f"{BASE_URL}/batch-summarize", json=payload, timeout=15)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        count = data.get('count', 0)
        return count == 3, f"Processed: {count} documents"
    except Exception as e:
        return False, str(e)

def test_error_handling() -> Tuple[bool, str]:
    """Test error handling for empty document"""
    try:
        payload = {"document": ""}
        response = requests.post(f"{BASE_URL}/summarize", json=payload, timeout=5)
        return response.status_code == 400, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_response_time() -> Tuple[bool, str]:
    """Test response time"""
    try:
        import time
        payload = {
            "document": "Quick test.",
            "quality_preference": "speed"
        }
        start = time.time()
        response = requests.post(f"{BASE_URL}/summarize", json=payload, timeout=5)
        elapsed = (time.time() - start) * 1000
        is_fast = elapsed < 3000
        return is_fast, f"{elapsed:.0f}ms"
    except Exception as e:
        return False, str(e)

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("🧪 SANITY CHECK & INTEGRATION TESTS")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Check API connection
    print(f"{Colors.BOLD}Checking API Connection...{Colors.RESET}")
    if not test_api_connection():
        print(f"{Colors.RED}❌ Cannot connect to {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Make sure the API is running:{Colors.RESET}")
        print(f"  python -m uvicorn src.api:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    print(f"{Colors.GREEN}✅ API is running{Colors.RESET}\n")
    
    # Run tests
    print(f"{Colors.BOLD}Running Tests...{Colors.RESET}\n")
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Languages Endpoint", test_languages_endpoint),
        ("Intents Endpoint", test_intents_endpoint),
        ("Simple Summarization", test_simple_summarization),
        ("Auto Model Selection", test_auto_summarize),
        ("Multilingual Support (Spanish)", test_multilingual),
        ("Batch Processing", test_batch_processing),
        ("Error Handling", test_error_handling),
        ("Response Time", test_response_time)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            status, message = test_func()
            print_test(test_name, status, message)
            if status:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_test(test_name, False, str(e))
            failed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}{Colors.RESET}")
    print(f"✅ Passed: {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"❌ Failed: {Colors.RED}{failed}{Colors.RESET}")
    print(f"📈 Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
