Execute implementation plan and generate TodoWrite task list with TASK-ID first format.

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

If feature_name not provided, ask user which feature to execute.
