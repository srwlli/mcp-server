# Components Documentation

**Project:** coderef-context MCP Server
**Framework:** Python MCP Server (asyncio-based)
**Version:** 1.1.0
**Last Updated:** 2025-12-30
**Status:** ✅ Production

---

## Purpose

This document catalogs the reusable components (tool handlers, utilities, and patterns) within the coderef-context MCP server. It provides a reference for understanding the modular architecture and how to extend the server with new tools or functionality.

**Note:** This is a Python server (not a UI framework like React), so "components" refers to **modular code units** (functions, classes, patterns) rather than UI components.

---

## Overview

The coderef-context server follows a **handler-based architecture** where each MCP tool is implemented as an independent async handler function. This modular design allows:
- Easy addition of new tools (add handler + registration)
- Independent testing of each tool
- Consistent error handling patterns
- Parallel execution of multiple tool calls

---

## What: Component Inventory

### 1. Core Components

#### 1.1 MCP Server (server.py)

**Purpose:** Main entry point and MCP protocol implementation

**Key Responsibilities:**
- Register MCP tools via `@app.list_tools()`
- Route tool calls to appropriate handlers via `@app.call_tool()`
- Manage server lifecycle (startup, shutdown)

**Code Example:**
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("coderef-context")

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(name="coderef_scan", description="...", inputSchema={...}),
        # ... 10 more tools
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "coderef_scan":
        return await handle_coderef_scan(arguments)
    # ... route to other handlers
```

**Dependencies:** `mcp`, `mcp.server.stdio`

---

#### 1.2 CLI Command Manager (get_cli_command)

**Purpose:** Smart CLI path detection and fallback logic

**Logic Flow:**
1. Check if `coderef` is globally installed (via `where` on Windows, `which` on Unix)
2. Test if global install actually works (`coderef --version`)
3. Fall back to local development path (`CODEREF_CLI_PATH` environment variable)
4. Final fallback: Try `coderef` command (may fail if not installed)

**Code Example:**
```python
def get_cli_command():
    """Get the CLI command, checking global install first."""
    try:
        result = subprocess.run(
            ["where", "coderef"] if os.name == "nt" else ["which", "coderef"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            test_result = subprocess.run(["coderef", "--version"], capture_output=True, timeout=5)
            if test_result.returncode == 0:
                return ["coderef"]
    except Exception as e:
        print(f"Global coderef check failed: {e}")

    # Fall back to local path
    cli_path = os.environ.get("CODEREF_CLI_PATH", default_path)
    cli_bin = os.path.join(cli_path, "dist", "cli.js")
    if os.path.exists(cli_bin):
        return ["node", cli_bin]

    return ["coderef"]

CLI_COMMAND = get_cli_command()
```

**Usage:** Called once at startup, result stored in `CLI_COMMAND` global

---

### 2. Tool Handler Components

All tool handlers follow a **standard async pattern**:

#### Handler Pattern Template
```python
async def handle_coderef_<tool>(args: dict) -> list[TextContent]:
    """Handle /<tool> tool - <description>.

    Uses async subprocess to prevent blocking the event loop.
    Timeout: <N>s (allows for <use case>).
    """
    # 1. Extract and validate arguments
    project_path = args.get("project_path", ".")
    param1 = args.get("param1")
    param2 = args.get("param2", default_value)

    if not required_param:
        return [TextContent(type="text", text="Error: required_param is required")]

    # 2. Build CLI command
    cmd = [
        *CLI_COMMAND, "<cli-command>",
        project_path,
        "--flag1", param1,
        "--flag2", str(param2),
        "--json"
    ]

    try:
        # 3. Execute async subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_path  # Optional: set working directory
        )

        # 4. Wait with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return [TextContent(type="text", text="Error: Timeout (120s exceeded)")]

        # 5. Check return code
        if process.returncode != 0:
            return [TextContent(type="text", text=f"Error: {stderr.decode()}")]

        # 6. Parse JSON output (with error handling)
        try:
            stdout_text = stdout.decode()
            # Skip CLI progress messages before JSON
            json_start = stdout_text.find('[') or stdout_text.find('{')
            if json_start >= 0:
                stdout_text = stdout_text[json_start:]
            data = json.loads(stdout_text)

            # 7. Return structured response
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "result_field": data
            }, indent=2))]
        except json.JSONDecodeError as e:
            return [TextContent(type="text", text=f"JSON parse error: {str(e)}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**Key Properties:**
- ✅ **Async/await** - Non-blocking subprocess execution
- ✅ **Timeout handling** - Prevents infinite hangs (120s default)
- ✅ **Error handling** - Graceful degradation with clear error messages
- ✅ **JSON parsing** - Skips CLI progress messages, validates JSON
- ✅ **Structured responses** - Consistent `{success: true, ...}` format

---

#### 2.1 Scan Handler (handle_coderef_scan)

**Purpose:** Discover all code elements in a project

**Inputs:**
- `project_path` (required)
- `languages` (optional, default: ["ts", "tsx", "js", "jsx"])
- `use_ast` (optional, default: true)

**CLI Command Built:**
```bash
coderef scan <project_path> --lang ts,tsx --json [--ast]
```

**Output Structure:**
```python
{
  "success": True,
  "elements_found": 247,
  "elements": [
    {"name": "ThemeProvider", "type": "component", "file": "src/theme/ThemeProvider.tsx", "line": 10}
  ]
}
```

**Code Location:** server.py:434-494

---

#### 2.2 Query Handler (handle_coderef_query)

**Purpose:** Query code relationships (calls, imports, dependencies)

**Inputs:**
- `project_path` (required)
- `query_type` (required: calls, calls-me, imports, imports-me, depends-on, depends-on-me)
- `target` (required: element to query)
- `max_depth` (optional, default: 3)

**CLI Command Built:**
```bash
coderef query <target> --type <type> --depth <depth> --format json
```

**Output Structure:**
```python
{
  "success": True,
  "query_type": "calls-me",
  "target": "login",
  "results": [
    {"from": "CheckoutComponent", "to": "PaymentGateway", "type": "import", "file": "..."}
  ]
}
```

**Code Location:** server.py:497-560

---

#### 2.3 Impact Handler (handle_coderef_impact)

**Purpose:** Analyze impact of changing a code element

**Inputs:**
- `project_path` (required)
- `element` (required: element to analyze)
- `operation` (optional: modify, delete, refactor)
- `max_depth` (optional, default: 3)

**CLI Command Built:**
```bash
coderef impact <element> --depth <depth> --format json
```

**Output Structure:**
```python
{
  "success": True,
  "element": "AuthService",
  "operation": "refactor",
  "impact": {
    "affected_files": 12,
    "risk_level": "MEDIUM",
    "ripple_effects": [...]
  }
}
```

**Code Location:** server.py:563-618

---

#### 2.4 Complexity Handler (handle_coderef_complexity)

**Purpose:** Get complexity metrics for a code element

**Inputs:**
- `project_path` (required)
- `element` (required)

**CLI Command Built:**
```bash
coderef context <project_path> --lang ts,tsx,js,jsx --json
```

**Note:** Complexity is derived from context generation (no dedicated CLI command)

**Code Location:** server.py:621-676

---

#### 2.5 Patterns Handler (handle_coderef_patterns)

**Purpose:** Discover code patterns and test coverage gaps

**Inputs:**
- `project_path` (required)
- `pattern_type` (optional)
- `limit` (optional, default: 10)

**CLI Command Built:**
```bash
coderef context <project_path> --lang ts,tsx,js,jsx --json
```

**Note:** Patterns are extracted from context generation's `testPatterns` field

**Code Location:** server.py:679-730

---

#### 2.6 Coverage Handler (handle_coderef_coverage)

**Purpose:** Analyze test coverage

**Inputs:**
- `project_path` (required)
- `format` (optional: summary, detailed)

**CLI Command Built:**
```bash
coderef coverage --format json
```

**Code Location:** server.py:733-779

---

#### 2.7 Context Handler (handle_coderef_context)

**Purpose:** Generate comprehensive codebase context

**Inputs:**
- `project_path` (required)
- `languages` (optional)
- `output_format` (optional: json, markdown, both)

**CLI Command Built:**
```bash
coderef context <project_path> --lang ts,tsx,js,jsx
```

**Code Location:** server.py:782-831

---

#### 2.8 Validate Handler (handle_coderef_validate)

**Purpose:** Validate CodeRef2 references in codebase

**Inputs:**
- `project_path` (required)
- `pattern` (optional, default: "**/*.ts")

**CLI Command Built:**
```bash
coderef validate <project_path> --pattern <pattern> --format json
```

**Code Location:** server.py:834-883

---

#### 2.9 Drift Handler (handle_coderef_drift)

**Purpose:** Detect drift between CodeRef index and current code

**Inputs:**
- `project_path` (required)
- `index_path` (optional, default: ".coderef-index.json")

**CLI Command Built:**
```bash
coderef drift <project_path> --index <index_path> --format json
```

**Code Location:** server.py:886-934

---

#### 2.10 Diagram Handler (handle_coderef_diagram)

**Purpose:** Generate visual dependency diagrams

**Inputs:**
- `project_path` (required)
- `diagram_type` (optional: dependencies, calls, imports, all)
- `format` (optional: mermaid, dot)
- `depth` (optional, default: 2)

**CLI Command Built:**
```bash
coderef diagram --format <format> --depth <depth>
```

**Special Handling:** Returns text directly for mermaid/dot, parses JSON for json format

**Code Location:** server.py:937-994

---

#### 2.11 Tag Handler (handle_coderef_tag)

**Purpose:** Add CodeRef2 tags to source files

**Inputs:**
- `path` (required: file or directory path)
- `dry_run`, `force`, `verbose`, `update_lineno`, `include_private` (optional boolean flags)
- `lang`, `exclude` (optional string parameters)

**CLI Command Built:**
```bash
coderef tag <path> [--dry-run] [--force] [--verbose] [--update-lineno] [--include-private] [--lang <langs>] [--exclude <patterns>]
```

**Special Handling:** Returns plain text output (not JSON)

**Code Location:** server.py:997-1054

---

### 3. Utility Components

#### 3.1 JSON Parser with Progress Skipping

**Purpose:** Parse CLI JSON output while ignoring progress messages

**Pattern:**
```python
stdout_text = stdout.decode()
# Skip lines until we find JSON array or object
json_start = stdout_text.find('[')
if json_start == -1:
    json_start = stdout_text.find('{')
if json_start >= 0:
    stdout_text = stdout_text[json_start:]
data = json.loads(stdout_text)
```

**Why:** @coderef/core CLI may output progress messages before JSON

**Used By:** All handlers except diagram/tag (which return text)

---

#### 3.2 Async Subprocess Pattern

**Purpose:** Non-blocking subprocess execution with timeout

**Pattern:**
```python
process = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    cwd=project_path  # Optional
)

try:
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=120
    )
except asyncio.TimeoutError:
    process.kill()
    await process.wait()
    return [TextContent(type="text", text="Error: Timeout")]
```

**Why:** Prevents event loop blocking, allows concurrent tool calls

**Used By:** All 11 tool handlers

---

## Why: Component Design Decisions

### Decision 1: Handler Functions (Not Classes)
**Why:** Simpler, functional approach; no shared state needed
**Benefit:** Easy to test, no side effects, clear inputs/outputs
**Alternative Rejected:** Class-based handlers (unnecessary complexity)

### Decision 2: Async/Await Throughout
**Why:** MCP protocol is async, subprocess I/O is async
**Benefit:** Non-blocking, supports concurrent agent requests
**Alternative Rejected:** Threading (more complex, less Pythonic)

### Decision 3: Subprocess Isolation
**Why:** Separate Node.js CLI from Python MCP server
**Benefit:** One CLI crash doesn't crash server, clean separation
**Alternative Rejected:** In-process CLI (would require Node.js bridge)

### Decision 4: Consistent Error Handling
**Why:** All handlers follow same pattern (try/except, timeout, JSON parse)
**Benefit:** Predictable behavior, easier debugging
**Alternative Rejected:** Per-handler error handling (inconsistent UX)

---

## When: Adding New Components

### How to Add a New Tool Handler

1. **Define Tool Schema** (in `@app.list_tools()`)
```python
Tool(
    name="coderef_newtool",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "..."},
            "param1": {"type": "string", "description": "..."}
        },
        "required": ["project_path"]
    }
)
```

2. **Add Handler Function**
```python
async def handle_coderef_newtool(args: dict) -> list[TextContent]:
    """Handle /newtool tool - description."""
    project_path = args.get("project_path", ".")
    param1 = args.get("param1")

    cmd = [*CLI_COMMAND, "newtool", project_path, "--param1", param1, "--json"]

    # ... follow async subprocess pattern ...
```

3. **Register in call_tool Router**
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "coderef_newtool":
            return await handle_coderef_newtool(arguments)
        # ... other handlers ...
```

4. **Test with Real CLI**
```python
# Manual test
python server.py
# In another terminal:
echo '{"tool": "coderef_newtool", "args": {"project_path": "/path/to/project"}}' | python -m mcp.client
```

---

## Examples

### Example 1: Using Scan Handler
```python
# Agent calls scan tool
args = {
    "project_path": "/Users/dev/frontend-app",
    "languages": ["ts", "tsx"],
    "use_ast": True
}

response = await handle_coderef_scan(args)
# Returns:
# [TextContent(type="text", text='{"success": true, "elements_found": 247, ...}')]
```

---

### Example 2: Using Query Handler
```python
# Agent calls query tool
args = {
    "project_path": "/Users/dev/app",
    "query_type": "calls-me",
    "target": "login"
}

response = await handle_coderef_query(args)
# Returns:
# [TextContent(type="text", text='{"success": true, "results": [...]}')]
```

---

### Example 3: Error Handling Pattern
```python
# Timeout scenario
args = {"project_path": "/very/large/project"}

response = await handle_coderef_scan(args)
# After 120s:
# [TextContent(type="text", text="Error: Scan timeout (120s exceeded)")]

# CLI not found scenario
response = await handle_coderef_scan(args)
# [TextContent(type="text", text="Error: [Errno 2] No such file or directory: 'coderef'")]
```

---

## State Management

**Server State:** Stateless
- No shared state between tool calls
- Each handler is independent
- No caching (intentional for accuracy)

**CLI State:** External
- @coderef/core CLI may maintain `.coderef-index.json` cache
- MCP server doesn't manage this state
- Fresh subprocess on each tool call

---

## References

- **[API.md](API.md)** - API endpoint documentation (tool schemas)
- **[SCHEMA.md](SCHEMA.md)** - Data schema definitions (input/output types)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (component interactions)
- **[server.py](../server.py)** - Full implementation source code

---

## AI Agent Instructions

**When extending this server:**
1. Follow the handler pattern template exactly (async, timeout, JSON parse, error handling)
2. Register new tools in both `list_tools()` and `call_tool()` router
3. Test with real @coderef/core CLI before committing
4. Document new tools in API.md and update SCHEMA.md

**When debugging handlers:**
1. Check CLI command construction first (print `cmd` variable)
2. Run CLI command manually to verify it works standalone
3. Check timeout duration (large projects need more time)
4. Verify JSON parsing logic (skip progress messages correctly)

**Best practices:**
- Keep handlers pure (no side effects, no shared state)
- Use descriptive error messages (help agents diagnose issues)
- Always validate required parameters before subprocess execution
- Return structured JSON (consistency across all tools)

---

**Generated:** 2025-12-30
**Maintained by:** coderef-context MCP Server
**For AI Agents:** This component reference helps you understand the modular architecture and extend the server with new code intelligence tools.
