# MCP-CLIENT.md - mcp_client.py Authoritative Reference

**File:** `mcp_client.py`
**Category:** Infrastructure / Inter-Server Communication
**Lines:** 243
**Version:** 1.2.0
**Status:** ✅ Production
**Generated:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-P1-001

---

## 1. Purpose & Scope

**What It Does:**
`mcp_client.py` is an async MCP (Model Context Protocol) client that enables inter-server communication. It allows coderef-workflow MCP server to call tools from coderef-context MCP server using JSON-RPC 2.0 protocol over stdio transport.

**Key Innovation:**
Singleton pattern with thread-safe async initialization, retry logic, and graceful error handling for reliable cross-server tool invocation.

**What It Returns:**
Dict with `{"success": True, "data": {...}, "tool_name": "..."}` on successful tool calls

**Dependencies:**
- **subprocess** - Spawns coderef-context server process
- **json** - JSON-RPC 2.0 message serialization
- **asyncio** - Async I/O operations with timeouts
- **logging** - Request/response logging for debugging
- **pathlib.Path** - Cross-platform path handling

**Core Workflow:**
```
MCPToolClient.call_tool(tool_name, tool_args)
├─ 1. Ensure connection (spawn subprocess if needed)
├─ 2. Build JSON-RPC 2.0 request
│  └─ {"jsonrpc": "2.0", "id": N, "method": "tools/call", "params": {...}}
├─ 3. Send request to server stdin
├─ 4. Read response from server stdout (with 120s timeout)
├─ 5. Parse JSON response
├─ 6. Handle errors (with retry for transient failures)
└─ 7. Return result dict or raise exception
```

**Performance:**
- Connection startup: ~500ms (subprocess spawn)
- Tool call overhead: ~50-100ms (JSON-RPC serialization + IPC)
- Timeout: 120s (configurable, 5x safety margin for large AST scans)

---

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **_instance** | MCPToolClient (class) | Optional[MCPToolClient] | Class-level singleton | `MCPToolClient._instance` |
| **_lock** | MCPToolClient (class) | asyncio.Lock | Class-level (thread-safe) | `MCPToolClient._lock` |
| **server_script_path** | MCPToolClient instance | str | Constructor argument | `self.server_script_path` |
| **process** | MCPToolClient instance | Optional[subprocess.Popen] | Runtime subprocess | `self.process` |
| **message_id** | MCPToolClient instance | int | Auto-incrementing counter | `self.message_id` |
| **timeout_seconds** | MCPToolClient instance | int | Hardcoded (120s) | `self.timeout_seconds = 120` |
| **max_retries** | MCPToolClient instance | int | Hardcoded (3) | `self.max_retries = 3` |

**Key Insight:** MCPToolClient is a **singleton** - only one instance per Python process. Thread-safe via async lock.

---

## 3. Architecture & Data Flow

### Class Structure

```
MCPToolClient (Singleton)
├─ __init__(server_script_path: Optional[str] = None)
│  └─ Sets paths, initializes process to None
├─ connect() → bool
│  └─ Spawns subprocess, returns True if successful
├─ call_tool(tool_name, tool_args, retry_count=0) → Dict
│  ├─ Ensures connection (spawns subprocess if needed)
│  ├─ Builds JSON-RPC request
│  ├─ Sends to stdin, reads from stdout (with timeout)
│  ├─ Parses response, checks for errors
│  └─ Retries on transient failures (max 3 attempts)
├─ _is_retryable(error_msg: str) → bool
│  └─ Checks if error message matches retryable patterns
├─ disconnect()
│  └─ Gracefully shuts down subprocess
└─ get_instance(server_path=None) → MCPToolClient (classmethod)
   └─ Thread-safe singleton accessor (async with lock)

Convenience Function:
└─ call_coderef_tool(tool_name, tool_args) → Dict
   └─ Shorthand for calling tools without managing client instance
```

### JSON-RPC 2.0 Protocol

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "coderef_scan",
    "arguments": {
      "project_path": "/path/to/project",
      "languages": ["py"]
    }
  }
}
```

**Response Format (Success):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "elements": [...],
    "count": 42
  }
}
```

**Response Format (Error):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32000,
    "message": "Tool execution failed: ..."
  }
}
```

### Retry Logic

```python
# Transient error patterns (retry up to 3 times)
retryable_patterns = [
    "timeout",
    "temporary",
    "busy",
    "try again",
    "connection reset"
]

if retry_count < max_retries and _is_retryable(error_msg):
    await asyncio.sleep(0.5)  # Brief backoff
    return await call_tool(tool_name, tool_args, retry_count + 1)
```

---

## 4. Method Catalog & Contracts

### 4.1 Constructor

```python
def __init__(self, server_script_path: Optional[str] = None)
```

**Args:**
- `server_script_path` (Optional[str]): Path to coderef-context `server.py`
  - If `None`, defaults to `../coderef-context/server.py` (sibling directory)

**Side Effects:**
- Sets `self.server_script_path`
- Initializes `self.process = None`
- Sets `self.message_id = 0`
- Sets `self.timeout_seconds = 120`
- Sets `self.max_retries = 3`
- Logs initialization

**Performance:** <1ms

**Example:**
```python
# Default path (sibling directory)
client = MCPToolClient()

# Custom path
client = MCPToolClient("/path/to/coderef-context/server.py")
```

---

### 4.2 Connection Manager

```python
async def connect(self) -> bool
```

**Purpose:** Spawn coderef-context server subprocess

**Returns:** `True` if connection successful, `False` otherwise

**Side Effects:**
- Creates `subprocess.Popen` process
- Starts `python server.py` with stdio pipes
- Sleeps 500ms to allow server startup
- Logs PID on success

**Error Handling:**
- Returns `False` on any exception
- Logs error message

**Performance:** ~500ms (subprocess spawn + startup delay)

**Example:**
```python
client = MCPToolClient()
connected = await client.connect()
if connected:
    print("Server ready")
```

**Note:** Idempotent - checks if process already running before spawning

---

### 4.3 Tool Invocation (Core API)

```python
async def call_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    retry_count: int = 0
) -> Dict[str, Any]
```

**Purpose:** Call a tool in coderef-context server via JSON-RPC

**Args:**
- `tool_name` (str): Tool to call (e.g., `"coderef_scan"`)
- `tool_args` (Dict): Arguments to pass to tool
- `retry_count` (int): Internal retry counter (0-3)

**Returns:** Dict with structure:
```python
{
    "success": True,
    "data": {...},  # Tool-specific response
    "tool_name": "coderef_scan"
}
```

**Raises:**
- `ConnectionError`: If unable to connect to server
- `TimeoutError`: If tool call exceeds 120s timeout
- `RuntimeError`: If tool execution fails

**Retry Logic:**
- Up to 3 retries for transient errors
- 500ms backoff between retries
- Retryable patterns: timeout, temporary, busy, try again, connection reset

**Performance:**
- First call: ~500ms (connection) + tool execution time
- Subsequent calls: ~50-100ms (IPC) + tool execution time
- Timeout: 120s maximum

**Example:**
```python
client = await MCPToolClient.get_instance()
result = await client.call_tool(
    "coderef_scan",
    {
        "project_path": "/path/to/project",
        "languages": ["py"]
    }
)
print(f"Found {len(result['data']['elements'])} elements")
```

**Security:** No input sanitization - assumes trusted tool names/args

---

### 4.4 Error Detection

```python
def _is_retryable(self, error_msg: str) -> bool
```

**Purpose:** Check if error is transient and worth retrying

**Args:**
- `error_msg` (str): Error message from server

**Returns:** `True` if error matches retryable patterns

**Algorithm:**
```python
retryable_patterns = [
    "timeout", "temporary", "busy",
    "try again", "connection reset"
]
return any(pattern in error_msg.lower() for pattern in retryable_patterns)
```

**Performance:** <1ms (substring search)

**Example:**
```python
client._is_retryable("Connection timeout")  # True
client._is_retryable("Invalid argument")    # False
```

---

### 4.5 Cleanup

```python
async def disconnect(self)
```

**Purpose:** Gracefully shutdown MCP server subprocess

**Side Effects:**
- Closes stdin pipe
- Waits up to 5 seconds for graceful exit
- Kills process if timeout expires
- Logs disconnect event

**Error Handling:**
- Catches all exceptions, logs warnings
- Always attempts `process.kill()` as fallback

**Performance:** ~5-10ms (graceful shutdown) or ~5s (timeout + kill)

**Example:**
```python
client = await MCPToolClient.get_instance()
# ... use client ...
await client.disconnect()
```

---

### 4.6 Singleton Accessor (Recommended API)

```python
@classmethod
async def get_instance(cls, server_path: Optional[str] = None) -> MCPToolClient
```

**Purpose:** Get thread-safe singleton instance

**Args:**
- `server_path` (Optional[str]): Custom server path (only used on first call)

**Returns:** Singleton `MCPToolClient` instance

**Thread Safety:** Uses async lock to prevent race conditions

**Side Effects:**
- First call: Creates instance, spawns subprocess
- Subsequent calls: Returns existing instance

**Performance:**
- First call: ~500ms (singleton creation + subprocess)
- Subsequent calls: <1ms (lock + return)

**Example:**
```python
# Recommended usage pattern
client = await MCPToolClient.get_instance()
result = await client.call_tool("coderef_scan", {...})
```

**Note:** Preferred over direct instantiation for singleton behavior

---

### 4.7 Convenience Function

```python
async def call_coderef_tool(
    tool_name: str,
    tool_args: Dict[str, Any]
) -> Dict[str, Any]
```

**Purpose:** High-level API for calling coderef tools

**Args:**
- `tool_name` (str): Tool to call
- `tool_args` (Dict): Tool arguments

**Returns:** Same as `MCPToolClient.call_tool()`

**Raises:** Same as `MCPToolClient.call_tool()`

**Implementation:**
```python
client = await MCPToolClient.get_instance()
return await client.call_tool(tool_name, tool_args)
```

**Performance:** Identical to `call_tool()` (no overhead)

**Example:**
```python
# Simplest usage pattern
result = await call_coderef_tool("coderef_scan", {
    "project_path": "/path/to/project",
    "languages": ["py"]
})
```

**Recommended For:** Quick one-off tool calls without managing client lifecycle

---

## 5. Integration Points

### 5.1 Called By (Consumers)

**Primary Consumer:**
- `generators/planning_analyzer.py` - Line 215, 397, 445
  - Calls `coderef_scan` for code inventory
  - Calls `coderef_query` for dependency analysis
  - Calls `coderef_patterns` for coding conventions

**Usage Pattern:**
```python
from mcp_client import call_coderef_tool

# In planning analyzer
result = await call_coderef_tool("coderef_scan", {
    "project_path": str(project_path),
    "languages": ["py", "js", "ts"]
})
elements = result["data"]["elements"]
```

---

### 5.2 Calls (Dependencies)

**External Process:**
- `coderef-context/server.py` - Spawned as subprocess
  - Provides tools: `coderef_scan`, `coderef_query`, `coderef_impact`, etc.
  - Communicates via JSON-RPC 2.0 over stdio

**Protocol Stack:**
```
mcp_client.py (JSON-RPC client)
    ↓ stdin/stdout pipes
subprocess.Popen (Python interpreter)
    ↓ executes
coderef-context/server.py (JSON-RPC server)
    ↓ wraps
@coderef/core CLI (TypeScript code analysis)
```

---

### 5.3 Integration Examples

**Example 1: Planning Workflow (planning_analyzer.py)**
```python
# Line 215: Read index for inventory
try:
    result = await call_coderef_tool("coderef_scan", {
        "project_path": str(project_path),
        "languages": ["py"]
    })
    elements = result["data"]["elements"]
except Exception as e:
    logger.warning(f"coderef_scan failed: {e}. Falling back to filesystem scan.")
    elements = []  # Fallback to regex-based scan
```

**Example 2: Dependency Analysis (planning_analyzer.py)**
```python
# Line 397: Call MCP tool for reference components
result = await call_coderef_tool("coderef_query", {
    "project_path": str(project_path),
    "query_type": "depends-on-me",
    "target": component_name
})
dependents = result["data"]["dependents"]
```

**Example 3: Pattern Detection (planning_analyzer.py)**
```python
# Line 445: Read patterns for conventions
result = await call_coderef_tool("coderef_patterns", {
    "project_path": str(project_path)
})
patterns = result["data"]["patterns"]
```

---

## 6. Error Handling & Failure Modes

### 6.1 Connection Failures

**Symptom:** `ConnectionError: Failed to connect to MCP server`

**Causes:**
- coderef-context server.py not found
- Python interpreter not in PATH
- Subprocess spawn permission denied

**Recovery:**
- Returns `False` from `connect()`
- Raises `ConnectionError` on `call_tool()`

**Mitigation:**
```python
try:
    result = await call_coderef_tool("coderef_scan", {...})
except ConnectionError:
    logger.error("MCP server unavailable. Using fallback analysis.")
    # Fallback to regex-based analysis
```

---

### 6.2 Timeout Errors

**Symptom:** `TimeoutError: Tool call 'coderef_scan' exceeded 120s timeout`

**Causes:**
- Large codebase (>100K LOC)
- Slow disk I/O
- AST parsing hangs on malformed code

**Recovery:**
- Raises `TimeoutError` (no retry for timeouts)

**Mitigation:**
- Increase `timeout_seconds` for large codebases
- Filter languages to reduce scan scope
- Use `.gitignore` patterns to exclude node_modules/vendor

**Example:**
```python
client = await MCPToolClient.get_instance()
client.timeout_seconds = 300  # 5 minutes for large repos
result = await client.call_tool("coderef_scan", {...})
```

---

### 6.3 Tool Execution Failures

**Symptom:** `RuntimeError: MCP tool 'coderef_scan' failed: [error message]`

**Causes:**
- Invalid tool arguments
- Tool bug or crash
- Project path not found

**Recovery:**
- Retries up to 3 times if error is retryable
- Raises `RuntimeError` if all retries fail

**Mitigation:**
```python
try:
    result = await call_coderef_tool("coderef_scan", {
        "project_path": "/invalid/path"
    })
except RuntimeError as e:
    logger.error(f"Tool failed: {e}")
    # Fallback or abort
```

---

### 6.4 Response Parsing Errors

**Symptom:** `RuntimeError: Invalid JSON response from MCP server`

**Causes:**
- Server crash mid-response
- Malformed JSON from server
- Stdout corruption (mixed stderr)

**Recovery:**
- Raises `RuntimeError` (no retry)

**Debugging:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Will log full request/response
client = await MCPToolClient.get_instance()
result = await client.call_tool("coderef_scan", {...})
```

---

## 7. Performance Characteristics

### 7.1 Latency Breakdown

| Operation | Cold Start | Warm (Cached) | Notes |
|-----------|------------|---------------|-------|
| `get_instance()` | ~500ms | <1ms | Subprocess spawn |
| `call_tool()` | ~50-100ms | ~50-100ms | IPC overhead |
| `coderef_scan` | ~1-10s | ~1-10s | Depends on codebase size |
| `disconnect()` | ~5-10ms | ~5-10ms | Graceful shutdown |

### 7.2 Memory Usage

- Client instance: ~10KB (negligible)
- Subprocess: ~50-100MB (Python interpreter + coderef-context server)
- Per-call overhead: ~1-2KB (JSON serialization)

### 7.3 Scalability Limits

**Subprocess Model:**
- 1 subprocess per Python process (singleton)
- No connection pooling (single server instance)

**Bottlenecks:**
- Serial execution (one tool call at a time)
- Subprocess spawn latency (~500ms on first call)
- No request pipelining (request/response pairs)

**Optimization Ideas:**
- Connection pooling (multiple server instances)
- Request pipelining (batch multiple calls)
- Persistent server (daemonize coderef-context)

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# test_mcp_client.py

@pytest.mark.asyncio
async def test_connect_success():
    client = MCPToolClient()
    assert await client.connect() == True
    assert client.process is not None
    await client.disconnect()

@pytest.mark.asyncio
async def test_call_tool_success():
    result = await call_coderef_tool("coderef_scan", {
        "project_path": "/path/to/test/project",
        "languages": ["py"]
    })
    assert result["success"] == True
    assert "data" in result

@pytest.mark.asyncio
async def test_timeout_error():
    client = await MCPToolClient.get_instance()
    client.timeout_seconds = 0.1  # Force timeout
    with pytest.raises(TimeoutError):
        await client.call_tool("coderef_scan", {...})

def test_is_retryable():
    client = MCPToolClient()
    assert client._is_retryable("Connection timeout") == True
    assert client._is_retryable("Invalid argument") == False
```

### 8.2 Integration Tests

```python
@pytest.mark.integration
async def test_planning_analyzer_integration():
    """Test real planning_analyzer.py usage"""
    from generators.planning_analyzer import PlanningAnalyzer

    analyzer = PlanningAnalyzer(Path("/path/to/project"))
    analysis = await analyzer.analyze()

    # Should have called coderef tools
    assert "foundation_docs" in analysis
    assert "coding_standards" in analysis
```

---

## 9. Configuration & Customization

### 9.1 Environment Variables

**Not Used:** No environment variable support (hardcoded paths)

### 9.2 Constructor Configuration

```python
# Custom server path
client = MCPToolClient(
    server_script_path="/custom/path/coderef-context/server.py"
)

# Default path (sibling directory)
client = MCPToolClient()  # Uses ../coderef-context/server.py
```

### 9.3 Runtime Configuration

```python
client = await MCPToolClient.get_instance()

# Increase timeout for large repos
client.timeout_seconds = 300  # 5 minutes

# Increase retry attempts
client.max_retries = 5

# Call tool with custom settings
result = await client.call_tool("coderef_scan", {...})
```

---

## 10. Security Considerations

### 10.1 Input Validation

**Tool Name:**
- ❌ No validation - trusts caller
- ⚠️ Could execute arbitrary MCP methods if server supports them

**Tool Arguments:**
- ❌ No sanitization - passed as-is
- ⚠️ Path traversal possible if tool args include file paths

**Mitigation:**
- Trust boundary at caller level (planning_analyzer validates inputs)
- Server-side validation in coderef-context server

### 10.2 Subprocess Security

**Command Injection:**
- ✅ Safe - uses `subprocess.Popen` with list args (not shell=True)

**Environment Isolation:**
- ⚠️ Subprocess inherits parent environment
- ⚠️ Could expose sensitive env vars to server

**Mitigation:**
```python
# Sanitize environment before spawning
import os
safe_env = {k: v for k, v in os.environ.items() if not k.startswith("SECRET_")}
self.process = subprocess.Popen(
    ["python", self.server_script_path],
    env=safe_env,  # Use sanitized environment
    ...
)
```

### 10.3 Resource Exhaustion

**Timeout Protection:**
- ✅ 120s timeout prevents infinite hangs

**Memory Limits:**
- ❌ No memory limit on subprocess
- ⚠️ Large AST scans could OOM

**Process Limits:**
- ✅ Singleton pattern prevents subprocess explosion

---

## 11. Maintenance & Evolution

### 11.1 Recent Changes (v1.2.0)

- ✅ Increased timeout from 30s to 120s (5x safety margin)
- ✅ Added singleton pattern with thread-safe async lock
- ✅ Enhanced retry logic with transient error detection
- ✅ Improved error logging for debugging

### 11.2 Known Issues

**None reported** - System is stable in production

### 11.3 Future Enhancements

**P1 (High Priority):**
- Connection pooling for concurrent tool calls
- Request pipelining to batch multiple calls
- Health check mechanism (ping/pong)

**P2 (Medium Priority):**
- Automatic retry backoff (exponential instead of fixed 500ms)
- Server keepalive (detect and restart crashed processes)
- Metrics collection (call latency, success rate)

**P3 (Low Priority):**
- TLS encryption for stdio transport
- Authentication tokens for multi-tenant servers
- Request cancellation support

---

## 12. Related Resources

### 12.1 Related Files

- **generators/planning_analyzer.py** - Primary consumer (lines 215, 397, 445)
- **coderef-context/server.py** - Server implementation
- **constants.py** - Path constants (future integration)

### 12.2 External Documentation

- **MCP Protocol Spec:** https://modelcontextprotocol.io/docs
- **JSON-RPC 2.0 Spec:** https://www.jsonrpc.org/specification
- **Python asyncio:** https://docs.python.org/3/library/asyncio.html

### 12.3 Generated Artifacts

- **coderef/schemas/mcp-client-schema.json** - JSON Schema type definitions
- **coderef/.jsdoc/mcp-client-jsdoc.txt** - JSDoc inline documentation suggestions

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P1-001
**Task:** SHEET-006
**Timestamp:** 2026-01-02
**Maintained by:** willh, Claude Code AI
