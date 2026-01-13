# TESTING AGENT BRIEFING - WO-RESOURCE-SHEET-CONSOLIDATION-001-TESTING

**From:** CodeRef Assistant (Orchestrator)
**To:** Testing Agent
**Date:** 2026-01-03
**Priority:** High
**Status:** Ready for Test Plan Development

---

## Executive Summary

**Your Mission:** Develop a comprehensive test plan for validating the resource sheet consolidation implementation (Phases 2-3) before it goes to production.

**Context:** A 4-agent synthesis session (WO-REFERENCE-SHEET-RECONCILIATION-001) discovered that two separate resource sheet systems can be consolidated into ONE by routing the `/create-resource-sheet` slash command to an existing MCP tool and enhancing it with missing features.

**Your Deliverable:** Complete test plan with test cases, validation criteria, performance benchmarks, and execution instructions ready for Phase 4 testing (after coderef-docs agent completes Phases 2-3).

---

## What You're Testing

### The Consolidation Project

**Goal:** Merge two resource sheet systems into unified MCP tool backend

**Tool 1:** `.claude/commands/create-resource-sheet.md` (240 lines - agent instruction template)
**Tool 2:** `.claude/commands/resource-sheet-catalog.md` (634 lines - 20 element type classifications)
**Target:** `mcp__coderef-docs__generate_resource_sheet` (existing MCP tool v3.4.0)

**Implementation Phases:**
- ✅ **Phase 1:** Deprecation warnings added (orchestrator - complete)
- 🔄 **Phase 2:** Route slash command to MCP tool (coderef-docs agent - pending, 1-2 hours)
- 🔄 **Phase 3:** Full MCP enhancement (coderef-docs agent - pending, 12-16 hours)
- 📋 **Phase 4:** Testing & validation (testing agent - **YOU**, 2-4 hours execution)

---

## Success Criteria to Validate

Your test plan must verify these 5 critical requirements:

### 1. Routing Works (100% Success Rate)
- **Requirement:** Every `/create-resource-sheet` invocation calls the MCP tool
- **Test:** Invoke command on 15 P1 examples, verify MCP tool is called (not .md file)
- **Pass Criteria:** 100% routing to MCP tool

### 2. Element Type Detection (80%+ Confidence)
- **Requirement:** All 20 element types detected with 80%+ confidence
- **Test:** Test detection algorithm on known examples from each of 20 categories
- **Pass Criteria:**
  - Stage 1 (filename patterns): 80-95% confidence on primary types
  - Stage 2 (code analysis): +10-20% confidence boost
  - Stage 3 (fallback): Prompts for manual review if <80%

### 3. Graph Auto-Fill (60-80% Completion)
- **Requirement:** 60-80% average completion rate via graph queries
- **Test:** Regenerate 15 P1 batch examples, measure completion percentage
- **Pass Criteria:**
  - Average across all examples: 60-80%
  - Dependencies section: 90% auto-fill
  - Public API section: 95% auto-fill
  - Usage Examples section: 70% auto-fill
  - Required Dependencies: 75% auto-fill

### 4. Validation Pipeline (4-Gate Quality)
- **Requirement:** 4-gate validation catches critical/major/minor errors
- **Test:** Submit intentionally malformed inputs, verify gates catch them
- **Pass Criteria:**
  - Gate 1 (Structural): Catches missing header, summary, required sections, state ownership
  - Gate 2 (Content Quality): Catches placeholders, incomplete sections, voice violations, missing tables
  - Gate 3 (Element-Specific): Catches missing focus areas, element-required sections, element tables
  - Gate 4 (Auto-Fill Threshold): Rejects if <60% completion

### 5. Performance Benchmarks (<2s Total)
- **Requirement:** <2 seconds total generation time
- **Test:** Measure end-to-end timing on P1 batch examples
- **Pass Criteria:**
  - Graph load: <500ms
  - 4 parallel queries: <50ms each
  - Template rendering: <1s
  - Total end-to-end: <2s

---

## Test Data You Have

### P1 Batch Reference Sheets (15 Files)

**Location:** `C:\Users\willh\.mcp-servers\coderef-workflow\coderef\reference-sheets\`

**Elements:** 5 types × 3 formats each = 15 files
1. **CONSTANTS.md** / CONSTANTS.json / CONSTANTS.jsdoc
2. **ERROR-RESPONSES.md** / ERROR-RESPONSES.json / ERROR-RESPONSES.jsdoc
3. **MCP-CLIENT.md** / MCP-CLIENT.json / MCP-CLIENT.jsdoc
4. **TYPE-DEFS.md** / TYPE-DEFS.json / TYPE-DEFS.jsdoc
5. **VALIDATION.md** / VALIDATION.json / VALIDATION.jsdoc

**Purpose:** These are REAL production reference sheets generated during the synthesis session. Use them as:
- Baseline for regression testing (regenerate and compare)
- Examples of expected output quality
- Validation of 3-format output (markdown, JSON schema, JSDoc)

### 20 Element Type Definitions

**Source:** `.claude/commands/resource-sheet-catalog.md`

**Priority 1 (Most Common):**
1. top_level_widgets (Page, Widget suffix)
2. stateful_containers (Container, Manager suffix)
3. global_state (Store, Context, Provider suffix)
4. custom_hooks (use* prefix)
5. api_clients (Client, API, Service suffix)

**Priority 2 (Common):**
6. data_models (Model, Schema, Entity suffix)
7. utility_modules (Utils, Helpers suffix)
8. constants (CONSTANTS, CONFIG files)
9. error_definitions (Error, Exception classes)
10. type_definitions (.d.ts files, type/ folders)

**Priority 3 (Specialized):**
11. validation (Validator, Schema suffix)
12. middleware (Middleware suffix)
13. transformers (Transformer, Mapper suffix)
14. event_handlers (Handler, Listener suffix)
15. services (Service suffix, service/ folders)

**Priority 4 (Advanced):**
16. configuration (Config, Settings files)
17. context_providers (Provider suffix)
18. decorators (@decorator pattern)
19. factories (Factory suffix)
20. observers (Observer, Watcher suffix)

**Detection Patterns:** Each type has filename patterns + code analysis rules for 3-stage detection.

---

## Reference Materials to Study

### Primary Synthesis Outputs (Read These First)

1. **orchestrator-output.md** - Complete synthesis from all 4 agents
   - Location: `C:\Users\willh\.mcp-servers\coderef\sessions\reference-sheet-reconciliation\orchestrator-output.md`
   - Why: Overview of entire consolidation approach

2. **coderef-output.md** - Consolidation design blueprint
   - Location: `C:\Users\willh\.mcp-servers\coderef\sessions\reference-sheet-reconciliation\coderef-output.md`
   - Why: Technical architecture and module design

3. **CODEREF-DOCS-HANDOFF.md** - Phase 2-3 implementation instructions
   - Location: `C:\Users\willh\Desktop\assistant\coderef\workorder\resource-sheet-consolidation\CODEREF-DOCS-HANDOFF.md`
   - Why: Detailed task breakdown of what's being implemented

### Secondary Agent Outputs (For Deep Dive)

4. **papertrail-output.json** - Unified template schema
   - Why: Understanding 13 base sections + 20 element overlays

5. **coderef-system-output.json** - Graph integration mappings
   - Why: Understanding 4 query functions for auto-fill

6. **coderef-docs-output.json** - Documentation standards
   - Why: Understanding 4-gate validation pipeline design

---

## Your Test Plan Should Cover

### Category 1: Routing Validation
- **Test 1.1:** Slash command invocation routes to MCP tool (not .md file)
- **Test 1.2:** Element type parameter passthrough works
- **Test 1.3:** Fallback behavior if MCP tool unavailable

### Category 2: Element Type Detection
- **Test 2.1:** Filename pattern matching (Stage 1) - 20 test cases
- **Test 2.2:** Code analysis refinement (Stage 2) - 10 edge cases
- **Test 2.3:** Fallback to manual review (Stage 3) - 5 ambiguous cases
- **Test 2.4:** Confidence scoring accuracy

### Category 3: Graph Integration Auto-Fill
- **Test 3.1:** Dependencies section auto-fill (90% target)
- **Test 3.2:** Public API section auto-fill (95% target)
- **Test 3.3:** Usage Examples section auto-fill (70% target)
- **Test 3.4:** Required Dependencies auto-fill (75% target)
- **Test 3.5:** Overall completion rate (60-80% target)

### Category 4: Validation Pipeline
- **Test 4.1:** Gate 1 - Structural validation (4 checks)
- **Test 4.2:** Gate 2 - Content quality (4 checks)
- **Test 4.3:** Gate 3 - Element-specific validation (3 checks)
- **Test 4.4:** Gate 4 - Auto-fill threshold (1 check)
- **Test 4.5:** Scoring system (pass/warn/reject)

### Category 5: Performance Benchmarks
- **Test 5.1:** Graph load time (<500ms)
- **Test 5.2:** Query execution time (<50ms per query × 4)
- **Test 5.3:** Template rendering time (<1s)
- **Test 5.4:** End-to-end generation time (<2s total)

### Category 6: Output Format Validation
- **Test 6.1:** Markdown format correctness
- **Test 6.2:** JSON schema format correctness
- **Test 6.3:** JSDoc format correctness
- **Test 6.4:** P1 batch regression (15 examples)

### Category 7: Edge Cases & Error Handling
- **Test 7.1:** Missing graph data (graceful degradation)
- **Test 7.2:** Ambiguous element type (manual review prompt)
- **Test 7.3:** Invalid file paths
- **Test 7.4:** Malformed input data

---

## Deliverables Expected from You

### 1. test-plan.json
Structured test plan with:
- Test categories (7 categories above)
- Test cases (detailed scenarios with expected outcomes)
- Pass/fail criteria for each test
- Test data requirements
- Execution sequence

### 2. test-cases.json
Detailed test case definitions:
- Test ID (e.g., ROUTE-001, DETECT-001, GRAPH-001)
- Description
- Preconditions
- Steps to execute
- Expected results
- Actual results (to be filled during execution)
- Status (pass/fail/blocked)

### 3. validation-checklist.md
Quality gate checklist:
- Pre-testing checklist (verify test data available, tools accessible)
- Testing execution checklist (run all test categories)
- Post-testing checklist (aggregate results, report findings)
- Acceptance criteria (what must pass to approve Phase 4)

### 4. testing-handoff.md
Step-by-step execution instructions:
- How to set up test environment
- How to run each test category
- How to measure performance benchmarks
- How to interpret results
- How to report back to orchestrator

---

## Workflow After Test Plan Complete

1. **You develop test plan** (this phase - 3-5 hours)
2. **Orchestrator reviews test plan** (approval or change requests)
3. **Test plan approved** → wait for coderef-docs agent to complete Phases 2-3
4. **coderef-docs agent reports completion** → orchestrator signals you to execute
5. **You run tests** (2-4 hours execution using your test plan)
6. **You report results** → orchestrator makes go/no-go decision
7. **If pass:** Orchestrator closes workorder, updates dashboard
8. **If fail:** Orchestrator delegates fixes back to coderef-docs agent

---

## Questions to Answer in Your Test Plan

1. **How will you verify routing?** (What evidence proves MCP tool is called?)
2. **How will you measure auto-fill percentage?** (Automated script? Manual review?)
3. **What constitutes a "pass" for each gate?** (Binary pass/fail or scoring system?)
4. **How will you time performance?** (What tool? What metrics?)
5. **What's the regression testing protocol?** (Exact steps for P1 batch)
6. **What's your rollback plan?** (If critical failures found in Phase 4)

---

## Success Criteria for Your Test Plan

Before submitting your test plan to orchestrator, verify:

- [ ] All 7 test categories covered with detailed test cases
- [ ] Pass/fail criteria defined for all 5 critical requirements
- [ ] P1 batch regression protocol established (15 examples)
- [ ] Performance measurement methodology specified
- [ ] Test data locations verified and documented
- [ ] Edge cases and error scenarios included
- [ ] Execution instructions clear enough for another agent to run
- [ ] Reporting format defined (how you'll communicate results)

---

## Next Steps

1. **Read reference materials** (start with orchestrator-output.md and CODEREF-DOCS-HANDOFF.md)
2. **Analyze P1 batch examples** (understand expected output quality)
3. **Study 20 element type definitions** (know what detection should catch)
4. **Develop test plan** (use deliverables structure above)
5. **Submit for review** (update instructions.json status to "plan_submitted")

---

## Communication Protocol

Update `instructions.json` in this directory as you progress:

```json
{
  "communication": {
    "testing_agent": {
      "status": "plan_in_progress",  // → "plan_submitted" → "plan_approved" → "executing" → "complete"
      "last_update": "2026-01-03",
      "notes": "Started test plan development. Reviewed reference materials."
    }
  }
}
```

---

## Questions or Blockers?

If you encounter issues:
1. Check the 4-agent synthesis outputs (especially orchestrator-output.md)
2. Review the P1 batch examples for clarification
3. Update instructions.json with blocker details
4. Orchestrator will respond with guidance

---

**Estimated Time:** 3-5 hours for complete test plan development

**Ready to begin!** Start by reading orchestrator-output.md to understand the full context, then dive into the P1 batch examples.

**Good luck!** 🧪
