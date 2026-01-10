"""
Code Analyzer - Orchestrates Code Analysis.

WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3B (GRAPH-001)

High-level analyzer that coordinates between coderef_scan,
AST parsing, characteristics detection, and graph queries.

Phase 3B integrates coderef query CLI for dependency/consumer/import analysis.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import subprocess
import shlex

from ..types import CodeCharacteristics
from .characteristics import CharacteristicsDetector


class CodeAnalyzer:
    """
    Orchestrates code analysis for resource sheet generation.

    Handles calling coderef_scan, parsing results, and detecting
    characteristics for module selection.
    """

    def __init__(self):
        self.detector = CharacteristicsDetector()

    async def _load_dependency_graph(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Load dependency graph from .coderef/exports/graph.json.

        Args:
            project_path: Project root path

        Returns:
            Graph data or None if unavailable
        """
        try:
            graph_path = Path(project_path) / ".coderef" / "exports" / "graph.json"
            if graph_path.exists():
                with open(graph_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Warning: Failed to load dependency graph: {e}")
            return None

    async def _query_graph_relationships(
        self,
        graph: Dict[str, Any],
        target_element: str,
        relationship_type: str
    ) -> List[Dict[str, Any]]:
        """
        Query relationships from dependency graph.

        Args:
            graph: Loaded graph data
            target_element: Element name to query
            relationship_type: Type of relationship (depends-on, imports, etc.)

        Returns:
            List of related elements
        """
        if not graph:
            return []

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        # Find target node
        target_node = None
        for node in nodes:
            if target_element in node.get("name", ""):
                target_node = node
                break

        if not target_node:
            return []

        target_id = target_node.get("id")
        results = []

        # Query edges based on relationship type
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            edge_type = edge.get("type", "")

            if relationship_type == "depends-on" and source == target_id:
                # Find target node details
                for node in nodes:
                    if node.get("id") == target:
                        results.append({
                            "name": node.get("name", ""),
                            "file": node.get("file", ""),
                            "type": node.get("type", "")
                        })

            elif relationship_type == "depends-on-me" and target == target_id:
                # Find source node details
                for node in nodes:
                    if node.get("id") == source:
                        results.append({
                            "name": node.get("name", ""),
                            "file": node.get("file", ""),
                            "type": node.get("type", "")
                        })

        return results

    async def query_dependencies(self, element_name: str, project_path: str) -> List[Dict[str, Any]]:
        """
        Query what this element depends on.

        GRAPH-001: Queries dependency graph from .coderef/exports/graph.json

        Args:
            element_name: Element to analyze
            project_path: Project root path

        Returns:
            List of dependencies (elements this code depends on/imports/calls)
        """
        graph = await self._load_dependency_graph(project_path)
        if graph:
            return await self._query_graph_relationships(graph, element_name, "depends-on")
        return []

    async def query_consumers(self, element_name: str, project_path: str) -> List[Dict[str, Any]]:
        """
        Query what consumes/calls/imports this element.

        GRAPH-001: Queries dependency graph from .coderef/exports/graph.json

        Args:
            element_name: Element to analyze
            project_path: Project root path

        Returns:
            List of consumers (elements that use/import/call this code)
        """
        graph = await self._load_dependency_graph(project_path)
        if graph:
            return await self._query_graph_relationships(graph, element_name, "depends-on-me")
        return []

    async def query_imports(self, element_name: str, project_path: str) -> List[Dict[str, Any]]:
        """
        Query what this element imports.

        GRAPH-001: Queries dependency graph from .coderef/exports/graph.json

        Args:
            element_name: Element to analyze
            project_path: Project root path

        Returns:
            List of imported modules/symbols
        """
        graph = await self._load_dependency_graph(project_path)
        if graph:
            return await self._query_graph_relationships(graph, element_name, "imports")
        return []

    async def query_callers(self, element_name: str, project_path: str) -> List[Dict[str, Any]]:
        """
        Query what calls this element.

        GRAPH-001: Queries dependency graph from .coderef/exports/graph.json

        Args:
            element_name: Element to analyze
            project_path: Project root path

        Returns:
            List of callers (functions/methods that invoke this code)
        """
        graph = await self._load_dependency_graph(project_path)
        if graph:
            return await self._query_graph_relationships(graph, element_name, "calls-me")
        return []

    async def analyze_element(
        self,
        element_name: str,
        project_path: str,
        use_coderef_scan: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze a code element to extract structure and characteristics.

        Args:
            element_name: Name of element to analyze (e.g., "AuthService")
            project_path: Path to project root
            use_coderef_scan: DEPRECATED - always False

        Returns:
            Analysis result with scan_data, characteristics, and metadata
        """
        scan_data = {}
        characteristics: CodeCharacteristics = {}

        # Always use file-based detection (coderef CLI removed)
        scan_data = None

        # File-based detection
        if not characteristics:
            file_path = self._find_element_file(element_name, project_path)
            if file_path:
                code = Path(file_path).read_text(encoding="utf-8")
                language = file_path.suffix.lstrip(".")
                characteristics = self.detector.detect_from_file_content(code, language)

        return {
            "element_name": element_name,
            "scan_data": scan_data,
            "characteristics": characteristics,
            "analysis_method": "file_content",
        }

    def _find_element_file(self, element_name: str, project_path: str) -> Optional[str]:
        """
        Find file containing the element.

        Args:
            element_name: Element name to find
            project_path: Project root

        Returns:
            File path if found, None otherwise
        """
        project = Path(project_path)

        # Common patterns for file names
        patterns = [
            f"**/{element_name}.ts",
            f"**/{element_name}.tsx",
            f"**/{element_name}.js",
            f"**/{element_name}.jsx",
            f"**/{element_name}.py",
            f"**/{element_name.lower()}.ts",
            f"**/{element_name.lower()}.tsx",
        ]

        for pattern in patterns:
            matches = list(project.glob(pattern))
            if matches:
                return str(matches[0])

        return None

    def get_characteristics_summary(self, characteristics: CodeCharacteristics) -> str:
        """
        Generate human-readable summary of detected characteristics.

        Args:
            characteristics: Detected characteristics

        Returns:
            Formatted summary string
        """
        true_characteristics = [k for k, v in characteristics.items() if v]

        if not true_characteristics:
            return "No characteristics detected"

        summary = "Detected Characteristics:\n"
        for char in true_characteristics:
            summary += f"  ✓ {char.replace('_', ' ').title()}\n"

        return summary
