Generate multi-agent communication.json from plan.json

Call the `mcp__coderef-docs__generate_agent_communication` tool with the current working directory as the project_path.

Ask the user for the feature name if not already provided.

This tool generates communication.json with:
- Precise steps extracted from implementation phases
- Forbidden files and allowed files from plan
- Success criteria from phase validation
- Agent status fields initialized (agent_1_status, agent_N_status, etc.)
- Workorder ID carried over from plan.json
