# Validation Checklist - WO-RESOURCE-SHEET-CONSOLIDATION-001-TESTING

**Workorder:** WO-RESOURCE-SHEET-CONSOLIDATION-001-TESTING
**Testing Agent:** Testing Specialist
**Version:** 1.0.0
**Created:** 2026-01-03
**Status:** Ready for Execution

---

## Purpose

This validation checklist ensures comprehensive testing of the resource sheet consolidation implementation (Phases 2-3) before production deployment. Use this checklist to verify all critical requirements, test execution steps, and acceptance criteria.

---

## Pre-Testing Checklist

### 1. Environment Setup

- [ ] **coderef-docs MCP server** running with Phases 2-3 implementation complete
- [ ] **coderef-context MCP server** accessible for graph integration tests
- [ ] **Test environment** isolated (no production data affected)
- [ ] **Logging enabled** for MCP tool invocation tracing
- [ ] **Timing tools** calibrated (Python timeit, time command, etc.)

### 2. Test Data Verification

- [ ] **P1 batch reference sheets** accessible at `C:\Users\willh\.mcp-servers\coderef-workflow\coderef\reference-sheets\`
- [ ] **All 10 P1 files** present and readable:
  - [ ] CONSTANTS.md + constants-jsdoc.txt
  - [ ] ERROR-RESPONSES.md + error-responses-jsdoc.txt
  - [ ] MCP-CLIENT.md + mcp-client-jsdoc.txt
  - [ ] TYPE-DEFS.md + type-defs-jsdoc.txt
  - [ ] VALIDATION.md + validation-jsdoc.txt
- [ ] **Graph data** generated: `.coderef/exports/graph.json` exists for coderef-workflow
- [ ] **Element type definitions** accessible: `.claude/commands/resource-sheet-catalog.md`
- [ ] **Synthetic test data** prepared for validation pipeline tests (malformed inputs)

### 3. Test Plan Review

- [ ] **test-plan.json** reviewed and approved by orchestrator
- [ ] **test-cases.json** contains all 49 test cases with clear steps
- [ ] **Acceptance criteria** understood: 100% critical requirements must pass
- [ ] **Rollback plan** reviewed and ready if critical failures found

### 4. Communication Protocol

- [ ] **instructions.json** status updated to "testing_in_progress"
- [ ] **Test results directory** created: `C:\Users\willh\.mcp-servers\coderef\sessions\resource-sheet-consolidation-testing\results\`
- [ ] **Orchestrator notified** testing is about to begin

---

## Testing Execution Checklist

### Category 1: Routing Validation (CRITICAL - MUST PASS)

**Objective:** Verify 100% routing to MCP tool

- [ ] **ROUTE-001:** Slash command invocation routes to MCP tool (not .md file)
  - Evidence: MCP tool invocation log showing `mcp__coderef-docs__generate_resource_sheet` called
- [ ] **ROUTE-002:** Element type parameter passthrough works
  - Evidence: Parameter logs showing element_type used correctly
- [ ] **ROUTE-003:** Backward compatibility - all 10 P1 examples route correctly
  - Evidence: 10/10 successful routing with output generation

**Gate Pass Criteria:** 100% of routing tests pass (3/3)

---

### Category 2: Element Type Detection (CRITICAL - MUST PASS)

**Objective:** Verify 80%+ confidence for all 20 element types

- [ ] **DETECT-001:** Stage 1 filename pattern matching achieves 80-95% confidence for 20 types
  - Evidence: Detection accuracy matrix showing 20/20 types with 80%+ confidence
- [ ] **DETECT-002:** Stage 2 code analysis adds +10-20% confidence boost
  - Evidence: Before/after confidence scores showing improvement
- [ ] **DETECT-003:** Stage 3 fallback prompts for manual review when confidence <80%
  - Evidence: Manual review prompts shown for ambiguous cases
- [ ] **DETECT-004:** Confidence scoring accuracy >=80% overall
  - Evidence: Confusion matrix showing >=80% detection accuracy

**Gate Pass Criteria:** 80%+ confidence for all 20 element types (4/4 tests pass)

---

### Category 3: Graph Integration Auto-Fill (CRITICAL - MUST PASS)

**Objective:** Verify 60-80% average completion rate

- [ ] **GRAPH-001:** Dependencies section auto-fill >=90%
  - Evidence: Auto-fill percentage report showing 90%+ for 10 P1 files
- [ ] **GRAPH-002:** Public API section auto-fill >=95%
  - Evidence: Auto-fill percentage report showing 95%+ for 10 P1 files
- [ ] **GRAPH-003:** Usage Examples section auto-fill >=70%
  - Evidence: Auto-fill percentage report showing 70%+ for 10 P1 files
- [ ] **GRAPH-004:** Required Dependencies section auto-fill >=75%
  - Evidence: Auto-fill percentage report showing 75%+ for 10 P1 files
- [ ] **GRAPH-005:** Overall completion rate 60-80%
  - Evidence: Comprehensive completion rate report with weighted average

**Gate Pass Criteria:** 60-80% average completion rate (5/5 tests pass)

---

### Category 4: Validation Pipeline (CRITICAL - MUST PASS)

**Objective:** Verify 4-gate validation catches all errors

- [ ] **VALID-001:** Gate 1 structural validation catches 4/4 errors
  - Evidence: Validation report showing missing header, summary, sections, state table caught
- [ ] **VALID-002:** Gate 2 content quality catches 4/4 errors
  - Evidence: Validation report showing placeholders, incomplete sections, voice violations, missing tables caught
- [ ] **VALID-003:** Gate 3 element-specific validation catches 3/3 errors
  - Evidence: Validation report showing missing focus areas, required sections, element tables caught
- [ ] **VALID-004:** Gate 4 auto-fill threshold rejects <60% completion
  - Evidence: Validation report showing rejection for low auto-fill rate
- [ ] **VALID-005:** Scoring system correctly categorizes Pass/Warn/Reject
  - Evidence: Validation reports showing correct scoring for all 3 cases

**Gate Pass Criteria:** 100% error detection for all 4 gates (5/5 tests pass)

---

### Category 5: Performance Benchmarks (CRITICAL - MUST PASS)

**Objective:** Verify <2s total end-to-end generation time

- [ ] **PERF-001:** Graph load time <500ms
  - Evidence: Timing report showing average load time <500ms (10 iterations)
- [ ] **PERF-002:** Query execution time <50ms per query
  - Evidence: Timing report showing all 4 queries <50ms each
- [ ] **PERF-003:** Template rendering time <1s
  - Evidence: Timing report showing average rendering <1s (10 iterations)
- [ ] **PERF-004:** End-to-end generation time <2s
  - Evidence: Performance report showing 95th percentile <2s across 100 tests

**Gate Pass Criteria:** <2s total generation time (4/4 tests pass)

---

### Category 6: Output Format Validation (HIGH - SHOULD PASS)

**Objective:** Verify 3 output formats + 0 regression failures

- [ ] **FORMAT-001:** Markdown format correctness
  - Evidence: Markdown validation report showing valid syntax
- [ ] **FORMAT-002:** JSON schema format correctness
  - Evidence: JSON Schema validation report showing Draft 7 compliance
- [ ] **FORMAT-003:** JSDoc format correctness
  - Evidence: JSDoc validation report showing JSDoc 3 standard compliance
- [ ] **FORMAT-004:** P1 batch regression test (0 content degradation)
  - Evidence: Regression report showing >=95% content similarity, 0 regressions

**Gate Pass Criteria:** 100% format correctness, 0 regressions (4/4 tests pass)

---

### Category 7: Edge Cases & Error Handling (MEDIUM - NICE TO HAVE)

**Objective:** Verify graceful degradation and error handling

- [ ] **EDGE-001:** Missing graph data handled gracefully
  - Evidence: Error handling logs showing warning + degraded output
- [ ] **EDGE-002:** Ambiguous element type prompts for manual review
  - Evidence: Prompt logs showing manual review request
- [ ] **EDGE-003:** Invalid file path shows helpful error
  - Evidence: Error message logs showing "File not found" message
- [ ] **EDGE-004:** Malformed input data rejected by validation
  - Evidence: Validation rejection logs with clear error messages

**Gate Pass Criteria:** 100% graceful error handling, no crashes (4/4 tests pass)

---

## Post-Testing Checklist

### 1. Results Aggregation

- [ ] **Test results** recorded in `test-results.json` (structured pass/fail data)
- [ ] **Test report** generated in `test-report.md` (human-readable summary)
- [ ] **Performance report** generated in `performance-report.md` (timing data)
- [ ] **Regression report** generated in `regression-report.md` (P1 batch diff analysis)
- [ ] **All evidence** collected and attached to reports (logs, diffs, screenshots)

### 2. Pass/Fail Analysis

- [ ] **Critical requirements** analyzed:
  - [ ] CR-1 (Routing): PASS / FAIL
  - [ ] CR-2 (Detection): PASS / FAIL
  - [ ] CR-3 (Auto-fill): PASS / FAIL
  - [ ] CR-4 (Validation): PASS / FAIL
  - [ ] CR-5 (Performance): PASS / FAIL
- [ ] **Failure severity** assessed: Critical / Major / Minor
- [ ] **Root cause** identified for all failures
- [ ] **Rollback decision** made if critical failures found

### 3. Reporting to Orchestrator

- [ ] **instructions.json** status updated:
  - [ ] "testing_complete" if all critical requirements passed
  - [ ] "testing_failed" if critical failures found
- [ ] **Summary report** prepared for orchestrator:
  - [ ] Pass/fail count by category
  - [ ] Critical failures highlighted
  - [ ] Recommendations (deploy / fix / rollback)
- [ ] **Handoff document** created: `testing-handoff-complete.md`

---

## Acceptance Criteria (GO/NO-GO Decision)

### GO - Ready for Production

**All of the following MUST be TRUE:**

- [ ] **CR-1 (Routing):** 100% routing to MCP tool (10/10 P1 examples)
- [ ] **CR-2 (Detection):** 80%+ confidence for all 20 element types
- [ ] **CR-3 (Auto-fill):** 60-80% average completion rate
- [ ] **CR-4 (Validation):** 100% error detection for 4-gate pipeline
- [ ] **CR-5 (Performance):** <2s total generation time (95th percentile)
- [ ] **P1 Regression:** 0 content degradation vs baseline
- [ ] **Edge Cases:** No crashes, graceful error handling

**Recommendation:** **DEPLOY** to production

---

### NO-GO - Requires Fixes

**Any of the following is TRUE:**

- [ ] **CR-1 FAIL:** Routing doesn't work (<100% success rate)
- [ ] **CR-2 FAIL:** Detection confidence <80% for any element type
- [ ] **CR-3 FAIL:** Auto-fill rate <60% average
- [ ] **CR-4 FAIL:** Validation gates don't catch critical errors
- [ ] **CR-5 FAIL:** Performance >2s (95th percentile)
- [ ] **P1 Regression:** Content quality degraded vs baseline
- [ ] **Critical Crash:** System crashes on valid input

**Recommendation:** **ROLLBACK** - delegate fixes to coderef-docs agent, re-test after fixes

---

### CONDITIONAL GO - Deploy with Warnings

**Acceptable if:**

- [ ] All critical requirements (CR-1 through CR-5) PASS
- [ ] Minor failures in edge cases (EDGE-001 through EDGE-004) only
- [ ] Performance slightly above target (<2.5s instead of <2s) but acceptable
- [ ] Documentation issues only (can be fixed post-launch)

**Recommendation:** **DEPLOY with monitoring** - fix minor issues in next iteration

---

## Rollback Trigger Conditions

**Immediate rollback required if any of these occur:**

1. **Routing failure:** /create-resource-sheet doesn't call MCP tool
2. **Detection failure:** <80% confidence for priority 1 element types
3. **Auto-fill failure:** <60% completion rate on P1 examples
4. **Validation failure:** Critical errors not caught by 4-gate pipeline
5. **Data corruption:** P1 regeneration produces invalid output
6. **System crash:** Any crash on valid input data

**Rollback steps:**
1. Document failure with evidence
2. Update instructions.json status to "testing_failed"
3. Report findings to orchestrator with severity assessment
4. Orchestrator delegates fixes to coderef-docs agent
5. Re-run tests after fixes implemented
6. Repeat until all critical requirements pass

---

## Notes for Testing Agent

### Testing Philosophy

- **Test what matters:** Focus on critical requirements (routing, detection, auto-fill, validation, performance)
- **Evidence-based:** Every pass/fail must have evidence (logs, diffs, timing data, screenshots)
- **No false positives:** If a test passes, the feature must actually work (no flaky tests)
- **Graceful failures:** Document failures clearly with actionable recommendations

### Risk Areas to Watch

1. **Graph integration:** Might fail if .coderef/exports/graph.json is missing or malformed
2. **Detection confidence:** Might be <80% for rarely-used element types (priority 4)
3. **Performance cold start:** First run might exceed 2s (acceptable if warm runs <2s)
4. **P1 regression:** Content might differ slightly due to improved auto-fill (acceptable if quality improved)

### Assumptions

1. coderef-docs agent implemented Phases 2-3 per CODEREF-DOCS-HANDOFF.md
2. P1 batch reference sheets represent expected output quality
3. Graph data (.coderef/exports/graph.json) available for coderef-workflow project
4. Testing environment isolated (no production data affected)

---

## Checklist Summary

**Pre-Testing:** 15 checklist items
**Testing Execution:** 49 test cases across 7 categories
**Post-Testing:** 11 checklist items
**Acceptance Criteria:** 3 decision paths (GO / NO-GO / CONDITIONAL GO)

**Total Checklist Items:** 75+

**Estimated Time:** 2-4 hours for complete execution

---

**Prepared by:** Testing Agent
**For:** Orchestrator (coderef-assistant)
**Status:** Ready for test execution after coderef-docs agent completes Phases 2-3

---

## Sign-Off

**Testing Agent:**
- [ ] Test plan complete and approved
- [ ] Test cases defined with clear steps
- [ ] Validation checklist ready for use
- [ ] Testing handoff document prepared

**Orchestrator:**
- [ ] Test plan reviewed and approved
- [ ] Ready to signal coderef-docs agent for Phase 2-3 implementation
- [ ] Ready to receive test results after Phase 4 execution

**Signature:** _________________________
**Date:** _________________________
