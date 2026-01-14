---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
generated_by: coderef-docs v1.0.0
feature_id: foundation-docs-generation
doc_type: readme
version: "1.0.0"
status: APPROVED
---

# Papertrail

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0)**

**Version:** 1.0.0
**Type:** Python Library + MCP Server
**Purpose:** Document validation and standards enforcement for the CodeRef ecosystem

---

## Purpose

Papertrail provides a **Python library and MCP server** for validating documents against Universal Documentation Standards (UDS) and Resource Sheet Metadata Standards (RSMS v2.0). It ensures every document in the CodeRef ecosystem has complete traceability, automated quality validation, and consistent structure through schema-based validation and score-based quality metrics.

**Problem Solved**: Inconsistent documentation across CodeRef MCP servers (missing metadata, no workorder tracking, no validation)

**Solution Provided**: 15 specialized validators, 11 JSON schemas, 7 MCP tools, and automated quality scoring (0-100 scale)

---

## Overview

Papertrail is a **4-layer architecture** (MCP Server → Factory → Validator → Schema) with **906 code elements** (662 methods, 135 functions, 109 classes) across 63 files.

**Core Capabilities**:

| Capability | Description | Details |
|------------|-------------|---------|
| **Document Validation** | Validate documents against UDS/RSMS schemas | 13 validators, 11 JSON schemas, 0-100 scoring |
| **Auto-Detection** | Automatically detect document type | ValidatorFactory with 30+ path patterns |
| **Quality Metrics** | Score documents on 0-100 scale | Weighted scoring (CRITICAL=-50, MAJOR=-20, MINOR=-10) |
| **Completeness Tracking** | Track section coverage (0-100%) | Foundation docs only (POWER framework) |
| **MCP Integration** | 7 tools for validation and batch checking | validate_document, check_all_docs, etc. |
| **RSMS v2.0 Compliance** | Resource sheet validation | snake_case frontmatter, naming conventions |

**Architecture**: Layered architecture with Template Method and Factory patterns

---

## What/Why/When

**What**: Papertrail is a Python library and MCP server providing Universal Documentation Standards (UDS) and Resource Sheet Metadata Standards (RSMS v2.0) for validation, scoring, and health monitoring of documentation.

**Why**: Ensures documentation consistency, traceability, and quality across the CodeRef ecosystem through automated validation, workorder tracking, and schema-based enforcement.

**When**: Use Papertrail during:
- Document generation (coderef-docs integration)
- Pre-commit validation (git hooks)
- CI/CD pipelines (quality gates)
- Workorder archival (compliance checks)
- Manual documentation reviews

---

## What: Key Features

### 1. Universal Documentation Standards (UDS) Validation

**Purpose**: Ensure all markdown documents have required metadata (agent, date, task)

**Coverage**: 11 JSON Schema Draft-07 files covering 13 document categories

| Schema | Document Types | Required Fields |
|--------|----------------|----------------|
| `base-frontmatter-schema.json` | All markdown (foundation) | agent, date, task |
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

**Validation Flow**:
```
File → ValidatorFactory.get_validator(file) → validator.validate_file(file) → ValidationResult (score 0-100)
```

---

### 2. Resource Sheet Metadata Standards (RSMS v2.0)

**Purpose**: Validate architectural reference documents (resource sheets) with versioning and relationship tracking

**Requirements**:
- **Naming Convention**: `{Subject}-RESOURCE-SHEET.md` (PascalCase-with-hyphens)
- **Required Fields**: `agent`, `date`, `task`, `subject`, `parent_project`, `category` (snake_case)
- **Category Enum**: 11 values (service, controller, model, utility, integration, component, middleware, validator, schema, config, other)
- **Optional Fields**: `version`, `related_files`, `related_docs`, `workorder`, `tags`, `status`

**Compliance Threshold**: Score >= 90/100

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
related_docs:
  - BaseUDSValidator-RESOURCE-SHEET.md
workorder: WO-VALIDATION-ENHANCEMENT-001
tags:
  - validation
  - foundation-docs
status: APPROVED
---
```

---

### 3. 15 Validator Components

**Purpose**: Implement validation logic for 13 document categories using Template Method pattern

**Component Hierarchy**:
```
UDSValidator (papertrail/validator.py)
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

**BaseUDSValidator Methods**:
- `validate_file(file_path)` - Main entry point (template method)
- `validate_content(content, file_path)` - Validate content string
- `validate_specific(frontmatter, content, file_path)` - Abstract hook method
- `_calculate_score(errors, warnings)` - Calculate 0-100 score
- `_calculate_completeness(frontmatter, content)` - Calculate 0-100% section coverage

---

### 4. 7 MCP Tools

**Purpose**: Expose validation capabilities via Model Context Protocol for AI agents (Claude Code, coderef-docs)

**Tools** (from `papertrail/server.py`, 571 lines):

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `validate_stub` | Validate stub.json with auto-fill | file_path, auto_fill, save | Validation report |
| `validate_resource_sheet` | RSMS v2.0 validation | file_path | Score (0-100) |
| `check_all_resource_sheets` | Batch RSMS validation | directory | Summary with avg score |
| `validate_document` | UDS validation (auto-detect) | file_path | Score (0-100) |
| `check_all_docs` | Batch UDS validation | directory, pattern | Summary with avg score |
| `validate_schema_completeness` | Schema sync validation | schema_name | Completeness report |
| `validate_all_schemas` | Batch schema validation | (none) | Summary with issues |

**Transport**: stdio (standard input/output)
**Protocol**: MCP 1.0

---

### 5. Score-Based Validation (0-100 scale)

**Purpose**: Provide actionable quality metrics instead of binary pass/fail

**Formula**:
```
score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
score = max(0, score)
```

**Severity Deductions**:
- **CRITICAL**: -50 points (missing required fields, invalid schema structure)
- **MAJOR**: -20 points (invalid enum values, format violations)
- **MINOR**: -10 points (recommended field missing)
- **WARNING**: -5 points (style issues)
- **Warnings**: -2 points each (informational)

**Validation Thresholds**:
- **90-100**: Excellent (validation passes) ✅
- **70-89**: Good (minor issues)
- **50-69**: Fair (multiple issues)
- **0-49**: Poor (major issues) ❌

---

### 6. ValidatorFactory Auto-Detection

**Purpose**: Automatically detect appropriate validator from file path and frontmatter

**Path Patterns** (30+):
- `.*-RESOURCE-SHEET\.md$` → ResourceSheetValidator
- `.*/README\.md$` → FoundationDocValidator
- `.*/DELIVERABLES\.md$` → WorkorderDocValidator
- `.*/CLAUDE\.md$` → SystemDocValidator
- `.*/plan\.json$` → PlanValidator
- (+ 25 more patterns)

**Detection Logic**:
1. Try path-based detection (30+ regex patterns)
2. Try frontmatter-based detection (workorder_id → WorkorderDocValidator)
3. Fallback to GeneralMarkdownValidator

---

### 7. Completeness Metric (Foundation Docs)

**Purpose**: Track section coverage for foundation docs (README, API, ARCHITECTURE, SCHEMA, COMPONENTS)

**Formula**:
```
completeness = (sections_found / sections_required) * 100
```

**Example**:
```
# README.md (doc_type: readme)
Required: ["Purpose", "Overview", "What/Why/When", "Examples", "References"]
Found: ["Purpose", "Overview", "Examples"] = 3/5 = 60%
```

---

## Why: Use Cases

### UC-1: Single Document Validation
```python
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory

# Auto-detect and validate
validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))

print(f"Valid: {result.valid}")           # True/False
print(f"Score: {result.score}/100")       # 98
print(f"Completeness: {result.completeness}%")  # 100
```

### UC-2: Batch Validation Before Commit
```python
# Validate all docs in coderef/foundation-docs/ before commit
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/coderef/foundation-docs",
    "pattern": "**/*.md"
})

# Average Score: 91.2/100 → 4/5 passed ✅
```

### UC-3: Resource Sheet Validation (RSMS v2.0)
```python
from papertrail.validators.resource_sheet import ResourceSheetValidator

validator = ResourceSheetValidator()
result = validator.validate_file(Path("AuthService-RESOURCE-SHEET.md"))

if result.score >= 90:
    print(f"✅ RSMS v2.0 compliant (score: {result.score}/100)")
```

### UC-4: Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --staged --name-only | grep '.md$'); do
    python -c "
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory

validator = ValidatorFactory.get_validator(Path('$file'))
result = validator.validate_file(Path('$file'))

if not result.valid:
    print(f'❌ Validation failed: $file (score: {result.score}/100)')
    exit(1)
"
done
```

---

## When: Getting Started

### Installation

```bash
# Install from source
cd papertrail
pip install -e .

# Install dependencies
pip install jsonschema pyyaml pathlib
```

### Quick Start (Programmatic API)

```python
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory

# 1. Auto-detect validator
validator = ValidatorFactory.get_validator(Path("README.md"))

# 2. Validate file
result = validator.validate_file(Path("README.md"))

# 3. Check results
if result.valid:
    print(f"✅ Valid (score: {result.score}/100)")
else:
    print(f"❌ Invalid (score: {result.score}/100)")
    for error in result.errors:
        print(f"  - [{error.severity.value}] {error.message}")
```

### Quick Start (MCP Tools)

```python
# Use MCP tools for validation
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/path/to/README.md"
})

# Batch validation
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/docs",
    "pattern": "**/*.md"
})
```

---

## Examples: Integration Patterns

### Example 1: With coderef-docs (Foundation Doc Generation)

```python
# coderef-docs generates README.md
await call_tool("coderef-docs", "generate_individual_doc", {
    "template_name": "readme",
    "project_path": "/path/to/project",
    "auto_validate": True  # ← Calls papertrail validate_document
})

# Papertrail validates
result = await call_tool("papertrail", "validate_document", {
    "file_path": "/path/to/project/coderef/foundation-docs/README.md"
})

# coderef-docs checks score
if result.score < 90:
    print(f"❌ Validation failed (score: {result.score}/100)")
```

### Example 2: With coderef-workflow (Workorder Management)

```python
# Before archiving feature, validate all docs
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "/path/to/coderef/workorder/feature-001",
    "pattern": "**/*.{md,json}"
})

# Only archive if all docs valid
if result.average_score >= 85:
    await call_tool("coderef-workflow", "archive_feature", {"feature_id": "feature-001"})
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/validate-docs.yml
name: Validate Documentation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Foundation Docs
        run: |
          python -c "
          from papertrail.server import check_all_docs
          import asyncio

          result = asyncio.run(check_all_docs({'directory': 'coderef/foundation-docs'}))
          print(result.text)
          "
```

---

## References

### Foundation Documentation

**Complete References** (Generated from real code intelligence):
- **[API.md](API.md)** - Complete API reference for 7 MCP tools (717 lines)
- **[SCHEMA.md](SCHEMA.md)** - All 11 JSON schemas with field validations (680 lines)
- **[COMPONENTS.md](COMPONENTS.md)** - 15 validator components with architecture (803 lines)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture (654 lines)

### Project Documentation

- **[CLAUDE.md](../../CLAUDE.md)** - AI context documentation (530+ lines)
- **[README.md](../../README.md)** - User-facing documentation

### External Resources

- [JSON Schema Draft-07 Specification](https://json-schema.org/draft-07/schema)
- [Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/)
- [Universal Documentation Standards (UDS)](../standards/documentation/uds-specification.md)
- [Resource Sheet Metadata Standards (RSMS) v2.0](../standards/documentation/resource-sheet-standards.md)
- [POWER Framework](../standards/documentation/power-framework.md)

---

## Integration with CodeRef Ecosystem

**Part of CodeRef Ecosystem** (5 MCP servers):
- **papertrail** - Documentation validation (this server)
- **coderef-context** - Code intelligence (dependency graph, impact analysis)
- **coderef-workflow** - Planning & orchestration (10-section plans)
- **coderef-docs** - Documentation generation (POWER framework templates)
- **coderef-personas** - Expert agents (9 domain specialists)

**Provides**:
- Universal Documentation Standards (UDS) enforcement
- Resource Sheet Metadata Standards (RSMS v2.0) compliance
- Validation infrastructure for all generated documentation
- Quality gates for foundation docs (score >= 90)

**Used By**:
- **coderef-docs** - Validates generated documentation
- **coderef-workflow** - Validates workorder documentation (DELIVERABLES, plan.json)
- **All MCP servers** - Validates CLAUDE.md, README.md, resource sheets

---

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_foundation_doc.py
pytest tests/test_resource_sheet.py
pytest tests/test_factory.py

# Run with coverage
pytest --cov=papertrail tests/

# Run only validators
pytest tests/validators/
```

**Test Coverage**:
- 30/30 tests passing (100%)
- Coverage: ~90%+ across all modules

---

## Project Statistics

**From `.coderef/context.json`**:
- **Total Elements**: 906 (662 methods, 135 functions, 109 classes)
- **Total Files**: 63
- **Languages**: Python (.py: 665 elements), TypeScript (.ts: 153 elements), JavaScript (.js: 88 elements)

**Component Breakdown**:
- **13 Validators**: FoundationDocValidator, ResourceSheetValidator, WorkorderDocValidator, SystemDocValidator, StandardsDocValidator, UserFacingDocValidator, MigrationDocValidator, InfrastructureDocValidator, SessionDocValidator, PlanValidator, StubValidator, AnalysisValidator, ExecutionLogValidator
- **1 Base Validator**: BaseUDSValidator (abstract base class, 150+ lines)
- **1 Factory**: ValidatorFactory (200+ lines, 30+ path patterns)
- **7 MCP Tools**: validate_stub, validate_resource_sheet, check_all_resource_sheets, validate_document, check_all_docs, validate_schema_completeness, validate_all_schemas
- **11 JSON Schemas**: Draft-07, allOf inheritance pattern

---

## Contributing

When adding new validators:

1. **Extend BaseUDSValidator** and implement `validate_specific()`
2. **Create JSON schema** in `schemas/documentation/{category}-frontmatter-schema.json`
3. **Add path pattern** to ValidatorFactory.PATH_PATTERNS
4. **Add tests** in `tests/validators/test_{category}.py`
5. **Update documentation** (this README, COMPONENTS.md)

**Example**:
```python
# 1. Create validator
class MyCustomValidator(BaseUDSValidator):
    schema_name = "my-custom-frontmatter-schema.json"
    doc_category = "my_custom"

    def validate_specific(self, frontmatter, content, file_path):
        errors = []
        warnings = []
        # Custom validation logic here
        return (errors, warnings)

# 2. Add to factory
ValidatorFactory.PATH_PATTERNS[r".*/MY-CUSTOM\.md$"] = "my_custom"
```

---

## License

**MIT License**

**Python Version**: 3.10+

**Maintained by**: CodeRef Ecosystem - Papertrail Team

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Status:** COMPLETE
