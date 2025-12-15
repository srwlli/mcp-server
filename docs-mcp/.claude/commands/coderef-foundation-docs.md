Generate comprehensive foundation documentation powered by coderef analysis.

Call the `mcp__docs-mcp__coderef_foundation_docs` tool with the current working directory as the project_path.

This unified command generates:
- **ARCHITECTURE.md** - Patterns, decisions, constraints (deep extraction)
- **SCHEMA.md** - Entities, relationships (deep extraction)
- **COMPONENTS.md** - Component hierarchy, props (for UI projects only)
- **project-context.json** - Structured context for planning

The tool performs:
1. Deep extraction from existing foundation docs (not shallow 500-char previews)
2. Auto-detection of API endpoints, database schemas, dependencies
3. Git activity analysis (recent commits, active files, contributors)
4. Code pattern detection via coderef-mcp integration
5. Similar feature discovery from coderef/archived/

This command replaces the following inventory commands:
- /api-inventory
- /database-inventory
- /dependency-inventory
- /config-inventory
- /test-inventory
- /inventory-manifest
- /documentation-inventory

Output files are saved to:
- Foundation docs → coderef/foundation-docs/
- Context JSON → coderef/working/{feature}/project-context.json (if feature specified)

Use this command at the start of the /start-feature workflow to gather comprehensive project context for planning.
