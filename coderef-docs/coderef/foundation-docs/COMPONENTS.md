# Components Reference - coderef-docs MCP Server

**Version:** 3.2.0
**Last Updated:** 2025-12-27
**Architecture:** Modular Python MCP Server

---

## Purpose

This document describes the software components (modules, generators, handlers, utilities) that make up the coderef-docs MCP server architecture.

---

## Overview

The coderef-docs server is organized into 8 main component categories with clear separation of concerns.

**Component Hierarchy:**
```
server.py (MCP entry point)
├── tool_handlers.py (11 tool handlers)
├── generators/ (Document generation logic)
├── extractors.py (Code intelligence extraction)
├── validation.py (Input validation)
├── error_responses.py (Error handling)
├── logger_config.py (Logging)
└── cli_utils.py (CLI integration)
```

---

## 1. Core Server Components

### server.py

**Purpose:** MCP server entry point and tool registration

**Responsibilities:**
- Initialize MCP server
- Register 11 tools with schemas
- Health check for @coderef/core CLI
- Route tool calls to handlers

**Key Functions:**
- `health_check()` - Detect CLI availability
- `list_tools()` - Return tool schemas
- `call_tool()` - Route to handler

**Dependencies:** mcp.server, tool_handlers

---

### tool_handlers.py

**Purpose:** Business logic for all 11 MCP tools

**Components:**
```
Template Tools:
- handle_list_templates()
- handle_get_template()

Foundation Generation:
- handle_generate_foundation_docs()
- handle_generate_individual_doc()

Changelog:
- handle_get_changelog()
- handle_add_changelog_entry()
- handle_record_changes()

Standards:
- handle_establish_standards()
- handle_audit_codebase()
- handle_check_consistency()

Quickref:
- handle_generate_quickref_interactive()
```

**Features:**
- Decorated with `@log_invocation` and `@mcp_error_handler`
- Context injection support (WO-CONTEXT-DOCS-INTEGRATION-001)
- Sequential doc generation orchestration

**Dependencies:** generators, extractors, validation, error_responses

---

## 2. Generator Components

### generators/base_generator.py

**Purpose:** Base class for all document generators

**Responsibilities:**
- Template loading
- Path resolution
- Output directory creation
- Common generation utilities

**Key Methods:**
- `read_template(name)` - Load POWER template
- `get_template_info(name)` - Parse template metadata
- `prepare_generation(project_path)` - Setup paths
- `get_doc_output_path(path, template)` - Determine output location

---

### generators/foundation_generator.py

**Purpose:** 5-document foundation workflow

**Workflow:**
```
api → schema → components → architecture → readme
```

**Key Methods:**
- `get_workflow_info()` - Return 5-template sequence
- `get_generation_plan(project_path)` - Human-readable plan

**Template Order:** Ordered by dependency (API first, README last)

---

### generators/changelog_generator.py

**Purpose:** Changelog CRUD operations

**Key Methods:**
- `load_changelog(project_path)` - Read CHANGELOG.json
- `save_changelog(project_path, data)` - Write with validation
- `add_entry(version, change_data)` - Append new change
- `get_version(version)` - Filter by version
- `get_by_type(change_type)` - Filter by type

**Validation:** Uses jsonschema for CHANGELOG.json schema

---

### generators/standards_generator.py

**Purpose:** Extract and document coding standards

**Key Methods:**
- `scan_codebase(project_path, focus_areas, depth)` - Extract patterns
- `generate_standards_docs(patterns)` - Create markdown files
- `create_standards_index(standards)` - Summary document

**Output:** 4 files in `coderef/standards/`

---

### generators/audit_generator.py

**Purpose:** Standards compliance auditing

**Key Methods:**
- `audit_files(files, standards)` - Check violations
- `calculate_compliance_score(violations)` - 0-100 score
- `generate_audit_report(results)` - Markdown report
- `suggest_fixes(violations)` - Auto-fix recommendations

**Scoring:** Weighted by severity (critical=10, major=5, minor=1)

---

### generators/quickref_generator.py

**Purpose:** Interactive quickref generation

**Key Methods:**
- `generate_interview_questions(app_type)` - Context gathering
- `process_user_responses(responses)` - Parse answers
- `generate_quickref(data)` - Create scannable guide

**Output:** `quickref.md` (150-250 lines)

---

## 3. Extraction Components

### extractors.py

**Purpose:** Code intelligence extraction via @coderef/core CLI

**Functions:**
```python
@lru_cache(maxsize=32)
def extract_apis(project_path: str) -> Dict[str, Any]:
    """Extract API endpoints from codebase"""

@lru_cache(maxsize=32)
def extract_schemas(project_path: str) -> Dict[str, Any]:
    """Extract data models and entities"""

@lru_cache(maxsize=32)
def extract_components(project_path: str) -> Dict[str, Any]:
    """Extract UI components"""
```

**Features:**
- Calls `coderef scan` command
- Parses JSON output
- Caches results with LRU cache
- Graceful fallback on failure

**Dependencies:** cli_utils, logger_config

---

## 4. Validation Components

### validation.py

**Purpose:** Input validation at API boundary (REF-003)

**Functions:**
- `validate_project_path_input(path)` - Path exists and is directory
- `validate_version_format(version)` - Matches x.y.z pattern
- `validate_template_name_input(name)` - Template exists
- `validate_changelog_inputs(args)` - Complete changelog data

**Error Handling:** Raises descriptive ValueError on validation failure

---

### error_responses.py

**Purpose:** Consistent error response formatting (ARCH-001)

**Class:**
```python
class ErrorResponse:
    @staticmethod
    def invalid_input(message: str) -> list[TextContent]:
        """Format invalid input error"""

    @staticmethod
    def file_not_found(path: str) -> list[TextContent]:
        """Format file not found error"""

    @staticmethod
    def validation_error(details: str) -> list[TextContent]:
        """Format validation error"""
```

**Format:** User-friendly error messages with context

---

## 5. Utility Components

### cli_utils.py

**Purpose:** @coderef/core CLI integration

**Functions:**
- `validate_cli_available()` - Check CLI exists (PATH first, then hardcoded)
- `get_cli_path()` - Return CLI executable path
- `run_coderef_command(cmd, args)` - Execute CLI with timeout

**Features:**
- Subprocess management
- JSON parsing
- Error handling
- Timeout support (120s default)

**CLI Detection Order:**
1. Check `coderef --version` in PATH (global npm install)
2. Fallback to hardcoded path `C:\...\cli.js`

---

### logger_config.py

**Purpose:** Centralized logging configuration

**Components:**
- `logger` - Global logger instance
- `log_tool_call(tool_name, args)` - Log MCP tool invocations
- `@log_invocation` decorator - Auto-log tool calls

**Format:** Structured logging with timestamps, levels, context

---

### constants.py

**Purpose:** Global constants (REF-002)

**Classes:**
```python
class Paths:
    TEMPLATES_DIR = "templates/power"
    TOOL_TEMPLATES_DIR = "templates/tools"
    OUTPUT_DIR = "coderef/foundation-docs"

class Files:
    CHANGELOG = "CHANGELOG.json"
    STANDARDS_INDEX = "standards-index.md"
```

---

### type_defs.py

**Purpose:** TypedDict and Literal type definitions

**Types:**
- `TemplateDict` - Template metadata
- `WorkflowStepDict` - Generation step
- `ChangeType` - Changelog change types
- `Severity` - Severity levels
- `ScanDepth` - Standards scan depth

**Usage:** Type hints for better IDE support and validation

---

## 6. Decorator Components

### Logging Decorators

```python
@log_invocation
def handler_function(args):
    """Automatically logs entry/exit"""
```

**Purpose:** Trace tool invocations

---

### Error Handling Decorators

```python
@mcp_error_handler
def handler_function(args):
    """Catches exceptions and formats errors"""
```

**Purpose:** Consistent error responses

---

## 7. Test Components

### tests/unit/

**Test Suites:**
- `test_server.py` - Server initialization
- `test_tool_handlers.py` - Handler logic
- `test_generators.py` - Generator output
- `test_validation.py` - Input validation

### tests/integration/

**Integration Tests:**
- `test_mcp_workflows.py` - End-to-end workflows
- `test_coderef_foundation_docs.py` - Context injection
- `test_tools_integration.py` - Tool integration

**Coverage:** 27/30 tests passing (90% coverage)

---

## 8. Template Components

### templates/power/

**POWER Framework Templates:**
- `readme.txt` - Project overview
- `architecture.txt` - System architecture
- `api.txt` - API reference
- `schema.txt` - Data schemas
- `components.txt` - Component structure
- `my-guide.txt` - Development guide
- `user-guide.txt` - User documentation

**Format:** Text files with embedded metadata

---

## Component Dependencies

```
server.py
    → tool_handlers.py
        → generators/ (all generators)
            → base_generator.py
            → foundation_generator.py
            → changelog_generator.py
            → standards_generator.py
            → audit_generator.py
            → quickref_generator.py
        → extractors.py
            → cli_utils.py
        → validation.py
        → error_responses.py
        → logger_config.py
```

---

## Design Patterns

**Factory Pattern:** BaseGenerator creates specific generators

**Decorator Pattern:** `@log_invocation`, `@mcp_error_handler`

**Strategy Pattern:** Different generators for different doc types

**Template Method:** BaseGenerator defines workflow, subclasses implement details

---

## References

- **Component Implementations:** All files in project root + `generators/`
- **Architectural Principles:** ARCHITECTURE.md
- **API Specifications:** API.md
- **Type Definitions:** `type_defs.py`

---

*Generated: 2025-12-27*
*For AI Agents: All components follow single responsibility principle*
