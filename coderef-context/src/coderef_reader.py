"""
CodeRef Data Reader

Reads pre-scanned data from .coderef/ directory instead of calling CLI.
Used by MCP server tools to provide code intelligence.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class CodeRefReader:
    """Reads and queries .coderef/ data files."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.coderef_dir = self.project_path / ".coderef"

    def _load_json(self, filename: str) -> Any:
        """Load JSON file from .coderef/ directory."""
        file_path = self.coderef_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"CodeRef data not found: {filename}. Run scan first.")

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_text(self, filename: str) -> str:
        """Load text file from .coderef/ directory."""
        file_path = self.coderef_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"CodeRef data not found: {filename}. Run scan first.")

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_index(self) -> List[Dict[str, Any]]:
        """Get all scanned elements from index.json."""
        return self._load_json("index.json")

    def get_graph(self) -> Dict[str, Any]:
        """Get dependency graph from graph.json."""
        return self._load_json("graph.json")

    def get_context(self, format: str = "json") -> Any:
        """Get project context (json or markdown)."""
        if format == "json":
            return self._load_json("context.json")
        else:
            return self._load_text("context.md")

    def get_patterns(self) -> Dict[str, Any]:
        """Get code patterns from reports/patterns.json."""
        return self._load_json("reports/patterns.json")

    def get_coverage(self) -> Dict[str, Any]:
        """Get test coverage from reports/coverage.json."""
        return self._load_json("reports/coverage.json")

    def get_validation(self) -> Dict[str, Any]:
        """Get reference validation from reports/validation.json."""
        return self._load_json("reports/validation.json")

    def get_drift(self) -> Dict[str, Any]:
        """Get drift detection from reports/drift.json."""
        return self._load_json("reports/drift.json")

    def get_diagram(self, diagram_type: str = "dependencies", format: str = "mermaid") -> str:
        """Get diagram from diagrams/ directory."""
        filename = f"diagrams/{diagram_type}.{format}"
        return self._load_text(filename)

    def get_export(self, format: str) -> Any:
        """Get export data from exports/ directory."""
        if format in ["json", "jsonld"]:
            return self._load_json(f"exports/graph.{format}")
        else:
            return self._load_text(f"exports/diagram-wrapped.md")

    def query_elements(
        self,
        element_type: Optional[str] = None,
        name_filter: Optional[str] = None,
        file_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query elements from index with filters."""
        elements = self.get_index()

        if element_type:
            elements = [e for e in elements if e.get("type") == element_type]

        if name_filter:
            elements = [e for e in elements if name_filter.lower() in e.get("name", "").lower()]

        if file_filter:
            elements = [e for e in elements if file_filter in e.get("file", "")]

        return elements

    def find_element(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a specific element by name."""
        elements = self.get_index()
        for element in elements:
            if element.get("name") == name:
                return element
        return None

    def get_element_relationships(self, element_name: str) -> Dict[str, Any]:
        """Get relationships for a specific element from graph."""
        graph = self.get_graph()

        # Find element in graph
        for node_id, node_data in graph.get("nodes", {}).items():
            if node_data.get("name") == element_name:
                return {
                    "element": node_data,
                    "dependencies": graph.get("edges", {}).get(node_id, []),
                    "dependents": self._find_dependents(graph, node_id)
                }

        return {"element": None, "dependencies": [], "dependents": []}

    def _find_dependents(self, graph: Dict[str, Any], target_id: str) -> List[str]:
        """Find all elements that depend on target element."""
        dependents = []
        edges = graph.get("edges", {})

        for node_id, deps in edges.items():
            if target_id in deps:
                dependents.append(node_id)

        return dependents

    def exists(self) -> bool:
        """Check if .coderef/ directory exists with required files."""
        required_files = ["index.json", "graph.json", "context.json"]
        return all((self.coderef_dir / f).exists() for f in required_files)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about scanned codebase."""
        if not self.exists():
            return {"error": "No scan data available"}

        index = self.get_index()

        # Count by type
        type_counts = {}
        for element in index:
            elem_type = element.get("type", "unknown")
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

        return {
            "total_elements": len(index),
            "elements_by_type": type_counts,
            "coderef_dir": str(self.coderef_dir),
            "has_graph": (self.coderef_dir / "graph.json").exists(),
            "has_patterns": (self.coderef_dir / "reports/patterns.json").exists(),
            "has_coverage": (self.coderef_dir / "reports/coverage.json").exists(),
        }

    def get_diagram_wrapped(self) -> str:
        """Get the ready-to-use diagram with usage instructions.

        This is a pre-formatted Mermaid diagram that includes:
        - Complete architecture visualization
        - Styling and formatting
        - Usage instructions for rendering

        Perfect for embedding in agent responses or documentation.
        """
        return self._load_text("exports/diagram-wrapped.md")
