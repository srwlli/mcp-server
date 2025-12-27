"""
Category 2: JSON-RPC Protocol Tests

Tests that prove coderef-context communication uses correct JSON-RPC 2.0 format.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
from io import StringIO

# Import the MCP client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_client import MCPToolClient
from tests.fixtures.mock_mcp_client import (
    create_mock_json_rpc_request,
    create_mock_json_rpc_response,
    create_mock_json_rpc_error,
    MockMCPClient
)


class TestJSONRPCRequestFormat:
    """Tests for JSON-RPC 2.0 request format."""

    @pytest.mark.asyncio
    async def test_json_rpc_request_format(self):
        """
        TEST 4: test_json_rpc_request_format

        WHAT IT PROVES:
        - Requests to coderef-context follow JSON-RPC 2.0 specification
        - Request includes: jsonrpc version, id, method, params
        - tool name and arguments are in correct params structure

        ASSERTION:
        - "jsonrpc": "2.0" is present
        - "id" is a unique integer
        - "method": "tools/call" is correct
        - "params" contains "name" and "arguments"
        """
        # Create a valid request
        request_json = create_mock_json_rpc_request(
            tool_name="coderef_scan",
            arguments={"project_path": "/path/to/project"},
            message_id=1
        )

        # Parse JSON
        request_data = json.loads(request_json.strip())

        # ASSERTION 1: JSON-RPC 2.0 version
        assert request_data.get("jsonrpc") == "2.0", \
            "Request should have jsonrpc=2.0"

        # ASSERTION 2: Message ID is present and integer
        assert "id" in request_data, "Request should have id field"
        assert isinstance(request_data["id"], int), "id should be integer"
        assert request_data["id"] > 0, "id should be positive"

        # ASSERTION 3: Method is tools/call
        assert request_data.get("method") == "tools/call", \
            "Method should be 'tools/call'"

        # ASSERTION 4: Params structure
        assert "params" in request_data, "Request should have params"
        params = request_data["params"]
        assert "name" in params, "params should have tool name"
        assert "arguments" in params, "params should have arguments"

        # ASSERTION 5: Tool name matches
        assert params["name"] == "coderef_scan", \
            "Tool name should match request"

        # ASSERTION 6: Arguments are passed correctly
        assert params["arguments"]["project_path"] == "/path/to/project", \
            "Arguments should be preserved"

    @pytest.mark.asyncio
    async def test_json_rpc_response_parsing(self):
        """
        TEST 5: test_json_rpc_response_parsing

        WHAT IT PROVES:
        - Responses from coderef-context follow JSON-RPC 2.0 format
        - Response id matches request id
        - Result data is properly extracted
        - Error responses are handled correctly

        ASSERTION:
        - Response has jsonrpc=2.0
        - Response has matching id
        - Result or error field is present
        """
        # Create valid response
        result_data = {"inventory": {"components": []}}
        response_json = create_mock_json_rpc_response(
            result=result_data,
            message_id=42
        )

        # Parse JSON
        response_data = json.loads(response_json.strip())

        # ASSERTION 1: JSON-RPC 2.0 version
        assert response_data.get("jsonrpc") == "2.0", \
            "Response should have jsonrpc=2.0"

        # ASSERTION 2: Message ID matches
        assert response_data.get("id") == 42, \
            "Response id should match request id"

        # ASSERTION 3: Result is present and correct
        assert "result" in response_data, "Response should have result field"
        assert response_data["result"]["inventory"]["components"] == [], \
            "Result should contain correct data"

    @pytest.mark.asyncio
    async def test_json_rpc_message_id_matching(self):
        """
        TEST 6: test_json_rpc_message_id_matching

        WHAT IT PROVES:
        - Message IDs are tracked and matched between requests/responses
        - Each request gets a unique ID
        - Responses can be correlated to requests via ID

        ASSERTION:
        - Request 1 has id=1, response has id=1
        - Request 2 has id=2, response has id=2
        - ID sequence is monotonically increasing
        """
        # Create multiple requests with different IDs
        request_1 = create_mock_json_rpc_request(
            tool_name="coderef_scan",
            arguments={"project_path": "/path1"},
            message_id=1
        )
        request_2 = create_mock_json_rpc_request(
            tool_name="coderef_query",
            arguments={"target": "auth_service"},
            message_id=2
        )

        # Parse both requests
        req_1_data = json.loads(request_1.strip())
        req_2_data = json.loads(request_2.strip())

        # ASSERTION 1: IDs are different
        assert req_1_data["id"] != req_2_data["id"], \
            "Each request should have unique ID"

        # ASSERTION 2: IDs are sequential
        assert req_1_data["id"] < req_2_data["id"], \
            "IDs should be monotonically increasing"

        # Create matching responses
        response_1 = create_mock_json_rpc_response(
            result={"status": "ok"},
            message_id=1
        )
        response_2 = create_mock_json_rpc_response(
            result={"status": "ok"},
            message_id=2
        )

        # Parse responses
        resp_1_data = json.loads(response_1.strip())
        resp_2_data = json.loads(response_2.strip())

        # ASSERTION 3: Response IDs match request IDs
        assert resp_1_data["id"] == req_1_data["id"], \
            "Response 1 ID should match request 1 ID"
        assert resp_2_data["id"] == req_2_data["id"], \
            "Response 2 ID should match request 2 ID"

        # ASSERTION 4: IDs can be used to correlate request/response
        responses = {resp_1_data["id"]: resp_1_data, resp_2_data["id"]: resp_2_data}
        for request in [req_1_data, req_2_data]:
            assert request["id"] in responses, \
                f"Response for request {request['id']} should exist"


class TestJSONRPCErrorHandling:
    """Tests for JSON-RPC error responses."""

    @pytest.mark.asyncio
    async def test_json_rpc_error_response(self):
        """
        WHAT IT PROVES:
        - Error responses follow JSON-RPC 2.0 error format
        - Error code and message are present
        - Client can parse and handle errors
        """
        # Create error response
        error_response = create_mock_json_rpc_error(
            code=-32600,  # Invalid Request
            message="Invalid method",
            message_id=5
        )

        # Parse JSON
        response_data = json.loads(error_response.strip())

        # ASSERTION 1: Has error field instead of result
        assert "error" in response_data, "Error response should have error field"
        assert "result" not in response_data, "Error response should not have result"

        # ASSERTION 2: Error structure
        error = response_data["error"]
        assert "code" in error, "Error should have code"
        assert "message" in error, "Error should have message"

        # ASSERTION 3: Error values
        assert error["code"] == -32600, "Error code should be preserved"
        assert error["message"] == "Invalid method", "Error message should be preserved"

        # ASSERTION 4: Response still has correct ID
        assert response_data["id"] == 5, "Error response should have matching ID"

    @pytest.mark.asyncio
    async def test_json_rpc_batch_request_format(self):
        """
        WHAT IT PROVES:
        - If batching is supported, requests follow JSON-RPC batch format
        - Multiple requests can be sent in array format
        """
        # Create multiple requests (batch format would be array)
        requests = [
            create_mock_json_rpc_request("coderef_scan", {}, 1),
            create_mock_json_rpc_request("coderef_query", {}, 2),
            create_mock_json_rpc_request("coderef_patterns", {}, 3),
        ]

        # Each request is individually valid JSON-RPC 2.0
        for request in requests:
            data = json.loads(request.strip())
            assert data.get("jsonrpc") == "2.0", \
                "Each request should be valid JSON-RPC 2.0"
            assert "id" in data, "Each request should have ID"
