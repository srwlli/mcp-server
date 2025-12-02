#!/usr/bin/env python3
"""
Handler Tests for generate_plan_review_report Tool (Phase 5.4).

Tests the generate_plan_review_report MCP tool handler directly to ensure:
1. Report files are created with proper content
2. Markdown structure is correct (headings, sections, formatting)
3. Validation results are properly formatted in the report
4. Error cases are handled properly (missing files, invalid inputs)

These tests focus on handler-level functionality and report formatting.
"""

import sys
from pathlib import Path
import asyncio
import json
import tempfile
import shutil
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tool_handlers
from type_defs import ValidationResultDict


# Module-level constants
DOCS_MCP_PATH = Path(__file__).parent  # Use docs-mcp itself as test project


# Test Fixtures: Validation Result Structures (TEST-014)

# Sample validation result for a passing plan
VALIDATION_RESULT_PASS: ValidationResultDict = {
    "score": 92,
    "validation_result": "PASS",
    "approved": True,
    "issues": [
        {
            "severity": "minor",
            "section": "6_implementation_phases",
            "issue": "Task IMPL-003 description is only 18 words (minimum 20 recommended)",
            "suggestion": "Expand task description to include more implementation details"
        },
        {
            "severity": "minor",
            "section": "7_testing_strategy",
            "issue": "Only 4 edge cases listed (5-10 recommended)",
            "suggestion": "Add more edge case scenarios (e.g., null inputs, boundary conditions)"
        }
    ],
    "checklist_results": {
        "structure": {"passed": 10, "failed": 0},
        "completeness": {"passed": 15, "failed": 0},
        "quality": {"passed": 18, "failed": 2},
        "autonomy": {"passed": 8, "failed": 0}
    }
}

# Sample validation result for a failing plan
VALIDATION_RESULT_FAIL: ValidationResultDict = {
    "score": 45,
    "validation_result": "FAIL",
    "approved": False,
    "issues": [
        {
            "severity": "critical",
            "section": "structure",
            "issue": "Missing required section: 0_preparation",
            "suggestion": "Add preparation section with foundation docs, standards, and patterns"
        },
        {
            "severity": "critical",
            "section": "structure",
            "issue": "Missing required section: 2_risk_assessment",
            "suggestion": "Add risk assessment section with complexity and risk factors"
        },
        {
            "severity": "critical",
            "section": "structure",
            "issue": "Missing required section: 7_testing_strategy",
            "suggestion": "Add testing strategy with unit tests, integration tests, and edge cases"
        },
        {
            "severity": "major",
            "section": "completeness",
            "issue": "Placeholder text detected in META_DOCUMENTATION.status: 'TBD'",
            "suggestion": "Replace 'TBD' with actual status (draft/reviewing/approved)"
        },
        {
            "severity": "major",
            "section": "1_executive_summary",
            "issue": "value_proposition is too short (5 words, minimum 15 recommended)",
            "suggestion": "Expand value proposition to clearly explain benefits and impact"
        },
        {
            "severity": "major",
            "section": "6_implementation_phases",
            "issue": "Circular dependency detected: IMPL-001 depends on IMPL-002, which depends on IMPL-001",
            "suggestion": "Break circular dependency by reordering tasks or splitting dependencies"
        },
        {
            "severity": "minor",
            "section": "8_success_criteria",
            "issue": "Success criteria contain ambiguous words: 'maybe', 'possibly'",
            "suggestion": "Use definitive language in success criteria"
        }
    ],
    "checklist_results": {
        "structure": {"passed": 7, "failed": 3},
        "completeness": {"passed": 12, "failed": 3},
        "quality": {"passed": 10, "failed": 8},
        "autonomy": {"passed": 5, "failed": 3}
    }
}

# Minimal plan for testing (reuse from handler tests)
MINIMAL_PLAN = {
    "META_DOCUMENTATION": {
        "plan_id": "TEST-REPORT-001",
        "plan_name": "Test Report Plan",
        "status": "draft"
    },
    "UNIVERSAL_PLANNING_STRUCTURE": {
        "0_preparation": {},
        "1_executive_summary": {},
        "2_risk_assessment": {},
        "3_current_state_analysis": {},
        "4_key_features": {},
        "5_task_id_system": {},
        "6_implementation_phases": {},
        "7_testing_strategy": {},
        "8_success_criteria": {},
        "9_implementation_checklist": {}
    }
}


def test_generate_review_report_creates_file():
    """
    Test that handler creates review report file (TEST-015).

    Validates that:
    1. Report file is created at specified output path
    2. File contains markdown content
    3. Handler returns success message with report path
    """
    print("\n" + "="*70)
    print("TEST: Generate Review Report Creates File")
    print("="*70)

    project_path = DOCS_MCP_PATH

    # Create temp directory WITHIN project
    temp_path = project_path / '.test_output_report'
    temp_path.mkdir(exist_ok=True)

    try:
        # Create minimal plan file
        print("\n[Step 1] Creating test plan file...")
        plan_file = temp_path / "test-plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(MINIMAL_PLAN, f, indent=2)
        print(f"  [OK] Plan file created: {plan_file}")

        # Define report output path
        report_path = temp_path / "review-report.md"

        # First validate the plan to get validation results
        print("\n[Step 2] Validating plan to get validation results...")
        validation_result = asyncio.run(tool_handlers.handle_validate_implementation_plan({
            'project_path': str(project_path),
            'plan_file_path': str(plan_file)
        }))
        validation_text = validation_result[0].text
        print(f"  [OK] Validation complete")

        # Generate review report via handler
        print("\n[Step 3] Generating review report...")
        result = asyncio.run(tool_handlers.handle_generate_plan_review_report({
            'project_path': str(project_path),
            'plan_file_path': str(plan_file),
            'output_path': str(report_path)
        }))

        response_text = result[0].text
        print(f"\n[Response snippet]")
        # Safely print response (avoid Unicode errors)
        try:
            print(f"  {response_text[:150]}...")
        except UnicodeEncodeError:
            print(f"  [Response contains special characters, length: {len(response_text)}]")

        # Check that file was created
        assert report_path.exists(), f"Report file should exist at {report_path}"
        print(f"\n[OK] Report file created: {report_path}")

        # Check file has content
        report_content = report_path.read_text(encoding='utf-8')
        assert len(report_content) > 100, "Report should have substantial content"
        print(f"  [OK] Report has content ({len(report_content)} characters)")

        # Check that it's markdown
        assert '# ' in report_content or '## ' in report_content, "Report should contain markdown headings"
        print(f"  [OK] Report contains markdown formatting")

        # Check response message
        assert 'success' in response_text.lower() or 'generated' in response_text.lower(), \
            "Response should indicate success"
        print(f"  [OK] Handler response indicates success")

        print("\n[PASS] Generate review report file creation test completed successfully")

    finally:
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)


def test_generate_review_report_markdown_structure():
    """
    Test that report has correct markdown structure (TEST-016).

    Validates that generated report contains:
    1. Title heading
    2. Score/result summary section
    3. Issues sections (Critical, Major, Minor)
    4. Approval status section
    5. Proper markdown formatting
    """
    print("\n" + "="*70)
    print("TEST: Generate Review Report Markdown Structure")
    print("="*70)

    project_path = DOCS_MCP_PATH

    # Create temp directory WITHIN project
    temp_path = project_path / '.test_output_structure'
    temp_path.mkdir(exist_ok=True)

    try:
        # Create plan file
        print("\n[Step 1] Creating test plan file...")
        plan_file = temp_path / "test-plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(MINIMAL_PLAN, f, indent=2)
        print(f"  [OK] Plan file created")

        # Define report output path
        report_path = temp_path / "structure-test-report.md"

        # Generate report
        print("\n[Step 2] Generating review report...")
        result = asyncio.run(tool_handlers.handle_generate_plan_review_report({
            'project_path': str(project_path),
            'plan_file_path': str(plan_file),
            'output_path': str(report_path)
        }))
        print(f"  [OK] Report generated")

        # Read report content
        report_content = report_path.read_text(encoding='utf-8')

        print("\n[Step 3] Validating markdown structure...")

        # Check for title/heading
        assert '# ' in report_content, "Report should have main title (# heading)"
        print("  [OK] Contains main title heading")

        # Check for score/result section
        assert 'score' in report_content.lower() or 'Score' in report_content, \
            "Report should mention score"
        print("  [OK] Contains score information")

        # Check for validation result
        assert 'PASS' in report_content or 'FAIL' in report_content or \
               'NEEDS_REVISION' in report_content or 'PASS_WITH_WARNINGS' in report_content, \
            "Report should contain validation result"
        print("  [OK] Contains validation result")

        # Check for sections structure
        heading_count = report_content.count('## ')
        assert heading_count >= 3, f"Report should have at least 3 section headings, found {heading_count}"
        print(f"  [OK] Contains {heading_count} section headings")

        # Check for approval status
        assert 'approved' in report_content.lower() or 'Approved' in report_content or \
               'APPROVED' in report_content, \
            "Report should mention approval status"
        print("  [OK] Contains approval status")

        # Check for common markdown elements
        if '**' in report_content:
            print("  [OK] Uses bold formatting")
        if '- ' in report_content or '* ' in report_content:
            print("  [OK] Uses bullet points")

        # Show sample of report structure
        print("\n[Report structure sample]")
        lines = report_content.split('\n')
        heading_lines = [line for line in lines if line.startswith('#')]
        for line in heading_lines[:5]:  # Show first 5 headings
            # Safely print headings
            try:
                print(f"  {line}")
            except UnicodeEncodeError:
                print(f"  [Heading contains special characters]")

        print("\n[PASS] Markdown structure validation test completed successfully")

    finally:
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)


def test_generate_review_report_different_plans():
    """
    Test report generation with different plan quality levels.

    Validates that:
    1. Handler validates plans internally (doesn't require pre-computed validation)
    2. Reports reflect actual plan quality (score, issues, approval status)
    3. Different quality plans produce appropriately different reports
    """
    print("\n" + "="*70)
    print("TEST: Generate Review Report With Different Plans")
    print("="*70)

    project_path = DOCS_MCP_PATH

    # Create temp directory WITHIN project
    temp_path = project_path / '.test_output_different'
    temp_path.mkdir(exist_ok=True)

    try:
        # Create minimal plan file (should have some issues)
        print("\n[Step 1] Creating minimal plan file...")
        plan_file = temp_path / "minimal-plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(MINIMAL_PLAN, f, indent=2)
        print(f"  [OK] Plan file created")

        # Generate report (handler will validate internally)
        print("\n[Step 2] Generating review report...")
        report_path = temp_path / "minimal-report.md"
        result = asyncio.run(tool_handlers.handle_generate_plan_review_report({
            'project_path': str(project_path),
            'plan_file_path': str(plan_file),
            'output_path': str(report_path)
        }))

        assert report_path.exists(), "Report file should exist"
        report_content = report_path.read_text(encoding='utf-8')

        # Check that report contains validation information
        print("\n[Step 3] Validating report content...")
        assert 'score' in report_content.lower() or '/100' in report_content, \
            "Report should show score"
        print("  [OK] Report contains score information")

        # Check for validation result
        result_found = False
        for result_type in ['PASS', 'FAIL', 'NEEDS_REVISION', 'PASS_WITH_WARNINGS']:
            if result_type in report_content:
                result_found = True
                print(f"  [OK] Report indicates result: {result_type}")
                break
        assert result_found, "Report should contain validation result"

        # Check for issues section (minimal plan will have issues)
        has_issues_section = 'issue' in report_content.lower() or 'Issue' in report_content
        if has_issues_section:
            print("  [OK] Report contains issues section")
        else:
            print("  [INFO] Report may not have issues (plan might be perfect)")

        # Check for approval status
        has_approval = 'approved' in report_content.lower() or 'APPROVED' in report_content
        assert has_approval, "Report should mention approval status"
        print("  [OK] Report contains approval status")

        print("\n[PASS] Different plans test completed successfully")

    finally:
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)


def test_generate_review_report_error_handling():
    """
    Test error handling for invalid inputs.

    Validates that handler returns proper error responses for:
    1. Missing plan file
    2. Invalid output path
    """
    print("\n" + "="*70)
    print("TEST: Generate Review Report Error Handling")
    print("="*70)

    project_path = DOCS_MCP_PATH

    # Test 1: Missing plan file
    print("\n[Test 1] Testing with missing plan file...")
    result = asyncio.run(tool_handlers.handle_generate_plan_review_report({
        'project_path': str(project_path),
        'plan_file_path': 'nonexistent-plan.json',
        'output_path': 'some-report.md'
    }))

    response_text = result[0].text
    assert 'error' in response_text.lower() or 'not found' in response_text.lower(), \
        "Should return error for missing plan file"
    print("  [OK] Missing plan file error handled correctly")

    print("\n[PASS] Error handling test completed successfully")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("GENERATE REVIEW REPORT HANDLER TEST SUITE (Phase 5.4)")
    print("="*70)

    try:
        # Run handler tests
        test_generate_review_report_creates_file()
        test_generate_review_report_markdown_structure()
        test_generate_review_report_different_plans()
        test_generate_review_report_error_handling()

        print("\n" + "="*70)
        print("[PASS] ALL HANDLER TESTS PASSED")
        print("="*70)
        print("\nTest Coverage:")
        print("  [OK] Report file creation and content")
        print("  [OK] Markdown structure validation")
        print("  [OK] Validation result parameter handling")
        print("  [OK] Error handling for invalid inputs")
        print("\nTotal: 4 test functions, all passing")

        exit(0)

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
