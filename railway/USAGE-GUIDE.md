# MCP Server Railway Deployment - Usage Guide

## Server Details

| Item | Value |
|------|-------|
| **URL** | `https://mcp-server-production-0ef4.up.railway.app` |
| **API Key** | `3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3` |
| **Tools Available** | 38 |
| **Auth Header** | `X-API-Key` |

---

# All Ways to Use Your Railway MCP Server

## AI Assistants & Chatbots

| Platform | How to Connect |
|----------|----------------|
| **ChatGPT Custom GPT** | Actions → Import OpenAPI spec |
| **OpenAI API** | Function calling with HTTP requests |
| **Claude API** | Tool use with HTTP requests |
| **Google Gemini** | Function calling |
| **Microsoft Copilot Studio** | Custom connector |
| **Slack Bot** | Bot that calls your API |
| **Discord Bot** | Bot that calls your API |
| **Telegram Bot** | Bot that calls your API |

## AI Frameworks & Orchestration

| Framework | Integration |
|-----------|-------------|
| **LangChain** | Custom tool wrapper |
| **LlamaIndex** | Tool integration |
| **AutoGPT** | Custom action |
| **CrewAI** | Tool definition |
| **Semantic Kernel** | Plugin |

## Development & Testing

| Tool | Use Case |
|------|----------|
| **Postman** | API testing & collections |
| **Insomnia** | REST client |
| **curl** | Command line testing |
| **HTTPie** | CLI HTTP client |
| **VS Code REST Client** | In-editor testing |

## Programming Languages

| Language | Example |
|----------|---------|
| **Python** | `requests` library |
| **JavaScript/Node** | `fetch` or `axios` |
| **TypeScript** | Type-safe API calls |
| **Go** | `net/http` |
| **Rust** | `reqwest` |
| **C#/.NET** | `HttpClient` |
| **Java** | `HttpURLConnection` |
| **Ruby** | `Net::HTTP` |
| **PHP** | `curl` or `Guzzle` |

## Automation & No-Code

| Platform | Integration |
|----------|-------------|
| **Zapier** | Webhooks / Custom API |
| **Make (Integromat)** | HTTP module |
| **n8n** | HTTP Request node |
| **Power Automate** | HTTP connector |
| **IFTTT** | Webhooks |
| **Pipedream** | HTTP action |

## CI/CD & DevOps

| Platform | Use Case |
|----------|----------|
| **GitHub Actions** | Workflow step |
| **GitLab CI** | Job script |
| **Jenkins** | Pipeline stage |
| **CircleCI** | Job step |

## Other

| Use Case | Description |
|----------|-------------|
| **Browser Extension** | Chrome/Firefox extension |
| **Mobile App** | iOS/Android HTTP calls |
| **Desktop App** | Electron, Tauri |
| **Webhooks** | Triggered by other services |
| **Cron Jobs** | Scheduled API calls |
| **IoT Devices** | ESP32, Raspberry Pi |

---

# Quick Start Examples

## Python

```python
import requests

API_KEY = "3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3"
BASE_URL = "https://mcp-server-production-0ef4.up.railway.app"

response = requests.post(
    f"{BASE_URL}/mcp",
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json={"method": "list_templates", "params": {}}
)
print(response.json())
```

## JavaScript / Node.js

```javascript
const API_KEY = "3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3";
const BASE_URL = "https://mcp-server-production-0ef4.up.railway.app";

fetch(`${BASE_URL}/mcp`, {
    method: "POST",
    headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({method: "list_templates", params: {}})
})
.then(r => r.json())
.then(console.log);
```

## curl (Windows)

```bash
curl.exe -X POST "https://mcp-server-production-0ef4.up.railway.app/mcp" -H "X-API-Key: 3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3" -H "Content-Type: application/json" -d "{\"method\":\"list_templates\",\"params\":{}}"
```

## curl (Linux/Mac)

```bash
curl -X POST "https://mcp-server-production-0ef4.up.railway.app/mcp" \
  -H "X-API-Key: 3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3" \
  -H "Content-Type: application/json" \
  -d '{"method":"list_templates","params":{}}'
```

## PowerShell

```powershell
$headers = @{
    "X-API-Key" = "3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3"
    "Content-Type" = "application/json"
}
$body = '{"method":"list_templates","params":{}}'
Invoke-RestMethod -Uri "https://mcp-server-production-0ef4.up.railway.app/mcp" -Method POST -Headers $headers -Body $body
```

---

# Endpoints Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Server info |
| `/health` | GET | No | Health check |
| `/tools` | GET | **Yes** | List all MCP tools (OpenRPC format) |
| `/mcp` | POST | **Yes** | Execute MCP tool calls |
| `/openapi.json` | GET | No | OpenAPI specification |

---

# ChatGPT Custom GPT Setup

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile → **My GPTs** → **Create a GPT**
3. Go to **Configure** tab
4. Scroll to **Actions** → Click **Create new action**
5. Click **Import from URL**
6. Enter: `https://mcp-server-production-0ef4.up.railway.app/openapi.json`
7. Under **Authentication**:
   - Type: **API Key**
   - Auth Type: **Custom**
   - Custom Header Name: `X-API-Key`
8. Click the gear icon next to Authentication
9. Paste API Key: `3ee1f59792038d0ae0f02344631dfd3fa0c9fcf9fcc3b1a973e96bcea23326c3`
10. Save and test!

---

# Available Tools (38 total)

## Documentation
- `list_templates` - List available templates
- `get_template` - Get template content
- `generate_foundation_docs` - Generate all foundation docs
- `generate_individual_doc` - Generate single doc

## Changelog
- `get_changelog` - Query changelog
- `add_changelog_entry` - Add changelog entry
- `update_changelog` - Agentic changelog update

## Planning
- `get_planning_template` - Get planning template
- `analyze_project_for_planning` - Analyze project
- `gather_context` - Gather feature context
- `create_plan` - Create implementation plan
- `validate_implementation_plan` - Validate plan
- `generate_plan_review_report` - Generate review report

## Standards & Audit
- `establish_standards` - Extract coding standards
- `audit_codebase` - Audit for violations
- `check_consistency` - Quick consistency check

## Inventory
- `inventory_manifest` - File inventory
- `dependency_inventory` - Dependencies
- `api_inventory` - API endpoints
- `database_inventory` - Database schemas
- `config_inventory` - Configuration files
- `test_inventory` - Test files
- `documentation_inventory` - Documentation files

## Multi-Agent
- `generate_agent_communication` - Generate communication.json
- `assign_agent_task` - Assign task to agent
- `verify_agent_completion` - Verify agent work
- `aggregate_agent_deliverables` - Aggregate metrics
- `track_agent_status` - Track agent status

## Workflow
- `generate_deliverables_template` - Generate DELIVERABLES.md
- `update_deliverables` - Update with git metrics
- `archive_feature` - Archive completed feature
- `update_all_documentation` - Update all docs
- `execute_plan` - Generate TodoWrite tasks
- `log_workorder` - Log workorder
- `get_workorder_log` - Query workorder log
- `generate_handoff_context` - Generate handoff context
- `assess_risk` - Risk assessment

## Other
- `generate_quickref_interactive` - Generate quickref guide

---

# Security Notes

- API key is required for `/tools` and `/mcp` endpoints
- Keep your API key secret - don't commit to public repos
- Regenerate key in Railway if compromised
- CORS is set to `*` (all origins allowed)

---

**Last Updated:** 2025-12-03
**Status:** Deployed & Secured
