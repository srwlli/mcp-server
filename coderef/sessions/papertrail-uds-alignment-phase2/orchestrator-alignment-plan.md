# Phase 2: Master Alignment Plan
## Target: 100% Validation Coverage

**Workorder:** WO-PAPERTRAIL-UDS-ALIGNMENT-002
**Phase:** Phase 2 - Gap Analysis & Implementation Planning
**Orchestrator:** coderef
**Date:** 2026-01-10
**Status:** Complete

---

## Executive Summary

All 3 agents completed gap analysis. **30 total gaps identified** across the CodeRef ecosystem requiring **60.5 hours total effort** to achieve **100% validation coverage**.

### Current State vs Target

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Validation Rate** | 12% (6/50) | 100% (50/50) | +44 outputs |
| **Papertrail** | 7 schemas, 5 validators | +2 schemas | analysis.json, execution-log.json |
| **Coderef-Docs** | 4/18 validated (22%) | 18/18 (100%) | +14 outputs |
| **Coderef-Workflow** | 2/32 validated (6%) | 32/32 (100%) | +30 outputs |

### Gap Distribution by Priority

| Priority | Papertrail | Coderef-Docs | Coderef-Workflow | **Total** | **Hours** |
|----------|------------|--------------|------------------|-----------|-----------|
| **P0** | 0 | 2 | 4 | **6** | **11.5** |
| **P1** | 1 | 1 | 8 | **10** | **27** |
| **P2** | 3 | 2 | 5 | **10** | **17** |
| **P3** | 1 | 1 | 2 | **4** | **5** |
| **TOTAL** | **5** | **6** | **19** | **30** | **60.5** |

---

## Phase 3 Implementation Strategy

### Timeline: 3-4 Weeks (Phased Rollout)

**Week 1: P0 Critical Gaps** (11.5 hours)
- Papertrail: No P0 gaps
- Coderef-Docs: Foundation docs + default change (4.5 hours)
- Coderef-Workflow: communication.json, context.json, plan.json migration (7 hours)

**Week 2: P1 High-Priority Gaps** (27 hours)
- Papertrail: execution-log schema (4 hours)
- Coderef-Docs: Standards docs (3 hours)
- Coderef-Workflow: Updates + foundation docs (20 hours)

**Week 3: P2 Medium-Priority Gaps** (17 hours)
- Papertrail: analysis.json schema + ValidatorFactory updates (6 hours)
- Coderef-Docs: Quickref + resource sheets (8 hours)
- Coderef-Workflow: Reviews, handoff docs, aggregates (5 hours)

**Week 4: P3 Low-Priority Gaps** (5 hours)
- Papertrail: Optional improvements (2.5 hours)
- Coderef-Docs: CHANGELOG migration (2 hours)
- Coderef-Workflow: Archive index + inventory (2.5 hours)

---

## Phase 3 Workorder Specifications

### WO-PAPERTRAIL-SCHEMA-ADDITIONS-001

**Agent:** papertrail
**Priority:** P1 (execution-log) + P2 (analysis) + P3 (skip risk-assessment)
**Effort:** 14 hours
**Timeline:** Week 1-2

**Context:**
```json
{
  "workorder_id": "WO-PAPERTRAIL-SCHEMA-ADDITIONS-001",
  "feature_name": "schema-additions-uds-alignment",
  "description": "Create 2 new schemas (analysis.json, execution-log.json) to enable coderef-workflow 100% validation coverage",
  "goal": "Add missing schemas identified in Phase 1/2 gap analysis to support workflow artifact validation",
  "requirements": [
    "Create analysis-json-schema.json in papertrail/schemas/workflow/",
    "Create execution-log-json-schema.json in papertrail/schemas/workflow/",
    "Create AnalysisValidator in papertrail/validators/analysis.py",
    "Create ExecutionLogValidator in papertrail/validators/execution_log.py",
    "Update ValidatorFactory patterns for new file types",
    "Add cross-validation between execution-log and plan.json (task_id references)",
    "Skip risk-assessment schema (data belongs in plan.json)"
  ],
  "constraints": [
    "Schemas must follow JSON Schema Draft-07",
    "Validators must inherit from BaseUDSValidator",
    "Score threshold >= 90 for validation pass",
    "Must coordinate with coderef-workflow for sample files"
  ],
  "dependencies": [
    "Requires sample analysis.json files from coderef-workflow",
    "Requires sample execution-log.json files from coderef-workflow"
  ]
}
```

**Tasks (Priority-Ordered):**

**P1 - execution-log.json (Week 1):**
1. Request sample execution-log.json from coderef-workflow
2. Design execution-log-json-schema.json (required: workorder_id, feature_id, started_at, tasks, status)
3. Create schema file in papertrail/schemas/workflow/
4. Create ExecutionLogValidator in papertrail/validators/execution_log.py
5. Add cross-validation: verify task_id references exist in plan.json
6. Update ValidatorFactory pattern: `r".*/coderef/workorder/.*/execution-log\.json$": "execution_log"`
7. Test validator with sample files
8. Document usage in UDS-IMPLEMENTATION-GUIDE.md

**P2 - analysis.json (Week 2-3):**
9. Request sample analysis.json from coderef-workflow
10. Design analysis-json-schema.json (required: project_path, analyzed_at, project_type, tech_stack, file_inventory, patterns_detected)
11. Create schema file in papertrail/schemas/workflow/
12. Create AnalysisValidator in papertrail/validators/analysis.py
13. Update ValidatorFactory pattern: `r".*/coderef/workorder/.*/analysis\.json$": "analysis"`
14. Test validator with sample files
15. Document usage

**P2 - Optional Improvements:**
16. Add cross-validation for execution-log ↔ plan.json task IDs (2.5 hours)
17. Add INFO severity level for non-blocking messages (1 hour)

**P3 - Skipped:**
- ❌ risk-assessment-json-schema.json - Redundant, data belongs in plan.json

**Success Criteria:**
- ✅ 2 new schemas created and validated
- ✅ 2 new validators functional with score >= 90 threshold
- ✅ ValidatorFactory detects new file types
- ✅ Documentation updated
- ✅ Tests pass

---

### WO-CODEREF-DOCS-UDS-COMPLIANCE-001

**Agent:** coderef-docs
**Priority:** P0 (foundation + default) + P1 (standards) + P2 (optional)
**Effort:** 17.5 hours (9.5 hours minimum for P0+P1)
**Timeline:** Week 1-3

**Context:**
```json
{
  "workorder_id": "WO-CODEREF-DOCS-UDS-COMPLIANCE-001",
  "feature_name": "uds-compliance-coderef-docs",
  "description": "Integrate Papertrail validators for 14 unvalidated outputs to achieve 100% validation coverage",
  "goal": "Add validation to all foundation docs, standards docs, and enable Papertrail by default",
  "requirements": [
    "Integrate FoundationDocValidator for 5 foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)",
    "Change PAPERTRAIL_ENABLED default from false to true",
    "Integrate validator for standards docs (ui-patterns, behavior-patterns, ux-patterns)",
    "Add validation to generate_foundation_docs tool (lines 127-237)",
    "Add validation to generate_individual_doc tool (lines 242-347)",
    "Add validation to establish_standards tool (lines 717-786)",
    "Return validation errors to user if score < 90"
  ],
  "constraints": [
    "Must add papertrail>=1.0.0 to requirements.txt",
    "Must add try/except for graceful degradation if Papertrail unavailable",
    "Breaking change: validation failures will block doc generation (stricter than current)",
    "Must update tests to handle validation errors"
  ],
  "dependencies": [
    "Papertrail FoundationDocValidator available",
    "Papertrail StandardsDocValidator or SystemDocValidator available"
  ],
  "decisions_needed": [
    "Quickref.md: Create schema or keep unstructured? (RECOMMEND: keep unstructured, P2)",
    "Resource sheets: Add UDS validation or keep validate_against_code? (RECOMMEND: keep current, P2)",
    "CHANGELOG.json: Migrate to Papertrail or keep jsonschema? (RECOMMEND: check if Papertrail has schema, P3)"
  ]
}
```

**Tasks (Priority-Ordered):**

**P0 - Foundation Docs (Week 1):**
1. Add `papertrail>=1.0.0` to requirements.txt
2. Update generate_foundation_docs (tool_handlers.py:127-237):
   - Import FoundationDocValidator
   - Call validator after each doc generation
   - Return errors if score < 90
3. Update generate_individual_doc (tool_handlers.py:242-347):
   - Change PAPERTRAIL_ENABLED default to True (line 270)
   - Add try/except for import failures
4. Test all 5 foundation docs: README, ARCHITECTURE, API, SCHEMA, COMPONENTS
5. Update documentation: note validation is enabled by default

**P1 - Standards Docs (Week 2):**
6. Confirm which validator to use: StandardsDocValidator or SystemDocValidator
7. Update establish_standards (tool_handlers.py:717-786):
   - Import appropriate validator
   - Call validator after generating ui-patterns.md, behavior-patterns.md, ux-patterns.md
   - Return errors if validation fails
8. Update generators/standards_generator.py save_standards() method
9. Test all 3 standards docs

**P2 - Optional (Week 3):**
10. DECISION: Quickref.md schema (recommend: skip, 5 hours)
11. DECISION: Resource sheets UDS validation (recommend: skip, 3 hours)

**P3 - Optional (Week 4):**
12. Check if Papertrail has CHANGELOG.json schema
13. If yes: Migrate from jsonschema to Papertrail validator (2 hours)
14. If no: Keep jsonschema validation (0 hours)

**Success Criteria:**
- ✅ 5 foundation docs validated (P0)
- ✅ PAPERTRAIL_ENABLED=true by default (P0)
- ✅ 3 standards docs validated (P1)
- ✅ Validation rate: 72% (13/18) after P0+P1
- ✅ Validation rate: 100% (18/18) if P2+P3 completed

---

### WO-CODEREF-WORKFLOW-UDS-COMPLIANCE-001

**Agent:** coderef-workflow
**Priority:** P0 (critical) + P1 (high) + P2 (medium) + P3 (low)
**Effort:** 29 hours
**Timeline:** Week 1-4

**Context:**
```json
{
  "workorder_id": "WO-CODEREF-WORKFLOW-UDS-COMPLIANCE-001",
  "feature_name": "uds-compliance-coderef-workflow",
  "description": "Migrate from internal validators to Papertrail, add validation to 30 unvalidated outputs, achieve 100% validation coverage",
  "goal": "Consolidate validation under Papertrail as single source of truth, validate all workflow artifacts",
  "requirements": [
    "Migrate plan.json validation from internal PlanValidator to Papertrail PlanValidator",
    "Deprecate generators/plan_validator.py and schema_validator.py",
    "Integrate SessionDocValidator for communication.json (create + all updates)",
    "Integrate WorkorderDocValidator for context.json, analysis.json, DELIVERABLES updates",
    "Integrate FoundationDocValidator for README, ARCHITECTURE, SCHEMA, COMPONENTS",
    "Integrate SystemDocValidator for CLAUDE.md",
    "Add validation to all 24 tools generating outputs",
    "Re-validate after all update operations"
  ],
  "constraints": [
    "Breaking changes: PlanValidator API differs (validate_plan() vs validate_file())",
    "Must update all imports from generators.plan_validator to papertrail.validators.plan",
    "Must update tests to use Papertrail validators",
    "Phased rollout required (3 stages) to mitigate risk"
  ],
  "dependencies": [
    "WO-PAPERTRAIL-SCHEMA-ADDITIONS-001 must complete first (analysis.json, execution-log.json schemas)",
    "Papertrail validators must be available: Plan, Session, Workorder, Foundation, System"
  ],
  "blockers": [
    "3 file types need schemas from Papertrail: analysis.json, execution-log.json, risk-assessment.json"
  ]
}
```

**Tasks (Priority-Ordered):**

**Stage 1: P0 Critical Gaps (Week 1):**
1. **GAP-001:** Integrate SessionDocValidator for communication.json (generate_agent_communication) - 1 hour
2. **GAP-002:** Integrate WorkorderDocValidator for context.json (gather_context) - 1 hour
3. **GAP-004:** Migrate plan.json to Papertrail PlanValidator (BREAKING CHANGE) - 4 hours:
   - Add deprecation warnings to generators/plan_validator.py
   - Update imports in create_plan (tool_handlers.py:1169)
   - Update imports in validate_implementation_plan (tool_handlers.py:1051)
   - Update all test files
   - Test validation with existing plan.json files
4. **GAP-005:** Add validation to communication.json updates (assign_agent_task, verify_agent_completion) - 1.5 hours
5. **GAP-006:** Add validation to DELIVERABLES.md updates (update_deliverables) - 1 hour

**Stage 2: P1 High-Priority Gaps (Week 2):**
6. **GAP-008:** Add validation to plan.json updates (update_task_status) - 1 hour
7. **GAP-009:** Integrate FoundationDocValidator for coderef_foundation_docs (ARCHITECTURE, SCHEMA, COMPONENTS) - 2 hours
8. **GAP-010:** Add validation to README.md updates (update_all_documentation) - 1 hour
9. **GAP-011:** Add validation to CLAUDE.md updates (update_all_documentation) - 1 hour
10. **GAP-007:** Integrate ExecutionLogValidator for execution-log.json (execute_plan) - 3 hours
    - **BLOCKER:** Requires WO-PAPERTRAIL-SCHEMA-ADDITIONS-001 complete

**Stage 3: P2 Medium-Priority Gaps (Week 3):**
11. **GAP-003:** Integrate validator for analysis.json (analyze_project_for_planning) - 3 hours
    - **BLOCKER:** Requires WO-PAPERTRAIL-SCHEMA-ADDITIONS-001 complete
12. **GAP-012:** Add validation to CHANGELOG.json (update_all_documentation, add_changelog_entry) - 1 hour
13. **GAP-013:** Add validation to review reports (generate_plan_review_report) - 1 hour
14. **GAP-014:** Add validation to handoff docs (generate_handoff_context) - 1 hour
15. **GAP-015:** Integrate validator for risk-assessment.json (assess_risk) - 2.5 hours (IF SCHEMA CREATED)
16. **GAP-016:** Add validation to DELIVERABLES-combined.md (aggregate_agent_deliverables) - 1 hour

**Stage 4: P3 Low-Priority Gaps (Week 4):**
17. **GAP-017:** Add validation to archive index.json (archive_feature) - 1.5 hours
18. **GAP-018:** Add validation to features-inventory.json/md (generate_features_inventory) - 1 hour
19. **GAP-019:** DECISION: Migrate workorder-log.txt to JSON or keep as text - 2 hours (IF MIGRATING)

**Deprecation Timeline:**
- Week 1: Add deprecation warnings to generators/plan_validator.py
- Week 2: Complete migration, remove imports of internal validators
- Week 3: Delete generators/plan_validator.py and schema_validator.py from codebase

**Success Criteria:**
- ✅ Internal validators deprecated and removed
- ✅ All 19 gaps addressed (100% coverage)
- ✅ Validation rate: 34% after Stage 1 (P0)
- ✅ Validation rate: 59% after Stage 2 (P0+P1)
- ✅ Validation rate: 100% after Stage 3+4 (full compliance)
- ✅ All tests pass
- ✅ Breaking changes documented

---

## Critical Dependencies & Coordination

### Cross-Project Dependencies

**Papertrail → Coderef-Workflow:**
- coderef-workflow CANNOT complete GAP-003, GAP-007, GAP-015 until Papertrail creates schemas
- Recommend: Papertrail completes WO-PAPERTRAIL-SCHEMA-ADDITIONS-001 by end of Week 1

**Coderef-Docs → Papertrail:**
- Needs confirmation: StandardsDocValidator exists? Or use SystemDocValidator?
- Needs decision: CHANGELOG.json schema exists in Papertrail?

**Coderef-Workflow → Papertrail:**
- Needs sample files: analysis.json, execution-log.json examples for schema design
- Must provide before Papertrail can complete schemas

### Blocker Resolution Plan

| Blocker | Owner | Resolution | Timeline |
|---------|-------|------------|----------|
| Sample analysis.json needed | coderef-workflow | Provide 2-3 examples to Papertrail | Week 1 Day 1 |
| Sample execution-log.json needed | coderef-workflow | Provide 2-3 examples to Papertrail | Week 1 Day 1 |
| StandardsDocValidator confirmation | Papertrail | Confirm validator exists or recommend alternative | Week 1 Day 1 |
| CHANGELOG.json schema check | Papertrail | Check if schema exists in Papertrail repo | Week 1 Day 1 |

---

## Validation Coverage Projection

### By Week

| Week | Focus | Papertrail | Coderef-Docs | Coderef-Workflow | **Ecosystem Total** |
|------|-------|------------|--------------|------------------|---------------------|
| **Current** | Baseline | 7 schemas | 4/18 (22%) | 2/32 (6%) | **6/50 (12%)** |
| **Week 1** | P0 Gaps | +0 schemas | 7/18 (39%) | 11/32 (34%) | **18/50 (36%)** |
| **Week 2** | P1 Gaps | +1 schema (execution-log) | 10/18 (56%) | 19/32 (59%) | **29/50 (58%)** |
| **Week 3** | P2 Gaps | +1 schema (analysis) | 13/18 (72%) | 24/32 (75%) | **37/50 (74%)** |
| **Week 4** | P3 Gaps | +0 schemas | 18/18 (100%) | 32/32 (100%) | **50/50 (100%)** ✅ |

### By Priority

| Priority | Gaps | Hours | Coverage Increase |
|----------|------|-------|-------------------|
| P0 | 6 | 11.5 | +24% (12% → 36%) |
| P1 | 10 | 27 | +22% (36% → 58%) |
| P2 | 10 | 17 | +16% (58% → 74%) |
| P3 | 4 | 5 | +26% (74% → 100%) |
| **TOTAL** | **30** | **60.5** | **+88%** |

---

## Risk Assessment

### High-Risk Items

**1. plan.json Migration (GAP-004) - BREAKING CHANGE**
- **Risk:** API differences between internal and Papertrail validators could break existing workflows
- **Mitigation:** Comprehensive test coverage, phased rollout with deprecation warnings
- **Contingency:** Keep internal validator as fallback for 1 week during transition

**2. PAPERTRAIL_ENABLED Default Change (GAP-DOCS-006)**
- **Risk:** Users without Papertrail installed will get import errors
- **Mitigation:** Add try/except for graceful degradation, document Papertrail as required dependency
- **Contingency:** Add environment variable override to disable if needed

**3. Cross-Project Dependencies**
- **Risk:** Coderef-workflow blocked on Papertrail schema creation
- **Mitigation:** Complete WO-PAPERTRAIL-SCHEMA-ADDITIONS-001 in Week 1
- **Contingency:** If schemas delayed, coderef-workflow skips dependent gaps and revisits in Week 3

### Medium-Risk Items

**4. Standards Doc Validator Uncertainty (GAP-DOCS-002)**
- **Risk:** Unclear which validator to use (StandardsDocValidator vs SystemDocValidator)
- **Mitigation:** Confirm with Papertrail agent on Day 1
- **Contingency:** Use SystemDocValidator if StandardsDocValidator doesn't exist

**5. 60.5 Hours Total Effort**
- **Risk:** Underestimated complexity could extend timeline
- **Mitigation:** P0+P1 only = 38.5 hours (achievable in 2 weeks), defer P2+P3 if needed
- **Contingency:** Target 74% validation rate (P0+P1+P2) if P3 deprioritized

---

## Success Metrics

### Phase 3 Completion Criteria

**Papertrail (WO-PAPERTRAIL-SCHEMA-ADDITIONS-001):**
- ✅ 2 new schemas created (analysis.json, execution-log.json)
- ✅ 2 new validators functional
- ✅ ValidatorFactory updated
- ✅ Cross-validation implemented (execution-log ↔ plan.json)

**Coderef-Docs (WO-CODEREF-DOCS-UDS-COMPLIANCE-001):**
- ✅ 5 foundation docs validated (P0)
- ✅ PAPERTRAIL_ENABLED=true by default (P0)
- ✅ 3 standards docs validated (P1)
- ✅ Validation rate >= 72% (P0+P1 complete)

**Coderef-Workflow (WO-CODEREF-WORKFLOW-UDS-COMPLIANCE-001):**
- ✅ Internal validators deprecated and removed
- ✅ 19 gaps addressed
- ✅ Validation rate >= 59% (P0+P1 complete)
- ✅ All tests pass

**Ecosystem-Wide:**
- ✅ **100% validation coverage (50/50 outputs)** ← PRIMARY GOAL
- ✅ All agents use Papertrail as single source of truth
- ✅ No internal validators remaining
- ✅ All workorder documentation updated

---

## Next Steps

### For Each Agent:

1. **Read this orchestrator plan** (`orchestrator-alignment-plan.md`)
2. **Extract your workorder section** (search for your WO-ID)
3. **Run `/create-workorder`** in your project
4. **Use the context.json specification** provided above
5. **Run `/execute-plan`** to convert plan to TodoWrite tasks
6. **Implement changes** following priority order (P0 → P1 → P2 → P3)
7. **Run `/update-deliverables`** when complete
8. **Run `/archive-feature`** to finalize

### Coordination Required:

**Week 1 Day 1:**
- Coderef-workflow: Provide sample analysis.json and execution-log.json to Papertrail
- Papertrail: Confirm StandardsDocValidator exists for coderef-docs
- Papertrail: Confirm CHANGELOG.json schema exists for coderef-docs

**Week 1 End:**
- Papertrail: Complete P1 schema (execution-log.json) for coderef-workflow

**Week 2-3:**
- Papertrail: Complete P2 schema (analysis.json) for coderef-workflow

---

## Timeline Summary

| Week | Papertrail | Coderef-Docs | Coderef-Workflow |
|------|------------|--------------|------------------|
| **1** | Sample coordination | P0: Foundation docs (4.5h) | P0: Critical gaps (8.5h) |
| **2** | P1: execution-log schema (4h) | P1: Standards docs (3h) | P1: High-priority (9h) |
| **3** | P2: analysis schema (4h) | P2: Optional (8h) | P2: Medium-priority (7.5h) |
| **4** | P3: Optional (2h) | P3: Optional (2h) | P3: Low-priority (4h) |
| **Total** | **14 hours** | **17.5 hours** | **29 hours** |

**Grand Total:** 60.5 hours = ~3-4 weeks with parallel execution

---

**Generated by:** coderef-orchestrator
**Session:** WO-PAPERTRAIL-UDS-ALIGNMENT-002
**Phase:** Phase 2 - Gap Analysis & Implementation Planning
**Date:** 2026-01-10
**Target:** 100% validation coverage (50/50 outputs validated)
