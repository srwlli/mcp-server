"""
MCP Tool Integration Tests for coderef-testing Server

Tests all 14 MCP tools exposed by the server to ensure correct
request handling, response formatting, and error handling.
"""

import pytest
import json
from pathlib import Path

# Import server handlers
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server import (
    handle_discover_tests,
    handle_list_frameworks,
    handle_run_all_tests,
    handle_run_test_file,
    handle_run_test_category,
    handle_run_tests_parallel,
    handle_get_test_results,
    handle_aggregate_results,
    handle_generate_test_report,
    handle_compare_test_runs,
    handle_analyze_coverage,
    handle_detect_flaky_tests,
    handle_analyze_test_performance,
    handle_validate_test_health
)


class TestDiscoveryTools:
    """Test MCP discovery tools (2 tools)"""

    @pytest.mark.asyncio
    async def test_discover_tests_tool(self, pytest_project):
        """Test discover_tests MCP tool"""
        args = {"project_path": str(pytest_project)}

        response = await handle_discover_tests(args)

        assert len(response) == 1
        content = response[0]
        assert content.type == "text"

        # Parse JSON response
        data = json.loads(content.text)
        assert "frameworks" in data
        assert "test_count" in data
        assert isinstance(data["frameworks"], list)
        assert isinstance(data["test_count"], int)

    @pytest.mark.asyncio
    async def test_list_test_frameworks_tool(self, pytest_project):
        """Test list_test_frameworks MCP tool"""
        args = {"project_path": str(pytest_project)}

        response = await handle_list_frameworks(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "framework_count" in data
        assert "frameworks" in data
        assert data["framework_count"] >= 1


class TestExecutionTools:
    """Test MCP execution tools (4 tools)"""

    @pytest.mark.asyncio
    async def test_run_all_tests_tool(self, pytest_project):
        """Test run_all_tests MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "framework": "pytest",
            "parallel_workers": 2,
            "timeout": 30
        }

        response = await handle_run_all_tests(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "framework" in data
        assert "summary" in data
        assert "test_count" in data

    @pytest.mark.asyncio
    async def test_run_test_file_tool(self, pytest_project):
        """Test run_test_file MCP tool"""
        # Create specific test file
        test_file = pytest_project / "tests" / "test_specific.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_example():\n    assert True")

        args = {
            "project_path": str(pytest_project),
            "test_file": "tests/test_specific.py"
        }

        response = await handle_run_test_file(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "test_file" in data
        assert data["test_file"] == "tests/test_specific.py"
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_run_test_category_tool(self, pytest_project):
        """Test run_test_category MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "pattern": "test_example"
        }

        response = await handle_run_test_category(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "pattern" in data
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_run_tests_in_parallel_tool(self, pytest_project):
        """Test run_tests_in_parallel MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "parallel_workers": 4
        }

        response = await handle_run_tests_parallel(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "workers" in data
        assert data["workers"] == 4
        assert "summary" in data


class TestManagementTools:
    """Test MCP management tools (4 tools)"""

    @pytest.mark.asyncio
    async def test_get_test_results_tool(self, pytest_project):
        """Test get_test_results MCP tool"""
        args = {"project_path": str(pytest_project)}

        response = await handle_get_test_results(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "total_runs" in data or "results" in data

    @pytest.mark.asyncio
    async def test_aggregate_results_tool(self, pytest_project):
        """Test aggregate_results MCP tool"""
        args = {"project_path": str(pytest_project)}

        response = await handle_aggregate_results(args)

        assert len(response) == 1
        # Response may be "No archived results" or actual data
        assert response[0].type == "text"

    @pytest.mark.asyncio
    async def test_generate_test_report_tool(self, pytest_project):
        """Test generate_test_report MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "format": "markdown"
        }

        response = await handle_generate_test_report(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "format" in data or "message" in data

    @pytest.mark.asyncio
    async def test_compare_test_runs_tool(self, pytest_project):
        """Test compare_test_runs MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "date1": "2025-12-01",
            "date2": "2025-12-30"
        }

        response = await handle_compare_test_runs(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "comparison" in data or "message" in data


class TestAnalysisTools:
    """Test MCP analysis tools (4 tools)"""

    @pytest.mark.asyncio
    async def test_analyze_coverage_tool(self, pytest_project):
        """Test analyze_coverage MCP tool"""
        args = {"project_path": str(pytest_project)}

        response = await handle_analyze_coverage(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        # Response contains analysis results or error message
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_detect_flaky_tests_tool(self, pytest_project):
        """Test detect_flaky_tests MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "runs": 5
        }

        response = await handle_detect_flaky_tests(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert "runs_analyzed" in data or "message" in data

    @pytest.mark.asyncio
    async def test_analyze_test_performance_tool(self, pytest_project):
        """Test analyze_test_performance MCP tool"""
        args = {
            "project_path": str(pytest_project),
            "threshold": 1.0
        }

        response = await handle_analyze_test_performance(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_validate_test_health_tool(self, pytest_project):
        """Test validate_test_health MCP tool"""
        args = {"project_path": str(pytest_project)}

        response = await handle_validate_test_health(args)

        assert len(response) == 1
        data = json.loads(response[0].text)
        assert isinstance(data, dict)


class TestErrorHandling:
    """Test error handling across all tools"""

    @pytest.mark.asyncio
    async def test_discover_tests_invalid_path(self):
        """Test discover_tests with invalid path"""
        args = {"project_path": "/nonexistent/path"}

        response = await handle_discover_tests(args)

        assert len(response) == 1
        text = response[0].text
        assert "Error" in text or "error" in text

    @pytest.mark.asyncio
    async def test_run_all_tests_missing_framework(self, tmp_path):
        """Test run_all_tests when framework cannot be detected"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        args = {"project_path": str(empty_dir)}

        response = await handle_run_all_tests(args)

        assert len(response) == 1
        # Should handle gracefully (error message or empty result)

    @pytest.mark.asyncio
    async def test_run_test_file_nonexistent_file(self, pytest_project):
        """Test run_test_file with non-existent file"""
        args = {
            "project_path": str(pytest_project),
            "test_file": "tests/nonexistent.py"
        }

        response = await handle_run_test_file(args)

        assert len(response) == 1
        text = response[0].text
        assert "Error" in text or "error" in text


class TestResponseFormat:
    """Test response format compliance"""

    @pytest.mark.asyncio
    async def test_all_tools_return_text_content(self, pytest_project):
        """Verify all tools return TextContent responses"""
        from mcp.types import TextContent

        test_cases = [
            (handle_discover_tests, {"project_path": str(pytest_project)}),
            (handle_list_frameworks, {"project_path": str(pytest_project)}),
            (handle_get_test_results, {"project_path": str(pytest_project)}),
            (handle_aggregate_results, {"project_path": str(pytest_project)}),
        ]

        for handler, args in test_cases:
            response = await handler(args)

            assert isinstance(response, list)
            assert len(response) >= 1
            for item in response:
                assert isinstance(item, TextContent)
                assert item.type == "text"
                assert isinstance(item.text, str)

    @pytest.mark.asyncio
    async def test_json_responses_are_valid(self, pytest_project):
        """Verify JSON responses are properly formatted"""
        args = {"project_path": str(pytest_project)}

        response = await handle_discover_tests(args)
        text = response[0].text

        # Should be valid JSON
        data = json.loads(text)
        assert isinstance(data, dict)


# Fixtures

@pytest.fixture
def pytest_project(tmp_path):
    """Create a minimal pytest project for testing"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create pyproject.toml
    (project_dir / "pyproject.toml").write_text("""
[tool.pytest.ini_options]
testpaths = ["tests"]
""")

    # Create test directory
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    # Create sample test file
    (tests_dir / "test_sample.py").write_text("""
def test_example():
    assert 1 + 1 == 2

def test_another():
    assert True
""")

    return project_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
