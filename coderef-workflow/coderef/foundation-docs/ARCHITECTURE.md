# Architecture Documentation

## Overview



## Module Dependency Graph

*Auto-scan attempted but failed. Check that:*
- *Node.js is installed*
- *CODEREF_CLI_PATH environment variable is set correctly*
- *The coderef CLI is built (`pnpm build` in cli directory)*

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

- `@pytest.mark.asyncio` (62 uses)
- `@log_invocation` (58 uses)
- `@mcp_error_handler` (58 uses)
- `@staticmethod` (16 uses)
- `@pytest.fixture` (5 uses)
- `@classmethod` (2 uses)
- `@wraps` (2 uses)
- `@app` (2 uses)
- `@app.list_tools` (1 uses)
- `@app.call_tool` (1 uses)

### Error Types

- `UnicodeDecodeError`
- `PermissionError`
- `FileNotFoundError`
- `IOError`
- `TimeoutError`
- `RuntimeError`
- `ValueError`
- `ConnectionError`
- `OSError`


*Generated: 2025-12-27T01:21:53.097177*