Generate my-guide quick reference documentation for the current project.

Call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: "my-guide"

This creates a concise 60-80 line quick reference document with:
- MCP tools organized by category (Documentation, Changelog, Standards, Planning)
- Slash commands organized by category
- One-line descriptions per tool/command
- Bullet-list format for quick scanning

The document will be saved to the project root as my-guide.md

Use this when you need a lightweight tool reference (vs comprehensive USER-GUIDE.md).
