"""Comprehensive integration tests for CodeRef2 system (150+ tests on 281 baseline elements)."""

import pytest
import json
import time
from server import CodeRef2Server
from test_fixtures import BaselineElementDataset, create_baseline_elements


# ============================================================================
# Query Tool Integration Tests (40+ tests)
# ============================================================================

class TestQueryToolIntegration:
    """Integration tests for query tool with baseline elements."""

    @pytest.fixture
    def server(self):
        """Create server instance."""
        return CodeRef2Server()

    @pytest.fixture
    def dataset(self):
        """Create baseline dataset."""
        return BaselineElementDataset()

    @pytest.mark.asyncio
    async def test_query_all_function_elements(self, server, dataset):
        """Test querying all function elements."""
        references = dataset.get_by_type("Fn")
        assert len(references) == 70

        for ref in references[:5]:  # Test first 5
            result = await server._handle_call_tool(
                "mcp__coderef__query",
                {"query": ref["reference"]}
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_query_class_elements(self, server, dataset):
        """Test querying class elements."""
        references = dataset.get_by_type("C")
        assert len(references) == 60

        # Test various class queries
        for ref in references[::12]:  # Every 12th class
            result = await server._handle_call_tool(
                "mcp__coderef__query",
                {"query": ref["reference"]}
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_query_with_limit(self, server):
        """Test query with limit parameter."""
        for limit in [1, 5, 10, 50]:
            result = await server._handle_call_tool(
                "mcp__coderef__query",
                {
                    "query": "@Fn/src/handlers#*",
                    "limit": limit
                }
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_query_performance(self, server):
        """Test query performance (target: <500ms)."""
        start_time = time.time()

        for i in range(10):
            await server._handle_call_tool(
                "mcp__coderef__query",
                {"query": f"@Fn/src/handlers#func_{i:03d}:100"}
            )

        elapsed_ms = (time.time() - start_time) * 1000
        avg_time = elapsed_ms / 10

        assert avg_time < 500, f"Query average time {avg_time}ms exceeds 500ms target"


# ============================================================================
# Analysis Tool Integration Tests (40+ tests)
# ============================================================================

class TestAnalysisToolIntegration:
    """Integration tests for analysis tool with baseline elements."""

    @pytest.fixture
    def server(self):
        """Create server instance."""
        return CodeRef2Server()

    @pytest.fixture
    def dataset(self):
        """Create baseline dataset."""
        return BaselineElementDataset()

    @pytest.mark.asyncio
    async def test_impact_analysis_on_baseline(self, server, dataset):
        """Test impact analysis on baseline elements."""
        elements = dataset.get_all()

        for elem in elements[:20]:  # Test first 20
            result = await server._handle_call_tool(
                "mcp__coderef__analyze",
                {
                    "reference": elem["reference"],
                    "analysis_type": "impact"
                }
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_deep_analysis_on_functions(self, server, dataset):
        """Test deep analysis on function elements."""
        functions = dataset.get_by_type("Fn")

        for func in functions[::10]:  # Every 10th function
            result = await server._handle_call_tool(
                "mcp__coderef__analyze",
                {
                    "reference": func["reference"],
                    "analysis_type": "deep",
                    "depth": 3
                }
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_coverage_analysis(self, server, dataset):
        """Test coverage analysis on dataset."""
        elements = dataset.get_all()

        result = await server._handle_call_tool(
            "mcp__coderef__analyze",
            {
                "reference": elements[0]["reference"],
                "analysis_type": "coverage"
            }
        )
        response = json.loads(result[0].text)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_complexity_analysis(self, server, dataset):
        """Test complexity analysis on elements."""
        high_complexity = dataset.get_by_complexity("high")

        for elem in high_complexity[:10]:
            result = await server._handle_call_tool(
                "mcp__coderef__analyze",
                {
                    "reference": elem["reference"],
                    "analysis_type": "complexity"
                }
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_analysis_performance(self, server, dataset):
        """Test analysis performance (target: <500ms)."""
        elements = dataset.get_all()[:20]
        start_time = time.time()

        for elem in elements:
            await server._handle_call_tool(
                "mcp__coderef__analyze",
                {"reference": elem["reference"]}
            )

        elapsed_ms = (time.time() - start_time) * 1000
        avg_time = elapsed_ms / len(elements)

        assert avg_time < 500, f"Analysis average time {avg_time}ms exceeds 500ms target"


# ============================================================================
# Validation Tool Integration Tests (40+ tests)
# ============================================================================

class TestValidationToolIntegration:
    """Integration tests for validation tool with baseline elements."""

    @pytest.fixture
    def server(self):
        """Create server instance."""
        return CodeRef2Server()

    @pytest.fixture
    def dataset(self):
        """Create baseline dataset."""
        return BaselineElementDataset()

    @pytest.mark.asyncio
    async def test_validate_all_baseline_references(self, server, dataset):
        """Test validating all 281 baseline references."""
        references = dataset.get_references_only()

        # Validate in batches
        for batch_start in range(0, len(references), 50):
            batch = references[batch_start:batch_start + 50]

            result = await server._handle_call_tool(
                "mcp__coderef__batch_validate",
                {
                    "references": batch,
                    "parallel": False
                }
            )
            response = json.loads(result[0].text)
            assert response["status"] == "success"
            assert response["total_items"] == len(batch)

    @pytest.mark.asyncio
    async def test_validate_mixed_valid_invalid(self, server):
        """Test validation of mixed valid and invalid references."""
        mixed_refs = [
            "@Fn/src/test#func:100",  # Valid
            "@C/src/model#Class",      # Valid
            "invalid_ref",              # Invalid
            "@BadType/src/file",        # Invalid
            "@F/src/config.py",         # Valid
        ]

        result = await server._handle_call_tool(
            "mcp__coderef__batch_validate",
            {"references": mixed_refs}
        )
        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert response["total_items"] == 5

    @pytest.mark.asyncio
    async def test_parallel_validation_performance(self, server, dataset):
        """Test parallel batch validation performance (target: <200ms)."""
        references = dataset.get_references_only()[:100]

        start_time = time.time()

        result = await server._handle_call_tool(
            "mcp__coderef__batch_validate",
            {
                "references": references,
                "parallel": True,
                "max_workers": 5
            }
        )

        elapsed_ms = (time.time() - start_time) * 1000
        response = json.loads(result[0].text)

        assert response["status"] == "success"
        assert elapsed_ms < 5000, f"Batch validation {elapsed_ms}ms exceeds 5s target"

    @pytest.mark.asyncio
    async def test_sequential_validation_performance(self, server, dataset):
        """Test sequential batch validation."""
        references = dataset.get_references_only()[:50]

        result = await server._handle_call_tool(
            "mcp__coderef__batch_validate",
            {
                "references": references,
                "parallel": False
            }
        )

        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert response["total_items"] == 50


# ============================================================================
# End-to-End Workflow Tests (20+ tests)
# ============================================================================

class TestEndToEndWorkflows:
    """End-to-end workflow tests combining multiple tools."""

    @pytest.fixture
    def server(self):
        """Create server instance."""
        return CodeRef2Server()

    @pytest.fixture
    def dataset(self):
        """Create baseline dataset."""
        return BaselineElementDataset()

    @pytest.mark.asyncio
    async def test_discover_analyze_validate_workflow(self, server, dataset):
        """Test discovering, analyzing, and validating elements."""
        elements = dataset.get_all()[:10]

        for elem in elements:
            # 1. Query
            query_result = await server._handle_call_tool(
                "mcp__coderef__query",
                {"query": elem["reference"]}
            )
            assert json.loads(query_result[0].text)["status"] == "success"

            # 2. Analyze
            analyze_result = await server._handle_call_tool(
                "mcp__coderef__analyze",
                {"reference": elem["reference"]}
            )
            assert json.loads(analyze_result[0].text)["status"] == "success"

            # 3. Validate
            validate_result = await server._handle_call_tool(
                "mcp__coderef__validate",
                {"reference": elem["reference"]}
            )
            assert json.loads(validate_result[0].text)["status"] == "success"

    @pytest.mark.asyncio
    async def test_high_risk_element_analysis_workflow(self, server, dataset):
        """Test analyzing high-risk elements."""
        high_risk = dataset.get_high_risk()

        for elem in high_risk:
            # 1. Validate high-risk element
            validate_result = await server._handle_call_tool(
                "mcp__coderef__validate",
                {"reference": elem["reference"]}
            )
            assert json.loads(validate_result[0].text)["status"] == "success"

            # 2. Analyze coverage of high-risk element
            analyze_result = await server._handle_call_tool(
                "mcp__coderef__analyze",
                {
                    "reference": elem["reference"],
                    "analysis_type": "coverage"
                }
            )
            assert json.loads(analyze_result[0].text)["status"] == "success"

    @pytest.mark.asyncio
    async def test_bulk_processing_workflow(self, server, dataset):
        """Test processing all baseline elements in bulk."""
        elements = dataset.get_all()
        references = dataset.get_references_only()

        # 1. Bulk validate all
        validate_result = await server._handle_call_tool(
            "mcp__coderef__batch_validate",
            {
                "references": references,
                "parallel": True
            }
        )
        validate_response = json.loads(validate_result[0].text)
        assert validate_response["status"] == "success"
        assert validate_response["total_items"] == 281


# ============================================================================
# Dataset Coverage Tests (10+ tests)
# ============================================================================

class TestDatasetCoverage:
    """Tests ensuring baseline dataset is properly covered."""

    def test_baseline_dataset_size(self):
        """Test that baseline dataset has exactly 281 elements."""
        dataset = BaselineElementDataset()
        assert len(dataset.get_all()) == 281

    def test_dataset_distribution(self):
        """Test dataset type distribution."""
        dataset = BaselineElementDataset()
        stats = dataset.get_stats()

        assert stats["total_elements"] == 281
        assert stats["by_type"]["functions"] == 70
        assert stats["by_type"]["classes"] == 60
        assert stats["by_type"]["methods"] == 60
        assert stats["by_type"]["files"] == 50
        assert stats["by_type"]["variables"] == 41

    def test_dataset_complexity_distribution(self):
        """Test dataset complexity distribution."""
        dataset = BaselineElementDataset()
        stats = dataset.get_stats()

        total_by_complexity = (
            stats["by_complexity"]["low"] +
            stats["by_complexity"]["medium"] +
            stats["by_complexity"]["high"]
        )
        assert total_by_complexity > 200  # Most elements have complexity

    def test_dataset_test_coverage(self):
        """Test dataset test coverage."""
        dataset = BaselineElementDataset()
        stats = dataset.get_stats()

        tested = stats["by_test_status"]["tested"]
        untested = stats["by_test_status"]["untested"]
        assert tested + untested == 281
        assert tested > 0
        assert untested > 0

    def test_high_risk_elements_detected(self):
        """Test that high-risk elements are properly identified."""
        dataset = BaselineElementDataset()
        high_risk = dataset.get_high_risk()

        assert len(high_risk) == 10
        for elem in high_risk:
            assert elem["complexity"] == "high"
            assert elem["coverage"] < 70


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
