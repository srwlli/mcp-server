"""Pydantic models for CodeRef2 elements, queries, and responses."""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Enums for CodeRef2 Type System
# ============================================================================

class TypeDesignator(str, Enum):
    """26 CodeRef2 type designators."""
    FILE = "F"
    DIRECTORY = "D"
    CLASS = "C"
    FUNCTION = "Fn"
    CLOSURE = "Cl"
    METHOD = "M"
    PROPERTY = "P"
    VARIABLE = "V"
    CONSTANT = "K"
    ENUM = "E"
    INTERFACE = "I"
    TRAIT = "Tr"
    MODULE = "Mo"
    PACKAGE = "Pkg"
    NAMESPACE = "N"
    TYPE_DEFINITION = "TD"
    GENERIC = "G"
    DECORATOR = "Dec"
    PARAMETER = "Param"
    FIELD = "Fd"
    ATTRIBUTE = "Attr"
    TEST_CASE = "Test"
    FIXTURE = "Fix"
    MACRO = "Macro"
    ANNOTATION = "Ann"
    CUSTOM = "Custom"


class MetadataCategory(str, Enum):
    """8 metadata categories for CodeRef2 elements."""
    STATUS = "status"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLEXITY = "complexity"
    COVERAGE = "coverage"
    MAINTENANCE = "maintenance"
    COMPATIBILITY = "compatibility"
    DOCUMENTATION = "documentation"


class RelationshipType(str, Enum):
    """Relationship types between CodeRef2 elements."""
    IMPORTS = "imports"
    CALLS = "calls"
    DEPENDS_ON = "depends-on"
    TESTS = "tests"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    CONTAINS = "contains"
    REFERENCES = "references"


# ============================================================================
# Metadata Models
# ============================================================================

class MetadataValue(BaseModel):
    """A single metadata value with category and content."""
    category: MetadataCategory
    value: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None


class ElementMetadata(BaseModel):
    """Complete metadata for a CodeRef2 element."""
    status: Optional[str] = None
    security: Optional[str] = None
    performance: Optional[str] = None
    complexity: Optional[str] = None
    coverage: Optional[str] = None
    maintenance: Optional[str] = None
    compatibility: Optional[str] = None
    documentation: Optional[str] = None
    custom: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dictionary of non-None values."""
        return {
            k: v for k, v in self.model_dump().items()
            if v is not None and k != "custom"
        }


# ============================================================================
# Relationship Models
# ============================================================================

class Relationship(BaseModel):
    """A relationship between two CodeRef2 elements."""
    relationship_type: RelationshipType
    source_reference: str  # Full CodeRef2 reference
    target_reference: str  # Full CodeRef2 reference
    line_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# CodeRef2 Element Models
# ============================================================================

class CodeRef2Element(BaseModel):
    """Core CodeRef2 element with complete information."""
    reference: str  # Full @Type/path#element:line{metadata} reference
    type_designator: TypeDesignator
    path: str
    element: Optional[str] = None  # Specific element name
    line: Optional[int] = None
    metadata: ElementMetadata = Field(default_factory=ElementMetadata)

    # Relationships
    incoming_relationships: List[Relationship] = Field(default_factory=list)
    outgoing_relationships: List[Relationship] = Field(default_factory=list)

    # Additional context
    source_code: Optional[str] = None  # Snippet of actual code
    documentation: Optional[str] = None
    test_coverage: Optional[float] = None  # Percentage 0-100
    last_modified: Optional[datetime] = None
    risk_score: Optional[float] = None  # 0-100, higher = riskier

    class Config:
        use_enum_values = False

    @property
    def full_reference(self) -> str:
        """Generate full CodeRef2 reference string."""
        return self.reference


# ============================================================================
# Query Models
# ============================================================================

class QueryFilter(BaseModel):
    """Filter criteria for element queries."""
    type_designators: Optional[List[TypeDesignator]] = None
    path_pattern: Optional[str] = None  # Glob pattern
    metadata_filters: Optional[Dict[str, str]] = None
    relationship_types: Optional[List[RelationshipType]] = None
    min_line: Optional[int] = None
    max_line: Optional[int] = None
    has_test_coverage: Optional[bool] = None


class QueryRequest(BaseModel):
    """Request to query CodeRef2 elements."""
    query: str  # Natural language or reference pattern
    filter: Optional[QueryFilter] = None
    limit: int = Field(default=100, ge=1, le=1000)
    include_relationships: bool = True
    include_metadata: bool = True
    include_source: bool = False


class QueryResponse(BaseModel):
    """Response containing queried CodeRef2 elements."""
    query: str
    elements: List[CodeRef2Element]
    total_count: int
    execution_time_ms: float
    query_status: str = "success"
    error_message: Optional[str] = None


# ============================================================================
# Analysis Models
# ============================================================================

class ImpactLevel(str, Enum):
    """Impact levels for change analysis."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactNode(BaseModel):
    """A single node in impact analysis graph."""
    reference: str
    element_type: TypeDesignator
    impact_level: ImpactLevel
    depth: int  # Distance from source
    reason: Optional[str] = None


class ImpactAnalysis(BaseModel):
    """Complete impact analysis for a change."""
    source_reference: str
    affected_elements: List[ImpactNode]
    impact_summary: Dict[str, Any]  # Statistics and insights
    total_affected: int
    critical_paths: List[List[str]] = Field(default_factory=list)  # Paths of critical dependencies


class AnalysisRequest(BaseModel):
    """Request for deep impact analysis."""
    reference: str
    analysis_type: str = "impact"  # "impact", "coverage", "complexity", etc.
    depth: int = Field(default=3, ge=1, le=10)
    include_test_impact: bool = True
    include_performance_impact: bool = False


class AnalysisResponse(BaseModel):
    """Response containing analysis results."""
    request_reference: str
    analysis_type: str
    results: Dict[str, Any]
    affected_count: int
    execution_time_ms: float
    analysis_status: str = "success"
    error_message: Optional[str] = None


# ============================================================================
# Coverage Detection Models
# ============================================================================

class CoverageInfo(BaseModel):
    """Coverage information for an element."""
    reference: str
    has_tests: bool
    test_count: Optional[int] = None
    coverage_percentage: Optional[float] = None
    uncovered_paths: Optional[List[str]] = None


class CoverageAnalysis(BaseModel):
    """Analysis of test coverage across elements."""
    total_elements: int
    covered_elements: int
    uncovered_elements: int
    coverage_percentage: float
    at_risk_elements: List[str]  # High-risk, low-coverage elements


# ============================================================================
# Graph Traversal Models
# ============================================================================

class TraversalRequest(BaseModel):
    """Request to traverse element relationships."""
    start_reference: str
    relationship_types: Optional[List[RelationshipType]] = None
    direction: str = "both"  # "outgoing", "incoming", "both"
    max_depth: int = Field(default=3, ge=1, le=10)
    include_circular: bool = False


class TraversalNode(BaseModel):
    """Node in traversal result."""
    reference: str
    element_type: TypeDesignator
    depth: int
    path_from_start: List[str]
    relationship_to_parent: Optional[RelationshipType] = None


class TraversalResponse(BaseModel):
    """Response containing traversal results."""
    start_reference: str
    nodes: List[TraversalNode]
    total_nodes: int
    has_circular_dependencies: bool
    execution_time_ms: float


# ============================================================================
# Batch Processing Models
# ============================================================================

class BatchQueryItem(BaseModel):
    """Single item in batch query."""
    id: str
    query: str
    filter: Optional[QueryFilter] = None


class BatchQueryRequest(BaseModel):
    """Request to process multiple queries."""
    queries: List[BatchQueryItem]
    parallel: bool = False
    timeout_ms: int = Field(default=5000, ge=1000)


class BatchQueryResult(BaseModel):
    """Result for single batch query item."""
    item_id: str
    success: bool
    elements: Optional[List[CodeRef2Element]] = None
    error: Optional[str] = None
    execution_time_ms: float


class BatchQueryResponse(BaseModel):
    """Response containing batch query results."""
    total_queries: int
    successful: int
    failed: int
    results: List[BatchQueryResult]
    total_execution_time_ms: float


# ============================================================================
# Error Response Models
# ============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error_code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# ============================================================================
# Service Status Models
# ============================================================================

class ToolStatus(BaseModel):
    """Status of a single MCP tool."""
    tool_name: str
    available: bool
    version: str
    performance_ms: Optional[float] = None


class ServiceStatus(BaseModel):
    """Overall service status."""
    service_name: str = "coderef-mcp"
    version: str
    status: str  # "operational", "degraded", "maintenance"
    tools: List[ToolStatus]
    uptime_seconds: Optional[float] = None
    last_check: datetime = Field(default_factory=datetime.utcnow)
