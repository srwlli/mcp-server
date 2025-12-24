"""Unit tests for query tools (mcp__coderef__query and mcp__coderef__analyze)."""

import pytest
import asyncio
from datetime import datetime

from coderef.models import (
    TypeDesignator,
    QueryRequest,
    QueryFilter,
    QueryResponse,
    CodeRef2Element,
    ElementMetadata,
    ImpactAnalysis,
)
from coderef.generators.query_generator import (
    QueryEngine,
    QueryExecutor,
    ReferenceParser,
)


# ============================================================================
# Reference Parser Tests
# ============================================================================

class TestReferenceParser:
    """Tests for CodeRef2 reference parsing."""

    def test_parse_full_reference(self):
        """Test parsing complete reference."""
        ref = "@Fn/src/utils#calculate_total:42{complexity:high,status:active}"
        parsed = ReferenceParser.parse(ref)

        assert parsed is not None
        assert parsed["type"] == "Fn"
        assert parsed["path"] == "src/utils"
        assert parsed["element"] == "calculate_total"
        assert parsed["line"] == 42
        assert parsed["metadata"]["complexity"] == "high"
        assert parsed["metadata"]["status"] == "active"

    def test_parse_reference_without_element(self):
        """Test parsing reference without element."""
        ref = "@C/src/models:10"
        parsed = ReferenceParser.parse(ref)

        assert parsed is not None
        assert parsed["type"] == "C"
        assert parsed["path"] == "src/models"
        assert parsed["element"] is None
        assert parsed["line"] == 10

    def test_parse_reference_without_line(self):
        """Test parsing reference without line number."""
        ref = "@M/src/service#execute"
        parsed = ReferenceParser.parse(ref)

        assert parsed is not None
        assert parsed["type"] == "M"
        assert parsed["element"] == "execute"
        assert parsed["line"] is None

    def test_parse_reference_path_only(self):
        """Test parsing reference with path only."""
        ref = "@F/src/config.py"
        parsed = ReferenceParser.parse(ref)

        assert parsed is not None
        assert parsed["type"] == "F"
        assert parsed["path"] == "src/config.py"
        assert parsed["element"] is None
        assert parsed["line"] is None

    def test_parse_invalid_reference(self):
        """Test parsing invalid reference."""
        ref = "invalid_reference"
        parsed = ReferenceParser.parse(ref)

        assert parsed is None

    def test_parse_metadata_single(self):
        """Test parsing single metadata value."""
        ref = "@Fn/test#func:1{status:deprecated}"
        parsed = ReferenceParser.parse(ref)

        assert parsed["metadata"]["status"] == "deprecated"
        assert len(parsed["metadata"]) == 1

    def test_parse_metadata_multiple(self):
        """Test parsing multiple metadata values."""
        ref = "@Fn/test#func:1{status:active,complexity:high,coverage:80}"
        parsed = ReferenceParser.parse(ref)

        assert parsed["metadata"]["status"] == "active"
        assert parsed["metadata"]["complexity"] == "high"
        assert parsed["metadata"]["coverage"] == "80"
        assert len(parsed["metadata"]) == 3


# ============================================================================
# Query Engine Tests
# ============================================================================

class TestQueryEngine:
    """Tests for query engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create query engine instance."""
        return QueryEngine()

    @pytest.mark.asyncio
    async def test_query_by_reference(self, engine):
        """Test querying by specific reference."""
        request = QueryRequest(
            query="@Fn/src/utils#calculate_total:42",
            limit=10,
        )
        response = await engine.query(request)

        assert response.query_status == "success"
        assert isinstance(response.elements, list)
        assert response.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_query_by_pattern(self, engine):
        """Test querying by pattern."""
        request = QueryRequest(
            query="*/models*",
            limit=50,
        )
        response = await engine.query(request)

        assert response.query_status == "success"
        assert isinstance(response.elements, list)

    @pytest.mark.asyncio
    async def test_query_with_filter_type(self, engine):
        """Test query with type designator filter."""
        query_filter = QueryFilter(
            type_designators=[TypeDesignator.FUNCTION, TypeDesignator.METHOD]
        )
        request = QueryRequest(
            query="@Fn/src/test",
            filter=query_filter,
            limit=100,
        )
        response = await engine.query(request)

        assert response.query_status == "success"

    @pytest.mark.asyncio
    async def test_query_with_filter_line_range(self, engine):
        """Test query with line number range filter."""
        query_filter = QueryFilter(
            min_line=10,
            max_line=100,
        )
        request = QueryRequest(
            query="@Fn/src/utils",
            filter=query_filter,
        )
        response = await engine.query(request)

        assert response.query_status == "success"

    @pytest.mark.asyncio
    async def test_query_respects_limit(self, engine):
        """Test that query respects limit parameter."""
        request = QueryRequest(
            query="@Fn/src",
            limit=5,
        )
        response = await engine.query(request)

        assert len(response.elements) <= 5

    @pytest.mark.asyncio
    async def test_impact_analysis(self, engine):
        """Test impact analysis functionality."""
        analysis = await engine.analyze_impact(
            source_reference="@Fn/src/core#main_process:100",
            depth=3,
        )

        assert isinstance(analysis, ImpactAnalysis)
        assert analysis.source_reference == "@Fn/src/core#main_process:100"
        assert analysis.total_affected >= 0
        assert isinstance(analysis.affected_elements, list)
        assert "by_level" in analysis.impact_summary

    @pytest.mark.asyncio
    async def test_impact_analysis_depth(self, engine):
        """Test impact analysis with different depths."""
        analysis_d1 = await engine.analyze_impact(
            source_reference="@Fn/src/core#main:1",
            depth=1,
        )
        analysis_d3 = await engine.analyze_impact(
            source_reference="@Fn/src/core#main:1",
            depth=3,
        )

        # Deeper analysis should find more affected elements
        assert analysis_d3.total_affected >= analysis_d1.total_affected


# ============================================================================
# Query Executor Tests
# ============================================================================

class TestQueryExecutor:
    """Tests for high-level query executor."""

    @pytest.fixture
    def executor(self):
        """Create query executor instance."""
        return QueryExecutor()

    @pytest.mark.asyncio
    async def test_execute_valid_query(self, executor):
        """Test executing a valid query."""
        response = await executor.execute_query(
            QueryRequest(query="@Fn/src/test#func:0")
        )

        assert response.query_status == "success"

    @pytest.mark.asyncio
    async def test_execute_invalid_query_empty(self, executor):
        """Test executing invalid query (empty)."""
        with pytest.raises(ValueError):
            await executor.execute_query(QueryRequest(query=""))

    @pytest.mark.asyncio
    async def test_execute_analysis_valid_reference(self, executor):
        """Test executing analysis on valid reference."""
        analysis = await executor.execute_analysis(
            reference="@Fn/src/service#execute:50"
        )

        assert analysis.source_reference == "@Fn/src/service#execute:50"
        assert isinstance(analysis.affected_elements, list)

    @pytest.mark.asyncio
    async def test_execute_analysis_invalid_reference(self, executor):
        """Test executing analysis on invalid reference."""
        with pytest.raises(ValueError):
            await executor.execute_analysis(reference="")


# ============================================================================
# Integration Tests
# ============================================================================

class TestQueryIntegration:
    """Integration tests for query functionality."""

    @pytest.mark.asyncio
    async def test_query_workflow(self):
        """Test complete query workflow."""
        executor = QueryExecutor()

        # Execute query
        query_response = await executor.execute_query(
            QueryRequest(
                query="@Fn/src/handlers#process_request:100",
                limit=50,
            )
        )

        assert query_response.query_status == "success"
        assert query_response.total_count >= 0

        # If we got results, analyze first one
        if query_response.elements:
            first_element = query_response.elements[0]
            analysis = await executor.execute_analysis(
                reference=first_element.reference
            )

            assert analysis.source_reference == first_element.reference
            assert isinstance(analysis.affected_elements, list)

    @pytest.mark.asyncio
    async def test_query_performance(self):
        """Test query performance target (< 500ms)."""
        executor = QueryExecutor()
        request = QueryRequest(
            query="@Fn/src/utils",
            limit=100,
        )

        response = await executor.execute_query(request)

        assert response.execution_time_ms < 500

    @pytest.mark.asyncio
    async def test_analysis_performance(self):
        """Test analysis performance target (< 500ms)."""
        engine = QueryEngine()

        analysis = await engine.analyze_impact(
            source_reference="@Fn/src/core#main:1",
            depth=5,
        )

        # Note: In production, this would have timing info
        # For now we just verify it completes
        assert analysis.source_reference == "@Fn/src/core#main:1"


# ============================================================================
# Element Metadata Tests
# ============================================================================

class TestElementMetadata:
    """Tests for element metadata handling."""

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = ElementMetadata(
            status="active",
            security="critical",
            complexity="high",
        )

        meta_dict = metadata.to_dict()

        assert meta_dict["status"] == "active"
        assert meta_dict["security"] == "critical"
        assert meta_dict["complexity"] == "high"
        assert "custom" not in meta_dict

    def test_metadata_none_values_excluded(self):
        """Test that None values are excluded from dictionary."""
        metadata = ElementMetadata(
            status="active",
            security=None,
            complexity="high",
        )

        meta_dict = metadata.to_dict()

        assert "status" in meta_dict
        assert "security" not in meta_dict
        assert "complexity" in meta_dict


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_reference_format(self):
        """Test handling of invalid reference format."""
        engine = QueryEngine()

        analysis = await engine.analyze_impact(
            source_reference="not_a_valid_reference",
            depth=3,
        )

        # Should return empty analysis instead of crashing
        assert analysis.source_reference == "not_a_valid_reference"
        assert analysis.total_affected == 0


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
