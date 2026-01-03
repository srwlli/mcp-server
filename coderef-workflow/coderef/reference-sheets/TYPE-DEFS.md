# TYPE-DEFS.md - type_defs.py Authoritative Reference

**File:** `type_defs.py`
**Category:** Type System / Single Source of Truth
**Lines:** 829
**TypedDicts:** 71
**Version:** 1.2.0
**Status:** ✅ Production
**Generated:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-P1-001

---

## 1. Purpose & Scope

**What It Does:**
`type_defs.py` is the canonical type system for coderef-workflow MCP server. Provides 71 TypedDict definitions and type aliases for better type safety and IDE support across all tools and generators.

**Key Innovation:**
Single source of truth for all structured data formats - every tool return type, every intermediate data structure, every MCP tool response is defined here.

**What It Returns:**
N/A - Pure type definition module (exports types via `__all__`)

**Dependencies:**
- **typing** - TypedDict, List, Optional, Dict, Any
- **pathlib.Path** - File path types

**Core Categories (14 domains):**
```
1. Generator Types (4 types)
   └─ PathsDict, TemplateInfoDict, TemplateDict, WorkflowStepDict

2. Changelog Types (2 types)
   └─ ChangeDict, VersionEntryDict

3. Standards Types (6 types)
   └─ UIPatternDict, BehaviorPatternDict, UXPatternDict, ComponentMetadataDict, StandardsResultDict

4. Audit Types (5 types)
   └─ StandardsDataDict, AuditViolationDict, ComplianceScoreDict, ViolationStatsDict, AuditResultDict

5. Consistency Types (2 types)
   └─ ConsistencyResultDict, CheckResultDict

6. Planning Workflow Types (6 types)
   └─ PlanningTemplateDict, PreparationSummaryDict, ValidationIssueDict, ValidationResultDict, PlanReviewDict, PlanResultDict

7. Inventory Types (4 types)
   └─ FileMetadataDict, ProjectMetricsDict, InventoryManifestDict, InventoryResultDict

8. Dependency Inventory (6 types)
   └─ DependencyDict, VulnerabilityDict, DependencyMetricsDict, DependencyManifestDict, DependencyResultDict

9. API Inventory (4 types)
   └─ APIEndpointDict, APIMetricsDict, APIManifestDict, APIResultDict

10. Database Inventory (8 types)
    └─ DatabaseColumnDict, DatabaseFieldDict, DatabaseRelationshipDict, DatabaseIndexDict, DatabaseSchemaDict, DatabaseMetricsDict, DatabaseManifestDict, DatabaseResultDict

11. Configuration Inventory (4 types)
    └─ ConfigFileDict, ConfigMetricsDict, ConfigManifestDict, ConfigResultDict

12. Test Inventory (4 types)
    └─ TestFileDict, TestMetricsDict, TestManifestDict, TestResultDict

13. Documentation Inventory (3 types)
    └─ DocumentationFileDict, DocumentationManifestDict, DocumentationResultDict

14. Risk Assessment (9 types)
    └─ RiskDimensionDict, CompositeScoreDict, RecommendationDict, MitigationStrategyDict, OptionComparisonDict, ProjectContextDict, ProposedChangeDict, RiskAssessmentDict, RiskAssessmentResultDict
```

**Performance:**
- Import time: <1ms (no runtime code execution)
- Memory overhead: Negligible (type metadata only)
- Zero runtime performance impact (types are erased at runtime)

---

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **Type Definitions** | Module | TypedDict classes | Static (no runtime state) | `type_defs.py` exports |
| **__all__ list** | Module | List[str] | Static | Line 10-90 (90 exported names) |
| **Actual Usage** | Tool implementations | Function return types | Ephemeral (runtime data) | Tool handlers, generators |

**Key Insight:** type_defs.py is **stateless** - pure type definitions with zero runtime behavior. All types are erased at runtime (Python's TypedDict is structural, not nominal).

---

## 3. Architecture & Data Flow

### Module Organization

```
type_defs.py (829 lines)
├─ Module docstring (lines 1-5)
├─ Imports (lines 7-8)
├─ __all__ exports (lines 10-90) - 90 exported names
│
├─ SECTION 1: Generator Types (lines 93-134)
│  ├─ PathsDict (project + output paths)
│  ├─ TemplateInfoDict (template metadata)
│  ├─ TemplateDict (template with status)
│  └─ WorkflowStepDict (workflow metadata)
│
├─ SECTION 2: Changelog Types (lines 136-165)
│  ├─ ChangeDict (single change entry)
│  └─ VersionEntryDict (version with changes list)
│
├─ SECTION 3: Standards Types (lines 167-217)
│  ├─ UIPatternDict (buttons, modals, forms, colors, typography, spacing, icons)
│  ├─ BehaviorPatternDict (error handling, loading states, toasts, validation, API communication)
│  ├─ UXPatternDict (navigation, permissions, offline handling, accessibility)
│  ├─ ComponentMetadataDict (component inventory)
│  └─ StandardsResultDict (standards generation result)
│
├─ SECTION 4: Audit Types (lines 219-278)
│  ├─ StandardsDataDict (parsed standards docs)
│  ├─ AuditViolationDict (single violation)
│  ├─ ComplianceScoreDict (compliance metrics)
│  ├─ ViolationStatsDict (violation statistics)
│  └─ AuditResultDict (complete audit results)
│
├─ SECTION 5: Consistency Types (lines 280-299)
│  ├─ ConsistencyResultDict (consistency check result)
│  └─ CheckResultDict (per-file check result)
│
├─ SECTION 6: Planning Workflow Types (lines 301-393)
│  ├─ PlanningTemplateDict (planning template structure)
│  ├─ PreparationSummaryDict (preparation analysis)
│  ├─ ValidationIssueDict (plan validation issue)
│  ├─ ValidationResultDict (validation results)
│  ├─ PlanReviewDict (plan review report)
│  └─ PlanResultDict (plan generation result)
│
├─ SECTION 7: Inventory Types (lines 395-404)
│  ├─ FileMetadataDict (file inventory entry)
│  ├─ ProjectMetricsDict (project-level metrics)
│  ├─ InventoryManifestDict (complete inventory)
│  └─ InventoryResultDict (inventory generation result)
│
├─ SECTION 8: Dependency Inventory (lines 406-477)
│  ├─ DependencyDict (single dependency metadata)
│  ├─ VulnerabilityDict (security vulnerability)
│  ├─ DependencyMetricsDict (aggregated metrics)
│  ├─ DependencyManifestDict (complete dependency manifest)
│  └─ DependencyResultDict (dependency analysis result)
│
├─ SECTION 9: API Inventory (lines 479-528)
│  ├─ APIEndpointDict (single API endpoint)
│  ├─ APIMetricsDict (API-level metrics)
│  ├─ APIManifestDict (complete API inventory)
│  └─ APIResultDict (API analysis result)
│
├─ SECTION 10: Database Inventory (lines 530-624)
│  ├─ DatabaseColumnDict (table column metadata)
│  ├─ DatabaseFieldDict (NoSQL field metadata)
│  ├─ DatabaseRelationshipDict (table relationship)
│  ├─ DatabaseIndexDict (database index)
│  ├─ DatabaseSchemaDict (complete schema)
│  ├─ DatabaseMetricsDict (database metrics)
│  ├─ DatabaseManifestDict (complete database inventory)
│  └─ DatabaseResultDict (database analysis result)
│
├─ SECTION 11: Configuration Inventory (lines 626-664)
│  ├─ ConfigFileDict (single config file)
│  ├─ ConfigMetricsDict (config metrics)
│  ├─ ConfigManifestDict (complete config inventory)
│  └─ ConfigResultDict (config analysis result)
│
├─ SECTION 12: Test Inventory (lines 666-702)
│  ├─ TestFileDict (single test file)
│  ├─ TestMetricsDict (test metrics)
│  ├─ TestManifestDict (complete test inventory)
│  └─ TestResultDict (test analysis result)
│
├─ SECTION 13: Documentation Inventory (lines 703-739)
│  ├─ DocumentationFileDict (single doc file)
│  ├─ DocumentationManifestDict (complete doc inventory)
│  └─ DocumentationResultDict (doc analysis result)
│
└─ SECTION 14: Risk Assessment (lines 741-829)
   ├─ RiskDimensionDict (single risk dimension)
   ├─ CompositeScoreDict (overall risk score)
   ├─ RecommendationDict (go/no-go decision)
   ├─ MitigationStrategyDict (actionable mitigation)
   ├─ OptionComparisonDict (multi-option comparison)
   ├─ ProjectContextDict (analyzed context)
   ├─ ProposedChangeDict (change details)
   ├─ RiskAssessmentDict (complete assessment)
   └─ RiskAssessmentResultDict (assessment tool result)
```

### TypedDict Design Patterns

**Pattern 1: Result Types (Tool Return Values)**
```python
class SomeResultDict(TypedDict):
    manifest_path: str  # Where result was saved
    success: bool       # Operation status
    metrics: SomeMetricsDict  # Aggregated metrics
    # ... tool-specific fields
```

**Pattern 2: Manifest Types (Complete Inventories)**
```python
class SomeManifestDict(TypedDict):
    project_name: str
    project_path: str
    generated_at: str  # ISO 8601 timestamp
    items: List[SomeItemDict]  # Inventory data
    metrics: SomeMetricsDict   # Aggregated metrics
```

**Pattern 3: Metrics Types (Aggregated Statistics)**
```python
class SomeMetricsDict(TypedDict, total=False):
    total_count: int
    category_breakdown: dict  # {category: count}
    # ... aggregated statistics
```

**Pattern 4: Item Types (Individual Entities)**
```python
class SomeItemDict(TypedDict, total=False):
    name: str
    type: str
    file_path: str
    # ... entity-specific fields
```

---

## 4. Key TypedDict Categories

### Category 1: Generator Types (4 types)

**PathsDict**
- **Purpose:** Return type for `prepare_generation()` method
- **Fields:** `project_path: Path`, `output_dir: Path`
- **Usage:** Template generation setup

**TemplateInfoDict (total=False)**
- **Purpose:** Template metadata extracted from template files
- **Fields:** `framework: str`, `purpose: str`, `save_as: str`, `store_as: str`
- **Usage:** Template discovery and loading

**TemplateDict (total=False)**
- **Purpose:** Template information from `get_templates_for_generation()`
- **Fields:** `template_name: str`, `template_content: str`, `status: str`, `error: str` (optional)
- **Usage:** Template loading with error handling

**WorkflowStepDict (total=False)**
- **Purpose:** Workflow step from `get_workflow_info()`
- **Fields:** Combines TemplateInfoDict + `template_name: str` + `error: str` (optional)
- **Usage:** Multi-step workflow orchestration

---

### Category 2: Changelog Types (2 types)

**ChangeDict (total=False)**
- **Purpose:** Single changelog entry
- **Required:** `id`, `type`, `severity`, `title`, `description`, `files`, `reason`, `impact`, `breaking`
- **Optional:** `migration` (for breaking changes)
- **Usage:** `CHANGELOG.json` change tracking

**VersionEntryDict (total=False)**
- **Purpose:** Complete version entry in changelog
- **Required:** `version`, `date`, `summary`, `changes: List[ChangeDict]`
- **Optional:** `contributors: List[str]`
- **Usage:** Version history in `CHANGELOG.json`

---

### Category 3: Standards Types (6 types)

**UIPatternDict (total=False)**
- **Purpose:** UI pattern standards
- **Fields:** `buttons`, `modals`, `forms`, `colors`, `typography`, `spacing`, `icons` (all dict)
- **Usage:** `ui-patterns.md` standard definition

**BehaviorPatternDict (total=False)**
- **Purpose:** Behavior pattern standards
- **Fields:** `error_handling`, `loading_states`, `toasts`, `validation`, `api_communication` (all dict)
- **Usage:** `behavior-patterns.md` standard definition

**UXPatternDict (total=False)**
- **Purpose:** UX flow pattern standards
- **Fields:** `navigation`, `permissions`, `offline_handling`, `accessibility` (all dict)
- **Usage:** `ux-patterns.md` standard definition

**ComponentMetadataDict**
- **Purpose:** Component inventory entry
- **Fields:** `name`, `type`, `usage_count`, `status`, `props: List[str]`, `file_path`, `notes`
- **Usage:** Component catalog

**StandardsResultDict**
- **Purpose:** Result from `save_standards` operation
- **Fields:** `files: List[str]`, `patterns_count: int`, `success: bool`, `ui_patterns_count`, `behavior_patterns_count`, `ux_patterns_count`, `components_count`
- **Usage:** `/establish-standards` tool return value

---

### Category 4: Audit Types (5 types)

**StandardsDataDict (total=False)**
- **Purpose:** Parsed standards data from markdown documents
- **Fields:** `ui_patterns`, `behavior_patterns`, `ux_patterns`, `components`, `source_files: List[str]`, `parse_errors: List[str]`
- **Usage:** Internal standards representation after parsing

**AuditViolationDict (total=False)**
- **Purpose:** Single violation detected during audit
- **Fields:** `id`, `type`, `severity`, `category`, `file_path`, `line_number`, `column`, `message`, `actual_value`, `expected_value`, `fix_suggestion`, `code_snippet`
- **Usage:** Violation reporting in audit reports

**ComplianceScoreDict**
- **Purpose:** Compliance metrics by category
- **Fields:** `overall_score: int (0-100)`, `ui_compliance`, `behavior_compliance`, `ux_compliance`, `grade: str (A/B/C/D/F)`, `passing: bool (>=80)`
- **Usage:** Compliance grading in audit reports

**ViolationStatsDict**
- **Purpose:** Statistics about violations found
- **Fields:** `total_violations`, `critical_count`, `major_count`, `minor_count`, `violations_by_file: dict`, `violations_by_type: dict`, `most_violated_file`, `most_common_violation`
- **Usage:** Violation summary in audit reports

**AuditResultDict (total=False)**
- **Purpose:** Complete audit results
- **Fields:** `report_path`, `compliance_score`, `compliance_details: ComplianceScoreDict`, `violation_stats: ViolationStatsDict`, `violations: List[AuditViolationDict]`, `scan_metadata: dict`, `success`
- **Usage:** `/audit-codebase` tool return value

---

### Category 5: Consistency Types (2 types)

**ConsistencyResultDict (total=False)**
- **Purpose:** Result from consistency check operation
- **Fields:** `status: str (pass/fail)`, `violations_found`, `violations: List[AuditViolationDict]`, `files_checked`, `files_list: List[str]`, `duration: float`, `severity_threshold`, `exit_code: int (0/1)`
- **Usage:** `/check-consistency` tool return value

**CheckResultDict (total=False)**
- **Purpose:** Per-file check result
- **Fields:** `file_path`, `violations: List[AuditViolationDict]`, `clean: bool`
- **Usage:** Internal per-file validation

---

### Category 6: Planning Workflow Types (6 types)

**PlanningTemplateDict (total=False)**
- **Purpose:** Planning template structure
- **Fields:** Plan structure with 10 sections (0_preparation through 9_implementation_checklist)
- **Usage:** `planning-template-for-ai.json` structure

**PreparationSummaryDict (total=False)**
- **Purpose:** Preparation analysis summary
- **Fields:** Foundation docs, coding standards, reference components, technology stack, gaps
- **Usage:** Section 0 of plan.json

**ValidationIssueDict (total=False)**
- **Purpose:** Plan validation issue
- **Fields:** `severity: str (critical/major/minor)`, `section`, `issue`, `suggestion`
- **Usage:** Plan quality scoring

**ValidationResultDict (total=False)**
- **Purpose:** Validation results
- **Fields:** `validation_result: str (excellent/good/needs work/poor)`, `score: int (0-100)`, `issues: List[ValidationIssueDict]`, `checklist_results`, `approved: bool`
- **Usage:** `/validate-plan` tool return value

**PlanReviewDict (total=False)**
- **Purpose:** Plan review report
- **Fields:** Review markdown with score, grade, issues breakdown
- **Usage:** `/generate-plan-review` tool return value

**PlanResultDict (total=False)**
- **Purpose:** Plan generation result
- **Fields:** `plan_path`, `feature_name`, `workorder_id`, `score`, `approved`, `success`
- **Usage:** `/create-plan` tool return value

---

### Category 7-13: Inventory Types (7 categories, 29 types)

**Common Pattern:**
All inventory categories follow the same 4-type structure:
1. **ItemDict** - Single entity metadata (file, dependency, endpoint, etc.)
2. **MetricsDict** - Aggregated statistics
3. **ManifestDict** - Complete inventory with project metadata
4. **ResultDict** - Tool return value with file paths and summary

**Category 7: File Inventory (4 types)**
- FileMetadataDict, ProjectMetricsDict, InventoryManifestDict, InventoryResultDict

**Category 8: Dependency Inventory (6 types)**
- DependencyDict, VulnerabilityDict, DependencyMetricsDict, DependencyManifestDict, DependencyResultDict

**Category 9: API Inventory (4 types)**
- APIEndpointDict, APIMetricsDict, APIManifestDict, APIResultDict

**Category 10: Database Inventory (8 types)**
- DatabaseColumnDict, DatabaseFieldDict, DatabaseRelationshipDict, DatabaseIndexDict, DatabaseSchemaDict, DatabaseMetricsDict, DatabaseManifestDict, DatabaseResultDict

**Category 11: Configuration Inventory (4 types)**
- ConfigFileDict, ConfigMetricsDict, ConfigManifestDict, ConfigResultDict

**Category 12: Test Inventory (4 types)**
- TestFileDict, TestMetricsDict, TestManifestDict, TestResultDict

**Category 13: Documentation Inventory (3 types)**
- DocumentationFileDict, DocumentationManifestDict, DocumentationResultDict

---

### Category 14: Risk Assessment Types (9 types)

**RiskDimensionDict (total=False)**
- **Purpose:** Risk evaluation for single dimension
- **Fields:** `severity: str (low/medium/high/critical)`, `likelihood: float (0-100)`, `score: float (0-100)`, `findings: List[str]`, `evidence: List[str]`, `mitigation_available: bool`
- **Usage:** 5 risk dimensions (breaking changes, security, performance, maintainability, reversibility)

**CompositeScoreDict**
- **Purpose:** Overall risk assessment score
- **Fields:** `score: float (0-100)`, `level: str (low/medium/high/critical)`, `explanation`, `confidence: float (0-1)`
- **Usage:** Aggregated risk score

**RecommendationDict (total=False)**
- **Purpose:** Go/no-go decision
- **Fields:** `decision: str (go/no-go/proceed-with-caution/needs-review)`, `rationale`, `conditions: List[str]`
- **Usage:** Final recommendation in assessment

**MitigationStrategyDict (total=False)**
- **Purpose:** Actionable mitigation
- **Fields:** `risk_dimension`, `strategy`, `priority: str (critical/high/medium/low)`, `estimated_effort: str (low/medium/high)`
- **Usage:** Risk mitigation plan

**OptionComparisonDict (total=False)**
- **Purpose:** Multi-option comparison entry
- **Fields:** `option_id`, `description`, `composite_score`, `rank`, `pros: List[str]`, `cons: List[str]`
- **Usage:** Comparing multiple implementation approaches

**ProjectContextDict (total=False)**
- **Purpose:** Analyzed project context
- **Fields:** `files_analyzed`, `dependencies_found`, `test_coverage`, `architecture_patterns: List[str]`, `gaps: List[str]`
- **Usage:** Context for risk evaluation

**ProposedChangeDict**
- **Purpose:** Details of proposed change
- **Fields:** `description`, `change_type: str (create/modify/delete/refactor/migrate)`, `files_affected: List[str]`, `context: Dict[str, Any]`
- **Usage:** Input to risk assessment

**RiskAssessmentDict (total=False)**
- **Purpose:** Complete risk assessment structure
- **Fields:** `assessment_id`, `generated_at`, `project_path`, `proposed_change: ProposedChangeDict`, `risk_dimensions: Dict[str, RiskDimensionDict]`, `composite_score: CompositeScoreDict`, `recommendation: RecommendationDict`, `mitigation_strategies: List[MitigationStrategyDict]`, `options_analyzed`, `comparison`, `project_context: ProjectContextDict`, `metadata`
- **Usage:** Saved assessment JSON file

**RiskAssessmentResultDict**
- **Purpose:** Tool return value
- **Fields:** `assessment_path`, `assessment_id`, `composite_score`, `risk_level`, `decision`, `options_analyzed`, `recommended_option`, `duration_ms`, `success`
- **Usage:** `/assess-risk` tool return value

---

## 5. TypedDict Usage Patterns

### Pattern 1: Tool Return Types

**Convention:** All MCP tools return a dict with `success: bool` field

```python
# Example: PlanResultDict
{
    "plan_path": "coderef/workorder/feature/plan.json",
    "feature_name": "dark-mode-toggle",
    "workorder_id": "WO-DARK-MODE-001",
    "score": 95,
    "approved": True,
    "success": True
}
```

**Used by:**
- StandardsResultDict
- AuditResultDict
- ConsistencyResultDict
- ValidationResultDict
- PlanResultDict
- InventoryResultDict
- DependencyResultDict
- APIResultDict
- DatabaseResultDict
- ConfigResultDict
- TestResultDict
- DocumentationResultDict
- RiskAssessmentResultDict

---

### Pattern 2: Manifest Structure

**Convention:** All inventory manifests include project metadata + timestamp

```python
# Example: DependencyManifestDict
{
    "project_name": "coderef-workflow",
    "project_path": "/path/to/project",
    "generated_at": "2026-01-02T00:00:00Z",
    "package_managers": ["pip"],
    "dependencies": {...},
    "vulnerabilities": [...],
    "metrics": {...}
}
```

**Used by:**
- InventoryManifestDict
- DependencyManifestDict
- APIManifestDict
- DatabaseManifestDict
- ConfigManifestDict
- TestManifestDict
- DocumentationManifestDict

---

### Pattern 3: Optional Fields (total=False)

**Convention:** Use `total=False` for TypedDicts with optional fields

```python
class ChangeDict(TypedDict, total=False):
    """All fields optional except those explicitly marked."""
    id: str          # Required (would raise error if missing)
    migration: str   # Optional (not required)
```

**When to use:**
- Fields that may be missing (template errors, conditional data)
- Fields with default values
- Fields that only exist in certain contexts

**Used by:** 56 out of 71 TypedDicts (79%)

---

### Pattern 4: Nested TypedDicts

**Convention:** Compose complex structures from smaller TypedDicts

```python
class VersionEntryDict(TypedDict, total=False):
    version: str
    changes: List[ChangeDict]  # Nested TypedDict
    # ...

class AuditResultDict(TypedDict, total=False):
    compliance_details: ComplianceScoreDict  # Nested TypedDict
    violation_stats: ViolationStatsDict      # Nested TypedDict
    violations: List[AuditViolationDict]     # List of nested TypedDicts
    # ...
```

**Benefits:**
- Reusable type components
- Clear composition hierarchy
- Better IDE support (autocomplete on nested fields)

---

## 6. Integration Points

### 6.1 Called By (Consumers)

**All Tool Handlers:**
- `tool_handlers.py` - Every tool uses type_defs for return types
- Example: `def establish_standards(...) -> StandardsResultDict`

**All Generators:**
- `generators/plan_generator.py` - Uses PlanningTemplateDict, PlanResultDict
- `generators/plan_validator.py` - Uses ValidationResultDict, ValidationIssueDict
- `generators/planning_analyzer.py` - Uses PreparationSummaryDict

**All Inventory Modules:**
- `generators/dependency_inventory.py` - Uses Dependency* types
- `generators/api_inventory.py` - Uses API* types
- `generators/database_inventory.py` - Uses Database* types
- `generators/config_inventory.py` - Uses Config* types
- `generators/test_inventory.py` - Uses Test* types
- `generators/documentation_inventory.py` - Uses Documentation* types

**Risk Assessment:**
- `generators/risk_assessor.py` - Uses RiskAssessment* types

---

### 6.2 Type Checking Workflow

```
Developer writes function:
def create_plan(...) -> PlanResultDict:
    return {
        "plan_path": str(path),
        "feature_name": name,
        "workorder_id": wo_id,
        "score": 95,
        "approved": True,
        "success": True
    }
    ↓
mypy validates:
- All required fields present
- Field types match definition
- No extra fields (strict mode)
    ↓
IDE provides:
- Autocomplete on field names
- Type hints for nested dicts
- Error highlighting
```

---

### 6.3 Runtime Validation

**Important:** TypedDict is structural, not nominal. No runtime checks by default.

**Best Practice:** Use type guards for runtime validation

```python
from typing import TypeGuard

def is_plan_result(data: dict) -> TypeGuard[PlanResultDict]:
    """Runtime check for PlanResultDict."""
    required_keys = {"plan_path", "feature_name", "success"}
    return (
        isinstance(data, dict) and
        required_keys.issubset(data.keys()) and
        isinstance(data["success"], bool)
    )

# Usage:
result = some_function()
if is_plan_result(result):
    # Type checker knows result is PlanResultDict
    print(result["plan_path"])
else:
    raise ValueError("Invalid result format")
```

---

## 7. Maintenance & Evolution

### 7.1 Adding New Types

**Process:**
1. Define TypedDict in appropriate category section
2. Add to `__all__` list (lines 10-90)
3. Document in docstring
4. Use in tool/generator return type

**Example:**
```python
# Step 1: Define type
class NewFeatureDict(TypedDict, total=False):
    """New feature metadata."""
    name: str
    version: str
    enabled: bool

# Step 2: Add to __all__
__all__ = [
    # ... existing exports
    'NewFeatureDict',
]

# Step 3: Document usage
# (Add to this resource sheet's Section 4)

# Step 4: Use in code
def get_new_feature() -> NewFeatureDict:
    return {
        "name": "feature-x",
        "version": "1.0.0",
        "enabled": True
    }
```

---

### 7.2 Versioning Strategy

**Current Version:** 1.2.0

**Versioning Rules:**
- **Major (x.0.0):** Breaking changes to existing TypedDicts (remove fields, change field types)
- **Minor (1.x.0):** New TypedDicts added, optional fields added to existing types
- **Patch (1.2.x):** Documentation updates, no type changes

**Example:**
- v1.2.0 → v1.3.0: Add 5 new RiskAssessment types (minor)
- v1.3.0 → v2.0.0: Remove deprecated fields from ChangeDict (major)
- v2.0.0 → v2.0.1: Fix docstring typo (patch)

---

### 7.3 Deprecation Process

**Step 1: Mark deprecated (minor version)**
```python
class LegacyDict(TypedDict, total=False):
    """DEPRECATED: Use NewDict instead. Will be removed in v2.0.0."""
    old_field: str
```

**Step 2: Provide migration path**
```python
def migrate_legacy_to_new(legacy: LegacyDict) -> NewDict:
    """Convert LegacyDict to NewDict."""
    return {
        "new_field": legacy["old_field"]
    }
```

**Step 3: Remove in next major version**
- Remove from type_defs.py
- Remove from `__all__` list
- Update consumers to use new type

---

### 7.4 Recent Changes (v1.2.0)

**Added:**
- RiskAssessment types (9 new types)
- Documentation inventory types (3 new types)
- Test inventory types (4 new types)

**Modified:**
- AuditViolationDict: Added `column: int` field
- PlanResultDict: Added `workorder_id` field

**Removed:**
- None (no breaking changes)

---

## 8. Testing Strategy

### 8.1 Type Checking Tests

```python
# test_type_defs.py

from typing import TYPE_CHECKING
from type_defs import PlanResultDict, ValidationResultDict

def test_plan_result_structure():
    """Verify PlanResultDict structure."""
    result: PlanResultDict = {
        "plan_path": "coderef/workorder/feature/plan.json",
        "feature_name": "test-feature",
        "workorder_id": "WO-TEST-001",
        "score": 95,
        "approved": True,
        "success": True
    }
    # mypy validates this structure at type-check time
    assert result["success"] is True

def test_validation_result_structure():
    """Verify ValidationResultDict structure."""
    result: ValidationResultDict = {
        "validation_result": "excellent",
        "score": 95,
        "issues": [],
        "checklist_results": {
            "structure": {"passed": 10, "failed": 0, "score": 100},
            "completeness": {"passed": 8, "failed": 0, "score": 100},
            "quality": {"passed": 5, "failed": 0, "score": 100},
            "autonomy": {"passed": 3, "failed": 0, "score": 100}
        },
        "approved": True
    }
    assert result["approved"] is True
```

---

### 8.2 Runtime Validation Tests

```python
def test_runtime_type_guard():
    """Test type guard for runtime validation."""
    valid_data = {
        "plan_path": "path/to/plan.json",
        "feature_name": "test",
        "success": True
    }
    assert is_plan_result(valid_data)

    invalid_data = {
        "plan_path": "path/to/plan.json"
        # Missing required fields
    }
    assert not is_plan_result(invalid_data)
```

---

## 9. Best Practices

### 9.1 Using TypedDicts

**DO:**
```python
# ✅ Use type hints for better IDE support
def create_plan(...) -> PlanResultDict:
    return {
        "plan_path": str(path),
        "feature_name": name,
        "success": True
    }

# ✅ Use total=False for optional fields
class MyDict(TypedDict, total=False):
    required_field: str
    optional_field: str  # Can be missing
```

**DON'T:**
```python
# ❌ Return untyped dict
def create_plan(...) -> dict:
    return {...}

# ❌ Mix required and optional without total=False
class MyDict(TypedDict):
    field: str  # Implicitly required
    # But some callers might omit it
```

---

### 9.2 Type Composition

**DO:**
```python
# ✅ Compose from smaller types
class AuditResultDict(TypedDict, total=False):
    compliance_details: ComplianceScoreDict  # Reuse existing type
    violation_stats: ViolationStatsDict      # Reuse existing type
```

**DON'T:**
```python
# ❌ Duplicate structure inline
class AuditResultDict(TypedDict, total=False):
    compliance_details: dict  # Unstructured, no autocomplete
```

---

### 9.3 Documentation

**DO:**
```python
# ✅ Document purpose and usage
class ChangeDict(TypedDict, total=False):
    """Changelog change entry.

    Required fields: id, type, severity, title, description, files, reason, impact, breaking
    Optional fields: migration

    Usage:
        >>> change = ChangeDict(
        ...     id="CHANGE-001",
        ...     type="feature",
        ...     breaking=False
        ... )
    """
```

**DON'T:**
```python
# ❌ No documentation
class ChangeDict(TypedDict, total=False):
    id: str
    type: str
```

---

## 10. Quick Reference

### 10.1 Most Used Types

**Top 10 by Usage Frequency:**
1. **PlanResultDict** - Used by planning workflow tools
2. **ValidationResultDict** - Used by plan validation
3. **StandardsResultDict** - Used by standards establishment
4. **AuditResultDict** - Used by audit tools
5. **ConsistencyResultDict** - Used by consistency checker
6. **ChangeDict** - Used by changelog management
7. **VersionEntryDict** - Used by version tracking
8. **DependencyResultDict** - Used by dependency analysis
9. **RiskAssessmentResultDict** - Used by risk assessment
10. **APIResultDict** - Used by API discovery

---

### 10.2 Type Hierarchy

```
Result Types (Tool Return Values)
├─ StandardsResultDict
├─ AuditResultDict
├─ ConsistencyResultDict
├─ ValidationResultDict
├─ PlanResultDict
├─ InventoryResultDict
├─ DependencyResultDict
├─ APIResultDict
├─ DatabaseResultDict
├─ ConfigResultDict
├─ TestResultDict
├─ DocumentationResultDict
└─ RiskAssessmentResultDict

Manifest Types (Complete Inventories)
├─ InventoryManifestDict
├─ DependencyManifestDict
├─ APIManifestDict
├─ DatabaseManifestDict
├─ ConfigManifestDict
├─ TestManifestDict
└─ DocumentationManifestDict

Metrics Types (Aggregated Statistics)
├─ ProjectMetricsDict
├─ DependencyMetricsDict
├─ APIMetricsDict
├─ DatabaseMetricsDict
├─ ConfigMetricsDict
├─ TestMetricsDict
└─ ViolationStatsDict
```

---

## 11. Related Resources

### 11.1 Related Files

- **tool_handlers.py** - Primary consumer (uses all Result types)
- **generators/*.py** - Uses domain-specific types
- **constants.py** - Enum constants used alongside TypedDicts

### 11.2 Generated Artifacts

- **coderef/schemas/type-defs-schema.json** - JSON Schema definitions
- **coderef/.jsdoc/type-defs-jsdoc.txt** - JSDoc inline documentation

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P1-001
**Task:** SHEET-007
**Timestamp:** 2026-01-02
**Maintained by:** willh, Claude Code AI
