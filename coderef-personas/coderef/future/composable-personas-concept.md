# Composable Personas Concept

**Status:** Active Development
**Created:** 2025-10-18
**Project:** personas-mcp

## Core Idea

Create an MCP server that provides **composable expert agent personas**. Users can activate personas that influence how the AI uses tools and approaches problems.

## Key Innovation

**Personas can call other MCP tools** while applying their domain expertise.

### Example:
```
User: /use-persona mcp-expert:docs-mcp

MCP Expert (docs-mcp specialist): "I'm now your docs-mcp expert"

User: "Help me add a new planning feature"

Expert: *Uses mcp__docs-mcp__gather_context with MCP expertise*
Expert: *Uses mcp__docs-mcp__analyze_project_for_planning*
Expert: *Applies docs-mcp patterns knowledge to guide implementation*
```

## Three Persona Modes

### 1. Single Persona
```
use_persona('mcp-expert')
# AI adopts general MCP expertise
```

### 2. Hierarchical (Specialized)
```
use_persona('mcp-expert:docs-mcp')
# AI has MCP expertise + deep docs-mcp tool knowledge
```

### 3. Stacked/Composed
```
use_persona('mcp-expert')
add_persona('planning-expert')
# AI combines MCP + planning expertise
```

## Architecture

### MCP Tools Provided
- `use_persona(name)` - Activate persona(s)
- `add_persona(name)` - Stack additional persona
- `clear_personas()` - Reset to default
- `list_personas()` - Show available personas tree
- `get_active_personas()` - Check current stack

### How It Works
1. Persona definitions stored as JSON (system prompts + metadata)
2. `use_persona` returns composed system prompt
3. AI applies persona context to all subsequent actions
4. Persona influences tool usage, problem-solving approach, communication style

### State Management
- Track active persona stack (ordered list)
- Later personas overlay on earlier ones
- Personas compose their contexts (merge system prompts)

## Planned Personas

### Base Personas (5)
1. **mcp-expert** - MCP protocol, tool design, architecture
2. **docs-specialist** - Technical writing, POWER framework
3. **planning-expert** - Feature planning, requirements, breakdown
4. **code-reviewer** - Code quality, best practices, security
5. **testing-expert** - Test strategy, coverage, QA

### Specialized Personas (4+)
1. **mcp-expert:docs-mcp** - docs-mcp tools specialist
2. **mcp-expert:planning** - Planning workflows specialist
3. **mcp-expert:inventory** - Inventory tools specialist
4. **mcp-expert:changelog** - Changelog management specialist

## Use Cases

### UC-1: MCP Feature Planning
```
use_persona('mcp-expert:planning')
# Get expert help planning new MCP feature
# Uses planning tools + MCP architecture knowledge
```

### UC-2: Documentation Writing
```
use_persona('docs-specialist')
# Get expert help writing docs
# Applies POWER framework, clarity best practices
```

### UC-3: Complex Planning
```
use_persona('mcp-expert')
add_persona('planning-expert')
# Plan MCP features with combined expertise
# Uses both MCP architecture + planning workflows
```

### UC-4: Code Review
```
use_persona('code-reviewer')
# Get expert code review
# Checks quality, security, performance, maintainability
```

## Technical Decisions

### Notation
- **Colon (`:`)** for specialization: `mcp-expert:docs-mcp`
- **Plus (`+`)** for composition: `mcp-expert+planning-expert`
- **Comma** for activation list: `use_persona('expert1,expert2')`

### Composition Strategy
- System prompt merging (concatenate contexts)
- Later personas overlay on earlier ones
- No conflicts - personas complement each other

### Storage Format
```json
{
  "name": "mcp-expert:docs-mcp",
  "parent": "mcp-expert",
  "system_prompt": "You are an MCP expert with deep knowledge of docs-mcp...",
  "expertise": ["docs-mcp tools", "POWER framework", "Planning workflows"],
  "preferred_tools": ["mcp__docs-mcp__*"],
  "use_cases": ["Planning docs-mcp features", "Debugging docs-mcp tools"]
}
```

## Benefits

1. **Reusable Expertise** - Define expert behaviors once, use everywhere
2. **Composable** - Combine multiple expertises as needed
3. **Tool-Agnostic** - Works with any MCP tools
4. **Lightweight** - Just context switching, no model changes
5. **Extensible** - Easy to add new personas
6. **Discoverable** - `list_personas` shows what's available

## Open Questions

1. **Persona Conflicts** - How to handle contradictory advice from stacked personas?
2. **Context Size** - Limit on how many personas can be stacked?
3. **Persistence** - Should persona state persist across sessions?
4. **User-Defined** - Allow users to create custom personas?
5. **Resource Usage** - Track via MCP resources or server-side state?

## Next Steps

1. ✅ Create context.json with requirements
2. ⏳ Run /analyze-for-planning on personas-mcp
3. ⏳ Run /create-plan to generate implementation plan
4. ⏳ Implement MCP server with persona tools
5. ⏳ Define initial persona set (5 base + 4 specialized)
6. ⏳ Test persona composition
7. ⏳ Document personas and usage patterns

## Related Files

- **Context:** `coderef/working/agent-persona-mcp/context.json`
- **Analysis:** `coderef/working/agent-persona-mcp/analysis.json` (pending)
- **Plan:** `coderef/working/agent-persona-mcp/plan.json` (pending)

---

**Meta:** This concept emerged from exploring how to make AI assistants more specialized and expert-like while maintaining flexibility. The composable nature allows combining expertise domains for complex tasks.
