# coderef-context MCP Server

**Project:** coderef-context
**Version:** 1.1.0
**Status:** ✅ Production
**Last Updated:** 2025-12-30
**Maintainer:** willh, Claude Code AI

**Expose @coderef/core CLI tools to Claude agents as standardized MCP tools**

---

## Purpose

The coderef-context MCP server provides AI agents with real-time code intelligence during feature implementation. It bridges Claude agents and the @coderef/core TypeScript analysis engine, enabling agents to:

- **Discover** what code elements exist before implementing new features
- **Understand** dependencies and relationships before refactoring
- **Assess** impact and risk before making breaking changes
- **Estimate** effort based on complexity metrics
- **Learn** from existing patterns to avoid reimplementation

**Core Innovation:** Eliminates "blind coding" by giving agents full codebase context through 11 MCP tools.

---

## Overview

### What This Server Does

coderef-context is a **Python-based MCP server** that wraps @coderef/core CLI commands and exposes them as tools for AI agents. It operates in the CodeRef ecosystem alongside:

- **coderef-workflow** - Planning and orchestration
- **coderef-docs** - Documentation generation
- **coderef-personas** - Expert agent roles
- **coderef-testing** - Test automation

### Why It Exists

Agents implementing features need code intelligence to make informed decisions:

❌ **Without coderef-context:**
```
Agent: "I'll create a new ThemeProvider component"
(Implements duplicate component, unaware existing one exists)
```

✅ **With coderef-context:**
```
Agent: "Let me scan the project first..."
(Calls coderef_scan, discovers existing ThemeProvider)
Agent: "ThemeProvider exists at src/theme/ThemeProvider.tsx. I'll extend it instead."
```

---

## What: Tools Exposed

### Core Intelligence Tools

**1. coderef_scan** - Discover all code elements
- **Input:** project_path, languages, use_ast
- **Output:** Array of functions, classes, components, hooks with locations
- **Use Case:** Initial project understanding before implementation

**2. coderef_query** - Query code relationships
- **Input:** project_path, query_type, target, max_depth
- **Query Types:** calls, calls-me, imports, imports-me, depends-on, depends-on-me
- **Use Case:** Understanding what depends on what before refactoring

**3. coderef_impact** - Analyze change impact
- **Input:** project_path, element, operation (modify/delete/refactor)
- **Output:** Affected files, risk level (LOW/MEDIUM/HIGH), ripple effects
- **Use Case:** Pre-refactoring risk assessment

**4. coderef_complexity** - Get complexity metrics
- **Input:** project_path, element
- **Output:** LOC, cyclomatic complexity, dependencies, test coverage %
- **Use Case:** Effort estimation for implementation

**5. coderef_patterns** - Discover code patterns
- **Input:** project_path, pattern_type, limit
- **Output:** Common patterns (React Query, Redux, etc.), usage counts
- **Use Case:** Learning existing conventions before implementing

### Supporting Tools

**6. coderef_coverage** - Test coverage analysis
**7. coderef_context** - Comprehensive codebase context (markdown + JSON)
**8. coderef_validate** - Validate CodeRef2 references
**9. coderef_drift** - Detect drift between index and code
**10. coderef_diagram** - Generate dependency diagrams (Mermaid/Graphviz)
**11. coderef_tag** - Add CodeRef2 tags to source files

---

## Why: Use Cases

### Use Case 1: Safe Refactoring (Impact Analysis)

**Scenario:** Agent needs to refactor AuthService

```python
# Step 1: Check impact
result = await call_tool("coderef_impact", {
    "project_path": "/path/to/app",
    "element": "AuthService",
    "operation": "refactor"
})

# Result:
{
  "affected_files": 12,
  "risk_level": "MEDIUM",
  "ripple_effects": [
    {"file": "src/login/Login.tsx", "impact": "direct call"},
    {"file": "src/profile/Profile.tsx", "impact": "direct call"}
  ]
}

# Decision: 12 files affected, MEDIUM risk → Create comprehensive plan first
```

### Use Case 2: Avoiding Duplication (Scan)

**Scenario:** Agent implementing dark mode toggle

```python
# Step 1: Scan for existing theme code
result = await call_tool("coderef_scan", {
    "project_path": "/path/to/frontend",
    "languages": ["ts", "tsx"],
    "use_ast": true
})

# Result finds:
- ThemeProvider (src/theme/ThemeProvider.tsx)
- useTheme hook (src/theme/useTheme.ts)
- ThemeContext (src/theme/context.ts)

# Decision: Extend existing ThemeProvider instead of building new system
```

### Use Case 3: Understanding Dependencies (Query)

**Scenario:** Agent adding authentication to checkout flow

```python
# Step 1: What does checkout depend on?
result = await call_tool("coderef_query", {
    "project_path": "/path/to/app",
    "query_type": "imports",
    "target": "CheckoutComponent"
})

# Result:
{
  "results": [
    {"from": "CheckoutComponent", "to": "PaymentGateway", "type": "import"},
    {"from": "CheckoutComponent", "to": "OrderService", "type": "import"}
  ]
}

# Decision: Add auth check at PaymentGateway entry point
```

---

## When: Integration Points

### With coderef-workflow (Planning)

During planning phase (section 0: PREPARATION), coderef-workflow calls:
- `coderef_scan` → Discover existing architecture
- `coderef_query` → Understand dependencies
- `coderef_impact` → Assess refactoring risk

Result: plan.json sections populated with real code intelligence

### With coderef-personas (Execution)

Agents (Ava, Marcus, Quinn) call tools during task execution:
- Before implementing → `coderef_scan` (what exists?)
- Before refactoring → `coderef_impact` (what breaks?)
- Before choosing approach → `coderef_patterns` (what patterns exist?)

Result: Informed decisions based on actual codebase

### With coderef-docs (Documentation)

When generating foundation docs, coderef-docs calls:
- `coderef_scan` → Extract API endpoints, schemas, components
- Populates API.md, SCHEMA.md, COMPONENTS.md with real data

Result: Documentation reflects actual code (not placeholders)

---

## Examples

### Example 1: Complete Agent Workflow

```python
# Agent task: "Implement user profile feature"

# Step 1: Understand existing code
scan_result = await call_tool("coderef_scan", {
    "project_path": "/Users/dev/app",
    "use_ast": true
})
# → 247 elements found (finds existing UserService, ProfileComponent)

# Step 2: Check existing profile implementation
query_result = await call_tool("coderef_query", {
    "query_type": "imports",
    "target": "ProfileComponent"
})
# → ProfileComponent imports UserService (pattern discovered)

# Step 3: Estimate effort
complexity_result = await call_tool("coderef_complexity", {
    "element": "UserService"
})
# → 145 LOC, complexity=8, 60% tested

# Step 4: Implement with full context
# Agent now knows:
# - ProfileComponent exists but is incomplete
# - UserService exists with moderate complexity
# - Need to add tests (only 60% coverage)
# Decision: Extend ProfileComponent, improve UserService tests
```

---

## Prerequisites

### Required

1. **Python 3.11+** (async/await support)
2. **@coderef/core CLI** installed (TypeScript analysis engine)
   - Global install: `npm install -g @coderef/core`
   - Or local: Set `CODEREF_CLI_PATH` environment variable

### Optional

- **Git repository** (for drift detection, DELIVERABLES tracking)
- **Test coverage data** (for coverage analysis)

---

## Installation

### Step 1: Install Python Package

```bash
cd C:\Users\willh\.mcp-servers\coderef-context
pip install -e .
```

### Step 2: Configure CLI Path

Set environment variable (if @coderef/core not globally installed):

```bash
export CODEREF_CLI_PATH="/path/to/coderef-system/packages/cli"
```

**Default Path (Windows):**
```
C:\Users\willh\Desktop\projects\coderef-system\packages\cli
```

### Step 3: Register in .mcp.json

Add to `~/.mcp.json`:

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

### Step 4: Restart Claude Code

- Close Claude Code completely
- Reopen Claude Code
- Verify tools appear in autocomplete

---

## Quick Start

### Test the Server

```bash
# Start server
python server.py

# In another terminal, test a tool
echo '{"tool": "coderef_scan", "args": {"project_path": "/path/to/project"}}' | python -m mcp.client
```

### Agent Usage

Agents can call tools directly:

```python
# Discover code elements
result = await call_tool("coderef_context", "coderef_scan", {
    "project_path": "/path/to/project",
    "use_ast": true
})

# Query dependencies
result = await call_tool("coderef_context", "coderef_query", {
    "project_path": "/path/to/project",
    "query_type": "calls-me",
    "target": "login"
})

# Analyze impact
result = await call_tool("coderef_context", "coderef_impact", {
    "project_path": "/path/to/project",
    "element": "AuthService",
    "operation": "refactor"
})
```

---

## Troubleshooting

### Error: CLI path not found

**Symptom:**
```
Error: [Errno 2] No such file or directory: 'coderef'
```

**Solution:**
```bash
# Option 1: Install globally
npm install -g @coderef/core

# Option 2: Set environment variable
export CODEREF_CLI_PATH="/path/to/coderef-system/packages/cli"

# Verify CLI works
coderef --version
# or
node /path/to/cli/dist/cli.js --version
```

---

### Error: Scan timeout (120s exceeded)

**Symptom:**
```
Error: Scan timeout (120s exceeded)
```

**Cause:** Project is very large (>500k LOC)

**Solutions:**
1. Use smaller scope (scan specific directories)
2. Disable AST analysis (use_ast=false) for faster scan
3. Increase timeout in server.py (advanced)

---

### Error: Tool not found

**Symptom:**
```
Tool 'coderef_scan' not found in autocomplete
```

**Solutions:**
1. Check `.mcp.json` registration
2. Restart Claude Code
3. Clear MCP cache:
```bash
rm "C:\Users\willh\.cursor\projects\{PROJECT_ID}\mcp-cache.json"
```
4. Verify server starts without errors:
```bash
python server.py
```

---

### Error: JSON parse error

**Symptom:**
```
JSON parse error: Unexpected token
```

**Cause:** CLI output contains progress messages before JSON

**Solution:** This is handled automatically in server.py (skips to JSON start). If persists:
1. Check CLI version compatibility
2. Verify CLI works standalone:
```bash
coderef scan /path/to/project --json
```

---

## Configuration

### Environment Variables

**CODEREF_CLI_PATH:**
- Purpose: Override default CLI path
- Default: `C:\Users\willh\Desktop\projects\coderef-system\packages\cli`
- Usage: Set in `.mcp.json` env section

### CLI Detection Logic

The server automatically detects CLI path in this order:

1. **Global install** (`where coderef` on Windows, `which coderef` on Unix)
2. **Test global** (`coderef --version`)
3. **Local path** (`$CODEREF_CLI_PATH/dist/cli.js`)
4. **Fallback** (try `coderef` command, may fail)

---

## File Structure

```
coderef-context/
├── server.py                    # MCP server entry point (1073 lines)
├── pyproject.toml               # Python package metadata
├── README.md                    # This file (user-facing overview)
├── CLAUDE.md                    # AI context documentation
├── coderef/
│   └── foundation-docs/
│       ├── API.md               # API endpoint reference
│       ├── SCHEMA.md            # Data schema definitions
│       ├── COMPONENTS.md        # Component architecture
│       └── ARCHITECTURE.md      # System architecture
└── tests/
    └── test_server.py           # Unit tests (future)
```

---

## Architecture

### High-Level Data Flow

```
AI Agent (Claude)
    ↓ MCP Protocol (JSON-RPC 2.0 over stdio)
Python MCP Server (coderef-context)
    ↓ Async subprocess execution
@coderef/core CLI (Node.js)
    ↓ File I/O + AST parsing
Project Codebase (TypeScript, JavaScript, React, etc.)
```

### Tool Handler Pattern

All 11 tools follow this async pattern:

1. **Validate** input arguments
2. **Build** CLI command (`coderef <command> <args> --json`)
3. **Execute** async subprocess (timeout: 120s)
4. **Parse** JSON output (skip CLI progress messages)
5. **Return** structured response (`{success: true, ...}`)
6. **Handle** errors (timeout, CLI crash, JSON parse)

---

## Performance

### Typical Response Times

- `coderef_scan`: 5-15s (50k LOC, AST mode)
- `coderef_query`: 1-3s (dependency lookup)
- `coderef_impact`: 2-5s (impact analysis)
- `coderef_complexity`: 10-30s (full context)
- Other tools: <5s

### Scalability

- ✅ Concurrent requests supported (async subprocess)
- ✅ 100k LOC projects complete within 120s timeout
- ❌ 500k LOC projects may timeout (use smaller scope)

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding New Tools

1. Define tool schema in `@app.list_tools()`
2. Implement handler function (follow pattern)
3. Add route in `@app.call_tool()`
4. Update API.md, SCHEMA.md, COMPONENTS.md

See [COMPONENTS.md](coderef/foundation-docs/COMPONENTS.md) for detailed pattern.

---

## Status & Roadmap

### Current Version: 1.1.0 (Production)

**Implemented:**
- ✅ 11 MCP tools (scan, query, impact, complexity, patterns, coverage, context, validate, drift, diagram, tag)
- ✅ Async subprocess architecture
- ✅ Smart CLI path detection
- ✅ Error handling & timeouts
- ✅ JSON parsing with progress message skipping
- ✅ Integration with coderef-workflow, coderef-personas, coderef-docs

**Limitations:**
- No caching (intentional for accuracy)
- 120s timeout (may need tuning for large projects)
- No result streaming (entire output returned at once)

### Future (v2.0)

- ⏳ Optional LRU cache with TTL
- ⏳ Streaming support for large results
- ⏳ Parallel analysis for multi-module projects
- ⏳ Performance metrics & monitoring
- ⏳ Health check endpoint

---

## Related Documentation

- **[API.md](coderef/foundation-docs/API.md)** - API endpoint reference with examples
- **[SCHEMA.md](coderef/foundation-docs/SCHEMA.md)** - Data schema definitions (input/output types)
- **[COMPONENTS.md](coderef/foundation-docs/COMPONENTS.md)** - Component architecture (handlers, patterns)
- **[ARCHITECTURE.md](coderef/foundation-docs/ARCHITECTURE.md)** - System architecture & design decisions
- **[CLAUDE.md](CLAUDE.md)** - AI context documentation (747 lines)

### Related Projects

- **[@coderef/core](https://github.com/coderef-system)** - TypeScript analysis engine
- **coderef-workflow** - Planning and orchestration MCP server
- **coderef-docs** - Documentation generation MCP server
- **coderef-personas** - Expert agent roles MCP server
- **coderef-testing** - Test automation MCP server

---

## Support

**Issues:** Report at https://github.com/anthropics/claude-code/issues
**Maintainer:** willh, Claude Code AI
**Status:** ✅ Production Ready

---

## AI Agent Instructions

**When using this server:**

1. **Discovery First** - Always call `coderef_scan` before implementing to understand what exists
2. **Dependency Awareness** - Use `coderef_query` to trace relationships before refactoring
3. **Risk Assessment** - Call `coderef_impact` to evaluate change risk before making breaking changes
4. **Pattern Learning** - Check `coderef_patterns` to discover existing conventions
5. **Effort Estimation** - Use `coderef_complexity` to estimate implementation time

**Error handling:**
- Retry once on timeout (may be temporary)
- If CLI not found, ask user to configure CODEREF_CLI_PATH
- Parse JSON carefully (skip CLI progress messages)

**Best practices:**
- Use AST analysis (use_ast=true) for 99% accuracy
- Set appropriate max_depth (3 is usually sufficient)
- Combine tools: scan → query → impact for comprehensive understanding

---

**Generated:** 2025-12-30
**Version:** 1.1.0
**Status:** ✅ Production
**For AI Agents:** This server provides code intelligence to eliminate blind coding. Use it proactively during all implementation tasks.
