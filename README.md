# MCP Servers Configuration

Central repository for Model Context Protocol (MCP) server configurations and AI agent personas.

## Overview

This directory contains the complete MCP server ecosystem for Claude Code, providing:
- **Expert AI Personas** via personas-mcp
- **Documentation & Planning Tools** via docs-mcp
- **Semantic Code Analysis** via coderef-mcp
- **IDE Integration** for VS Code/Jupyter
- **Multi-Agent Coordination** workflows

## Quick Start

### View Available Tools
Open `index.html` in your browser for a visual reference of all tools and commands.

### Activate MCP Servers
All servers are configured in `.mcp.json` and should auto-load with Claude Code.

```bash
# List active MCP servers
claude mcp list

# View server details
claude mcp get personas-mcp
```

## Directory Structure

```
.mcp-servers/
├── .claude/                    # Claude Code configuration
│   ├── agents/                 # Agent definitions (mvp-architect, coderef-system-expert)
│   ├── commands/               # Global slash commands (deployed from MCP servers)
│   └── settings.local.json     # Local Claude Code settings
├── coderef-mcp/                # Semantic code reference analysis server
├── docs-mcp/                   # Documentation & planning workflow server
├── personas-mcp/               # Expert AI personas server (10 personas)
├── hello-world-mcp/            # Example MCP server template
├── .mcp.json                   # MCP server configuration
├── index.html                  # Visual quick reference guide
├── my-guide.md                 # Text-based quick reference
├── MCP-CONFIGURATION-GUIDE.md  # MCP setup guide
└── KNOWLEDGE-STRUCTURE-TEMPLATE.md  # Knowledge organization template
```

## Available MCP Servers

### personas-mcp (10 personas)
Expert AI agent personas for specialized tasks:

**Expert Personas (4):**
- `mcp-expert` - MCP Protocol & Server Implementation Expert
- `docs-expert` - Documentation & Planning Specialist
- `coderef-expert` - Code Analysis & Architecture Expert
- `nfl-scraper-expert` - NFL Data Scraping Specialist

**Coordinator (1):**
- `lloyd-expert` - Multi-Agent Coordination & Workorder Management

**Specialists (4):**
- `ava` - Frontend Development Specialist (Agent 2)
- `marcus` - Backend Development Specialist (Agent 3)
- `quinn` - Testing & QA Specialist (Agent 4)
- `devon` - Project Setup & Bootstrap Specialist (Agent 5)

**Generalist (1):**
- `taylor` - General Purpose Implementation Agent

**Tools:** 4 (use_persona, get_active_persona, clear_persona, list_personas)
**Slash Commands:** `/lloyd`, `/ava`, `/marcus`, `/quinn`, `/devon`, `/taylor`, `/use-persona`, `/docs-expert`, `/coderef-expert`, `/nfl-scraper-expert`

### docs-mcp (39 slash commands)
Comprehensive documentation and planning workflow tools:

- **Documentation Generation:** Foundation docs, user guides, quickrefs
- **Changelog Management:** Auto-update with version bumping
- **Standards & Consistency:** Extract and enforce codebase patterns
- **Planning & Validation:** Feature planning with workorder tracking
- **Project Inventory:** Dependencies, APIs, databases, configs, tests
- **Multi-Agent Coordination:** Parallel agent workflows with communication.json
- **Deliverables Tracking:** Git metrics (LOC, commits, time)
- **Workorder Logging:** Global activity tracking

**Tools:** 36
**Slash Commands:** 39 (see `/list-templates` for full list)

### coderef-mcp (6 tools)
Semantic code reference system for deep code analysis:

- Query elements by CodeRef patterns
- Deep impact analysis (dependencies, usage)
- Batch validation for multiple references
- Documentation generation from code
- Coverage and complexity audits

**Tools:** 6 (query, analyze, validate, batch_validate, generate_docs, audit)
**Slash Commands:** `/coderef-query`, `/coderef-analyze`, `/coderef-validate`, `/coderef-batch-validate`, `/coderef-docs`, `/coderef-audit`

### ide (2 tools)
VS Code and Jupyter notebook integration:

- `getDiagnostics` - Language server diagnostics
- `executeCode` - Python code execution in Jupyter kernels

## Configuration Files

### .mcp.json
Main MCP server configuration. Defines which servers are active and their settings.

### .claude/settings.local.json
Claude Code local settings including:
- Auto-run tools configuration
- Hook settings
- User preferences

### .claude/commands/
Global slash commands directory. Commands here are available across all projects.

## Usage

### Activating Personas
```bash
# Using slash commands
/lloyd              # Activate Lloyd coordinator
/ava                # Activate Ava (Frontend)
/devon              # Activate Devon (Project Setup)

# Using MCP tools
mcp__personas-mcp__use_persona(name: "lloyd-expert")
```

### Documentation Workflows
```bash
/gather-context     # Start feature planning
/create-plan        # Generate implementation plan
/execute-plan       # Convert plan to TodoWrite tasks
/update-deliverables # Track git metrics
/update-docs        # Update README, CLAUDE, CHANGELOG
/archive-feature    # Archive completed features
```

### Multi-Agent Workflows
```bash
/generate-agent-communication  # Generate communication.json
/assign-agent-task            # Assign work to specific agent
/verify-agent-completion      # Verify agent deliverables
/track-agent-status           # Real-time coordination dashboard
```

## Documentation

- **Quick Reference:** `index.html` (visual) or `my-guide.md` (text)
- **MCP Configuration:** `MCP-CONFIGURATION-GUIDE.md`
- **Knowledge Structure:** `KNOWLEDGE-STRUCTURE-TEMPLATE.md`
- **Server-Specific Docs:**
  - `personas-mcp/README.md` - Persona system documentation
  - `docs-mcp/README.md` - Documentation tools guide
  - `coderef-mcp/README.md` - Code reference system guide

## Stats

- **Total MCP Tools:** 48 (4 personas + 36 docs + 6 coderef + 2 ide)
- **Total Slash Commands:** 55+ (10 personas + 39 docs + 6 coderef)
- **Active Personas:** 10 (4 expert + 1 coordinator + 4 specialists + 1 generalist)
- **Active MCP Servers:** 5 (personas, docs, coderef, hello-world, ide)

## Contributing

When adding new personas or tools:

1. Update server-specific documentation (README.md, CLAUDE.md)
2. Deploy slash commands to `.claude/commands/` for global availability
3. Update `index.html` and `my-guide.md` quick references
4. Bump version numbers in CLAUDE.md
5. Commit with proper workorder tracking

## Version History

- **v1.3.0** (2025-10-23) - Added Devon persona (Project Setup Specialist)
- **v1.2.0** (2025-10-23) - Added Ava, Marcus, Quinn, Taylor specialists
- **v1.1.0** (2025-10-19) - Added Lloyd coordinator persona
- **v1.0.0** (2025-10-19) - Initial MCP server configuration

## Links

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [personas-mcp Repository](./personas-mcp)
- [docs-mcp Repository](./docs-mcp)
- [coderef-mcp Repository](./coderef-mcp)
