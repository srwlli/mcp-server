"""Simple test to capture JSON output"""
import json
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))
from coderef_reader import CodeRefReader
from handlers_refactored import handle_coderef_context


async def main():
    result = await handle_coderef_context({'project_path': '.', 'output_format': 'json'})
    data = json.loads(result[0].text)

    # Write to file
    with open('phase1_sample_response.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    # Count tool calls (before = 6, after = 1)
    fields_present = []
    if data.get('visual_architecture'):
        fields_present.append('visual_architecture')
    if data.get('elements_by_type'):
        fields_present.append('elements_by_type')
    if data.get('complexity_hotspots'):
        fields_present.append('complexity_hotspots')
    if data.get('documentation_summary'):
        fields_present.append('documentation_summary')

    print(f"Fields present: {len(fields_present)}/4")
    for field in fields_present:
        print(f"  - {field}: OK")

    return data, fields_present


if __name__ == "__main__":
    asyncio.run(main())
