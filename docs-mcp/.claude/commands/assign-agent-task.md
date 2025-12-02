Assign specific task to agent with workorder scoping

Call the `mcp__docs-mcp__assign_agent_task` tool with the current working directory as the project_path.

Ask the user for:
1. Feature name
2. Agent number (1-10)
3. Phase ID (optional - e.g., "phase_2")

This tool:
- Generates agent-scoped workorder ID (WO-FEATURE-002, WO-FEATURE-003)
- Updates communication.json with agent assignment
- Detects conflicting assignments (warns if agent already assigned)
- Sets agent status to ASSIGNED
