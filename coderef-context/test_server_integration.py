"""Test that the enhanced coderef_context is deployed in the MCP server"""
import json
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))
from handlers_refactored import handle_coderef_context


async def test_server_integration():
    """Verify the enhanced handler is what the server uses"""
    print("=" * 70)
    print("SERVER INTEGRATION TEST")
    print("=" * 70)

    print("\n[Test 1] Handler Import Check")
    print("-" * 70)
    print(f"Handler module: {handle_coderef_context.__module__}")
    print(f"Handler file: {handle_coderef_context.__code__.co_filename}")
    print("[PASS] Enhanced handler from src/handlers_refactored.py imported")

    print("\n[Test 2] Enhanced Response Verification")
    print("-" * 70)
    result = await handle_coderef_context({
        'project_path': '.',
        'output_format': 'json'
    })

    data = json.loads(result[0].text)

    # Check for enhancement fields
    enhanced_fields = [
        'visual_architecture',
        'elements_by_type',
        'complexity_hotspots',
        'documentation_summary'
    ]

    print("Checking for enhanced fields:")
    all_present = True
    for field in enhanced_fields:
        present = field in data and data[field] is not None
        status = "[OK]" if present else "[MISSING]"
        print(f"  {status} {field}")
        if not present:
            all_present = False

    if all_present:
        print("\n[PASS] All 4 enhanced fields present in response")
    else:
        print("\n[FAIL] Some enhanced fields missing")
        return False

    print("\n[Test 3] Server.py Integration Check")
    print("-" * 70)

    # Read server.py to verify import
    server_py = Path(__file__).parent / "server.py"
    server_content = server_py.read_text()

    checks = [
        ("from src.handlers_refactored import", "Handler imported"),
        ("handle_coderef_context,", "Handler listed in imports"),
        ("return await handle_coderef_context(arguments)", "Handler called in tool dispatcher")
    ]

    for check_str, description in checks:
        if check_str in server_content:
            print(f"  [OK] {description}")
        else:
            print(f"  [FAIL] {description}")
            all_present = False

    print("\n[Test 4] Tool Description Check")
    print("-" * 70)

    # Check if tool description mentions enhancements
    if "visual architecture diagram" in server_content:
        print("  [OK] Tool description mentions visual architecture")
    else:
        print("  [WARN] Tool description may be outdated")

    print("\n" + "=" * 70)
    if all_present:
        print("INTEGRATION STATUS: DEPLOYED")
        print("=" * 70)
        print("\nThe enhanced coderef_context handler is:")
        print("  1. Imported in server.py")
        print("  2. Registered as MCP tool")
        print("  3. Returns all 4 enhanced fields")
        print("  4. Ready for use by coderef-docs and coderef-workflow")
        return True
    else:
        print("INTEGRATION STATUS: INCOMPLETE")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_server_integration())
    sys.exit(0 if success else 1)
