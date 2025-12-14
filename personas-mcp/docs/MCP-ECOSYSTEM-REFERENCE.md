# MCP Ecosystem Reference

**Purpose:** Detailed reference documentation for the 3-server MCP ecosystem. Lloyd can query this when detailed tool/workflow information is needed.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP ECOSYSTEM ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │   personas-mcp   │  │    docs-mcp      │  │ coderef-  │ │
│  │   (Identity)     │  │   (Execution)    │  │   mcp     │ │
│  │                  │  │                  │  │ (Analysis)│ │
│  │  • 4 Personas    │  │  • 31 Tools      │  │ • 6 Tools │ │
│  │  • Expertise     │  │  • Workflows     │  │ • Semantic│ │
│  │  • Behavior      │  │  • Planning      │  │   Query   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └─────┬─────┘ │
│           │                     │                   │       │
│           └────────────┬────────┴───────────────────┘       │
│                        │                                    │
│                  AI AGENT LAYER                             │
│         (Claude Code, Lloyd, Specialists)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. personas-mcp (Identity Layer) v1.0.0

**Purpose:** Expert system prompts that influence AI behavior and tool usage.

**Core Innovation:** Personas DON'T wrap tools - they INFLUENCE how AI uses ANY available tools.

### Available Personas

| Persona | Version | Lines | Best For |
|---------|---------|-------|----------|
| mcp-expert | v1.0.0 | ~2,500 | Building MCP servers, protocol compliance |
| docs-expert | v1.0.0 | ~6,000 | Documentation, planning, standards |
| coderef-expert | v1.0.0 | ~5,000 | Code analysis, impact assessment |
| nfl-scraper-expert | v1.2.0 | ~1,500 | next-scraper platform |

### MCP Tools

- `use_persona(name)` - Activate persona
- `get_active_persona()` - Get current persona
- `clear_persona()` - Reset to default
- `list_personas()` - Show available

---

## 2. docs-mcp (Execution Engine) v2.4.0

**Purpose:** The workhorse server for DOING THE WORK. 31 specialized tools across 7 domains.

### Tool Domains

#### Domain 1: Documentation Generation (5 tools)
- `generate_foundation_docs` - POWER framework templates
- `generate_individual_doc` - Single doc generation
- `list_templates` - Available templates
- `get_template` - Template content

#### Domain 2: Changelog Management (3 tools)
- `get_changelog` - Read changelog
- `add_changelog_entry` - Add entry
- `update_changelog` - Meta-tool pattern

#### Domain 3: Consistency Management (3 tools)
- `establish_standards` - Extract patterns from codebase
- `audit_codebase` - Full compliance audit (0-100 score)
- `check_consistency` - Quick pre-commit gate

#### Domain 4: Planning Workflows (5 tools)
- `gather_context` - Capture requirements → context.json
- `analyze_project_for_planning` - Discover patterns → analysis.json
- `create_plan` - Generate 10-section plan → plan.json
- `validate_plan` - Score 0-100, identify issues
- `generate_plan_review_report` - Markdown review

#### Domain 5: Deliverables Tracking (2 tools)
- `generate_deliverables_template` - Auto-created by /create-plan
- `update_deliverables` - Git-based metrics (LOC, commits, time)

#### Domain 6: Multi-Agent Coordination (5 tools)
- `generate_agent_communication` - communication.json from plan
- `assign_agent_task` - Workorder scoping
- `verify_agent_completion` - Automated verification
- `aggregate_agent_deliverables` - Combined metrics
- `track_agent_status` - Real-time dashboard

#### Domain 7: Project Inventory (7 tools)
- `inventory_manifest` - File catalog
- `dependency_inventory` - npm, pip, cargo + OSV security
- `api_inventory` - FastAPI, Flask, Express, GraphQL
- `database_inventory` - PostgreSQL, MySQL, MongoDB, SQLite
- `config_inventory` - JSON, YAML, TOML, INI, ENV
- `test_inventory` - pytest, jest, mocha + coverage
- `documentation_inventory` - Markdown, RST, AsciiDoc

---

## 3. coderef-mcp (Analysis Engine) v1.0.0

**Purpose:** Semantic code analysis via CodeRef references.

### CodeRef Syntax
```
@Type/path/file.ext#element:line{key=value}
```

Examples:
- `@Class/src/auth.py#User` - Class User in auth.py
- `@Function/api/routes.js#login:42` - Function at line 42
- `@Method/models.py#User.validate` - Method in class

### MCP Tools

| Tool | Purpose |
|------|---------|
| `query` | Find elements by reference/pattern |
| `analyze` | Deep analysis (impact, coverage, complexity) |
| `validate` | Reference format validation |
| `batch_validate` | Parallel/sequential batch processing |
| `generate_docs` | Documentation generation |
| `audit` | Validation, coverage, performance audits |

---

## Feature Implementation Workflow (9 Steps)

```
Step 0: Coordinator active (Lloyd)
Step 1: /gather-context          → context.json (WO-{FEATURE}-001)
Step 2: /analyze-for-planning    → analysis.json
Step 3: /create-plan             → plan.json + DELIVERABLES.md
Step 4: /validate-plan           → Score >= 90 to approve
Step 5: Implementation           → Execute tasks
Step 6: /update-deliverables     → Git-based metrics
Step 7: /update-docs             → README, CLAUDE, CHANGELOG
Step 8: /archive-feature         → Move to coderef/archived/
```

### Feature Directory Structure
```
coderef/working/{feature}/
├── context.json           (Step 1)
├── analysis.json          (Step 2)
├── plan.json              (Step 3)
├── DELIVERABLES.md        (Step 3)
└── communication.json     (Optional: multi-agent)
```

---

## Multi-Agent Coordination

### Agent Assignment Matrix

| Domain | Agent | Keywords |
|--------|-------|----------|
| Frontend | Ava | React, CSS, UI, Tailwind, accessibility |
| Backend | Marcus | API, database, auth, SQL, security |
| Testing | Quinn | tests, coverage, TDD, mocks |
| General | Taylor | (any) - balanced code/test/docs |
| Setup | Devon | project init, CI/CD, monorepo |

### When to Use Multi-Agent
- 3+ phases that can run in parallel
- Clear domain boundaries
- Total tasks > 15
- User has multiple Claude sessions

### communication.json Workflow
1. `/generate-agent-communication` - Create from plan
2. `/assign-agent-task` - Assign with scoped workorders
3. Agents work independently (respect forbidden_files)
4. `/verify-agent-completion` - Validate each agent
5. `/aggregate-agent-deliverables` - Combine metrics

---

## Enterprise Patterns

| Pattern | Description |
|---------|-------------|
| ARCH-001 | ErrorResponse factory |
| ARCH-003 | Structured logging |
| ARCH-004/005 | Decorator patterns |
| SEC-001-005 | Security hardening |
| QUA-001-004 | Quality patterns (TypedDict, etc.) |

---

## Context Expert System

### Tools
- `list_context_experts` - See existing experts
- `get_context_expert` - Load full context
- `suggest_context_experts` - Find candidates
- `create_context_expert` - Create new expert
- `update_context_expert` - Refresh after changes
- `activate_context_expert` - Onboard with briefing

### Expert ID Format
`CE-{slug}-NNN` (e.g., CE-server_py-001)

### Integration Points
- During /start-feature: Check for relevant experts
- During /execute-plan: Load expert context for files
- After implementation: Update stale experts
