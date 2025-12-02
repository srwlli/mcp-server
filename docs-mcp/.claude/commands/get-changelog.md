Get changelog entries for the current project with optional filters.

Call the `mcp__docs-mcp__get_changelog` tool with the current working directory as the project_path.

Optional filters (you can prompt user for these):
- version: Get specific version (e.g., "1.0.2")
- change_type: Filter by type (bugfix, enhancement, feature, breaking_change, deprecation, security)
- breaking_only: Show only breaking changes (true/false)

Returns structured changelog data in JSON format with:
- Version summaries
- Change entries with type, severity, description
- Files affected
- Impact and reason for changes
- Contributors

This is useful for:
- Viewing project history
- Understanding what changed in a specific version
- Finding all breaking changes or security fixes
- Planning releases and documentation updates
