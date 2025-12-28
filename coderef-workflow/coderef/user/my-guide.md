# coderef-workflow - Tool Reference

Quick reference for MCP tools and slash commands.

## MCP Tools (23 total)

### Planning & Analysis
- gather_context - Collect feature requirements and constraints
- analyze_project_for_planning - Scan codebase for architecture patterns
- get_planning_template - Get the 10-section plan template
- create_plan - Generate complete implementation plan from context
- validate_implementation_plan - Score plan quality (0-100)
- generate_plan_review_report - Create markdown review report

### Execution & Tracking
- execute_plan - Align plan with TodoWrite task list
- update_task_status - Track individual task progress
- track_agent_status - Dashboard for agent task assignments
- generate_handoff_context - Create claude.md for agent handoffs
- assign_agent_task - Assign specific task to agent (1-10)
- verify_agent_completion - Validate agent work with git diffs

### Deliverables & Documentation
- generate_deliverables_template - Create DELIVERABLES.md structure
- update_deliverables - Update metrics from git history
- update_all_documentation - Update README/CHANGELOG/CLAUDE.md
- aggregate_agent_deliverables - Combine metrics from multi-agent runs

### Risk & Integration
- assess_risk - AI-powered risk scoring (0-100)
- generate_agent_communication - Create multi-agent coordination file

### Archival & Inventory
- archive_feature - Move completed feature to archive
- generate_features_inventory - List all active & archived features
- audit_plans - Health check on all plans in coderef/workorder

### Workorder Tracking
- log_workorder - Add entry to global workorder log
- get_workorder_log - Query workorder history

## Slash Commands

### Planning Commands
- /create-workorder - Full 11-step planning workflow
- /create-plan - Create plan from existing context
- /analyze-for-planning - Analyze project structure
- /gather-context - Collect requirements only
- /validate-plan - Score existing plan quality
- /generate-plan-review - Generate markdown review
- /get-planning-template - View 10-section template

### Execution Commands
- /align-plan - Align plan with TodoWrite task list
- /update-task-status - Track task progress
- /track-agent-status - View agent dashboard
- /assign-agent-task - Assign task to agent
- /verify-agent-completion - Validate agent work
- /generate-handoff-context - Create agent handoff docs

### Documentation Commands
- /update-docs - Update README/CHANGELOG/CLAUDE.md
- /update-deliverables - Update metrics from git
- /generate-deliverables - Create DELIVERABLES.md
- /aggregate-agent-deliverables - Sum multi-agent metrics

### Feature Management
- /archive-feature - Archive completed feature
- /features-inventory - List all features
- /audit-plans - Health check all plans

### Workorder Management
- /log-workorder - Add to global log
- /get-workorder-log - Query workorder history

## Quick Workflow

```
/create-workorder → /align-plan → Implement → /update-deliverables → /archive-feature
```

## Key Concepts

- **Workorder ID:** WO-{FEATURE}-{CATEGORY}-### format
- **Plan Structure:** 10-section JSON (META, PREP, SUMMARY, RISK, etc.)
- **Task Tracking:** TodoWrite integration with CLI display
- **Multi-Agent:** Parallel execution with communication.json
