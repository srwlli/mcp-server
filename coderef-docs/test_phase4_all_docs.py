#!/usr/bin/env python3
"""
Phase 4 Comprehensive Test - All 5 Foundation Docs with Papertrail UDS

Tests all 5 doc types: README, ARCHITECTURE, API, SCHEMA, COMPONENTS
"""

import os
import sys
from pathlib import Path
import asyncio

# Enable Papertrail
os.environ["PAPERTRAIL_ENABLED"] = "true"

# Add coderef-docs to path
sys.path.insert(0, str(Path(__file__).parent))

# Import handler
from tool_handlers import handle_generate_individual_doc

print("=" * 80)
print("PHASE 4 COMPREHENSIVE TEST: All 5 Foundation Docs with Papertrail UDS")
print("=" * 80)

# Set required globals
import tool_handlers
tool_handlers.TEMPLATES_DIR = Path(__file__).parent / "templates" / "power"

async def test_doc_generation(template_name: str):
    """Test document generation with UDS"""
    print(f"\n[TEST {template_name.upper()}] Generating with Papertrail UDS")
    print("-" * 80)

    # Prepare arguments
    arguments = {
        "project_path": str(Path(__file__).parent.parent / "papertrail"),
        "template_name": template_name,
        "workorder_id": "WO-PAPERTRAIL-PYTHON-PACKAGE-001",
        "feature_id": "papertrail-uds",
        "version": "1.0.0"
    }

    try:
        # Call handler
        result = await handle_generate_individual_doc(arguments)

        # Extract text from result
        doc = result[0].text

        # Verify UDS present
        checks = {
            "workorder_id": "workorder_id: WO-PAPERTRAIL-PYTHON-PACKAGE-001" in doc,
            "generated_by": "generated_by: coderef-docs" in doc,
            "feature_id": "feature_id: papertrail-uds" in doc,
            "timestamp": "timestamp:" in doc,
            "copyright": "Copyright" in doc,
            "UDS header": "---" in doc[:500],  # YAML frontmatter
        }

        all_passed = all(checks.values())
        status = "[PASS]" if all_passed else "[FAIL]"

        print(f"{status} {template_name.upper()}: {sum(checks.values())}/6 checks passed")

        if not all_passed:
            print("  Failed checks:")
            for check, result in checks.items():
                if not result:
                    print(f"    - {check}")

        return all_passed

    except Exception as e:
        print(f"[FAIL] {template_name.upper()}: {e}")
        return False


async def run_all_tests():
    """Test all 5 foundation doc types"""
    doc_types = ["readme", "architecture", "api", "schema", "components"]
    results = {}

    for doc_type in doc_types:
        results[doc_type] = await test_doc_generation(doc_type)

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 4 TEST RESULTS")
    print("=" * 80)

    passed = sum(results.values())
    total = len(results)

    for doc_type, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {doc_type.upper()}")

    print("=" * 80)
    print(f"TOTAL: {passed}/{total} doc types passed")

    if passed == total:
        print("\n[SUCCESS] All 5 foundation docs generated with Papertrail UDS!\n")
        print("Phase 4 Gradual Rollout: COMPLETE")
        return True
    else:
        print(f"\n[FAIL] {total - passed} doc types failed.\n")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
