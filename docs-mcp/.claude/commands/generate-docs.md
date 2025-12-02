Generate foundation documentation for the current project using the docs-mcp POWER framework templates.

Call the `mcp__docs-mcp__generate_foundation_docs` tool with the current working directory as the project_path.

This will return 5 foundation document templates (README, ARCHITECTURE, API, COMPONENTS, SCHEMA). Analyze the project code, fill in the templates with project-specific details, and save the documents to the appropriate locations:
- README.md → project root
- All others → coderef/foundation-docs/

Note: USER-GUIDE.md is optional and generated separately using the `generate_individual_doc` tool.

Focus on creating comprehensive, accurate documentation that reflects the actual implementation.