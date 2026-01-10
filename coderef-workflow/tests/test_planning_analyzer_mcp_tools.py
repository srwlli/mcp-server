"""
Unit tests for PlanningAnalyzer MCP tool integration.

Tests the 4 new MCP tool methods:
- analyze_dependencies() - Uses coderef_query
- analyze_impact() - Uses coderef_impact
- analyze_complexity() - Uses coderef_complexity
- generate_architecture_diagram() - Uses coderef_diagram

Also tests telemetry tracking for data source usage.
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Import the analyzer
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from generators.planning_analyzer import PlanningAnalyzer


class TestAnalyzeDependencies:
    """Test analyze_dependencies() method using coderef_query."""

    @pytest.mark.asyncio
    async def test_analyze_dependencies_success(self, tmp_path):
        """Test successful dependency analysis."""
        analyzer = PlanningAnalyzer(tmp_path)

        # Mock successful coderef_query response
        mock_response = {
            "success": True,
            "data": {
                "target": "AuthService",
                "dependencies": ["UserController", "LoginHandler"],
                "count": 2
            }
        }

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.analyze_dependencies("AuthService")

            # Verify tool was called correctly
            mock_call.assert_called_once_with(
                "coderef_query",
                {
                    "project_path": str(tmp_path),
                    "query_type": "depends-on-me",
                    "target": "AuthService",
                    "max_depth": 2
                }
            )

            # Verify result
            assert result is not None
            assert result["target"] == "AuthService"
            assert result["count"] == 2

            # Verify telemetry tracking
            assert len(analyzer.telemetry['mcp_tool_calls']) == 1
            assert analyzer.telemetry['mcp_tool_calls'][0]['tool'] == 'coderef_query'
            assert analyzer.telemetry['mcp_tool_calls'][0]['success'] is True

    @pytest.mark.asyncio
    async def test_analyze_dependencies_failure(self, tmp_path):
        """Test dependency analysis when tool fails."""
        analyzer = PlanningAnalyzer(tmp_path)

        # Mock failed response
        mock_response = {"success": False, "error": "Element not found"}

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.analyze_dependencies("NonExistent")

            # Verify returns None on failure
            assert result is None

            # Verify telemetry tracked failure
            assert len(analyzer.telemetry['mcp_tool_calls']) == 1
            assert analyzer.telemetry['mcp_tool_calls'][0]['success'] is False

    @pytest.mark.asyncio
    async def test_analyze_dependencies_exception(self, tmp_path):
        """Test dependency analysis when tool raises exception."""
        analyzer = PlanningAnalyzer(tmp_path)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("Connection error")

            result = await analyzer.analyze_dependencies("AuthService")

            # Verify graceful failure
            assert result is None


class TestAnalyzeImpact:
    """Test analyze_impact() method using coderef_impact."""

    @pytest.mark.asyncio
    async def test_analyze_impact_modify(self, tmp_path):
        """Test impact analysis for modify operation."""
        analyzer = PlanningAnalyzer(tmp_path)

        mock_response = {
            "success": True,
            "data": {
                "element": "UserService",
                "operation": "modify",
                "affected_elements": ["UserController", "ProfileHandler", "AuthMiddleware"],
                "risk_level": "medium"
            }
        }

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.analyze_impact("UserService", "modify")

            # Verify tool was called correctly
            mock_call.assert_called_once_with(
                "coderef_impact",
                {
                    "project_path": str(tmp_path),
                    "element": "UserService",
                    "operation": "modify",
                    "max_depth": 3
                }
            )

            # Verify result
            assert result is not None
            assert len(result["affected_elements"]) == 3
            assert result["risk_level"] == "medium"

            # Verify telemetry
            assert analyzer.telemetry['mcp_tool_calls'][0]['tool'] == 'coderef_impact'

    @pytest.mark.asyncio
    async def test_analyze_impact_delete(self, tmp_path):
        """Test impact analysis for delete operation."""
        analyzer = PlanningAnalyzer(tmp_path)

        mock_response = {
            "success": True,
            "data": {
                "element": "LegacyService",
                "operation": "delete",
                "affected_elements": [],
                "risk_level": "low"
            }
        }

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.analyze_impact("LegacyService", "delete")

            # Verify zero affected elements (safe to delete)
            assert len(result["affected_elements"]) == 0


class TestAnalyzeComplexity:
    """Test analyze_complexity() method using coderef_complexity."""

    @pytest.mark.asyncio
    async def test_analyze_complexity_success(self, tmp_path):
        """Test successful complexity analysis."""
        analyzer = PlanningAnalyzer(tmp_path)

        mock_response = {
            "success": True,
            "data": {
                "element": "PaymentProcessor",
                "cyclomatic_complexity": 15,
                "cognitive_complexity": 22,
                "lines_of_code": 340,
                "difficulty": "high"
            }
        }

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.analyze_complexity("PaymentProcessor")

            # Verify tool called correctly
            mock_call.assert_called_once_with(
                "coderef_complexity",
                {
                    "project_path": str(tmp_path),
                    "element": "PaymentProcessor"
                }
            )

            # Verify result
            assert result["cyclomatic_complexity"] == 15
            assert result["difficulty"] == "high"

            # Verify telemetry
            assert analyzer.telemetry['mcp_tool_calls'][0]['tool'] == 'coderef_complexity'


class TestGenerateArchitectureDiagram:
    """Test generate_architecture_diagram() method using coderef_diagram."""

    @pytest.mark.asyncio
    async def test_generate_diagram_dependencies(self, tmp_path):
        """Test dependency diagram generation."""
        analyzer = PlanningAnalyzer(tmp_path)

        mock_diagram = """graph LR
    A[UserService] --> B[AuthService]
    B --> C[TokenService]"""

        mock_response = {
            "success": True,
            "data": {
                "diagram": mock_diagram,
                "format": "mermaid",
                "node_count": 3
            }
        }

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.generate_architecture_diagram("dependencies", depth=2)

            # Verify tool called correctly
            mock_call.assert_called_once_with(
                "coderef_diagram",
                {
                    "project_path": str(tmp_path),
                    "diagram_type": "dependencies",
                    "format": "mermaid",
                    "depth": 2
                }
            )

            # Verify result
            assert "UserService" in result
            assert "AuthService" in result
            assert "graph LR" in result

            # Verify telemetry
            assert analyzer.telemetry['mcp_tool_calls'][0]['tool'] == 'coderef_diagram'

    @pytest.mark.asyncio
    async def test_generate_diagram_calls(self, tmp_path):
        """Test call graph diagram generation."""
        analyzer = PlanningAnalyzer(tmp_path)

        mock_response = {
            "success": True,
            "data": {
                "diagram": "graph TD\n    login --> authenticate\n    authenticate --> validateToken",
                "format": "mermaid"
            }
        }

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await analyzer.generate_architecture_diagram("calls", depth=3)

            # Verify diagram type parameter
            call_args = mock_call.call_args[0][1]
            assert call_args["diagram_type"] == "calls"
            assert call_args["depth"] == 3


class TestTelemetryTracking:
    """Test telemetry tracking functionality."""

    def test_telemetry_initialization(self, tmp_path):
        """Test telemetry dict is initialized correctly."""
        analyzer = PlanningAnalyzer(tmp_path)

        assert 'coderef_file_reads' in analyzer.telemetry
        assert 'mcp_tool_calls' in analyzer.telemetry
        assert 'foundation_doc_reads' in analyzer.telemetry
        assert analyzer.telemetry['total_sources_used'] == 0

    def test_track_coderef_file_read(self, tmp_path):
        """Test _track_coderef_file_read() helper."""
        analyzer = PlanningAnalyzer(tmp_path)

        analyzer._track_coderef_file_read('.coderef/index.json')

        assert len(analyzer.telemetry['coderef_file_reads']) == 1
        assert analyzer.telemetry['coderef_file_reads'][0] == '.coderef/index.json'
        assert analyzer.telemetry['total_sources_used'] == 1

    def test_track_mcp_tool_call(self, tmp_path):
        """Test _track_mcp_tool_call() helper."""
        analyzer = PlanningAnalyzer(tmp_path)

        analyzer._track_mcp_tool_call('coderef_query', True)
        analyzer._track_mcp_tool_call('coderef_impact', False)

        assert len(analyzer.telemetry['mcp_tool_calls']) == 2
        assert analyzer.telemetry['mcp_tool_calls'][0]['tool'] == 'coderef_query'
        assert analyzer.telemetry['mcp_tool_calls'][0]['success'] is True
        assert analyzer.telemetry['mcp_tool_calls'][1]['success'] is False
        assert analyzer.telemetry['total_sources_used'] == 2

    def test_track_foundation_doc_read(self, tmp_path):
        """Test _track_foundation_doc_read() helper."""
        analyzer = PlanningAnalyzer(tmp_path)

        analyzer._track_foundation_doc_read('ARCHITECTURE.md')

        assert len(analyzer.telemetry['foundation_doc_reads']) == 1
        assert analyzer.telemetry['foundation_doc_reads'][0] == 'ARCHITECTURE.md'
        assert analyzer.telemetry['total_sources_used'] == 1

    def test_get_telemetry_summary(self, tmp_path):
        """Test get_telemetry_summary() generates correct statistics."""
        analyzer = PlanningAnalyzer(tmp_path)

        # Simulate various data source usage
        analyzer._track_coderef_file_read('.coderef/index.json')
        analyzer._track_coderef_file_read('.coderef/reports/patterns.json')
        analyzer._track_mcp_tool_call('coderef_query', True)
        analyzer._track_mcp_tool_call('coderef_impact', True)
        analyzer._track_mcp_tool_call('coderef_diagram', False)
        analyzer._track_foundation_doc_read('ARCHITECTURE.md')

        summary = analyzer.get_telemetry_summary()

        # Verify counts
        assert summary['total_sources_used'] == 6
        assert summary['coderef_file_reads']['count'] == 2
        assert summary['mcp_tool_calls']['count'] == 3
        assert summary['mcp_tool_calls']['success_count'] == 2
        assert summary['foundation_doc_reads']['count'] == 1

        # Verify percentages (approximately)
        assert abs(summary['coderef_file_reads']['percentage'] - 33.33) < 0.1
        assert abs(summary['mcp_tool_calls']['percentage'] - 50.0) < 0.1
        assert abs(summary['foundation_doc_reads']['percentage'] - 16.67) < 0.1

        # Verify lists
        assert '.coderef/index.json' in summary['coderef_file_reads']['files']
        assert 'coderef_query' in summary['mcp_tool_calls']['tools']
        assert 'ARCHITECTURE.md' in summary['foundation_doc_reads']['docs']


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for tests."""
    return tmp_path_factory.mktemp("test_project")
