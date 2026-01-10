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
5. **MCP Tools** - 6 tools for validation and health checking

---

## MCP Tools

**Total:** 6 tools

1. **validate_document** - Validate against UDS schema
2. **check_document_health** - Calculate 0-100 health score
3. **log_workorder** - Log workorder to global log
4. **get_workorder_log** - Query workorder history
5. **inject_uds_headers** - Add UDS headers to documents
6. **generate_from_template** - Render Jinja2 templates with CodeRef extensions

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
