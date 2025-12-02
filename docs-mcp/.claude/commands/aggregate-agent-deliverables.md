Aggregate metrics from multiple agent DELIVERABLES.md files

Call the `mcp__docs-mcp__aggregate_agent_deliverables` tool with the current working directory as the project_path.

Ask the user for the feature name.

This tool:
- Finds all DELIVERABLES.md files in feature directory
- Aggregates LOC (lines added, deleted, net)
- Sums total commits across all agents
- Merges unique contributors
- Calculates total time elapsed from first to last commit
- Generates DELIVERABLES-COMBINED.md report with aggregated metrics
