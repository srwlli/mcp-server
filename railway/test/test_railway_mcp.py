#!/usr/bin/env python3
"""
Test suite for Railway MCP Server deployment.

Tests public endpoints, authentication, and tool execution.

Usage:
    python test_railway_mcp.py           # Run all tests
    python test_railway_mcp.py -v        # Verbose output
    pytest test_railway_mcp.py -v        # Run with pytest
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "https://mcp-server-production-0ef4.up.railway.app"
API_KEY = "3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3"

# Expected values
EXPECTED_SERVERS = ["docs-mcp", "personas-mcp", "coderef-mcp"]
EXPECTED_MIN_TOOLS = 50  # Should be ~54

# =============================================================================
# TEST UTILITIES
# =============================================================================

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "", details: Any = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        msg = f"  [{status}] {self.name}"
        if self.message:
            msg += f" - {self.message}"
        return msg


def make_request(
    endpoint: str,
    method: str = "GET",
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: int = 30
) -> requests.Response:
    """Make HTTP request to the server."""
    url = f"{BASE_URL}{endpoint}"
    return requests.request(
        method=method,
        url=url,
        headers=headers or {},
        json=json_data,
        timeout=timeout
    )


def auth_headers() -> Dict[str, str]:
    """Return headers with API key."""
    return {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# =============================================================================
# PUBLIC ENDPOINT TESTS
# =============================================================================

def test_root_endpoint() -> TestResult:
    """Test / endpoint is accessible without auth."""
    try:
        resp = make_request("/")
        if resp.status_code == 200:
            data = resp.json()
            if "status" in data or "version" in data:
                return TestResult("Root endpoint", True, f"Status {resp.status_code}")
            return TestResult("Root endpoint", True, "Accessible")
        return TestResult("Root endpoint", False, f"Unexpected status: {resp.status_code}")
    except Exception as e:
        return TestResult("Root endpoint", False, str(e))


def test_health_endpoint() -> TestResult:
    """Test /health endpoint returns server status."""
    try:
        resp = make_request("/health")
        if resp.status_code != 200:
            return TestResult("Health endpoint", False, f"Status {resp.status_code}")

        data = resp.json()

        # Check required fields
        required = ["status", "servers_loaded", "servers_total", "servers"]
        missing = [f for f in required if f not in data]
        if missing:
            return TestResult("Health endpoint", False, f"Missing fields: {missing}")

        # Check all servers operational
        servers = data.get("servers", {})
        failed = [s for s, info in servers.items() if info.get("status") != "operational"]
        if failed:
            return TestResult("Health endpoint", False, f"Failed servers: {failed}")

        return TestResult(
            "Health endpoint",
            True,
            f"{data['servers_loaded']}/{data['servers_total']} servers, {data.get('tools_available', 0)} tools"
        )
    except Exception as e:
        return TestResult("Health endpoint", False, str(e))


def test_openapi_endpoint() -> TestResult:
    """Test /openapi.json is accessible without auth."""
    try:
        resp = make_request("/openapi.json")
        if resp.status_code == 200:
            data = resp.json()
            if "openapi" in data or "info" in data or "paths" in data:
                return TestResult("OpenAPI endpoint", True, "Valid OpenAPI spec")
            return TestResult("OpenAPI endpoint", True, "Accessible")
        return TestResult("OpenAPI endpoint", False, f"Status {resp.status_code}")
    except Exception as e:
        return TestResult("OpenAPI endpoint", False, str(e))


def test_debug_endpoint() -> TestResult:
    """Test /debug endpoint shows server info."""
    try:
        resp = make_request("/debug")
        if resp.status_code != 200:
            return TestResult("Debug endpoint", False, f"Status {resp.status_code}")

        data = resp.json()
        loaded = data.get("loaded_servers", [])
        errors = data.get("import_errors", {})

        if errors:
            return TestResult("Debug endpoint", False, f"Import errors: {errors}")

        return TestResult("Debug endpoint", True, f"Loaded: {loaded}")
    except Exception as e:
        return TestResult("Debug endpoint", False, str(e))


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

def test_auth_required_for_tools() -> TestResult:
    """Test /tools requires authentication."""
    try:
        resp = make_request("/tools")
        if resp.status_code == 401:
            return TestResult("Auth required for /tools", True, "Correctly returns 401")
        return TestResult("Auth required for /tools", False, f"Expected 401, got {resp.status_code}")
    except Exception as e:
        return TestResult("Auth required for /tools", False, str(e))


def test_auth_required_for_mcp() -> TestResult:
    """Test /mcp requires authentication."""
    try:
        resp = make_request("/mcp", method="POST", json_data={"method": "list_templates"})
        if resp.status_code == 401:
            return TestResult("Auth required for /mcp", True, "Correctly returns 401")
        return TestResult("Auth required for /mcp", False, f"Expected 401, got {resp.status_code}")
    except Exception as e:
        return TestResult("Auth required for /mcp", False, str(e))


def test_invalid_api_key() -> TestResult:
    """Test invalid API key is rejected."""
    try:
        headers = {"X-API-Key": "invalid-key-12345"}
        resp = make_request("/tools", headers=headers)
        if resp.status_code == 401:
            return TestResult("Invalid API key rejected", True, "Correctly returns 401")
        return TestResult("Invalid API key rejected", False, f"Expected 401, got {resp.status_code}")
    except Exception as e:
        return TestResult("Invalid API key rejected", False, str(e))


def test_valid_api_key() -> TestResult:
    """Test valid API key grants access."""
    try:
        resp = make_request("/tools", headers=auth_headers())
        if resp.status_code == 200:
            return TestResult("Valid API key accepted", True, "Access granted")
        return TestResult("Valid API key accepted", False, f"Expected 200, got {resp.status_code}")
    except Exception as e:
        return TestResult("Valid API key accepted", False, str(e))


# =============================================================================
# SERVER LOADING TESTS
# =============================================================================

def test_all_servers_loaded() -> TestResult:
    """Test all 3 MCP servers are loaded."""
    try:
        resp = make_request("/health")
        if resp.status_code != 200:
            return TestResult("All servers loaded", False, f"Health check failed: {resp.status_code}")

        data = resp.json()
        servers = data.get("servers", {})

        missing = [s for s in EXPECTED_SERVERS if s not in servers]
        if missing:
            return TestResult("All servers loaded", False, f"Missing: {missing}")

        failed = [s for s in EXPECTED_SERVERS if servers.get(s, {}).get("status") != "operational"]
        if failed:
            return TestResult("All servers loaded", False, f"Failed: {failed}")

        return TestResult("All servers loaded", True, f"All {len(EXPECTED_SERVERS)} servers operational")
    except Exception as e:
        return TestResult("All servers loaded", False, str(e))


def test_tool_count() -> TestResult:
    """Test expected number of tools are available."""
    try:
        resp = make_request("/health")
        if resp.status_code != 200:
            return TestResult("Tool count", False, f"Health check failed: {resp.status_code}")

        data = resp.json()
        tool_count = data.get("tools_available", 0)

        if tool_count >= EXPECTED_MIN_TOOLS:
            return TestResult("Tool count", True, f"{tool_count} tools (expected >= {EXPECTED_MIN_TOOLS})")
        return TestResult("Tool count", False, f"Only {tool_count} tools (expected >= {EXPECTED_MIN_TOOLS})")
    except Exception as e:
        return TestResult("Tool count", False, str(e))


def test_tools_endpoint_returns_methods() -> TestResult:
    """Test /tools returns tool definitions."""
    try:
        resp = make_request("/tools", headers=auth_headers())
        if resp.status_code != 200:
            return TestResult("Tools endpoint", False, f"Status {resp.status_code}")

        data = resp.json()
        methods = data.get("methods", [])

        if not methods:
            return TestResult("Tools endpoint", False, "No methods returned")

        # Check a few expected tools exist
        tool_names = [m.get("name") for m in methods]
        expected_tools = ["list_templates", "get_changelog", "list_personas"]
        found = [t for t in expected_tools if t in tool_names]

        return TestResult("Tools endpoint", True, f"{len(methods)} tools, found {found}")
    except Exception as e:
        return TestResult("Tools endpoint", False, str(e))


# =============================================================================
# MCP TOOL EXECUTION TESTS
# =============================================================================

def test_mcp_list_templates() -> TestResult:
    """Test executing list_templates via /mcp."""
    try:
        resp = make_request(
            "/mcp",
            method="POST",
            headers=auth_headers(),
            json_data={"method": "list_templates", "params": {}}
        )

        if resp.status_code != 200:
            return TestResult("MCP list_templates", False, f"Status {resp.status_code}")

        data = resp.json()
        if "error" in data:
            return TestResult("MCP list_templates", False, f"Error: {data['error']}")

        return TestResult("MCP list_templates", True, "Tool executed successfully")
    except Exception as e:
        return TestResult("MCP list_templates", False, str(e))


def test_mcp_list_personas() -> TestResult:
    """Test executing list_personas via /mcp."""
    try:
        resp = make_request(
            "/mcp",
            method="POST",
            headers=auth_headers(),
            json_data={"method": "list_personas", "params": {}}
        )

        if resp.status_code != 200:
            return TestResult("MCP list_personas", False, f"Status {resp.status_code}")

        data = resp.json()
        if "error" in data:
            return TestResult("MCP list_personas", False, f"Error: {data['error']}")

        return TestResult("MCP list_personas", True, "Tool executed successfully")
    except Exception as e:
        return TestResult("MCP list_personas", False, str(e))


def test_mcp_invalid_tool() -> TestResult:
    """Test calling non-existent tool returns error."""
    try:
        resp = make_request(
            "/mcp",
            method="POST",
            headers=auth_headers(),
            json_data={"method": "nonexistent_tool_xyz", "params": {}}
        )

        # Should return error (either 400/404 or 200 with error in body)
        data = resp.json()
        if "error" in data or resp.status_code >= 400:
            return TestResult("MCP invalid tool", True, "Correctly returns error")

        return TestResult("MCP invalid tool", False, "Should have returned error")
    except Exception as e:
        return TestResult("MCP invalid tool", False, str(e))


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_all_tests(verbose: bool = False) -> bool:
    """Run all tests and report results."""
    print("=" * 60)
    print("Railway MCP Server Test Suite")
    print(f"Target: {BASE_URL}")
    print("=" * 60)

    test_groups = [
        ("Public Endpoints", [
            test_root_endpoint,
            test_health_endpoint,
            test_openapi_endpoint,
            test_debug_endpoint,
        ]),
        ("Authentication", [
            test_auth_required_for_tools,
            test_auth_required_for_mcp,
            test_invalid_api_key,
            test_valid_api_key,
        ]),
        ("Server Loading", [
            test_all_servers_loaded,
            test_tool_count,
            test_tools_endpoint_returns_methods,
        ]),
        ("MCP Tool Execution", [
            test_mcp_list_templates,
            test_mcp_list_personas,
            test_mcp_invalid_tool,
        ]),
    ]

    total_passed = 0
    total_failed = 0
    failed_tests = []

    for group_name, tests in test_groups:
        print(f"\n{group_name}:")
        print("-" * 40)

        for test_fn in tests:
            result = test_fn()
            print(result)

            if result.passed:
                total_passed += 1
            else:
                total_failed += 1
                failed_tests.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Total:  {total_passed + total_failed}")

    if failed_tests:
        print("\nFailed tests:")
        for result in failed_tests:
            print(f"  - {result.name}: {result.message}")

    success = total_failed == 0
    print(f"\nResult: {'ALL TESTS PASSED' if success else 'SOME TESTS FAILED'}")
    print("=" * 60)

    return success


# =============================================================================
# PYTEST COMPATIBILITY
# =============================================================================

# For pytest discovery
def test_pytest_root_endpoint():
    result = test_root_endpoint()
    assert result.passed, result.message

def test_pytest_health_endpoint():
    result = test_health_endpoint()
    assert result.passed, result.message

def test_pytest_openapi_endpoint():
    result = test_openapi_endpoint()
    assert result.passed, result.message

def test_pytest_debug_endpoint():
    result = test_debug_endpoint()
    assert result.passed, result.message

def test_pytest_auth_required_for_tools():
    result = test_auth_required_for_tools()
    assert result.passed, result.message

def test_pytest_auth_required_for_mcp():
    result = test_auth_required_for_mcp()
    assert result.passed, result.message

def test_pytest_invalid_api_key():
    result = test_invalid_api_key()
    assert result.passed, result.message

def test_pytest_valid_api_key():
    result = test_valid_api_key()
    assert result.passed, result.message

def test_pytest_all_servers_loaded():
    result = test_all_servers_loaded()
    assert result.passed, result.message

def test_pytest_tool_count():
    result = test_tool_count()
    assert result.passed, result.message

def test_pytest_tools_endpoint_returns_methods():
    result = test_tools_endpoint_returns_methods()
    assert result.passed, result.message

def test_pytest_mcp_list_templates():
    result = test_mcp_list_templates()
    assert result.passed, result.message

def test_pytest_mcp_list_personas():
    result = test_mcp_list_personas()
    assert result.passed, result.message

def test_pytest_mcp_invalid_tool():
    result = test_mcp_invalid_tool()
    assert result.passed, result.message


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    success = run_all_tests(verbose=verbose)
    sys.exit(0 if success else 1)
