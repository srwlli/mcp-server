# API Reference

**Version:** 3.4.0
**Last Updated:** 2026-01-10
**Server:** coderef-docs
**Protocol:** MCP (Model Context Protocol) 1.0

---

## Purpose

This document provides the technical API reference for the **coderef-docs MCP server**. It defines all 13 tools available through the MCP protocol, their input schemas, expected outputs, and integration patterns. This reference enables AI agents and developers to effectively use the documentation generation capabilities.

---

## Overview

The coderef-docs server exposes 13 MCP tools organized into 4 functional domains:

1. **Documentation Generation** (4 tools) - Foundation docs using POWER framework
2. **Resource Sheets** (1 tool) - Composable module-based documentation (NEW in v3.4.0)
3. **Changelog Management** (3 tools) - Version tracking and change recording
4. **Standards & Compliance** (3 tools) - Code pattern enforcement
5. **Validation** (2 tools) - Document health checks

All tools follow JSON-RPC 2.0 over stdio and return structured `TextContent` responses.

---

## Authentication & Access

**Authentication:** None required (local stdio-based MCP server)
**Authorization:** File system permissions (read/write to project directories)
**Rate Limits:** No rate limiting (local execution)

---

## Tool Catalog

### 1. Documentation Generation

#### 1.1 `list_templates`

Lists all available POWER framework templates.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Output:**
```
Available templates: readme, architecture, api, components, schema, user-guide, my-guide
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "list_templates",
    "arguments": {}
  }
}
```

---

#### 1.2 `get_template`

Retrieves the raw POWER framework template content.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "template_name": {
      "type": "string",
      "enum": ["readme", "architecture", "api", "components", "my-guide", "schema", "user-guide"]
    }
  },
  "required": ["template_name"]
}
```

**Output:**
Raw template content with POWER framework structure and AI guidance placeholders.

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_template",
    "arguments": {
      "template_name": "api"
    }
  }
}
```

---

#### 1.3 `generate_foundation_docs`

Generates all 5 foundation documents sequentially with context injection.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    }
  },
  "required": ["project_path"]
}
```

**Output:**
Sequential generation plan with [1/5] through [5/5] progress indicators.

**Generation Sequence:**
1. API.md
2. SCHEMA.md
3. COMPONENTS.md
4. ARCHITECTURE.md
5. README.md

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_foundation_docs",
    "arguments": {
      "project_path": "C:/Users/willh/.mcp-servers/coderef-docs"
    }
  }
}
```

---

#### 1.4 `generate_individual_doc`

Generates a single foundation document with optional UDS metadata.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "template_name": {
      "type": "string",
      "enum": ["readme", "architecture", "api", "components", "my-guide", "schema", "user-guide"]
    },
    "workorder_id": {
      "type": "string",
      "description": "Optional: Workorder ID for UDS tracking (e.g., WO-FEATURE-001)"
    },
    "feature_id": {
      "type": "string",
      "description": "Optional: Feature ID for UDS tracking"
    },
    "version": {
      "type": "string",
      "description": "Optional: Document version (default: 1.0.0)"
    }
  },
  "required": ["project_path", "template_name"]
}
```

**Output:**
Template content with extraction instructions and save path.

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_individual_doc",
    "arguments": {
      "project_path": "C:/Users/willh/.mcp-servers/coderef-docs",
      "template_name": "schema"
    }
  }
}
```

---

### 2. Resource Sheet Generation (NEW in v3.4.0)

#### 2.1 `generate_resource_sheet`

Generates composable module-based documentation in 3 formats (Markdown, JSON Schema, JSDoc).

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "element_name": {
      "type": "string",
      "description": "Name of element to document (e.g., 'AuthService', 'UserModel')"
    },
    "mode": {
      "type": "string",
      "enum": ["reverse-engineer", "template", "refresh"],
      "description": "Generation mode"
    },
    "output_format": {
      "type": "string",
      "enum": ["markdown", "json", "jsdoc", "all"],
      "description": "Output format (default: markdown)"
    }
  },
  "required": ["project_path", "element_name", "mode"]
}
```

**Modes:**
- `reverse-engineer`: Analyze existing code and generate docs
- `template`: Generate scaffolding for new element
- `refresh`: Update existing docs with current code state

**Output:**
Composable documentation with 4 universal modules + conditional modules based on detected characteristics.

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_resource_sheet",
    "arguments": {
      "project_path": "C:/Users/willh/.mcp-servers/coderef-docs",
      "element_name": "FoundationGenerator",
      "mode": "reverse-engineer",
      "output_format": "all"
    }
  }
}
```

---

### 3. Changelog Management

#### 3.1 `add_changelog_entry`

Manually adds a changelog entry with full metadata.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "change_type": {
      "type": "string",
      "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
    },
    "severity": {
      "type": "string",
      "enum": ["critical", "major", "minor", "patch"]
    },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "files": { "type": "array", "items": { "type": "string" } },
    "reason": { "type": "string" },
    "impact": { "type": "string" },
    "breaking": { "type": "boolean", "default": false },
    "migration": { "type": "string" },
    "contributors": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["project_path", "version", "change_type", "severity", "title", "description", "files", "reason", "impact"]
}
```

**Output:**
Confirmation with entry summary and CHANGELOG.json path.

---

#### 3.2 `record_changes`

Smart agentic changelog recording with git auto-detection and AI confirmation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "version": { "type": "string" },
    "workorder_id": { "type": "string" }
  },
  "required": ["project_path", "version"]
}
```

**Workflow:**
1. Auto-detects git changes
2. Suggests change_type and severity
3. Extracts file list from git diff
4. AI agent confirms/adjusts details
5. Writes to CHANGELOG.json

**Output:**
Change suggestion with confirmation prompt.

---

### 4. Standards & Compliance

#### 4.1 `establish_standards`

Extracts coding standards from existing codebase using .coderef/ data.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "focus_areas": {
      "type": "array",
      "items": { "enum": ["ui_components", "behavior_patterns", "ux_flows", "all"] },
      "default": ["all"]
    },
    "scan_depth": {
      "type": "string",
      "enum": ["quick", "standard", "deep"],
      "default": "standard"
    }
  },
  "required": ["project_path"]
}
```

**Output:**
4 markdown files in `coderef/standards/`:
- ui-patterns.md
- behavior-patterns.md
- ux-patterns.md
- coding-conventions.md

**Performance:**
- With .coderef/: ~50ms (10x faster)
- Without .coderef/: ~5-60 seconds (full scan)

---

#### 4.2 `audit_codebase`

Validates codebase compliance against established standards.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "scope": {
      "type": "array",
      "items": { "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"] },
      "default": ["all"]
    },
    "severity_filter": {
      "type": "string",
      "enum": ["critical", "major", "minor", "all"],
      "default": "all"
    },
    "generate_fixes": { "type": "boolean", "default": true },
    "standards_dir": { "type": "string", "default": "coderef/standards" }
  },
  "required": ["project_path"]
}
```

**Output:**
Compliance report with 0-100 score, violations by severity, and fix suggestions.

---

#### 4.3 `check_consistency`

Pre-commit gate for staged file changes.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "files": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Files to check (auto-detects git changes if omitted)"
    },
    "scope": {
      "type": "array",
      "items": { "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"] },
      "default": ["all"]
    },
    "severity_threshold": {
      "type": "string",
      "enum": ["critical", "major", "minor"],
      "default": "major"
    },
    "fail_on_violations": { "type": "boolean", "default": true },
    "standards_dir": { "type": "string", "default": "coderef/standards" }
  },
  "required": ["project_path"]
}
```

**Output:**
Pass/fail status with violation details for modified files only.

---

### 5. Validation

#### 5.1 `validate_document`

Validates document against UDS (Universal Document Standard) schema.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "document_path": { "type": "string" },
    "document_type": {
      "type": "string",
      "enum": ["plan", "context", "analysis", "deliverables", "claude"],
      "description": "Type of document to validate"
    }
  },
  "required": ["project_path", "document_path", "document_type"]
}
```

**Output:**
Validation result with schema compliance status.

---

#### 5.2 `check_document_health`

Calculates document health score (0-100) based on completeness and quality.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "document_path": { "type": "string" },
    "document_type": {
      "type": "string",
      "enum": ["plan", "context", "deliverables", "architecture", "readme"]
    }
  },
  "required": ["project_path", "document_path", "document_type"]
}
```

**Output:**
Health score with breakdown:
- Completeness (40%)
- Quality (30%)
- Freshness (20%)
- Standards compliance (10%)

---

### 6. Quickref Generation

#### 6.1 `generate_quickref_interactive`

Interactive workflow to generate universal quickref guide.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": { "type": "string" },
    "app_type": {
      "type": "string",
      "enum": ["cli", "web", "api", "desktop", "library"],
      "description": "Type of application (can be inferred from user responses)"
    }
  },
  "required": ["project_path"]
}
```

**Output:**
Interview questions for AI to ask user → generates scannable quickref.md (150-250 lines).

---

## Error Handling

All tools return standardized error responses:

```json
{
  "type": "text",
  "text": "❌ Error: [Error message]\n\nDetails: [Stack trace or context]\n\nSuggestion: [How to fix]"
}
```

**Common Errors:**
- `Invalid project path` - Path doesn't exist or isn't accessible
- `Template not found` - Invalid template_name provided
- `CHANGELOG.json validation failed` - Invalid JSON schema
- `Standards not established` - Run establish_standards first
- `Git repository required` - record_changes needs git

---

## References

- **Server Implementation:** [server.py](../../server.py)
- **Tool Handlers:** [tool_handlers.py](../../tool_handlers.py)
- **POWER Framework:** [templates/power/](../../templates/power/)
- **Standards System:** [CLAUDE.md](../../CLAUDE.md#standards--compliance-system)
- **UDS Specification:** [CLAUDE.md](../../CLAUDE.md#universal-document-standard-uds)
- **MCP Specification:** https://spec.modelcontextprotocol.io/

---

**Maintained by:** coderef-docs MCP server
**Generated:** 2026-01-10
**AI Assistance:** Claude Code (Sonnet 4.5)
