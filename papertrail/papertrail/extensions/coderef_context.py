"""
CodeRef Context Extension - Integration with coderef-context MCP server

Provides template tags for code intelligence:
- {% coderef.get_components_added(baseline, current) %} - Components added
- {% coderef.get_functions_added(baseline, current) %} - Functions added
- {% coderef.calculate_complexity_delta(baseline, current) %} - Complexity change

Enhanced with index.json snapshot comparison (WO-PAPERTRAIL-EXTENSIONS-001 Phase 2)
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import json


class CodeRefContextExtension:
    """
    Template extension for coderef-context integration

    Enhanced with index.json snapshot comparison for accurate component/function tracking
    """

    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize CodeRef context extension

        Args:
            project_path: Default project path for scans
        """
        self.project_path = Path(project_path) if project_path else None

    def _load_index(self, index_path: Path) -> List[Dict[str, Any]]:
        """
        Load index.json file

        Args:
            index_path: Path to index.json

        Returns:
            list: List of code elements or empty list if file doesn't exist
        """
        try:
            if not index_path.exists():
                return []

            with open(index_path, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "elements" in data:
                return data["elements"]
            else:
                return []

        except (json.JSONDecodeError, OSError):
            return []

    def get_components_added(
        self,
        baseline_path: str,
        current_path: str
    ) -> List[Dict[str, Any]]:
        """
        Compare two index.json snapshots to find added components

        Args:
            baseline_path: Path to baseline index.json (feature start)
            current_path: Path to current index.json (feature end)

        Returns:
            list: List of added components with name, type, file, line
        """
        baseline = self._load_index(Path(baseline_path))
        current = self._load_index(Path(current_path))

        baseline_ids = set()
        for elem in baseline:
            if elem.get("type") in ["component", "class"]:
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                baseline_ids.add(elem_id)

        added_components = []
        for elem in current:
            if elem.get("type") in ["component", "class"]:
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                if elem_id not in baseline_ids:
                    added_components.append({
                        "name": elem.get("name", ""),
                        "type": elem.get("type", ""),
                        "file": elem.get("file", ""),
                        "line": elem.get("line", 0)
                    })

        return added_components

    def get_functions_added(
        self,
        baseline_path: str,
        current_path: str
    ) -> List[Dict[str, Any]]:
        """
        Compare two index.json snapshots to find added functions

        Args:
            baseline_path: Path to baseline index.json
            current_path: Path to current index.json

        Returns:
            list: List of added functions with name, type, file, line
        """
        baseline = self._load_index(Path(baseline_path))
        current = self._load_index(Path(current_path))

        baseline_ids = set()
        for elem in baseline:
            if elem.get("type") in ["function", "method"]:
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                baseline_ids.add(elem_id)

        added_functions = []
        for elem in current:
            if elem.get("type") in ["function", "method"]:
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                if elem_id not in baseline_ids:
                    added_functions.append({
                        "name": elem.get("name", ""),
                        "type": elem.get("type", ""),
                        "file": elem.get("file", ""),
                        "line": elem.get("line", 0)
                    })

        return added_functions

    def calculate_complexity_delta(
        self,
        baseline_path: str,
        current_path: str
    ) -> float:
        """
        Calculate average complexity change between two snapshots

        Args:
            baseline_path: Path to baseline index.json
            current_path: Path to current index.json

        Returns:
            float: Average complexity change (positive = increased, negative = decreased)
        """
        baseline = self._load_index(Path(baseline_path))
        current = self._load_index(Path(current_path))

        baseline_complexity = {}
        for elem in baseline:
            if "complexity" in elem:
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                baseline_complexity[elem_id] = elem["complexity"]

        current_complexity = {}
        for elem in current:
            if "complexity" in elem:
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                current_complexity[elem_id] = elem["complexity"]

        deltas = []
        for elem_id in current_complexity:
            if elem_id in baseline_complexity:
                delta = current_complexity[elem_id] - baseline_complexity[elem_id]
                deltas.append(delta)

        return sum(deltas) / len(deltas) if deltas else 0.0

    def get_all_changes(
        self,
        baseline_path: str,
        current_path: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive change summary between two snapshots

        Args:
            baseline_path: Path to baseline index.json
            current_path: Path to current index.json

        Returns:
            dict: Complete change summary with components, functions, complexity
        """
        return {
            "components_added": self.get_components_added(baseline_path, current_path),
            "functions_added": self.get_functions_added(baseline_path, current_path),
            "complexity_delta": self.calculate_complexity_delta(baseline_path, current_path)
        }

    # Legacy methods (kept for backward compatibility)

    def scan(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan codebase for dependencies (legacy stub)
        """
        path = project_path or self.project_path
        return {
            "status": "success",
            "project_path": str(path) if path else None,
            "elements_found": 0,
            "dependencies": 0,
            "message": "(Legacy stub - use get_components_added/get_functions_added)"
        }

    def query(self, element: str, query_type: str = "calls") -> Dict[str, Any]:
        """
        Query code relationships (legacy stub)
        """
        return {
            "status": "success",
            "element": element,
            "query_type": query_type,
            "results": [],
            "message": "(Legacy stub)"
        }

    def impact(self, element: str) -> Dict[str, Any]:
        """
        Analyze impact of changing element (legacy stub)
        """
        return {
            "status": "success",
            "element": element,
            "affected_files": [],
            "risk_level": "unknown",
            "message": "(Legacy stub)"
        }
