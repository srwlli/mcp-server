# Task Tracking Workflow for Agentic Implementation

**Status:** Explicit instructions added to planning template (v1.11.0)
**Last Updated:** 2025-10-18

---

## Overview

Agents implementing features from plan.json now have **explicit instructions** to track task completion in real-time by updating the implementation checklist (section 9) as they work.

---

## Current Implementation

### What Exists Today

✅ **Section 9 (Implementation Checklist)** in plan.json
- Contains all tasks with checkbox format
- Format: `☐ TASK-ID: Description` (unchecked)

✅ **Multi-Agent Coordination** (communication.json)
- Agent status tracking: `ASSIGNED` → `IN_PROGRESS` → `COMPLETE` → `VERIFIED`
- Tracks agent-level status for parallel workflows
- Supports 10 agents working in parallel

✅ **Explicit Tracking Instructions** (NEW - v1.11.0)
- Added `CRITICAL_AGENTIC_WORKFLOW` section to planning template
- Step-by-step instructions for updating plan.json
- Clear status values with emojis
- Workflow integration for single and multi-agent scenarios

---

## Task Status Values

| Status | Symbol | Format | When to Use |
|--------|--------|--------|-------------|
| Not Started | ☐ | `☐ TASK-ID: Description` | Task hasn't been started |
| In Progress | ⏳ | `⏳ TASK-ID: Description (IN PROGRESS)` | Currently working on task |
| Blocked | 🚫 | `🚫 TASK-ID: Description (BLOCKED: reason)` | Cannot proceed, waiting for dependency |
| Completed | ☑ | `☑ TASK-ID: Description` | Task fully implemented and tested |

---

## Workflow Integration

### Single-Agent Workflow

```
1. Review plan.json section 9 to identify next unchecked task
2. Implement the task (write code, test, verify)
3. IMMEDIATELY after completion:
   - Open plan.json
   - Find task in section 9: "☐ SETUP-001: Install dependencies..."
   - Change to: "☑ SETUP-001: Install dependencies..."
   - Save plan.json
4. Continue to next task
```

**Example:**
```json
// Before
"☐ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1 in requirements.txt"

// After completing task
"☑ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1 in requirements.txt"
```

### Multi-Agent Workflow

```
1. Agent is assigned to feature via /assign-agent-task
   - communication.json updated: agent_X_status = "ASSIGNED"

2. Agent starts work:
   - Update communication.json: agent_X_status = "IN_PROGRESS"
   - Mark first task in plan.json: ⏳ TASK-ID: Description (IN PROGRESS)

3. Agent completes each task:
   - Update plan.json: ☑ TASK-ID: Description

4. Agent finishes all assigned tasks:
   - Update communication.json: agent_X_status = "COMPLETE"
   - All tasks in plan.json marked: ☑

5. Coordinator runs /verify-agent-completion:
   - Validates forbidden files unchanged
   - Validates success criteria met
   - Updates communication.json: agent_X_status = "VERIFIED"
```

---

## Benefits

### Real-Time Visibility
- See which tasks are complete, in-progress, or blocked
- Calculate % completion at any time
- Identify bottlenecks early

### Accurate Progress Tracking
- Count completed tasks: `grep -c "☑" plan.json`
- Calculate percentage: `completed_tasks / total_tasks * 100`
- Track blockers: `grep "🚫" plan.json`

### Documentation & Handoffs
- Clear audit trail of what was completed
- Easy handoffs between agents (see what's done)
- Blocker documentation for debugging

### Integration with Deliverables
- `/update-deliverables` can parse plan.json to calculate metrics
- LOC, commits, and time already tracked via git
- Task completion % can be added to DELIVERABLES.md

---

## Example: Full Implementation Cycle

**Scenario:** Agent implements authentication feature with 12 tasks

### Initial State (plan.json section 9)
```
☐ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
☐ SETUP-002: Create auth/ directory structure
☐ DB-001: Create users table with password_hash column
☐ DB-002: Create migration for users table
☐ LOGIC-001: Implement hash_password() function
☐ LOGIC-002: Implement verify_password() function
☐ LOGIC-003: Implement generate_jwt_token() function
☐ API-001: Create POST /auth/login endpoint
☐ API-002: Create POST /auth/register endpoint
☐ TEST-001: Unit tests for password hashing
☐ TEST-002: Unit tests for JWT generation
☐ TEST-003: Integration tests for login/register endpoints
```

### After Completing SETUP Tasks
```
☑ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
☑ SETUP-002: Create auth/ directory structure
☐ DB-001: Create users table with password_hash column
...
```

### Encountered Blocker
```
☑ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
☑ SETUP-002: Create auth/ directory structure
🚫 DB-001: Create users table with password_hash column (BLOCKED: Need DB schema approval from team)
⏳ LOGIC-001: Implement hash_password() function (IN PROGRESS - working on this while blocked on DB)
...
```

### Final State (All Complete)
```
☑ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
☑ SETUP-002: Create auth/ directory structure
☑ DB-001: Create users table with password_hash column
☑ DB-002: Create migration for users table
☑ LOGIC-001: Implement hash_password() function
☑ LOGIC-002: Implement verify_password() function
☑ LOGIC-003: Implement generate_jwt_token() function
☑ API-001: Create POST /auth/login endpoint
☑ API-002: Create POST /auth/register endpoint
☑ TEST-001: Unit tests for password hashing
☑ TEST-002: Unit tests for JWT generation
☑ TEST-003: Integration tests for login/register endpoints
```

**Completion: 12/12 tasks (100%)**

---

## Future Enhancement: track_implementation_progress Tool

**Priority:** #1 in 20-tool roadmap
**Status:** Not yet implemented

**Proposed Functionality:**
```python
track_implementation_progress(
    project_path="C:/path/to/project",
    feature_name="auth-system",
    task_id="SETUP-001",
    status="complete",  # not_started, in_progress, blocked, complete
    notes="Installed pyjwt 2.8.0 and bcrypt 4.0.1 successfully"
)
```

**Benefits over manual updates:**
- Automatic status updates in plan.json
- Calculate % completion automatically
- Log blocker notes with timestamps
- Generate progress reports
- Track time spent per task
- Integration with /update-deliverables

**Why not implemented yet:**
Manual updates work well for now, and explicit instructions ensure agents track progress. The tool would automate what agents can already do manually via editing plan.json.

---

## Integration with Existing Tools

### /create-plan
- Generates section 9 with all tasks unchecked (☐)
- Includes CRITICAL_AGENTIC_WORKFLOW instructions
- Agent sees tracking workflow when reading plan

### /validate-plan
- Could validate that checklist is properly structured
- Could check for duplicate task IDs
- Could warn if tasks missing from checklist

### /update-deliverables
- Already parses git metrics (LOC, commits, time)
- Could parse plan.json to extract task completion %
- Could add "Tasks Completed: 12/12 (100%)" to DELIVERABLES.md

### /verify-agent-completion (Multi-Agent)
- Checks communication.json for agent_X_status = "COMPLETE"
- Could also verify plan.json shows all assigned tasks as ☑
- Ensures both files are in sync

### /archive-feature
- Archives entire feature folder including plan.json with task status
- Preserves implementation history
- Useful for retrospectives and estimation analysis

---

## Recommendations for Agents

### Best Practices

1. **Update Immediately**
   - Don't batch updates - update after each task completion
   - Keeps plan.json in sync with actual progress
   - Reduces risk of forgetting what was done

2. **Be Specific with Blockers**
   - Document exact blocker reason
   - Include what's needed to unblock
   - Example: `🚫 DB-001: ... (BLOCKED: Waiting for schema approval from @user)`

3. **Use In-Progress Status**
   - Mark current task as ⏳ when starting work
   - Helps identify where you left off if interrupted
   - Clear signal to other agents what's being worked on

4. **Verify Before Marking Complete**
   - Only mark ☑ when task is fully implemented AND tested
   - Don't mark complete if known issues exist
   - Quality over speed

5. **Multi-Agent Coordination**
   - Always update both plan.json AND communication.json
   - Keep statuses in sync
   - Communicate blockers to coordinator

---

## Metrics & Analytics

### Calculate Completion Percentage

```bash
# Count completed tasks
completed=$(grep -c "☑" plan.json)

# Count total tasks (all checkbox lines)
total=$(grep -c "☐\|☑\|⏳\|🚫" plan.json)

# Calculate percentage
echo "scale=2; $completed / $total * 100" | bc
# Output: 75.00
```

### Identify Blockers

```bash
# Find all blocked tasks
grep "🚫" plan.json

# Output:
# 🚫 DB-001: Create users table (BLOCKED: Need approval)
# 🚫 API-003: Add rate limiting (BLOCKED: Waiting for library decision)
```

### Track In-Progress Work

```bash
# Find what agent is currently working on
grep "⏳" plan.json

# Output:
# ⏳ LOGIC-002: Implement verify_password() (IN PROGRESS)
```

---

## Conclusion

With the addition of **CRITICAL_AGENTIC_WORKFLOW** to the planning template, agents now have:

✅ **Explicit instructions** on when and how to update task status
✅ **Clear status values** with visual indicators (☐ ☑ ⏳ 🚫)
✅ **Workflow integration** for both single and multi-agent scenarios
✅ **Real-time progress tracking** via simple file edits
✅ **Blocker documentation** for debugging and coordination

This ensures the **agentic workflow supports live tracking** without requiring a separate tool (though `track_implementation_progress` remains high priority for automation).

---

**Next Steps:**
1. Agents read planning template with tracking instructions
2. Agents implement features and update plan.json as they work
3. Monitor effectiveness and gather feedback
4. Consider implementing `track_implementation_progress` tool if manual updates prove cumbersome
