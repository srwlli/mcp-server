#!/usr/bin/env python
"""
Simple test runner for MCP HTTP Server (no pytest dependency).
Tests core functionality of endpoints and error handling.
"""

import json
import sys
from http_server import create_app


def test_endpoints():
    """Run simple tests on HTTP endpoints."""
    app = create_app()
    client = app.test_client()

    tests_passed = 0
    tests_failed = 0

    print("\n" + "="*70)
    print("MCP HTTP Server - Basic Functionality Tests")
    print("="*70)

    # Test 1: Health endpoint
    print("\n[1] Testing GET /health...")
    response = client.get('/health')
    if response.status_code == 200:
        data = response.get_json()
        if 'status' in data and 'timestamp' in data and 'version' in data:
            print("    PASS: /health returns correct structure")
            tests_passed += 1
        else:
            print("    FAIL: /health missing required fields")
            tests_failed += 1
    else:
        print(f"    FAIL: /health returned {response.status_code}")
        tests_failed += 1

    # Test 2: Tools endpoint
    print("\n[2] Testing GET /tools...")
    response = client.get('/tools')
    if response.status_code == 200:
        data = response.get_json()
        if 'tools' in data and isinstance(data['tools'], list) and len(data['tools']) > 0:
            print(f"    PASS: /tools returns {data['count']} tools")
            tests_passed += 1
        else:
            print("    FAIL: /tools missing tools array")
            tests_failed += 1
    else:
        print(f"    FAIL: /tools returned {response.status_code}")
        tests_failed += 1

    # Test 3: Valid tool call
    print("\n[3] Testing POST /mcp with valid tool call...")
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'list_templates',
        'params': {}
    }
    response = client.post(
        '/mcp',
        data=json.dumps(payload),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.get_json()
        if 'result' in data and data.get('id') == 1:
            print("    PASS: Valid tool call succeeds")
            tests_passed += 1
        else:
            print("    FAIL: Response structure incorrect")
            tests_failed += 1
    else:
        print(f"    FAIL: /mcp returned {response.status_code}")
        tests_failed += 1

    # Test 4: Unknown tool error
    print("\n[4] Testing POST /mcp with unknown tool...")
    payload = {
        'jsonrpc': '2.0',
        'id': 2,
        'method': 'fake_tool_xyz',
        'params': {}
    }
    response = client.post(
        '/mcp',
        data=json.dumps(payload),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.get_json()
        if 'error' in data and data['error']['code'] == -32601:
            print("    PASS: Unknown tool returns -32601 error")
            tests_passed += 1
        else:
            print(f"    FAIL: Wrong error code {data.get('error', {}).get('code')}")
            tests_failed += 1
    else:
        print(f"    FAIL: /mcp returned {response.status_code}")
        tests_failed += 1

    # Test 5: Missing params object
    print("\n[5] Testing POST /mcp with non-object params...")
    payload = {
        'jsonrpc': '2.0',
        'id': 3,
        'method': 'list_templates',
        'params': []
    }
    response = client.post(
        '/mcp',
        data=json.dumps(payload),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.get_json()
        if 'error' in data and data['error']['code'] == -32602:
            print("    PASS: Non-object params returns -32602 error")
            tests_passed += 1
        else:
            print(f"    FAIL: Wrong error code {data.get('error', {}).get('code')}")
            tests_failed += 1
    else:
        print(f"    FAIL: /mcp returned {response.status_code}")
        tests_failed += 1

    # Test 6: Malformed JSON
    print("\n[6] Testing POST /mcp with malformed JSON...")
    response = client.post(
        '/mcp',
        data='{invalid json',
        content_type='application/json'
    )
    if response.status_code == 400:
        data = response.get_json()
        if 'error' in data and data['error']['code'] == -32700:
            print("    PASS: Malformed JSON returns -32700 error")
            tests_passed += 1
        else:
            print("    FAIL: Wrong error response")
            tests_failed += 1
    else:
        print(f"    FAIL: /mcp returned {response.status_code}, expected 400")
        tests_failed += 1

    # Test 7: Missing jsonrpc field
    print("\n[7] Testing POST /mcp with missing jsonrpc field...")
    payload = {
        'id': 4,
        'method': 'list_templates',
        'params': {}
    }
    response = client.post(
        '/mcp',
        data=json.dumps(payload),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.get_json()
        if 'error' in data and data['error']['code'] == -32600:
            print("    PASS: Missing jsonrpc returns -32600 error")
            tests_passed += 1
        else:
            print(f"    FAIL: Wrong error code {data.get('error', {}).get('code')}")
            tests_failed += 1
    else:
        print(f"    FAIL: /mcp returned {response.status_code}")
        tests_failed += 1

    # Test 8: 404 handling
    print("\n[8] Testing 404 on invalid endpoint...")
    response = client.get('/invalid/endpoint')
    if response.status_code == 404:
        print("    PASS: Invalid endpoint returns 404")
        tests_passed += 1
    else:
        print(f"    FAIL: Invalid endpoint returned {response.status_code}")
        tests_failed += 1

    # Test 9: JSON-RPC response format
    print("\n[9] Testing JSON-RPC response format...")
    payload = {
        'jsonrpc': '2.0',
        'id': 'test-id',
        'method': 'list_templates',
        'params': {}
    }
    response = client.post(
        '/mcp',
        data=json.dumps(payload),
        content_type='application/json'
    )
    data = response.get_json()
    if (data.get('jsonrpc') == '2.0' and
        data.get('id') == 'test-id' and
        ('result' in data or 'error' in data)):
        print("    PASS: Response follows JSON-RPC 2.0 structure")
        tests_passed += 1
    else:
        print("    FAIL: Response doesn't follow JSON-RPC 2.0")
        tests_failed += 1

    # Test 10: Tool discovery completeness
    print("\n[10] Testing tool discovery...")
    response = client.get('/tools')
    data = response.get_json()
    tool_names = [t['name'] for t in data['tools']]
    expected_tools = ['list_templates', 'get_template', 'generate_foundation_docs']
    found_tools = [t for t in expected_tools if t in tool_names]
    if len(found_tools) >= 2:
        print(f"    PASS: Found {len(data['tools'])} tools including core tools")
        tests_passed += 1
    else:
        print(f"    FAIL: Missing expected tools. Found: {found_tools}")
        tests_failed += 1

    # Summary
    print("\n" + "="*70)
    print(f"Results: {tests_passed} PASSED, {tests_failed} FAILED")
    print("="*70 + "\n")

    return tests_failed == 0


if __name__ == '__main__':
    success = test_endpoints()
    sys.exit(0 if success else 1)
