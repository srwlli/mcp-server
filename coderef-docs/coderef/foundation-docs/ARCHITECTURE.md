# Architecture Reference - coderef-docs MCP Server

**Version:** 3.2.0
**Last Updated:** 2025-12-27
**Style:** Modular Python with MCP Protocol

---

## Purpose

This document describes the system architecture, design principles, data flow, and integration patterns of the coderef-docs MCP server.

---

## Overview

The coderef-docs MCP server is designed as a **documentation-focused microservice** that integrates with the Model Context Protocol to provide AI agents with 11 specialized documentation tools.

**Core Architecture Principles:**
1. **Single Responsibility** - Each component has one clear purpose
2. **Separation of Concerns** - Handlers, generators, validation, errors separated
3. **Fail-Safe Degradation** - Context injection degrades gracefully to placeholders
4. **Validation at Boundaries** - All inputs validated before processing
5. **Consistent Error Handling** - Uniform error response format

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│         MCP Client (Claude Code / ChatGPT)          │
└──────────────────┬──────────────────────────────────┘
                   │ MCP Protocol (JSON-RPC over stdio)
                   ↓
┌─────────────────────────────────────────────────────┐
│              server.py (MCP Entry Point)             │
│  • Health Check (@coderef/core CLI detection)       │
│  • Tool Registration (11 tools)                     │
│  • Request Routing                                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│          tool_handlers.py (Business Logic)          │
│  • @log_invocation decorator                        │
│  • @mcp_error_handler decorator                     │
│  • 11 handler functions                             │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┬──────────────┬─────────┐
         ↓                   ↓              ↓         ↓
    ┌─────────┐      ┌──────────────┐  ┌──────┐  ┌─────────┐
    │Generator│      │ extractors.py│  │Valid.│  │ Errors  │
    │ Stack   │      │   (Context   │  │      │  │         │
    │         │      │  Injection)  │  │      │  │         │
    └─────────┘      └──────────────┘  └──────┘  └─────────┘
         │                   │
         ↓                   ↓
    ┌─────────┐      ┌──────────────┐
    │Templates│      │  cli_utils   │
    │ (POWER) │      │(@coderef CLI)│
    └─────────┘      └──────────────┘
         │                   │
         ↓                   ↓
    ┌─────────────────────────────┐
    │  File System (JSON + MD)    │
    └─────────────────────────────┘
```

---

## Component Architecture

### Layer 1: MCP Protocol Layer

**Component:** `server.py`

**Responsibilities:**
- Initialize MCP server instance
- Register 11 tools with JSON schemas
- Health check for @coderef/core CLI availability
- Route tool calls to handlers

**Key Design Decision:**
- **Health check on startup** sets global `CODEREF_CONTEXT_AVAILABLE` flag
- If CLI unavailable, server runs in degraded mode (fallback to placeholders)

---

### Layer 2: Handler Layer

**Component:** `tool_handlers.py`

**Responsibilities:**
- Implement business logic for all 11 tools
- Coordinate between generators, extractors, validators
- Apply decorators for logging and error handling

**Handler Categories:**
1. **Template Tools** (2) - list_templates, get_template
2. **Foundation Generation** (2) - generate_foundation_docs, generate_individual_doc
3. **Changelog** (3) - get_changelog, add_changelog_entry, record_changes
4. **Standards** (3) - establish_standards, audit_codebase, check_consistency
5. **Quickref** (1) - generate_quickref_interactive

**Decorator Stack:**
```python
@log_invocation  # Outer: Logs entry/exit with args
@mcp_error_handler  # Inner: Catches exceptions, formats errors
async def handle_tool_name(arguments: dict) -> list[TextContent]:
    # Validate inputs at boundary
    project_path = validate_project_path_input(arguments.get("project_path"))

    # Business logic
    result = generator.generate(project_path)

    # Return TextContent
    return [TextContent(type="text", text=result)]
```

---

### Layer 3: Generator Layer

**Components:** `generators/` (6 generators + 1 base)

**Pattern:** Template Method + Strategy

**Base Class:** `BaseGenerator`
- Defines common workflow (load template, prepare paths, parse metadata)
- Subclasses implement specific generation logic

**Generators:**
1. `FoundationGenerator` - Orchestrates 5-doc workflow
2. `ChangelogGenerator` - CRUD for CHANGELOG.json
3. `StandardsGenerator` - Extract coding standards from codebase
4. `AuditGenerator` - Compliance checking with scoring
5. `QuickrefGenerator` - Interactive quickref generation
6. `HandoffGenerator` - Agent handoff context (legacy)

**Key Design Decision:**
- Generators are **stateless** - all state passed via method parameters
- All generators extend `BaseGenerator` for consistent interface

---

### Layer 4: Extraction Layer

**Component:** `extractors.py` (WO-CONTEXT-DOCS-INTEGRATION-001)

**Purpose:** Code intelligence extraction via @coderef/core CLI

**Functions:**
```python
@lru_cache(maxsize=32)
def extract_apis(project_path: str) -> Dict[str, Any]:
    """Extract API endpoints from codebase via CLI scan"""

@lru_cache(maxsize=32)
def extract_schemas(project_path: str) -> Dict[str, Any]:
    """Extract data models and entities"""

@lru_cache(maxsize=32)
def extract_components(project_path: str) -> Dict[str, Any]:
    """Extract UI components"""
```

**Design Decisions:**
- **LRU Cache:** Results cached to avoid redundant CLI calls
- **Graceful Degradation:** Returns `source: "placeholder"` on CLI failure
- **Subprocess Isolation:** CLI runs in separate process with timeout

**Integration:**
```
extractors.py → cli_utils.py → subprocess → coderef scan → JSON output
```

---

### Layer 5: Validation Layer

**Component:** `validation.py` (REF-003 principle)

**Purpose:** Validate all inputs at API boundary before processing

**Functions:**
- `validate_project_path_input(path)` - Path exists and is directory
- `validate_version_format(version)` - Matches semantic versioning
- `validate_template_name_input(name)` - Template exists in POWER framework
- `validate_changelog_inputs(args)` - Complete changelog data

**Error Handling:**
```python
def validate_project_path_input(path: str) -> str:
    if not path:
        raise ValueError("project_path is required")
    if not Path(path).exists():
        raise ValueError(f"project_path does not exist: {path}")
    if not Path(path).is_dir():
        raise ValueError(f"project_path is not a directory: {path}")
    return str(Path(path).resolve())
```

**Key Design Decision:**
- Validation raises `ValueError` with descriptive messages
- Handlers catch and convert to error responses via decorator

---

### Layer 6: Error Handling Layer

**Component:** `error_responses.py` (ARCH-001 principle)

**Purpose:** Consistent error response formatting

**Factory Methods:**
```python
class ErrorResponse:
    @staticmethod
    def invalid_input(message: str) -> list[TextContent]:
        return [TextContent(type="text", text=f"Error: {message}")]

    @staticmethod
    def file_not_found(path: str) -> list[TextContent]:
        return [TextContent(type="text", text=f"Error: File not found - {path}")]
```

**Integration with Decorator:**
```python
@mcp_error_handler
async def handle_tool(args):
    # If any ValueError raised...
    # Decorator catches and calls ErrorResponse.invalid_input()
```

---

## Data Flow

### Tool Invocation Flow

```
1. MCP Client sends tool call (JSON-RPC)
      ↓
2. server.py routes to handler
      ↓
3. @log_invocation logs entry
      ↓
4. Validation layer checks inputs (raises ValueError on fail)
      ↓
5. Handler calls generator/extractor
      ↓
6. Generator loads template from templates/power/
      ↓
7. Extractor calls @coderef/core CLI (if available)
      ↓
8. Generator combines template + extracted data
      ↓
9. Handler formats response as TextContent
      ↓
10. @log_invocation logs exit
      ↓
11. MCP server returns response to client
```

### Context Injection Flow (WO-CONTEXT-DOCS-INTEGRATION-001)

```
1. handle_generate_individual_doc(template="api")
      ↓
2. Check CODEREF_CONTEXT_AVAILABLE flag
      ↓
3. If TRUE and template in ["api", "schema", "components"]:
      ↓
   4. Call extract_apis(project_path)
         ↓
   5. cli_utils.run_coderef_command("scan", ["--project", path])
         ↓
   6. subprocess executes: coderef scan --project /path --output json
         ↓
   7. Parse JSON output, extract endpoints
         ↓
   8. Cache result with @lru_cache
      ↓
9. Return template + extracted data (or template only if extraction failed)
```

---

## Design Patterns

### 1. Decorator Pattern

**Usage:** Logging and error handling

```python
@log_invocation  # Cross-cutting concern: logging
@mcp_error_handler  # Cross-cutting concern: error formatting
async def handle_tool(args):
    pass
```

**Benefits:**
- Separates cross-cutting concerns from business logic
- Consistent behavior across all 11 handlers

---

### 2. Template Method Pattern

**Usage:** BaseGenerator and subclasses

```python
class BaseGenerator:
    def generate(self, project_path):
        # Template method defines workflow
        self.prepare_generation(project_path)
        template = self.read_template()
        return self.process_template(template)

class FoundationGenerator(BaseGenerator):
    def process_template(self, template):
        # Subclass implements specific logic
        pass
```

**Benefits:**
- Consistent workflow across all generators
- Easy to add new generator types

---

### 3. Strategy Pattern

**Usage:** Different generators for different doc types

```python
# Select strategy based on template_name
if template_name == "api":
    generator = APIGenerator()
elif template_name == "schema":
    generator = SchemaGenerator()
```

**Benefits:**
- Flexible doc generation
- Each strategy encapsulates specific algorithm

---

### 4. Factory Pattern

**Usage:** Error response creation

```python
ErrorResponse.invalid_input(message)  # Factory method
ErrorResponse.file_not_found(path)    # Factory method
```

**Benefits:**
- Centralized error response creation
- Consistent error formatting

---

## Architectural Principles (REF-xxx)

### ARCH-001: Consistent Error Response Format

All errors returned as `TextContent` with user-friendly messages.

**Implementation:** `error_responses.py` + `@mcp_error_handler` decorator

---

### REF-002: Centralized Constants

All paths, filenames, configurations in `constants.py`.

**Implementation:**
```python
class Paths:
    TEMPLATES_DIR = "templates/power"
    OUTPUT_DIR = "coderef/foundation-docs"
```

---

### REF-003: Validation at Boundaries

All inputs validated before entering business logic.

**Implementation:** `validation.py` with descriptive ValueError messages

---

### ARCH-004: Structured Logging

All tool calls logged with entry/exit, arguments, results.

**Implementation:** `logger_config.py` + `@log_invocation` decorator

---

### ARCH-005: Graceful Degradation

Context injection fails gracefully to template placeholders.

**Implementation:** `extractors.py` returns `source: "placeholder"` on error

---

## Integration Architecture

### Integration with @coderef/core CLI

**Detection Strategy:**
1. Check `coderef --version` in PATH (global npm install)
2. Fallback to hardcoded path `C:\Users\willh\Desktop\projects\coderef-system\packages\cli\dist\cli.js`

**Execution:**
```python
subprocess.run(["coderef", "scan", "--project", path], timeout=120)
```

**Error Handling:**
- `FileNotFoundError` → CLI not found (fallback mode)
- `subprocess.TimeoutExpired` → Timeout (fallback mode)
- `json.JSONDecodeError` → Invalid output (fallback mode)

---

### Integration with coderef-workflow

**Relationship:** coderef-docs provides documentation tools; coderef-workflow orchestrates planning

**Integration Points:**
- Workflow calls `generate_foundation_docs` after feature completion
- Workflow calls `record_changes` to update changelog
- Workflow calls `generate_quickref_interactive` for quickref guides

---

## Security Architecture

### Input Validation

All file paths resolved to absolute paths and validated before use.

**Protection Against:**
- Path traversal attacks (../)
- Invalid file operations
- Command injection (subprocess uses list args, not shell=True)

---

### Subprocess Isolation

CLI commands executed with:
- **No shell expansion** (`shell=False`)
- **Timeout limits** (120s default)
- **Separate process** (isolated from server)

---

## Performance Architecture

### Caching Strategy

**LRU Cache on Extractors:**
```python
@lru_cache(maxsize=32)
def extract_apis(project_path: str):
    # Expensive CLI call cached
```

**Benefits:**
- Avoid redundant CLI scans
- 32-entry cache covers typical usage
- Cache keyed by project_path

---

### Async Design

All tool handlers are `async` for non-blocking I/O:
```python
async def handle_tool(args):
    result = await some_async_operation()
```

**Benefits:**
- MCP server can handle concurrent requests
- Non-blocking file I/O

---

## Deployment Architecture

### File-Based Storage

No database required. All data stored as JSON files:
- `coderef/changelog/CHANGELOG.json`
- `coderef/standards/*.md`
- `coderef/workorder/{feature}/*.json`

**Benefits:**
- Simple deployment
- Git-friendly
- No database overhead

---

### Configuration

**MCP Configuration** (`~/.mcp.json` or `.claude/settings.json`):
```json
{
  "mcpServers": {
    "coderef-docs": {
      "command": "python",
      "args": ["-m", "coderef-docs.server"]
    }
  }
}
```

---

## References

- **Component Details:** COMPONENTS.md
- **API Specifications:** API.md
- **Data Schemas:** SCHEMA.md
- **MCP Specification:** https://spec.modelcontextprotocol.io/

---

*Generated: 2025-12-27*
*For AI Agents: This architecture prioritizes simplicity, modularity, and fail-safe degradation*
