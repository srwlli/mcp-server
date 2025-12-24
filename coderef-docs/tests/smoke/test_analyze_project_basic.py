#!/usr/bin/env python3
"""
Basic smoke test for analyze_project_for_planning tool (Tool #2).
Tests on coderef-docs project itself to verify implementation works.
"""

import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tool_handlers


async def test_analyze_docs_mcp():
    """Test analyze_project_for_planning on coderef-docs project itself."""
    print("Testing analyze_project_for_planning tool...\n")

    # Test on coderef-docs project itself (two levels up from tests/smoke/)
    project_path = str(Path(__file__).parent.parent.parent)
    print(f"Analyzing project: {project_path}\n")

    result = await tool_handlers.handle_analyze_project_for_planning({
        'project_path': project_path
    })

    # Parse result
    result_text = result[0].text
    result_data = json.loads(result_text)

    print("=" * 60)
    print("ANALYSIS RESULTS:")
    print("=" * 60)
    print()

    # Check foundation_docs
    print("Foundation Docs:")
    print(f"  Available: {len(result_data['foundation_docs']['available'])}")
    for doc in result_data['foundation_docs']['available']:
        print(f"    - {doc}")
    print(f"  Missing: {len(result_data['foundation_docs']['missing'])}")
    if result_data['foundation_docs']['missing']:
        for doc in result_data['foundation_docs']['missing'][:3]:
            print(f"    - {doc}")
    print()

    # Check coding_standards
    print("Coding Standards:")
    print(f"  Available: {len(result_data['coding_standards']['available'])}")
    for standard in result_data['coding_standards']['available']:
        print(f"    - {standard}")
    print(f"  Missing: {len(result_data['coding_standards']['missing'])}")
    print()

    # Check technology stack
    print("Technology Stack:")
    print(f"  Language: {result_data['technology_stack']['language']}")
    print(f"  Framework: {result_data['technology_stack']['framework']}")
    print(f"  Testing: {result_data['technology_stack']['testing']}")
    print()

    # Check patterns
    print("Patterns Identified:")
    print(f"  Count: {len(result_data['key_patterns_identified'])}")
    for pattern in result_data['key_patterns_identified'][:5]:
        print(f"    - {pattern}")
    print()

    # Check project structure
    print("Project Structure:")
    print(f"  Organization: {result_data['project_structure']['organization_pattern']}")
    print(f"  Main Directories: {len(result_data['project_structure']['main_directories'])}")
    print()

    # Check gaps
    print("Gaps and Risks:")
    print(f"  Count: {len(result_data['gaps_and_risks'])}")
    for gap in result_data['gaps_and_risks'][:5]:
        print(f"    - {gap}")
    print()

    print("=" * 60)
    print("[PASS] Analysis completed successfully!")
    print("=" * 60)

    # Basic assertions
    assert 'foundation_docs' in result_data, "Missing foundation_docs"
    assert 'coding_standards' in result_data, "Missing coding_standards"
    assert 'technology_stack' in result_data, "Missing technology_stack"
    assert 'key_patterns_identified' in result_data, "Missing key_patterns_identified"
    assert 'project_structure' in result_data, "Missing project_structure"
    assert 'gaps_and_risks' in result_data, "Missing gaps_and_risks"

    # Verify Python detected
    assert result_data['technology_stack']['language'] == 'Python', f"Expected Python, got {result_data['technology_stack']['language']}"

    # Verify some docs exist
    assert len(result_data['foundation_docs']['available']) > 0, "Should have found some foundation docs"

    print("\n[PASS] All assertions passed!")
    return True


if __name__ == '__main__':
    try:
        success = asyncio.run(test_analyze_docs_mcp())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
