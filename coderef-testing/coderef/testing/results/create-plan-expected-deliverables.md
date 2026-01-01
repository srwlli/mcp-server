# Expected Deliverables: create_plan Tool (coderef-workflow)

**Tool:** `mcp__coderef-workflow__create_plan`
**Server:** coderef-workflow
**Purpose:** Generate complete implementation plans from feature requirements
**Test Analysis Date:** 2026-01-01

---

## Tool Workflow

```
User Input
    ↓
gather_context (interactive Q&A)
    ↓ Produces: context.json
analyze_project_for_planning (scan codebase)
    ↓ Produces: analysis.json
create_plan (synthesize context + analysis + template)
    ↓ Should Produce: plan.json (complete, executable)
validate_implementation_plan (quality check)
    ↓ Produces: validation report (score 0-100)
[If score >= 90] → execute_plan
[If score < 90] → refine plan → re-validate
```

---

## Primary Deliverable: plan.json

**File Location:** `coderef/workorder/{feature-name}/plan.json`
**Format:** JSON (10-section structure)
**Expected State:** Complete, executable, no TODOs
**Current State:** ⚠️ Skeleton with TODOs (stub implementation)

### Structure (10 Sections)

#### Section: META_DOCUMENTATION
**Required Fields:**
- `feature_name` (string)
- `workorder_id` (string, format: `WO-{FEATURE}-{CATEGORY}-###`)
- `version` (string, semver)
- `status` (enum: "planning", "in_progress", "completed")
- `generated_by` (string)
- `uds` (object, UDS metadata)

**Current Status:** ✅ Generated correctly

---

#### Section 0: preparation (0_preparation)
**Purpose:** Project discovery and analysis results
**Required Fields:**
- `foundation_docs` (object with `available` and `missing` arrays)
- `coding_standards` (object with `available` and `missing` arrays)
- `reference_components` (object with `primary` and `secondary`)
- `key_patterns_identified` (array of strings)
- `technology_stack` (object with `languages`, `frameworks`, `key_libraries`)
- `gaps_and_risks` (array of strings)

**Current Status:** ⚠️ Populated from `analysis.json` if exists, else placeholder messages
**Issue:** Should synthesize from actual project scan

---

#### Section 1: executive_summary (1_executive_summary)
**Purpose:** What and why (3-5 bullets)
**Required Fields (NEW schema):**
- `goal` (string)
- `description` (string)
- `scope` (string)

**Current Status:** ❌ Generates OLD format with TODOs:
- `purpose` (partial - from context if available)
- `value_proposition` → **"TODO: Define value proposition"**
- `real_world_analogy` → **"TODO: Add real-world analogy"**
- `use_case` → **"TODO: Add use case workflow"**
- `output` → **"TODO: List tangible artifacts"**

**Issue:** Should synthesize from `context.description` and `context.goal`

---

#### Section 2: risk_assessment (2_risk_assessment)
**Purpose:** Identify breaking changes, security, performance concerns
**Required Fields:**
- `overall_risk` (enum: low/medium/high/critical)
- `complexity` (string with estimate)
- `scope` (string)
- `file_system_risk` (enum)
- `dependencies` (array)
- `performance_concerns` (array)
- `security_considerations` (array)
- `breaking_changes` (string)

**Current Status:** ⚠️ Hardcoded defaults:
- `complexity` → **"medium (TODO: estimate file count and lines)"**
- `scope` → **"Medium - TODO files, TODO components affected"**
- `performance_concerns` → **["TODO: identify performance concerns"]**
- `security_considerations` → **["TODO: identify security considerations"]**

**Issue:** Should analyze `context.constraints` and `analysis` data

---

#### Section 3: current_state_analysis (3_current_state_analysis)
**Purpose:** Existing architecture and affected files
**Required Fields:**
- `affected_files` (array of file paths)
- `dependencies` (object with 4 arrays: existing_internal, existing_external, new_external, new_internal)
- `architecture_context` (string)

**Current Status:** ❌ All TODOs:
- `affected_files` → **["TODO: List all files to create/modify"]**
- `architecture_context` → **"TODO: Describe architecture layer and patterns"**

**Issue:** Should use `analysis.reference_components` and coderef-context tools

---

#### Section 4: key_features (4_key_features)
**Purpose:** Must-have requirements
**Required Fields:**
- `primary_features` (array, 3-5 items)
- `secondary_features` (array, 2-3 items)
- `edge_case_handling` (array)
- `configuration_options` (array)

**Current Status:** ⚠️ Partial:
- If `context.requirements` exists → uses first 5 items
- Else → **["TODO: List 3-5 primary features"]**
- `edge_case_handling` → **["TODO: Define edge cases"]**

**Issue:** Should synthesize from `context.requirements` comprehensively

---

#### Section 5: task_id_system (5_task_id_system)
**Purpose:** Task breakdown with IDs
**Required Fields:**
- `tasks` (array of task objects with `id`, `description`, `depends_on`)

**Current Status:** ❌ Placeholder tasks:
```json
{
  "tasks": [
    "SETUP-001: TODO: Initial setup task",
    "LOGIC-001: TODO: Core logic task",
    "TEST-001: TODO: Testing task",
    "DOC-001: TODO: Documentation task"
  ]
}
```

**Issue:** Should generate specific tasks from feature requirements

---

#### Section 6: implementation_phases (6_implementation_phases)
**Purpose:** Phased breakdown with dependencies
**Required Fields (NEW schema):**
- `phases` (array of objects with `phase`, `name`, `tasks`, `deliverables`)

**Current Status:** ❌ Wrong format:
- Generates OLD format: `title`, `purpose`, `complexity`, `effort_level`, `tasks`, `completion_criteria`
- Missing NEW fields: `phase`, `name`, `deliverables`

**Issue:** Schema mismatch - generates 4 generic phases instead of feature-specific breakdown

---

#### Section 7: testing_strategy (7_testing_strategy)
**Purpose:** Unit, integration, e2e tests
**Required Fields:**
- `unit_tests` (array)
- `integration_tests` (array)
- `end_to_end_tests` (array)
- `edge_case_scenarios` (array of objects with scenario/setup/expected_behavior/verification/error_handling)

**Current Status:** ❌ All TODOs:
- `unit_tests` → **["TODO: List unit tests"]**
- `integration_tests` → **["TODO: List integration tests"]**
- Edge case scenarios → **"TODO: Edge case 1"** placeholders

**Issue:** Should derive from feature requirements and patterns

---

#### Section 8: success_criteria (8_success_criteria)
**Purpose:** How to verify completion
**Required Fields:**
- `functional_requirements` (array of objects with requirement/metric/target/validation)
- `quality_requirements` (array)
- `performance_requirements` (array)
- `security_requirements` (array)

**Current Status:** ⚠️ Partial:
- `functional_requirements` → **[{"requirement": "TODO", "metric": "TODO", "target": "TODO", "validation": "TODO"}]**
- `quality_requirements` → Has 1 real entry (code coverage >80%)
- Performance/security → Empty arrays

**Issue:** Should map from `context.success_criteria` if provided

---

#### Section 9: implementation_checklist (9_implementation_checklist)
**Purpose:** Pre-flight and finalization checklists
**Required Fields:**
- `pre_implementation` (array of checkbox items)
- `phase_1`, `phase_2`, `phase_3`, `phase_4` (arrays)
- `finalization` (array)

**Current Status:** ⚠️ Generic checklist:
- Pre-implementation: 3 generic items (✅)
- Phase checklists: **"☐ SETUP-001: TODO"** placeholders
- Finalization: 4 generic items (✅)

**Issue:** Should generate feature-specific checklist items

---

## Secondary Deliverables

### 1. Workorder Log Entry
**File:** `coderef/workorder-log.txt`
**Format:** One-line entry
**Content:** `WO-{ID} | {project} | {description} | {timestamp}`
**Status:** ⚠️ Generated if `workorder_id` provided

### 2. UDS Metadata
**Location:** Embedded in `plan.json` → `META_DOCUMENTATION.uds`
**Fields:**
- `generated_by` (server version)
- `document_type` ("Implementation Plan")
- `last_updated` (ISO date)
- `ai_assistance` (boolean)
- `next_review` (ISO date, +30 days)
**Status:** ✅ Generated correctly (lines 531-545)

### 3. DELIVERABLES.md Template
**File:** `coderef/workorder/{feature-name}/DELIVERABLES.md`
**Generated by:** `generate_deliverables_template` (separate tool)
**Status:** Not part of `create_plan` (separate workflow step)

---

## Quality Gates

### Validation Tool: validate_implementation_plan
**Checks:**
- Structure completeness (10 sections present)
- No placeholder text (TODO, TBD, etc.)
- Task IDs valid and unique
- Success criteria measurable
- No circular dependencies
- No ambiguous language

**Scoring:**
- Critical issue: -10 points
- Major issue: -5 points
- Minor issue: -1 point
- Passing score: ≥90

**Current create_plan Output:**
- Expected score: **~15-20** (fails validation)
- 33 major issues (TODOs): -165 points
- 12 major issues (missing fields): -60 points
- Total deduction: -225 points → **Score: 0** (capped at minimum)

---

## Expected vs Actual

| Deliverable | Expected | Actual Status |
|-------------|----------|---------------|
| plan.json | Complete, executable, 0 TODOs | ⚠️ Skeleton with 33+ TODOs |
| Section 0-9 | All populated with real data | ⚠️ Mix of partial/TODO/wrong format |
| Phase structure | NEW format (phase/name/deliverables) | ❌ OLD format (title/purpose/complexity) |
| Task breakdown | Feature-specific tasks | ❌ Generic 4-task stub |
| Validation score | ≥90 (passing) | ~0 (failing) |
| Workorder log | 1 entry created | ✅ Works if workorder_id provided |
| UDS metadata | Complete metadata | ✅ Generated correctly |

---

## Summary

**Primary Deliverable:** `plan.json` (10-section implementation plan)
**Expected Quality:** Complete, executable, validation score ≥90
**Actual Quality:** Skeleton with TODOs, validation score ~0

**Root Issue:** `create_plan` is a stub that generates plan structure but not content. Requires AI synthesis implementation to produce complete plans.

**Recommendation:** Tool should be marked as "beta" or "scaffold mode" until AI synthesis logic is implemented.

---

**Test Report Generated by:** coderef-testing v1.0.0
**Analysis Type:** Expected deliverables vs actual output
**Date:** 2026-01-01
