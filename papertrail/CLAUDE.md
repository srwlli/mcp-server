---
agent: 'Lloyd (Planning Assistant)'
date: '2026-01-10'
task: UPDATE
project: Papertrail
version: '1.0.0'
status: Production
title: 'Papertrail - AI Context Documentation'
---

# Papertrail - AI Context Documentation

**Project:** Papertrail (Universal Documentation Standards)
**Version:** 1.0.0
**Status:** Production
**Type:** Python Library + MCP Server
**Purpose:** Universal Documentation Standards (UDS) enforcement for CodeRef ecosystem

---

## What is Papertrail?

Papertrail is a **Python library and MCP server** that provides Universal Documentation Standards (UDS) and Resource Sheet Metadata Standards (RSMS) for the CodeRef ecosystem. It ensures every document has complete traceability, MCP attribution, quality validation, and health monitoring.

**Core Capabilities:**
- Complete workorder traceability (WO-ID linking) for implementation docs
- Resource sheet metadata tracking (RSMS) for architectural docs
- Automated UDS/RSMS header injection
- Schema-based validation (0-100 scoring)
- Health monitoring (4-factor scoring)
- Jinja2 template automation with CodeRef extensions

---

## Problem & Solution

### Problem
Documentation across CodeRef MCP servers was inconsistent, lacked traceability, and couldn't be validated automatically. Implementation docs had no workorder tracking, and architectural docs (resource sheets) had no versioning or relationship tracking.

### Solution
Papertrail provides **three metadata standards**:

**1. UDS (Universal Documentation Standards)** - For workorder-based implementation docs
- Workorder traceability (WO-ID linking)
- MCP attribution (which server generated it)
- Feature scoping (feature_id)
- Automated validation (0-100 health scores)

**2. RSMS (Resource Sheet Metadata Standards)** - For architectural reference docs
- Version tracking (semver)
- Project scoping (parent_project)
- Relationship tracking (related_files, related_docs)
- Subject/category classification

**3. Standard Markdown** - For general documentation
- No metadata requirements
- Used for README, guides, tutorials

**4. Global Documentation Standards** - Cross-cutting rules for all documents
- Headers: YAML front matter (agent, date, task)
- Footers: Document metadata (Last Updated, Version, Maintained by)
- No Emojis: Use text markers ([PASS], [FAIL], [WARN], [INFO])

---

## Architecture

**Language:** Python 3.10+
**Dependencies:** Jinja2, Pydantic, jsonschema
**Integration:** MCP server + Python library

**Key Components:**
1. **UDS Schema Validator** - Validates document structure
2. **Health Scorer** - 4-factor scoring (traceability 40%, completeness 30%, freshness 20%, validation 10%)
3. **Template Engine** - Jinja2 with CodeRef extensions
4. **Workorder Logger** - Global workorder tracking
5. **MCP Tools** - 2 tools for validation and batch checking

---

## UDS System Architecture

### 3-Tier Metadata Hierarchy

UDS enforces a **3-tier hierarchy** for all markdown documentation:

**Tier 1: Base UDS (Required for ALL markdown)**
- `agent`: Who created/updated the document
- `date`: When it was created/updated (YYYY-MM-DD format)
- `task`: What action was performed (CREATE, UPDATE, REVIEW, etc.)

**Tier 2: Category Extensions (Required for specific doc types)**
- **Foundation Docs**: `workorder_id`, `generated_by`, `feature_id`, `doc_type`
- **Workorder Docs**: Same as foundation + `status`
- **System Docs**: `project`, `version`, `status`
- **Standards Docs**: `scope`, `version`, `enforcement`
- **User-Facing Docs**: `audience`, `doc_type`, `difficulty`
- **Migration Docs**: `migration_type`, `from_version`, `to_version`
- **Infrastructure Docs**: `infra_type`, `environment`, `platform`
- **Session Docs**: `session_type`, `session_id`, `orchestrator`

**Tier 3: Type-Specific Fields (Optional)**
- Additional metadata specific to document subtype
- Examples: `prerequisites`, `participants`, `breaking_changes`

### Schema Inheritance Pattern

All schemas use **JSON Schema Draft-07 allOf pattern** for inheritance:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "allOf": [
    {
      "$ref": "./base-frontmatter-schema.json"
    },
    {
      "type": "object",
      "required": ["category_specific_field"],
      "properties": {
        "category_specific_field": {
          "type": "string",
          "description": "Category-specific metadata"
        }
      }
    }
  ]
}
```

**Schema Resolution**: BaseUDSValidator manually merges schemas via `_resolve_allof()` method to avoid network fetch errors from Draft7Validator.

### Validator Hierarchy

**BaseUDSValidator (Abstract Base Class)**
- **Location**: `papertrail/validators/base.py`
- **Responsibilities**:
  - Schema loading and $ref resolution
  - YAML frontmatter extraction
  - JSON schema validation
  - Score calculation (0-100)
  - Error/warning aggregation
- **Key Methods**:
  - `validate_file(file_path)`: Main validation entry point
  - `_load_schema()`: Load JSON schema and resolve allOf
  - `_resolve_allof()`: Manual schema merging
  - `_extract_frontmatter(content)`: Parse YAML front matter
  - `validate_specific(frontmatter, content, file_path)`: Abstract method for category-specific checks
  - `_calculate_score(errors, warnings)`: Score calculation algorithm

**10 Category-Specific Validators**

All extend BaseUDSValidator and implement `validate_specific()` for custom validation:

1. **FoundationDocValidator** (`papertrail/validators/foundation.py`)
   - Schema: `foundation-doc-frontmatter-schema.json`
   - Category: `foundation`
   - Checks: POWER framework sections (Purpose, Overview, What/Why/When, Examples, References)

2. **WorkorderDocValidator** (`papertrail/validators/workorder.py`)
   - Schema: `workorder-doc-frontmatter-schema.json`
   - Category: `workorder`
   - Checks: Workorder sections (Tasks, Status, Dependencies, Testing, Risks)

3. **SystemDocValidator** (`papertrail/validators/system.py`)
   - Schema: `system-doc-frontmatter-schema.json`
   - Category: `system`
   - Checks: System sections (Quick Summary, Architecture, File Structure, Design Decisions, Integration, Use Cases)

4. **StandardsDocValidator** (`papertrail/validators/standards.py`)
   - Schema: `standards-doc-frontmatter-schema.json`
   - Category: `standards`
   - Checks: Standards sections (Purpose, Scope, Requirements, Validation, Examples)

5. **UserFacingDocValidator** (`papertrail/validators/user_facing.py`)
   - Schema: `user-facing-doc-frontmatter-schema.json`
   - Category: `user-facing`
   - Checks: Audience, difficulty level, tutorial sections

6. **MigrationDocValidator** (`papertrail/validators/migration.py`)
   - Schema: `migration-doc-frontmatter-schema.json`
   - Category: `migration`
   - Checks: Breaking changes section, migration steps

7. **InfrastructureDocValidator** (`papertrail/validators/infrastructure.py`)
   - Schema: `infrastructure-doc-frontmatter-schema.json`
   - Category: `infrastructure`
   - Checks: Prerequisites, Setup, Configuration, Deployment sections

8. **SessionDocValidator** (`papertrail/validators/session.py`)
   - Schema: `session-doc-frontmatter-schema.json`
   - Category: `session`
   - Checks: Session ID format (kebab-case), orchestrator field, participants

9. **PlanValidator** (`papertrail/validators/plan.py`)
   - Schema: `plan.schema.json`
   - Category: `plan`
   - Checks: plan.json structure (10-section format)

10. **GeneralMarkdownValidator** (`papertrail/validators/general.py`)
    - Schema: `base-frontmatter-schema.json`
    - Category: `general`
    - Checks: Base UDS fields only (fallback for unclassified docs)

### ValidatorFactory (Auto-Detection)

**Location**: `papertrail/validators/factory.py`

**Purpose**: Automatically detect document type and return appropriate validator

**Detection Logic** (30+ path patterns):
1. **Path-based detection**:
   - `README.md` → FoundationDocValidator
   - `DELIVERABLES.md` → WorkorderDocValidator
   - `CLAUDE.md` → SystemDocValidator
   - `*-standards.md` → StandardsDocValidator
   - `*-guide.md` → UserFacingDocValidator
   - `MIGRATION*.md` → MigrationDocValidator
   - `communication.json` → SessionDocValidator
   - `plan.json` → PlanValidator

2. **Frontmatter-based detection**:
   - `workorder_id` present → WorkorderDocValidator
   - `session_id` present → SessionDocValidator
   - `migration_type` present → MigrationDocValidator

3. **Fallback**:
   - If no match → GeneralMarkdownValidator

**Usage**:
```python
from papertrail.validators.factory import ValidatorFactory

validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))
```

### Score Calculation Algorithm

**Formula**:
```python
score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
score = max(0, score)  # Floor at 0
```

**Severity Levels**:
- **CRITICAL**: Missing required fields, invalid schema structure
- **MAJOR**: Invalid enum values, format violations
- **MINOR**: Recommended field missing
- **WARNING**: Minor style issues, missing optional sections

**Interpretation**:
- 90-100: Excellent (validation passes)
- 70-89: Good (minor issues)
- 50-69: Fair (multiple issues)
- 0-49: Poor (major issues)

### ValidationResult Object

**Structure**:
```python
class ValidationResult:
    valid: bool           # True if score >= 90
    errors: list[ValidationError]
    warnings: list[str]
    score: int           # 0-100
```

**ValidationError**:
```python
class ValidationError:
    severity: ValidationSeverity  # CRITICAL, MAJOR, MINOR, WARNING
    message: str
    field: Optional[str]
```

---

## MCP Tools

**Total:** 2 tools

### 1. validate_document

**Purpose**: Validate a single document against UDS schema

**Input**:
```json
{
  "file_path": "/absolute/path/to/document.md"
}
```

**Output**:
```markdown
# Validation Results: document.md

**Valid:** Yes
**Score:** 98/100
**Category:** foundation

## Warnings (1)

- Missing recommended POWER section: Examples

✅ Document validates successfully!
```

**Usage Example**:
```python
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/path/to/README.md"
})
```

### 2. check_all_docs

**Purpose**: Validate all documents in a directory recursively

**Input**:
```json
{
  "directory": "/absolute/path/to/directory",
  "pattern": "**/*.md"  # Optional, default: **/*.md
}
```

**Output**:
```markdown
# Validation Summary: directory_name

**Total Files:** 10
**Passed:** 8
**Failed:** 2
**Average Score:** 92.5/100

## Results

✅ **README.md** - Score: 98/100
✅ **ARCHITECTURE.md** - Score: 95/100
❌ **INVALID.md** - Score: 45/100 (3 errors, 2 warnings)
```

**Usage Example**:
```python
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/docs",
    "pattern": "**/*.md"
})
```

---

## Validator Organization

**Standard:** Each validator type has its own dedicated folder

**Structure:**
```
validators/
├── resource-sheets/     # RSMS v2.0 compliance validation
│   └── validate.ps1
├── scripts/             # Script/test frontmatter validation
│   └── validate.py
├── plans/               # plan.json schema validation
│   ├── validate.py
│   ├── format_validator.py
│   └── schema_validator.py
├── sessions/            # communication.json validation (multi-agent sessions)
│   └── validate.ps1
└── typescript/          # TypeScript-specific validators
    └── (6 files)
```

### Resource Sheet Validation

**Script:** `validators/resource-sheets/validate.ps1`

**Purpose:** RSMS v2.0 compliance validation (snake_case fields, required metadata)

**Usage:**
```powershell
.\validators\resource-sheets\validate.ps1 -Path "docs/"
```

**Current Validation Checks:**
1. ✅ YAML front matter presence (must start with `---`)
2. ✅ Required UDS fields: `agent`, `date`, `task` (snake_case)
3. ✅ Date format validation (`YYYY-MM-DD`)
4. ✅ Task enum validation (`REVIEW`, `CONSOLIDATE`, `DOCUMENT`, `UPDATE`, `CREATE`)
5. ✅ Naming convention (`{ComponentName}-RESOURCE-SHEET.md`)
6. ✅ UDS section headers (`Executive Summary`, `Audience & Intent`, `Quick Reference`)
7. ✅ No Emojis (detects and reports emoji characters)

**RSMS v2.0 Validation (COMPLETE):**
- ✅ **subject** field validation (required)
- ✅ **parent_project** field validation (required)
- ✅ **category** field validation (required, enum check)
- ✅ **version** field validation (semver format)
- ✅ **related_files** validation (file path format)
- ✅ **related_docs** validation (`.md` file format)

**Integration Points:**
- Run manually after creating/updating resource sheets: `.\validators\documentation\validate-resource-sheets.ps1 -Path "docs/"`
- Can be integrated into pre-commit hooks
- Should be run before archiving workorders

**Example Output:**
```
✅ YAML Front Matter
✅ Naming Convention
✅ PASSED
```

### Script/Test Frontmatter Validation

**Script:** `validators/scripts/validate.py`

**Purpose:** Triangular bidirectional reference validation (resource sheet ↔ script ↔ test)

**Usage:**
```bash
python validators/scripts/validate.py /path/to/project
python validators/scripts/validate.py /path/to/project --path src/
```

**Validation Checks:**
1. ✅ YAML frontmatter presence in scripts/tests
2. ✅ Required field: `resource_sheet`
3. ✅ Script has `related_test`, test has `related_script`
4. ✅ Resource sheet exists and lists file in `related_files`
5. ✅ Bidirectional consistency (script ↔ test references match)

**Supported Languages:** Python (.py), Bash (.sh), PowerShell (.ps1), TypeScript (.ts), JavaScript (.js)

### Session Validation

**Script:** `validators/sessions/validate.ps1`

**Purpose:** Validates multi-agent session communication files against JSON schema

**Usage:**
```bash
# Validate all sessions
pwsh validators/sessions/validate.ps1

# Verbose output (show workorder, status, agent counts)
pwsh validators/sessions/validate.ps1 -Verbose

# Auto-fix common status typos
pwsh validators/sessions/validate.ps1 -FixTypos
```

**Validation Checks:**
1. ✅ Workorder ID format: `WO-{CATEGORY}-{ID}-###`
2. ✅ Feature name format: kebab-case
3. ✅ Status enums: `not_started`, `in_progress`, `complete`
4. ✅ Agent IDs: Valid CodeRef ecosystem agents
5. ✅ File paths: Absolute Windows paths
6. ✅ Required fields: workorder_id, feature_name, created, status, description, instructions_file, orchestrator, agents

**Auto-Fix Typos:**
- `completed` → `complete`
- `done` → `complete`
- `finished` → `complete`
- `started` → `in_progress`
- `running` → `in_progress`
- `pending` → `not_started`

**Schema:** `schemas/sessions/communication-schema.json`

---

## File Structure

```
papertrail/
├── CLAUDE.md                    # This file
├── README.md                    # User documentation
├── pyproject.toml              # Python package config
├── src/
│   └── papertrail/
│       ├── __init__.py
│       ├── validator.py        # UDS/RSMS schema validation
│       ├── health.py           # Health scoring
│       ├── templates.py        # Jinja2 engine
│       └── logger.py           # Workorder logging
├── schemas/
│   ├── documentation/
│   │   ├── resource-sheet-metadata-schema.json  # RSMS v2.0 schema
│   │   └── script-frontmatter-schema.json       # Script/test frontmatter schema
│   ├── sessions/
│   │   └── communication-schema.json            # Multi-agent session schema
│   ├── uds-document.json       # UDS schema (workorder-based docs)
│   └── workorder-log.json      # Workorder log schema
├── standards/
│   └── documentation/
│       ├── global-documentation-standards.md    # Global standards (headers, footers, no emojis)
│       ├── resource-sheet-standards.md          # RSMS v2.0 standards
│       └── script-frontmatter-standards.md      # Script/test frontmatter standards
├── scripts/
│   └── remove-emojis.py         # Emoji removal utility
├── docs/
│   ├── RSMS-SPECIFICATION.md   # RSMS v1.0 specification
│   └── RESOURCE-SHEET-*.md     # Resource sheets (using RSMS)
└── coderef/
    └── workorder/              # Active workorders
        └── resource-sheet-metadata/  # WO-RSMS-METADATA-001
```

---

## Integration with CodeRef Ecosystem

**Used by:**
- coderef-docs - Document generation with UDS compliance
- coderef-workflow - Workorder logging and tracking
- All MCP servers - Documentation validation

**Depends on:**
- None (foundational library)

---

## Design Decisions

**1. Python Library + MCP Server (Hybrid)**
- ✅ Chosen: Both library and MCP tools
- ❌ Rejected: MCP-only or library-only
- Reason: Library for programmatic use, MCP for agent integration

**2. 4-Factor Health Scoring**
- ✅ Chosen: Traceability (40%), Completeness (30%), Freshness (20%), Validation (10%)
- ❌ Rejected: Simple pass/fail validation
- Reason: Weighted scoring provides actionable quality metrics

**3. Jinja2 with CodeRef Extensions**
- ✅ Chosen: Extend Jinja2 with git/workflow/code intelligence filters
- ❌ Rejected: Custom template language
- Reason: Leverage existing ecosystem, add CodeRef-specific helpers

**4. Dual Metadata Standards (UDS + RSMS)**
- ✅ Chosen: Separate standards for implementation docs vs architectural docs
- ❌ Rejected: Single metadata standard for all docs
- Reason: Implementation docs need workorder tracking, architectural docs need versioning/relationships - different purposes require different metadata

---

## Status

**Current Phase:** Production + Active Development
**Active Workorder:** WO-RSMS-METADATA-001

**Completed:**
- ✅ UDS schema definition (workorder-based docs)
- ✅ Validation engine
- ✅ Health scoring (0-100)
- ✅ Workorder logging
- ✅ MCP tool exposure
- ✅ Template engine with extensions

**In Progress (WO-RSMS-METADATA-001):**
- 🔄 RSMS schema definition (resource sheets)
- 🔄 RSMS validation integration
- 🔄 /create-resource-sheet template update
- 🔄 Documentation and migration

---

## Metadata Standards Comparison

| Aspect | UDS | RSMS | Standard Markdown |
|--------|-----|------|-------------------|
| **Purpose** | Implementation docs | Architectural docs | General docs |
| **Workorder ID** | ✅ Required | ❌ Not applicable | ❌ Not applicable |
| **Versioning** | ❌ Not tracked | ✅ Semver required | ❌ Not tracked |
| **MCP Attribution** | ✅ Required | ❌ Not applicable | ❌ Not applicable |
| **Relationships** | ❌ Not tracked | ✅ related_files, related_docs | ❌ Not tracked |
| **Use Case** | Plan.json, DELIVERABLES.md | Resource sheets, architecture docs | README, guides |
| **Validation** | ✅ Schema-based | ✅ Schema-based | ❌ None |

---

**Maintained by:** CodeRef Ecosystem
**Attribution:** Part of CodeRef v2 ecosystem
