# personas-mcp

**Independent Expert Agent Personas for AI Assistants**

An MCP server that provides expert personas that influence how AI approaches problems and uses tools.

## What is This?

personas-mcp allows you to activate expert "personas" that give AI assistants specialized knowledge and behavior. Think of it like switching between different expert consultants - each with deep domain knowledge in specific areas.

### v1.4.0 Features

- ✅ **10 base personas** - mcp-expert, docs-expert, coderef-expert, nfl-scraper-expert, lloyd-expert, ava (frontend specialist), marcus (backend specialist), quinn (testing specialist), taylor (general purpose agent), devon (setup specialist)
- ✅ **Custom persona creation** - NEW! Create custom personas with guided workflow, automatic system prompt generation, and multi-stage validation
- ✅ **Specialized agents** - Ava (Frontend Specialist) with React/CSS/accessibility expertise, Quinn (Testing Specialist) with comprehensive testing, TDD, and QA expertise
- ✅ **Multi-agent coordination** - Specialized and generalist agents work with Lloyd via communication.json protocol for parallel task execution
- ✅ **Comprehensive expertise** - 1000-6000+ line system prompts designed for agentic use
- ✅ **Simple activation** - Use `/use-persona <name>` or shortcuts (`/docs-expert`, `/coderef-expert`, `/ava`, `/marcus`, `/quinn`, `/taylor`)
- ✅ **5 MCP tools** - use_persona, get_active_persona, clear_persona, list_personas, create_custom_persona
- ✅ **Claude Code integration** - Works seamlessly with Claude Code's MCP client

## Installation

### Prerequisites

- Python 3.10 or higher
- Claude Code (or another MCP-compatible client)

### Setup

1. **Install dependencies:**
```bash
cd C:\Users\willh\.mcp-servers\personas-mcp
pip install -e .
```

2. **Add to Claude Code config:**

Edit your `.claude/settings.json`:

```json
{
  "mcpServers": {
    "personas-mcp": {
      "command": "python",
      "args": ["C:\\Users\\willh\\.mcp-servers\\personas-mcp\\server.py"]
    }
  }
}
```

3. **Restart Claude Code**

## Usage

### Quick Start

1. **Activate a persona:**
```
/use-persona mcp-expert          # MCP protocol & server implementation
/use-persona docs-expert          # Documentation & planning (docs-mcp tools)
/use-persona coderef-expert       # CodeRef-MCP server building
/use-persona nfl-scraper-expert   # NFL data scraping (next-scraper platform)
/use-persona ava                  # Frontend development (React, CSS, accessibility)
/use-persona marcus               # Backend development (REST/GraphQL, databases, auth)
/use-persona devon                # Project setup & infrastructure (Next.js, Docker, CI/CD)

# Or use shortcuts:
/docs-expert
/coderef-expert
/nfl-scraper-expert
/ava
/marcus
/devon
```

2. **Ask expert-level questions:**
```
How should I design a new MCP tool that needs to access a database?
```

The AI will respond with domain-specific expertise, referencing protocol patterns and best practices.

3. **Check active persona:**
```
Use the get_active_persona tool
```

4. **Deactivate:**
```
Use the clear_persona tool
```

### Available Tools

#### Core Persona Tools

- **`use_persona(name)`** - Activate a persona
- **`get_active_persona()`** - Check which persona is active
- **`clear_persona()`** - Deactivate current persona
- **`list_personas()`** - See all available personas

#### Custom Persona Creation (NEW in v1.4.0)

- **`create_custom_persona(...)`** - Create custom personas through guided workflow
  - Provide: name, description, expertise areas, use cases, communication style
  - System generates complete persona with system prompt
  - Multi-stage validation (schema → semantic → quality)
  - Saved to `personas/custom/{name}.json`
  - Immediately usable with `use_persona(name)`
  - See `/create-persona` slash command for interactive workflow

### Available Personas

#### Base Expert Personas

**mcp-expert** (v1.0.0)
- **Expertise:** MCP protocol (2024-11-05), server architecture, tool design, Python MCP SDK, JSON-RPC 2.0
- **Best for:** Building MCP servers, designing tools, MCP integration questions, protocol compliance
- **System prompt:** ~2,500 lines (14 expertise areas)

**docs-expert** (v1.0.0)
- **Expertise:** POWER framework, 30 docs-mcp tools, planning workflows, standards enforcement, multi-agent coordination
- **Best for:** Documentation generation, implementation planning, standards auditing, project inventory
- **System prompt:** ~6,000 lines (20 expertise areas)

**coderef-expert** (v1.0.0)
- **Expertise:** Building CodeRef-MCP server (AST scanning, drift detection, query engines, integration patterns)
- **Best for:** Implementing code analysis tools, building connected MCP network, AST-based parsing
- **System prompt:** ~5,000 lines (18 expertise areas)

**nfl-scraper-expert** (v1.2.0)
- **Expertise:** NFL data scraping, ESPN API integration, next-scraper platform (5 scrapers, NFL data model, Docker deployment)
- **Best for:** Building/maintaining next-scraper platform, ESPN API debugging, NFL data normalization, production deployment
- **System prompt:** ~1,500 lines (18 expertise areas)

**lloyd-expert** (v1.1.0)
- **Expertise:** Project coordination, task decomposition, progress tracking, multi-agent coordination
- **Best for:** Managing complex multi-step projects, coordinating parallel agent execution
- **System prompt:** ~3,000 lines

#### Specialized Execution Agents

**ava** (v1.0.0) - Frontend Specialist (Agent 2) **NEW in v1.2.0**
- **Expertise:** React development, modern CSS (Tailwind/CSS Modules), accessibility (WCAG 2.1), responsive design, component patterns, state management, UI testing
- **Best for:** Building React components, implementing responsive layouts, fixing accessibility issues, styling with Tailwind, form validation, UI testing
- **System prompt:** ~1,600 lines (21 expertise areas)
- **Specialties:**
  - React (hooks, Context API, performance optimization)
  - CSS architecture (Tailwind, CSS Modules, Styled-components)
  - HTML5 semantic markup
  - WCAG 2.1 Level AA compliance
  - Design systems and component libraries

**marcus** (v1.0.0) - Backend Specialist (Agent 3) **NEW in v1.2.0**
- **Expertise:** REST/GraphQL APIs, SQL/NoSQL databases, JWT/OAuth authentication, RBAC authorization, security best practices (OWASP), API documentation, caching, background jobs
- **Best for:** Designing backend APIs, implementing authentication systems, database schema design, query optimization, security hardening, API documentation
- **System prompt:** ~1,500 lines (24 expertise areas)
- **Specialties:**
  - RESTful and GraphQL API design
  - SQL (PostgreSQL, MySQL) and NoSQL (MongoDB, Redis) databases
  - Authentication (JWT, OAuth) and authorization (RBAC)
  - Data validation (Joi, Zod) and error handling
  - Security (OWASP, rate limiting, CSRF, XSS prevention)
  - Caching strategies and background job queues

**quinn** (v1.0.0) - Testing Specialist (Agent 4) **NEW in v1.2.0**
- **Expertise:** Unit testing (Jest/pytest), integration testing, TDD, E2E testing (Playwright/Cypress), test coverage analysis, mocking/stubbing, debugging, QA workflows, test automation, performance testing
- **Best for:** Writing unit test suites (80-90%+ coverage), integration tests for APIs, implementing TDD workflows, debugging failing tests, E2E scenarios, test automation, coverage improvement
- **System prompt:** ~1,800 lines (22 expertise areas)
- **Specialties:**
  - Unit testing frameworks (Jest, pytest, JUnit, RSpec)
  - Integration testing (Supertest, pytest fixtures, Testcontainers)
  - E2E testing (Playwright, Cypress, Selenium, Puppeteer)
  - Test coverage analysis and improvement
  - Mocking/stubbing strategies
  - CI/CD test automation

**devon** (v1.0.0) - Project Setup & Bootstrap Specialist (Agent 5) **NEW in v1.3.0**
- **Expertise:** Frontend/backend framework initialization, infrastructure as code (Docker/CI/CD), monorepo architecture, package management, database setup, testing infrastructure, linting/formatting, architectural decision documentation, handoff to specialists
- **Best for:** Initializing new projects (Next.js, React, Express, FastAPI), setting up monorepos (Turborepo, Nx), configuring Docker/GitHub Actions, installing dependencies, creating comprehensive setup documentation, handing off to Ava/Marcus/Quinn
- **System prompt:** ~2,500 lines (20 expertise areas)
- **Specialties:**
  - Next.js, React, Vue, Svelte initialization
  - Express, NestJS, FastAPI, Django setup
  - Docker, docker-compose, GitHub Actions CI/CD
  - Turborepo, Nx monorepo architecture
  - Prisma, Supabase, MongoDB database setup
  - Vitest, Jest, Playwright testing infrastructure

## How It Works

1. Personas are defined in `personas/base/*.json` files
2. Each persona has a system prompt defining expertise and behavior
3. When activated, the persona's system prompt is returned to the AI
4. The AI adopts the persona's knowledge and communication style
5. The persona influences how the AI uses other MCP tools

**Key principle:** Personas are context providers, not tool wrappers. They don't modify other tools - they influence how the AI uses them.

## Project Structure

```
personas-mcp/
├── server.py              # MCP server entry point
├── pyproject.toml         # Python project config
├── personas/
│   └── base/
│       ├── mcp-expert.json           # MCP protocol expert
│       ├── docs-expert.json          # Documentation & planning expert
│       ├── coderef-expert.json       # CodeRef-MCP server building expert
│       ├── nfl-scraper-expert.json   # NFL data scraping expert
│       ├── lloyd-expert.json         # Project coordinator
│       ├── ava.json                  # Frontend specialist (Agent 2)
│       ├── marcus.json               # Backend specialist (Agent 3)
│       ├── quinn.json                # Testing specialist (Agent 4)
│       ├── taylor.json               # General purpose agent
│       └── devon.json                # Setup specialist (Agent 5)
├── src/
│   ├── models.py          # Pydantic schemas (PersonaDefinition)
│   └── persona_manager.py  # Persona loading and activation logic
└── .claude/
    └── commands/
        ├── use-persona.md      # General persona activation
        ├── docs-expert.md      # /docs-expert shortcut
        ├── coderef-expert.md   # /coderef-expert shortcut
        ├── lloyd.md            # /lloyd shortcut
        ├── ava.md              # /ava shortcut
        ├── marcus.md           # /marcus shortcut
        ├── quinn.md            # /quinn shortcut
        ├── taylor.md           # /taylor shortcut
        └── devon.md            # /devon shortcut
```

## Development

### Running Tests
```bash
pytest
```

### Adding a New Persona

1. Create `personas/base/your-persona.json`:
```json
{
  "name": "your-persona",
  "version": "1.0.0",
  "description": "Brief description",
  "system_prompt": "Comprehensive system prompt defining expertise...",
  "expertise": ["Area 1", "Area 2"],
  "use_cases": ["Use case 1", "Use case 2"],
  "behavior": {
    "communication_style": "How this persona communicates",
    "problem_solving": "How this persona approaches problems",
    "tool_usage": "How this persona uses tools"
  },
  "created_at": "2025-10-18",
  "updated_at": "2025-10-18"
}
```

2. Restart the MCP server
3. Use `/use-persona your-persona`

## Future Enhancements

See `coderef/future/claude-20-personas.md` for the complete expansion roadmap.

**Next Milestones:**
- [ ] Expand to 20 personas (mcp-client-expert, mcp-security-expert, code-reviewer-expert, etc.)
- [ ] Persona stacking/composition (combine multiple expertises with add_persona)
- [ ] Persona metadata search (find by expertise, use case)
- [ ] Persona recommendation engine
- [ ] Specialized hierarchical personas (mcp-expert:docs-mcp, etc.)

**Completed:**
- [x] 3 independent base personas (mcp-expert, docs-expert, coderef-expert)
- [x] Comprehensive system prompts (1000-6000+ lines for agentic use)
- [x] Slash command shortcuts

## License

MIT

## Contributing

This is an experimental MCP server. Contributions welcome!

## Version

- **Current:** 1.3.0
- **Status:** Production-ready (10 personas: 4 expert + 1 coordinator (Lloyd) + 4 specialists (Ava/Marcus/Quinn/Devon) + 1 generalist (Taylor))
- **MCP Protocol:** 2024-11-05

### Version History
- **v1.3.0** (2025-10-23): Devon setup specialist persona - Project initialization, infrastructure setup, comprehensive handoff to domain specialists
- **v1.2.0** (2025-10-23): Ava frontend specialist persona (WO-AGENT-SPECIALIZATION-002) - React, CSS, accessibility expertise
- **v1.1.0** (2025-10-20): Multi-agent coordination with Lloyd and 3 generalist execution agents
- **v1.0.0** (2025-10-18): 3 independent base personas, comprehensive system prompts, slash commands
- **v0.1.0** (2025-10-18): Initial MVP with mcp-expert persona
