# Workorder Workflow Breakdown Diagnosis

**Date:** 2026-01-16
**Issue:** Dashboard UI shows no progress despite agent actively working
**Root Cause:** Missing connection between agent workorder and session tracking

---

## Problem Statement

**Observed Behavior:**
1. Agent runs `/create-workorder` successfully
2. Agent creates `coderef/workorder/scanner-integration/` with context.json, analysis.json, plan.json
3. Agent runs `/align-plan` and shows TodoWrite task list
4. Agent is actively working (updating API documentation, completing tasks)
5. **Dashboard UI shows "No workorders created"**
6. **Session communication.json shows status='not_started'**

**Expected Behavior:**
1. Agent creates workorder
2. Agent updates session communication.json with workorder reference
3. Dashboard UI shows workorder progress
4. Session tracking shows agent status='in_progress'

---

## Root Cause Analysis

### The Disconnect

**Agent Created:**
```
Location: C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\coderef\workorder\scanner-integration\
Files:
- context.json
- analysis.json
- plan.json (WO-SCANNER-INTEGRATION-001)
```

**Session Expects:**
```
Location: C:\Users\willh\.mcp-servers\coderef\sessions\scanner-complete-integration\coderef-core\communication.json
Field: outputs.workorders_created = []
Status: not_started
```

**The Gap:** The workorder exists in the agent's home project, but the session communication.json hasn't been updated to reference it.

---

## Workflow Step Breakdown

### Where It's Breaking:

**Current Flow:**
```
Step 1: Agent reads session instructions ✅
Step 2: Agent reads resources/index.md ✅
Step 3: Agent runs /create-workorder ✅
  → Creates WO-SCANNER-INTEGRATION-001
  → Location: coderef-core/coderef/workorder/scanner-integration/
Step 4: Agent starts implementing tasks ✅
  → Running through TodoWrite checklist
  → Updating API documentation
Step 5: Agent should update session communication.json ❌ NOT HAPPENING
  → Should add to outputs.workorders_created[]
  → Should update status='in_progress'
```

**Missing Step:** Agent isn't updating the SESSION communication.json after creating the workorder.

---

## Schema Analysis

### Session communication.json Schema

**Expected Structure:**
```json
{
  "workorder_id": "WO-SCANNER-COMPLETE-INTEGRATION-001-CODEREF-CORE",
  "status": "in_progress",  // ❌ Currently: "not_started"

  "outputs": {
    "workorders_created": [  // ❌ Currently: Missing or empty
      {
        "workorder_id": "WO-SCANNER-INTEGRATION-001",
        "feature_name": "scanner-integration",
        "location": "C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core\\coderef\\workorder\\scanner-integration",
        "plan_path": "coderef/workorder/scanner-integration/plan.json",
        "status": "in_progress",
        "created_at": "2026-01-15T23:07:00.000Z"
      }
    ],
    "primary_output": "outputs/coderef-core-phase1-scanner-improvements.md"
  }
}
```

**What's Missing:**
1. `outputs.workorders_created` array is not being populated
2. `status` is not being updated from "not_started" to "in_progress"

---

## Agent Instructions Analysis

### What Instructions Say:

**From coderef-core/instructions.json (Step 3):**
```json
{
  "step_3": "RUN /create-workorder in coderef-core project to create WO-SCANNER-IMPROVEMENTS-PHASE2-001 workorder using context_json_template (creates coderef/workorder/scanner-improvements-phase2/ with context.json, analysis.json, plan.json)"
}
```

**What's Missing:** No explicit instruction to update session communication.json after creating workorder.

**Expected Instruction:**
```json
{
  "step_3": "RUN /create-workorder in coderef-core project to create workorder",
  "step_3b": "UPDATE session communication.json: Add workorder to outputs.workorders_created[] and set status='in_progress'"
}
```

---

## Why Dashboard Shows "No workorders created"

**Dashboard Query:**
```typescript
// Dashboard reads session communication.json
const session = readSessionCommunication(sessionId);
const agent = session.agents.find(a => a.agent_id === 'coderef-core');

// Checks outputs.workorders_created array
if (!agent.outputs?.workorders_created || agent.outputs.workorders_created.length === 0) {
  return "No workorders created";
}
```

**Result:** Since `outputs.workorders_created` is empty/missing, dashboard correctly shows "No workorders created" even though the workorder DOES exist in the agent's home project.

---

## Fix Options

### Option A: Update Agent Instructions (Explicit)

**Modify:** `coderef-core/instructions.json`

**Add explicit step:**
```json
{
  "execution_steps": {
    "step_1": "READ resources/index.md",
    "step_2": "READ instructions.json",
    "step_3": "RUN /create-workorder in agent home project",
    "step_3b": "UPDATE session communication.json with workorder details", // ⭐ NEW
    "step_4": "FOR EACH TASK: Execute → Update communication.json → Repeat"
  }
}
```

**Detailed instruction:**
```json
{
  "step_3b": {
    "action": "UPDATE session communication.json",
    "file": "C:\\Users\\willh\\.mcp-servers\\coderef\\sessions\\scanner-complete-integration\\coderef-core\\communication.json",
    "changes": [
      "Add workorder details to outputs.workorders_created[] array",
      "Update status from 'not_started' to 'in_progress'",
      "Record workorder_id, feature_name, location, plan_path"
    ],
    "example": {
      "outputs": {
        "workorders_created": [{
          "workorder_id": "WO-SCANNER-INTEGRATION-001",
          "feature_name": "scanner-integration",
          "location": "C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core\\coderef\\workorder\\scanner-integration",
          "plan_path": "coderef/workorder/scanner-integration/plan.json",
          "status": "in_progress",
          "created_at": "2026-01-15T23:07:00.000Z"
        }]
      },
      "status": "in_progress"
    }
  }
}
```

---

### Option B: Update /create-workorder Command (Automatic)

**Modify:** `/create-workorder` to automatically update session communication.json

**Add to Step 9 (Commit & Push):**
```markdown
### Step 9b: Update Session Tracking (If in Session)

If agent is part of a multi-agent session:

1. Detect session: Check for `../../../sessions/{session-name}/{agent-id}/communication.json`
2. Read session communication.json
3. Add workorder to outputs.workorders_created[]
4. Update status='in_progress'
5. Commit session communication.json

Example:
```python
if session_comm_path.exists():
    session_comm = json.loads(session_comm_path.read_text())
    session_comm['outputs']['workorders_created'].append({
        'workorder_id': workorder_id,
        'feature_name': feature_name,
        'location': workorder_path,
        'plan_path': plan_json_path,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat()
    })
    session_comm['status'] = 'in_progress'
    session_comm_path.write_text(json.dumps(session_comm, indent=2))
```
```

---

### Option C: Update /create-session Template (Prevention)

**Modify:** `/create-session.md` agent instructions template

**Change Step 3 to include update:**
```json
{
  "execution_steps": {
    "step_3": "RUN /create-workorder in agent home project to create workorder using context_json_template (creates coderef/workorder/{feature_name}/ with context.json, analysis.json, plan.json). THEN UPDATE this communication.json: add workorder to outputs.workorders_created[] and set status='in_progress'"
  }
}
```

---

## Recommended Solution

**Hybrid Approach:**

1. **Immediate Fix (Manual):** Update session communication.json for current session
2. **Short-term (Option A):** Update scanner-complete-integration agent instructions
3. **Long-term (Option C):** Update /create-session template to include explicit update step
4. **Future Enhancement (Option B):** Make /create-workorder auto-detect and update session tracking

---

## Immediate Action: Manual Fix

### Update Current Session

**File:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-complete-integration\coderef-core\communication.json`

**Add:**
```json
{
  "status": "in_progress",
  "outputs": {
    "workorders_created": [
      {
        "workorder_id": "WO-SCANNER-INTEGRATION-001",
        "feature_name": "scanner-integration",
        "location": "C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core\\coderef\\workorder\\scanner-integration",
        "plan_path": "coderef/workorder/scanner-integration/plan.json",
        "status": "in_progress",
        "created_at": "2026-01-15T23:07:00.000Z"
      }
    ],
    "primary_output": "outputs/coderef-core-phase1-scanner-improvements.md",
    "format": "markdown"
  }
}
```

**After this change, dashboard should show:**
- Agent status: in_progress
- Workorder: WO-SCANNER-INTEGRATION-001
- Feature: scanner-integration
- Location: (clickable link to plan.json)

---

## Prevention for Future Sessions

### Update /create-session Template

**File:** `C:\Users\willh\.claude\commands\create-session.md`

**Line 259 (agent execution_steps template):**

**Before:**
```json
"step_3": "RUN /create-workorder in agent home project to create workorder using context_json_template (creates coderef/workorder/{feature_name}/ with context.json, analysis.json, plan.json)"
```

**After:**
```json
"step_3": "RUN /create-workorder in agent home project to create workorder using context_json_template (creates coderef/workorder/{feature_name}/ with context.json, analysis.json, plan.json), THEN immediately UPDATE this communication.json file: (1) add workorder details to outputs.workorders_created[] array, (2) update status from 'not_started' to 'in_progress'"
```

---

## Validation Checklist

After implementing fix:

- [ ] Session communication.json has `outputs.workorders_created` array
- [ ] Array contains workorder entry with workorder_id, feature_name, location, plan_path
- [ ] Session status updated to 'in_progress'
- [ ] Dashboard UI shows workorder in "Workorders Created" section
- [ ] Dashboard UI shows agent status as "in_progress"
- [ ] Clicking workorder link navigates to plan.json
- [ ] Future sessions created with updated template include this step

---

## Summary

**The Problem:** Agent creates workorder successfully but doesn't update session tracking.

**The Cause:** Missing instruction to update session communication.json after /create-workorder.

**The Fix:**
1. Immediate: Manually update session communication.json
2. Short-term: Update current session agent instructions
3. Long-term: Update /create-session template to include explicit update step

**Result:** Dashboard will show agent progress and workorder tracking will work correctly.

---

**Diagnosed By:** Claude Code AI
**Reference:** scanner-complete-integration session (WO-SCANNER-COMPLETE-INTEGRATION-001)
