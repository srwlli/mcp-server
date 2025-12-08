# DELIVERABLES: known-issue-fixes

**Project**: docs-mcp
**Feature**: known-issue-fixes
**Workorder**: WO-KNOWN-ISSUE-FIXES-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-08

---

## Executive Summary

**Goal**: Fix two production issues affecting coderef workflow reliability

**Description**: During test suite review, two issues were identified: (1) Plan validator scores comprehensive plans below 85 threshold due to overly strict scoring, (2) Arrow function detection in context_expert_generator misses functions without parentheses (const fn = x => x). Both issues affect user experience and code analysis accuracy.

---

## Implementation Phases

### Phase 1: Diagnosis

**Description**: Analyze root causes of both issues before making changes

**Estimated Duration**: TBD

**Deliverables**:
- Root cause analysis for validator scoring
- VALID_PLAN fixture review

### Phase 2: Validator Fix

**Description**: Fix the plan validator scoring to properly score comprehensive plans

**Estimated Duration**: TBD

**Deliverables**:
- Validator logic fixed
- Test threshold restored to 85

### Phase 3: Arrow Function Fix

**Description**: Expand regex patterns to detect arrow functions without parentheses

**Estimated Duration**: TBD

**Deliverables**:
- New regex patterns added
- Tests for new patterns

### Phase 4: Verification

**Description**: Verify all fixes work and document changes

**Estimated Duration**: TBD

**Deliverables**:
- All tests passing
- Changelog updated


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

- [ ] [DIAG-001] Analyze validate_plan_handler.py scoring logic - identify why comprehensive plans score below 85
- [ ] [DIAG-002] Review VALID_PLAN fixture in tests - ensure it represents a truly valid comprehensive plan
- [ ] [FIX-001] Fix validator scoring logic or VALID_PLAN fixture to achieve >= 85 score
- [ ] [FIX-002] Restore test threshold assertion from >= 60 back to >= 85
- [ ] [REGEX-001] Add regex pattern for arrow functions without parentheses: const fn = x => expr
- [ ] [REGEX-002] Add regex pattern for async arrow functions without parentheses: const fn = async x => expr
- [ ] [TEST-001] Add test for arrow function without parentheses detection
- [ ] [TEST-002] Add test for async arrow function without parentheses detection
- [ ] [VERIFY-001] Run full test suite to verify no regressions
- [ ] [DOC-001] Add changelog entry for fixes

---

## Files Created/Modified

- **generators/context_expert_generator.py** - TBD
- **handlers/validate_plan_handler.py** - TBD
- **tests/unit/generators/test_context_expert_generator.py** - TBD
- **tests/unit/handlers/test_validate_plan_handler.py** - TBD

---

## Success Criteria

- No success criteria defined

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-08
