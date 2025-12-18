# Architecture Documentation

## Module Dependency Graph

*Run `coderef index` to generate module dependency diagrams and metrics.*

## Code Patterns

### Handler Functions

- `handle_my_tool` in `handler_decorators.py`
- `handle_my_tool` in `handler_decorators.py`
- `handle_my_tool` in `handler_decorators.py`
- `handle_list_templates` in `tool_handlers.py`
- `handle_get_template` in `tool_handlers.py`
- `handle_generate_foundation_docs` in `tool_handlers.py`
- `handle_generate_individual_doc` in `tool_handlers.py`
- `handle_get_changelog` in `tool_handlers.py`
- `handle_add_changelog_entry` in `tool_handlers.py`
- `handle_update_changelog` in `tool_handlers.py`

### Common Decorators

- `@pytest.mark.asyncio` (131 uses)
- `@mcp_error_handler` (79 uses)
- `@log_invocation` (69 uses)
- `@pytest.fixture` (62 uses)
- `@app.route` (18 uses)
- `@pytest.mark.performance` (14 uses)
- `@staticmethod` (10 uses)
- `@app.get` (9 uses)
- `@test.com` (6 uses)
- `@example.com` (3 uses)

### Error Types

- `TimeoutError`
- `FileNotFoundError`
- `PermissionError`
- `RuntimeError`
- `ValueError`
- `UnicodeEncodeError`
- `ImportError`
- `IOError`
- `OSError`
- `UnicodeDecodeError`

## API Architecture

**Frameworks:** Flask, FastAPI
**Authentication:** Unknown
**Error Format:** RFC 7807
**Endpoint Count:** 27


*Generated: 2025-12-15T15:05:23.284036*