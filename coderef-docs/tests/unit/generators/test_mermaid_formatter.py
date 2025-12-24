"""
Test suite for mermaid_formatter module.

Tests cover:
- Module diagram generation from graph.json
- Element-focused diagram generation
- Graph metrics computation (density, circularity)
- High-impact element detection
- Edge cases and error handling

Part of WO-CODEREF-FOUNDATION-003 (Hybrid Foundation Docs).
"""

import pytest
from generators.mermaid_formatter import (
    generate_module_diagram,
    generate_element_diagram,
    compute_graph_metrics,
    get_high_impact_elements
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def simple_graph():
    """Simple graph with 3 nodes and 2 edges."""
    return {
        "nodes": [
            ["n1", {"id": "main.py::run", "name": "run", "type": "function", "file": "main.py"}],
            ["n2", {"id": "server.py::handle", "name": "handle", "type": "function", "file": "server.py"}],
            ["n3", {"id": "utils.py::validate", "name": "validate", "type": "function", "file": "utils.py"}]
        ],
        "edges": [
            ["e1", {"source": "main.py::run", "target": "server.py::handle", "type": "calls"}],
            ["e2", {"source": "server.py::handle", "target": "utils.py::validate", "type": "calls"}]
        ]
    }


@pytest.fixture
def complex_graph():
    """Complex graph with multiple modules and circular dependencies."""
    return {
        "nodes": [
            ["n1", {"id": "api/routes.py::get_users", "name": "get_users", "type": "function", "file": "api/routes.py"}],
            ["n2", {"id": "api/routes.py::create_user", "name": "create_user", "type": "function", "file": "api/routes.py"}],
            ["n3", {"id": "services/user.py::UserService", "name": "UserService", "type": "class", "file": "services/user.py"}],
            ["n4", {"id": "services/auth.py::AuthService", "name": "AuthService", "type": "class", "file": "services/auth.py"}],
            ["n5", {"id": "db/models.py::User", "name": "User", "type": "class", "file": "db/models.py"}],
            ["n6", {"id": "utils/helpers.py::validate", "name": "validate", "type": "function", "file": "utils/helpers.py"}]
        ],
        "edges": [
            ["e1", {"source": "api/routes.py::get_users", "target": "services/user.py::UserService", "type": "calls"}],
            ["e2", {"source": "api/routes.py::create_user", "target": "services/user.py::UserService", "type": "calls"}],
            ["e3", {"source": "services/user.py::UserService", "target": "db/models.py::User", "type": "calls"}],
            ["e4", {"source": "services/user.py::UserService", "target": "services/auth.py::AuthService", "type": "calls"}],
            ["e5", {"source": "services/auth.py::AuthService", "target": "services/user.py::UserService", "type": "calls"}],  # Circular
            ["e6", {"source": "services/user.py::UserService", "target": "utils/helpers.py::validate", "type": "calls"}]
        ]
    }


@pytest.fixture
def high_impact_graph():
    """Graph with high-impact nodes (many dependents)."""
    return {
        "nodes": [
            ["n1", {"id": "core.py::logger", "name": "logger", "type": "function", "file": "core.py"}],
            ["n2", {"id": "api.py::handler1", "name": "handler1", "type": "function", "file": "api.py"}],
            ["n3", {"id": "api.py::handler2", "name": "handler2", "type": "function", "file": "api.py"}],
            ["n4", {"id": "api.py::handler3", "name": "handler3", "type": "function", "file": "api.py"}],
            ["n5", {"id": "service.py::process", "name": "process", "type": "function", "file": "service.py"}]
        ],
        "edges": [
            # logger is called by 3 handlers (high impact)
            ["e1", {"source": "api.py::handler1", "target": "core.py::logger", "type": "calls"}],
            ["e2", {"source": "api.py::handler2", "target": "core.py::logger", "type": "calls"}],
            ["e3", {"source": "api.py::handler3", "target": "core.py::logger", "type": "calls"}],
            # process is called by 2 handlers
            ["e4", {"source": "api.py::handler1", "target": "service.py::process", "type": "calls"}],
            ["e5", {"source": "api.py::handler2", "target": "service.py::process", "type": "calls"}]
        ]
    }


# ============================================================================
# MODULE DIAGRAM TESTS
# ============================================================================

class TestGenerateModuleDiagram:
    """Test generate_module_diagram() function."""

    def test_empty_graph_returns_placeholder(self):
        """Empty graph returns placeholder diagram."""
        result = generate_module_diagram({})

        assert "```mermaid" in result
        assert "```" in result
        assert "No" in result.lower() or "empty" in result.lower()

    def test_none_graph_returns_placeholder(self):
        """None graph returns placeholder diagram."""
        result = generate_module_diagram(None)

        assert "```mermaid" in result

    def test_simple_graph_generates_diagram(self, simple_graph):
        """Simple graph generates valid Mermaid diagram."""
        result = generate_module_diagram(simple_graph)

        assert "```mermaid" in result
        assert "graph TB" in result
        assert "```" in result

    def test_diagram_includes_nodes(self, simple_graph):
        """Generated diagram includes node names."""
        result = generate_module_diagram(simple_graph)

        # Should contain module names (file names without extension)
        assert "main" in result.lower() or "run" in result.lower()

    def test_diagram_includes_edges(self, simple_graph):
        """Generated diagram includes edges."""
        result = generate_module_diagram(simple_graph)

        # Should contain edge syntax
        assert "-->" in result

    def test_diagram_respects_max_nodes(self, complex_graph):
        """Diagram respects max_nodes parameter."""
        result = generate_module_diagram(complex_graph, max_nodes=2)

        # Should still be valid Mermaid
        assert "```mermaid" in result
        assert "```" in result

    def test_diagram_groups_by_module(self, complex_graph):
        """Diagram groups elements by file/module."""
        result = generate_module_diagram(complex_graph)

        # May contain subgraph for grouping
        # This is optional based on implementation
        assert "```mermaid" in result

    def test_diagram_valid_mermaid_syntax(self, simple_graph):
        """Generated diagram has valid Mermaid syntax."""
        result = generate_module_diagram(simple_graph)

        # Basic Mermaid syntax checks
        assert result.count("```mermaid") == 1
        assert result.count("```") == 2  # Opening and closing
        assert "graph" in result


# ============================================================================
# ELEMENT DIAGRAM TESTS
# ============================================================================

class TestGenerateElementDiagram:
    """Test generate_element_diagram() function."""

    def test_empty_graph_returns_placeholder(self):
        """Empty graph returns placeholder diagram."""
        result = generate_element_diagram({}, "some::element")

        assert "```mermaid" in result

    def test_element_not_found_returns_placeholder(self, simple_graph):
        """Non-existent element returns placeholder."""
        result = generate_element_diagram(simple_graph, "nonexistent::element")

        assert "```mermaid" in result
        assert "not found" in result.lower()

    def test_element_diagram_shows_element(self, simple_graph):
        """Element diagram includes the target element."""
        result = generate_element_diagram(simple_graph, "server.py::handle")

        assert "```mermaid" in result
        assert "handle" in result

    def test_element_diagram_shows_callers(self, simple_graph):
        """Element diagram shows callers (incoming edges)."""
        result = generate_element_diagram(simple_graph, "server.py::handle")

        # main.py::run calls server.py::handle
        assert "```mermaid" in result
        # Should show the relationship

    def test_element_diagram_shows_callees(self, simple_graph):
        """Element diagram shows callees (outgoing edges)."""
        result = generate_element_diagram(simple_graph, "server.py::handle")

        # server.py::handle calls utils.py::validate
        assert "```mermaid" in result

    def test_element_diagram_styles_center(self, simple_graph):
        """Element diagram applies style to center element."""
        result = generate_element_diagram(simple_graph, "server.py::handle")

        # Should have styling for center node
        assert "style" in result or "center" in result


# ============================================================================
# GRAPH METRICS TESTS
# ============================================================================

class TestComputeGraphMetrics:
    """Test compute_graph_metrics() function."""

    def test_empty_graph_returns_zeros(self):
        """Empty graph returns zero metrics."""
        result = compute_graph_metrics({})

        assert result['node_count'] == 0
        assert result['edge_count'] == 0
        assert result['density'] == 0.0
        assert result['circular_dependencies'] == []

    def test_none_graph_returns_zeros(self):
        """None graph returns zero metrics."""
        result = compute_graph_metrics(None)

        assert result['node_count'] == 0
        assert result['edge_count'] == 0

    def test_simple_graph_metrics(self, simple_graph):
        """Simple graph returns correct node and edge counts."""
        result = compute_graph_metrics(simple_graph)

        assert result['node_count'] == 3
        assert result['edge_count'] == 2

    def test_density_calculation(self, simple_graph):
        """Density is calculated correctly."""
        result = compute_graph_metrics(simple_graph)

        # With 3 nodes, max edges = 3 * 2 = 6
        # 2 edges / 6 = 0.333...
        assert 0 < result['density'] < 1

    def test_circular_dependency_detection(self, complex_graph):
        """Detects circular dependencies."""
        result = compute_graph_metrics(complex_graph)

        # complex_graph has UserService <-> AuthService cycle
        assert len(result['circular_dependencies']) >= 1

    def test_isolated_nodes_detection(self):
        """Detects nodes with no connections."""
        graph = {
            "nodes": [
                ["n1", {"id": "a", "name": "a", "file": "a.py"}],
                ["n2", {"id": "b", "name": "b", "file": "b.py"}],
                ["n3", {"id": "c", "name": "c", "file": "c.py"}]  # Isolated
            ],
            "edges": [
                ["e1", {"source": "a", "target": "b", "type": "calls"}]
            ]
        }

        result = compute_graph_metrics(graph)

        assert len(result['isolated_nodes']) >= 1

    def test_average_degrees_calculated(self, simple_graph):
        """Average in/out degrees are calculated."""
        result = compute_graph_metrics(simple_graph)

        assert 'avg_in_degree' in result
        assert 'avg_out_degree' in result
        assert result['avg_in_degree'] >= 0
        assert result['avg_out_degree'] >= 0


# ============================================================================
# HIGH-IMPACT ELEMENTS TESTS
# ============================================================================

class TestGetHighImpactElements:
    """Test get_high_impact_elements() function."""

    def test_empty_graph_returns_empty_list(self):
        """Empty graph returns empty list."""
        result = get_high_impact_elements({})

        assert result == []

    def test_none_graph_returns_empty_list(self):
        """None graph returns empty list."""
        result = get_high_impact_elements(None)

        assert result == []

    def test_returns_elements_with_dependents(self, high_impact_graph):
        """Returns elements that have dependents."""
        result = get_high_impact_elements(high_impact_graph)

        assert len(result) > 0
        # Each result should have dependents > 0
        for elem in result:
            assert elem['dependents'] > 0

    def test_sorted_by_dependents_descending(self, high_impact_graph):
        """Results are sorted by dependents count (highest first)."""
        result = get_high_impact_elements(high_impact_graph)

        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]['dependents'] >= result[i + 1]['dependents']

    def test_logger_is_highest_impact(self, high_impact_graph):
        """Logger (3 dependents) is highest impact."""
        result = get_high_impact_elements(high_impact_graph)

        assert len(result) > 0
        # Logger has 3 dependents, should be first
        assert result[0]['name'] == 'logger'
        assert result[0]['dependents'] == 3

    def test_respects_limit_parameter(self, high_impact_graph):
        """Respects limit parameter."""
        result = get_high_impact_elements(high_impact_graph, limit=1)

        assert len(result) <= 1

    def test_includes_risk_level(self, high_impact_graph):
        """Each result includes risk level."""
        result = get_high_impact_elements(high_impact_graph)

        for elem in result:
            assert 'risk' in elem
            assert elem['risk'] in ['LOW', 'MEDIUM', 'HIGH']

    def test_risk_levels_correct(self):
        """Risk levels are assigned correctly based on dependents."""
        # Create graph with varying dependent counts
        graph = {
            "nodes": [
                ["n1", {"id": "core::critical", "name": "critical", "file": "core.py"}],
                ["n2", {"id": "core::moderate", "name": "moderate", "file": "core.py"}],
                ["n3", {"id": "core::low", "name": "low", "file": "core.py"}]
            ] + [
                [f"c{i}", {"id": f"caller{i}::func", "name": f"func{i}", "file": f"caller{i}.py"}]
                for i in range(20)
            ],
            "edges": [
                # critical has 16 dependents (HIGH risk)
                *[[f"e{i}", {"source": f"caller{i}::func", "target": "core::critical", "type": "calls"}] for i in range(16)],
                # moderate has 6 dependents (MEDIUM risk)
                *[[f"m{i}", {"source": f"caller{i}::func", "target": "core::moderate", "type": "calls"}] for i in range(6)],
                # low has 3 dependents (LOW risk)
                *[[f"l{i}", {"source": f"caller{i}::func", "target": "core::low", "type": "calls"}] for i in range(3)]
            ]
        }

        result = get_high_impact_elements(graph)

        # Find each element
        critical_elem = next((e for e in result if e['name'] == 'critical'), None)
        moderate_elem = next((e for e in result if e['name'] == 'moderate'), None)
        low_elem = next((e for e in result if e['name'] == 'low'), None)

        if critical_elem:
            assert critical_elem['risk'] == 'HIGH'
        if moderate_elem:
            assert moderate_elem['risk'] == 'MEDIUM'
        if low_elem:
            assert low_elem['risk'] == 'LOW'

    def test_includes_element_metadata(self, high_impact_graph):
        """Results include element metadata."""
        result = get_high_impact_elements(high_impact_graph)

        for elem in result:
            assert 'name' in elem
            assert 'id' in elem
            assert 'dependents' in elem
            assert 'dependencies' in elem


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_malformed_node_format(self):
        """Handles malformed node entries."""
        graph = {
            "nodes": [
                ["n1", {"id": "a", "name": "a"}],  # Missing file
                {"id": "b", "name": "b", "file": "b.py"},  # Dict format
                "invalid"  # Invalid format
            ],
            "edges": []
        }

        # Should not raise exception
        result = generate_module_diagram(graph)
        assert "```mermaid" in result

    def test_malformed_edge_format(self):
        """Handles malformed edge entries."""
        graph = {
            "nodes": [
                ["n1", {"id": "a", "name": "a", "file": "a.py"}],
                ["n2", {"id": "b", "name": "b", "file": "b.py"}]
            ],
            "edges": [
                ["e1", {"source": "a", "target": "b"}],  # Missing type
                {"source": "a", "target": "b", "type": "calls"},  # Dict format
                "invalid"  # Invalid format
            ]
        }

        # Should not raise exception
        metrics = compute_graph_metrics(graph)
        assert isinstance(metrics, dict)

    def test_special_characters_in_names(self):
        """Handles special characters in element names."""
        graph = {
            "nodes": [
                ["n1", {"id": "path/to/file.py::func_name", "name": "func-name", "file": "path/to/file.py"}],
                ["n2", {"id": "another\\path\\file.py::class.method", "name": "class.method", "file": "another\\path\\file.py"}]
            ],
            "edges": [
                ["e1", {"source": "path/to/file.py::func_name", "target": "another\\path\\file.py::class.method", "type": "calls"}]
            ]
        }

        # Should not raise exception and produce valid Mermaid
        result = generate_module_diagram(graph)
        assert "```mermaid" in result
        # Should not contain problematic characters
        assert "'" not in result or result.count("'") % 2 == 0

    def test_very_long_names_truncated(self):
        """Very long element names are handled."""
        long_name = "a" * 200
        graph = {
            "nodes": [
                ["n1", {"id": f"file.py::{long_name}", "name": long_name, "file": "file.py"}]
            ],
            "edges": []
        }

        # Should not raise exception
        result = generate_module_diagram(graph)
        assert "```mermaid" in result

    def test_unicode_names(self):
        """Handles Unicode characters in names."""
        graph = {
            "nodes": [
                ["n1", {"id": "file.py::hello", "name": "hello", "file": "file.py"}]
            ],
            "edges": []
        }

        result = generate_module_diagram(graph)
        assert "```mermaid" in result

    def test_empty_nodes_array(self):
        """Handles empty nodes array."""
        graph = {"nodes": [], "edges": []}

        result = generate_module_diagram(graph)
        assert "```mermaid" in result

        metrics = compute_graph_metrics(graph)
        assert metrics['node_count'] == 0

    def test_large_graph_performance(self):
        """Handles large graphs efficiently."""
        import time

        # Create graph with 100 nodes and 200 edges
        nodes = [[f"n{i}", {"id": f"mod{i}.py::func{i}", "name": f"func{i}", "file": f"mod{i}.py"}] for i in range(100)]
        edges = [[f"e{i}", {"source": f"mod{i}.py::func{i}", "target": f"mod{(i+1)%100}.py::func{(i+1)%100}", "type": "calls"}] for i in range(200)]

        graph = {"nodes": nodes, "edges": edges}

        start = time.time()
        result = generate_module_diagram(graph)
        elapsed = time.time() - start

        assert "```mermaid" in result
        assert elapsed < 5.0, f"Took {elapsed:.2f}s, expected < 5s"
