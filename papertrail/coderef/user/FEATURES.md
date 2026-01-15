---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
feature_id: user-docs-generation
doc_type: user-facing
audience: developers
version: "1.0.0"
status: APPROVED
---

# Papertrail Features

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0)**

---

## Overview

Papertrail provides **7 core features** for validating, scoring, and monitoring documentation quality across the CodeRef ecosystem. This document shows what Papertrail can do, how each feature works, and when to use it.

---

## Table of Contents

1. [Universal Documentation Standards (UDS) Validation](#1-universal-documentation-standards-uds-validation)
2. [Resource Sheet Metadata Standards (RSMS v2.0)](#2-resource-sheet-metadata-standards-rsms-v20)
3. [15 Validator Components](#3-15-validator-components)
4. [7 MCP Tools](#4-7-mcp-tools)
5. [Score-Based Validation (0-100 Scale)](#5-score-based-validation-0-100-scale)
6. [ValidatorFactory Auto-Detection](#6-validatorfactory-auto-detection)
7. [Completeness Metric (Foundation Docs)](#7-completeness-metric-foundation-docs)
8. [Feature Comparison](#feature-comparison)
9. [Benefits by User Type](#benefits-by-user-type)

---

## 1. Universal Documentation Standards (UDS) Validation

### What It Does

Validates markdown documents against 11 JSON Schema Draft-07 files covering 13 document categories. Ensures all docs have required metadata (agent, date, task) and category-specific fields.

### How It Works

```
File → ValidatorFactory → BaseUDSValidator → Schema → ValidationResult (score 0-100)
```

### Schema Coverage

| Schema | Document Types | Required Fields |
|--------|----------------|----------------|
| `base-frontmatter-schema.json` | All markdown | agent, date, task |
| `foundation-doc-frontmatter-schema.json` | README, API, ARCHITECTURE, SCHEMA, COMPONENTS | +workorder_id, generated_by, feature_id, doc_type |
| `resource-sheet-metadata-schema.json` | Resource sheets (RSMS v2.0) | +subject, parent_project, category |
| `workorder-doc-frontmatter-schema.json` | DELIVERABLES, context, analysis | +workorder_id, feature_id |
| `system-doc-frontmatter-schema.json` | CLAUDE.md, SYSTEM.md | +project, version, status |
| `standards-doc-frontmatter-schema.json` | Coding/doc standards | +scope, version, enforcement |
| `user-facing-doc-frontmatter-schema.json` | Guides, tutorials, FAQs | +audience, doc_type |
| `migration-doc-frontmatter-schema.json` | Migration guides | +migration_type, from_version, to_version |
| `infrastructure-doc-frontmatter-schema.json` | FILE-TREE, INVENTORY, INDEX | +infra_type, environment, platform |
| `session-doc-frontmatter-schema.json` | communication.json, instructions.json | +session_type, session_id, orchestrator |
| `script-frontmatter-schema.json` | Script/test file frontmatter | +resource_sheet |

### Use Cases

- **Pre-commit validation**: Ensure all committed docs meet UDS standards
- **CI/CD quality gates**: Block PRs with invalid documentation
- **Documentation audits**: Identify docs missing required metadata
- **Workorder tracking**: Link docs to workorders via workorder_id field

### Example

```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-EXAMPLE-001
generated_by: coderef-docs v1.0.0
feature_id: example-feature
doc_type: readme
---

# My Project
...
```

**Validation**: ✅ Passes UDS validation (score: 100/100)

---

## 2. Resource Sheet Metadata Standards (RSMS v2.0)

### What It Does

Validates architectural reference documents (resource sheets) with versioning, relationship tracking, and naming conventions. Enforces snake_case frontmatter and PascalCase-with-hyphens filenames.

### Requirements

- **Naming Convention**: `{Subject}-RESOURCE-SHEET.md` (e.g., `AuthService-RESOURCE-SHEET.md`)
- **Required Fields**: `agent`, `date`, `task`, `subject`, `parent_project`, `category` (all snake_case)
- **Category Enum**: 11 values (service, controller, model, utility, integration, component, middleware, validator, schema, config, other)
- **Optional Fields**: `version`, `related_files`, `related_docs`, `workorder`, `tags`, `status`

### Compliance Threshold

Score >= 90/100

### Use Cases

- **Resource sheet creation**: Validate during `/create-resource-sheet` workflow
- **Architecture documentation**: Track relationships between components
- **Version tracking**: Monitor resource sheet versions with semver
- **Triangular references**: Link resource sheets ↔ scripts ↔ tests

### Example

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
related_docs:
  - BaseUDSValidator-RESOURCE-SHEET.md
workorder: WO-VALIDATION-ENHANCEMENT-001
tags:
  - validation
  - foundation-docs
status: APPROVED
---

# FoundationDocValidator Resource Sheet
...
```

**Validation**: ✅ Passes RSMS v2.0 validation (score: 100/100)

---

## 3. 15 Validator Components

### What It Does

Implements validation logic for 13 document categories using Template Method pattern. Provides BaseUDSValidator abstract class with 8 methods and 14 category-specific validators.

### Component Hierarchy

```
UDSValidator (interface)
└── BaseUDSValidator (abstract base, 150+ lines, 8 methods)
    ├── FoundationDocValidator (README, API, ARCHITECTURE, SCHEMA, COMPONENTS)
    ├── WorkorderDocValidator (DELIVERABLES, context, analysis)
    ├── SystemDocValidator (CLAUDE.md, SYSTEM.md)
    ├── StandardsDocValidator (coding/doc standards)
    ├── UserFacingDocValidator (guides, tutorials, FAQs)
    ├── MigrationDocValidator (migration guides, breaking changes)
    ├── InfrastructureDocValidator (FILE-TREE, INVENTORY, INDEX)
    ├── SessionDocValidator (communication.json, instructions.json)
    ├── PlanValidator (plan.json structure validation)
    ├── ResourceSheetValidator (RSMS v2.0 compliance)
    ├── StubValidator (stub.json validation)
    ├── AnalysisValidator (analysis.json validation)
    ├── ExecutionLogValidator (execution-log.json validation)
    └── GeneralMarkdownValidator (fallback for unclassified docs)

ValidatorFactory (auto-detection via 30+ path patterns)
```

### BaseUDSValidator Methods

- `validate_file(file_path)` - Main entry point (template method)
- `validate_content(content, file_path)` - Validate content string
- `validate_specific(frontmatter, content, file_path)` - Abstract hook method (subclasses implement)
- `_calculate_score(errors, warnings)` - Calculate 0-100 score
- `_calculate_completeness(frontmatter, content)` - Calculate 0-100% section coverage
- `_load_schema()` - Load and resolve allOf references
- `_extract_frontmatter(content)` - Parse YAML front matter
- `_validate_required_sections(frontmatter, content)` - Check doc_type sections

### Use Cases

- **Extensibility**: Add new validators by extending BaseUDSValidator
- **Custom validation**: Override validate_specific() for category-specific checks
- **Code reuse**: Inherit common logic (schema loading, scoring, completeness)

### Example: Custom Validator

```python
from papertrail.validators.base import BaseUDSValidator
from papertrail.validator import ValidationError, ValidationSeverity

class CustomDocValidator(BaseUDSValidator):
    schema_name = "custom-doc-schema.json"
    doc_category = "custom"

    def validate_specific(self, frontmatter, content, file_path):
        errors = []
        warnings = []

        if "custom_field" not in frontmatter:
            errors.append(ValidationError(
                severity=ValidationSeverity.MAJOR,
                message="Missing custom_field",
                field="custom_field"
            ))

        return (errors, warnings)
```

---

## 4. 7 MCP Tools

### What It Does

Exposes validation capabilities via Model Context Protocol (MCP) for AI agents (Claude Code, coderef-docs). Provides 7 tools via stdio transport.

### Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `validate_stub` | Validate stub.json with auto-fill | file_path, auto_fill, save | Validation report |
| `validate_resource_sheet` | RSMS v2.0 validation | file_path | Score (0-100) |
| `check_all_resource_sheets` | Batch RSMS validation | directory | Summary with avg score |
| `validate_document` | UDS validation (auto-detect) | file_path | Score (0-100) |
| `check_all_docs` | Batch UDS validation | directory, pattern | Summary with avg score |
| `validate_schema_completeness` | Schema sync validation | schema_name | Completeness report |
| `validate_all_schemas` | Batch schema validation | (none) | Summary with issues |

### Transport

**Protocol**: MCP 1.0
**Transport**: stdio (standard input/output)
**Format**: JSON-RPC 2.0

### Use Cases

- **AI agent integration**: Claude Code calls tools for validation
- **Automated workflows**: coderef-docs validates generated docs
- **CI/CD pipelines**: Call tools for quality gates
- **Custom automation**: Integrate with any MCP-compatible client

### Example

```python
# Via MCP client
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/path/to/README.md"
})

# Returns:
# Valid: True
# Score: 95/100
# Completeness: 80%
# Category: foundation
```

---

## 5. Score-Based Validation (0-100 Scale)

### What It Does

Provides actionable quality metrics instead of binary pass/fail. Uses weighted severity deductions to calculate 0-100 score.

### Formula

```
score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
score = max(0, score)
```

### Severity Deductions

| Severity | Points Deducted | Examples |
|----------|----------------|----------|
| CRITICAL | -50 | Missing required field, invalid schema structure |
| MAJOR | -20 | Invalid enum value, format violation |
| MINOR | -10 | Recommended field missing |
| WARNING | -5 | Style issues, missing optional sections |
| Warnings | -2 each | Informational messages |

### Validation Thresholds

| Score Range | Status | Action |
|-------------|--------|--------|
| 90-100 | ✅ Excellent | Validation passes |
| 70-89 | ⚠️ Good | Minor issues, consider fixing |
| 50-69 | ⚠️ Fair | Multiple issues, should fix |
| 0-49 | ❌ Poor | Major issues, must fix |

### Use Cases

- **Progressive improvement**: Identify highest-impact fixes (CRITICAL first)
- **Quality metrics**: Track average score across documentation
- **CI/CD thresholds**: Fail builds if score < 90
- **Reporting**: Generate quality reports with score distributions

### Example

```
# Document with 2 MAJOR errors + 1 WARNING
score = 100 - 20*2 - 5*1 = 55/100 (Fair)

# Fix both MAJOR errors → score = 100 - 5 = 95/100 (Excellent) ✅
```

---

## 6. ValidatorFactory Auto-Detection

### What It Does

Automatically detects appropriate validator from file path and frontmatter using 30+ regex patterns. Eliminates need for manual validator selection.

### Path Patterns (30+)

| Pattern | Validator |
|---------|-----------|
| `.*-RESOURCE-SHEET\.md$` | ResourceSheetValidator |
| `.*/README\.md$` | FoundationDocValidator |
| `.*/DELIVERABLES\.md$` | WorkorderDocValidator |
| `.*/CLAUDE\.md$` | SystemDocValidator |
| `.*/plan\.json$` | PlanValidator |
| `.*/communication\.json$` | SessionDocValidator |
| `.*/stub\.json$` | StubValidator |
| (+ 23 more patterns) | ... |

### Detection Logic

1. **Try path-based detection** (30+ regex patterns)
2. **Try frontmatter-based detection** (workorder_id → WorkorderDocValidator)
3. **Fallback to GeneralMarkdownValidator**

### Use Cases

- **Simplified API**: No need to specify validator type
- **Convention over configuration**: Filename determines validator
- **Flexibility**: Supports both path and frontmatter detection

### Example

```python
from papertrail.validators.factory import ValidatorFactory
from pathlib import Path

# Auto-detects FoundationDocValidator from filename
validator = ValidatorFactory.get_validator(Path("README.md"))

# Auto-detects ResourceSheetValidator from filename
validator = ValidatorFactory.get_validator(Path("AuthService-RESOURCE-SHEET.md"))

# Auto-detects PlanValidator from filename
validator = ValidatorFactory.get_validator(Path("plan.json"))
```

---

## 7. Completeness Metric (Foundation Docs)

### What It Does

Tracks section coverage for foundation docs (README, API, ARCHITECTURE, SCHEMA, COMPONENTS). Measures how many required sections are present.

### Formula

```
completeness = (sections_found / sections_required) * 100
```

### Required Sections by Doc Type

| Doc Type | Required Sections |
|----------|-------------------|
| readme | Purpose, Overview, What/Why/When, Examples, References |
| api | Endpoints, Authentication, Request/Response Examples, Error Codes |
| schema | Data Models, Field Descriptions, Validation Rules, Relationships |
| components | Component Catalog, Props/Parameters, Usage Examples, Dependencies |
| architecture | System Overview, Key Components, Design Decisions, Integration Points |

### Use Cases

- **Documentation quality**: Ensure all required sections present
- **Template compliance**: Verify POWER framework adherence
- **Progressive documentation**: Track completion progress (60% → 80% → 100%)

### Example

```python
# README.md (doc_type: readme)
Required: ["Purpose", "Overview", "What/Why/When", "Examples", "References"]
Found: ["Purpose", "Overview", "Examples"] = 3/5 = 60%

# Add missing sections → 5/5 = 100% ✅
```

---

## Feature Comparison

| Feature | Purpose | Input | Output | Use When |
|---------|---------|-------|--------|----------|
| **UDS Validation** | Validate markdown metadata | file_path | Score (0-100) | Any markdown doc |
| **RSMS v2.0** | Validate resource sheets | file_path | Score (0-100) | Resource sheets only |
| **15 Validators** | Category-specific validation | content | errors, warnings | Extending system |
| **7 MCP Tools** | AI agent integration | via MCP | ValidationResult | Claude Code, automation |
| **Score-Based** | Actionable quality metrics | errors | score (0-100) | CI/CD, reporting |
| **Auto-Detection** | Automatic validator selection | file_path | validator | All validation |
| **Completeness** | Section coverage tracking | frontmatter, content | percentage (0-100%) | Foundation docs |

---

## Benefits by User Type

### For AI Agents (Claude Code, coderef-docs)

✅ **MCP Integration**: 7 tools for validation via stdio transport
✅ **Auto-detection**: No need to specify validator type
✅ **Detailed errors**: Severity, message, field for each error
✅ **Score-based**: Actionable 0-100 metric instead of binary pass/fail

### For Developers

✅ **Pre-commit validation**: Ensure docs meet standards before commit
✅ **Extensibility**: Add custom validators by extending BaseUDSValidator
✅ **Clear thresholds**: Score >= 90 = passing
✅ **Progressive improvement**: Fix CRITICAL errors first for biggest impact

### For Documentation Writers

✅ **UDS compliance**: Ensure required metadata (agent, date, task)
✅ **Completeness tracking**: See which sections missing (60% → 100%)
✅ **RSMS v2.0**: Validate resource sheets with version tracking
✅ **Immediate feedback**: Real-time validation results with scores

### For Project Managers

✅ **Quality metrics**: Track average score across all docs
✅ **Workorder tracking**: Link docs to workorders via workorder_id
✅ **CI/CD gates**: Block PRs with invalid documentation
✅ **Audit reports**: Batch validate entire directory with summaries

---

## Getting Started

1. **Install Papertrail**: `pip install -e .`
2. **Configure MCP Server**: Add papertrail to `~/.mcp.json`
3. **Validate a doc**: Call `validate_document` tool
4. **Review score**: Aim for >= 90/100
5. **Fix errors**: Address CRITICAL, then MAJOR, then MINOR
6. **Re-validate**: Verify score improved

**For complete tutorial, see:** `coderef/user/USER-GUIDE.md`
**For quick tool lookup, see:** `coderef/user/my-guide.md`
**For API reference, see:** `coderef/foundation-docs/API.md`

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem
