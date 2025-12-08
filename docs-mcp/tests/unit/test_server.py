"""
Unit tests for server.py

Tests the MCP server module including:
- Module constants and configuration
- list_tools() function
- call_tool() function and handler dispatch
- Server initialization

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# MODULE CONSTANTS TESTS
# ============================================================================

class TestModuleConstants:
    """Test server module constants."""

    def test_version_format(self):
        """Version should be in X.Y.Z format."""
        import server
        assert hasattr(server, '__version__')
        parts = server.__version__.split('.')
        assert len(parts) == 3, f"Version should have 3 parts: {server.__version__}"
        for part in parts:
            assert part.isdigit(), f"Version parts should be numeric: {part}"

    def test_schema_version_format(self):
        """Schema version should be in X.Y.Z format."""
        import server
        assert hasattr(server, '__schema_version__')
        parts = server.__schema_version__.split('.')
        assert len(parts) == 3

    def test_mcp_version_exists(self):
        """MCP version should be defined."""
        import server
        assert hasattr(server, '__mcp_version__')
        assert server.__mcp_version__ == "1.0"

    def test_server_dir_is_path(self):
        """SERVER_DIR should be a Path object."""
        import server
        assert hasattr(server, 'SERVER_DIR')
        assert isinstance(server.SERVER_DIR, Path)

    def test_templates_dir_is_path(self):
        """TEMPLATES_DIR should be a Path object."""
        import server
        assert hasattr(server, 'TEMPLATES_DIR')
        assert isinstance(server.TEMPLATES_DIR, Path)

    def test_tool_templates_dir_is_path(self):
        """TOOL_TEMPLATES_DIR should be a Path object."""
        import server
        assert hasattr(server, 'TOOL_TEMPLATES_DIR')
        assert isinstance(server.TOOL_TEMPLATES_DIR, Path)


class TestServerInitialization:
    """Test server initialization."""

    def test_app_is_server_instance(self):
        """App should be a Server instance."""
        import server
        from mcp.server import Server
        assert hasattr(server, 'app')
        assert isinstance(server.app, Server)

    def test_app_has_name(self):
        """Server should be named 'docs-mcp'."""
        import server
        assert server.app.name == "docs-mcp"


# ============================================================================
# LIST_TOOLS TESTS
# ============================================================================

class TestListTools:
    """Test list_tools() function."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """list_tools should return a list."""
        import server
        tools = await server.list_tools()
        assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_list_tools_returns_tool_objects(self):
        """list_tools should return Tool objects."""
        import server
        from mcp.types import Tool
        tools = await server.list_tools()
        for tool in tools:
            assert isinstance(tool, Tool)

    @pytest.mark.asyncio
    async def test_list_tools_count(self):
        """list_tools should return expected number of tools."""
        import server
        tools = await server.list_tools()
        # Should have 40+ tools based on CLAUDE.md (45 specialized tools)
        assert len(tools) >= 40, f"Expected 40+ tools, got {len(tools)}"

    @pytest.mark.asyncio
    async def test_list_tools_has_required_tools(self):
        """list_tools should include core documentation tools."""
        import server
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]

        # Core documentation tools
        assert 'list_templates' in tool_names
        assert 'get_template' in tool_names
        assert 'generate_foundation_docs' in tool_names
        assert 'generate_individual_doc' in tool_names

        # Changelog tools
        assert 'get_changelog' in tool_names
        assert 'add_changelog_entry' in tool_names
        assert 'update_changelog' in tool_names

        # Planning tools
        assert 'get_planning_template' in tool_names
        assert 'analyze_project_for_planning' in tool_names
        assert 'create_plan' in tool_names
        assert 'validate_implementation_plan' in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_has_consistency_tools(self):
        """list_tools should include consistency management tools."""
        import server
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]

        assert 'establish_standards' in tool_names
        assert 'audit_codebase' in tool_names
        assert 'check_consistency' in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_has_inventory_tools(self):
        """list_tools should include inventory tools."""
        import server
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]

        assert 'inventory_manifest' in tool_names
        assert 'dependency_inventory' in tool_names
        assert 'api_inventory' in tool_names
        assert 'database_inventory' in tool_names
        assert 'config_inventory' in tool_names
        assert 'test_inventory' in tool_names
        assert 'documentation_inventory' in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_has_agent_coordination_tools(self):
        """list_tools should include agent coordination tools."""
        import server
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]

        assert 'generate_agent_communication' in tool_names
        assert 'assign_agent_task' in tool_names
        assert 'verify_agent_completion' in tool_names
        assert 'aggregate_agent_deliverables' in tool_names
        assert 'track_agent_status' in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_has_context_expert_tools(self):
        """list_tools should include context expert tools."""
        import server
        tools = await server.list_tools()
        tool_names = [t.name for t in tools]

        assert 'create_context_expert' in tool_names
        assert 'list_context_experts' in tool_names
        assert 'get_context_expert' in tool_names
        assert 'suggest_context_experts' in tool_names
        assert 'update_context_expert' in tool_names
        assert 'activate_context_expert' in tool_names


class TestToolSchemas:
    """Test tool input schemas."""

    @pytest.mark.asyncio
    async def test_all_tools_have_input_schema(self):
        """All tools should have inputSchema defined."""
        import server
        tools = await server.list_tools()
        for tool in tools:
            assert hasattr(tool, 'inputSchema'), f"Tool {tool.name} missing inputSchema"
            assert tool.inputSchema is not None, f"Tool {tool.name} has None inputSchema"

    @pytest.mark.asyncio
    async def test_all_tools_have_description(self):
        """All tools should have a description."""
        import server
        tools = await server.list_tools()
        for tool in tools:
            assert hasattr(tool, 'description'), f"Tool {tool.name} missing description"
            assert tool.description, f"Tool {tool.name} has empty description"
            assert len(tool.description) > 10, f"Tool {tool.name} description too short"

    @pytest.mark.asyncio
    async def test_input_schema_is_object_type(self):
        """All inputSchemas should be of type 'object'."""
        import server
        tools = await server.list_tools()
        for tool in tools:
            assert tool.inputSchema.get('type') == 'object', \
                f"Tool {tool.name} inputSchema should be type 'object'"

    @pytest.mark.asyncio
    async def test_input_schema_has_properties(self):
        """All inputSchemas should have 'properties' field."""
        import server
        tools = await server.list_tools()
        for tool in tools:
            assert 'properties' in tool.inputSchema, \
                f"Tool {tool.name} inputSchema missing 'properties'"

    @pytest.mark.asyncio
    async def test_input_schema_has_required(self):
        """All inputSchemas should have 'required' field."""
        import server
        tools = await server.list_tools()
        for tool in tools:
            assert 'required' in tool.inputSchema, \
                f"Tool {tool.name} inputSchema missing 'required'"

    @pytest.mark.asyncio
    async def test_project_path_tools_require_it(self):
        """Tools that use project_path should have it as required."""
        import server
        tools = await server.list_tools()

        # Tools that should require project_path
        tools_needing_project_path = [
            'generate_foundation_docs', 'generate_individual_doc',
            'get_changelog', 'add_changelog_entry', 'update_changelog',
            'establish_standards', 'audit_codebase', 'check_consistency',
            'analyze_project_for_planning', 'create_plan',
        ]

        for tool in tools:
            if tool.name in tools_needing_project_path:
                assert 'project_path' in tool.inputSchema.get('required', []), \
                    f"Tool {tool.name} should require 'project_path'"


class TestSpecificToolSchemas:
    """Test specific tool schema correctness."""

    @pytest.mark.asyncio
    async def test_list_templates_schema(self):
        """list_templates should have no required parameters."""
        import server
        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'list_templates')

        assert tool.inputSchema['required'] == []
        assert tool.inputSchema['properties'] == {}

    @pytest.mark.asyncio
    async def test_get_template_schema(self):
        """get_template should require template_name with enum."""
        import server
        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'get_template')

        assert 'template_name' in tool.inputSchema['required']
        props = tool.inputSchema['properties']
        assert 'template_name' in props
        assert 'enum' in props['template_name']
        assert 'readme' in props['template_name']['enum']
        assert 'architecture' in props['template_name']['enum']

    @pytest.mark.asyncio
    async def test_add_changelog_entry_schema(self):
        """add_changelog_entry should have comprehensive required fields."""
        import server
        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'add_changelog_entry')

        required = tool.inputSchema['required']
        assert 'project_path' in required
        assert 'version' in required
        assert 'change_type' in required
        assert 'severity' in required
        assert 'title' in required
        assert 'description' in required
        assert 'files' in required
        assert 'reason' in required
        assert 'impact' in required

    @pytest.mark.asyncio
    async def test_version_pattern_validation(self):
        """Tools with version should have pattern validation."""
        import server
        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'add_changelog_entry')

        props = tool.inputSchema['properties']
        assert 'pattern' in props['version']
        # Should match X.Y.Z format
        assert '^[0-9]+' in props['version']['pattern']

    @pytest.mark.asyncio
    async def test_assign_agent_task_schema(self):
        """assign_agent_task should validate agent_number range."""
        import server
        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'assign_agent_task')

        props = tool.inputSchema['properties']
        assert 'agent_number' in props
        assert props['agent_number'].get('minimum') == 1
        assert props['agent_number'].get('maximum') == 10


# ============================================================================
# CALL_TOOL TESTS
# ============================================================================

class TestCallTool:
    """Test call_tool() function."""

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool_raises(self):
        """call_tool should raise ValueError for unknown tool."""
        import server

        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool("nonexistent_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_dispatches_to_handler(self):
        """call_tool should dispatch to correct handler."""
        import server
        import tool_handlers

        # Mock a handler
        mock_handler = AsyncMock(return_value=[Mock()])
        original_handlers = tool_handlers.TOOL_HANDLERS.copy()

        try:
            tool_handlers.TOOL_HANDLERS['test_tool'] = mock_handler

            result = await server.call_tool('test_tool', {'arg': 'value'})

            mock_handler.assert_called_once_with({'arg': 'value'})
        finally:
            tool_handlers.TOOL_HANDLERS = original_handlers

    @pytest.mark.asyncio
    async def test_call_tool_returns_handler_result(self):
        """call_tool should return result from handler."""
        import server
        import tool_handlers
        from mcp.types import TextContent

        expected_result = [TextContent(type="text", text="test result")]
        mock_handler = AsyncMock(return_value=expected_result)
        original_handlers = tool_handlers.TOOL_HANDLERS.copy()

        try:
            tool_handlers.TOOL_HANDLERS['test_tool'] = mock_handler

            result = await server.call_tool('test_tool', {})

            assert result == expected_result
        finally:
            tool_handlers.TOOL_HANDLERS = original_handlers

    @pytest.mark.asyncio
    async def test_call_tool_logs_invocation(self):
        """call_tool should log tool invocations."""
        import server
        import tool_handlers

        mock_handler = AsyncMock(return_value=[Mock()])
        original_handlers = tool_handlers.TOOL_HANDLERS.copy()

        try:
            tool_handlers.TOOL_HANDLERS['test_tool'] = mock_handler

            with patch('server.log_tool_call') as mock_log:
                await server.call_tool('test_tool', {'key1': 'val1', 'key2': 'val2'})

                mock_log.assert_called_once_with('test_tool', args_keys=['key1', 'key2'])
        finally:
            tool_handlers.TOOL_HANDLERS = original_handlers


class TestCallToolHandlerRegistry:
    """Test that all listed tools have handlers."""

    @pytest.mark.asyncio
    async def test_all_tools_have_handlers(self):
        """Every tool in list_tools should have a handler in TOOL_HANDLERS."""
        import server
        import tool_handlers

        tools = await server.list_tools()
        tool_names = [t.name for t in tools]

        missing_handlers = []
        for name in tool_names:
            if name not in tool_handlers.TOOL_HANDLERS:
                missing_handlers.append(name)

        assert not missing_handlers, \
            f"Tools missing handlers: {missing_handlers}"

    @pytest.mark.asyncio
    async def test_handlers_are_callable(self):
        """All handlers should be callable (async functions)."""
        import server
        import tool_handlers

        tools = await server.list_tools()

        for tool in tools:
            handler = tool_handlers.TOOL_HANDLERS.get(tool.name)
            assert handler is not None, f"No handler for {tool.name}"
            assert callable(handler), f"Handler for {tool.name} is not callable"


# ============================================================================
# INTEGRATION WITH TOOL_HANDLERS TESTS
# ============================================================================

class TestToolHandlersIntegration:
    """Test integration with tool_handlers module."""

    def test_templates_dir_is_set(self):
        """TEMPLATES_DIR should be set in tool_handlers."""
        import tool_handlers
        # This is called in server.py initialization
        assert hasattr(tool_handlers, 'TEMPLATES_DIR')

    def test_tool_templates_dir_is_set(self):
        """TOOL_TEMPLATES_DIR should be set in tool_handlers."""
        import tool_handlers
        assert hasattr(tool_handlers, 'TOOL_TEMPLATES_DIR')

    def test_handler_registry_not_empty(self):
        """TOOL_HANDLERS should have entries."""
        import tool_handlers
        assert len(tool_handlers.TOOL_HANDLERS) > 0

    def test_handler_registry_has_expected_tools(self):
        """TOOL_HANDLERS should have core tools."""
        import tool_handlers

        expected = [
            'list_templates', 'get_template',
            'generate_foundation_docs', 'generate_individual_doc',
            'get_changelog', 'add_changelog_entry',
        ]

        for tool_name in expected:
            assert tool_name in tool_handlers.TOOL_HANDLERS, \
                f"Expected {tool_name} in TOOL_HANDLERS"


# ============================================================================
# IMPORTS AND DEPENDENCIES TESTS
# ============================================================================

class TestImports:
    """Test that all required imports are present."""

    def test_imports_mcp_server(self):
        """Should import mcp.server.Server."""
        import server
        from mcp.server import Server
        assert Server is not None

    def test_imports_mcp_types(self):
        """Should import mcp.types."""
        import server
        from mcp.types import Tool, TextContent
        assert Tool is not None
        assert TextContent is not None

    def test_imports_tool_handlers(self):
        """Should import tool_handlers."""
        import server
        import tool_handlers
        assert tool_handlers is not None

    def test_imports_constants(self):
        """Should import constants."""
        import server
        from constants import Paths, Files
        assert Paths is not None
        assert Files is not None

    def test_imports_validation(self):
        """Should import validation module."""
        import server
        from validation import validate_project_path_input
        assert validate_project_path_input is not None

    def test_imports_error_responses(self):
        """Should import error_responses module."""
        import server
        from error_responses import ErrorResponse
        assert ErrorResponse is not None

    def test_imports_logger_config(self):
        """Should import logger_config module."""
        import server
        from logger_config import logger, log_tool_call
        assert logger is not None
        assert log_tool_call is not None


# ============================================================================
# MAIN FUNCTION TESTS
# ============================================================================

class TestMainFunction:
    """Test main() function."""

    def test_main_exists(self):
        """main() function should exist."""
        import server
        assert hasattr(server, 'main')
        assert callable(server.main)

    def test_main_is_async(self):
        """main() should be an async function."""
        import server
        import asyncio
        assert asyncio.iscoroutinefunction(server.main)


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_call_tool_with_empty_arguments(self):
        """call_tool should handle empty arguments dict."""
        import server
        import tool_handlers

        mock_handler = AsyncMock(return_value=[Mock()])
        original_handlers = tool_handlers.TOOL_HANDLERS.copy()

        try:
            tool_handlers.TOOL_HANDLERS['test_tool'] = mock_handler

            result = await server.call_tool('test_tool', {})

            mock_handler.assert_called_once_with({})
        finally:
            tool_handlers.TOOL_HANDLERS = original_handlers

    @pytest.mark.asyncio
    async def test_call_tool_preserves_exception_from_handler(self):
        """call_tool should propagate exceptions from handlers."""
        import server
        import tool_handlers

        mock_handler = AsyncMock(side_effect=RuntimeError("Handler error"))
        original_handlers = tool_handlers.TOOL_HANDLERS.copy()

        try:
            tool_handlers.TOOL_HANDLERS['test_tool'] = mock_handler

            with pytest.raises(RuntimeError, match="Handler error"):
                await server.call_tool('test_tool', {})
        finally:
            tool_handlers.TOOL_HANDLERS = original_handlers

    @pytest.mark.asyncio
    async def test_call_tool_logs_unknown_tool(self):
        """call_tool should log error for unknown tool."""
        import server

        with patch.object(server.logger, 'error') as mock_error:
            try:
                await server.call_tool('definitely_not_a_real_tool', {})
            except ValueError:
                pass  # Expected

            # Should have logged error
            mock_error.assert_called()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.asyncio
    async def test_list_tools_performance(self):
        """list_tools should complete quickly."""
        import server
        import time

        start = time.perf_counter()
        for _ in range(100):
            await server.list_tools()
        elapsed = time.perf_counter() - start

        # 100 calls should take less than 1 second
        assert elapsed < 1.0, f"list_tools too slow: {elapsed:.3f}s for 100 calls"

    @pytest.mark.asyncio
    async def test_call_tool_dispatch_performance(self):
        """call_tool dispatch should be fast."""
        import server
        import tool_handlers
        import time

        mock_handler = AsyncMock(return_value=[Mock()])
        original_handlers = tool_handlers.TOOL_HANDLERS.copy()

        try:
            tool_handlers.TOOL_HANDLERS['perf_test'] = mock_handler

            start = time.perf_counter()
            for _ in range(1000):
                await server.call_tool('perf_test', {})
            elapsed = time.perf_counter() - start

            # 1000 dispatches should take less than 1 second
            assert elapsed < 1.0, f"call_tool dispatch too slow: {elapsed:.3f}s for 1000 calls"
        finally:
            tool_handlers.TOOL_HANDLERS = original_handlers


# ============================================================================
# TOOL NAME CONSISTENCY TESTS
# ============================================================================

class TestToolNameConsistency:
    """Test tool naming conventions."""

    @pytest.mark.asyncio
    async def test_tool_names_are_snake_case(self):
        """All tool names should be snake_case."""
        import server
        import re

        tools = await server.list_tools()

        snake_case_pattern = re.compile(r'^[a-z][a-z0-9_]*$')

        non_snake_case = []
        for tool in tools:
            if not snake_case_pattern.match(tool.name):
                non_snake_case.append(tool.name)

        assert not non_snake_case, \
            f"Tool names not in snake_case: {non_snake_case}"

    @pytest.mark.asyncio
    async def test_tool_names_are_unique(self):
        """All tool names should be unique."""
        import server

        tools = await server.list_tools()
        names = [t.name for t in tools]

        duplicates = [n for n in names if names.count(n) > 1]

        assert not duplicates, \
            f"Duplicate tool names: {set(duplicates)}"


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Test security aspects of server configuration."""

    @pytest.mark.asyncio
    async def test_template_name_has_enum_validation(self):
        """Template name should only allow known values."""
        import server

        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'get_template')

        props = tool.inputSchema['properties']
        assert 'enum' in props['template_name'], \
            "template_name should have enum validation"

        # Should not allow path traversal attempts
        allowed = props['template_name']['enum']
        assert '../' not in str(allowed)
        assert '..' not in allowed

    @pytest.mark.asyncio
    async def test_feature_name_pattern_validation(self):
        """Feature name should have pattern validation."""
        import server

        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'create_plan')

        props = tool.inputSchema['properties']
        assert 'pattern' in props['feature_name'], \
            "feature_name should have pattern validation"

        # Pattern should restrict to safe characters
        pattern = props['feature_name']['pattern']
        assert 'a-zA-Z0-9' in pattern

    @pytest.mark.asyncio
    async def test_workorder_id_pattern_validation(self):
        """Workorder ID should have strict pattern validation."""
        import server

        tools = await server.list_tools()
        tool = next(t for t in tools if t.name == 'log_workorder')

        props = tool.inputSchema['properties']
        assert 'pattern' in props['workorder_id'], \
            "workorder_id should have pattern validation"

        # Should match WO-XXX-NNN format
        pattern = props['workorder_id']['pattern']
        assert 'WO-' in pattern
