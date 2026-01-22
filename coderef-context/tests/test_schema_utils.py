"""
Tests for schema version detection and normalization.

Tests both v1.0.0 (flat array) and v2.0.0 (nested structure) formats.
"""

import pytest
from src.schema_utils import (
    detect_schema_version,
    normalize_index_data,
    normalize_graph_nodes,
    normalize_graph_data
)


class TestSchemaVersionDetection:
    """Test schema version detection logic."""

    def test_detect_v1_schema(self):
        """v1.0.0 schema: flat array."""
        data = [
            {"name": "func1", "type": "function", "file": "test.py", "line": 10},
            {"name": "func2", "type": "function", "file": "test.py", "line": 20}
        ]
        assert detect_schema_version(data) == "v1.0.0"

    def test_detect_v2_schema(self):
        """v2.0.0 schema: dict with 'version' field."""
        data = {
            "version": "v2.0.0",
            "elements": [
                {"name": "func1", "type": "function", "file": "test.py", "line": 10}
            ]
        }
        assert detect_schema_version(data) == "v2.0.0"

    def test_detect_unknown_schema(self):
        """Unknown schema: dict without 'version' field."""
        data = {"random": "data"}
        assert detect_schema_version(data) == "unknown"

    def test_detect_empty_list(self):
        """Empty list should be detected as v1.0.0."""
        data = []
        assert detect_schema_version(data) == "v1.0.0"

    def test_detect_production_v2_schema(self):
        """Production v2 schema: version '2.0.0' without 'v' prefix."""
        data = {
            "version": "2.0.0",
            "elements": [
                {"name": "func1", "type": "function", "file": "test.py", "line": 10}
            ]
        }
        assert detect_schema_version(data) == "2.0.0"


class TestIndexDataNormalization:
    """Test index.json normalization."""

    def test_normalize_v1_index_unchanged(self):
        """v1.0.0 index should pass through unchanged."""
        data = [
            {"name": "func1", "type": "function", "file": "test.py", "line": 10},
            {"name": "func2", "type": "function", "file": "test.py", "line": 20}
        ]
        result = normalize_index_data(data)
        assert result == data
        assert len(result) == 2

    def test_normalize_v2_index_extracts_elements(self):
        """v2.0.0 index should extract 'elements' array."""
        data = {
            "version": "v2.0.0",
            "elements": [
                {"name": "func1", "type": "function", "file": "test.py", "line": 10},
                {"name": "func2", "type": "function", "file": "test.py", "line": 20}
            ]
        }
        result = normalize_index_data(data)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "func1"
        assert result[1]["name"] == "func2"

    def test_normalize_v2_index_empty_elements(self):
        """v2.0.0 with empty elements should return empty list."""
        data = {
            "version": "v2.0.0",
            "elements": []
        }
        result = normalize_index_data(data)
        assert result == []

    def test_normalize_v2_index_missing_elements(self):
        """v2.0.0 without 'elements' field should return empty list."""
        data = {
            "version": "v2.0.0"
        }
        result = normalize_index_data(data)
        assert result == []

    def test_normalize_unknown_schema_returns_empty(self):
        """Unknown schema should return empty array."""
        data = {"random": "data"}
        result = normalize_index_data(data)
        assert result == []

    def test_normalize_production_v2_index(self):
        """Production v2.0.0 (no 'v' prefix) should extract elements."""
        data = {
            "version": "2.0.0",
            "generatedAt": "2026-01-20T17:59:45.297Z",
            "projectPath": "C:\\Users\\willh\\Desktop\\games",
            "totalElements": 2,
            "elements": [
                {"name": "GameClient", "type": "component", "file": "game.tsx", "line": 10},
                {"name": "Tetris", "type": "component", "file": "tetris.tsx", "line": 20}
            ]
        }
        result = normalize_index_data(data)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "GameClient"
        assert result[1]["name"] == "Tetris"


class TestGraphNodesNormalization:
    """Test graph.json nodes normalization."""

    def test_normalize_v1_nodes_unchanged(self):
        """v1.0.0 nodes (dict) should pass through unchanged."""
        nodes = {
            "node1": {"id": "node1", "name": "func1"},
            "node2": {"id": "node2", "name": "func2"}
        }
        result = normalize_graph_nodes(nodes)
        assert result == nodes
        assert len(result) == 2

    def test_normalize_v2_nodes_converts_list_to_dict(self):
        """v2.0.0 nodes (list) should convert to dict."""
        nodes = [
            {"id": "node1", "name": "func1", "type": "function"},
            {"id": "node2", "name": "func2", "type": "function"}
        ]
        result = normalize_graph_nodes(nodes)
        assert isinstance(result, dict)
        assert len(result) == 2
        assert "node1" in result
        assert "node2" in result
        assert result["node1"]["name"] == "func1"
        assert result["node2"]["name"] == "func2"

    def test_normalize_v2_nodes_empty_list(self):
        """v2.0.0 with empty nodes list should return empty dict."""
        nodes = []
        result = normalize_graph_nodes(nodes)
        assert result == {}

    def test_normalize_v2_nodes_missing_id(self):
        """v2.0.0 nodes without 'id' field should be skipped."""
        nodes = [
            {"id": "node1", "name": "func1"},
            {"name": "func2"}  # Missing 'id'
        ]
        result = normalize_graph_nodes(nodes)
        assert len(result) == 1
        assert "node1" in result
        assert "func2" not in result


class TestGraphDataNormalization:
    """Test complete graph.json normalization."""

    def test_normalize_v1_graph_unchanged(self):
        """v1.0.0 graph should pass through unchanged."""
        data = {
            "nodes": {
                "node1": {"id": "node1", "name": "func1"},
                "node2": {"id": "node2", "name": "func2"}
            },
            "edges": {
                "node1": ["node2"]
            }
        }
        result = normalize_graph_data(data)
        assert result == data

    def test_normalize_v2_graph_converts_nodes(self):
        """v2.0.0 graph should convert nodes list to dict."""
        data = {
            "version": "v2.0.0",
            "nodes": [
                {"id": "node1", "name": "func1"},
                {"id": "node2", "name": "func2"}
            ],
            "edges": {
                "node1": ["node2"]
            }
        }
        result = normalize_graph_data(data)
        assert isinstance(result["nodes"], dict)
        assert len(result["nodes"]) == 2
        assert "node1" in result["nodes"]
        assert "node2" in result["nodes"]
        assert result["edges"] == data["edges"]

    def test_normalize_v2_graph_empty_nodes(self):
        """v2.0.0 graph with empty nodes should return empty dict."""
        data = {
            "version": "v2.0.0",
            "nodes": [],
            "edges": []
        }
        result = normalize_graph_data(data)
        assert result["nodes"] == {}
        assert result["edges"] == []

    def test_normalize_unknown_graph_returns_empty(self):
        """Unknown schema should return empty structure."""
        data = {"random": "data"}
        result = normalize_graph_data(data)
        assert result == {"nodes": {}, "edges": []}


class TestRealWorldScenarios:
    """Test with realistic data structures."""

    def test_gameclient_v2_complexity(self):
        """Simulate GameClient component from v2.0.0 schema."""
        index_data = {
            "version": "v2.0.0",
            "elements": [
                {
                    "name": "GameClient",
                    "type": "component",
                    "file": "src/components/GameClient.tsx",
                    "line": 15,
                    "parameters": [
                        {"name": "game", "type": "Game"},
                        {"name": "onConnect", "type": "function"}
                    ]
                }
            ]
        }
        result = normalize_index_data(index_data)
        assert len(result) == 1
        assert result[0]["name"] == "GameClient"
        assert len(result[0]["parameters"]) == 2

    def test_tetris_v2_complexity(self):
        """Simulate Tetris component from v2.0.0 schema."""
        index_data = {
            "version": "v2.0.0",
            "elements": [
                {
                    "name": "Tetris",
                    "type": "component",
                    "file": "src/games/tetris/Tetris.tsx",
                    "line": 20,
                    "parameters": []
                }
            ]
        }
        result = normalize_index_data(index_data)
        assert len(result) == 1
        assert result[0]["name"] == "Tetris"
        assert result[0]["parameters"] == []

    def test_games_registry_v2_query(self):
        """Simulate GAMES_REGISTRY query from v2.0.0 schema."""
        graph_data = {
            "version": "v2.0.0",
            "nodes": [
                {
                    "id": "GAMES_REGISTRY",
                    "name": "GAMES_REGISTRY",
                    "type": "const",
                    "file": "src/config/games.ts",
                    "line": 5
                },
                {
                    "id": "GameLauncher",
                    "name": "GameLauncher",
                    "type": "component",
                    "file": "src/components/GameLauncher.tsx",
                    "line": 10
                }
            ],
            "edges": {
                "GameLauncher": ["GAMES_REGISTRY"]
            }
        }
        result = normalize_graph_data(graph_data)
        assert isinstance(result["nodes"], dict)
        assert "GAMES_REGISTRY" in result["nodes"]
        assert "GameLauncher" in result["nodes"]
        assert result["edges"]["GameLauncher"] == ["GAMES_REGISTRY"]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_normalize_index_with_invalid_json(self):
        """Invalid data should return empty array with logged error."""
        data = None
        result = normalize_index_data(data)
        # Should not crash, should return empty array
        assert result == []

    def test_normalize_graph_with_invalid_json(self):
        """Invalid data should return empty structure with logged error."""
        data = None
        result = normalize_graph_data(data)
        # Should not crash, should return empty structure
        assert result == {"nodes": {}, "edges": []}

    def test_detect_schema_with_none(self):
        """None input should return 'unknown'."""
        result = detect_schema_version(None)
        assert result == "unknown"
