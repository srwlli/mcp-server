---
generated_by: coderef-docs
template: api
date: "2026-01-14T01:20:46Z"
doc_type: api
feature_id: foundation-docs
workorder_id: foundation-docs-001
task: Generate foundation documentation
agent: Claude Code AI
_uds:
  validation_score: 95
  validated_at: "2026-01-14T01:20:46Z"
  validator: UDSValidator
---

# API Reference

**[Date]** 2026-01-14 | **[Version]** 2.0.0

## Purpose

This document provides complete API reference for all MCP tools exposed by the CodeRef Context server. Each tool enables AI agents to query and analyze code intelligence from pre-scanned `.coderef/` data.

## Overview

The CodeRef Context MCP server exposes 14 tools organized into categories:
- **Discovery**: Scan and discover code elements
- **Query**: Query relationships and dependencies
- **Analysis**: Impact, complexity, patterns, coverage
- **Generation**: Context, diagrams, exports
- **Validation**: Reference validation and drift detection
- **Modification**: Tag source files (requires CLI)

All tools are read-only except `coderef_tag` which modifies source files.

## Authentication

No authentication required. MCP server runs via stdio and handles requests from configured MCP clients.

## Base URL

MCP tools are accessed via stdio protocol. Configure in MCP client settings:
```
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

## Endpoints

### 1. coderef_scan

**Description**: Scan project and discover all code elements (functions, classes, components, hooks)

**Request**:
```json
{
  "name": "coderef_scan",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "languages": ["ts", "tsx", "js", "jsx"],
    "use_ast": true
  }
}
```

**Parameters**:
- `project_path` (required, string): Absolute path to project root
- `languages` (optional, array): Languages to scan (default: `["ts", "tsx", "js", "jsx"]`)
- `use_ast` (optional, boolean): Use AST-based analysis vs regex (default: `true`)

**Response**:
```json
{
  "success": true,
  "elements_found": 250,
  "elements": [
    {
      "type": "function",
      "name": "export_coderef",
      "file": "processors/export_processor.py",
      "line": 26,
      "exported": false
    }
  ],
  "source": "file://.coderef/index.json"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "No scan data found. Run scan first to create .coderef/ directory.",
  "hint": "Use dashboard scanner or run: python scripts/populate-coderef.py /path/to/project"
}
```

---

### 2. coderef_query

**Description**: Query code relationships (what-calls, what-imports, shortest-path, etc)

**Request**:
```json
{
  "name": "coderef_query",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "query_type": "calls",
    "target": "authenticateUser",
    "source": "loginHandler",
    "max_depth": 3
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `query_type` (required, enum): Relationship type
  - `"calls"` - What does target call?
  - `"calls-me"` - What calls target?
  - `"imports"` - What does target import?
  - `"imports-me"` - What imports target?
  - `"depends-on"` - What does target depend on?
  - `"depends-on-me"` - What depends on target?
- `target` (required, string): Element to query (e.g., `"authenticateUser"` or `"AuthService#login"`)
- `source` (optional, string): For path queries: starting element
- `max_depth` (optional, integer): Maximum traversal depth (default: `3`)

**Response**:
```json
{
  "success": true,
  "query_type": "calls",
  "target": "authenticateUser",
  "results": ["validateToken", "checkPermissions"],
  "element": {
    "name": "authenticateUser",
    "type": "function",
    "file": "src/auth.ts"
  }
}
```

---

### 3. coderef_impact

**Description**: Analyze impact of modifying or deleting a code element

**Request**:
```json
{
  "name": "coderef_impact",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "element": "AuthService",
    "operation": "modify",
    "max_depth": 3
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `element` (required, string): Element to analyze (e.g., `"AuthService"`)
- `operation` (optional, enum): Type of change (default: `"modify"`)
  - `"modify"` - Impact of modification
  - `"delete"` - Impact of deletion
  - `"refactor"` - Impact of refactoring
- `max_depth` (optional, integer): Maximum traversal depth (default: `3`)

**Response**:
```json
{
  "success": true,
  "element": "AuthService",
  "operation": "modify",
  "affected_elements": ["UserController", "AdminController"],
  "impact_level": "high"
}
```

---

### 4. coderef_complexity

**Description**: Get complexity metrics for a code element

**Request**:
```json
{
  "name": "coderef_complexity",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "element": "processPayment"
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `element` (required, string): Element to analyze

**Response**:
```json
{
  "success": true,
  "element": "processPayment",
  "complexity": {
    "cyclomatic": 12,
    "cognitive": 8,
    "lines_of_code": 45
  }
}
```

---

### 5. coderef_patterns

**Description**: Discover code patterns and test coverage gaps

**Request**:
```json
{
  "name": "coderef_patterns",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "pattern_type": "singleton",
    "limit": 10
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `pattern_type` (optional, string): Type of pattern to find
- `limit` (optional, integer): Maximum results (default: `10`)

**Response**:
```json
{
  "success": true,
  "patterns": [
    {
      "type": "singleton",
      "count": 5,
      "files": ["src/config.ts", "src/logger.ts"]
    }
  ],
  "test_gaps": ["src/auth.ts", "src/payment.ts"]
}
```

---

### 6. coderef_coverage

**Description**: Analyze test coverage in the codebase

**Request**:
```json
{
  "name": "coderef_coverage",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "format": "summary"
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `format` (optional, enum): Coverage report format (default: `"summary"`)
  - `"summary"` - High-level coverage stats
  - `"detailed"` - Per-file coverage breakdown

**Response**:
```json
{
  "success": true,
  "coverage": {
    "overall": 0.75,
    "by_file": {
      "src/auth.ts": 0.90,
      "src/payment.ts": 0.60
    }
  }
}
```

---

### 7. coderef_context

**Description**: Generate comprehensive codebase context (markdown + JSON)

**Request**:
```json
{
  "name": "coderef_context",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "languages": ["ts", "tsx"],
    "output_format": "both"
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `languages` (optional, array): Languages to scan (default: `["ts", "tsx", "js", "jsx"]`)
- `output_format` (optional, enum): Output format (default: `"json"`)
  - `"json"` - JSON format
  - `"markdown"` - Markdown format
  - `"both"` - Both formats

**Response**:
```json
{
  "success": true,
  "context": {
    "json": {...},
    "markdown": "# Codebase Context\n\n..."
  }
}
```

---

### 8. coderef_validate

**Description**: Validate CodeRef2 references in codebase

**Request**:
```json
{
  "name": "coderef_validate",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "pattern": "**/*.ts"
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `pattern` (optional, string): File glob pattern (default: `"**/*.ts"`)

**Response**:
```json
{
  "success": true,
  "valid": true,
  "errors": [],
  "warnings": []
}
```

---

### 9. coderef_drift

**Description**: Detect drift between CodeRef index and current code

**Request**:
```json
{
  "name": "coderef_drift",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "index_path": ".coderef-index.json"
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `index_path` (optional, string): Path to coderef-index.json (default: `".coderef-index.json"`)

**Response**:
```json
{
  "success": true,
  "drift_detected": true,
  "changed_files": ["src/auth.ts", "src/payment.ts"],
  "new_files": ["src/new-feature.ts"]
}
```

---

### 10. coderef_incremental_scan

**Description**: Perform incremental scan (only re-scan files with detected drift, merge with existing index)

**Request**:
```json
{
  "name": "coderef_incremental_scan",
  "arguments": {
    "project_path": "/absolute/path/to/project"
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root

**Response**:
```json
{
  "success": true,
  "files_scanned": 5,
  "elements_added": 12,
  "elements_updated": 3
}
```

---

### 11. coderef_diagram

**Description**: Generate visual dependency diagrams (Mermaid or Graphviz)

**Request**:
```json
{
  "name": "coderef_diagram",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "diagram_type": "dependencies",
    "format": "mermaid",
    "depth": 2
  }
}
```

**Parameters**:
- `project_path` (required, string): Project root
- `diagram_type` (optional, enum): Type of diagram (default: `"dependencies"`)
  - `"dependencies"` - Dependency graph
  - `"calls"` - Call graph
  - `"imports"` - Import graph
  - `"all"` - Combined graph
- `format` (optional, enum): Output format (default: `"mermaid"`)
  - `"mermaid"` - Mermaid diagram syntax
  - `"dot"` - Graphviz DOT format
- `depth` (optional, integer): Maximum depth (default: `2`)

**Response**:
```json
{
  "success": true,
  "diagram": "graph TD\n    A[AuthService] --> B[UserController]\n    ...",
  "format": "mermaid"
}
```

---

### 12. coderef_tag

**Description**: Add CodeRef2 tags to source files for better tracking and validation

**Request**:
```json
{
  "name": "coderef_tag",
  "arguments": {
    "path": "src/auth.ts",
    "dry_run": false,
    "force": false,
    "verbose": false,
    "update_lineno": false,
    "include_private": false,
    "lang": "ts,tsx,js,jsx",
    "exclude": "node_modules"
  }
}
```

**Parameters**:
- `path` (required, string): File or directory path to tag
- `dry_run` (optional, boolean): Preview changes without writing (default: `false`)
- `force` (optional, boolean): Force update existing tags (default: `false`)
- `verbose` (optional, boolean): Show detailed output (default: `false`)
- `update_lineno` (optional, boolean): Update line numbers in existing tags (default: `false`)
- `include_private` (optional, boolean): Include private elements (default: `false`)
- `lang` (optional, string): File extensions to process (default: `"ts,tsx,js,jsx"`)
- `exclude` (optional, string): Exclusion patterns (comma-separated)

**Response**:
```json
{
  "success": true,
  "files_tagged": 5,
  "tags_added": 23
}
```

**Note**: This tool modifies source files. Requires CLI integration.

---

### 13. coderef_export

**Description**: Export coderef data in various formats (JSON, JSON-LD, Mermaid, DOT)

**Request**:
```json
{
  "name": "coderef_export",
  "arguments": {
    "project_path": "/absolute/path/to/project",
    "format": "json",
    "output_path": ".coderef/exports/graph.json",
    "max_nodes": 1000
  }
}
```

**Parameters**:
- `project_path` (required, string): Absolute path to project root
- `format` (required, enum): Export format
  - `"json"` - Raw JSON data
  - `"jsonld"` - JSON-LD (Linked Data)
  - `"mermaid"` - Mermaid diagram
  - `"dot"` - Graphviz DOT format
- `output_path` (optional, string): Custom output file path
- `max_nodes` (optional, integer): Limit on graph nodes (for large codebases)

**Response**:
```json
{
  "success": true,
  "format": "json",
  "output_path": ".coderef/exports/graph.json",
  "nodes_exported": 250
}
```

---

### 14. validate_coderef_outputs

**Description**: Validate `.coderef/` files against schemas using Papertrail MCP validation

**Request**:
```json
{
  "name": "validate_coderef_outputs",
  "arguments": {
    "project_path": "/absolute/path/to/project"
  }
}
```

**Parameters**:
- `project_path` (required, string): Absolute path to project root

**Response**:
```json
{
  "success": true,
  "valid": true,
  "files_validated": ["index.json", "graph.json", "context.json"],
  "errors": [],
  "warnings": []
}
```

---

## Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common error scenarios:
- **Missing scan data**: `.coderef/` directory not found or incomplete
- **Invalid parameters**: Required parameters missing or invalid values
- **File system errors**: Permission issues or corrupted files
- **JSON parsing errors**: Corrupted `.coderef/` JSON files

## Rate Limits

No rate limits enforced. Tools read from local filesystem, so performance is limited only by disk I/O.

## Pagination

Not applicable. All tools return complete results. For large codebases, use `max_depth` or `limit` parameters to constrain results.

## Examples

### cURL Equivalent (Conceptual)

Since MCP uses stdio protocol, here's a conceptual example:

```bash
# Scan codebase
echo '{"name":"coderef_scan","arguments":{"project_path":"/path/to/project"}}' | python server.py

# Query relationships
echo '{"name":"coderef_query","arguments":{"project_path":"/path/to/project","query_type":"calls","target":"authenticateUser"}}' | python server.py
```

### Error Response Example

```json
{
  "success": false,
  "error": "No scan data found. Run scan first to create .coderef/ directory.",
  "hint": "Use dashboard scanner or run: python scripts/populate-coderef.py /path/to/project"
}
```

---

**AI Agent Note**: All tools are read-only except `coderef_tag`. Tools return JSON responses via MCP TextContent format. For integration examples, see [ARCHITECTURE.md](ARCHITECTURE.md).
