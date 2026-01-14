---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
generated_by: coderef-docs v1.0.0
feature_id: foundation-docs-generation
doc_type: api
version: "1.0.0"
status: APPROVED
---

# Papertrail API Reference

**Universal Documentation Standards (UDS) Validation MCP Tools**

---

## Purpose

This document provides complete API reference for Papertrail's 7 MCP tools, enabling agents to validate documents, resource sheets, and schemas against Universal Documentation Standards (UDS) and Resource Sheet Metadata Standards (RSMS v2.0).

## Overview

Papertrail exposes 7 MCP tools through `papertrail/server.py` for document validation:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `validate_stub` | Validate stub.json files | file_path, auto_fill, save | Validation report with errors/warnings |
| `validate_resource_sheet` | RSMS v2.0 validation | file_path | Score (0-100) with compliance report |
| `check_all_resource_sheets` | Batch RSMS validation | directory | Summary with pass/fail counts |
| `validate_document` | UDS validation (auto-detect) | file_path | Score (0-100) with category detection |
| `check_all_docs` | Batch UDS validation | directory, pattern | Summary with average score |
| `validate_schema_completeness` | Schema sync validation | schema_name | Completeness report per doc_type |
| `validate_all_schemas` | Batch schema validation | (none) | Summary with issue counts |

**Total Elements:** 906 (662 methods, 135 functions, 109 classes across 63 files)

---

## Endpoints

Papertrail exposes 7 MCP tools via stdio transport (not HTTP REST endpoints). Tools are called via MCP protocol with JSON-RPC 2.0 format. See [What: MCP Tools Reference](#what-mcp-tools-reference) for complete tool signatures.

## Authentication

No authentication required. Papertrail runs as a local MCP server accessed via stdio transport. Security is handled by file system permissions on validated documents.

## Request/Response Examples

All tools follow MCP protocol format. See individual tool sections below for complete request/response examples with actual validation results.

## Error Codes

Validation results use severity-based error codes:
- **CRITICAL**: Missing required fields, invalid schema structure (-50 points)
- **MAJOR**: Invalid enum values, format violations (-20 points)
- **MINOR**: Recommended field missing (-10 points)
- **WARNING**: Minor style issues (-5 points)

---

## What: MCP Tools Reference

### 1. validate_stub

**Purpose**: Validate stub.json files against stub-schema.json with optional auto-fill

**Signature**:
```python
async def validate_stub(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Absolute path to stub.json file"
    },
    "auto_fill": {
      "type": "boolean",
      "description": "Auto-fill missing required fields with defaults (default: false)",
      "default": false
    },
    "save": {
      "type": "boolean",
      "description": "Save updated stub to file if auto_fill is true (default: false)",
      "default": false
    }
  },
  "required": ["file_path"]
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "validate_stub", {
    "file_path": "C:/path/to/coderef/working/my-feature/stub.json",
    "auto_fill": True,
    "save": False
})
```

**Example Response**:
```markdown
# Stub Validation: my-feature/stub.json

**Valid:** Yes [PASS]
**Auto-fill:** Enabled
**Saved:** No

## Auto-filled Fields

```json
{
  "stub_id": "my-feature",
  "feature_name": "My Feature",
  "created": "2026-01-13",
  "status": "not_started",
  "description": "Feature description",
  "tags": ["feature"]
}
```

[INFO] Updated stub shown above. Use save=true to write to file.

[PASS] Stub is valid and conforms to stub-schema.json!
```

**Error Codes**:
- `File not found` - stub.json doesn't exist at path
- `Error: Stub file must be named 'stub.json'` - Naming convention violation
- `Error validating stub: {exception}` - Schema validation failure

**Naming Convention**: Must be named `stub.json` (enforced at papertrail/server.py:171)

---

### 2. validate_resource_sheet

**Purpose**: Validate resource sheet documents against RSMS v2.0 schema

**Signature**:
```python
async def validate_resource_sheet(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Absolute path to resource sheet file (must end with -RESOURCE-SHEET.md)"
    }
  },
  "required": ["file_path"]
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "validate_resource_sheet", {
    "file_path": "C:/path/to/docs/FoundationDocValidator-RESOURCE-SHEET.md"
})
```

**Example Response**:
```markdown
# RSMS v2.0 Validation: FoundationDocValidator-RESOURCE-SHEET.md

**Valid:** Yes ✅
**Score:** 96/100
**Standard:** Resource Sheet Metadata Standards (RSMS) v2.0

## Warnings (2)

- Missing recommended section: Related Components
- Missing recommended section: Known Issues

**Address warnings to improve documentation quality.**

✅ **Resource sheet is RSMS v2.0 compliant!**
```

**RSMS v2.0 Requirements**:
- **Naming**: `{Subject}-RESOURCE-SHEET.md` (PascalCase-with-hyphens)
- **Required Fields**: `subject`, `parent_project`, `category` (snake_case in frontmatter)
- **Recommended Sections**: Executive Summary, Audience & Intent, Quick Reference
- **Score Threshold**: >= 90 for compliance

**Error Codes**:
- `Error: Resource sheet must end with -RESOURCE-SHEET.md` - Naming violation (papertrail/server.py:242)
- `[CRITICAL] Missing required field: {field}` - Required frontmatter field missing
- `[MAJOR] Invalid category enum` - category must be validator/tool/workflow/docs/testing

**Naming Convention**: Must end with `-RESOURCE-SHEET.md` (enforced at papertrail/server.py:242)

---

### 3. check_all_resource_sheets

**Purpose**: Batch validate all resource sheets in a directory

**Signature**:
```python
async def check_all_resource_sheets(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "directory": {
      "type": "string",
      "description": "Absolute path to directory containing resource sheets"
    }
  },
  "required": ["directory"]
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "check_all_resource_sheets", {
    "directory": "C:/path/to/coderef/resources-sheets"
})
```

**Example Response**:
```markdown
# RSMS v2.0 Batch Validation: resources-sheets

**Total Resource Sheets:** 5
**Passed:** 4 ✅
**Failed:** 1 ❌
**Average Score:** 92.6/100
**Standard:** Resource Sheet Metadata Standards (RSMS) v2.0

## Results

✅ **FoundationDocValidator-RESOURCE-SHEET.md** - Score: 96/100
✅ **ValidatorFactory-RESOURCE-SHEET.md** - Score: 95/100
✅ **BaseUDSValidator-RESOURCE-SHEET.md** - Score: 94/100
✅ **ResourceSheetValidator-RESOURCE-SHEET.md** - Score: 91/100
❌ **Invalid-Sheet.md** - Score: 37/100 (5 errors, 3 warnings)

⚠️ **1 resource sheet(s) failed validation. Use validate_resource_sheet to see detailed errors.**
```

**Scan Pattern**: Automatically searches for `**/*-RESOURCE-SHEET.md` (hardcoded at papertrail/server.py:298)

---

### 4. validate_document

**Purpose**: Validate any document with auto-detection of validator type using ValidatorFactory

**Signature**:
```python
async def validate_document(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Absolute path to document file (markdown or JSON)"
    }
  },
  "required": ["file_path"]
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/path/to/coderef/foundation-docs/README.md"
})
```

**Example Response**:
```markdown
# Validation Results: README.md

**Valid:** Yes
**Score:** 98/100
**Completeness:** 100%
**Category:** foundation

## Warnings (1)

- [WARNING] Missing recommended POWER section: Examples

✅ Document validates successfully!
```

**Auto-Detection Logic** (ValidatorFactory with 30+ path patterns):
- `README.md` → FoundationDocValidator
- `DELIVERABLES.md` → WorkorderDocValidator
- `CLAUDE.md` → SystemDocValidator
- `*-standards.md` → StandardsDocValidator
- `*-GUIDE.md` → UserGuideValidator
- `MIGRATION*.md` → MigrationDocValidator
- `communication.json` → SessionDocValidator
- `plan.json` → PlanValidator
- `analysis.json` → AnalysisValidator
- `execution-log.json` → ExecutionLogValidator

**Completeness Metric**: 0-100% calculation of section coverage based on required_sections per doc_type

**Error Codes**:
- `Error: File not found` - Document doesn't exist
- `[CRITICAL] Missing required field: {field}` - UDS base fields (agent, date, task) missing
- `[MAJOR] Invalid doc_type enum` - doc_type not in allowed values
- `Error validating document: {exception}` - Unexpected validation failure

---

### 5. check_all_docs

**Purpose**: Batch validate all documents in a directory with optional glob pattern

**Signature**:
```python
async def check_all_docs(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "directory": {
      "type": "string",
      "description": "Absolute path to directory to scan"
    },
    "pattern": {
      "type": "string",
      "description": "Optional glob pattern (default: **/*.md)"
    }
  },
  "required": ["directory"]
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/coderef/foundation-docs",
    "pattern": "**/*.md"
})
```

**Example Response**:
```markdown
# Validation Summary: foundation-docs

**Total Files:** 5
**Passed:** 4
**Failed:** 1
**Average Score:** 91.2/100

## Results

✅ **README.md** - Score: 98/100
✅ **ARCHITECTURE.md** - Score: 95/100
✅ **API.md** - Score: 94/100
✅ **SCHEMA.md** - Score: 88/100 (2 errors, 1 warnings)
❌ **COMPONENTS.md** - Score: 41/100 (Error: Missing required sections)
```

**Default Pattern**: `**/*.md` (recursive markdown scan, papertrail/server.py:439)

---

### 6. validate_schema_completeness

**Purpose**: Validate a JSON schema has required_sections defined for all doc_types

**Signature**:
```python
async def validate_schema_completeness(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "schema_name": {
      "type": "string",
      "description": "Name of schema file (e.g., 'foundation-doc-frontmatter-schema.json')"
    }
  },
  "required": ["schema_name"]
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "validate_schema_completeness", {
    "schema_name": "foundation-doc-frontmatter-schema.json"
})
```

**Example Response**:
```markdown
# Schema Completeness Report: foundation-doc-frontmatter-schema.json

**Status:** PASS
**Doc Types:** 5
**Total Sections:** 22

## Doc Type Coverage

| doc_type | Required Sections | Count |
|----------|-------------------|-------|
| readme | Purpose, Overview, What/Why/When, Examples, References | 5 |
| architecture | System Overview, Key Components, Design Decisions, Integration Points | 4 |
| api | Endpoints, Authentication, Request/Response Examples, Error Codes | 4 |
| schema | Schema Overview, Field Definitions, Validation Rules, Examples | 4 |
| components | Component Catalog, Props/Parameters, Usage Examples, Dependencies | 5 |

✅ Schema is complete and synchronized with templates!
```

**Use Case**: Ensure schema-template synchronization to prevent drift

**Schema Location**: `schemas/documentation/{schema_name}` (relative to project root)

**Tool Location**: Uses `SchemaSyncTool` from `papertrail/tools/sync_schemas.py` (380 lines, 9 methods)

---

### 7. validate_all_schemas

**Purpose**: Batch validate all JSON schemas in schemas/documentation/ directory

**Signature**:
```python
async def validate_all_schemas(arguments: dict) -> list[TextContent]
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Request**:
```python
result = await call_tool("papertrail", "validate_all_schemas", {})
```

**Example Response**:
```markdown
# All Schemas Validation Report

**Total Schemas:** 10
**Passed:** 9
**Failed:** 1

## Results

✅ **foundation-doc-frontmatter-schema.json** - 5 doc_types, 22 sections
✅ **workorder-doc-frontmatter-schema.json** - 1 doc_type, 8 sections
✅ **system-doc-frontmatter-schema.json** - 1 doc_type, 9 sections
✅ **standards-doc-frontmatter-schema.json** - 1 doc_type, 7 sections
✅ **user-facing-doc-frontmatter-schema.json** - 3 doc_types, 12 sections
✅ **migration-doc-frontmatter-schema.json** - 1 doc_type, 6 sections
✅ **infrastructure-doc-frontmatter-schema.json** - 1 doc_type, 6 sections
✅ **session-doc-frontmatter-schema.json** - 1 doc_type, 5 sections
✅ **resource-sheet-metadata-schema.json** - RSMS v2.0 schema
❌ **incomplete-schema.json** - Missing required_sections for doc_type 'api'

⚠️ 1 schema(s) have issues. Run validate_schema_completeness on failed schemas for details.
```

**Scan Location**: `schemas/documentation/` (hardcoded directory)

**Integration**: Can be run in CI/CD to prevent schema drift before deployment

---

## Why: Use Cases

### UC-1: Single Document Validation
```python
# Validate a resource sheet during /create-resource-sheet workflow
result = await call_tool("papertrail", "validate_resource_sheet", {
    "file_path": "C:/path/to/MyComponent-RESOURCE-SHEET.md"
})

# Score: 96/100 → RSMS v2.0 compliant ✅
```

### UC-2: Batch Validation Before Commit
```python
# Validate all docs in coderef/foundation-docs/ before git commit
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/coderef/foundation-docs",
    "pattern": "**/*.md"
})

# Average Score: 91.2/100 → 4/5 passed ✅
```

### UC-3: Schema Sync Validation
```python
# Ensure foundation schema has all required sections
result = await call_tool("papertrail", "validate_schema_completeness", {
    "schema_name": "foundation-doc-frontmatter-schema.json"
})

# Status: PASS → 5 doc_types, 22 sections defined ✅
```

### UC-4: Stub Validation with Auto-Fill
```python
# Validate stub and auto-fill missing fields
result = await call_tool("papertrail", "validate_stub", {
    "file_path": "C:/path/to/coderef/working/new-feature/stub.json",
    "auto_fill": True,
    "save": True
})

# Auto-filled: stub_id, created, status → Saved to file ✅
```

### UC-5: CI/CD Schema Validation
```python
# Run in CI pipeline to catch schema drift
result = await call_tool("papertrail", "validate_all_schemas", {})

# 9/10 schemas passed → Fail pipeline due to incomplete-schema.json ❌
```

---

## When: Integration Points

### With coderef-docs
**Tool**: `generate_individual_doc`, `generate_foundation_docs`
**Integration**: Calls `validate_document` after generation to ensure UDS compliance

**Example**:
```python
# coderef-docs generates README.md
await call_tool("coderef-docs", "generate_individual_doc", {
    "template_name": "readme",
    "project_path": "/path/to/project",
    "auto_validate": True  # ← Calls papertrail validate_document
})

# Papertrail validates and returns score: 98/100 ✅
```

### With coderef-workflow
**Tool**: `/create-workorder`, `/archive-feature`
**Integration**: Validates plan.json, DELIVERABLES.md, stub.json before archiving

**Example**:
```python
# Before archiving, validate all workorder docs
await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/coderef/workorder/feature-001",
    "pattern": "**/*.{md,json}"
})

# All docs valid → Safe to archive ✅
```

### Pre-Commit Hook
**Tool**: `check_all_docs`, `check_all_resource_sheets`
**Integration**: Run validation on staged files before commit

**Example**:
```bash
# .git/hooks/pre-commit
python -c "
from papertrail.validators.factory import ValidatorFactory
import sys

# Validate all staged markdown files
for file in $(git diff --staged --name-only | grep '.md$'):
    validator = ValidatorFactory.get_validator(file)
    result = validator.validate_file(file)
    if not result.valid:
        print(f'Validation failed: {file}')
        sys.exit(1)
"
```

### CI/CD Pipeline
**Tool**: `validate_all_schemas`, `check_all_docs`
**Integration**: Automated validation on PR creation

**Example**:
```yaml
# .github/workflows/validate-docs.yml
- name: Validate Schemas
  run: python -c "from papertrail.server import validate_all_schemas; import asyncio; asyncio.run(validate_all_schemas({}))"

- name: Validate Foundation Docs
  run: python -c "from papertrail.server import check_all_docs; import asyncio; asyncio.run(check_all_docs({'directory': 'coderef/foundation-docs'}))"
```

---

## Examples: Complete Workflows

### Example 1: Resource Sheet Validation Workflow
```python
# Step 1: Create resource sheet
with open("MyComponent-RESOURCE-SHEET.md", "w") as f:
    f.write("""---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
subject: MyComponent
parent_project: my-project
category: component
version: "1.0.0"
---

# MyComponent Resource Sheet

## Executive Summary
...
""")

# Step 2: Validate against RSMS v2.0
result = await call_tool("papertrail", "validate_resource_sheet", {
    "file_path": "C:/path/to/MyComponent-RESOURCE-SHEET.md"
})

# Step 3: Check score
if result.score >= 90:
    print("✅ RSMS v2.0 compliant!")
else:
    print(f"❌ Score: {result.score}/100 - Fix errors")
```

### Example 2: Batch Validation with Error Reporting
```python
# Validate all docs in directory
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/coderef/foundation-docs",
    "pattern": "**/*.md"
})

# Parse results
lines = result.text.split("\n")
failed_docs = [line for line in lines if line.startswith("❌")]

# Report failures
if failed_docs:
    print(f"Failed validation: {len(failed_docs)} docs")
    for doc in failed_docs:
        # Use validate_document to get detailed errors
        doc_name = doc.split("**")[1]
        detail = await call_tool("papertrail", "validate_document", {
            "file_path": f"C:/path/to/coderef/foundation-docs/{doc_name}"
        })
        print(detail.text)
```

### Example 3: Schema Completeness Check
```python
# Validate schema has all required sections
result = await call_tool("papertrail", "validate_schema_completeness", {
    "schema_name": "foundation-doc-frontmatter-schema.json"
})

# Check for issues
if "FAIL" in result.text:
    print("❌ Schema incomplete - fix before deploying")
    print(result.text)
else:
    print("✅ Schema complete - safe to deploy")
```

### Example 4: Stub Auto-Fill Workflow
```python
# Create minimal stub
stub_path = "C:/path/to/coderef/working/new-feature/stub.json"
with open(stub_path, "w") as f:
    f.write('{"description": "New feature"}')

# Validate with auto-fill enabled
result = await call_tool("papertrail", "validate_stub", {
    "file_path": stub_path,
    "auto_fill": True,
    "save": True
})

# Result: stub.json now has stub_id, created, status, tags auto-filled ✅
```

---

## References

### Internal
- **ValidatorFactory**: `papertrail/validators/factory.py` (30+ path patterns)
- **BaseUDSValidator**: `papertrail/validators/base.py` (abstract base class)
- **SchemaSyncTool**: `papertrail/tools/sync_schemas.py` (380 lines, 9 methods)
- **MCP Server**: `papertrail/server.py` (571 lines, 7 tools, 17 tool handlers)

### External
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Universal Documentation Standards (UDS)](../standards/documentation/uds-specification.md)
- [Resource Sheet Metadata Standards (RSMS) v2.0](../standards/documentation/resource-sheet-standards.md)
- [POWER Framework](../standards/documentation/power-framework.md)

### Related Documents
- [SCHEMA.md](SCHEMA.md) - JSON schema definitions for all validators
- [COMPONENTS.md](COMPONENTS.md) - Validator architecture and class hierarchy
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design patterns
- [README.md](README.md) - Project overview and quick start

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem - Papertrail MCP Server
