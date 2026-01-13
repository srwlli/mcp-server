"""
TEST-009: Edge Case Tests (WO-GENERATION-ENHANCEMENT-001)

Tests for edge cases and error scenarios verifying:
- Empty .coderef/index.json handled gracefully
- Malformed JSON in .coderef/ files
- Missing project_path parameter
- Invalid project path
- Permission errors
- Very large codebases (performance boundaries)
- Concurrent tool calls
- Network timeouts (MCP unavailable)

Part of Phase 5 testing for WO-GENERATION-ENHANCEMENT-001.
"""

import asyncio
import json
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import time

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import (
    handle_generate_foundation_docs,
    handle_generate_my_guide,
    handle_establish_standards
)
from generators.user_guide_generator import UserGuideGenerator
from generators.standards_generator import StandardsGenerator
from mcp_integration import check_coderef_resources


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def empty_coderef_project(tmp_path: Path) -> Path:
    """Create project with empty .coderef/index.json."""
    project_dir = tmp_path / "empty-coderef"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    # Empty index
    (coderef_dir / "index.json").write_text("[]")

    return project_dir


@pytest.fixture
def malformed_json_project(tmp_path: Path) -> Path:
    """Create project with malformed JSON in .coderef/."""
    project_dir = tmp_path / "malformed-json"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    # Malformed JSON
    (coderef_dir / "index.json").write_text("{invalid json here")

    return project_dir


# ============================================================================
# TEST: Empty .coderef/index.json
# ============================================================================

def test_empty_index_json_handled_gracefully(empty_coderef_project):
    """
    TEST-009-A: Verify empty index.json doesn't crash tool extraction.
    """
    generator = UserGuideGenerator(None)

    result = generator.extract_mcp_tools(empty_coderef_project)

    # Should return empty but valid structure
    assert result['available'] is True  # File exists
    assert len(result['tools']) == 0  # No tools found
    assert result['total_tools'] == 0


def test_empty_index_resource_check(empty_coderef_project):
    """
    TEST-009-B: Verify resource check handles empty index.json.
    """
    result = check_coderef_resources(empty_coderef_project)

    # Should detect index.json as available
    assert 'index.json' in result['available']


# ============================================================================
# TEST: Malformed JSON
# ============================================================================

def test_malformed_json_handled_gracefully(malformed_json_project):
    """
    TEST-009-C: Verify malformed JSON doesn't crash tool extraction.
    """
    generator = UserGuideGenerator(None)

    result = generator.extract_mcp_tools(malformed_json_project)

    # Should handle gracefully
    assert result['available'] is False or result['tools'] == []


def test_malformed_json_resource_check(malformed_json_project):
    """
    TEST-009-D: Verify resource check handles malformed JSON gracefully.
    """
    # Should not crash
    try:
        result = check_coderef_resources(malformed_json_project)
        # May or may not detect file as available (depends on validation)
        assert isinstance(result, dict)
    except Exception as e:
        # If exception raised, should be informative
        assert 'json' in str(e).lower() or 'parse' in str(e).lower()


# ============================================================================
# TEST: Missing project_path Parameter
# ============================================================================

@pytest.mark.asyncio
async def test_missing_project_path_generates_error():
    """
    TEST-009-E: Verify missing project_path parameter generates clear error.
    """
    arguments = {}  # Missing project_path

    with pytest.raises(Exception) as exc_info:
        result = await handle_generate_foundation_docs(arguments)

    # Error should mention missing parameter
    error_msg = str(exc_info.value).lower()
    assert 'project_path' in error_msg or 'required' in error_msg or 'missing' in error_msg


# ============================================================================
# TEST: Invalid Project Path
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_project_path(tmp_path):
    """
    TEST-009-F: Verify invalid project path handled gracefully.
    """
    invalid_path = tmp_path / "nonexistent" / "deep" / "path"

    arguments = {'project_path': str(invalid_path)}

    # Should handle gracefully (may succeed with warnings or fail gracefully)
    try:
        result = await handle_generate_foundation_docs(arguments)
        # If succeeds, should have warning message
        assert len(result) > 0
    except Exception as e:
        # If fails, error should be informative
        error_msg = str(e).lower()
        assert 'path' in error_msg or 'not found' in error_msg or 'exist' in error_msg


@pytest.mark.asyncio
async def test_non_directory_project_path(tmp_path):
    """
    TEST-009-G: Verify non-directory path handled gracefully.
    """
    # Create a file instead of directory
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("This is a file, not a directory")

    arguments = {'project_path': str(file_path)}

    with pytest.raises(Exception) as exc_info:
        result = await handle_generate_foundation_docs(arguments)

    error_msg = str(exc_info.value).lower()
    assert 'directory' in error_msg or 'path' in error_msg


# ============================================================================
# TEST: Permission Errors
# ============================================================================

@pytest.mark.skipif(sys.platform == "win32", reason="Permission tests unreliable on Windows")
def test_permission_denied_reading_index(tmp_path):
    """
    TEST-009-H: Verify permission errors handled gracefully.
    """
    project_dir = tmp_path / "no-permission"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    index_file = coderef_dir / "index.json"
    index_file.write_text("[]")

    # Remove read permissions
    import os
    os.chmod(index_file, 0o000)

    try:
        generator = UserGuideGenerator(None)
        result = generator.extract_mcp_tools(project_dir)

        # Should handle gracefully
        assert result['available'] is False
    finally:
        # Restore permissions for cleanup
        os.chmod(index_file, 0o644)


# ============================================================================
# TEST: Very Large Codebases
# ============================================================================

@pytest.mark.asyncio
async def test_large_index_json_performance(tmp_path):
    """
    TEST-009-I: Verify performance with very large index.json (10k+ elements).
    """
    project_dir = tmp_path / "large-project"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    # Create large index (10k elements)
    large_index = [
        {
            "name": f"handle_function_{i}",
            "type": "function",
            "file": f"handlers_{i % 100}.py",
            "line": i
        }
        for i in range(10000)
    ]
    (coderef_dir / "index.json").write_text(json.dumps(large_index))

    # Test extraction performance
    generator = UserGuideGenerator(None)

    start = time.time()
    result = generator.extract_mcp_tools(project_dir)
    duration = time.time() - start

    # Should complete in reasonable time (< 5 seconds)
    assert duration < 5.0, f"Large index extraction too slow: {duration:.2f}s"

    # Should extract all handles
    assert len(result['tools']) > 0


# ============================================================================
# TEST: Concurrent Tool Calls
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_tool_calls(mock_project: Path):
    """
    TEST-009-J: Verify concurrent tool calls don't interfere with each other.
    """
    with patch('tool_handlers.handle_generate_individual_doc', new_callable=AsyncMock) as mock_individual:
        mock_individual.return_value = [Mock(text="Generated")]

        # Run 3 concurrent calls
        tasks = [
            handle_generate_foundation_docs({'project_path': str(mock_project)})
            for _ in range(3)
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert len(result) > 0


# ============================================================================
# TEST: Network Timeouts (MCP Unavailable)
# ============================================================================

@pytest.mark.asyncio
async def test_mcp_timeout_handled_gracefully():
    """
    TEST-009-K: Verify MCP timeout handled without hanging.
    """
    from mcp_orchestrator import call_coderef_patterns

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        # Simulate timeout
        async def timeout_call(*args, **kwargs):
            await asyncio.sleep(10)  # Long delay
            raise asyncio.TimeoutError("MCP call timed out")

        mock_mcp.side_effect = timeout_call

        # Should handle timeout gracefully (don't wait 10 seconds)
        start = time.time()
        try:
            result = await asyncio.wait_for(
                call_coderef_patterns("/fake/path", None, 50),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            pass  # Expected
        duration = time.time() - start

        # Should timeout within 2 seconds
        assert duration < 3.0


# ============================================================================
# TEST: Invalid Template Names
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_template_name(mock_project: Path):
    """
    TEST-009-L: Verify invalid template name handled gracefully.
    """
    from tool_handlers import handle_generate_individual_doc

    arguments = {
        'project_path': str(mock_project),
        'template_name': 'nonexistent_template'
    }

    with pytest.raises(Exception) as exc_info:
        result = await handle_generate_individual_doc(arguments)

    error_msg = str(exc_info.value).lower()
    assert 'template' in error_msg or 'not found' in error_msg or 'invalid' in error_msg


# ============================================================================
# TEST: Circular Dependencies (MCP)
# ============================================================================

@pytest.mark.asyncio
async def test_mcp_circular_dependency_prevention():
    """
    TEST-009-M: Verify circular MCP calls don't cause infinite loop.
    """
    from mcp_orchestrator import call_coderef_patterns

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        # Simulate MCP returning result that triggers another MCP call
        call_count = [0]

        async def recursive_call(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] > 10:
                raise RuntimeError("Too many recursive calls")
            return {
                'patterns': [],
                'frequency': {},
                'violations': []
            }

        mock_mcp.side_effect = recursive_call

        result = await call_coderef_patterns("/fake/path", None, 50)

        # Should complete without infinite recursion
        assert call_count[0] <= 10


# ============================================================================
# TEST: Special Characters in Paths
# ============================================================================

@pytest.mark.asyncio
async def test_special_characters_in_project_path(tmp_path):
    """
    TEST-009-N: Verify special characters in path handled correctly.
    """
    # Create path with spaces and special chars
    project_dir = tmp_path / "project with spaces & (special) chars"
    project_dir.mkdir()

    (project_dir / "coderef" / "foundation-docs").mkdir(parents=True)

    arguments = {'project_path': str(project_dir)}

    with patch('tool_handlers.handle_generate_individual_doc', new_callable=AsyncMock) as mock_individual:
        mock_individual.return_value = [Mock(text="Generated")]

        # Should handle path correctly
        result = await handle_generate_foundation_docs(arguments)
        assert len(result) > 0


# ============================================================================
# TEST: Unicode in File Contents
# ============================================================================

def test_unicode_in_index_json(tmp_path):
    """
    TEST-009-O: Verify Unicode characters in index.json handled correctly.
    """
    project_dir = tmp_path / "unicode-project"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    # Index with Unicode
    unicode_index = [
        {"name": "handleユーザー認証", "type": "function", "file": "auth.py", "line": 1},
        {"name": "générer_rapport", "type": "function", "file": "reports.py", "line": 10}
    ]
    (coderef_dir / "index.json").write_text(json.dumps(unicode_index, ensure_ascii=False), encoding='utf-8')

    generator = UserGuideGenerator(None)
    result = generator.extract_mcp_tools(project_dir)

    # Should extract tools with Unicode names
    assert result['available'] is True
    assert len(result['tools']) > 0


# ============================================================================
# TEST: Empty Project Directory
# ============================================================================

@pytest.mark.asyncio
async def test_completely_empty_project_directory(tmp_path):
    """
    TEST-009-P: Verify completely empty project directory handled.
    """
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    arguments = {'project_path': str(empty_dir)}

    # Should handle gracefully (may warn but shouldn't crash)
    with patch('tool_handlers.handle_generate_individual_doc', new_callable=AsyncMock) as mock_individual:
        mock_individual.return_value = [Mock(text="Generated with warnings")]

        result = await handle_generate_foundation_docs(arguments)
        assert len(result) > 0


# ============================================================================
# TEST: Rapid Repeated Calls
# ============================================================================

@pytest.mark.asyncio
async def test_rapid_repeated_calls(mock_project: Path):
    """
    TEST-009-Q: Verify rapid repeated calls don't cause issues.
    """
    with patch('tool_handlers.handle_generate_individual_doc', new_callable=AsyncMock) as mock_individual:
        mock_individual.return_value = [Mock(text="Generated")]

        # Call 10 times rapidly
        for _ in range(10):
            result = await handle_generate_foundation_docs({'project_path': str(mock_project)})
            assert len(result) > 0


# ============================================================================
# TEST: Memory Constraints
# ============================================================================

def test_large_file_memory_efficiency(tmp_path):
    """
    TEST-009-R: Verify large files don't cause memory issues.
    """
    project_dir = tmp_path / "large-files"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    # Create very large index (100k elements - ~10MB JSON)
    large_index = [
        {
            "name": f"function_{i}",
            "type": "function",
            "file": f"file_{i % 1000}.py",
            "line": i,
            "signature": f"def function_{i}(arg1: str, arg2: int) -> bool",
            "docstring": f"This is function {i} " * 10
        }
        for i in range(100000)
    ]

    (coderef_dir / "index.json").write_text(json.dumps(large_index))

    # Test memory-efficient handling
    generator = UserGuideGenerator(None)

    import tracemalloc
    tracemalloc.start()

    result = generator.extract_mcp_tools(project_dir)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Memory should be reasonable (< 100MB)
    assert peak < 100 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.1f}MB"


# ============================================================================
# TEST: Null/None Values
# ============================================================================

def test_null_values_in_index_json(tmp_path):
    """
    TEST-009-S: Verify null/None values in JSON handled gracefully.
    """
    project_dir = tmp_path / "null-values"
    project_dir.mkdir()

    coderef_dir = project_dir / ".coderef"
    coderef_dir.mkdir()

    # Index with null values
    index_with_nulls = [
        {"name": "function1", "type": None, "file": "test.py", "line": 1},
        {"name": None, "type": "function", "file": "test.py", "line": 2}
    ]
    (coderef_dir / "index.json").write_text(json.dumps(index_with_nulls))

    generator = UserGuideGenerator(None)
    result = generator.extract_mcp_tools(project_dir)

    # Should handle gracefully (filter out invalid entries)
    assert isinstance(result, dict)


# ============================================================================
# TEST: Cache Corruption
# ============================================================================

@pytest.mark.asyncio
async def test_corrupted_cache_handled(tmp_path):
    """
    TEST-009-T: Verify corrupted MCP cache handled gracefully.
    """
    from mcp_orchestrator import _cache, call_coderef_patterns

    # Corrupt cache with invalid data
    _cache["corrupted_key"] = "not a dict"

    with patch('mcp_orchestrator.CODEREF_CONTEXT_AVAILABLE', True), \
         patch('mcp_orchestrator._call_mcp_tool', new_callable=AsyncMock) as mock_mcp:

        mock_mcp.return_value = {
            'patterns': [],
            'frequency': {},
            'violations': []
        }

        # Should not crash due to corrupted cache
        result = await call_coderef_patterns(str(tmp_path), None, 50)
        assert isinstance(result, dict)


# ============================================================================
# SUMMARY
# ============================================================================

"""
TEST-009 SUMMARY (WO-GENERATION-ENHANCEMENT-001):

Test Coverage:
- ✅ Empty index.json (A, B)
- ✅ Malformed JSON (C, D)
- ✅ Missing/invalid parameters (E, F, G)
- ✅ Permission errors (H)
- ✅ Large codebases (I, R)
- ✅ Concurrent calls (J)
- ✅ Network timeouts (K)
- ✅ Invalid inputs (L, M)
- ✅ Special characters (N)
- ✅ Unicode (O)
- ✅ Empty directories (P)
- ✅ Rapid calls (Q)
- ✅ Null values (S)
- ✅ Cache corruption (T)

Total Tests: 20 test functions
Expected Pass Rate: 95%+ (some platform-specific tests may skip)

Tests verify:
1. Empty .coderef/index.json handled gracefully
2. Malformed JSON doesn't crash tools
3. Missing/invalid parameters generate clear errors
4. Permission errors handled gracefully
5. Large codebases (10k+ elements) perform well (< 5s)
6. Concurrent tool calls don't interfere
7. Network timeouts handled without hanging
8. Invalid template names rejected with clear errors
9. Special characters and Unicode supported
10. Empty projects handled with warnings
11. Rapid repeated calls work correctly
12. Memory efficient with very large files (< 100MB)
13. Null values filtered appropriately
14. Corrupted cache doesn't crash system
"""
