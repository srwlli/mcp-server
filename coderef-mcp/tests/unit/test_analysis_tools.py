"""Unit tests for analysis tools (graph traversal, coverage, complexity)."""

import pytest
from coderef.models import TypeDesignator, RelationshipType
from coderef.generators.analysis_generator import (
    DependencyGraphEngine,
    CoverageAnalysisEngine,
    ComplexityAnalysisEngine,
    DeepAnalysisEngine,
)


# ============================================================================
# Dependency Graph Engine Tests
# ============================================================================

class TestDependencyGraphEngine:
    """Tests for dependency graph analysis."""

    @pytest.fixture
    def engine(self):
        """Create a dependency graph engine with test data."""
        engine = DependencyGraphEngine()

        # Build a sample graph
        # A -> B -> C -> D
        # A -> E -> D
        engine.add_node("A", TypeDesignator.FUNCTION, {"name": "main"})
        engine.add_node("B", TypeDesignator.FUNCTION, {"name": "process"})
        engine.add_node("C", TypeDesignator.FUNCTION, {"name": "validate"})
        engine.add_node("D", TypeDesignator.FUNCTION, {"name": "store"})
        engine.add_node("E", TypeDesignator.FUNCTION, {"name": "cache"})

        engine.add_edge("A", "B", RelationshipType.CALLS)
        engine.add_edge("B", "C", RelationshipType.CALLS)
        engine.add_edge("C", "D", RelationshipType.CALLS)
        engine.add_edge("A", "E", RelationshipType.CALLS)
        engine.add_edge("E", "D", RelationshipType.CALLS)

        return engine

    def test_add_node(self, engine):
        """Test adding nodes to graph."""
        assert "A" in engine.graph
        assert "B" in engine.graph
        assert len(engine.graph) == 5

    def test_add_edge(self, engine):
        """Test adding edges to graph."""
        assert "B" in engine.graph["A"].outgoing_edges
        assert "A" in engine.graph["B"].incoming_edges

    def test_find_dependents(self, engine):
        """Test finding dependents of a node."""
        dependents = engine.find_all_dependents("D", max_depth=5)

        # D has no outgoing edges, so no dependents
        assert len(dependents) == 0

    def test_find_dependencies(self, engine):
        """Test finding dependencies of a node."""
        deps = engine.find_all_dependencies("A", max_depth=5)

        # A depends on B and E
        assert len(deps) == 4  # B, C, D, E

    def test_find_cycles_no_cycle(self, engine):
        """Test cycle detection on acyclic graph."""
        cycles = engine.find_cycles("A")

        assert len(cycles) == 0

    def test_add_cycle_detection(self):
        """Test cycle detection on graph with cycles."""
        engine = DependencyGraphEngine()
        engine.add_node("X", TypeDesignator.FUNCTION)
        engine.add_node("Y", TypeDesignator.FUNCTION)
        engine.add_node("Z", TypeDesignator.FUNCTION)

        # Create a cycle: X -> Y -> Z -> X
        engine.add_edge("X", "Y")
        engine.add_edge("Y", "Z")
        engine.add_edge("Z", "X")

        cycles = engine.find_cycles("X")
        assert len(cycles) > 0

    def test_breadth_first_traversal(self, engine):
        """Test BFS traversal."""
        nodes = engine.traverse_breadth_first("A", max_depth=3, direction="outgoing")

        # Should find B, C, D, E
        references = {n.reference for n in nodes}
        assert "B" in references
        assert "E" in references

    def test_traversal_depth_limit(self, engine):
        """Test that traversal respects depth limit."""
        nodes_d1 = engine.traverse_breadth_first("A", max_depth=1, direction="outgoing")
        nodes_d2 = engine.traverse_breadth_first("A", max_depth=2, direction="outgoing")

        # Deeper traversal should find more nodes
        assert len(nodes_d2) >= len(nodes_d1)


# ============================================================================
# Coverage Analysis Engine Tests
# ============================================================================

class TestCoverageAnalysisEngine:
    """Tests for coverage analysis."""

    @pytest.fixture
    def engine(self):
        """Create coverage analysis engine with test data."""
        engine = CoverageAnalysisEngine()

        # Register coverage for various elements
        engine.register_coverage("func_a", 100.0, 5)
        engine.register_coverage("func_b", 80.0, 3)
        engine.register_coverage("func_c", 50.0, 2)
        engine.register_coverage("func_d", 0.0, 0)
        engine.register_coverage("func_e", 30.0, 1)

        return engine

    def test_register_coverage(self, engine):
        """Test registering coverage data."""
        coverage = engine.get_coverage_info("func_a")

        assert coverage.has_tests
        assert coverage.test_count == 5
        assert coverage.coverage_percentage == 100.0

    def test_analyze_coverage(self, engine):
        """Test coverage analysis across elements."""
        elements = ["func_a", "func_b", "func_c", "func_d", "func_e"]
        analysis = engine.analyze_coverage(elements, risk_threshold=50.0)

        assert analysis.total_elements == 5
        assert analysis.covered_elements == 4  # a, b, c, e have coverage
        assert analysis.uncovered_elements == 1  # d has no coverage
        assert "func_e" in analysis.at_risk_elements
        assert "func_d" in analysis.at_risk_elements

    def test_coverage_percentage_calculation(self, engine):
        """Test coverage percentage calculation."""
        elements = ["func_a", "func_b", "func_c"]
        analysis = engine.analyze_coverage(elements)

        # (100 + 80 + 50) / 3 = 76.67
        assert 75 < analysis.coverage_percentage < 78

    def test_at_risk_detection(self, engine):
        """Test at-risk element detection."""
        elements = ["func_a", "func_b", "func_c", "func_d", "func_e"]
        analysis = engine.analyze_coverage(elements, risk_threshold=60.0)

        # Elements below 60% are at-risk: c (50%), d (0%), e (30%)
        assert len(analysis.at_risk_elements) >= 2
        assert "func_c" in analysis.at_risk_elements


# ============================================================================
# Complexity Analysis Engine Tests
# ============================================================================

class TestComplexityAnalysisEngine:
    """Tests for complexity analysis."""

    @pytest.fixture
    def engine(self):
        """Create complexity analysis engine."""
        return ComplexityAnalysisEngine()

    def test_calculate_simple_complexity(self, engine):
        """Test complexity calculation for simple code."""
        score = engine.calculate_complexity(
            "func_simple",
            line_count=10,
            branching_factor=1,
            nesting_depth=1
        )

        assert 0 <= score <= 100
        assert score < 30  # Should be low complexity

    def test_calculate_complex_code(self, engine):
        """Test complexity calculation for complex code."""
        score = engine.calculate_complexity(
            "func_complex",
            line_count=100,
            branching_factor=10,
            nesting_depth=5
        )

        assert score > 50  # Should be higher complexity

    def test_complexity_caching(self, engine):
        """Test that complexity scores are cached."""
        score1 = engine.calculate_complexity("func_test", 20, 2, 2)
        score2 = engine.get_complexity_score("func_test")

        assert score1 == score2

    def test_categorize_complexity(self, engine):
        """Test complexity categorization."""
        assert engine.categorize_complexity(10) == "low"
        assert engine.categorize_complexity(35) == "medium"
        assert engine.categorize_complexity(65) == "high"
        assert engine.categorize_complexity(85) == "critical"


# ============================================================================
# Deep Analysis Engine Tests
# ============================================================================

class TestDeepAnalysisEngine:
    """Tests for deep analysis coordinator."""

    @pytest.fixture
    def engine(self):
        """Create deep analysis engine with sample data."""
        engine = DeepAnalysisEngine()

        # Build sample graph
        engine.graph_engine.add_node("main", TypeDesignator.FUNCTION)
        engine.graph_engine.add_node("process", TypeDesignator.FUNCTION)
        engine.graph_engine.add_node("validate", TypeDesignator.FUNCTION)

        engine.graph_engine.add_edge("main", "process")
        engine.graph_engine.add_edge("process", "validate")

        # Register coverage data
        engine.coverage_engine.register_coverage("main", 95.0, 5)
        engine.coverage_engine.register_coverage("process", 70.0, 3)
        engine.coverage_engine.register_coverage("validate", 40.0, 1)

        return engine

    @pytest.mark.asyncio
    async def test_deep_analysis(self, engine):
        """Test deep analysis execution."""
        analysis = await engine.perform_deep_analysis("main", analysis_depth=2)

        assert "element" in analysis
        assert "dependents" in analysis
        assert "dependencies" in analysis
        assert "cycles_detected" in analysis

    @pytest.mark.asyncio
    async def test_coverage_gap_analysis(self, engine):
        """Test coverage gap analysis."""
        elements = ["main", "process", "validate"]
        analysis = await engine.analyze_coverage_gaps(elements, risk_threshold=60.0)

        assert analysis["total_elements"] == 3
        assert analysis["at_risk_count"] >= 1
        assert "validate" in analysis["at_risk_elements"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestAnalysisIntegration:
    """Integration tests for analysis tools."""

    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self):
        """Test complete analysis workflow."""
        engine = DeepAnalysisEngine()

        # Build a realistic graph
        elements = ["main", "auth", "db", "cache", "logger"]
        for elem in elements:
            engine.graph_engine.add_node(elem, TypeDesignator.FUNCTION)

        # Create dependencies
        engine.graph_engine.add_edge("main", "auth")
        engine.graph_engine.add_edge("auth", "db")
        engine.graph_engine.add_edge("main", "cache")
        engine.graph_engine.add_edge("cache", "db")
        engine.graph_engine.add_edge("main", "logger")

        # Register coverage
        for i, elem in enumerate(elements):
            coverage = 100 - (i * 15)
            engine.coverage_engine.register_coverage(elem, coverage, i + 1)

        # Perform analysis
        impact = await engine.perform_deep_analysis("main")
        coverage = await engine.analyze_coverage_gaps(elements)

        assert impact["element"] == "main"
        assert coverage["total_elements"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
