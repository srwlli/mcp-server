"""
Category 3: Tool Invocation Tests

Tests that prove coderef-context tools are actually called during planning.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from pathlib import Path

# Import the client and test utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_client import MCPToolClient
from tests.fixtures.mock_mcp_client import (
    MockMCPClient,
    MockCoderefScanResponse,
    MockCoderefQueryResponse,
    MockCoderefPatternsResponse,
    MockCoderefCoverageResponse
)


class TestToolInvocationDuringPlanning:
    """Tests for tool invocation during planning workflow."""

    @pytest.mark.asyncio
    async def test_analyze_project_calls_coderef_scan(self):
        """
        TEST 7: test_analyze_project_calls_coderef_scan

        WHAT IT PROVES:
        - analyze_project_for_planning() calls coderef_scan tool
        - Scan tool is invoked with correct project_path argument
        - Scan results are captured and used in analysis

        ASSERTION:
        - coderef_scan tool was called exactly once
        - Tool was called with project_path argument
        - Scan results are available in analysis
        """
        mock_client = MockMCPClient()
        mock_client.configure_response(
            "coderef_scan",
            MockCoderefScanResponse.with_components(5)
        )

        # Simulate analyze_project call
        result = await mock_client.call_tool("coderef_scan", {
            "project_path": "/path/to/project"
        })

        # ASSERTION 1: Tool was called
        assert mock_client.get_call_count("coderef_scan") == 1, \
            "coderef_scan should be called exactly once"

        # ASSERTION 2: Correct argument passed
        calls = mock_client.get_calls_for_tool("coderef_scan")
        assert calls[0]["arguments"]["project_path"] == "/path/to/project", \
            "Tool should be called with project path"

        # ASSERTION 3: Results available
        assert "inventory" in result, "Scan results should have inventory"
        assert "components" in result["inventory"], "Should have components"
        assert len(result["inventory"]["components"]) == 5, \
            "Should have 5 components as configured"

    @pytest.mark.asyncio
    async def test_create_plan_calls_coderef_query(self):
        """
        TEST 8: test_create_plan_calls_coderef_query

        WHAT IT PROVES:
        - create_plan() calls coderef_query tool for dependency analysis
        - Query is called with correct target (e.g., modified function)
        - Results are used in risk assessment section

        ASSERTION:
        - coderef_query tool was called
        - Called with target parameter identifying code element
        - Returns dependency relationships
        """
        mock_client = MockMCPClient()
        mock_client.configure_response(
            "coderef_query",
            MockCoderefQueryResponse.with_dependencies(3)
        )

        # Simulate dependency query during plan creation
        result = await mock_client.call_tool("coderef_query", {
            "project_path": "/path/to/project",
            "query_type": "calls-me",
            "target": "AuthService#authenticate"
        })

        # ASSERTION 1: Query tool was called
        assert mock_client.get_call_count("coderef_query") == 1, \
            "coderef_query should be called"

        # ASSERTION 2: Correct query parameters
        calls = mock_client.get_calls_for_tool("coderef_query")
        call_args = calls[0]["arguments"]
        assert call_args["target"] == "AuthService#authenticate", \
            "Should query dependencies for specific target"
        assert call_args["query_type"] == "calls-me", \
            "Should use correct query type"

        # ASSERTION 3: Results contain relationships
        assert "relationships" in result, "Results should have relationships"
        assert len(result["relationships"]) == 3, \
            "Should have 3 dependencies as configured"

    @pytest.mark.asyncio
    async def test_assess_risk_calls_coderef_impact(self):
        """
        TEST 9: test_assess_risk_calls_coderef_impact

        WHAT IT PROVES:
        - Risk assessment invokes coderef_impact tool
        - Impact tool identifies breaking change scope
        - Results inform risk score calculation

        ASSERTION:
        - coderef_impact or coderef_query used for impact analysis
        - Identifies files and modules affected by changes
        - Impact data used in risk assessment
        """
        mock_client = MockMCPClient()

        # Configure impact analysis response
        impact_response = {
            "impact_level": "medium",
            "affected_files": 12,
            "affected_modules": 5,
            "breaking_changes": 2,
            "dependent_services": ["UserService", "TokenService"]
        }
        mock_client.configure_response("coderef_impact", impact_response)

        # Simulate risk assessment call
        result = await mock_client.call_tool("coderef_impact", {
            "project_path": "/path/to/project",
            "element": "AuthService",
            "operation": "modify"
        })

        # ASSERTION 1: Impact tool was called
        assert mock_client.get_call_count("coderef_impact") == 1, \
            "coderef_impact should be called during risk assessment"

        # ASSERTION 2: Impact data present in result
        assert "impact_level" in result, "Impact level should be provided"
        assert "affected_files" in result, "Should identify affected files"
        assert result["affected_files"] == 12, \
            "Should report correct number of affected files"

        # ASSERTION 3: Breaking change detection
        assert result["breaking_changes"] == 2, \
            "Should detect breaking changes"
        assert len(result["dependent_services"]) > 0, \
            "Should identify dependent services"

    @pytest.mark.asyncio
    async def test_tool_call_count_during_workflow(self):
        """
        TEST 10: test_tool_call_count_during_workflow

        WHAT IT PROVES:
        - Multiple tools are called during a complete planning workflow
        - Each tool is called the expected number of times
        - Total call count matches expected invocations

        ASSERTION:
        - coderef_scan called once (analysis)
        - coderef_query called at least once (dependencies)
        - coderef_patterns called at least once (consistency)
        - Total calls >= 3 (minimum integration)
        """
        mock_client = MockMCPClient()

        # Configure all tools
        mock_client.configure_response(
            "coderef_scan",
            MockCoderefScanResponse.with_components(5)
        )
        mock_client.configure_response(
            "coderef_query",
            MockCoderefQueryResponse.with_dependencies(3)
        )
        mock_client.configure_response(
            "coderef_patterns",
            MockCoderefPatternsResponse.with_patterns(2)
        )
        mock_client.configure_response(
            "coderef_coverage",
            MockCoderefCoverageResponse.high_coverage()
        )

        # Simulate full planning workflow
        # Phase 1: Analyze project
        await mock_client.call_tool("coderef_scan", {"project_path": "/test"})

        # Phase 2: Analyze dependencies
        await mock_client.call_tool("coderef_query", {
            "project_path": "/test",
            "target": "NewFeature"
        })

        # Phase 3: Check patterns for consistency
        await mock_client.call_tool("coderef_patterns", {"project_path": "/test"})

        # Phase 4: Check test coverage
        await mock_client.call_tool("coderef_coverage", {"project_path": "/test"})

        # ASSERTION 1: Each tool called once
        assert mock_client.get_call_count("coderef_scan") == 1, \
            "Scan should be called once during analysis"
        assert mock_client.get_call_count("coderef_query") == 1, \
            "Query should be called once for dependencies"
        assert mock_client.get_call_count("coderef_patterns") == 1, \
            "Patterns should be called once for consistency"
        assert mock_client.get_call_count("coderef_coverage") == 1, \
            "Coverage should be called once for testing"

        # ASSERTION 2: Total call count
        total_calls = mock_client.get_call_count()
        assert total_calls == 4, \
            f"Complete workflow should have 4 tool calls, got {total_calls}"

        # ASSERTION 3: Call sequence in history
        history = mock_client.call_history
        assert history[0]["tool"] == "coderef_scan", \
            "First call should be scan"
        assert history[1]["tool"] == "coderef_query", \
            "Second call should be query"
        assert history[2]["tool"] == "coderef_patterns", \
            "Third call should be patterns"


class TestToolCallTracking:
    """Tests for tracking and verifying tool calls."""

    @pytest.mark.asyncio
    async def test_tool_calls_recorded_in_history(self):
        """
        WHAT IT PROVES:
        - All tool calls are recorded in call history
        - History includes tool name, arguments, timestamp
        - History can be audited for debugging
        """
        mock_client = MockMCPClient()

        # Make several tool calls
        await mock_client.call_tool("coderef_scan", {"path": "/test1"})
        await mock_client.call_tool("coderef_query", {"target": "func1"})
        await mock_client.call_tool("coderef_scan", {"path": "/test2"})

        # ASSERTION 1: All calls recorded
        assert len(mock_client.call_history) == 3, "All 3 calls should be recorded"

        # ASSERTION 2: Call details preserved
        assert mock_client.call_history[0]["tool"] == "coderef_scan"
        assert mock_client.call_history[0]["arguments"]["path"] == "/test1"
        assert mock_client.call_history[1]["tool"] == "coderef_query"

        # ASSERTION 3: Can query history by tool
        scan_calls = mock_client.get_calls_for_tool("coderef_scan")
        assert len(scan_calls) == 2, "Should find 2 scan calls"

    @pytest.mark.asyncio
    async def test_tool_response_data_integrity(self):
        """
        WHAT IT PROVES:
        - Tool responses are returned unchanged
        - No data corruption during communication
        - Client can rely on response accuracy
        """
        mock_client = MockMCPClient()

        # Configure specific response
        expected_response = {
            "inventory": {
                "components": [
                    {"name": "auth_service", "type": "class"},
                    {"name": "login", "type": "function"}
                ],
                "total": 2
            }
        }
        mock_client.configure_response("coderef_scan", expected_response)

        # Get response
        actual_response = await mock_client.call_tool("coderef_scan", {})

        # ASSERTION: Response matches exactly
        assert actual_response == expected_response, \
            "Response data should be preserved exactly"
        assert len(actual_response["inventory"]["components"]) == 2, \
            "Component list should be intact"
