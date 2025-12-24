Update task status in plan.json during feature implementation.

This command allows you to track progress as you complete individual tasks from your implementation plan.

## Workflow

### Step 1: Ask for Task Details

Use AskUserQuestion to gather task information:

```
Question: "Which task are you updating?"
Header: "Task ID"
Options: [
  {"label": "Let me type it", "description": "I'll provide the task ID (e.g., SETUP-001)"}
]
```

Also ask:

```
Question: "What's the new status?"
Header: "Status"
Options: [
  {"label": "in_progress", "description": "Task is being worked on"},
  {"label": "completed", "description": "Task is finished"},
  {"label": "blocked", "description": "Task is blocked on dependencies"}
]
```

And optionally:

```
Question: "Any notes about this status change?"
Header: "Notes (Optional)"
multiSelect: false
Options: [
  {"label": "Let me add notes", "description": "I'll provide context about the status change"}
]
```

### Step 2: Update Task Status

Call the `mcp__coderef_workflow__update_task_status` tool:

```python
mcp__coderef_workflow__update_task_status(
    project_path=<current_working_directory>,
    feature_name=<feature_name>,
    task_id=<task_id>,
    status=<status>,
    notes=<optional_notes>
)
```

This automatically:
- Updates task status in section 5 (tasks array)
- Updates task checkboxes in section 9 (implementation checklist)
- Recalculates progress summary (total, completed, in_progress, blocked, percent)
- Adds timestamps to track when tasks were updated
- Validates status values and prevents corruption

### Step 3: Confirm Update

Display confirmation:

```
✅ Task Status Updated

Task: SETUP-001
Status: in_progress
Progress: 2/27 tasks complete (7%)

Updated at: 2025-12-23T20:15:30Z
```

## Status Values

- `pending` - Task not yet started
- `in_progress` - Currently working on task
- `completed` - Task finished and working
- `blocked` - Task blocked on dependencies or external factors

## When to Use

Use this command:
- As you work through implementation tasks
- To track progress during feature development
- To mark tasks as blocking progress
- To provide context notes about task status

Related to:
- `/execute-plan` - Generate task list from plan
- `/update-deliverables` - Capture final metrics after implementation

## Notes

**plan.json is the source of truth** for task tracking during implementation.

This command updates both:
1. **Section 5 (tasks array)** - Machine-readable task status with timestamps
2. **Section 9 (implementation checklist)** - Human-readable checkbox format

Both are synchronized automatically.

For features with multiple agents, each agent updates their assigned tasks independently using this command.
