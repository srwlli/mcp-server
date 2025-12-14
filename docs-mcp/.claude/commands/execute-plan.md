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
2. **Update communication.json** (if multi-agent mode):
   - Set task status to `"in_progress"`
3. Implement the task following plan guidance
4. Mark as `completed` in TodoWrite
5. **Update communication.json** (if multi-agent mode):
   - Set task status to `"complete"`
   - Add `completed_at` timestamp (ISO 8601)

**communication.json is the source of truth for task tracking.** Lloyd and other agents can check progress at any time by reading this file.

Example task update:
```json
{
  "id": "STEP-003",
  "description": "Update pyproject.toml",
  "status": "complete",
  "completed_at": "2025-12-07T23:30:00Z",
  "notes": null
}
```

---

If feature_name not provided, ask user which feature to execute.
