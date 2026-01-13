# Document Report: assistant (Orchestrator)

**Agent:** assistant
**Path:** C:\Users\willh\Desktop\assistant
**Workorder:** WO-CODEREF-IO-INVENTORY-002
**Generated:** 2026-01-02

---

## Complete Document List

| Filename | Type | I/O | Source/Destination | Notes |
|----------|------|-----|-------------------|-------|
| CLAUDE.md | foundation_doc | input | Self (orchestrator) | Primary context document |
| projects.md | other | both | Self (orchestrator) | Master project list, stub inventory |
| workorders.json | workflow_doc | both | Self (orchestrator) | Centralized workorder tracking |
| terminal-profiles.md | other | both | Self (orchestrator) | Windows Terminal config reference |
| stub-schema.json | config | input | Self (orchestrator) | Canonical stub validation schema |
| coderef/working/{feature}/stub.json | workflow_doc | both | Self → MCP servers | Stub metadata for ideas |
| coderef/workflows/*.md | other | both | Self (orchestrator) | Workflow documentation |
| coderef/workflows/*.json | other | both | Self (orchestrator) | Workflow schemas |
| coderef/workflows/prompts/*.json | other | both | Self (orchestrator) | Standardized prompt templates |
| {project}/coderef/workorder/{feature}/context.json | workflow_doc | both | Self → MCP servers | Workorder context delegation |
| {project}/coderef/workorder/{feature}/communication.json | workflow_doc | both | Self ↔ All agents | Multi-agent coordination |
| {project}/coderef/workorder/{feature}/plan.json | workflow_doc | input | MCP servers → Self | Implementation plans verification |
| {project}/coderef/workorder/{feature}/DELIVERABLES.md | workflow_doc | input | MCP servers → Self | Completion metrics verification |
| index.html | other | output | Self (orchestrator) | Visual workorder dashboard |
| .mcp/coderef/sessions/inventory-docs/*.json | workflow_doc | output | Self (orchestrator) | Session coordination files |
| coderef/sessions/inventory-docs/*.json | workflow_doc | output | Self (orchestrator) | Inventory coordination files |

**Total Documents:** 16 unique filenames (13 inputs, 12 outputs, 9 both)

---

## Cross-Agent Dependencies

### Documents READ from Other Agents

| Document | Source Agent | Purpose |
|----------|--------------|---------|
| {project}/coderef/workorder/{feature}/plan.json | coderef-workflow | Verify implementation plans |
| {project}/coderef/workorder/{feature}/DELIVERABLES.md | coderef-workflow | Verify completion metrics |
| {project}/coderef/workorder/{feature}/communication.json | All agents | Track agent status/progress |

### Documents WRITTEN for Other Agents

| Document | Destination Agents | Purpose |
|----------|-------------------|---------|
| {project}/coderef/workorder/{feature}/context.json | coderef-workflow | Delegate workorder context |
| {project}/coderef/workorder/{feature}/communication.json | All agents | Coordinate multi-agent tasks |
| coderef/working/{feature}/stub.json | coderef-workflow | Promote stubs to workorders |
| coderef/sessions/inventory-docs/*.json | All agents | Coordinate inventory sessions |

---

## External Sources

### Read From External Systems
- **Windows Terminal**: terminal-profiles.md (configuration reference)
- **Stub System**: stub-schema.json (validation rules)

### Write To External Systems
- **Dashboard UI**: index.html (workorder visualization)
- **Session Coordination**: .mcp/coderef/sessions/* (multi-agent sessions)

---

## Document Flow Patterns

**Primary Role:** Orchestrator & Workorder Manager

**Input Flow:**
```
[MCP Servers] → plan.json, DELIVERABLES.md → [assistant] (verification)
[Self] → CLAUDE.md, projects.md, workorders.json → [assistant] (context)
```

**Output Flow:**
```
[assistant] → context.json, communication.json → [MCP Servers] (delegation)
[assistant] → workorders.json, projects.md → [Self] (tracking)
[assistant] → index.html → [Dashboard UI] (visualization)
```

**Coordination Pattern:**
- Reads: Workorder results from MCP servers
- Writes: Workorder coordination to MCP servers
- Maintains: Central tracking in projects.md & workorders.json

---

## Notes

- **Bidirectional Communication:** communication.json is both read and written for multi-agent coordination
- **Stub Promotion:** Reads stub.json from coderef/working, promotes to workorders via coderef-workflow
- **Central Hub:** Acts as orchestrator - reads results, writes tasks, tracks status
- **Session Coordination:** Creates inventory coordination files for multi-agent sessions

---

**Report Generated:** 2026-01-02
**Source Data:** C:\Users\willh\.mcp-servers\coderef\sessions\coderef-io-inventory\io-reports\assistant-io.json
