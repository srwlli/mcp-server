# CodeRef Ecosystem - Reference Paths

Quick reference for agents working in the coderef ecosystem.

---

## Primary References

### 1. CodeRef Dashboard (Workflows UI)
**URL:** `http://localhost:3000/prompts`
**Purpose:** Interactive prompting workflow system - select prompts, add attachments, export for agent execution
**Local Path:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\prompts\`

### 2. Intelligence Directory
**Path:** `C:\Users\willh\.mcp-servers\coderef\intelligence\`
**Purpose:** AI-generated insights, analysis reports, ecosystem reviews

### 3. Workflows Documentation
**Path:** `C:\Users\willh\Desktop\assistant\coderef\workflows\`
**Purpose:** Paired .md/.json workflow documentation (human + AI readable)
**Subfolders:**
- `prompts/` - Standardized prompt templates
- `note/` - Meta-documentation and guides

### 4. Sessions Coordination
**Path:** `C:\Users\willh\.mcp-servers\coderef\sessions\`
**Purpose:** Active multi-agent coordination sessions
**Subfolders:**
- `inventory-docs/` - Current I/O inventory session
- `output/` - Agent output files

### 5. Global Workorder Log
**Path:** `C:\Users\willh\.mcp-servers\coderef\workorder-log.txt`
**Purpose:** Centralized workorder tracking across all projects
**Format:** `WO-ID | Project | Description | Timestamp`

---

## Additional Key Locations

### Foundation Docs (Per Project)
```
{project}/coderef/foundation-docs/
├── README.md
├── ARCHITECTURE.md
├── API.md
├── COMPONENTS.md
├── SCHEMA.md
└── CLAUDE.md (root level)
```

### Standards Docs (Per Project)
```
{project}/coderef/standards/
├── ui-patterns.md
├── behavior-patterns.md
├── ux-patterns.md
└── standards-overview.md
```

### Workorder Files (Per Project)
```
{project}/coderef/workorder/{feature-name}/
├── context.json
├── plan.json
├── communication.json
└── DELIVERABLES.md
```

### CodeRef Analysis Outputs (Per Project)
```
{project}/.coderef/
├── index.json
├── context.md
├── reports/
│   ├── patterns.json
│   ├── coverage.json
│   └── complexity.json
├── diagrams/
│   ├── dependencies.mmd
│   └── dependencies.dot
└── exports/
    └── graph.json
```

---

## MCP Server Locations

All MCP servers located at: `C:\Users\willh\.mcp-servers\`

- `coderef-context/`
- `coderef-workflow/`
- `coderef-docs/`
- `coderef-personas/`
- `coderef-testing/`
- `papertrail/`

---

## Target Projects (CodeRef Ecosystem)

### Core Projects
- **Assistant (Orchestrator):** `C:\Users\willh\Desktop\assistant\`
- **CodeRef System:** `C:\Users\willh\Desktop\projects\coderef-system\`
- **CodeRef Dashboard:** `C:\Users\willh\Desktop\coderef-dashboard\`

### MCP Servers
- **CodeRef Context:** `C:\Users\willh\.mcp-servers\coderef-context\`
- **CodeRef Workflow:** `C:\Users\willh\.mcp-servers\coderef-workflow\`
- **CodeRef Docs:** `C:\Users\willh\.mcp-servers\coderef-docs\`
- **CodeRef Personas:** `C:\Users\willh\.mcp-servers\coderef-personas\`
- **CodeRef Testing:** `C:\Users\willh\.mcp-servers\coderef-testing\`
- **Papertrail:** `C:\Users\willh\.mcp-servers\papertrail\`

---

**Created:** 2026-01-01
**Workorder:** WO-CODEREF-IO-INVENTORY-001
**Purpose:** Quick reference for agent navigation
