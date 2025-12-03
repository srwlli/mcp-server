# MCP Server API - Railway Deployment

## Base URL
```
https://mcp-server-production-0ef4.up.railway.app
```

## API Key
```
3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3
```

---

## Test Commands

### With API Key (200 OK)
```
curl.exe -H "X-API-Key: 3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3" "https://mcp-server-production-0ef4.up.railway.app/tools"
```

### Without API Key (401 Unauthorized)
```
curl.exe "https://mcp-server-production-0ef4.up.railway.app/tools"
```

---

## Endpoints

| Endpoint | Auth Required | Description |
|----------|---------------|-------------|
| `/` | No | Server info |
| `/health` | No | Health check |
| `/tools` | **Yes** | List all MCP tools (OpenRPC) |
| `/mcp` | **Yes** | Execute MCP tool calls |
| `/openapi.json` | No | OpenAPI specification |

---

## Authentication

All protected endpoints require the `X-API-Key` header:
```
X-API-Key: 3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3
```

---

## Status: DEPLOYED & SECURED
- Railway URL: Active
- API Key Auth: Working
- 38 MCP tools available
