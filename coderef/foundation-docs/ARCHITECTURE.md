# Architecture Documentation

## Overview

# Architecture Documentation

## Module Dependency Graph

*Run `coderef index` to generate module dependency diagrams and metrics.*

## Code Patterns

### Handler Functions

- `handle_query_elements` in `coderef-mcp\tool_handlers.py`
- `handle_analyze_impact` in `coderef-mcp\tool_handlers.py`
- `handle_validate_references` in `coderef-mcp\tool_handlers.py`
- `handle_batch_validate` in `coderef-mcp\tool_handlers.py`
- `handle_generate_docs` in `coderef-mcp\tool_handlers.py`
- `handle_audit` in `coderef-mcp\tool_handlers.py`
- `handle_nl_query` in `coderef-mcp\tool_handlers.py`
- `handle_scan_realtime` in `coderef-mcp\tool_handlers.py`
- `handle_my_tool` in `docs-mcp\handler_decorators.py`
- `handle_my_tool` in `docs-mcp\handler_decorators.py`

### Common Decorators

- `@pytest.mark.asyncio` (214 uses)
- `@pytest.fixture` (101 uses)
- `@mcp_error_handler` (80 uses)
- `@log_invocation` (70 uses)
- `@Fn` (58 uses)
- `@staticmethod` (20 uses)
- `@app.route` (18 uses)
- `@pytest.mark.perform

## Module Dependency Graph

*Run `coderef index` to generate module dependency diagrams and metrics.*

## Code Patterns

### Handler Functions

- `handle_query_elements` in `coderef-mcp\tool_handlers.py`
- `handle_analyze_impact` in `coderef-mcp\tool_handlers.py`
- `handle_validate_references` in `coderef-mcp\tool_handlers.py`
- `handle_batch_validate` in `coderef-mcp\tool_handlers.py`
- `handle_generate_docs` in `coderef-mcp\tool_handlers.py`
- `handle_audit` in `coderef-mcp\tool_handlers.py`
- `handle_nl_query` in `coderef-mcp\tool_handlers.py`
- `handle_scan_realtime` in `coderef-mcp\tool_handlers.py`
- `handle_my_tool` in `docs-mcp\handler_decorators.py`
- `handle_my_tool` in `docs-mcp\handler_decorators.py`

### Common Decorators

- `@pytest.mark.asyncio` (214 uses)
- `@pytest.fixture` (101 uses)
- `@mcp_error_handler` (83 uses)
- `@log_invocation` (73 uses)
- `@Fn` (58 uses)
- `@staticmethod` (20 uses)
- `@app.route` (18 uses)
- `@pytest.mark.performance` (14 uses)
- `@C` (14 uses)
- `@dataclass` (13 uses)

### Error Types

- `ServiceUnavailableError`
- `UnicodeDecodeError`
- `RuntimeError`
- `FileNotFoundError`
- `PermissionError`
- `ValidationError`
- `TimeoutError`
- `IOError`
- `ValueError`
- `ImportError`

## API Architecture

**Frameworks:** Flask, FastAPI
**Authentication:** Unknown
**Error Format:** RFC 7807
**Endpoint Count:** 27

## Recent Activity


*Generated: 2025-12-18T00:34:05.556459*