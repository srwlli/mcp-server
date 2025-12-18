# Claude Code Tools Reference

**Generated:** 2025-12-15
**Total Tools:** ~65 across core functionality and 3 MCP servers

---

## Table of Contents

1. [Core Claude Code Tools](#core-claude-code-tools)
2. [MCP: personas-mcp](#mcp-personas-mcp)
3. [MCP: docs-mcp](#mcp-docs-mcp)
4. [MCP: coderef-mcp](#mcp-coderef-mcp)
5. [MCP Resources](#mcp-resources)

---

## Core Claude Code Tools

Built-in tools available in every Claude Code session.

| Tool | Description |
|------|-------------|
| `Task` | Launch specialized agents (Explore, Plan, general-purpose, claude-code-guide, mvp-architect, coderef-system-expert) |
| `Bash` | Execute shell commands with optional timeout and background execution |
| `Glob` | Fast file pattern matching (e.g., `**/*.js`, `src/**/*.ts`) |
| `Grep` | Content search with full regex syntax, supports multiple output modes |
| `Read` | Read files (text, images, PDFs, Jupyter notebooks) |
| `Edit` | Edit files via exact string replacement |
| `Write` | Create or overwrite files |
| `NotebookEdit` | Edit Jupyter notebook cells |
| `WebFetch` | Fetch and process web content with AI |
| `WebSearch` | Search the web for up-to-date information |
| `TodoWrite` | Create and manage task lists for progress tracking |
| `AskUserQuestion` | Ask user clarifying questions with multiple choice options |
| `EnterPlanMode` | Enter planning mode for complex tasks |
| `ExitPlanMode` | Exit planning mode after plan approval |
| `BashOutput` | Retrieve output from background shell processes |
| `KillShell` | Terminate background shell processes |
| `Skill` | Execute available skills |
| `SlashCommand` | Execute custom slash commands |

### Task Agent Types

| Agent Type | Use Case |
|------------|----------|
| `general-purpose` | Complex multi-step tasks, code search |
| `Explore` | Fast codebase exploration, file/keyword search |
| `Plan` | Design implementation plans |
| `claude-code-guide` | Questions about Claude Code features |
| `mvp-architect` | MVP design and planning |
| `coderef-system-expert` | CodeRef system architecture guidance |

---

## MCP: personas-mcp

Expert persona management system.

| Tool | Description |
|------|-------------|
| `mcp__personas-mcp__use_persona` | Activate an expert persona by name |
| `mcp__personas-mcp__get_active_persona` | Get information about currently active persona |
| `mcp__personas-mcp__clear_persona` | Deactivate current persona, return to default |
| `mcp__personas-mcp__list_personas` | List all available personas with descriptions |
| `mcp__personas-mcp__create_custom_persona` | Create custom persona via guided workflow |
| `mcp__personas-mcp__generate_todo_list` | Convert plan task breakdown to TodoWrite format |
| `mcp__personas-mcp__track_plan_execution` | Sync plan progress with todo status in real-time |
| `mcp__personas-mcp__execute_plan_interactive` | Execute plan with step-by-step or batch mode |

### Available Personas

- `docs-expert` - Documentation and planning specialist
- `mcp-expert` - MCP server development expert
- (Use `list_personas` to see all available)

---

## MCP: docs-mcp

Comprehensive documentation, planning, and project management system (32 tools).

### Documentation Generation (6 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__list_templates` | List all POWER framework templates |
| `mcp__docs-mcp__get_template` | Get specific template content (readme, architecture, api, components, schema, user-guide) |
| `mcp__docs-mcp__generate_foundation_docs` | Generate all 5 foundation documents |
| `mcp__docs-mcp__generate_individual_doc` | Generate single document from template |
| `mcp__docs-mcp__generate_quickref_interactive` | Interactive interview-based quickref generation (150-250 lines) |
| `mcp__docs-mcp__coderef_foundation_docs` | **NEW** Unified foundation docs with auto-detection (replaces 7 inventory tools) |

### Changelog Management (3 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__get_changelog` | Query changelog with filters (version, type, breaking_only) |
| `mcp__docs-mcp__add_changelog_entry` | Add new structured changelog entry |
| `mcp__docs-mcp__update_changelog` | Agentic workflow for changelog updates |

### Standards & Consistency (3 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__establish_standards` | Extract UI/behavior/UX patterns into standards docs |
| `mcp__docs-mcp__audit_codebase` | Full compliance audit with scoring (0-100) |
| `mcp__docs-mcp__check_consistency` | Fast pre-commit check on modified files only |

### Planning Workflow (7 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__get_planning_template` | Get 10-section planning template |
| `mcp__docs-mcp__gather_context` | Interactive requirements gathering with workorder assignment |
| `mcp__docs-mcp__analyze_project_for_planning` | Discover docs, standards, patterns, tech stack |
| `mcp__docs-mcp__create_plan` | Generate complete implementation plan |
| `mcp__docs-mcp__validate_implementation_plan` | Score plan quality (0-100), validate workorder consistency |
| `mcp__docs-mcp__generate_plan_review_report` | Generate markdown review report |
| `mcp__docs-mcp__execute_plan` | Generate TodoWrite task list from plan.json |

### Deliverables Tracking (2 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__generate_deliverables_template` | Generate DELIVERABLES.md from plan.json |
| `mcp__docs-mcp__update_deliverables` | Update deliverables with git metrics (LOC, commits, time) |

### Multi-Agent Coordination (5 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__generate_agent_communication` | Generate communication.json for multi-agent workflows |
| `mcp__docs-mcp__assign_agent_task` | Assign task to agent with workorder scoping |
| `mcp__docs-mcp__verify_agent_completion` | Verify agent completion with automated checks |
| `mcp__docs-mcp__aggregate_agent_deliverables` | Aggregate metrics from multiple agents |
| `mcp__docs-mcp__track_agent_status` | Real-time coordination dashboard |

### Workorder & Archive (4 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__log_workorder` | Log workorder to global activity log |
| `mcp__docs-mcp__get_workorder_log` | Query workorder log with filters |
| `mcp__docs-mcp__archive_feature` | Archive completed features to coderef/archived/ |
| `mcp__docs-mcp__update_all_documentation` | Agentic update of all docs after feature completion |

### Other (2 tools)

| Tool | Description |
|------|-------------|
| `mcp__docs-mcp__generate_handoff_context` | Generate agent handoff context files |
| `mcp__docs-mcp__assess_risk` | AI-powered risk assessment across 5 dimensions |

### Key Workflows

```
New Projects:     /establish-standards → /generate-docs
Features:         /coderef-foundation-docs → /create-workorder → /execute-plan
Maintenance:      /audit-codebase → /check-consistency
Post-Feature:     /update-deliverables → /update-docs → /archive-feature
```

### coderef_foundation_docs Tool

**Purpose:** Unified foundation docs generator that replaces 7 inventory tools.

**Generates:**
- `ARCHITECTURE.md` - Code patterns, API architecture, recent activity
- `SCHEMA.md` - Database tables, relationships, migrations
- `COMPONENTS.md` - UI component hierarchy (auto-detected for UI projects)
- `API.md` - Endpoints, authentication, error handling
- `project-context.json` - Structured context for planning workflows

**Auto-detects:**
- API endpoints (FastAPI, Flask, Express)
- Database schemas (SQLAlchemy models)
- Dependencies (requirements.txt, package.json, pyproject.toml)
- Git activity (commits, active files, contributors)
- Code patterns (handlers, decorators, error types)

**Parameters:**
- `project_path` (required) - Absolute path to project
- `include_components` (optional) - Force COMPONENTS.md generation (default: auto-detect)
- `deep_extraction` (optional) - Extract from existing docs (default: true)
- `use_coderef` (optional) - Use coderef-mcp for patterns (default: true)

---

## MCP: coderef-mcp

Code reference tracking and analysis system.

| Tool | Description |
|------|-------------|
| `mcp__coderef-mcp__mcp__coderef__query` | Query CodeRef elements by reference or pattern |
| `mcp__coderef-mcp__mcp__coderef__analyze` | Deep analysis (impact, coverage, complexity) |
| `mcp__coderef-mcp__mcp__coderef__validate` | Validate CodeRef reference format and structure |
| `mcp__coderef-mcp__mcp__coderef__batch_validate` | Batch validate multiple references (parallel/sequential) |
| `mcp__coderef-mcp__mcp__coderef__generate_docs` | Generate documentation for CodeRef elements |
| `mcp__coderef-mcp__mcp__coderef__audit` | Audit CodeRef elements for validation/coverage/performance |
| `mcp__coderef-mcp__mcp__coderef__nl_query` | Natural language query interface ("what calls login?") |
| `mcp__coderef-mcp__mcp__coderef__scan_realtime` | Scan source code and update index in real-time |

### Analysis Types

- `impact` - Analyze impact of changes
- `deep` - Deep code analysis
- `coverage` - Test coverage analysis
- `complexity` - Code complexity metrics

---

## MCP Resources

Generic MCP resource access tools.

| Tool | Description |
|------|-------------|
| `ListMcpResourcesTool` | List available resources from MCP servers |
| `ReadMcpResourceTool` | Read specific resource by server name and URI |

---

## Quick Reference

### Most Used Tools

| Task | Tool |
|------|------|
| Search for files | `Glob` with pattern |
| Search file contents | `Grep` with regex |
| Read a file | `Read` |
| Edit a file | `Edit` |
| Run a command | `Bash` |
| Track tasks | `TodoWrite` |
| Explore codebase | `Task` with `Explore` agent |
| Generate project context | `mcp__docs-mcp__coderef_foundation_docs` |
| Create implementation plan | `mcp__docs-mcp__create_plan` |
| Activate expert persona | `mcp__personas-mcp__use_persona` |

### Slash Commands

Custom slash commands available via `SlashCommand` tool:

**Persona Activation:**
- `/ava` - Activate Ava (Frontend Specialist)
- `/devon` - Activate Devon (Project Setup Specialist)
- `/taylor` - Activate Taylor (General Purpose Agent)

**docs-mcp Workflows:**
- `/coderef-foundation-docs` - Generate unified foundation docs (ARCHITECTURE, SCHEMA, COMPONENTS)
- `/create-workorder` - Full planning workflow (gather → analyze → plan → validate)
- `/execute-plan` - Generate TodoWrite task list from plan
- `/update-docs` - Update all documentation after feature completion
- `/archive-feature` - Archive completed features

---

## Server Status

Check MCP server health:
```bash
claude mcp list
```

Current servers:
- `docs-mcp` - Documentation tools
- `coderef-mcp` - Code reference tools
- `personas-mcp` - Persona management

---

*Last updated: 2025-12-15 - Added coderef_foundation_docs tool, removed 7 inventory tools (WO-REFINE-CONTEXT-001)*
