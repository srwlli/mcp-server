# 🔄 Agent Handoff - Unified MCP HTTP Server Implementation

**Workorder:** `WO-UNIFIED-MCP-HTTP-SERVER-001`
**Status:** Ready for Implementation
**Estimated Time:** 3-4 hours
**Priority:** High

---

## 📋 Context Summary

### Current State
- ✅ ChatGPT MCP connector is working
- ✅ Only **docs-mcp** (33 tools) is exposed via HTTP
- ❌ 3 other MCP servers exist but are not accessible:
  - `coderef-mcp` (code reference tools)
  - `hello-world-mcp` (test/demo)
  - `personas-mcp` (persona management)
- ✅ Troubleshooting guide documented the integration journey
- ✅ Implementation plan created and committed

### Goal
Expose all 4 MCP servers through the unified HTTP endpoint so ChatGPT can access all tools (not just docs-mcp's 33)

---

## 📁 Key Files

### 1. Implementation Plan
**Location:** `coderef/working/unified-mcp-http-server/plan.json` (522 lines)

**Contents:**
- 5 implementation phases
- 20 detailed tasks with workorder IDs
- Complete testing strategy
- Edge case handling
- Success criteria

**Status:** ✅ Complete and committed

### 2. File to Modify
**Location:** `http_server.py` (561 lines currently)

**Changes Needed:** ~200 lines added for:
- Multi-server loader
- Unified tool registry
- Routing dispatcher
- Updated endpoints

### 3. Servers to Import
```
C:\Users\willh\.mcp-servers\
├── docs-mcp/server.py       (✅ already working - 33 tools)
├── coderef-mcp/server.py    (❌ needs import)
├── hello-world-mcp/server.py (❌ needs import)
└── personas-mcp/server.py   (❌ needs import)
```

### 4. Reference Documentation
- `CHATGPT-INTEGRATION-TROUBLESHOOTING.md` - Documents the 3 errors we fixed
- `CLAUDE.md` - Comprehensive MCP server documentation
- `plan.json` - Complete implementation plan

---

## 🎯 Implementation Dry-Run

### Phase 1: Exploration & Verification (15-20 minutes)

#### EXPLORE-001: Verify all server directories exist
```bash
cd C:\Users\willh\.mcp-servers
ls -la docs-mcp/server.py
ls -la coderef-mcp/server.py
ls -la hello-world-mcp/server.py
ls -la personas-mcp/server.py
```

**Expected:** All 4 files exist

#### EXPLORE-002: Test importing each server individually
```python
cd docs-mcp
python -c "
import sys
import asyncio
from pathlib import Path

parent = Path('.').parent

# Test docs-mcp (already working)
sys.path.insert(0, str(parent / 'docs-mcp'))
try:
    import server as docs_server
    tools = asyncio.run(docs_server.list_tools())
    print(f'✅ docs-mcp: {len(tools)} tools')
except Exception as e:
    print(f'❌ docs-mcp failed: {e}')

# Test coderef-mcp
sys.path.insert(0, str(parent / 'coderef-mcp'))
try:
    import server as coderef_server
    tools = asyncio.run(coderef_server.list_tools())
    print(f'✅ coderef-mcp: {len(tools)} tools')
except Exception as e:
    print(f'❌ coderef-mcp failed: {e}')

# Test hello-world-mcp
sys.path.insert(0, str(parent / 'hello-world-mcp'))
try:
    import server as hello_server
    tools = asyncio.run(hello_server.list_tools())
    print(f'✅ hello-world-mcp: {len(tools)} tools')
except Exception as e:
    print(f'❌ hello-world-mcp failed: {e}')

# Test personas-mcp
sys.path.insert(0, str(parent / 'personas-mcp'))
try:
    import server as personas_server
    tools = asyncio.run(personas_server.list_tools())
    print(f'✅ personas-mcp: {len(tools)} tools')
except Exception as e:
    print(f'❌ personas-mcp failed: {e}')
"
```

**Expected Output:**
```
✅ docs-mcp: 33 tools
✅ coderef-mcp: X tools
✅ hello-world-mcp: Y tools
✅ personas-mcp: Z tools
```

---

### Phase 2: Core Implementation (1-1.5 hours)

#### IMPL-001: Add SERVER_DIRS constant
**Location:** Top of `http_server.py` (after imports)

```python
# ============================================================================
# MULTI-SERVER CONFIGURATION
# ============================================================================

SERVER_DIRS = ['docs-mcp', 'coderef-mcp', 'hello-world-mcp', 'personas-mcp']
LOADED_SERVERS = {}  # Will hold {server_name: module}
TOOL_REGISTRY = {}   # Will hold {tool_name: server_name}
```

#### IMPL-002: Create _load_mcp_servers() function
**Location:** Before `create_app()` function

```python
def _load_mcp_servers() -> Dict[str, Any]:
    """
    Dynamically import all MCP servers from sibling directories.

    Returns:
        Dict mapping server_name to imported module
    """
    loaded = {}
    parent_dir = Path(__file__).parent.parent  # Go up to .mcp-servers/

    for server_dir in SERVER_DIRS:
        server_path = parent_dir / server_dir

        if not server_path.exists():
            logger.warning(f"Server directory not found: {server_dir}")
            continue

        if not (server_path / 'server.py').exists():
            logger.warning(f"No server.py found in: {server_dir}")
            continue

        try:
            # Add to sys.path if not already there
            server_path_str = str(server_path)
            if server_path_str not in sys.path:
                sys.path.insert(0, server_path_str)

            # Import with unique name to avoid collisions
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"{server_dir}.server",
                server_path / 'server.py'
            )
            server_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server_module)

            # Verify it has list_tools
            if not hasattr(server_module, 'list_tools'):
                logger.error(f"Server {server_dir} missing list_tools()")
                continue

            loaded[server_dir] = server_module
            logger.info(f"✅ Loaded server: {server_dir}")

        except ImportError as e:
            logger.error(f"Failed to import {server_dir}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {server_dir}: {e}")

    logger.info(f"Loaded {len(loaded)}/{len(SERVER_DIRS)} servers")
    return loaded
```

#### IMPL-003: Create _build_unified_tool_registry()
**Location:** After `_load_mcp_servers()`

```python
async def _build_unified_tool_registry() -> Dict[str, str]:
    """
    Build unified tool registry from all loaded servers.

    Returns:
        Dict mapping tool_name to server_name
    """
    registry = {}
    tool_counts = {}

    for server_name, server_module in LOADED_SERVERS.items():
        try:
            tools = await server_module.list_tools()
            tool_counts[server_name] = len(tools)
            logger.info(f"Server {server_name}: {len(tools)} tools")

            for tool in tools:
                tool_name = tool.name

                # Detect duplicates
                if tool_name in registry:
                    logger.warning(
                        f"⚠️  Duplicate tool '{tool_name}' in {server_name} "
                        f"(already in {registry[tool_name]}). Using first occurrence."
                    )
                    continue

                registry[tool_name] = server_name

        except Exception as e:
            logger.error(f"Failed to get tools from {server_name}: {e}")

    total_tools = len(registry)
    logger.info(f"Built registry with {total_tools} total tools: {tool_counts}")
    return registry
```

#### IMPL-004: Create _route_tool_call()
**Location:** After `_build_unified_tool_registry()`

```python
async def _route_tool_call(tool_name: str, params: dict) -> Any:
    """
    Route tool call to the correct server.

    Args:
        tool_name: Name of tool to invoke
        params: Tool parameters

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool not found
        RuntimeError: If server not loaded
    """
    # Look up which server owns this tool
    server_name = TOOL_REGISTRY.get(tool_name)

    if not server_name:
        available = ', '.join(sorted(TOOL_REGISTRY.keys())[:10])
        raise ValueError(
            f"Unknown tool: {tool_name}. "
            f"Available tools: {available}..."
        )

    server_module = LOADED_SERVERS.get(server_name)

    if not server_module:
        raise RuntimeError(
            f"Server {server_name} not loaded (owns tool {tool_name})"
        )

    logger.info(f"Routing {tool_name} → {server_name}")

    # Get the tool handler from the server
    # Assuming servers follow MCP pattern with TOOL_HANDLERS registry
    from tool_handlers import TOOL_HANDLERS

    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        raise ValueError(f"Tool {tool_name} has no handler")

    # Execute handler
    if asyncio.iscoroutinefunction(handler):
        result = await handler(params)
    else:
        result = handler(params)

    return result
```

**Expected Outcome:**
- All 4 core functions implemented
- Code compiles without syntax errors
- Logging statements in place

---

### Phase 3: Endpoint Updates (45 minutes - 1 hour)

#### IMPL-005: Update /tools endpoint
**Location:** Replace existing `/tools` route in `create_app()`

```python
@app.route('/tools', methods=['GET'])
def tools() -> Tuple[Dict[str, Any], int]:
    """
    OpenRPC tool discovery endpoint - unified across all servers.

    Returns OpenRPC 1.3.2 specification with all available MCP tools.
    """
    try:
        all_tools = []
        tools_by_server = {}

        # Collect tools from all loaded servers
        for server_name, server_module in LOADED_SERVERS.items():
            try:
                tools_list = asyncio.run(server_module.list_tools())
                all_tools.extend(tools_list)
                tools_by_server[server_name] = len(tools_list)
                logger.info(f"Added {len(tools_list)} tools from {server_name}")
            except Exception as e:
                logger.error(f"Failed to get tools from {server_name}: {e}")

        # Build unified OpenRPC spec
        openrpc_spec = _build_openrpc_spec(all_tools)
        openrpc_spec['info']['description'] = (
            f"Unified MCP server exposing {len(all_tools)} tools "
            f"from {len(LOADED_SERVERS)} servers: {', '.join(LOADED_SERVERS.keys())}"
        )

        logger.info(
            f"Generated OpenRPC spec: {len(all_tools)} tools "
            f"from {len(LOADED_SERVERS)} servers"
        )

        return jsonify(openrpc_spec), 200

    except Exception as e:
        logger.error(f"Error in /tools endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 500
        }), 500
```

#### IMPL-006: Update /mcp tools/list
**Location:** Inside `/mcp` endpoint, replace `tools/list` handler

```python
# Handle tools/list method
if method == 'tools/list':
    logger.info("MCP tools/list request received")

    # Build unified tool list from all servers
    all_tools = []

    for server_name, server_module in LOADED_SERVERS.items():
        try:
            tools = asyncio.run(server_module.list_tools())

            # Convert Tool objects to dicts for JSON-RPC
            for tool in tools:
                all_tools.append({
                    'name': tool.name,
                    'description': tool.description,
                    'inputSchema': tool.inputSchema
                })

            logger.debug(f"Added {len(tools)} tools from {server_name}")

        except Exception as e:
            logger.error(f"Failed to list tools from {server_name}: {e}")

    logger.info(f"Returning {len(all_tools)} tools from {len(LOADED_SERVERS)} servers")

    return jsonify({
        'jsonrpc': '2.0',
        'id': request_id,
        'result': {'tools': all_tools}
    }), 200
```

#### IMPL-007: Update /mcp tool execution
**Location:** Inside `/mcp` endpoint, replace tool execution section

```python
# ================================================================
# TOOL EXECUTION (Unified Routing)
# ================================================================

# Check if method is a tool name in our registry
if method in TOOL_REGISTRY:
    logger.info(f"Tool call: {method}")

    try:
        # Route to correct server using unified router
        result = asyncio.run(_route_tool_call(method, params))

        # Format response
        response_data = _format_tool_response(result)

        return jsonify({
            'jsonrpc': '2.0',
            'id': request_id,
            'result': response_data
        }), 200

    except ValueError as e:
        # Tool not found
        logger.error(f"Tool not found: {method}")
        return jsonify({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32601,
                'message': f'Method not found: {method}',
                'data': {'details': str(e)}
            }
        }), 200

    except Exception as e:
        # Execution error
        logger.error(f"Tool execution error for {method}: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32603,
                'message': 'Internal error',
                'data': {'details': str(e)}
            }
        }), 500

# Unknown method
return jsonify({
    'jsonrpc': '2.0',
    'id': request_id,
    'error': {
        'code': -32601,
        'message': f'Method not found: {method}'
    }
}), 200
```

#### IMPL-008: Update /health endpoint
**Location:** Replace existing `/health` route

```python
@app.route('/health', methods=['GET'])
def health() -> Tuple[Dict[str, Any], int]:
    """Health check endpoint with multi-server status."""
    servers_status = {
        name: name in LOADED_SERVERS
        for name in SERVER_DIRS
    }

    tools_by_server = {}
    for tool_name, server_name in TOOL_REGISTRY.items():
        tools_by_server.setdefault(server_name, 0)
        tools_by_server[server_name] += 1

    return jsonify({
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '2.0.0',
        'servers_loaded': servers_status,
        'servers_count': f"{len(LOADED_SERVERS)}/{len(SERVER_DIRS)}",
        'total_tools': len(TOOL_REGISTRY),
        'tools_by_server': tools_by_server
    }), 200
```

#### IMPL-009: Update root / endpoint
**Location:** Replace existing `/` route

```python
@app.route('/', methods=['GET'])
def root() -> Tuple[Dict[str, Any], int]:
    """Root endpoint - Unified MCP server information."""
    tools_by_server = {}
    for tool_name, server_name in TOOL_REGISTRY.items():
        tools_by_server.setdefault(server_name, 0)
        tools_by_server[server_name] += 1

    return jsonify({
        'name': 'Unified MCP HTTP Server',
        'version': '2.0.0',
        'description': f'Unified HTTP wrapper exposing {len(LOADED_SERVERS)} MCP servers with {len(TOOL_REGISTRY)} total tools',
        'servers': list(LOADED_SERVERS.keys()),
        'servers_loaded': f"{len(LOADED_SERVERS)}/{len(SERVER_DIRS)}",
        'total_tools': len(TOOL_REGISTRY),
        'tools_by_server': tools_by_server,
        'endpoints': {
            'health': '/health',
            'tools': '/tools (OpenRPC 1.3.2 discovery)',
            'sse': '/sse (Server-Sent Events)',
            'mcp': '/mcp (JSON-RPC 2.0 invocation)'
        }
    }), 200
```

#### Add initialization at module level
**Location:** Before `if __name__ == '__main__':` block

```python
# ============================================================================
# INITIALIZE MULTI-SERVER SYSTEM
# ============================================================================

print("=" * 80)
print("LOADING MCP SERVERS")
print("=" * 80)

try:
    # Load all MCP servers
    LOADED_SERVERS = _load_mcp_servers()
    print(f"✅ Loaded {len(LOADED_SERVERS)}/{len(SERVER_DIRS)} servers")

    # Build unified tool registry
    TOOL_REGISTRY = asyncio.run(_build_unified_tool_registry())
    print(f"✅ Built registry with {len(TOOL_REGISTRY)} total tools")

    print("=" * 80)
    print("MULTI-SERVER SYSTEM READY")
    print("=" * 80)

except Exception as e:
    print("!" * 80)
    print(f"ERROR INITIALIZING MULTI-SERVER SYSTEM: {e}")
    print("!" * 80)
    import traceback
    traceback.print_exc()
```

**Expected Outcome:**
- All endpoints updated
- Server initializes with all 4 servers
- Tool count shows >33

---

### Phase 4: Testing & Validation (30-45 minutes)

#### TEST-001: Test /tools endpoint
```bash
cd C:\Users\willh\.mcp-servers\docs-mcp

# Start server locally
python http_server.py &

# Wait for startup
sleep 2

# Test /tools endpoint
curl http://localhost:5000/tools | jq '.methods | length'
# Expected: >33 (combined tools from all servers)

curl http://localhost:5000/tools | jq '.info.description'
# Expected: Shows unified server description
```

#### TEST-002: Test /mcp tools/list
```bash
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | jq '.result.tools | length'
# Expected: >33
```

#### TEST-003: Test tool invocation from each server
```bash
# Test docs-mcp tool (list_templates)
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"list_templates","params":{}}' \
  | jq '.'
# Expected: Success response with template list

# Test coderef-mcp tool (query - if exists)
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"query","params":{"query":"test"}}' \
  | jq '.'
# Expected: Success response or error if tool doesn't exist

# Test hello-world-mcp tool (greet - if exists)
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"greet","params":{"name":"Claude"}}' \
  | jq '.'
# Expected: Success response or error if tool doesn't exist

# Test personas-mcp tool (use_persona - if exists)
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"use_persona","params":{"name":"test"}}' \
  | jq '.'
# Expected: Success response or error if tool doesn't exist
```

#### TEST-004: Test graceful degradation
```bash
# Stop server
pkill -f "python http_server.py"

# Temporarily disable one server
cd C:\Users\willh\.mcp-servers
mv hello-world-mcp hello-world-mcp.disabled

# Start server again
cd docs-mcp
python http_server.py &
sleep 2

# Check health - should show 3/4 servers loaded
curl http://localhost:5000/health | jq '.servers_loaded'
# Expected: {"docs-mcp": true, "coderef-mcp": true, "hello-world-mcp": false, "personas-mcp": true}

# Verify other servers still work
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"list_templates","params":{}}' \
  | jq '.'
# Expected: Success

# Restore disabled server
pkill -f "python http_server.py"
cd C:\Users\willh\.mcp-servers
mv hello-world-mcp.disabled hello-world-mcp
```

#### TEST-005: Test /health shows all servers
```bash
cd C:\Users\willh\.mcp-servers\docs-mcp
python http_server.py &
sleep 2

curl http://localhost:5000/health | jq '.'
# Expected:
# {
#   "status": "operational",
#   "servers_loaded": {
#     "docs-mcp": true,
#     "coderef-mcp": true,
#     "hello-world-mcp": true,
#     "personas-mcp": true
#   },
#   "servers_count": "4/4",
#   "total_tools": XX,
#   "tools_by_server": {
#     "docs-mcp": 33,
#     "coderef-mcp": Y,
#     ...
#   }
# }

# Stop server
pkill -f "python http_server.py"
```

**Expected Outcome:**
- ✅ All tests pass
- ✅ Tool count >33
- ✅ Each server's tools accessible
- ✅ Graceful degradation works
- ✅ Health endpoint accurate

---

### Phase 5: Deployment & Integration (30-45 minutes)

#### DEPLOY-001: Verify Railway directory access
```bash
# Check current Railway deployment structure
# Railway should have access to all 4 directories:
# - docs-mcp/
# - coderef-mcp/
# - hello-world-mcp/
# - personas-mcp/

# If Railway only deploys docs-mcp, need to update configuration
# Check railway.toml or Railway dashboard settings
```

#### DEPLOY-002: Commit changes
```bash
cd C:\Users\willh\.mcp-servers\docs-mcp

git add http_server.py

git commit -m "$(cat <<'EOF'
Implement unified MCP HTTP server (WO-UNIFIED-MCP-HTTP-SERVER-001)

Exposes all 4 MCP servers through single HTTP endpoint:
- docs-mcp (33 tools)
- coderef-mcp (code reference tools)
- hello-world-mcp (test/demo tools)
- personas-mcp (persona management tools)

Changes:
- Added dynamic multi-server loader with importlib
- Built unified tool registry with collision detection
- Implemented intelligent routing to dispatch calls to correct server
- Updated /tools endpoint to merge OpenRPC specs from all servers
- Updated /mcp tools/list to return unified tool list
- Updated /mcp tool execution to route through dispatcher
- Updated /health endpoint to show status of all 4 servers
- Updated / endpoint to show breakdown by server
- Graceful degradation: continues if one server fails to load

Architecture:
- _load_mcp_servers() - Dynamically imports all servers from sibling dirs
- _build_unified_tool_registry() - Maps tool names to owning servers
- _route_tool_call() - Dispatches tool calls to correct server

ChatGPT can now access ALL MCP tools through:
https://docs-mcp-production.up.railway.app/mcp

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

#### DEPLOY-003: Push to Railway
```bash
git push origin main

# Wait 60-90 seconds for Railway auto-deploy
# Monitor deployment: https://railway.app/project/[project-id]

# Check Railway logs for:
# - "LOADING MCP SERVERS"
# - "✅ Loaded X/4 servers"
# - "✅ Built registry with XX total tools"
# - "MULTI-SERVER SYSTEM READY"

# Verify production deployment
curl https://docs-mcp-production.up.railway.app/health | jq '.'
# Expected: All 4 servers loaded

curl https://docs-mcp-production.up.railway.app/ | jq '.total_tools'
# Expected: >33
```

#### INTEGRATE-001: Test ChatGPT connector
```
1. Open ChatGPT (https://chat.openai.com/)
2. Connector should already be configured: docs-mcp
3. Test: "What tools do you have available from docs-mcp?"
4. Expected: ChatGPT lists tools from all 4 servers

5. Test invocation: "List available documentation templates"
6. Expected: Calls list_templates tool successfully

7. Test other servers: "What persona tools are available?"
8. Expected: Shows tools from personas-mcp
```

#### DOC-001: Update troubleshooting guide
```bash
# Edit CHATGPT-INTEGRATION-TROUBLESHOOTING.md
# Add new section after "Why Only docs-mcp is Exposed"
```

**Add this section:**

```markdown
## ✅ UPDATE: All 4 MCP Servers Now Exposed (2025-10-20)

As of commit [hash], all 4 MCP servers are now accessible through the unified HTTP endpoint.

### Current Architecture (Updated)

```
ChatGPT
    ↓
Railway (HTTPS)
    ↓
http_server.py (Unified Flask Gateway)
    ↓
    ├── docs-mcp/server.py (33 tools) ✅
    ├── coderef-mcp/server.py (X tools) ✅
    ├── hello-world-mcp/server.py (Y tools) ✅
    └── personas-mcp/server.py (Z tools) ✅
```

### Tool Count Breakdown

| Server | Tools | Status |
|--------|-------|--------|
| docs-mcp | 33 | ✅ Active |
| coderef-mcp | X | ✅ Active |
| hello-world-mcp | Y | ✅ Active |
| personas-mcp | Z | ✅ Active |
| **Total** | **XX** | **✅ All Accessible** |

### How It Works

1. **Dynamic Server Loading**: `_load_mcp_servers()` scans `../[server-name]/` directories and imports each `server.py`
2. **Unified Registry**: `_build_unified_tool_registry()` merges tool lists and maps tool names to their owning server
3. **Intelligent Routing**: `_route_tool_call()` dispatches tool invocations to the correct server
4. **Graceful Degradation**: If one server fails to load, others continue to work

### Testing

**Verify all servers loaded:**
```bash
curl https://docs-mcp-production.up.railway.app/health | jq '.servers_loaded'
# Should show all 4 servers as true
```

**Check total tool count:**
```bash
curl https://docs-mcp-production.up.railway.app/ | jq '.total_tools'
# Should show >33
```

**View breakdown by server:**
```bash
curl https://docs-mcp-production.up.railway.app/ | jq '.tools_by_server'
```

### Known Limitations

**Previous limitation (RESOLVED):**
- ~~Only docs-mcp exposed (33 tools)~~
- ~~Other 3 servers not in HTTP wrapper~~

**Current status:**
- ✅ All 4 servers exposed
- ✅ Unified tool namespace
- ✅ Graceful degradation
- ✅ No manual configuration needed
```

**Commit documentation update:**
```bash
git add CHATGPT-INTEGRATION-TROUBLESHOOTING.md
git commit -m "Update troubleshooting guide - all 4 MCP servers now exposed

Documents unified multi-server architecture with tool count breakdown.

🤖 Generated with Claude Code"
git push origin main
```

**Expected Outcome:**
- ✅ Railway deployment successful
- ✅ All 4 servers load in production
- ✅ ChatGPT can see tools from all servers
- ✅ ChatGPT can invoke tools from all servers
- ✅ Documentation updated and committed

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Import Conflicts
**Problem:** Multiple servers define classes/functions with same names

**Solution:** Use `importlib.util` with unique module names
```python
spec = importlib.util.spec_from_file_location(
    f"{server_dir}.server",  # Unique name per server
    server_path / 'server.py'
)
```

**Why this works:** Each server gets its own namespace in `sys.modules`

---

### Issue 2: Async Event Loop Conflicts
**Problem:** Multiple `asyncio.run()` calls may conflict

**Solution:** Reuse event loop or handle closed loops
```python
try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
```

**Why this works:** Ensures a valid event loop always exists

---

### Issue 3: Railway Directory Structure
**Problem:** Railway may only deploy docs-mcp directory

**Symptoms:**
- Import errors in Railway logs
- `Server directory not found: coderef-mcp`
- Only docs-mcp tools accessible

**Solution A:** Update Railway root directory to parent level
```toml
# railway.toml
[build]
builder = "nixpacks"
buildCommand = "cd docs-mcp && pip install -r requirements.txt"

[deploy]
startCommand = "cd docs-mcp && gunicorn http_server:app"
```

**Solution B:** Ensure Railway watches entire `.mcp-servers/` directory
- Railway Dashboard → Settings → Root Directory → Set to `.`
- This gives access to all sibling directories

**Verification:**
```bash
# Check Railway logs for successful imports
# Should see: "✅ Loaded server: docs-mcp"
#            "✅ Loaded server: coderef-mcp"
#            etc.
```

---

### Issue 4: Unknown Tool Counts
**Problem:** Don't know how many tools each non-docs server has

**Solution:** Run exploration phase first
```bash
# Get accurate counts before implementation
python -c "
import sys
import asyncio
from pathlib import Path

parent = Path('.').parent
sys.path.insert(0, str(parent / 'coderef-mcp'))
import server
tools = asyncio.run(server.list_tools())
print(f'coderef-mcp: {len(tools)} tools')
"
```

**Expected Range:** Total 40-70 tools across all servers

---

### Issue 5: Tool Invocation Pattern Differences
**Problem:** Each server may expose handlers differently

**Symptoms:**
- `AttributeError: module has no attribute 'call_tool'`
- Tool routing fails even though tool exists

**Solution:** Check each server's handler pattern
```python
# Pattern A: Direct handler registry (docs-mcp uses this)
from tool_handlers import TOOL_HANDLERS
handler = TOOL_HANDLERS[tool_name]

# Pattern B: call_tool() method on server
result = await server.call_tool(tool_name, params)

# Pattern C: Direct function calls
handler_func = getattr(server, f'handle_{tool_name}')
result = await handler_func(params)
```

**Fallback Strategy:**
```python
# Try multiple patterns
try:
    # Try pattern A
    from tool_handlers import TOOL_HANDLERS
    handler = TOOL_HANDLERS[tool_name]
except (ImportError, KeyError):
    try:
        # Try pattern B
        result = await server_module.call_tool(tool_name, params)
    except AttributeError:
        # Try pattern C
        handler_func = getattr(server_module, f'handle_{tool_name}')
        result = await handler_func(params)
```

---

### Issue 6: Tool Name Collisions
**Problem:** Two servers define same tool name (e.g., both have `list_templates`)

**Symptoms:**
- Warning in logs: `⚠️ Duplicate tool 'list_templates'`
- Only first server's tool is accessible

**Solution:** Use first-wins policy (already implemented)
```python
if tool_name in registry:
    logger.warning(f"Duplicate tool '{tool_name}' - using first")
    continue  # Skip duplicate
```

**Alternative:** Namespace tools by server
```python
# Instead of: "list_templates"
# Use: "docs-mcp.list_templates", "coderef-mcp.list_templates"
registry[f"{server_name}.{tool_name}"] = server_name
```

---

### Issue 7: Startup Performance
**Problem:** Loading 4 servers increases startup time

**Symptoms:**
- Railway health check timeouts
- Slow server initialization

**Solution:** Add startup logging to diagnose
```python
import time

start = time.time()
LOADED_SERVERS = _load_mcp_servers()
load_time = time.time() - start
logger.info(f"Server loading took {load_time:.2f}s")

start = time.time()
TOOL_REGISTRY = asyncio.run(_build_unified_tool_registry())
registry_time = time.time() - start
logger.info(f"Registry building took {registry_time:.2f}s")
```

**Acceptable:** <2 seconds total
**If slower:** Consider lazy loading or caching

---

## 📊 Success Metrics

### Before (Current State)
- ✅ ChatGPT connected
- ✅ 33 tools accessible (docs-mcp only)
- ❌ coderef-mcp not accessible
- ❌ hello-world-mcp not accessible
- ❌ personas-mcp not accessible

### After (Target State)
- ✅ ChatGPT connected
- ✅ >33 tools accessible (all servers)
- ✅ coderef-mcp accessible
- ✅ hello-world-mcp accessible
- ✅ personas-mcp accessible
- ✅ Graceful degradation working
- ✅ Tool routing accurate
- ✅ All tests passing
- ✅ Documentation updated

---

## 🔗 Resources

### Files
- **Plan:** `coderef/working/unified-mcp-http-server/plan.json` (522 lines)
- **Code:** `http_server.py` (current: 561 lines, after: ~760 lines)
- **Troubleshooting:** `CHATGPT-INTEGRATION-TROUBLESHOOTING.md`
- **Docs:** `CLAUDE.md`, `README.md`
- **Workorder Log:** `coderef/workorder-log.txt` (global activity tracking)

### URLs
- **Production:** https://docs-mcp-production.up.railway.app
- **Railway Project:** https://railway.app/project/[project-id]
- **GitHub Repo:** https://github.com/srwlli/docs-mcp

### Commands
```bash
# Project directory
cd C:\Users\willh\.mcp-servers\docs-mcp

# Start local server
python http_server.py

# Run tests
curl http://localhost:5000/health | jq '.'

# View workorder activity
/get-workorder-log --pattern WO-UNIFIED
```

### Workorder Tracking
**Workorder ID:** WO-UNIFIED-MCP-HTTP-SERVER-001

Tools will auto-log progress to `coderef/workorder-log.txt` as you complete tasks.
View activity with `/get-workorder-log` command.

---

## 🎯 Next Steps for Implementing Agent

1. **Read this entire handoff document** (estimated: 10 minutes)
2. **Start with Phase 1 exploration** to verify environment
3. **Follow dry-run sequence** through all 5 phases
4. **Run all tests** before deploying to Railway
5. **Monitor Railway logs** during deployment
6. **Test ChatGPT integration** after successful deploy
7. **Update documentation** when complete

**Estimated Total Time:** 3-4 hours

**Questions?** Review the plan.json for detailed task breakdown or check CLAUDE.md for architecture details.

---

## ✅ Handoff Checklist

- ✅ Implementation plan created (plan.json)
- ✅ Plan committed to git
- ✅ Handoff document created (this file)
- ✅ Context documented
- ✅ Dry-run provided
- ✅ Potential issues documented
- ✅ Success metrics defined
- ✅ Resources linked

**Status:** Ready for implementation

**Created:** 2025-10-20
**Workorder:** WO-UNIFIED-MCP-HTTP-SERVER-001
**By:** Claude Code AI

---

🚀 **Ready for next agent to begin implementation!**
