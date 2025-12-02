# ChatGPT MCP Connector Integration - Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** 2025-10-20
**Based on:** Real integration experience with docs-mcp

---

## Table of Contents

1. [The Journey: What Actually Happened](#the-journey-what-actually-happened)
2. [Error 1: 404 on /sse](#error-1-404-on-sse)
3. [Error 2: 404 on Root URL](#error-2-404-on-root-url)
4. [Error 3: Request Timeout](#error-3-request-timeout)
5. [The Working Solution](#the-working-solution)
6. [Why Only docs-mcp is Exposed](#why-only-docs-mcp-is-exposed)
7. [Testing Checklist](#testing-checklist)

---

## The Journey: What Actually Happened

We attempted to connect ChatGPT to our MCP server hosted on Railway. Here's the chronological progression of errors we encountered and fixed:

### Initial State
- **Server:** docs-mcp deployed on Railway
- **URL:** `https://docs-mcp-production.up.railway.app`
- **Endpoints available:** `/health`, `/mcp` (JSON-RPC), `/tools` (OpenRPC)
- **Expected:** 4 MCP servers (docs-mcp, coderef-mcp, hello-world-mcp, personas-mcp)
- **Reality:** Only docs-mcp is in the HTTP wrapper

---

## Error 1: 404 on /sse

### What Happened
```
Error creating connector
Client error '404 Not Found' for url 'https://docs-mcp-production.up.railway.app/sse'
```

### Root Cause
ChatGPT tried to establish a Server-Sent Events (SSE) connection by probing for `/sse` endpoint. Our server didn't have this endpoint.

### What We Learned
ChatGPT's MCP connector expects an SSE endpoint for real-time streaming communication, even though it ultimately uses the `/mcp` endpoint for JSON-RPC.

### The Fix

**Added SSE endpoint to `http_server.py`:**

```python
@app.route('/sse', methods=['GET'])
def sse_endpoint():
    """
    Server-Sent Events (SSE) endpoint for ChatGPT MCP connector.
    ChatGPT expects a text/event-stream response for SSE transport.
    Returns streaming response with proper SSE headers.
    """
    logger.info("SSE endpoint accessed by ChatGPT connector")

    def generate():
        # Send initial connection event
        yield 'event: connected\n'
        yield 'data: {"status":"ok","transport":"sse"}\n\n'

    from flask import Response
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )
```

**Key details:**
- Content-Type: `text/event-stream` (not `application/json`)
- Headers: Must include `Cache-Control`, `Connection`, `X-Accel-Buffering`
- Format: SSE format with `event:` and `data:` lines

**Verification:**
```bash
curl -H "Accept: text/event-stream" https://docs-mcp-production.up.railway.app/sse
# Returns:
# event: connected
# data: {"status":"ok","transport":"sse"}
```

### Deployment
```bash
git add http_server.py
git commit -m "Add /sse endpoint for ChatGPT MCP connector handshake"
git push origin main
# Wait 30-60 seconds for Railway deployment
```

---

## Error 2: 404 on Root URL

### What Happened
```
Error creating connector
Client error '404 Not Found' for url 'https://docs-mcp-production.up.railway.app'
```

### Root Cause
ChatGPT probes the **root URL** (`/`) before trying `/sse` or `/mcp`. Our server had no root endpoint, so it returned 404.

### What We Learned
ChatGPT does a probe sequence:
1. `GET /` → expects 200 OK
2. `GET /sse` → expects SSE stream
3. `POST /mcp` with `initialize` → required for actual connection

### The Fix

**Added root endpoint to `http_server.py`:**

```python
@app.route('/', methods=['GET'])
def root() -> Tuple[Dict[str, Any], int]:
    """Root endpoint - MCP server information."""
    return jsonify({
        'name': 'docs-mcp HTTP Server',
        'version': '2.0.0',
        'description': 'MCP server providing 33 tools for documentation generation, changelog management, planning workflows, and project inventory',
        'endpoints': {
            'health': '/health',
            'tools': '/tools (OpenRPC 1.3.2 discovery)',
            'sse': '/sse (Server-Sent Events)',
            'mcp': '/mcp (JSON-RPC 2.0 invocation)'
        },
        'total_tools': len(TOOL_HANDLERS)
    }), 200
```

**Key details:**
- Returns server metadata
- Lists all available endpoints
- Shows tool count
- Helps with debugging

**Verification:**
```bash
curl https://docs-mcp-production.up.railway.app/
# Returns JSON with server info and endpoints
```

### Deployment
```bash
git add http_server.py
git commit -m "Add root endpoint for ChatGPT MCP connector probe"
git push origin main
# Wait 30-60 seconds for Railway deployment
```

---

## Error 3: Request Timeout

### What Happened
```
Error creating connector
Request timeout
```

### Root Cause
We were providing the **base URL** instead of the **specific /mcp endpoint**:
- ❌ Wrong: `https://docs-mcp-production.up.railway.app`
- ✅ Correct: `https://docs-mcp-production.up.railway.app/mcp`

### What We Learned
According to OpenAI's official documentation:

> **Connector URL**: "the public `/mcp` endpoint of your server (for example `https://abc123.ngrok.app/mcp`)"

ChatGPT expects the **full path** to the MCP endpoint, not just the domain.

### The Fix

**Use the correct URL format in ChatGPT Settings:**

```
https://docs-mcp-production.up.railway.app/mcp
```

**Not:**
```
https://docs-mcp-production.up.railway.app
https://docs-mcp-production.up.railway.app/
https://docs-mcp-production.up.railway.app/sse
```

### Verification

Test the endpoint directly:

```bash
curl -X POST https://docs-mcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {}
    },
    "serverInfo": {
      "name": "docs-mcp",
      "version": "2.0.0"
    }
  }
}
```

---

## The Working Solution

### Final Configuration

**ChatGPT Connector Settings:**
- **Connector name:** docs-mcp
- **Description:** Documentation generation and project management tools
- **Connector URL:** `https://docs-mcp-production.up.railway.app/mcp` ← **Must include /mcp**

### Required Endpoints

Our `http_server.py` now has these endpoints:

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/` | GET | Server info | ✅ Added |
| `/health` | GET | Health check | ✅ Existing |
| `/tools` | GET | OpenRPC 1.3.2 discovery | ✅ Existing |
| `/sse` | GET | Server-Sent Events | ✅ Added |
| `/mcp` | POST | JSON-RPC 2.0 invocation | ✅ Existing |

### What Worked

After adding the root and SSE endpoints, and using the correct `/mcp` URL:

1. ✅ ChatGPT successfully created the connector
2. ✅ All 33 tools from docs-mcp are visible
3. ✅ Tools can be invoked from ChatGPT
4. ✅ Connection is stable

### Commits Made

```bash
# Commit 1: Added SSE endpoint
git commit -m "Add /sse endpoint for ChatGPT MCP connector handshake"

# Commit 2: Added root endpoint
git commit -m "Add root endpoint for ChatGPT MCP connector probe"

# Commit 3: Fixed SSE to return proper stream
git commit -m "Fix /sse endpoint to return proper SSE stream"
```

---

## Why Only docs-mcp is Exposed

### Current Architecture

```
ChatGPT
    ↓
Railway (HTTPS)
    ↓
http_server.py (Flask)
    ↓
docs-mcp/server.py (33 tools)

❌ NOT INCLUDED:
   - coderef-mcp/server.py
   - hello-world-mcp/server.py
   - personas-mcp/server.py
```

### Why This Happened

The `http_server.py` file **only imports** `docs-mcp/server.py`:

```python
# In http_server.py
import server  # This imports docs-mcp/server.py

# Later...
tools_list = asyncio.run(server.list_tools())  # Only gets docs-mcp tools
```

### What Would Be Needed

To expose all 4 servers, you would need:

1. **Import all 4 server modules:**
```python
import sys
sys.path.insert(0, '../docs-mcp')
sys.path.insert(0, '../coderef-mcp')
sys.path.insert(0, '../hello-world-mcp')
sys.path.insert(0, '../personas-mcp')

import docs_mcp.server as docs_server
import coderef_mcp.server as coderef_server
# etc.
```

2. **Merge tool lists from all servers:**
```python
all_tools = []
all_tools.extend(await docs_server.list_tools())
all_tools.extend(await coderef_server.list_tools())
all_tools.extend(await hello_server.list_tools())
all_tools.extend(await personas_server.list_tools())
```

3. **Route tool calls to correct server:**
```python
# Map tool names to servers
TOOL_MAP = {}
for tool in all_tools:
    TOOL_MAP[tool.name] = appropriate_server
```

### Current Status

**As of now:**
- ✅ ChatGPT can access all 33 docs-mcp tools
- ❌ coderef-mcp tools not accessible (not in HTTP wrapper)
- ❌ hello-world-mcp tools not accessible (not in HTTP wrapper)
- ❌ personas-mcp tools not accessible (not in HTTP wrapper)

**This is a known limitation** documented in the troubleshooting guide.

---

## Testing Checklist

### Before Creating ChatGPT Connector

Run these tests to verify your server is ready:

**1. Root endpoint responds:**
```bash
curl https://docs-mcp-production.up.railway.app/
# Expected: 200 OK with JSON server info
```

**2. SSE endpoint streams:**
```bash
curl -H "Accept: text/event-stream" https://docs-mcp-production.up.railway.app/sse
# Expected: SSE stream with "event: connected"
```

**3. MCP initialize works:**
```bash
curl -X POST https://docs-mcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
# Expected: JSON-RPC success with serverInfo
```

**4. Tools list works:**
```bash
curl -X POST https://docs-mcp-production.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
# Expected: Array of 33 tools
```

### After Creating ChatGPT Connector

**1. Connector creates successfully** ✅
- No 404 errors
- No timeout errors
- Shows "Connection successful"

**2. Tools are visible** ✅
- ChatGPT lists available tools
- Should show 33 docs-mcp tools

**3. Tools can be invoked** ✅
- Try: "List available documentation templates"
- Should call `list_templates` tool successfully

---

## Quick Reference

### Correct URL Format
```
✅ https://docs-mcp-production.up.railway.app/mcp
❌ https://docs-mcp-production.up.railway.app
❌ https://docs-mcp-production.up.railway.app/
```

### Required Endpoints Checklist
- ✅ `GET /` - Server info (200 OK)
- ✅ `GET /sse` - SSE stream (text/event-stream)
- ✅ `POST /mcp` - JSON-RPC 2.0 (initialize, tools/list, tool invocation)

### Common Mistakes
1. ❌ Using base URL instead of `/mcp` endpoint
2. ❌ Missing `/sse` endpoint (causes 404)
3. ❌ Missing root `/` endpoint (causes 404)
4. ❌ Wrong Content-Type on `/sse` (must be `text/event-stream`)

### If You Still Get Errors

1. Check Railway deployment logs
2. Verify all endpoints return 200
3. Test with curl commands above
4. Use the exact URL format: `https://your-domain/mcp`

---

## Summary

**What we fixed:**
1. Added `/sse` endpoint with proper SSE streaming
2. Added `/` root endpoint for initial probe
3. Used correct URL format with `/mcp` path

**What works now:**
- ✅ ChatGPT connector creates successfully
- ✅ All 33 docs-mcp tools are accessible
- ✅ Tools can be invoked from ChatGPT

**Known limitation:**
- Only docs-mcp is exposed (33 tools)
- Other 3 servers not included in HTTP wrapper
- Would require unified server implementation

---

**Last Updated:** 2025-10-20
**Working Deployment:** Railway @ `https://docs-mcp-production.up.railway.app/mcp`
