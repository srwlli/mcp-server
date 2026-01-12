# API Reference - coderef-docs

**Project:** coderef-docs (MCP Server)
**Version:** 3.7.0
**Last Updated:** 2026-01-11
**Protocol:** MCP (Model Context Protocol) 1.0

---

## Purpose

This document provides the complete MCP tool interface reference for coderef-docs, a documentation generation server that provides 13 specialized tools for foundation docs, changelog management, standards enforcement, and composable resource sheets.

## Overview

**What's Included:**
- 13 MCP tool endpoints with complete schemas
- Direct validation integration details (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)
- Request/response examples
- Error handling patterns
- Tool orchestration workflows

**Not Included:**
- Internal implementation details (see ARCHITECTURE.md)
- Setup/deployment (see README.md)

---

## Authentication & Transport

**Protocol:** JSON-RPC 2.0 over stdio
**Authentication:** None (local MCP server)
**Content-Type:** application/json

### Connection

The server runs as a subprocess and communicates via standard input/output:

```python
# From .mcp.json configuration
{
  "coderef-docs": {
    "command": "python",
    "args": ["C:/Users/willh/.mcp-servers/coderef-docs/server.py"],
    "cwd": "C:/Users/willh/.mcp-servers/coderef-docs"
  }
}
```

---

## Tool Endpoints

### 1. Template Management

#### list_templates

List all available POWER framework templates.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_templates",
    "arguments": {}
  }
}
```

**Response:**
```json
{
  "result": [
    {
      "type": "text",
      "text": "Available templates: readme, architecture, api, components, schema, user-guide, my-guide"
    }
  ]
}
```

---

#### get_template

Retrieve specific template content.

**Parameters:**
- `template_name` (string, required): One of readme, architecture, api, components, my-guide, schema, user-guide

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_template",
    "arguments": {
      "template_name": "readme"
    }
  }
}
```

**Response:**
```json
{
  "result": [
    {
      "type": "text",
      "text": "framework: POWER\npurpose: Generate README.md as the discovery entry document.\n..."
    }
  ]
}
```

---

### 2. Foundation Documentation

#### generate_foundation_docs

Generate all 5 foundation documents (README, ARCHITECTURE, API, COMPONENTS, SCHEMA) with sequential workflow and .coderef/ integration.

**Parameters:**
- `project_path` (string, required): Absolute path to project directory

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_foundation_docs",
    "arguments": {
      "project_path": "C:/Users/willh/.mcp-servers/coderef-docs"
    }
  }
}
```

**Response:**
```json
{
  "result": [
    {
      "type": "text",
      "text": "Foundation Documentation Generation Plan\n\n.coderef/ resources: ✅ Available\n\nDocuments to generate (5):\n1. API.md\n2. SCHEMA.md\n3. COMPONENTS.md\n4. ARCHITECTURE.md\n5. README.md\n\nWorkflow: Read .coderef/ files → Extract elements → Populate templates"
    }
  ]
}
```

---

#### generate_individual_doc

Generate a single documentation file with **direct validation integration** (v3.7.0).

**Parameters:**
- `project_path` (string, required): Absolute path to project directory
- `template_name` (string, required): Template to generate
- `workorder_id` (string, optional): Workorder ID for UDS tracking (enables Papertrail if PAPERTRAIL_ENABLED=true)
- `feature_id` (string, optional): Feature ID for UDS tracking (defaults to template_name)
- `version` (string, optional): Document version (default: 1.0.0)

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_individual_doc",
    "arguments": {
      "project_path": "C:/Users/willh/.mcp-servers/coderef-docs",
      "template_name": "readme"
    }
  }
}
```

**Response (Direct Validation - v3.7.0):**
```json
{
  "result": [
    {
      "type": "text",
      "text": "✅ Generated and saved README.md\n\n📁 Location: C:/Users/willh/.mcp-servers/coderef-docs/README.md\n📄 Template: readme\n\n📊 Validation: 95/100\n  ✅ 0 errors, 1 warnings\n  • Metadata written to frontmatter _uds section\n\n✅ Validation passed (score: 95, threshold: 90)"
    }
  ]
}
```

**Key Feature (WO-CODEREF-DOCS-DIRECT-VALIDATION-001):**
- Tool executes validation at runtime (NOT Claude)
- Tool saves file → runs validator → writes `_uds` metadata to frontmatter
- Returns simple result message (NO instruction blocks)

---

### 3. Changelog Management

#### add_changelog_entry

Manually add changelog entry with all details.

**Parameters:**
- `project_path` (string, required)
- `version` (string, required): Pattern `^\d+\.\d+\.\d+$`
- `change_type` (string, required): bugfix, enhancement, feature, breaking_change, deprecation, security
- `severity` (string, required): critical, major, minor, patch
- `title` (string, required): Short description
- `description` (string, required): Detailed description
- `files` (array[string], required): List of affected files
- `reason` (string, required): Why change was made
- `impact` (string, required): Impact on users/system
- `breaking` (boolean, optional): Default false
- `migration` (string, optional): Migration guide for breaking changes
- `summary` (string, optional): Version summary
- `contributors` (array[string], optional): List of contributors

---

#### record_changes

Smart agentic changelog recording with git auto-detection (recommended).

**Parameters:**
- `project_path` (string, required)
- `version` (string, required): Pattern `^\d+\.\d+\.\d+$`
- `context` (object, optional): Manual context for git-less environments

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "record_changes",
    "arguments": {
      "project_path": "C:/Users/willh/.mcp-servers/coderef-docs",
      "version": "3.7.0"
    }
  }
}
```

**Response:**
```json
{
  "result": [
    {
      "type": "text",
      "text": "📊 Git Auto-Detection Results:\n\nFiles changed (staged): 2\n  • tool_handlers.py\n  • tests/test_direct_validation.py\n\nSuggested change_type: feature\nCalculated severity: major\n\n✅ Confirm to create changelog entry?"
    }
  ]
}
```

---

### 4. Quick Reference

#### generate_quickref_interactive

Interactive workflow to generate universal quickref guide for any application type.

**Parameters:**
- `project_path` (string, required)
- `app_type` (string, optional): cli, web, api, desktop, library (can be inferred)

---

### 5. Resource Sheets

#### generate_resource_sheet

Generate composable module-based technical documentation with auto-detection and 3-format output.

**Parameters:**
- `element_name` (string, required): Code element name
- `project_path` (string, required)
- `element_type` (string, optional): component, hook, service (auto-detected)
- `mode` (string, optional): reverse-engineer, template, refresh (default: reverse-engineer)
- `auto_analyze` (boolean, optional): Use coderef_scan (default: true)
- `output_path` (string, optional): Custom output directory
- `validate_against_code` (boolean, optional): Drift detection (default: true)

---

### 6. Standards & Compliance

#### establish_standards

Scan codebase to discover and document coding standards (run ONCE per project).

**Parameters:**
- `project_path` (string, required)
- `scan_depth` (string, optional): quick, standard, deep (default: standard)
- `focus_areas` (array[string], optional): ui_components, behavior_patterns, ux_flows, all (default: ["all"])

**Response (Direct Validation - v3.7.0):**
```json
{
  "result": [
    {
      "type": "text",
      "text": "✅ Standards establishment completed successfully!\n\n📊 RESULTS:\nFiles Created: 3\nTotal Patterns Discovered: 15\n\n📋 VALIDATION RESULTS:\n  ✅ PASSED ui-patterns.md: 94/100\n  ✅ PASSED behavior-patterns.md: 92/100\n  ✅ PASSED ux-patterns.md: 91/100\n\n💾 Validation metadata saved to frontmatter _uds sections"
    }
  ]
}
```

---

#### audit_codebase

Audit codebase for standards violations (requires established standards).

**Parameters:**
- `project_path` (string, required)
- `standards_dir` (string, optional): Default "coderef/standards"
- `severity_filter` (string, optional): critical, major, minor, all (default: all)
- `scope` (array[string], optional): ui_patterns, behavior_patterns, ux_patterns, all
- `generate_fixes` (boolean, optional): Default true

---

#### check_consistency

Pre-commit gate for modified files (lightweight quality check).

**Parameters:**
- `project_path` (string, required)
- `files` (array[string], optional): Files to check (auto-detects git changes)
- `standards_dir` (string, optional): Default "coderef/standards"
- `severity_threshold` (string, optional): critical, major, minor (default: major)
- `scope` (array[string], optional): ui_patterns, behavior_patterns, ux_patterns, all
- `fail_on_violations` (boolean, optional): Default true

---

### 7. Document Validation

#### validate_document

Validate document against UDS (Universal Documentation Standards) schema.

**Parameters:**
- `document_path` (string, required): Absolute path to document file
- `doc_type` (string, required): plan, deliverables, architecture, readme, api

---

#### check_document_health

Calculate document health score (0-100) based on traceability, completeness, freshness, and validation.

**Parameters:**
- `document_path` (string, required)
- `doc_type` (string, required): plan, deliverables, architecture, readme, api

**Response:**
```json
{
  "result": [
    {
      "type": "text",
      "text": "Document Health Score: 92/100\n\nBreakdown:\n  • Traceability (40%): 38/40\n  • Completeness (30%): 28/30\n  • Freshness (20%): 18/20\n  • Validation (10%): 8/10\n\nStatus: HEALTHY"
    }
  ]
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "details": "project_path is required"
    }
  }
}
```

### Common Error Codes

| Code | Message | Description |
|------|---------|-------------|
| -32600 | Invalid Request | Malformed JSON-RPC request |
| -32601 | Method not found | Unknown tool name |
| -32602 | Invalid params | Missing or invalid parameters |
| -32603 | Internal error | Server-side error during execution |

---

## Tool Orchestration Workflows

### Workflow 1: Complete Foundation Documentation

```
1. generate_foundation_docs (returns plan)
2. For each template in plan:
   - generate_individual_doc (generates + validates)
3. Verify all 5 docs exist with _uds metadata
```

### Workflow 2: Standards Establishment & Compliance

```
1. establish_standards (scan_depth: standard)
2. audit_codebase (severity_filter: major)
3. For CI/CD: check_consistency (auto-detects git changes)
```

### Workflow 3: Feature Documentation Lifecycle

```
1. generate_individual_doc (workorder_id: WO-FEATURE-001)
2. add_changelog_entry (version: 1.1.0, change_type: feature)
3. validate_document (doc_type: api)
4. check_document_health (verify score >= 90)
```

---

## Versioning

**API Version:** Follows MCP protocol 1.0
**Tool Schema Version:** 1.0.0

**Version History:**
- v3.7.0 (2026-01-11): Direct validation integration (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)
- v3.6.0 (2026-01-10): Papertrail validators integration (deprecated)
- v3.5.0: .coderef/ integration for foundation docs
- v3.4.0: Resource sheet MCP tool

---

## References

- **ARCHITECTURE.md** - Internal implementation details
- **README.md** - Setup and usage guide
- **SCHEMA.md** - Data structures and schemas
- **COMPONENTS.md** - Key modules and components
- **MCP Specification** - https://spec.modelcontextprotocol.io/

---

**Maintained by:** willh, Claude Code AI
**Last API Update:** 2026-01-11 (v3.7.0 - Direct Validation Integration)
**Status:** ✅ Production Ready
