# API Reference - coderef-docs MCP Server

**Version:** 3.2.0
**Last Updated:** 2025-12-28
**Framework:** MCP (Model Context Protocol) 1.0+

---

## Purpose

This document serves as the complete API reference for the coderef-docs MCP server, documenting all 11 tools, their schemas, request/response formats, and integration patterns. It enables AI agents and developers to understand and invoke documentation generation tools programmatically.

---

## Overview

The coderef-docs MCP server exposes 11 tools via JSON-RPC 2.0 over stdio, organized into three domains:

1. **Documentation Generation** (5 tools) - Foundation docs, templates, quickref
2. **Changelog Management** (3 tools) - Get, add, record changes
3. **Standards & Compliance** (3 tools) - Establish, audit, check consistency

All tools follow async/await patterns and return structured JSON responses.

---

## Authentication

**Protocol:** No authentication required (local stdio communication)
**Transport:** JSON-RPC 2.0 over stdio
**Server Start:** `python -m coderef-docs.server`

MCP servers communicate via stdio pipes with the Claude Code client. No HTTP endpoints or API keys required.

---

## Base URL / Endpoint

**N/A** - MCP uses JSON-RPC 2.0 over stdio (not HTTP)

**Communication Pattern:**
```
Claude Code → stdio → coderef-docs.server.py → Tool Handler → Response
```

---

## API Domains

### 1. Documentation Generation

#### `list_templates`

**Description:** List all available POWER framework templates

**Input Schema:**
```json
{}
```

**Response:**
```json
{
  "templates": [
    {
      "name": "readme",
      "description": "Project README and overview",
      "output_file": "README.md"
    },
    {
      "name": "architecture",
      "description": "Overall system architecture",
      "output_file": "ARCHITECTURE.md"
    },
    {
      "name": "api",
      "description": "API endpoints and integrations",
      "output_file": "API.md"
    },
    {
      "name": "components",
      "description": "UI components and architecture",
      "output_file": "COMPONENTS.md"
    },
    {
      "name": "schema",
      "description": "Database schema and data models",
      "output_file": "SCHEMA.md"
    },
    {
      "name": "user-guide",
      "description": "User-facing documentation",
      "output_file": "USER-GUIDE.md"
    },
    {
      "name": "my-guide",
      "description": "Internal tool guide",
      "output_file": "my-guide.md"
    }
  ]
}
```

**Example:**
```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_templates",
    "arguments": {}
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "templates": [...]
  }
}
```

---

#### `get_template`

**Description:** Retrieve specific template content by name

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "template_name": {
      "type": "string",
      "enum": ["readme", "architecture", "api", "components", "schema", "user-guide", "my-guide"],
      "description": "Name of template to retrieve"
    }
  },
  "required": ["template_name"]
}
```

**Response:**
```json
{
  "template_name": "readme",
  "content": "framework: POWER\npurpose: Generate README.md...",
  "framework": "POWER",
  "output_file": "README.md"
}
```

**Example:**
```bash
# Request
{
  "template_name": "architecture"
}

# Response
{
  "template_name": "architecture",
  "content": "framework: POWER\npurpose: ...",
  "framework": "POWER",
  "output_file": "ARCHITECTURE.md"
}
```

---

#### `generate_foundation_docs`

**Description:** Generate all 5 foundation documents sequentially with context injection

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "force_regenerate": {
      "type": "boolean",
      "description": "Regenerate even if docs exist (default: false)"
    },
    "use_coderef": {
      "type": "boolean",
      "description": "Use @coderef/core CLI for context injection (default: true)"
    }
  },
  "required": ["project_path"]
}
```

**Response:**
```json
{
  "status": "planned",
  "total_documents": 5,
  "context_injection": "enabled",
  "generation_plan": [
    {"sequence": 1, "template": "api", "context_injection": true},
    {"sequence": 2, "template": "schema", "context_injection": true},
    {"sequence": 3, "template": "components", "context_injection": true},
    {"sequence": 4, "template": "architecture", "context_injection": false},
    {"sequence": 5, "template": "readme", "context_injection": false}
  ],
  "instructions": "Call generate_individual_doc for each template in sequence"
}
```

**Example:**
```json
// Request
{
  "project_path": "/path/to/project",
  "force_regenerate": false,
  "use_coderef": true
}

// Response shows generation plan with [1/5] through [5/5] progress
```

---

#### `generate_individual_doc`

**Description:** Generate single document from template with optional context injection

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "template_name": {
      "type": "string",
      "enum": ["readme", "architecture", "api", "components", "schema", "user-guide", "my-guide"],
      "description": "Template to generate"
    }
  },
  "required": ["project_path", "template_name"]
}
```

**Response (with context injection):**
```json
{
  "template_name": "api",
  "output_path": "coderef/foundation-docs/API.md",
  "context_injection": "enabled",
  "extracted_data": {
    "apis": [
      {"endpoint": "/api/users", "method": "GET"},
      {"endpoint": "/api/users/:id", "method": "POST"}
    ]
  },
  "template_content": "framework: POWER\n...",
  "instructions": "Populate template with extracted API data"
}
```

**Response (without context injection):**
```json
{
  "template_name": "architecture",
  "output_path": "coderef/foundation-docs/ARCHITECTURE.md",
  "context_injection": "disabled",
  "template_content": "framework: POWER\n...",
  "instructions": "Generate architecture documentation using template"
}
```

---

#### `generate_quickref_interactive`

**Description:** Interactive workflow to generate quickref guide for any application type

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "app_type": {
      "type": "string",
      "enum": ["cli", "web", "api", "desktop", "library"],
      "description": "Application type (optional, can be inferred)"
    }
  },
  "required": ["project_path"]
}
```

**Response:**
```json
{
  "status": "interview_started",
  "questions": [
    "What is the primary purpose of this application?",
    "Who is the target audience (developers, end-users, both)?",
    "What are the top 5 most important features?",
    "Are there any common use cases or workflows?",
    "What are the installation/setup steps?"
  ],
  "instructions": "AI will guide user through interview, then generate quickref.md (150-250 lines)"
}
```

---

### 2. Changelog Management

#### `get_changelog`

**Description:** Query changelog by version or change type

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Optional: Get specific version (e.g., '1.0.1')"
    },
    "change_type": {
      "type": "string",
      "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"],
      "description": "Optional: Filter by change type"
    },
    "breaking_only": {
      "type": "boolean",
      "description": "Optional: Show only breaking changes"
    }
  },
  "required": ["project_path"]
}
```

**Response:**
```json
{
  "changelog_path": "coderef/CHANGELOG.json",
  "total_versions": 3,
  "versions": [
    {
      "version": "1.0.2",
      "release_date": "2025-12-28",
      "summary": "Bug fixes and performance improvements",
      "changes": [
        {
          "type": "bugfix",
          "severity": "minor",
          "title": "Fix template loading path",
          "description": "Corrected template path resolution",
          "files": ["generators/base_generator.py"],
          "breaking": false
        }
      ]
    }
  ]
}
```

---

#### `add_changelog_entry`

**Description:** Manually add changelog entry with full metadata

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {"type": "string"},
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "change_type": {
      "type": "string",
      "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
    },
    "severity": {
      "type": "string",
      "enum": ["critical", "major", "minor", "patch"]
    },
    "title": {"type": "string"},
    "description": {"type": "string"},
    "files": {
      "type": "array",
      "items": {"type": "string"}
    },
    "reason": {"type": "string"},
    "impact": {"type": "string"},
    "breaking": {"type": "boolean", "default": false}
  },
  "required": ["project_path", "version", "change_type", "severity", "title", "description", "files", "reason", "impact"]
}
```

**Response:**
```json
{
  "success": true,
  "version": "1.0.3",
  "entry_added": {
    "type": "feature",
    "severity": "minor",
    "title": "Add semantic search",
    "files": ["generators/search_engine.py"]
  },
  "changelog_path": "coderef/CHANGELOG.json"
}
```

---

#### `record_changes`

**Description:** Smart agentic changelog recording with git auto-detection

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {"type": "string"},
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "context": {
      "type": "object",
      "description": "Optional context for git-less environments"
    }
  },
  "required": ["project_path", "version"]
}
```

**Response:**
```json
{
  "status": "preview",
  "detected_changes": {
    "files_changed": ["generators/uds_ai_generator.py", "server.py"],
    "commit_messages": ["feat: Add UDS AI generator"],
    "suggested_change_type": "feature",
    "suggested_severity": "minor"
  },
  "preview": {
    "version": "1.0.3",
    "change_type": "feature",
    "title": "Add UDS AI generator",
    "files": ["generators/uds_ai_generator.py"],
    "requires_confirmation": true
  },
  "instructions": "Review preview, confirm to create changelog entry"
}
```

---

### 3. Standards & Compliance

#### `establish_standards`

**Description:** Scan codebase to discover and document UI/UX/behavior patterns

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {"type": "string"},
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
    }
  },
  "required": ["project_path"]
}
```

**Response:**
```json
{
  "status": "completed",
  "standards_created": [
    "coderef/standards/ui-patterns.md",
    "coderef/standards/behavior-patterns.md",
    "coderef/standards/ux-patterns.md",
    "coderef/standards/index.md"
  ],
  "patterns_discovered": {
    "ui_components": 47,
    "behavior_patterns": 23,
    "ux_flows": 15
  },
  "scan_duration": "3.2s"
}
```

---

#### `audit_codebase`

**Description:** Audit codebase for standards violations with compliance scoring

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {"type": "string"},
    "scope": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"]
      },
      "default": ["all"]
    },
    "severity_filter": {
      "type": "string",
      "enum": ["critical", "major", "minor", "all"],
      "default": "all"
    },
    "generate_fixes": {
      "type": "boolean",
      "default": true
    }
  },
  "required": ["project_path"]
}
```

**Response:**
```json
{
  "compliance_score": 87,
  "total_violations": 23,
  "violations_by_severity": {
    "critical": 2,
    "major": 8,
    "minor": 13
  },
  "violations": [
    {
      "file": "components/Button.tsx",
      "line": 42,
      "severity": "major",
      "pattern": "ui_patterns",
      "violation": "Button variant 'danger' does not match standard variants",
      "fix_suggestion": "Change to 'destructive' variant"
    }
  ],
  "report_path": "coderef/standards/audit-report-2025-12-28.md"
}
```

---

#### `check_consistency`

**Description:** Pre-commit gate for staged file changes

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {"type": "string"},
    "files": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Optional: Files to check (auto-detects git staged if omitted)"
    },
    "scope": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"]
      },
      "default": ["all"]
    },
    "severity_threshold": {
      "type": "string",
      "enum": ["critical", "major", "minor"],
      "default": "major"
    },
    "fail_on_violations": {
      "type": "boolean",
      "default": true
    }
  },
  "required": ["project_path"]
}
```

**Response:**
```json
{
  "status": "failed",
  "files_checked": 3,
  "violations_found": 2,
  "blocking_violations": [
    {
      "file": "components/Modal.tsx",
      "severity": "critical",
      "message": "Missing required close button (UX pattern violation)"
    }
  ],
  "exit_code": 1,
  "message": "Consistency check failed: 2 violations at 'major' severity or above"
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params: template_name must be one of [readme, architecture, api, components, schema, user-guide, my-guide]",
    "data": {
      "param": "template_name",
      "provided": "invalid-template",
      "expected": ["readme", "architecture", "api", "components", "schema", "user-guide", "my-guide"]
    }
  }
}
```

### Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `-32700` | Parse error | Invalid JSON received |
| `-32600` | Invalid request | JSON-RPC request malformed |
| `-32601` | Method not found | Tool name doesn't exist |
| `-32602` | Invalid params | Tool arguments invalid or missing |
| `-32603` | Internal error | Server-side processing error |
| `-32000` | File not found | Template or file path doesn't exist |
| `-32001` | Validation error | Schema validation failed |
| `-32002` | Context injection failed | @coderef/core CLI error |

---

## Rate Limiting

**N/A** - Local stdio communication has no rate limits

For AI enhancement features (optional):
- OpenAI API: 3,500 requests/min (tier-based)
- Anthropic API: 50 requests/min (default tier)

---

## Pagination

**N/A** - All responses return complete datasets

Changelog queries with many versions return full history. For large changelogs (100+ versions), consider filtering by version range (future enhancement).

---

## Versioning

**API Version:** 3.2.0
**Protocol:** MCP 1.0+ (JSON-RPC 2.0)
**Breaking Changes:** Tracked in CHANGELOG.json

The MCP server follows semantic versioning:
- **Major:** Breaking changes to tool schemas
- **Minor:** New tools or backward-compatible enhancements
- **Patch:** Bug fixes, no schema changes

---

## Examples

### Complete Workflow: Generate Foundation Docs

```json
// Step 1: List available templates
{
  "tool": "list_templates",
  "arguments": {}
}

// Step 2: Generate foundation docs
{
  "tool": "generate_foundation_docs",
  "arguments": {
    "project_path": "/path/to/project",
    "use_coderef": true
  }
}

// Step 3: Generate each doc sequentially
{
  "tool": "generate_individual_doc",
  "arguments": {
    "project_path": "/path/to/project",
    "template_name": "api"
  }
}
// ... repeat for schema, components, architecture, readme

// Step 4: Verify output
// Check: README.md in project root
// Check: API.md, SCHEMA.md, COMPONENTS.md, ARCHITECTURE.md in coderef/foundation-docs/
```

### Complete Workflow: Record Changes

```json
// Step 1: Detect changes with git auto-detection
{
  "tool": "record_changes",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "1.0.3"
  }
}
// Returns preview with suggested change_type and severity

// Step 2: Review preview, confirm or manually add entry
{
  "tool": "add_changelog_entry",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "1.0.3",
    "change_type": "feature",
    "severity": "minor",
    "title": "Add semantic search",
    "description": "Implemented vector-based semantic search across all docs",
    "files": ["generators/search_engine.py", "server.py"],
    "reason": "Enable natural language doc discovery",
    "impact": "Users can search by intent instead of keywords"
  }
}

// Step 3: Verify changelog
{
  "tool": "get_changelog",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "1.0.3"
  }
}
```

---

## References

- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **Server Implementation:** `server.py` (374 lines)
- **Tool Handlers:** `tool_handlers.py` (925+ lines)
- **POWER Framework:** Templates in `templates/power/`
- **CLAUDE.md:** Complete server architecture and design decisions

---

**Copyright © 2025 | CodeRef Documentation System**
**Generated by:** coderef-docs v3.2.0
**AI Assistance:** true
**Last Updated:** 2025-12-28
