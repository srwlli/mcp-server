Add a new entry to the project changelog.

Prompt the user for the following required information:
- version: Version number (format: X.Y.Z, e.g., "1.0.3")
- change_type: bugfix | enhancement | feature | breaking_change | deprecation | security
- severity: critical | major | minor | patch
- title: Short title of the change
- description: Detailed description of what changed
- files: List of files affected (comma-separated or array)
- reason: Why this change was made
- impact: Impact on users/system

Optional information:
- breaking: Whether this is a breaking change (true/false)
- migration: Migration guide if breaking change
- summary: Version summary for new versions
- contributors: List of contributors

Then call the `mcp__docs-mcp__add_changelog_entry` tool with:
- project_path: Current working directory
- All the information collected above

This is useful for:
- Documenting changes immediately after implementation
- Maintaining structured project history
- Generating release notes
- Tracking breaking changes and migrations

Example workflow:
1. User makes code changes
2. User runs /add-changelog
3. AI prompts for change details
4. AI adds entry to CHANGELOG.json
5. Entry is validated against JSON schema
