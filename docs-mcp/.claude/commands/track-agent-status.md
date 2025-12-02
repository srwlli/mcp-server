Track agent status across features with real-time dashboard

Call the `mcp__docs-mcp__track_agent_status` tool with the current working directory as the project_path.

Optionally ask the user for a specific feature name. If omitted, tracks all features.

This tool provides:
- Feature-level tracking: Agent numbers, statuses, blockers
- Project-wide dashboard: Status counts (available, assigned, in_progress, complete, verified, blocked)
- Overall status: READY, IN_PROGRESS, COMPLETE, BLOCKED
- Blocker detection: Identifies failed verifications, tests, forbidden file violations

Use this for real-time coordination of multi-agent workflows.
