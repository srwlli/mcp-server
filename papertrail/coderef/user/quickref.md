---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
feature_id: user-docs-generation
doc_type: user-facing
audience: developers
difficulty: beginner
version: "1.0.0"
status: APPROVED
---

# Papertrail - Quick Reference

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0) Validation**

---

## At a Glance

Papertrail validates documentation against schemas and returns quality scores (0-100).

**Core Capabilities:**
- Validate markdown docs with UDS schemas (11 schemas, 13 categories)
- Validate resource sheets with RSMS v2.0 standards
- Auto-detect validator type from 30+ file patterns
- Batch validate directories with summary reports
- Track section completeness (0-100%) for foundation docs

---

## Actions (7 MCP Tools)

| Tool | Purpose | Time |
|------|---------|------|
| `validate_document` | Validate any doc (auto-detect type) | ~200ms |
| `validate_resource_sheet` | Validate resource sheet (RSMS v2.0) | ~200ms |
| `validate_stub` | Validate stub.json with auto-fill | ~150ms |
| `check_all_docs` | Batch validate directory | ~1-3s (10 docs) |
| `check_all_resource_sheets` | Batch validate resource sheets | ~1-3s (10 docs) |
| `validate_schema_completeness` | Check schema has required_sections | ~100ms |
| `validate_all_schemas` | Validate all 11 schemas | ~500ms |

---

## Features by Category

### Single Document Validation

| Feature | Input | Output |
|---------|-------|--------|
| Auto-detect validator | file_path | FoundationDocValidator, ResourceSheetValidator, etc. |
| Validate frontmatter | YAML front matter | Errors for missing fields (agent, date, task) |
| Validate sections | Markdown content | Errors for missing required sections |
| Calculate score | Errors + warnings | Score (0-100) with severity deductions |
| Calculate completeness | Found vs required sections | Percentage (0-100%) |

### Batch Validation

| Feature | Input | Output |
|---------|-------|--------|
| Recursive scan | directory + pattern | List of matching files |
| Parallel validation | List of files | ValidationResult per file |
| Summary report | All results | Total, passed, failed, avg score |

### Schema Validation

| Feature | Input | Output |
|---------|-------|--------|
| Schema completeness | schema_name | Coverage per doc_type |
| Batch schema check | (all schemas) | Pass/fail per schema |

---

## Common Workflows

### Workflow 1: Validate Single Document

1. Create markdown with frontmatter (agent, date, task)
2. Call `validate_document(file_path="path/to/doc.md")`
3. Review score (aim for >= 90/100)
4. Fix errors (CRITICAL → MAJOR → MINOR)
5. Re-validate until passing

### Workflow 2: Batch Validate Directory

1. Prepare directory with multiple markdown files
2. Call `check_all_docs(directory="path/to/docs", pattern="**/*.md")`
3. Review summary (total, passed, failed, avg score)
4. Identify failed docs (score < 90)
5. Validate each failed doc individually to see detailed errors
6. Fix and re-validate

### Workflow 3: Resource Sheet Validation

1. Create resource sheet: `ComponentName-RESOURCE-SHEET.md`
2. Add snake_case frontmatter (subject, parent_project, category)
3. Call `validate_resource_sheet(file_path="path/to/sheet.md")`
4. Fix RSMS violations (naming, frontmatter, required fields)
5. Re-validate until score >= 90

### Workflow 4: Pre-Commit Check

1. Stage markdown changes: `git add coderef/foundation-docs/*.md`
2. Call `check_all_docs(directory="coderef/foundation-docs")`
3. If all passed: `git commit -m "docs: Update foundation docs"`
4. If any failed: Fix errors, re-validate, then commit

### Workflow 5: Stub Auto-Fill

1. Create minimal stub.json with feature_name
2. Call `validate_stub(file_path="stub.json", auto_fill=True, save=True)`
3. Tool auto-fills: stub_id, created, status, tags
4. Review auto-filled stub
5. Edit as needed and save

---

## Reference Format

### Frontmatter (UDS Base)

```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
---
```

### Frontmatter (Foundation Docs)

```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-EXAMPLE-001
generated_by: coderef-docs v1.0.0
feature_id: example-feature
doc_type: readme
version: "1.0.0"
status: APPROVED
---
```

### Frontmatter (Resource Sheets - RSMS v2.0)

```yaml
---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
subject: AuthService
parent_project: papertrail
category: service
version: "1.0.0"
related_files:
  - papertrail/validators/auth.py
related_docs:
  - BaseService-RESOURCE-SHEET.md
workorder: WO-EXAMPLE-001
tags:
  - authentication
  - validation
status: APPROVED
---
```

### Calling Tools (MCP Client)

```python
# Validate single document
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/path/to/README.md"
})

# Batch validate directory
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/docs",
    "pattern": "**/*.md"
})

# Validate resource sheet
result = await call_tool("papertrail", "validate_resource_sheet", {
    "file_path": "C:/path/to/Component-RESOURCE-SHEET.md"
})

# Validate stub with auto-fill
result = await call_tool("papertrail", "validate_stub", {
    "file_path": "C:/path/to/stub.json",
    "auto_fill": True,
    "save": True
})
```

### Python API (Direct Usage)

```python
from papertrail.validators.factory import ValidatorFactory
from pathlib import Path

# Auto-detect and validate
validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))

# Check results
print(f"Valid: {result.valid}")           # True/False
print(f"Score: {result.score}/100")       # 98
print(f"Completeness: {result.completeness}%")  # 100

# Print errors
for error in result.errors:
    print(f"[{error.severity.name}] {error.message}")
```

---

## Output Locations

| Type | Location | Files |
|------|----------|-------|
| User Docs | `coderef/user/` | my-guide.md, USER-GUIDE.md, FEATURES.md, quickref.md |
| Foundation Docs | `coderef/foundation-docs/` | README.md, API.md, SCHEMA.md, COMPONENTS.md, ARCHITECTURE.md |
| Resource Sheets | `coderef/` or project root | *-RESOURCE-SHEET.md |
| Schemas | `schemas/documentation/` | 11 JSON schemas |
| Validators | `papertrail/validators/` | base.py, foundation.py, etc. (15 files) |
| Validation Results | Terminal/MCP response | ValidationResult (score, errors, warnings) |

---

## Key Concepts

### 1. Severity-Based Scoring

Score calculated with weighted deductions:
- CRITICAL: -50 points (missing required fields)
- MAJOR: -20 points (invalid enum values)
- MINOR: -10 points (recommended field missing)
- WARNING: -5 points (style issues)
- Warnings: -2 points each

**Threshold**: Score >= 90 = passing ✅

### 2. Template Method Pattern

BaseUDSValidator defines workflow, subclasses implement category-specific checks:
```
validate_file() [template method]
  ├─ _load_schema()
  ├─ _extract_frontmatter()
  ├─ validate_specific() [hook - subclasses override]
  ├─ _validate_required_sections()
  ├─ _calculate_score()
  └─ _calculate_completeness()
```

### 3. Auto-Detection (ValidatorFactory)

30+ path patterns map filenames to validators:
- `README.md` → FoundationDocValidator
- `*-RESOURCE-SHEET.md` → ResourceSheetValidator
- `plan.json` → PlanValidator
- `communication.json` → SessionDocValidator

**Fallback**: GeneralMarkdownValidator for unmatched files

### 4. Completeness Tracking

Foundation docs only (README, API, SCHEMA, COMPONENTS, ARCHITECTURE):
```
completeness = (sections_found / sections_required) * 100
```

Example:
```
README.md (doc_type: readme)
Required: ["Purpose", "Overview", "What/Why/When", "Examples", "References"]
Found: 4/5 = 80%
```

---

## Summary

**Total Tools**: 7 MCP tools
**Total Validators**: 15 (1 base + 13 validators + 1 factory)
**Total Schemas**: 11 JSON Schema Draft-07 files
**Total Categories**: 13 document categories

**Score Range**: 0-100 (>= 90 = passing)
**Completeness Range**: 0-100% (foundation docs only)

---

## Quick Links

- **Full Tutorial**: `coderef/user/USER-GUIDE.md`
- **Feature Overview**: `coderef/user/FEATURES.md`
- **Tool Lookup**: `coderef/user/my-guide.md`
- **API Reference**: `coderef/foundation-docs/API.md`
- **Architecture**: `coderef/foundation-docs/ARCHITECTURE.md`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Maintained by**: CodeRef Ecosystem
