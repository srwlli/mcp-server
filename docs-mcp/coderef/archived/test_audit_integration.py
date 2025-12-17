#!/usr/bin/env python3
"""
Integration test for audit_codebase tool.

Tests the complete workflow:
1. Establish standards from docs-mcp codebase
2. Run audit on docs-mcp codebase
3. Verify report generation and compliance scoring
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tool_handlers

async def test_audit_workflow():
    """Test complete audit workflow."""
    print("Testing audit_codebase integration...\n")

    # Test 1: Establish standards (should already exist from Tool #8)
    print("Test 1: Checking if standards exist...")
    project_path = str(Path(__file__).parent.resolve())
    standards_dir = Path(project_path) / "coderef" / "standards"

    if not standards_dir.exists():
        print("[FAIL] Standards directory not found. Run establish_standards first.")
        return False

    print(f"[PASS] Standards directory found: {standards_dir}\n")

    # Test 2: Run audit
    print("Test 2: Running audit_codebase...")
    try:
        # Set templates dir (required by handlers)
        tool_handlers.set_templates_dir(Path(project_path) / "templates" / "power")

        result = await tool_handlers.handle_audit_codebase({
            "project_path": project_path,
            "standards_dir": "coderef/standards",
            "severity_filter": "all",
            "scope": ["all"],
            "generate_fixes": True
        })

        result_text = result[0].text
        print("[PASS] Audit completed successfully!\n")

        # Test 3: Verify report content
        print("Test 3: Verifying report content...")

        checks = [
            ("Compliance Score" in result_text, "Contains compliance score"),
            ("Violations Found" in result_text, "Contains violation count"),
            ("Files Scanned" in result_text, "Contains files scanned"),
            ("Scan Duration" in result_text, "Contains scan duration"),
            ("AUDIT REPORT" in result_text or "Audit Report" in result_text, "Contains report path")
        ]

        all_passed = True
        for check, description in checks:
            status = "[PASS]" if check else "[FAIL]"
            print(f"{status} {description}")
            if not check:
                all_passed = False

        print("\n" + "="*60)
        print("AUDIT OUTPUT SUMMARY:")
        print("="*60)
        # Extract key metrics without emojis
        lines = result_text.split('\n')[:20]
        for line in lines:
            try:
                # Try to print, skip lines with encoding issues
                print(line.encode('ascii', errors='ignore').decode('ascii'))
            except:
                pass
        print("...")
        print("="*60 + "\n")

        if all_passed:
            print("[PASS] All integration tests passed!")
            return True
        else:
            print("[FAIL] Some tests failed")
            return False

    except Exception as e:
        print(f"[FAIL] Error during audit: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_audit_workflow())
    sys.exit(0 if success else 1)
