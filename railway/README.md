# Railway MCP Server Deployment

Multi-server MCP gateway deployed on Railway with API key authentication.

## Server Details

| Property | Value |
|----------|-------|
| **URL** | `https://mcp-server-production-0ef4.up.railway.app` |
| **API Key** | `3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3` |
| **Servers** | 3 (docs-mcp, personas-mcp, coderef-mcp) |
| **Total Tools** | 54 |
| **Version** | 2.0.0 |

## Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | No | Server info |
| `/health` | GET | No | Health check with server status |
| `/debug` | GET | No | Debug info (import errors, loaded servers) |
| `/openapi.json` | GET | No | OpenAPI specification |
| `/tools` | GET | **Yes** | List all available tools (OpenRPC format) |
| `/mcp` | POST | **Yes** | Execute MCP tool calls |

## Authentication

Protected endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" https://mcp-server-production-0ef4.up.railway.app/tools
```

## Quick Start

### Check Server Status
```bash
curl https://mcp-server-production-0ef4.up.railway.app/health
```

### List Available Tools
```bash
curl -H "X-API-Key: 3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3" \
  https://mcp-server-production-0ef4.up.railway.app/tools
```

### Execute a Tool
```bash
curl -X POST \
  -H "X-API-Key: 3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3" \
  -H "Content-Type: application/json" \
  -d '{"method": "list_templates", "params": {}}' \
  https://mcp-server-production-0ef4.up.railway.app/mcp
```

## Loaded Servers

### docs-mcp (38 tools)
Documentation generation, changelog management, planning workflows, project inventory.

Key tools:
- `list_templates` - List documentation templates
- `generate_foundation_docs` - Generate project documentation
- `get_changelog` / `add_changelog_entry` - Changelog management
- `create_plan` / `validate_implementation_plan` - Implementation planning
- `inventory_manifest` / `dependency_inventory` - Project inventory

### personas-mcp (8 tools)
AI persona management for specialized expertise.

Key tools:
- `list_personas` - List available personas
- `use_persona` - Activate a persona
- `get_active_persona` - Get current persona
- `clear_persona` - Deactivate persona
- `create_custom_persona` - Create new persona

### coderef-mcp (8 tools)
Code reference analysis and semantic queries.

Key tools:
- `mcp__coderef__query` - Query code elements
- `mcp__coderef__analyze` - Deep code analysis
- `mcp__coderef__validate` - Validate references
- `mcp__coderef__nl_query` - Natural language queries

## Configuration

### Railway Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MCP_API_KEY` | Yes | API key for authentication |
| `STANDALONE_MODE` | No | `true` = only docs-mcp, `false` = all servers |
| `ALLOWED_ORIGINS` | No | CORS origins (default: `*`) |

### Deployment

The server auto-deploys from GitHub on push to main branch.

```bash
# Local testing
cd docs-mcp
python http_server.py

# Push to deploy
git add . && git commit -m "Update" && git push
```

## Testing

Run the test suite:

```bash
cd railway/test
python test_railway_mcp.py
```

Or with pytest:

```bash
pytest test_railway_mcp.py -v
```

## Architecture

```
Railway
└── http_server.py (Flask gateway)
    ├── docs-mcp/server.py (38 tools)
    ├── personas-mcp/server.py (8 tools)
    └── coderef-mcp/server.py (8 tools)
```

### Multi-Server Loading

The gateway dynamically loads all MCP servers from sibling directories:
1. Adds each server's directory to `sys.path`
2. Clears conflicting module names to prevent collisions
3. Imports server module and extracts tools
4. Builds unified tool registry

### Authentication Flow

```
Request → check_api_key() → Route to handler
           ↓
    Public endpoint? → Allow
           ↓
    API key valid? → Allow
           ↓
    Return 401 Unauthorized
```

## Files

```
railway/
├── README.md           # This file
├── USAGE-GUIDE.md      # Comprehensive usage examples
├── API-TEST.md         # Quick API test reference
└── test/
    └── test_railway_mcp.py  # Test suite
```

## Troubleshooting

### Check for import errors
```bash
curl https://mcp-server-production-0ef4.up.railway.app/debug
```

### Verify servers loaded
```bash
curl https://mcp-server-production-0ef4.up.railway.app/health
```

### Common issues

1. **401 Unauthorized**: Check API key in `X-API-Key` header
2. **Server failed to load**: Check `/debug` for import errors
3. **Tool not found**: Verify tool name via `/tools` endpoint

## Security

- API key required for `/tools` and `/mcp` endpoints
- Keep API key secret - don't commit to public repos
- Regenerate key in Railway dashboard if compromised
- CORS set to `*` by default (configure via `ALLOWED_ORIGINS`)

---

**Last Updated**: 2025-12-03
**Status**: Deployed & Operational
