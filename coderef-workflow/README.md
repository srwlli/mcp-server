# workorder-mcp

Enterprise-Grade MCP Server for Feature Lifecycle Management and Workflow Orchestration

## Overview

**workorder-mcp** is a specialized MCP server that handles the workflow orchestration side of feature development, including:

- **Context Gathering** - Collect requirements and feature specifications
- **Planning** - Generate detailed implementation plans with task breakdowns
- **Execution** - Orchestrate task execution and progress tracking
- **Deliverables** - Track metrics and completion status
- **Archiving** - Manage completed features

## Relationship to docs-mcp

This is a sister MCP to **docs-mcp**, which handles pure documentation generation. Together they provide a complete feature lifecycle system:

| Server | Purpose | Tools |
|--------|---------|-------|
| **docs-mcp** | Documentation generation & standards | 10 documentation tools |
| **workorder-mcp** | Workflow orchestration | 30 workflow management tools |

Both MCPs share access to the same `coderef/workflow` folder, enabling seamless coordination between documentation and execution phases.

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv sync
```

## Running

```bash
python server.py
```

## Architecture

- **server.py** - MCP entry point and tool registration
- **src/** - Tool implementations
- **generators/** - Planning and analysis generators
- **coderef/workorder/** - Feature workorder directories

## MCP-to-MCP Integration

### Overview

**coderef-workflow** integrates with **coderef-context** MCP server to enhance analysis quality:

- **MCP Client Layer** (`mcp_client.py`): JSON-RPC 2.0 protocol over subprocess stdio
- **Tool Integration**: 4 coderef tools integrated into analysis methods
- **Graceful Fallback**: All tools have fallback implementations when unavailable

### Integrated Tools

| Tool | Method | Purpose | Fallback |
|------|--------|---------|----------|
| `coderef_query` | `find_reference_components()` | Dependency analysis | Regex-based search |
| `coderef_patterns` | `identify_patterns()` | Code pattern detection (99% accuracy) | Regex analysis |
| `coderef_scan` | `read_inventory_data()` | Live AST-based inventory | Read manifest files |
| `coderef_coverage` | `identify_gaps_and_risks()` | Test coverage analysis | Filesystem checks |

### Setup

1. **Install coderef-context MCP** in `~/.mcp-servers/coderef-context/`
2. **Configure Claude Desktop** to load both servers
3. **Server Auto-Connection**: MCPToolClient automatically finds and connects to coderef-context

### Error Handling

All MCP tool calls use try-catch with graceful fallbacks:

```python
try:
    result = await call_coderef_tool("coderef_query", {...})
    # Use result from tool
except Exception as e:
    logger.warning(f"Tool unavailable: {e}, using fallback")
    # Fall back to manual implementation
```

### Testing

- **Unit Tests** (21 tests): `tests/test_mcp_client.py`
  - JSON-RPC protocol, connection management, error handling

- **Integration Tests** (16 tests): `tests/test_planning_analyzer_integration.py`
  - Tool integration, async methods, fallback modes, end-to-end flow

Run tests:
```bash
pytest tests/ -v
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov
```

## License

MIT

## Authors

- willh
- Claude Code AI
