"""Integration tests for CodeRef2 MCP Server."""

import pytest
import asyncio
import json
from server import CodeRef2Server, get_server, TOOL_SCHEMAS
from tool_handlers import TOOL_HANDLERS


# ============================================================================
# Server Initialization Tests
# ============================================================================

class TestServerInitialization:
    """Tests for server initialization and startup."""

    def test_server_singleton(self):
        """Test that server uses singleton pattern."""
        server1 = get_server()
        server2 = get_server()

        assert server1 is server2

    @pytest.mark.asyncio
    async def test_server_startup(self):
        """Test server startup."""
        coderef_server = CodeRef2Server()
        await coderef_server.start()

        assert coderef_server._tools_registered == len(TOOL_HANDLERS)

    @pytest.mark.asyncio
    async def test_server_health_check(self):
        """Test server health check."""
        coderef_server = CodeRef2Server()
        await coderef_server.start()

        health = await coderef_server.health_check()

        assert health["status"] == "healthy"
        assert health["service"] == "coderef2-mcp"
        assert health["tools_available"] == len(TOOL_HANDLERS)


# ============================================================================
# Tool Discovery Tests
# ============================================================================

class TestToolDiscovery:
    """Tests for tool discovery and schema."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        coderef_server = CodeRef2Server()
        tools = await coderef_server._handle_list_tools()

        assert len(tools) == 6
        tool_names = {t.name for t in tools}

        # Check all tools are present
        assert "mcp__coderef__query" in tool_names
        assert "mcp__coderef__analyze" in tool_names
        assert "mcp__coderef__validate" in tool_names
        assert "mcp__coderef__batch_validate" in tool_names
        assert "mcp__coderef__uds_compliance_check" in tool_names
        assert "mcp__coderef__generate_with_uds" in tool_names

    @pytest.mark.asyncio
    async def test_tool_schemas(self):
        """Test that tool schemas are properly defined."""
        coderef_server = CodeRef2Server()
        tools = await coderef_server._handle_list_tools()

        for tool in tools:
            assert tool.name in TOOL_SCHEMAS
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert "properties" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_query_tool_schema(self):
        """Test query tool schema details."""
        schema = TOOL_SCHEMAS["mcp__coderef__query"]

        assert "query" in schema["inputSchema"]["properties"]
        assert "query" in schema["inputSchema"]["required"]
        assert schema["inputSchema"]["properties"]["query"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_analyze_tool_schema(self):
        """Test analyze tool schema details."""
        schema = TOOL_SCHEMAS["mcp__coderef__analyze"]

        assert "reference" in schema["inputSchema"]["properties"]
        assert "reference" in schema["inputSchema"]["required"]
        assert "analysis_type" in schema["inputSchema"]["properties"]


# ============================================================================
# Tool Invocation Tests
# ============================================================================

class TestToolInvocation:
    """Tests for tool invocation through the server."""

    @pytest.mark.asyncio
    async def test_invoke_query_tool(self):
        """Test invoking query tool through server."""
        coderef_server = CodeRef2Server()

        result = await coderef_server._handle_call_tool(
            "mcp__coderef__query",
            {"query": "@Fn/src/test#func"}
        )

        assert len(result) > 0
        assert result[0].type == "text"
        # Result should be JSON
        response = json.loads(result[0].text)
        assert "status" in response

    @pytest.mark.asyncio
    async def test_invoke_analyze_tool(self):
        """Test invoking analyze tool through server."""
        coderef_server = CodeRef2Server()

        result = await coderef_server._handle_call_tool(
            "mcp__coderef__analyze",
            {"reference": "@Fn/src/test#func"}
        )

        assert len(result) > 0
        response = json.loads(result[0].text)
        assert "status" in response

    @pytest.mark.asyncio
    async def test_invoke_validate_tool(self):
        """Test invoking validate tool through server."""
        coderef_server = CodeRef2Server()

        result = await coderef_server._handle_call_tool(
            "mcp__coderef__validate",
            {"reference": "@Fn/src/test#func"}
        )

        assert len(result) > 0
        response = json.loads(result[0].text)
        assert "status" in response

    @pytest.mark.asyncio
    async def test_invoke_batch_validate_tool(self):
        """Test invoking batch validate tool through server."""
        coderef_server = CodeRef2Server()

        result = await coderef_server._handle_call_tool(
            "mcp__coderef__batch_validate",
            {
                "references": ["@Fn/src/a#func", "@C/src/b#Class"],
                "parallel": False
            }
        )

        assert len(result) > 0
        response = json.loads(result[0].text)
        assert "status" in response

    @pytest.mark.asyncio
    async def test_invoke_unknown_tool(self):
        """Test invoking unknown tool returns error."""
        coderef_server = CodeRef2Server()

        result = await coderef_server._handle_call_tool(
            "unknown_tool",
            {}
        )

        assert len(result) > 0
        assert result[0].isError is True
        response = json.loads(result[0].text)
        assert response["status"] == "error"
        assert response["error_code"] == "UNKNOWN_TOOL"

    @pytest.mark.asyncio
    async def test_invoke_tool_with_invalid_args(self):
        """Test invoking tool with invalid arguments."""
        coderef_server = CodeRef2Server()

        # Query tool requires "query" parameter
        result = await coderef_server._handle_call_tool(
            "mcp__coderef__query",
            {}  # Missing required "query"
        )

        # Should return error response
        response = json.loads(result[0].text)
        assert response["status"] == "error"


# ============================================================================
# Tool Handler Registration Tests
# ============================================================================

class TestToolHandlerRegistration:
    """Tests for tool handler registration."""

    def test_all_handlers_registered(self):
        """Test that all tool handlers are registered."""
        assert len(TOOL_HANDLERS) == 6

        # Check specific handlers
        assert "mcp__coderef__query" in TOOL_HANDLERS
        assert "mcp__coderef__analyze" in TOOL_HANDLERS
        assert "mcp__coderef__validate" in TOOL_HANDLERS
        assert "mcp__coderef__batch_validate" in TOOL_HANDLERS
        assert "mcp__coderef__uds_compliance_check" in TOOL_HANDLERS
        assert "mcp__coderef__generate_with_uds" in TOOL_HANDLERS

    def test_handlers_are_callable(self):
        """Test that all handlers are callable."""
        for name, handler in TOOL_HANDLERS.items():
            assert callable(handler), f"Handler {name} is not callable"


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling in server."""

    @pytest.mark.asyncio
    async def test_error_json_format(self):
        """Test error JSON formatting."""
        coderef_server = CodeRef2Server()

        error_json = coderef_server._error_json("TEST_ERROR", "Test message")
        error_dict = json.loads(error_json)

        assert error_dict["status"] == "error"
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test message"
        assert "timestamp" in error_dict

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self):
        """Test that handler exceptions are caught and formatted."""
        coderef_server = CodeRef2Server()

        # Call with invalid data that might cause internal error
        result = await coderef_server._handle_call_tool(
            "mcp__coderef__query",
            {"query": "@Fn/src/test#func"}
        )

        # Should not raise, should return ToolResult
        assert len(result) > 0
        assert result[0].type == "text"


# ============================================================================
# Integration Workflow Tests
# ============================================================================

class TestIntegrationWorkflows:
    """Tests for complete workflows through the server."""

    @pytest.mark.asyncio
    async def test_query_and_analyze_workflow(self):
        """Test querying and then analyzing results."""
        coderef_server = CodeRef2Server()

        # First: query for elements
        query_result = await coderef_server._handle_call_tool(
            "mcp__coderef__query",
            {"query": "@Fn/src/test#func"}
        )

        assert len(query_result) > 0
        query_response = json.loads(query_result[0].text)
        assert query_response["status"] == "success"

        # Second: analyze first result (if any)
        if query_response.get("total_count", 0) > 0:
            first_ref = query_response["elements"][0]["reference"]

            analyze_result = await coderef_server._handle_call_tool(
                "mcp__coderef__analyze",
                {"reference": first_ref}
            )

            assert len(analyze_result) > 0
            analyze_response = json.loads(analyze_result[0].text)
            assert analyze_response["status"] == "success"

    @pytest.mark.asyncio
    async def test_validate_and_batch_validate_workflow(self):
        """Test validating references individually and in batch."""
        coderef_server = CodeRef2Server()

        references = [
            "@Fn/src/a#func",
            "@C/src/b#Class",
            "invalid_ref",
        ]

        # Single validation
        single_result = await coderef_server._handle_call_tool(
            "mcp__coderef__validate",
            {"reference": references[0]}
        )

        assert len(single_result) > 0
        single_response = json.loads(single_result[0].text)
        assert single_response["status"] == "success"

        # Batch validation
        batch_result = await coderef_server._handle_call_tool(
            "mcp__coderef__batch_validate",
            {"references": references, "parallel": False}
        )

        assert len(batch_result) > 0
        batch_response = json.loads(batch_result[0].text)
        assert batch_response["status"] == "success"
        assert batch_response["total_items"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
