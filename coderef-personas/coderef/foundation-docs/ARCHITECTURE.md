# Architecture Documentation

## Module Dependency Graph

*Auto-scan attempted but failed. Check that:*
- *Node.js is installed*
- *CODEREF_CLI_PATH environment variable is set correctly*
- *The coderef CLI is built (`pnpm build` in cli directory)*

## Code Patterns

### Handler Functions

- `handle_use_persona` in `server.py`
- `handle_get_active_persona` in `server.py`
- `handle_clear_persona` in `server.py`
- `handle_list_personas` in `server.py`
- `handle_generate_todo_list` in `server.py`
- `handle_track_plan_execution` in `server.py`
- `handle_execute_plan_interactive` in `server.py`
- `handle_create_custom_persona` in `server.py`

### Common Decorators

- `@pytest.fixture` (22 uses)
- `@Lloyd` (9 uses)
- `@Type` (3 uses)
- `@staticmethod` (3 uses)
- `@app.list_tools` (1 uses)
- `@app.call_tool` (1 uses)
- `@mcp_error_handler` (1 uses)
- `@log_invocation` (1 uses)
- `@Class` (1 uses)
- `@Function` (1 uses)

### Error Types

- `ValidationError`
- `ValueError`
- `FileNotFoundError`
- `JSONSchemaValidationError`


*Generated: 2025-12-20T04:17:11.397811*