# Use Persona Command

Activate an expert persona to gain specialized knowledge and behavior.

**Usage:** `/use-persona <persona-name>`

**Available Personas:**
- `mcp-expert` - MCP protocol and server implementation expert
- `docs-expert` - Documentation and planning expert (docs-mcp tools)
- `coderef-expert` - CodeRef-MCP server building expert

**Example:**
```
/use-persona mcp-expert
/use-persona docs-expert
/use-persona coderef-expert
```

This command activates the specified persona by calling the `use_persona` MCP tool. Once active, you will adopt the persona's expertise, communication style, and problem-solving approach.

Use the `get_active_persona` tool to check which persona is currently active, or `clear_persona` to deactivate.
