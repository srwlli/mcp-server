"""Test the enhanced coderef_context tool"""
import json
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import after path modification
from coderef_reader import CodeRefReader
from handlers_refactored import handle_coderef_context


async def test_enhanced_context():
    """Test the enhanced coderef_context with all new fields"""
    print("Testing enhanced coderef_context tool...")
    print("=" * 60)

    result = await handle_coderef_context({
        'project_path': '.',
        'output_format': 'json'
    })

    data = json.loads(result[0].text)

    # Check for all expected fields
    print("\nResponse keys:")
    for key in data.keys():
        print(f"  - {key}")

    # Check visual_architecture
    if data.get('visual_architecture'):
        lines = data['visual_architecture'].count('\n') + 1
        chars = len(data['visual_architecture'])
        print(f"\n✓ visual_architecture: {lines} lines, {chars} chars")
    else:
        print("\n✗ visual_architecture: NOT PRESENT")

    # Check elements_by_type
    if data.get('elements_by_type'):
        total = data['elements_by_type'].get('total', 0)
        types = len(data['elements_by_type'].get('counts', {}))
        print(f"✓ elements_by_type: {total} elements across {types} types")
    else:
        print("✗ elements_by_type: NOT PRESENT")

    # Check complexity_hotspots
    if data.get('complexity_hotspots'):
        count = len(data['complexity_hotspots'])
        print(f"✓ complexity_hotspots: {count} files")
    else:
        print("✗ complexity_hotspots: NOT PRESENT (expected if complexity.json missing)")

    # Check documentation_summary
    if data.get('documentation_summary'):
        coverage = data['documentation_summary'].get('coverage_percent', 0)
        score = data['documentation_summary'].get('quality_score', 0)
        print(f"✓ documentation_summary: {coverage}% coverage, {score} quality score")
    else:
        print("✗ documentation_summary: NOT PRESENT")

    print("\n" + "=" * 60)
    print("Full response:")
    print(json.dumps(data, indent=2))

    return data


if __name__ == "__main__":
    asyncio.run(test_enhanced_context())
