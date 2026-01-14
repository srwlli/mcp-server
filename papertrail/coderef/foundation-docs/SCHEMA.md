---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
generated_by: coderef-docs v1.0.0
feature_id: foundation-docs-generation
doc_type: schema
version: "1.0.0"
status: APPROVED
---

# Papertrail Schema Reference

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0)**

---

## Purpose

This document provides complete schema reference for all 11 JSON schemas in Papertrail, defining field validation rules, inheritance patterns, and required_sections per doc_type for UDS and RSMS v2.0 compliance.

## Overview

Papertrail uses **11 JSON Schema Draft-07 schemas** to validate document frontmatter and JSON files:

| Schema | Purpose | Required Fields | Optional Fields | Doc Types |
|--------|---------|----------------|----------------|-----------|
| `base-frontmatter-schema.json` | UDS base fields (all markdown) | agent, date, task | timestamp | N/A |
| `foundation-doc-frontmatter-schema.json` | Foundation docs (README, API, etc.) | +workorder_id, generated_by, feature_id, doc_type | title, version, status | 5 (readme, architecture, api, schema, components) |
| `resource-sheet-metadata-schema.json` | Resource sheets (RSMS v2.0) | +subject, parent_project, category | version, related_files, related_docs, workorder, tags, status | N/A |
| `workorder-doc-frontmatter-schema.json` | Workorder docs (DELIVERABLES, etc.) | +workorder_id, feature_id | status | 1 (workorder) |
| `system-doc-frontmatter-schema.json` | System docs (CLAUDE.md, etc.) | +project, version, status | N/A | 1 (system) |
| `standards-doc-frontmatter-schema.json` | Standards docs | +scope, version, enforcement | N/A | 1 (standards) |
| `user-facing-doc-frontmatter-schema.json` | User guides, tutorials | +audience, doc_type | difficulty, prerequisites | 3 (guide, tutorial, quickstart) |
| `migration-doc-frontmatter-schema.json` | Migration docs | +migration_type, from_version, to_version | breaking_changes | 1 (migration) |
| `infrastructure-doc-frontmatter-schema.json` | Infrastructure docs | +infra_type, environment, platform | N/A | 1 (infrastructure) |
| `session-doc-frontmatter-schema.json` | Session communication files | +session_type, session_id, orchestrator | participants | 1 (session) |
| `script-frontmatter-schema.json` | Script/test file frontmatter | +resource_sheet | related_test, related_script | N/A |

**Total Schemas:** 11 (1 base + 10 category-specific)

---

## Data Models

Papertrail defines 11 JSON schemas representing documentation metadata models:
- **Base Model**: `base-frontmatter-schema.json` (3 required fields: agent, date, task)
- **Category Models**: 10 specialized schemas extending the base model via `allOf` pattern
- **Inheritance**: All category schemas inherit base fields + add category-specific requirements

See [What: Schema Definitions](#what-schema-definitions) for complete data model structure.

## Field Descriptions

All schemas define field constraints using JSON Schema Draft-07:
- **Type validation**: string, number, boolean, array, object
- **Pattern validation**: Regex patterns (workorder_id, date, version, kebab-case, snake_case)
- **Enum validation**: Restricted value lists (task, status, category, doc_type)
- **Length validation**: minLength, maxLength constraints
- **Required vs Optional**: Clearly defined per schema

See individual schema sections for complete field descriptions.

## Validation Rules

Schema validation enforces:
- **Format rules**: Date format (YYYY-MM-DD), workorder format (WO-{CAT}-###), semver (X.Y.Z)
- **Naming rules**: kebab-case (feature_id), snake_case (RSMS frontmatter), UPPER_SNAKE_CASE (task enum)
- **Required sections**: Per doc_type (readme, api, schema, components, architecture)
- **Inheritance rules**: Category schemas must extend base-frontmatter-schema.json
- **Completeness scoring**: 0-100% based on present/required section ratio

## Relationships

Schema relationships follow 3-tier hierarchy:
- **Tier 1 (Base)**: `base-frontmatter-schema.json` → All markdown inherits
- **Tier 2 (Categories)**: 10 category schemas extend base via `allOf`
- **Tier 3 (Types)**: Doc-specific variations (doc_type enum determines required_sections)

Cross-schema dependencies:
- Foundation schemas reference base schema via `$ref: "./base-frontmatter-schema.json"`
- ValidatorFactory maps file paths → schemas → validators
- Score calculation aggregates errors across base + category validation

---

## What: Schema Definitions

### 1. Base Frontmatter Schema

**File**: `schemas/documentation/base-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Universal fields required for ALL markdown documents in CodeRef ecosystem

**Required Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `agent` | string | minLength: 1, maxLength: 100 | Name of agent/contributor who created/updated document |
| `date` | string | pattern: `^\d{4}-\d{2}-\d{2}$` | Date in YYYY-MM-DD format |
| `task` | string | enum: [CREATE, UPDATE, REVIEW, DOCUMENT, CONSOLIDATE, MIGRATE, ARCHIVE] | Type of work performed |

**Optional Fields** (1):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `timestamp` | string | pattern: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$` | ISO 8601 timestamp with timezone |

**Example**:
```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
timestamp: "2026-01-13T12:00:00Z"
---
```

**Validation Rules**:
- `agent`: Must be 1-100 characters
- `date`: Must match YYYY-MM-DD format (e.g., `2026-01-13`)
- `task`: Must be one of 7 enum values
- `timestamp`: Optional but must be ISO 8601 with timezone if provided

---

### 2. Foundation Doc Frontmatter Schema

**File**: `schemas/documentation/foundation-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Foundation documentation (README, ARCHITECTURE, API, SCHEMA, COMPONENTS) generated by coderef-docs

**Inheritance**: Extends `base-frontmatter-schema.json` via `allOf`

**Additional Required Fields** (4):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `workorder_id` | string | pattern: `^WO-[A-Z0-9-]+-\d{3}$` | Workorder tracking ID (format: WO-{FEATURE}-{CATEGORY}-###) |
| `generated_by` | string | pattern: `^coderef-docs` | MCP server/tool that generated document |
| `feature_id` | string | pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`, minLength: 1, maxLength: 100 | Feature identifier (kebab-case) |
| `doc_type` | string | enum: [readme, architecture, api, schema, components] | Type of foundation document |

**Additional Optional Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `title` | string | minLength: 1, maxLength: 200 | Document title |
| `version` | string | pattern: `^\d+\.\d+\.\d+$` | Semantic version (e.g., 1.0.0) |
| `status` | string | enum: [DRAFT, REVIEW, APPROVED, DEPRECATED] | Document status lifecycle |

**Required Sections by doc_type**:

| doc_type | Required Sections | Count |
|----------|-------------------|-------|
| `readme` | Purpose, Overview, What/Why/When, Examples, References | 5 |
| `architecture` | System Overview, Key Components, Design Decisions, Integration Points | 4 |
| `api` | Endpoints, Authentication, Request/Response Examples, Error Codes | 4 |
| `schema` | Data Models, Field Descriptions, Validation Rules, Relationships | 4 |
| `components` | Component Catalog, Props/Parameters, Usage Examples, Dependencies | 5 |

**Example**:
```yaml
---
agent: coderef-docs v1.2.0
date: "2026-01-13"
task: DOCUMENT
workorder_id: WO-VALIDATION-ENHANCEMENT-001
generated_by: coderef-docs v1.2.0
feature_id: foundation-docs-generation
doc_type: api
title: Papertrail API Reference
version: "1.0.0"
status: APPROVED
---
```

**Validation Rules**:
- `workorder_id`: Must match `WO-{FEATURE}-{CATEGORY}-###` pattern
- `generated_by`: Must start with `coderef-docs`
- `feature_id`: Must be kebab-case (lowercase with hyphens)
- `doc_type`: Must be one of 5 foundation types
- `version`: Must be semantic versioning (X.Y.Z)
- `status`: Must be one of 4 lifecycle states

---

### 3. Resource Sheet Metadata Schema (RSMS v2.0)

**File**: `schemas/documentation/resource-sheet-metadata-schema.json`
**Version**: 2.0.0
**Purpose**: Resource/reference sheets for components, services, and architectural elements

**Required Fields** (6):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `agent` | string | minLength: 1, maxLength: 100 | Agent/contributor name (UDS required) |
| `date` | string | pattern: `^\d{4}-\d{2}-\d{2}$` | Date in YYYY-MM-DD format (UDS required) |
| `task` | string | enum: [REVIEW, CONSOLIDATE, DOCUMENT, UPDATE, CREATE] | Type of work (UDS required) |
| `subject` | string | minLength: 1, maxLength: 200 | Primary component/service/topic being documented (RSMS required) |
| `parent_project` | string | minLength: 1, maxLength: 100 | Parent project/codebase (RSMS required) |
| `category` | string | enum: [service, controller, model, utility, integration, component, middleware, validator, schema, config, other] | Resource type classification (RSMS required) |

**Optional Fields** (7):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `timestamp` | string | pattern: ISO 8601 with timezone | Optional timestamp |
| `version` | string | pattern: `^\d+\.\d+\.\d+$` | Semantic version (RSMS recommended) |
| `related_files` | array[string] | pattern: `^[a-zA-Z0-9/_.-]+\.[a-zA-Z0-9]+$`, uniqueItems | Source code files (enables navigation) |
| `related_docs` | array[string] | pattern: `^[a-zA-Z0-9/_.-]+\.md$`, uniqueItems | Related documentation files |
| `workorder` | string | pattern: `^WO-[A-Z0-9-]+-\d{3}$` | Associated workorder ID |
| `tags` | array[string] | minLength: 1, maxLength: 50, uniqueItems | Tags for categorization/search |
| `status` | string | enum: [DRAFT, REVIEW, APPROVED, ARCHIVED] | Documentation status |

**Category Enum** (11 values):
- `service` - Backend services
- `controller` - API controllers
- `model` - Data models
- `utility` - Utility functions
- `integration` - External integrations
- `component` - UI/Frontend components
- `middleware` - Middleware layers
- `validator` - Validation logic
- `schema` - Schema definitions
- `config` - Configuration
- `other` - Uncategorized

**Example**:
```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
subject: FoundationDocValidator
parent_project: papertrail
category: validator
version: "1.0.0"
related_files:
  - papertrail/validators/foundation.py
  - tests/validators/test_foundation.py
related_docs:
  - BaseUDSValidator-RESOURCE-SHEET.md
  - ValidatorFactory-RESOURCE-SHEET.md
workorder: WO-VALIDATION-ENHANCEMENT-001
tags:
  - validation
  - foundation-docs
  - uds
status: APPROVED
---
```

**Validation Rules**:
- `subject`: 1-200 characters (PascalCase recommended)
- `parent_project`: 1-100 characters (kebab-case recommended)
- `category`: Must be one of 11 enum values
- `version`: Must be semantic versioning if provided
- `related_files`: Array of valid file paths (not markdown)
- `related_docs`: Array of markdown file paths ending with `.md`
- `workorder`: Must match workorder ID pattern if provided
- `tags`: Array of 1-50 character strings (unique)

**Naming Convention**: `{Subject}-RESOURCE-SHEET.md` (enforced by ResourceSheetValidator)

**RSMS v2.0 Compliance Threshold**: Score >= 90/100

---

### 4. Workorder Doc Frontmatter Schema

**File**: `schemas/documentation/workorder-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Workorder documentation (DELIVERABLES.md, plan.json, etc.)

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (2):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `workorder_id` | string | pattern: `^WO-[A-Z0-9-]+-\d{3}$` | Workorder tracking ID |
| `feature_id` | string | pattern: kebab-case | Feature identifier |

**Additional Optional Fields** (1):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `status` | string | enum: [PLANNING, IN_PROGRESS, TESTING, COMPLETE, ARCHIVED] | Workorder status |

**Example**:
```yaml
---
agent: Lloyd
date: "2026-01-13"
task: UPDATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
feature_id: validation-enhancement
status: COMPLETE
---
```

---

### 5. System Doc Frontmatter Schema

**File**: `schemas/documentation/system-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: System documentation (CLAUDE.md, SESSION-INDEX.md, etc.)

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `project` | string | minLength: 1, maxLength: 100 | Project name |
| `version` | string | pattern: `^\d+\.\d+\.\d+$` | Project version |
| `status` | string | enum: [DEVELOPMENT, PRODUCTION, DEPRECATED] | Project status |

**Example**:
```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: UPDATE
project: papertrail
version: "1.0.0"
status: PRODUCTION
---
```

---

### 6. Standards Doc Frontmatter Schema

**File**: `schemas/documentation/standards-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Standards documentation (coding standards, style guides, etc.)

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `scope` | string | enum: [project, organization, team] | Standards scope |
| `version` | string | pattern: `^\d+\.\d+\.\d+$` | Standards version |
| `enforcement` | string | enum: [mandatory, recommended, optional] | Enforcement level |

**Example**:
```yaml
---
agent: Marcus
date: "2026-01-13"
task: CREATE
scope: organization
version: "1.0.0"
enforcement: mandatory
---
```

---

### 7. User-Facing Doc Frontmatter Schema

**File**: `schemas/documentation/user-facing-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: User guides, tutorials, FAQs, and quickstarts

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (2):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `audience` | string | minLength: 1, maxLength: 100 | Target audience |
| `doc_type` | string | enum: [guide, tutorial, faq, quickstart, reference, troubleshooting] | User doc type |

**Additional Optional Fields** (2):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `difficulty` | string | enum: [beginner, intermediate, advanced] | Difficulty level |
| `prerequisites` | array[string] | Array of prerequisite topics | Prerequisites |

**Example**:
```yaml
---
agent: Ava
date: "2026-01-13"
task: CREATE
audience: developers
doc_type: tutorial
difficulty: intermediate
prerequisites:
  - Basic Python knowledge
  - Understanding of JSON Schema
---
```

---

### 8. Migration Doc Frontmatter Schema

**File**: `schemas/documentation/migration-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Migration guides, breaking change docs, audit reports

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `migration_type` | string | enum: [version_upgrade, api_change, schema_migration, breaking_change] | Migration type |
| `from_version` | string | pattern: `^\d+\.\d+\.\d+$` | Source version |
| `to_version` | string | pattern: `^\d+\.\d+\.\d+$` | Target version |

**Additional Optional Fields** (1):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `breaking_changes` | array[string] | Array of breaking change descriptions | Breaking changes |

**Example**:
```yaml
---
agent: Quinn
date: "2026-01-13"
task: DOCUMENT
migration_type: breaking_change
from_version: "1.0.0"
to_version: "2.0.0"
breaking_changes:
  - Removed deprecated validate_file() method
  - Changed ValidationResult structure
---
```

---

### 9. Infrastructure Doc Frontmatter Schema

**File**: `schemas/documentation/infrastructure-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Infrastructure documentation (FILE-TREE.md, INVENTORY.md, etc.)

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `infra_type` | string | enum: [file_tree, inventory, index, catalog] | Infrastructure doc type |
| `environment` | string | enum: [development, staging, production, all] | Environment scope |
| `platform` | string | enum: [windows, linux, macos, cross_platform] | Platform scope |

**Example**:
```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
infra_type: file_tree
environment: all
platform: cross_platform
---
```

---

### 10. Session Doc Frontmatter Schema

**File**: `schemas/documentation/session-doc-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Multi-agent session communication files (communication.json, instructions.json)

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (3):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `session_type` | string | enum: [multi_agent, single_agent, orchestrated] | Session type |
| `session_id` | string | pattern: kebab-case | Session identifier |
| `orchestrator` | string | Agent name coordinating session | Orchestrator agent name |

**Additional Optional Fields** (1):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `participants` | array[string] | Array of agent names | Participating agents |

**Example**:
```yaml
---
agent: Lloyd
date: "2026-01-13"
task: CREATE
session_type: multi_agent
session_id: foundation-docs-consolidation-review
orchestrator: Lloyd
participants:
  - Ava
  - Taylor
  - Marcus
---
```

---

### 11. Script Frontmatter Schema

**File**: `schemas/documentation/script-frontmatter-schema.json`
**Version**: 1.0.0
**Purpose**: Script and test file frontmatter (triangular bidirectional reference validation)

**Inheritance**: Extends `base-frontmatter-schema.json`

**Additional Required Fields** (1):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `resource_sheet` | string | pattern: `.*-RESOURCE-SHEET\.md$` | Related resource sheet file |

**Additional Optional Fields** (2):

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `related_test` | string | File path to related test file | Related test (for scripts) |
| `related_script` | string | File path to related script file | Related script (for tests) |

**Example**:
```python
"""
---
agent: Marcus
date: "2026-01-13"
task: CREATE
resource_sheet: FoundationDocValidator-RESOURCE-SHEET.md
related_test: tests/validators/test_foundation.py
---

FoundationDocValidator implementation
"""
```

---

## Why: Schema Inheritance & Patterns

### Inheritance Hierarchy

```
base-frontmatter-schema.json (3 required: agent, date, task)
├── foundation-doc-frontmatter-schema.json (+4 required: workorder_id, generated_by, feature_id, doc_type)
├── workorder-doc-frontmatter-schema.json (+2 required: workorder_id, feature_id)
├── system-doc-frontmatter-schema.json (+3 required: project, version, status)
├── standards-doc-frontmatter-schema.json (+3 required: scope, version, enforcement)
├── user-facing-doc-frontmatter-schema.json (+2 required: audience, doc_type)
├── migration-doc-frontmatter-schema.json (+3 required: migration_type, from_version, to_version)
├── infrastructure-doc-frontmatter-schema.json (+3 required: infra_type, environment, platform)
└── session-doc-frontmatter-schema.json (+3 required: session_type, session_id, orchestrator)

resource-sheet-metadata-schema.json (6 required: agent, date, task, subject, parent_project, category)
script-frontmatter-schema.json (4 required: agent, date, task, resource_sheet)
```

### allOf Pattern

**All schemas (except RSMS and script)** extend base-frontmatter-schema.json using JSON Schema `allOf`:

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
        "category_specific_field": { ... }
      }
    }
  ]
}
```

**Schema Resolution**: BaseUDSValidator manually merges schemas via `_resolve_allof()` method to avoid network fetch errors from Draft7Validator.

---

## When: Validation Use Cases

### UC-1: Foundation Doc Validation (POWER Framework)
```python
# Validate README.md with POWER framework sections
validator = FoundationDocValidator()
result = validator.validate_file(Path("README.md"))

# Checks:
# - Base fields: agent, date, task ✅
# - Foundation fields: workorder_id, generated_by, feature_id, doc_type ✅
# - Required sections: Purpose, Overview, What/Why/When, Examples, References ✅
# - Score: 98/100 ✅
```

### UC-2: Resource Sheet Validation (RSMS v2.0)
```python
# Validate resource sheet with RSMS v2.0 compliance
validator = ResourceSheetValidator()
result = validator.validate_file(Path("FoundationDocValidator-RESOURCE-SHEET.md"))

# Checks:
# - UDS fields: agent, date, task ✅
# - RSMS fields: subject, parent_project, category ✅
# - Naming: *-RESOURCE-SHEET.md ✅
# - Category enum: validator ✅
# - Score: 96/100 ✅
```

### UC-3: Workorder Doc Validation
```python
# Validate DELIVERABLES.md with workorder tracking
validator = WorkorderDocValidator()
result = validator.validate_file(Path("DELIVERABLES.md"))

# Checks:
# - Base fields ✅
# - Workorder fields: workorder_id, feature_id ✅
# - Status enum ✅
```

---

## Examples: Schema Validation Flow

### Example 1: ValidatorFactory Auto-Detection
```python
from papertrail.validators.factory import ValidatorFactory

# Auto-detect validator based on file path and frontmatter
validator = ValidatorFactory.get_validator(Path("README.md"))
# Returns: FoundationDocValidator (detects README.md pattern)

validator = ValidatorFactory.get_validator(Path("MyComponent-RESOURCE-SHEET.md"))
# Returns: ResourceSheetValidator (detects -RESOURCE-SHEET.md suffix)

validator = ValidatorFactory.get_validator(Path("CLAUDE.md"))
# Returns: SystemDocValidator (detects CLAUDE.md pattern)
```

### Example 2: Schema Completeness Check
```python
from papertrail.tools.sync_schemas import SchemaSyncTool

# Validate foundation schema has required_sections for all doc_types
tool = SchemaSyncTool()
report = tool.generate_schema_report("foundation-doc-frontmatter-schema.json")

# Output:
# - Doc Types: 5
# - Total Sections: 22
# - readme: 5 sections (Purpose, Overview, What/Why/When, Examples, References)
# - architecture: 4 sections
# - api: 4 sections
# - schema: 4 sections
# - components: 5 sections
```

### Example 3: Manual Schema Validation
```python
import json
from jsonschema import validate, Draft7Validator

# Load schema
schema = json.loads(Path("schemas/documentation/base-frontmatter-schema.json").read_text())

# Validate frontmatter
frontmatter = {
    "agent": "Claude Sonnet 4.5",
    "date": "2026-01-13",
    "task": "CREATE"
}

# Validate
validate(instance=frontmatter, schema=schema)
# Success: No errors ✅
```

---

## References

### Internal
- **BaseUDSValidator**: `papertrail/validators/base.py` (abstract base class, _resolve_allof() method)
- **ValidatorFactory**: `papertrail/validators/factory.py` (30+ path patterns for auto-detection)
- **SchemaSyncTool**: `papertrail/tools/sync_schemas.py` (380 lines, 9 methods, schema completeness validation)
- **11 Category Validators**: `papertrail/validators/{foundation,resource_sheet,workorder,system,standards,user_facing,migration,infrastructure,session,general,plan}.py`

### External
- [JSON Schema Draft-07 Specification](https://json-schema.org/draft-07/schema)
- [Universal Documentation Standards (UDS)](../standards/documentation/uds-specification.md)
- [Resource Sheet Metadata Standards (RSMS) v2.0](../standards/documentation/resource-sheet-standards.md)
- [POWER Framework](../standards/documentation/power-framework.md)

### Related Documents
- [API.md](API.md) - MCP tools for validation
- [COMPONENTS.md](COMPONENTS.md) - Validator architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [README.md](README.md) - Project overview

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem - Papertrail MCP Server
