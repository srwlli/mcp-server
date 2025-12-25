Lightweight workflow for small changes that don't need full planning - workflow tweaks, config updates, minor features.

## When to Use

**Use `/fix` for:**
- Small workflow changes
- Config/template updates
- Adding a flag or option
- Minor feature additions
- Documentation improvements
- Bug fixes with clear scope

**Use `/create-workorder` for:**
- New features requiring design
- Multi-phase implementations
- Architectural changes
- Anything needing stakeholder review

## Workflow

### Step 1: Get Description

Use AskUserQuestion:

```
Question: "What are you fixing/changing?"
Header: "Description"
multiSelect: false
Options: [
  {"label": "I'll describe it", "description": "Type in the Other field"}
]
```

User provides brief description in "Other" field.

### Step 2: Generate Workorder ID

Generate a workorder ID for traceability:

```
WO-FIX-{TIMESTAMP}
```

Example: `WO-FIX-20251218-1430`

### Step 3: Implement

Make the changes directly. No planning artifacts needed.

### Step 4: Log Workorder

Call log_workorder to track completion:

```python
mcp__coderef-docs__log_workorder({
    "project_path": <current_working_directory>,
    "workorder_id": <generated_id>,
    "project_name": <project_name>,
    "description": <user_description>
})
```

### Step 5: Commit

```bash
git add <changed_files>
git commit -m "fix(<scope>): <brief_description>

Workorder: <workorder_id>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 6: Summary

```
✅ Fix Complete

Workorder: <workorder_id>
Description: <description>
Files Changed: <count>
Commit: <hash>

Logged to workorder-log.txt
```

## What This Skips

- ❌ No plan.json
- ❌ No DELIVERABLES.md
- ❌ No context.json
- ❌ No stub.json
- ❌ No validation loop
- ❌ No coderef/workorder/ folder

Just: describe → implement → log → commit
