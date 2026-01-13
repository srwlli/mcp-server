# CodeRef-Context MCP Tools - Quick Reference

**Version:** 2.0.0
**Total Tools:** 13
**Last Updated:** 2026-01-13

## Tool Categories

- **Scan & Discovery** (2 tools) - Get code elements and perform scans
- **Query & Relationships** (2 tools) - Query dependencies and relationships
- **Analysis** (3 tools) - Analyze impact, complexity, and patterns
- **Validation & Drift** (3 tools) - Validate references and detect drift
- **Export & Visualization** (3 tools) - Export data and generate diagrams

---

## Scan & Discovery

### coderef_scan
**Purpose:** Get all scanned code elements from index.json (optionally include live Python scan)

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "include_python": false                  // Optional: Run live Python AST scan
}
```

**Example:**
```python
result = await call_tool("coderef_scan", {
    "project_path": "C:/projects/myapp",
    "include_python": true
})
# Returns: {"success": true, "elements_found": 208, "elements": [...]}
```

**Returns:** Array of elements with name, type, file, line, language

---

### coderef_incremental_scan
**Purpose:** Detect changed files via drift and recommend incremental re-scan (10x+ faster)

**Parameters:**
```json
{
  "project_path": "/path/to/project"      // Required
}
```

**Example:**
```python
result = await call_tool("coderef_incremental_scan", {
    "project_path": "C:/projects/myapp"
})
# Returns: {"drift_detected": true, "changed_files": ["src/auth.py"], "cli_command": "..."}
```

**Returns:** Drift status, changed files list, CLI command to re-scan

---

## Query & Relationships

### coderef_query
**Purpose:** Query code relationships (what-calls, what-imports, depends-on)

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "query_type": "depends-on-me",          // Required: calls, calls-me, imports, imports-me, depends-on, depends-on-me
  "target": "AuthService",                // Required: Element to query
  "max_depth": 3                          // Optional: Traversal depth (default: 3)
}
```

**Example:**
```python
result = await call_tool("coderef_query", {
    "project_path": "C:/projects/myapp",
    "query_type": "depends-on-me",
    "target": "AuthService"
})
# Returns: {"target": "AuthService", "results": ["UserController", "LoginHandler"]}
```

**Returns:** Target element and array of related elements

---

### coderef_impact
**Purpose:** Analyze impact of modifying/deleting a code element

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "element": "AuthService",               // Required: Element to analyze
  "operation": "modify",                  // Optional: modify, delete, refactor (default: modify)
  "max_depth": 3                          // Optional: Traversal depth (default: 3)
}
```

**Example:**
```python
result = await call_tool("coderef_impact", {
    "project_path": "C:/projects/myapp",
    "element": "AuthService",
    "operation": "refactor"
})
# Returns: {"risk_level": "MEDIUM", "direct_dependents": 3, "dependents": [...]}
```

**Returns:** Risk level, dependents count, affected elements

---

## Analysis

### coderef_complexity
**Purpose:** Get complexity metrics for a code element

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "element": "processPayment"             // Required: Element to analyze
}
```

**Example:**
```python
result = await call_tool("coderef_complexity", {
    "project_path": "C:/projects/myapp",
    "element": "processPayment"
})
# Returns: {"element": "processPayment", "parameters": 5, "complexity": "high"}
```

**Returns:** Element name, parameter count, complexity estimate

---

### coderef_patterns
**Purpose:** Discover code patterns (handlers, decorators, common structures)

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "pattern_type": "handlers",             // Optional: Specific pattern type
  "limit": 10                             // Optional: Max results (default: 10)
}
```

**Example:**
```python
result = await call_tool("coderef_patterns", {
    "project_path": "C:/projects/myapp",
    "limit": 20
})
# Returns: {"handlers": [...], "decorators": [...], "common_patterns": [...]}
```

**Returns:** Categorized patterns found in codebase

---

### coderef_coverage
**Purpose:** Analyze test coverage gaps

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "format": "summary"                     // Optional: summary, detailed (default: summary)
}
```

**Example:**
```python
result = await call_tool("coderef_coverage", {
    "project_path": "C:/projects/myapp",
    "format": "detailed"
})
# Returns: {"coverage_percentage": 73, "uncovered_elements": [...]}
```

**Returns:** Coverage stats and uncovered elements

---

## Validation & Drift

### coderef_validate
**Purpose:** Validate CodeRef2 references in codebase

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "pattern": "**/*.ts"                    // Optional: File glob pattern (default: **/*.ts)
}
```

**Example:**
```python
result = await call_tool("coderef_validate", {
    "project_path": "C:/projects/myapp",
    "pattern": "src/**/*.py"
})
# Returns: {"valid_refs": 45, "invalid_refs": 2, "errors": [...]}
```

**Returns:** Validation counts and error details

---

### coderef_drift
**Purpose:** Detect drift between index and current code

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "index_path": ".coderef-index.json"     // Optional: Path to index (default: .coderef-index.json)
}
```

**Example:**
```python
result = await call_tool("coderef_drift", {
    "project_path": "C:/projects/myapp"
})
# Returns: {"drift_percentage": 8.5, "changes": {"added": [...], "modified": [...], "removed": [...]}}
```

**Returns:** Drift report with added/modified/removed elements

---

### coderef_context
**Purpose:** Get comprehensive codebase context (markdown or JSON)

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "output_format": "json",                // Optional: json, markdown, both (default: json)
  "languages": ["ts", "tsx", "js", "jsx"] // Optional: Languages to include
}
```

**Example:**
```python
result = await call_tool("coderef_context", {
    "project_path": "C:/projects/myapp",
    "output_format": "markdown"
})
# Returns: Markdown-formatted project overview
```

**Returns:** Project context in requested format

---

## Export & Visualization

### coderef_diagram
**Purpose:** Generate visual dependency diagrams (Mermaid or Graphviz DOT)

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "diagram_type": "dependencies",         // Optional: dependencies, calls, imports, all (default: dependencies)
  "format": "mermaid",                    // Optional: mermaid, dot (default: mermaid)
  "depth": 2                              // Optional: Max depth (default: 2)
}
```

**Example:**
```python
result = await call_tool("coderef_diagram", {
    "project_path": "C:/projects/myapp",
    "diagram_type": "dependencies",
    "format": "mermaid"
})
# Returns: Mermaid graph syntax (embeddable in Markdown)
```

**Returns:** Diagram in requested format

---

### coderef_export
**Purpose:** Export coderef data in various formats (JSON, JSON-LD, Mermaid, DOT)

**Parameters:**
```json
{
  "project_path": "/path/to/project",     // Required
  "format": "json",                       // Required: json, jsonld, mermaid, dot
  "output_path": "/path/to/output",       // Optional: Output file path
  "max_nodes": 1000                       // Optional: Limit graph nodes for large codebases
}
```

**Example:**
```python
result = await call_tool("coderef_export", {
    "project_path": "C:/projects/myapp",
    "format": "jsonld"
})
# Returns: {"success": true, "format": "jsonld", "data": {...}}
```

**Returns:** Exported data in requested format

---

### coderef_tag
**Purpose:** Add CodeRef2 tags to source files (requires CLI - not supported in read-only MCP)

**Parameters:**
```json
{
  "path": "/path/to/file"                 // Required
}
```

**Example:**
```python
result = await call_tool("coderef_tag", {
    "path": "C:/projects/myapp/src/auth.py"
})
# Returns: {"success": false, "error": "Tag operation requires CLI (modifies files)"}
```

**Returns:** Error message (tagging requires external CLI)

---

## Common Workflows

### Workflow 1: Planning a Feature
```python
# Step 1: Get inventory
scan = await call_tool("coderef_scan", {"project_path": "/path", "include_python": true})

# Step 2: Find existing patterns
patterns = await call_tool("coderef_patterns", {"project_path": "/path"})

# Step 3: Check impact of changes
impact = await call_tool("coderef_impact", {
    "project_path": "/path",
    "element": "AuthService",
    "operation": "refactor"
})
```

### Workflow 2: Generating Documentation
```python
# Step 1: Get all elements
scan = await call_tool("coderef_scan", {"project_path": "/path"})

# Step 2: Get dependency diagram
diagram = await call_tool("coderef_diagram", {
    "project_path": "/path",
    "diagram_type": "dependencies",
    "format": "mermaid"
})

# Step 3: Get context overview
context = await call_tool("coderef_context", {
    "project_path": "/path",
    "output_format": "markdown"
})
```

### Workflow 3: Incremental Updates
```python
# Step 1: Check for drift
drift = await call_tool("coderef_drift", {"project_path": "/path"})

# Step 2: If drift detected, get changed files
if drift["drift_percentage"] > 5:
    incremental = await call_tool("coderef_incremental_scan", {"project_path": "/path"})

    # Step 3: Re-scan only changed files (via CLI command returned)
    # Run: incremental["cli_command"]
```

---

## Error Handling

All tools return a consistent error format:

```json
{
  "success": false,
  "error": "Error message",
  "hint": "Suggestion to fix (e.g., 'Run: coderef scan /path')"
}
```

Common errors:
- **Missing .coderef/ directory**: Run `coderef scan /path` or `python scripts/populate-coderef.py /path`
- **File not found**: Specific report/diagram not generated - re-run full scan
- **Invalid parameters**: Check required parameters above

---

## Performance Notes

- **coderef_scan (with include_python)**: 100-500ms for live Python scan
- **coderef_incremental_scan**: 10-100x faster than full re-scan (depends on drift %)
- **Read-only operations**: 3-10ms average (direct file reads)
- **Export operations**: 50-200ms (depends on project size)

---

## Related Documentation

- **SCHEMA.md** - Complete .coderef/ file format reference
- **INTEGRATION.md** - Integration examples with coderef-docs
- **README.md** - Full MCP server documentation
- **ARCHITECTURE.md** - Server architecture details
