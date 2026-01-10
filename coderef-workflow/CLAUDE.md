# coderef-workflow - AI Context Documentation

**Project:** coderef-workflow (MCP Server)
**Version:** 1.4.0
**Status:** ✅ Production - Feature lifecycle management orchestration
**Created:** 2024-12-24
**Last Updated:** 2025-01-04 (v1.4.0 - Simplified workflow)

---

## Quick Summary

**coderef-workflow** is an enterprise-grade MCP server that orchestrates the complete feature development lifecycle. It handles context gathering, planning, execution tracking, deliverables management, and feature archiving using a **workorder-centric architecture**.

**Core Innovation:** Works in tandem with **coderef-context** (code intelligence) and **coderef-docs** (documentation generation) to provide AI agents with the tools to manage complex, multi-phase feature implementations. **NEW:** Workorder ID tracking for complete audit trail and feature lifecycle management.

**Latest Update (v1.5.0 - 2025-01-10):**
- ✅ Added 4 new MCP tool integration methods to planning_analyzer.py
- ✅ `analyze_dependencies()` - Uses coderef_query for dependency analysis
- ✅ `analyze_impact()` - Uses coderef_impact for change impact assessment
- ✅ `analyze_complexity()` - Uses coderef_complexity for effort estimation
- ✅ `generate_architecture_diagram()` - Uses coderef_diagram for visualization
- ✅ Comprehensive telemetry tracking for data source usage (file reads vs MCP calls)
- ✅ Unit tests for all 4 MCP tool methods with mocked responses

**Previous (v1.4.0 - 2025-01-04):**
- ✅ Simplified /create-workorder workflow (11 steps → 9 steps)
- ✅ Step 2: User provides context directly (no interactive Q&A)
- ✅ Step 3: Uses .coderef/ exclusively (no fallbacks, errors if missing)
- ✅ Step 4: Creates plan.json only (DELIVERABLES.md removed)

**Previous (v1.3.0 - 2025-01-02):**
- ✅ Integrated .coderef/ structure into planning workflow
- ✅ Planning analyzer now reads patterns.json, coverage.json, index.json (5-10x faster)
- ✅ Automatic drift detection warns if .coderef/ is >10% stale

**Previous (v1.2.0):**
- ✅ Added autonomous /complete-workorder command
- ✅ Integrated TodoWrite tracking with real-time progress updates

**Key Relationship:**
- **coderef-workflow** = Orchestration & planning
- **coderef-docs** = Documentation generation (tools + slash commands)
- **coderef-context** = Code intelligence (AST analysis, dependency tracking)

Together they form a complete feature lifecycle system where:
1. **Context is gathered** (requirements, constraints)
2. **Plans are created** (task breakdown, phase management)
3. **Code is analyzed** (coderef-context provides intelligence)
4. **Execution is tracked** (progress, deliverables, metrics)
5. **Documentation is generated** (changelog, foundation docs)
6. **Features are archived** (for historical reference and recovery)

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

### Overview

coderef-workflow orchestrates the complete feature development lifecycle using a **workorder-centric architecture** with **code intelligence integration** from coderef-context. Each feature follows a structured flow: context gathering → analysis → planning → execution → documentation → archival.

### Context-Based Workflow Planning (v1.3.0 - .coderef/ Integration)

The workflow system uses **pre-scanned .coderef/ data** for lightning-fast planning:

```
Feature Planning Flow:
├─ gather_context() → Collect requirements
├─ analyze_project_for_planning()
│  ├─ Check .coderef/reports/drift.json (warn if >10% stale)
│  ├─ Read .coderef/index.json (code inventory, 5-10x faster)
│  ├─ Read .coderef/reports/patterns.json (coding conventions)
│  ├─ Read .coderef/reports/coverage.json (test gaps)
│  └─ Fallback: call coderef_scan if .coderef/ missing
├─ create_plan()
│  └─ Uses analysis.json from step above
└─ align_plan() → Align plan with todo list for tracking
```

**Key Integration Points (v1.5.0):**
- **Priority 1:** Read `.coderef/` pre-scanned data (fastest, 5-10x speedup)
- **Priority 2:** Call MCP tools for dynamic analysis (see below)
- **Priority 3:** Fallback to regex-based filesystem analysis
- **Freshness Check:** Warns if drift >10%, prompts re-scan before planning

**MCP Tools for Dynamic Analysis (v1.5.0):**
- `coderef_query` - Dependency/relationship analysis (what depends on X?)
- `coderef_impact` - Impact analysis (what breaks if I change X?)
- `coderef_complexity` - Complexity metrics for effort estimation
- `coderef_diagram` - Architecture diagram generation (Mermaid)

**Telemetry Tracking (v1.5.0):**
- Tracks all data sources used: `.coderef/` file reads, MCP tool calls, foundation doc reads
- Logs with emoji indicators: 📁 file, 🔧 MCP tool, 📄 doc
- `get_telemetry_summary()` provides usage statistics and percentages

**How to Generate .coderef/ (before planning):**
```bash
# Quick scan (index.json only, ~5-10 seconds)
coderef scan /path/to/project

# Full structure (all 16 outputs, ~30-60 seconds)
python scripts/populate-coderef.py /path/to/project
```

### Workorder System (v1.1.0+)

**Format:** `WO-{FEATURE}-{CATEGORY}-{SEQUENCE}`
**Example:** `WO-AUTH-SYSTEM-001`, `WO-API-DESIGN-002`

**Directory Structure:**
```
coderef/workorder/                    # All new features use workorder IDs
├── WO-AUTH-SYSTEM-001/               # Feature workorder
│  ├── context.json                   # Requirements & constraints
│  ├── analysis.json                  # Project analysis
│  ├── plan.json                      # Implementation plan + workorder_id
│  └── DELIVERABLES.md               # Progress & metrics

coderef/working/                      # Legacy features (unchanged)
├── old-feature-name/
└── another-old-feature/
```

**Workorder Tracking:**
Each plan.json includes workorder tracking in META_DOCUMENTATION:
```json
{
  "META_DOCUMENTATION": {
    "feature_name": "new-feature",
    "workorder_id": "WO-FEATURE-001",
    "status": "planning",
    "generated_by": "AI Assistant",
    "has_context": true,
    "has_analysis": true
  }
}
```

### Data Flow

```
User Request
    ↓
Slash Command (coderef-docs)
    ↓
coderef-workflow Tool (orchestration)
    ↓
    ├─ Gather/Analyze Data
    │  └─ Calls coderef-context tools when code intelligence needed
    ├─ Generate Plan (JSON structure)
    ├─ Generate Deliverables Template
    └─ Store in coderef/workorder/{feature}/
    ↓
coderef-docs Tools (documentation)
    ├─ Generate foundation docs (README, ARCHITECTURE, etc.)
    ├─ Generate/update CHANGELOG
    └─ Generate standards documentation
```

---

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** MCP (Model Context Protocol) 1.0+
- **Async:** asyncio (fully async/await)
- **Validation:** jsonschema 4.0+
- **Testing:** pytest 8.0+ with pytest-asyncio
- **Linting:** ruff
- **Type Checking:** mypy
- **Package Manager:** uv (or pip)

---

## Project Structure

```
coderef-workflow/
├── server.py                      # MCP server entry point & tool registration
├── pyproject.toml                 # Project metadata & dependencies
├── README.md                      # User-facing documentation
├── CLAUDE.md                      # This file (AI context)
├── SETUP_GUIDE.md                 # Installation guide
├── CODEREF_INTEGRATION_GUIDE.md   # How to integrate with coderef-context
├── CODEREF_TYPE_REFERENCE.md      # Type definitions & schemas
├── CODEREF_CONTEXT_MCP_VISION.md  # Architecture vision document
│
├── src/                           # Tool implementations
│  ├── plan_executor.py            # Executes plans step-by-step
│  ├── planning_analyzer.py        # Analyzes projects for planning
│  ├── mcp_client.py               # Async client for calling coderef-context
│  └── validators.py               # Input validation
│
├── generators/                    # Plan & analysis generators
│  ├── plan_generator.py           # Creates plan.json from context
│  └── analysis_generator.py       # Generates project analysis
│
├── coderef/workorder/               # Active feature workspaces
│  └── {feature-name}/
│     ├── context.json             # Requirements & constraints
│     ├── analysis.json            # Project analysis results
│     ├── plan.json                # Implementation plan (10 sections)
│     ├── communication.json       # Multi-agent coordination
│     ├── DELIVERABLES.md          # Metrics & tracking
│     └── execution-log.json       # Progress tracking
│
├── coderef/archived/              # Completed features
│  └── index.json                  # Archive metadata
│
└── tests/                         # Test suite
   ├── test_plan_executor.py
   ├── test_planning_analyzer.py
   └── test_mcp_client.py
```

---

## Core Tools (24 MCP Tools)

### Planning & Analysis Phase

| Tool | Purpose | Uses coderef-context? |
|------|---------|----------------------|
| `gather_context` | Collect feature requirements & constraints | No |
| `analyze_project_for_planning` | Scan codebase for architecture/patterns | **Yes** (coderef_scan) |
| `get_planning_template` | Get the 10-section plan template | No |
| `create_plan` | Generate complete implementation plan | **Yes** (coderef_query, coderef_patterns) |
| `validate_implementation_plan` | Score plan quality (0-100) | No |
| `generate_plan_review_report` | Create markdown review report | No |

### Execution & Tracking Phase

| Tool | Purpose | Uses coderef-context? |
|------|---------|----------------------|
| `execute_plan` | Align plan with todo list for tracking (command: `/align-plan`) | No |
| `update_task_status` | Track individual task progress | No |
| `track_agent_status` | Dashboard for agent task assignments | No |
| `generate_handoff_context` | Create claude.md for agent handoffs | No |
| `assign_agent_task` | Assign specific task to agent (1-10) | No |
| `verify_agent_completion` | Validate agent work with git diffs | No |

### Deliverables & Documentation

| Tool | Purpose | Uses coderef-context? |
|------|---------|----------------------|
| `generate_deliverables_template` | Create DELIVERABLES.md structure | No |
| `update_deliverables` | Update metrics from git history | No |
| `update_all_documentation` | Update README/CHANGELOG/CLAUDE.md | No |
| `aggregate_agent_deliverables` | Combine metrics from multi-agent runs | No |

### Risk & Integration

| Tool | Purpose | Uses coderef-context? |
|------|---------|----------------------|
| `assess_risk` | AI-powered risk scoring (0-100) | **Yes** (for impact analysis) |
| `generate_agent_communication` | Create multi-agent coordination file | No |

### Archival & Inventory

| Tool | Purpose | Uses coderef-context? |
|------|---------|----------------------|
| `archive_feature` | Move completed feature to archive | No |
| `generate_features_inventory` | List all active & archived features | No |
| `audit_plans` | Health check on all plans in coderef/workorder | No |

### Workorder Tracking

| Tool | Purpose | Uses coderef-context? |
|------|---------|----------------------|
| `log_workorder` | Add entry to global workorder log | No |
| `get_workorder_log` | Query workorder history | No |

### Foundation Docs (delegated to coderef-docs)

| Tool | Purpose |
|------|---------|
| `coderef_foundation_docs` | Unified generator for ARCHITECTURE/SCHEMA/API/COMPONENTS |

---

## Slash Commands (40+ available in coderef-docs)

These commands trigger coderef-workflow and coderef-docs tools:

### Planning & Context Commands

```
/create-workorder              # Gather context → analyze → create plan
/create-plan                   # Create plan from existing context
/analyze-for-planning          # Analyze project structure for planning
/gather-context                # Collect feature requirements
/validate-plan                 # Score existing plan quality
/generate-plan-review          # Generate markdown review report
/get-planning-template         # View 10-section plan template
```

### Execution & Tracking Commands

```
/align-plan                    # Align plan with todo list for tracking
/update-task-status            # Track individual task progress
/track-agent-status            # View agent assignment dashboard
/assign-agent-task             # Assign task to specific agent (1-10)
/verify-agent-completion       # Validate agent work completion
/generate-handoff-context      # Create claude.md for agent handoffs
```

### Documentation Commands

```
/update-docs                   # Update README/CHANGELOG/CLAUDE.md
/update-deliverables           # Update metrics from git history
/update-changelog              # Record feature changes
/add-changelog                 # Add changelog entry
/get-changelog                 # View changelog history
/generate-deliverables         # Create DELIVERABLES.md template
/aggregate-agent-deliverables  # Sum metrics from multi-agent work
```

### Foundation Documentation

```
/coderef-foundation-docs       # Generate ARCHITECTURE/SCHEMA/API/COMPONENTS
/generate-foundation-docs      # Alias for above
/update-foundation-docs        # Regenerate existing foundation docs
/list-templates                # List available doc templates
/get-template                  # View specific template content
/generate-quickref             # Create quick reference guide
/generate-user-guide           # Generate user documentation
/generate-my-guide             # Generate internal guide
```

### Standards & Quality

```
/establish-standards           # Scan codebase and establish UI/UX/behavior standards
/audit-codebase                # Audit codebase against standards
/check-consistency             # Check changes against standards (pre-commit)
/audit-plans                   # Health check on all plans
```

### Feature Management

```
/archive-feature               # Archive completed feature
/features-inventory            # List all active & archived features
```

### Workorder Management

```
/log-workorder                 # Add to global workorder log
/get-workorder-log             # Query workorder history
```

### Git & Release

```
/git-release                   # Prepare git release
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
       → Works through tasks step by step
       → Calls coderef-context for CSS/component patterns
       ↓
User: /update-deliverables → /archive-feature
      → Captures metrics, archives
```

### UC-2: Multi-Agent Feature Implementation
```
User: /create-workorder --multi-agent
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

---

## Essential Commands

### Development
```bash
# Install
pip install -e .
# or with uv
uv sync

# Run server
python server.py

# Run tests
pytest tests/ -v

# Type check
mypy src/

# Lint
ruff check src/
```

### Project Management
```bash
# Create new feature
/create-workorder feature-name

# Align plan with todo list
/align-plan feature-name

# Update docs
/update-docs feature-name 1.0.1

# Archive when complete
/archive-feature feature-name
```

---

---

## Recent Changes (v1.3.0 - 2025-01-02)

**Major Feature - .coderef/ Integration for 5-10x Faster Planning**

### New Features
- ✅ Removed redundant foundation docs generation from `/create-workorder` Step 3
- ✅ Planning analyzer now reads pre-scanned `.coderef/` data first (patterns, coverage, index)
- ✅ Automatic drift detection warns if `.coderef/` is >10% stale before planning
- ✅ 3-tier fallback system: .coderef/ files → MCP tools → regex analysis
- ✅ Reduced `/create-workorder` from 11 steps to 10 steps

### Performance Improvements
- ⚡ **5-10x faster planning** - reads pre-scanned data instead of live generation
- ⚡ **Zero redundant work** - uses existing `.coderef/index.json` instead of re-scanning
- ⚡ **Smart freshness check** - warns if drift >10%, prompts re-scan

### Implementation Details
- ✅ Enhanced `planning_analyzer.py:identify_patterns()` to read `patterns.json` first
- ✅ Enhanced `planning_analyzer.py:identify_gaps_and_risks()` to read `coverage.json` first
- ✅ Added `planning_analyzer.py:check_coderef_freshness()` for drift detection
- ✅ Updated `create-workorder.md` to remove Step 3 and renumber steps
- ✅ Foundation docs generation now optional via `/coderef-foundation-docs` post-implementation

### Workflow Changes
- **Before (v1.2.0):** Gather Context → **Generate Foundation Docs (30-60s)** → Analyze → Plan
- **After (v1.3.0):** Gather Context → Analyze (reads .coderef/, <5s) → Plan

**Files Changed:**
- `.claude/commands/create-workorder.md` (removed Step 3, renumbered)
- `generators/planning_analyzer.py` (3 methods enhanced with .coderef/ reading)
- `CLAUDE.md` (documentation updated)

---

## Previous Changes (v1.2.0 - 2025-12-28)

**Major Feature - Autonomous Implementation Command**

### New Features
- ✅ Created `/complete-workorder` slash command for fully autonomous feature implementation
- ✅ Automatic execution of all tasks from plan.json phases sequentially
- ✅ Real-time TodoWrite progress tracking with CLI display
- ✅ Integrated testing, deliverables updates, and documentation generation
- ✅ Auto-archive on completion when all success criteria met

### Implementation Details
- ✅ 323-line command file with comprehensive workflow orchestration
- ✅ Parses 10-section plan.json structure
- ✅ Updates task status (pending → in_progress → completed)
- ✅ Git commits after each task with workorder tracking
- ✅ Calls update_deliverables and update_all_documentation automatically
- ✅ Error handling follows plan's risk assessment guidance

### Workflow Enhancement
- ✅ Complete lifecycle now: `/create-workorder` → manual review → `/complete-workorder` → done
- ✅ Zero manual implementation steps required
- ✅ Full audit trail from planning through archival

**Reference:** WO-COMPLETE-WORKORDER-CMD-001 (16/16 tasks complete, 323 LOC)

---

## Previous Changes (v1.1.0)

**Major Release - Workorder System & Bug Fixes**

### Bug Fixes
- ✅ Fixed deliverables crash in generate_deliverables_template (tool_handlers.py:1607)
- ✅ Fixed plan status lifecycle - now starts as "planning" not "complete"

### Enhancements
- ✅ Implemented workorder_id tracking throughout system
- ✅ workorder_id now stored in plan.json META_DOCUMENTATION for audit trail
- ✅ create_plan tool schema updated to accept optional workorder_id parameter
- ✅ Workorder-centric architecture with WO-{FEATURE}-{CATEGORY}-### format

### Refactoring
- ✅ Updated 6 Python files (42 changes) - path from coderef/working → coderef/workorder
- ✅ Updated 13 slash command files (35 changes)
- ✅ Updated main documentation (README.md, CLAUDE.md)
- ✅ All references to coderef/working updated to coderef/workorder

### Testing
- ✅ All 4 critical tests passed (100% pass rate)
- ✅ Validated with real plan.json from WO-WORKFLOW-REFACTOR-001
- ✅ Zero regressions detected

### Documentation
- ✅ Created comprehensive migration guide
- ✅ Created detailed change inventory
- ✅ All user-facing documentation updated

**Reference:** WO-WORKFLOW-REFACTOR-001 (16/16 tasks complete)

---

## Earlier Changes (v1.0.0)

- ✅ Complete feature lifecycle management
- ✅ Context-based planning with coderef-context integration
- ✅ Multi-agent task coordination
- ✅ Automated deliverables tracking
- ✅ Feature archival system
- ✅ Risk assessment with code intelligence
- ✅ Plan validation and scoring (0-100)

---

## Next Steps

### Feature Enhancements (P0)
- ⏳ Enhanced plan validation with AI-powered quality scoring
- ⏳ Automated plan refinement suggestions
- ⏳ Real-time plan progress tracking dashboard
- ⏳ Plan versioning with diff comparison
- ⏳ Multi-language support for plan generation

### Multi-Agent Coordination (P1)
- ⏳ Agent task dependency resolution (automatic ordering)
- ⏳ Agent communication protocol improvements
- ⏳ Parallel agent execution with proper isolation
- ⏳ Agent failure recovery and retry logic
- ⏳ Cross-agent deliverables aggregation

### Integration & Ecosystem (P1)
- ⏳ Deeper coderef-context integration (more tool usage)
- ⏳ coderef-docs automation (auto-generate docs on archive)
- ⏳ coderef-personas coordination (auto-select expert for task type)
- ⏳ coderef-testing integration (test coverage in plan validation)
- ⏳ GitHub Actions workflow for CI/CD automation

### Performance & Scalability (P2)
- ⏳ Async plan generation for large codebases
- ⏳ Incremental planning (update existing plans vs regenerate)
- ⏳ Plan caching with smart invalidation
- ⏳ Parallel workorder processing
- ⏳ Optimize memory usage for large feature sets

### Tool Improvements (P2)
- ⏳ Add `preview_plan_changes` tool (dry-run mode)
- ⏳ Add `estimate_effort` tool (AI-powered time estimation)
- ⏳ Add `suggest_task_breakdown` tool (auto-split complex tasks)
- ⏳ Add `detect_blocking_tasks` tool (dependency analysis)
- ⏳ Enhanced risk assessment with ML-based predictions

### Documentation & UX (P3)
- ⏳ Interactive plan builder (step-by-step wizard)
- ⏳ Plan templates for common feature types
- ⏳ Video tutorials for /create-workorder workflow
- ⏳ Best practices guide for multi-agent features
- ⏳ API reference with OpenAPI spec

### Quality & Reliability (P3)
- ⏳ Comprehensive test suite for all 24 tools
- ⏳ Integration tests with real workorders
- ⏳ Performance benchmarking (target <10s for plan generation)
- ⏳ Error recovery and graceful degradation
- ⏳ Health monitoring and telemetry

---

## Troubleshooting

### "Error: Feature not found in coderef/workorder/"

```bash
# Check if feature exists
ls coderef/workorder/

# Verify feature name spelling (case-sensitive)
ls coderef/workorder/ | grep -i "feature-name"

# Check if already archived
ls coderef/archived/ | grep -i "feature-name"
```

### "Error: plan.json validation failed"

```bash
# Validate JSON syntax
python -m json.tool coderef/workorder/{feature}/plan.json

# Check plan structure
cat coderef/workorder/{feature}/plan.json | grep META_DOCUMENTATION

# Re-run plan validation
/validate-plan {feature-name}
```

### "Error: coderef-context tools not available"

```
→ Check if coderef-context MCP server is running
→ Verify .mcp.json configuration includes coderef-context
→ Check CODEREF_CLI_PATH environment variable
→ Restart Claude Code to reload MCP servers
```

### "Error: Workorder ID generation failed"

```bash
# Check workorder log
cat coderef/workorder-log.txt | tail -20

# Manually specify workorder ID
/create-plan --workorder-id "WO-FEATURE-NAME-001"

# Verify workorder format (WO-{FEATURE}-{CATEGORY}-###)
```

### "Error: DELIVERABLES.md not found"

```
→ Feature may not have completed planning phase
→ Run /generate-deliverables to create template
→ Ensure plan.json exists before generating deliverables
```

### "Error: Archive operation failed"

```bash
# Check if feature already archived
ls coderef/archived/{feature-name}

# Check DELIVERABLES.md status
cat coderef/workorder/{feature-name}/DELIVERABLES.md | grep "Status:"

# Force archive (skip confirmation)
/archive-feature {feature-name} --force
```

---

**Last Updated:** December 25, 2025 (v1.1.0 release)
**Previous Update:** December 24, 2024 (v1.0.0)
**Maintained by:** willh, Claude Code AI
