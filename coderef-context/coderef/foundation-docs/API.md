# API Documentation

**Project:** coderef-context MCP Server
**Version:** 1.1.0
**Last Updated:** 2025-12-30
**Status:** ✅ Production

---

## Purpose

This document describes the MCP (Model Context Protocol) API exposed by the coderef-context server. It provides 11 tools that enable AI agents to understand code structure, dependencies, relationships, impact of changes, complexity metrics, patterns, and test coverage through the @coderef/core CLI.

---

## Overview

The coderef-context server exposes code intelligence tools via the MCP protocol (JSON-RPC 2.0). Each tool wraps a @coderef/core CLI command and returns structured JSON responses suitable for agent consumption.

**Base Protocol:** MCP (Model Context Protocol) over stdio
**Architecture:** Python MCP server → Node.js subprocess (@coderef/core CLI) → JSON response
**Transport:** Standard I/O (stdin/stdout)
**Authentication:** None (local server, trusted environment)

---

## What: API Endpoints

### 1. coderef_scan

**Purpose:** Discover all code elements (functions, classes, components, hooks)

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "languages": ["string"] (optional, default: ["ts", "tsx", "js", "jsx"]),
  "use_ast": "boolean" (optional, default: true)
}
```

**Response:**
```json
{
  "success": true,
  "elements_found": 247,
  "elements": [
    {
      "name": "ThemeProvider",
      "type": "component",
      "file": "src/theme/ThemeProvider.tsx",
      "line": 10
    }
  ]
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef scan <project_path> --lang <langs> --json [--ast]`

---

### 2. coderef_query

**Purpose:** Query code relationships (what-calls, what-imports, shortest-path, etc)

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "query_type": "enum (required)" // calls, calls-me, imports, imports-me, depends-on, depends-on-me
  "target": "string (required)", // e.g., 'authenticateUser' or 'AuthService#login'
  "source": "string (optional)", // For path queries
  "max_depth": "integer (optional, default: 3)"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "calls-me",
  "target": "login",
  "results": [
    {
      "from": "CheckoutComponent",
      "to": "PaymentGateway",
      "type": "import",
      "file": "src/checkout/Checkout.tsx"
    }
  ]
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef query <target> --type <type> --depth <depth> --format json`

---

### 3. coderef_impact

**Purpose:** Analyze impact of modifying or deleting a code element

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "element": "string (required)", // e.g., 'AuthService'
  "operation": "enum (optional, default: modify)", // modify, delete, refactor
  "max_depth": "integer (optional, default: 3)"
}
```

**Response:**
```json
{
  "success": true,
  "element": "AuthService",
  "operation": "refactor",
  "impact": {
    "affected_files": 12,
    "risk_level": "MEDIUM",
    "ripple_effects": [
      {
        "file": "src/login/Login.tsx",
        "impact": "direct call"
      }
    ]
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef impact <element> --depth <depth> --format json`

---

### 4. coderef_complexity

**Purpose:** Get complexity metrics for a code element

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "element": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "element": "ReportGenerator",
  "note": "Complexity metrics derived from context generation",
  "context": {
    "lines_of_code": 245,
    "cyclomatic_complexity": 8,
    "dependencies": 6,
    "test_coverage": 0.65
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef context <project_path> --lang <langs> --json` (filtered by element)

---

### 5. coderef_patterns

**Purpose:** Discover code patterns and test coverage gaps

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "pattern_type": "string (optional)", // Type of pattern to find
  "limit": "integer (optional, default: 10)"
}
```

**Response:**
```json
{
  "success": true,
  "pattern_type": "data-fetching",
  "limit": 5,
  "patterns": {
    "React Query pattern": {
      "files": ["src/api/hooks.ts"],
      "usage": 23
    }
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef context <project_path> --lang <langs> --json` (extracts test patterns)

---

### 6. coderef_coverage

**Purpose:** Analyze test coverage in the codebase

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "format": "enum (optional, default: summary)" // summary, detailed
}
```

**Response:**
```json
{
  "success": true,
  "coverage": {
    "overall": 0.72,
    "by_file": {
      "src/auth.ts": 0.85,
      "src/checkout.ts": 0.60
    }
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef coverage --format json`

---

### 7. coderef_context

**Purpose:** Generate comprehensive codebase context (markdown + JSON)

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "languages": ["string"] (optional, default: ["ts", "tsx", "js", "jsx"]),
  "output_format": "enum (optional, default: json)" // json, markdown, both
}
```

**Response:**
```json
{
  "success": true,
  "format": "json",
  "context": {
    "project_summary": "...",
    "elements": [...],
    "dependencies": {...},
    "test_patterns": {...}
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef context <project_path> --lang <langs>`

---

### 8. coderef_validate

**Purpose:** Validate CodeRef2 references in codebase

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "pattern": "string (optional, default: **/*.ts)" // File glob pattern
}
```

**Response:**
```json
{
  "success": true,
  "pattern": "**/*.ts",
  "validation": {
    "valid_references": 120,
    "invalid_references": 3,
    "errors": [...]
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef validate <project_path> --pattern <pattern> --format json`

---

### 9. coderef_drift

**Purpose:** Detect drift between CodeRef index and current code

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "index_path": "string (optional, default: .coderef-index.json)"
}
```

**Response:**
```json
{
  "success": true,
  "drift_report": {
    "added_elements": 5,
    "removed_elements": 2,
    "modified_elements": 8
  }
}
```

**Timeout:** 120 seconds
**CLI Command:** `coderef drift <project_path> --index <index_path> --format json`

---

### 10. coderef_diagram

**Purpose:** Generate visual dependency diagrams (Mermaid or Graphviz)

**Input Schema:**
```json
{
  "project_path": "string (required)",
  "diagram_type": "enum (optional, default: dependencies)", // dependencies, calls, imports, all
  "format": "enum (optional, default: mermaid)", // mermaid, dot
  "depth": "integer (optional, default: 2)"
}
```

**Response:**
```
graph TD
  A[AuthService] --> B[LoginComponent]
  A --> C[ProfileComponent]
```

**Timeout:** 120 seconds
**CLI Command:** `coderef diagram --format <format> --depth <depth>`

---

### 11. coderef_tag

**Purpose:** Add CodeRef2 tags to source files for better tracking and validation

**Input Schema:**
```json
{
  "path": "string (required)", // File or directory path
  "dry_run": "boolean (optional, default: false)",
  "force": "boolean (optional, default: false)",
  "verbose": "boolean (optional, default: false)",
  "update_lineno": "boolean (optional, default: false)",
  "include_private": "boolean (optional, default: false)",
  "lang": "string (optional, default: ts,tsx,js,jsx)",
  "exclude": "string (optional)" // Comma-separated exclusion patterns
}
```

**Response:**
```
Tagged 45 elements in 12 files:
- 18 functions (@Fn)
- 12 classes (@Cl)
- 15 components (@Cp)
```

**Timeout:** 120 seconds
**CLI Command:** `coderef tag <path> [options]`

---

## Why: Use Cases

### UC-1: Discovery (scan)
**Scenario:** Agent needs to understand what exists in a project before implementing a new feature.

**Example:**
```json
Request: {"tool": "coderef_scan", "args": {"project_path": "/path/to/app"}}
Response: {"success": true, "elements_found": 247, "elements": [...]}
Agent Decision: "ThemeProvider exists, I'll extend it instead of creating a new one"
```

### UC-2: Dependency Tracing (query)
**Scenario:** Agent wants to know what depends on a function before refactoring.

**Example:**
```json
Request: {"tool": "coderef_query", "args": {"query_type": "calls-me", "target": "login"}}
Response: {"results": ["signup.ts", "profile.ts", "dashboard.ts"]}
Agent Decision: "3 files call login(), I need to update all of them"
```

### UC-3: Risk Assessment (impact)
**Scenario:** Agent evaluates the risk of deleting a service.

**Example:**
```json
Request: {"tool": "coderef_impact", "args": {"element": "AuthService", "operation": "delete"}}
Response: {"affected_files": 12, "risk_level": "MEDIUM"}
Agent Decision: "12 files affected, this is risky. I'll create a comprehensive plan first."
```

---

## When: Integration Points

### Integration with coderef-workflow
The coderef-workflow server calls coderef_scan, coderef_query, and coderef_impact during the planning phase (section 0: PREPARATION) to gather project intelligence before creating implementation plans.

### Integration with coderef-personas
Expert personas (Ava, Marcus, Quinn, etc.) call coderef_query and coderef_impact tools during task execution to make informed decisions about code changes.

### Integration with coderef-docs
The coderef-docs server may call coderef_scan to extract real API endpoints, components, and schemas when generating foundation documentation.

---

## Examples

### Example 1: Scan a Project
**Request:**
```bash
# MCP Tool Call (internal)
{
  "tool": "coderef_scan",
  "arguments": {
    "project_path": "/Users/dev/frontend-app",
    "languages": ["ts", "tsx"],
    "use_ast": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "elements_found": 247,
  "elements": [
    {
      "name": "ThemeProvider",
      "type": "component",
      "file": "src/theme/ThemeProvider.tsx",
      "line": 10
    },
    {
      "name": "useTheme",
      "type": "hook",
      "file": "src/theme/useTheme.ts",
      "line": 5
    }
  ]
}
```

---

### Example 2: Query Dependencies
**Request:**
```bash
# MCP Tool Call (internal)
{
  "tool": "coderef_query",
  "arguments": {
    "project_path": "/Users/dev/checkout-app",
    "query_type": "imports",
    "target": "CheckoutComponent"
  }
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "imports",
  "target": "CheckoutComponent",
  "results": [
    {
      "from": "CheckoutComponent",
      "to": "PaymentGateway",
      "type": "import",
      "file": "src/checkout/Checkout.tsx"
    }
  ]
}
```

---

### Example 3: Assess Impact
**Request:**
```bash
# MCP Tool Call (internal)
{
  "tool": "coderef_impact",
  "arguments": {
    "project_path": "/Users/dev/app",
    "element": "AuthService",
    "operation": "refactor"
  }
}
```

**Response:**
```json
{
  "success": true,
  "element": "AuthService",
  "operation": "refactor",
  "impact": {
    "affected_files": 12,
    "risk_level": "MEDIUM",
    "ripple_effects": [
      {
        "file": "src/login/Login.tsx",
        "impact": "direct call"
      }
    ]
  }
}
```

---

## Error Handling

### Timeout Errors
All tools have a 120-second timeout. If the CLI command exceeds this:

```json
{
  "error": "Error: Scan timeout (120s exceeded)"
}
```

**Solution:** Use smaller scope, disable AST analysis (use_ast=false), or increase timeout.

---

### CLI Not Found Errors
If the @coderef/core CLI is not installed or configured:

```json
{
  "error": "Error: CLI path not found"
}
```

**Solution:** Set CODEREF_CLI_PATH environment variable or install @coderef/core globally.

---

### JSON Parse Errors
If CLI output is malformed:

```json
{
  "error": "JSON parse error: Unexpected token"
}
```

**Solution:** Check CLI version compatibility, verify CLI works standalone.

---

## Rate Limits & Performance

**Rate Limits:** None (local server, no network)
**Concurrency:** Unlimited (each tool call spawns independent subprocess)
**Caching:** None (fresh analysis on each call for accuracy)

**Performance Benchmarks:**
- `coderef_scan`: ~5-15s for 50k LOC project (AST mode)
- `coderef_query`: ~1-3s for dependency lookup
- `coderef_impact`: ~2-5s for impact analysis
- `coderef_context`: ~10-30s for full project context

---

## References

- **[CLAUDE.md](../CLAUDE.md)** - AI context documentation with architecture details
- **[README.md](../README.md)** - User-facing overview
- **[server.py](../server.py)** - MCP server implementation
- **[@coderef/core](https://github.com/coderef-system)** - Upstream TypeScript analysis engine

---

## AI Agent Instructions

**When using this API:**
1. Always call `coderef_scan` first to understand what exists before implementing
2. Use `coderef_query` to trace dependencies before refactoring
3. Call `coderef_impact` to assess risk before making breaking changes
4. Leverage `coderef_complexity` for effort estimation
5. Check `coderef_patterns` to discover existing code patterns (avoid reimplementation)

**Error handling:**
- Retry once on timeout errors (may be temporary)
- If CLI not found, ask user to configure CODEREF_CLI_PATH
- Parse JSON carefully (skip CLI progress messages before JSON)

**Best practices:**
- Use AST analysis (use_ast=true) for 99% accuracy
- Set appropriate max_depth (3 is usually sufficient)
- Combine tools: scan → query → impact for comprehensive understanding

---

**Generated:** 2025-12-30
**Maintained by:** coderef-context MCP Server
**For AI Agents:** This API enables code intelligence during implementation. Use it to avoid blind coding.
