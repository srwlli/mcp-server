Update all project documentation after feature completion.

**AGENTIC DESIGN**: This tool is for AI agents who just completed a feature. The agent provides context directly from their work instead of parsing files.

**How it works:**
1. Agent calls `update_all_documentation` with context they already have:
   - What type of change they made (feature, bugfix, etc.)
   - Description of what changed
   - Their workorder ID
   - List of files modified
2. Tool auto-increments version using semantic versioning:
   - breaking_change → major bump (1.x.x → 2.0.0)
   - feature → minor bump (1.0.x → 1.1.0)
   - bugfix/enhancement → patch bump (1.0.0 → 1.0.1)
3. Updates README.md, CLAUDE.md, and CHANGELOG.json

**When to use:**
Run AFTER `/update-deliverables` and BEFORE `/archive-feature` in the feature completion workflow:
```
Feature Implementation → /update-deliverables → /update-docs → /archive-feature
```

**Example (Agent usage):**
```python
# After completing update_all_documentation tool implementation
await mcp__docs_mcp__update_all_documentation({
    'project_path': 'C:/Users/willh/.mcp-servers/docs-mcp',
    'change_type': 'feature',
    'feature_description': 'Added update_all_documentation tool for automated doc updates',
    'workorder_id': 'WO-UPDATE-DOCS-001',
    'files_changed': ['server.py', 'tool_handlers.py', 'handler_helpers.py'],
    'feature_name': 'update-all-documentation'
})
```

**Required inputs (agent provides from context):**
- `change_type`: What type of change (feature, bugfix, enhancement, etc.)
- `feature_description`: What was changed
- `workorder_id`: Agent's workorder ID for tracking

**What gets updated:**
- README.md: Version number, What's New section
- CLAUDE.md: Version number, version history
- CHANGELOG.json: New version entry with workorder tracking

**Manual updates needed:**
- user-guide.md: Add feature documentation manually
- my-guide.md: Add tool to tool list manually

**Workorder tracking:**
All changes are logged with the workorder ID in CHANGELOG.json for traceability.
