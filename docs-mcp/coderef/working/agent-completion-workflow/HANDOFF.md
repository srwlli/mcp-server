# HANDOFF: WO-AGENT-COMPLETION-WORKFLOW-001

**Feature:** agent-completion-workflow
**Target Project:** docs-mcp
**Workorder Type:** Delegated (workflow documentation)
**Priority:** High
**Status:** Pending

---

## Overview

Document and enforce the workflow where **agents complete ALL tasks** (including /update-deliverables and /archive-feature) before marking work complete, and **orchestrator ONLY verifies** and updates tracking.

**Problem:** Currently unclear who should archive features after completion. Agents complete work but leave deliverables unpopulated and features unarchived. Orchestrator steps in and does the archival (wrong role).

**Solution:** Make it explicit in documentation that agent archives, orchestrator only verifies.

---

## Your Task

**Location:** `C:\Users\willh\.mcp-servers\docs-mcp\coderef\working\agent-completion-workflow\`

### Files Available

1. **context.json** - Full requirements, problem description, correct workflow specification
2. **communication.json** - Workflow tracking with 3 tasks

---

## The Problem (Real Example)

**WO-PERSONA-MANAGEMENT-001:**

What happened:
1. ✅ Agent completed both persona tasks (remove + create)
2. ❌ Agent did NOT run /update-deliverables
3. ❌ Agent did NOT run /archive-feature
4. ❌ Agent did NOT update communication.json to 'complete'
5. ❌ Orchestrator stepped in and archived (wrong role)

Why this is bad:
- Violates orchestrator principle: "identify, delegate, collect" (not execute)
- DELIVERABLES.md left with TBD metrics
- Orchestrator touching files in target projects
- Confusion about who does what

---

## The Correct Workflow

### Agent Responsibilities (The Implementor)

**Phase 1: Implementation**
```
1. Execute approved plan tasks
2. Update plan.json task statuses as work progresses
3. Update communication.json: status → "implementing"
```

**Phase 2: Completion Tasks** ⭐ THIS IS THE KEY CHANGE
```
4. Run /update-deliverables to populate DELIVERABLES.md with git metrics
5. Run /archive-feature to move feature to coderef/archived/
6. Update communication.json:
   - status → "complete"
   - archived → true
   - Add final entry to communication_log
7. Notify orchestrator that work is complete and archived
```

### Orchestrator Responsibilities (Verification Only)

**Phase 1: Verify Completion**
```
1. Read communication.json - confirm status = 'complete' AND archived = true
2. Read DELIVERABLES.md - confirm metrics populated (NOT TBD)
3. Check coderef/archived/ - confirm feature folder moved
4. Validate deliverables match requirements
```

**Phase 2: Update Tracking**
```
5. Update workorders.json: move to completed_workorders
6. Add summary and deliverables list
7. Update last_updated timestamp
8. Done - DO NOT touch any files in target project
```

---

## Tasks (3 total)

### Task 1: Update Orchestrator CLAUDE.md

**File:** `C:\Users\willh\Desktop\assistant\CLAUDE.md`

**Section to update:** "Workorder Handoff Protocol"

**Changes needed:**

1. **Phase 3 (Implementation)** - Add agent completion tasks:
```markdown
Phase 3: Implementation (agent)
  - Agent executes approved plan
  - Agent updates DELIVERABLES.md progress
  - Agent updates communication.json: status → "implementing" → "complete"

  ⭐ BEFORE marking complete, agent MUST:
  1. Run /update-deliverables to populate metrics
  2. Run /archive-feature to move to coderef/archived/
  3. Update communication.json: status → "complete" + archived → true
```

2. **Phase 4 (Verification)** - Clarify orchestrator only verifies:
```markdown
Phase 4: Verification (orchestrator)
  - Orchestrator verifies deliverables (does NOT archive)
  - Checks communication.json: status = "complete" AND archived = true
  - Checks DELIVERABLES.md: metrics populated (NOT TBD)
  - Checks coderef/archived/: feature folder moved
  - Updates communication.json: status → "verified"
  - Closes workorder in workorders.json
```

**Update communication.json:**
```json
{
  "tasks": [
    {
      "task": 1,
      "status": "complete"
    }
  ]
}
```

---

### Task 2: Update Handoff Template

**Location:** HANDOFF.md template used in delegation prompts

**Add completion section:**

```markdown
## Completion Checklist

Before updating communication.json to "complete", you MUST:

1. **Populate Deliverables**
   ```bash
   /update-deliverables
   ```
   - Validates DELIVERABLES.md has actual metrics (not TBD)
   - Populates from git history

2. **Archive Feature**
   ```bash
   /archive-feature
   ```
   - Moves feature from coderef/working/ to coderef/archived/
   - Updates archive index

3. **Update Communication**
   ```json
   {
     "workorder": {
       "status": "complete",
       "archived": true,
       "completed": "YYYY-MM-DD"
     }
   }
   ```
   - Add final entry to communication_log with completion summary

4. **Notify Orchestrator**
   - Work is complete and archived
   - Ready for verification

## Validation

Before marking complete, verify:
- [ ] DELIVERABLES.md has actual metrics (no TBD)
- [ ] Feature moved to coderef/archived/
- [ ] communication.json updated with complete + archived
- [ ] All tasks in plan.json marked complete
```

**Update communication.json:**
```json
{
  "tasks": [
    {
      "task": 2,
      "status": "complete"
    }
  ]
}
```

---

### Task 3: Create Workflow Documentation

**Create new file:** `WORKFLOW-AGENT-ORCHESTRATOR-RESPONSIBILITIES.md`

**Content:**

```markdown
# Agent vs Orchestrator Responsibilities

## Core Principle

**Agent:** Executor - completes ALL implementation tasks
**Orchestrator:** Coordinator - tracks, verifies, aggregates (does NOT execute)

---

## Agent Responsibilities

### During Implementation
- Execute approved plan tasks
- Write code, tests, documentation
- Update plan.json task statuses
- Update communication.json: "implementing"

### ⭐ Before Marking Complete
1. Run `/update-deliverables` - populate metrics
2. Run `/archive-feature` - move to coderef/archived/
3. Update communication.json:
   - status: "complete"
   - archived: true
   - Add completion summary to communication_log

### Why Agent Archives
- Agent has full context (knows what was done)
- Agent owns closure on their work
- Orchestrator stays in verification role

---

## Orchestrator Responsibilities

### Verification Only
1. Read communication.json - confirm complete + archived
2. Read DELIVERABLES.md - confirm metrics (not TBD)
3. Check coderef/archived/ - confirm moved
4. Validate deliverables match requirements

### Update Tracking
1. Update workorders.json - move to completed
2. Add summary and deliverables
3. Update timestamp

### ❌ Orchestrator Does NOT
- Archive features
- Update DELIVERABLES.md
- Execute implementation tasks
- Touch files in target projects

---

## Workflow Diagram

```
Agent Implementation Phase:
  Execute tasks → Update plan.json → Update communication.json ("implementing")

Agent Completion Phase: ⭐
  /update-deliverables → /archive-feature → Update communication.json ("complete" + archived)

Orchestrator Verification Phase:
  Check complete + archived → Validate deliverables → Update workorders.json
```

---

## Example: Correct Flow

**Agent (personas-mcp):**
1. ✅ Complete persona tasks
2. ✅ Run /update-deliverables
3. ✅ Run /archive-feature
4. ✅ Update communication.json: complete + archived
5. ✅ Notify orchestrator

**Orchestrator:**
1. ✅ Read communication.json (complete + archived)
2. ✅ Check DELIVERABLES.md (metrics populated)
3. ✅ Check coderef/archived/ (folder exists)
4. ✅ Update workorders.json
5. ✅ Done

---

## Validation Criteria

Success indicators:
- All agents run /update-deliverables before /archive-feature
- All coderef/archived/ features have populated DELIVERABLES.md
- Orchestrator never uses archive_feature tool
- communication.json always updated by agent, not orchestrator
```

**Update communication.json:**
```json
{
  "tasks": [
    {
      "task": 3,
      "status": "complete"
    }
  ],
  "workorder": {
    "status": "complete",
    "archived": true
  }
}
```

**THEN run /archive-feature yourself** (you're the agent implementing this!)

---

## Success Criteria

### Functional
- [ ] CLAUDE.md explicitly states agent archives, orchestrator verifies
- [ ] Handoff templates include completion checklist
- [ ] Workflow documentation created and clear
- [ ] All agents know to run /update-deliverables + /archive-feature

### Quality
- [ ] Documentation is unambiguous
- [ ] Examples show correct workflow
- [ ] Validation criteria defined

---

## Key Principle

**Agent = Executor (ALL tasks including completion)**
**Orchestrator = Verifier (tracking only, NO execution)**

---

## Communication

Update communication.json after each task:
1. After Task 1: tasks[0].status = "complete"
2. After Task 2: tasks[1].status = "complete"
3. After Task 3: tasks[2].status = "complete"
4. After all tasks: workorder.status = "complete" + archived = true
5. Run /update-deliverables and /archive-feature before marking complete

---

**Ready to execute. Begin Task 1.**
