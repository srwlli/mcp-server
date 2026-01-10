# Schema Reference

**Version:** 3.4.0
**Last Updated:** 2026-01-10
**Server:** coderef-docs

---

## Purpose

This document defines all data schemas, structures, and models used in the coderef-docs MCP server. It provides the technical specification for JSON schemas, internal data models, validation rules, and data flow patterns. This reference ensures consistency in data handling across all documentation generation operations.

---

## Overview

The coderef-docs server uses several JSON schemas and data models:

1. **CHANGELOG.json Schema** - Structured version history
2. **UDS (Universal Document Standard) Schema** - Workorder metadata
3. **MCP Protocol Schemas** - Tool input/output contracts
4. **Resource Sheet Schemas** - Module-based documentation (NEW in v3.4.0)
5. **Internal Data Models** - Python classes and validation

---

## 1. CHANGELOG.json Schema

The changelog schema defines the structure for versioned project change tracking.

### Schema Definition

**File:** `coderef/changelog/schema.json`
**Schema Version:** draft-07
**Purpose:** Structured changelog with workorder tracking

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "coderef-docs Changelog Schema",
  "type": "object",
  "required": ["project", "changelog_version", "current_version", "entries"],
  "properties": {
    "project": {
      "type": "string",
      "const": "coderef-docs"
    },
    "changelog_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Schema version (e.g., '1.0')"
    },
    "current_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Latest project version (semver)"
    },
    "entries": {
      "type": "array",
      "items": { "$ref": "#/definitions/ChangelogEntry" }
    }
  }
}
```

### Example Instance

```json
{
  "project": "coderef-docs",
  "changelog_version": "1.0",
  "current_version": "3.4.0",
  "entries": [
    {
      "version": "3.4.0",
      "date": "2026-01-02",
      "summary": "Added resource sheet generator",
      "changes": [
        {
          "id": "change-001",
          "type": "feature",
          "severity": "major",
          "title": "Resource sheet MCP tool",
          "description": "Composable module-based documentation",
          "files": ["generators/resource_sheet_generator.py"],
          "reason": "Enable flexible documentation",
          "impact": "Replaces 20 rigid templates",
          "breaking": false
        }
      ]
    }
  ]
}
```

---

## 2. Universal Document Standard (UDS) Schema

UDS provides metadata for workorder-generated documents.

### UDS for Markdown

```yaml
---
title: DELIVERABLES - feature-name
version: 1.0
generated_by: coderef-docs v3.4.0
workorder_id: WO-FEATURE-001
status: IN_PROGRESS
timestamp: 2026-01-10T00:00:00Z
---
```

### UDS for JSON

```json
{
  "_uds": {
    "generated_by": "coderef-docs v3.4.0",
    "document_type": "Feature Plan",
    "workorder_id": "WO-FEATURE-001",
    "status": "DRAFT",
    "last_updated": "2026-01-10"
  }
}
```

---

## 3. Internal Data Models

### Enums

```python
class ChangeType(Enum):
    BUGFIX = "bugfix"
    ENHANCEMENT = "enhancement"
    FEATURE = "feature"
    BREAKING_CHANGE = "breaking_change"
    DEPRECATION = "deprecation"
    SECURITY = "security"

class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
```

---

## 4. Validation Rules

### Version Format
**Pattern:** `^[0-9]+\.[0-9]+\.[0-9]+$`
**Example:** `3.4.0`

### Workorder ID Format
**Pattern:** `^WO-[A-Z0-9-]+-\d{3}$`
**Example:** `WO-RESOURCE-SHEET-001`

---

## References

- **CHANGELOG Schema:** [coderef/changelog/schema.json](../../coderef/changelog/schema.json)
- **Schema Validator:** [schema_validator.py](../../schema_validator.py)
- **JSON Schema Spec:** https://json-schema.org/draft-07/schema

---

**Maintained by:** coderef-docs MCP server
**Generated:** 2026-01-10
**AI Assistance:** Claude Code (Sonnet 4.5)
