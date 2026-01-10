# Papertrail UDS Standards - Phase 1 Inventory

**Agent:** papertrail
**Date:** 2026-01-10
**Phase:** Phase 1: Inventory
**Purpose:** Document Papertrail validation system for coderef-docs and coderef-workflow alignment

---

## Executive Summary

Papertrail provides **Universal Documentation Standards (UDS)** - a schema-based validation system for all CodeRef ecosystem documentation. UDS enforces a **3-tier metadata hierarchy** (Base → Category → Type-Specific) with 10 validators covering foundation docs, workorder docs, plans, sessions, and system docs.

**Key Achievement:** All documentation has complete traceability (workorder IDs), MCP attribution (which server generated it), and automated quality scoring (0-100).

**Current Status:** ✅ Production Ready (WO-UDS-SYSTEM-001 complete - 33/33 tasks done)

---

## What is UDS?

**Universal Documentation Standards (UDS)** = Schema-based validation framework that ensures:

1. **Complete Traceability** - Every doc links to a workorder ID (WO-{FEATURE}-{CATEGORY}-###)
2. **MCP Attribution** - Every doc declares which MCP server generated it
3. **Consistent Structure** - Required fields enforced via JSON Schema Draft-07
4. **Automated Validation** - 0-100 scoring with severity-weighted errors
5. **Quality Monitoring** - Pass/fail threshold (score >= 90 = valid)

---

## 3-Tier Metadata Hierarchy

UDS enforces metadata in **3 tiers**:

### Tier 1: Base UDS (Required for ALL markdown)

**Schema:** `base-frontmatter-schema.json`

**Required Fields:**
- `agent` (string) - Who created/updated the document (person, MCP server, or AI agent)
- `date` (string, YYYY-MM-DD) - Date of creation or last update
- `task` (enum) - Type of work performed: CREATE, UPDATE, REVIEW, DOCUMENT, CONSOLIDATE, MIGRATE, ARCHIVE

**Example:**
```yaml
---
agent: 'Claude Sonnet 4.5'
date: '2026-01-10'
task: CREATE
---
```

### Tier 2: Category Extensions (Required for specific doc types)

**Foundation Docs** (`foundation-doc-frontmatter-schema.json`)
- Applies to: README.md, ARCHITECTURE.md, API.md, SCHEMA.md, COMPONENTS.md
- Additional required fields:
  - `workorder_id` (WO-{FEATURE}-{CATEGORY}-###) - Workorder tracking
  - `generated_by` (starts with "coderef-docs") - MCP server attribution
  - `feature_id` (kebab-case) - Feature identifier
  - `doc_type` (enum: readme, architecture, api, schema, components)

**Workorder Docs** (`workorder-doc-frontmatter-schema.json`)
- Applies to: DELIVERABLES.md, context.json, analysis.json
- Additional required fields:
  - `workorder_id` (WO-{FEATURE}-{CATEGORY}-###)
  - `generated_by` (starts with "coderef-workflow")
  - `feature_id` (kebab-case)
  - `doc_type` (enum: plan, deliverables, context, analysis, instructions)
  - `status` (enum: draft, in_progress, blocked, review, complete, archived)

**Plan Documents** (`plan.schema.json`)
- Applies to: plan.json
- Required top-level keys:
  - `META_DOCUMENTATION` - Contains feature_name, schema_version, status
  - `UNIVERSAL_PLANNING_STRUCTURE` - 10 planning sections

**Session Documents** (`communication-schema.json`)
- Applies to: communication.json, instructions.json
- Required fields:
  - `workorder_id`, `feature_name`, `created`, `status`, `description`
  - `instructions_file`, `orchestrator`, `agents`

**System Documents** (`system-doc-frontmatter-schema.json`)
- Applies to: CLAUDE.md, SESSION-INDEX.md
- Additional required fields:
  - `project` (string) - Project name
  - `version` (semver) - Semantic version
  - `status` (enum: Production, Development, Deprecated, Archived)

**Standards Documents** (`standards-doc-frontmatter-schema.json`)
- Applies to: global-documentation-standards.md, *-standards.md
- Additional required fields:
  - `scope` (enum: global, project, category)
  - `version` (semver)
  - `enforcement` (enum: required, recommended, optional)

### Tier 3: Type-Specific Fields (Optional)

Additional metadata specific to document subtype (e.g., `prerequisites`, `participants`, `breaking_changes`).

---

## Validators

Papertrail provides **10 validators** for different document categories:

### 1. FoundationDocValidator
- **Location:** `papertrail/validators/foundation.py`
- **Schema:** `foundation-doc-frontmatter-schema.json`
- **Validates:** README.md, ARCHITECTURE.md, API.md, SCHEMA.md, COMPONENTS.md
- **Checks:**
  - Base UDS fields (agent, date, task)
  - Foundation fields (workorder_id, generated_by, feature_id, doc_type)
  - POWER framework sections (Purpose, Overview, What/Why/When, Examples, References)

### 2. WorkorderDocValidator
- **Location:** `papertrail/validators/workorder.py`
- **Schema:** `workorder-doc-frontmatter-schema.json`
- **Validates:** DELIVERABLES.md, context.json, analysis.json
- **Checks:**
  - Base UDS fields
  - Workorder fields (workorder_id, generated_by, feature_id, doc_type, status)
  - Workorder sections (Tasks, Status, Dependencies, Testing, Risks)

### 3. PlanValidator
- **Location:** `papertrail/validators/plan.py`
- **Schema:** `plan.schema.json`
- **Validates:** plan.json
- **Checks:**
  - META_DOCUMENTATION structure
  - 10-section planning structure (0_preparation through 9_implementation_checklist)
  - Required fields in each section
  - Workorder ID format validation

### 4. SessionDocValidator
- **Location:** `papertrail/validators/session.py`
- **Schema:** `communication-schema.json`
- **Validates:** communication.json, instructions.json
- **Checks:**
  - Workorder ID format (WO-{CATEGORY}-{ID}-###)
  - Feature name format (kebab-case)
  - Status enums (not_started, in_progress, complete)
  - Agent IDs (valid CodeRef ecosystem agents)
  - File paths (absolute Windows paths)

### 5. SystemDocValidator
- **Location:** `papertrail/validators/system.py`
- **Schema:** `system-doc-frontmatter-schema.json`
- **Validates:** CLAUDE.md, SESSION-INDEX.md
- **Checks:**
  - Base UDS fields
  - System fields (project, version, status)
  - System sections (Quick Summary, Architecture, File Structure, Design Decisions)

### 6-10. Other Validators
- **StandardsDocValidator** - Validates standards documentation
- **UserFacingDocValidator** - Validates guides, tutorials, FAQs
- **MigrationDocValidator** - Validates migration guides
- **InfrastructureDocValidator** - Validates deployment, CI/CD docs
- **GeneralMarkdownValidator** - Fallback for unclassified docs (base UDS fields only)

---

## ValidatorFactory (Auto-Detection)

**Purpose:** Automatically detect document type and return appropriate validator

**Location:** `papertrail/validators/factory.py`

**Detection Methods:**
1. **Path-based detection** (30+ file path patterns)
   - Example: `README.md` → FoundationDocValidator
   - Example: `DELIVERABLES.md` → WorkorderDocValidator
   - Example: `plan.json` → PlanValidator
   - Example: `communication.json` → SessionDocValidator

2. **Frontmatter-based detection** (field presence)
   - Example: `workorder_id` present → WorkorderDocValidator
   - Example: `session_id` present → SessionDocValidator

3. **Fallback**
   - If no match → GeneralMarkdownValidator

**Usage:**
```python
from papertrail.validators.factory import ValidatorFactory

validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))

if result.valid:
    print(f"✅ Document validates with score {result.score}/100")
else:
    print(f"❌ Validation failed with score {result.score}/100")
    for error in result.errors:
        print(f"  - [{error.severity.value}] {error.message}")
```

---

## Score Calculation Algorithm

**Formula:**
```python
score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
score = max(0, score)  # Floor at 0
```

**Severity Levels:**

| Severity | Penalty | Examples |
|----------|---------|----------|
| CRITICAL | -50 points | Missing required field, invalid schema structure |
| MAJOR | -20 points | Invalid enum value, format violation |
| MINOR | -10 points | Recommended field missing |
| WARNING | -5 points | Minor style issue, missing optional section |

**Interpretation:**

| Score Range | Quality | Valid? |
|-------------|---------|--------|
| 90-100 | Excellent | ✅ Yes |
| 70-89 | Good | ❌ No |
| 50-69 | Fair | ❌ No |
| 0-49 | Poor | ❌ No |

**Pass/Fail Threshold:** Score >= 90 = `result.valid = True`

---

## ValidationResult Object

**Structure:**
```python
class ValidationResult:
    valid: bool           # True if score >= 90
    errors: list[ValidationError]
    warnings: list[str]
    score: int           # 0-100

class ValidationError:
    severity: ValidationSeverity  # CRITICAL, MAJOR, MINOR, WARNING
    message: str
    field: Optional[str]
```

**Example Output:**
```python
ValidationResult(
    valid=True,
    errors=[],
    warnings=['Missing recommended POWER section: Examples'],
    score=98
)
```

---

## Integration Patterns

### For coderef-docs Generators

**Recommended Workflow:**

1. Generate foundation doc (README.md, ARCHITECTURE.md, etc.)
2. Call `FoundationDocValidator.validate_file(doc_path)`
3. If `result.valid` is False, log errors and optionally fail generation
4. If `result.valid` is True, log score and proceed

**Python Code Example:**
```python
from papertrail.validators.foundation import FoundationDocValidator
from pathlib import Path

# After generating README.md
validator = FoundationDocValidator()
result = validator.validate_file(Path("coderef/foundation-docs/README.md"))

if not result.valid:
    print(f"❌ README.md validation failed with score {result.score}/100")
    for error in result.errors:
        print(f"  - [{error.severity.value}] {error.message}")
    # Optionally: raise Exception("Validation failed")
else:
    print(f"✅ README.md validates with score {result.score}/100")
```

**Auto-Detection Alternative (Recommended):**
```python
from papertrail.validators.factory import ValidatorFactory
from pathlib import Path

# ValidatorFactory automatically detects FoundationDocValidator for README.md
validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))
```

### For coderef-workflow Generators

**Recommended Workflow:**

1. Generate workorder doc (DELIVERABLES.md, context.json, plan.json)
2. For plan.json: call `PlanValidator.validate_file(plan_path)`
3. For DELIVERABLES.md: call `WorkorderDocValidator.validate_file(deliverables_path)`
4. If `result.valid` is False, log errors and optionally fail generation
5. If `result.valid` is True, log score and proceed

**Python Code Example:**
```python
from papertrail.validators.plan import PlanValidator
from papertrail.validators.workorder import WorkorderDocValidator
from pathlib import Path

# Validate plan.json
plan_validator = PlanValidator()
plan_result = plan_validator.validate_file(Path("coderef/workorder/auth-system/plan.json"))

if not plan_result.valid:
    print(f"❌ plan.json validation failed with score {plan_result.score}/100")
    for error in plan_result.errors:
        print(f"  - [{error.severity.value}] {error.message}")

# Validate DELIVERABLES.md
deliverables_validator = WorkorderDocValidator()
deliverables_result = deliverables_validator.validate_file(Path("coderef/workorder/auth-system/DELIVERABLES.md"))

if not deliverables_result.valid:
    print(f"❌ DELIVERABLES.md validation failed")
```

---

## MCP Tools

Papertrail provides **2 MCP tools** for agent integration:

### 1. validate_document

**Purpose:** Validate a single document against UDS schema

**Input:**
```json
{
  "file_path": "/absolute/path/to/document.md"
}
```

**Output:** Markdown report with score, errors, warnings

**Example:**
```python
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/Users/willh/.mcp-servers/coderef-docs/coderef/foundation-docs/README.md"
})
```

### 2. check_all_docs

**Purpose:** Validate all documents in a directory recursively

**Input:**
```json
{
  "directory": "/absolute/path/to/directory",
  "pattern": "**/*.md"  # Optional, default: **/*.md
}
```

**Output:** Summary with pass/fail counts, average score

**Example:**
```python
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/Users/willh/.mcp-servers/coderef-docs/coderef/foundation-docs",
    "pattern": "**/*.md"
})
```

---

## Key Design Decisions

### 1. JSON Schema Draft-07

All schemas use JSON Schema Draft-07 for validation.

### 2. allOf Inheritance Pattern

All category schemas extend `base-frontmatter-schema.json` using `allOf` pattern:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "allOf": [
    { "$ref": "./base-frontmatter-schema.json" },
    {
      "type": "object",
      "required": ["category_field"],
      "properties": { ... }
    }
  ]
}
```

### 3. Manual Schema Merging

**Problem:** JSON Schema Draft-07's `$ref` resolution tried to fetch URLs as network resources, causing `HTTPSConnectionPool` errors.

**Solution:** `BaseUDSValidator` manually merges schemas via `_resolve_allof()` method:
- Manually loads referenced schemas from disk
- Merges required fields and properties
- **Critical:** Removes `allOf` key after merging to prevent Draft7Validator re-resolution

### 4. Validator Organization

**Decision:** One validator per category, not per document type

**Rationale:** Reduces code duplication, easier maintenance, flexible validation logic

**Example:** FoundationDocValidator validates all 5 foundation doc types (README, ARCHITECTURE, API, SCHEMA, COMPONENTS) instead of having 5 separate validators.

---

## Important Notes

1. **All validators extend BaseUDSValidator** - Inherit schema loading, frontmatter extraction, score calculation
2. **ValidatorFactory is recommended** - Agents don't need to manually choose validators
3. **Score >= 90 is passing** - `result.valid = True` when score >= 90
4. **Validators can be imported directly** - Use `FoundationDocValidator()` or `ValidatorFactory.get_validator()`
5. **MCP tools available** - Agents can call `validate_document` and `check_all_docs` via MCP
6. **Validation is non-blocking** - Generators can log warnings but still proceed (or choose to fail)

---

## Schema Inheritance Diagram

```
base-frontmatter-schema.json (Tier 1)
├─ foundation-doc-frontmatter-schema.json (Tier 2)
│  └─ README.md, ARCHITECTURE.md, API.md, SCHEMA.md, COMPONENTS.md
├─ workorder-doc-frontmatter-schema.json (Tier 2)
│  └─ DELIVERABLES.md, context.json, analysis.json
├─ system-doc-frontmatter-schema.json (Tier 2)
│  └─ CLAUDE.md, SESSION-INDEX.md
├─ standards-doc-frontmatter-schema.json (Tier 2)
│  └─ global-documentation-standards.md, *-standards.md
├─ user-facing-doc-frontmatter-schema.json (Tier 2)
│  └─ USER-GUIDE.md, TUTORIAL-*.md, HOW-TO-*.md
├─ migration-doc-frontmatter-schema.json (Tier 2)
│  └─ MIGRATION-*.md, AUDIT-*.md, COMPLETION-*.md
├─ infrastructure-doc-frontmatter-schema.json (Tier 2)
│  └─ FILE-TREE.md, *-INVENTORY.md, *-INDEX.md
└─ session-doc-frontmatter-schema.json (Tier 2)
   └─ communication.json, instructions.json

plan.schema.json (Standalone)
└─ plan.json

communication-schema.json (Standalone)
└─ communication.json
```

---

## Quick Reference

| Document Type | Schema | Validator | Required Fields (beyond base UDS) |
|---------------|--------|-----------|-----------------------------------|
| README.md | foundation-doc-frontmatter-schema.json | FoundationDocValidator | workorder_id, generated_by, feature_id, doc_type |
| ARCHITECTURE.md | foundation-doc-frontmatter-schema.json | FoundationDocValidator | workorder_id, generated_by, feature_id, doc_type |
| DELIVERABLES.md | workorder-doc-frontmatter-schema.json | WorkorderDocValidator | workorder_id, generated_by, feature_id, doc_type, status |
| plan.json | plan.schema.json | PlanValidator | META_DOCUMENTATION, UNIVERSAL_PLANNING_STRUCTURE |
| communication.json | communication-schema.json | SessionDocValidator | workorder_id, feature_name, created, status, orchestrator, agents |
| CLAUDE.md | system-doc-frontmatter-schema.json | SystemDocValidator | project, version, status |

---

## Documentation Resources

| Resource | Purpose | Location |
|----------|---------|----------|
| **CLAUDE.md** | UDS system architecture | `C:\Users\willh\.mcp-servers\papertrail\CLAUDE.md` |
| **UDS-IMPLEMENTATION-GUIDE.md** | Developer guide for creating new validators | `C:\Users\willh\.mcp-servers\papertrail\docs\UDS-IMPLEMENTATION-GUIDE.md` |
| **WO-UDS-SYSTEM-001-COMPLETION-SUMMARY.md** | Workorder completion summary | `C:\Users\willh\.mcp-servers\papertrail\WO-UDS-SYSTEM-001-COMPLETION-SUMMARY.md` |
| **Schemas directory** | All JSON schemas (23 schemas) | `C:\Users\willh\.mcp-servers\papertrail\schemas\` |
| **Validators directory** | All Python validators (10 validators + factory) | `C:\Users\willh\.mcp-servers\papertrail\papertrail\validators\` |

---

## Next Steps for Integration

### For coderef-docs Agent:
1. **Self-audit:** Inventory ALL files generated by your tools (see instructions.json)
2. **Identify outputs:** List every tool that creates README.md, ARCHITECTURE.md, etc.
3. **Map to schemas:** Determine which schema applies to each output (foundation-doc-frontmatter-schema.json)
4. **Report current validation status:** Does your generator currently call validators?

### For coderef-workflow Agent:
1. **Self-audit:** Inventory ALL files generated by your workflows
2. **Identify outputs:** List every workflow that creates plan.json, DELIVERABLES.md, context.json, etc.
3. **Map to schemas:** Determine which schema applies to each output (plan.schema.json, workorder-doc-frontmatter-schema.json)
4. **Report current validation status:** Do your generators currently call validators?

---

**Generated by:** papertrail agent
**Session:** WO-PAPERTRAIL-UDS-ALIGNMENT-001
**Phase:** Phase 1: Inventory
**Date:** 2026-01-10
