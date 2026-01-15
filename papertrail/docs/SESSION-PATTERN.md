# Hierarchical Agent-Subdirectory Session Pattern

**Version:** 1.0.0
**Status:** ✅ Production Standard
**Created:** 2026-01-15
**Workorder:** WO-SESSION-STRUCTURE-001

---

## Overview

The **Hierarchical Agent-Subdirectory Pattern** is the official standard for multi-agent sessions in the CodeRef ecosystem. It provides isolation, clear ownership, and structured coordination across 1-20 autonomous agents working on complex, multi-phase initiatives.

### Key Innovation

**Two-Tier Communication Tracking:**
- **Session-level** `communication.json` = Master roster (orchestrator owns)
- **Agent-level** `communication.json` = Task tracking (each agent owns their own)

This separation prevents file locking conflicts and enables true parallel execution.

---

## Core Principles

### 1. Hierarchical Isolation
Each agent has their own isolated subdirectory with complete autonomy:
```
sessions/{session-name}/
├── communication.json          # Session-level coordination
├── instructions.json           # Orchestrator master plan
├── {agent-1}/
│   ├── communication.json      # Agent 1's tasks
│   ├── instructions.json       # Agent 1's execution steps
│   ├── resources/index.md      # Agent 1's resource links
│   └── outputs/                # Agent 1's work products
└── {agent-2}/
    ├── communication.json      # Agent 2's tasks
    ├── instructions.json       # Agent 2's execution steps
    ├── resources/index.md      # Agent 2's resource links
    └── outputs/                # Agent 2's work products
```

### 2. Resources as Indexes (Not Copies)
**Problem:** Copying documents into agent directories creates drift and bloat.

**Solution:** `resources/index.md` contains **links only**, pointing to source documents:
```markdown
# Resources Index

## Primary Specifications
- [CONTEXT-LEVERAGE-ANALYSIS.md](../../docs/CONTEXT-LEVERAGE-ANALYSIS.md)
- [Scanner Effectiveness Improvements](../../resources/Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md)

## Session Documents
- [Master Plan](../scanner-complete-context.md)
- [Phase 1 Progress](../phase1-progress.md)
```

### 3. Phase-Based Gates
Multi-phase sessions use gates to control progression:
- **Phase 1** agents complete → **Gate validation** → **Phase 2** unlocked
- Prevents downstream work starting before dependencies ready
- Tracked in session-level `communication.json` with `phases` field

### 4. Workorder ID Hierarchy
- **Session-level:** `WO-SCANNER-CONTEXT-ENHANCEMENT-001`
- **Agent-level:** `WO-SCANNER-CONTEXT-ENHANCEMENT-001-CODEREF-CONTEXT`

Agent workorder IDs append agent suffix for traceability.

---

## File Structure Reference

### Session-Level Files

**communication.json** (Session Coordination)
- **Schema:** `communication-schema.json`
- **Owner:** Orchestrator (coderef agent)
- **Purpose:** Master roster, agent status tracking, phase progress
- **Key Fields:**
  - `workorder_id` - Session identifier (e.g., `WO-AUTH-SYSTEM-001`)
  - `agents[]` - Array of participating agents with status
  - `phases` - Optional phase tracking with gate criteria
  - `orchestrator` - Orchestrator's role and output file
  - `aggregation` - Computed agent counts (orchestrator updates)

**instructions.json** (Orchestrator Guidance)
- **Schema:** Custom (orchestrator-specific)
- **Purpose:** High-level session context, orchestrator coordination steps
- **Contains:** Session goals, phase breakdown, orchestrator synthesis steps

### Agent-Level Files (Per Subdirectory)

**communication.json** (Agent Task Tracking)
- **Schema:** `agent-communication-schema.json`
- **Owner:** Individual agent (agent updates their own)
- **Purpose:** Task status, success metrics, phase gate checklist
- **Key Fields:**
  - `workorder_id` - Agent-specific (e.g., `WO-AUTH-001-CODEREF-WORKFLOW`)
  - `parent_session` - Parent session workorder ID
  - `tasks[]` - Array of tasks with status, commits, proof
  - `success_metrics` - Baseline → Target tracking
  - `resources.index` - Must be `"resources/index.md"`
  - `outputs.primary_output` - Must start with `"outputs/"`
  - `phase_gate` - Required criteria for phase advancement

**instructions.json** (Agent Execution Steps)
- **Schema:** `agent-instructions-schema.json`
- **Owner:** Orchestrator creates, agent reads
- **Purpose:** Step-by-step execution guidance with code examples
- **Key Fields:**
  - `context` - Problem/solution/impact summary
  - `execution_steps` - Sequential steps (step_1, step_2, etc.)
  - `tasks` - Detailed task specs with implementation details
  - `context_json_template` - Template for agent to create their own workorder
  - `success_criteria` - How to know tasks are complete
  - `phase_gate_checklist` - Items to check before advancing

**resources/index.md** (Resource Links)
- **Format:** Markdown with relative links
- **Rule:** Links only, NO copied content
- **Validation:** File size < 5KB, no code blocks

**outputs/** (Agent Work Products)
- **Purpose:** Agent creates all outputs here
- **Examples:** `coderef-context-phase1-output.json`, `test-results.md`
- **Access:** Orchestrator reads from here for synthesis

---

## Workflow Pattern

### Phase 1: Session Setup (Orchestrator)

1. **Create session directory:**
   ```
   C:\Users\willh\.mcp-servers\coderef\sessions\{session-name}\
   ```

2. **Create session-level files:**
   - `communication.json` - Master roster with all agents
   - `instructions.json` - Orchestrator coordination plan
   - `README.md` - Session overview
   - Planning documents (phase1-progress.md, etc.)

3. **For each agent, create subdirectory:**
   ```
   {session-name}/{agent-id}/
   ├── communication.json
   ├── instructions.json
   ├── resources/
   │   └── index.md
   └── outputs/
   ```

4. **Populate agent files:**
   - `communication.json` - Agent tasks, metrics, phase gate
   - `instructions.json` - Execution steps, code examples, context.json template
   - `resources/index.md` - Links to source documents

### Phase 2: Agent Execution

**Agent receives handoff:**
```
NEW SESSION: WO-SCANNER-CONTEXT-ENHANCEMENT-001
Agent: coderef-context
Location: C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\coderef-context\

Your Tasks:
1. READ resources/index.md - understand all resources
2. READ instructions.json - detailed execution steps
3. Use context_json_template from instructions.json
4. RUN /create-workorder in your home project (C:\Users\willh\.mcp-servers\coderef-context)
5. Execute tasks 1-7 as specified
6. CREATE outputs in outputs/ directory
7. UPDATE communication.json after each task completion

IMPORTANT: Update communication.json status after EVERY task.
```

**Agent workflow:**
1. Navigate to agent subdirectory
2. Read `resources/index.md` → Access source documents
3. Read `instructions.json` → Understand task details
4. Use `context_json_template` → Create workorder in home project
5. Execute tasks → Create outputs in `outputs/`
6. Update `communication.json` → Mark tasks complete, add proof

### Phase 3: Orchestrator Synthesis

1. **Read agent outputs:**
   - Check each `{agent-id}/outputs/` directory
   - Read agent `communication.json` for status/proof

2. **Validate phase gates:**
   - Verify all `phase_gate.criteria` met
   - Check `success_metrics` reached targets

3. **Update session communication.json:**
   - Update `phases.phase_1.status` → `"complete"`
   - Update `aggregation` counts
   - Add orchestrator notes

4. **Synthesize results:**
   - Create orchestrator output (e.g., `orchestrator-phase1-report.md`)
   - Document cross-agent insights
   - Prepare for Phase 2 (if applicable)

---

## Example: 2-Agent Session

### Session Structure
```
scanner-context-enhancement/
│
├── Session-level (Orchestrator)
│   ├── communication.json         # Master roster (11 agents listed)
│   ├── instructions.json          # Orchestrator coordination
│   ├── README.md
│   ├── scanner-complete-context.md
│   ├── phase1-progress.md
│   └── INTEGRATION-SUMMARY.md
│
├── coderef-context/               # Agent 1
│   ├── communication.json         # 7 tasks, success metrics
│   ├── instructions.json          # Step-by-step execution
│   ├── resources/
│   │   └── index.md              # Links to CONTEXT-LEVERAGE-ANALYSIS.md, etc.
│   └── outputs/
│       └── coderef-context-phase1-output.json
│
└── coderef-core/                  # Agent 2
    ├── communication.json         # 4 tasks, success metrics
    ├── instructions.json          # Step-by-step execution
    ├── resources/
    │   └── index.md              # Links to Scanner-Effectiveness-Improvements.md
    └── outputs/
        └── coderef-core-quickwins-report.md
```

### Session communication.json
```json
{
  "workorder_id": "WO-SCANNER-CONTEXT-ENHANCEMENT-001",
  "feature_name": "scanner-context-enhancement",
  "status": "in_progress",
  "phases": {
    "phase_1": {
      "name": "Core Enhancements",
      "status": "in_progress",
      "progress": "1/11 tasks complete (9%)",
      "lead_agents": ["coderef-context", "coderef-dashboard"]
    }
  },
  "agents": [
    {
      "agent_id": "coderef-context",
      "agent_path": "C:\\Users\\willh\\.mcp-servers\\coderef-context",
      "output_file": "..\\coderef-context\\outputs\\coderef-context-phase1-output.json",
      "status": "in_progress",
      "notes": "1/7 tasks complete"
    }
  ]
}
```

### Agent communication.json
```json
{
  "workorder_id": "WO-SCANNER-CONTEXT-ENHANCEMENT-001-CODEREF-CONTEXT",
  "parent_session": "WO-SCANNER-CONTEXT-ENHANCEMENT-001",
  "agent_id": "coderef-context",
  "phase": "phase_1",
  "tasks": [
    {
      "task_id": "task_1",
      "description": "Auto-include visual_architecture field in coderef_context responses",
      "status": "complete",
      "completed": "2026-01-14",
      "commit": "69aafd0",
      "proof": "C:\\Users\\willh\\.mcp-servers\\coderef-context\\PROOF-OF-ENHANCEMENT.md"
    }
  ],
  "resources": {
    "index": "resources/index.md"
  },
  "outputs": {
    "primary_output": "outputs/coderef-context-phase1-output.json",
    "format": "json"
  }
}
```

---

## Validation

### Schema Validation
```powershell
# Validate session-level communication.json
ajv validate -s C:\Users\willh\.mcp-servers\papertrail\schemas\sessions\communication-schema.json `
  -d communication.json --strict=false

# Validate agent-level communication.json
ajv validate -s C:\Users\willh\.mcp-servers\papertrail\schemas\sessions\agent-communication-schema.json `
  -d coderef-context\communication.json --strict=false

# Validate agent instructions.json
ajv validate -s C:\Users\willh\.mcp-servers\papertrail\schemas\sessions\agent-instructions-schema.json `
  -d coderef-context\instructions.json --strict=false
```

### Automated Validation
```powershell
# Run dual-path validator (auto-detects session vs agent level)
C:\Users\willh\.mcp-servers\papertrail\validators\sessions\validate.ps1 -Verbose

# Validate agent subdirectory structure
C:\Users\willh\.mcp-servers\papertrail\validators\sessions\validate-agent-resources.ps1 `
  -SessionPath "C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement" -Verbose
```

---

## Integration with /create-session

The `/create-session` command has been updated to support this pattern:

**Step 5: Create Agent Subdirectories** (NEW)
- For each agent, create: `{agent-id}/` subdirectory
- Populate: `communication.json`, `instructions.json`, `resources/index.md`, `outputs/`
- Use templates from this document

**Step 6: Validation** (UPDATED)
- Run `validate.ps1` to check all communication.json files
- Run `validate-agent-resources.ps1` to check agent subdirectory structure
- Ensure all schemas pass before proceeding

See updated `/create-session` command for full workflow.

---

## Best Practices

### 1. Agent Isolation
✅ **DO:**
- Give each agent their own subdirectory
- Let agents update only their own `communication.json`
- Use `resources/index.md` with links (not copies)

❌ **DON'T:**
- Have multiple agents share a subdirectory
- Let agents modify session-level `communication.json`
- Copy documents into agent directories

### 2. Phase Gates
✅ **DO:**
- Define clear `phase_gate.criteria` in agent communication.json
- Validate all criteria before advancing to next phase
- Use `success_metrics` with baseline/target/current values

❌ **DON'T:**
- Skip phase validation
- Advance phases with incomplete tasks
- Ignore phase dependencies

### 3. Resource Management
✅ **DO:**
- Keep `resources/index.md` under 5KB
- Use relative links to source documents
- Validate resources exist before starting

❌ **DON'T:**
- Copy entire documents into `resources/`
- Use absolute paths in `index.md`
- Leave broken links

### 4. Output Organization
✅ **DO:**
- Create all agent outputs in `outputs/` directory
- Use descriptive filenames (e.g., `coderef-context-phase1-output.json`)
- Include proof documents referenced in `communication.json`

❌ **DON'T:**
- Create outputs outside `outputs/` directory
- Overwrite orchestrator's session-level files
- Forget to update `communication.json` with output paths

---

## Migration from Flat Sessions

**Flat Session (Old Pattern):**
```
sessions/{session-name}/
├── communication.json
├── instructions.json
└── outputs/
```

**Hierarchical Session (New Pattern):**
```
sessions/{session-name}/
├── communication.json          # Session-level
├── instructions.json           # Session-level
├── {agent-1}/
│   ├── communication.json      # Agent-level
│   ├── instructions.json       # Agent-level
│   ├── resources/index.md
│   └── outputs/
└── {agent-2}/
    ├── communication.json
    ├── instructions.json
    ├── resources/index.md
    └── outputs/
```

**Backward Compatibility:**
- `validate.ps1` detects file depth and selects appropriate schema
- Flat sessions continue to work (depth 1 = session-level schema)
- Hierarchical sessions validated with agent-level schema (depth 2+)

---

## Troubleshooting

### Validation Fails: "must NOT have additional properties"
**Cause:** Schema is too restrictive for real-world usage

**Fix:** Schemas updated to allow `additionalProperties: true` for:
- `orchestrator` (for `phase_outputs`, etc.)
- `agents[]` (for `role`, `phases`, `progress`, etc.)
- `aggregation` (for phase-specific counts like `phase_1_agents`)

### Agent Can't Find Resources
**Cause:** Broken links in `resources/index.md`

**Fix:**
1. Validate all links exist: `Test-Path` each link target
2. Use relative paths: `../../docs/file.md` not absolute
3. Check for typos in filenames

### Phase Gate Won't Advance
**Cause:** Not all criteria met

**Fix:**
1. Check `phase_gate.criteria` in agent `communication.json`
2. Verify all tasks `status: "complete"`
3. Ensure `success_metrics.current` >= `success_metrics.target`
4. Validate proof documents exist

### File Locking Conflicts
**Cause:** Multiple agents updating same file

**Fix:**
- **Orchestrator** updates: session-level `communication.json`, `aggregation`
- **Agents** update: only their own agent-level `communication.json`
- Never have agents modify session-level files

---

## Related Documentation

- **Schemas:** `C:\Users\willh\.mcp-servers\papertrail\schemas\sessions\`
  - `communication-schema.json` (session-level)
  - `agent-communication-schema.json` (agent-level)
  - `agent-instructions-schema.json` (agent execution)

- **Validators:** `C:\Users\willh\.mcp-servers\papertrail\validators\sessions\`
  - `validate.ps1` (dual-path communication.json validation)
  - `validate-agent-resources.ps1` (subdirectory structure validation)

- **Commands:** `C:\Users\willh\.claude\commands\create-session.md`

- **Reference Implementation:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement\`

---

**Last Updated:** 2026-01-15
**Maintainer:** CodeRef Orchestrator
**Status:** ✅ Production Standard
