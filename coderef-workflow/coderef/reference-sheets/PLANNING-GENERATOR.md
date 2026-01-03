# PLANNING-GENERATOR.md - planning_generator.py Authoritative Reference

**File:** `generators/planning_generator.py`
**Category:** Planning & Synthesis Engine
**Lines:** 699
**Version:** 1.2.0
**Status:** ✅ Production
**Generated:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-P0-001

---

## 1. Purpose & Scope

**What It Does:**
`planning_generator.py` is the plan synthesis engine that creates complete 10-section implementation plans by combining context.json (requirements), analysis.json (project structure), and planning-template-for-ai.json (structure).

**Key Innovation:**
Batch mode plan generation - synthesizes all 10 sections in a single operation instead of step-by-step prompting. Saves partial plans with TODOs if generation fails.

**What It Returns:**
Complete `plan.json` with META_DOCUMENTATION + UNIVERSAL_PLANNING_STRUCTURE (10 sections)

**Dependencies:**
- **context.json** (from gather_context) - Feature requirements & constraints
- **analysis.json** (from planning_analyzer) - Project structure & patterns
- **planning-template-for-ai.json** (MCP server) - AI-optimized template
- **constants.py** - `Paths`, `Files` enums
- **logger_config.py** - Logging utilities
- **uds_helpers.py** - `get_server_version()`

**Core Workflow:**
```
PlanningGenerator.generate_plan()
├─ 1. Validate feature_name (alphanumeric, hyphens, underscores only)
├─ 2. Load context.json (requirements) - optional
├─ 3. Load analysis.json (project structure) - optional
├─ 4. Load planning-template-for-ai.json (structure)
├─ 5. Generate plan (_generate_plan_internal with retry)
│  ├─ META_DOCUMENTATION section
│  └─ UNIVERSAL_PLANNING_STRUCTURE (10 sections)
│     ├─ 0_preparation (from analysis)
│     ├─ 1_executive_summary (from context)
│     ├─ 2_risk_assessment (from context + analysis)
│     ├─ 3_current_state_analysis (from analysis)
│     ├─ 4_key_features (from context)
│     ├─ 5_task_id_system (generated)
│     ├─ 6_implementation_phases (generated)
│     ├─ 7_testing_strategy (generated)
│     ├─ 8_success_criteria (from context)
│     └─ 9_implementation_checklist (generated)
└─ 6. Save to coderef/workorder/{feature}/plan.json

If generation fails:
└─ Create partial plan with TODOs → Save → Raise error
```

**Performance:**
- Plan generation: ~2-5 seconds (10-section synthesis)
- File I/O: ~50-100ms (load 3 files, save 1)
- Total: ~3-6 seconds per feature

---

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **project_path** | PlanningGenerator instance | Path | Constructor argument | `self.project_path = project_path` |
| **context_dir** | PlanningGenerator instance | Path | Constructor (derived) | `server_root / "coderef" / "context"` |
| **template_file** | PlanningGenerator instance | Path | Constructor (derived) | `context_dir / "planning-template-for-ai.json"` |
| **Generated plan** | generate_plan() | Dict | Return value → saved to plan.json | Synthesized from context + analysis + template |
| **context.json** | External (gather_context) | JSON file | Disk (coderef/workorder/{feature}/) | Feature requirements |
| **analysis.json** | External (planning_analyzer) | JSON file | Disk (coderef/workorder/{feature}/) | Project analysis |
| **planning-template-for-ai.json** | MCP server | JSON file | Disk (MCP server coderef/context/) | Plan structure template |

**Key Insight:** PlanningGenerator is **stateless** - it owns only paths. Plans are generated fresh on each call, no caching.

---

## 3. Architecture & Data Flow

### Class Structure

```
PlanningGenerator
├─ __init__(project_path: Path)
├─ validate_feature_name(feature_name: str) → str (sanitizes input)
├─ load_context(feature_name: str) → Optional[Dict] (reads context.json)
├─ load_analysis(feature_name: str) → Optional[Dict] (reads analysis.json)
├─ load_template() → Dict (reads planning-template-for-ai.json)
├─ generate_plan(feature_name, context, analysis, workorder_id) → Dict
│  └─ Main entry point (orchestrates generation with retry)
├─ _generate_plan_internal(...) → Dict (internal synthesis logic)
│  ├─ _generate_preparation_section() → Dict
│  ├─ _generate_executive_summary() → Dict
│  ├─ _generate_risk_assessment() → Dict
│  ├─ _generate_current_state() → Dict
│  ├─ _generate_key_features() → Dict
│  ├─ _generate_tasks() → Dict
│  ├─ _generate_phases() → List[Dict]
│  ├─ _generate_testing_strategy() → Dict
│  ├─ _generate_success_criteria() → Dict
│  └─ _generate_checklist() → Dict
├─ _create_partial_plan(feature_name, error_msg) → Dict (fallback)
└─ save_plan(feature_name, plan) → Path (writes plan.json)
```

### Plan Structure

```json
{
  "META_DOCUMENTATION": {
    "feature_name": "new-feature",
    "workorder_id": "WO-NEW-FEATURE-001",
    "version": "1.0.0",
    "status": "planning",
    "generated_by": "PlanningGenerator",
    "has_context": true,
    "has_analysis": true
  },
  "UNIVERSAL_PLANNING_STRUCTURE": {
    "0_preparation": {...},        // From analysis.json
    "1_executive_summary": {...},  // From context.json
    "2_risk_assessment": {...},    // Combined
    "3_current_state_analysis": {...},  // From analysis.json
    "4_key_features": [...],       // From context.json
    "5_task_id_system": {...},     // Generated
    "6_implementation_phases": [...],  // Generated
    "7_testing_strategy": {...},   // Generated
    "8_success_criteria": {...},   // From context.json
    "9_implementation_checklist": {...}  // Generated
  }
}
```

### Retry Logic

```python
try:
    plan = _generate_plan_internal(...)  # First attempt
except Exception as e:
    logger.warning(f"First attempt failed: {e}. Retrying...")
    try:
        plan = _generate_plan_internal(...)  # Second attempt
    except Exception as retry_error:
        # Save partial plan with TODOs
        partial_plan = _create_partial_plan(feature_name, error_msg)
        save_plan(feature_name, partial_plan)
        raise ValueError(f"Plan generation failed. Partial plan saved.")
```

---

## 4. Method Catalog & Contracts

### 4.1 Constructor

```python
def __init__(self, project_path: Path)
```

**Args:**
- `project_path` (Path): Absolute path to project directory

**Side Effects:**
- Sets `self.project_path`
- Computes `self.context_dir` (MCP server directory, NOT user project)
- Computes `self.template_file` (planning-template-for-ai.json path)
- Logs initialization

**Important:** Template path is in **MCP server directory**, not user's project. This ensures template consistency across all projects.

**Performance:** <1ms

---

### 4.2 Feature Name Validator

```python
def validate_feature_name(self, feature_name: str) -> str
```

**Purpose:** Sanitizes feature name to prevent path traversal attacks

**Validation Rules:**
- Must be non-empty
- Only alphanumeric, hyphens, underscores allowed
- No path separators (`/`, `\`)
- Matches regex: `^[a-zA-Z0-9_-]+$`

**Returns:** Sanitized feature name (same as input if valid)

**Raises:** `ValueError` if invalid characters detected

**Security:** Logs security event on invalid input

**Example:**
```python
validate_feature_name("dark-mode-toggle")  # ✅ Valid
validate_feature_name("dark_mode")         # ✅ Valid
validate_feature_name("../../../etc")      # ❌ ValueError (path traversal)
validate_feature_name("my feature")        # ❌ ValueError (space not allowed)
```

**Performance:** <1ms

---

### 4.3 Context Loader

```python
def load_context(self, feature_name: str) -> Optional[Dict[str, Any]]
```

**Purpose:** Loads context.json for the feature (if exists)

**File Path:** `{project_path}/coderef/working/{feature_name}/context.json`

**Returns:**
- `Dict`: Context data if file exists and is valid JSON
- `None`: If file doesn't exist

**Raises:**
- `ValueError`: If file exists but is malformed JSON

**Logs:**
- `WARNING`: If file not found
- `INFO`: If file loaded successfully
- `ERROR`: If JSON decode fails

**Example:**
```python
context = generator.load_context("dark-mode-toggle")
# Returns:
{
    "description": "Add dark mode support",
    "goal": "Improve user experience",
    "requirements": ["Toggle button in settings", "Persist preference"],
    "constraints": ["Must work with existing theme system"]
}
```

**Performance:** ~10-20ms (single file read)

---

### 4.4 Analysis Loader

```python
def load_analysis(self, feature_name: str = None) -> Optional[Dict[str, Any]]
```

**Purpose:** Loads analysis.json from planning_analyzer

**File Path:** `{project_path}/coderef/workorder/{feature_name}/analysis.json`

**Returns:**
- `Dict`: Analysis data if file exists and is valid JSON
- `None`: If feature_name not provided or file doesn't exist

**Graceful Degradation:**
- If file malformed → Logs error, returns None (doesn't raise)
- If file missing → Logs debug, returns None

**Example:**
```python
analysis = generator.load_analysis("dark-mode-toggle")
# Returns PreparationSummaryDict from PlanningAnalyzer
{
    "foundation_docs": {...},
    "coding_standards": {...},
    "technology_stack": {...},
    ...
}
```

**Performance:** ~10-20ms (single file read)

---

### 4.5 Template Loader

```python
def load_template(self) -> Dict[str, Any]
```

**Purpose:** Loads AI-optimized planning template from MCP server

**File Path:** `{MCP_server_root}/coderef/context/planning-template-for-ai.json`

**Returns:** Template data dict

**Raises:**
- `FileNotFoundError`: If template file missing (critical error)
- `ValueError`: If template is malformed JSON

**Important:** Template must exist - it's bundled with MCP server, not user-provided

**Example:**
```python
template = generator.load_template()
# Returns:
{
    "_AI_INSTRUCTIONS": {...},
    "META_DOCUMENTATION": {...},
    "UNIVERSAL_PLANNING_STRUCTURE": {...}
}
```

**Performance:** ~10-20ms (single file read)

---

### 4.6 Main Plan Generator

```python
def generate_plan(
    self,
    feature_name: str,
    context: Optional[Dict[str, Any]] = None,
    analysis: Optional[Dict[str, Any]] = None,
    workorder_id: Optional[str] = None
) -> Dict[str, Any]
```

**Purpose:** Main entry point - generates complete 10-section implementation plan

**Workflow:**
1. Validate feature_name (sanitize input)
2. Load context.json if not provided (optional)
3. Load analysis.json if not provided (optional)
4. Load planning-template-for-ai.json (required)
5. Generate plan via `_generate_plan_internal()` with retry
6. Return complete plan dict

**Args:**
- `feature_name` (str): Feature name (validated)
- `context` (Optional[Dict]): Context data (or loads from file)
- `analysis` (Optional[Dict]): Analysis data (or loads from file)
- `workorder_id` (Optional[str]): Workorder ID for tracking

**Returns:** Complete plan dict with META_DOCUMENTATION + 10 sections

**Retry Logic:**
- First attempt fails → Log warning, retry once
- Second attempt fails → Create partial plan with TODOs, save, raise error

**Example:**
```python
generator = PlanningGenerator(project_path)
plan = generator.generate_plan(
    feature_name="dark-mode-toggle",
    workorder_id="WO-DARK-MODE-001"
)
# Returns complete plan.json structure
```

**Performance:** ~2-5 seconds (plan synthesis)

**Raises:** `ValueError` if both attempts fail (partial plan saved)

---

### 4.7 Internal Plan Generator

```python
def _generate_plan_internal(
    self,
    feature_name: str,
    context: Optional[Dict[str, Any]],
    analysis: Optional[Dict[str, Any]],
    template: Dict[str, Any],
    workorder_id: Optional[str] = None
) -> Dict[str, Any]
```

**Purpose:** Internal synthesis logic - combines inputs into complete plan

**NOTE:** Simplified implementation - in production, would use AI model (Claude) for synthesis.

**Current Behavior:** Creates skeleton plan structure by calling 10 section generators

**Returns:** Plan dict with META_DOCUMENTATION + UNIVERSAL_PLANNING_STRUCTURE

**Performance:** ~1-2 seconds (calls 10 section generators)

---

### 4.8 Section Generators (10 methods)

#### 4.8.1 Preparation Section (Section 0)

```python
def _generate_preparation_section(
    self, context: Optional[Dict], analysis: Optional[Dict]
) -> Dict[str, Any]
```

**Data Source:** Primarily from `analysis.json` (PlanningAnalyzer output)

**Returns:**
```python
{
    "foundation_docs": {"available": [...], "missing": [...]},
    "coding_standards": {"available": [...], "missing": [...]},
    "reference_components": {"primary": "...", "secondary": [...]},
    "key_patterns_identified": ["Pattern 1", ...],
    "technology_stack": {"languages": [...], "frameworks": [...], ...},
    "gaps_and_risks": ["Gap 1", ...]
}
```

**Fallback:** If no analysis → Returns placeholders with "Run /analyze-for-planning" messages

---

#### 4.8.2 Executive Summary (Section 1)

```python
def _generate_executive_summary(
    self, feature_name: str, context: Optional[Dict]
) -> Dict[str, Any]
```

**Data Source:** Primarily from `context.json` (gather_context output)

**Returns:**
```python
{
    "purpose": "...",  # From context.description
    "value_proposition": "...",  # From context.goal
    "real_world_analogy": "...",  # Generated
    "use_case": "...",  # Generated from context.requirements
    "output": "..."  # Summary of requirements
}
```

**Fallback:** If no context → Generates minimal structure from feature_name

---

#### 4.8.3 Risk Assessment (Section 2)

```python
def _generate_risk_assessment(
    self, context: Optional[Dict], analysis: Optional[Dict]
) -> Dict[str, Any]
```

**Data Source:** Combined from context + analysis

**Returns:**
```python
{
    "breaking_changes": "...",
    "security": "...",
    "performance": "...",
    "data_migration": "...",
    "rollback_strategy": "..."
}
```

---

#### 4.8.4 Current State Analysis (Section 3)

```python
def _generate_current_state(self, analysis: Optional[Dict]) -> Dict[str, Any]
```

**Data Source:** From `analysis.json`

**Returns:**
```python
{
    "existing_architecture": "...",
    "existing_patterns": [...],
    "constraints": [...]
}
```

---

#### 4.8.5 Key Features (Section 4)

```python
def _generate_key_features(self, context: Optional[Dict]) -> List[str]
```

**Data Source:** From `context.requirements`

**Returns:** List of requirement strings

---

#### 4.8.6 Task ID System (Section 5)

```python
def _generate_tasks(
    self, context: Optional[Dict], analysis: Optional[Dict]
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "format": "CATEGORY-NNN",
    "categories": {
        "SETUP": "Setup and configuration tasks",
        "IMPL": "Implementation tasks",
        ...
    }
}
```

---

#### 4.8.7 Implementation Phases (Section 6)

```python
def _generate_phases(self) -> List[Dict[str, Any]]
```

**Returns:** List of phase objects with tasks

**Structure:**
```python
[
    {
        "phase_id": "phase_1",
        "name": "Setup & Preparation",
        "tasks": [
            {
                "task_id": "SETUP-001",
                "description": "...",
                "status": "pending",
                "dependencies": [],
                "estimated_effort": "medium"
            },
            ...
        ],
        "dependencies": [],
        "parallel_capable": true
    },
    ...
]
```

---

#### 4.8.8 Testing Strategy (Section 7)

```python
def _generate_testing_strategy(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    "unit_tests": [...],
    "integration_tests": [...],
    "e2e_tests": [...]
}
```

---

#### 4.8.9 Success Criteria (Section 8)

```python
def _generate_success_criteria(self, context: Optional[Dict]) -> Dict[str, Any]
```

**Data Source:** From `context.requirements`

**Returns:**
```python
{
    "functional": [...],  # Derived from requirements
    "non_functional": {
        "performance": "...",
        "security": "...",
        "usability": "..."
    }
}
```

---

#### 4.8.10 Implementation Checklist (Section 9)

```python
def _generate_checklist(self) -> Dict[str, List[str]]
```

**Returns:**
```python
{
    "pre_implementation": [...],
    "during_implementation": [...],
    "post_implementation": [...]
}
```

---

### 4.9 Partial Plan Creator (Fallback)

```python
def _create_partial_plan(self, feature_name: str, error_msg: str) -> Dict[str, Any]
```

**Purpose:** Creates partial plan with TODOs when generation fails

**Returns:** Minimal plan structure with error message in TODOs

**Example:**
```python
{
    "META_DOCUMENTATION": {
        "feature_name": "dark-mode-toggle",
        "status": "incomplete",
        "error": "Plan generation failed: ..."
    },
    "UNIVERSAL_PLANNING_STRUCTURE": {
        "0_preparation": {"TODO": "Plan generation failed. Complete manually."},
        "1_executive_summary": {"TODO": "Plan generation failed. Complete manually."},
        ...
    }
}
```

**Performance:** <1ms (creates skeleton)

---

### 4.10 Plan Saver

```python
def save_plan(self, feature_name: str, plan: Dict[str, Any]) -> Path
```

**Purpose:** Writes plan.json to coderef/workorder/{feature}/

**File Path:** `{project_path}/coderef/workorder/{feature_name}/plan.json`

**Creates Directory:** If coderef/workorder/{feature}/ doesn't exist

**Returns:** Path to saved plan.json file

**Side Effects:**
- Creates directory tree if missing
- Writes JSON with 2-space indentation
- Logs save location

**Example:**
```python
plan_path = generator.save_plan("dark-mode-toggle", plan)
# Returns: Path("coderef/workorder/dark-mode-toggle/plan.json")
```

**Performance:** ~50ms (creates dir + writes file)

---

## 5. Integration Points

### 5.1 With gather_context

**Input:** context.json
**Used By:**
- `_generate_executive_summary()` - Uses description, goal, requirements
- `_generate_key_features()` - Uses requirements list
- `_generate_success_criteria()` - Uses requirements for functional criteria

---

### 5.2 With planning_analyzer

**Input:** analysis.json (PreparationSummaryDict)
**Used By:**
- `_generate_preparation_section()` - Direct passthrough of analysis data
- `_generate_risk_assessment()` - Uses gaps_and_risks for risk identification
- `_generate_current_state()` - Uses technology_stack, project_structure

---

### 5.3 With plan_validator

**Output:** plan.json
**Consumer:** PlanValidator reads plan.json and scores quality (0-100)

---

### 5.4 With execute_plan

**Output:** plan.json
**Consumer:** execute_plan tool reads plan.json and generates TodoWrite task list

---

## 6. Performance Characteristics

### Timing Breakdown

| Operation | Time | Bottleneck |
|-----------|------|------------|
| validate_feature_name() | <1ms | Regex match |
| load_context() | ~10-20ms | File I/O |
| load_analysis() | ~10-20ms | File I/O |
| load_template() | ~10-20ms | File I/O |
| _generate_plan_internal() | ~1-2s | Section generators |
| save_plan() | ~50ms | Create dir + write file |
| **Total** | **~2-5s** | Plan synthesis |

### Memory Usage

- Plan dict: ~50-200 KB (in-memory)
- Template: ~30-50 KB
- Context + Analysis: ~20-50 KB
- **Peak memory:** ~100-300 KB per feature

---

## 7. Error Handling & Recovery

### Error Scenarios

1. **Invalid feature_name** → ValueError (path traversal protection)
2. **context.json malformed** → ValueError (JSON decode error)
3. **Template missing** → FileNotFoundError (critical, no fallback)
4. **Plan generation fails** → Retry once, then save partial plan

### Recovery Paths

```python
# Retry logic
try:
    plan = _generate_plan_internal(...)
except Exception as e:
    logger.warning("First attempt failed. Retrying...")
    try:
        plan = _generate_plan_internal(...)  # Retry
    except Exception as retry_error:
        partial_plan = _create_partial_plan(feature_name, str(retry_error))
        save_plan(feature_name, partial_plan)
        raise ValueError("Plan generation failed. Partial plan saved.")
```

---

## 8. Common Pitfalls & Gotchas

### Pitfall 1: Template Path Confusion
**Problem:** Users expect template in their project directory
**Reality:** Template is in **MCP server directory** (not user project)
**Path:** `{MCP_server_root}/coderef/context/planning-template-for-ai.json`

### Pitfall 2: Missing context.json or analysis.json
**Problem:** Plan generation works without them (returns placeholders)
**Impact:** Plan has "Run /analyze-for-planning" TODOs
**Solution:** Always run gather_context and analyze_project_for_planning first

### Pitfall 3: Partial Plan Confusion
**Problem:** Plan saved with TODOs after failure
**Detection:** Check `META_DOCUMENTATION.status == "incomplete"`
**Solution:** Fix error, re-run generate_plan

### Pitfall 4: Workorder ID Format
**Problem:** Invalid workorder_id format (not validated)
**Impact:** plan.json has workorder_id but may not match WO-{FEATURE}-{CATEGORY}-### format
**Solution:** Validate workorder_id in caller (tool_handlers.py)

---

## 9. Testing Strategy

### Unit Tests
- Test each section generator independently
- Mock context, analysis inputs
- Validate plan structure matches schema
- Test retry logic (simulate failure then success)

### Integration Tests
- Test with real context.json and analysis.json
- Validate saved plan.json is valid JSON
- Test partial plan creation on failure

### Edge Cases
- Test without context (None)
- Test without analysis (None)
- Test without both (minimal plan)
- Test invalid feature_name (path traversal)

---

## 10. Version History

### v1.2.0 - Current
- ✅ Workorder ID tracking in META_DOCUMENTATION
- ✅ Path migration: coderef/working → coderef/workorder
- ✅ Retry logic with partial plan fallback
- ✅ Feature name validation (security)

### v1.0.0 - Initial Release
- ✅ 10-section plan generation
- ✅ Context + analysis + template synthesis
- ✅ Batch mode generation

---

## 11. Usage Examples

### Example 1: Basic Usage

```python
from pathlib import Path
from generators.planning_generator import PlanningGenerator

generator = PlanningGenerator(Path("/path/to/project"))
plan = generator.generate_plan(
    feature_name="dark-mode-toggle",
    workorder_id="WO-DARK-MODE-001"
)

print(plan['META_DOCUMENTATION']['feature_name'])
# dark-mode-toggle

print(len(plan['UNIVERSAL_PLANNING_STRUCTURE']))
# 10 (sections 0-9)
```

### Example 2: With Explicit Context and Analysis

```python
context = {
    "description": "Add dark mode support",
    "goal": "Improve user experience",
    "requirements": ["Toggle button", "Persist preference"]
}

analysis = {
    "foundation_docs": {...},
    "technology_stack": {...},
    ...
}

plan = generator.generate_plan(
    feature_name="dark-mode-toggle",
    context=context,
    analysis=analysis,
    workorder_id="WO-DARK-MODE-001"
)
```

### Example 3: Save and Validate

```python
# Generate plan
plan = generator.generate_plan("dark-mode-toggle")

# Save to disk
plan_path = generator.save_plan("dark-mode-toggle", plan)
print(plan_path)
# coderef/workorder/dark-mode-toggle/plan.json

# Validate (with plan_validator)
from generators.plan_validator import PlanValidator
validator = PlanValidator(project_path)
score = validator.validate_plan(plan)
print(score)
# 85 (out of 100)
```

---

## 12. Related Files

- **tool_handlers.py:handle_create_plan()** - MCP tool that calls PlanningGenerator
- **generators/planning_analyzer.py** - Produces analysis.json input
- **generators/plan_validator.py** - Validates plan.json output
- **coderef/context/planning-template-for-ai.json** - Template source
- **constants.py** - Paths, Files enums
- **type_defs.py** - PlanResultDict type definition

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P0-001
**Task:** SHEET-004
**Timestamp:** 2026-01-02
