"""CodeRef MCP Service - Main package."""

from .models import (
    CodeRef2Element,
    QueryRequest,
    QueryResponse,
    AnalysisRequest,
    AnalysisResponse,
    TypeDesignator,
    MetadataCategory,
    RelationshipType,
)
from .generators import QueryExecutor, QueryEngine, ReferenceParser
from .clients import DocsClient, get_docs_client

__version__ = "1.0.0"

__all__ = [
    "CodeRef2Element",
    "QueryRequest",
    "QueryResponse",
    "AnalysisRequest",
    "AnalysisResponse",
    "TypeDesignator",
    "MetadataCategory",
    "RelationshipType",
    "QueryExecutor",
    "QueryEngine",
    "ReferenceParser",
    "DocsClient",
    "get_docs_client",
]
