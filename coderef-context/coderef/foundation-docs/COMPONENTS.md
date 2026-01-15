---
generated_by: coderef-docs
template: components
date: "2026-01-14T01:20:47Z"
doc_type: components
feature_id: foundation-docs
workorder_id: foundation-docs-001
task: Generate foundation documentation
agent: Claude Code AI
_uds:
  validation_score: 95
  validated_at: "2026-01-14T01:20:47Z"
  validator: UDSValidator
---

# Components Reference

**[Date]** 2026-01-14 | **[Version]** 2.0.0

## Purpose

This document catalogs all modules, classes, functions, and components in the CodeRef Context MCP server codebase. It provides a comprehensive reference for understanding the codebase structure and component relationships.

## Overview

The CodeRef Context server is organized into three main modules:
1. **Server** (`server.py`): MCP server entry point and tool definitions
2. **Reader** (`src/coderef_reader.py`): Data access layer for `.coderef/` files
3. **Handlers** (`src/handlers_refactored.py`): Async handlers for each MCP tool
4. **Processors** (`processors/export_processor.py`): Export operation processor

## Core Components

### Server Module

**File**: `server.py`

**Purpose**: MCP server entry point that exposes tools to AI agents

**Key Components**:

#### `Server` Instance
```python
app = Server("coderef-context")
```

#### `list_tools()`
- **Type**: Async function
- **Purpose**: List all available MCP tools
- **Returns**: `List[Tool]` with 14 tool definitions
- **Location**: Lines 71-428

#### `call_tool(name, arguments)`
- **Type**: Async function
- **Purpose**: Route tool calls to appropriate handlers
- **Parameters**:
  - `name` (str): Tool name
  - `arguments` (dict): Tool arguments
- **Returns**: `List[TextContent]` with JSON response
- **Location**: Lines 429-472

#### `main()`
- **Type**: Async function
- **Purpose**: Start MCP server via stdio
- **Location**: Lines 473-476

---

### CodeRefReader Class

**File**: `src/coderef_reader.py`

**Purpose**: Read and query `.coderef/` data files

**Class Definition**:
```python
class CodeRefReader:
    def __init__(self, project_path: str)
```

**Properties**:
- `project_path` (Path): Project root directory
- `coderef_dir` (Path): `.coderef/` directory path

**Methods**:

#### `_load_json(filename: str) -> Any`
- **Purpose**: Load JSON file from `.coderef/` directory
- **Parameters**: `filename` (str): JSON filename
- **Returns**: Parsed JSON object
- **Raises**: `FileNotFoundError` if file doesn't exist
- **Location**: Lines 21-28

#### `_load_text(filename: str) -> str`
- **Purpose**: Load text file from `.coderef/` directory
- **Parameters**: `filename` (str): Text filename
- **Returns**: File contents as string
- **Raises**: `FileNotFoundError` if file doesn't exist
- **Location**: Lines 30-37

#### `get_index() -> List[Dict[str, Any]]`
- **Purpose**: Get all scanned elements from `index.json`
- **Returns**: List of element dictionaries
- **Location**: Lines 39-41

#### `get_graph() -> Dict[str, Any]`
- **Purpose**: Get dependency graph from `graph.json`
- **Returns**: Graph dictionary with nodes and edges
- **Location**: Lines 43-45

#### `get_context(format: str = "json") -> Any`
- **Purpose**: Get project context (JSON or markdown)
- **Parameters**: `format` (str): `"json"` or `"markdown"`
- **Returns**: Context data in requested format
- **Location**: Lines 47-52

#### `get_patterns() -> Dict[str, Any]`
- **Purpose**: Get code patterns from `reports/patterns.json`
- **Returns**: Patterns dictionary
- **Location**: Lines 54-56

#### `get_coverage() -> Dict[str, Any]`
- **Purpose**: Get test coverage from `reports/coverage.json`
- **Returns**: Coverage dictionary
- **Location**: Lines 58-60

#### `get_validation() -> Dict[str, Any]`
- **Purpose**: Get reference validation from `reports/validation.json`
- **Returns**: Validation dictionary
- **Location**: Lines 62-64

#### `get_drift() -> Dict[str, Any]`
- **Purpose**: Get drift detection from `reports/drift.json`
- **Returns**: Drift dictionary
- **Location**: Lines 66-68

#### `get_diagram(diagram_type: str, format: str) -> str`
- **Purpose**: Get diagram from `diagrams/` directory
- **Parameters**:
  - `diagram_type` (str): `"dependencies"`, `"calls"`, `"imports"`, or `"all"`
  - `format` (str): `"mermaid"` or `"dot"`
- **Returns**: Diagram content as string
- **Location**: Lines 70-73

#### `get_export(format: str) -> Any`
- **Purpose**: Get export data from `exports/` directory
- **Parameters**: `format` (str): `"json"`, `"jsonld"`, `"mermaid"`, or `"dot"`
- **Returns**: Export data
- **Location**: Lines 75-80

#### `query_elements(...) -> List[Dict[str, Any]]`
- **Purpose**: Query elements from index with filters
- **Parameters**:
  - `element_type` (Optional[str]): Filter by type
  - `name_filter` (Optional[str]): Filter by name
  - `file_filter` (Optional[str]): Filter by file
- **Returns**: Filtered list of elements
- **Location**: Lines 82-100

#### `find_element(name: str) -> Optional[Dict[str, Any]]`
- **Purpose**: Find a specific element by name
- **Parameters**: `name` (str): Element name
- **Returns**: Element dictionary or None
- **Location**: Lines 102-108

#### `get_element_relationships(element_name: str) -> Dict[str, Any]`
- **Purpose**: Get relationships for a specific element from graph
- **Parameters**: `element_name` (str): Element name
- **Returns**: Dictionary with element, dependencies, and dependents
- **Location**: Lines 110-123

#### `_find_dependents(graph: Dict, target_id: str) -> List[str]`
- **Purpose**: Find all elements that depend on target element (private helper)
- **Parameters**:
  - `graph` (Dict): Graph dictionary
  - `target_id` (str): Target node ID
- **Returns**: List of dependent node IDs
- **Location**: Lines 125-134

#### `exists() -> bool`
- **Purpose**: Check if `.coderef/` directory exists with required files
- **Returns**: True if all required files exist
- **Location**: Lines 136-139

#### `get_stats() -> Dict[str, Any]`
- **Purpose**: Get statistics about scanned codebase
- **Returns**: Statistics dictionary
- **Location**: Lines 141-161

---

### Handler Functions

**File**: `src/handlers_refactored.py`

**Purpose**: Async handlers for each MCP tool

**Handler Functions**:

#### `handle_coderef_scan(args: dict) -> List[TextContent]`
- **Purpose**: Return scan data from `.coderef/index.json`
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with elements list
- **Location**: Lines 14-50

#### `handle_coderef_query(args: dict) -> List[TextContent]`
- **Purpose**: Query relationships from `.coderef/graph.json`
- **Parameters**: `args` with `project_path`, `query_type`, `target`
- **Returns**: JSON response with query results
- **Location**: Lines 53-98

#### `handle_coderef_impact(args: dict) -> List[TextContent]`
- **Purpose**: Analyze impact from `.coderef/graph.json`
- **Parameters**: `args` with `project_path`, `element`
- **Returns**: JSON response with impact analysis
- **Location**: Lines 101-133

#### `handle_coderef_complexity(args: dict) -> List[TextContent]`
- **Purpose**: Get complexity from element data
- **Parameters**: `args` with `project_path`, `element`
- **Returns**: JSON response with complexity metrics
- **Location**: Lines 136-170

#### `handle_coderef_patterns(args: dict) -> List[TextContent]`
- **Purpose**: Get patterns from `.coderef/reports/patterns.json`
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with patterns
- **Location**: Lines 173-192

#### `handle_coderef_coverage(args: dict) -> List[TextContent]`
- **Purpose**: Get coverage from `.coderef/reports/coverage.json`
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with coverage data
- **Location**: Lines 195-214

#### `handle_coderef_context(args: dict) -> List[TextContent]`
- **Purpose**: Get context from `.coderef/context.json` or `context.md`
- **Parameters**: `args` with `project_path`, `output_format`
- **Returns**: JSON or markdown response
- **Location**: Lines 217-236

#### `handle_coderef_validate(args: dict) -> List[TextContent]`
- **Purpose**: Get validation from `.coderef/reports/validation.json`
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with validation results
- **Location**: Lines 239-258

#### `handle_coderef_drift(args: dict) -> List[TextContent]`
- **Purpose**: Get drift from `.coderef/reports/drift.json`
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with drift report
- **Location**: Lines 261-280

#### `handle_coderef_incremental_scan(args: dict) -> List[TextContent]`
- **Purpose**: Perform incremental scan (requires CLI integration)
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with scan results
- **Location**: Lines 462-526

#### `handle_coderef_diagram(args: dict) -> List[TextContent]`
- **Purpose**: Get diagram from `.coderef/diagrams/`
- **Parameters**: `args` with `project_path`, `diagram_type`, `format`
- **Returns**: Diagram content as text
- **Location**: Lines 283-298

#### `handle_coderef_tag(args: dict) -> List[TextContent]`
- **Purpose**: Add CodeRef2 tags to source files (requires CLI)
- **Parameters**: `args` with `path` and various tag options
- **Returns**: JSON response with tagging results
- **Location**: Lines 301-311

#### `handle_coderef_export(args: dict) -> List[TextContent]`
- **Purpose**: Export coderef data via export processor
- **Parameters**: `args` with `project_path`, `format`, `output_path`, `max_nodes`
- **Returns**: JSON response with export results
- **Location**: Lines 312-341

#### `handle_validate_coderef_outputs(args: dict) -> List[TextContent]`
- **Purpose**: Validate `.coderef/` files against schemas
- **Parameters**: `args` with `project_path`
- **Returns**: JSON response with validation results
- **Location**: Lines 342-461

---

### Export Processor

**File**: `processors/export_processor.py`

**Purpose**: Handles export operations for various output formats

**Functions**:

#### `export_coderef(...) -> List[TextContent]`
- **Type**: Async function
- **Purpose**: Export coderef data in specified format
- **Parameters**:
  - `cli_command` (List[str]): CLI command array
  - `project_path` (str): Absolute path to project root
  - `format` (str): Export format (`json`|`jsonld`|`mermaid`|`dot`)
  - `output_path` (Optional[str]): Output file path
  - `max_nodes` (Optional[int]): Limit on graph nodes
  - `timeout` (int): Subprocess timeout (default: 120)
- **Returns**: TextContent with export result
- **Location**: Lines 26-201

#### `validate_export_format(format: str) -> bool`
- **Type**: Function
- **Purpose**: Validate export format
- **Parameters**: `format` (str): Format to validate
- **Returns**: True if valid format
- **Location**: Lines 156-160

---

## Component Relationships

```
server.py
    ├── list_tools() → Tool definitions
    ├── call_tool() → Route to handlers
    └── main() → Start server

handlers_refactored.py
    ├── handle_coderef_scan() → CodeRefReader.get_index()
    ├── handle_coderef_query() → CodeRefReader.get_element_relationships()
    ├── handle_coderef_impact() → CodeRefReader.get_element_relationships()
    ├── handle_coderef_complexity() → CodeRefReader.find_element()
    ├── handle_coderef_patterns() → CodeRefReader.get_patterns()
    ├── handle_coderef_coverage() → CodeRefReader.get_coverage()
    ├── handle_coderef_context() → CodeRefReader.get_context()
    ├── handle_coderef_validate() → CodeRefReader.get_validation()
    ├── handle_coderef_drift() → CodeRefReader.get_drift()
    ├── handle_coderef_diagram() → CodeRefReader.get_diagram()
    ├── handle_coderef_export() → export_coderef()
    └── handle_validate_coderef_outputs() → Multiple CodeRefReader methods

coderef_reader.py
    └── CodeRefReader
        ├── _load_json() → File I/O
        ├── _load_text() → File I/O
        └── All get_* methods → Query .coderef/ files

export_processor.py
    └── export_coderef() → CLI subprocess (async)
```

---

## Module Dependencies

```
server.py
    ├── mcp.server.Server
    ├── mcp.types.Tool, TextContent
    ├── mcp.server.stdio.stdio_server
    └── src.handlers_refactored (all handlers)

handlers_refactored.py
    ├── mcp.types.TextContent
    └── src.coderef_reader.CodeRefReader

coderef_reader.py
    ├── json
    ├── pathlib.Path
    └── typing (Dict, List, Optional, Any)

export_processor.py
    ├── asyncio
    ├── json
    ├── pathlib.Path
    └── mcp.types.TextContent
```

---

## Component Statistics

Based on `.coderef/index.json` analysis:

- **Total Elements**: 250+
- **Functions**: 120+
- **Classes**: 8
- **Methods**: 122+
- **Files**: 15 Python files

**Top Files by Element Count**:
1. `server.py` - 45 elements
2. `src/handlers_refactored.py` - 14 handler functions
3. `src/coderef_reader.py` - 16 methods
4. `processors/export_processor.py` - 2 functions

---

**AI Agent Note**: All components are Python-based. No UI components exist (this is a backend MCP server). For frontend components, see the CodeRef dashboard project.
