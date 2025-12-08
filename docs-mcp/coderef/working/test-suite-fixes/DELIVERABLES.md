# DELIVERABLES: test-suite-fixes

**Project**: docs-mcp
**Feature**: test-suite-fixes
**Workorder**: WO-TEST-SUITE-FIXES-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-08

---

## Executive Summary

**Goal**: Achieve 100% test pass rate by fixing all 26 failing tests and identifying necessary handler changes

**Description**: Fix all 26 failing tests across 5 categories: JSON response format mismatches (7), wrong file path references (6), mock tool names in server tests (6), assertion text mismatches (2), and language detection bug (1). Current state: 642 passed, 26 failed (96% pass rate). Target: 668 passed, 0 failed (100% pass rate).

---

## Implementation Phases

### Phase 1: JSON Response Format Fixes

**Description**: Fix 11 tests that expect JSON responses but receive text. Analyze response patterns and update tests to parse actual format or add helper functions.

**Estimated Duration**: TBD

**Deliverables**:
- Updated test_mcp_workflows.py with proper response parsing
- Updated test_planning_workflow.py with proper response parsing
- Helper function for parsing tool responses if needed

### Phase 2: File Path Reference Fixes

**Description**: Fix 6 tests looking for files in wrong directories. Update to use project root paths.

**Estimated Duration**: TBD

**Deliverables**:
- Updated test_user_approval_gate.py with correct paths
- Updated test_workflow_documentation.py with correct paths

### Phase 3: Server Unit Test Mock Fixes

**Description**: Fix 6 server unit tests that use non-existent tool names. Add proper TOOL_HANDLERS mocking.

**Estimated Duration**: TBD

**Deliverables**:
- Updated test_server.py with proper mock setup
- TOOL_HANDLERS mock fixture if needed

### Phase 4: Minor Fixes and Verification

**Description**: Fix assertion mismatches and language detection. Run full test suite for verification.

**Estimated Duration**: TBD

**Deliverables**:
- Updated assertion expectations
- Fixed language detection or test
- Full test suite passing (668/668)


---

## Metrics

### Code Changes
- **Lines of Code Added**: TBD
- **Lines of Code Deleted**: TBD
- **Net LOC**: TBD
- **Files Modified**: TBD

### Commit Activity
- **Total Commits**: TBD
- **First Commit**: TBD
- **Last Commit**: TBD
- **Contributors**: TBD

### Time Investment
- **Days Elapsed**: TBD
- **Hours Spent (Wall Clock)**: TBD

---

## Task Completion Checklist

- [ ] [JSON-001] Fix test_gather_context_workflow JSON parsing
- [ ] [JSON-002] Fix test_create_and_list_expert_workflow JSON parsing
- [ ] [JSON-003] Fix test_suggest_experts_workflow JSON parsing
- [ ] [JSON-004] Fix test_planning_to_execution_workflow JSON parsing
- [ ] [JSON-005] Fix test_gather_context_creates_context_file
- [ ] [JSON-006] Fix test_gather_context_generates_workorder_id
- [ ] [JSON-007] Fix test_gather_context_validates_required_fields
- [ ] [PATH-001] Fix test_approval_gate_documentation path reference
- [ ] [PATH-002] Fix test_workflow_includes_approval_step path reference
- [ ] [PATH-003] Fix test_approval_gate_clarity path reference
- [ ] [PATH-004] Fix test_claude_md_documents_review_loop path reference
- [ ] [PATH-005] Fix test_meta_plan_shows_review_loop_in_workflow path reference
- [ ] [PATH-006] Fix test_workflow_examples_show_iteration_pattern path reference
- [ ] [MOCK-001] Fix test_call_tool_dispatches_to_handler mock setup
- [ ] [MOCK-002] Fix test_call_tool_returns_handler_result mock setup
- [ ] [MOCK-003] Fix test_call_tool_logs_invocation mock setup
- [ ] [MOCK-004] Fix test_call_tool_with_empty_arguments mock setup
- [ ] [MOCK-005] Fix test_call_tool_preserves_exception_from_handler mock setup
- [ ] [MOCK-006] Fix test_call_tool_dispatch_performance mock setup
- [ ] [ASSERT-001] Fix test_invalid_template_name_handling assertion
- [ ] [ASSERT-002] Fix test_missing_required_arguments assertion
- [ ] [VALID-001] Fix test_gather_context_validates_feature_name
- [ ] [VALID-002] Fix test_validate_plan_handles_missing_file
- [ ] [VALID-003] Fix test_validate_plan_handles_malformed_json
- [ ] [VALID-004] Fix test_full_planning_workflow end-to-end
- [ ] [DETECT-001] Fix test_analyze_docs_mcp language detection

---

## Files Created/Modified

- **tests/integration/test_mcp_workflows.py** - TBD
- **tests/integration/test_planning_workflow.py** - TBD
- **tests/integration/test_user_approval_gate.py** - TBD
- **tests/integration/test_workflow_documentation.py** - TBD
- **tests/unit/test_server.py** - TBD
- **tests/smoke/test_analyze_project_basic.py** - TBD
- **tool_handlers.py** - TBD
- **generators/planning_generator.py** - TBD

---

## Success Criteria

- All 668 tests pass (0 failures)
- No new test warnings introduced
- Existing functionality unchanged

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-08
