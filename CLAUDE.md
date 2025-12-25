# CodeRef Ecosystem - AI Context Documentation

**Project:** CodeRef Ecosystem (4-Server MCP System)
**Version:** 1.0.0
**Status:** ✅ Production
**Created:** 2025-12-25
**Last Updated:** 2025-12-25

---

## Quick Summary

**CodeRef Ecosystem** is an integrated system of 4 MCP servers that enables AI agents to plan, understand, implement, and document software features with complete code context and dependency awareness.

**Core Innovation:** Solves the "agent blind coding" problem by combining code intelligence (coderef-context), structured planning (coderef-workflow), expert personas (coderef-personas), and documentation automation (coderef-docs).

**Latest Update (v1.0.0):**
- ✅ Universal CLAUDEMD-TEMPLATE.json for consistent documentation
- ✅ Simplified /stub command (2 prompts, centralized backlog)
- ✅ Refactored coderef-docs/CLAUDE.md (93% reduction: 3,250 → 227 lines)
- ✅ Updated Lloyd persona for workorder-centric architecture

**Key Relationships:**
- **coderef-context** = Code intelligence (dependency graph, impact analysis)
- **coderef-workflow** = Planning & orchestration (10-section plans)
- **coderef-docs** = Documentation (POWER framework templates)
- **coderef-personas** = Expert agents (9 domain specialists)

Together they form a complete feature lifecycle: Context → Plan → Code (with intelligence) → Documentation → Archive.

---

## System Architecture

### How It Works

```
Feature Idea
    ↓
coderef-workflow (/create-workorder)
├─ Gathers requirements & constraints
├─ Analyzes project (code intelligence from coderef-context)
├─ Creates 10-section implementation plan
└─ Validates quality (0-100 score)
    ↓
Agent + Personas (/execute-plan)
├─ Activates domain expert (Ava for frontend, Marcus for backend, etc)
├─ Implements tasks with code context
├─ Calls coderef-context for dependencies & impact
└─ Updates DELIVERABLES.md with progress
    ↓
coderef-docs (/record-changes)
├─ Auto-detects git changes
├─ Updates CHANGELOG.json with workorder tracking
├─ Generates foundation docs (README, ARCHITECTURE, SCHEMA)
└─ Archives completed features
    ↓
Complete, documented, tested feature
```

### The 4 MCP Servers

| Server | Purpose | Key Tools | Status |
|--------|---------|-----------|--------|
| **coderef-context** | Code Intelligence | scan, query, impact, complexity, patterns, drift | ✅ Production (wraps @coderef/core) |
| **coderef-workflow** | Planning & Orchestration | gather_context, create_plan, execute_plan, verify_agent, archive | ✅ Production (v1.1.0 workorder-centric) |
| **coderef-docs** | Documentation | generate_docs, record_changes, establish_standards, audit | ✅ Production (POWER framework) |
| **coderef-personas** | Expert Agents | use_persona, create_custom_persona (9 personas) | ✅ Production |

---

## Complete Feature Lifecycle

### Phase 1: PLAN (5-10 min)
```
/create-workorder
├─ Gather context (interactive Q&A)
├─ Analyze project (coderef-context provides code intelligence)
├─ Create plan (10-section JSON with tasks)
└─ Validate (score >= 90 recommended)

Output: coderef/workorder/{feature}/plan.json
```

### Phase 2: EXECUTE (1-8 hours)
```
/execute-plan
├─ Generate TodoWrite task list
├─ Activate expert persona (Ava, Marcus, Quinn, etc)
├─ Implement tasks with full code context
├─ Update task status as work completes
└─ Capture metrics in DELIVERABLES.md

Output: Code implementation + progress tracking
```

### Phase 3: DOCUMENT (2-5 min)
```
/update-deliverables → /record-changes → /update-docs
├─ Capture git metrics (LOC, commits, time)
├─ Auto-detect changes, update CHANGELOG
├─ Bump version, update README
└─ Generate foundation docs if needed

Output: Updated CHANGELOG.json, README, CLAUDE.md
```

### Phase 4: ARCHIVE (1 min)
```
/archive-feature
├─ Move feature to coderef/archived/
├─ Update archive index
└─ Feature available for reference/recovery

Output: Completed feature in historical archive
```

---

## Key Concepts

### Workorder System
**Format:** `WO-{FEATURE}-{CATEGORY}-###`

Example: `WO-AUTH-SYSTEM-001`
- Tracked in `coderef/workorder-log.txt` (global audit trail)
- Stored in plan.json META_DOCUMENTATION
- Enables multi-agent coordination with unique IDs per agent

### Plan.json Structure (10 Sections)
1. **META_DOCUMENTATION** - Metadata (version, workorder_id, status)
2. **0_PREPARATION** - Discovery and analysis
3. **1_EXECUTIVE_SUMMARY** - What & why (3-5 bullets)
4. **2_RISK_ASSESSMENT** - Breaking changes, security, performance
5. **3_CURRENT_STATE_ANALYSIS** - Existing architecture & patterns
6. **4_KEY_FEATURES** - Must-have requirements
7. **5_TASK_ID_SYSTEM** - Task naming conventions
8. **6_IMPLEMENTATION_PHASES** - Phased breakdown with dependencies
9. **7_TESTING_STRATEGY** - Unit, integration, e2e tests
10. **8_SUCCESS_CRITERIA** - How to verify completion

### POWER Framework
All documentation uses **POWER** for consistency:
- **Purpose** - Why this exists
- **Overview** - What it covers
- **What/Why/When** - Detailed content & context
- **Examples** - Concrete illustrations
- **References** - Links to related docs

---

## File Structure

```
C:\Users\willh\.mcp-servers/
├── coderef-context/                    # Code Intelligence (Python)
│   ├── server.py                       # MCP server
│   ├── src/                            # Wraps @coderef/core CLI
│   └── README.md
├── coderef-workflow/                   # Planning & Orchestration (Python)
│   ├── server.py                       # MCP server
│   ├── generators/                     # plan.json, analysis generation
│   ├── .claude/commands/               # 26 slash commands
│   └── CLAUDE.md                       # Architecture
├── coderef-docs/                       # Documentation (Python)
│   ├── server.py                       # MCP server
│   ├── generators/                     # doc generation
│   ├── templates/power/                # POWER framework
│   ├── .claude/commands/               # 26 slash commands
│   └── CLAUDE.md                       # (refactored to 227 lines)
├── coderef-personas/                   # Expert Personas (Python)
│   ├── server.py                       # MCP server
│   ├── personas/base/                  # 9 domain experts
│   ├── .claude/commands/               # Persona commands
│   └── CLAUDE.md
├── CLAUDEMD-TEMPLATE.json              # Universal doc template (v1.0.0)
├── CLAUDE.md                           # This file (ecosystem overview)
├── README.md                           # User-facing ecosystem guide
├── coderef/                            # Global artifacts
│   ├── workorder/                      # Active features
│   ├── archived/                       # Completed features
│   └── workorder-log.txt               # Audit trail
└── .mcp.json                           # MCP configuration
```

---

## Design Decisions

**1. Four Separate Servers vs Monolith**
- ✅ Chosen: 4 focused MCP servers (context, workflow, docs, personas)
- ❌ Rejected: Single monolithic server
- Reason: Separation of concerns, easier testing, independent scaling, clearer responsibilities

**2. Workorder-Centric Architecture**
- ✅ Chosen: WO-{FEATURE}-{CATEGORY}-### format with global audit trail
- ❌ Rejected: Simple feature naming without tracking
- Reason: Complete audit trail, multi-agent coordination, feature lifecycle tracking

**3. Universal CLAUDE.md Template**
- ✅ Chosen: 15-section template (530-600 lines per server)
- ❌ Rejected: Custom formats per server
- Reason: Consistency, easier onboarding, lean documentation (no bloat)

**4. Centralized Stub Backlog**
- ✅ Chosen: Single C:\Users\willh\Desktop\assistant\coderef\working\ location
- ❌ Rejected: Per-project stubs
- Reason: Global idea backlog, easier browsing, works from any project

---

## Integration Guide

### With External Systems
- **@coderef/core** (TypeScript) - External analysis engine
  - coderef-context wraps its CLI
  - Provides AST-based dependency graphs, impact analysis
  - Requires: C:/Users/willh/Desktop/projects/coderef-system/packages/cli

- **Git Repository** - Source of truth for code
  - DELIVERABLES tracks commits, LOC, time
  - CHANGELOG auto-detects diffs
  - Archive maintains git history

### Between Servers
- **coderef-workflow → coderef-context** - For code intelligence during planning
- **coderef-workflow → coderef-docs** - For foundation doc generation
- **coderef-personas ← all servers** - For agent expertise injection
- **coderef-docs ← Agent** - For documentation at feature completion

---

## Essential Commands

### Development
```bash
# Test all 4 servers
cd C:\Users\willh\.mcp-servers
python -m coderef-context.server           # Start coderef-context
python -m coderef-workflow.server          # Start coderef-workflow
python -m coderef-docs.server              # Start coderef-docs
python -m coderef-personas.server          # Start coderef-personas

# Verify MCP configuration
cat ~/.mcp.json                            # Check configuration
```

### Usage (Main Workflows)
```bash
/stub                          # Capture quick idea (2 prompts)
/create-workorder              # Full planning workflow
/execute-plan                  # Generate & track execution
/record-changes                # Auto-detect & record changes
/generate-docs                 # Create foundation docs
/archive-feature               # Move to archive
```

---

## Use Cases

### UC-1: Plan & Implement a New Feature
```
User: /create-workorder
      → Feature: "dark-mode-toggle"
      → Gathers context, analyzes project, creates plan
      ↓
Agent: /execute-plan
       → Works through tasks using Ava (frontend specialist)
       → Calls coderef-context for CSS/component patterns
       ↓
User: /update-deliverables → /record-changes → /archive-feature
      → Captures metrics, updates CHANGELOG, archives
```

### UC-2: Multi-Agent Feature Implementation
```
User: /create-workorder
      → Creates plan with 3 parallel phases
      ↓
Lloyd (Coordinator): /generate-agent-communication
                     → Creates communication.json for agents
                     ↓
Agent 1 (Ava): /assign-agent-task → Works on frontend
Agent 2 (Marcus): /assign-agent-task → Works on backend
Agent 3 (Quinn): /assign-agent-task → Works on tests
                     ↓
Lloyd: /verify-agent-completion → Validates all agents
       ↓
/aggregate-agent-deliverables → Combines metrics
/archive-feature → Complete
```

### UC-3: Refactoring with Impact Analysis
```
Agent: "I want to rename this function"
       ↓
coderef-context: /coderef_impact
                 ↓ Returns: "12 files depend on this, here's the ripple"
                 ↓
Agent: "Now I know what breaks. Here's my implementation plan."
       ↓ Safe refactoring with full context
```

---

## Recent Changes

### v1.0.0 - Complete Ecosystem Release
- ✅ Universal CLAUDEMD-TEMPLATE.json (15-section template, 530-600 lines)
- ✅ Refactored coderef-docs/CLAUDE.md (3,250 → 227 lines, 93% reduction)
- ✅ Simplified /stub command (4 prompts → 2 prompts, centralized backlog)
- ✅ Updated Lloyd persona (v1.4.0 aligned with workorder-centric architecture)
- ✅ Created comprehensive ecosystem README.md

### Previous: v0.9.0 - Workorder System Implementation
- ✅ WO-WORKFLOW-REFACTOR-001 (16/16 tasks complete)
- ✅ Implemented workorder_id tracking throughout
- ✅ Path migration: coderef/working/ → coderef/workorder/
- ✅ Bug fixes: deliverables type checking, plan status lifecycle

---

## Next Steps

- ⏳ Refactor remaining CLAUDE.md files (coderef-context, coderef-workflow)
- ⏳ REST API wrapper for ChatGPT integration
- ⏳ Extended template library for specialized docs
- ⏳ Performance optimizations for large codebases
- ⏳ Enhanced semantic search (RAG integration)

---

## Resources

- **[README.md](README.md)** - User-facing ecosystem overview
- **[CLAUDEMD-TEMPLATE.json](CLAUDEMD-TEMPLATE.json)** - Universal doc template (v1.0.0)
- **[coderef-context/README.md](coderef-context/README.md)** - Code intelligence
- **[coderef-workflow/CLAUDE.md](coderef-workflow/CLAUDE.md)** - Planning architecture
- **[coderef-docs/CLAUDE.md](coderef-docs/CLAUDE.md)** - Documentation system
- **[coderef-personas/CLAUDE.md](coderef-personas/CLAUDE.md)** - Persona system

---

**Maintained by:** willh, Claude Code AI

**System Status:** ✅ Production Ready - All 4 servers operational, workorder-centric architecture fully integrated, complete feature lifecycle tested
