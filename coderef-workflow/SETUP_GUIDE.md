# MCP Integration Setup & Troubleshooting Guide

## Quick Start

### Prerequisites
- Python 3.10+
- coderef-context MCP server installed
- Claude Desktop or Claude Code configured

### Installation Steps

1. **Install coderef-workflow MCP**
   ```bash
   cd ~/.mcp-servers/coderef-workflow
   pip install -e .
   ```

2. **Install coderef-context MCP** (if not already installed)
   ```bash
   cd ~/.mcp-servers/coderef-context
   pip install -e .
   ```

3. **Configure Claude Desktop** (`~/.claude/claude.json`)
   ```json
   {
     "mcpServers": {
       "coderef-workflow": {
         "command": "python",
         "args": ["~/.mcp-servers/coderef-workflow/server.py"]
       },
       "coderef-context": {
         "command": "python",
         "args": ["~/.mcp-servers/coderef-context/server.py"]
       }
     }
   }
   ```

4. **Verify Installation**
   ```bash
   # Test coderef-workflow MCP
   python server.py

   # Should output MCP server messages
   ```

## Architecture Overview

### Communication Flow

```
Claude Code
    ↓
coderef-workflow MCP (workorder creation, planning)
    ↓
MCPToolClient (JSON-RPC 2.0 over stdio)
    ↓
coderef-context MCP (code analysis tools)
    ↓
Analysis Results (patterns, dependencies, coverage)
```

### JSON-RPC Protocol

MCPToolClient implements JSON-RPC 2.0:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "coderef_query",
  "params": {
    "project_path": "/path/to/project",
    "query_type": "depends-on-me",
    "target": "*",
    "max_depth": 2
  }
}
```

**Response (Success):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true,
    "data": { "component1": {}, "component2": {} }
  }
}
```

**Response (Error):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal server error"
  }
}
```

## MCP Tool Integration

### Integrated Tools

#### 1. coderef_query
**Purpose:** Dependency analysis
**Used in:** `find_reference_components()`
**Query Types:** depends-on-me, depends-on, imports

**Example:**
```python
result = await call_coderef_tool(
    "coderef_query",
    {
        "project_path": "/path/to/project",
        "query_type": "depends-on-me",
        "target": "*",
        "max_depth": 2
    }
)
```

#### 2. coderef_patterns
**Purpose:** Code pattern detection (99% accuracy with AST)
**Used in:** `identify_patterns()`
**Pattern Types:** all, error_handling, naming, organization, component

**Example:**
```python
result = await call_coderef_tool(
    "coderef_patterns",
    {
        "project_path": "/path/to/project",
        "pattern_type": "all",
        "limit": 20
    }
)
```

#### 3. coderef_scan
**Purpose:** Live AST-based inventory generation
**Used in:** `read_inventory_data()`
**Supported Languages:** TypeScript, JavaScript, Python

**Example:**
```python
result = await call_coderef_tool(
    "coderef_scan",
    {
        "project_path": "/path/to/project",
        "languages": ["ts", "tsx", "js", "jsx", "py"]
    }
)
```

#### 4. coderef_coverage
**Purpose:** Test coverage analysis
**Used in:** `identify_gaps_and_risks()`

**Example:**
```python
result = await call_coderef_tool(
    "coderef_coverage",
    {
        "project_path": "/path/to/project",
        "format": "summary"
    }
)
```

## Error Handling & Recovery

### Fallback Strategy

Each MCP tool call includes fallback logic:

```python
try:
    result = await call_coderef_tool(tool_name, args)
    if result.get("success"):
        # Use result from tool
        return process_tool_result(result)
except Exception as e:
    logger.warning(f"Tool {tool_name} failed: {e}, using fallback")
    return fallback_implementation()
```

### Common Errors

#### 1. "coderef-context server not found"
**Cause:** coderef-context MCP not installed or not in expected location
**Solution:**
```bash
# Install coderef-context
cd ~/.mcp-servers/coderef-context
pip install -e .

# Verify path in mcp_client.py defaults
python -c "from pathlib import Path; print(Path(__file__).parent.parent / 'coderef-context' / 'server.py')"
```

#### 2. "Timeout waiting for tool response"
**Cause:** Tool taking too long (> 30 seconds) or server crashed
**Solution:**
- Increase timeout in mcp_client.py: `self.timeout_seconds = 60`
- Check if coderef-context server is responsive
- Review logs in ~/.mcp-servers/coderef-context/

#### 3. "JSON-RPC parse error"
**Cause:** Malformed response from tool
**Solution:**
- Check coderef-context MCP version compatibility
- Review stderr logs from subprocess
- Restart both MCP servers

#### 4. "Tool not found: coderef_xyz"
**Cause:** Tool not available in connected coderef-context version
**Solution:**
- Update coderef-context MCP to latest version
- Check available tools: review coderef-context/server.py

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/test_mcp_client.py -v

# Integration tests only
pytest tests/test_planning_analyzer_integration.py -v

# With coverage
pytest tests/ --cov=generators --cov=mcp_client --cov-report=html
```

### Test Coverage

- **21 unit tests** covering MCPToolClient:
  - JSON-RPC protocol
  - Connection management
  - Error handling
  - Retry logic
  - Timeout handling

- **16 integration tests** covering PlanningAnalyzer:
  - Async method execution
  - Tool integration
  - Fallback modes
  - End-to-end workflows
  - Concurrent execution
  - Error recovery

### Manual Testing

```python
import asyncio
from generators.planning_analyzer import PlanningAnalyzer
from pathlib import Path

async def test():
    analyzer = PlanningAnalyzer(Path("/path/to/project"))

    # Test with coderef tools
    components = await analyzer.find_reference_components()
    patterns = await analyzer.identify_patterns()
    inventory = await analyzer.read_inventory_data()
    risks = await analyzer.identify_gaps_and_risks()

    print(f"Components: {components}")
    print(f"Patterns: {patterns}")
    print(f"Inventory: {inventory}")
    print(f"Risks: {risks}")

asyncio.run(test())
```

## Performance

### Benchmarks

- **find_reference_components()**: 500-2000ms (depends on project size)
- **identify_patterns()**: 1-5s (AST analysis is slower but more accurate)
- **read_inventory_data()**: 2-10s (live AST scan)
- **identify_gaps_and_risks()**: 500-2000ms

### Optimization Tips

1. **Limit project scope** when possible
   - Use smaller directories for testing
   - Exclude node_modules, dist, etc.

2. **Increase timeouts** for large projects
   ```python
   client.timeout_seconds = 60  # From default 30
   ```

3. **Reuse client** via singleton pattern
   ```python
   client = await MCPToolClient.get_instance()
   # Reuse same client instance across calls
   ```

4. **Parallel execution** for independent analyses
   ```python
   results = await asyncio.gather(
       analyzer.find_reference_components(),
       analyzer.identify_patterns(),
   )
   ```

## Logging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Will now show:
# - JSON-RPC requests/responses
# - Tool calls and results
# - Error details with stack traces
```

### Log Locations

- **coderef-workflow**: Check Python stdout/stderr
- **coderef-context**: `~/.mcp-servers/coderef-context/logs/`

### Important Log Messages

```
DEBUG: JSON-RPC request: {"jsonrpc": "2.0", "id": 1, ...}
DEBUG: Calling tool: coderef_query with args: {...}
INFO: Found 5 patterns via coderef_patterns
WARNING: Tool unavailable: timeout, using fallback
ERROR: MCP tool 'coderef_query' failed: Connection refused
```

## Troubleshooting Checklist

- [ ] Both MCP servers installed in `~/.mcp-servers/`
- [ ] Claude Desktop configured with both servers
- [ ] Python 3.10+ installed
- [ ] All dependencies installed: `pip install -e .`
- [ ] coderef-context server is running and responsive
- [ ] Network connectivity between servers (if not localhost)
- [ ] Sufficient disk space for coderef temp files
- [ ] File permissions for reading projects
- [ ] No port conflicts if running multiple instances

## Support & Issues

For issues, check:
1. Server logs: `tail -f ~/.mcp-servers/coderef-context/logs/`
2. Test suite: `pytest tests/ -v`
3. JSON-RPC protocol compliance
4. Python version compatibility (3.10+)

## Next Steps

- Review [MCP Integration Architecture](README.md#mcp-to-mcp-integration)
- Run tests to validate setup: `pytest tests/`
- Check [coderef-context documentation](~/.mcp-servers/coderef-context/README.md)
