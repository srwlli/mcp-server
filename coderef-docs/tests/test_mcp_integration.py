"""
Unit tests for MCP integration helper module.

Tests the orchestration pattern for coderef-context MCP tool integration.
"""

import pytest
from pathlib import Path
from mcp_integration import (
    get_scan_instructions,
    get_query_instructions,
    format_scan_request,
    format_query_request,
    process_scan_response,
    process_query_response
)


class TestGetScanInstructions:
    """Test get_scan_instructions function."""

    def test_returns_correct_structure(self):
        """Verify instruction dict has all required fields."""
        project_path = Path("/test/project")
        result = get_scan_instructions(project_path)

        assert result['action'] == 'call_mcp_tool'
        assert result['tool_name'] == 'coderef_scan'
        assert 'description' in result
        assert 'example_call' in result
        assert 'expected_response' in result
        assert 'next_step' in result

    def test_example_call_has_project_path(self):
        """Verify example call includes project path."""
        project_path = Path("/test/project")
        result = get_scan_instructions(project_path)

        assert result['example_call']['project_path'] == str(project_path)
        assert 'languages' in result['example_call']
        assert 'use_ast' in result['example_call']

    def test_expected_response_structure(self):
        """Verify expected response format is documented."""
        project_path = Path("/test/project")
        result = get_scan_instructions(project_path)

        expected = result['expected_response']
        assert 'elements' in expected
        assert 'total_count' in expected
        assert 'scan_time_ms' in expected


class TestGetQueryInstructions:
    """Test get_query_instructions function."""

    def test_returns_correct_structure(self):
        """Verify instruction dict has all required fields."""
        project_path = Path("/test/project")
        result = get_query_instructions(project_path, "calls", "AuthService")

        assert result['action'] == 'call_mcp_tool'
        assert result['tool_name'] == 'coderef_query'
        assert 'description' in result
        assert 'example_call' in result
        assert 'expected_response' in result

    def test_example_call_includes_parameters(self):
        """Verify example call includes all parameters."""
        project_path = Path("/test/project")
        result = get_query_instructions(project_path, "imports", "UserService")

        call = result['example_call']
        assert call['project_path'] == str(project_path)
        assert call['query_type'] == "imports"
        assert call['target'] == "UserService"
        assert call['max_depth'] == 3


class TestFormatScanRequest:
    """Test format_scan_request function."""

    def test_returns_formatted_string(self):
        """Verify returns a formatted instruction string."""
        project_path = Path("/test/project")
        result = format_scan_request(project_path)

        assert isinstance(result, str)
        assert "mcp__coderef_context__coderef_scan" in result
        assert str(project_path) in result

    def test_includes_languages_parameter(self):
        """Verify languages are included in formatted string."""
        project_path = Path("/test/project")
        result = format_scan_request(project_path, languages=["py", "js"])

        assert "['py', 'js']" in result or '["py", "js"]' in result

    def test_uses_default_languages_when_none_provided(self):
        """Verify default languages used when not specified."""
        project_path = Path("/test/project")
        result = format_scan_request(project_path)

        # Should include default languages
        assert "ts" in result or "tsx" in result or "py" in result


class TestFormatQueryRequest:
    """Test format_query_request function."""

    def test_returns_formatted_string(self):
        """Verify returns a formatted instruction string."""
        project_path = Path("/test/project")
        result = format_query_request(project_path, "calls", "AuthService")

        assert isinstance(result, str)
        assert "mcp__coderef_context__coderef_query" in result
        assert str(project_path) in result
        assert "AuthService" in result

    def test_includes_all_parameters(self):
        """Verify all parameters included in formatted string."""
        project_path = Path("/test/project")
        result = format_query_request(project_path, "imports", "UserService", max_depth=5)

        assert "imports" in result
        assert "UserService" in result
        assert "5" in result  # max_depth


class TestProcessScanResponse:
    """Test process_scan_response function."""

    def test_categorizes_functions(self):
        """Verify functions are categorized correctly."""
        response = {
            'elements': [
                {'name': 'getUserById', 'type': 'function'},
                {'name': 'createUser', 'type': 'function'}
            ]
        }

        result = process_scan_response(response)

        assert len(result['functions']) == 2
        assert result['functions'][0]['name'] == 'getUserById'

    def test_categorizes_classes(self):
        """Verify classes are categorized correctly."""
        response = {
            'elements': [
                {'name': 'UserService', 'type': 'class'},
                {'name': 'AuthService', 'type': 'class'}
            ]
        }

        result = process_scan_response(response)

        assert len(result['classes']) == 2
        assert result['classes'][0]['name'] == 'UserService'

    def test_categorizes_components(self):
        """Verify components are categorized correctly."""
        response = {
            'elements': [
                {'name': 'UserProfile', 'type': 'component'},
                {'name': 'LoginForm', 'type': 'component'}
            ]
        }

        result = process_scan_response(response)

        assert len(result['components']) == 2
        assert result['components'][0]['name'] == 'UserProfile'

    def test_categorizes_interfaces(self):
        """Verify interfaces are categorized correctly."""
        response = {
            'elements': [
                {'name': 'IUser', 'type': 'interface'}
            ]
        }

        result = process_scan_response(response)

        assert len(result['interfaces']) == 1
        assert result['interfaces'][0]['name'] == 'IUser'

    def test_all_elements_preserved(self):
        """Verify all elements preserved in 'all' category."""
        response = {
            'elements': [
                {'name': 'func1', 'type': 'function'},
                {'name': 'Class1', 'type': 'class'},
                {'name': 'IFace1', 'type': 'interface'}
            ]
        }

        result = process_scan_response(response)

        assert len(result['all']) == 3

    def test_handles_empty_response(self):
        """Verify handles empty element list."""
        response = {'elements': []}

        result = process_scan_response(response)

        assert len(result['functions']) == 0
        assert len(result['classes']) == 0
        assert len(result['components']) == 0


class TestProcessQueryResponse:
    """Test process_query_response function."""

    def test_processes_callers(self):
        """Verify callers are extracted correctly."""
        response = {
            'relationships': [
                {'type': 'called_by', 'source': 'main', 'target': 'getUserById'}
            ]
        }

        result = process_query_response(response)

        assert len(result['callers']) == 1
        assert result['callers'][0] == 'main'

    def test_processes_callees(self):
        """Verify callees are extracted correctly."""
        response = {
            'relationships': [
                {'type': 'calls', 'source': 'getUserById', 'target': 'findUser'}
            ]
        }

        result = process_query_response(response)

        assert len(result['callees']) == 1
        assert result['callees'][0] == 'findUser'

    def test_processes_importers(self):
        """Verify importers are extracted correctly."""
        response = {
            'relationships': [
                {'type': 'imported_by', 'source': 'app.py', 'target': 'UserService'}
            ]
        }

        result = process_query_response(response)

        assert len(result['importers']) == 1
        assert result['importers'][0] == 'app.py'

    def test_processes_imports(self):
        """Verify imports are extracted correctly."""
        response = {
            'relationships': [
                {'type': 'imports', 'source': 'UserService', 'target': 'Database'}
            ]
        }

        result = process_query_response(response)

        assert len(result['imports']) == 1
        assert result['imports'][0] == 'Database'

    def test_processes_dependencies(self):
        """Verify dependencies are extracted correctly."""
        response = {
            'relationships': [
                {'type': 'depends_on', 'source': 'UserService', 'target': 'AuthService'}
            ]
        }

        result = process_query_response(response)

        assert len(result['dependencies']) == 1
        assert result['dependencies'][0] == 'AuthService'

    def test_handles_empty_relationships(self):
        """Verify handles empty relationship list."""
        response = {'relationships': []}

        result = process_query_response(response)

        assert len(result['callers']) == 0
        assert len(result['callees']) == 0
        assert len(result['importers']) == 0
        assert len(result['imports']) == 0
        assert len(result['dependencies']) == 0

    def test_handles_mixed_relationships(self):
        """Verify handles multiple relationship types."""
        response = {
            'relationships': [
                {'type': 'calls', 'source': 'A', 'target': 'B'},
                {'type': 'called_by', 'source': 'C', 'target': 'A'},
                {'type': 'imports', 'source': 'A', 'target': 'D'}
            ]
        }

        result = process_query_response(response)

        assert len(result['callees']) == 1
        assert len(result['callers']) == 1
        assert len(result['imports']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
