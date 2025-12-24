# coderef-context MCP Tools Reference

**MCP Server Version:** 1.0.0
**CLI Tools Wrapped:** 14 @coderef/cli commands
**Date:** 2025-12-24

---

## Overview

The `coderef-context` MCP server exposes 10 primary tools that wrap @coderef/cli commands, providing agents with real-time code intelligence during implementation tasks.

All tools return JSON responses with a `success` flag and structured data for parsing.

---

## Core Analysis Tools

### 1. `coderef_scan`

**Purpose:** Discover all code elements in a project.

**Description:**
Scans a project directory and returns all discovered code elements (functions, classes, methods, interfaces, enums, constants, types, etc.) with their locations and metadata.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to scan (required)
  "languages": string[];?;       // Languages to scan (default: ["ts", "tsx", "js", "jsx"])
  "use_ast": boolean?;           // Use AST-based analysis (default: false)
}
```

**Output Schema:**
```json
{
  "success": true,
  "elements_found": 1021,
  "elements": [
    {
      "type": "function",
      "name": "authenticate",
      "file": "/path/to/auth.ts",
      "line": 24,
      "exported": true
    }
  ]
}
```

**Use Cases:**
- Initial project understanding
- Element inventory
- API surface discovery

**Performance:**
- Regex mode: <1s for 1000 elements
- AST mode: 1-3s for 1000 elements (99% accuracy)

**Timeout:** 30s

---

### 2. `coderef_query`

**Purpose:** Query relationships between code elements.

**Description:**
Traverses the dependency graph to answer questions about how code elements relate to each other.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "query_type": string;          // Query type (required)
  "target": string;              // Element to query (required)
  "max_depth": number?;          // Traversal depth (default: 3)
}
```

**Query Types:**
- `calls` - What does this element call?
- `calls-me` - What calls this element?
- `imports` - What does this import?
- `imports-me` - What imports this?
- `depends-on` - What does this depend on?
- `depends-on-me` - What depends on this? (default)
- `shortest-path` - Shortest path to target
- `all-paths` - All paths to target

**Output Schema:**
```json
{
  "success": true,
  "query_type": "calls-me",
  "target": "authenticate",
  "results": [
    {
      "id": "login",
      "type": "function",
      "file": "/path/to/login.ts",
      "line": 42,
      "dependents": ["authenticate"]
    }
  ]
}
```

**Use Cases:**
- Understanding code flow
- Finding callers/importers
- Dependency analysis
- Tracing data flow

**Performance:**
- Cached query: <50ms
- Uncached query: 100-500ms
- Path finding: 200-1000ms depending on graph size

**Timeout:** 30s

---

### 3. `coderef_impact`

**Purpose:** Analyze the impact of changing a code element.

**Description:**
Determines what would be affected if an element is modified, deleted, or refactored. Helps assess risk before making changes.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "element": string;             // Element to analyze (required)
  "operation": string?;          // Type of operation (default: "modify")
  "max_depth": number?;          // Traversal depth (default: 3)
}
```

**Operation Types:**
- `modify` - Changing the element
- `delete` - Removing the element
- `refactor` - Restructuring the element

**Output Schema:**
```json
{
  "success": true,
  "element": "AuthService",
  "operation": "modify",
  "impact": {
    "directDependents": [
      {
        "name": "login",
        "type": "function",
        "file": "/path/to/login.ts",
        "line": 24
      }
    ],
    "transitiveImpact": [
      {
        "name": "AuthController",
        "type": "class",
        "depth": 2,
        "affectedCount": 5
      }
    ],
    "riskLevel": "CRITICAL",
    "estimatedAffected": 47,
    "testCoverage": 0.92
  }
}
```

**Use Cases:**
- Risk assessment before changes
- Effort estimation
- Finding breaking change scope
- Test impact analysis

**Performance:** <30s for typical codebases

**Timeout:** 30s

---

### 4. `coderef_complexity`

**Purpose:** Get complexity metrics for code elements.

**Description:**
Analyzes code complexity using the 6-phase context generation system. Returns metrics like cyclomatic complexity, lines of code, parameters, and nesting depth.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "element": string;             // Element to analyze (required)
}
```

**Output Schema:**
```json
{
  "success": true,
  "element": "authenticate",
  "note": "Complexity metrics derived from context generation",
  "context": {
    "phases": {
      "complexity": {
        "analyzed": 1021,
        "avgComplexity": 4.2,
        "medianLOC": 12,
        "highComplexity": 47
      }
    }
  }
}
```

**Complexity Metrics:**
- Cyclomatic complexity: 1-N (1=simple, >10=complex)
- Lines of code: Size indicator
- Parameters: API complexity
- Nesting depth: Code structure complexity

**Use Cases:**
- Effort estimation
- Finding high-risk code
- Refactoring target identification
- Code quality assessment

**Performance:** <60s

**Timeout:** 60s

---

### 5. `coderef_patterns`

**Purpose:** Discover code patterns and test coverage gaps.

**Description:**
Analyzes the codebase to identify common patterns, test coverage gaps, and anti-patterns. Helps new developers learn from existing code.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "pattern_type": string?;       // Type of pattern (default: "all")
  "limit": number?;              // Max results (default: 10)
}
```

**Output Schema:**
```json
{
  "success": true,
  "pattern_type": "all",
  "limit": 10,
  "patterns": {
    "coverage": 0.85,
    "unitTests": 234,
    "integrationTests": 45,
    "patterns": 12
  }
}
```

**Pattern Types:**
- Error handling patterns
- Null check patterns
- Guard clause patterns
- Test assertion types
- Mock usage patterns
- Best practices
- Anti-patterns

**Use Cases:**
- Learning project conventions
- Finding gaps in test coverage
- Identifying anti-patterns
- Code review preparation

**Performance:** <60s

**Timeout:** 60s

---

### 6. `coderef_coverage`

**Purpose:** Analyze test coverage across the codebase.

**Description:**
Generates a test coverage report showing which functions, classes, and modules are tested and which aren't.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "format": string?;             // Output format (default: "summary")
}
```

**Format Options:**
- `summary` - Overall percentage only
- `table` - Formatted table view
- `json` - Structured data

**Output Schema:**
```json
{
  "success": true,
  "coverage": {
    "overall": {
      "percentage": 0.85,
      "covered": 120,
      "total": 141
    },
    "modules": [
      {
        "name": "analyzer",
        "percentage": 0.85,
        "covered": 34,
        "total": 40,
        "elements": [
          {
            "name": "AnalyzerService",
            "type": "class",
            "coverage": 0.95
          }
        ]
      }
    ]
  }
}
```

**Use Cases:**
- Test gap identification
- Coverage target tracking
- Risk area identification
- Test strategy planning

**Performance:** <30s

**Timeout:** 30s

---

## Advanced Tools

### 7. `coderef_context`

**Purpose:** Generate comprehensive 6-phase context for AI agents.

**Description:**
Generates multi-phase context that prepares all code intelligence for agent consumption. This is the most comprehensive tool—it runs 6 analysis phases sequentially.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "languages": string[]?;        // Languages (default: ["ts", "tsx", "js", "jsx"])
  "output_format": string?;      // Output format (default: "json")
}
```

**6 Phases:**

1. **Phase 1: Complexity Scoring**
   - Cyclomatic complexity per element
   - Lines of code
   - Parameter count
   - Nesting depth

2. **Phase 2: Task Context Filtering**
   - Filter by complexity
   - Filter by coverage
   - Filter by file patterns
   - Keyword-based filtering

3. **Phase 3: Edge Case Detection**
   - Null/undefined checks
   - Error handling patterns
   - Try/catch blocks
   - Boundary conditions
   - Guard clauses

4. **Phase 4: Test Pattern Analysis**
   - Test file discovery
   - Coverage calculation
   - Test type classification (unit, integration, e2e)
   - Assertion pattern detection
   - Mock usage patterns

5. **Phase 5: Example Extraction**
   - Usage examples
   - Common scenarios
   - Best practices
   - Anti-pattern detection
   - Example test cases

6. **Phase 6: Agentic Formatting**
   - JSON serialization
   - Markdown formatting
   - Field prioritization
   - AI-optimized structure

**Output Schema:**
```json
{
  "success": true,
  "format": "json",
  "context": {
    "sourceDir": "./src",
    "generatedAt": "2025-12-24T12:00:00Z",
    "phases": {
      "complexity": { "analyzed": 1021, "avgComplexity": 4.2 },
      "taskContext": { "filtered": 47, "criteria": {} },
      "edgeCases": { "total": 124, "errorHandling": 89 },
      "testPatterns": { "coverage": 0.85, "unitTests": 234 },
      "examples": { "extracted": 67, "usagePatterns": 23 },
      "agenticFormat": { "ready": true, "elements": [] }
    }
  }
}
```

**Use Cases:**
- Complete project understanding before feature implementation
- Agent preparation for complex tasks
- Risk assessment before major refactoring
- Feature planning and scoping
- Performance analysis

**Performance:** 5-30s per 1000 elements

**Timeout:** 120s

---

### 8. `coderef_validate`

**Purpose:** Validate CodeRef2 reference syntax.

**Description:**
Scans a codebase for CodeRef references (like `@Fn/auth#login:24`) and validates their syntax. Helps maintain reference hygiene.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to scan (required)
  "pattern": string?;            // File glob pattern (default: "**/*.ts")
}
```

**Output Schema:**
```json
{
  "success": true,
  "pattern": "**/*.ts",
  "validation": {
    "total": 150,
    "valid": 138,
    "invalid": 12,
    "percentage": 0.92,
    "errors": [
      {
        "reference": "@ZZ/path#element",
        "file": "auth.ts",
        "line": 24,
        "error": "Invalid type designator 'ZZ'",
        "suggestions": ["Did you mean 'Fn'?"],
        "fixable": true
      }
    ]
  }
}
```

**Valid Type Designators (22 types):**
```
Fn, C, Cl, M, H, T, A, I, Cfg, Enum, Const, Type,
Service, Controller, Hook, Guard, Middleware, Schema,
Model, Provider, Resolver, Query
```

**Reference Format:**
```
@TypeDesignator/path/to/file#elementName:lineNumber{metadata}
```

**Use Cases:**
- Reference syntax enforcement
- Documentation validation
- Automated reference checking
- Pre-commit validation

**Performance:** <30s

**Timeout:** 30s

---

### 9. `coderef_drift`

**Purpose:** Detect drift between CodeRef references and actual code.

**Description:**
Compares CodeRef index with current code to find references that are stale, moved, renamed, or missing. Helps maintain reference accuracy.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to scan (required)
  "index_path": string?;         // Index file path (default: ".coderef-index.json")
}
```

**Output Schema:**
```json
{
  "success": true,
  "drift_report": [
    {
      "reference": "@Fn/auth/login#authenticate:24",
      "status": "moved",
      "oldLine": 20,
      "newLine": 24,
      "suggestion": "@Fn/auth/login#authenticate:24",
      "confidence": 1.0,
      "autoFixable": true
    },
    {
      "reference": "@Fn/auth/login#loginUser:42",
      "status": "renamed",
      "oldName": "loginUser",
      "newName": "authenticate",
      "suggestion": "@Fn/auth/login#authenticate:42",
      "confidence": 0.95,
      "autoFixable": true
    },
    {
      "reference": "@Cl/models/User#User:8",
      "status": "missing",
      "suggestion": null,
      "confidence": 0,
      "autoFixable": false
    }
  ]
}
```

**Drift Status Values:**
- `unchanged` - Reference still valid
- `moved` - Element moved to different line (auto-fixable)
- `renamed` - Element renamed (auto-fixable if confidence > threshold)
- `missing` - Element no longer exists (not fixable)
- `ambiguous` - Multiple possible matches (not fixable)

**Use Cases:**
- Reference maintenance
- Detecting code changes
- Automated reference updates
- Documentation integrity

**Performance:** <30s

**Timeout:** 30s

---

### 10. `coderef_diagram`

**Purpose:** Generate dependency diagrams in multiple formats.

**Description:**
Creates visual representations of code dependencies using various diagram formats. Helps understand architecture and dependencies.

**Input Parameters:**
```typescript
{
  "project_path": string;        // Directory to analyze (required)
  "diagram_type": string?;       // Diagram type (default: "dependencies")
  "format": string?;             // Output format (default: "mermaid")
  "depth": number?;              // Graph depth (default: 2)
}
```

**Format Options:**
- `mermaid` - Markdown-compatible diagram syntax
- `dot` - Graphviz format
- `json` - Structured data

**Output (Mermaid Format):**
```
graph TD
    A["AnalyzerService"]
    B["GraphBuilder"]
    C["CallDetector"]
    D["ImportParser"]

    A -->|uses| B
    B -->|uses| C
    B -->|uses| D
    C -->|detects| E["Calls"]
    D -->|parses| F["Imports"]
```

**Output (JSON Format):**
```json
{
  "success": true,
  "diagram": {
    "nodes": [
      {
        "id": "AnalyzerService",
        "type": "class",
        "label": "AnalyzerService"
      }
    ],
    "edges": [
      {
        "from": "AnalyzerService",
        "to": "GraphBuilder",
        "type": "uses"
      }
    ],
    "metadata": {
      "direction": "TB",
      "depth": 2
    }
  }
}
```

**Use Cases:**
- Architecture visualization
- Dependency documentation
- Communication with stakeholders
- Design review preparation
- System understanding

**Performance:** <30s

**Timeout:** 30s

---

## Quick Reference Table

| Tool | Primary Use | Input Type | Timeout | Performance |
|------|------------|-----------|---------|-------------|
| **scan** | Element discovery | project_path | 30s | <1s (regex) / 1-3s (AST) |
| **query** | Relationship analysis | element + type | 30s | <50ms cached / 100-500ms uncached |
| **impact** | Risk assessment | element | 30s | <30s |
| **complexity** | Effort estimation | element | 60s | <60s |
| **patterns** | Pattern learning | project_path | 60s | <60s |
| **coverage** | Test analysis | project_path | 30s | <30s |
| **context** | Agent preparation | project_path | 120s | 5-30s per 1000 elements |
| **validate** | Reference validation | project_path | 30s | <30s |
| **drift** | Maintenance detection | project_path | 30s | <30s |
| **diagram** | Visualization | project_path | 30s | <30s |

---

## Agent Usage Examples

### Example 1: Scan and Understand a Project

```python
# Agent scans project
scan_result = await call_tool("coderef-context", "coderef_scan", {
    "project_path": "./src",
    "languages": ["ts", "tsx"],
    "use_ast": True
})

# Response contains 1,021 elements discovered
elements = scan_result["elements"]  # Array of {type, name, file, line, exported}
```

### Example 2: Assess Impact of Change

```python
# Agent is about to modify AuthService
impact_result = await call_tool("coderef-context", "coderef_impact", {
    "project_path": "./src",
    "element": "AuthService",
    "operation": "modify",
    "max_depth": 5
})

# Response shows 47 affected elements, CRITICAL risk
risk_level = impact_result["impact"]["riskLevel"]  # "CRITICAL"
affected_count = impact_result["impact"]["estimatedAffected"]  # 47
```

### Example 3: Find All Callers

```python
# Agent needs to understand who calls authenticate()
query_result = await call_tool("coderef-context", "coderef_query", {
    "project_path": "./src",
    "target": "authenticate",
    "query_type": "calls-me",
    "max_depth": 5
})

# Response shows all functions that call authenticate()
callers = query_result["results"]  # Array of calling functions
```

### Example 4: Generate Context for Feature Implementation

```python
# Agent preparing to implement a feature
context_result = await call_tool("coderef-context", "coderef_context", {
    "project_path": "./src",
    "languages": ["ts", "tsx"],
    "output_format": "json"
})

# Response includes all 6 phases of context analysis
phases = context_result["context"]["phases"]
# Contains complexity, edge cases, test patterns, examples, etc.
```

### Example 5: Check Test Coverage

```python
# Agent wants to know what's tested
coverage_result = await call_tool("coderef-context", "coderef_coverage", {
    "project_path": "./src"
})

# Response shows coverage by module
overall_coverage = coverage_result["coverage"]["overall"]["percentage"]  # 0.85
modules = coverage_result["coverage"]["modules"]  # Breakdown by module
```

---

## Error Handling

All tools return errors in this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common errors:
- `ENOENT: no such file or directory` - Path doesn't exist
- `Permission denied` - Cannot read files
- `Timeout` - Operation exceeded time limit
- `JSON parse error` - CLI output couldn't be parsed

---

## Configuration

**MCP Server Location:**
`C:\Users\willh\.mcp-servers\coderef-context\`

**CLI Path:**
`C:\Users\willh\Desktop\projects\coderef-system\packages\cli`

**Global Registration:**
`.mcp.json` at `C:\Users\willh\.mcp.json`

---

## Related Documentation

- **README.md** - Server overview and architecture
- **IMPLEMENTATION_PLAN.md** - Implementation approach and timeline
- **CLI_SPEC.md** - Complete CLI command specifications
- **CORE_TOOLS_INVENTORY.md** - @coderef/core module inventory

---

**Version:** 1.0.0
**Last Updated:** 2025-12-24
**Status:** Production Ready ✅
