Audit all implementation plans in the project's coderef/workorder/ directory.

Call the `mcp__coderef-docs__audit_plans` tool with the current working directory as the project_path.

This will:
1. Scan all features in coderef/workorder/
2. Validate plan.json format for each feature (must be valid JSON)
3. Check for stale plans (not updated in 7+ days)
4. Extract progress status from each plan
5. Identify issues (missing plans, blocked tasks, invalid formats)
6. Calculate health score (0-100)
7. Generate actionable recommendations

The audit returns:
- Total features and valid/invalid plan counts
- Progress breakdown (completed, in_progress, pending, blocked)
- Health score with issues and recommendations
- Per-feature details with workorder IDs

Use this to:
- Get overview of all active feature work
- Identify stale or abandoned plans
- Find blocked tasks needing attention
- Ensure plan format compliance (JSON only)

Options:
- Set stale_days to change staleness threshold (default: 7)
- Set include_archived=true to also audit archived plans
