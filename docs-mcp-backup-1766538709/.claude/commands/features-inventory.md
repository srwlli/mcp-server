Generate features inventory for the current project.

This command scans coderef/working/ and coderef/archived/ to create a comprehensive inventory of all features with their status, progress, and workorder tracking.

## Workflow

1. Call `mcp__docs-mcp__generate_features_inventory` with:
   - `project_path`: Current working directory
   - `format`: "json" (default) or "markdown" based on user preference
   - `include_archived`: true (default)
   - `save_to_file`: false (default) - set to true to save output

2. Display the inventory summary:
   - Active feature count
   - Archived feature count
   - Features with workorders
   - Features with plans

3. Optionally provide detailed breakdowns:
   - Active features with progress percentages
   - Archived features with archive dates
   - Workflow coverage statistics

## Example Usage

```bash
# Basic inventory (JSON)
/features-inventory

# Markdown format
/features-inventory
# format: markdown

# Save to file
/features-inventory
# save_to_file: true
```

## Output Example

```json
{
  "summary": {
    "active_count": 7,
    "archived_count": 44,
    "total_count": 51
  },
  "statistics": {
    "features_with_workorder": 35,
    "features_with_plan": 42,
    "features_with_context": 30,
    "features_with_deliverables": 25
  },
  "active_features": [...],
  "archived_features": [...]
}
```

## When to Use

- Get project status overview
- Before starting new work
- During sprint planning
- Onboarding new team members
- Audit and compliance documentation
