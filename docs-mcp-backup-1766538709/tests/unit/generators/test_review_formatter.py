#!/usr/bin/env python3
"""
Comprehensive tests for ReviewFormatter class (Tool #4).

Tests markdown report generation from validation results.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.review_formatter import ReviewFormatter
from type_defs import ValidationResultDict


# Test Fixtures
PERFECT_RESULT: ValidationResultDict = {
    'score': 100,
    'validation_result': 'PASS',
    'issues': [],
    'checklist_results': {
        'has_meta_documentation': True,
        'has_all_required_sections': True,
        'tasks_have_unique_ids': True,
        'tasks_have_dependencies': True,
        'dependencies_are_valid': True,
        'no_circular_dependencies': True,
        'has_acceptance_criteria': True,
        'has_effort_estimates': True,
        'descriptions_are_detailed': True,
        'has_success_criteria': True,
        'success_criteria_measurable': True,
        'has_rollback_plan': True,
        'security_considered': True,
        'performance_considered': True,
        'has_testing_strategy': True,
        'has_implementation_checklist': True,
        'no_placeholders': True,
        'no_ambiguous_language': True,
        'structure_is_valid': True,
        'dependencies_status_current': True,
        'effort_estimates_reasonable': True,
        'risk_assessment_complete': True,
        'examples_are_concrete': True,
        'task_breakdown_appropriate': True
    },
    'approved': True
}

FLAWED_RESULT: ValidationResultDict = {
    'score': 75,
    'validation_result': 'NEEDS_REVISION',
    'issues': [
        {
            'severity': 'critical',
            'section': 'structure',
            'issue': 'Missing required section: 7_testing_strategy',
            'suggestion': 'Add section 7_testing_strategy with unit_tests, integration_tests, and test_cases'
        },
        {
            'severity': 'critical',
            'section': 'dependencies',
            'issue': 'Circular dependency detected: TASK-001 → TASK-002 → TASK-001',
            'suggestion': 'Reorder tasks to remove circular dependency or split into phases'
        },
        {
            'severity': 'major',
            'section': 'completeness',
            'issue': 'Placeholder text found in task TASK-003: "TBD - to be determined"',
            'suggestion': 'Replace all placeholder text with concrete implementation details'
        },
        {
            'severity': 'major',
            'section': 'quality',
            'issue': 'Task TASK-005 description is too short (12 words)',
            'suggestion': 'Expand task description to at least 20 words with technical details'
        },
        {
            'severity': 'major',
            'section': 'success_criteria',
            'issue': 'Success criteria lack specific metrics',
            'suggestion': 'Make success criteria measurable (e.g., response time < 2s, coverage > 90%)'
        },
        {
            'severity': 'minor',
            'section': 'quality',
            'issue': 'Ambiguous language found: "Should probably implement caching?"',
            'suggestion': 'Remove questions and uncertain phrases; use definitive statements'
        },
        {
            'severity': 'minor',
            'section': 'quality',
            'issue': 'Task TASK-007 description is too short (15 words)',
            'suggestion': 'Expand description with implementation approach and technical details'
        }
    ],
    'checklist_results': {
        'has_meta_documentation': True,
        'has_all_required_sections': False,  # Missing testing_strategy
        'tasks_have_unique_ids': True,
        'tasks_have_dependencies': True,
        'dependencies_are_valid': False,  # Circular dependency
        'no_circular_dependencies': False,
        'has_acceptance_criteria': True,
        'has_effort_estimates': True,
        'descriptions_are_detailed': False,  # Short descriptions
        'has_success_criteria': True,
        'success_criteria_measurable': False,  # Vague criteria
        'has_rollback_plan': True,
        'security_considered': True,
        'performance_considered': True,
        'has_testing_strategy': False,
        'has_implementation_checklist': True,
        'no_placeholders': False,  # Has TBD
        'no_ambiguous_language': False,  # Has questions
        'structure_is_valid': True,
        'dependencies_status_current': True,
        'effort_estimates_reasonable': True,
        'risk_assessment_complete': True,
        'examples_are_concrete': True,
        'task_breakdown_appropriate': True
    },
    'approved': False
}

FAILED_RESULT: ValidationResultDict = {
    'score': 45,
    'validation_result': 'FAIL',
    'issues': [
        {
            'severity': 'critical',
            'section': 'structure',
            'issue': 'Missing required section: 0_preparation',
            'suggestion': 'Add section 0_preparation with foundation_docs, standards, patterns'
        },
        {
            'severity': 'critical',
            'section': 'structure',
            'issue': 'Missing required section: 6_implementation_phases',
            'suggestion': 'Add section 6_implementation_phases with task breakdown'
        },
        {
            'severity': 'critical',
            'section': 'structure',
            'issue': 'Missing required section: 7_testing_strategy',
            'suggestion': 'Add section 7_testing_strategy'
        },
        {
            'severity': 'critical',
            'section': 'structure',
            'issue': 'Missing required section: 8_success_criteria',
            'suggestion': 'Add section 8_success_criteria'
        },
        {
            'severity': 'critical',
            'section': 'dependencies',
            'issue': 'Multiple circular dependencies detected',
            'suggestion': 'Review all task dependencies and create valid DAG'
        },
        {
            'severity': 'major',
            'section': 'completeness',
            'issue': '15 instances of placeholder text (TBD/TODO/[placeholder])',
            'suggestion': 'Replace all placeholders with concrete details'
        },
        {
            'severity': 'major',
            'section': 'quality',
            'issue': '8 tasks have descriptions shorter than 20 words',
            'suggestion': 'Expand all task descriptions with technical details'
        }
    ],
    'checklist_results': {
        'has_meta_documentation': True,
        'has_all_required_sections': False,
        'tasks_have_unique_ids': True,
        'tasks_have_dependencies': False,
        'dependencies_are_valid': False,
        'no_circular_dependencies': False,
        'has_acceptance_criteria': False,
        'has_effort_estimates': False,
        'descriptions_are_detailed': False,
        'has_success_criteria': False,
        'success_criteria_measurable': False,
        'has_rollback_plan': False,
        'security_considered': False,
        'performance_considered': False,
        'has_testing_strategy': False,
        'has_implementation_checklist': False,
        'no_placeholders': False,
        'no_ambiguous_language': False,
        'structure_is_valid': False,
        'dependencies_status_current': True,
        'effort_estimates_reasonable': True,
        'risk_assessment_complete': False,
        'examples_are_concrete': False,
        'task_breakdown_appropriate': False
    },
    'approved': False
}


def test_format_report_perfect_plan():
    """Test report generation for perfect plan (score 100, no issues)."""
    print("\n" + "="*60)
    print("TEST: Perfect Plan Report")
    print("="*60)

    formatter = ReviewFormatter(PERFECT_RESULT, 'test-perfect-plan')
    report = formatter.format_report()

    # Verify header
    assert '# Implementation Plan Review Report' in report
    assert 'test-perfect-plan' in report
    assert '100/100 (A)' in report
    assert 'PASS ✅' in report
    assert 'Yes ✅' in report

    # Verify summary
    assert '## Summary' in report
    assert '**Critical Issues:** 0 🔴' in report
    assert '**Major Issues:** 0 🟡' in report
    assert '**Minor Issues:** 0 🟢' in report
    assert 'ready for implementation' in report

    # Verify no issue sections (should be filtered out)
    assert '## Critical Issues' not in report
    assert '## Major Issues' not in report
    assert '## Minor Issues' not in report

    # Verify no recommendations section (no issues = no recommendations)
    assert '## Recommendations' not in report

    # Verify approval status
    assert '## Approval Status ✅' in report
    assert 'APPROVED FOR IMPLEMENTATION' in report

    print("[PASS] Perfect plan report validated")
    print(f"Report length: {len(report)} characters")
    return report


def test_format_report_flawed_plan():
    """Test report generation for flawed plan (score 75, mixed issues)."""
    print("\n" + "="*60)
    print("TEST: Flawed Plan Report")
    print("="*60)

    formatter = ReviewFormatter(FLAWED_RESULT, 'test-flawed-plan')
    report = formatter.format_report()

    # Verify header
    assert '# Implementation Plan Review Report' in report
    assert 'test-flawed-plan' in report
    assert '75/100 (C)' in report
    assert 'NEEDS_REVISION 🔄' in report
    assert 'No ❌' in report

    # Verify summary
    assert '## Summary' in report
    assert '**Critical Issues:** 2 🔴' in report
    assert '**Major Issues:** 3 🟡' in report
    assert '**Minor Issues:** 2 🟢' in report
    assert 'requires revisions' in report

    # Verify issue sections are present
    assert '## Critical Issues 🔴' in report
    assert '## Major Issues 🟡' in report
    assert '## Minor Issues 🟢' in report

    # Verify specific issues
    assert 'Missing required section: 7_testing_strategy' in report
    assert 'Circular dependency detected' in report
    assert 'Placeholder text found' in report

    # Verify recommendations section
    assert '## Recommendations' in report
    assert 'PRIORITY: Fix all 2 critical issues first' in report

    # Verify approval status
    assert '## Approval Status ❌' in report
    assert 'NOT APPROVED - REVISIONS REQUIRED' in report
    assert '**Gap:** 15 points' in report

    print("[PASS] Flawed plan report validated")
    print(f"Report length: {len(report)} characters")
    return report


def test_format_report_failed_plan():
    """Test report generation for failed plan (score 45, many critical issues)."""
    print("\n" + "="*60)
    print("TEST: Failed Plan Report")
    print("="*60)

    formatter = ReviewFormatter(FAILED_RESULT, 'test-failed-plan')
    report = formatter.format_report()

    # Verify header
    assert '# Implementation Plan Review Report' in report
    assert 'test-failed-plan' in report
    assert '45/100 (F)' in report
    assert 'FAIL ❌' in report
    assert 'No ❌' in report

    # Verify summary
    assert '## Summary' in report
    assert '**Critical Issues:** 5 🔴' in report
    assert '**Major Issues:** 2 🟡' in report
    assert 'significant quality issues' in report

    # Verify critical section is prominent
    assert '## Critical Issues 🔴' in report
    assert 'Missing required section: 0_preparation' in report
    assert 'Missing required section: 6_implementation_phases' in report

    # Verify recommendations prioritize critical issues
    assert '## Recommendations' in report
    assert 'PRIORITY: Fix all 5 critical issues first - these are blockers' in report

    # Verify approval status shows large gap
    assert '## Approval Status ❌' in report
    assert '**Gap:** 45 points' in report

    print("[PASS] Failed plan report validated")
    print(f"Report length: {len(report)} characters")
    return report


def test_score_to_grade_mapping():
    """Test score-to-grade mapping for all grade boundaries."""
    print("\n" + "="*60)
    print("TEST: Score-to-Grade Mapping")
    print("="*60)

    test_cases = [
        (100, 'A'), (95, 'A'), (90, 'A'),
        (89, 'B'), (87, 'B'), (85, 'B'),
        (84, 'C'), (75, 'C'), (70, 'C'),
        (69, 'D'), (65, 'D'), (60, 'D'),
        (59, 'F'), (45, 'F'), (0, 'F')
    ]

    for score, expected_grade in test_cases:
        result: ValidationResultDict = {
            'score': score,
            'validation_result': 'PASS',
            'issues': [],
            'checklist_results': {},
            'approved': True
        }
        formatter = ReviewFormatter(result, 'test-plan')
        report = formatter.format_report()

        assert f'{score}/100 ({expected_grade})' in report, f"Score {score} should map to grade {expected_grade}"
        print(f"  [OK] Score {score:3d} -> Grade {expected_grade}")

    print("[PASS] All score-to-grade mappings validated")


def test_result_to_emoji_mapping():
    """Test validation result to emoji mapping."""
    print("\n" + "="*60)
    print("TEST: Result-to-Emoji Mapping")
    print("="*60)

    test_cases = [
        ('PASS', '✅', 100),
        ('PASS_WITH_WARNINGS', '⚠️', 87),
        ('NEEDS_REVISION', '🔄', 75),
        ('FAIL', '❌', 45)
    ]

    for result_type, expected_emoji, score in test_cases:
        result: ValidationResultDict = {
            'score': score,
            'validation_result': result_type,
            'issues': [],
            'checklist_results': {},
            'approved': score >= 90
        }
        formatter = ReviewFormatter(result, 'test-plan')
        report = formatter.format_report()

        assert f'{result_type} {expected_emoji}' in report, f"Result {result_type} should have emoji {expected_emoji}"
        print(f"  [OK] {result_type:20s} -> emoji present")

    print("[PASS] All result-to-emoji mappings validated")


def test_recommendations_generation():
    """Test pattern-based recommendations generation."""
    print("\n" + "="*60)
    print("TEST: Recommendations Generation")
    print("="*60)

    formatter = ReviewFormatter(FLAWED_RESULT, 'test-plan')
    report = formatter.format_report()

    # Verify recommendations section exists
    assert '## Recommendations' in report

    # Verify critical issue priority
    assert 'PRIORITY: Fix all 2 critical issues first' in report

    # Verify pattern detection
    assert 'missing' in report.lower() or 'complete' in report.lower()  # Missing sections pattern
    assert 'placeholder' in report.lower() or 'replace' in report.lower()  # Placeholder pattern
    assert 'circular' in report.lower() or 'dependencies' in report.lower()  # Circular deps pattern

    # Verify numbered list format
    assert '1.' in report
    assert '2.' in report

    print("[PASS] Recommendations generation validated")

    # Test no recommendations for perfect plan
    formatter_perfect = ReviewFormatter(PERFECT_RESULT, 'test-plan')
    report_perfect = formatter_perfect.format_report()
    assert '## Recommendations' not in report_perfect
    print("[PASS] No recommendations for perfect plan - validated")


def test_approval_status_formatting():
    """Test approval status section formatting."""
    print("\n" + "="*60)
    print("TEST: Approval Status Formatting")
    print("="*60)

    # Test approved status
    formatter_approved = ReviewFormatter(PERFECT_RESULT, 'test-plan')
    report_approved = formatter_approved.format_report()
    assert '## Approval Status ✅' in report_approved
    assert 'APPROVED FOR IMPLEMENTATION' in report_approved
    assert 'score of 100/100' in report_approved
    print("  [OK] Approved status formatted correctly")

    # Test not approved status
    formatter_not_approved = ReviewFormatter(FLAWED_RESULT, 'test-plan')
    report_not_approved = formatter_not_approved.format_report()
    assert '## Approval Status ❌' in report_not_approved
    assert 'NOT APPROVED - REVISIONS REQUIRED' in report_not_approved
    assert '**Current Score:** 75/100' in report_not_approved
    assert '**Approval Threshold:** 90/100' in report_not_approved
    assert '**Gap:** 15 points' in report_not_approved
    print("  [OK] Not approved status formatted correctly")

    # Test with large gap
    formatter_failed = ReviewFormatter(FAILED_RESULT, 'test-plan')
    report_failed = formatter_failed.format_report()
    assert '**Gap:** 45 points' in report_failed
    print("  [OK] Large gap (45 points) formatted correctly")

    print("[PASS] Approval status formatting validated")


def test_issue_grouping_by_severity():
    """Test that issues are correctly grouped by severity."""
    print("\n" + "="*60)
    print("TEST: Issue Grouping by Severity")
    print("="*60)

    formatter = ReviewFormatter(FLAWED_RESULT, 'test-plan')

    # Test critical issues section
    critical_section = formatter._format_issues_by_severity('critical')
    assert critical_section is not None
    assert '## Critical Issues 🔴' in critical_section
    assert 'Missing required section: 7_testing_strategy' in critical_section
    assert 'Circular dependency detected' in critical_section
    # Should NOT contain major or minor issues
    assert 'Placeholder text found' not in critical_section
    assert 'Ambiguous language' not in critical_section
    print("  [OK] Critical issues section contains only critical issues")

    # Test major issues section
    major_section = formatter._format_issues_by_severity('major')
    assert major_section is not None
    assert '## Major Issues 🟡' in major_section
    assert 'Placeholder text found' in major_section
    assert 'description is too short (12 words)' in major_section
    # Should NOT contain critical or minor issues
    assert 'Circular dependency' not in major_section
    assert 'Ambiguous language found' not in major_section
    print("  [OK] Major issues section contains only major issues")

    # Test minor issues section
    minor_section = formatter._format_issues_by_severity('minor')
    assert minor_section is not None
    assert '## Minor Issues 🟢' in minor_section
    assert 'Ambiguous language found' in minor_section
    # Should NOT contain critical or major issues
    assert 'Circular dependency' not in minor_section
    assert 'Placeholder text found' not in minor_section
    print("  [OK] Minor issues section contains only minor issues")

    # Test empty severity returns None
    formatter_perfect = ReviewFormatter(PERFECT_RESULT, 'test-plan')
    assert formatter_perfect._format_issues_by_severity('critical') is None
    assert formatter_perfect._format_issues_by_severity('major') is None
    assert formatter_perfect._format_issues_by_severity('minor') is None
    print("  [OK] Empty severity levels return None (correctly filtered)")

    print("[PASS] Issue grouping by severity validated")


def test_markdown_structure():
    """Test that generated markdown has valid structure."""
    print("\n" + "="*60)
    print("TEST: Markdown Structure")
    print("="*60)

    formatter = ReviewFormatter(FLAWED_RESULT, 'test-plan')
    report = formatter.format_report()

    # Verify heading hierarchy
    assert report.count('# Implementation Plan Review Report') == 1
    assert '##' in report  # Has second-level headings
    assert '###' in report  # Has third-level headings (issue items)
    print("  [OK] Heading hierarchy valid (# -> ## -> ###)")

    # Verify sections separated by horizontal rules
    assert '\n\n---\n\n' in report
    print("  [OK] Sections separated by horizontal rules (---)")

    # Verify bold labels
    assert '**Plan:**' in report
    assert '**Score:**' in report
    assert '**Issue:**' in report
    assert '**Suggestion:**' in report
    print("  [OK] Bold labels present (**label:**)")

    # Verify emoji usage
    assert '✅' in report or '❌' in report  # Approval emoji
    assert '🔴' in report  # Critical emoji
    assert '🟡' in report  # Major emoji
    print("  [OK] Emoji indicators used")

    # Verify no broken markdown (basic check)
    assert report.count('**') % 2 == 0  # Bold markers balanced
    print("  [OK] Bold markers balanced")

    print("[PASS] Markdown structure validated")


def run_all_tests():
    """Run all ReviewFormatter tests."""
    print("\n" + "="*60)
    print("REVIEW FORMATTER TEST SUITE")
    print("="*60)

    try:
        # Test complete workflows
        test_format_report_perfect_plan()
        test_format_report_flawed_plan()
        test_format_report_failed_plan()

        # Test specific mappings
        test_score_to_grade_mapping()
        test_result_to_emoji_mapping()

        # Test feature-specific functionality
        test_recommendations_generation()
        test_approval_status_formatting()
        test_issue_grouping_by_severity()

        # Test markdown structure
        test_markdown_structure()

        print("\n" + "="*60)
        print("[PASS] ALL TESTS PASSED")
        print("="*60)
        print("\nTest Coverage:")
        print("  [OK] Perfect plan reports (score 100, no issues)")
        print("  [OK] Flawed plan reports (score 75, mixed issues)")
        print("  [OK] Failed plan reports (score 45, many critical issues)")
        print("  [OK] Score-to-grade mapping (A-F)")
        print("  [OK] Result-to-emoji mapping (PASS/WARN/REVISE/FAIL)")
        print("  [OK] Recommendations generation (pattern-based)")
        print("  [OK] Approval status formatting (approved/not approved)")
        print("  [OK] Issue grouping by severity (critical/major/minor)")
        print("  [OK] Markdown structure validation")
        print("\nTotal: 9 test functions, all passing [PASS]")

        return True

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
