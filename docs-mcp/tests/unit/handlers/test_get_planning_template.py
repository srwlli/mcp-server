#!/usr/bin/env python3
"""
Unit tests for get_planning_template tool (Tool #1).
"""

import asyncio
import sys
import time
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tool_handlers


async def test_get_planning_template():
    """Test get_planning_template tool functionality."""
    print("Testing get_planning_template tool...\n")

    # Test 1: Get all sections
    print("Test 1: Get all sections (section='all')...")
    result = await tool_handlers.handle_get_planning_template({'section': 'all'})
    result_text = result[0].text
    result_data = json.loads(result_text)

    assert result_data['section'] == 'all', "Section should be 'all'"
    assert 'content' in result_data, "Result should have 'content' key"
    assert 'META_DOCUMENTATION' in result_data['content'], "Content should have META_DOCUMENTATION"
    print("[PASS] Returns full template\n")

    # Test 2: Get specific section (META_DOCUMENTATION)
    print("Test 2: Get META_DOCUMENTATION section...")
    result = await tool_handlers.handle_get_planning_template({'section': 'META_DOCUMENTATION'})
    result_text = result[0].text
    result_data = json.loads(result_text)

    assert result_data['section'] == 'META_DOCUMENTATION', "Section should be META_DOCUMENTATION"
    assert 'version' in result_data['content'], "META_DOCUMENTATION should have version"
    print("[PASS] Returns META_DOCUMENTATION section\n")

    # Test 3: Get section from UNIVERSAL_PLANNING_STRUCTURE
    print("Test 3: Get 0_preparation section...")
    result = await tool_handlers.handle_get_planning_template({'section': '0_preparation'})
    result_text = result[0].text
    result_data = json.loads(result_text)

    assert result_data['section'] == '0_preparation', "Section should be 0_preparation"
    assert 'purpose' in result_data['content'], "0_preparation should have purpose"
    print("[PASS] Returns 0_preparation section\n")

    # Test 4: Default section (no parameter)
    print("Test 4: Default section (no parameter)...")
    result = await tool_handlers.handle_get_planning_template({})
    result_text = result[0].text
    result_data = json.loads(result_text)

    assert result_data['section'] == 'all', "Should default to 'all'"
    print("[PASS] Defaults to 'all'\n")

    # Test 5: Invalid section name
    print("Test 5: Invalid section name...")
    result = await tool_handlers.handle_get_planning_template({'section': 'invalid_section'})
    result_text = result[0].text

    assert 'error' in result_text.lower() or 'invalid' in result_text.lower(), "Should return error"
    print("[PASS] Rejects invalid section name\n")

    # Test 6: Verify handler registration
    print("Test 6: Handler registration...")
    assert 'get_planning_template' in tool_handlers.TOOL_HANDLERS, "Handler should be registered"
    print("[PASS] Handler registered in TOOL_HANDLERS\n")

    # Test 7: Performance benchmark with statistical significance
    print("Test 7: Performance benchmark (10 iterations for statistical significance)...")
    durations = []
    for i in range(10):
        start = time.perf_counter()
        result = await tool_handlers.handle_get_planning_template({'section': 'all'})
        duration = time.perf_counter() - start
        durations.append(duration)

    # Calculate statistics
    avg_duration = sum(durations) / len(durations)
    sorted_durations = sorted(durations)
    p95_index = int(len(sorted_durations) * 0.95)
    p95_duration = sorted_durations[p95_index]

    # Assert performance targets
    assert avg_duration < 0.1, f"Average response time {avg_duration*1000:.1f}ms exceeds 100ms target"
    assert p95_duration < 0.12, f"P95 response time {p95_duration*1000:.1f}ms exceeds 120ms target"

    print(f"[PASS] Performance benchmark:")
    print(f"       Average: {avg_duration*1000:.1f}ms (target: <100ms)")
    print(f"       P95: {p95_duration*1000:.1f}ms (target: <120ms)")
    print(f"       Iterations: 10\n")

    print("="*60)
    print("[PASS] All get_planning_template tests passed!")
    print("="*60)
    return True


if __name__ == '__main__':
    success = asyncio.run(test_get_planning_template())
    sys.exit(0 if success else 1)
