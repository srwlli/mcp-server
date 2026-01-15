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

# Papertrail User Guide

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0)**

**Version:** 1.0.0
**Date:** January 13, 2026
**Author:** CodeRef Ecosystem

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [How It Works](#how-it-works)
4. [Getting Started](#getting-started)
5. [Tools Reference](#tools-reference)
6. [Use Cases](#use-cases)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Quick Reference](#quick-reference)
10. [AI Integration](#ai-integration)

---

## Prerequisites

Before using Papertrail, verify you have:

### Python 3.10+
```bash
python --version
# Expected: Python 3.10.0 or higher
```

### MCP-Compatible Client
- Claude Code CLI
- Cursor IDE with MCP support
- Any MCP-compatible agent framework

### Verification
```bash
# Check if Papertrail MCP server is configured
cat ~/.mcp.json | grep papertrail
# Expected: Entry for papertrail server with path to server.py
```

---

## Installation

### Step 1: Install Papertrail

```bash
cd C:\Users\willh\.mcp-servers\papertrail
pip install -e .
```

**Expected Output:**
```
Successfully installed papertrail-1.0.0
```

### Step 2: Configure MCP Server

Add to `~/.mcp.json` (or your MCP configuration):

```json
{
  "mcpServers": {
    "papertrail": {
      "command": "python",
      "args": ["-m", "papertrail.server"],
      "cwd": "C:/Users/willh/.mcp-servers/papertrail"
    }
  }
}
```

### Step 3: Verify Installation

Restart your MCP client and check for Papertrail tools:

```bash
# In Claude Code or compatible client
# Type: /tools
# Expected: 7 Papertrail tools listed (validate_document, check_all_docs, etc.)
```

---

## How It Works

Papertrail implements a **layered validation architecture** using the MCP protocol:

```
┌─────────────────────────────────────────────┐
│         MCP Client (Claude Code)            │
│  - Calls tools via JSON-RPC 2.0             │
│  - Receives validation results              │
└─────────────────┬───────────────────────────┘
                  │ stdio transport
┌─────────────────▼───────────────────────────┐
│      Papertrail MCP Server (server.py)      │
│  - Exposes 7 tools via @app.list_tools()    │
│  - Routes to validation handlers            │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      ValidatorFactory (factory.py)          │
│  - Auto-detects doc type from 30+ patterns  │
│  - Returns appropriate validator instance   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│   Category Validators (foundation.py, etc.) │
│  - Extends BaseUDSValidator                 │
│  - Validates frontmatter + content          │
│  - Calculates score (0-100)                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│     JSON Schemas (schemas/documentation/)   │
│  - 11 schemas define validation rules       │
│  - Draft-07 format with allOf inheritance   │
└─────────────────────────────────────────────┘
```

**Behind the Scenes:**

1. **Tool Call**: Client sends JSON-RPC request with tool name + arguments
2. **Routing**: Server routes to appropriate handler (validate_document, check_all_docs, etc.)
3. **Auto-Detection**: ValidatorFactory examines file path/frontmatter to select validator
4. **Schema Loading**: Validator loads corresponding JSON schema and resolves `allOf` references
5. **Validation**: Runs frontmatter validation + required sections check + category-specific checks
6. **Scoring**: Calculates 0-100 score based on weighted severity deductions
7. **Response**: Returns ValidationResult with errors, warnings, score, completeness

**Time Estimates:**
- Single document validation: ~100-300ms
- Batch validation (10 docs): ~1-3 seconds
- Schema completeness check: ~50-100ms

---

## Getting Started

### Tutorial 1: Validate a Single Document

**Scenario**: You've just created a README.md and want to validate it against UDS standards.

**Step 1**: Ensure your README has frontmatter

```markdown
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

**Step 2**: Call validate_document tool

```python
# Via MCP client
result = await call_tool("papertrail", "validate_document", {
    "file_path": "C:/path/to/README.md"
})
```

**Step 3**: Review results

```
# Validation Results: README.md

**Valid:** Yes
**Score:** 95/100
**Completeness:** 80%
**Category:** foundation

## Warnings (1)
- Missing recommended POWER section: Examples

✅ Document validates successfully!
```

**What Just Happened:**
- ValidatorFactory detected "README.md" → FoundationDocValidator
- Validator loaded `foundation-doc-frontmatter-schema.json`
- Checked required fields: agent, date, task, workorder_id, generated_by, feature_id, doc_type ✅
- Checked required sections for doc_type="readme": Purpose, Overview, What/Why/When, Examples, References
- Found 4/5 sections present → 80% completeness
- Calculated score: 100 - 5 (1 warning) = 95/100

---

### Tutorial 2: Batch Validate a Directory

**Scenario**: You have a `coderef/foundation-docs/` directory with 5 markdown files and want to validate all at once.

**Step 1**: Call check_all_docs tool

```python
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "C:/path/to/coderef/foundation-docs",
    "pattern": "**/*.md"  # Optional, default is **/*.md
})
```

**Step 2**: Review summary

```
# Validation Summary: foundation-docs

**Total Files:** 5
**Passed:** 4
**Failed:** 1
**Average Score:** 92.0/100

## Results

✅ **README.md** - Score: 95/100
✅ **API.md** - Score: 100/100
✅ **SCHEMA.md** - Score: 100/100
❌ **COMPONENTS.md** - Score: 60/100 (3 errors, 2 warnings)
✅ **ARCHITECTURE.md** - Score: 98/100
```

**Step 3**: Fix failing docs

Identify which doc failed (COMPONENTS.md with score 60), call validate_document on it to see detailed errors, fix issues, and re-validate.

---

## Tools Reference

### validate_document

**Purpose**: Auto-detect and validate any document against UDS schemas

**Parameters:**
```json
{
  "file_path": "string (required) - Absolute path to document"
}
```

**Returns:**
```
Valid: bool
Score: 0-100
Category: foundation|workorder|system|etc.
Errors: [{ severity, message, field }]
Warnings: [string]
Completeness: 0-100% (for foundation docs)
```

**Use When:**
- Validating a single README, ARCHITECTURE, API, or other doc
- Getting detailed error reports for fixing issues
- Checking doc health before committing

---

### validate_resource_sheet

**Purpose**: Validate resource sheets against RSMS v2.0 standards

**Parameters:**
```json
{
  "file_path": "string (required) - Path to -RESOURCE-SHEET.md file"
}
```

**Returns:**
```
Valid: bool
Score: 0-100
Subject: string
Category: service|controller|model|etc.
Errors: [{ severity, message, field }]
```

**Use When:**
- Validating resource sheets after creation
- Checking RSMS v2.0 compliance (snake_case, naming convention)
- Ensuring resource sheet metadata is complete

---

### check_all_docs

**Purpose**: Batch validate all documents in a directory

**Parameters:**
```json
{
  "directory": "string (required) - Absolute path to directory",
  "pattern": "string (optional) - Glob pattern, default: **/*.md"
}
```

**Returns:**
```
Total Files: int
Passed: int
Failed: int
Average Score: float
Results: [{ filename, score, status }]
```

**Use When:**
- Pre-commit validation of all docs
- CI/CD quality gates
- Periodic documentation health checks

---

### validate_stub

**Purpose**: Validate stub.json files with optional auto-fill

**Parameters:**
```json
{
  "file_path": "string (required) - Path to stub.json",
  "auto_fill": "boolean (optional) - Auto-fill missing fields, default: false",
  "save": "boolean (optional) - Save auto-filled stub, default: false"
}
```

**Use When:**
- Validating feature stubs during planning
- Auto-filling stub metadata (stub_id, created, status, tags)
- Checking stub format before workorder creation

---

### check_all_resource_sheets

**Purpose**: Batch validate all resource sheets in a directory

**Parameters:**
```json
{
  "directory": "string (required) - Directory containing resource sheets"
}
```

**Use When:**
- Validating all resource sheets after bulk creation
- Checking RSMS compliance across project
- Generating compliance reports

---

### validate_schema_completeness

**Purpose**: Check if schema has required_sections for all doc_types

**Parameters:**
```json
{
  "schema_name": "string (required) - Schema filename (e.g., 'foundation-doc-frontmatter-schema.json')"
}
```

**Use When:**
- Ensuring schema-template synchronization
- Verifying all doc_types have required_sections defined
- Debugging schema coverage gaps

---

### validate_all_schemas

**Purpose**: Validate all JSON schemas in schemas/documentation/

**Parameters:** None

**Use When:**
- CI/CD schema validation
- Catching schema drift or incompleteness
- Periodic schema health checks

---

## Use Cases

### UC-1: Pre-Commit Documentation Validation

**Workflow:**

1. **Stage your markdown changes**
   ```bash
   git add coderef/foundation-docs/README.md
   ```

2. **Validate staged files**
   ```python
   result = await call_tool("papertrail", "check_all_docs", {
       "directory": "C:/path/to/coderef/foundation-docs"
   })
   ```

3. **Review results**
   - If all passed (score >= 90): Proceed with commit
   - If any failed: Fix errors, re-validate, then commit

4. **Commit**
   ```bash
   git commit -m "docs: Update README with validation passing"
   ```

**Expected Outcome**: All committed documentation meets UDS standards

---

### UC-2: Resource Sheet Creation & Validation

**Workflow:**

1. **Create resource sheet**
   ```markdown
   ---
   agent: Claude Sonnet 4.5
   date: "2026-01-13"
   task: CREATE
   subject: AuthService
   parent_project: papertrail
   category: service
   version: "1.0.0"
   ---

   # AuthService Resource Sheet

   ## Executive Summary
   ...
   ```

2. **Validate RSMS compliance**
   ```python
   result = await call_tool("papertrail", "validate_resource_sheet", {
       "file_path": "C:/path/to/AuthService-RESOURCE-SHEET.md"
   })
   ```

3. **Fix any issues**
   - Ensure snake_case frontmatter (not camelCase)
   - Check naming convention (-RESOURCE-SHEET.md suffix)
   - Verify required fields (subject, parent_project, category)

4. **Re-validate until score >= 90**

---

### UC-3: CI/CD Quality Gate

**Workflow:**

1. **Add validation step to GitHub Actions**
   ```yaml
   # .github/workflows/validate-docs.yml
   - name: Validate Documentation
     run: |
       python -m papertrail.server &
       sleep 5
       # Call check_all_docs via MCP client
       # Exit with error code if any docs fail
   ```

2. **On Pull Request**: Validation runs automatically

3. **If validation fails**: PR blocked until docs fixed

**Expected Outcome**: No PRs merged with invalid documentation

---

## Best Practices

### ✅ Do

- **Always include frontmatter** in markdown docs
  ```markdown
  ---
  agent: Claude Sonnet 4.5
  date: "2026-01-13"
  task: CREATE
  ---
  ```

- **Use batch validation** before committing multiple docs
  ```python
  check_all_docs(directory="coderef/foundation-docs")
  ```

- **Fix errors progressively** - Start with CRITICAL, then MAJOR, then MINOR
- **Run validation in CI/CD** to prevent invalid docs from merging
- **Use auto_fill for stubs** to save time on boilerplate fields

### 🚫 Don't

- **Don't skip frontmatter** - All UDS docs require agent, date, task
- **Don't ignore MAJOR errors** - Score will be below 90 (failing threshold)
- **Don't use camelCase in RSMS** - Use snake_case (subject, parent_project, not subjectName)
- **Don't commit without validation** - Always validate before git commit
- **Don't modify .json schemas manually** - Use schema tools to ensure consistency

### 💡 Tips

- **Score >= 90 = passing** - Aim for this threshold
- **Completeness tracks section coverage** - 100% means all required sections present
- **ValidatorFactory auto-detects** - No need to specify validator type manually
- **Severity levels matter**:
  - CRITICAL: -50 points
  - MAJOR: -20 points
  - MINOR: -10 points
  - WARNING: -5 points

---

## Troubleshooting

### Symptom: "File has not been read yet"

**Cause**: Trying to validate a file that doesn't exist or path is incorrect

**Solution:**
1. Verify file exists: `ls C:/path/to/file.md`
2. Use absolute paths, not relative paths
3. Check for typos in file path

---

### Symptom: Score = 0, "Missing required fields"

**Cause**: Frontmatter missing required UDS fields (agent, date, task)

**Solution:**
1. Add frontmatter to top of markdown:
   ```markdown
   ---
   agent: Your Name
   date: "2026-01-13"
   task: CREATE
   ---
   ```
2. Re-validate

---

### Symptom: "Invalid enum value for status"

**Cause**: Status field has incorrect value (e.g., "COMPLETE" instead of "APPROVED")

**Solution:**
1. Check schema for valid enum values:
   - Foundation docs: DRAFT, REVIEW, APPROVED, DEPRECATED
   - Workorder docs: not_started, in_progress, complete
2. Update frontmatter with valid value
3. Re-validate

---

### Symptom: "Missing required section: Endpoints"

**Cause**: Foundation doc with doc_type="api" missing required API sections

**Solution:**
1. Check schema's required_sections for doc_type
   - api: Endpoints, Authentication, Request/Response Examples, Error Codes
2. Add missing section headers to markdown:
   ```markdown
   ## Endpoints
   ...
   ```
3. Re-validate

---

### Symptom: ValidationResult shows completeness = 0%

**Cause**: Doc missing all required sections for its doc_type

**Solution:**
1. Check doc_type in frontmatter (readme, api, schema, etc.)
2. Refer to schema for required sections list
3. Add all required sections
4. Re-validate until completeness = 100%

---

## Quick Reference

### Validation Severity Levels

| Severity | Points Deducted | Examples |
|----------|----------------|----------|
| CRITICAL | -50 | Missing required field, invalid schema structure |
| MAJOR | -20 | Invalid enum value, format violation |
| MINOR | -10 | Recommended field missing |
| WARNING | -5 | Minor style issues, missing optional sections |

### Score Interpretation

| Score Range | Status | Action |
|-------------|--------|--------|
| 90-100 | ✅ Excellent | Document validates successfully |
| 70-89 | ⚠️ Good | Minor issues, consider fixing |
| 50-69 | ⚠️ Fair | Multiple issues, should fix |
| 0-49 | ❌ Poor | Major issues, must fix |

### Common Commands

```bash
# Validate single doc
validate_document(file_path="C:/path/to/README.md")

# Batch validate directory
check_all_docs(directory="C:/path/to/docs", pattern="**/*.md")

# Validate resource sheet
validate_resource_sheet(file_path="C:/path/to/Component-RESOURCE-SHEET.md")

# Validate stub with auto-fill
validate_stub(file_path="stub.json", auto_fill=True, save=True)

# Check schema completeness
validate_schema_completeness(schema_name="foundation-doc-frontmatter-schema.json")

# Validate all schemas
validate_all_schemas()
```

---

## AI Integration

Papertrail is designed for seamless AI agent integration via MCP protocol.

### Claude Code Integration

**Usage:**
```python
# In Claude Code conversation
"Validate all foundation docs in coderef/foundation-docs/"

# Claude Code will:
# 1. Call papertrail:check_all_docs tool
# 2. Parse results
# 3. Report pass/fail counts and scores
# 4. Suggest fixes for failing docs
```

### Custom Agent Integration

**Example:**
```python
from mcp import ClientSession

async def validate_with_papertrail(file_path: str):
    async with ClientSession() as session:
        # Connect to Papertrail MCP server
        await session.connect("papertrail")

        # Call validate_document tool
        result = await session.call_tool("validate_document", {
            "file_path": file_path
        })

        # Parse and return results
        return result
```

### Tool Schema Access

All 7 Papertrail tools expose JSON schemas via `@app.list_tools()`:

```python
tools = await papertrail_server.list_tools()
# Returns: [Tool(name="validate_document", inputSchema={...}), ...]
```

Agents can introspect tool schemas to understand:
- Required vs optional parameters
- Parameter types and descriptions
- Expected return formats

---

**For API reference, see:** `coderef/foundation-docs/API.md`
**For architecture details, see:** `coderef/foundation-docs/ARCHITECTURE.md`
**For quick tool lookup, see:** `coderef/user/my-guide.md`

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem
