"""
Integration tests for PlanningAnalyzer with MCP tool integration.

Tests async methods with coderef tools and fallback modes.
Validates end-to-end workorder creation flow.
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from generators.planning_analyzer import PlanningAnalyzer
from mcp_client import call_coderef_tool


class TestPlanningAnalyzerAsync:
    """Test async methods in PlanningAnalyzer."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create PlanningAnalyzer instance for testing."""
        return PlanningAnalyzer(tmp_path)

    @pytest.mark.asyncio
    async def test_analyze_is_async(self, analyzer):
        """Test that analyze() is async method."""
        assert asyncio.iscoroutinefunction(analyzer.analyze)

    @pytest.mark.asyncio
    async def test_find_reference_components_is_async(self, analyzer):
        """Test that find_reference_components() is async."""
        assert asyncio.iscoroutinefunction(analyzer.find_reference_components)

    @pytest.mark.asyncio
    async def test_identify_patterns_is_async(self, analyzer):
        """Test that identify_patterns() is async."""
        assert asyncio.iscoroutinefunction(analyzer.identify_patterns)

    @pytest.mark.asyncio
    async def test_read_inventory_data_is_async(self, analyzer):
        """Test that read_inventory_data() is async."""
        assert asyncio.iscoroutinefunction(analyzer.read_inventory_data)

    @pytest.mark.asyncio
    async def test_identify_gaps_and_risks_is_async(self, analyzer):
        """Test that identify_gaps_and_risks() is async."""
        assert asyncio.iscoroutinefunction(analyzer.identify_gaps_and_risks)


class TestMCPToolIntegration:
    """Test MCP tool integration in analysis methods."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create PlanningAnalyzer instance for testing."""
        return PlanningAnalyzer(tmp_path)

    @pytest.mark.asyncio
    async def test_find_reference_components_with_mock_tool(self, analyzer):
        """Test find_reference_components with mocked coderef_query."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "data": {"component1": {}, "component2": {}, "component3": {}}
            }

            result = await analyzer.find_reference_components()

            # Verify tool was called
            mock_tool.assert_called_once()
            # Verify result structure
            assert "secondary" in result
            assert "total_found" in result
            assert result["total_found"] == 3

    @pytest.mark.asyncio
    async def test_find_reference_components_fallback(self, analyzer):
        """Test find_reference_components falls back on tool error."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.side_effect = Exception("Connection failed")

            result = await analyzer.find_reference_components()

            # Should return fallback structure
            assert "secondary" in result
            assert "total_found" in result
            assert result["total_found"] == 0

    @pytest.mark.asyncio
    async def test_identify_patterns_with_mock_tool(self, analyzer):
        """Test identify_patterns with mocked coderef_patterns."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "data": {
                    "patterns": [
                        "error_handling",
                        "factory_pattern",
                        "singleton_pattern"
                    ]
                }
            }

            result = await analyzer.identify_patterns()

            # Verify tool was called
            mock_tool.assert_called_once()
            # Verify patterns returned
            assert isinstance(result, list)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_identify_patterns_fallback(self, analyzer):
        """Test identify_patterns falls back on tool error."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.side_effect = Exception("Tool unavailable")

            # Create some mock files so fallback doesn't fail
            with patch.object(analyzer, '_scan_source_files', return_value=[]):
                result = await analyzer.identify_patterns()

            # Should return fallback result (possibly empty list)
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_read_inventory_data_with_mock_tool(self, analyzer):
        """Test read_inventory_data with mocked coderef_scan."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "data": {
                    "summary": {
                        "total_elements": 150,
                        "classes": 42,
                        "functions": 87
                    }
                }
            }

            result = await analyzer.read_inventory_data()

            # Verify tool was called
            mock_tool.assert_called_once()
            # Verify result structure
            assert "scan_results" in result
            assert result["source"] == "coderef_scan"

    @pytest.mark.asyncio
    async def test_read_inventory_data_fallback(self, analyzer):
        """Test read_inventory_data falls back on tool error."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.side_effect = Exception("Scan failed")

            result = await analyzer.read_inventory_data()

            # Should return fallback with available/missing keys
            assert "available" in result or "missing" in result

    @pytest.mark.asyncio
    async def test_identify_gaps_and_risks_with_mock_tool(self, analyzer):
        """Test identify_gaps_and_risks with mocked coderef_coverage."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "data": {"coverage_percent": 45}
            }

            # Mock the filesystem checks
            with patch.object(analyzer, 'scan_foundation_docs', return_value={'missing': [], 'available': []}):
                with patch.object(analyzer, 'scan_coding_standards', return_value={'missing': [], 'available': []}):
                    result = await analyzer.identify_gaps_and_risks()

            # Should include coverage gap
            assert isinstance(result, list)
            # Should have coverage warning
            coverage_gaps = [g for g in result if "coverage" in g.lower()]
            assert len(coverage_gaps) > 0

    @pytest.mark.asyncio
    async def test_identify_gaps_and_risks_fallback(self, analyzer):
        """Test identify_gaps_and_risks falls back on tool error."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.side_effect = Exception("Coverage analysis failed")

            # Mock filesystem checks
            with patch.object(analyzer, 'scan_foundation_docs', return_value={'missing': [], 'available': []}):
                with patch.object(analyzer, 'scan_coding_standards', return_value={'missing': [], 'available': []}):
                    result = await analyzer.identify_gaps_and_risks()

            # Should return list of gaps from fallback
            assert isinstance(result, list)


class TestEndToEndWorkorderCreation:
    """Test complete workorder creation flow."""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a minimal test project."""
        # Create basic structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "README.md").write_text("# Test Project")
        return tmp_path

    @pytest.mark.asyncio
    async def test_full_analyze_flow(self, test_project):
        """Test complete analyze() flow with mocked tools."""
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Mock tool responses
            def mock_tool_side_effect(tool_name, args, **kwargs):
                if tool_name == "coderef_query":
                    return {"success": True, "data": {"comp1": {}, "comp2": {}}}
                elif tool_name == "coderef_patterns":
                    return {"success": True, "data": {"patterns": ["pattern1", "pattern2"]}}
                elif tool_name == "coderef_scan":
                    return {"success": True, "data": {"summary": {"total_elements": 100}}}
                elif tool_name == "coderef_coverage":
                    return {"success": True, "data": {"coverage_percent": 75}}
                return {"success": False}

            mock_tool.side_effect = mock_tool_side_effect

            # Run full analysis
            result = await analyzer.analyze()

            # Verify result structure
            assert isinstance(result, dict)
            assert "foundation_docs" in result
            assert "coding_standards" in result
            assert "technology_stack" in result
            assert "project_structure" in result
            assert "key_patterns_identified" in result
            assert "gaps_and_risks" in result

            # Verify tools were called
            assert mock_tool.call_count >= 4


class TestConcurrentExecution:
    """Test concurrent async method execution."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create PlanningAnalyzer instance for testing."""
        return PlanningAnalyzer(tmp_path)

    @pytest.mark.asyncio
    async def test_concurrent_method_calls(self, analyzer):
        """Test multiple async methods running concurrently."""
        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {"success": True, "data": {}}

            # Run multiple methods concurrently
            tasks = [
                analyzer.find_reference_components(),
                analyzer.identify_patterns(),
            ]

            results = await asyncio.gather(*tasks)

            # Should complete without errors
            assert len(results) == 2
            assert all(isinstance(r, (dict, list)) for r in results)


class TestErrorRecovery:
    """Test error recovery and resilience."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create PlanningAnalyzer instance for testing."""
        return PlanningAnalyzer(tmp_path)

    @pytest.mark.asyncio
    async def test_partial_tool_failure(self, analyzer):
        """Test handling when some tools fail but others succeed."""
        call_count = 0

        async def selective_mock_tool(tool_name, args):
            nonlocal call_count
            call_count += 1
            if tool_name == "coderef_query":
                return {"success": True, "data": {"comp1": {}}}
            elif tool_name == "coderef_patterns":
                raise Exception("Patterns tool crashed")
            return {"success": False}

        with patch('generators.planning_analyzer.call_coderef_tool', side_effect=selective_mock_tool):
            # Should not raise exception, should use fallbacks
            result1 = await analyzer.find_reference_components()
            result2 = await analyzer.identify_patterns()

            # Both should return results (one from tool, one from fallback)
            assert result1 is not None
            assert result2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
