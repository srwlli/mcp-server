# CodeRef2 MCP Service - API Documentation

**Version:** 1.0.0
**Last Updated:** Phase 6 Complete

---

## Table of Contents

1. [Protocol Overview](#protocol-overview)
2. [Authentication](#authentication)
3. [Tool Specifications](#tool-specifications)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

---

## Protocol Overview

### MCP (Model Context Protocol)

CodeRef2 implements the MCP specification for tool exposure:

- **Protocol Version:** MCP 1.0
- **Transport:** Stdio (default), SSE optional
- **Encoding:** JSON
- **Async Support:** Yes (all tools support async)

### Tool Discovery

List all available tools:

```python
await server.list_tools()
```

Returns 6 tools with schemas, descriptions, and input specifications.

---

## Authentication

**Current Implementation:** No authentication required

CodeRef2 is designed to run in secure environments (local, private networks, or protected APIs).

### Future Considerations

- API key authentication
- OAuth2 integration
- Rate limiting per client
- Request signing

---

## Tool Specifications

### Tool 1: Query (`mcp__coderef__query`)

**Status:** ✅ Fully Implemented

#### Description
Find and retrieve CodeRef2 elements by reference or pattern matching.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "CodeRef2 reference (@Type/path#element:line) or search pattern",
      "example": "@Fn/src/utils#calculate:42"
    },
    "filter": {
      "type": "object",
      "description": "Optional filter criteria",
      "properties": {
        "type_designators": {
          "type": "array",
          "description": "Filter by type (e.g., [\"Fn\", \"C\"])",
          "items": {"type": "string"}
        },
        "path_pattern": {
          "type": "string",
          "description": "Glob pattern for path (e.g., \"src/*\")"
        },
        "metadata_filters": {
          "type": "object",
          "description": "Match metadata values",
          "example": {"status": "active", "complexity": "high"}
        },
        "relationship_types": {
          "type": "array",
          "description": "Filter by relationship type"
        },
        "min_line": {"type": "integer"},
        "max_line": {"type": "integer"},
        "has_test_coverage": {"type": "boolean"}
      }
    },
    "limit": {
      "type": "integer",
      "description": "Maximum results (1-1000)",
      "default": 100,
      "minimum": 1,
      "maximum": 1000
    },
    "include_relationships": {
      "type": "boolean",
      "description": "Include relationship information",
      "default": true
    },
    "include_metadata": {
      "type": "boolean",
      "description": "Include element metadata",
      "default": true
    },
    "include_source": {
      "type": "boolean",
      "description": "Include source code snippets",
      "default": false
    }
  },
  "required": ["query"]
}
```

#### Output Schema

```json
{
  "type": "object",
  "properties": {
    "status": {"type": "string", "enum": ["success", "error"]},
    "query": {"type": "string"},
    "total_count": {"type": "integer"},
    "elements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "reference": {"type": "string"},
          "type_designator": {"type": "string"},
          "path": {"type": "string"},
          "element": {"type": ["string", "null"]},
          "line": {"type": ["integer", "null"]},
          "metadata": {"type": "object"},
          "has_relationships": {"type": "boolean"},
          "test_coverage": {"type": ["number", "null"]}
        }
      }
    },
    "execution_time_ms": {"type": "number"},
    "query_status": {"type": "string"},
    "timestamp": {"type": "string", "format": "date-time"}
  }
}
```

#### Performance
- **Target:** < 500ms
- **Typical:** 200-400ms
- **Max depth:** Not limited (depends on pattern complexity)

#### Error Codes
- `INVALID_REQUEST` - Missing or invalid parameters
- `QUERY_ERROR` - Query execution failed
- `INVALID_FILTER` - Filter configuration invalid

---

### Tool 2: Analyze (`mcp__coderef__analyze`)

**Status:** ✅ Fully Implemented

#### Description
Perform deep analysis on CodeRef2 elements (impact, coverage, complexity, graph traversal).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "reference": {
      "type": "string",
      "description": "CodeRef2 reference to analyze",
      "example": "@Fn/src/core#main:100"
    },
    "analysis_type": {
      "type": "string",
      "enum": ["impact", "deep", "coverage", "complexity"],
      "description": "Type of analysis",
      "default": "impact"
    },
    "depth": {
      "type": "integer",
      "description": "Analysis traversal depth",
      "default": 3,
      "minimum": 1,
      "maximum": 10
    },
    "include_test_impact": {
      "type": "boolean",
      "description": "Include test-related impacts",
      "default": true
    }
  },
  "required": ["reference"]
}
```

#### Analysis Types

##### Impact Analysis
Determine what breaks if this element changes.

```json
{
  "status": "success",
  "reference": "@Fn/src/core#main:100",
  "analysis_type": "impact",
  "total_affected": 15,
  "affected_elements": [
    {
      "reference": "@Fn/src/handler#process",
      "element_type": "Fn",
      "impact_level": "critical",
      "depth": 1,
      "reason": "Direct caller"
    }
  ],
  "impact_summary": {
    "by_level": {"critical": 1, "high": 3, "medium": 5, "low": 6},
    "max_depth": 3
  }
}
```

##### Deep Analysis
Full graph traversal with cycle detection.

```json
{
  "analysis_type": "deep",
  "results": {
    "dependents": {"total": 15, "by_depth": {"1": 3, "2": 5, "3": 7}},
    "dependencies": {"total": 8},
    "cycles_detected": 0,
    "cycles": []
  }
}
```

##### Coverage Analysis
Test coverage statistics.

```json
{
  "analysis_type": "coverage",
  "coverage_results": {
    "total_elements": 1,
    "covered_elements": 1,
    "uncovered_elements": 0,
    "coverage_percentage": 85.5,
    "at_risk_count": 2,
    "at_risk_elements": ["@Fn/src/utils#helper"]
  }
}
```

##### Complexity Analysis
Code complexity metrics.

```json
{
  "analysis_type": "complexity",
  "complexity_score": 42.5,
  "complexity_category": "medium"
}
```

#### Performance
- **Target:** < 500ms
- **Typical:** 300-450ms

#### Error Codes
- `INVALID_REFERENCE` - Reference format invalid
- `ANALYSIS_ERROR` - Analysis execution failed
- `UNSUPPORTED_ANALYSIS` - Unknown analysis type

---

### Tool 3: Validate (`mcp__coderef__validate`)

**Status:** ✅ Fully Implemented

#### Description
Validate CodeRef2 reference format and structure. Supports single or multiple references.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "reference": {
      "type": "string",
      "description": "Single reference to validate"
    },
    "references": {
      "type": "array",
      "description": "Multiple references to validate",
      "items": {"type": "string"}
    },
    "validate_existence": {
      "type": "boolean",
      "description": "Check if element exists",
      "default": false
    }
  }
}
```

**Note:** Provide either `reference` or `references`, not both.

#### Output Schema

```json
{
  "status": "success",
  "total_references": 1,
  "valid_count": 1,
  "invalid_count": 0,
  "results": [
    {
      "reference": "@Fn/src/utils#calculate_total:42",
      "status": "valid",
      "is_valid": true,
      "issues": [
        {
          "severity": "warning",
          "code": "CUSTOM_METADATA",
          "message": "Metadata not in standard categories",
          "field": "metadata",
          "suggestion": "Consider using standard categories"
        }
      ],
      "validation_time_ms": 2.3
    }
  ],
  "validation_status": "success"
}
```

#### Validation Rules

1. **Format:** Must match `@Type/path#element:line{metadata}`
2. **Type:** Must be valid designator (26 types)
3. **Path:** Must contain valid path characters
4. **Element:** Optional, must be identifier
5. **Line:** Optional, must be positive integer
6. **Metadata:** Optional, key:value pairs

#### Severity Levels
- `info` - Informational
- `warning` - Potential issue
- `error` - Validation failed
- `critical` - Must fix

#### Error Codes
- `EMPTY_REFERENCE` - Reference is empty
- `MALFORMED_REFERENCE` - Format doesn't match pattern
- `INVALID_TYPE` - Type designator not recognized
- `EMPTY_PATH` - Path is missing
- `NEGATIVE_LINE` - Line number < 0
- `INVALID_METADATA_FORMAT` - Metadata syntax error

---

### Tool 4: Batch Validate (`mcp__coderef__batch_validate`)

**Status:** ✅ Fully Implemented

#### Description
Validate multiple references efficiently (sequential or parallel).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "references": {
      "type": "array",
      "description": "References to validate",
      "items": {"type": "string"},
      "minItems": 1
    },
    "parallel": {
      "type": "boolean",
      "description": "Process in parallel",
      "default": true
    },
    "max_workers": {
      "type": "integer",
      "description": "Max concurrent workers",
      "default": 5,
      "minimum": 1,
      "maximum": 20
    },
    "timeout_ms": {
      "type": "integer",
      "description": "Batch timeout milliseconds",
      "default": 5000,
      "minimum": 1000,
      "maximum": 30000
    }
  },
  "required": ["references"]
}
```

#### Output Schema

```json
{
  "status": "success",
  "total_items": 100,
  "successful": 98,
  "failed": 2,
  "warnings": 5,
  "results": [
    {
      "reference": "@Fn/src/a#func",
      "status": "valid",
      "is_valid": true,
      "issue_count": 0,
      "error_count": 0,
      "warning_count": 0
    }
  ],
  "summary": {
    "success_rate": 98.0,
    "average_validation_time_ms": 2.1
  },
  "batch_execution_time_ms": 215.3
}
```

#### Performance
- **Sequential:** ~2-3ms per reference
- **Parallel (5 workers):** ~20-30ms per reference
- **Target for 100 items:** < 5000ms

#### Optimization Tips
- Use `parallel: true` for 50+ items
- Increase `max_workers` for CPU-bound systems
- Batch size 100-500 for optimal performance

---

### Tool 5 & 6: UDS Tools (Placeholder)

**Status:** ⏳ Deferred (P6.4-P6.5)

#### Tool 5: UDS Compliance Check (`mcp__coderef__uds_compliance_check`)

```json
{
  "status": "pending",
  "message": "UDS compliance checking implementation in P6.4"
}
```

#### Tool 6: Generate with UDS (`mcp__coderef__generate_with_uds`)

```json
{
  "status": "pending",
  "message": "UDS-compliant generation implementation in P6.5"
}
```

---

## Data Models

### CodeRef2 Reference

```typescript
@Type/path#element:line{metadata}

// Components:
Type: TypeDesignator        // One of 26 types (Fn, C, M, etc.)
path: string                // File or module path
element?: string            // Optional element name
line?: integer              // Optional line number
metadata?: {key: string}    // Optional metadata tags
```

### Element Metadata

```typescript
{
  status?: "active" | "deprecated" | "experimental",
  security?: "public" | "internal" | "private" | "critical",
  performance?: "fast" | "normal" | "slow" | "critical",
  complexity?: "low" | "medium" | "high" | "critical",
  coverage?: "0-100" (percentage),
  maintenance?: "active" | "stable" | "deprecated",
  compatibility?: "v1" | "v2" | "breaking",
  documentation?: "complete" | "partial" | "minimal"
}
```

### Relationship Types

```typescript
enum RelationshipType {
  IMPORTS = "imports",
  CALLS = "calls",
  DEPENDS_ON = "depends-on",
  TESTS = "tests",
  IMPLEMENTS = "implements",
  EXTENDS = "extends",
  CONTAINS = "contains",
  REFERENCES = "references"
}
```

### Type Designators (26 total)

```typescript
F        // File
D        // Directory
C        // Class
Fn       // Function
Cl       // Closure
M        // Method
P        // Property
V        // Variable
K        // Constant
E        // Enum
I        // Interface
Tr       // Trait
Mo       // Module
Pkg      // Package
N        // Namespace
TD       // Type Definition
G        // Generic
Dec      // Decorator
Param    // Parameter
Fd       // Field
Attr     // Attribute
Test     // Test Case
Fix      // Fixture
Macro    // Macro
Ann      // Annotation
Custom   // Custom Type
```

---

## Error Handling

### Standard Error Response

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "suggestion": "What to do about it"
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Error Categories

#### Validation Errors (400)
- `INVALID_REQUEST` - Invalid input parameters
- `VALIDATION_ERROR` - Reference validation failed
- `MALFORMED_REFERENCE` - Reference format invalid

#### Execution Errors (500)
- `QUERY_ERROR` - Query execution failed
- `ANALYSIS_ERROR` - Analysis execution failed
- `BATCH_VALIDATION_ERROR` - Batch processing failed
- `TOOL_EXECUTION_ERROR` - General tool execution error

#### Configuration Errors (500)
- `UNKNOWN_TOOL` - Tool not found
- `UNSUPPORTED_ANALYSIS` - Analysis type not supported

---

## Rate Limiting

**Current:** No rate limiting

### Planned Limits
- 100 requests/second per client
- 1000 elements per query
- 500 elements per batch
- 10 second timeout per request

---

## Examples

### Example 1: Query Elements

```python
import json
from server import CodeRef2Server

async def example():
    server = CodeRef2Server()

    result = await server._handle_call_tool(
        "mcp__coderef__query",
        {
            "query": "@Fn/src/utils#*",
            "limit": 10,
            "include_metadata": True
        }
    )

    response = json.loads(result[0].text)
    print(json.dumps(response, indent=2))
```

### Example 2: Analyze Impact

```python
result = await server._handle_call_tool(
    "mcp__coderef__analyze",
    {
        "reference": "@Fn/src/core#main:100",
        "analysis_type": "impact",
        "depth": 3
    }
)

response = json.loads(result[0].text)
print(f"Elements affected: {response['total_affected']}")
for elem in response['affected_elements']:
    print(f"  - {elem['reference']} ({elem['impact_level']})")
```

### Example 3: Batch Validate

```python
result = await server._handle_call_tool(
    "mcp__coderef__batch_validate",
    {
        "references": [
            "@Fn/src/a#func",
            "@C/src/b#Class",
            "invalid_ref",
            "@F/src/config.py"
        ],
        "parallel": True,
        "max_workers": 4
    }
)

response = json.loads(result[0].text)
print(f"Success rate: {response['summary']['success_rate']}%")
for result in response['results']:
    status = "✓" if result['is_valid'] else "✗"
    print(f"  {status} {result['reference']}")
```

---

## Integration Guide

### Using with Claude or Agents

```json
{
  "mcpServers": {
    "coderef2": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "CODEREF_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Direct Python Integration

```python
from server import get_server
import asyncio

async def main():
    server = get_server()

    # List tools
    tools = await server._handle_list_tools()
    print(f"Available tools: {len(tools)}")

    # Health check
    health = await server.health_check()
    print(f"Status: {health['status']}")
```

---

**API Version:** 1.0.0
**Last Updated:** Phase 6 Implementation Complete
