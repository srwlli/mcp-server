"""Query generator for CodeRef2 element discovery and analysis.

This module implements the core query functionality for finding and retrieving
CodeRef2 elements from the knowledge base.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from coderef.models import (
    CodeRef2Element,
    ElementMetadata,
    QueryFilter,
    QueryRequest,
    QueryResponse,
    TypeDesignator,
    RelationshipType,
    Relationship,
    TraversalRequest,
    TraversalResponse,
    TraversalNode,
    ImpactAnalysis,
    ImpactNode,
    ImpactLevel,
)
from coderef.clients.docs_client import get_docs_client

logger = logging.getLogger(__name__)


# ============================================================================
# Query Grammar Parser
# ============================================================================

class ReferenceParser:
    """Parser for CodeRef2 reference syntax.

    Syntax: @Type/path#element:line{metadata}
    Example: @Fn/src/utils#calculate_total:42{complexity:high}
    """

    REFERENCE_PATTERN = re.compile(
        r"@(?P<type>\w+)/(?P<path>[^#:{}]+)(?:#(?P<element>[^:{}]+))?(?::(?P<line>\d+))?(?:\{(?P<metadata>[^}]*)\})?"
    )

    @classmethod
    def parse(cls, reference: str) -> Optional[Dict[str, Any]]:
        """Parse a CodeRef2 reference string.

        Args:
            reference: CodeRef2 reference string

        Returns:
            dict: Parsed components or None if invalid
        """
        match = cls.REFERENCE_PATTERN.match(reference)
        if not match:
            logger.warning(f"Invalid reference format: {reference}")
            return None

        groups = match.groupdict()
        parsed = {
            "type": groups["type"],
            "path": groups["path"],
            "element": groups["element"],
            "line": int(groups["line"]) if groups["line"] else None,
            "metadata": cls._parse_metadata(groups["metadata"]),
        }
        return parsed

    @classmethod
    def _parse_metadata(cls, metadata_str: Optional[str]) -> Dict[str, str]:
        """Parse metadata portion of reference.

        Args:
            metadata_str: Metadata string (e.g., "complexity:high,status:active")

        Returns:
            dict: Parsed metadata key-value pairs
        """
        if not metadata_str:
            return {}

        metadata = {}
        for item in metadata_str.split(","):
            if ":" in item:
                key, value = item.split(":", 1)
                metadata[key.strip()] = value.strip()
        return metadata

    @classmethod
    def to_reference(cls, element: CodeRef2Element) -> str:
        """Convert element to CodeRef2 reference string.

        Args:
            element: CodeRef2Element

        Returns:
            str: Reference string
        """
        ref = f"@{element.type_designator.value}/{element.path}"
        if element.element:
            ref += f"#{element.element}"
        if element.line:
            ref += f":{element.line}"
        return ref


# ============================================================================
# Query Engine
# ============================================================================

@dataclass
class QueryStats:
    """Statistics about a query execution."""
    total_scanned: int = 0
    total_matched: int = 0
    filters_applied: int = 0
    execution_time_ms: float = 0.0


class QueryEngine:
    """Main query engine for CodeRef2 elements."""

    def __init__(self):
        """Initialize query engine."""
        self.logger = logging.getLogger(f"{__name__}.QueryEngine")
        self.docs_client = get_docs_client()
        self._element_cache: Dict[str, CodeRef2Element] = {}
        self._relationship_cache: Dict[str, List[Relationship]] = {}

    def load_elements(self, elements: List[Dict[str, Any]]) -> int:
        """Load elements from scan results into cache.

        Args:
            elements: List of element dicts from CLI scan

        Returns:
            Number of elements loaded
        """
        self._element_cache.clear()
        for elem in elements:
            ref = self._build_reference(elem)
            self._element_cache[ref] = self._convert_element(elem)
        self.logger.info(f"Loaded {len(self._element_cache)} elements into cache")
        return len(self._element_cache)

    def _convert_element(self, elem: Dict[str, Any]) -> CodeRef2Element:
        """Convert CLI element dict to CodeRef2Element."""
        type_str = elem.get("type", "function")

        # Map CLI type strings to TypeDesignator enum
        type_mapping = {
            "function": TypeDesignator.FUNCTION,
            "method": TypeDesignator.METHOD,
            "class": TypeDesignator.CLASS,
            "variable": TypeDesignator.VARIABLE,
            "constant": TypeDesignator.CONSTANT,
            "interface": TypeDesignator.INTERFACE,
            "type": TypeDesignator.TYPE_DEFINITION,
            "enum": TypeDesignator.ENUM,
            "module": TypeDesignator.MODULE,
            "file": TypeDesignator.FILE,
            "decorator": TypeDesignator.DECORATOR,
            "property": TypeDesignator.PROPERTY,
        }
        type_des = type_mapping.get(type_str, TypeDesignator.FUNCTION)

        return CodeRef2Element(
            reference=self._build_reference(elem),
            type_designator=type_des,
            path=elem.get("file", ""),
            element=elem.get("name", ""),
            line=elem.get("line", 0),
            metadata=ElementMetadata(
                status="active",
                documentation=elem.get("documentation", ""),
            ),
        )

    def _build_reference(self, elem: Dict[str, Any]) -> str:
        """Build CodeRef2 reference string from element."""
        type_abbrev = {
            "function": "fn",
            "method": "mt",
            "class": "cl",
            "variable": "var",
            "constant": "const",
            "interface": "if",
            "type": "ty",
            "enum": "en",
            "module": "mod",
            "file": "file",
        }
        t = type_abbrev.get(elem.get("type", "function"), "fn")
        return f"@{t}/{elem.get('file', '')}#{elem.get('name', '')}:{elem.get('line', 0)}"

    def _matches_pattern(self, elem: CodeRef2Element, pattern: str) -> bool:
        """Check if element matches search pattern."""
        pattern_lower = pattern.lower()
        return (
            pattern_lower in elem.element.lower() or
            pattern_lower in elem.path.lower() or
            pattern_lower in elem.reference.lower()
        )

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the element cache."""
        type_counts: Dict[str, int] = {}
        for elem in self._element_cache.values():
            t = elem.type_designator.value
            type_counts[t] = type_counts.get(t, 0) + 1
        return {
            "total_elements": len(self._element_cache),
            "by_type": type_counts,
        }

    async def query(
        self,
        query_request: QueryRequest
    ) -> QueryResponse:
        """Execute a query for CodeRef2 elements.

        Args:
            query_request: Query specification

        Returns:
            QueryResponse: Results and metadata
        """
        start_time = time.time()
        self.logger.debug(f"Executing query: {query_request.query}")

        try:
            # Parse and validate query
            parsed = ReferenceParser.parse(query_request.query)
            if parsed:
                elements = await self._query_by_reference(parsed, query_request.filter)
            else:
                elements = await self._query_by_pattern(query_request.query, query_request.filter)

            # Apply limit
            elements = elements[: query_request.limit]

            execution_time_ms = (time.time() - start_time) * 1000

            return QueryResponse(
                query=query_request.query,
                elements=elements,
                total_count=len(elements),
                execution_time_ms=execution_time_ms,
                query_status="success",
            )

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            execution_time_ms = (time.time() - start_time) * 1000
            return QueryResponse(
                query=query_request.query,
                elements=[],
                total_count=0,
                execution_time_ms=execution_time_ms,
                query_status="error",
                error_message=str(e),
            )

    async def _query_by_reference(
        self,
        parsed: Dict[str, Any],
        filter: Optional[QueryFilter] = None
    ) -> List[CodeRef2Element]:
        """Query by specific CodeRef2 reference.

        Args:
            parsed: Parsed reference components
            filter: Optional filter criteria

        Returns:
            list: Matching elements
        """
        self.logger.debug(f"Querying by reference: {parsed}")

        # In production: would look up from knowledge base/database
        # For now: generate a synthetic element for demonstration
        type_des = TypeDesignator(parsed["type"])
        element = CodeRef2Element(
            reference=ReferenceParser.to_reference(
                CodeRef2Element(
                    reference="",
                    type_designator=type_des,
                    path=parsed["path"],
                    element=parsed["element"],
                    line=parsed["line"],
                )
            ),
            type_designator=type_des,
            path=parsed["path"],
            element=parsed["element"],
            line=parsed["line"],
            metadata=ElementMetadata(
                status="active",
                documentation="Query result element"
            ),
        )

        elements = [element]

        # Apply filters
        if filter:
            elements = self._apply_filters(elements, filter)

        return elements

    async def _query_by_pattern(
        self,
        pattern: str,
        filter: Optional[QueryFilter] = None
    ) -> List[CodeRef2Element]:
        """Query by pattern matching against cached elements.

        Args:
            pattern: Search pattern (supports wildcards)
            filter: Optional filter criteria

        Returns:
            list: Matching elements from cache
        """
        self.logger.debug(f"Querying by pattern: {pattern} (cache size: {len(self._element_cache)})")

        elements = []

        # Search the actual cache
        if self._element_cache:
            for ref, elem in self._element_cache.items():
                if self._matches_pattern(elem, pattern):
                    elements.append(elem)
            self.logger.debug(f"Found {len(elements)} matches for pattern '{pattern}'")
        else:
            self.logger.warning("Element cache is empty - run scan_realtime first")

        # Apply filters
        if filter:
            elements = self._apply_filters(elements, filter)

        return elements

    def _apply_filters(
        self,
        elements: List[CodeRef2Element],
        filter: QueryFilter
    ) -> List[CodeRef2Element]:
        """Apply filter criteria to elements.

        Args:
            elements: Elements to filter
            filter: Filter criteria

        Returns:
            list: Filtered elements
        """
        filtered = elements

        # Filter by type designators
        if filter.type_designators:
            allowed_types = set(t.value for t in filter.type_designators)
            filtered = [
                e for e in filtered
                if e.type_designator.value in allowed_types
            ]

        # Filter by path pattern
        if filter.path_pattern:
            import fnmatch
            filtered = [
                e for e in filtered
                if fnmatch.fnmatch(e.path, filter.path_pattern)
            ]

        # Filter by metadata
        if filter.metadata_filters:
            for key, value in filter.metadata_filters.items():
                meta_dict = e.metadata.to_dict()
                filtered = [
                    e for e in filtered
                    if meta_dict.get(key) == value
                ]

        # Filter by line range
        if filter.min_line is not None:
            filtered = [e for e in filtered if e.line is None or e.line >= filter.min_line]
        if filter.max_line is not None:
            filtered = [e for e in filtered if e.line is None or e.line <= filter.max_line]

        # Filter by test coverage
        if filter.has_test_coverage is not None:
            filtered = [
                e for e in filtered
                if (e.test_coverage is not None and e.test_coverage > 0) == filter.has_test_coverage
            ]

        return filtered

    async def analyze_impact(
        self,
        source_reference: str,
        depth: int = 3,
        include_test_impact: bool = True
    ) -> ImpactAnalysis:
        """Analyze impact of changes to an element.

        Args:
            source_reference: Reference to element
            depth: Maximum depth to traverse
            include_test_impact: Whether to include test-related impacts

        Returns:
            ImpactAnalysis: Impact analysis results
        """
        self.logger.debug(f"Analyzing impact for: {source_reference}")

        # Parse reference
        parsed = ReferenceParser.parse(source_reference)
        if not parsed:
            self.logger.error(f"Invalid source reference: {source_reference}")
            return ImpactAnalysis(
                source_reference=source_reference,
                affected_elements=[],
                impact_summary={},
                total_affected=0,
            )

        # Perform traversal to find affected elements
        affected = await self._find_affected_elements(source_reference, depth)

        # Analyze impact levels
        impact_nodes = []
        for ref, traversal_depth in affected:
            impact_level = self._calculate_impact_level(traversal_depth, depth)
            node = ImpactNode(
                reference=ref,
                element_type=TypeDesignator.FUNCTION,  # Would be actual type
                impact_level=impact_level,
                depth=traversal_depth,
                reason=f"Affected at depth {traversal_depth}",
            )
            impact_nodes.append(node)

        # Generate summary
        impact_summary = {
            "total_affected": len(impact_nodes),
            "by_level": self._count_by_impact_level(impact_nodes),
            "max_depth": max((n.depth for n in impact_nodes), default=0),
        }

        return ImpactAnalysis(
            source_reference=source_reference,
            affected_elements=impact_nodes,
            impact_summary=impact_summary,
            total_affected=len(impact_nodes),
        )

    async def _find_affected_elements(
        self,
        source_reference: str,
        max_depth: int
    ) -> List[Tuple[str, int]]:
        """Find all elements affected by changes to source.

        Args:
            source_reference: Source reference
            max_depth: Maximum traversal depth

        Returns:
            list: Tuples of (reference, depth)
        """
        affected = []
        visited = {source_reference}
        queue = [(source_reference, 0)]

        while queue and len(visited) < 100:  # Safety limit
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            # In production: would query relationship graph
            # For now: generate sample dependent elements
            dependents = [
                f"@Fn/dependent/module#func_{i}:0"
                for i in range(min(2, max_depth - depth))
            ]

            for dependent in dependents:
                if dependent not in visited:
                    visited.add(dependent)
                    affected.append((dependent, depth + 1))
                    queue.append((dependent, depth + 1))

        return affected

    def _calculate_impact_level(self, depth: int, max_depth: int) -> ImpactLevel:
        """Calculate impact level based on depth.

        Args:
            depth: Current depth
            max_depth: Maximum depth

        Returns:
            ImpactLevel: Calculated impact level
        """
        if depth == 0:
            return ImpactLevel.CRITICAL
        elif depth == 1:
            return ImpactLevel.HIGH
        elif depth == 2:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW

    def _count_by_impact_level(self, nodes: List[ImpactNode]) -> Dict[str, int]:
        """Count nodes by impact level.

        Args:
            nodes: Impact nodes

        Returns:
            dict: Count by impact level
        """
        counts = {level.value: 0 for level in ImpactLevel}
        for node in nodes:
            counts[node.impact_level.value] += 1
        return counts


# ============================================================================
# Query Executor (High-level API)
# ============================================================================

class QueryExecutor:
    """High-level query execution API."""

    def __init__(self):
        """Initialize query executor."""
        self.engine = QueryEngine()
        self.logger = logging.getLogger(f"{__name__}.QueryExecutor")

    async def execute_query(self, request: QueryRequest) -> QueryResponse:
        """Execute a query request.

        Args:
            request: Query request

        Returns:
            QueryResponse: Query results

        Raises:
            ValueError: If query is invalid
        """
        if not request.query:
            raise ValueError("Query cannot be empty")

        self.logger.debug(f"Executing query: {request.query}")
        return await self.engine.query(request)

    async def execute_analysis(
        self,
        reference: str,
        depth: int = 3
    ) -> ImpactAnalysis:
        """Execute impact analysis.

        Args:
            reference: Element reference
            depth: Analysis depth

        Returns:
            ImpactAnalysis: Analysis results
        """
        if not reference:
            raise ValueError("Reference cannot be empty")

        self.logger.debug(f"Executing analysis: {reference}")
        return await self.engine.analyze_impact(reference, depth)
