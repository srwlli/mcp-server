# Architecture Documentation

**Project:** coderef-context MCP Server
**Version:** 1.1.0
**Last Updated:** 2025-12-30
**Status:** ✅ Production

---

## Purpose

This document describes the system architecture of the coderef-context MCP server. It explains the design decisions, module boundaries, data flow, technology stack, and integration points with the broader CodeRef ecosystem.

---

## Overview

The coderef-context server is a **Python-based MCP (Model Context Protocol) server** that exposes code intelligence tools from the @coderef/core CLI to AI agents. It acts as a bridge between:
- **AI Agents** (Claude, GPT, etc.) via MCP protocol
- **@coderef/core** (TypeScript analysis engine) via Node.js subprocess

**Architecture Style:** Microservice (single-purpose server in multi-server ecosystem)
**Communication:** Async I/O (stdio-based MCP protocol + subprocess)
**State Management:** Stateless (no persistent storage)

---

## What: System Topology

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI Agent (Claude)                        │
│                     (Persona: Ava, Marcus, etc.)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol (JSON-RPC 2.0)
                             │ Transport: stdio (stdin/stdout)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   coderef-context MCP Server                     │
│                        (Python, asyncio)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  MCP Server Core (server.py)                             │   │
│  │  - Tool registration (@app.list_tools)                   │   │
│  │  - Tool routing (@app.call_tool)                         │   │
│  │  - Error handling & validation                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────────────────▼────────────────────────────────┐  │
│  │  Tool Handlers (11 async functions)                       │  │
│  │  - handle_coderef_scan                                    │  │
│  │  - handle_coderef_query                                   │  │
│  │  - handle_coderef_impact                                  │  │
│  │  - ... (8 more handlers)                                  │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │ Subprocess (asyncio)
                              │ Commands: CLI_COMMAND + args
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    @coderef/core CLI                             │
│                   (TypeScript/Node.js)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CLI Commands (via dist/cli.js)                          │   │
│  │  - scan, query, impact, complexity                       │   │
│  │  - patterns, coverage, context                           │   │
│  │  - validate, drift, diagram, tag                         │   │
│  └──────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              │ File I/O + AST parsing
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Project Codebase                          │
│           (TypeScript, JavaScript, React, etc.)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Module Boundaries

#### Layer 1: MCP Protocol Layer (server.py)
**Responsibilities:**
- Accept MCP tool calls via stdin (JSON-RPC 2.0)
- Validate input schemas
- Route to appropriate tool handler
- Return responses via stdout

**Key Components:**
- `@app.list_tools()` - Tool registration
- `@app.call_tool()` - Tool routing
- `get_cli_command()` - CLI path detection

**Dependencies:** `mcp`, `mcp.server.stdio`

---

#### Layer 2: Tool Handler Layer (server.py:434-1054)
**Responsibilities:**
- Parse tool arguments
- Build CLI commands
- Execute async subprocess
- Parse JSON responses
- Handle errors (timeout, CLI failure, JSON parse)

**Key Components:**
- 11 async handler functions (handle_coderef_scan, etc.)
- Shared patterns: async subprocess, timeout, JSON parse

**Dependencies:** `asyncio`, `subprocess`, `json`

---

#### Layer 3: CLI Subprocess Layer (@coderef/core)
**Responsibilities:**
- Perform actual code analysis (AST parsing, dependency graph, etc.)
- Execute commands (scan, query, impact, etc.)
- Return structured JSON output

**Key Components:**
- CLI commands (scan, query, impact, complexity, patterns, etc.)
- AST parser (TypeScript analysis)
- Dependency graph engine

**Dependencies:** `@coderef/core` (external TypeScript package)

---

#### Layer 4: Codebase Layer (User's Project)
**Responsibilities:**
- Provide source code for analysis
- Maintain CodeRef2 index (`.coderef-index.json`)

**Key Components:**
- Source files (.ts, .tsx, .js, .jsx, etc.)
- Test files
- Dependencies (node_modules, package.json)

---

### Data Flow

#### Example: Agent Calls coderef_scan

```
1. Agent Request (MCP Protocol)
   ↓
   {"tool": "coderef_scan", "args": {"project_path": "/path/to/app", "use_ast": true}}

2. MCP Server (Python)
   ↓
   - Validate: project_path exists, use_ast is boolean
   - Route to: handle_coderef_scan(args)

3. Tool Handler (Python)
   ↓
   - Build command: ["coderef", "scan", "/path/to/app", "--lang", "ts,tsx", "--json", "--ast"]
   - Execute: await asyncio.create_subprocess_exec(*cmd)
   - Wait: timeout=120s

4. CLI Subprocess (@coderef/core)
   ↓
   - Parse: Scan /path/to/app for .ts/.tsx files
   - Analyze: AST parsing to find functions, classes, components
   - Output: JSON array to stdout

5. Tool Handler (Python)
   ↓
   - Parse: json.loads(stdout_text)
   - Format: {"success": true, "elements_found": 247, "elements": [...]}
   - Return: [TextContent(type="text", text=json_output)]

6. MCP Server (Python)
   ↓
   - Send response to stdout (MCP protocol)

7. Agent Receives
   ↓
   {"success": true, "elements_found": 247, "elements": [...]}
```

---

## Why: Design Decisions

### Decision 1: Subprocess vs In-Process

**Chosen:** Subprocess-based CLI wrapping
**Why:**
- @coderef/core is TypeScript (requires Node.js runtime)
- Python MCP server is separate process (no Node.js bridge needed)
- Isolation: One CLI crash doesn't crash MCP server
- Single source of truth: CLI is canonical implementation

**Alternative Rejected:** Port @coderef/core to Python
**Why Rejected:** 6-month effort, maintenance burden, feature parity issues

---

### Decision 2: Async/Await Throughout

**Chosen:** All handlers use `async def` + `asyncio.create_subprocess_exec`
**Why:**
- MCP protocol is async (JSON-RPC 2.0)
- Subprocess I/O is inherently async
- Allows concurrent tool calls (multiple agents)
- Non-blocking event loop (server stays responsive)

**Alternative Rejected:** Blocking `subprocess.run()` + threading
**Why Rejected:** Threading adds complexity, async is more Pythonic

---

### Decision 3: Stateless Server

**Chosen:** No caching, no persistent state
**Why:**
- Codebase changes frequently during development
- Stale analysis could lead to wrong decisions
- Agents need latest truth (not cached results)
- Simpler to manage (no cache invalidation logic)

**Alternative Rejected:** LRU cache with TTL
**Why Rejected:** Added complexity, unclear invalidation strategy

---

### Decision 4: 120s Timeout Per Tool

**Chosen:** Fixed 120s timeout for all tools
**Why:**
- Prevents infinite hangs (if CLI crashes or loops)
- Reasonable for most projects (<100k LOC)
- Long enough for AST scans (~15-20s for 50k LOC)
- Short enough to fail fast for agents

**Alternative Rejected:** Configurable timeout per tool
**Why Rejected:** Over-engineering, 120s works for 95% of cases

---

### Decision 5: Handler-Based (Not Class-Based)

**Chosen:** Each tool is a standalone async function
**Why:**
- Simple, functional approach
- No shared state needed (stateless)
- Easy to test in isolation
- Clear input/output contract

**Alternative Rejected:** Class-based handlers with inheritance
**Why Rejected:** Unnecessary complexity, no code reuse benefit

---

## When: Integration Points

### Integration with coderef-workflow

**Use Case:** Planning phase (section 0: PREPARATION)

**Flow:**
```
coderef-workflow (Python MCP Server)
    ├─ Calls: coderef_scan to discover existing code
    ├─ Calls: coderef_query to understand dependencies
    ├─ Calls: coderef_impact to assess refactoring risk
    └─ Uses results to populate plan.json sections:
        - 3_CURRENT_STATE_ANALYSIS
        - 2_RISK_ASSESSMENT
        - 6_IMPLEMENTATION_PHASES
```

**Communication:** Both servers use MCP protocol (can call each other via MCP client)

---

### Integration with coderef-personas

**Use Case:** Agent execution (tasks)

**Flow:**
```
Agent (Ava, Marcus, etc.)
    ├─ Activates via: /ava, /marcus (slash commands)
    ├─ During task execution:
    │   ├─ Calls: coderef_query ("What does this depend on?")
    │   ├─ Calls: coderef_impact ("What breaks if I change this?")
    │   └─ Calls: coderef_complexity ("How complex is this?")
    └─ Makes informed decisions based on code intelligence
```

**Communication:** Personas call coderef-context tools via MCP protocol

---

### Integration with coderef-docs

**Use Case:** Foundation doc generation

**Flow:**
```
coderef-docs (Python MCP Server)
    ├─ Calls: coderef_scan to extract API endpoints
    ├─ Calls: coderef_scan to extract schema entities
    ├─ Calls: coderef_scan to extract UI components
    └─ Populates templates:
        - API.md (with real endpoints)
        - SCHEMA.md (with real data models)
        - COMPONENTS.md (with real UI components)
```

**Communication:** Both servers use MCP protocol

---

### Integration with @coderef/core

**Use Case:** All tool operations

**Flow:**
```
coderef-context MCP Server
    ├─ Detects CLI path via get_cli_command()
    │   ├─ Check global: coderef --version
    │   ├─ Check local: $CODEREF_CLI_PATH/dist/cli.js
    │   └─ Fallback: "coderef" command
    │
    ├─ Executes CLI commands via subprocess:
    │   ├─ coderef scan <path> --json --ast
    │   ├─ coderef query <target> --type <type> --json
    │   └─ ... (11 commands total)
    │
    └─ Parses JSON output and returns to agent
```

**Communication:** Subprocess stdio (stdin/stdout)

---

## Technology Stack

### Python Stack

**Core:**
- Python 3.11+ (async/await, type hints)
- `mcp` - MCP protocol implementation
- `asyncio` - Async subprocess execution
- `json` - JSON parsing/serialization

**Development:**
- `pytest` - Unit testing
- `mypy` - Type checking (future)
- `black` - Code formatting (future)

---

### External Dependencies

**@coderef/core:**
- TypeScript/Node.js
- AST parsing (ts-morph, babel-parser)
- Dependency graph analysis
- Pattern detection

**Installation:**
- Global: `npm install -g @coderef/core`
- Local: `CODEREF_CLI_PATH=/path/to/cli`

---

### File System

**Project Structure:**
```
coderef-context/
├── server.py                    # MCP server (1073 lines)
├── pyproject.toml               # Python dependencies
├── README.md                    # User-facing docs
├── CLAUDE.md                    # AI context docs
├── coderef/
│   └── foundation-docs/
│       ├── API.md               # API reference (generated)
│       ├── SCHEMA.md            # Schema reference (generated)
│       ├── COMPONENTS.md        # Component reference (generated)
│       └── ARCHITECTURE.md      # This file
└── tests/
    └── test_server.py           # Unit tests (future)
```

---

## Deployment

### Global Deployment (.mcp.json)

```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-context/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-context",
      "env": {
        "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
      },
      "description": "MCP server exposing @coderef/core CLI tools to Claude agents",
      "tools": [
        "coderef_scan", "coderef_query", "coderef_impact",
        "coderef_complexity", "coderef_patterns", "coderef_coverage",
        "coderef_context", "coderef_validate", "coderef_drift",
        "coderef_diagram", "coderef_tag"
      ]
    }
  }
}
```

**Location:** `~/.mcp.json` (global configuration)
**Effect:** All Claude Code sessions have access to coderef-context tools

---

### Environment Configuration

**CODEREF_CLI_PATH:**
- Purpose: Override default CLI path
- Default: `C:\Users\willh\Desktop\projects\coderef-system\packages\cli`
- Usage: Set in `.mcp.json` env section

**CLI Detection Logic:**
1. Global install: `where coderef` (Windows) or `which coderef` (Unix)
2. Test global: `coderef --version`
3. Local path: `$CODEREF_CLI_PATH/dist/cli.js`
4. Fallback: Try `coderef` command (may fail if not installed)

---

## Performance Characteristics

### Latency

**Tool Response Times (typical):**
- `coderef_scan`: 5-15s (50k LOC, AST mode)
- `coderef_query`: 1-3s (dependency lookup)
- `coderef_impact`: 2-5s (impact analysis)
- `coderef_complexity`: 10-30s (full context generation)
- `coderef_patterns`: 10-30s (full context generation)
- `coderef_context`: 10-30s (full project context)
- Other tools: <5s

**Bottlenecks:**
- AST parsing (CPU-intensive, ~10-15s for 50k LOC)
- File I/O (disk speed matters for large projects)
- Subprocess overhead (~100-200ms per call)

---

### Scalability

**Concurrent Requests:**
- ✅ Supported (async subprocess allows parallel execution)
- Each tool call spawns independent subprocess
- No shared state = no locking needed

**Large Projects:**
- ✅ 100k LOC: Scans complete in ~30-40s (within 120s timeout)
- ❌ 500k LOC: May exceed 120s timeout (use smaller scope or increase timeout)

**Memory:**
- Python server: ~50-100 MB RAM
- CLI subprocess: ~200-500 MB RAM per call (depends on project size)

---

### Caching Strategy

**Current:** No caching (intentional)
**Reason:** Accuracy over speed (code changes frequently)

**Future (v2.0):**
- Optional LRU cache with TTL (configurable)
- Cache key: `(project_path, tool, args)`
- Invalidation: Manual (agent calls cache_clear) or TTL expiry

---

## Error Handling & Resilience

### Error Categories

**1. Timeout Errors**
- Cause: CLI command exceeds 120s
- Recovery: Kill subprocess, return timeout error
- Agent Action: Retry with smaller scope or ask user

**2. CLI Not Found Errors**
- Cause: @coderef/core not installed or configured
- Recovery: Return clear error message
- Agent Action: Ask user to configure CODEREF_CLI_PATH

**3. JSON Parse Errors**
- Cause: CLI output malformed or contains progress messages
- Recovery: Skip to JSON start (`[` or `{`), retry parse
- Agent Action: Retry once, escalate if fails again

**4. Subprocess Errors**
- Cause: CLI crashes, OOM, permission denied
- Recovery: Capture stderr, return error message
- Agent Action: Check CLI works standalone, report to user

---

### Resilience Patterns

**1. Graceful Degradation**
- If CLI not found, return clear error (don't crash server)
- If timeout, kill subprocess cleanly (no zombie processes)

**2. Error Propagation**
- CLI errors propagate to agent (stderr → JSON error response)
- Agent can diagnose issues from error messages

**3. No Cascading Failures**
- One tool failure doesn't affect other tools (stateless)
- Subprocess isolation prevents server crashes

---

## Security Considerations

### Trust Model

**Assumption:** Local server, trusted environment
- No authentication required
- Agents run on same machine
- User controls codebase access

**Risks:**
- Malicious codebase could exploit CLI (AST parsing vulnerabilities)
- No sandboxing (CLI has full file system access)

**Mitigations:**
- CLI is read-only (doesn't modify code except tag command)
- Subprocess isolation limits blast radius
- Timeout prevents infinite loops

---

### Input Validation

**Validated:**
- `project_path` must be absolute path (prevent path traversal)
- `query_type`, `operation`, `format` must be enum values
- `max_depth` must be positive integer 1-10

**Not Validated:**
- File contents (CLI handles parsing)
- Element names (CLI validates existence)

---

## Future Architecture

### v2.0 Planned Changes

**1. Streaming Support**
- Stream large scan results (avoid 100k element JSON)
- Use MCP streaming protocol (future spec)

**2. Optional Caching**
- LRU cache with TTL (configurable)
- Cache invalidation via agent call

**3. Parallel Analysis**
- Scan multiple directories in parallel
- Reduce latency for multi-module projects

**4. Performance Metrics**
- Track latency per tool
- Expose `/metrics` endpoint for monitoring

**5. Health Checks**
- `/health` endpoint for uptime monitoring
- CLI version compatibility checks

---

## References

- **[API.md](API.md)** - API endpoint documentation
- **[SCHEMA.md](SCHEMA.md)** - Data schema definitions
- **[COMPONENTS.md](COMPONENTS.md)** - Component reference (handlers, patterns)
- **[CLAUDE.md](../CLAUDE.md)** - AI context documentation
- **[server.py](../server.py)** - Full implementation source code
- **[@coderef/core](https://github.com/coderef-system)** - Upstream TypeScript analysis engine

---

## AI Agent Instructions

**When using this architecture:**
1. Understand data flow: Agent → MCP Server → CLI Subprocess → Codebase
2. Respect 120s timeout (large projects may need smaller scope)
3. Handle errors gracefully (retry on timeout, ask user on CLI not found)
4. Leverage stateless design (concurrent tool calls are safe)

**When debugging:**
1. Check CLI path detection logic first (`get_cli_command()`)
2. Verify CLI works standalone (`coderef scan /path --json`)
3. Check subprocess command construction (print `cmd` variable)
4. Validate JSON parsing (CLI may output progress before JSON)

**When extending:**
1. Follow handler pattern (async, timeout, JSON parse, error handling)
2. Add tool to both `list_tools()` and `call_tool()` router
3. Test with real @coderef/core CLI before committing
4. Update API.md, SCHEMA.md, COMPONENTS.md documentation

---

**Generated:** 2025-12-30
**Maintained by:** coderef-context MCP Server
**For AI Agents:** This architecture reference helps you understand the system design, integration points, and how to extend the server with new capabilities.
