# CodeRef Ecosystem - AI Context Documentation

**Project:** CodeRef Ecosystem (5-Server MCP System)
**Version:** 1.0.0
**Status:** ✅ Production
**Created:** 2025-12-25
**Last Updated:** 2025-12-28

---

## Quick Summary

**CodeRef Ecosystem** is an integrated system of 5 MCP servers that enables AI agents to plan, understand, implement, test, and document software features with complete code context and dependency awareness.

**Core Innovation:** Solves the "agent blind coding" problem by combining code intelligence (coderef-context), structured planning (coderef-workflow), expert personas (coderef-personas), documentation automation (coderef-docs), and test automation (coderef-testing).

**Latest Update (v1.1.0):**
- ✅ Enhanced /stub command with optional conversation context capture
- ✅ Smart context extraction from conversation history
- ✅ Conditional JSON field (context included only when relevant discussion exists)
- ✅ Complete implementation guide (STUB_COMMAND_IMPLEMENTATION_GUIDE.md)

**Key Relationships:**
- **coderef-context** = Code intelligence (dependency graph, impact analysis)
- **coderef-workflow** = Planning & orchestration (10-section plans)
- **coderef-docs** = Documentation (POWER framework templates)
- **coderef-personas** = Expert agents (9 domain specialists)
- **coderef-testing** = Test automation (pytest integration, coverage, reporting)

Together they form a complete feature lifecycle: Context → Plan → Code (with intelligence) → Test → Documentation → Archive.

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

### The 5 MCP Servers

| Server | Purpose | Key Tools | Status |
|--------|---------|-----------|--------|
| **coderef-context** | Code Intelligence | scan, query, impact, complexity, patterns, tag, drift | ✅ Production (wraps @coderef/core) |
| **coderef-workflow** | Planning & Orchestration | gather_context, create_plan, execute_plan, verify_agent, archive | ✅ Production (v1.1.0 workorder-centric) |
| **coderef-docs** | Documentation | generate_docs, record_changes, establish_standards, audit | ✅ Production (POWER framework) |
| **coderef-personas** | Expert Agents | use_persona, create_custom_persona (9 personas) | ✅ Production |
| **coderef-testing** | Test Automation | run_tests, test_coverage, test_health, discover_tests | ✅ Production (pytest integration) |

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
├── coderef-testing/                    # Test Automation (Python)
│   ├── server.py                       # MCP server
│   ├── pytest_runner.py                # pytest integration
│   ├── .claude/commands/               # Test commands
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

## Using .coderef/ Structure (Agent Workflow)

### Overview

The universal `.coderef/` structure provides agents with static code intelligence files and dynamic MCP tools for understanding and modifying projects. All 6 MCP servers now have complete `.coderef/` directories with 16 output types.

### Step 1: Generate Structure (One-Time Setup)

```bash
# Complete structure (all 16 outputs, ~30-60 seconds)
python scripts/populate-coderef.py /path/to/project

# Quick foundation only (2 files, ~5-10 seconds)
./scripts/scan-all.py /path/to/project

# Example for MCP server:
python scripts/populate-coderef.py C:/Users/willh/.mcp-servers/coderef-workflow
```

**Output:** Creates `.coderef/` with:
- 4 root files (index.json, graph.json, context.json, context.md)
- 5 reports (patterns, coverage, validation, drift, complexity)
- 4 diagrams (dependencies, calls, imports)
- 3 exports (graph.json, graph.jsonld, diagram-wrapped.md)

### Step 2: Agent Reads Files (During Tasks)

#### For Understanding Project Structure:
```python
# Read foundation scan
index = json.loads(read_file("project/.coderef/index.json"))
# Returns: Array of all functions, classes, components with locations

# Example: "What components exist?"
components = [e for e in index if e["type"] == "component"]
```

#### For Planning Features:
```python
# Read existing patterns (reuse vs rebuild decision)
patterns = json.loads(read_file("project/.coderef/reports/patterns.json"))
# Returns: Existing code patterns to follow

# Read architecture context
context = read_file("project/.coderef/context.md")
# Returns: Human-readable project overview
```

#### For Impact Analysis (Use MCP Tools, Not Files):
```python
# Real-time analysis (doesn't read files, runs fresh scan)
result = await call_tool("coderef_context", "coderef_impact", {
    "project_path": "/path/to/project",
    "element": "AuthService",
    "operation": "refactor"
})
# Returns: What breaks if I change this element
```

#### For Documentation:
```python
# Embed diagrams in README/ARCHITECTURE.md
diagram = read_file("project/.coderef/diagrams/dependencies.mmd")
wrapped = read_file("project/.coderef/exports/diagram-wrapped.md")
```

### Step 3: When to Re-Generate

**Re-run populate-coderef.py when:**
- Major code changes (new files, renamed modules, refactoring)
- Before planning workflows (`/create-workorder`)
- After completing features (for updated documentation)
- When drift detected (see check below)

**Check if refresh needed:**
```bash
# Check drift (compares index vs current code)
coderef drift /path/to/project --json -i .coderef/index.json

# If drift > 10%, re-generate:
python scripts/populate-coderef.py /path/to/project
```

### File-to-Use-Case Mapping

| Agent Task | Read These Files | Call These MCP Tools |
|------------|------------------|---------------------|
| **"What exists?"** | `index.json` | `coderef_scan` (for fresh data) |
| **"Plan feature"** | `context.md`, `patterns.json` | `coderef_patterns` |
| **"Refactor safely"** | - | `coderef_impact`, `coderef_query` |
| **"Document architecture"** | `diagrams/*.mmd`, `exports/diagram-wrapped.md` | - |
| **"Find similar code"** | `patterns.json` | `coderef_patterns` |
| **"Check coverage"** | `reports/coverage.json` | `coderef_coverage` |

### Integration Examples

#### Example 1: Planning Workflow (Already Integrated!)
```python
# coderef-workflow/generators/planning_analyzer.py

# Line 215: Read index for inventory
index_data = json.loads(Path(project_path / ".coderef/index.json").read_text())

# Line 397: Call MCP tool for reference components
result = await call_coderef_tool("coderef_query", {
    "query_type": "depends-on-me",
    "target": component_name
})

# Line 445: Read patterns for conventions
patterns = json.loads(Path(project_path / ".coderef/reports/patterns.json").read_text())
```

#### Example 2: Agent Implementing Feature
```python
# Task: "Add dark mode toggle"

# Step 1: Check what exists
index = json.loads(read_file(".coderef/index.json"))
theme_components = [e for e in index if "theme" in e["name"].lower()]
# Finds: ThemeProvider, useTheme, ThemeContext exist

# Step 2: Understand patterns
patterns = json.loads(read_file(".coderef/reports/patterns.json"))
# Finds: React hooks pattern used 23 times → follow convention

# Step 3: Check dependencies
await call_tool("coderef_context", "coderef_query", {
    "query_type": "imports",
    "target": "ThemeProvider"
})
# Returns: 3 files import ThemeProvider

# Step 4: Implement extending existing theme system (not rebuilding)
```

#### Example 3: Documentation Update
```python
# Task: "Update ARCHITECTURE.md with dependency diagram"

# Read wrapped diagram (includes usage notes)
diagram = read_file(".coderef/exports/diagram-wrapped.md")

# Embed in ARCHITECTURE.md
architecture = f"""
# Architecture

{diagram}

## Key Components
...
"""
```

### Quick Reference

```bash
# Generate everything (run once per project)
python scripts/populate-coderef.py /path/to/project

# Quick scan (foundation only, faster)
./scripts/scan-all.py /path/to/project

# Check if stale
coderef drift /path/to/project --json -i .coderef/index.json

# Re-generate if needed
python scripts/populate-coderef.py /path/to/project
```

### Key Principles

1. **Files are static context** - Use for quick lookups during implementation
2. **MCP tools are dynamic analysis** - Use for real-time dependency/impact checks
3. **Re-generate after major changes** - Keep index fresh for accurate data
4. **Read, don't modify** - `.coderef/` is generated, never hand-edited

### Documentation

- **Complete Reference:** `scripts/README-CODEREF-STRUCTURE.md` (500+ lines)
- **All 16 Output Types:** Detailed descriptions, use cases, examples
- **Completion Report:** `scripts/WORKORDER-COMPLETION-SUMMARY.md`

---

## Essential Commands

### Development
```bash
# Test all 5 servers
cd C:\Users\willh\.mcp-servers
python -m coderef-context.server           # Start coderef-context
python -m coderef-workflow.server          # Start coderef-workflow
python -m coderef-docs.server              # Start coderef-docs
python -m coderef-personas.server          # Start coderef-personas
python -m coderef-testing.server           # Start coderef-testing

# Verify MCP configuration
cat ~/.mcp.json                            # Check configuration
```

### Usage (Main Workflows)
```bash
/stub                          # Capture quick idea + optional conversation context
/create-workorder              # Full planning workflow
/align-plan                    # Align plan with todo list for tracking
/run-tests                     # Run test suite with coverage
/record-changes                # Auto-detect & record changes
/generate-docs                 # Create foundation docs
/archive-feature               # Move to archive
```

---

## Troubleshooting: MCP Cache Issues

### Problem: Duplicate Commands in Autocomplete

**Symptoms:**
- `/create-plan` appears multiple times in autocomplete (labeled as both "(user)" and "(project)")
- `/get-planning-template` appears multiple times
- Duplicate tool references after deleting local command files

**Root Cause:**
Claude Code caches MCP tool and command definitions in `mcp-cache.json`. When you delete local commands or modify server configurations, the cache becomes stale and shows old/duplicate references.

### Solution: Clear MCP Cache

**Step 1: Locate the cache file**

The MCP cache is stored in Claude Code's project-specific cache directory. Find it at:

```
C:\Users\{USERNAME}\.cursor\projects\{PROJECT_ID}\mcp-cache.json
```

**The PROJECT_ID is a hash based on your project folder name.** For the CodeRef ecosystem:

```
C:\Users\willh\.cursor\projects\c-Users-willh-Desktop-projects-current-location-coderef-system\mcp-cache.json
```

**Step 2: Delete the cache file**

```bash
# Windows
del "C:\Users\willh\.cursor\projects\c-Users-willh-Desktop-projects-current-location-coderef-system\mcp-cache.json"

# or use Bash
rm "C:\Users\willh\.cursor\projects\c-Users-willh-Desktop-projects-current-location-coderef-system\mcp-cache.json"
```

**Step 3: Restart Claude Code**

- Close Claude Code completely
- Reopen Claude Code
- Claude Code will automatically rebuild `mcp-cache.json` with current server definitions

**Result:**
- ✅ Duplicate commands disappear
- ✅ All 5 servers (coderef-context, coderef-docs, coderef-personas, coderef-workflow, coderef-testing) refresh
- ✅ Global commands from `~/.claude/commands/` load cleanly
- ✅ No stale references

### Important Notes

**Single Cache for All Servers:**
The `mcp-cache.json` file contains cached definitions for ALL 5 MCP servers. Deleting one file clears the cache for all servers simultaneously.

**Project-Specific Caches:**
Each Claude Code project has its own cache. If you work on multiple projects, each may have a separate `mcp-cache.json` file in its own `.cursor/projects/{PROJECT_ID}/` directory.

**When to Clear Cache:**
- After deleting local command files
- After modifying `.mcp.json` configuration
- After adding/removing MCP servers
- When tools don't appear in autocomplete
- When seeing duplicate command references
- After updating tool schemas in server code

### Finding Your PROJECT_ID

If you're unsure of your PROJECT_ID, list all cached projects:

```bash
# List all cached project directories
ls "C:\Users\willh\.cursor\projects\"

# Or search for any mcp-cache.json files
find "C:\Users\willh\.cursor" -name "mcp-cache.json" -type f
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

## Active Workorders

### WO-CODEREF-OUTPUT-UTILIZATION-001 - Phase 3: Workflow Integration

**Status:** 5/20 tasks complete (preparation done, implementation in progress)
**Plan:** `coderef/workorder/workflow-integration-phase3/plan.json`
**Goal:** Increase .coderef/ output utilization from 2.6% to 80%+ by integrating scan outputs into 4 workflows
**Risk:** Low (existing production scripts proven, just need integration wrappers)
**Effort:** 9 units (reduced from 11 by leveraging existing scripts)

#### Progress Summary

**✅ Preparation Complete (5/5)**
- Verified .coderef/ structure on all 5+ MCP servers
- Validated scan-all.py populated all required files
- Validated existing scripts: `packages/parse_coderef_data.py` (149 lines, 275K elements) ✅
- Validated existing scripts: `scripts/parse_coderef_data.py` (492 lines, 8 docs generated) ✅

**Phase 1: Adapt Existing Scripts (0/1)** - Effort: 1
- ☐ ADAPT-001: Create wrapper utilities in `coderef/utils/`

**Phase 2: Core Integrations (0/4)** - Effort: 3
- ☐ INTEGRATE-001: Update `analysis_generator.py` → call `packages/parse_coderef_data.py`
- ☐ INTEGRATE-002: Update `foundation_generator.py` → call `scripts/parse_coderef_data.py` ⭐ *~80% done*
- ☐ INTEGRATE-003: Update 9 personas → load `.coderef/patterns.json`
- ☐ INTEGRATE-004: Update `pytest_runner.py` → use `coderef_impact` tool

**Phase 3: Testing (0/5)** - Effort: 3
- ☐ TEST-001 through TEST-005 (integration tests + E2E verification)

**Phase 4: Documentation (0/5)** - Effort: 2
- ☐ DOC-001 through DOC-005 (update CLAUDE.md files + create integration guide)

**Finalization (0/5)**
- ☐ All tests passing (>80% coverage)
- ☐ Verify 80%+ utilization target met (12+/15 outputs used)
- ☐ Documentation complete
- ☐ Performance targets verified (<5s planning, <10s docs)
- ☐ Update workorder-log.txt

**Key Decisions:**
- Using existing production scripts instead of creating new ones (50% effort reduction)
- `.coderef/generated-docs/` pattern for drafts, `coderef/foundation-docs/` for final output
- INTEGRATE-002 mostly complete (script exists, just needs wrapper integration)

---

## Recent Changes

### v1.1.0 - Enhanced Stub Command with Context Capture
- ✅ Enhanced /stub command with smart conversation context extraction
- ✅ Optional `context` field in stub.json (conditionally included)
- ✅ Single /stub command (not two versions) - automatically detects context relevance
- ✅ Complete implementation guide with examples (STUB_COMMAND_IMPLEMENTATION_GUIDE.md)
- ✅ Integration with /create-workorder (stub.json used as seed data)

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

**System Status:** ✅ Production Ready - All 5 servers operational, workorder-centric architecture fully integrated, complete feature lifecycle tested
