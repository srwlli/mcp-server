# Implementation Progress - WO-UNIFIED-MCP-HTTP-SERVER-001

**Feature:** Unified MCP HTTP Server
**Workorder:** WO-UNIFIED-MCP-HTTP-SERVER-001
**Status:** 🚧 In Progress (Phase 2 complete, tool discovery fixed, endpoint updates pending)
**Last Updated:** 2025-10-20 23:45 UTC

---

## Executive Summary

**Goal:** Expose all 4 MCP servers (docs-mcp, coderef-mcp, hello-world-mcp, personas-mcp) through unified HTTP endpoint for ChatGPT integration.

**Current State:**
- ✅ Multi-server loading infrastructure implemented
- ✅ 3 out of 4 servers loading successfully (docs-mcp, hello-world-mcp, personas-mcp)
- ✅ **Tool discovery working for all server patterns** ← NEW!
- ⚠️ 1 server blocked by dependency issue (coderef-mcp)
- ⏳ Endpoint updates pending

**Before:** ChatGPT accesses 36 tools (docs-mcp only)
**Now:** Server loads 3 servers with **44 tools exposed** (docs-mcp: 36, hello-world-mcp: 1, personas-mcp: 7)
**Target:** All 4 servers with 100+ total tools (or 44+ with graceful degradation)

---

## Phase Completion Status

### ✅ Phase 1: Exploration & Verification (COMPLETE)
- ✅ EXPLORE-001: All 4 MCP server directories verified
- ✅ EXPLORE-002: Server imports tested, identified coderef-mcp issue

**Discovery:**
- docs-mcp: Uses TOOL_HANDLERS pattern (36 tools)
- coderef-mcp: Uses TOOL_HANDLERS pattern but has logger_config dependency conflict
- hello-world-mcp: Uses MCP Server pattern (@app decorators, 1 tool)
- personas-mcp: Uses MCP Server pattern (@app decorators, 7 tools)

---

### ✅ Phase 2: Core Implementation (COMPLETE)
- ✅ IMPL-001: Added SERVER_DIRS constant
- ✅ IMPL-002: Created `_load_mcp_servers()` function
- ✅ IMPL-003: Created `_build_unified_tool_registry()` function
- ✅ IMPL-004: Created `_route_tool_call()` function

**Code Added:** ~200 lines in http_server.py

**Functions Implemented:**

```python
# Multi-server loading (lines 77-124)
def _load_mcp_servers() -> Dict[str, Any]:
    """Dynamically import all MCP servers from sibling directories."""
    # Uses importlib.util for dynamic imports
    # Adds server directories to sys.path
    # Returns {server_name: module}

# Unified tool registry (lines 127-166)
def _build_unified_tool_registry() -> Tuple[Dict[str, str], Dict[str, Any]]:
    """Build unified tool registry from all loaded servers."""
    # Handles both TOOL_HANDLERS pattern and MCP Server pattern
    # Returns (tool_registry, all_tool_handlers)
    # Detects and logs duplicate tool names

# Intelligent routing (lines 169-213)
def _route_tool_call(tool_name: str, arguments: dict) -> Any:
    """Route tool call to the appropriate server."""
    # Checks ALL_TOOL_HANDLERS first (TOOL_HANDLERS pattern)
    # Falls back to MCP Server pattern for decorated handlers
    # Handles both sync and async execution
```

**Current Loading Results:**
```
✅ docs-mcp: Loaded (36 tools via TOOL_HANDLERS)
❌ coderef-mcp: Failed - logger_config import error
✅ hello-world-mcp: Loaded (MCP Server pattern)
✅ personas-mcp: Loaded (MCP Server pattern)

Servers: 3/4 successful
Tools discovered: 36 (docs-mcp only)
```

---

### 🚧 Phase 3: Endpoint Updates (PARTIAL)
- ⏳ IMPL-005: Update /tools endpoint (NOT STARTED)
- ⏳ IMPL-006: Update /mcp tools/list (NOT STARTED)
- ⏳ IMPL-007: Update /mcp tool execution (NOT STARTED)
- ⏳ IMPL-008: Update /health endpoint (NOT STARTED)
- ⏳ IMPL-009: Update root / endpoint (NOT STARTED)

**What needs updating:**
1. `/tools` - Call list_tools() on all MCP Server pattern servers
2. `/mcp` tools/list - Return unified tool list from all servers
3. `/mcp` tools/call - Use `_route_tool_call()` instead of direct TOOL_HANDLERS
4. `/health` - Show status of all 4 servers (loaded vs failed)
5. `/` - Update tool count and show breakdown by server

---

### ⏳ Phase 4: Testing & Validation (NOT STARTED)
All tests pending endpoint updates.

---

### ⏳ Phase 5: Deployment & Integration (NOT STARTED)
Waiting for Phase 3-4 completion.

---

## Issues Discovered

### Issue 1: coderef-mcp Import Failure ❌ BLOCKING

**Error:**
```
cannot import name 'setup_logging' from 'logger_config'
(C:\Users\willh\.mcp-servers\docs-mcp\logger_config.py)
```

**Root Cause:**
- coderef-mcp has its own `logger_config.py` with `setup_logging()` function
- docs-mcp has `logger_config.py` with just `logger` object
- When both directories added to sys.path, Python imports docs-mcp's version
- coderef-mcp code expects `setup_logging()` → import fails

**Impact:** coderef-mcp cannot load (0 tools exposed from this server)

**Possible Solutions:**
1. **Namespace isolation:** Import coderef-mcp's logger_config as different name
2. **Mock the function:** Add `setup_logging()` stub to docs-mcp's logger_config
3. **Patch coderef-mcp:** Modify its imports to not use setup_logging
4. **Separate process:** Run coderef-mcp in isolation (complex)

**Recommended:** Solution #2 (quickest) or #3 (cleanest)

---

### ✅ Issue 2: MCP Server Pattern Tool Discovery (RESOLVED - Commit 9de99ce)

**Problem:**
- hello-world-mcp and personas-mcp use `@app.list_tools()` decorators
- Calling `app.list_tools()` directly returned a decorator, not a coroutine
- Result: Servers loaded but 0 tools exposed

**Root Cause:**
- `app.list_tools()` is a decorator factory, not the actual handler
- MCP Server stores handlers in `app.request_handlers[ListToolsRequest]`

**Solution Implemented (lines 153-189):**
```python
from mcp.types import ListToolsRequest

elif hasattr(server_module, 'app'):
    app = server_module.app

    # Access the handler from request_handlers
    if hasattr(app, 'request_handlers') and ListToolsRequest in app.request_handlers:
        handler = app.request_handlers[ListToolsRequest]
        request = ListToolsRequest()
        result = asyncio.run(handler(request))

        # Extract tools from result.root.tools
        tools = result.root.tools
        logger.info(f"  {server_name}: {len(tools)} tools (MCP Server pattern)")

        # Register each tool
        for tool in tools:
            tool_registry[tool.name] = server_name
            all_handlers[tool.name] = app
```

**Result:**
- hello-world-mcp: 1 tool discovered ✅
- personas-mcp: 7 tools discovered ✅
- Total: 44 tools in unified registry ✅

**Documentation:** See TROUBLESHOOTING.md for detailed analysis

---

## Files Modified

### http_server.py (188 lines added)
**Commit:** 6a6b08b "WIP: Add multi-server loading infrastructure"

**Changes:**
- Added imports: `importlib.util`, `Path`
- Added constants: `SERVER_DIRS`, `LOADED_SERVERS`, `TOOL_REGISTRY`, `ALL_TOOL_HANDLERS`
- Added functions: `_load_mcp_servers()`, `_build_unified_tool_registry()`, `_route_tool_call()`
- Added startup code: Server loading with graceful fallback
- No endpoint updates yet (backward compatible)

---

## Next Steps for Next Agent

### Immediate (Fix Blockers):

**1. Fix coderef-mcp Import (15 min)**
```python
# Option A: Add stub to docs-mcp/logger_config.py
def setup_logging():
    """Stub for coderef-mcp compatibility."""
    pass

# Option B: Patch coderef-mcp import in _load_mcp_servers()
# Before importing coderef-mcp:
sys.modules['logger_config'] = coderef_mcp_logger_config
```

**2. Implement MCP Server Pattern Tool Discovery (30 min)**
Update `_build_unified_tool_registry()` to:
- Call `asyncio.run(server_module.app.list_tools())` for MCP Server pattern
- Extract tool names and register them
- Store app reference for routing

### Then Continue Implementation:

**3. Update Endpoints (1 hour)**
- Update `/tools` to call all servers
- Update `/mcp` to use `_route_tool_call()`
- Update `/health` to show all server statuses
- Update `/` to show tool breakdown

**4. Test Locally (30 min)**
- Test `/tools` returns >40 tools
- Test calling tools from each server
- Test graceful degradation (remove one server)

**5. Deploy to Railway (15 min)**
- Git commit final changes
- Push to trigger Railway deployment
- Monitor Railway logs for successful server loading

**6. Test ChatGPT Integration (15 min)**
- Verify ChatGPT sees all tools
- Test invoking tools from different servers

---

## Estimated Remaining Time

- Fix coderef-mcp: 15 min
- MCP Server tool discovery: 30 min
- Endpoint updates: 1 hour
- Local testing: 30 min
- Deployment: 15 min
- ChatGPT testing: 15 min

**Total: ~2.5 hours remaining** (of 3-4 hour estimate)

---

## Success Metrics (from plan.json)

**Functional:**
- [ ] All 4 servers load successfully (currently 3/4)
- [ ] Tool count >33 (currently 36, target >40)
- [ ] Tool routing works for all servers
- [ ] ChatGPT can access all tools

**Quality:**
- [x] Graceful degradation (coderef-mcp fails, others work)
- [x] Error logging (import failures logged)
- [ ] No breaking changes (backward compatible - not yet tested)

**Performance:**
- [x] Startup time <2 seconds (currently ~1s)
- [ ] Tool routing overhead <10ms (not yet measured)

---

## Git History

```
6a6b08b (2025-10-20 22:53) WIP: Add multi-server loading infrastructure
- Added SERVER_DIRS, _load_mcp_servers(), _build_unified_tool_registry(), _route_tool_call()
- Successfully loading 3/4 servers
- Identified coderef-mcp dependency issue
- Identified MCP Server pattern tool discovery gap

9de99ce (2025-10-20 23:43) Fix MCP Server pattern tool discovery - 44 tools now working
- Fixed _build_unified_tool_registry() to use request_handlers[ListToolsRequest]
- Now properly discovers tools from hello-world-mcp (1) and personas-mcp (7)
- Total: 44 tools from 3 servers (up from 36)
- Updated CLAUDE.md with unified HTTP server documentation

1d29cf2 (2025-10-20 23:45) Add comprehensive troubleshooting guide
- Created TROUBLESHOOTING.md with root cause analysis
- Documents the decorator vs handler issue
- Includes verification steps and prevention guidelines
```

---

## Notes for Next Agent

**Key Files:**
- `http_server.py` - Main implementation (lines 24-242)
- `plan.json` - Original implementation plan
- `HANDOFF.md` - Comprehensive implementation guide (1,143 lines)

**Current Behavior:**
- Server starts successfully with 3 servers loaded
- Only docs-mcp tools (36) currently accessible
- hello-world-mcp and personas-mcp loaded but tools not discovered
- coderef-mcp blocked by import error

**Architecture Decision:**
- Using "gateway pattern" - single HTTP endpoint routing to multiple backend servers
- Two server patterns supported: TOOL_HANDLERS (docs-mcp, coderef-mcp) and MCP Server decorators (hello-world-mcp, personas-mcp)
- Graceful degradation if any server fails to load

**Testing Strategy:**
- Fix blockers first (coderef-mcp, tool discovery)
- Then update endpoints
- Test incrementally (don't deploy broken state)
- Verify backward compatibility (existing docs-mcp tools still work)

---

**Status:** 🚧 WIP - Core infrastructure complete, endpoint updates pending
**Blocking Issues:** 2 (coderef-mcp import, MCP Server tool discovery)
**Estimated Completion:** 2.5 hours of focused work

🎯 **Ready for next agent to continue implementation**
