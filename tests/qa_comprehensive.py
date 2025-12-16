#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for SHRTNR URL Shortener
Tests all API endpoints and functionality against live deployment
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Test Configuration
BASE_URL = "https://urlshortner-dun.vercel.app"
API_BASE = f"{BASE_URL}/api"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []

    def add_test(self, category: str, test_name: str, passed: bool, message: str = "", warning: bool = False):
        status = "PASS" if passed else ("WARN" if warning else "FAIL")
        self.tests.append({
            'category': category,
            'name': test_name,
            'status': status,
            'message': message
        })
        if passed and not warning:
            self.passed += 1
        elif warning:
            self.warnings += 1
        else:
            self.failed += 1

    def print_summary(self):
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}TEST SUMMARY{RESET}")
        print(f"{'='*80}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{YELLOW}Warnings: {self.warnings}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"Total: {self.passed + self.warnings + self.failed}")
        print(f"{'='*80}\n")

        # Group by category
        categories = {}
        for test in self.tests:
            cat = test['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(test)

        for category, tests in categories.items():
            print(f"\n{BOLD}{BLUE}{category}{RESET}")
            print("-" * 80)
            for test in tests:
                if test['status'] == 'PASS':
                    icon = f"{GREEN}✓{RESET}"
                elif test['status'] == 'WARN':
                    icon = f"{YELLOW}⚠{RESET}"
                else:
                    icon = f"{RED}✗{RESET}"

                msg = f" - {test['message']}" if test['message'] else ""
                print(f"  {icon} {test['name']}{msg}")

results = TestResults()

def test_header(category: str):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}Testing: {category}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def log_test(test_name: str, success: bool, details: str = ""):
    status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
    print(f"  [{status}] {test_name}")
    if details:
        print(f"         {details}")

# ============================================================================
# TEST 1: CORE URL SHORTENING
# ============================================================================

def test_url_shortening():
    test_header("1. Core URL Shortening")
    category = "Core URL Shortening"

    # Test 1.1: Basic URL shortening
    print("  Testing basic URL shortening...")
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.example.com"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            required_fields = ['id', 'original_url', 'short_code', 'created_at', 'click_count', 'short_url']
            missing = [f for f in required_fields if f not in data]
            if missing:
                results.add_test(category, "Basic URL shortening", False, f"Missing fields: {missing}")
                log_test("Basic URL shortening", False, f"Missing fields: {missing}")
            else:
                results.add_test(category, "Basic URL shortening", True, f"Short code: {data['short_code']}")
                log_test("Basic URL shortening", True, f"Short code: {data['short_code']}")
                return data  # Return for later tests
        else:
            results.add_test(category, "Basic URL shortening", False, f"Status: {response.status_code}")
            log_test("Basic URL shortening", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test(category, "Basic URL shortening", False, str(e))
        log_test("Basic URL shortening", False, str(e))

    # Test 1.2: URL without protocol
    print("  Testing URL without protocol...")
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "example.com"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['original_url'].startswith('https://'):
                results.add_test(category, "Auto-add HTTPS protocol", True)
                log_test("Auto-add HTTPS protocol", True)
            else:
                results.add_test(category, "Auto-add HTTPS protocol", False, f"Got: {data['original_url']}")
                log_test("Auto-add HTTPS protocol", False)
        else:
            results.add_test(category, "Auto-add HTTPS protocol", False, f"Status: {response.status_code}")
            log_test("Auto-add HTTPS protocol", False)
    except Exception as e:
        results.add_test(category, "Auto-add HTTPS protocol", False, str(e))
        log_test("Auto-add HTTPS protocol", False)

    # Test 1.3: Custom code
    print("  Testing custom code...")
    custom_code = f"test_{int(time.time())}"
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.example.com/custom", "custom_code": custom_code},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['short_code'] == custom_code:
                results.add_test(category, "Custom code creation", True, f"Code: {custom_code}")
                log_test("Custom code creation", True)
            else:
                results.add_test(category, "Custom code creation", False, f"Expected {custom_code}, got {data['short_code']}")
                log_test("Custom code creation", False)
        else:
            results.add_test(category, "Custom code creation", False, f"Status: {response.status_code}")
            log_test("Custom code creation", False)
    except Exception as e:
        results.add_test(category, "Custom code creation", False, str(e))
        log_test("Custom code creation", False)

    # Test 1.4: Duplicate custom code
    print("  Testing duplicate custom code...")
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.example.com/dup", "custom_code": custom_code},
            timeout=10
        )
        if response.status_code == 400:
            data = response.json()
            if 'already taken' in data.get('detail', '').lower():
                results.add_test(category, "Duplicate code rejection", True)
                log_test("Duplicate code rejection", True)
            else:
                results.add_test(category, "Duplicate code rejection", False, f"Wrong error: {data.get('detail')}")
                log_test("Duplicate code rejection", False)
        else:
            results.add_test(category, "Duplicate code rejection", False, f"Should return 400, got {response.status_code}")
            log_test("Duplicate code rejection", False)
    except Exception as e:
        results.add_test(category, "Duplicate code rejection", False, str(e))
        log_test("Duplicate code rejection", False)

    # Test 1.5: Invalid URL
    print("  Testing invalid URL...")
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": ""},
            timeout=10
        )
        if response.status_code == 400:
            results.add_test(category, "Empty URL rejection", True)
            log_test("Empty URL rejection", True)
        else:
            results.add_test(category, "Empty URL rejection", False, f"Should return 400, got {response.status_code}")
            log_test("Empty URL rejection", False)
    except Exception as e:
        results.add_test(category, "Empty URL rejection", False, str(e))
        log_test("Empty URL rejection", False)

    # Test 1.6: CORS headers
    print("  Testing CORS headers...")
    try:
        response = requests.options(f"{API_BASE}/shorten", timeout=10)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header == '*':
            results.add_test(category, "CORS headers", True)
            log_test("CORS headers", True)
        else:
            results.add_test(category, "CORS headers", False, f"Got: {cors_header}")
            log_test("CORS headers", False)
    except Exception as e:
        results.add_test(category, "CORS headers", False, str(e))
        log_test("CORS headers", False)

# ============================================================================
# TEST 2: URL REDIRECT
# ============================================================================

def test_url_redirect():
    test_header("2. URL Redirect")
    category = "URL Redirect"

    # Create a test URL first
    print("  Creating test URL...")
    test_code = None
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.google.com"},
            timeout=10
        )
        if response.status_code == 200:
            test_code = response.json()['short_code']
            print(f"  Created test URL: {test_code}")
    except Exception as e:
        print(f"  {RED}Failed to create test URL: {e}{RESET}")
        results.add_test(category, "Redirect test", False, "Could not create test URL")
        return

    if not test_code:
        results.add_test(category, "Redirect test", False, "Could not create test URL")
        return

    # Test 2.1: Redirect with interstitial
    print("  Testing redirect with interstitial...")
    try:
        response = requests.get(f"{BASE_URL}/{test_code}", allow_redirects=False, timeout=10)
        if response.status_code == 200:
            if 'SHRTNR' in response.text and 'Redirecting' in response.text:
                results.add_test(category, "Interstitial page", True)
                log_test("Interstitial page", True)
            else:
                results.add_test(category, "Interstitial page", False, "Missing branding")
                log_test("Interstitial page", False)
        else:
            results.add_test(category, "Interstitial page", False, f"Status: {response.status_code}")
            log_test("Interstitial page", False)
    except Exception as e:
        results.add_test(category, "Interstitial page", False, str(e))
        log_test("Interstitial page", False)

    # Test 2.2: Non-existent code
    print("  Testing non-existent short code...")
    try:
        response = requests.get(f"{BASE_URL}/nonexistent999", allow_redirects=False, timeout=10)
        if response.status_code == 404:
            results.add_test(category, "404 for invalid code", True)
            log_test("404 for invalid code", True)
        else:
            results.add_test(category, "404 for invalid code", False, f"Got: {response.status_code}")
            log_test("404 for invalid code", False)
    except Exception as e:
        results.add_test(category, "404 for invalid code", False, str(e))
        log_test("404 for invalid code", False)

    # Test 2.3: Click tracking
    print("  Testing click tracking...")
    time.sleep(1)  # Wait a moment for click to be recorded
    try:
        response = requests.get(f"{API_BASE}/urls/{test_code}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('click_count', 0) > 0:
                results.add_test(category, "Click tracking", True, f"Clicks: {data['click_count']}")
                log_test("Click tracking", True)
            else:
                results.add_test(category, "Click tracking", True, "No clicks yet", warning=True)
                log_test("Click tracking", True, "(no clicks recorded yet)")
        else:
            results.add_test(category, "Click tracking", False, f"Status: {response.status_code}")
            log_test("Click tracking", False)
    except Exception as e:
        results.add_test(category, "Click tracking", False, str(e))
        log_test("Click tracking", False)

# ============================================================================
# TEST 3: URL LISTING
# ============================================================================

def test_url_listing():
    test_header("3. URL Listing")
    category = "URL Listing"

    # Test 3.1: Get all URLs
    print("  Testing URL listing...")
    try:
        response = requests.get(f"{API_BASE}/urls", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                results.add_test(category, "List URLs", True, f"Found {len(data)} URLs")
                log_test("List URLs", True, f"Found {len(data)} URLs")

                # Verify structure
                if len(data) > 0:
                    url = data[0]
                    required = ['id', 'original_url', 'short_code', 'created_at', 'click_count']
                    missing = [f for f in required if f not in url]
                    if missing:
                        results.add_test(category, "URL list structure", False, f"Missing: {missing}")
                        log_test("URL list structure", False)
                    else:
                        results.add_test(category, "URL list structure", True)
                        log_test("URL list structure", True)
            else:
                results.add_test(category, "List URLs", False, "Response not a list")
                log_test("List URLs", False)
        else:
            results.add_test(category, "List URLs", False, f"Status: {response.status_code}")
            log_test("List URLs", False)
    except Exception as e:
        results.add_test(category, "List URLs", False, str(e))
        log_test("List URLs", False)

    # Test 3.2: Pagination
    print("  Testing pagination...")
    try:
        response = requests.get(f"{API_BASE}/urls?limit=5&offset=0", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) <= 5:
                results.add_test(category, "Pagination", True)
                log_test("Pagination", True)
            else:
                results.add_test(category, "Pagination", False, f"Expected ≤5, got {len(data)}")
                log_test("Pagination", False)
        else:
            results.add_test(category, "Pagination", False, f"Status: {response.status_code}")
            log_test("Pagination", False)
    except Exception as e:
        results.add_test(category, "Pagination", False, str(e))
        log_test("Pagination", False)

# ============================================================================
# TEST 4: URL DETAILS & ANALYTICS
# ============================================================================

def test_url_details():
    test_header("4. URL Details & Analytics")
    category = "URL Details & Analytics"

    # Create test URL
    print("  Creating test URL...")
    test_code = None
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.example.com/analytics"},
            timeout=10
        )
        if response.status_code == 200:
            test_code = response.json()['short_code']
    except Exception as e:
        print(f"  {RED}Failed to create test URL{RESET}")
        results.add_test(category, "URL details", False, "Could not create test URL")
        return

    if not test_code:
        results.add_test(category, "URL details", False, "Could not create test URL")
        return

    # Test 4.1: Get URL details
    print("  Testing URL details...")
    try:
        response = requests.get(f"{API_BASE}/urls/{test_code}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required = ['id', 'original_url', 'short_code', 'created_at', 'click_count', 'top_referers']
            missing = [f for f in required if f not in data]
            if missing:
                results.add_test(category, "URL details structure", False, f"Missing: {missing}")
                log_test("URL details structure", False)
            else:
                results.add_test(category, "URL details structure", True)
                log_test("URL details structure", True)
        else:
            results.add_test(category, "URL details structure", False, f"Status: {response.status_code}")
            log_test("URL details structure", False)
    except Exception as e:
        results.add_test(category, "URL details structure", False, str(e))
        log_test("URL details structure", False)

    # Test 4.2: Top referrers
    print("  Testing top referrers...")
    try:
        response = requests.get(f"{API_BASE}/urls/{test_code}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'top_referers' in data and isinstance(data['top_referers'], list):
                results.add_test(category, "Top referrers", True)
                log_test("Top referrers", True)
            else:
                results.add_test(category, "Top referrers", False)
                log_test("Top referrers", False)
        else:
            results.add_test(category, "Top referrers", False)
            log_test("Top referrers", False)
    except Exception as e:
        results.add_test(category, "Top referrers", False, str(e))
        log_test("Top referrers", False)

# ============================================================================
# TEST 5: URL DELETION
# ============================================================================

def test_url_deletion():
    test_header("5. URL Deletion")
    category = "URL Deletion"

    # Create test URL to delete
    print("  Creating test URL to delete...")
    test_code = None
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.example.com/delete-me"},
            timeout=10
        )
        if response.status_code == 200:
            test_code = response.json()['short_code']
    except Exception as e:
        print(f"  {RED}Failed to create test URL{RESET}")
        results.add_test(category, "URL deletion", False, "Could not create test URL")
        return

    if not test_code:
        results.add_test(category, "URL deletion", False, "Could not create test URL")
        return

    # Test 5.1: Delete URL
    print("  Testing URL deletion...")
    try:
        response = requests.delete(f"{API_BASE}/urls/{test_code}", timeout=10)
        if response.status_code == 200:
            results.add_test(category, "Delete URL", True)
            log_test("Delete URL", True)

            # Verify deletion
            response = requests.get(f"{API_BASE}/urls/{test_code}", timeout=10)
            if response.status_code == 404:
                results.add_test(category, "Verify deletion", True)
                log_test("Verify deletion", True)
            else:
                results.add_test(category, "Verify deletion", False, "URL still exists")
                log_test("Verify deletion", False)
        else:
            results.add_test(category, "Delete URL", False, f"Status: {response.status_code}")
            log_test("Delete URL", False)
    except Exception as e:
        results.add_test(category, "Delete URL", False, str(e))
        log_test("Delete URL", False)

    # Test 5.2: Delete non-existent URL
    print("  Testing deletion of non-existent URL...")
    try:
        response = requests.delete(f"{API_BASE}/urls/nonexistent999", timeout=10)
        if response.status_code == 404:
            results.add_test(category, "Delete non-existent URL", True)
            log_test("Delete non-existent URL", True)
        else:
            results.add_test(category, "Delete non-existent URL", False, f"Expected 404, got {response.status_code}")
            log_test("Delete non-existent URL", False)
    except Exception as e:
        results.add_test(category, "Delete non-existent URL", False, str(e))
        log_test("Delete non-existent URL", False)

# ============================================================================
# TEST 6: QR CODE GENERATION
# ============================================================================

def test_qr_code():
    test_header("6. QR Code Generation")
    category = "QR Code Generation"

    # Create test URL
    print("  Creating test URL...")
    test_code = None
    try:
        response = requests.post(
            f"{API_BASE}/shorten",
            json={"url": "https://www.example.com/qr"},
            timeout=10
        )
        if response.status_code == 200:
            test_code = response.json()['short_code']
    except Exception as e:
        print(f"  {RED}Failed to create test URL{RESET}")
        results.add_test(category, "QR code generation", False, "Could not create test URL")
        return

    if not test_code:
        results.add_test(category, "QR code generation", False, "Could not create test URL")
        return

    # Test 6.1: Generate QR code
    print("  Testing QR code generation...")
    try:
        response = requests.get(f"{API_BASE}/urls/{test_code}/qr", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'qr_code' in data:
                qr_data = data['qr_code']
                if qr_data.startswith('data:image/png;base64,'):
                    results.add_test(category, "QR code generation", True)
                    log_test("QR code generation", True)
                else:
                    results.add_test(category, "QR code generation", False, "Invalid format")
                    log_test("QR code generation", False)
            else:
                results.add_test(category, "QR code generation", False, "Missing qr_code field")
                log_test("QR code generation", False)
        else:
            results.add_test(category, "QR code generation", False, f"Status: {response.status_code}")
            log_test("QR code generation", False)
    except Exception as e:
        results.add_test(category, "QR code generation", False, str(e))
        log_test("QR code generation", False)

    # Test 6.2: QR for non-existent URL
    print("  Testing QR for non-existent URL...")
    try:
        response = requests.get(f"{API_BASE}/urls/nonexistent999/qr", timeout=10)
        if response.status_code == 404:
            results.add_test(category, "QR for invalid URL", True)
            log_test("QR for invalid URL", True)
        else:
            results.add_test(category, "QR for invalid URL", False, f"Expected 404, got {response.status_code}")
            log_test("QR for invalid URL", False)
    except Exception as e:
        results.add_test(category, "QR for invalid URL", False, str(e))
        log_test("QR for invalid URL", False)

# ============================================================================
# TEST 7: GLOBAL STATS
# ============================================================================

def test_global_stats():
    test_header("7. Global Statistics")
    category = "Global Statistics"

    # Test 7.1: Get global stats
    print("  Testing global stats...")
    try:
        response = requests.get(f"{API_BASE}/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required = ['total_urls', 'total_clicks', 'urls_today', 'clicks_today']
            missing = [f for f in required if f not in data]
            if missing:
                results.add_test(category, "Global stats structure", False, f"Missing: {missing}")
                log_test("Global stats structure", False)
            else:
                results.add_test(category, "Global stats structure", True)
                log_test("Global stats structure", True, f"URLs: {data['total_urls']}, Clicks: {data['total_clicks']}")
        else:
            results.add_test(category, "Global stats structure", False, f"Status: {response.status_code}")
            log_test("Global stats structure", False)
    except Exception as e:
        results.add_test(category, "Global stats structure", False, str(e))
        log_test("Global stats structure", False)

# ============================================================================
# TEST 8: TRENDING LINKS
# ============================================================================

def test_trending():
    test_header("8. Trending Links")
    category = "Trending Links"

    # Test 8.1: Get trending
    print("  Testing trending links...")
    try:
        response = requests.get(f"{API_BASE}/trending", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                results.add_test(category, "Trending links", True, f"Found {len(data)} trending")
                log_test("Trending links", True, f"Found {len(data)} trending links")

                # Verify structure if data exists
                if len(data) > 0:
                    item = data[0]
                    required = ['id', 'short_code', 'click_count', 'short_url']
                    missing = [f for f in required if f not in item]
                    if missing:
                        results.add_test(category, "Trending structure", False, f"Missing: {missing}")
                        log_test("Trending structure", False)
                    else:
                        results.add_test(category, "Trending structure", True)
                        log_test("Trending structure", True)
            else:
                results.add_test(category, "Trending links", False, "Response not a list")
                log_test("Trending links", False)
        else:
            results.add_test(category, "Trending links", False, f"Status: {response.status_code}")
            log_test("Trending links", False)
    except Exception as e:
        results.add_test(category, "Trending links", False, str(e))
        log_test("Trending links", False)

# ============================================================================
# TEST 9: API KEY MANAGEMENT
# ============================================================================

def test_api_keys():
    test_header("9. API Key Management")
    category = "API Key Management"

    # Test 9.1: Create API key
    print("  Testing API key creation...")
    api_key_id = None
    api_key_value = None
    try:
        response = requests.post(
            f"{API_BASE}/keys",
            json={"name": f"Test Key {int(time.time())}"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            required = ['id', 'key', 'name', 'created_at', 'is_active']
            missing = [f for f in required if f not in data]
            if missing:
                results.add_test(category, "Create API key", False, f"Missing: {missing}")
                log_test("Create API key", False)
            else:
                api_key_id = data['id']
                api_key_value = data['key']
                results.add_test(category, "Create API key", True, f"Key: {data['key'][:10]}...")
                log_test("Create API key", True)
        else:
            results.add_test(category, "Create API key", False, f"Status: {response.status_code}")
            log_test("Create API key", False)
    except Exception as e:
        results.add_test(category, "Create API key", False, str(e))
        log_test("Create API key", False)

    # Test 9.2: List API keys
    print("  Testing API key listing...")
    try:
        response = requests.get(f"{API_BASE}/keys", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                results.add_test(category, "List API keys", True, f"Found {len(data)} keys")
                log_test("List API keys", True)
            else:
                results.add_test(category, "List API keys", False, "Response not a list")
                log_test("List API keys", False)
        else:
            results.add_test(category, "List API keys", False, f"Status: {response.status_code}")
            log_test("List API keys", False)
    except Exception as e:
        results.add_test(category, "List API keys", False, str(e))
        log_test("List API keys", False)

    # Test 9.3: Use API key for URL creation
    if api_key_value:
        print("  Testing API key usage...")
        try:
            response = requests.post(
                f"{API_BASE}/shorten",
                json={"url": "https://www.example.com/with-key"},
                headers={"X-API-Key": api_key_value},
                timeout=10
            )
            if response.status_code == 200:
                results.add_test(category, "Use API key", True)
                log_test("Use API key", True)
            else:
                results.add_test(category, "Use API key", False, f"Status: {response.status_code}")
                log_test("Use API key", False)
        except Exception as e:
            results.add_test(category, "Use API key", False, str(e))
            log_test("Use API key", False)

    # Test 9.4: Revoke API key
    if api_key_id:
        print("  Testing API key revocation...")
        try:
            response = requests.delete(f"{API_BASE}/keys/{api_key_id}", timeout=10)
            if response.status_code == 200:
                results.add_test(category, "Revoke API key", True)
                log_test("Revoke API key", True)
            else:
                results.add_test(category, "Revoke API key", False, f"Status: {response.status_code}")
                log_test("Revoke API key", False)
        except Exception as e:
            results.add_test(category, "Revoke API key", False, str(e))
            log_test("Revoke API key", False)

    # Test 9.5: Invalid API key name
    print("  Testing empty API key name...")
    try:
        response = requests.post(
            f"{API_BASE}/keys",
            json={"name": ""},
            timeout=10
        )
        if response.status_code == 400:
            results.add_test(category, "Reject empty key name", True)
            log_test("Reject empty key name", True)
        else:
            results.add_test(category, "Reject empty key name", False, f"Expected 400, got {response.status_code}")
            log_test("Reject empty key name", False)
    except Exception as e:
        results.add_test(category, "Reject empty key name", False, str(e))
        log_test("Reject empty key name", False)

# ============================================================================
# TEST 10: FRONTEND FUNCTIONALITY
# ============================================================================

def test_frontend():
    test_header("10. Frontend")
    category = "Frontend"

    # Test 10.1: Homepage loads
    print("  Testing homepage...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            if 'SHRTNR' in response.text:
                results.add_test(category, "Homepage loads", True)
                log_test("Homepage loads", True)
            else:
                results.add_test(category, "Homepage loads", False, "Missing branding")
                log_test("Homepage loads", False)
        else:
            results.add_test(category, "Homepage loads", False, f"Status: {response.status_code}")
            log_test("Homepage loads", False)
    except Exception as e:
        results.add_test(category, "Homepage loads", False, str(e))
        log_test("Homepage loads", False)

    # Test 10.2: Essential UI elements
    print("  Checking essential UI elements...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            html = response.text
            elements = {
                'Form input': 'input' in html.lower(),
                'Shorten button': 'shorten' in html.lower() or 'button' in html.lower(),
            }
            all_present = all(elements.values())
            if all_present:
                results.add_test(category, "Essential UI elements", True)
                log_test("Essential UI elements", True)
            else:
                missing = [k for k, v in elements.items() if not v]
                results.add_test(category, "Essential UI elements", False, f"Missing: {missing}")
                log_test("Essential UI elements", False)
        else:
            results.add_test(category, "Essential UI elements", False)
            log_test("Essential UI elements", False)
    except Exception as e:
        results.add_test(category, "Essential UI elements", False, str(e))
        log_test("Essential UI elements", False)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}SHRTNR URL Shortener - Comprehensive QA Test Suite{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}Target:{RESET} {BASE_URL}")
    print(f"{BOLD}Time:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    try:
        # Run all tests
        test_url_shortening()
        test_url_redirect()
        test_url_listing()
        test_url_details()
        test_url_deletion()
        test_qr_code()
        test_global_stats()
        test_trending()
        test_api_keys()
        test_frontend()

        # Print summary
        results.print_summary()

        # Return exit code
        return 0 if results.failed == 0 else 1

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user{RESET}")
        return 1
    except Exception as e:
        print(f"\n\n{RED}Fatal error: {e}{RESET}")
        return 1

if __name__ == "__main__":
    exit(main())
