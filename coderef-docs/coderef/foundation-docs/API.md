# API Reference - coderef-docs MCP Server

**Version:** 3.2.0  
**Last Updated:** 2025-12-27  
**Protocol:** Model Context Protocol (MCP)  
**Total Tools:** 11

---

## Purpose

This document provides the complete API reference for the coderef-docs MCP server's 11 specialized tools for documentation generation, changelog management, and standards enforcement.

---

## Overview

The coderef-docs MCP server exposes tools through the Model Context Protocol, enabling AI assistants to generate, maintain, and validate project documentation with optional real code intelligence from @coderef/core CLI.

**Tool Categories:**
1. Documentation Templates (2 tools)
2. Foundation Generation (2 tools)  
3. Changelog Management (3 tools)
4. Standards & Compliance (3 tools)
5. Interactive Quickref (1 tool)

---

## MCP Tools

### 1. Documentation Templates

#### `list_templates`

Lists all available POWER framework templates.

**Arguments:** None

**Returns:** List of template names (readme, architecture, api, schema, components, my-guide, user-guide)

---

#### `get_template`

Retrieves a specific template by name.

**Arguments:**
- `template_name` (string): Template identifier

**Returns:** Template content in POWER framework format

---

### 2. Foundation Documentation Generation

#### `generate_foundation_docs`

Orchestrates sequential generation of 5 foundation documents with context injection.

**Arguments:**
- `project_path` (string): Absolute path to project directory

**Returns:** Generation plan with:
- Document sequence: API → Schema → Components → Architecture → README
- Context injection status
- Progress indicators [1/5] through [5/5]

**Features:**
- Extracts real API endpoints via @coderef/core CLI
- Extracts real data entities  
- Extracts real UI components
- Sequential generation to avoid timeouts

---

#### `generate_individual_doc`

Generates a single documentation file with optional context injection.

**Arguments:**
- `project_path` (string): Absolute path to project
- `template_name` (string): Template to generate

**Returns:** Template + extracted data (if context injection enabled)

**Output Paths:**
- README.md → Project root
- All others → `coderef/foundation-docs/`

---

### 3. Changelog Management

#### `get_changelog`

Retrieves project changelog with optional filtering.

**Arguments:**
- `project_path` (string): Absolute path to project
- `version` (string, optional): Filter by version
- `change_type` (string, optional): Filter by type
- `breaking_only` (boolean, optional): Show only breaking changes

**Returns:** Structured changelog entries in JSON format

---

#### `add_changelog_entry`

Manually adds a changelog entry with full metadata.

**Required Arguments:**
- `project_path`, `version`, `change_type`, `severity`, `title`, `description`, `files`, `reason`, `impact`

**Optional Arguments:**
- `breaking`, `migration`, `contributors`, `summary`

**Returns:** Confirmation of entry creation

---

#### `record_changes`

Smart changelog recording with git auto-detection (agentic tool).

**Arguments:**
- `project_path` (string): Absolute path to project
- `version` (string): Version number
- `context` (object, optional): Additional context

**Behavior:**
1. Auto-detects changed files via git
2. Suggests change_type from commits
3. Calculates severity from scope
4. Shows preview for confirmation
5. Creates changelog entry

---

### 4. Standards & Compliance

#### `establish_standards`

Scans codebase to discover UI/UX/behavior patterns.

**Arguments:**
- `project_path` (string): Absolute path to project
- `focus_areas` (array, optional): Areas to analyze
- `scan_depth` (string, optional): Analysis depth (quick/standard/deep)

**Output:** Creates 4 markdown files in `coderef/standards/`

---

#### `audit_codebase`

Audits codebase for standards violations.

**Arguments:**
- `project_path` (string): Absolute path to project
- `scope` (array, optional): Areas to audit
- `severity_filter` (string, optional): Filter by severity
- `generate_fixes` (boolean, optional): Include fix suggestions

**Returns:** Compliance report with 0-100 score

---

#### `check_consistency`

Pre-commit gate for checking staged changes.

**Arguments:**
- `project_path` (string): Absolute path to project
- `files` (array, optional): Files to check (auto-detects if omitted)
- `scope` (array, optional): Standards to check
- `severity_threshold` (string, optional): Fail threshold
- `fail_on_violations` (boolean, optional): Return error status

**Returns:** Violations or success status

---

### 5. Interactive Quickref

#### `generate_quickref_interactive`

Interactive workflow for universal quickref guide generation.

**Arguments:**
- `project_path` (string): Absolute path to project
- `app_type` (string, optional): Application type (cli/web/api/desktop/library)

**Returns:** Interview questions for AI to ask user

**Output:** Generates `quickref.md` (150-250 lines) after user responses

---

## Error Handling

All tools use consistent error response format with descriptive messages.

**Common Errors:**
- Invalid project path
- Template not found
- Git repository required
- Version format invalid
- Standards directory missing

---

## Context Injection

When @coderef/core CLI is available:

**API.md:** Extracts real API endpoints from codebase  
**SCHEMA.md:** Extracts real data entities  
**COMPONENTS.md:** Extracts real UI components

**Fallback:** Uses template placeholders if CLI unavailable

**Cache:** Extracted data cached with `@lru_cache(maxsize=32)`

---

## Examples

### Generate Foundation Docs with Context Injection

```json
{
  "tool": "generate_foundation_docs",
  "arguments": {
    "project_path": "/path/to/project"
  }
}
```

Returns sequential plan → Call `generate_individual_doc` 5 times → Complete docs with real code intelligence

### Smart Changelog Recording

```json
{
  "tool": "record_changes",
  "arguments": {
    "project_path": "/path/to/project",
    "version": "3.2.0"
  }
}
```

Auto-detects git changes → Suggests metadata → Shows preview → Creates entry

### Pre-commit Standards Check

```json
{
  "tool": "check_consistency",
  "arguments": {
    "project_path": "/path/to/project",
    "severity_threshold": "major"
  }
}
```

Checks staged files → Returns violations or success

---

## References

- **Server Implementation:** `server.py`, `tool_handlers.py`
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **POWER Framework:** `templates/power/`
- **Context Injection:** `extractors.py` (WO-CONTEXT-DOCS-INTEGRATION-001)
- **Related Documentation:** ARCHITECTURE.md, SCHEMA.md, COMPONENTS.md

---

*Generated: 2025-12-27*  
*For AI Agents: This API is optimized for AI-driven documentation workflows*
