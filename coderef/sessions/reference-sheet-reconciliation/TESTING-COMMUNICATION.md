# TESTING COMMUNICATION - Reference Sheet Reconciliation Session

**Session:** WO-REFERENCE-SHEET-RECONCILIATION-001
**Status:** Ready for Testing
**Created:** 2026-01-02

---

## Session Overview

**Goal:** Consolidate two separate resource sheet systems into ONE unified system.

**Agents:** 3 (coderef, coderef-docs, papertrail)
**Orchestrator:** coderef-assistant

---

## Files Structure

```
C:\Users\willh\.mcp-servers\coderef\sessions\reference-sheet-reconciliation\
├── instructions.json - Master session file with all agent assignments
├── WILL-READ-THIS-YOU-IDIOT.md - Session guide explaining the goal
├── TESTING-COMMUNICATION.md - This file (testing protocol)
```

---

## Testing Protocol

### Step 1: Agent Reads Instructions
Each agent should:
1. Read `instructions.json`
2. Find their entry in `communication.agents[]`
3. Note their assigned task
4. Note their output file paths

### Step 2: Agent Confirms Understanding
Agent posts to this file:
- Agent ID
- Understood task
- Plans to review
- Output files to create

### Step 3: Agent Executes Task
Agent follows `agent_instructions` section matching their ID in instructions.json

### Step 4: Agent Reports Completion
Agent updates:
- Status in instructions.json → "complete"
- Posts summary here

---

## Agent Check-In Area

### Agent: coderef (Main MCP)
**Status:** Not started
**Task:** Review all 3 plans, synthesize best consolidation approach
**Plans to Review:**
- Plan 1: `C:\Users\willh\Desktop\assistant\coderef\workorder\resource-sheet-system\plan.json`
- Plan 2: `C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\resource-sheet-reconciliation\plan.json`
- Plan 3: `C:\Users\willh\Desktop\projects\coderef-system\coderef\workorder\resource-sheet-graph-integration\plan.json`

**Will Create:**
- `coderef-output.json`
- `coderef-output.md`

**Notes:**

---

### Agent: coderef-docs
**Status:** Not started
**Task:** Generate documentation workflow templates and standards
**Reference Plan:**
- `C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\resource-sheet-reconciliation\plan.json`

**Will Create:**
- `coderef-docs-output.json`
- `coderef-docs-output.md`

**Notes:**

---

### Agent: papertrail
**Status:** Not started
**Task:** Create generated template system for resource sheets
**Reference Plans:**
- All 3 plans (for understanding template requirements)

**Will Create:**
- `papertrail-output.json`
- `papertrail-output.md`

**Notes:**

---

## Orchestrator Check-In

### Orchestrator: coderef-assistant
**Status:** Standby
**Task:** Coordinate agents, collect outputs, create handoff package

**Waiting for:** All 3 agents to complete

**Will Create:**
- `orchestrator-output.json`
- `orchestrator-output.md`

**Notes:**

---

## Session Completion Checklist

- [ ] Agent 1 (coderef) - Status: complete, outputs created
- [ ] Agent 2 (coderef-docs) - Status: complete, outputs created
- [ ] Agent 3 (papertrail) - Status: complete, outputs created
- [ ] Orchestrator - Collected all outputs
- [ ] Orchestrator - Verified completeness
- [ ] Orchestrator - Created handoff package
- [ ] User - Reviewed handoff package
- [ ] User - Made decision on approach
- [ ] Final workorder - Created from synthesis

---

## Communication Log

_Agents post updates here as they progress_

---

**Ready for testing. Agents may begin.**
