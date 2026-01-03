# PLAN-VALIDATOR.md - plan_validator.py Authoritative Reference

**File:** `generators/plan_validator.py`
**Category:** Planning & Quality Assurance
**Lines:** 622
**Version:** 1.2.0
**Status:** ✅ Production
**Generated:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-P0-001

---

## 1. Purpose & Scope

**What It Does:**
`plan_validator.py` validates implementation plans against schema and quality checklist, scoring them 0-100 based on completeness, quality, and autonomy. Enables iterative review loop until score >= 90 (approval threshold).

**Key Innovation:**
Single source of truth validation - validates against `plan.schema.json` for structure + quality checklist for content. Returns detailed issues by severity (critical/major/minor) with fix suggestions.

**What It Returns:**
`ValidationResultDict` with score, issues list, checklist results, and approval boolean

**Dependencies:**
- **plan.schema.json** (coderef/schemas/) - Plan structure schema
- **type_defs.py** - `ValidationResultDict`, `ValidationIssueDict` types
- **logger_config.py** - Logging utilities

**Core Workflow:**
```
PlanValidator.validate()
├─ 1. Load plan.json file
├─ 2. Load plan.schema.json (cached)
├─ 3. validate_structure() - Check 10 required sections
├─ 4. validate_completeness() - No placeholders, valid task IDs
├─ 5. validate_quality() - Content quality checks
├─ 6. validate_workorder() - Optional workorder_id validation
├─ 7. validate_autonomy() - Implementation details for agents
├─ 8. Check circular dependencies in phases
├─ 9. calculate_score() - 0-100 scoring
├─ 10. determine_result() - "excellent"/"good"/"needs work"/"poor"
└─ 11. Return ValidationResultDict

Scoring breakdown:
- Structure: 30% (all 10 sections present)
- Completeness: 25% (no placeholders, valid IDs)
- Quality: 25% (detailed content, examples)
- Autonomy: 20% (actionable steps, clear dependencies)
```

**Performance:**
- Validation: ~50-100ms (for typical plan)
- Schema loading: ~10ms (cached after first load)
- Total: ~100-200ms

---

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **plan_path** | PlanValidator instance | Path | Constructor argument | `self.plan_path = plan_path` |
| **plan_data** | PlanValidator instance | Dict | Loaded from disk | plan.json file |
| **issues** | PlanValidator instance | List[ValidationIssueDict] | Ephemeral (collected during validation) | Accumulated during validate() |
| **_schema** | PlanValidator instance | Dict (cached) | Loaded once, reused | plan.schema.json file |
| **plan.schema.json** | External (project) | JSON file | Disk (coderef/schemas/) | Plan structure definition |

**Key Insight:** PlanValidator is **stateful** for one validation run - loads plan_data and accumulates issues. For new plan, create new instance.

---

## 3. Architecture & Data Flow

### Class Structure

```
PlanValidator
├─ __init__(plan_path: Path)
├─ validate() → ValidationResultDict (main entry point)
├─ _load_plan() (reads plan.json)
├─ _load_schema() → Optional[Dict] (reads plan.schema.json, cached)
├─ validate_structure() (checks 10 required sections)
├─ validate_completeness() (no placeholders, valid task IDs)
│  ├─ _validate_task_ids(phases_data)
│  └─ _validate_no_circular_dependencies(phases_data)
├─ validate_quality() (content quality checks)
├─ validate_workorder() (optional workorder_id validation)
├─ validate_autonomy() (actionable steps, clear dependencies)
├─ calculate_score() → int (0-100 scoring)
├─ determine_result(score) → str ("excellent"/"good"/"needs work"/"poor")
└─ _build_checklist_results() → Dict (detailed checklist breakdown)
```

### Validation Result Structure

```python
ValidationResultDict = {
    "validation_result": "excellent",  # or "good", "needs work", "poor"
    "score": 95,  # 0-100
    "issues": [
        {
            "severity": "critical",  # or "major", "minor"
            "section": "structure",  # or "completeness", "quality", "autonomy"
            "issue": "Missing section 0_preparation",
            "suggestion": "Add section 0_preparation to UNIVERSAL_PLANNING_STRUCTURE"
        },
        ...
    ],
    "checklist_results": {
        "structure": {"passed": 9, "failed": 1, "score": 90},
        "completeness": {"passed": 8, "failed": 2, "score": 80},
        "quality": {"passed": 10, "failed": 0, "score": 100},
        "autonomy": {"passed": 7, "failed": 3, "score": 70}
    },
    "approved": true  # true if score >= 90
}
```

### Scoring Algorithm

```python
def calculate_score() -> int:
    # Count issues by severity
    critical_count = len([i for i in issues if i['severity'] == 'critical'])
    major_count = len([i for i in issues if i['severity'] == 'major'])
    minor_count = len([i for i in issues if i['severity'] == 'minor'])

    # Deduct points based on severity
    score = 100
    score -= critical_count * 20  # Critical: -20 points each
    score -= major_count * 10     # Major: -10 points each
    score -= minor_count * 5      # Minor: -5 points each

    return max(0, score)  # Clamp to 0-100
```

---

## 4. Method Catalog & Contracts

### 4.1 Constructor

```python
def __init__(self, plan_path: Path)
```

**Args:**
- `plan_path` (Path): Absolute path to plan.json file

**Side Effects:**
- Sets `self.plan_path`
- Initializes `self.plan_data = None`
- Initializes `self.issues = []`
- Initializes `self._schema = None`

**Performance:** <1ms

---

### 4.2 Main Validation Method

```python
def validate(self) -> ValidationResultDict
```

**Purpose:** Main entry point - orchestrates all validation checks

**Workflow:**
1. Load plan.json file (`_load_plan()`)
2. Load plan.schema.json (`_load_schema()`, cached)
3. Run 5 validators (structure, completeness, quality, workorder, autonomy)
4. Check circular dependencies
5. Calculate score (0-100)
6. Determine result ("excellent"/"good"/"needs work"/"poor")
7. Build checklist results
8. Return `ValidationResultDict`

**Returns:** `ValidationResultDict` with score, issues, checklist, approval

**Performance:** ~100-200ms (for typical plan)

**Example:**
```python
validator = PlanValidator(Path("plan.json"))
result = validator.validate()

print(result['score'])  # 95
print(result['validation_result'])  # "excellent"
print(result['approved'])  # True
```

---

### 4.3 Plan Loader

```python
def _load_plan(self)
```

**Purpose:** Loads and parses plan.json file

**Side Effects:** Sets `self.plan_data`

**Raises:**
- `ValueError`: If JSON is malformed
- `FileNotFoundError`: If plan file doesn't exist

**Performance:** ~10-20ms (single file read)

---

### 4.4 Schema Loader (Cached)

```python
def _load_schema(self) -> Optional[Dict[str, Any]]
```

**Purpose:** Loads plan.schema.json from `coderef/schemas/plan.schema.json`

**Caching:** Loads once, stores in `self._schema`, returns cached on subsequent calls

**Returns:**
- `Dict`: Schema data if file exists
- `None`: If file missing or malformed (logs warning, doesn't raise)

**File Path:** `{project_root}/coderef/schemas/plan.schema.json`

**Performance:**
- First call: ~10ms (file read)
- Subsequent calls: <1ms (cached)

---

### 4.5 Structure Validator

```python
def validate_structure(self)
```

**Purpose:** Validates plan has all required sections

**Checks:**
1. META_DOCUMENTATION section exists
2. UNIVERSAL_PLANNING_STRUCTURE section exists
3. All 10 required sections (0-9) exist within UNIVERSAL_PLANNING_STRUCTURE

**Required Sections:**
```python
REQUIRED_SECTIONS = [
    "0_preparation",
    "1_executive_summary",
    "2_risk_assessment",
    "3_current_state_analysis",
    "4_key_features",
    "5_task_id_system",
    "6_implementation_phases",
    "7_testing_strategy",
    "8_success_criteria",
    "9_implementation_checklist"
]
```

**Issues Generated:**
- Missing META_DOCUMENTATION → Critical
- Missing UNIVERSAL_PLANNING_STRUCTURE → Critical
- Missing any section (0-9) → Critical

**Performance:** ~1-5ms

---

### 4.6 Completeness Validator

```python
def validate_completeness(self)
```

**Purpose:** Validates no placeholders, all task IDs valid

**Checks:**
1. No placeholder text (TBD, TODO, [placeholder], Coming soon, Fill this in, to be determined)
2. All task IDs are unique
3. All task dependencies reference existing tasks
4. No circular dependencies (via `_validate_no_circular_dependencies()`)

**Placeholder Detection:**
Uses regex: `r'\b(TBD|TODO|\[placeholder\]|Coming soon|Fill this in|to be determined)\b'`

**Issues Generated:**
- Placeholder text found → Major
- Duplicate task ID → Critical
- Invalid dependency (non-existent task) → Critical
- Circular dependency → Critical

**Performance:** ~10-20ms (regex scan + dependency graph analysis)

---

### 4.7 Task ID Validator (Helper)

```python
def _validate_task_ids(self, phases_data)
```

**Purpose:** Validates task IDs are unique and dependencies are valid

**Algorithm:**
1. Extract all task IDs from all phases
2. Check for duplicates (same ID in multiple tasks)
3. Extract all dependencies (depends_on fields)
4. Verify each dependency references an existing task ID

**Issues Generated:**
- Duplicate task ID → Critical
- Dependency on non-existent task → Critical

**Performance:** ~5-10ms (traverses all tasks)

---

### 4.8 Circular Dependency Detector

```python
def _validate_no_circular_dependencies(self, phases_data)
```

**Purpose:** Detects circular dependencies using DFS

**Algorithm:**
1. Build adjacency list (graph) from task dependencies
2. Run DFS on each task
3. Track visited nodes and recursion stack
4. If node already in recursion stack → cycle detected

**Example Circular Dependency:**
```
Task A depends on Task B
Task B depends on Task C
Task C depends on Task A  # ← Circular!
```

**Issues Generated:**
- Circular dependency detected → Critical (with cycle path)

**Performance:** ~10-20ms (graph traversal)

---

### 4.9 Quality Validator

```python
def validate_quality(self)
```

**Purpose:** Validates content quality (detailed descriptions, examples)

**Checks:**
1. Executive summary has required fields (goal, description, scope)
2. Risk assessment sections are non-empty
3. Tasks have detailed descriptions (>20 chars)
4. Success criteria are specific (not vague)
5. Testing strategy covers all test levels (unit, integration, e2e)

**Issues Generated:**
- Missing required field in executive summary → Major
- Empty risk assessment section → Major
- Task description too short (<20 chars) → Minor
- Vague success criteria → Minor
- Missing test level → Minor

**Performance:** ~10-20ms (content checks)

---

### 4.10 Workorder Validator (Optional)

```python
def validate_workorder(self)
```

**Purpose:** Validates workorder_id format (if present)

**Optional:** Only runs if `META_DOCUMENTATION.workorder_id` exists

**Format:** `WO-{FEATURE}-{CATEGORY}-{SEQUENCE}`
- Example: `WO-AUTH-SYSTEM-001`
- Regex: `^WO-[A-Z0-9-]+-\d{3}$`

**Issues Generated:**
- Invalid workorder_id format → Minor (doesn't block approval)

**Performance:** ~1ms (regex match)

---

### 4.11 Autonomy Validator

```python
def validate_autonomy(self)
```

**Purpose:** Validates plan provides enough detail for autonomous implementation

**Checks:**
1. Tasks have clear, actionable steps (not vague like "implement feature")
2. Dependencies are explicit (no missing dependencies)
3. Phase structure is logical (setup → implementation → testing → deployment)
4. Implementation checklist has all 3 phases (pre/during/post)

**Issues Generated:**
- Vague task description → Minor
- Missing dependency (task references other tasks but no depends_on) → Major
- Illogical phase order → Major
- Missing checklist phase → Minor

**Performance:** ~10-20ms (content analysis)

---

### 4.12 Score Calculator

```python
def calculate_score(self) -> int
```

**Purpose:** Calculates 0-100 score based on issues

**Scoring Formula:**
```python
score = 100
score -= critical_count * 20  # Critical: -20 points each
score -= major_count * 10     # Major: -10 points each
score -= minor_count * 5      # Minor: -5 points each
return max(0, score)  # Clamp to 0-100
```

**Examples:**
- 0 issues → 100 (perfect)
- 1 critical → 80
- 2 major → 80
- 3 minor → 85
- 1 critical + 2 major + 3 minor → 45 (needs work)

**Performance:** <1ms (simple arithmetic)

---

### 4.13 Result Determiner

```python
def determine_result(self, score: int) -> str
```

**Purpose:** Maps score to result category

**Thresholds:**
- 90-100 → "excellent" (approved)
- 75-89 → "good" (near approval)
- 50-74 → "needs work" (significant issues)
- 0-49 → "poor" (major rework needed)

**Performance:** <1ms

---

### 4.14 Checklist Results Builder

```python
def _build_checklist_results(self) -> Dict[str, Dict[str, int]]
```

**Purpose:** Builds detailed breakdown of checks by category

**Returns:**
```python
{
    "structure": {"passed": 9, "failed": 1, "score": 90},
    "completeness": {"passed": 8, "failed": 2, "score": 80},
    "quality": {"passed": 10, "failed": 0, "score": 100},
    "autonomy": {"passed": 7, "failed": 3, "score": 70}
}
```

**Calculation:**
- Count issues by section (structure/completeness/quality/autonomy)
- Calculate score per section: `(passed / (passed + failed)) * 100`

**Performance:** ~1-5ms

---

## 5. Integration Points

### 5.1 With plan_generator

**Input:** plan.json (generated by PlanningGenerator)
**Usage:** Validates generated plan before saving/approving

---

### 5.2 With review_formatter

**Output:** ValidationResultDict
**Consumer:** ReviewFormatter reads ValidationResultDict and generates markdown review report

---

### 5.3 With execute_plan

**Check:** Plan must be approved (score >= 90) before execution
**Usage:** execute_plan checks `ValidationResultDict.approved` before proceeding

---

## 6. Performance Characteristics

### Timing Breakdown

| Operation | Time | Bottleneck |
|-----------|------|------------|
| _load_plan() | ~10-20ms | File I/O |
| _load_schema() (first) | ~10ms | File I/O |
| _load_schema() (cached) | <1ms | Memory lookup |
| validate_structure() | ~1-5ms | Dict traversal |
| validate_completeness() | ~10-20ms | Regex + graph |
| validate_quality() | ~10-20ms | Content checks |
| validate_workorder() | ~1ms | Regex |
| validate_autonomy() | ~10-20ms | Content analysis |
| calculate_score() | <1ms | Arithmetic |
| determine_result() | <1ms | Conditional |
| _build_checklist_results() | ~1-5ms | Issue aggregation |
| **Total** | **~100-200ms** | File I/O + regex |

### Memory Usage

- Plan data: ~50-200 KB (in-memory)
- Schema: ~30-50 KB (cached)
- Issues list: ~5-20 KB (ephemeral)
- **Peak memory:** ~100-300 KB per validation

---

## 7. Error Handling & Recovery

### Error Scenarios

1. **plan.json missing** → FileNotFoundError
2. **plan.json malformed** → ValueError (JSON decode error)
3. **plan.schema.json missing** → Warning logged, validation continues (degrades gracefully)
4. **Empty plan.json** → ValidationResultDict with score 0 (all structure checks fail)

### Recovery Paths

```python
# Graceful degradation
def _load_schema() -> Optional[Dict]:
    try:
        return json.load(schema_file)
    except Exception as e:
        logger.warning(f"Could not load schema: {e}")
        return None  # Validation continues without schema
```

---

## 8. Common Pitfalls & Gotchas

### Pitfall 1: Stateful Validator Instance
**Problem:** Reusing same PlanValidator instance for multiple plans
**Impact:** Issues from previous validation accumulate
**Solution:** Create new instance per plan

**Example:**
```python
# ❌ Wrong - issues accumulate
validator = PlanValidator(plan1_path)
result1 = validator.validate()
result2 = validator.validate()  # result2 has issues from result1!

# ✅ Correct - new instance per plan
validator1 = PlanValidator(plan1_path)
result1 = validator1.validate()
validator2 = PlanValidator(plan2_path)
result2 = validator2.validate()
```

### Pitfall 2: Missing plan.schema.json
**Problem:** Schema file missing, validation degrades gracefully
**Detection:** Check logs for "Could not load plan schema" warning
**Solution:** Ensure `coderef/schemas/plan.schema.json` exists

### Pitfall 3: Approval Threshold Hardcoded
**Problem:** Approval threshold is hardcoded at 90
**Impact:** Can't adjust threshold without code change
**Workaround:** Check score manually, set custom threshold

### Pitfall 4: Legacy vs New Executive Summary Format
**Problem:** Validator supports both OLD and NEW formats
**Impact:** Plans with either format pass validation
**Clarification:** NEW format preferred (goal, description, scope)

---

## 9. Testing Strategy

### Unit Tests
- Test each validator method independently
- Mock plan_data with known issues
- Verify issues list has expected entries
- Test score calculation with various issue combinations

### Integration Tests
- Test with real plan.json files
- Validate end-to-end validation flow
- Test with valid plan (score 100)
- Test with invalid plan (score <50)

### Edge Cases
- Empty plan.json → Score 0
- Plan with all critical issues → Score 0
- Plan with all minor issues → Score 70-80
- Circular dependency → Critical issue

---

## 10. Version History

### v1.2.0 - Current
- ✅ Workorder ID validation (optional)
- ✅ Circular dependency detection
- ✅ Schema caching for performance
- ✅ Checklist results breakdown

### v1.0.0 - Initial Release
- ✅ Structure validation (10 required sections)
- ✅ Completeness validation (no placeholders, valid task IDs)
- ✅ Quality validation (content checks)
- ✅ Autonomy validation (actionable steps)
- ✅ 0-100 scoring system

---

## 11. Usage Examples

### Example 1: Basic Validation

```python
from pathlib import Path
from generators.plan_validator import PlanValidator

plan_path = Path("coderef/workorder/dark-mode-toggle/plan.json")
validator = PlanValidator(plan_path)
result = validator.validate()

print(f"Score: {result['score']}/100")
print(f"Result: {result['validation_result']}")
print(f"Approved: {result['approved']}")
print(f"Issues: {len(result['issues'])}")
```

### Example 2: Iterative Review Loop

```python
# AI agent validates plan, refines based on feedback, re-validates
score = 0
attempts = 0

while score < 90 and attempts < 3:
    validator = PlanValidator(plan_path)
    result = validator.validate()
    score = result['score']

    if score < 90:
        # Refine plan based on issues
        for issue in result['issues']:
            print(f"[{issue['severity']}] {issue['issue']}")
            print(f"  Fix: {issue['suggestion']}")

        # AI refines plan...
        attempts += 1

if score >= 90:
    print("✅ Plan approved!")
else:
    print(f"⚠️ Plan needs work (score: {score}/100)")
```

### Example 3: Generate Review Report

```python
from generators.review_formatter import ReviewFormatter

validator = PlanValidator(plan_path)
result = validator.validate()

formatter = ReviewFormatter()
review_md = formatter.format_review(result)

# Save to file
review_path = plan_path.parent / "review-report.md"
review_path.write_text(review_md)
```

---

## 12. Related Files

- **generators/planning_generator.py** - Produces plan.json to be validated
- **generators/review_formatter.py** - Consumes ValidationResultDict to generate review reports
- **coderef/schemas/plan.schema.json** - Schema source of truth
- **type_defs.py** - ValidationResultDict, ValidationIssueDict types
- **tool_handlers.py:handle_validate_implementation_plan()** - MCP tool wrapper

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P0-001
**Task:** SHEET-005
**Timestamp:** 2026-01-02
