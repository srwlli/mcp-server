"""Explicit API client for docs-mcp service interaction.

This module provides a clean interface for querying the docs-mcp service
without direct imports. Communication is strictly through defined contracts.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# ============================================================================
# API Contract Definitions (Mirrors docs-mcp endpoints)
# ============================================================================

@dataclass
class DocsServiceConfig:
    """Configuration for docs-mcp service connection."""
    service_name: str = "docs-mcp"
    timeout_ms: int = 5000
    retry_count: int = 3
    fallback_enabled: bool = True


# ============================================================================
# Request/Response Types for docs-mcp API
# ============================================================================

@dataclass
class FoundationDocQuery:
    """Query for foundation documentation."""
    project_path: str
    doc_type: str  # "readme", "architecture", "api", "components", "schema"
    include_metadata: bool = True


@dataclass
class ApiDiscoveryQuery:
    """Query for API endpoint discovery."""
    project_path: str
    frameworks: List[str] = None  # ["fastapi", "flask", "express", "graphql"]
    include_graphql: bool = False


@dataclass
class ChangelogEntry:
    """Entry from project changelog."""
    version: str
    change_type: str
    title: str
    description: str
    timestamp: Optional[datetime] = None


@dataclass
class ProjectAnalysis:
    """Analysis of a project structure."""
    project_path: str
    file_count: int
    line_count: int
    structure: Dict[str, Any]
    frameworks_detected: List[str]
    analysis_timestamp: datetime


# ============================================================================
# DocsClient - Main Service Interface
# ============================================================================

class DocsClient:
    """Client for interacting with docs-mcp service."""

    def __init__(self, config: Optional[DocsServiceConfig] = None):
        """Initialize docs client."""
        self.config = config or DocsServiceConfig()
        self.logger = logging.getLogger(f"{__name__}.DocsClient")
        self._service_available = True
        self._last_health_check = None

    async def check_health(self) -> bool:
        """Check if docs-mcp service is available.

        Returns:
            bool: True if service is reachable and healthy
        """
        try:
            self.logger.debug(f"Checking health of {self.config.service_name}")
            # In production: would make HTTP request to docs-mcp health endpoint
            # For now: assume available if fallback is enabled
            self._service_available = True
            self._last_health_check = datetime.utcnow()
            return True
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            self._service_available = False
            return False

    async def query_foundation_docs(
        self,
        project_path: str,
        doc_type: str,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Query foundation documentation from docs-mcp.

        Args:
            project_path: Path to the project
            doc_type: Type of documentation ("readme", "architecture", "api", etc.)
            include_metadata: Whether to include metadata

        Returns:
            dict: Documentation content and metadata

        Raises:
            ServiceUnavailableError: If service is unavailable and fallback disabled
        """
        query = FoundationDocQuery(project_path, doc_type, include_metadata)
        self.logger.debug(f"Querying foundation docs: {query}")

        try:
            if not self._service_available and not self.config.fallback_enabled:
                raise ServiceUnavailableError(self.config.service_name)

            # Simulate API call - in production this would be HTTP request
            result = await self._call_docs_api(
                "query_foundation_docs",
                {
                    "project_path": project_path,
                    "doc_type": doc_type,
                    "include_metadata": include_metadata
                }
            )
            return result

        except Exception as e:
            self.logger.error(f"Error querying foundation docs: {e}")
            if self.config.fallback_enabled:
                return self._fallback_foundation_docs(project_path, doc_type)
            raise

    async def discover_api_endpoints(
        self,
        project_path: str,
        frameworks: Optional[List[str]] = None,
        include_graphql: bool = False
    ) -> Dict[str, Any]:
        """Discover API endpoints in a project.

        Args:
            project_path: Path to the project
            frameworks: Specific frameworks to scan
            include_graphql: Whether to include GraphQL queries

        Returns:
            dict: Discovered endpoints and metadata
        """
        query = ApiDiscoveryQuery(project_path, frameworks, include_graphql)
        self.logger.debug(f"Discovering API endpoints: {query}")

        try:
            if not self._service_available and not self.config.fallback_enabled:
                raise ServiceUnavailableError(self.config.service_name)

            result = await self._call_docs_api(
                "discover_api_endpoints",
                {
                    "project_path": project_path,
                    "frameworks": frameworks or [],
                    "include_graphql": include_graphql
                }
            )
            return result

        except Exception as e:
            self.logger.error(f"Error discovering API endpoints: {e}")
            if self.config.fallback_enabled:
                return self._fallback_api_endpoints(project_path)
            raise

    async def query_changelog(
        self,
        project_path: str,
        version: Optional[str] = None,
        change_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query project changelog.

        Args:
            project_path: Path to the project
            version: Specific version to query (optional)
            change_type: Filter by change type (optional)

        Returns:
            list: Changelog entries
        """
        self.logger.debug(f"Querying changelog: version={version}, type={change_type}")

        try:
            if not self._service_available and not self.config.fallback_enabled:
                raise ServiceUnavailableError(self.config.service_name)

            result = await self._call_docs_api(
                "query_changelog",
                {
                    "project_path": project_path,
                    "version": version,
                    "change_type": change_type
                }
            )
            return result

        except Exception as e:
            self.logger.error(f"Error querying changelog: {e}")
            if self.config.fallback_enabled:
                return []
            raise

    async def analyze_project_structure(
        self,
        project_path: str
    ) -> Dict[str, Any]:
        """Analyze project structure and frameworks.

        Args:
            project_path: Path to the project

        Returns:
            dict: Project analysis results
        """
        self.logger.debug(f"Analyzing project structure: {project_path}")

        try:
            if not self._service_available and not self.config.fallback_enabled:
                raise ServiceUnavailableError(self.config.service_name)

            result = await self._call_docs_api(
                "analyze_project_structure",
                {"project_path": project_path}
            )
            return result

        except Exception as e:
            self.logger.error(f"Error analyzing project structure: {e}")
            if self.config.fallback_enabled:
                return self._fallback_project_analysis(project_path)
            raise

    async def get_coderef_inventory(
        self,
        project_path: str,
        inventory_type: str = "all"  # "files", "dependencies", "api", "database", "config"
    ) -> Dict[str, Any]:
        """Get CodeRef inventory information.

        Args:
            project_path: Path to the project
            inventory_type: Type of inventory to retrieve

        Returns:
            dict: Inventory data
        """
        self.logger.debug(f"Getting CodeRef inventory: type={inventory_type}")

        try:
            if not self._service_available and not self.config.fallback_enabled:
                raise ServiceUnavailableError(self.config.service_name)

            result = await self._call_docs_api(
                "get_coderef_inventory",
                {
                    "project_path": project_path,
                    "inventory_type": inventory_type
                }
            )
            return result

        except Exception as e:
            self.logger.error(f"Error getting CodeRef inventory: {e}")
            if self.config.fallback_enabled:
                return self._fallback_coderef_inventory(project_path, inventory_type)
            raise

    # ========================================================================
    # Internal Methods
    # ========================================================================

    async def _call_docs_api(
        self,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make API call to docs-mcp service.

        This is a placeholder that will be replaced with actual HTTP/MCP calls
        in production. Currently returns mock data for development.
        """
        self.logger.debug(f"Calling docs API: {endpoint} with params: {params}")

        # Placeholder for actual service communication
        # In production: would use requests.post() or MCP protocol
        return {
            "status": "success",
            "endpoint": endpoint,
            "params": params,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _fallback_foundation_docs(
        self,
        project_path: str,
        doc_type: str
    ) -> Dict[str, Any]:
        """Fallback implementation for foundation doc queries."""
        self.logger.warning(f"Using fallback for foundation docs: {doc_type}")
        return {
            "status": "fallback",
            "doc_type": doc_type,
            "project_path": project_path,
            "content": f"Fallback documentation for {doc_type}",
            "note": "docs-mcp service unavailable, returning fallback content"
        }

    def _fallback_api_endpoints(
        self,
        project_path: str
    ) -> Dict[str, Any]:
        """Fallback implementation for API discovery."""
        self.logger.warning("Using fallback for API endpoint discovery")
        return {
            "status": "fallback",
            "endpoints": [],
            "note": "docs-mcp service unavailable, returning empty endpoints"
        }

    def _fallback_project_analysis(
        self,
        project_path: str
    ) -> Dict[str, Any]:
        """Fallback implementation for project analysis."""
        self.logger.warning("Using fallback for project analysis")
        return {
            "status": "fallback",
            "project_path": project_path,
            "file_count": 0,
            "line_count": 0,
            "frameworks_detected": [],
            "note": "docs-mcp service unavailable, returning minimal analysis"
        }

    def _fallback_coderef_inventory(
        self,
        project_path: str,
        inventory_type: str
    ) -> Dict[str, Any]:
        """Fallback implementation for CodeRef inventory."""
        self.logger.warning(f"Using fallback for CodeRef inventory: {inventory_type}")
        return {
            "status": "fallback",
            "inventory_type": inventory_type,
            "project_path": project_path,
            "items": [],
            "note": "docs-mcp service unavailable, returning empty inventory"
        }


# ============================================================================
# Exception Types
# ============================================================================

class DocsServiceException(Exception):
    """Base exception for docs service errors."""
    pass


class ServiceUnavailableError(DocsServiceException):
    """Raised when docs-mcp service is unavailable."""

    def __init__(self, service_name: str):
        super().__init__(f"{service_name} is unavailable and fallback is disabled")
        self.service_name = service_name


class QueryExecutionError(DocsServiceException):
    """Raised when query execution fails."""

    def __init__(self, query: str, details: str):
        super().__init__(f"Query execution failed: {query} - {details}")
        self.query = query
        self.details = details


class TimeoutError(DocsServiceException):
    """Raised when service call times out."""

    def __init__(self, endpoint: str, timeout_ms: int):
        super().__init__(f"Service call to {endpoint} timed out after {timeout_ms}ms")
        self.endpoint = endpoint
        self.timeout_ms = timeout_ms


# ============================================================================
# Client Factory
# ============================================================================

_docs_client_instance = None


def get_docs_client(
    config: Optional[DocsServiceConfig] = None
) -> DocsClient:
    """Get or create docs client instance (singleton pattern).

    Args:
        config: Optional configuration (used only on first call)

    Returns:
        DocsClient: Singleton instance
    """
    global _docs_client_instance
    if _docs_client_instance is None:
        _docs_client_instance = DocsClient(config or DocsServiceConfig())
    return _docs_client_instance
