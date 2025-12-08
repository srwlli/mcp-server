Execute implementation plan and generate TodoWrite task list with TASK-ID first format.

## Workflow

### Step 1: Load Context Experts (NEW)

Before executing tasks, load relevant context experts for the files being modified:

1. **Read plan.json** to identify files in current phase
2. **Check for existing experts** for those files:

```python
mcp__docs_mcp__list_context_experts({
    "project_path": <current_working_directory>
})
```

3. **Load expert context** for files with experts:

```python
# For each file with an expert:
mcp__docs_mcp__get_context_expert({
    "project_path": <current_working_directory>,
    "expert_id": <expert_id>  # e.g., "CE-src-auth-handlers_py-001"
})
```

4. **Use expert context** during implementation:
   - Code structure (functions, classes, complexity)
   - Relationships (what depends on this file)
   - Recent git history (recent changes)
   - Usage patterns (how this file is used)

### Step 2: Generate Task List

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
3. Load expert context for files being modified (if experts exist)
4. Implement the task following plan guidance
5. Mark as `completed` in TodoWrite
6. **Update communication.json** (if multi-agent mode):
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

### Step 4: Update Experts (Optional)

After completing implementation, update any stale experts:

```python
mcp__docs_mcp__update_context_expert({
    "project_path": <current_working_directory>,
    "expert_id": <expert_id>
})
```

---

If feature_name not provided, ask user which feature to execute.
