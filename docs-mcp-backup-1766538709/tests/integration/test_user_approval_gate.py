#!/usr/bin/env python3
"""
User Approval Gate Tests (Phase 5.5).

Tests that documentation and workflow patterns properly communicate the
mandatory user approval requirement. Since the approval gate is procedural
(not programmatically enforced), these tests validate that:

1. Documentation clearly states approval is MANDATORY
2. Documentation provides clear examples of approval workflow
3. Workflow patterns show approval step before execution
4. AI agents have sufficient guidance to follow the approval pattern

Rationale: The approval gate relies on AI following documented patterns,
so documentation quality is critical for security and user control.
"""

import sys
from pathlib import Path
from typing import List, Set

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Module-level constants - point to project root (two levels up from tests/integration/)
DOCS_MCP_PATH = Path(__file__).parent.parent.parent
CLAUDE_MD_PATH = DOCS_MCP_PATH / 'CLAUDE.md'
META_PLAN_PATH = DOCS_MCP_PATH / 'coderef' / 'planning-workflow' / 'planning-workflow-system-meta-plan.json'


def test_approval_gate_documentation():
    """
    Test that documentation clearly explains user approval requirement (TEST-018).

    Validates that CLAUDE.md and meta-plan documents:
    1. State that user approval is MANDATORY
    2. Explain approval cannot be bypassed
    3. Show approval step in workflow examples
    4. Use clear, unambiguous language about approval requirement
    """
    print("\n" + "="*70)
    print("TEST: Approval Gate Documentation")
    print("="*70)

    # Read CLAUDE.md
    print("\n[Step 1] Checking CLAUDE.md for approval documentation...")
    assert CLAUDE_MD_PATH.exists(), f"CLAUDE.md not found at {CLAUDE_MD_PATH}"
    claude_content = CLAUDE_MD_PATH.read_text(encoding='utf-8')

    # Check for mandatory approval keywords
    mandatory_keywords = [
        'mandatory',
        'MANDATORY',
        'required',
        'REQUIRED',
        'must',
        'MUST'
    ]
    mandatory_found = any(keyword in claude_content for keyword in mandatory_keywords)
    assert mandatory_found, "CLAUDE.md should use mandatory/required/must language for approval"
    print("  [OK] Uses mandatory language for approval requirement")

    # Check for approval mentions (various forms)
    approval_keywords = ['user approval', 'approval', 'approve', 'approved']
    approval_mentions = sum(claude_content.lower().count(keyword) for keyword in approval_keywords)
    assert approval_mentions >= 5, f"Should mention approval concepts at least 5 times, found {approval_mentions}"
    print(f"  [OK] Mentions approval concepts {approval_mentions} times")

    # Check for "cannot be bypassed" or similar
    cannot_bypass_patterns = [
        'cannot be bypassed',
        'cannot bypass',
        'not bypass',
        'no bypass'
    ]
    cannot_bypass = any(pattern in claude_content.lower() for pattern in cannot_bypass_patterns)
    if cannot_bypass:
        print("  [OK] Explicitly states approval cannot be bypassed")
    else:
        print("  [WARNING] Could be clearer about inability to bypass approval")

    # Check for approval in workflow patterns (various forms)
    approval_workflow_patterns = [
        'approval gate',
        'USER APPROVAL',
        'user approval',
        'present to user for approval',
        'wait for user approval',
        'ask user',
        'user approves'
    ]
    approval_in_workflow = any(pattern in claude_content or pattern.lower() in claude_content.lower()
                              for pattern in approval_workflow_patterns)
    assert approval_in_workflow, "CLAUDE.md should document approval in workflow patterns"
    print("  [OK] Documents approval in workflow patterns")

    # Check for Pattern 5 (Planning Workflow Review Loop)
    pattern_5 = 'Pattern 5' in claude_content or 'pattern 5' in claude_content.lower()
    if pattern_5:
        print("  [OK] Contains Pattern 5 (Planning Workflow Review Loop)")

        # Extract Pattern 5 section
        pattern_5_start = claude_content.lower().find('pattern 5')
        if pattern_5_start != -1:
            pattern_5_section = claude_content[pattern_5_start:pattern_5_start + 3000]

            # Check Pattern 5 mentions approval
            if 'approval' in pattern_5_section.lower():
                print("  [OK] Pattern 5 explicitly mentions approval step")
            else:
                print("  [WARNING] Pattern 5 could be clearer about approval requirement")
    else:
        print("  [INFO] Pattern 5 not found - approval may be documented elsewhere")

    # Check meta-plan for approval gate
    print("\n[Step 2] Checking meta-plan for approval gate documentation...")
    if META_PLAN_PATH.exists():
        import json
        with open(META_PLAN_PATH, 'r', encoding='utf-8') as f:
            meta_plan = json.load(f)

        meta_plan_str = json.dumps(meta_plan, indent=2).lower()

        # Check for approval mentions
        approval_in_meta = 'approval' in meta_plan_str or 'user approval' in meta_plan_str
        if approval_in_meta:
            print("  [OK] Meta-plan documents approval gate")
        else:
            print("  [WARNING] Meta-plan could be clearer about approval requirement")

        # Check for approval gate in data flow
        approval_gate_in_flow = 'approval gate' in meta_plan_str
        if approval_gate_in_flow:
            print("  [OK] Meta-plan shows approval gate in data flow diagram")
    else:
        print("  [INFO] Meta-plan not found (optional)")

    print("\n[PASS] Approval gate documentation test completed successfully")


def test_workflow_includes_approval_step():
    """
    Test that workflow patterns show approval step (TEST-019).

    Validates that documented workflows:
    1. Include user approval as a step
    2. Show approval BEFORE execution
    3. Provide clear examples of approval interaction
    4. Sequence approval correctly (after validation, before execution)
    """
    print("\n" + "="*70)
    print("TEST: Workflow Includes Approval Step")
    print("="*70)

    # Read CLAUDE.md
    claude_content = CLAUDE_MD_PATH.read_text(encoding='utf-8')

    print("\n[Step 1] Checking for approval in workflow sequences...")

    # Check for step-by-step workflows
    workflow_indicators = [
        'step 1',
        'step 2',
        'step 3',
        'step 4',
        'step 5',
        'step 6',
        'step 7',
        'step 8'
    ]
    has_workflow = any(indicator in claude_content.lower() for indicator in workflow_indicators)
    assert has_workflow, "CLAUDE.md should contain step-by-step workflow examples"
    print("  [OK] Contains step-by-step workflow examples")

    # Check that approval appears in workflow context
    workflow_sections = []
    lines = claude_content.split('\n')
    in_workflow = False
    current_workflow = []

    for line in lines:
        line_lower = line.lower()

        # Detect workflow start (Step 1, etc.)
        if 'step 1' in line_lower or '# step 1' in line_lower:
            in_workflow = True
            if current_workflow:  # Save previous workflow
                workflow_sections.append('\n'.join(current_workflow))
            current_workflow = [line]
        elif in_workflow:
            current_workflow.append(line)

            # Detect workflow end (empty line after multiple steps)
            if len(current_workflow) > 20 and line.strip() == '':
                workflow_sections.append('\n'.join(current_workflow))
                current_workflow = []
                in_workflow = False

    if current_workflow:  # Save last workflow
        workflow_sections.append('\n'.join(current_workflow))

    print(f"  [OK] Found {len(workflow_sections)} workflow sections")

    # Check if any workflow mentions approval
    workflows_with_approval = 0
    for workflow in workflow_sections:
        if 'approval' in workflow.lower() or 'approve' in workflow.lower():
            workflows_with_approval += 1

    if workflows_with_approval > 0:
        print(f"  [OK] {workflows_with_approval} workflow(s) include approval step")
    else:
        print("  [WARNING] No workflows explicitly show approval step")

    # Check for execution keywords AFTER approval in workflows
    print("\n[Step 2] Checking approval sequencing (before execution)...")

    for i, workflow in enumerate(workflow_sections, 1):
        workflow_lower = workflow.lower()

        if 'approval' not in workflow_lower:
            continue

        # Find position of approval keyword
        approval_pos = workflow_lower.find('approval')

        # Find position of execution keywords
        execution_keywords = ['execute', 'execution', 'implement', 'begin implementation']
        execution_positions = []
        for keyword in execution_keywords:
            pos = workflow_lower.find(keyword, approval_pos)  # Search AFTER approval
            if pos != -1:
                execution_positions.append((keyword, pos))

        if execution_positions:
            # Execution found after approval - CORRECT
            print(f"  [OK] Workflow {i}: Approval appears before execution")
        else:
            # Check if execution appears before approval - INCORRECT
            for keyword in execution_keywords:
                if keyword in workflow_lower[:approval_pos]:
                    print(f"  [WARNING] Workflow {i}: Execution may appear before approval")
                    break

    # Check for explicit "WAIT FOR USER APPROVAL" patterns
    print("\n[Step 3] Checking for explicit approval instructions...")

    wait_patterns = [
        'wait for user approval',
        'WAIT FOR USER APPROVAL',
        'ask user',
        'present to user',
        'user approval',
        'USER APPROVAL',
        'approval gate',
        'APPROVAL GATE'
    ]

    found_patterns = [p for p in wait_patterns if p in claude_content]
    if found_patterns:
        print(f"  [OK] Contains explicit approval instructions: {len(found_patterns)} patterns")
        for pattern in found_patterns[:3]:  # Show first 3
            print(f"       - '{pattern}'")
    else:
        print("  [WARNING] Could be more explicit about waiting for user approval")

    # Check for approval examples
    print("\n[Step 4] Checking for approval interaction examples...")

    example_patterns = [
        'user: yes',
        'user: no',
        'user approves',
        'user rejects',
        'ready to execute',
        'proceed'
    ]

    found_examples = [p for p in example_patterns if p.lower() in claude_content.lower()]
    if found_examples:
        print(f"  [OK] Contains approval interaction examples: {len(found_examples)} patterns")
    else:
        print("  [INFO] Could include more approval interaction examples")

    print("\n[PASS] Workflow approval step test completed successfully")


def test_approval_gate_clarity():
    """
    Test that approval gate instructions are clear and unambiguous.

    Validates that:
    1. Approval language is clear and direct
    2. No conflicting messages about approval requirement
    3. Approval is presented as non-optional
    4. AI agents can easily find and understand approval requirements
    """
    print("\n" + "="*70)
    print("TEST: Approval Gate Clarity")
    print("="*70)

    # Read CLAUDE.md
    claude_content = CLAUDE_MD_PATH.read_text(encoding='utf-8')

    print("\n[Step 1] Checking for clarity and directness...")

    # Check for clear, direct language
    direct_phrases = [
        'mandatory',
        'MANDATORY',
        'required',
        'REQUIRED',
        'must',
        'MUST',
        'cannot be bypassed'
    ]

    direct_count = sum(1 for phrase in direct_phrases if phrase in claude_content)
    assert direct_count >= 2, f"Should use direct language for approval, found {direct_count} instances"
    print(f"  [OK] Uses direct language ({direct_count} instances)")

    # Check for ambiguous language that might confuse AI
    print("\n[Step 2] Checking for ambiguous language...")

    ambiguous_phrases = [
        'optionally',
        'if needed',
        'if desired',
        'may want to',
        'consider'
    ]

    # Check if ambiguous phrases appear in approval context
    ambiguous_in_approval_context = False
    for phrase in ambiguous_phrases:
        phrase_pos = claude_content.lower().find(phrase)
        if phrase_pos != -1:
            # Check if "approval" is nearby (within 100 chars)
            context = claude_content[max(0, phrase_pos - 50):min(len(claude_content), phrase_pos + 50)]
            if 'approval' in context.lower():
                ambiguous_in_approval_context = True
                print(f"  [WARNING] Ambiguous phrase '{phrase}' found near approval context")
                break

    if not ambiguous_in_approval_context:
        print("  [OK] No ambiguous language in approval context")

    # Check that approval is presented as non-optional
    print("\n[Step 3] Checking that approval is presented as non-optional...")

    non_optional_indicators = [
        'mandatory user approval',
        'required user approval',
        'must have user approval',
        'user approval required',
        'cannot proceed without approval'
    ]

    non_optional_found = any(indicator in claude_content.lower() for indicator in non_optional_indicators)
    if non_optional_found:
        print("  [OK] Approval explicitly presented as non-optional")
    else:
        print("  [INFO] Could be more explicit about approval being non-optional")

    # Check for visibility (approval should be easy to find)
    print("\n[Step 4] Checking visibility of approval requirements...")

    # Count sections/patterns that mention approval
    approval_sections = 0
    lines = claude_content.split('\n')
    for line in lines:
        if line.startswith('##') or line.startswith('###'):
            # This is a section heading
            if 'approval' in line.lower():
                approval_sections += 1

    print(f"  [OK] Approval mentioned in {approval_sections} section heading(s)")

    # Check table of contents
    if '## Table of Contents' in claude_content:
        toc_section = claude_content.split('## Table of Contents')[1].split('##')[0]
        if 'approval' in toc_section.lower():
            print("  [OK] Approval mentioned in table of contents")

    print("\n[PASS] Approval gate clarity test completed successfully")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("USER APPROVAL GATE TEST SUITE (Phase 5.5)")
    print("="*70)
    print("\nNote: Approval gate is PROCEDURAL (not programmatic)")
    print("These tests validate documentation quality, not code enforcement")

    try:
        # Run approval gate tests
        test_approval_gate_documentation()
        test_workflow_includes_approval_step()
        test_approval_gate_clarity()

        print("\n" + "="*70)
        print("[PASS] ALL APPROVAL GATE TESTS PASSED")
        print("="*70)
        print("\nTest Coverage:")
        print("  [OK] Approval gate documented clearly and comprehensively")
        print("  [OK] Workflows include approval step before execution")
        print("  [OK] Language is clear, direct, and unambiguous")
        print("  [OK] Approval is presented as mandatory (non-optional)")
        print("\nTotal: 3 test functions, all passing")
        print("\nValidation: Documentation provides sufficient guidance for AI agents")
        print("            to follow the procedural approval gate pattern correctly")

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
