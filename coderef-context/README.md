# coderef-context MCP Server

**Expose @coderef/core CLI tools to Claude agents as standardized MCP tools**

---

## Overview

This MCP server wraps the @coderef/core CLI commands and exposes them as tools that Claude agents can access during task execution.

### Why This Exists

Agents need real-time access to code intelligence when implementing features. Instead of building intelligence into coderef-workflow MCPs, we:

1. **Keep @coderef/core CLI** as the single source of truth for analysis
2. **Wrap CLI commands** as MCP tools
3. **Agents call tools** directly during task execution

This keeps concerns separated:
- **@coderef/core** = Analysis engine
- **packages/cli** = CLI interface
- **coderef-context MCP** = Agent tool wrapper
- **coderef-workflow MCP** = Planning & documentation

---

## Tools Exposed

### Core Tools (Agent-Focused)

1. **`/scan`** - Discover all code elements
   - Returns: Element list with types, locations, relationships
   - Use: Initial project understanding

2. **`/query`** - Query relationships
   - Types: what-calls, what-imports, depends-on, etc.
   - Use: Understanding dependencies before implementation

3. **`/impact`** - Analyze change impact
   - Returns: Affected files, risk level, recommendations
   - Use: Risk assessment before refactoring

4. **`/complexity`** - Get complexity metrics
   - Returns: LOC, cyclomatic complexity, dependencies, test coverage
   - Use: Effort estimation

5. **`/patterns`** - Discover patterns
   - Returns: Common patterns, test coverage gaps
   - Use: Learning from existing code

### Supporting Tools

6. **`/coverage`** - Test coverage analysis
7. **`/context`** - Comprehensive codebase context
8. **`/validate`** - Validate CodeRef2 references
9. **`/drift`** - Detect reference drift
10. **`/diagram`** - Generate visual diagrams

---

## Architecture

```
Claude Agent
    │
    └─ Calls MCP Tools
        │
        ├─ /scan (MCP tool)
        │   └─ subprocess → node cli.js scan
        │       └─ @coderef/core scanner
        │
        ├─ /query (MCP tool)
        │   └─ subprocess → node cli.js query
        │       └─ @coderef/core query executor
        │
        ├─ /impact (MCP tool)
        │   └─ subprocess → node cli.js impact
        │       └─ @coderef/core analyzer
        │
        └─ ... more tools
```

---

## Implementation Status

### Current Phase: Setup
- ✅ MCP server skeleton
- ✅ Tool definitions (10 tools)
- ⏳ Tool handlers (waiting for CLI_SPEC.md)

### Waiting On
**Agent task: WO-CODEREF-TOOLS-AUDIT-001**

The agent is auditing @coderef/core and packages/cli to create `CLI_SPEC.md`, which documents:
- Every CLI command
- Input parameters
- JSON output schema
- Error handling
- Examples

Once CLI_SPEC.md is ready, I'll implement all tool handlers.

---

## Development Workflow

1. **Agent creates CLI_SPEC.md** (documents all CLI commands)
2. **I implement tool handlers** (wrap CLI calls)
3. **Register in .mcp.json** (make globally available)
4. **Test with agents** (verify tool usage)

---

## Configuration

### Environment Variable

```bash
export CODEREF_CLI_PATH="/path/to/coderef-system/packages/cli"
```

Default: `C:\Users\willh\Desktop\projects\coderef-system\packages\cli`

### Installation

```bash
cd C:\Users\willh\.mcp-servers\coderef-context
pip install -e .
```

### Registration (.mcp.json)

```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:\\Users\\willh\\.mcp-servers\\coderef-context\\server.py"],
      "cwd": "C:\\Users\\willh\\.mcp-servers\\coderef-context",
      "env": {
        "CODEREF_CLI_PATH": "C:\\Users\\willh\\Desktop\\projects\\coderef-system\\packages\\cli"
      }
    }
  }
}
```

---

## Usage Example (Once Implemented)

```python
# Agent implementation task

# Step 1: Understand the project
result = await call_tool("coderef_context", "/scan", {
    "project_path": "/path/to/project"
})
# → Gets: 247 code elements

# Step 2: Find existing auth
result = await call_tool("coderef_context", "/query", {
    "query_type": "imports",
    "target": "AuthService"
})
# → Gets: 4 files importing AuthService

# Step 3: Check impact of changes
result = await call_tool("coderef_context", "/impact", {
    "element": "AuthService",
    "operation": "modify"
})
# → Gets: 10 affected files, MEDIUM risk

# Agent now implements with full intelligence ✅
```

---

## File Structure

```
coderef-context/
├── server.py                 ← MCP entry point
├── pyproject.toml           ← Package metadata
├── README.md                ← This file
├── TOOLS_REFERENCE.md       ← Complete tool specs (WIP)
├── IMPLEMENTATION_LOG.md    ← Implementation progress
└── src/
    └── (handlers will go here once ready)
```

---

## Status & Next Steps

**Current Status**: Skeleton complete, waiting for CLI audit

**Next Steps**:
1. Agent completes WO-CODEREF-TOOLS-AUDIT-001
2. Agent creates CLI_SPEC.md
3. I implement all tool handlers
4. Register in .mcp.json
5. Test with real agents

---

## Related

- **@coderef/core** - Analysis engine (TypeScript library)
- **packages/cli** - CLI wrapper (being audited)
- **coderef-workflow MCP** - Planning & docs (uses subprocess for now)
- **WO-CODEREF-TOOLS-AUDIT-001** - Agent audit task (current)
- **WO-CODEREF-CONTEXT-MCP-001** - This MCP server (current)

---

**Status**: 🟡 In Progress
**Phase**: Setup & Awaiting CLI Specification
**Owner**: Lloyd (MCP implementation)
**Blocked On**: CLI_SPEC.md from agent audit
