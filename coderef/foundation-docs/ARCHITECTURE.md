# Architecture Documentation

## Module Dependency Graph

*Auto-scan attempted but failed. Check that:*
- *Node.js is installed*
- *CODEREF_CLI_PATH environment variable is set correctly*
- *The coderef CLI is built (`pnpm build` in cli directory)*

## Code Patterns

### Handler Functions

- `handle_coderef_scan` in `coderef-context\server.py`
- `handle_coderef_query` in `coderef-context\server.py`
- `handle_coderef_impact` in `coderef-context\server.py`
- `handle_coderef_complexity` in `coderef-context\server.py`
- `handle_coderef_patterns` in `coderef-context\server.py`
- `handle_coderef_coverage` in `coderef-context\server.py`
- `handle_coderef_context` in `coderef-context\server.py`
- `handle_coderef_validate` in `coderef-context\server.py`
- `handle_coderef_drift` in `coderef-context\server.py`
- `handle_coderef_diagram` in `coderef-context\server.py`

### Common Decorators

- `@pytest.mark.asyncio` (386 uses)
- `@pytest.fixture` (155 uses)
- `@mcp_error_handler` (107 uses)
- `@log_invocation` (97 uses)
- `@Fn` (58 uses)
- `@patch` (46 uses)
- `@coderef` (45 uses)
- `@staticmethod` (39 uses)
- `@app.route` (19 uses)
- `@dataclass` (19 uses)

### Error Types

- `ServiceUnavailableError`
- `RuntimeError`
- `ValidationError`
- `TypeError`
- `TimeoutError`
- `UnicodeDecodeError`
- `ConnectionError`
- `AssertionError`
- `OSError`
- `JSONSchemaValidationError`

## API Architecture

**Frameworks:** FastAPI, Flask
**Authentication:** Unknown
**Error Format:** RFC 7807
**Endpoint Count:** 30

## Recent Activity


*Generated: 2025-12-31T02:19:16.648501*