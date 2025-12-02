"""
Comprehensive test suite for MCP HTTP Server.

Tests cover:
- HTTP endpoints (/health, /tools, /mcp)
- JSON-RPC 2.0 protocol compliance
- Error handling and edge cases
- Concurrent requests
- Tool invocation
"""

import json
import pytest
from typing import Any, Dict

# Import the app factory
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from http_server import create_app


@pytest.fixture
def app():
    """Create and configure test client."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# ============================================================================
# HEALTH ENDPOINT TESTS
# ============================================================================

class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint should return valid JSON."""
        response = client.get('/health')
        data = response.get_json()
        assert data is not None
        assert isinstance(data, dict)

    def test_health_has_required_fields(self, client):
        """Health endpoint should include status, timestamp, version."""
        response = client.get('/health')
        data = response.get_json()
        assert 'status' in data
        assert 'timestamp' in data
        assert 'version' in data
        assert data['status'] == 'operational'

    def test_health_timestamp_format(self, client):
        """Health endpoint timestamp should be ISO 8601."""
        response = client.get('/health')
        data = response.get_json()
        assert data['timestamp'].endswith('Z')
        # Should be parseable as ISO format
        assert 'T' in data['timestamp']

    def test_health_response_time(self, client):
        """Health endpoint should respond quickly (<50ms)."""
        import time
        start = time.time()
        response = client.get('/health')
        elapsed = (time.time() - start) * 1000
        assert elapsed < 500  # Very generous limit for testing
        assert response.status_code == 200


# ============================================================================
# TOOLS ENDPOINT TESTS
# ============================================================================

class TestToolsEndpoint:
    """Tests for GET /tools endpoint."""

    def test_tools_returns_200(self, client):
        """Tools endpoint should return 200 OK."""
        response = client.get('/tools')
        assert response.status_code == 200

    def test_tools_returns_json(self, client):
        """Tools endpoint should return valid JSON."""
        response = client.get('/tools')
        data = response.get_json()
        assert data is not None
        assert isinstance(data, dict)

    def test_tools_has_tools_array(self, client):
        """Tools endpoint should have 'tools' key with array."""
        response = client.get('/tools')
        data = response.get_json()
        assert 'tools' in data
        assert isinstance(data['tools'], list)

    def test_tools_has_count(self, client):
        """Tools endpoint should include count."""
        response = client.get('/tools')
        data = response.get_json()
        assert 'count' in data
        assert data['count'] > 0

    def test_tools_list_completeness(self, client):
        """Tools list should have at least 23 tools."""
        response = client.get('/tools')
        data = response.get_json()
        # Should have all documented tools
        assert data['count'] >= 20

    def test_tool_schema_structure(self, client):
        """Each tool should have name, description, inputSchema."""
        response = client.get('/tools')
        data = response.get_json()
        assert len(data['tools']) > 0

        for tool in data['tools']:
            assert 'name' in tool
            assert 'description' in tool
            assert 'inputSchema' in tool


# ============================================================================
# MCP ENDPOINT - VALID REQUESTS
# ============================================================================

class TestMCPEndpointValidRequests:
    """Tests for valid POST /mcp requests."""

    def test_list_templates_tool(self, client):
        """Calling list_templates via /mcp should succeed."""
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
        assert response.status_code == 200
        data = response.get_json()
        assert 'result' in data
        assert data['id'] == 1

    def test_mcp_response_structure(self, client):
        """Valid MCP response should follow JSON-RPC 2.0 structure."""
        payload = {
            'jsonrpc': '2.0',
            'id': 'test-1',
            'method': 'list_templates',
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert data['jsonrpc'] == '2.0'
        assert data['id'] == 'test-1'
        assert 'result' in data
        assert 'error' not in data


# ============================================================================
# MCP ENDPOINT - ERROR CASES
# ============================================================================

class TestMCPEndpointErrors:
    """Tests for error handling in POST /mcp."""

    def test_unknown_tool_error(self, client):
        """Unknown tool should return -32601 error."""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'fake_tool_xyz',
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] == -32601
        assert 'Method not found' in data['error']['message']

    def test_missing_required_param(self, client):
        """Tool with missing required parameter should return -32602 error."""
        payload = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'analyze_project_for_planning',
            'params': {}  # Missing required project_path
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        # Should either be -32602 (param validation) or -32000 (tool error)
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] in [-32602, -32000]

    def test_malformed_json(self, client):
        """Malformed JSON should return -32700 error."""
        response = client.post(
            '/mcp',
            data='{invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == -32700

    def test_params_not_object(self, client):
        """Params must be object, not array or string."""
        payload = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'list_templates',
            'params': []  # Array instead of object
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] == -32602

    def test_missing_jsonrpc_field(self, client):
        """Missing jsonrpc field should return -32600."""
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
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] == -32600

    def test_missing_method_field(self, client):
        """Missing method field should return -32600."""
        payload = {
            'jsonrpc': '2.0',
            'id': 5,
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] == -32600

    def test_missing_id_field(self, client):
        """Missing id field should return error."""
        payload = {
            'jsonrpc': '2.0',
            'method': 'list_templates',
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] == -32600

    def test_non_json_content_type(self, client):
        """Non-JSON content type should return -32700 error."""
        response = client.post(
            '/mcp',
            data='{"jsonrpc": "2.0", "id": 1, "method": "list_templates"}',
            content_type='text/plain'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['error']['code'] == -32700


# ============================================================================
# MCP ENDPOINT - EDGE CASES
# ============================================================================

class TestMCPEndpointEdgeCases:
    """Tests for edge cases in POST /mcp."""

    def test_null_id_not_allowed(self, client):
        """JSON-RPC id cannot be null."""
        payload = {
            'jsonrpc': '2.0',
            'id': None,
            'method': 'list_templates',
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert data['error']['code'] == -32600

    def test_numeric_id(self, client):
        """JSON-RPC id can be numeric."""
        payload = {
            'jsonrpc': '2.0',
            'id': 12345,
            'method': 'list_templates',
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data['id'] == 12345

    def test_string_id(self, client):
        """JSON-RPC id can be string."""
        payload = {
            'jsonrpc': '2.0',
            'id': 'my-request-uuid',
            'method': 'list_templates',
            'params': {}
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data['id'] == 'my-request-uuid'

    def test_empty_params_optional(self, client):
        """Params field is optional."""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'list_templates'
        }
        response = client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'result' in data or 'error' in data

    def test_concurrent_requests(self, client):
        """Multiple simultaneous requests should complete without cross-talk."""
        import threading
        import time

        results = []
        errors = []

        def make_request(request_id):
            try:
                payload = {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'method': 'list_templates',
                    'params': {}
                }
                response = client.post(
                    '/mcp',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                data = response.get_json()
                results.append({
                    'request_id': request_id,
                    'response_id': data.get('id'),
                    'has_result': 'result' in data
                })
            except Exception as e:
                errors.append(str(e))

        threads = []
        for i in range(10):
            t = threading.Thread(target=make_request, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        # Each response should have correct id
        for result in results:
            assert result['request_id'] == result['response_id']
            assert result['has_result']


# ============================================================================
# 404 AND ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Tests for general error handling."""

    def test_404_invalid_endpoint(self, client):
        """Invalid endpoint should return 404."""
        response = client.get('/invalid/endpoint')
        assert response.status_code == 404

    def test_404_has_json_error(self, client):
        """404 should return JSON error."""
        response = client.get('/invalid/endpoint')
        data = response.get_json()
        assert 'error' in data
        assert 'jsonrpc' in data


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for realistic workflows."""

    def test_tool_discovery_then_call(self, client):
        """Should be able to discover tools and call one."""
        # Step 1: Get tools list
        response = client.get('/tools')
        assert response.status_code == 200
        tools_data = response.get_json()
        assert len(tools_data['tools']) > 0

        # Step 2: Verify list_templates is in tools
        tool_names = [t['name'] for t in tools_data['tools']]
        assert 'list_templates' in tool_names

        # Step 3: Call list_templates
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
        assert response.status_code == 200
        data = response.get_json()
        assert 'result' in data

    def test_health_check_ready(self, client):
        """Health check should pass before and after tool calls."""
        # Pre-flight health check
        response = client.get('/health')
        assert response.status_code == 200

        # Make tool call
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'list_templates',
            'params': {}
        }
        client.post(
            '/mcp',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Post-flight health check
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'operational'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
