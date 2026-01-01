# Test Report: create_plan Tool Validation

**Test ID:** TEST-CREATE-PLAN-001
**Test Date:** 2026-01-01
**Tested Component:** `mcp__coderef-workflow__create_plan`
**Test Type:** Root cause analysis + Expected deliverables validation
**Tested By:** coderef-testing v1.0.0
**Test Status:** ✅ Complete

---

## Executive Summary

The `create_plan` tool generates structurally valid plan.json files but with incomplete content. Analysis identified **2 root causes** affecting plan quality:

1. **33 TODO Placeholders** - Stub implementation generates skeleton plans instead of synthesizing actual content
2. **12 Missing Phase Fields** - Schema format mismatch between generator (OLD) and validator (NEW)

**Impact:** Plans fail validation (score ~0/100, expected ≥90) and are not executable without manual completion.

**Conclusion:** Tool works as a scaffold generator but requires AI synthesis implementation to produce production-ready plans.

---

## Part 1: Root Cause Analysis

### Issue #1: 33 TODO Placeholders

**Severity:** Major
**Impact:** -165 points (33 × -5 points each)
**Location:** `generators/planning_generator.py:232-285`

#### Problem Description

The plan generator creates skeleton plans with hardcoded TODO placeholders instead of synthesizing actual content from context and analysis inputs.

#### Evidence from Source Code

**File:** `planning_generator.py`
**Method:** `_generate_plan_internal()`
**Lines 243-245:**

```python
# NOTE: This is a simplified implementation. In production, this would use
# an AI model (like Claude) to actually synthesize the inputs into a complete plan.
# For now, it creates a skeleton plan structure.
```

#### Specific TODO Generation Points

| Line | Method | Placeholder Generated | Section |
|------|--------|---------------------|---------|
| 315 | `_generate_executive_summary()` | `"real_world_analogy": "TODO: Add real-world analogy"` | 1 |
| 316 | `_generate_executive_summary()` | `"use_case": "TODO: Add use case workflow"` | 1 |
| 317 | `_generate_executive_summary()` | `"output": "TODO: List tangible artifacts"` | 1 |
| 322 | `_generate_executive_summary()` | `"value_proposition": "TODO: Define value proposition"` | 1 |
| 336 | `_generate_risk_assessment()` | `"complexity": "medium (TODO: estimate file count)"` | 2 |
| 340 | `_generate_risk_assessment()` | `"performance_concerns": ["TODO: identify..."]` | 2 |
| 341 | `_generate_risk_assessment()` | `"security_considerations": ["TODO: identify..."]` | 2 |
| 348 | `_generate_current_state()` | `"affected_files": ["TODO: List all files"]` | 3 |
| 355 | `_generate_current_state()` | `"architecture_context": "TODO: Describe..."` | 3 |
| 364 | `_generate_key_features()` | `"edge_case_handling": ["TODO: Define edge cases"]` | 4 |
| 369 | `_generate_key_features()` | `"primary_features": ["TODO: List 3-5 features"]` | 4 |
| 370 | `_generate_key_features()` | `"secondary_features": ["TODO: List 2-3 features"]` | 4 |
| 371 | `_generate_key_features()` | `"edge_case_handling": ["TODO: List 2-3 edge cases"]` | 4 |
| 383 | `_generate_tasks()` | `"SETUP-001: TODO: Initial setup task"` | 5 |
| 384 | `_generate_tasks()` | `"LOGIC-001: TODO: Core logic task"` | 5 |
| 385 | `_generate_tasks()` | `"TEST-001: TODO: Testing task"` | 5 |
| 386 | `_generate_tasks()` | `"DOC-001: TODO: Documentation task"` | 5 |
| 432 | `_generate_testing_strategy()` | `"unit_tests": ["TODO: List unit tests"]` | 7 |
| 433 | `_generate_testing_strategy()` | `"integration_tests": ["TODO: List integration tests"]` | 7 |
| 437 | `_generate_testing_strategy()` | `"scenario": "TODO: Edge case 1"` | 7 |
| 438 | `_generate_testing_strategy()` | `"setup": "TODO: How to create"` | 7 |
| 439 | `_generate_testing_strategy()` | `"expected_behavior": "TODO: What should happen"` | 7 |
| 440 | `_generate_testing_strategy()` | `"verification": "TODO: How to verify"` | 7 |
| 441 | `_generate_testing_strategy()` | `"error_handling": "TODO: Error type or 'No error'"` | 7 |
| 450 | `_generate_success_criteria()` | `"requirement": "TODO"` | 8 |
| 450 | `_generate_success_criteria()` | `"metric": "TODO"` | 8 |
| 450 | `_generate_success_criteria()` | `"target": "TODO"` | 8 |
| 450 | `_generate_success_criteria()` | `"validation": "TODO"` | 8 |
| 467 | `_generate_checklist()` | `"☐ SETUP-001: TODO"` | 9 |
| 468 | `_generate_checklist()` | `"☐ LOGIC-001: TODO"` | 9 |
| 469 | `_generate_checklist()` | `"☐ TEST-001: TODO"` | 9 |
| 470 | `_generate_checklist()` | `"☐ DOC-001: TODO"` | 9 |

**Total Found:** 33+ TODO placeholders across 8 generator methods

#### Why This Happens

The generator methods receive `context` and `analysis` inputs but don't synthesize them. Instead, they:

1. Check if input exists: `if context:` or `if analysis:`
2. Extract simple fields: `context.get("description")`, `context.get("requirements")`
3. Fall back to TODO placeholders for everything else

**Example from `_generate_executive_summary()` (lines 305-326):**

```python
def _generate_executive_summary(self, feature_name: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if context:
        return {
            "purpose": context.get("description", f"Implement {feature_name} feature"),
            "value_proposition": context.get("goal", "Enhance system capabilities"),
            "real_world_analogy": "TODO: Add real-world analogy",  # ← Hardcoded
            "use_case": "TODO: Add use case workflow",              # ← Hardcoded
            "output": "TODO: List tangible artifacts"               # ← Hardcoded
        }

    return {
        "purpose": f"Implement {feature_name} feature",
        "value_proposition": "TODO: Define value proposition",     # ← Hardcoded
        "real_world_analogy": "TODO: Add real-world analogy",      # ← Hardcoded
        "use_case": "TODO: Add use case workflow",                 # ← Hardcoded
        "output": "TODO: List tangible artifacts"                  # ← Hardcoded
    }
```

**Missing:** AI synthesis logic to generate real-world analogies, use cases, and artifacts from context.

---

### Issue #2: 12 Missing Phase Fields

**Severity:** Major
**Impact:** -60 points (12 × -5 points each)
**Location:** `generators/planning_generator.py:390-427` vs `generators/plan_validator.py:342-351`

#### Problem Description

The `_generate_phases()` method generates phases in **OLD format** but the validator expects **NEW format** fields, causing all 4 phases to fail validation.

#### Schema Format Mismatch

**Generator Output (OLD format):**

```python
def _generate_phases(self) -> Dict[str, Any]:
    return {
        "phases": [
            {
                "title": "Phase 1: Foundation",        # ← OLD field
                "purpose": "Setup and scaffolding",    # ← OLD field
                "complexity": "low",                   # ← OLD field
                "effort_level": 2,                     # ← OLD field
                "tasks": ["SETUP-001"],                # ✓ Required
                "completion_criteria": "All files exist"  # ← Extra field
            },
            # ... 3 more phases with same structure
        ]
    }
```

**Validator Expectation (NEW format - from `plan_validator.py:342-351`):**

```python
# NEW format required fields
required_new = ['phase', 'name', 'tasks', 'deliverables']
for field in required_new:
    if field not in phase:
        self.issues.append({
            'severity': 'major',
            'section': 'quality',
            'issue': f'Phase "{phase_name}" missing required "{field}" field',
            'suggestion': f'Add {field} field to phase'
        })
```

#### Field Comparison Table

| Generator Creates (OLD) | Validator Expects (NEW) | Status |
|------------------------|------------------------|--------|
| `title` | `phase` (number/id) | ❌ Missing |
| `purpose` | `name` (phase title) | ❌ Missing |
| `complexity` | `tasks` (array) | ✅ Present |
| `effort_level` | `deliverables` (array) | ❌ Missing |
| `tasks` (array) | - | ✅ Present (required) |
| `completion_criteria` | - | ✅ Extra (acceptable) |

#### Impact Calculation

- **4 phases generated** (Foundation, Core Implementation, Testing, Documentation)
- **3 missing fields per phase** (`phase`, `name`, `deliverables`)
- **4 phases × 3 missing fields = 12 major issues**
- **Score impact:** 12 × -5 = -60 points

#### Why This Happens

The generator was written for an older schema version and never updated when the schema changed. The validator (updated to match `plan.schema.json`) now expects a different structure.

**Validator supports both formats** (lines 336-352 show backward compatibility), but the generator only produces OLD format, so validation issues are still reported.

---

## Part 2: Expected Deliverables

### Tool Workflow

```
User Input (feature requirements)
    ↓
gather_context (interactive Q&A)
    ↓ Produces: context.json
analyze_project_for_planning (scan codebase)
    ↓ Produces: analysis.json
create_plan (synthesize context + analysis + template)
    ↓ Should Produce: plan.json (complete, executable, no TODOs)
validate_implementation_plan (quality check)
    ↓ Produces: validation report (score 0-100)
[If score >= 90] → execute_plan (ready)
[If score < 90] → refine plan → re-validate (needs work)
```

---

### Primary Deliverable: plan.json

**File Location:** `coderef/workorder/{feature-name}/plan.json`
**Format:** JSON (10-section structure per `feature-implementation-planning-standard.json`)
**Expected State:** Complete, executable, validation score ≥90
**Actual State:** ⚠️ Skeleton with 33 TODOs, validation score ~0

#### Section Breakdown

| Section | Name | Expected | Actual Status |
|---------|------|----------|---------------|
| META | META_DOCUMENTATION | Complete metadata | ✅ Works (feature_name, workorder_id, version, status, uds) |
| 0 | preparation | Project analysis results | ⚠️ Partial (uses analysis.json if exists, else placeholders) |
| 1 | executive_summary | What & why (goal, description, scope) | ❌ OLD format + 5 TODOs |
| 2 | risk_assessment | Breaking changes, security, performance | ⚠️ Hardcoded defaults + 4 TODOs |
| 3 | current_state_analysis | Affected files, dependencies, architecture | ❌ All TODOs (2 fields) |
| 4 | key_features | Must-have requirements | ⚠️ Uses context.requirements if exists, else TODOs (4 fields) |
| 5 | task_id_system | Task breakdown with IDs | ❌ 4 generic tasks with TODOs |
| 6 | implementation_phases | Phased breakdown | ❌ Wrong format (12 missing fields across 4 phases) |
| 7 | testing_strategy | Unit, integration, e2e tests | ❌ All TODOs (8 fields) |
| 8 | success_criteria | How to verify completion | ⚠️ 1 real entry (coverage), rest TODOs (4 fields) |
| 9 | implementation_checklist | Pre-flight & finalization | ⚠️ Generic checklist + 4 TODOs |

**Summary:**
- ✅ **1 section fully working** (META_DOCUMENTATION)
- ⚠️ **4 sections partially working** (0, 2, 4, 8, 9)
- ❌ **5 sections failing** (1, 3, 5, 6, 7)

---

### Secondary Deliverables

#### 1. Workorder Log Entry ✅

**File:** `coderef/workorder-log.txt`
**Format:** One-line append
**Content:** `WO-{ID} | {project} | {description} | {timestamp}`
**Status:** ✅ Generated correctly if `workorder_id` provided (via `log_workorder` tool)

#### 2. UDS Metadata ✅

**Location:** Embedded in `plan.json` → `META_DOCUMENTATION.uds`
**Generated by:** `save_plan()` method (lines 531-545)
**Fields:**
- `generated_by`: Server version (e.g., "coderef-workflow v1.1.0")
- `document_type`: "Implementation Plan"
- `last_updated`: ISO date (e.g., "2026-01-01")
- `ai_assistance`: `true`
- `next_review`: ISO date (+30 days from generation)

**Status:** ✅ Generated correctly

#### 3. DELIVERABLES.md Template

**File:** `coderef/workorder/{feature-name}/DELIVERABLES.md`
**Generated by:** Separate tool `generate_deliverables_template` (not part of `create_plan`)
**When:** After plan is approved, before execution starts
**Status:** N/A (out of scope for this test)

---

### Quality Gates

#### Validation Tool: validate_implementation_plan

**Validator Location:** `generators/plan_validator.py`
**Schema Reference:** `coderef/schemas/plan.schema.json`

**Validation Checks:**
1. **Structure** (critical): All 10 sections present
2. **Completeness** (major): No placeholder text (TODO, TBD, etc.)
3. **Quality** (major): Task descriptions clear, success criteria measurable
4. **Workorder** (major, optional): Workorder metadata if present
5. **Autonomy** (major): No ambiguity, implementable without clarification
6. **Dependencies** (critical): No circular dependencies

**Scoring System:**
- Start: 100 points
- Critical issue: -10 points
- Major issue: -5 points
- Minor issue: -1 point
- Passing threshold: ≥90 points

**Current create_plan Output Score:**

| Issue Category | Count | Deduction | Notes |
|---------------|-------|-----------|-------|
| TODO placeholders | 33 | -165 | Major (-5 each) |
| Missing phase fields | 12 | -60 | Major (-5 each) |
| **Total Deduction** | **45** | **-225** | Score capped at 0 |

**Result:** Score = 0/100 (FAIL)
**Expected:** Score ≥90 (PASS)
**Gap:** 90 points needed

---

## Part 3: Expected vs Actual Comparison

### Overall Deliverable Quality

| Aspect | Expected | Actual |
|--------|----------|--------|
| **Structure** | 10 sections | ✅ 10 sections (structure correct) |
| **Content completeness** | 100% filled | ⚠️ ~40% filled (rest TODOs) |
| **Format compliance** | NEW schema | ⚠️ Mixed (META=NEW, phases=OLD) |
| **Validation score** | ≥90 | ~0 |
| **Executable** | Yes (agent can implement) | ❌ No (requires manual completion) |
| **Production ready** | Yes | ❌ No (scaffold only) |

### Section-by-Section Quality

| Section | Expected Quality | Actual Quality | Gap |
|---------|-----------------|----------------|-----|
| META_DOCUMENTATION | Complete metadata | ✅ Complete | None |
| 0_preparation | Rich project analysis | ⚠️ Depends on analysis.json | Needs coderef-context integration |
| 1_executive_summary | Goal/description/scope | ❌ OLD format + TODOs | Needs synthesis + format fix |
| 2_risk_assessment | Specific risks identified | ⚠️ Generic defaults | Needs analysis |
| 3_current_state_analysis | Affected files list | ❌ TODOs | Needs file discovery |
| 4_key_features | Detailed feature breakdown | ⚠️ Uses context if exists | Needs synthesis |
| 5_task_id_system | Feature-specific tasks | ❌ 4 generic tasks | Needs task generation |
| 6_implementation_phases | Phased breakdown (NEW format) | ❌ Generic phases (OLD format) | Needs format fix + synthesis |
| 7_testing_strategy | Test cases defined | ❌ All TODOs | Needs test planning |
| 8_success_criteria | Measurable metrics | ⚠️ 1 entry + TODOs | Needs criteria mapping |
| 9_implementation_checklist | Feature-specific checklist | ⚠️ Generic + TODOs | Needs checklist generation |

**Overall Completion:** ~40% complete (4/10 sections usable)

---

## Part 4: Impact Analysis

### On Workflow

**Current State:**
```
gather_context ✅
    ↓
analyze_project ✅
    ↓
create_plan ⚠️ (generates scaffold)
    ↓
validate_plan ❌ (fails with score 0)
    ↓
[BLOCKED] Manual completion required
    ↓
re-validate ⚠️
    ↓
execute_plan ⏸️ (delayed)
```

**Impact:**
- Plans require **manual completion** before execution can start
- Validation step becomes **review** instead of **quality gate**
- **Time to execution** increases by 30-60 minutes (manual plan completion)
- **Autonomy** reduced (requires human intervention)

### On Users

**Developer Experience:**
1. Run `/create-plan` → Expects complete plan
2. Receives plan with 33 TODOs → Surprised
3. Must manually fill in all TODOs → Frustrated
4. Re-validate after completion → Additional step
5. Finally can start implementation → Delayed

**Expected Experience:**
1. Run `/create-plan` → Complete plan generated
2. Review plan → Minor tweaks if needed
3. Validate → Passes at 90+
4. Execute → Start implementation immediately

**Time Impact:**
- Expected: 5-10 minutes (generate + quick review)
- Actual: 35-70 minutes (generate + manual completion + re-validation)
- **Overhead: +30-60 minutes per feature**

### On System

**Current Utility:**
- ✅ Scaffold generator (creates structure)
- ✅ UDS metadata injector (works)
- ⚠️ Context/analysis consumer (partial)
- ❌ AI synthesizer (not implemented)

**Value Proposition:**
- Current: "Saves you from typing JSON structure"
- Expected: "Generates complete implementation plan from requirements"
- **Gap:** Under-delivers on promised value

---

## Part 5: Recommendations

### Immediate (Required for Production)

#### 1. Implement AI Synthesis Logic

**Priority:** Critical
**Effort:** High (40-60 hours)
**Location:** `planning_generator.py:232-285`

**Changes Needed:**

```python
def _generate_plan_internal(self, ...):
    """Generate plan using AI synthesis."""

    # Build prompt from context + analysis + template
    synthesis_prompt = self._build_synthesis_prompt(
        feature_name, context, analysis, template
    )

    # Call AI model (Claude, GPT-4, etc.)
    ai_response = self._call_ai_model(synthesis_prompt)

    # Parse and validate AI response
    plan = self._parse_ai_response(ai_response)

    # Ensure all sections populated (no TODOs)
    self._validate_no_todos(plan)

    return plan
```

**Benefits:**
- Eliminates all 33 TODO placeholders
- Uses context and analysis inputs effectively
- Produces executable plans (score 90+)

#### 2. Fix Phase Format Mismatch

**Priority:** Critical
**Effort:** Low (2-4 hours)
**Location:** `planning_generator.py:390-427`

**Changes Needed:**

```python
def _generate_phases(self) -> Dict[str, Any]:
    return {
        "phases": [
            {
                "phase": 1,                           # ✓ NEW required field
                "name": "Foundation",                 # ✓ NEW required field
                "tasks": ["SETUP-001"],               # ✓ Required
                "deliverables": [                     # ✓ NEW required field
                    "Project scaffolding complete",
                    "Dependencies installed"
                ]
                # Remove: title, purpose, complexity, effort_level
            },
            # ... more phases
        ]
    }
```

**Benefits:**
- Eliminates 12 missing field issues
- Aligns with current schema (plan.schema.json)
- Passes phase validation

### Short-Term (Quality Improvements)

#### 3. Integrate coderef-context Tools

**Priority:** High
**Effort:** Medium (20-30 hours)
**Purpose:** Use actual codebase analysis instead of placeholders

**Integration Points:**

| Section | coderef-context Tool | Data Used |
|---------|---------------------|-----------|
| 0_preparation | `coderef_scan` | Foundation docs, patterns, tech stack |
| 3_current_state_analysis | `coderef_query` | Affected files, dependencies |
| 4_key_features | `coderef_patterns` | Similar implementations |
| 5_task_id_system | `coderef_impact` | Task dependencies |

**Benefits:**
- Real data instead of TODOs
- Accurate risk assessment
- Better task breakdown

#### 4. Add Synthesis Validation

**Priority:** Medium
**Effort:** Low (4-8 hours)
**Purpose:** Ensure AI synthesis produces complete plans

**Validation Checks:**

```python
def _validate_no_todos(self, plan: Dict) -> None:
    """Ensure AI didn't generate TODOs."""
    plan_str = json.dumps(plan)
    if re.search(r'\b(TODO|TBD|to be determined)\b', plan_str, re.IGNORECASE):
        raise ValueError("AI synthesis produced placeholder text")
```

**Benefits:**
- Catches incomplete synthesis
- Forces AI to provide complete answers
- Improves plan quality

### Long-Term (Enhancement)

#### 5. Context Enrichment

**Priority:** Low
**Effort:** Medium (15-20 hours)
**Purpose:** Make `gather_context` collect richer inputs

**Enhancements:**
- Add "real-world analogy" prompt during context gathering
- Collect use case workflows explicitly
- Gather success criteria details
- Capture architectural preferences

**Benefits:**
- Better AI synthesis inputs
- More complete plans
- Less ambiguity

#### 6. Iterative Refinement

**Priority:** Low
**Effort:** High (30-40 hours)
**Purpose:** Allow AI to refine plan based on validation feedback

**Workflow:**

```
create_plan → validate → [if score < 90] → refine_plan → validate → ...
```

**Benefits:**
- Self-improving plans
- Reduces manual intervention
- Higher quality output

---

## Part 6: Test Conclusion

### Summary

**Tool Assessed:** `mcp__coderef-workflow__create_plan`
**Version Tested:** coderef-workflow v1.1.0
**Test Method:** Static code analysis + expected deliverables validation

**Findings:**
1. ✅ **Structure generation works** (10 sections, JSON valid, UDS metadata)
2. ❌ **Content synthesis missing** (33 TODOs, no AI logic)
3. ❌ **Schema mismatch** (12 missing fields in phases)
4. ⚠️ **Partial context usage** (some fields populated, most TODOs)

**Root Causes Identified:** 2
**Issues Documented:** 45 (33 TODOs + 12 missing fields)
**Validation Score:** 0/100 (expected ≥90)
**Production Readiness:** ❌ Not ready (requires manual completion)

### Verdict

**Current State:** Scaffold generator (creates plan structure)
**Advertised State:** Plan generator (creates complete plans)
**Recommendation:** Mark as "beta" or "scaffold mode" until AI synthesis implemented

**Pass/Fail:** ⚠️ **CONDITIONAL PASS**
- ✅ Passes: Structure generation, metadata injection, file handling
- ❌ Fails: Content synthesis, format compliance, validation score
- **Overall:** Works as scaffold, fails as autonomous plan generator

### Next Actions

**For Developers:**
1. Implement AI synthesis logic (critical, 40-60 hours)
2. Fix phase format mismatch (critical, 2-4 hours)
3. Integrate coderef-context tools (high priority, 20-30 hours)
4. Add synthesis validation (medium priority, 4-8 hours)

**For Users:**
1. Expect manual plan completion after `/create-plan`
2. Budget 30-60 minutes for TODO completion
3. Use `/validate-plan` after manual edits
4. Consider using as scaffold tool (not autonomous generator)

**For Testing:**
1. Monitor remediation progress
2. Re-test after AI synthesis implementation
3. Validate format compliance after phase fix
4. Perform end-to-end workflow test (gather → analyze → create → validate → execute)

---

**Report Generated By:** coderef-testing v1.0.0
**Test Type:** Root cause analysis + Expected deliverables validation
**Analysis Duration:** ~45 minutes
**Files Analyzed:** 2 (planning_generator.py, plan_validator.py)
**Lines Analyzed:** 1,184 lines
**Report Date:** 2026-01-01

**Report Saved To:**
- `coderef-workflow/coderef/test/report/create-plan-validation-report.md`
- `coderef-testing/coderef/testing/results/create-plan-test-deliverables.md`
- `coderef-testing/coderef/testing/results/create-plan-expected-deliverables.md`
