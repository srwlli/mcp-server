# LLOYD IMPLEMENTATION WORKORDER
## WO-CODEREF-CONTEXT-MCP-SERVER-001 (Phase 2: Implementation)

**Status:** 🟢 READY TO BEGIN
**Assigned To:** Lloyd
**Prerequisite:** WO-CODEREF-TOOLS-AUDIT-001 ✅ COMPLETE
**Start Date:** 2025-12-23
**Estimated Duration:** 2-3 days
**Blocker:** None - All prerequisites satisfied

---

## Executive Summary

The audit phase (WO-CODEREF-TOOLS-AUDIT-001) is **complete**. All CLI specifications are documented in `CLI_SPEC.md`. Your job is to implement the MCP tool handlers that wrap these CLI commands.

**What you need to do:**
1. Read `CLI_SPEC.md` to understand all 14 CLI commands
2. Implement handlers in `src/` directory (currently empty)
3. Update `server.py` to add missing 5 tools
4. Test that all tools work correctly
5. Register in `.mcp.json`

**Time estimate:** 2-3 days for complete implementation

---

## Current State

### ✅ What's Already Done

**Audit Phase Completed:**
- AUDIT-001: @coderef/core modules fully inventoried
- AUDIT-002: All 14 CLI commands audited and tested
- AUDIT-003: Gap analysis completed (96% coverage, 0 critical gaps)
- TEST-001: All 14 commands tested with real inputs
- DOC-001: CORE_TOOLS_INVENTORY.md published
- DOC-002: CLI_COMMAND_COVERAGE.md published
- DOC-003: **CLI_SPEC.md published** ⭐ YOU NEED THIS
- DOC-004: AUDIT_FINDINGS.md published

**MCP Server Skeleton:**
- ✅ `server.py` - MCP server initialized with 10 tool definitions
- ✅ `pyproject.toml` - Dependencies configured
- ✅ README.md - Overview documentation
- ✅ IMPLEMENTATION_PLAN.md - Original plan document

### ❌ What's NOT Done (Your Job)

**Missing Implementations:**
- ❌ `src/` directory is EMPTY (no handlers)
- ❌ 5 tool definitions missing from `server.py`:
  - rag-ask
  - rag-index
  - rag-config
  - update-ref
  - format-ref

**Missing Integration:**
- ❌ Not registered in `.mcp.json` (users can't access it yet)

---

## Implementation Tasks

### Task 1: Read CLI_SPEC.md (30 minutes)

**Location:** `C:\Users\willh\Desktop\projects\coderef-system\coderef\working\coderef-tools-audit\CLI_SPEC.md`

This document contains EVERYTHING you need to know about the 14 CLI commands:
- Command syntax
- All input parameters (names, types, constraints)
- Output JSON schemas (exact structure)
- Example invocations with sample output
- Error cases and error messages
- Performance characteristics

**What to look for:**
1. Command syntax: `node cli.js [command] [args] --json`
2. All flags and their types
3. JSON output structure for each command
4. Error conditions (what goes wrong and how)

---

### Task 2: Add Missing 5 Tools to server.py (1 hour)

Currently `server.py` defines 10 tools. You need to add 5 more:

1. **rag-config**
   - Description: Configure RAG system and test connectivity
   - Inputs:
     - `project_path` (string, required)
     - `test_llm` (boolean, optional) - Test LLM provider
     - `test_vector` (boolean, optional) - Test vector store
     - `test_all` (boolean, optional) - Test all connections
   - Output: Configuration status and test results

2. **rag-index**
   - Description: Index codebase for semantic search
   - Inputs:
     - `project_path` (string, required)
     - `languages` (array, optional) - Languages to index
     - `incremental` (boolean, optional) - Only index changed files
     - `force` (boolean, optional) - Force full re-index
     - `namespace` (string, optional) - Multi-tenancy namespace
   - Output: Indexing results with statistics

3. **rag-ask**
   - Description: Ask natural language questions about codebase
   - Inputs:
     - `question` (string, required) - Question in plain English
     - `project_path` (string, required) - Project to search
     - `session_id` (string, optional) - Conversation session
     - `new_session` (boolean, optional) - Start new conversation
     - `strategy` (string, optional) - Query strategy (semantic, centrality, quality, usage, public)
   - Output: Answer with sources and confidence score

4. **update-ref**
   - Description: Find and fix stale CodeRef references
   - Inputs:
     - `project_path` (string, required)
     - `fix` (boolean, optional) - Auto-fix references
   - Output: Report of updates applied

5. **format-ref**
   - Description: Normalize CodeRef reference format
   - Inputs:
     - `project_path` (string, required)
     - `fix` (boolean, optional) - Apply formatting changes
   - Output: Formatting report

**Where to add them:** In the `@app.list_tools()` function, after the existing 10 tools.

**Schema template** (reference existing tools for full structure):
```python
Tool(
    name="coderef_rag_config",
    description="Configure RAG system and test connectivity",
    inputSchema={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "description": "Path to project root"
            },
            "test_llm": {
                "type": "boolean",
                "description": "Test LLM provider connectivity",
                "default": False
            },
            # ... more properties
        },
        "required": ["project_path"]
    }
)
```

---

### Task 3: Create Tool Handlers in src/ (6-8 hours)

Create handlers for all 14 tools. The directory structure should be:

```
src/
├── handlers.py           # All handler implementations
├── utils.py             # Helper functions (CLI subprocess, JSON parsing)
└── __init__.py          # Package initialization
```

#### Handler Pattern

Each handler follows this pattern:

```python
async def handle_coderef_scan(args: dict) -> list[TextContent]:
    """
    Handler for coderef_scan tool.

    Args:
        args: Tool input parameters from MCP request

    Returns:
        List of TextContent with JSON results
    """
    # 1. Extract inputs from args dict
    project_path = args['project_path']
    languages = args.get('languages', ['ts', 'tsx', 'js', 'jsx'])
    use_ast = args.get('use_ast', True)

    # 2. Build CLI command from CLI_SPEC.md
    cmd = [
        'node',
        CLI_BIN,
        'scan',
        project_path,
        '--lang', ','.join(languages),
        '--analyzer', 'ast' if use_ast else 'regex',
        '--json'
    ]

    # 3. Execute subprocess
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # Adjust per command
            cwd=str(Path(CLI_BIN).parent.parent)  # Run from cli package
        )
    except subprocess.TimeoutExpired:
        return [TextContent(text=json.dumps({
            "error": "Command timed out",
            "command": "scan"
        }, indent=2))]
    except Exception as e:
        return [TextContent(text=json.dumps({
            "error": str(e),
            "command": "scan"
        }, indent=2))]

    # 4. Handle errors
    if result.returncode != 0:
        return [TextContent(
            text=json.dumps({
                "error": result.stderr,
                "exit_code": result.returncode
            }, indent=2),
            is_error=True
        )]

    # 5. Parse JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return [TextContent(
            text=json.dumps({
                "error": f"Invalid JSON from CLI: {e}",
                "raw_output": result.stdout[:500]  # First 500 chars
            }, indent=2),
            is_error=True
        )]

    # 6. Format response
    return [TextContent(text=json.dumps({
        "success": True,
        "tool": "scan",
        "elements_found": len(data.get('elements', [])),
        "data": data
    }, indent=2))]
```

#### Implement These Handlers

**Fast commands** (Group A - finish first):
1. `coderef_scan` - Scan code elements (20 minutes)
2. `coderef_validate` - Validate references (15 minutes)
3. `coderef_rag_config` - Configure RAG (15 minutes)

**Analysis commands** (Group B - medium complexity):
4. `coderef_query` - Query relationships (30 minutes)
5. `coderef_impact` - Change impact analysis (30 minutes)
6. `coderef_coverage` - Test coverage (20 minutes)

**Complex commands** (Group C - finish last):
7. `coderef_context` - 6-phase context generation (30 minutes)
8. `coderef_drift` - Drift detection (20 minutes)
9. `coderef_diagram` - Generate diagrams (20 minutes)
10. `coderef_complexity` - Complexity metrics (15 minutes)
11. `coderef_patterns` - Pattern discovery (15 minutes)

**RAG commands** (Group D - requires async):
12. `coderef_rag_index` - Index codebase (25 minutes - long-running)
13. `coderef_rag_ask` - Q&A (20 minutes)
14. `coderef_update_ref` - Fix references (15 minutes)
15. `coderef_format_ref` - Format references (15 minutes)

**Total estimate:** 6-8 hours of implementation

#### Special Considerations

**For long-running commands:**
- `rag-index` can take 30+ seconds
- Use appropriate timeouts (60-120 seconds)
- Consider progress reporting

**For multi-turn conversations:**
- `rag-ask` supports `--session` parameter
- Track session IDs in handler

**For commands without JSON support:**
- Text-based output: update-ref, format-ref, diagram, dashboard
- Parse text output or request JSON support from CLI team
- Document limitation in error response

---

### Task 4: Register Tool Handlers in server.py (1-2 hours)

Update `server.py` to wire handlers to the MCP protocol:

```python
# At the top of server.py, import handlers
from src.handlers import (
    handle_coderef_scan,
    handle_coderef_query,
    handle_coderef_impact,
    # ... all 14 handlers
)

# Add the @app.call_tool() decorator
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handlers."""

    handlers = {
        "coderef_scan": handle_coderef_scan,
        "coderef_query": handle_coderef_query,
        "coderef_impact": handle_coderef_impact,
        # ... all 14 mappings
    }

    if name not in handlers:
        return [TextContent(
            text=json.dumps({
                "error": f"Unknown tool: {name}",
                "available_tools": list(handlers.keys())
            }, indent=2),
            is_error=True
        )]

    try:
        return await handlers[name](arguments)
    except Exception as e:
        return [TextContent(
            text=json.dumps({
                "error": str(e),
                "tool": name
            }, indent=2),
            is_error=True
        )]
```

---

### Task 5: Test All Handlers (2-3 hours)

Create a test script `test_handlers.py`:

```python
#!/usr/bin/env python3
"""Test all coderef-context MCP handlers."""

import asyncio
import json
from src.handlers import (
    handle_coderef_scan,
    handle_coderef_query,
    # ... all handlers
)

async def test_all():
    """Test each handler with sample inputs."""

    # Test 1: Scan
    print("Testing scan...")
    result = await handle_coderef_scan({
        "project_path": "C:\\Users\\willh\\Desktop\\projects\\coderef-system\\packages\\core",
        "languages": ["ts"],
        "use_ast": True
    })
    assert result, "scan returned empty"
    data = json.loads(result[0].text)
    assert data.get("success"), f"scan failed: {data}"
    print(f"✅ Scan found {data['elements_found']} elements")

    # Test 2: Validate
    print("Testing validate...")
    result = await handle_coderef_validate({
        "project_path": "C:\\Users\\willh\\Desktop\\projects\\coderef-system\\packages\\core"
    })
    assert result, "validate returned empty"
    print("✅ Validate completed")

    # ... test all 14 handlers

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_all())
```

**Test checklist:**
- [ ] All 14 tools listed in `list_tools()`
- [ ] All 14 handlers implemented
- [ ] Handlers parse inputs correctly
- [ ] Handlers build correct CLI commands
- [ ] Handlers parse JSON output
- [ ] Handlers handle errors properly
- [ ] Long-running commands have appropriate timeouts
- [ ] JSON responses are valid
- [ ] Agents can parse responses

---

### Task 6: Fix Cross-Platform Path Issues (30 minutes)

Current problem in `server.py` line 39-42:

```python
DEFAULT_CLI_PATH = os.path.expandvars(
    r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli"
)
```

This is Windows-specific. Fix it:

```python
import os
from pathlib import Path

# Try to find CLI automatically
def find_cli_path():
    """Find coderef CLI in common locations."""
    candidates = [
        # Environment variable
        os.environ.get("CODEREF_CLI_PATH"),
        # Relative to this file
        Path(__file__).parent.parent.parent / "packages" / "cli",
        # User's home .mcp-servers location
        Path.home() / ".mcp-servers" / "coderef-context" / ".." / ".." / "packages" / "cli",
        # Hardcoded fallback (your current setup)
        r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli",
    ]

    for path in candidates:
        if path is None:
            continue
        path = Path(path).resolve()
        cli_bin = path / "dist" / "cli.js"
        if cli_bin.exists():
            return str(cli_bin)

    # If nothing found, use best guess
    return str(Path(r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli") / "dist" / "cli.js")

CLI_BIN = find_cli_path()
```

This allows:
1. Environment variable override: `CODEREF_CLI_PATH=...`
2. Auto-discovery based on file location
3. Fallback to known location

---

### Task 7: Register in .mcp.json (15 minutes)

Users can't access the server until it's registered.

**Create `.mcp.json` in your home directory:**

```bash
# Find: ~/.mcp.json or %APPDATA%\.mcp.json (on Windows)
```

**Add entry:**

```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": [
        "-m",
        "coderef_context.server"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\willh\\.mcp-servers\\coderef-context"
      }
    }
  }
}
```

Or if installed as a package:
```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "coderef-context"
    }
  }
}
```

---

## Detailed Implementation Guide

### Step 1: Create src/utils.py

Shared utilities for all handlers:

```python
"""Utility functions for MCP handlers."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Tuple

CLI_BIN = "node /path/to/cli.js"  # Set from server.py

async def run_cli_command(
    command: str,
    args: list[str],
    timeout: int = 30
) -> Tuple[int, str, str]:
    """
    Run a CLI command and return exit code, stdout, stderr.

    Args:
        command: CLI command name (scan, query, etc)
        args: List of command arguments
        timeout: Command timeout in seconds

    Returns:
        (exit_code, stdout, stderr)
    """
    cmd = ["node", CLI_BIN, command] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path(CLI_BIN).parent.parent)
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


async def format_success(tool: str, data: dict) -> str:
    """Format a successful response."""
    return json.dumps({
        "success": True,
        "tool": tool,
        "data": data
    }, indent=2)


async def format_error(tool: str, error: str, exit_code: int = 1) -> str:
    """Format an error response."""
    return json.dumps({
        "success": False,
        "tool": tool,
        "error": error,
        "exit_code": exit_code
    }, indent=2)
```

### Step 2: Create src/handlers.py

All 14 handler implementations. **Start with this template:**

```python
"""MCP tool handlers for coderef-context."""

import json
from typing import Any
from mcp.types import TextContent
from .utils import run_cli_command, format_success, format_error

# Handler template
async def handle_coderef_TOOLNAME(args: dict) -> list[TextContent]:
    """
    Handler for coderef_TOOLNAME tool.

    See CLI_SPEC.md for complete specification.
    """
    try:
        # 1. Validate and extract inputs
        project_path = args.get('project_path')
        if not project_path:
            return [TextContent(
                text=await format_error('TOOLNAME', 'project_path is required'),
                is_error=True
            )]

        # 2. Build CLI arguments
        cli_args = [
            project_path,
            '--json'  # Always request JSON
        ]

        # Add optional arguments per CLI_SPEC.md
        # if 'param_name' in args:
        #     cli_args.append(f'--flag-name={args["param_name"]}')

        # 3. Execute CLI command
        exit_code, stdout, stderr = await run_cli_command(
            'COMMAND_NAME',  # From CLI_SPEC.md
            cli_args,
            timeout=30  # Adjust per command
        )

        # 4. Handle errors
        if exit_code != 0:
            return [TextContent(
                text=await format_error('TOOLNAME', stderr, exit_code),
                is_error=True
            )]

        # 5. Parse JSON output
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return [TextContent(
                text=await format_error('TOOLNAME', f'Invalid JSON output: {stdout[:200]}'),
                is_error=True
            )]

        # 6. Return formatted response
        return [TextContent(text=await format_success('TOOLNAME', data))]

    except Exception as e:
        return [TextContent(
            text=await format_error('TOOLNAME', str(e)),
            is_error=True
        )]

# Now implement all 14 handlers using this pattern...
```

---

## Reference: CLI Command Details

Quick reference for all 14 commands (from CLI_SPEC.md):

| Tool | Command | Timeout | Key Args |
|------|---------|---------|----------|
| scan | `scan` | 30s | path, --lang, --analyzer |
| query | `query` | 10s | element-name, --type |
| impact | `impact` | 15s | element-name, --depth |
| complexity | `complexity` | 10s | path |
| patterns | `patterns` | 20s | path |
| coverage | `coverage` | 10s | path |
| context | `context` | 30s | path, --phase |
| validate | `validate` | 10s | path |
| drift | `drift` | 30s | path, --fix |
| diagram | `diagram` | 15s | path, --format |
| rag-config | `rag-config` | 5s | --test-llm, --test-vector |
| rag-index | `rag-index` | 120s | path, --lang, --incremental |
| rag-ask | `rag-ask` | 20s | question, --session |
| update-ref | `update-ref` | 30s | path, --fix |
| format-ref | `format-ref` | 20s | path, --fix |

**Note:** See `CLI_SPEC.md` for complete details on each command.

---

## Testing Your Implementation

### Unit Test

```bash
cd C:\Users\willh\.mcp-servers\coderef-context
python -m pytest test_handlers.py -v
```

### Integration Test

```bash
# Start the MCP server
python -m coderef_context.server

# In another terminal, test with actual agents
# Once registered in .mcp.json, agents can call:
# /scan project_path="..."
# /query project_path="..." query_type="calls-me"
# etc.
```

### Manual Test

```python
import asyncio
from src.handlers import handle_coderef_scan

result = asyncio.run(handle_coderef_scan({
    "project_path": "C:\\Users\\willh\\Desktop\\projects\\coderef-system\\packages\\core",
    "languages": ["ts"],
    "use_ast": True
}))

print(result[0].text)
```

---

## Troubleshooting

### Issue: "CLI not found"
**Fix:** Update `CLI_BIN` path in `server.py` or set `CODEREF_CLI_PATH` environment variable

### Issue: "Node not found"
**Fix:** Make sure Node.js is in PATH: `node --version` should work

### Issue: "Subprocess timeout"
**Fix:** Increase timeout for long-running commands (rag-index, context, etc.)

### Issue: "Invalid JSON from CLI"
**Fix:** Verify CLI command supports `--json` flag. See CLI_SPEC.md

### Issue: "Python module not found"
**Fix:** Make sure MCP SDK is installed: `pip install mcp`

---

## Success Criteria

When you're done, these should all be true:

- [ ] All 14 tool definitions in `server.py` with correct input schemas
- [ ] All 14 handlers implemented in `src/handlers.py`
- [ ] All handlers correctly parse CLI output
- [ ] Error handling works for all commands
- [ ] Long-running commands have appropriate timeouts
- [ ] Registered in `.mcp.json`
- [ ] Test script passes for all handlers
- [ ] Agents can call all tools and get results
- [ ] Cross-platform path handling fixed

---

## Files You'll Create/Modify

**Create:**
- `src/__init__.py` - Package initialization (can be empty)
- `src/utils.py` - Shared utilities
- `src/handlers.py` - All 14 handlers
- `test_handlers.py` - Test script
- `LLOYD_IMPLEMENTATION_NOTES.md` - Document any special handling

**Modify:**
- `server.py` - Add 5 missing tool definitions + call_tool() handler + imports
- `pyproject.toml` - If you add test dependencies

---

## Next Steps

1. **Read CLI_SPEC.md** to understand all commands
2. **Create src/ directory** with utils.py and handlers.py
3. **Implement handlers** - Start with fast ones (scan, validate, rag-config)
4. **Update server.py** - Add missing tools and wire handlers
5. **Test** - Run test script to verify all handlers
6. **Register** - Add to .mcp.json
7. **Validate** - Ask agents to use tools in real tasks

---

## Questions?

All specifications are in:
- `CLI_SPEC.md` - Command specifications
- `AUDIT_FINDINGS.md` - Gap analysis and recommendations
- `CORE_TOOLS_INVENTORY.md` - What tools are available
- `CLI_COMMAND_COVERAGE.md` - Coverage analysis

---

## Summary

You have everything you need:
- ✅ Complete CLI specifications
- ✅ MCP server skeleton
- ✅ Clear understanding of architecture
- ✅ Test subject (coderef-context itself)

Just implement the 14 handlers and you're done. Good luck!

---

**Document Created:** 2025-12-24
**Based On:** WO-CODEREF-TOOLS-AUDIT-001 (COMPLETE)
**Status:** Ready to implement
