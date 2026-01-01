# Schema Documentation

**Project:** coderef-context MCP Server
**Version:** 1.1.0
**Schema Version:** 1.0
**Last Updated:** 2025-12-30
**Status:** ✅ Production

---

## Purpose

This document defines the data schemas and type definitions used by the coderef-context MCP server. It describes the structure of tool inputs, outputs, CLI responses, and internal data models used for code intelligence operations.

---

## Overview

The coderef-context server operates on structured JSON data exchanged between:
1. **MCP Client** (AI Agent) ↔ MCP Server (Python)
2. **MCP Server** (Python) ↔ CLI Subprocess (@coderef/core)

All data follows strict JSON Schema validation. No database is used—data flows entirely through in-memory JSON structures and subprocess stdio.

---

## What: Schema Definitions

### 1. Tool Input Schemas

All MCP tools accept structured JSON inputs validated against these schemas:

#### ScanInput
```typescript
interface ScanInput {
  project_path: string;           // Absolute path to project root
  languages?: string[];           // Default: ["ts", "tsx", "js", "jsx"]
  use_ast?: boolean;              // Default: true (99% accuracy vs regex)
}
```

**Validation Rules:**
- `project_path` must be absolute path
- `languages` must be valid file extensions
- `use_ast` must be boolean

**Example:**
```json
{
  "project_path": "/Users/dev/frontend-app",
  "languages": ["ts", "tsx"],
  "use_ast": true
}
```

---

#### QueryInput
```typescript
interface QueryInput {
  project_path: string;
  query_type: "calls" | "calls-me" | "imports" | "imports-me" | "depends-on" | "depends-on-me";
  target: string;                 // e.g., 'authenticateUser' or 'AuthService#login'
  source?: string;                // For path queries
  max_depth?: number;             // Default: 3
}
```

**Validation Rules:**
- `query_type` must be one of 6 enum values
- `target` is required, must be non-empty string
- `max_depth` must be positive integer 1-10

**Example:**
```json
{
  "project_path": "/Users/dev/app",
  "query_type": "calls-me",
  "target": "login",
  "max_depth": 3
}
```

---

#### ImpactInput
```typescript
interface ImpactInput {
  project_path: string;
  element: string;                // Element to analyze (e.g., 'AuthService')
  operation?: "modify" | "delete" | "refactor";  // Default: "modify"
  max_depth?: number;             // Default: 3
}
```

**Validation Rules:**
- `element` must be valid code element name
- `operation` must be one of 3 enum values
- `max_depth` must be positive integer 1-10

**Example:**
```json
{
  "project_path": "/Users/dev/app",
  "element": "AuthService",
  "operation": "refactor",
  "max_depth": 3
}
```

---

#### ComplexityInput
```typescript
interface ComplexityInput {
  project_path: string;
  element: string;                // Element to analyze
}
```

**Validation Rules:**
- `element` must be non-empty string

---

#### PatternsInput
```typescript
interface PatternsInput {
  project_path: string;
  pattern_type?: string;          // Type of pattern to find (optional)
  limit?: number;                 // Default: 10
}
```

**Validation Rules:**
- `limit` must be positive integer 1-100

---

#### CoverageInput
```typescript
interface CoverageInput {
  project_path: string;
  format?: "summary" | "detailed";  // Default: "summary"
}
```

---

#### ContextInput
```typescript
interface ContextInput {
  project_path: string;
  languages?: string[];           // Default: ["ts", "tsx", "js", "jsx"]
  output_format?: "json" | "markdown" | "both";  // Default: "json"
}
```

---

#### ValidateInput
```typescript
interface ValidateInput {
  project_path: string;
  pattern?: string;               // File glob pattern, default: "**/*.ts"
}
```

---

#### DriftInput
```typescript
interface DriftInput {
  project_path: string;
  index_path?: string;            // Default: ".coderef-index.json"
}
```

---

#### DiagramInput
```typescript
interface DiagramInput {
  project_path: string;
  diagram_type?: "dependencies" | "calls" | "imports" | "all";  // Default: "dependencies"
  format?: "mermaid" | "dot";     // Default: "mermaid"
  depth?: number;                 // Default: 2
}
```

---

#### TagInput
```typescript
interface TagInput {
  path: string;                   // File or directory path to tag
  dry_run?: boolean;              // Default: false
  force?: boolean;                // Default: false
  verbose?: boolean;              // Default: false
  update_lineno?: boolean;        // Default: false
  include_private?: boolean;      // Default: false
  lang?: string;                  // Default: "ts,tsx,js,jsx" (comma-separated)
  exclude?: string;               // Comma-separated exclusion patterns
}
```

**Validation Rules:**
- `path` is required, must be valid file or directory path
- All flags are optional booleans

---

### 2. Tool Output Schemas

All MCP tools return structured JSON responses:

#### ScanOutput
```typescript
interface ScanOutput {
  success: boolean;
  elements_found: number;
  elements: CodeElement[];
}

interface CodeElement {
  name: string;                   // Element name (e.g., "ThemeProvider")
  type: "function" | "class" | "component" | "hook" | "interface" | "type";
  file: string;                   // Relative file path
  line: number;                   // Line number where defined
  metadata?: Record<string, any>; // Additional metadata
}
```

**Example:**
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

---

#### QueryOutput
```typescript
interface QueryOutput {
  success: boolean;
  query_type: string;
  target: string;
  results: Relationship[];
}

interface Relationship {
  from: string;                   // Source element
  to: string;                     // Target element
  type: "import" | "call" | "dependency";
  file: string;                   // Where relationship exists
  line?: number;                  // Line number (optional)
}
```

**Example:**
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
      "file": "src/checkout/Checkout.tsx",
      "line": 5
    }
  ]
}
```

---

#### ImpactOutput
```typescript
interface ImpactOutput {
  success: boolean;
  element: string;
  operation: "modify" | "delete" | "refactor";
  impact: ImpactAnalysis;
}

interface ImpactAnalysis {
  affected_files: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  ripple_effects: RippleEffect[];
}

interface RippleEffect {
  file: string;                   // Affected file path
  impact: string;                 // Description (e.g., "direct call", "indirect dependency")
  severity?: "minor" | "major" | "breaking";
}
```

**Example:**
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
        "impact": "direct call",
        "severity": "major"
      }
    ]
  }
}
```

---

#### ComplexityOutput
```typescript
interface ComplexityOutput {
  success: boolean;
  element: string;
  note: string;
  context: ComplexityMetrics;
}

interface ComplexityMetrics {
  lines_of_code: number;
  cyclomatic_complexity: number;  // Measure of code paths
  dependencies: number;           // Count of imports/dependencies
  test_coverage: number;          // Decimal 0.0-1.0 (e.g., 0.65 = 65%)
}
```

**Example:**
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

---

#### PatternsOutput
```typescript
interface PatternsOutput {
  success: boolean;
  pattern_type: string;
  limit: number;
  patterns: Record<string, PatternInfo>;
}

interface PatternInfo {
  files: string[];                // Files where pattern appears
  usage: number;                  // Count of occurrences
  description?: string;           // Pattern description
}
```

**Example:**
```json
{
  "success": true,
  "pattern_type": "data-fetching",
  "limit": 5,
  "patterns": {
    "React Query pattern": {
      "files": ["src/api/hooks.ts"],
      "usage": 23,
      "description": "Async data fetching with caching"
    }
  }
}
```

---

#### CoverageOutput
```typescript
interface CoverageOutput {
  success: boolean;
  coverage: CoverageReport;
}

interface CoverageReport {
  overall: number;                // Overall coverage % (0.0-1.0)
  by_file: Record<string, number>; // Per-file coverage
  untested_files?: string[];      // Files with 0% coverage
}
```

**Example:**
```json
{
  "success": true,
  "coverage": {
    "overall": 0.72,
    "by_file": {
      "src/auth.ts": 0.85,
      "src/checkout.ts": 0.60
    },
    "untested_files": ["src/legacy.ts"]
  }
}
```

---

#### ContextOutput
```typescript
interface ContextOutput {
  success: boolean;
  format: "json" | "markdown" | "both";
  context: ProjectContext;
}

interface ProjectContext {
  project_summary: string;
  elements: CodeElement[];
  dependencies: Record<string, string[]>;
  test_patterns: Record<string, PatternInfo>;
  architecture_notes?: string;
}
```

---

#### ValidateOutput
```typescript
interface ValidateOutput {
  success: boolean;
  pattern: string;
  validation: ValidationReport;
}

interface ValidationReport {
  valid_references: number;
  invalid_references: number;
  errors: ValidationError[];
}

interface ValidationError {
  file: string;
  line: number;
  reference: string;
  error: string;
}
```

---

#### DriftOutput
```typescript
interface DriftOutput {
  success: boolean;
  drift_report: DriftReport;
}

interface DriftReport {
  added_elements: number;
  removed_elements: number;
  modified_elements: number;
  details?: DriftDetail[];
}

interface DriftDetail {
  element: string;
  change_type: "added" | "removed" | "modified";
  file: string;
}
```

---

#### DiagramOutput
```typescript
// For Mermaid/Dot formats, returns text directly
type DiagramOutput = string;

// For JSON format, returns structured graph
interface DiagramOutputJSON {
  success: boolean;
  diagram: GraphData;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface GraphNode {
  id: string;
  label: string;
  type: "function" | "class" | "component" | "module";
}

interface GraphEdge {
  from: string;
  to: string;
  label?: string;
}
```

---

#### TagOutput
```typescript
// Returns plain text output (not JSON)
type TagOutput = string;

// Example output:
// "Tagged 45 elements in 12 files:
//  - 18 functions (@Fn)
//  - 12 classes (@Cl)
//  - 15 components (@Cp)"
```

---

### 3. Error Schemas

All tools return structured errors on failure:

```typescript
interface ToolError {
  error: string;                  // Human-readable error message
  code?: string;                  // Error code (e.g., "TIMEOUT", "CLI_NOT_FOUND")
  details?: any;                  // Additional context
}
```

**Common Error Codes:**
- `TIMEOUT` - Command exceeded 120s timeout
- `CLI_NOT_FOUND` - @coderef/core CLI not installed or configured
- `JSON_PARSE_ERROR` - CLI output malformed
- `INVALID_INPUT` - Input validation failed
- `ELEMENT_NOT_FOUND` - Target element doesn't exist
- `SUBPROCESS_ERROR` - CLI subprocess crashed

**Example:**
```json
{
  "error": "Error: Scan timeout (120s exceeded)",
  "code": "TIMEOUT",
  "details": {
    "project_path": "/large/project",
    "timeout": 120
  }
}
```

---

## Why: Schema Design Decisions

### Decision 1: JSON-Only Communication
**Why:** MCP protocol is JSON-based, @coderef/core CLI supports `--json` flag
**Benefit:** Type-safe, structured, parseable by agents
**Alternative Rejected:** Plain text output (harder to parse, error-prone)

### Decision 2: Flat Input Schemas
**Why:** Simple to validate, easy for agents to construct
**Benefit:** Fewer nesting errors, clear parameter expectations
**Alternative Rejected:** Nested object parameters (more complexity)

### Decision 3: Success Boolean
**Why:** Explicit success/failure distinction
**Benefit:** Agents can check `success` before processing results
**Alternative Rejected:** HTTP-style status codes (overkill for local server)

### Decision 4: Enums for Fixed Values
**Why:** Prevents typos, provides autocomplete hints
**Benefit:** Compile-time validation, clear API contract
**Alternative Rejected:** Arbitrary strings (error-prone)

---

## When: Schema Evolution

### Versioning Strategy
Schema version follows semantic versioning (SemVer):
- **Major:** Breaking changes (remove fields, change types)
- **Minor:** Backward-compatible additions (new optional fields)
- **Patch:** Documentation updates, clarifications

### Current Version: 1.0
- All 11 tools have stable input/output schemas
- No breaking changes planned for v1.x series

### Future Schema Changes (v2.0 candidates)
- Add streaming support for large scan results
- Add pagination for query results
- Add optional caching layer with cache keys

---

## Examples

### Example 1: Valid ScanInput
```json
{
  "project_path": "/Users/dev/frontend-app",
  "languages": ["ts", "tsx"],
  "use_ast": true
}
```

**Validation:** ✅ Pass
**Reason:** All required fields present, types correct, AST flag is boolean

---

### Example 2: Invalid QueryInput (Missing target)
```json
{
  "project_path": "/Users/dev/app",
  "query_type": "calls-me"
}
```

**Validation:** ❌ Fail
**Error:** `target parameter is required`

---

### Example 3: Valid ImpactOutput
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
        "impact": "direct call",
        "severity": "major"
      }
    ]
  }
}
```

**Validation:** ✅ Pass
**Reason:** All required fields present, risk_level is valid enum

---

## Relationships & Constraints

### Schema Relationships

```
ScanInput → ScanOutput → CodeElement[]
QueryInput → QueryOutput → Relationship[]
ImpactInput → ImpactOutput → ImpactAnalysis → RippleEffect[]
```

### Cross-Schema Constraints

1. **CodeElement.type** values must match query target types
2. **QueryOutput.results** must reference valid **CodeElement** names from scan
3. **ImpactOutput.impact.affected_files** count must match **RippleEffect[]** length
4. **ComplexityMetrics.test_coverage** must be decimal 0.0-1.0

---

## References

- **[API.md](API.md)** - API endpoint documentation (uses these schemas)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (data flow through schemas)
- **[server.py](../server.py)** - Schema validation implementation
- **[@coderef/core CLI](https://github.com/coderef-system)** - Upstream schema definitions

---

## AI Agent Instructions

**When constructing tool inputs:**
1. Validate required fields before calling tool (prevent validation errors)
2. Use enums exactly as defined (avoid typos)
3. Provide absolute paths for `project_path` (not relative)
4. Set appropriate timeouts for large projects

**When parsing tool outputs:**
1. Check `success` field first before accessing results
2. Handle errors gracefully (retry on TIMEOUT, ask user on CLI_NOT_FOUND)
3. Validate output schema before using data (defensive parsing)
4. Extract `CodeElement[]` from scan, then use names in query/impact calls

**Schema validation tips:**
- TypeScript interfaces above are for documentation—Python server uses JSON Schema internally
- Missing optional fields default to documented defaults
- Extra fields are ignored (forward compatibility)

---

**Generated:** 2025-12-30
**Maintained by:** coderef-context MCP Server
**For AI Agents:** This schema reference ensures type-safe tool usage. Validate inputs before calling tools to avoid errors.
