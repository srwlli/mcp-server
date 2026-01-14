# Schema Reference - coderef-docs

**Project:** coderef-docs (MCP Server)
**Version:** 4.0.0
**Last Updated:** 2026-01-13

---

## Purpose

This document defines all data schemas, structures, and models used in the coderef-docs MCP server. It provides the technical specification for JSON schemas, internal data models, validation rules, and data flow patterns, including new v4.0.0 additions for MCP orchestration, user docs automation, and standards enhancement.

---

## Overview

The coderef-docs server uses several JSON schemas and data models:

1. **CHANGELOG.json Schema** - Structured version history with workorder tracking
2. **UDS (Universal Document Standard) Schema** - Workorder metadata (v3.6.0)
3. **MCP Protocol Schemas** - Tool input/output contracts (16 tools in v4.0.0)
4. **Resource Sheet Schemas** - Module-based documentation (v3.4.0)
5. **MCP Orchestration Schemas** - Drift detection, pattern analysis (NEW in v4.0.0)
6. **User Docs Schemas** - my-guide, USER-GUIDE, FEATURES (NEW in v4.0.0)
7. **Internal Data Models** - Python classes and validation

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
      "description": "Changelog schema version (e.g., '2.0')"
    },
    "current_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Current project version (semantic versioning)"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of last update"
    },
    "entries": {
      "type": "array",
      "description": "Array of changelog entries",
      "items": {
        "$ref": "#/definitions/changelogEntry"
      }
    }
  },
  "definitions": {
    "changelogEntry": {
      "type": "object",
      "required": ["version", "date", "changes"],
      "properties": {
        "version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        },
        "date": {
          "type": "string",
          "format": "date"
        },
        "summary": {
          "type": "string",
          "description": "High-level summary of version changes"
        },
        "workorder_id": {
          "type": "string",
          "pattern": "^WO-[A-Z0-9-]+-[0-9]{3}$",
          "description": "Associated workorder ID (e.g., WO-GENERATION-ENHANCEMENT-001)"
        },
        "changes": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/change"
          }
        }
      }
    },
    "change": {
      "type": "object",
      "required": ["type", "severity", "title", "description", "files", "reason", "impact"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
        },
        "severity": {
          "type": "string",
          "enum": ["critical", "major", "minor", "patch"]
        },
        "title": {
          "type": "string",
          "minLength": 5,
          "maxLength": 100
        },
        "description": {
          "type": "string",
          "minLength": 10
        },
        "files": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "minItems": 1
        },
        "reason": {
          "type": "string",
          "description": "Why this change was made"
        },
        "impact": {
          "type": "string",
          "description": "Impact on users/system"
        },
        "breaking": {
          "type": "boolean",
          "default": false
        },
        "migration": {
          "type": "string",
          "description": "Migration guide (if breaking)"
        },
        "contributors": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

### Example Usage

```json
{
  "project": "coderef-docs",
  "changelog_version": "2.0",
  "current_version": "4.0.0",
  "last_updated": "2026-01-13T00:00:00Z",
  "entries": [
    {
      "version": "4.0.0",
      "date": "2026-01-13",
      "summary": "MCP integration & user docs automation",
      "workorder_id": "WO-GENERATION-ENHANCEMENT-001",
      "changes": [
        {
          "type": "feature",
          "severity": "major",
          "title": "MCP tool orchestration layer",
          "description": "Centralized MCP calling with drift detection and semantic patterns",
          "files": ["mcp_orchestrator.py", "mcp_integration.py"],
          "reason": "Enable code intelligence for documentation generation",
          "impact": "75%+ auto-fill rate for user docs, 80%+ quality for standards",
          "breaking": false
        }
      ]
    }
  ]
}
```

### Validation Rules

- **version:** Must follow semantic versioning (X.Y.Z)
- **date:** ISO 8601 date format (YYYY-MM-DD)
- **workorder_id:** Format WO-{FEATURE}-{CATEGORY}-### (optional but recommended)
- **type:** One of 6 predefined change types
- **severity:** One of 4 severity levels
- **files:** At least 1 file must be specified

---

## 2. UDS (Universal Document Standard) Schema

UDS provides structured metadata for workorder documentation (introduced in v3.6.0).

### Schema Definition

**File:** `schemas/documentation/uds-schema.json`
**Purpose:** Workorder document metadata for traceability
**Applies to:** plan.json, context.json, analysis.json, DELIVERABLES.md, claude.md

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Universal Document Standard (UDS)",
  "type": "object",
  "required": ["generated_by", "document_type", "workorder_id", "last_updated"],
  "properties": {
    "generated_by": {
      "type": "string",
      "pattern": "^coderef-(docs|workflow) v[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Server name and version (e.g., 'coderef-docs v4.0.0')"
    },
    "document_type": {
      "type": "string",
      "enum": ["Feature Plan", "Feature Context", "Feature Analysis", "Deliverables", "Handoff"],
      "description": "Document classification"
    },
    "workorder_id": {
      "type": "string",
      "pattern": "^WO-[A-Z0-9-]+-[0-9]{3}$",
      "description": "Unique workorder identifier"
    },
    "feature_id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Feature identifier (lowercase-kebab-case)"
    },
    "last_updated": {
      "type": "string",
      "format": "date",
      "description": "Last modification date (YYYY-MM-DD)"
    },
    "ai_assistance": {
      "type": "boolean",
      "default": true,
      "description": "Whether AI assisted in generation"
    },
    "status": {
      "type": "string",
      "enum": ["DRAFT", "IN_REVIEW", "APPROVED", "ARCHIVED"],
      "description": "Document lifecycle status"
    },
    "next_review": {
      "type": "string",
      "format": "date",
      "description": "Scheduled review date (auto-calculated: +30 days)"
    }
  }
}
```

### UDS in Markdown Files (YAML Frontmatter)

```markdown
---
title: DELIVERABLES - feature-name
version: 1.0
generated_by: coderef-workflow v1.7.0
workorder_id: WO-GENERATION-ENHANCEMENT-001
feature_id: generation-enhancement-001
status: COMPLETE
timestamp: 2026-01-13T00:00:00Z
---

[Document content]

---
generated_by: coderef-workflow v1.7.0
workorder: WO-GENERATION-ENHANCEMENT-001
feature: generation-enhancement-001
last_updated: 2026-01-13
ai_assistance: true
status: COMPLETE
next_review: 2026-02-12
---
```

### UDS in JSON Files (_uds Section)

```json
{
  "_uds": {
    "generated_by": "coderef-docs v4.0.0",
    "document_type": "Feature Plan",
    "workorder_id": "WO-GENERATION-ENHANCEMENT-001",
    "feature_id": "generation-enhancement-001",
    "last_updated": "2026-01-13",
    "ai_assistance": true,
    "status": "APPROVED",
    "next_review": "2026-02-12"
  },
  ...rest of document
}
```

---

## 3. MCP Protocol Schemas

MCP tool input/output schemas for all 16 tools (v4.0.0).

### 3.1 Tool Input Schema (Common Pattern)

All MCP tools follow this request structure:

```json
{
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "project_path": "/absolute/path/to/project",
      ...tool-specific arguments
    }
  }
}
```

### 3.2 Tool Output Schema (Common Pattern)

All MCP tools return this response structure:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Tool output text..."
    }
  ],
  "isError": false
}
```

### 3.3 Foundation Docs Tools

#### generate_foundation_docs

**Input Schema:**
```json
{
  "type": "object",
  "required": ["project_path"],
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "auto_validate": {
      "type": "boolean",
      "default": true,
      "description": "Auto-validate with Papertrail"
    }
  }
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "drift_check": {
      "type": "object",
      "properties": {
        "drift_percentage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "severity": {
          "type": "string",
          "enum": ["none", "standard", "severe"]
        },
        "message": {
          "type": "string"
        }
      }
    },
    "resource_check": {
      "type": "object",
      "properties": {
        "available": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "missing": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    },
    "generation_plan": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "template_name": {
            "type": "string",
            "enum": ["readme", "architecture", "api", "schema", "components"]
          },
          "progress": {
            "type": "string",
            "pattern": "^\\[[0-9]+/[0-9]+\\]$"
          },
          "context_files": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}
```

### 3.4 User Docs Tools (NEW in v4.0.0)

#### generate_my_guide

**Input Schema:**
```json
{
  "type": "object",
  "required": ["project_path"],
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    }
  }
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "auto_fill_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Percentage of content auto-generated"
    },
    "tools_extracted": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "pattern": "^handle_[a-z_]+$"
          },
          "category": {
            "type": "string",
            "enum": ["Documentation", "Changelog", "Standards", "Validation", "Advanced"]
          }
        }
      }
    },
    "commands_extracted": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "pattern": "^/[a-z-]+$"
          },
          "file": {
            "type": "string"
          }
        }
      }
    },
    "output_path": {
      "type": "string"
    }
  }
}
```

#### generate_user_guide

**Input Schema:** Same as generate_my_guide

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "auto_fill_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "sections": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "Prerequisites",
          "Installation",
          "Architecture Overview",
          "Tools Reference",
          "Commands Reference",
          "Common Workflows",
          "Best Practices",
          "Troubleshooting",
          "FAQ",
          "Quick Reference"
        ]
      }
    },
    "output_path": {
      "type": "string"
    }
  }
}
```

#### generate_features

**Input Schema:** Same as generate_my_guide

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "auto_fill_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "active_features": {
      "type": "number",
      "description": "Count of features in coderef/workorder/"
    },
    "archived_features": {
      "type": "number",
      "description": "Count of features in coderef/archived/"
    },
    "workorders": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "workorder_id": {
            "type": "string",
            "pattern": "^WO-[A-Z0-9-]+-[0-9]{3}$"
          },
          "status": {
            "type": "string",
            "enum": ["active", "complete", "archived"]
          },
          "version": {
            "type": "string",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
          }
        }
      }
    },
    "output_path": {
      "type": "string"
    }
  }
}
```

### 3.5 Standards Tools (ENHANCED in v4.0.0)

#### establish_standards

**Input Schema:**
```json
{
  "type": "object",
  "required": ["project_path"],
  "properties": {
    "project_path": {
      "type": "string"
    },
    "focus_areas": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["ui_components", "behavior_patterns", "ux_flows", "all"]
      },
      "default": ["all"]
    },
    "scan_depth": {
      "type": "string",
      "enum": ["quick", "standard", "deep"],
      "default": "standard"
    },
    "auto_validate": {
      "type": "boolean",
      "default": true
    }
  }
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "mcp_enabled": {
      "type": "boolean",
      "description": "Whether MCP semantic patterns were used"
    },
    "pattern_frequency": {
      "type": "object",
      "additionalProperties": {
        "type": "number",
        "description": "Occurrence count for each pattern"
      }
    },
    "violations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string"
          },
          "line": {
            "type": "number"
          },
          "pattern": {
            "type": "string"
          },
          "message": {
            "type": "string"
          }
        }
      }
    },
    "quality_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Overall quality (80%+ with MCP, 55% regex-only)"
    },
    "output_files": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

---

## 4. Resource Sheet Schemas (v3.4.0)

Resource sheet schemas for composable module-based documentation.

### 4.1 Resource Sheet Metadata

**Frontmatter Schema:**
```yaml
---
subject: "AuthService"
parent_project: "coderef-docs"
category: "service"
version: "1.0.0"
last_updated: "2026-01-13"
status: "active"
tags:
  - authentication
  - security
  - api
---
```

### 4.2 Module Selection Schema

**Internal Schema for Module Detection:**
```json
{
  "type": "object",
  "properties": {
    "characteristics": {
      "type": "object",
      "properties": {
        "has_async_methods": {
          "type": "boolean"
        },
        "has_dependencies": {
          "type": "boolean"
        },
        "has_state": {
          "type": "boolean"
        },
        "has_lifecycle": {
          "type": "boolean"
        },
        "has_validation": {
          "type": "boolean"
        },
        "is_tested": {
          "type": "boolean"
        }
      }
    },
    "selected_modules": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "architecture",
          "integration",
          "testing-stub",
          "performance-stub",
          ...
        ]
      }
    },
    "auto_fill_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    }
  }
}
```

---

## 5. MCP Orchestration Schemas (NEW in v4.0.0)

Schemas for MCP integration layer (drift detection, pattern analysis).

### 5.1 Drift Detection Schema

**Function:** `check_drift()`
**Purpose:** Detects .coderef/index.json staleness

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "drift_percentage": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "severity": {
      "type": "string",
      "enum": ["none", "standard", "severe"],
      "description": "none: ≤10%, standard: >10% ≤50%, severe: >50%"
    },
    "added": {
      "type": "number",
      "description": "Number of elements added since scan"
    },
    "removed": {
      "type": "number",
      "description": "Number of elements removed since scan"
    },
    "modified": {
      "type": "number",
      "description": "Number of elements modified since scan"
    },
    "total": {
      "type": "number",
      "description": "Total elements in index"
    },
    "message": {
      "type": "string",
      "description": "Human-readable drift status"
    }
  }
}
```

### 5.2 Pattern Analysis Schema

**Function:** `call_coderef_patterns()`
**Purpose:** Fetches semantic patterns from coderef-context MCP

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "patterns": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "pattern_type": {
            "type": "string",
            "examples": ["async_function", "class_definition", "test_function"]
          },
          "count": {
            "type": "number",
            "minimum": 0
          },
          "files": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "examples": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string"
                },
                "file": {
                  "type": "string"
                },
                "line": {
                  "type": "number"
                }
              }
            }
          }
        }
      }
    },
    "frequency": {
      "type": "object",
      "additionalProperties": {
        "type": "number"
      },
      "description": "Pattern occurrence counts (e.g., 'async_function': 45)"
    },
    "violations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string"
          },
          "line": {
            "type": "number"
          },
          "pattern": {
            "type": "string"
          },
          "message": {
            "type": "string"
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "major", "minor"]
          }
        }
      }
    },
    "cached": {
      "type": "boolean",
      "description": "Whether result was from cache"
    }
  }
}
```

### 5.3 Resource Check Schema

**Function:** `check_coderef_resources()`
**Purpose:** Validates .coderef/ file availability

```json
{
  "type": "object",
  "properties": {
    "available": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string",
            "examples": ["index.json", "context.md", "patterns.json"]
          },
          "size": {
            "type": "number",
            "description": "File size in bytes"
          },
          "elements": {
            "type": "number",
            "description": "Element count (for index.json)"
          }
        }
      }
    },
    "missing": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string"
          },
          "required": {
            "type": "boolean",
            "description": "Whether file is required vs optional"
          },
          "used_by": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Templates that use this file"
          }
        }
      }
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

---

## 6. Internal Data Models

Python classes and TypedDicts used internally.

### 6.1 ChangelogEntry (type_defs.py)

```python
from typing import TypedDict, List, Literal, Optional

class ChangelogChange(TypedDict):
    type: Literal["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
    severity: Literal["critical", "major", "minor", "patch"]
    title: str
    description: str
    files: List[str]
    reason: str
    impact: str
    breaking: bool
    migration: Optional[str]
    contributors: Optional[List[str]]

class ChangelogEntry(TypedDict):
    version: str  # Semantic version (X.Y.Z)
    date: str  # ISO 8601 date (YYYY-MM-DD)
    summary: Optional[str]
    workorder_id: Optional[str]  # WO-{FEATURE}-{CATEGORY}-###
    changes: List[ChangelogChange]
```

### 6.2 UDSMetadata (type_defs.py)

```python
from typing import TypedDict, Literal, Optional

class UDSMetadata(TypedDict):
    generated_by: str  # e.g., "coderef-docs v4.0.0"
    document_type: Literal["Feature Plan", "Feature Context", "Feature Analysis", "Deliverables", "Handoff"]
    workorder_id: str  # WO-{FEATURE}-{CATEGORY}-###
    feature_id: str  # lowercase-kebab-case
    last_updated: str  # YYYY-MM-DD
    ai_assistance: bool
    status: Literal["DRAFT", "IN_REVIEW", "APPROVED", "ARCHIVED"]
    next_review: str  # YYYY-MM-DD (auto: +30 days)
```

### 6.3 DriftResult (NEW in v4.0.0)

```python
from typing import TypedDict, Literal

class DriftResult(TypedDict):
    success: bool
    drift_percentage: float  # 0-100
    severity: Literal["none", "standard", "severe"]
    added: int
    removed: int
    modified: int
    total: int
    message: str
```

### 6.4 PatternAnalysisResult (NEW in v4.0.0)

```python
from typing import TypedDict, List, Dict, Optional

class PatternExample(TypedDict):
    name: str
    file: str
    line: int

class PatternInfo(TypedDict):
    pattern_type: str
    count: int
    files: List[str]
    examples: List[PatternExample]

class PatternViolation(TypedDict):
    file: str
    line: int
    pattern: str
    message: str
    severity: Literal["critical", "major", "minor"]

class PatternAnalysisResult(TypedDict):
    success: bool
    patterns: List[PatternInfo]
    frequency: Dict[str, int]  # e.g., {"async_function": 45}
    violations: List[PatternViolation]
    cached: bool
```

### 6.5 UserDocsResult (NEW in v4.0.0)

```python
from typing import TypedDict, List, Literal

class ToolInfo(TypedDict):
    name: str
    category: Literal["Documentation", "Changelog", "Standards", "Validation", "Advanced"]

class CommandInfo(TypedDict):
    name: str  # e.g., "/generate-docs"
    file: str

class UserDocsResult(TypedDict):
    auto_fill_rate: float  # 0-100
    tools_extracted: List[ToolInfo]
    commands_extracted: List[CommandInfo]
    output_path: str
```

---

## 7. Validation Rules

### 7.1 Semantic Versioning

All version strings must follow semantic versioning:
- **Format:** `X.Y.Z` (major.minor.patch)
- **Regex:** `^[0-9]+\.[0-9]+\.[0-9]+$`
- **Examples:** `4.0.0`, `1.2.3`, `10.15.99`

### 7.2 Workorder ID Format

Workorder IDs must follow this pattern:
- **Format:** `WO-{FEATURE}-{CATEGORY}-###`
- **Regex:** `^WO-[A-Z0-9-]+-[0-9]{3}$`
- **Examples:**
  - `WO-GENERATION-ENHANCEMENT-001`
  - `WO-CONTEXT-DOCS-INTEGRATION-001`
  - `WO-RESOURCE-SHEET-MCP-TOOL-001`

### 7.3 Feature ID Format

Feature IDs must use lowercase kebab-case:
- **Format:** `lowercase-with-hyphens`
- **Regex:** `^[a-z0-9-]+$`
- **Examples:**
  - `generation-enhancement-001`
  - `context-docs-integration-001`
  - `resource-sheet-mcp-tool-001`

### 7.4 Date Formats

**ISO 8601 Date:**
- **Format:** `YYYY-MM-DD`
- **Regex:** `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`
- **Example:** `2026-01-13`

**ISO 8601 Timestamp:**
- **Format:** `YYYY-MM-DDTHH:MM:SSZ`
- **Example:** `2026-01-13T00:00:00Z`

### 7.5 MCP Handler Names

MCP tool handler functions must follow this pattern:
- **Format:** `handle_{tool_name}`
- **Regex:** `^handle_[a-z_]+$`
- **Examples:**
  - `handle_generate_foundation_docs`
  - `handle_generate_my_guide`
  - `handle_establish_standards`

### 7.6 Slash Command Names

Slash commands must use lowercase with hyphens:
- **Format:** `/{command-name}`
- **Regex:** `^/[a-z-]+$`
- **Examples:**
  - `/generate-docs`
  - `/generate-user-docs`
  - `/establish-standards`

---

## 8. Schema Evolution

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0.0 | 2026-01-13 | Added MCP orchestration schemas, user docs schemas, pattern analysis |
| 3.7.0 | 2026-01-10 | Added direct validation integration schemas |
| 3.6.0 | 2026-01-10 | Added UDS (Universal Document Standard) schema |
| 3.4.0 | 2026-01-02 | Added Resource Sheet schemas |
| 3.2.0 | 2025-12-27 | Added context injection schemas |
| 3.0.0 | 2025-12-20 | Added standards compliance schemas |
| 2.0.0 | 2025-10-15 | Introduced changelog schema v2.0 with workorder tracking |

### Backward Compatibility

**Breaking Changes in v4.0.0:**
- None (all changes are additions)

**Deprecated in v4.0.0:**
- `coderef_foundation_docs` tool (replaced by `generate_foundation_docs`)
- Will be removed in v5.0.0

**Migration Paths:**
- UDS is backward compatible (only applies when workorder_id exists)
- MCP orchestration gracefully degrades when MCP unavailable
- User docs tools are new additions (no migration needed)

---

## 9. Schema References

### External Schemas

- **JSON Schema Draft-07:** http://json-schema.org/draft-07/schema#
- **MCP Protocol:** https://spec.modelcontextprotocol.io/
- **Semantic Versioning:** https://semver.org/

### Internal Schema Files

```
coderef-docs/
├── schemas/
│   ├── documentation/
│   │   ├── uds-schema.json
│   │   ├── foundation-doc-frontmatter-schema.json
│   │   └── resource-sheet-metadata-schema.json
│   └── changelog/
│       └── schema.json
├── coderef/
│   └── changelog/
│       └── CHANGELOG.json  # Conforms to changelog schema
└── type_defs.py  # Python TypedDict definitions
```

---

## 10. Examples

### Example 1: Complete Changelog Entry

```json
{
  "version": "4.0.0",
  "date": "2026-01-13",
  "summary": "MCP integration & user docs automation (WO-GENERATION-ENHANCEMENT-001)",
  "workorder_id": "WO-GENERATION-ENHANCEMENT-001",
  "changes": [
    {
      "type": "feature",
      "severity": "major",
      "title": "MCP tool orchestration layer",
      "description": "Centralized MCP calling with caching, drift detection, and semantic pattern analysis",
      "files": ["mcp_orchestrator.py", "mcp_integration.py"],
      "reason": "Enable code intelligence for documentation generation",
      "impact": "70%+ cache hit rate, 99%+ drift detection accuracy, 80%+ standards quality",
      "breaking": false,
      "contributors": ["willh", "Claude"]
    },
    {
      "type": "feature",
      "severity": "minor",
      "title": "User documentation automation (3 new tools)",
      "description": "Auto-generate my-guide, USER-GUIDE, and FEATURES with 75%+ auto-fill rate",
      "files": ["generators/user_guide_generator.py", "tool_handlers.py"],
      "reason": "Eliminate 75%+ manual documentation work",
      "impact": "3 new tools with MCP tool/command extraction from .coderef/",
      "breaking": false
    }
  ]
}
```

### Example 2: UDS Metadata in plan.json

```json
{
  "_uds": {
    "generated_by": "coderef-workflow v1.7.0",
    "document_type": "Feature Plan",
    "workorder_id": "WO-GENERATION-ENHANCEMENT-001",
    "feature_id": "generation-enhancement-001",
    "last_updated": "2026-01-13",
    "ai_assistance": true,
    "status": "APPROVED",
    "next_review": "2026-02-12"
  },
  "META_DOCUMENTATION": {
    "plan_version": "1.0",
    "workorder_id": "WO-GENERATION-ENHANCEMENT-001",
    ...
  },
  ...
}
```

### Example 3: Drift Detection Result

```python
# From check_drift() function
{
    "success": True,
    "drift_percentage": 15.0,
    "severity": "standard",
    "added": 50,
    "removed": 10,
    "modified": 25,
    "total": 500,
    "message": "⚠️ Warning: Index has moderate drift (15%). Consider re-scanning."
}
```

### Example 4: Pattern Analysis Result

```python
# From call_coderef_patterns() function
{
    "success": True,
    "patterns": [
        {
            "pattern_type": "async_function",
            "count": 45,
            "files": ["tool_handlers.py", "generators/foundation_generator.py"],
            "examples": [
                {
                    "name": "handle_generate_foundation_docs",
                    "file": "tool_handlers.py",
                    "line": 233
                }
            ]
        }
    ],
    "frequency": {
        "async_function": 45,
        "class_definition": 23,
        "test_function": 67
    },
    "violations": [
        {
            "file": "handlers.py",
            "line": 150,
            "pattern": "async_function",
            "message": "Missing await keyword",
            "severity": "major"
        }
    ],
    "cached": False
}
```

---

## References

- **[API.md](API.md)** - Complete API reference for all 16 tools
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[COMPONENTS.md](COMPONENTS.md)** - Components and generators catalog
- **[README.md](../../README.md)** - User-facing guide
- **[INTEGRATION.md](../../INTEGRATION.md)** - MCP integration guide

---

**Generated by:** coderef-docs v4.0.0
**Last Updated:** 2026-01-13
**Workorder:** WO-GENERATION-ENHANCEMENT-001
**MCP Integration:** ✅ Enabled (drift detection, pattern analysis, resource checking)
