"""
Impact Analysis Handler for Code Change Impact Assessment.

Analyzes transitive dependencies using ElementData.dependencies and ElementData.calledBy
to determine the ripple effects of code changes.

Part of WO-WORKFLOW-SCANNER-INTEGRATION-001 IMPL-004, IMPL-005, IMPL-006
"""

from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from coderef.utils import read_coderef_output

from logger_config import logger


class ImpactAnalyzer:
    """
    Analyzes code change impact using relationship graphs.

    Uses ElementData.dependencies and ElementData.calledBy fields to:
    1. Perform transitive dependency traversal (BFS)
    2. Calculate impact scores (low/medium/high/critical)
    3. Generate impact reports with Mermaid dependency graphs
    """

    def __init__(self, project_path: Path):
        """
        Initialize ImpactAnalyzer.

        Args:
            project_path: Path to project root directory
        """
        self.project_path = project_path
        self.elements_cache = None  # Lazy-loaded from .coderef/index.json
        logger.debug(f"ImpactAnalyzer initialized for: {project_path}")

    def _load_elements(self) -> List[Dict]:
        """
        Load elements from .coderef/index.json (lazy loading).

        Returns:
            List of ElementData dictionaries
        """
        if self.elements_cache is None:
            try:
                self.elements_cache = read_coderef_output(str(self.project_path), 'index')
                if not self.elements_cache:
                    self.elements_cache = []
                logger.info(f"Loaded {len(self.elements_cache)} elements from .coderef/index.json")
            except Exception as e:
                logger.warning(f"Failed to load .coderef/index.json: {str(e)}")
                self.elements_cache = []

        return self.elements_cache

    def _find_element_by_name(self, element_name: str) -> Optional[Dict]:
        """
        Find an element by name in the loaded elements.

        Args:
            element_name: Name of the element to find

        Returns:
            ElementData dict or None if not found
        """
        elements = self._load_elements()

        for elem in elements:
            if elem.get('name') == element_name:
                return elem

        return None

    def traverse_dependencies(
        self,
        element_name: str,
        max_depth: int = 3,
        direction: str = 'downstream'
    ) -> List[Dict]:
        """
        Traverse dependencies using BFS to find all affected elements.

        Args:
            element_name: Name of the element to analyze
            max_depth: Maximum traversal depth (default: 3)
            direction: 'downstream' (who depends on me) or 'upstream' (what I depend on)

        Returns:
            List of affected elements with:
            - name: Element name
            - type: Element type
            - file: File path
            - depth: Distance from starting element
            - path: Relationship path (e.g., "A → B → C")
        """
        logger.debug(f"Traversing {direction} dependencies for: {element_name}, max_depth={max_depth}")

        elements = self._load_elements()
        if not elements:
            logger.warning("No elements loaded - cannot traverse dependencies")
            return []

        # Build relationship map: element_name -> [dependent_names]
        relationship_map: Dict[str, List[str]] = {}

        for elem in elements:
            name = elem.get('name')
            if not name:
                continue

            # Skip .venv and node_modules
            file_path = elem.get('file', '')
            if '.venv' in file_path or 'node_modules' in file_path:
                continue

            if direction == 'downstream':
                # Who calls/uses this element? (calledBy field)
                calledBy = elem.get('calledBy', [])
                if calledBy:
                    relationship_map[name] = calledBy
            else:
                # What does this element depend on? (dependencies field)
                dependencies = elem.get('dependencies', [])
                if dependencies:
                    relationship_map[name] = dependencies

        # BFS traversal
        affected = []
        visited: Set[str] = set()
        queue: List[Tuple[str, int, List[str]]] = [(element_name, 0, [element_name])]

        visited.add(element_name)

        while queue:
            current_name, depth, path = queue.pop(0)

            # Stop if max depth reached
            if depth >= max_depth:
                continue

            # Get elements that depend on current element
            dependents = relationship_map.get(current_name, [])

            for dependent in dependents:
                if dependent not in visited:
                    visited.add(dependent)

                    # Find full element data
                    elem_data = self._find_element_by_name(dependent)
                    if elem_data:
                        affected.append({
                            'name': dependent,
                            'type': elem_data.get('type', 'unknown'),
                            'file': elem_data.get('file', ''),
                            'line': elem_data.get('line', 0),
                            'depth': depth + 1,
                            'path': ' → '.join(path + [dependent])
                        })

                        # Add to queue for further traversal
                        queue.append((dependent, depth + 1, path + [dependent]))

        logger.info(f"Found {len(affected)} affected elements (max_depth={max_depth})")
        return affected

    def calculate_impact_score(self, affected_elements: List[Dict]) -> Dict:
        """
        Calculate impact score based on number of affected elements.

        Args:
            affected_elements: List from traverse_dependencies()

        Returns:
            dict with:
            - impact_score: int (count of affected elements)
            - risk_level: 'low' | 'medium' | 'high' | 'critical'
            - breakdown: dict with counts by depth
        """
        count = len(affected_elements)

        # Categorize risk level
        if count == 0:
            risk_level = 'low'
        elif count <= 5:
            risk_level = 'low'
        elif count <= 15:
            risk_level = 'medium'
        elif count <= 50:
            risk_level = 'high'
        else:
            risk_level = 'critical'

        # Breakdown by depth
        breakdown = {}
        for elem in affected_elements:
            depth = elem.get('depth', 0)
            breakdown[f'depth_{depth}'] = breakdown.get(f'depth_{depth}', 0) + 1

        logger.info(f"Impact score: {count} affected elements, risk: {risk_level}")

        return {
            'impact_score': count,
            'risk_level': risk_level,
            'breakdown': breakdown,
            'affected_count': count
        }

    def generate_impact_report(
        self,
        element_name: str,
        affected_elements: List[Dict],
        impact_score: Dict
    ) -> str:
        """
        Generate markdown impact report with Mermaid dependency graph.

        Args:
            element_name: Name of the element being analyzed
            affected_elements: List from traverse_dependencies()
            impact_score: Dict from calculate_impact_score()

        Returns:
            Markdown string with report
        """
        risk_level = impact_score.get('risk_level', 'unknown')
        count = impact_score.get('affected_count', 0)

        # Start report
        lines = [
            f"# Impact Analysis: {element_name}",
            "",
            "## Summary",
            "",
            f"- **Affected Elements:** {count}",
            f"- **Risk Level:** {risk_level.upper()}",
            ""
        ]

        # Add breakdown by depth
        breakdown = impact_score.get('breakdown', {})
        if breakdown:
            lines.append("## Impact by Depth")
            lines.append("")
            for depth_key in sorted(breakdown.keys()):
                lines.append(f"- {depth_key.replace('_', ' ').title()}: {breakdown[depth_key]} elements")
            lines.append("")

        # List affected elements
        if affected_elements:
            lines.append("## Affected Elements")
            lines.append("")

            # Group by depth for readability
            by_depth = {}
            for elem in affected_elements:
                depth = elem.get('depth', 0)
                if depth not in by_depth:
                    by_depth[depth] = []
                by_depth[depth].append(elem)

            for depth in sorted(by_depth.keys()):
                lines.append(f"### Depth {depth} ({len(by_depth[depth])} elements)")
                lines.append("")

                for elem in by_depth[depth]:
                    name = elem.get('name', 'unknown')
                    elem_type = elem.get('type', 'unknown')
                    file_path = elem.get('file', '')
                    line = elem.get('line', 0)
                    path = elem.get('path', '')

                    # Format: - ElementName (type) - file:line
                    #         Path: A → B → C
                    lines.append(f"- **{name}** ({elem_type}) - `{file_path}:{line}`")
                    if path:
                        lines.append(f"  - Path: `{path}`")

                lines.append("")

        # Generate Mermaid dependency graph (limit to depth 3 for readability)
        if affected_elements:
            lines.append("## Dependency Graph")
            lines.append("")
            lines.append("```mermaid")
            lines.append("graph TD")

            # Add root node
            lines.append(f"    {self._sanitize_mermaid_id(element_name)}[\"{element_name}\"]")

            # Add edges (limit to first 50 to avoid huge graphs)
            edges_added = set()
            for i, elem in enumerate(affected_elements[:50]):
                path_parts = elem.get('path', '').split(' → ')

                # Create edges for the path
                for j in range(len(path_parts) - 1):
                    source = self._sanitize_mermaid_id(path_parts[j])
                    target = self._sanitize_mermaid_id(path_parts[j + 1])
                    edge = f"{source} --> {target}"

                    if edge not in edges_added:
                        lines.append(f"    {edge}")
                        edges_added.add(edge)

            if len(affected_elements) > 50:
                lines.append(f"    Note[\"... and {len(affected_elements) - 50} more elements\"]")

            lines.append("```")
            lines.append("")

        return '\n'.join(lines)

    def _sanitize_mermaid_id(self, name: str) -> str:
        """
        Sanitize element name for use as Mermaid node ID.

        Args:
            name: Element name

        Returns:
            Sanitized ID (alphanumeric + underscore only)
        """
        import re
        # Replace non-alphanumeric with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure starts with letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'elem_' + sanitized
        return sanitized or 'unknown'

    def analyze_element_impact(
        self,
        element_name: str,
        max_depth: int = 3
    ) -> Optional[Dict]:
        """
        High-level method to perform complete impact analysis.

        Combines traverse_dependencies, calculate_impact_score, and generate_impact_report.

        Args:
            element_name: Name of element to analyze
            max_depth: Maximum traversal depth

        Returns:
            dict with:
            - affected_elements: List of affected elements
            - impact_score: Impact score dict
            - report: Markdown report string
        """
        logger.info(f"Analyzing impact for: {element_name}")

        # Check if element exists
        elem = self._find_element_by_name(element_name)
        if not elem:
            logger.warning(f"Element not found: {element_name}")
            return None

        # Traverse dependencies
        affected = self.traverse_dependencies(element_name, max_depth=max_depth, direction='downstream')

        # Calculate impact score
        score = self.calculate_impact_score(affected)

        # Generate report
        report = self.generate_impact_report(element_name, affected, score)

        return {
            'element_name': element_name,
            'affected_elements': affected,
            'impact_score': score,
            'report': report
        }
