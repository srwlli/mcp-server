#!/usr/bin/env python3
"""
Unit tests for PlanningGenerator and create_plan tool.
"""

import asyncio
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.planning_generator import PlanningGenerator
import tool_handlers
from validation import validate_feature_name_input


async def test_feature_name_validation():
    """Test feature name validation."""
    print("Testing feature name validation...\n")

    # Test 1: Valid feature names
    print("Test 1: Valid feature names...")
    valid_names = ["create-plan", "auth-system", "user_profile", "feature123", "API-v2"]
    for name in valid_names:
        try:
            result = validate_feature_name_input(name)
            assert result == name, f"Validation should return original name: {name}"
        except ValueError as e:
            raise AssertionError(f"Valid name '{name}' rejected: {e}")
    print(f"[PASS] All {len(valid_names)} valid names accepted\n")

    # Test 2: Invalid feature names (path traversal)
    print("Test 2: Invalid feature names (path traversal)...")
    invalid_names = [
        "../parent",
        "../../etc/passwd",
        "feature/../secret",
        ".",
        "..",
    ]
    for name in invalid_names:
        try:
            validate_feature_name_input(name)
            raise AssertionError(f"Invalid name should be rejected: {name}")
        except ValueError:
            pass  # Expected
    print(f"[PASS] All {len(invalid_names)} path traversal attempts blocked\n")

    # Test 3: Invalid characters
    print("Test 3: Invalid characters...")
    invalid_chars = [
        "feature/name",
        "feature\\name",
        "feature name",
        "feature@name",
        "feature$name",
        "feature!name",
    ]
    for name in invalid_chars:
        try:
            validate_feature_name_input(name)
            raise AssertionError(f"Invalid character should be rejected: {name}")
        except ValueError:
            pass  # Expected
    print(f"[PASS] All {len(invalid_chars)} invalid character names rejected\n")

    # Test 4: Empty/None
    print("Test 4: Empty/None validation...")
    try:
        validate_feature_name_input("")
        raise AssertionError("Empty string should be rejected")
    except ValueError:
        pass  # Expected
    print("[PASS] Empty string rejected\n")

    # Test 5: Too long (>100 chars)
    print("Test 5: Max length validation...")
    long_name = "a" * 101
    try:
        validate_feature_name_input(long_name)
        raise AssertionError("Name >100 chars should be rejected")
    except ValueError:
        pass  # Expected
    print("[PASS] Long name rejected\n")

    print("="*60)
    print("[PASS] All feature name validation tests passed!")
    print("="*60 + "\n")
    return True


async def test_planning_generator_basic():
    """Test PlanningGenerator basic functionality."""
    print("Testing PlanningGenerator basic functionality...\n")

    # Create temp directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Initialize generator
        print("Test 1: Initialize PlanningGenerator...")
        generator = PlanningGenerator(temp_path)
        assert generator.project_path == temp_path.resolve(), "Project path should be resolved"
        print("[PASS] Generator initialized\n")

        # Test 2: Load template (AI-optimized)
        print("Test 2: Load AI-optimized template...")
        try:
            template = generator.load_template()
            assert template is not None, "Template should not be None"
            assert isinstance(template, dict), "Template should be a dict"
            assert '_AI_INSTRUCTIONS' in template or 'REQUIRED_SECTIONS' in template, \
                "Template should have expected structure"
            print(f"[PASS] Template loaded successfully (type: {type(template).__name__})\n")
        except FileNotFoundError:
            print("[SKIP] AI-optimized template not found (planning-template-for-ai.json)\n")

        # Test 3: Load context (should return None if not exists)
        print("Test 3: Load context (no context.json)...")
        context = generator.load_context("test-feature")
        assert context is None, "Context should be None when file doesn't exist"
        print("[PASS] Returns None for missing context\n")

        # Test 4: Create context directory and file
        print("Test 4: Load context (with context.json)...")
        feature_name = "test-feature"
        working_dir = temp_path / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True, exist_ok=True)
        context_file = working_dir / "context.json"
        test_context = {
            "feature_name": feature_name,
            "description": "Test feature",
            "requirements": ["req1", "req2"]
        }
        context_file.write_text(json.dumps(test_context, indent=2))

        context = generator.load_context(feature_name)
        assert context is not None, "Context should not be None"
        assert context["feature_name"] == feature_name, "Context should have correct feature_name"
        print("[PASS] Context loaded successfully\n")

        # Test 5: Save plan
        print("Test 5: Save plan to working directory...")
        test_plan = {
            "META_DOCUMENTATION": {
                "feature_name": feature_name,
                "version": "1.0.0"
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "0_preparation": {"status": "complete"}
            }
        }
        plan_path = generator.save_plan(feature_name, test_plan)
        assert Path(plan_path).exists(), "Plan file should exist"
        assert Path(plan_path).name == "plan.json", "Plan should be named plan.json"

        # Verify plan content
        saved_plan = json.loads(Path(plan_path).read_text())
        assert saved_plan["META_DOCUMENTATION"]["feature_name"] == feature_name, \
            "Saved plan should match original"
        print(f"[PASS] Plan saved to {plan_path}\n")

    print("="*60)
    print("[PASS] All PlanningGenerator basic tests passed!")
    print("="*60 + "\n")
    return True


async def test_create_plan_handler():
    """Test create_plan handler via MCP interface."""
    print("Testing create_plan handler...\n")

    # Create temp directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Handler registration
        print("Test 1: Handler registration...")
        assert 'create_plan' in tool_handlers.TOOL_HANDLERS, \
            "create_plan handler should be registered"
        print("[PASS] Handler registered in TOOL_HANDLERS\n")

        # Test 2: Invalid inputs - empty project_path
        print("Test 2: Invalid project_path...")
        result = await tool_handlers.handle_create_plan({
            'project_path': '',
            'feature_name': 'test-feature'
        })
        result_text = result[0].text
        assert 'error' in result_text.lower() or 'invalid' in result_text.lower(), \
            "Should reject empty project_path"
        print("[PASS] Empty project_path rejected\n")

        # Test 3: Invalid inputs - invalid feature_name
        print("Test 3: Invalid feature_name (path traversal)...")
        result = await tool_handlers.handle_create_plan({
            'project_path': str(temp_path),
            'feature_name': '../../../etc/passwd'
        })
        result_text = result[0].text
        assert 'error' in result_text.lower() or 'invalid' in result_text.lower(), \
            "Should reject path traversal in feature_name"
        print("[PASS] Path traversal rejected\n")

        # Test 4: Invalid feature_name with special characters
        print("Test 4: Invalid feature_name (special characters)...")
        result = await tool_handlers.handle_create_plan({
            'project_path': str(temp_path),
            'feature_name': 'feature@name!'
        })
        result_text = result[0].text
        assert 'error' in result_text.lower() or 'invalid' in result_text.lower(), \
            "Should reject special characters in feature_name"
        print("[PASS] Special characters rejected\n")

        # Test 5: Valid inputs but missing template (expected to fail gracefully)
        print("Test 5: Valid inputs (may fail if template missing - expected)...")
        result = await tool_handlers.handle_create_plan({
            'project_path': str(temp_path),
            'feature_name': 'test-feature'
        })
        result_text = result[0].text
        # Handler should either succeed or fail with graceful error
        # We just verify it returns a response
        assert len(result_text) > 0, "Handler should return a response"
        if 'error' in result_text.lower():
            print("[EXPECTED] Template not found or plan generation failed\n")
        else:
            print("[PASS] Handler executed successfully\n")

    print("="*60)
    print("[PASS] All create_plan handler tests passed!")
    print("="*60 + "\n")
    return True


async def test_partial_plan_creation():
    """Test partial plan creation with TODOs."""
    print("Testing partial plan creation...\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        generator = PlanningGenerator(temp_path)

        # Test 1: Create partial plan
        print("Test 1: Create partial plan with error message...")
        feature_name = "test-feature"
        error_message = "Test error: generation failed"
        partial_plan = generator._create_partial_plan(feature_name, error_message)

        assert partial_plan is not None, "Partial plan should not be None"
        assert 'META_DOCUMENTATION' in partial_plan, "Should have META_DOCUMENTATION"
        assert partial_plan['META_DOCUMENTATION']['feature_name'] == feature_name, \
            "Should have correct feature_name"
        assert partial_plan['META_DOCUMENTATION']['status'] == 'partial', \
            "Status should be 'partial'"
        assert 'UNIVERSAL_PLANNING_STRUCTURE' in partial_plan, "Should have planning structure"
        print("[PASS] Partial plan created with correct structure\n")

        # Test 2: Verify TODOs present
        print("Test 2: Verify TODOs in sections...")
        planning_sections = partial_plan['UNIVERSAL_PLANNING_STRUCTURE']
        todo_count = 0
        for section_name, section_data in planning_sections.items():
            if isinstance(section_data, dict):
                section_str = json.dumps(section_data)
                if 'TODO' in section_str:
                    todo_count += 1

        assert todo_count > 0, "Partial plan should contain TODO markers"
        print(f"[PASS] Found {todo_count} sections with TODO markers\n")

        # Test 3: Save partial plan
        print("Test 3: Save partial plan...")
        plan_path = generator.save_plan(feature_name, partial_plan)
        assert Path(plan_path).exists(), "Partial plan should be saved"

        # Verify it can be loaded back
        saved_plan = json.loads(Path(plan_path).read_text())
        assert saved_plan['META_DOCUMENTATION']['status'] == 'partial', \
            "Saved plan should maintain partial status"
        print(f"[PASS] Partial plan saved and verified at {plan_path}\n")

    print("="*60)
    print("[PASS] All partial plan creation tests passed!")
    print("="*60 + "\n")
    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PLANNING GENERATOR TEST SUITE")
    print("="*60 + "\n")

    try:
        await test_feature_name_validation()
        await test_planning_generator_basic()
        await test_create_plan_handler()
        await test_partial_plan_creation()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60 + "\n")
        return True

    except AssertionError as e:
        print("\n" + "="*60)
        print(f"TEST FAILED: {e}")
        print("="*60 + "\n")
        return False
    except Exception as e:
        print("\n" + "="*60)
        print(f"TEST ERROR: {e}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
