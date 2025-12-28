# Data Schema Reference - coderef-docs MCP Server

**Version:** 3.2.0
**Last Updated:** 2025-12-27
**Schema Format:** JSON (file-based storage)

---

## Purpose

This document defines all data schemas used by the coderef-docs MCP server for changelogs, templates, standards, and configuration data.

---

## Overview

The coderef-docs server uses file-based JSON storage. No database required. All schemas are validated using jsonschema.

**Schema Categories:**
1. Changelog Schema
2. Template Metadata Schema
3. Standards Schema
4. Risk Assessment Schema
5. Tool Communication Schema

---

## 1. Changelog Schema

### CHANGELOG.json Structure

**Location:** `coderef/changelog/CHANGELOG.json`

```json
{
  "project": {
    "name": "string",
    "version": "string (x.y.z)",
    "description": "string"
  },
  "versions": [
    {
      "version": "string (x.y.z)",
      "date": "string (ISO 8601)",
      "summary": "string",
      "changes": [
        {
          "type": "enum (feature|bugfix|enhancement|breaking_change|deprecation|security)",
          "severity": "enum (critical|major|minor|patch)",
          "title": "string",
          "description": "string",
          "files": ["string"],
          "reason": "string",
          "impact": "string",
          "breaking": "boolean",
          "workorder_id": "string (WO-XXX-###, optional)"
        }
      ]
    }
  ]
}
```

**Validation:**
- Version pattern: `^\d+\.\d+\.\d+$`
- Workorder pattern: `^WO-[A-Z0-9-]+-\d{3}$`
- Files array must not be empty

---

## 2. Template Metadata Schema

### Template Info Structure

**Location:** Embedded in template files

```json
{
  "framework": "POWER",
  "purpose": "string",
  "output": "string",
  "work": "string",
  "examples": ["string"],
  "requirements": "string",
  "save_as": "string (.md filename)",
  "store_as": "string (context key)"
}
```

**Validation:**
- `framework` must be "POWER"
- `save_as` must end with ".md"
- `store_as` must be valid identifier

---

## 3. Standards Schema

### Standards Document Structure

**Location:** `coderef/standards/*.md`

**Types:**
- `ui-patterns.md` - UI component standards
- `behavior-patterns.md` - Error handling, loading states
- `ux-patterns.md` - Navigation, permissions

**Violation Schema:**
```json
{
  "file": "string",
  "line": "number",
  "pattern": "string",
  "severity": "enum (critical|major|minor)",
  "message": "string",
  "fix_suggestion": "string (optional)"
}
```

---

## 4. Risk Assessment Schema

**Location:** `templates/risk/assessment-schema.json`

```json
{
  "workorder_id": "string",
  "proposed_change": {
    "description": "string",
    "change_type": "enum (create|modify|delete|refactor|migrate)",
    "files_affected": ["string"]
  },
  "risk_dimensions": {
    "breaking_changes": {"score": 0-100, "impact": "enum"},
    "security": {"score": 0-100, "impact": "enum"},
    "performance": {"score": 0-100, "impact": "enum"},
    "maintainability": {"score": 0-100, "impact": "enum"},
    "reversibility": {"score": 0-100, "impact": "enum"}
  },
  "overall_risk_score": "number (0-100)",
  "recommendation": "enum (go|caution|no-go)"
}
```

**Recommendation Logic:**
- `go` if score < 30
- `caution` if 30-70
- `no-go` if > 70

---

## 5. Agent Communication Schema

**Location:** `coderef/workorder/{feature}/communication.json`

```json
{
  "feature_name": "string",
  "workorder_id": "string",
  "agents": [
    {
      "agent_id": "string (Agent-#)",
      "status": "enum (IDLE|ASSIGNED|WORKING|COMPLETED|VERIFIED)",
      "assigned_phase": "string",
      "forbidden_files": ["string"],
      "success_criteria": ["string"]
    }
  ],
  "coordination": {
    "current_phase": "string",
    "completion_status": "string"
  }
}
```

**Agent Status Lifecycle:**
```
IDLE → ASSIGNED → WORKING → COMPLETED → VERIFIED
```

---

## 6. Python Type Definitions

**Location:** `type_defs.py`

```python
from typing import TypedDict, Literal

class TemplateDict(TypedDict):
    framework: str
    purpose: str
    save_as: str
    store_as: str

ChangeType = Literal[
    "feature", "bugfix", "enhancement",
    "breaking_change", "deprecation", "security"
]

Severity = Literal["critical", "major", "minor", "patch"]

ScanDepth = Literal["quick", "standard", "deep"]
```

---

## Validation & Error Handling

All JSON structures validated using `jsonschema`:

```python
import jsonschema

def validate_changelog_entry(entry: dict) -> None:
    schema = load_changelog_schema()
    jsonschema.validate(instance=entry, schema=schema)
```

**Common Validation Errors:**
- Invalid type (string vs number)
- Missing required field
- Pattern mismatch
- Enum value not allowed

---

## Data Flow

```
User Input → MCP Tool → Validation → Handler → File Storage → Response
```

---

## References

- **Schema Definitions:** `type_defs.py`, `validation.py`
- **Template Schemas:** `templates/prompts/_schema.json`
- **Risk Schema:** `templates/risk/assessment-schema.json`
- **Related Docs:** API.md, ARCHITECTURE.md

---

*Generated: 2025-12-27*
*For AI Agents: All schemas use strict validation with descriptive errors*
