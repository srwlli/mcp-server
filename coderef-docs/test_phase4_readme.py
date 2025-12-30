#!/usr/bin/env python3
"""
Phase 4 Test - README Generation with Papertrail UDS

Tests generate_individual_doc with workorder tracking.
"""

import os
import sys
from pathlib import Path

# Enable Papertrail
os.environ["PAPERTRAIL_ENABLED"] = "true"

# Add coderef-docs to path
sys.path.insert(0, str(Path(__file__).parent))

# Import handler
from tool_handlers import handle_generate_individual_doc
import asyncio

print("=" * 70)
print("PHASE 4 TEST: README Generation with Papertrail UDS")
print("=" * 70)

async def test_readme_generation():
    """Test README generation with UDS"""
    print("\n[TEST] Generating README with Papertrail UDS")
    print("-" * 70)

    # Prepare arguments
    arguments = {
        "project_path": str(Path(__file__).parent.parent / "papertrail"),
        "template_name": "readme",
        "workorder_id": "WO-PAPERTRAIL-PYTHON-PACKAGE-001",
        "feature_id": "papertrail-uds",
        "version": "1.0.0"
    }

    print(f"Project: {arguments['project_path']}")
    print(f"Template: {arguments['template_name']}")
    print(f"Workorder: {arguments['workorder_id']}")
    print(f"Feature: {arguments['feature_id']}")
    print(f"Version: {arguments['version']}")

    try:
        # Set required globals
        import tool_handlers
        tool_handlers.TEMPLATES_DIR = Path(__file__).parent / "templates" / "power"

        # Call handler
        result = await handle_generate_individual_doc(arguments)

        # Extract text from result
        doc = result[0].text

        print("\n[SUCCESS] Generated README with UDS")
        print("=" * 70)
        print("First 1000 characters:")
        print("-" * 70)
        print(doc[:1000])
        print("-" * 70)

        # Verify UDS present
        checks = {
            "workorder_id present": "workorder_id: WO-PAPERTRAIL-PYTHON-PACKAGE-001" in doc,
            "generated_by present": "generated_by: coderef-docs" in doc,
            "feature_id present": "feature_id: papertrail-uds" in doc,
            "timestamp present": "timestamp:" in doc,
            "copyright present": "Copyright" in doc,
            "UDS header present": "---" in doc[:500],  # YAML frontmatter
        }

        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        all_passed = True
        for check, result in checks.items():
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {check}")
            if not result:
                all_passed = False

        print("=" * 70)
        if all_passed:
            print("\n[SUCCESS] All Phase 4 UDS checks passed!\n")
            return True
        else:
            print("\n[FAIL] Some checks failed.\n")
            return False

    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_readme_generation())
    sys.exit(0 if success else 1)
