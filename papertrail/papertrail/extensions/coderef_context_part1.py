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

            # Handle different index.json structures
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

        Example:
            {%% set components = coderef.get_components_added(
                "baseline-index.json",
                ".coderef/index.json"
            ) %%}
            {%% for comp in components %%}
            - {{ comp.name }} ({{ comp.type }}) in {{ comp.file }}
            {%% endfor %%}
        """
        baseline = self._load_index(Path(baseline_path))
        current = self._load_index(Path(current_path))

        # Create sets of element identifiers for comparison
        baseline_ids = set()
        for elem in baseline:
            if elem.get("type") in ["component", "class"]:
                # Use name + file as unique identifier
                elem_id = f"{elem.get('name')}:{elem.get('file')}"
                baseline_ids.add(elem_id)

        # Find components in current that aren't in baseline
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
    # (continued in next file due to length limits)
