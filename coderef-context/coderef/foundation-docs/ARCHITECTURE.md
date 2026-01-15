---
generated_by: coderef-docs
template: architecture
date: "2026-01-14T01:20:47Z"
doc_type: architecture
feature_id: foundation-docs
workorder_id: foundation-docs-001
task: Generate foundation documentation
agent: Claude Code AI
_uds:
  validation_score: 95
  validated_at: "2026-01-14T01:20:47Z"
  validator: UDSValidator
---

# System Architecture

**[Date]** 2026-01-14 | **[Version]** 2.0.0

## Purpose

This document describes the overall system architecture of the CodeRef Context MCP server, including design decisions, module boundaries, data flow, and integration patterns.

## Overview

CodeRef Context is a read-only MCP server that provides fast access to pre-scanned code intelligence. It reads from `.coderef/` directory files instead of calling CLI subprocesses, resulting in 100x faster response times.

**Key Design Principle**: Pre-scan codebases once, query instantly many times.

## System Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (Claude, etc.)                │
└──────────────────────────┬──────────────────────────────────┘
                           │ stdio protocol
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    server.py                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Server (mcp.server.Server)                      │  │
│  │  - list_tools() → Tool definitions                    │  │
│  │  - call_tool() → Route to handlers                   │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ async function calls
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              src/handlers_refactored.py                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  14 Handler Functions                                 │  │
│  │  - handle_coderef_scan()                             │  │
│  │  - handle_coderef_query()                           │  │
│  │  - handle_coderef_impact()                           │  │
│  │  - ... (11 more handlers)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ CodeRefReader method calls
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              src/coderef_reader.py                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CodeRefReader Class                                 │  │
│  │  - get_index() → Read index.json                     │  │
│  │  - get_graph() → Read graph.json                    │  │
│  │  - get_context() → Read context.json/md              │  │
│  │  - get_patterns() → Read reports/patterns.json       │  │
│  │  - ... (8 more get methods)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ File I/O (read-only)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              .coderef/ Directory                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pre-scanned Code Intelligence Files                  │  │
│  │  - index.json (250+ elements)                        │  │
│  │  - graph.json (dependency graph)                     │  │
│  │  - context.json (project metadata)                   │  │
│  │  - reports/patterns.json (optional)                  │  │
│  │  - reports/coverage.json (optional)                   │  │
│  │  - diagrams/*.mermaid (optional)                     │  │
│  │  - exports/*.json (optional)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Module Boundaries

### 1. Server Layer (`server.py`)

**Responsibility**: MCP protocol handling, tool registration, request routing

**Boundaries**:
- **Input**: MCP stdio protocol messages
- **Output**: MCP TextContent responses
- **Dependencies**: `mcp` library, `handlers_refactored` module
- **No Dependencies On**: File system, `.coderef/` files

**Key Functions**:
- `list_tools()`: Expose tool definitions to MCP clients
- `call_tool()`: Route tool calls to appropriate handlers
- `main()`: Start stdio server

---

### 2. Handler Layer (`src/handlers_refactored.py`)

**Responsibility**: Business logic for each MCP tool, request validation, response formatting

**Boundaries**:
- **Input**: Tool arguments dictionary
- **Output**: `List[TextContent]` with JSON responses
- **Dependencies**: `CodeRefReader` class
- **No Dependencies On**: MCP protocol details, file I/O implementation

**Key Functions**:
- 14 handler functions (one per MCP tool)
- Error handling and validation
- JSON response formatting

---

### 3. Data Access Layer (`src/coderef_reader.py`)

**Responsibility**: Read and query `.coderef/` files, provide unified data interface

**Boundaries**:
- **Input**: File paths, query parameters
- **Output**: Parsed JSON data, text content
- **Dependencies**: `json`, `pathlib` (standard library)
- **No Dependencies On**: MCP protocol, handler logic

**Key Classes**:
- `CodeRefReader`: Main data access class
- Methods: `get_index()`, `get_graph()`, `get_context()`, etc.

---

### 4. Processor Layer (`processors/export_processor.py`)

**Responsibility**: Handle export operations (requires CLI integration)

**Boundaries**:
- **Input**: Export parameters (format, output path, etc.)
- **Output**: Export file or error message
- **Dependencies**: `asyncio` for subprocess execution
- **No Dependencies On**: MCP protocol, CodeRefReader

**Key Functions**:
- `export_coderef()`: Async export operation
- `validate_export_format()`: Format validation

---

## Data Flow

### Request Flow

```
1. MCP Client → stdio → server.py (call_tool)
2. server.py → route → handlers_refactored.py (handle_*)
3. handlers_refactored.py → CodeRefReader → coderef_reader.py
4. coderef_reader.py → file I/O → .coderef/*.json
5. .coderef/*.json → JSON parse → coderef_reader.py
6. coderef_reader.py → return data → handlers_refactored.py
7. handlers_refactored.py → format JSON → server.py
8. server.py → TextContent → stdio → MCP Client
```

### Response Flow

```
1. .coderef/*.json (data source)
2. CodeRefReader (data access)
3. Handler (business logic)
4. Server (protocol)
5. MCP Client (consumer)
```

---

## Design Decisions

### Decision 1: Read-Only File Access

**Rationale**: 
- 100x faster than CLI subprocess calls
- No external process overhead
- Predictable performance
- Safe for automated workflows

**Trade-offs**:
- Requires pre-scanning step
- Data may be stale if code changes
- No real-time code analysis

**Solution**: Incremental scan tool (`coderef_incremental_scan`) detects drift and updates index.

---

### Decision 2: Async Handler Functions

**Rationale**:
- MCP protocol is async
- Non-blocking I/O for file reads
- Scalable for concurrent requests

**Trade-offs**:
- Slightly more complex than sync
- File I/O is fast anyway (local filesystem)

**Solution**: Use async/await pattern throughout for consistency.

---

### Decision 3: Unified CodeRefReader Interface

**Rationale**:
- Single point of data access
- Consistent error handling
- Easy to mock for testing
- Encapsulates file system details

**Trade-offs**:
- All handlers depend on one class
- Potential bottleneck (mitigated by read-only access)

**Solution**: CodeRefReader is lightweight and stateless.

---

### Decision 4: JSON-Only Responses

**Rationale**:
- MCP TextContent format
- Easy to parse by clients
- Consistent response structure
- Human-readable for debugging

**Trade-offs**:
- No binary data support
- Larger payload size (mitigated by compression)

**Solution**: Use JSON with consistent structure across all tools.

---

### Decision 5: Optional CLI Integration

**Rationale**:
- Most tools are read-only (no CLI needed)
- Export and tag tools require CLI for code modification
- Graceful degradation if CLI unavailable

**Trade-offs**:
- Some tools may fail if CLI not installed
- Inconsistent behavior across tools

**Solution**: Clear error messages when CLI required but unavailable.

---

## Stack Decisions

### Language: Python 3.10+

**Rationale**:
- MCP Python SDK available
- Excellent async support
- Rich standard library
- Easy JSON handling

### Framework: MCP (Model Context Protocol)

**Rationale**:
- Standard protocol for AI agent tools
- stdio-based (simple integration)
- Tool discovery and validation
- Type-safe schemas

### Data Format: JSON

**Rationale**:
- Human-readable
- Easy to parse
- Standard format
- No schema compilation needed

### File System: Local `.coderef/` Directory

**Rationale**:
- Fast local file reads
- No network overhead
- Version control friendly
- Portable across systems

---

## Integration Patterns

### Pattern 1: Pre-Scan Workflow

```
1. Developer runs CodeRef scanner (dashboard or CLI)
2. Scanner generates .coderef/ directory
3. MCP server reads from .coderef/ files
4. AI agents query via MCP tools
```

### Pattern 2: Incremental Updates

```
1. Code changes detected (git, file watcher)
2. coderef_drift tool detects changes
3. coderef_incremental_scan updates index
4. Updated data available immediately
```

### Pattern 3: Export Workflow

```
1. AI agent calls coderef_export tool
2. Handler calls export_coderef processor
3. Processor executes CLI subprocess
4. Export file written to .coderef/exports/
5. Response includes file path
```

---

## Error Handling Strategy

### Layer 1: File System Errors

**Handled By**: `CodeRefReader._load_json()` and `_load_text()`

**Strategy**: Raise `FileNotFoundError` with helpful message

**Example**:
```python
if not file_path.exists():
    raise FileNotFoundError(f"CodeRef data not found: {filename}. Run scan first.")
```

### Layer 2: Handler Errors

**Handled By**: Each handler function

**Strategy**: Catch exceptions, return error JSON response

**Example**:
```python
try:
    reader = CodeRefReader(project_path)
    # ... operation ...
except Exception as e:
    return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}))]
```

### Layer 3: Server Errors

**Handled By**: `server.py` call_tool()

**Strategy**: Catch handler exceptions, return generic error

**Example**:
```python
try:
    return await handler(args)
except Exception as e:
    return [TextContent(type="text", text=f"Tool error: {str(e)}")]
```

---

## Performance Characteristics

### File Read Performance

- **Local filesystem**: < 10ms for typical `.coderef/index.json` (250 elements)
- **JSON parsing**: < 5ms for 250-element array
- **Total handler time**: < 50ms for most operations

### Scalability

- **Concurrent requests**: Limited by Python GIL (single-threaded)
- **File I/O**: Fast (local filesystem, no network)
- **Memory**: Low (reads only needed data, no caching)

### Optimization Opportunities

1. **Caching**: Cache frequently accessed files (not implemented)
2. **Lazy loading**: Load files only when needed (already implemented)
3. **Indexing**: Pre-build query indexes (future enhancement)

---

## Security Considerations

### Read-Only Operations

- **No code modification**: All tools are read-only except `coderef_tag`
- **File system access**: Limited to `.coderef/` directory
- **No network access**: All operations are local

### Input Validation

- **Path validation**: Ensure `project_path` is absolute and exists
- **Format validation**: Validate export formats, diagram types
- **Parameter validation**: Check required parameters in handlers

### Error Information

- **No sensitive data**: Error messages don't expose file system structure
- **Helpful hints**: Error messages include actionable suggestions

---

## Testing Strategy

### Unit Tests

- **CodeRefReader**: Mock file I/O, test query methods
- **Handlers**: Mock CodeRefReader, test response formatting
- **Export Processor**: Mock subprocess, test export logic

### Integration Tests

- **End-to-end**: Test MCP tool calls with real `.coderef/` files
- **Error scenarios**: Test missing files, corrupted JSON, etc.

### Test Files

- `tests/test_tools.py`: Unit tests for handlers
- `tests/test_integration.py`: Integration tests
- `tests/test_export_processor.py`: Export processor tests

---

## Future Enhancements

### 1. Caching Layer

**Proposal**: Add in-memory cache for frequently accessed files

**Benefits**: Faster repeated queries

**Trade-offs**: Memory usage, cache invalidation complexity

### 2. Streaming Responses

**Proposal**: Stream large responses instead of loading all at once

**Benefits**: Lower memory usage for large codebases

**Trade-offs**: More complex handler logic

### 3. GraphQL Interface

**Proposal**: Add GraphQL endpoint for flexible queries

**Benefits**: Client-defined queries, reduced payload size

**Trade-offs**: Additional dependency, complexity

### 4. WebSocket Support

**Proposal**: Add WebSocket server for real-time updates

**Benefits**: Push notifications when code changes

**Trade-offs**: Additional protocol, complexity

---

## References

- [README.md](../README.md): Project overview and quick start
- [API.md](API.md): Complete API reference
- [SCHEMA.md](SCHEMA.md): Data model documentation
- [COMPONENTS.md](COMPONENTS.md): Component reference

---

**AI Agent Note**: This architecture prioritizes speed and simplicity. The read-only file access pattern enables fast, predictable performance for AI agent workflows. For code modification, use the `coderef_tag` tool which requires CLI integration.
