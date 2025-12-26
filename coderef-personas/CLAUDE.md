# personas-mcp - AI Context Documentation

**Project:** personas-mcp
**Version:** 1.4.0
**Status:** ✅ Implemented (5 personas: 1 expert + 1 coordinator + 3 specialists)
**Created:** 2025-10-18
**Last Updated:** 2025-12-25

---

## Quick Summary

**personas-mcp** is an MCP server that provides **independent expert agent personas**. Users can activate personas (like "mcp-expert", "lloyd", "ava", "marcus", or "quinn") that influence how the AI uses tools and approaches problems. Each persona provides comprehensive domain expertise with system prompts designed for agentic use.

**v1.4.0 Update (Lloyd Optimization):** Lloyd persona slimmed from 1,017 lines to 153 lines (85% reduction). Reference documentation extracted to `docs/MCP-ECOSYSTEM-REFERENCE.md` and `docs/LLOYD-REFERENCE.md`.

**Core Innovation:** Personas can call other MCP tools (like `mcp__docs-mcp__gather_context`) while acting with specialized knowledge and behavior patterns.

**Current Implementation:** 1 expert base persona (mcp-expert) + specialized agent personas (lloyd, ava, marcus, quinn) - no hierarchical dependencies, all standalone.

---

## Project Vision

### The Problem
AI assistants are generalists. Sometimes you need an **expert** - someone with deep knowledge in a specific domain (MCP architecture, technical writing, code review, etc.).

### The Solution
Create an MCP server that provides expert personas that can be activated:

```
# Activate MCP expert
use_persona('mcp-expert')

# Activate multi-agent coordinator
use_persona('lloyd')

# Activate frontend specialist
use_persona('ava')
```

**Note:** Original plan included hierarchical personas (mcp-expert:docs-mcp) and stacking. Final implementation uses independent personas with comprehensive standalone expertise for agentic use.

---

## 🌍 Global Deployment Rule

**NOTHING IS LOCAL. ENTIRE ECOSYSTEM IS GLOBAL.**

All tools, commands, and artifacts must use **global paths only**:
- `~/.claude/commands/` (commands)
- `coderef/workorder/` (plans)
- `coderef/foundation-docs/` (documentation)
- `coderef/archived/` (completed features)
- `coderef/standards/` (standards)
- MCP tools (global endpoints only)

❌ **FORBIDDEN:** Local copies, project-specific variations, `coderef/working/`, per-project configurations

**Rule:** No fallbacks, no exceptions, no local alternatives. Single global source of truth.

---

### How It Works
1. User activates a persona via MCP tool
2. Persona returns system prompt/context
3. AI adopts that persona's expertise and behavior
4. AI uses any available MCP tools **with that persona's knowledge applied**
5. Persona influences problem-solving approach, tool usage, communication style

---

## Current Implementation

### Core Expert Persona

**mcp-expert**
```
use_persona('mcp-expert')
# MCP protocol and server implementation expert
# 14 expertise areas, ~2,500 line system prompt
```

**Architecture:** All personas are independent (parent: null) with no hierarchical dependencies. Each has comprehensive standalone expertise designed for agentic use.

### Personas Can Use MCP Tools

This is the key innovation:

```
User: use_persona('mcp-expert:planning')

User: "Help me plan a new inventory feature"

Planning Expert:
  - Uses mcp__docs-mcp__gather_context (with MCP expertise)
  - Uses mcp__docs-mcp__analyze_project_for_planning
  - Applies MCP patterns knowledge to guide implementation
  - Provides expert recommendations
```

---

## Implemented MCP Tools

### Core Tools (v1.0.0)

**Implemented:**
- ✅ `use_persona(name)` - Activate a persona
- ✅ `get_active_persona()` - Get currently active persona
- ✅ `clear_persona()` - Reset to default state
- ✅ `list_personas()` - Show available personas

### Custom Persona Creation (v1.4.0 - WO-CREATE-CUSTOM-PERSONA-001)

- ✅ `create_custom_persona(...)` - Create custom personas with guided workflow
  - **Inputs:** name, description, expertise areas (3-10), use cases (3-10), communication style
  - **Optional:** problem_solving, tool_usage, specializations, key_principles, example_responses
  - **Validation:** Multi-stage pipeline (schema → semantic → quality)
  - **Generation:** Template-based system prompt generation with {{placeholders}}
  - **Output:** Complete PersonaDefinition saved to `personas/custom/{name}.json`
  - **Activation:** Immediately usable with `use_persona(name)`

**Future (Stacking/Composition):**
- ⏳ `add_persona(name)` - Stack additional persona
- ⏳ `get_active_personas()` - Show current persona stack (plural)

### Implemented Personas

**Core Personas (5):**

1. ✅ **lloyd-expert** (v1.2.0)
   - Role: Multi-Agent Coordinator
   - Expertise: Project coordination, workorder tracking, task-to-agent assignment, domain validation, multi-agent orchestration
   - Assignment Logic: Keyword-based scoring with 50+ keywords per domain (frontend, backend, testing)
   - System prompt: ~3,000 lines with Multi-Agent Coordination & Task Assignment section

2. ✅ **mcp-expert** (v1.0.0)
   - Expertise: MCP protocol specification, server architecture, tool design, Python SDK, JSON-RPC 2.0
   - Use cases: Planning MCP features, debugging MCP tools, architecture decisions, protocol compliance
   - System prompt: ~2,500 lines (14 expertise areas)

**Specialist Personas (3) - NEW in v1.2-1.3:**

3. ✅ **ava** (v1.2.0) - Frontend Specialist (Agent 2)
   - Domains: UI, React, CSS/Tailwind, accessibility (WCAG 2.1), responsive design, component architecture
   - Expertise: 15+ frontend areas including React hooks, state management, forms, animations, performance optimization
   - Domain Boundaries: Refuses backend/testing tasks, redirects to Marcus/Quinn
   - System prompt: ~1,500 lines with domain boundary detection
   - Slash command: /ava

4. ✅ **marcus** (v1.2.0) - Backend Specialist (Agent 3)
   - Domains: REST/GraphQL APIs, SQL/NoSQL databases, JWT/OAuth auth, RBAC, server architecture, security (OWASP)
   - Expertise: 15+ backend areas including API design, database modeling, caching, background jobs, query optimization
   - Domain Boundaries: Refuses frontend/testing tasks, redirects to Ava/Quinn
   - System prompt: ~1,500 lines with domain boundary detection
   - Slash command: /marcus

5. ✅ **quinn** (v1.2.0) - Testing Specialist (Agent 4)
   - Domains: Unit/integration/E2E testing, TDD, coverage analysis, QA workflows, debugging, test automation
   - Expertise: 15+ testing areas including Jest/pytest, mocking, Playwright/Cypress, performance testing, CI/CD
   - Domain Boundaries: Refuses frontend/backend tasks, redirects to Ava/Marcus
   - System prompt: ~1,500 lines with domain boundary detection
   - Slash command: /quinn

6. ✅ **taylor** (v1.2.0) - General Purpose Agent
   - Domains: Generalist execution (code, tests, docs) - no domain boundaries
   - Expertise: 12+ areas including multi-agent coordination, code implementation, testing, documentation, git workflow
   - Capabilities: Balanced code/test/docs skills, can handle any workorder from Lloyd
   - System prompt: ~3,000 lines with communication.json protocol
   - Slash command: /taylor

7. ✅ **research-scout** (v1.0.0) - Research & Discovery Specialist
   - Domains: Research synthesis, information gathering, trend analysis, competitive intelligence
   - Expertise: 10+ areas including web search, documentation analysis, code pattern discovery
   - Slash command: /research-scout

**Future Personas:** See `coderef/future/claude-20-personas.md` for expansion roadmap

---

## Architecture

### Persona Storage
```
personas/
├── base/
│   └── mcp-expert.json (v1.0.0, parent: null)
└── custom/
    ├── lloyd.json
    ├── ava.json
    ├── marcus.json
    ├── quinn.json
    ├── taylor.json
    └── research-scout.json
```

All personas are independent (no hierarchical structure). Future expansion will add more specialized personas.

### Persona Definition Format
```json
{
  "name": "docs-expert",
  "parent": null,
  "version": "1.0.0",
  "system_prompt": "You are an MCP expert with deep knowledge of the docs-mcp server...",
  "expertise": [
    "docs-mcp tools and generators",
    "POWER framework templates",
    "Planning workflow (gather → analyze → create → validate)",
    "Inventory tools (manifest, dependencies, API, database, config, tests, docs)"
  ],
  "preferred_tools": [
    "mcp__docs-mcp__*"
  ],
  "use_cases": [
    "Planning new docs-mcp features",
    "Debugging docs-mcp tools",
    "Implementing docs-mcp patterns"
  ],
  "behavior": {
    "communication_style": "Expert, technical, references specific tools and patterns",
    "problem_solving": "Uses docs-mcp workflows, follows existing patterns",
    "tool_usage": "Leverages docs-mcp tools effectively for planning and analysis"
  }
}
```

### State Management
- **Persona Stack:** Ordered list of active personas
- **Context Composition:** Later personas overlay on earlier ones
- **System Prompt Merging:** Concatenate contexts when stacking
- **Tool Integration:** Personas influence AI behavior, not tool behavior

### MCP Server Implementation
```python
# server.py
from mcp.server import Server

app = Server("personas-mcp")

@app.list_tools()
async def list_tools():
    return [
        Tool(name='use_persona', ...),
        Tool(name='add_persona', ...),
        Tool(name='clear_personas', ...),
        Tool(name='list_personas', ...),
        Tool(name='get_active_personas', ...)
    ]

# Handle persona activation
async def handle_use_persona(arguments):
    persona_name = arguments['name']
    persona = load_persona(persona_name)

    # Return composed system prompt
    return {
        'system_prompt': persona.system_prompt,
        'active_personas': [persona_name],
        'expertise': persona.expertise
    }
```

---

## Example Use Cases

### UC-1: MCP Feature Planning with Expert
```
User: use_persona('mcp-expert:planning')

AI: "I'm now your MCP planning expert, specializing in the docs-mcp planning workflow."

User: "Help me plan a new feature for gathering context with AskUserQuestion"

MCP Planning Expert:
  1. Uses mcp__docs-mcp__gather_context (with expertise)
  2. Asks expert questions about MCP tool design
  3. Uses mcp__docs-mcp__analyze_project_for_planning
  4. Applies MCP patterns knowledge
  5. Creates expert implementation plan
```

### UC-2: Documentation Writing
```
User: use_persona('docs-specialist')

AI: "I'm now your documentation specialist, expert in POWER framework."

User: "Help me document the persona system"

Docs Specialist:
  1. Analyzes existing documentation patterns
  2. Applies POWER framework (Purpose, Overview, What/Why/When, Examples, References)
  3. Ensures clarity and completeness
  4. Creates well-structured documentation
```

### UC-3: Complex Task with Stacked Personas
```
User: use_persona('mcp-expert')
User: add_persona('planning-expert')

AI: "I'm combining MCP expertise with planning expertise."

User: "Plan a new changelog feature for docs-mcp"

Combined Expert:
  1. Uses MCP architecture knowledge
  2. Applies planning workflows
  3. Uses docs-mcp tools effectively
  4. Creates comprehensive plan with both expertises
```

### UC-4: Creating a Custom Persona (NEW in v1.4.0)
```
User: "I need a persona for API design expertise"

AI: "I'll help you create a custom api-design expert persona."

AI calls create_custom_persona with:
- name: "api-expert"
- description: "REST API design and development specialist focusing on best practices"
- expertise: ["RESTful architecture", "OpenAPI specification", "API security", "Rate limiting", "Versioning strategies"]
- use_cases: ["Designing new endpoints", "Reviewing API architecture", "Implementing auth flows"]
- communication_style: "Technical and example-driven, references REST/OpenAPI standards"

System response:
✅ Custom Persona Created Successfully
- Name: api-expert
- System prompt generated (1500+ lines)
- Saved to: personas/custom/api-expert.json
- Ready to activate

User: use_persona('api-expert')

AI: "I'm now your API design expert, specializing in RESTful architecture and best practices."

User: "How should I version my API?"

API Expert:
  1. Explains versioning strategies (URI, header, query param)
  2. Recommends semantic versioning (v1, v2) in URI path
  3. Provides examples of backward compatibility
  4. References OpenAPI 3.0 best practices
```

---

## Project Status

### Current Phase: ✅ v1.4.1 - Lloyd Optimization

**v1.4.1 (2025-12-13) - Lloyd Persona Optimization (WO-SLIM-LLOYD-PERSONA-001):**
- ✅ Reduced lloyd.json system_prompt from 1,017 lines to 153 lines (85% reduction)
- ✅ Extracted reference material to `docs/MCP-ECOSYSTEM-REFERENCE.md`
- ✅ Extracted workflows/scenarios to `docs/LLOYD-REFERENCE.md`
- ✅ Removed duplicate "Big Picture" and "Deep Understanding" sections
- ✅ Replaced verbose tool catalogs with summary tables
- ✅ Added reference pointers to extracted docs
- ✅ Updated lloyd.json version to 1.2.0
- ✅ All tests passing (JSON parsing, MCP loading, /lloyd command)

**v1.4.0 (2025-10-23) - Custom Persona Creation (WO-CREATE-CUSTOM-PERSONA-001):**
- ✅ `create_custom_persona` MCP tool with guided workflow
- ✅ Multi-stage validation pipeline (schema → semantic → quality)
- ✅ Template-based system prompt generation with {{placeholders}}
- ✅ CustomPersonaInput Pydantic schema (3-10 expertise areas, 3-10 use cases)
- ✅ PersonaValidator with uniqueness checking (prevents base persona conflicts)
- ✅ PersonaGenerator with TemplateRenderer (supports conditional sections)
- ✅ 33 unit + integration tests (100% pass rate)
- ✅ /create-persona slash command
- ✅ Documentation: README, CLAUDE.md, CUSTOMIZATION-GUIDE.md
- ✅ Custom personas saved to personas/custom/ and immediately usable

### Previous Phase: ✅ v1.2.0 - Agent Specialization & Domain Boundaries

**v1.2.0 (2025-10-23) - Lloyd Coordination Enhancement:**
- ✅ Transformed generalist agents into domain specialists:
  - Agent 2: **Ava** (Frontend Specialist) - React, CSS, accessibility, UI
  - Agent 3: **Marcus** (Backend Specialist) - API, database, auth, security
  - Agent 4: **Quinn** (Testing Specialist) - Unit/integration tests, QA, coverage
- ✅ Lloyd (Agent 1) enhanced with task-to-agent assignment logic:
  - Keyword-based domain matching (50+ keywords per domain)
  - Scoring algorithm assigns tasks to appropriate specialist
  - Domain validation before assignment
- ✅ Domain boundary detection added to all specialists:
  - Each agent refuses out-of-domain tasks with clear error messages
  - Redirects to correct specialist with @Lloyd tagging
  - Refusal protocol: Acknowledge → Identify → Explain → Recommend → Tag
- ✅ communication.json schema updated:
  - Added `agent_specialization` field ("frontend" | "backend" | "testing")
- ✅ Workorders: WO-AGENT-SPECIALIZATION-001 through WO-AGENT-SPECIALIZATION-004
- ✅ All specialists have 1500+ line system prompts with:
  - Deep domain expertise (15+ expertise areas each)
  - MCP ecosystem knowledge (workorders, docs-mcp tools, protocols)
  - Multi-agent coordination skills
  - Domain boundary refusal logic

**v1.1.0 (2025-10-20) - Multi-Agent Generalist Personas:**
- ✅ Added taylor.json (general purpose agent with balanced code, test, docs capabilities)
- ✅ General purpose agent for any workorder type from Lloyd
- ✅ Understands communication.json protocol for Lloyd coordination
- ✅ Slash command: /taylor
- ✅ MVP focus: Connection + communication basics, specialization comes later
- ✅ Workorder: WO-AGENT-SPECIALIZATION-005

**v1.0.0 (2025-10-18) - Initial Release:**
- ✅ Core concept defined
- ✅ MCP server implemented (server.py with 4 tools)
- ✅ PersonaManager implemented and simplified (base/ directory only)
- ✅ 1 independent base persona created (mcp-expert)
- ✅ Lloyd-expert added as coordinator persona
- ✅ Comprehensive system prompts (1000-6000+ lines for agentic use)
- ✅ Slash commands created (/use-persona)
- ✅ All personas tested and validated locally
- ✅ Documentation complete (PERSONAS-CREATED.md, my-guide.md, CLAUDE.md)

**Next Steps:**
1. ⏳ Refine agent roles based on real-world usage
2. ⏳ Expand to 20 personas (see coderef/future/claude-20-personas.md)
3. ⏳ Implement persona stacking/composition (add_persona, get_active_personas)
4. ⏳ Add persona metadata queries (expertise search, use case search)
5. ⏳ Create persona recommendation engine
6. ⏳ Add persona version management
7. ⏳ Implement persona updates and migrations

---

## File Structure

```
personas-mcp/
├── CLAUDE.md                          ← You are here (AI context - updated)
├── PERSONAS-CREATED.md                ← Complete implementation summary
├── my-guide.md                        ← Quick reference guide
├── .claude/
│   └── commands/
│       └── use-persona.md             ← /use-persona <name>
├── coderef/
│   ├── future/
│   │   ├── composable-personas-concept.md  ← Core concept
│   │   └── claude-20-personas.md      ← Future persona expansion (to be created)
│   └── working/
│       └── agent-persona-mcp/
│           └── context.json           ← Feature requirements
├── personas/
│   ├── base/
│   │   └── mcp-expert.json            ← ✅ v1.0.0 (14 expertise areas)
│   └── custom/
│       ├── lloyd.json
│       ├── ava.json
│       ├── marcus.json
│       ├── quinn.json
│       ├── taylor.json
│       └── research-scout.json
├── src/
│   ├── models.py                      ← PersonaDefinition Pydantic schema
│   └── persona_manager.py             ← PersonaManager (simplified)
└── server.py                          ← ✅ MCP server (4 tools implemented)
```

---

## Key Design Decisions

**1. Independent vs Hierarchical** (Changed in v1.0.0)
- ✅ Independent personas (parent: null) - comprehensive standalone expertise
- ❌ Hierarchical notation (parent:child) - deferred to future
- Reason: Agentic use requires complete context without dependencies

**2. Comprehensive System Prompts**
- 1000-6000+ line system prompts (not minimal summaries)
- Include workflows, examples, tool knowledge, best practices
- Designed for AI-to-AI (agentic) interaction, not just human guidance

**3. Stateless Personas**
- No memory across sessions
- State tracked during session only
- Clean slate on server restart

**4. Single Active Persona** (v1.0.0)
- One persona active at a time
- Future: Stacking/composition with add_persona()
- Deferred to preserve simplicity in v1.0.0

**5. Tool Integration**
- Personas don't wrap tools
- Personas provide context that influences AI behavior
- AI applies persona knowledge when using any available tools

**6. MCP Protocol Compliance**
- Follow MCP specification strictly
- Use standard tool patterns (JSON-RPC 2.0 over stdio)
- Compatible with all MCP clients (Claude Code, etc.)

---

## Related Projects

**docs-mcp:**
- Provides planning, documentation, and inventory tools
- Personas will use docs-mcp tools extensively
- `mcp-expert:docs-mcp` persona specializes in docs-mcp knowledge

**Other MCP Servers:**
- Personas can use tools from any MCP server
- Tool usage influenced by active persona expertise
- Enables expert-guided workflows across MCP ecosystem

---

## For AI Agents

When working on personas-mcp:

1. **Read this file first** - Understand the core concept
2. **Check context.json** - See detailed requirements
3. **Review concept doc** - Understand architecture decisions
4. **Follow MCP patterns** - Use existing MCP server patterns
5. **Test with docs-mcp** - Verify persona/tool integration works

**Key Principle:** Personas are **context providers**, not tool wrappers. They influence how the AI thinks and acts, but don't modify tool behavior.

---

## Questions?

**Q: How do personas differ from system prompts?**
A: Personas ARE system prompts, but composable and domain-specific. They're designed to be activated/deactivated on demand.

**Q: Can personas conflict?**
A: Designed to complement. If conflicts arise, later personas take precedence (overlay pattern).

**Q: Are personas stateful?**
A: Yes within a session, no across sessions. Track active persona stack during session only.

**Q: Can users create custom personas?**
A: Not in v1. Pre-defined personas only. Custom personas could be future enhancement.

**Q: How many personas can be stacked?**
A: No hard limit, but context size may impose practical limits (likely 3-4 max).

---

**Last Updated:** 2025-10-18
**Next Review:** After implementation plan created

---

*This is a living document. Update as the project evolves.*
