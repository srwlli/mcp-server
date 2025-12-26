# coderef-docs - AI Context Documentation

**Project:** coderef-docs (MCP Server)
**Version:** 3.1.0
**Status:** ✅ Production
**Created:** 2024-10-18
**Last Updated:** 2025-12-25

---

## Quick Summary

**coderef-docs** is a focused MCP server providing **11 specialized tools** for documentation generation, changelog management, standards enforcement, and quickref guides. It works with coderef-workflow to deliver end-to-end feature lifecycle documentation.

**Core Innovation:** POWER framework templates + agentic changelog recording with git auto-detection and AI confirmation flow.

**Latest Update (v3.1.0):**
- ✅ Record_changes tool with smart agentic workflow and git integration
- ✅ Standards audit system (establish_standards + audit_codebase + check_consistency)
- ✅ Quickref generation for any application type (CLI, Web, API, Desktop, Library)

**Key Relationships:**
- **coderef-workflow** = Orchestration & planning
- **coderef-context** = Code intelligence (optional integration)

Together they form a complete feature lifecycle: Context → Plan → Code → Documentation → Archive.

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

## Architecture

### Core Responsibility
Generates all project documentation artifacts (README, ARCHITECTURE, SCHEMA, API, COMPONENTS, CHANGELOG, standards guides, quickref). Integrates with coderef-workflow to document completed features and track changes.

### Documentation Domains
```
Foundation Docs → README, ARCHITECTURE, SCHEMA, API, COMPONENTS
Changelog Ops → Get, add, and record changes with git auto-detection
Standards & Compliance → Extract patterns, audit for violations, pre-commit checks
Quickref → Interactive generation for any app type
```

### Key Integration Points
- **Depends on:** coderef-workflow (for feature context), git (for changelog recording)
- **Used by:** AI agents and users for documentation workflows
- **Orchestrated via:** 26 slash commands in `~/.claude/commands/`

---

## Tools Catalog

| Tool | Purpose | Type |
|------|---------|------|
| `list_templates` | Show available POWER framework templates | Utility |
| `get_template` | Get specific template by name | Utility |
| `generate_foundation_docs` | Create README, ARCHITECTURE, SCHEMA, etc. | Generator |
| `generate_individual_doc` | Create single doc from template | Generator |
| `generate_quickref_interactive` | Interactive quickref for any app type ⭐ | Generator |
| `get_changelog` | Query changelog by version/type | Reader |
| `add_changelog_entry` | Manually add changelog entry | Writer |
| `record_changes` | Smart recording with git auto-detection ⭐ | Agentic |
| `establish_standards` | Extract coding standards from codebase | Analyzer |
| `audit_codebase` | Check standards compliance (0-100 score) | Auditor |
| `check_consistency` | Pre-commit gate for staged changes | Auditor |

**Total:** 11 tools across 3 domains (Documentation, Changelog, Standards)

---

## POWER Framework

All documentation uses **POWER** structure for consistency:

- **Purpose** - Why this document exists and what problem it solves
- **Overview** - What's included and scope
- **What/Why/When** - Detailed content with context
- **Examples** - Concrete, working illustrations
- **References** - Links to related documentation

This ensures all generated docs follow the same proven pattern and are immediately recognizable.

---

## File Structure

```
coderef-docs/
├── server.py                      # MCP server entry point (374 lines)
├── tool_handlers.py               # 11 tool handlers (835 lines)
├── generators/
│   ├── foundation_generator.py    # Multi-doc generation
│   ├── changelog_generator.py     # CRUD + schema validation
│   ├── standards_generator.py     # Standards extraction
│   └── audit_generator.py         # Compliance auditing
├── templates/power/               # POWER framework templates
├── README.md                      # User-facing guide
├── CLAUDE.md                      # This file (AI context)
└── .claude/commands/              # 26 slash commands
    ├── /generate-docs
    ├── /generate-quickref
    ├── /record-changes
    └── {22 others}
```

---

## Design Decisions

**1. Separated from coderef-workflow**
- ✅ Chosen: coderef-docs handles docs only
- ❌ Rejected: Combine docs + workflow in single server
- Reason: Single responsibility principle, easier to test and maintain independently

**2. POWER Framework for All Documentation**
- ✅ Chosen: Universal template applied to all doc types
- ❌ Rejected: Custom templates for each doc type
- Reason: Consistency across projects, reduced maintenance, proven effectiveness

**3. Agentic Record_Changes Tool**
- ✅ Chosen: Smart tool with git auto-detection + AI confirmation
- ❌ Rejected: Manual form-based changelog entry
- Reason: Reduces friction for AI agents, captures context automatically, validates before writing

**4. 11 Tools vs 30+**
- ✅ Chosen: Focused toolset (11 core tools)
- ❌ Rejected: Include all inventory tools from v2.0.0
- Reason: v2.0.0 merged with coderef-workflow; docs stays focused on documentation

---

## Integration Guide

### With coderef-workflow
- Workflow creates features and plans → coderef-docs generates documentation
- Tools orchestrated via slash commands (user-friendly entry points)
- Called automatically at feature completion (update_docs, archive_feature)
- DELIVERABLES.md and CHANGELOG tracked across lifecycle

### With coderef-context
- Standards auditing can optionally use coderef patterns for advanced analysis
- Not required; works standalone without coderef-context

---

## Essential Commands

### Development
```bash
# Install & run
uv sync
python server.py

# Run tests
pytest tests/ -v

# Type check
mypy src/
```

### Usage / Slash Commands
```bash
/generate-docs              # Generate foundation docs (README, ARCHITECTURE, etc)
/generate-quickref          # Interactive quickref for any app type
/record-changes             # Smart changelog with git auto-detection
/establish-standards        # Extract coding standards
/audit-codebase            # Check standards compliance (0-100 score)
/check-consistency         # Pre-commit gate for modified files
```

---

## Use Cases

### UC-1: Generate Complete Project Documentation
```
User: /generate-docs
Tool: Analyzes project structure
Claude: Generates and fills POWER templates
Output: README.md, ARCHITECTURE.md, SCHEMA.md, API.md, COMPONENTS.md
All docs follow POWER framework for consistency
```

### UC-2: Record Feature Completion with Smart Changelog
```
User: Completes feature implementation
Tool: /record-changes triggered (or called by coderef-workflow)
Tool: Auto-detects git changes, suggests change_type (feature/bugfix/breaking)
Claude: Reviews suggestion, confirms details
Output: CHANGELOG.json entry with workorder tracking, README version bump
```

---

## Recent Changes

### v3.1.0 - Focused Documentation System
- ✅ Record_changes agentic tool with git auto-detection and AI confirmation
- ✅ Standards establishment and compliance auditing (establish_standards, audit_codebase, check_consistency)
- ✅ Quickref generation for any application type (CLI, Web, API, Desktop, Library)
- 🗑️ Deprecated update_changelog (replaced by agentic record_changes)

### v3.0.0 - Standards & Compliance System
- ✅ Establish_standards tool discovers UI/behavior/UX patterns from codebase
- ✅ Audit_codebase validates compliance with standards (0-100 score)
- ✅ Check_consistency pre-commit gate for staged file changes

---

## Next Steps

- ⏳ REST API wrapper for ChatGPT integration (Unified HTTP Server)
- ⏳ Extended template library for specialized documentation types
- ⏳ Multi-language support for generated docs
- ⏳ Integration with coderef-context for advanced standards analysis

---

## Resources

- **[README.md](README.md)** - User-facing documentation guide
- **[SLASH-COMMANDS-REFERENCE.md](SLASH-COMMANDS-REFERENCE.md)** - Detailed slash command docs (if separate doc exists)
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official MCP protocol
- **[POWER Framework](https://example.com/power-framework)** - Documentation template guide

---

**Maintained by:** willh, Claude Code AI
