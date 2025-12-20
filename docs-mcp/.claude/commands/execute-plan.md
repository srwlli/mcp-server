Execute implementation plan and generate TodoWrite task list with TASK-ID first format.

## Workflow

### Step 1: Generate Task List

Call the `mcp__docs-mcp__execute_plan` tool with the current working directory as project_path and the feature name.

This generates a TodoWrite-formatted task list from plan.json with:
- Workorder name displayed at top of checklist
- Task ID first (SETUP-001, PARSER-001, etc.)
- Active form for in-progress display
- Status based on task checkboxes (☐/☑/⏳/🚫)

Example output format:
```
Workorder: WO-AUTH-001 - Authentication System

☐ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
☐ SETUP-002: Create auth/ directory structure
```

### Step 3: Execute Tasks

For each task:
1. Mark as `in_progress` in TodoWrite
2. **Update task status in plan.json**:
   ```python
   mcp__docs_mcp__update_task_status(
       project_path=<current_directory>,
       feature_name=<feature_name>,
       task_id="SETUP-001",
       status="in_progress"
   )
   ```
3. Implement the task following plan guidance
4. Mark as `completed` in TodoWrite
5. **Update task status to completed**:
   ```python
   mcp__docs_mcp__update_task_status(
       project_path=<current_directory>,
       feature_name=<feature_name>,
       task_id="SETUP-001",
       status="completed"
   )
   ```

**plan.json is the source of truth for task tracking.** The update_task_status tool automatically:
- Updates task status in section 5 (tasks array)
- Updates task checkboxes in section 9 (implementation checklist)
- Recalculates progress summary (total, completed, in_progress, blocked, percent)
- Adds timestamps to track when tasks were updated
- Validates status values and prevents corruption

**Multi-agent mode:** Each agent updates their assigned tasks using the tool. Progress is tracked in plan.json.

---

If feature_name not provided, ask user which feature to execute.
