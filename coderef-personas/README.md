# CodeRef Personas MCP Server

**Project:** coderef-personas
**Version:** 1.5.0
**Date:** 2025-12-30
**Status:** ✅ Production

---

## Purpose

The coderef-personas MCP server provides expert AI personas that influence how AI assistants approach problems and use tools. Think of it as switching between different expert consultants - each with deep domain knowledge in specific areas.

---

## Overview

**coderef-personas** is a Python-based MCP server that implements the Model Context Protocol (MCP) to provide specialized expert personas. When activated, these personas give AI assistants comprehensive domain knowledge, communication patterns, and problem-solving approaches.

**Key Features:**
- ✅ **11 Expert Personas** - Domain specialists from MCP architecture to frontend/backend/testing
- ✅ **Custom Persona Creation** - Create custom personas with guided workflow and multi-stage validation
- ✅ **Multi-Agent Coordination** - Lloyd coordinates task assignment to specialist agents (Ava, Marcus, Quinn)
- ✅ **Lloyd Integration** - Todo generation, plan tracking, and interactive plan execution
- ✅ **8 MCP Tools** - Persona management + Lloyd integration + custom persona creation
- ✅ **Claude Code Integration** - Works seamlessly with Claude Code's MCP client

---

## What You'll Find Here

### Quick Start

- Prerequisites and installation
- Basic usage examples
- Available personas and tools

### Installation

- Step-by-step setup instructions
- MCP configuration for Claude Code

### Usage Patterns

- Activating personas
- Using Lloyd for multi-agent coordination
- Creating custom personas
- Common workflows

### Troubleshooting

- Common issues and resolutions
- Error patterns and solutions

---

## Prerequisites

- **Python 3.10 or higher**
- **Claude Code** (or another MCP-compatible client)
- **pip** or **poetry** for package management

---

## Installation

### Step 1: Install Dependencies

```bash
cd C:\Users\willh\.mcp-servers\coderef-personas
pip install -e .
```

**Expected output:**
```
Successfully installed coderef-personas-1.5.0
```

---

### Step 2: Configure MCP Client

Add to your `~/.mcp.json` (or Claude Code's MCP configuration):

```json
{
  "mcpServers": {
    "coderef-personas": {
      "command": "python",
      "args": [
        "-m",
        "coderef-personas.server"
      ],
      "env": {}
    }
  }
}
```

**For Claude Code specifically**, edit `.claude/settings.json`:

```json
{
  "mcpServers": {
    "coderef-personas": {
      "command": "python",
      "args": [
        "C:\\Users\\willh\\.mcp-servers\\coderef-personas\\server.py"
      ]
    }
  }
}
```

---

### Step 3: Restart MCP Client

- **Claude Code:** Restart Claude Code completely
- **Other MCP clients:** Follow client-specific restart instructions

---

### Step 4: Verify Installation

Test that personas are available:

```bash
# Use list_personas tool
mcp__coderef-personas__list_personas()
```

**Expected output:**
```
# Available Personas

## lloyd (v1.5.0)
**Description:** Multi-agent coordinator specializing in task assignment...

## ava (v1.2.0)
**Description:** Frontend specialist focusing on React, CSS, accessibility...

[... 9 more personas ...]

**Total:** 11 persona(s) available
```

---

## Usage

### Quick Start Guide

#### 1. Activate a Persona

```
# Use the use_persona tool
mcp__coderef-personas__use_persona(name: "lloyd")

# Or use slash commands (if configured)
/lloyd
/ava
/marcus
/quinn
```

**Output:**
```markdown
# Persona Activated: lloyd

**Version:** 1.5.0
**Description:** Multi-agent coordinator specializing in task assignment...

---

## System Prompt

You are Lloyd, the Multi-Agent Coordinator...
[Full 8,820-character system prompt]

---

✅ Persona 'lloyd' is now active. You should adopt this persona's expertise...
```

---

#### 2. Use the Persona's Expertise

With Lloyd active:

```
User: I need to implement an authentication system.

Lloyd: I'll analyze this task and assign it to the appropriate specialist agent.

[Task Analysis]
- Domain: Backend (authentication, JWT, database)
- Complexity: High (security, sessions, authorization)
- Agent: Marcus (Backend Specialist)

Assigning to Marcus...

@Marcus: Please implement JWT authentication system with refresh tokens.
```

---

#### 3. Check Active Persona

```
mcp__coderef-personas__get_active_persona()
```

**Output:**
```markdown
# Active Persona: lloyd

**Version:** 1.5.0
**Description:** Multi-agent coordinator specializing in task assignment and workorder tracking
**Activated:** 2025-12-30 14:23:15

## Current Expertise

- Project coordination and workorder tracking
- Task-to-agent assignment (keyword-based scoring)
...

You are currently operating with the lloyd persona active.
```

---

#### 4. Clear Persona

```
mcp__coderef-personas__clear_persona()
```

**Output:**
```markdown
✅ Persona 'lloyd' has been deactivated. Returning to default behavior.
```

---

### Available Personas

#### 1. Lloyd (Multi-Agent Coordinator)

**Version:** 1.5.0
**Best For:** Project coordination, task assignment, multi-agent orchestration

**Expertise:**
- Project coordination and workorder tracking
- Task-to-agent assignment (keyword-based scoring with 50+ keywords per domain)
- Domain validation (frontend, backend, testing)
- Multi-agent orchestration and communication.json protocol
- Planning workflow (/create-workorder 11-step automation)
- Foundation docs generation (ARCHITECTURE, SCHEMA, COMPONENTS)
- Progress tracking and deliverables management

**When to Use:**
- Managing complex multi-step projects
- Coordinating parallel agent execution
- Assigning tasks to specialist agents (Ava, Marcus, Quinn)
- Tracking workorder progress

**Command:** `/lloyd` or `use_persona("lloyd")`

---

#### 2. Ava (Frontend Specialist)

**Version:** 1.2.0
**Best For:** React development, CSS/Tailwind styling, UI/UX implementation

**Expertise:**
- React hooks and component architecture
- CSS/Tailwind styling and responsive design
- HTML5 semantic markup
- WCAG 2.1 Level AA accessibility compliance
- Forms, validation, and state management
- UI component libraries and design systems

**When to Use:**
- Building React components
- Implementing responsive layouts
- Fixing accessibility issues
- Styling with Tailwind or CSS Modules

**Command:** `/ava` or `use_persona("ava")`

---

#### 3. Marcus (Backend Specialist)

**Version:** 1.2.0
**Best For:** REST/GraphQL APIs, databases, authentication, backend architecture

**Expertise:**
- RESTful and GraphQL API design
- SQL (PostgreSQL, MySQL) and NoSQL (MongoDB, Redis) databases
- Authentication (JWT, OAuth) and authorization (RBAC)
- Security best practices (OWASP, rate limiting, XSS prevention)
- Caching strategies and background job queues
- API documentation (OpenAPI, GraphQL schemas)

**When to Use:**
- Designing backend APIs
- Implementing authentication systems
- Database schema design and optimization
- Security hardening

**Command:** `/marcus` or `use_persona("marcus")`

---

#### 4. Quinn (Testing Specialist)

**Version:** 1.2.0
**Best For:** Unit/integration/E2E testing, TDD, test automation

**Expertise:**
- Unit testing frameworks (Jest, pytest, JUnit)
- Integration testing (Supertest, pytest fixtures)
- E2E testing (Playwright, Cypress, Selenium)
- Test coverage analysis and improvement
- Mocking/stubbing strategies
- CI/CD test automation

**When to Use:**
- Writing unit test suites (targeting 80-90%+ coverage)
- Integration tests for APIs
- Implementing TDD workflows
- E2E test scenarios

**Command:** `/quinn` or `use_persona("quinn")`

---

#### 5. Taylor (General Purpose Agent)

**Version:** 1.2.0
**Best For:** Balanced code/test/docs tasks, any workorder from Lloyd

**Expertise:**
- Multi-agent coordination and communication.json protocol
- Code implementation (balanced frontend/backend)
- Testing (unit, integration, E2E)
- Documentation (inline comments, READMEs, API docs)
- Git workflow and version control

**When to Use:**
- Tasks that cross multiple domains
- Workorders requiring balanced code/test/docs skills
- General-purpose implementation tasks

**Command:** `/taylor` or `use_persona("taylor")`

---

#### 6-11. CodeRef Ecosystem Agents

**coderef-mcp-lead** (v1.1.0) - Lead System Architect
- Oversight of all 5 MCP servers (context, workflow, docs, personas, testing)
- Command: `/coderef-mcp-lead`

**coderef-context-agent** (v1.0.0) - Code Intelligence Specialist
- AST parsing, dependency graphs, impact analysis
- Command: `use_persona("coderef-context-agent")`

**coderef-docs-agent** (v1.0.0) - Documentation & Planning Specialist
- POWER framework, planning workflows, changelog management
- Command: `use_persona("coderef-docs-agent")`

**coderef-testing-agent** (v1.0.0) - Test Automation Specialist
- Pytest integration, coverage analysis, test health metrics
- Command: `use_persona("coderef-testing-agent")`

**research-scout** (v1.0.0) - Research & Discovery Specialist
- Research synthesis, information gathering, trend analysis
- Command: `use_persona("research-scout")`

---

### Creating Custom Personas

**NEW in v1.4.0:** Create custom personas with guided workflow!

#### Example: Create an API Design Expert

```python
mcp__coderef-personas__create_custom_persona(
    name="api-expert",
    description="REST API design and development specialist focusing on OpenAPI standards",
    expertise="RESTful architecture, OpenAPI 3.0, API versioning, Rate limiting, Authentication patterns",
    use_cases="Designing REST endpoints, Reviewing API specs, Implementing auth flows, Optimizing performance",
    communication_style="Technical and example-driven, references REST/OpenAPI best practices"
)
```

**Output:**
```markdown
# ✅ Custom Persona Created Successfully

**Name:** api-expert
**Version:** 1.0.0
**Description:** REST API design and development specialist focusing on OpenAPI standards
**Saved to:** personas/custom/api-expert.json

## Persona Details

**Expertise Areas (5):**
- RESTful architecture
- OpenAPI 3.0
- API versioning
- Rate limiting
- Authentication patterns

**Use Cases (4):**
- Designing REST endpoints
- Reviewing API specs
- Implementing auth flows
- Optimizing performance

**Communication Style:**
Technical and example-driven, references REST/OpenAPI best practices

## Next Steps

1. **Activate your persona:**
   ```
   use_persona('api-expert')
   ```

2. **List all personas (including custom):**
   ```
   list_personas()
   ```

✅ Your custom persona is ready to use!
```

---

### Lloyd Integration (Multi-Agent Workflows)

Lloyd can coordinate multi-agent task execution using `communication.json` protocol:

#### Example Workflow

**Step 1:** Create implementation plan

```bash
/create-workorder
# Generates plan.json in coderef/workorder/{feature}/
```

**Step 2:** Generate TodoWrite task list

```python
mcp__coderef-personas__generate_todo_list(
    plan_path="coderef/workorder/auth-system/plan.json",
    workorder_id="WO-AUTH-SYSTEM-001",
    mode="all"
)
```

**Step 3:** Lloyd assigns tasks to specialist agents

```
Lloyd analyzes task: "Implement JWT authentication middleware"

Domain keywords detected:
- "authentication" (backend)
- "JWT" (backend)
- "middleware" (backend)

Score: Backend = 85, Frontend = 5, Testing = 10

Assigning to Marcus (Backend Specialist)...
```

**Step 4:** Track progress

```python
mcp__coderef-personas__track_plan_execution(
    plan_path="coderef/workorder/auth-system/plan.json",
    workorder_id="WO-AUTH-SYSTEM-001",
    todo_status=[
        {"task_id": "SETUP-001", "status": "completed"},
        {"task_id": "IMPL-001", "status": "in_progress"},
        ...
    ]
)
```

---

## Available Tools

### Core Persona Management

1. **`use_persona(name)`** - Activate a persona
2. **`get_active_persona()`** - Check active persona
3. **`clear_persona()`** - Deactivate persona
4. **`list_personas()`** - List all available personas

### Lloyd Integration (Phase 1)

5. **`generate_todo_list(plan_path, workorder_id, mode)`** - Convert plan to TodoWrite format
6. **`track_plan_execution(plan_path, workorder_id, todo_status)`** - Sync plan progress
7. **`execute_plan_interactive(plan_path, workorder_id, mode)`** - Execute plan (step-by-step or batch)

### Custom Persona Creation

8. **`create_custom_persona(...)`** - Create custom personas with validation

---

## Common Workflows

### Workflow 1: Single Specialist Task

```
1. User: "Fix accessibility issues in the navigation component"
2. /ava (activate Ava, frontend specialist)
3. Ava: Analyzes component, identifies ARIA issues, provides fixes
4. Implementation: Fix accessibility issues
5. /quinn (activate Quinn, testing specialist)
6. Quinn: Writes accessibility tests
7. clear_persona() (return to default)
```

---

### Workflow 2: Multi-Agent Feature Implementation

```
1. /create-workorder (generates plan.json)
2. /lloyd (activate Lloyd, coordinator)
3. Lloyd: Generates communication.json with agent assignments
4. Lloyd: Assigns frontend tasks to Ava, backend to Marcus, tests to Quinn
5. Agents work in parallel on assigned tasks
6. Lloyd: Tracks progress, verifies completion
7. /aggregate-agent-deliverables (combines metrics)
8. /archive-feature (archives completed feature)
```

---

### Workflow 3: Create Custom Persona

```
1. Identify domain expertise needed
2. Call create_custom_persona with:
   - name (alphanumeric, hyphens, underscores)
   - description (20-200 chars)
   - expertise (3-10 items)
   - use_cases (3-10 items)
   - communication_style (20-200 chars)
3. System validates (schema → semantic → quality)
4. Persona generated with system prompt
5. Saved to personas/custom/{name}.json
6. Immediately usable with use_persona(name)
```

---

## Troubleshooting

### Error: "Persona not found"

**Symptoms:**
```
Error: Persona 'invalid-name' not found. Available personas: lloyd, ava, marcus...
```

**Resolution:**
1. List available personas: `list_personas()`
2. Check spelling (persona names are case-sensitive)
3. Verify persona JSON file exists in `personas/custom/` or `personas/coderef-personas/`

---

### Error: "Validation failed" (Custom Persona Creation)

**Symptoms:**
```
# Persona Creation Failed

**Validation Errors:**

- [schema] name must match pattern ^[a-z0-9_-]+$
- [semantic] expertise must contain 3-10 unique items (found 2)
```

**Resolution:**
1. **Name:** Use only lowercase alphanumeric, hyphens, underscores
2. **Expertise:** Provide 3-10 unique expertise areas
3. **Use Cases:** Provide 3-10 unique use cases
4. **Description:** 20-200 characters
5. **Communication Style:** 20-200 characters

---

### Error: "No persona is currently active"

**Symptoms:**
```
No persona is currently active. Use 'use_persona' to activate a persona.
```

**Resolution:**
1. Activate a persona: `use_persona("lloyd")`
2. Or use slash command: `/lloyd`

---

### Error: MCP Server Not Responding

**Symptoms:**
- Tools don't appear in autocomplete
- MCP calls timeout

**Resolution:**
1. **Check MCP configuration:**
   ```bash
   cat ~/.mcp.json
   # Verify coderef-personas is configured
   ```

2. **Restart MCP server:**
   - Close Claude Code completely
   - Reopen Claude Code
   - MCP server will restart automatically

3. **Verify Python environment:**
   ```bash
   python -m coderef-personas.server
   # Should start the server without errors
   ```

4. **Clear MCP cache (if needed):**
   ```bash
   rm ~/.cursor/projects/{PROJECT_ID}/mcp-cache.json
   # Restart Claude Code
   ```

---

## Project Structure

```
coderef-personas/
├── server.py                 # MCP server entry point
├── pyproject.toml            # Python project configuration
├── README.md                 # This file
├── CLAUDE.md                 # AI context documentation
├── src/
│   ├── __init__.py
│   ├── models.py             # Pydantic data models
│   ├── persona_manager.py    # Persona loading/activation
│   ├── validators.py         # Multi-stage validation
│   ├── persona_generator.py  # Custom persona generation
│   ├── generators/
│   │   └── todo_list_generator.py
│   ├── trackers/
│   │   └── plan_execution_tracker.py
│   └── executors/
│       └── interactive_plan_executor.py
├── personas/
│   ├── custom/               # Custom personas
│   │   ├── lloyd.json
│   │   ├── ava.json
│   │   ├── marcus.json
│   │   ├── quinn.json
│   │   ├── taylor.json
│   │   └── research-scout.json
│   └── coderef-personas/     # CodeRef ecosystem agents
│       ├── coderef-mcp-lead.json
│       ├── coderef-context-agent.json
│       ├── coderef-docs-agent.json
│       └── coderef-testing-agent.json
├── tests/                    # Test suite
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_persona_generator.py
│   └── integration/
└── coderef/
    └── foundation-docs/      # Generated documentation
        ├── API.md
        ├── SCHEMA.md
        ├── COMPONENTS.md
        └── ARCHITECTURE.md
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_validators.py

# Run specific test
pytest tests/test_validators.py::test_schema_validation
```

---

### Adding a New Persona

**Option 1: Use create_custom_persona Tool**

```python
mcp__coderef-personas__create_custom_persona(
    name="your-persona",
    description="Brief description (20-200 chars)",
    expertise="Area 1, Area 2, Area 3, ...",
    use_cases="Use case 1, Use case 2, Use case 3, ...",
    communication_style="How this persona communicates (20-200 chars)"
)
```

**Option 2: Manual JSON Creation**

1. Create `personas/custom/your-persona.json`:
   ```json
   {
     "name": "your-persona",
     "version": "1.0.0",
     "parent": null,
     "description": "Brief description",
     "system_prompt": "Comprehensive system prompt...",
     "expertise": ["Area 1", "Area 2", "Area 3"],
     "use_cases": ["Use case 1", "Use case 2", "Use case 3"],
     "behavior": {
       "communication_style": "How this persona communicates",
       "problem_solving": "How this persona approaches problems",
       "tool_usage": "How this persona uses tools",
       "guidance_pattern": null
     },
     "specializations": null,
     "example_responses": null,
     "key_principles": null,
     "created_at": "2025-12-30T00:00:00Z",
     "updated_at": "2025-12-30T00:00:00Z"
   }
   ```

2. Restart MCP server
3. Activate: `use_persona("your-persona")`

---

## Additional Resources

- **[API.md](coderef/foundation-docs/API.md)** - MCP tool schemas and endpoints
- **[SCHEMA.md](coderef/foundation-docs/SCHEMA.md)** - Data models and validation
- **[COMPONENTS.md](coderef/foundation-docs/COMPONENTS.md)** - Software components
- **[ARCHITECTURE.md](coderef/foundation-docs/ARCHITECTURE.md)** - System architecture
- **[CLAUDE.md](CLAUDE.md)** - AI context and implementation guide

---

## Footer

**Version:** 1.5.0
**Status:** ✅ Production
**Last Updated:** 2025-12-30
**Maintained By:** willh, Claude Code AI

**MCP Protocol:** JSON-RPC 2.0 over stdio (MCP specification v1.0)
**Python Version:** 3.10+
**License:** MIT

---

## AI Usage Note

This MCP server is designed for AI agent consumption. All tools return markdown-formatted responses optimized for LLM parsing. System prompts are comprehensive (1,500-8,820 characters) to enable effective persona adoption without external knowledge injection.

**Design Philosophy:** Simple, understandable, maintainable. Personas are context providers, not tool wrappers. They influence how AI approaches problems and uses other MCP tools.
