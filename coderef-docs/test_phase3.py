#!/usr/bin/env python3
"""
Phase 3 Integration Test

Tests Papertrail integration in coderef-docs.
"""

import os
import sys
from pathlib import Path

# Set feature flag
os.environ["PAPERTRAIL_ENABLED"] = "true"

# Add coderef-docs to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.foundation_generator import FoundationGenerator

def test_generate_with_uds():
    """Test generate_with_uds() method"""
    print("=" * 60)
    print("TEST 1: generate_with_uds() with PAPERTRAIL_ENABLED=true")
    print("=" * 60)

    # Create generator
    templates_dir = Path(__file__).parent / "templates" / "power"
    gen = FoundationGenerator(templates_dir)

    # Test context
    context = {
        "title": "Test Project",
        "project_path": str(Path(__file__).parent),
        "description": "A test project for Phase 3 validation",
        "version": "1.0.0"
    }

    # Generate with UDS
    try:
        result = gen.generate_with_uds(
            template_name="readme",
            context=context,
            workorder_id="WO-TEST-PHASE3-001",
            feature_id="phase3-test",
            version="1.0.0"
        )

        print("\n[SUCCESS] Generated document with UDS\n")
        print("First 800 characters:")
        print("-" * 60)
        print(result[:800])
        print("-" * 60)

        # Verify UDS header present
        assert "workorder_id: WO-TEST-PHASE3-001" in result, "Missing workorder_id"
        assert "generated_by: coderef-docs" in result, "Missing generated_by"
        assert "feature_id: phase3-test" in result, "Missing feature_id"
        assert "timestamp:" in result, "Missing timestamp"

        # Verify UDS footer present
        assert "Copyright ©" in result, "Missing copyright footer"

        print("\n[PASS] All UDS fields verified!")
        return True

    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_mode():
    """Test fallback to legacy when flag is OFF"""
    print("\n" + "=" * 60)
    print("TEST 2: Fallback mode with PAPERTRAIL_ENABLED=false")
    print("=" * 60)

    # Disable feature flag
    os.environ["PAPERTRAIL_ENABLED"] = "false"

    # Reimport to pick up new flag value
    import importlib
    from generators import foundation_generator
    importlib.reload(foundation_generator)
    from generators.foundation_generator import FoundationGenerator

    templates_dir = Path(__file__).parent / "templates" / "power"
    gen = FoundationGenerator(templates_dir)

    context = {
        "title": "Test Project",
        "project_path": str(Path(__file__).parent),
    }

    try:
        result = gen.generate_with_uds(
            template_name="readme",
            context=context,
            workorder_id="WO-TEST-PHASE3-002",
            feature_id="phase3-test"
        )

        # Should fall back to legacy (no UDS headers)
        if "workorder_id:" in result:
            print("[FAIL] UDS headers present when flag is OFF")
            return False

        print("\n[PASS] Fallback to legacy generator works")
        print("(No UDS headers in output when flag=false)")
        return True

    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nPhase 3 Integration Tests")
    print("Testing Papertrail integration in coderef-docs\n")

    test1_passed = test_generate_with_uds()
    test2_passed = test_fallback_mode()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Test 1 (UDS generation):     {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"Test 2 (Fallback mode):      {'[PASS]' if test2_passed else '[FAIL]'}")
    print("=" * 60)

    if test1_passed and test2_passed:
        print("\n[SUCCESS] All tests passed! Phase 3 integration working correctly.\n")
        sys.exit(0)
    else:
        print("\n[FAIL] Some tests failed. Check output above.\n")
        sys.exit(1)
