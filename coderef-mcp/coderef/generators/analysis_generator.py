"""Analysis generator for CodeRef2 deep analysis, graph traversal, and coverage detection.

This module provides comprehensive analysis capabilities including:
- Deep impact analysis with multi-level traversal
- Dependency graph traversal with cycle detection
- Test coverage analysis and gap detection
- Complexity metrics calculation
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import deque

from coderef.models import (
    TypeDesignator,
    RelationshipType,
    ImpactAnalysis,
    ImpactNode,
    ImpactLevel,
    CoverageAnalysis,
    CoverageInfo,
    TraversalRequest,
    TraversalResponse,
    TraversalNode,
    Relationship,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures for Graph Analysis
# ============================================================================

@dataclass
class GraphNode:
    """Node in dependency graph."""
    reference: str
    element_type: TypeDesignator
    metadata: Dict[str, Any] = field(default_factory=dict)
    incoming_edges: Set[str] = field(default_factory=set)
    outgoing_edges: Set[str] = field(default_factory=set)


@dataclass
class CyclePath:
    """Representation of a cycle in the dependency graph."""
    path: List[str]  # List of node references forming a cycle


# ============================================================================
# Graph Traversal Engine
# ============================================================================

class DependencyGraphEngine:
    """Engine for analyzing and traversing dependency graphs."""

    def __init__(self):
        """Initialize graph engine."""
        self.logger = logging.getLogger(f"{__name__}.DependencyGraphEngine")
        self.graph: Dict[str, GraphNode] = {}
        self._cycle_cache: Dict[str, List[CyclePath]] = {}

    def add_node(
        self,
        reference: str,
        element_type: TypeDesignator,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a node to the graph.

        Args:
            reference: Node reference
            element_type: Type of element
            metadata: Optional metadata
        """
        if reference not in self.graph:
            self.graph[reference] = GraphNode(
                reference=reference,
                element_type=element_type,
                metadata=metadata or {},
            )

    def add_edge(
        self,
        source: str,
        target: str,
        relationship_type: RelationshipType = RelationshipType.DEPENDS_ON
    ) -> None:
        """Add an edge between nodes.

        Args:
            source: Source node reference
            target: Target node reference
            relationship_type: Type of relationship
        """
        if source not in self.graph:
            self.add_node(source, TypeDesignator.FILE)
        if target not in self.graph:
            self.add_node(target, TypeDesignator.FILE)

        self.graph[source].outgoing_edges.add(target)
        self.graph[target].incoming_edges.add(source)

        self.logger.debug(f"Added edge: {source} -> {target} ({relationship_type.value})")

    def find_all_dependents(
        self,
        reference: str,
        max_depth: int = 5
    ) -> List[Tuple[str, int]]:
        """Find all elements that depend on the given reference.

        Args:
            reference: Starting reference
            max_depth: Maximum traversal depth

        Returns:
            list: Tuples of (reference, depth) for all dependent elements
        """
        if reference not in self.graph:
            return []

        dependents = []
        visited = {reference}
        queue = deque([(reference, 0)])

        while queue and len(visited) < 1000:  # Safety limit
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue

            node = self.graph.get(current)
            if not node:
                continue

            # Find all nodes that depend on current
            for other_ref, other_node in self.graph.items():
                if current in other_node.outgoing_edges and other_ref not in visited:
                    visited.add(other_ref)
                    dependents.append((other_ref, depth + 1))
                    queue.append((other_ref, depth + 1))

        return dependents

    def find_all_dependencies(
        self,
        reference: str,
        max_depth: int = 5
    ) -> List[Tuple[str, int]]:
        """Find all elements that the given reference depends on.

        Args:
            reference: Starting reference
            max_depth: Maximum traversal depth

        Returns:
            list: Tuples of (reference, depth) for all dependency elements
        """
        if reference not in self.graph:
            return []

        dependencies = []
        visited = {reference}
        queue = deque([(reference, 0)])

        while queue and len(visited) < 1000:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue

            node = self.graph.get(current)
            if not node:
                continue

            # Find all dependencies of current
            for dep_ref in node.outgoing_edges:
                if dep_ref not in visited:
                    visited.add(dep_ref)
                    dependencies.append((dep_ref, depth + 1))
                    queue.append((dep_ref, depth + 1))

        return dependencies

    def find_cycles(self, start_reference: str) -> List[CyclePath]:
        """Find all cycles reachable from a starting reference.

        Args:
            start_reference: Starting reference

        Returns:
            list: List of cycle paths
        """
        if start_reference in self._cycle_cache:
            return self._cycle_cache[start_reference]

        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            """DFS to find cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            if node in self.graph:
                for neighbor in self.graph[node].outgoing_edges:
                    if neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        cycles.append(CyclePath(cycle))
                    elif neighbor not in visited:
                        dfs(neighbor, path)

            path.pop()
            rec_stack.remove(node)

        dfs(start_reference, [])
        self._cycle_cache[start_reference] = cycles
        return cycles

    def traverse_breadth_first(
        self,
        start_reference: str,
        max_depth: int = 3,
        direction: str = "both"
    ) -> List[TraversalNode]:
        """Perform breadth-first traversal from a starting node.

        Args:
            start_reference: Starting reference
            max_depth: Maximum traversal depth
            direction: "outgoing", "incoming", or "both"

        Returns:
            list: Traversal nodes in BFS order
        """
        if start_reference not in self.graph:
            return []

        nodes = []
        visited = {start_reference}
        queue = deque([(start_reference, 0, [])])

        while queue:
            current, depth, path = queue.popleft()
            if depth > 0:  # Don't include start node
                nodes.append(
                    TraversalNode(
                        reference=current,
                        element_type=self.graph[current].element_type,
                        depth=depth,
                        path_from_start=path + [current],
                    )
                )

            if depth >= max_depth:
                continue

            current_node = self.graph.get(current)
            if not current_node:
                continue

            # Add outgoing edges
            if direction in ("outgoing", "both"):
                for neighbor in current_node.outgoing_edges:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1, path + [current]))

            # Add incoming edges
            if direction in ("incoming", "both"):
                for neighbor in current_node.incoming_edges:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1, path + [current]))

        return nodes


# ============================================================================
# Coverage Analysis Engine
# ============================================================================

class CoverageAnalysisEngine:
    """Engine for analyzing test coverage across elements."""

    def __init__(self):
        """Initialize coverage analysis engine."""
        self.logger = logging.getLogger(f"{__name__}.CoverageAnalysisEngine")
        self._coverage_data: Dict[str, float] = {}
        self._test_mappings: Dict[str, List[str]] = {}

    def register_coverage(
        self,
        element_reference: str,
        coverage_percentage: float,
        test_count: Optional[int] = None
    ) -> None:
        """Register coverage information for an element.

        Args:
            element_reference: Element reference
            coverage_percentage: Coverage percentage (0-100)
            test_count: Number of tests covering this element
        """
        self._coverage_data[element_reference] = coverage_percentage
        if test_count is not None:
            self._test_mappings[element_reference] = [f"test_{i}" for i in range(test_count)]

    def analyze_coverage(
        self,
        elements: List[str],
        risk_threshold: float = 50.0
    ) -> CoverageAnalysis:
        """Analyze coverage across a set of elements.

        Args:
            elements: List of element references to analyze
            risk_threshold: Coverage percentage below which element is considered at-risk

        Returns:
            CoverageAnalysis: Coverage analysis results
        """
        total_elements = len(elements)
        covered_elements = 0
        uncovered_elements = 0
        total_coverage = 0.0
        at_risk = []

        for element in elements:
            coverage = self._coverage_data.get(element, 0.0)
            total_coverage += coverage

            if coverage > 0:
                covered_elements += 1
            else:
                uncovered_elements += 1

            if coverage < risk_threshold:
                at_risk.append(element)

        coverage_percentage = (total_coverage / total_elements * 100) if total_elements > 0 else 0

        return CoverageAnalysis(
            total_elements=total_elements,
            covered_elements=covered_elements,
            uncovered_elements=uncovered_elements,
            coverage_percentage=coverage_percentage,
            at_risk_elements=at_risk,
        )

    def get_coverage_info(self, element_reference: str) -> CoverageInfo:
        """Get coverage information for a single element.

        Args:
            element_reference: Element reference

        Returns:
            CoverageInfo: Coverage information
        """
        coverage = self._coverage_data.get(element_reference, 0.0)
        test_count = len(self._test_mappings.get(element_reference, []))

        return CoverageInfo(
            reference=element_reference,
            has_tests=test_count > 0,
            test_count=test_count if test_count > 0 else None,
            coverage_percentage=coverage if coverage > 0 else None,
        )


# ============================================================================
# Complexity Analysis Engine
# ============================================================================

class ComplexityAnalysisEngine:
    """Engine for analyzing code complexity metrics."""

    def __init__(self):
        """Initialize complexity analysis engine."""
        self.logger = logging.getLogger(f"{__name__}.ComplexityAnalysisEngine")
        self._complexity_scores: Dict[str, float] = {}

    def calculate_complexity(
        self,
        element_reference: str,
        line_count: int,
        branching_factor: int = 1,
        nesting_depth: int = 1
    ) -> float:
        """Calculate complexity score for an element.

        Args:
            element_reference: Element reference
            line_count: Number of lines in element
            branching_factor: Number of branches (if/else, loops, etc.)
            nesting_depth: Maximum nesting depth

        Returns:
            float: Complexity score (0-100)
        """
        # Simple cyclomatic complexity inspired score
        base_score = min(line_count / 10, 30)  # Lines contribute up to 30
        branch_score = branching_factor * 10  # Each branch adds 10
        nesting_score = nesting_depth * 5  # Each nesting level adds 5

        total_score = min(base_score + branch_score + nesting_score, 100)
        self._complexity_scores[element_reference] = total_score
        return total_score

    def get_complexity_score(self, element_reference: str) -> Optional[float]:
        """Get cached complexity score.

        Args:
            element_reference: Element reference

        Returns:
            float: Complexity score or None if not calculated
        """
        return self._complexity_scores.get(element_reference)

    def categorize_complexity(self, score: float) -> str:
        """Categorize complexity score.

        Args:
            score: Complexity score

        Returns:
            str: Complexity category ("low", "medium", "high", "critical")
        """
        if score < 20:
            return "low"
        elif score < 50:
            return "medium"
        elif score < 80:
            return "high"
        else:
            return "critical"


# ============================================================================
# Deep Analysis Coordinator
# ============================================================================

class DeepAnalysisEngine:
    """Coordinator for deep analysis across multiple engines."""

    def __init__(self):
        """Initialize deep analysis engine."""
        self.logger = logging.getLogger(f"{__name__}.DeepAnalysisEngine")
        self.graph_engine = DependencyGraphEngine()
        self.coverage_engine = CoverageAnalysisEngine()
        self.complexity_engine = ComplexityAnalysisEngine()

    async def perform_deep_analysis(
        self,
        element_reference: str,
        analysis_depth: int = 3
    ) -> Dict[str, Any]:
        """Perform comprehensive deep analysis.

        Args:
            element_reference: Element to analyze
            analysis_depth: Depth of analysis

        Returns:
            dict: Comprehensive analysis results
        """
        start_time = time.time()

        # Find dependents (things that break if this changes)
        dependents = self.graph_engine.find_all_dependents(
            element_reference,
            max_depth=analysis_depth
        )

        # Find dependencies (things this depends on)
        dependencies = self.graph_engine.find_all_dependencies(
            element_reference,
            max_depth=analysis_depth
        )

        # Detect cycles
        cycles = self.graph_engine.find_cycles(element_reference)

        # Build impact summary
        impact_by_depth = {}
        for ref, depth in dependents:
            if depth not in impact_by_depth:
                impact_by_depth[depth] = []
            impact_by_depth[depth].append(ref)

        execution_time_ms = (time.time() - start_time) * 1000

        return {
            "element": element_reference,
            "analysis_depth": analysis_depth,
            "dependents": {
                "total": len(dependents),
                "by_depth": {str(d): len(refs) for d, refs in impact_by_depth.items()},
            },
            "dependencies": {
                "total": len(dependencies),
            },
            "cycles_detected": len(cycles),
            "cycles": [c.path for c in cycles] if cycles else [],
            "execution_time_ms": execution_time_ms,
        }

    async def analyze_coverage_gaps(
        self,
        elements: List[str],
        risk_threshold: float = 50.0
    ) -> Dict[str, Any]:
        """Analyze coverage gaps in a set of elements.

        Args:
            elements: Elements to analyze
            risk_threshold: Coverage threshold for risk detection

        Returns:
            dict: Coverage analysis results
        """
        coverage_analysis = self.coverage_engine.analyze_coverage(
            elements,
            risk_threshold=risk_threshold
        )

        return {
            "total_elements": coverage_analysis.total_elements,
            "covered_elements": coverage_analysis.covered_elements,
            "uncovered_elements": coverage_analysis.uncovered_elements,
            "coverage_percentage": coverage_analysis.coverage_percentage,
            "at_risk_count": len(coverage_analysis.at_risk_elements),
            "at_risk_elements": coverage_analysis.at_risk_elements[:20],  # Top 20
        }
