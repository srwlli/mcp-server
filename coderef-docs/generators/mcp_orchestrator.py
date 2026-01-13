"""
MCP Orchestrator for coderef-context tool calls.

Centralized module for calling coderef-context MCP tools with error handling,
caching, and response validation (WO-GENERATION-ENHANCEMENT-001).

Functions:
    call_coderef_query: Query code relationships (calls, imports, dependencies)
    call_coderef_patterns: Discover code patterns and conventions
    call_coderef_complexity: Get complexity metrics for code elements
    call_coderef_coverage: Analyze test coverage in codebase
    call_coderef_impact: Analyze impact of modifying/deleting elements
    call_coderef_drift: Check if .coderef/ index is stale
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from type_defs import (
    MCPQueryResultDict,
    MCPPatternsResultDict,
    DriftCheckResultDict,
)
from constants import MCP_TIMEOUT_MS, CODEREF_CONTEXT_AVAILABLE

logger = logging.getLogger(__name__)

# ORCH-008: Caching layer
_cache: Dict[str, tuple[Any, datetime]] = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


def _generate_cache_key(tool_name: str, params: Dict[str, Any]) -> str:
    """
    Generate cache key from tool name and parameters.

    Args:
        tool_name: MCP tool name
        params: Tool parameters

    Returns:
        Cache key string
    """
    # Sort params for consistent key generation
    sorted_params = sorted(params.items())
    params_str = ','.join(f'{k}={v}' for k, v in sorted_params)
    return f'{tool_name}:{params_str}'


def _get_cached_result(cache_key: str) -> Optional[Any]:
    """
    Get cached result if available and not expired.

    Args:
        cache_key: Cache key to lookup

    Returns:
        Cached result or None if not found/expired
    """
    if cache_key in _cache:
        result, cached_at = _cache[cache_key]
        age = datetime.now() - cached_at
        if age < timedelta(seconds=_CACHE_TTL_SECONDS):
            logger.debug(f'Cache hit for {cache_key} (age: {age.total_seconds():.1f}s)')
            return result
        else:
            logger.debug(f'Cache expired for {cache_key} (age: {age.total_seconds():.1f}s)')
            del _cache[cache_key]
    return None


def _set_cached_result(cache_key: str, result: Any) -> None:
    """
    Store result in cache with current timestamp.

    Args:
        cache_key: Cache key
        result: Result to cache
    """
    _cache[cache_key] = (result, datetime.now())
    logger.debug(f'Cached result for {cache_key}')


def _clear_cache() -> None:
    """Clear all cached results."""
    _cache.clear()
    logger.debug('Cache cleared')


def _handle_mcp_error(
    tool_name: str,
    error: Exception,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    ORCH-007: Error handling wrapper for MCP tool calls.

    Standardizes error responses and logging across all MCP orchestration functions.

    Args:
        tool_name: Name of MCP tool that failed
        error: Exception that was raised
        context: Additional context (params, project_path, etc)

    Returns:
        Standardized error response dictionary
    """
    error_msg = str(error)
    logger.error(
        f'MCP tool {tool_name} failed: {error_msg}',
        extra={'context': context},
        exc_info=True
    )

    return {
        'success': False,
        'error': f'{tool_name} failed: {error_msg}',
        'tool': tool_name,
        'context': context,
    }


async def call_coderef_query(
    project_path: Path,
    query_type: str,
    target: str,
    max_depth: int = 3,
) -> MCPQueryResultDict:
    """
    ORCH-001: Query code relationships via coderef-context MCP tool.

    Calls coderef_query to discover relationships like:
    - calls: What does this element call?
    - calls-me: What calls this element?
    - imports: What does this element import?
    - imports-me: What imports this element?
    - depends-on: What does this element depend on?
    - depends-on-me: What depends on this element?

    Args:
        project_path: Absolute path to project root
        query_type: Type of relationship query
        target: Element to query (e.g., 'authenticateUser' or 'AuthService#login')
        max_depth: Maximum traversal depth (default: 3)

    Returns:
        MCPQueryResultDict with relationships found or error info
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        logger.warning('coderef-context MCP not available, skipping query')
        return {
            'query_type': query_type,
            'target': target,
            'relationships': [],
            'depth': max_depth,
            'element_count': 0,
            'success': False,
            'error': 'coderef-context MCP server not available',
        }

    cache_key = _generate_cache_key('coderef_query', {
        'project_path': str(project_path),
        'query_type': query_type,
        'target': target,
        'max_depth': max_depth,
    })

    cached = _get_cached_result(cache_key)
    if cached is not None:
        return cached

    try:
        logger.info(f'Calling coderef_query: {query_type} for {target} (depth={max_depth})')

        # TODO: Implement actual MCP call when MCP client is ready
        # For now, return placeholder response
        result: MCPQueryResultDict = {
            'query_type': query_type,
            'target': target,
            'relationships': [],
            'depth': max_depth,
            'element_count': 0,
            'success': False,
            'error': 'MCP client not implemented yet',
        }

        _set_cached_result(cache_key, result)
        return result

    except Exception as e:
        error_response = _handle_mcp_error('coderef_query', e, {
            'project_path': str(project_path),
            'query_type': query_type,
            'target': target,
            'max_depth': max_depth,
        })
        return {
            'query_type': query_type,
            'target': target,
            'relationships': [],
            'depth': max_depth,
            'element_count': 0,
            'success': False,
            'error': error_response['error'],
        }


async def call_coderef_patterns(
    project_path: Path,
    pattern_type: Optional[str] = None,
    limit: int = 10,
) -> MCPPatternsResultDict:
    """
    ORCH-002: Discover code patterns via coderef-context MCP tool.

    Calls coderef_patterns to discover:
    - Coding conventions and patterns
    - Pattern frequency across codebase
    - Pattern locations
    - Consistency violations

    Args:
        project_path: Absolute path to project root
        pattern_type: Optional pattern type filter
        limit: Maximum results (default: 10)

    Returns:
        MCPPatternsResultDict with patterns found or error info
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        logger.warning('coderef-context MCP not available, skipping patterns')
        return {
            'pattern_type': pattern_type,
            'patterns': [],
            'frequency': {},
            'locations': {},
            'violations': [],
            'pattern_count': 0,
            'success': False,
            'error': 'coderef-context MCP server not available',
        }

    cache_key = _generate_cache_key('coderef_patterns', {
        'project_path': str(project_path),
        'pattern_type': pattern_type or 'all',
        'limit': limit,
    })

    cached = _get_cached_result(cache_key)
    if cached is not None:
        return cached

    try:
        logger.info(f'Calling coderef_patterns: type={pattern_type}, limit={limit}')

        # TODO: Implement actual MCP call when MCP client is ready
        result: MCPPatternsResultDict = {
            'pattern_type': pattern_type,
            'patterns': [],
            'frequency': {},
            'locations': {},
            'violations': [],
            'pattern_count': 0,
            'success': False,
            'error': 'MCP client not implemented yet',
        }

        _set_cached_result(cache_key, result)
        return result

    except Exception as e:
        error_response = _handle_mcp_error('coderef_patterns', e, {
            'project_path': str(project_path),
            'pattern_type': pattern_type,
            'limit': limit,
        })
        return {
            'pattern_type': pattern_type,
            'patterns': [],
            'frequency': {},
            'locations': {},
            'violations': [],
            'pattern_count': 0,
            'success': False,
            'error': error_response['error'],
        }


async def call_coderef_complexity(
    project_path: Path,
    element: str,
) -> Dict[str, Any]:
    """
    ORCH-003: Get complexity metrics via coderef-context MCP tool.

    Calls coderef_complexity to analyze:
    - Cyclomatic complexity
    - Lines of code (LOC)
    - Number of dependencies
    - Maintainability index

    Args:
        project_path: Absolute path to project root
        element: Element to analyze

    Returns:
        Dictionary with complexity metrics or error info
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        logger.warning('coderef-context MCP not available, skipping complexity')
        return {
            'element': element,
            'complexity': {},
            'success': False,
            'error': 'coderef-context MCP server not available',
        }

    cache_key = _generate_cache_key('coderef_complexity', {
        'project_path': str(project_path),
        'element': element,
    })

    cached = _get_cached_result(cache_key)
    if cached is not None:
        return cached

    try:
        logger.info(f'Calling coderef_complexity for {element}')

        # TODO: Implement actual MCP call when MCP client is ready
        result = {
            'element': element,
            'complexity': {},
            'success': False,
            'error': 'MCP client not implemented yet',
        }

        _set_cached_result(cache_key, result)
        return result

    except Exception as e:
        return _handle_mcp_error('coderef_complexity', e, {
            'project_path': str(project_path),
            'element': element,
        })


async def call_coderef_coverage(
    project_path: Path,
    format: str = 'summary',
) -> Dict[str, Any]:
    """
    ORCH-004: Analyze test coverage via coderef-context MCP tool.

    Calls coderef_coverage to discover:
    - Overall coverage percentage
    - Uncovered files/functions
    - Coverage by module

    Args:
        project_path: Absolute path to project root
        format: Coverage format ('summary' or 'detailed')

    Returns:
        Dictionary with coverage data or error info
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        logger.warning('coderef-context MCP not available, skipping coverage')
        return {
            'coverage_percent': 0,
            'format': format,
            'success': False,
            'error': 'coderef-context MCP server not available',
        }

    cache_key = _generate_cache_key('coderef_coverage', {
        'project_path': str(project_path),
        'format': format,
    })

    cached = _get_cached_result(cache_key)
    if cached is not None:
        return cached

    try:
        logger.info(f'Calling coderef_coverage (format={format})')

        # TODO: Implement actual MCP call when MCP client is ready
        result = {
            'coverage_percent': 0,
            'format': format,
            'success': False,
            'error': 'MCP client not implemented yet',
        }

        _set_cached_result(cache_key, result)
        return result

    except Exception as e:
        return _handle_mcp_error('coderef_coverage', e, {
            'project_path': str(project_path),
            'format': format,
        })


async def call_coderef_impact(
    project_path: Path,
    element: str,
    operation: str = 'modify',
    max_depth: int = 3,
) -> Dict[str, Any]:
    """
    ORCH-005: Analyze impact via coderef-context MCP tool.

    Calls coderef_impact to discover:
    - What breaks if element is modified/deleted
    - Ripple effects across codebase
    - Affected files and elements

    Args:
        project_path: Absolute path to project root
        element: Element to analyze
        operation: Type of change ('modify', 'delete', 'refactor')
        max_depth: Maximum traversal depth (default: 3)

    Returns:
        Dictionary with impact analysis or error info
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        logger.warning('coderef-context MCP not available, skipping impact')
        return {
            'element': element,
            'operation': operation,
            'affected_elements': [],
            'success': False,
            'error': 'coderef-context MCP server not available',
        }

    cache_key = _generate_cache_key('coderef_impact', {
        'project_path': str(project_path),
        'element': element,
        'operation': operation,
        'max_depth': max_depth,
    })

    cached = _get_cached_result(cache_key)
    if cached is not None:
        return cached

    try:
        logger.info(f'Calling coderef_impact: {operation} {element} (depth={max_depth})')

        # TODO: Implement actual MCP call when MCP client is ready
        result = {
            'element': element,
            'operation': operation,
            'affected_elements': [],
            'success': False,
            'error': 'MCP client not implemented yet',
        }

        _set_cached_result(cache_key, result)
        return result

    except Exception as e:
        return _handle_mcp_error('coderef_impact', e, {
            'project_path': str(project_path),
            'element': element,
            'operation': operation,
            'max_depth': max_depth,
        })


async def call_coderef_drift(
    project_path: Path,
    index_path: Optional[Path] = None,
) -> DriftCheckResultDict:
    """
    ORCH-006: Check .coderef/ index drift via coderef-context MCP tool.

    Calls coderef_drift to determine if .coderef/index.json is stale compared
    to current codebase. Returns drift percentage and recommendation.

    Args:
        project_path: Absolute path to project root
        index_path: Optional path to index.json (default: .coderef/index.json)

    Returns:
        DriftCheckResultDict with drift analysis or error info
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        logger.warning('coderef-context MCP not available, skipping drift check')
        return {
            'drift_percent': 0.0,
            'stale': False,
            'index_age': 'unknown',
            'index_modified': datetime.now().isoformat(),
            'recommendation': 'ok',
            'files_changed': 0,
            'files_added': 0,
            'files_deleted': 0,
            'success': False,
            'error': 'coderef-context MCP server not available',
        }

    # Don't cache drift checks - they should be fresh
    try:
        logger.info(f'Calling coderef_drift for {project_path}')

        # TODO: Implement actual MCP call when MCP client is ready
        result: DriftCheckResultDict = {
            'drift_percent': 0.0,
            'stale': False,
            'index_age': 'unknown',
            'index_modified': datetime.now().isoformat(),
            'recommendation': 'ok',
            'files_changed': 0,
            'files_added': 0,
            'files_deleted': 0,
            'success': False,
            'error': 'MCP client not implemented yet',
        }

        return result

    except Exception as e:
        error_response = _handle_mcp_error('coderef_drift', e, {
            'project_path': str(project_path),
            'index_path': str(index_path) if index_path else None,
        })
        return {
            'drift_percent': 0.0,
            'stale': False,
            'index_age': 'unknown',
            'index_modified': datetime.now().isoformat(),
            'recommendation': 'ok',
            'files_changed': 0,
            'files_added': 0,
            'files_deleted': 0,
            'success': False,
            'error': error_response['error'],
        }
