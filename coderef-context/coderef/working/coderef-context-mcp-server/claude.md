# Agent Handoff Context - CodeRef Context MCP Server

**Workorder ID:** WO-CODEREF-CONTEXT-MCP-SERVER-001
**Feature:** coderef-context-mcp-server
**Generated:** 2025-12-23

---

## Quick Overview

You are building a **new MCP server** called `coderef-context` that wraps the entire `@coderef/core` TypeScript system (all 10 modules) and exposes them as MCP tools.

**What this means:**
- **Old approach:** coderef-mcp had its own Python code duplicating analysis logic
- **New approach:** coderef-context is a thin Python MCP wrapper that calls @coderef/core via subprocess
- **Result:** Single source of truth, all analysis logic centralized in @coderef/core

---

## Key Files to Read First

1. **Context & Requirements:**
   - `context.json` - Feature description, requirements, constraints, decisions
   - `analysis.json` - Project structure analysis (mostly empty since this is new)

2. **Implementation Plan:**
   - `plan.json` - Complete 10-section implementation plan with 4 phases, 18 tasks
   - `DELIVERABLES.md` - Task checklist and success metrics

3. **Reference Documentation:**
   - `C:\Users\willh\Desktop\projects\coderef-system\CLAUDE.md` - Complete CodeRef system documentation
   - `C:\Users\willh\Desktop\projects\coderef-system\packages\core\demo-all-modules.ts` - Shows all 10 modules working

---

## The 10 Modules You're Exposing

| Module | Purpose | MCP Tool Name |
|--------|---------|---------------|
| 1. Scanner | Discover code elements (functions, classes, etc) | `scan_elements` |
| 2. Analyzer | Build dependency graph with nodes/edges | `analyze_codebase` |
| 3. Query Engine | Traverse graph for relationships | `query_graph` |
| 4. Parser | Parse CodeRef tag format (@Fn/path#element:line) | `parse_tag` |
| 5. Validator | Check references against codebase | `validate_reference` |
| 6. Exporter | Serialize graphs to JSON/other formats | `export_graph` |
| 7. Context (6-phase) | Generate agentic context with confidence | `generate_context` |
| 8. Integration/RAG | Semantic search and Q&A over codebase | `rag_ask_question` |
| 9. Error Handling | Graceful error handling (internal) | N/A |
| 10. Types & Utilities | Type system and helpers (internal) | N/A |

---

## Architecture Overview

```
User Question via Claude
        ↓
MCP Protocol Handler (server.py)
        ↓
Tool Handler (tool_handlers.py)
        ↓
CodeRefCoreBridge (coderef_bridge.py)
        ↓
Subprocess: pnpm start [command]
        ↓
@coderef/core TypeScript
        ↓
Returns JSON Response
        ↓
CacheManager (cache_manager.py) ← Store & Retrieve
        ↓
Format as MPC Response
        ↓
Return to Claude
```

**Key points:**
- All communication with @coderef/core goes through subprocess (no direct imports)
- Responses cached (5-minute TTL, LRU eviction)
- Python handles JSON parsing, validation, formatting
- Each tool is idempotent and can be called repeatedly

---

## Implementation Phases

### Phase 1: Setup & Infrastructure (2 weeks)
**Status:** Not started
**Tasks:** SETUP-001, SETUP-002, BRIDGE-001, BRIDGE-002
**Goal:** Get foundation working (server startup, bridge communication, caching)

Start here. You need:
- Project structure (directories, files, dependencies)
- MCP server that listens and handles protocol
- CodeRefCoreBridge that executes `pnpm start` commands
- CacheManager with TTL/LRU

### Phase 2: Core Analysis Tools (2.5 weeks)
**Status:** Not started (depends on Phase 1)
**Tasks:** SCANNER-001, ANALYZER-001, QUERY-001, PARSER-001
**Goal:** Implement 4 main analysis tools

### Phase 3: Validation & Export (1.5 weeks)
**Status:** Not started (depends on Phase 2)
**Tasks:** VALIDATOR-001, EXPORTER-001
**Goal:** Add validation and export capabilities

### Phase 4: Advanced Features & Polish (2.5 weeks)
**Status:** Not started (depends on Phase 3)
**Tasks:** CONTEXT-001, RAG-001, TYPES-001, ERROR-001, TEST-001, PERF-001, DOCS-001
**Goal:** Complete system with context generation, RAG, full testing, documentation

---

## Success Criteria

### Must Have (Blocking)
- [ ] All 10 @coderef/core modules working via MPC tools
- [ ] <5 second response time for most queries (cached)
- [ ] 90%+ test coverage
- [ ] Zero crashes or unhandled errors
- [ ] Windows & Unix path handling working

### Should Have (Important)
- [ ] Performance: <1s for cached queries
- [ ] Caching: >70% hit rate
- [ ] Full documentation
- [ ] Integration with real projects

### Nice to Have (Polish)
- [ ] Advanced performance optimizations
- [ ] Detailed troubleshooting guide
- [ ] Example scripts for each tool

---

## Critical Implementation Details

### Subprocess Communication Pattern

```python
# Example from CodeRefCoreBridge
result = subprocess.run(
    [
        "pnpm",
        "start",
        "scan",
        "./src",
        "--lang", "ts,tsx",
        "--json"
    ],
    capture_output=True,
    text=True,
    timeout=30,  # Critical: prevent hanging
    cwd=CODEREF_CLI_PATH  # Path to @coderef/core CLI
)

if result.returncode != 0:
    raise SubprocessError(f"Scan failed: {result.stderr}")

response = json.loads(result.stdout)
return response
```

**Critical points:**
- Always use `--json` flag for machine-readable output
- Always set 30-second timeout
- Always check return code
- Always validate JSON parsing
- Path normalization: convert Windows `\` to `/`

### Caching Strategy

```python
# Cache key structure
cache_key = f"{tool_name}:{json.dumps(inputs, sort_keys=True)}:{source_dir_hash}"

# TTL: 5 minutes by default
# Max entries: 100 (LRU eviction)
# Hit rate goal: >70%
```

### Type Safety with Pydantic

```python
from pydantic import BaseModel
from typing import List, Optional

class ElementData(BaseModel):
    type: str  # 'function', 'class', 'method', etc
    name: str
    file: str
    line: int
    exported: bool = False

class ScanResponse(BaseModel):
    elements: List[ElementData]
    statistics: dict
    execution_time: float
```

---

## Common Pitfalls to Avoid

1. **Path Handling**
   - ❌ Don't: `cmd = f"scan {path}"`  (fails on Windows)
   - ✅ Do: Normalize to forward slashes, use pathlib

2. **JSON Parsing**
   - ❌ Don't: `json.loads(output)` without try/except
   - ✅ Do: Wrap in try/except, validate schema

3. **Performance**
   - ❌ Don't: Call subprocess for every request (will be slow)
   - ✅ Do: Aggressive caching (5-minute TTL)

4. **Error Handling**
   - ❌ Don't: Let subprocess errors crash the server
   - ✅ Do: Catch, map to MCP error types, return clean response

5. **Testing**
   - ❌ Don't: Test against non-existent directories
   - ✅ Do: Use coderef-system itself as test subject (1000+ elements)

---

## Development Workflow

### 1. Start with Phase 1 Boilerplate
```bash
cd C:\Users\willh\.mcp-servers\coderef-context

# Create Python project structure
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # mcp, pydantic, pytest, etc

# Start server (will fail until bridge ready, that's OK)
python server.py
```

### 2. Build CodeRefCoreBridge
- Test subprocess communication: `pnpm start scan ./src --json`
- Test response parsing
- Test error handling
- Test path normalization (especially Windows)

### 3. Test with Real Codebase
Use this for testing:
```
C:\Users\willh\Desktop\projects\coderef-system
```

This has:
- 1,000+ TypeScript elements
- Real dependency graph
- Multiple file types (ts, tsx, js, json)
- Good test subject for all tools

### 4. Add Tests First
Write tests before implementation (TDD approach):
```python
# tests/test_bridge.py
def test_scan_elements_returns_list():
    elements = bridge.scan_elements('./src', ['ts'])
    assert isinstance(elements, list)
    assert len(elements) > 0
    assert all(hasattr(e, 'type') for e in elements)
```

### 5. Performance Tuning
Once functional, optimize:
- Profile with pytest-benchmark
- Ensure cache hit rate >70%
- Verify all response times <5s

---

## Key Environment Variables

```
# Where @coderef/core CLI is located
CODEREF_CLI_PATH=C:\Users\willh\Desktop\projects\coderef-system\packages\cli

# Subprocess timeout (seconds)
CODEREF_SUBPROCESS_TIMEOUT=30

# Cache TTL (seconds)
CODEREF_CACHE_TTL=300

# Max cache entries
CODEREF_CACHE_MAX_ENTRIES=100

# Debug mode
CODEREF_DEBUG=False
```

---

## Questions to Answer During Implementation

1. **Path Normalization:** How will you handle Windows backslashes vs Unix forward slashes?
   → See `utils.py` - implement `normalize_path()` function

2. **Cache Invalidation:** When should cache be cleared?
   → TTL-based only (5 minutes). No explicit invalidation needed.

3. **Subprocess Pooling:** Will you reuse subprocess instances?
   → Not needed. Simple subprocess.run() is sufficient (fast startup).

4. **Error Context:** What info to include in error responses?
   → Stderr from subprocess + input parameters + error type

5. **Type Validation:** How strict should Pydantic validation be?
   → Strict. Use coerce mode only for strings. Fail fast on schema mismatch.

---

## Next Steps

1. **Read the full plan.json** - Understand all 18 tasks
2. **Set up Python project** - Create structure, install deps
3. **Start Phase 1** - Implement SETUP-001 and SETUP-002
4. **Build bridge** - Implement BRIDGE-001 and BRIDGE-002
5. **Write tests** - Test each component as you go
6. **Implement Phase 2** - Scanner, Analyzer, Query, Parser tools
7. **Continue Phases 3-4** - Validator, Exporter, Context, RAG

---

## Resources

**Documentation:**
- `plan.json` - Full implementation plan
- `context.json` - Requirements and constraints
- `DELIVERABLES.md` - Task checklist

**Reference Code:**
- `C:\Users\willh\.mcp-servers\coderef-mcp\server.py` - Current MCP implementation
- `C:\Users\willh\.mcp-servers\coderef-mcp\tool_handlers.py` - Current tool handlers
- `C:\Users\willh\Desktop\projects\coderef-system\packages\core\demo-all-modules.ts` - All 10 modules demo

**TypeScript API Reference:**
- Export list: `C:\Users\willh\Desktop\projects\coderef-system\packages\core\src\index.ts`
- All module types: `C:\Users\willh\Desktop\projects\coderef-system\packages\core\src\types\types.ts`
- CLI docs: `C:\Users\willh\Desktop\projects\coderef-system\CLAUDE.md`

---

## Questions? Issues?

Update this document as you discover:
- [ ] New design decisions
- [ ] Architectural changes
- [ ] Performance findings
- [ ] Testing strategies
- [ ] Integration patterns

**Current Status:** 🚧 Ready for Phase 1 implementation

**Agent Assignment:** Awaiting assignment
**Start Date:** TBD
**Estimated Completion:** 8-10 weeks from start
