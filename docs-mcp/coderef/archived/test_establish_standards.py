#!/usr/bin/env python3
"""
Quick test script for establish_standards tool
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the handler
import tool_handlers

async def test_establish_standards():
    """Test establish_standards on docs-mcp project"""

    print("[TEST] Testing establish_standards tool on docs-mcp project\n")
    print("=" * 70)

    # Set templates dir (required for tool_handlers)
    tool_handlers.set_templates_dir(Path(__file__).parent / "templates" / "power")

    # Test arguments
    arguments = {
        "project_path": str(Path(__file__).parent.resolve()),
        "scan_depth": "standard",
        "focus_areas": ["all"]
    }

    print(f"[PATH] Project Path: {arguments['project_path']}")
    print(f"[SCAN] Scan Depth: {arguments['scan_depth']}")
    print(f"[FOCUS] Focus Areas: {arguments['focus_areas']}\n")
    print("=" * 70)
    print("\n[RUNNING] Running establish_standards...\n")

    try:
        # Call the handler
        result = await tool_handlers.handle_establish_standards(arguments)

        # Print result
        print("[SUCCESS] Result:")
        print("=" * 70)
        for item in result:
            # Handle Unicode properly for Windows console
            text = item.text
            # Encode with ASCII, replacing emojis with '?'
            text_ascii = text.encode('ascii', errors='replace').decode('ascii')
            print(text_ascii)
            print()

        return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_establish_standards())
    sys.exit(0 if success else 1)
