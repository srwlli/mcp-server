# personas-mcp Quick Reference

**Project:** Expert agent personas for AI assistants via MCP
**Version:** 1.5.0

---

## MCP Tools

### Persona Management
- **use_persona** - Activate an expert persona (e.g., 'mcp-expert', 'mcp-expert:coderef')
- **get_active_persona** - Show currently active persona and expertise
- **clear_persona** - Deactivate current persona, return to default behavior
- **list_personas** - List all available personas with descriptions

---

## Slash Commands

### Persona Shortcuts
- **/use-persona <name>** - Activate a persona
- **/coderef-mcp-lead** - Quick activation of Lead System Architect
- **/lloyd** - Quick activation of Lloyd project coordinator
- **/ava** - Quick activation of Ava, the Frontend Specialist
- **/marcus** - Quick activation of Marcus, the Backend Specialist
- **/quinn** - Quick activation of Quinn, the Testing Specialist
- **/taylor** - Quick activation of Taylor, the General Purpose Agent

---

## Available Personas

### Base Personas
- **mcp-expert** (v1.0.0)
  - MCP protocol specification and architecture
  - Server implementation patterns (Python SDK, async handlers)
  - Tool design best practices and composability
  - JSON-RPC 2.0 communication and error handling

- **coderef-mcp-lead** (v1.1.0)
  - Lead system architect for all 5 MCP servers (context, workflow, docs, personas, testing)
  - MCP server architecture and Python SDK patterns
  - Tool interaction flows and cross-server dependencies
  - Global deployment architecture and workorder-centric workflow
  - Server communication via JSON-RPC 2.0
  - Integration testing and troubleshooting across servers
  - System-level analysis and optimization
  - Slash command: /coderef-mcp-lead

- **lloyd** (v1.5.0)
  - Project coordinator and technical leader (Scrum Master + Tech Lead)
  - Orchestrates complete 11-step `/create-workorder` workflow
  - Foundation docs generation, plan validation, task alignment
  - Task decomposition and progress tracking (TodoWrite)
  - Uses docs-mcp and coderef-mcp tools for planning and analysis
  - Coordinates multi-agent execution with communication.json protocol
  - Pre-execution git checkpoints for approved plans

### Multi-Agent Execution Agents (v1.2.0)

- **ava** (v1.0.0) - Frontend Specialist (Agent 2)
  - UI development with React (functional components, hooks, Context API)
  - Modern CSS architecture (Tailwind, CSS Modules, Styled-components)
  - Accessibility expertise (WCAG 2.1 Level AA compliance)
  - Responsive design and mobile-first development
  - Component design patterns (Atomic Design, compound components)
  - State management (Context API, Redux, Zustand, React Query)
  - UI testing with React Testing Library
  - Performance optimization (memoization, code splitting)
  - Forms and validation (React Hook Form, Zod)
  - Design systems and component libraries
  - Works with Lloyd via communication.json protocol for frontend tasks

- **marcus** (v1.0.0) - Backend Specialist (Agent 3)
  - RESTful API design and implementation (resource modeling, HTTP methods, status codes)
  - GraphQL API design and schema modeling (queries, mutations, resolvers, DataLoader)
  - SQL database design (PostgreSQL, MySQL) - normalization, foreign keys, indexes
  - NoSQL database design (MongoDB, Redis) - document modeling, aggregations
  - Authentication systems (JWT, OAuth 2.0, session-based) - bcrypt, token rotation
  - Authorization patterns (RBAC, ABAC) - roles, permissions, access control
  - Data validation and sanitization (Joi, Zod)
  - Error handling patterns and centralized error handlers
  - Security best practices (OWASP Top 10) - SQL injection, XSS, CSRF protection
  - API documentation (OpenAPI/Swagger)
  - Background job processing (Bull, BeeQueue) with Redis
  - Caching strategies (Redis, in-memory)
  - Database migrations and ORM patterns (Sequelize, TypeORM, Prisma, Mongoose)
  - Query optimization and indexing
  - Rate limiting, CORS, security headers (helmet.js)
  - Works with Lloyd via communication.json protocol for backend workorders

- **quinn** (v1.0.0) - Testing Specialist (Agent 4)
  - Unit testing (Jest, pytest, JUnit, RSpec)
  - Integration testing (Supertest, pytest fixtures, Testcontainers)
  - Test-Driven Development (TDD) - Red-Green-Refactor cycle
  - E2E testing (Playwright, Cypress, Selenium, Puppeteer)
  - Test coverage analysis (80-90%+ targets with Jest --coverage, pytest-cov)
  - Mocking and stubbing (jest.mock, sinon, unittest.mock, Mockito)
  - Debugging and troubleshooting (Chrome DevTools, pdb, VS Code debugger)
  - QA workflows and test planning
  - Test automation and CI/CD integration (GitHub Actions, GitLab CI, Jenkins)
  - Performance and load testing (k6, Artillery, JMeter, Locust)
  - Works with Lloyd via communication.json protocol for testing assignments
  - Reports test results with detailed metrics (tests passing, coverage %, execution time)

- **taylor** (v1.2.0) - General Purpose Agent
  - Generalist execution agent with balanced code, test, and docs capabilities
  - Multi-agent coordination via communication.json protocol
  - Code implementation following project patterns
  - Unit and integration testing
  - API documentation and technical writing
  - CHANGELOG management and git workflow
  - Precise step execution from workorder assignments
  - Boundary respect (forbidden files, allowed files)
  - Status updates and progress reporting
  - Error handling and blocker reporting
  - Debugging and troubleshooting across the stack
  - Pattern recognition and code consistency
  - Works with Lloyd via communication.json protocol for any type of workorder
  - Can handle code, tests, docs, or other work as assigned

---

## Quick Workflows

### Activate Expert Persona
```
/use-persona mcp-expert
/coderef-mcp-lead
/lloyd
/ava
/marcus
/quinn
/taylor
```

### Check Active Persona
```
Call: get_active_persona tool
Shows: Current expertise and activation time
```

### Return to Default
```
Call: clear_persona tool
Deactivates current persona
```

---

## Architecture

**Persona Structure:**
- `personas/base/` - Independent base persona (mcp-expert)
- `personas/custom/` - Specialist personas (lloyd, ava, marcus, quinn, taylor, research-scout)
- All personas are standalone - no hierarchical dependencies

**Server Components:**
- `server.py` - MCP server entry point
- `src/persona_manager.py` - Persona loading and activation
- `src/models.py` - Pydantic schemas for validation

---

## File Locations

- Personas: `personas/base/*.json`
- Slash commands: `.claude/commands/*.md`
- Server: `server.py`
- Models: `src/models.py`, `src/persona_manager.py`

---

**Last Updated:** 2025-12-28
