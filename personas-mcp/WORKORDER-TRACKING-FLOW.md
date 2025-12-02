# Workorder Tracking Flow - personas-mcp

**Last Updated:** 2025-10-23
**Status:** ✅ Active - v1.2.0

---

## Overview

Workorders are unique identifiers that flow through the entire feature lifecycle, from initial planning through completion and archiving. They provide traceability across all feature artifacts.

## Workorder Format

```
WO-{FEATURE}-{NUMBER}
```

**Examples:**
- `WO-AGENT-SPECIALIZATION-001` - Agent specialization coordination
- `WO-AGENT-SPECIALIZATION-002` - Ava frontend specialist
- `WO-AGENT-SPECIALIZATION-LLOYD` - Lloyd coordination enhancement
- `WO-STORYBOOK-001` - Storybook setup for Ava

**Special Cases:**
- Named workorders (e.g., `WO-AGENT-SPECIALIZATION-LLOYD`) for coordinator tasks
- Phased workorders (e.g., `WO-NFL-SCRAPER-PERSONA-001-P1`) for multi-phase features

---

## Complete Tracking Flow

### 1. Feature Initialization (`context.json`)

**Location:** `coderef/working/{feature-name}/context.json`

```json
{
  "feature_name": "ava-frontend-specialist",
  "workorder_id": "WO-AGENT-SPECIALIZATION-002",
  "description": "Transform into Ava, Frontend Specialist",
  "goal": "Create specialized frontend agent",
  "requirements": [...],
  "created_at": "2025-10-23T09:00:00Z"
}
```

**Purpose:** First appearance of workorder - establishes feature identity

---

### 2. Implementation Planning (`plan.json`)

**Location:** `coderef/working/{feature-name}/plan.json`

```json
{
  "workorder_id": "WO-AGENT-SPECIALIZATION-002",
  "feature": "Ava Frontend Specialist",
  "agent": "Ava (Agent 2)",
  "tasks": [
    {
      "id": "AVA-001",
      "description": "Rename persona file",
      "workorder_id": "WO-AGENT-SPECIALIZATION-002"
    }
  ]
}
```

**Purpose:** Workorder appears in plan header and optionally in each task

---

### 3. Agent Communication (`communication-{agent}.json`)

**Location:** `coderef/working/{feature-name}/communication-{agent}.json`

```json
{
  "feature": "AVA-FRONTEND-SPECIALIST",
  "workorder_id": "WO-AGENT-SPECIALIZATION-002",
  "from": "Lloyd (Agent 1 - Coordinator)",
  "to": "Ava (Agent 2)",
  "agent_specialization": "frontend",
  "precise_steps": [...],
  "agent_2_status": "ASSIGNED",
  "agent_2_workorder": "WO-AGENT-SPECIALIZATION-002",
  "agent_2_completion": {
    "status": "COMPLETE",
    "commit_hash": "589d152",
    "commit_message": "Add Ava frontend specialist (WO-AGENT-SPECIALIZATION-002)"
  }
}
```

**Purpose:** Workorder tracks assignment, execution, and completion status

---

### 4. Implementation & Git Commits

**Git commit messages include workorder:**

```bash
git commit -m "Add Ava frontend specialist persona (WO-AGENT-SPECIALIZATION-002)

✅ Ava (Agent 2) complete
✅ System prompt: 1,600+ lines
✅ Slash command: /ava
✅ All 17 steps completed

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Purpose:** Git history is searchable by workorder for traceability

---

### 5. Deliverables Tracking (`DELIVERABLES.md`)

**Location:** `coderef/working/{feature-name}/DELIVERABLES.md`

```markdown
# Deliverables: Ava Frontend Specialist

**Workorder:** WO-AGENT-SPECIALIZATION-002
**Feature:** Ava Frontend Specialist
**Agent:** Ava (Agent 2)
**Status:** Complete

## Implementation Metrics
- **Lines of Code Added:** 1,650
- **Commits:** 3
- **Time Elapsed:** 2 hours
```

**Purpose:** Track completion metrics tied to workorder

---

### 6. Documentation Updates

**Files that reference workorders:**

1. **CLAUDE.md** - Project status and version history
```markdown
**v1.2.0 (2025-10-23) - Lloyd Coordination Enhancement:**
- ✅ Workorders: WO-AGENT-SPECIALIZATION-001 through WO-AGENT-SPECIALIZATION-005
```

2. **CHANGELOG.json** - Structured change history
```json
{
  "version": "1.2.0",
  "changes": [
    {
      "workorder_id": "WO-AGENT-SPECIALIZATION-002",
      "title": "Added Ava frontend specialist persona"
    }
  ]
}
```

3. **README.md** - Feature announcements
```markdown
## v1.2.0 - Agent Specialization
- Ava (Frontend) - WO-AGENT-SPECIALIZATION-002
```

---

### 7. Archive Process

**After completion:**

```bash
# Move to archive
mv coderef/working/ava-frontend-specialist/ coderef/archived/

# Archive index updated
coderef/archived/index.json
{
  "features": [
    {
      "feature_name": "Ava Frontend Specialist",
      "folder_name": "ava-frontend-specialist",
      "workorder_id": "WO-AGENT-SPECIALIZATION-002",
      "archived_at": "2025-10-23T14:00:00Z"
    }
  ]
}
```

**Purpose:** Preserve workorder in archive for historical reference

---

## Current Active Workorders

### Completed (Ready to Archive)
- ✅ `WO-AGENT-SPECIALIZATION-001` - Agent specialization coordination
- ✅ `WO-AGENT-SPECIALIZATION-002` - Ava frontend specialist
- ✅ `WO-AGENT-SPECIALIZATION-LLOYD` - Lloyd coordination enhancement
- ✅ `WO-AGENT-SPECIALIZATION-005` - Taylor generalist rename

### In Progress
- 🔄 `WO-AGENT-SPECIALIZATION-003` - Marcus backend specialist
- 🔄 `WO-AGENT-SPECIALIZATION-004` - Quinn testing specialist

### Planned
- ⏳ `WO-STORYBOOK-001` - Ava's Storybook setup

---

## Workorder Naming Conventions

### Pattern: `WO-{FEATURE}-{NUMBER}`

**Feature Name Guidelines:**
- Use UPPERCASE-KEBAB-CASE
- Be descriptive but concise
- Group related work under same feature prefix

**Examples:**
```
WO-AUTH-001          → First auth workorder
WO-AUTH-002          → Second auth workorder
WO-AUTH-REFACTOR-001 → Auth refactor sub-feature
```

**Special Patterns:**
```
WO-AGENT-SPECIALIZATION-LLOYD  → Named coordinator workorder
WO-NFL-SCRAPER-001-P1          → Phase 1 of multi-phase feature
```

---

## Traceability Benefits

1. **Git History Search:**
   ```bash
   git log --grep="WO-AGENT-SPECIALIZATION-002"
   ```

2. **File Search:**
   ```bash
   grep -r "WO-AGENT-SPECIALIZATION-002" coderef/
   ```

3. **Cross-Reference:**
   - Find all files touched by a workorder
   - Trace feature from planning → execution → archive
   - Identify related commits

4. **Audit Trail:**
   - Who worked on it (agent assignments)
   - When it was completed (timestamps)
   - What changed (file lists)
   - Why it was done (context.json goals)

---

## Integration with docs-mcp Tools

### Workorder-Aware Tools (docs-expert v2.0 - Planned)

```javascript
// Generate todos from plan with workorder context
generate_todo_list(plan_path, workorder_id)

// Track execution with workorder
track_plan_execution(plan_path, workorder_id, todo_status)

// Execute plan interactively
execute_plan_interactive(plan_path, workorder_id, mode)
```

**Future Enhancement:** docs-mcp will have native workorder tracking for cross-project coordination.

---

## Best Practices

### ✅ DO:
- Include workorder in ALL feature files (context, plan, communication)
- Reference workorder in ALL git commits
- Use consistent format (WO-{FEATURE}-{NUMBER})
- Update communication.json with completion status
- Archive completed workorders

### ❌ DON'T:
- Reuse workorder IDs for different features
- Skip workorder in git commits
- Use inconsistent naming (wo-feature-001 vs WO-FEATURE-001)
- Forget to update agent_completion status
- Leave orphaned workorders in working/

---

## Workorder Lifecycle States

```
1. PLANNED     → context.json created
2. ASSIGNED    → communication.json agent_status = "ASSIGNED"
3. IN_PROGRESS → agent starts execution
4. COMPLETE    → agent_completion.status = "COMPLETE"
5. VERIFIED    → agent_1_verification.status = "VERIFIED"
6. ARCHIVED    → moved to coderef/archived/
```

---

## Example: Complete Workorder Flow

**WO-AGENT-SPECIALIZATION-002 (Ava Frontend Specialist)**

```
1. Created:    context.json with workorder_id
2. Planned:    plan.json with 17 tasks
3. Assigned:   communication-ava.json (Lloyd → Ava)
4. Executed:   Ava completed all 17 steps
5. Committed:  3 git commits with WO-AGENT-SPECIALIZATION-002
6. Updated:    DELIVERABLES.md with metrics
7. Documented: CLAUDE.md, README.md, CHANGELOG.json
8. Verified:   Lloyd verification pending
9. Ready:      For archiving to coderef/archived/
```

---

## Related Documentation

- **planning-standard.json** - Implementation planning templates
- **communication.json** - Multi-agent protocol
- **DELIVERABLES.md** - Metrics and completion tracking
- **CHANGELOG.json** - Structured version history

---

**Status:** Active tracking system for all features across personas-mcp ecosystem.
