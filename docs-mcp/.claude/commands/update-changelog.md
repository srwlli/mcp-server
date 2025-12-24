Agentic workflow to analyze recent changes and update the changelog automatically.

Prompt the user for:
- version: Version number for this change (format: X.Y.Z, e.g., "1.0.3")

Then call the `mcp__coderef-docs__update_changelog` tool with:
- project_path: Current working directory
- version: The version number provided

This is a **meta-tool** that returns a 3-step instruction guide for the AI agent:

**STEP 1: Analyze Your Changes**
- Review conversation context and recent file modifications
- Examine what was added, modified, or removed
- Understand the scope and purpose of changes

**STEP 2: Determine Change Details**
- Classify change_type based on what was done:
  - bugfix: Fixed a bug or error
  - enhancement: Improved existing feature
  - feature: Added new functionality
  - breaking_change: Changed existing behavior (breaking)
  - deprecation: Marked something for removal
  - security: Security-related fix or improvement
- Assign severity level:
  - critical: Major issues, security fixes, breaking changes
  - major: Significant features or improvements
  - minor: Small enhancements, non-critical fixes
  - patch: Trivial changes, typos, docs

**STEP 3: Call add_changelog_entry**
- Use the analyzed information to call `mcp__coderef-docs__add_changelog_entry`
- Provide all required fields based on your analysis

This is useful for:
- Self-documenting AI agent changes
- Automatic changelog maintenance after code modifications
- Consistent change tracking across the project
- Reducing manual changelog writing effort

**Key difference from /add-changelog:**
- /add-changelog: User provides all details manually
- /update-changelog: AI analyzes context and determines details automatically
