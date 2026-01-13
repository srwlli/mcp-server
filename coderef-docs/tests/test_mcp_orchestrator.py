"""
TEST-001: MCP Orchestration Tests (WO-GENERATION-ENHANCEMENT-001)

Tests for mcp_orchestrator.py module verifying:
- call_coderef_patterns returns correct data structure
- Caching works properly
- Error handling returns expected error responses
- Graceful degradation when CODEREF_CONTEXT_AVAILABLE is False

Part of Phase 5 testing for WO-GENERATION-ENHANCEMENT-001.
"""

import asyncio
import json
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_orchestrator import (
    call_coderef_patterns,
    _call_mcp_tool,
    _cache,
    CODEREF_CONTEXT_AVAILABLE
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_patterns_response() -> Dict[str, Any]:
    """Sample successful response from coderef_patterns tool."""
    return {
        "patterns": [
            {
                "pattern": "async def.*\\(",
                "type": "async_function",
                "count": 15,
                "locations": ["src/handlers.py:45", "src/generators.py:123"]
            },
            {
                "pattern": "class.*:",
                "type": "class_definition",
                "count": 8,
                "locations": ["src/models.py:10", "src/utils.py:56"]
            },
            {
                "pattern": "def handle_.*\\(",
                "type": "handler_function",
                "count": 12,
                "locations": ["src/tool_handlers.py:100", "src/tool_handlers.py:250"]
            }
        ],
        "frequency": {
            "async_function": 15,
            "class_definition": 8,
            "handler_function": 12
        },
        "violations": [
            {
                "file": "src/deprecated.py",
                "line": 50,
                "pattern": "old_pattern",
                "reason": "Uses deprecated pattern"
            }
        ],
        "pattern_count": 3,
        "total_matches": 35
    }


@pytest.fixture
def sample_error_response() -> Dict[str, Any]:
    """Sample error response from MCP tool."""
    return {
        "error": "coderef-context MCP server not available",
        "details": "Connection refused"
    }


# ============================================================================
# TEST: call_coderef_patterns - Success Cases
# ============================================================================

@pytest.mark.asyncio
async def test_call_coderef_patterns_success(mock_project, sample_patterns_response):
    """
    TEST-001-A: Verify call_coderef_patterns returns correct data structure.

    Tests:
    - Function returns expected structure
    - success=True when MCP available
    - All expected keys present
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = sample_patterns_response

        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type="async_function",
            limit=50
        )

        # Verify structure
        assert result['success'] is True
        assert 'patterns' in result
        assert 'frequency' in result
        assert 'violations' in result
        assert 'pattern_count' in result

        # Verify data
        assert len(result['patterns']) == 3
        assert result['frequency']['async_function'] == 15
        assert len(result['violations']) == 1
        assert result['pattern_count'] == 3


@pytest.mark.asyncio
async def test_call_coderef_patterns_with_filters(mock_project, sample_patterns_response):
    """
    TEST-001-B: Verify call_coderef_patterns respects pattern_type filter.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        # Simulate filtered response
        filtered_response = {
            **sample_patterns_response,
            "patterns": [p for p in sample_patterns_response["patterns"] if p["type"] == "async_function"]
        }
        mock_mcp.return_value = filtered_response

        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type="async_function",
            limit=10
        )

        # Verify MCP called with correct parameters
        mock_mcp.assert_called_once()
        call_args = mock_mcp.call_args[1]
        assert call_args['pattern_type'] == "async_function"
        assert call_args['limit'] == 10

        # Verify filtered results
        assert result['success'] is True
        assert all(p['type'] == 'async_function' for p in result['patterns'])


# ============================================================================
# TEST: call_coderef_patterns - Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_call_coderef_patterns_unavailable(mock_project):
    """
    TEST-001-C: Verify graceful degradation when CODEREF_CONTEXT_AVAILABLE is False.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', False):
        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=50
        )

        # Verify error response structure
        assert result['success'] is False
        assert 'error' in result
        assert 'coderef-context MCP' in result['error']
        assert 'patterns' in result
        assert result['patterns'] == []
        assert result['frequency'] == {}
        assert result['violations'] == []


@pytest.mark.asyncio
async def test_call_coderef_patterns_mcp_error(mock_project, sample_error_response):
    """
    TEST-001-D: Verify error handling when MCP tool raises exception.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.side_effect = Exception("Connection timeout")

        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=50
        )

        # Verify error response
        assert result['success'] is False
        assert 'error' in result
        assert 'Connection timeout' in result['error']
        assert result['patterns'] == []


@pytest.mark.asyncio
async def test_call_coderef_patterns_invalid_path(tmp_path):
    """
    TEST-001-E: Verify error handling for invalid project path.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True):
        invalid_path = tmp_path / "nonexistent" / "project"

        result = await call_coderef_patterns(
            project_path=str(invalid_path),
            pattern_type=None,
            limit=50
        )

        # Should handle gracefully
        assert result['success'] is False
        assert 'error' in result


# ============================================================================
# TEST: Caching Mechanism
# ============================================================================

@pytest.mark.asyncio
async def test_caching_enabled(mock_project, sample_patterns_response):
    """
    TEST-001-F: Verify caching works properly for repeated calls.
    """
    # Clear cache before test
    _cache.clear()

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = sample_patterns_response

        # First call - should hit MCP
        result1 = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type="async_function",
            limit=50
        )

        # Second call with same params - should hit cache
        result2 = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type="async_function",
            limit=50
        )

        # Verify MCP called only once (second call cached)
        assert mock_mcp.call_count == 1

        # Verify both results identical
        assert result1 == result2
        assert result1['success'] is True


@pytest.mark.asyncio
async def test_caching_different_params(mock_project, sample_patterns_response):
    """
    TEST-001-G: Verify cache differentiates between different parameters.
    """
    # Clear cache before test
    _cache.clear()

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = sample_patterns_response

        # Call 1: pattern_type="async_function"
        await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type="async_function",
            limit=50
        )

        # Call 2: pattern_type="class_definition" (different param)
        await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type="class_definition",
            limit=50
        )

        # Verify MCP called twice (different params = cache miss)
        assert mock_mcp.call_count == 2


@pytest.mark.asyncio
async def test_cache_key_generation(mock_project):
    """
    TEST-001-H: Verify cache key generation is consistent.
    """
    # Clear cache before test
    _cache.clear()

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = {"patterns": [], "frequency": {}, "violations": []}

        # Make same call multiple times
        for _ in range(3):
            await call_coderef_patterns(
                project_path=str(mock_project),
                pattern_type="test",
                limit=10
            )

        # Should only call MCP once (all hits same cache key)
        assert mock_mcp.call_count == 1


# ============================================================================
# TEST: _call_mcp_tool Internal Function
# ============================================================================

@pytest.mark.asyncio
async def test_call_mcp_tool_success(mock_project, sample_patterns_response):
    """
    TEST-001-I: Verify _call_mcp_tool handles successful MCP response.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._get_mcp_client') as mock_client:

        # Mock MCP client
        mock_session = AsyncMock()
        mock_session.call_tool.return_value = sample_patterns_response
        mock_client.return_value.__aenter__.return_value = mock_session

        result = await _call_mcp_tool(
            tool_name="coderef_patterns",
            project_path=str(mock_project),
            pattern_type="async_function",
            limit=50
        )

        assert result == sample_patterns_response


@pytest.mark.asyncio
async def test_call_mcp_tool_error(mock_project):
    """
    TEST-001-J: Verify _call_mcp_tool handles MCP errors gracefully.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._get_mcp_client') as mock_client:

        # Mock MCP client that raises exception
        mock_client.side_effect = Exception("MCP server connection failed")

        with pytest.raises(Exception, match="MCP server connection failed"):
            await _call_mcp_tool(
                tool_name="coderef_patterns",
                project_path=str(mock_project)
            )


# ============================================================================
# TEST: Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_call_coderef_patterns_empty_response(mock_project):
    """
    TEST-001-K: Verify handling of empty patterns response.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = {
            "patterns": [],
            "frequency": {},
            "violations": [],
            "pattern_count": 0
        }

        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=50
        )

        assert result['success'] is True
        assert result['patterns'] == []
        assert result['frequency'] == {}
        assert result['pattern_count'] == 0


@pytest.mark.asyncio
async def test_call_coderef_patterns_malformed_response(mock_project):
    """
    TEST-001-L: Verify handling of malformed MCP response.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        # Return malformed response (missing expected keys)
        mock_mcp.return_value = {
            "data": "unexpected format"
        }

        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=50
        )

        # Should handle gracefully with default empty values
        assert 'patterns' in result
        assert 'frequency' in result
        assert 'violations' in result


@pytest.mark.asyncio
async def test_call_coderef_patterns_limit_boundary(mock_project, sample_patterns_response):
    """
    TEST-001-M: Verify limit parameter boundary cases.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = sample_patterns_response

        # Test limit=0 (should use default)
        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=0
        )
        assert result['success'] is True

        # Test limit=1000 (high value)
        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=1000
        )
        assert result['success'] is True


# ============================================================================
# TEST: Integration with CODEREF_CONTEXT_AVAILABLE Flag
# ============================================================================

def test_coderef_context_available_flag():
    """
    TEST-001-N: Verify CODEREF_CONTEXT_AVAILABLE flag is properly imported.
    """
    # This test ensures the flag is accessible
    assert isinstance(CODEREF_CONTEXT_AVAILABLE, bool)


@pytest.mark.asyncio
async def test_all_functions_respect_availability_flag(mock_project):
    """
    TEST-001-O: Verify all orchestrator functions check CODEREF_CONTEXT_AVAILABLE.
    """
    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', False):
        # call_coderef_patterns should return error when unavailable
        result = await call_coderef_patterns(
            project_path=str(mock_project),
            pattern_type=None,
            limit=50
        )

        assert result['success'] is False
        assert 'error' in result
        assert 'not available' in result['error'].lower()


# ============================================================================
# TEST: Performance
# ============================================================================

@pytest.mark.asyncio
async def test_caching_performance(mock_project, sample_patterns_response):
    """
    TEST-001-P: Verify caching improves performance for repeated calls.
    """
    import time

    _cache.clear()

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        # Simulate slow MCP call (50ms delay)
        async def slow_mcp_call(*args, **kwargs):
            await asyncio.sleep(0.05)
            return sample_patterns_response

        mock_mcp.side_effect = slow_mcp_call

        # First call (should be slow)
        start = time.time()
        await call_coderef_patterns(str(mock_project), None, 50)
        first_duration = time.time() - start

        # Second call (should be fast - cached)
        start = time.time()
        await call_coderef_patterns(str(mock_project), None, 50)
        second_duration = time.time() - start

        # Cached call should be significantly faster
        assert second_duration < first_duration * 0.5  # At least 50% faster


# ============================================================================
# SUMMARY
# ============================================================================

"""
TEST-001 SUMMARY (WO-GENERATION-ENHANCEMENT-001):

Test Coverage:
- ✅ Success cases (A, B)
- ✅ Error handling (C, D, E)
- ✅ Caching mechanism (F, G, H)
- ✅ Internal functions (I, J)
- ✅ Edge cases (K, L, M)
- ✅ Flag integration (N, O)
- ✅ Performance (P)

Total Tests: 16 test functions
Expected Pass Rate: 100%

Tests verify:
1. call_coderef_patterns returns correct data structure
2. Caching works properly (reduces MCP calls)
3. Error handling returns expected error responses
4. Graceful degradation when CODEREF_CONTEXT_AVAILABLE is False
5. Performance improvements from caching
6. Edge cases handled gracefully
"""
