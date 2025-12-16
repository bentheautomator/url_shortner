#!/usr/bin/env python3
"""
Dynamic API Testing for SHRTNR

Automatically discovers and tests all API routes.
Uses httpx for HTTP requests and dynamically tests endpoints.

Run: python tests/test_dynamic.py
Or CLI: schemathesis run api/openapi.json --base-url https://short.automatorprojects.space
"""

import httpx
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys

BASE_URL = "https://short.automatorprojects.space"

class DynamicAPITester:
    """Dynamically discovers and tests all API routes."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30)
        self.results = {"passed": [], "failed": [], "errors": []}
        self.created_resources = {"urls": [], "keys": []}

    def discover_routes(self) -> List[Dict]:
        """Load routes from OpenAPI spec."""
        spec_path = Path(__file__).parent.parent / "api" / "openapi.json"
        if spec_path.exists():
            with open(spec_path) as f:
                spec = json.load(f)
                return self._parse_openapi(spec)
        return self._default_routes()

    def _parse_openapi(self, spec: Dict) -> List[Dict]:
        """Parse OpenAPI spec into testable routes."""
        routes = []
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "DELETE", "PUT", "PATCH"]:
                    routes.append({
                        "path": path,
                        "method": method.upper(),
                        "operation_id": details.get("operationId", f"{method}_{path}"),
                        "summary": details.get("summary", ""),
                        "parameters": details.get("parameters", []),
                        "request_body": details.get("requestBody"),
                    })
        return routes

    def _default_routes(self) -> List[Dict]:
        """Fallback routes if no OpenAPI spec."""
        return [
            {"path": "/api/stats", "method": "GET", "operation_id": "getStats"},
            {"path": "/api/trending", "method": "GET", "operation_id": "getTrending"},
            {"path": "/api/urls", "method": "GET", "operation_id": "listUrls"},
            {"path": "/api/keys", "method": "GET", "operation_id": "listKeys"},
            {"path": "/api/shorten", "method": "POST", "operation_id": "shortenUrl"},
            {"path": "/api/keys", "method": "POST", "operation_id": "createKey"},
        ]

    def test_route(self, route: Dict) -> Tuple[bool, str, Any]:
        """Test a single route."""
        path = route["path"]
        method = route["method"]

        # Handle path parameters
        if "{code}" in path:
            if not self.created_resources["urls"]:
                return None, "skipped", "No URL created yet"
            path = path.replace("{code}", self.created_resources["urls"][0])

        if "{id}" in path:
            if not self.created_resources["keys"]:
                return None, "skipped", "No key created yet"
            path = path.replace("{id}", str(self.created_resources["keys"][0]))

        try:
            if method == "GET":
                response = self.client.get(path, follow_redirects=False)
            elif method == "POST":
                body = self._generate_body(route)
                response = self.client.post(path, json=body)
            elif method == "DELETE":
                # Try DELETE first, then fall back to POST with override
                response = self.client.delete(path)
                if response.status_code == 405:
                    # Vercel workaround: POST with X-HTTP-Method-Override
                    response = self.client.post(
                        path,
                        headers={"X-HTTP-Method-Override": "DELETE"}
                    )
            else:
                return None, "skipped", f"Unsupported method: {method}"

            # Track created resources
            if response.status_code == 200:
                self._track_resource(route, response)

            # Check success
            success = response.status_code in [200, 201, 204, 307, 302]
            return success, response.status_code, response.text[:200] if not success else "OK"

        except Exception as e:
            return False, "error", str(e)

    def _generate_body(self, route: Dict) -> Dict:
        """Generate request body for POST/PUT."""
        if route["operation_id"] == "shortenUrl":
            return {"url": f"https://httpbin.org/get?test={len(self.created_resources['urls'])}"}
        elif route["operation_id"] == "createKey":
            return {"name": f"test-key-{len(self.created_resources['keys'])}"}
        return {}

    def _track_resource(self, route: Dict, response: httpx.Response):
        """Track created resources for subsequent tests."""
        try:
            data = response.json()
            if route["operation_id"] == "shortenUrl" and "short_code" in data:
                self.created_resources["urls"].append(data["short_code"])
            elif route["operation_id"] == "createKey" and "id" in data:
                self.created_resources["keys"].append(data["id"])
        except:
            pass

    def run_all_tests(self):
        """Run all discovered tests."""
        print("\n" + "="*70)
        print("🔍 SHRTNR Dynamic API Test Suite")
        print(f"   Base URL: {self.base_url}")
        print("="*70 + "\n")

        routes = self.discover_routes()
        print(f"📋 Discovered {len(routes)} routes from OpenAPI spec\n")

        # Sort routes: GET before POST, POST before DELETE
        # Also ensure /api/shorten and /api/keys POST run first
        priority = {"POST": 1, "GET": 2, "DELETE": 3}
        routes.sort(key=lambda r: (
            priority.get(r["method"], 4),
            0 if r["path"] in ["/api/shorten", "/api/keys"] else 1
        ))

        for route in routes:
            path = route["path"]
            method = route["method"]
            op_id = route["operation_id"]

            result, status, detail = self.test_route(route)

            if result is None:
                print(f"⏭️  {method:6} {path:30} - SKIPPED ({detail})")
            elif result:
                self.results["passed"].append(f"{method} {path}")
                print(f"✅ {method:6} {path:30} - {status}")
            else:
                self.results["failed"].append((f"{method} {path}", status, detail))
                print(f"❌ {method:6} {path:30} - {status}")

        self._print_summary()
        return len(self.results["failed"]) == 0

    def _print_summary(self):
        """Print test summary."""
        total = len(self.results["passed"]) + len(self.results["failed"])
        passed = len(self.results["passed"])

        print("\n" + "="*70)
        print(f"📊 Results: {passed}/{total} passed ({100*passed//total if total else 0}%)")
        print("="*70)

        if self.results["failed"]:
            print("\n❌ Failed tests:")
            for name, status, detail in self.results["failed"]:
                print(f"   • {name}: {status}")
                if detail and detail != "OK":
                    print(f"     └─ {detail[:100]}")

        if self.results["passed"]:
            print("\n✅ Passed tests:")
            for name in self.results["passed"]:
                print(f"   • {name}")

        # Resources created during testing
        print(f"\n📦 Resources created during tests:")
        print(f"   • URLs: {len(self.created_resources['urls'])}")
        print(f"   • Keys: {len(self.created_resources['keys'])}")

    def cleanup(self):
        """Cleanup created resources."""
        print("\n🧹 Cleaning up test resources...")
        for code in self.created_resources["urls"]:
            try:
                self.client.delete(f"/api/urls/{code}")
                print(f"   Deleted URL: {code}")
            except:
                pass
        for key_id in self.created_resources["keys"]:
            try:
                self.client.delete(f"/api/keys/{key_id}")
                print(f"   Revoked key: {key_id}")
            except:
                pass
        self.client.close()


def main():
    """Run dynamic API tests."""
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    tester = DynamicAPITester(url)

    try:
        success = tester.run_all_tests()
        # Optionally cleanup: tester.cleanup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    finally:
        tester.client.close()


if __name__ == "__main__":
    main()
