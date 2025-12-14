# CLAUDE.md - docs-mcp AI Context Documentation

**Version**: 3.0.0 | **Python**: 3.11+ | **Audience**: AI Assistants (Development & Usage)

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [For AI Assistants Using This Server](#for-ai-assistants-using-this-server)
3. [For AI Assistants Developing This Server](#for-ai-assistants-developing-this-server)
4. [Tool Catalog](#tool-catalog)
5. [Design Patterns](#design-patterns)
6. [Adding New Tools](#adding-new-tools)
7. [MCP Compatibility & Cross-Agent Access](#mcp-compatibility--cross-agent-access)

---

## Quick Reference

### What This Server Does

**docs-mcp** is an MCP server providing:
- **39 specialized tools** for documentation generation, changelog management, planning, quickref generation, consistency auditing, deliverables tracking, **AI-powered risk assessment**, **multi-agent coordination**, **feature archiving**, **global workorder tracking**, **LLM workflow**, and comprehensive project inventory (files, dependencies, APIs, databases, configurations, tests, documentation)
- **Workorder Tracking System** - Automatic unique ID assignment (WO-{FEATURE-NAME}-001) for all features in MCP planning workflow (v1.5.0)
- **Global Workorder Logging** - Simple one-line logging for tracking workorder completion across projects (NEW in v1.11.0)
- **Deliverables Tracking System** - Automatic DELIVERABLES.md generation with git-based metrics (LOC, commits, time) (v1.6.0)
- **Feature Archive System** - Automated archiving of completed features from working to archived directory with index tracking (v1.10.0)
- **48 slash commands** for quick access to common workflows including documentation, planning, standards, agent coordination, archiving, workorder logging, LLM workflow, and inventory tools
- **POWER framework templates** for comprehensive technical documentation
- **Agentic workflows** enabling AI self-documentation via meta-tools
- **Consistency Trilogy** pattern for living standards and compliance auditing
- **Enterprise patterns**: modular handlers, structured logging, type safety, security hardening

### System Architecture

```
server.py (299 lines)           # MCP entry point, 9 tool definitions
http_server.py (~300 lines)     # HTTP wrapper for ChatGPT (multi-server support - WIP)
tool_handlers.py (~1679 lines)  # 21 handlers + registry pattern
handler_decorators.py (188 lines) # @mcp_error_handler, @log_invocation (ARCH-004, ARCH-005)
handler_helpers.py (49 lines)   # format_success_response() (QUA-004)
error_responses.py              # ErrorResponse factory (ARCH-001)
type_defs.py (219 lines)        # TypedDict definitions (QUA-001)
logger_config.py                # Structured logging (ARCH-003)
constants.py (119 lines)        # Paths, Files, enums (REF-002, QUA-003)
validation.py (271 lines)       # Input validation layer (REF-003)
generators/
  ├── base_generator.py         # Base template operations
  ├── foundation_generator.py   # Multi-document generation
  ├── changelog_generator.py    # Changelog CRUD + schema validation
  ├── standards_generator.py    # Standards extraction (~400 lines)
  └── audit_generator.py        # Compliance auditing (~863 lines)
templates/power/                # POWER framework templates
  ├── readme.txt
  ├── architecture.txt
  ├── api.txt
  ├── components.txt
  ├── schema.txt
  └── user-guide.txt
coderef/
  ├── working/                  # Feature-specific working directories (NEW in v1.4.4)
  │   └── {feature_name}/
  │       ├── context.json      # Feature context (from /gather-context) with workorder ID
  │       ├── analysis.json     # Project analysis (from /analyze-for-planning) with workorder
  │       └── plan.json         # Implementation plan (from /create-plan) with workorder in section 5
  ├── changelog/
  │   ├── CHANGELOG.json        # Structured changelog data
  │   └── schema.json           # JSON schema for validation
  ├── foundation-docs/          # Generated documentation output
  ├── standards/                # Extracted standards documents
  │   ├── UI-STANDARDS.md
  │   ├── BEHAVIOR-STANDARDS.md
  │   ├── UX-PATTERNS.md
  │   └── COMPONENT-INDEX.md
  └── audits/                   # Compliance audit reports
      └── audit-YYYYMMDD-HHMMSS.md
```

### Unified HTTP Server (Multi-Server Gateway) - READY FOR CHATGPT

**Workorder:** WO-UNIFIED-MCP-HTTP-SERVER-001
**Status:** ✅ Ready for ChatGPT Integration (Pending Railway config)
**Session Date:** 2025-10-21
**Key Commits:**
- `6a6b08b` - First successful multi-server loading (3/4 servers)
- `826192b` - All endpoints updated, 44 tools discovered
- `332639b` - Added standalone mode for Railway
- `3804e45` - Added Railway environment configuration
- `f210256` - Session status documentation

**Goal:** Expose MCP tools through unified HTTP endpoint for ChatGPT integration.

**Current State:**

**Local Deployment (✅ Working):**
- ✅ Multi-server loading infrastructure complete
- ✅ All endpoints updated (/, /health, /tools, /mcp)
- ✅ 44 tools discovered from 3 servers (docs-mcp, hello-world-mcp, personas-mcp)
- ✅ docs-mcp (36 tools) - FULLY FUNCTIONAL
- ✅ Unified routing tested and working

**Railway Deployment (⏳ Pending Manual Step):**
- ⏳ Requires `STANDALONE_MODE=true` environment variable to be set in Railway dashboard
- 📍 Once set, will deploy with 36 docs-mcp tools for ChatGPT
- 🔗 URL: https://docs-mcp-production.up.railway.app/mcp

**Architecture Pattern:** Gateway pattern with dual-mode support:
- **Multi-Server Mode** (local): Loads all available MCP servers from sibling directories
- **Standalone Mode** (Railway): Runs docs-mcp independently with 36 tools

**Server Patterns Supported:**
1. **TOOL_HANDLERS pattern** (docs-mcp): Direct handler dictionary - ✅ WORKING
2. **MCP Server pattern** (hello-world-mcp, personas-mcp): @app decorators - Discovered (8 tools), execution pending

**Known Issues (Non-Blocking):**
1. **MCP Server pattern execution** - Deferred for investigation (doesn't affect docs-mcp)
2. **coderef-mcp dependency conflicts** - Graceful degradation working (3/4 servers load)

**Next Steps:**
1. Set `STANDALONE_MODE=true` in Railway dashboard → Variables
2. Verify Railway deployment: `curl https://docs-mcp-production.up.railway.app/`
3. Configure ChatGPT Actions with Railway URL
4. Test MCP tools in ChatGPT

**Documentation:**
- `coderef/working/unified-mcp-http-server/STATUS.md` - Complete session summary
- `coderef/working/unified-mcp-http-server/PROGRESS.md` - Detailed progress
- `coderef/working/unified-mcp-http-server/TROUBLESHOOTING.md` - Tool discovery fix

---

## For AI Assistants Using This Server

### When to Use docs-mcp Tools

**Use these tools when:**
- User asks to "generate documentation" or "create a README"
- User wants to "document changes" or "update the changelog"
- User needs project architecture, API, or component documentation
- User asks to "extract standards" or "establish coding standards"
- User wants to "audit codebase for consistency" or "check compliance"
- You're completing work and need to document what you've done
- You need to ensure code consistency across a project

**Available in your tool palette as:**
- `mcp__docs-mcp__list_templates`
- `mcp__docs-mcp__get_template`
- `mcp__docs-mcp__generate_foundation_docs`
- `mcp__docs-mcp__generate_individual_doc`
- `mcp__docs-mcp__get_changelog`
- `mcp__docs-mcp__add_changelog_entry`
- `mcp__docs-mcp__update_changelog`
- `mcp__docs-mcp__generate_quickref_interactive`
- `mcp__docs-mcp__establish_standards`
- `mcp__docs-mcp__audit_codebase`
- `mcp__docs-mcp__check_consistency`
- `mcp__docs-mcp__get_planning_template`
- `mcp__docs-mcp__analyze_project_for_planning`
- `mcp__docs-mcp__create_plan`
- `mcp__docs-mcp__validate_implementation_plan`
- `mcp__docs-mcp__generate_plan_review_report`
- `mcp__docs-mcp__inventory_manifest`
- `mcp__docs-mcp__dependency_inventory`
- `mcp__docs-mcp__api_inventory`
- `mcp__docs-mcp__database_inventory`
- `mcp__docs-mcp__config_inventory`
- `mcp__docs-mcp__test_inventory`
- `mcp__docs-mcp__documentation_inventory`
- `mcp__docs-mcp__archive_feature`

### Slash Commands (Claude Code Shortcuts)

**docs-mcp** includes 33 slash commands for quick access to common workflows:

#### `/generate-docs`
Generates foundation documentation for current project.
- Calls `generate_foundation_docs` with current directory
- Returns 5 foundation document templates (README, ARCHITECTURE, API, COMPONENTS, SCHEMA)
- AI then fills templates and saves documents
- Note: USER-GUIDE is optional and generated separately via `generate_individual_doc`

```bash
# User types: /generate-docs
# Claude executes workflow and generates README, ARCHITECTURE, API, etc.
```

#### `/generate-user-guide`
Generates USER-GUIDE documentation for current project.
- Calls `generate_individual_doc` with current directory and template_name="user-guide"
- Returns USER-GUIDE template
- AI then fills template and saves document

```bash
# User types: /generate-user-guide
# Claude executes workflow and generates comprehensive USER-GUIDE.md
```

#### `/generate-quickref`
Generates universal quickref guide for ANY application via interactive interview.
- Calls `generate_quickref_interactive` with current directory
- AI asks 9 interview questions to gather app information
- User answers in plain English
- AI generates scannable quickref.md (150-250 lines) following universal pattern
- Saves to `coderef/quickref.md`

```bash
# User types: /generate-quickref
# Claude interviews user about the app, then generates quickref.md
# Supports CLI, Web, API, Desktop, and Library applications
```

#### `/establish-standards`
Extracts coding standards from current project.
- Calls `establish_standards` with current directory
- Scans codebase for UI/behavior/UX patterns
- Creates 4 standards documents in `coderef/standards/`
- **Run ONCE per project** to establish baseline

```bash
# User types: /establish-standards
# Claude scans code and creates UI-STANDARDS.md, BEHAVIOR-STANDARDS.md, etc.
```

#### `/audit-codebase`
Audits current project for standards compliance.
- Calls `audit_codebase` with current directory
- Compares code against established standards
- Generates compliance report with score (0-100)
- Lists violations by severity and provides fixes

```bash
# User types: /audit-codebase
# Claude audits entire codebase and generates compliance report
```

#### `/check-consistency`
Quick consistency check on modified files (pre-commit gate).
- Calls `check_consistency` with current directory
- Auto-detects git changes (staged files)
- Only scans modified files (fast!)
- Reports violations at or above severity threshold

```bash
# User types: /check-consistency
# Claude checks only modified files for standards violations
```

#### `/start-feature` (RECOMMENDED)
**Primary entry point for feature planning.** Orchestrates the full workflow in one command.
- Asks for feature name
- Runs gather-context (interactive Q&A)
- Runs analyze-project-for-planning (automatic)
- Runs create-plan (automatic)
- Runs validate-plan (auto-fixes until score >= 90)
- Commits planning artifacts to git

```bash
# User types: /start-feature
# Claude runs entire planning pipeline: gather → analyze → plan → validate → commit
# Creates: context.json, analysis.json, plan.json, DELIVERABLES.md
```

**Complete Feature Lifecycle:**
```
/start-feature → /execute-plan → implement → /update-deliverables → /update-docs → /update-foundation-docs → /archive-feature
     │                │              │                │                  │                  │                    │
     │                │              │                │                  │                  │                    └─ Archive to coderef/archived/
     │                │              │                │                  │                  └─ Update API.md, user-guide.md, etc.
     │                │              │                │                  └─ Update changelog, README, CLAUDE.md
     │                │              │                └─ Capture git metrics (LOC, commits, time)
     │                │              └─ Write code following plan phases
     │                └─ Generate TodoWrite task list
     └─ Plan: gather context → analyze → create plan → validate
```

**IMPORTANT: Always complete the full lifecycle including changelog (/update-docs) and foundation docs (/update-foundation-docs)**

---

#### `/analyze-for-planning` (Advanced)
Standalone project analysis - use when you already have context or need fine-grained control.
- Calls `analyze_project_for_planning` with current directory
- Discovers foundation docs, standards, patterns
- Identifies tech stack and reference components
- **Note:** Usually not needed - `/start-feature` runs this automatically

```bash
# User types: /analyze-for-planning
# Claude analyzes project and provides planning context (80ms)
```

#### `/validate-plan`
Validates implementation plan quality.
- Asks user for plan file path
- Calls `validate_implementation_plan` with plan file
- Scores plan 0-100 based on completeness/quality
- **Validates workorder consistency** - format, task references, metadata
- Identifies issues by severity with fix suggestions
- **Iterative review loop** until score >= 90

```bash
# User types: /validate-plan
# Claude validates plan and provides feedback for improvement
# Includes workorder validation (optional, backward compatible)
```

#### `/get-planning-template`
Get feature implementation planning template for AI reference.
- Calls `get_planning_template` with optional section parameter
- Returns JSON template structure with all required fields
- Includes quality standards and best practices
- Available sections: all, 0_preparation through 9_implementation_checklist

```bash
# User types: /get-planning-template
# Claude returns the full planning template or specific section
```

#### `/create-plan` (Advanced)
Standalone plan creation - use when you already have context.json and analysis.json.
- **Tip:** Use `/start-feature` instead for the full automated workflow
- Asks user for feature name (alphanumeric, hyphens, underscores only)
- Calls `create_plan` with current directory and feature name
- Loads context.json and analysis.json if available
- Generates complete 10-section plan
- Saves to coderef/working/{feature_name}/plan.json

```bash
# User types: /create-plan
# Claude asks for feature name, then generates implementation plan
# Best results require both context and analysis (use /start-feature)
```

#### `/generate-plan-review`
Generate markdown review report from validation results.
- Asks user for plan file path
- Calls `generate_plan_review_report` with plan file
- Transforms validation results into comprehensive markdown report
- Includes score, issues by severity, and actionable recommendations
- Saves to coderef/reviews/ directory

```bash
# User types: /generate-plan-review
# Claude generates formatted review report for the plan
```

#### `/generate-deliverables` (NEW in v1.6.0)
Generate DELIVERABLES.md template from plan.json structure.
- Asks user for feature name
- Calls `generate_deliverables_template` with current directory and feature name
- Creates DELIVERABLES.md with phases, tasks, metrics placeholders
- Includes workorder ID from plan
- Status: 🚧 Not Started

**Note**: Automatically called by `/create-plan`, usually don't need to run manually

```bash
# User types: /generate-deliverables
# Claude asks for feature name, generates DELIVERABLES.md template
# Template includes TBD placeholders for LOC, commits, time
```

#### `/update-deliverables` (NEW in v1.6.0)
Update DELIVERABLES.md with actual metrics from git history.
- Asks user for feature name
- Calls `update_deliverables` with current directory and feature name
- Parses git log to find feature-related commits (case-insensitive)
- Calculates LOC from git diff --stat
- Counts commits and contributors
- Measures time from first to last commit
- Replaces TBD placeholders with actual values
- Updates status to ✅ Complete

**Git Integration**: Searches commit messages for feature name, so include feature name in commits

```bash
# User types: /update-deliverables
# Claude asks for feature name, calculates metrics from git history
# Example: 5 commits, 450 LOC added, 120 deleted, 3 days elapsed
```

#### `/update-docs` (NEW in v2.4.0)
Update all project documentation after feature completion.
- Calls `update_all_documentation` with feature context
- Auto-increments version based on change_type (feature=minor, bugfix=patch, breaking=major)
- Updates README.md version and What's New section
- Updates CLAUDE.md version history
- Adds CHANGELOG.json entry with workorder tracking
- Designed for AI agents who provide context from their work

**Workflow Integration**: Run AFTER `/update-deliverables` and BEFORE `/archive-feature`

```bash
# User types: /update-docs
# Claude provides: change_type, description, workorder_id, files_changed
# Tool auto-increments version and updates all docs
# Feature Implementation → /update-deliverables → /update-docs → /archive-feature
```

#### `/database-inventory`
Generate comprehensive database schema inventory.
- Calls `database_inventory` with current directory
- Discovers tables and collections across PostgreSQL, MySQL, MongoDB, SQLite
- Parses ORM models (SQLAlchemy, Sequelize, Mongoose) using AST/regex
- Extracts migration files (Alembic, Knex.js)
- Captures column/field metadata with relationships and indexes
- Generates database.json with schema metadata and system breakdown

```bash
# User types: /database-inventory
# Claude analyzes database schemas and generates inventory manifest
```

#### `/documentation-inventory`
Generate comprehensive documentation inventory.
- Calls `documentation_inventory` with current directory
- Discovers documentation files across 5 formats (Markdown, RST, AsciiDoc, HTML, Org-mode)
- Analyzes quality metrics (freshness, completeness, coverage)
- Calculates quality score 0-100 based on patterns found
- Generates documentation.json with format breakdown and metrics

```bash
# User types: /documentation-inventory
# Claude scans documentation and generates quality report
```

#### `/generate-agent-communication` **NEW in v1.9.0**
Generate multi-agent communication.json from plan.json.
- Asks user for feature name
- Calls `generate_agent_communication` with current directory and feature name
- Extracts precise steps from implementation phases
- Includes forbidden files, allowed files, success criteria
- Initializes agent status fields with workorder ID

```bash
# User types: /generate-agent-communication
# Claude asks for feature name, generates communication.json
```

#### `/assign-agent-task` **NEW in v1.9.0**
Assign specific task to agent with workorder scoping.
- Asks user for feature name, agent number (1-10), and optional phase ID
- Calls `assign_agent_task` with parameters
- Generates agent-scoped workorder ID (WO-FEATURE-002, WO-FEATURE-003)
- Updates communication.json with assignment
- Detects conflicting assignments

```bash
# User types: /assign-agent-task
# Claude asks for feature name and agent number
# Assigns agent with unique workorder
```

#### `/verify-agent-completion` **NEW in v1.9.0**
Verify agent completion with automated checks.
- Asks user for feature name and agent number to verify
- Calls `verify_agent_completion` with parameters
- Validates agent status is COMPLETE
- Runs git diff on forbidden files
- Validates success criteria from communication.json
- Updates status to VERIFIED or VERIFICATION_FAILED

```bash
# User types: /verify-agent-completion
# Claude asks for feature name and agent number
# Runs automated verification checks
```

#### `/aggregate-agent-deliverables` **NEW in v1.9.0**
Aggregate metrics from multiple agent DELIVERABLES.md files.
- Asks user for feature name
- Calls `aggregate_agent_deliverables` with current directory and feature name
- Finds all DELIVERABLES.md files in feature directory
- Aggregates LOC, commits, contributors, time
- Generates DELIVERABLES-COMBINED.md report

```bash
# User types: /aggregate-agent-deliverables
# Claude asks for feature name, generates combined report
```

#### `/track-agent-status` **NEW in v1.9.0**
Track agent status across features with real-time dashboard.
- Optionally asks user for specific feature name
- Calls `track_agent_status` with current directory
- Provides feature-level or project-wide tracking
- Shows status counts (available, assigned, in_progress, complete, verified, blocked)
- Identifies blockers and overall workflow status

```bash
# User types: /track-agent-status
# Claude shows real-time coordination dashboard
# Displays agent statuses and blockers
```

---

### Multi-Agent Workflow Example

**Scenario**: Implement authentication feature using 3 parallel agents

```bash
# Step 1: Create plan (single agent)
/start-feature
# Feature name: auth-system
# Creates: plan.json with workorder WO-AUTH-SYSTEM-001

# Step 2: Generate communication protocol
/generate-agent-communication
# Feature name: auth-system
# Creates: communication.json with agent slots and forbidden files

# Step 3: Assign work to parallel agents
/assign-agent-task
# Feature: auth-system, Agent: 1, Phase: phase_1_setup
# Agent 1 gets WO-AUTH-SYSTEM-002 (dependencies + directory structure)

/assign-agent-task
# Feature: auth-system, Agent: 2, Phase: phase_2_core
# Agent 2 gets WO-AUTH-SYSTEM-003 (JWT + password hashing)

/assign-agent-task
# Feature: auth-system, Agent: 3, Phase: phase_3_tests
# Agent 3 gets WO-AUTH-SYSTEM-004 (unit + integration tests)

# Step 4: Agents work in parallel (each in separate terminal)
# Each agent updates communication.json tasks as they work:
#   - Set task status to "in_progress" when starting
#   - Set status to "complete" with timestamp when done
# Lloyd can check progress anytime by reading communication.json
# Agent 1: Completes setup, updates task status to COMPLETE
# Agent 2: Completes core logic, updates task status to COMPLETE
# Agent 3: Completes tests, updates task status to COMPLETE

# Step 5: Verify each agent's work
/verify-agent-completion
# Feature: auth-system, Agent: 1
# Validates: forbidden files unchanged, success criteria met
# Status: VERIFIED ✅

/verify-agent-completion
# Feature: auth-system, Agent: 2
# Status: VERIFIED ✅

/verify-agent-completion
# Feature: auth-system, Agent: 3
# Status: VERIFIED ✅

# Step 6: Monitor overall progress
/track-agent-status
# Feature: auth-system
# Output:
# ┌─────────────────────────────────────┐
# │ Agent Status: auth-system           │
# ├─────────────────────────────────────┤
# │ Agent 1: VERIFIED ✅                │
# │ Agent 2: VERIFIED ✅                │
# │ Agent 3: VERIFIED ✅                │
# │ Overall: 3/3 complete               │
# └─────────────────────────────────────┘

# Step 7: Aggregate deliverables
/aggregate-agent-deliverables
# Feature: auth-system
# Creates: DELIVERABLES-COMBINED.md with total LOC, commits, time

# Step 8: Archive completed feature
/archive-feature
# Feature: auth-system
# Moves to: coderef/archived/auth-system/
```

**communication.json Structure** (v1.1.0 - Task Tracking):
```json
{
  "workorder_id": "WO-AUTH-SYSTEM-001",
  "feature_name": "auth-system",
  "tasks": [
    {"id": "STEP-001", "description": "Read plan.json", "status": "complete", "completed_at": "2025-12-07T23:15:00Z"},
    {"id": "STEP-002", "description": "Create conftest.py", "status": "in_progress", "completed_at": null},
    {"id": "STEP-003", "description": "Update pyproject.toml", "status": "pending", "completed_at": null}
  ],
  "progress": {
    "total": 18,
    "complete": 5,
    "in_progress": 1,
    "pending": 12,
    "blocked": 0,
    "percent": 28
  },
  "details": {
    "forbidden_files": ["server.py", "tool_handlers.py"],
    "allowed_files": ["tests/**/*.py", "pyproject.toml"]
  },
  "agent_2_status": "ASSIGNED",
  "agent_2_workorder_id": "WO-AUTH-SYSTEM-002"
}
```

**Task Status Values**: `pending` | `in_progress` | `complete` | `blocked`

**Key Benefits**:
- **Single Source of Truth**: communication.json is where task status lives
- **Real-time Progress**: Lloyd checks progress anytime via `progress.percent`
- **Conflict Prevention**: Forbidden files prevent agents from stepping on each other
- **Traceability**: Each agent has unique workorder for audit trail
- **Verification**: Automated checks ensure quality before merge

---

#### `/archive-feature` **NEW in v1.10.0**
Archive completed features from coderef/working/ to coderef/archived/.
- Asks user for feature name
- Calls `archive_feature` with current directory and feature name
- Checks DELIVERABLES.md status and prompts if status != Complete
- Moves entire feature folder using shutil.move()
- Updates archive index.json with metadata

```bash
# User types: /archive-feature
# Claude asks for feature name
# Checks status and archives feature folder
# Updates coderef/archived/index.json
```

**Status Handling:**
- ✅ Complete → Archives immediately without confirmation
- 🚧 In Progress / Not Started → Prompts user for confirmation
- UNKNOWN (no DELIVERABLES.md) → Prompts user for confirmation

**What gets archived:**
- Entire feature folder with ALL files preserved
- plan.json, DELIVERABLES.md, communication.json, context.json
- All implementation artifacts and working files

**Safety Features:**
- Checks if feature exists before archiving
- Prevents duplicate archives (error if already exists)
- Atomic folder relocation using shutil.move()
- Updates searchable archive index

**When to use:**
Run AFTER completing feature implementation and running /update-deliverables.

#### `/execute-plan` **NEW in v2.5.0**
Generate TodoWrite task list from plan.json with TASK-ID first format for Lloyd's CLI checklist display.
- Asks user for feature name
- Calls `execute_plan` with current directory and feature name
- Reads plan.json from coderef/working/{feature}/
- Extracts workorder_id from META_DOCUMENTATION section
- Parses all tasks from section 9 (9_implementation_checklist)
- Generates TodoWrite format: `TASK-ID: Description`
- Creates activeForm field with gerund conversion (Install → Installing)
- Logs execution to execution-log.json with timestamp
- Detects task status from checkboxes (☐/☑/⏳/🚫)

```bash
# User types: /execute-plan
# Claude asks for feature name
# Generates TodoWrite task list with TASK-ID first
# Example output:
# SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
# SETUP-002: Create auth/ directory structure
# PARSER-001: Implement load_plan() function
```

**Workorder Display:**
- Workorder name displayed at top of TodoWrite list
- Individual tasks show TASK-ID first: `SETUP-001: Description`
- Active form shows: `SETUP-001: Installing dependencies`
- Status preserved from plan: pending, in_progress, completed, blocked

**Output Format:**
```json
{
  "workorder_id": "WO-AUTH-001",
  "workorder_name": "Authentication System",
  "tasks": [
    {
      "content": "SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1",
      "activeForm": "SETUP-001: Installing dependencies",
      "status": "pending"
    }
  ]
}
```

**When to use:**
Run AFTER /create-plan to generate formatted task list for execution. Lloyd uses this to display organized checklists in CLI.

#### `/log-workorder` **NEW in v2.6.0**
Manually log workorder to global workorder activity log.
- Asks user for workorder_id, project, and description
- Calls `log_workorder` with provided parameters
- Appends entry to `coderef/workorder-log.txt` (latest first)
- Format: `WO-ID | Project | Description | Timestamp`
- Auto-timestamps with ISO 8601 format

```bash
# User types: /log-workorder
# Claude asks for: workorder_id, project, description
# Logs to coderef/workorder-log.txt
```

**Note:** Most tools auto-log on completion, so manual logging is rarely needed.

**When to use:**
- Custom workorders outside standard workflow
- Retroactive logging of work
- Testing workorder-log functionality

#### `/get-workorder-log` **NEW in v2.6.0**
View and query the global workorder activity log.
- Optionally asks user for filters: project_name, workorder_pattern, limit
- Calls `get_workorder_log` with current directory and filters
- Returns entries in reverse chronological order (latest first)
- Shows total count and filtered count

```bash
# View all workorders
/get-workorder-log

# Filter by project
/get-workorder-log
# project_name: docs-mcp

# Filter by pattern
/get-workorder-log
# workorder_pattern: WO-AUTH

# Get latest 10
/get-workorder-log
# limit: 10
```

**Output:**
```json
{
  "entries": [
    {
      "workorder_id": "WO-AUTH-001",
      "project": "docs-mcp",
      "description": "Implement authentication system",
      "timestamp": "2025-10-21T02:08:51+00:00"
    }
  ],
  "total_count": 50,
  "filtered_count": 1,
  "log_file": "coderef/workorder-log.txt"
}
```

**When to use:**
- View recent project activity
- Find workorders for specific projects
- Quick project status overview
- Search workorder history

#### `/generate-handoff-context` (renamed from /handoff)
Generate automated agent handoff context files for seamless agent transitions.
- Asks user for feature name
- Optionally asks for mode (full/minimal, default: full)
- Calls `generate_handoff_context` with current directory, feature name, and mode
- Auto-populates 80%+ context fields from plan.json, analysis.json, and git history
- Generates `coderef/working/{feature}/claude.md`

```bash
# Generate full handoff context
/generate-handoff-context
# feature_name: auth-system
# mode: full

# Generate minimal handoff context
/generate-handoff-context
# feature_name: auth-system
# mode: minimal
```

**What gets auto-populated:**
- Workorder ID from plan.json
- Project overview and goals
- Current progress (completed/total tasks)
- Current phase detection from task status
- Recent git commits matching feature name
- Uncommitted changes (git status)
- Next 3 pending tasks from checklist
- Technology stack from analysis.json
- File references (plan, context, analysis paths)

**Output Example** (`coderef/working/auth-system/claude.md`):
```markdown
# Agent Handoff Context: auth-system

**Generated:** 2025-10-23T03:38:47
**Workorder:** WO-AUTH-SYSTEM-001
**Mode:** full

## 📋 Project Overview
JWT authentication system with refresh tokens...

## ✅ Current Progress
**Completed Tasks:** 12 / 27
**Current Phase:** Phase 2 Implementation

### Recent Commits
abc123 Add login endpoint
def456 Implement JWT validation

## 🚧 Work In Progress
M src/auth.py
M tests/test_auth.py

## ⏭️ Next Steps
1. IMPL-003: Add refresh token logic
2. IMPL-004: Implement logout endpoint
3. TEST-002: Write integration tests
```

**When to use:**
- Before passing feature work to another agent
- Mid-phase checkpoints for progress documentation
- Creating quick context summaries (minimal mode)
- Agent handoff time < 5 minutes (vs 20-30 minutes manual)

**Reduces handoff time from 20-30 minutes to under 5 minutes** by automatically extracting context from existing project files.

#### `/llm-prompt` **NEW in v2.9.0**
Generate a structured LLM prompt for multi-LLM querying with consistent JSON output.
- Asks user for feature name (used for folder in `coderef/working/{feature}/`)
- Asks user for task type (code-review, architecture, security-audit, implementation, refactor)
- Generates structured prompt with JSON output schema
- Saves to `coderef/working/{feature}/llm-prompt.json`

```bash
# User types: /llm-prompt
# Claude asks for feature name and task type
# Generates llm-prompt.json with structured JSON schema
# User copies prompt to ChatGPT, Claude, Gemini
```

**Task Types:**
- `code-review` - Analyze code for issues and improvements
- `architecture` - Evaluate design and suggest patterns
- `security-audit` - Identify vulnerabilities and risks
- `implementation` - Suggest approaches for requirements
- `refactor` - Identify improvement opportunities

**When to use:**
- Before code reviews requiring multiple perspectives
- Architecture decisions needing diverse input
- Security audits where consensus matters

#### `/consolidate` **NEW in v2.9.0**
Parse and consolidate multiple LLM responses into unified output.
- Asks user for feature name
- Asks user for output formats (json, markdown, html)
- Reads responses from `coderef/working/{feature}/llm-responses.txt`
- Merges all LLM responses into `coderef/working/{feature}/llm-consolidated.json`

```bash
# User types: /consolidate
# Claude asks for feature name and output formats
# Parses llm-responses.txt with LLM markers
# Generates consolidated output with:
# - Merged findings (consensus tracking)
# - Unique insights (single-source findings)
# - Conflicts (where LLMs disagreed)
# - Aggregated metrics
```

**Response File Format** (`llm-responses.txt`):
```text
=== ChatGPT ===
{ JSON response }

=== Claude ===
{ JSON response }

=== Gemini ===
{ JSON response }
```

**Output Structure:**
- `findings.merged` - Findings multiple LLMs agreed on
- `findings.unique` - Insights only one LLM caught (worth extra attention)
- `conflicts` - Where LLMs disagreed (needs human decision)
- `metrics.aggregated` - Averaged confidence scores

**When to use:**
- After collecting responses from multiple LLMs
- Before creating implementation plans based on multi-LLM review
- When consensus or unique insights are valuable

**When to use slash commands:**
- Faster than typing full MCP tool names
- User-friendly shortcuts for common workflows
- Pre-configured with sensible defaults
- Automatically uses current working directory

**When to use MCP tools directly:**
- Need fine-grained control over parameters
- Custom scan depth, filters, or scopes
- Programmatic access from other tools
- Building complex automation workflows

### Deploying Slash Commands Globally

**CRITICAL: Slash commands must be deployed to `~/.claude/commands/` to work across all projects.**

#### Understanding Command Directories

Slash commands can exist in two locations:

1. **Project-Local** (`.claude/commands/` in project root)
   - Only available when working in that specific project
   - Useful for project-specific workflows
   - Not accessible from other projects

2. **Global** (`~/.claude/commands/` in user home directory)
   - Available in ALL projects
   - Persists across Claude Code sessions
   - **Recommended location for docs-mcp commands**

#### Current Deployment Status

**Globally Deployed** (12 commands in `~/.claude/commands/`):
- ✅ analyze-for-planning
- ✅ audit-codebase
- ✅ check-consistency
- ✅ create-plan
- ✅ establish-standards
- ✅ gather-context
- ✅ generate-docs
- ✅ generate-plan-review
- ✅ generate-quickref
- ✅ generate-user-guide
- ✅ get-planning-template
- ✅ validate-plan

**Missing from Global** (16 commands - need deployment):
- ❌ archive-feature **NEW**
- ❌ generate-agent-communication **NEW**
- ❌ assign-agent-task **NEW**
- ❌ verify-agent-completion **NEW**
- ❌ aggregate-agent-deliverables **NEW**
- ❌ track-agent-status **NEW**
- ❌ add-changelog
- ❌ get-changelog
- ❌ update-changelog
- ❌ inventory-manifest
- ❌ dependency-inventory
- ❌ api-inventory
- ❌ database-inventory
- ❌ generate-my-guide
- ❌ list-templates
- ❌ get-template

**Inventory Commands** (6 commands in `.claude/commands/` - deployment ready):
- ✅ documentation-inventory
- ✅ inventory-manifest
- ✅ dependency-inventory
- ✅ api-inventory
- ✅ database-inventory
- ✅ test-inventory

#### Deployment Commands

**Deploy all 28 commands globally:**

```bash
# Navigate to docs-mcp project
cd ~/.mcp-servers/docs-mcp

# Copy ALL commands to global directory
cp .claude/commands/*.md ~/.claude/commands/

# Copy commands registry (optional but recommended)
cp .claude/commands.json ~/.claude/

# Verify deployment
ls -l ~/.claude/commands/*.md | wc -l  # Should show 33 files
```

**Deploy specific command:**

```bash
# Example: Deploy changelog commands
cp ~/.mcp-servers/docs-mcp/.claude/commands/add-changelog.md ~/.claude/commands/
cp ~/.mcp-servers/docs-mcp/.claude/commands/get-changelog.md ~/.claude/commands/
cp ~/.mcp-servers/docs-mcp/.claude/commands/update-changelog.md ~/.claude/commands/
cp ~/.mcp-servers/docs-mcp/.claude/commands/update-docs.md ~/.claude/commands/
```

**Deploy inventory commands (NEW in v1.8.0):**

```bash
# Deploy all 4 inventory commands
cp ~/.mcp-servers/docs-mcp/.claude/commands/inventory-manifest.md ~/.claude/commands/
cp ~/.mcp-servers/docs-mcp/.claude/commands/dependency-inventory.md ~/.claude/commands/
cp ~/.mcp-servers/docs-mcp/.claude/commands/api-inventory.md ~/.claude/commands/
cp ~/.mcp-servers/docs-mcp/.claude/commands/database-inventory.md ~/.claude/commands/
```

#### Verification

After deployment, verify commands are available:

```bash
# List all global commands
ls ~/.claude/commands/*.md

# Count total commands
ls ~/.claude/commands/*.md | wc -l

# Search for specific command
ls ~/.claude/commands/ | grep changelog
```

Then reload Claude Code:
- `Ctrl+Shift+P` → "Developer: Reload Window"
- Type `/` in chat to see autocomplete list
- All 22 commands should appear

#### Maintenance Workflow

**When adding a new slash command:**

1. Create command file in `docs-mcp/.claude/commands/`
   ```bash
   # Example: new-command.md
   echo "Description of new command" > .claude/commands/new-command.md
   ```

2. Update `commands.json` registry
   ```json
   {
     "commands": [
       {
         "name": "new-command",
         "description": "Description",
         "category": "appropriate-category"
       }
     ]
   }
   ```

3. **DEPLOY GLOBALLY** (don't forget this step!)
   ```bash
   cp .claude/commands/new-command.md ~/.claude/commands/
   cp .claude/commands.json ~/.claude/
   ```

4. Update documentation
   - Add to this CLAUDE.md section
   - Update README.md slash commands section
   - Update `.claude/commands/README.md`

5. Commit changes
   ```bash
   git add .claude/commands/new-command.md .claude/commands.json
   git commit -m "Add /new-command slash command"
   ```

#### Troubleshooting

**Command doesn't appear in autocomplete:**
1. Check file exists: `ls ~/.claude/commands/new-command.md`
2. Verify file has `.md` extension
3. Reload Claude Code window
4. Check for syntax errors in command file
5. Try typing full command manually: `/new-command`

**Command exists but doesn't work:**
1. Check first line is the description (used for autocomplete)
2. Verify MCP tool name is correct in command body
3. Ensure MCP server is running
4. Check tool is registered in `server.py`

**Commands work in docs-mcp but not other projects:**
- Commands are in `.claude/commands/` (project-local)
- Need to copy to `~/.claude/commands/` (global)
- Run deployment commands above

### Usage Patterns

#### Pattern 1: Generate Project Documentation

```python
# User: "Generate documentation for my project at C:\path\to\my-project"

# Step 1: List available templates
mcp__docs_mcp__list_templates()
# Returns: readme, architecture, api, components, my-guide, schema, user-guide

# Step 2: Generate all foundation docs
mcp__docs_mcp__generate_foundation_docs(
    project_path="C:/path/to/my-project"
)
# Returns: Templates + generation plan

# Step 3: YOU generate and save the actual documents
# - Analyze the project code
# - Fill in the templates with project-specific details
# - Save to the paths specified in the response
```

**Key insight**: The tool gives you templates and instructions. **You** do the actual content generation using your context of the project.

#### Pattern 2: Self-Document Your Changes (Agentic Workflow)

```python
# After you've made changes to a project

# Option A: Autonomous workflow (recommended)
mcp__docs_mcp__update_changelog(
    project_path="C:/path/to/project",
    version="1.0.3"
)
# Returns: 3-step instruction guide

# YOU then:
# 1. Analyze what you changed (you have context!)
# 2. Determine change_type and severity
# 3. Call add_changelog_entry with details

# Option B: Direct entry (if you already know details)
mcp__docs_mcp__add_changelog_entry(
    project_path="C:/path/to/project",
    version="1.0.3",
    change_type="enhancement",  # bugfix|enhancement|feature|breaking_change|deprecation|security
    severity="minor",            # critical|major|minor|patch
    title="Improved error handling in authentication module",
    description="Added retry logic and better error messages for auth failures",
    files=["src/auth.py", "tests/test_auth.py"],
    reason="Users reported confusing error messages during network issues",
    impact="Users now see clear error messages and automatic retry on transient failures",
    breaking=false,
    contributors=["Claude"]
)
```

#### Pattern 3: Query Changelog History

```python
# Get full changelog
mcp__docs_mcp__get_changelog(
    project_path="C:/path/to/project"
)

# Get specific version details
mcp__docs_mcp__get_changelog(
    project_path="C:/path/to/project",
    version="1.0.2"
)

# Find all breaking changes
mcp__docs_mcp__get_changelog(
    project_path="C:/path/to/project",
    breaking_only=true
)

# Filter by change type
mcp__docs_mcp__get_changelog(
    project_path="C:/path/to/project",
    change_type="security"
)
```

#### Pattern 4: Consistency Management ("Trilogy Workflow")

```python
# User: "Extract standards from my React project and audit it for consistency"

# Step 1: Extract standards from existing codebase
mcp__docs_mcp__establish_standards(
    project_path="C:/path/to/react-project"
)
# Returns: {
#   "files": [
#     "coderef/standards/UI-STANDARDS.md",
#     "coderef/standards/BEHAVIOR-STANDARDS.md",
#     "coderef/standards/UX-PATTERNS.md",
#     "coderef/standards/COMPONENT-INDEX.md"
#   ],
#   "patterns_count": 47,
#   "ui_patterns_count": 18,
#   "behavior_patterns_count": 12,
#   "ux_patterns_count": 8,
#   "components_count": 23,
#   "success": true
#}

# Step 2: Audit codebase against extracted standards
mcp__docs_mcp__audit_codebase(
    project_path="C:/path/to/react-project",
    standards_dir="coderef/standards",  # Optional, defaults to this
    severity_filter="all",               # critical|major|minor|all
    scope=["all"],                       # ui_patterns|behavior_patterns|ux_patterns|all
    generate_fixes=true
)
# Returns: {
#   "report_path": "coderef/audits/audit-20251010-143022.md",
#   "compliance_score": 82,
#   "compliance_details": {
#     "overall_score": 82,
#     "ui_compliance": 85,
#     "behavior_compliance": 78,
#     "ux_compliance": 83,
#     "grade": "B",
#     "passing": true
#   },
#   "violation_stats": {
#     "total_violations": 18,
#     "critical_count": 0,
#     "major_count": 4,
#     "minor_count": 14,
#     "most_violated_file": "src/components/Button.tsx",
#     "most_common_violation": "non_standard_button_size"
#   },
#   "success": true
#}

# Step 3: Apply filters for focused auditing
mcp__docs_mcp__audit_codebase(
    project_path="C:/path/to/react-project",
    severity_filter="critical",          # Only show critical violations
    scope=["ui_patterns", "ux_patterns"] # Skip behavior patterns
)

# Step 4: Fix violations and re-audit
# YOU: Fix the violations reported in the audit
# Then re-run audit to verify improvements
mcp__docs_mcp__audit_codebase(
    project_path="C:/path/to/react-project"
)
# Should show improved compliance score
```

**Key insights:**
- **Living standards** - Standards are extracted from actual code, not written manually
- **Objective scoring** - Compliance is quantifiable (0-100 score, A-F grade)
- **Iterative improvement** - Fix violations → re-audit → verify improvement
- **Technical debt tracking** - Track compliance over time as project evolves

**When to use this workflow:**
- Starting a new project (extract standards from reference codebase)
- Code reviews (audit before merging)
- Refactoring (ensure consistency is maintained)
- Onboarding (understand project's coding standards)
- CI/CD integration (fail build if compliance < threshold)

#### Pattern 5: Planning Workflow Review Loop (Procedural AI Pattern)

```python
# User: "Create an implementation plan for adding user authentication"

# Step 1: Gather context (optional but recommended)
# Use /gather-context to collect feature requirements
# Saves to coderef/working/{feature_name}/context.json

# Step 2: Analyze project for planning context
mcp__docs_mcp__analyze_project_for_planning(
    project_path="C:/path/to/project"
)
# Returns: Foundation docs, standards, patterns, tech stack, gaps

# Step 3: Create implementation plan (NEW!)
mcp__docs_mcp__create_plan(
    project_path="C:/path/to/project",
    feature_name="auth-system"
)
# Returns: {
#   "plan_path": "coderef/working/auth-system/plan.json",
#   "feature_name": "auth-system",
#   "sections_completed": ["0_preparation", "1_executive_summary", ...],
#   "status": "complete",
#   "has_context": true,
#   "has_analysis": true,
#   "next_steps": ["Validate plan with /validate-plan"],
#   "success": true
# }
# Generates complete 10-section plan in batch mode
# Loads context.json and analysis automatically
# Uses AI-optimized template (63% smaller than full template)

# Step 4: Validate the plan
mcp__docs_mcp__validate_implementation_plan(
    project_path="C:/path/to/project",
    plan_file_path="coderef/working/auth-system/plan.json"
)
# Returns: {
#   "score": 75,
#   "validation_result": "NEEDS_REVISION",
#   "issues": [...],
#   "approved": false
# }

# Step 5: Review loop (if score < 90)
# YOU iteratively refine the plan based on issues:
# - Fix critical issues first (missing sections, circular dependencies)
# - Fix major issues (placeholders, vague criteria)
# - Fix minor issues (short descriptions)
# - Re-validate after each refinement
# - Repeat until score >= 90 (max 5 iterations)

# Step 6: Generate review report
mcp__docs_mcp__generate_plan_review_report(
    project_path="C:/path/to/project",
    plan_file_path="coderef/working/auth-system/plan.json"
)
# Returns: Markdown report with score, issues, recommendations

# Step 7: Present to user for approval
# - Show the plan and review report
# - If score >= 90: Plan is approved, ready for implementation
# - If score < 90: Continue refinement
```

**Review Loop Workflow:**
- **Approval Threshold**: Score >= 90 (plans below 90 require revision)
- **Max Iterations**: Up to 5 refinement cycles
- **Scoring**: 100 - (10*critical + 5*major + 1*minor)
- **Result Types**: PASS (>=90), PASS_WITH_WARNINGS (>=85), NEEDS_REVISION (>=70), FAIL (<70)

**When to use this workflow:**
- Before implementing any non-trivial feature
- For architectural changes requiring careful planning
- When creating implementation guides for other developers
- To ensure autonomous AI agents have clear, complete plans

**Key insight**: This is a **procedural** workflow (not programmatic). The AI agent drives the review loop by checking scores, analyzing issues, refining the plan, and re-validating until the quality threshold is met.

### The "Meta-Tool" Pattern

`update_changelog` is a **meta-tool**: it doesn't perform actions directly, but **instructs you** to perform a workflow using your context.

**Why this works:**
- You have full context of recent changes (file diffs, conversation history)
- You can analyze and categorize changes better than any tool
- The meta-tool just guides you through the process

**When to use meta-tools:**
- `update_changelog` - After you've made code changes
- (Future) `update_docs` - After refactoring/adding features
- (Future) `review_documentation` - To validate docs match code

### Critical Rules for Tool Usage

1. **Always use absolute paths** - `C:/path/to/project`, not `./project`
2. **Templates are guides, not final content** - You fill in project-specific details
3. **Changelog requires all fields** - version, change_type, severity, title, description, files, reason, impact
4. **Version format is strict** - `1.0.3`, not `v1.0.3` or `1.0.3-beta`
5. **Read before write** - Call `get_changelog` before `add_changelog_entry` to understand context

### Common Mistakes to Avoid

❌ **Using relative paths**
```python
generate_foundation_docs(project_path="./my-project")  # WRONG
```

✅ **Use absolute paths**
```python
generate_foundation_docs(project_path="C:/Users/willh/my-project")  # CORRECT
```

❌ **Expecting tools to write files for you**
```python
# Tools return TEMPLATES and PLANS, not final documents
# YOU generate the actual content using your understanding of the project
```

✅ **Understanding tool outputs**
```python
# Tool gives you: Template + Instructions
# You provide: Project analysis + Content generation
# Result: Professional documentation that actually describes the project
```

---

## For AI Assistants Developing This Server

### Critical: Correct MCP Tool Usage

When working **on this codebase** (not just using the tools):

#### ❌ WRONG - Direct Python Access
```python
from generators.changelog_generator import ChangelogGenerator
gen = ChangelogGenerator(Path('.'))
gen.add_change(...)  # DON'T DO THIS when developing
```

#### ✅ CORRECT - Use MCP Tool Handlers
```python
import tool_handlers
await tool_handlers.handle_add_changelog_entry(arguments)  # Use handler
```

**Why?** Testing the actual MCP tool flow ensures:
- Input validation works
- Error handling works
- Logging works
- Schema validation works

### Design Patterns (Architecture)

#### 1. ErrorResponse Factory (ARCH-001)
All errors use consistent factory methods:

```python
from error_responses import ErrorResponse

# Invalid input
return ErrorResponse.invalid_input(
    "Project path must be absolute",
    "Use C:/path/to/project instead of ./project"
)

# Not found
return ErrorResponse.not_found(
    "Template 'foo'",
    "Available: readme, architecture, api, components, my-guide, schema, user-guide"
)

# Permission denied (security)
return ErrorResponse.permission_denied(
    "Cannot access /etc/passwd",
    "Check file permissions"
)

# Generic error
return ErrorResponse.generic_error(
    f"Unexpected error: {str(e)}"
)
```

**Available methods:**
- `invalid_input(error, suggestion)`
- `not_found(resource, suggestion)`
- `permission_denied(error, suggestion)`
- `io_error(error, suggestion)`
- `encoding_error(error, suggestion)`
- `malformed_json(error)`
- `validation_failed(validation_error)`
- `generic_error(error)`

#### 2. No Magic Strings (REF-002, QUA-003)
Use constants and enums:

```python
from constants import Paths, Files, TemplateNames, ChangeType, Severity

# Paths
changelog_dir = project_path / Paths.CHANGELOG_DIR  # "coderef/changelog"
output_dir = project_path / Paths.FOUNDATION_DOCS   # "coderef/foundation-docs"

# Files
changelog_file = changelog_dir / Files.CHANGELOG    # "CHANGELOG.json"
schema_file = changelog_dir / Files.SCHEMA          # "schema.json"

# Enums
if change_type not in ChangeType.values():
    raise ValueError(f"Invalid change_type: {change_type}")
```

#### 3. TypedDict for Complex Returns (QUA-001)
Define return types in `type_defs.py`:

```python
from type_defs import ChangelogEntry, TemplateInfo, GenerationPaths

def get_template_info(name: str) -> TemplateInfo:
    return {
        'template_name': name,
        'save_as': f'{name.upper()}.md',
        'description': '...'
    }
```

#### 4. Handler Registry Pattern (QUA-002)
Tools dispatch via registry:

```python
# In tool_handlers.py
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    'generate_foundation_docs': handle_generate_foundation_docs,
    # ... etc
}

# In server.py
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = tool_handlers.TOOL_HANDLERS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(arguments)
```

#### 5. Decorator Pattern for Handlers (ARCH-004, ARCH-005)
All handlers use standardized decorators for error handling and logging:

**Location**: Decorators extracted to `handler_decorators.py`, helper functions in `handler_helpers.py`

```python
from handler_decorators import mcp_error_handler, log_invocation
from handler_helpers import format_success_response

# Apply decorators in correct order (log_invocation first, then mcp_error_handler)
@log_invocation          # ARCH-005: Automatic invocation logging
@mcp_error_handler       # ARCH-004: Centralized error handling
async def handle_my_tool(arguments: dict) -> list[TextContent]:
    """Handle my_tool tool call."""
    # Validate inputs
    project_path = validate_project_path_input(arguments.get("project_path"))

    # Do work - can raise exceptions freely
    result = do_work(project_path)

    # Return formatted response
    return format_success_response(
        data={'files': files_list, 'count': len(files_list)},
        message="✅ Operation completed successfully"
    )
```

**@mcp_error_handler Benefits:**
- Automatically catches and logs all exceptions with handler context
- Maps exceptions to appropriate ErrorResponse factory methods
- Eliminates repetitive try/except blocks (saves ~20-30 lines per handler)
- Ensures consistent error response format across all tools

**Exception Mapping:**
- `ValueError` → `ErrorResponse.invalid_input`
- `PermissionError` → `ErrorResponse.permission_denied` (logged as security event)
- `FileNotFoundError` → `ErrorResponse.not_found`
- `IOError` → `ErrorResponse.io_error`
- `UnicodeDecodeError` → `ErrorResponse.encoding_error`
- `json.JSONDecodeError` → `ErrorResponse.malformed_json`
- `jsonschema.ValidationError` → `ErrorResponse.validation_failed`
- `Exception` (catch-all) → `ErrorResponse.generic_error`

**@log_invocation Benefits:**
- Automatically logs tool invocations at entry with handler name and argument keys
- Eliminates manual `log_tool_call()` invocations (saves 1 line per handler)
- Provides audit trail for debugging and monitoring
- Performance overhead: <0.05ms per call (well under 1ms target)

**format_success_response() Helper:**
- Consistent JSON formatting with optional success message
- Reduces boilerplate for standard success responses
- Supports nested data structures, arrays, special characters

**Decorator Stacking Order (Critical):**
1. **@log_invocation** (outermost) - Logs invocation before error handling
2. **@mcp_error_handler** (inner) - Wraps execution with error handling

**Backward Compatibility:**
- All 21 handlers refactored to use decorators (Phase 1 complete)
- Decorators extracted to separate modules (Phase 2 complete)
- 29/29 tests passing (19 decorator + 10 helper tests)
- Zero functionality changes - 100% backward compatible

**Impact:**
- Reduced tool_handlers.py from 2168 → 1679 lines (-489 lines, -22.5%)
- Eliminated ~600 lines of try/except blocks
- Eliminated ~21 manual log_tool_call() invocations
- Improved maintainability and consistency across all handlers

#### 6. Structured Logging (ARCH-003)
All operations logged:

```python
from logger_config import logger, log_tool_call, log_error, log_security_event

# Tool invocation
log_tool_call('my_tool', args_keys=list(arguments.keys()))

# Errors
log_error('validation_error', str(e), project_path=path)

# Security events
log_security_event('path_traversal_attempt', str(e), path=dangerous_path)

# General logging
logger.info("Operation completed", extra={'version': version, 'count': 5})
logger.debug("Reading template", extra={'template_name': name})
logger.warning("Template not found", extra={'template_name': name})
```

#### 7. Input Validation at Boundaries (REF-003)
Validate all MCP inputs:

```python
from validation import (
    validate_project_path_input,
    validate_version_format,
    validate_template_name_input,
    validate_changelog_inputs
)

# Validate paths (raises ValueError if invalid)
project_path = validate_project_path_input(arguments.get("project_path"))

# Validate version (raises ValueError if not X.Y.Z format)
version = validate_version_format(arguments.get("version"))

# Validate template name (raises ValueError if contains path traversal)
template_name = validate_template_name_input(arguments.get("template_name"))

# Validate all changelog fields at once
validated = validate_changelog_inputs(
    version=arguments.get("version"),
    change_type=arguments.get("change_type"),
    severity=arguments.get("severity"),
    # ... etc
)
```

### Security (Critical Implementation Details)

- **SEC-001**: Path traversal protection
  ```python
  path = Path(user_input).resolve()  # Canonicalize ALL user paths
  ```

- **SEC-002**: JSON schema validation
  ```python
  # Automatic on all changelog operations via ChangelogGenerator
  generator.add_change(...)  # Validates against schema.json
  ```

- **SEC-003**: Smart output routing
  ```python
  # README.md → project root
  # All others → coderef/foundation-docs/
  if template_name == 'readme':
      output_path = project_path / 'README.md'
  else:
      output_path = project_path / Paths.FOUNDATION_DOCS / f'{template_name.upper()}.md'
  ```

- **SEC-005**: Template name sanitization
  ```python
  # Regex: ^[a-zA-Z0-9_-]+$
  # Prevents: ../../../etc/passwd
  ```

### Standard Handler Pattern

```python
from mcp.types import TextContent
from error_responses import ErrorResponse
from logger_config import log_tool_call, log_error, log_security_event
from validation import validate_project_path_input
import json

async def handle_my_tool(arguments: dict) -> list[TextContent]:
    """Handle my_tool tool call."""
    try:
        # Log invocation
        log_tool_call('my_tool', args_keys=list(arguments.keys()))

        # Validate inputs at boundary
        project_path = validate_project_path_input(arguments.get("project_path", ""))

        # Log operation start
        logger.info(f"Starting my_tool operation", extra={'project_path': project_path})

        # Do work
        result = do_work(project_path)

        # Log success
        logger.info("my_tool completed successfully")

        # Return structured response
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except ValueError as e:
        log_error('my_tool_validation_error', str(e), project_path=project_path)
        return ErrorResponse.invalid_input(
            str(e),
            "Helpful suggestion for user"
        )
    except PermissionError as e:
        log_security_event('permission_denied', str(e), project_path=project_path)
        return ErrorResponse.permission_denied(
            str(e),
            "Check file permissions"
        )
    except Exception as e:
        log_error('my_tool_error', str(e), project_path=project_path)
        return ErrorResponse.generic_error(
            f"Failed to execute my_tool: {str(e)}"
        )
```

---

## Tool Catalog

### Documentation Generation Tools

#### `list_templates`
**Purpose**: List all available POWER framework templates

**Input**: None

**Output**: Text list of template names

**Example**:
```python
list_templates()
# Returns:
# Available POWER Framework Templates:
# 1. api
# 2. architecture
# 3. components
# 4. readme
# 5. schema
# 6. user-guide
# Total: 6 templates (5 foundation docs + 1 optional)
```

---

#### `get_template`
**Purpose**: Retrieve content of a specific template

**Input**:
- `template_name` (string, required): One of: readme, architecture, api, components, my-guide, schema, user-guide

**Output**: Template content as text

**Example**:
```python
get_template(template_name="readme")
# Returns: Full README.txt template content
```

---

#### `generate_foundation_docs`
**Purpose**: Generate all foundation documentation for a project

**Input**:
- `project_path` (string, required): Absolute path to project directory

**Output**: All templates + generation plan + save locations

**Example**:
```python
generate_foundation_docs(project_path="C:/Users/willh/my-project")
# Returns:
# - Generation plan
# - 5 foundation document templates (README, ARCHITECTURE, API, COMPONENTS, SCHEMA)
# - Save locations for each document
# - Instructions for AI to follow
# Note: USER-GUIDE.md is optional and generated separately using generate_individual_doc
```

**Important**: This tool returns templates and instructions. The AI assistant must:
1. Analyze the project code
2. Fill in templates with project-specific details
3. Save documents to specified locations

---

#### `generate_individual_doc`
**Purpose**: Generate a single documentation file

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `template_name` (string, required): readme, architecture, api, components, schema, or user-guide

**Output**: Template + generation instructions for single document

**Example**:
```python
generate_individual_doc(
    project_path="C:/Users/willh/my-project",
    template_name="api"
)
# Returns:
# - API template
# - Output path
# - Generation instructions
```

---

### Changelog Management Tools

#### `get_changelog`
**Purpose**: Query project changelog with optional filters

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `version` (string, optional): Get specific version (e.g., "1.0.2")
- `change_type` (string, optional): Filter by type (bugfix, enhancement, feature, breaking_change, deprecation, security)
- `breaking_only` (boolean, optional): Show only breaking changes

**Output**: JSON-formatted changelog data

**Examples**:
```python
# Get full changelog
get_changelog(project_path="C:/path/to/project")

# Get specific version
get_changelog(project_path="C:/path/to/project", version="1.0.2")

# Get all breaking changes
get_changelog(project_path="C:/path/to/project", breaking_only=true)

# Filter by type
get_changelog(project_path="C:/path/to/project", change_type="security")
```

---

#### `add_changelog_entry`
**Purpose**: Add a new entry to the project changelog

**Input** (all required except noted):
- `project_path` (string): Absolute path to project directory
- `version` (string): Version number (format: X.Y.Z, e.g., "1.0.3")
- `change_type` (string): bugfix | enhancement | feature | breaking_change | deprecation | security
- `severity` (string): critical | major | minor | patch
- `title` (string): Short title of the change
- `description` (string): Detailed description of what changed
- `files` (array of strings): List of files affected
- `reason` (string): Why this change was made
- `impact` (string): Impact on users/system
- `breaking` (boolean, optional): Whether this is a breaking change (default: false)
- `migration` (string, optional): Migration guide if breaking change
- `summary` (string, optional): Version summary for new versions
- `contributors` (array of strings, optional): List of contributors

**Output**: Confirmation with change ID

**Example**:
```python
add_changelog_entry(
    project_path="C:/path/to/project",
    version="1.0.3",
    change_type="enhancement",
    severity="minor",
    title="Improved error handling in authentication",
    description="Added retry logic and better error messages for auth failures",
    files=["src/auth.py", "tests/test_auth.py"],
    reason="Users reported confusing error messages during network issues",
    impact="Users now see clear error messages and automatic retry on transient failures",
    breaking=false,
    contributors=["willh", "Claude"]
)
```

---

#### `update_changelog` (Meta-Tool)
**Purpose**: Agentic workflow tool that instructs AI to analyze changes and update changelog

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `version` (string, required): Version number for this change (format: X.Y.Z)

**Output**: 3-step instruction guide for AI

**Example**:
```python
update_changelog(
    project_path="C:/path/to/project",
    version="1.0.3"
)
# Returns:
# STEP 1: Analyze Your Changes
# STEP 2: Determine Change Details
# STEP 3: Call add_changelog_entry
# (Detailed instructions for AI to follow)
```

**How AI should respond**:
1. Review conversation context and recent file changes
2. Determine change_type and severity based on what was done
3. Call `add_changelog_entry` with appropriate details

---

#### `update_all_documentation`
**Purpose**: Update all project documentation (README, CLAUDE, CHANGELOG) with automatic version increment and workorder tracking

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `change_type` (string, required): Type of change - feature | bugfix | enhancement | breaking_change | security | deprecation
- `feature_description` (string, required): Description of what was changed (agent provides from context)
- `workorder_id` (string, required): Workorder ID for tracking (format: WO-{FEATURE}-{NUMBER})
- `files_changed` (array, optional): List of files modified
- `feature_name` (string, optional): Feature name for reference

**Output**: Success response with updated files and version bump

**Example**:
```python
update_all_documentation(
    project_path="C:/Users/willh/.mcp-servers/docs-mcp",
    change_type="feature",
    feature_description="Added update_all_documentation tool for automated doc updates",
    workorder_id="WO-UPDATE-DOCS-001",
    files_changed=["server.py", "tool_handlers.py", "handler_helpers.py"],
    feature_name="update-all-documentation"
)
# Returns:
# {
#   "updated_files": ["README.md", "CLAUDE.md", "CHANGELOG.json"],
#   "version_bump": "1.0.3 → 1.1.0",
#   "workorder_id": "WO-UPDATE-DOCS-001",
#   "success": true
# }
```

**Agentic Design**:
This tool is designed for AI agents who have full context of their work:
- Agent provides change details directly (no file parsing)
- Auto-increments version based on change type:
  - `breaking_change` → major bump (1.x.x → 2.0.0)
  - `feature` → minor bump (1.0.x → 1.1.0)
  - `bugfix`/`enhancement` → patch bump (1.0.0 → 1.0.1)
- Updates README.md version and "What's New" section
- Updates CLAUDE.md version history
- Adds CHANGELOG.json entry with workorder tracking

**Workflow Integration**:
```
Feature Implementation → /update-deliverables → /update-docs → /archive-feature
```

**When to use**:
- After completing feature implementation
- After running `/update-deliverables`
- Before running `/archive-feature`
- Agent has full context of what changed

---

### Consistency Management Tools

#### `establish_standards`
**Purpose**: Extract UI/behavior/UX patterns from codebase and generate standards documents

**Input**:
- `project_path` (string, required): Absolute path to project directory

**Output**: JSON with files created, pattern counts, and success status

**Example**:
```python
establish_standards(project_path="C:/path/to/react-project")
# Returns:
# {
#   "files": [
#     "coderef/standards/UI-STANDARDS.md",
#     "coderef/standards/BEHAVIOR-STANDARDS.md",
#     "coderef/standards/UX-PATTERNS.md",
#     "coderef/standards/COMPONENT-INDEX.md"
#   ],
#   "patterns_count": 47,
#   "ui_patterns_count": 18,
#   "behavior_patterns_count": 12,
#   "ux_patterns_count": 8,
#   "components_count": 23,
#   "success": true
# }
```

**What it extracts:**
- **UI Patterns**: Button sizes/variants, modal configs, colors, typography, spacing, icons
- **Behavior Patterns**: Error messages, loading states, toasts, validation rules, API patterns
- **UX Patterns**: Navigation, permissions, offline handling, accessibility (ARIA, keyboard)
- **Components**: Component inventory with usage counts, props, status (active/deprecated)

**Output files** (coderef/standards/):
- `UI-STANDARDS.md` - Visual component standards
- `BEHAVIOR-STANDARDS.md` - Interaction and state management standards
- `UX-PATTERNS.md` - User experience and accessibility standards
- `COMPONENT-INDEX.md` - Complete component catalog

---

#### `audit_codebase`
**Purpose**: Audit codebase for standards violations and generate compliance report

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `standards_dir` (string, optional): Path to standards directory (default: "coderef/standards")
- `severity_filter` (string, optional): Filter violations by severity - "critical" | "major" | "minor" | "all" (default: "all")
- `scope` (array, optional): Audit scope - ["ui_patterns", "behavior_patterns", "ux_patterns", "all"] (default: ["all"])
- `generate_fixes` (boolean, optional): Include fix suggestions in report (default: true)

**Output**: JSON with report path, compliance score, violation stats

**Example**:
```python
audit_codebase(
    project_path="C:/path/to/react-project",
    severity_filter="all",
    scope=["all"],
    generate_fixes=true
)
# Returns:
# {
#   "report_path": "coderef/audits/audit-20251010-143022.md",
#   "compliance_score": 82,
#   "compliance_details": {
#     "overall_score": 82,
#     "ui_compliance": 85,
#     "behavior_compliance": 78,
#     "ux_compliance": 83,
#     "grade": "B",
#     "passing": true
#   },
#   "violation_stats": {
#     "total_violations": 18,
#     "critical_count": 0,
#     "major_count": 4,
#     "minor_count": 14,
#     "violations_by_file": {...},
#     "violations_by_type": {...},
#     "most_violated_file": "src/components/Button.tsx",
#     "most_common_violation": "non_standard_button_size"
#   },
#   "violations": [...],  # Full list of violations
#   "scan_metadata": {
#     "timestamp": "2025-10-10T14:30:22",
#     "duration": 2.34,
#     "files_scanned": 127
#   },
#   "success": true
# }
```

**Compliance scoring:**
- Base score: 100
- Critical violation: -10 points
- Major violation: -5 points
- Minor violation: -1 point
- Grade: A (90-100), B (80-89), C (70-79), D (60-69), F (0-59)
- Passing: score >= 80

**Report sections:**
1. Executive Summary - Score, grade, pass/fail
2. Compliance by Category - UI/behavior/UX scores
3. Violations by Severity - Grouped by critical/major/minor
4. Violations by File - Hotspot analysis
5. Fix Recommendations - Actionable steps
6. Scan Metadata - Timestamp, duration, files scanned

**Violation types:**
- **UI**: Non-standard button sizes/variants, unapproved colors, typography issues
- **Behavior**: Non-standard error messages, missing loading states, improper validation
- **UX**: Missing ARIA attributes, keyboard navigation issues, inaccessible elements

---

### Planning Workflow Tools

#### `analyze_project_for_planning`
**Purpose**: Analyze project structure to discover foundation docs, standards, patterns, and tech stack for implementation planning

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `feature_name` (string, optional): Feature name for saving analysis to `coderef/working/{feature_name}/analysis.json`. If omitted, analysis is returned without saving. Alphanumeric, hyphens, and underscores only. Max 100 characters.

**Output**: JSON with analysis results and optional metadata (saved to feature folder when `feature_name` provided)

**Example (with feature_name - saves to file)**:
```python
analyze_project_for_planning(
    project_path="C:/path/to/project",
    feature_name="auth-system"
)
# Returns:
# {
#   "foundation_docs": {
#     "available": ["README.md", "ARCHITECTURE.md"],
#     "missing": ["API.md", "COMPONENTS.md"]
#   },
#   "coding_standards": {
#     "available": ["coderef/standards/UI-STANDARDS.md"],
#     "missing": []
#   },
#   "technology_stack": {
#     "language": "Python",
#     "framework": "FastAPI",
#     "testing": "pytest"
#   },
#   "key_patterns_identified": [
#     "Async/await pattern for I/O operations",
#     "Factory pattern for error responses"
#   ],
#   "project_structure": {
#     "organization_pattern": "modular",
#     "main_directories": ["src", "tests", "docs"]
#   },
#   "gaps_and_risks": [
#     "Missing API documentation",
#     "No integration tests found"
#   ],
#   "_metadata": {
#     "saved_to": "coderef/working/auth-system/analysis.json",
#     "feature_name": "auth-system",
#     "generated_at": "2025-10-14T15:30:22.123456"
#   }
# }
```

**Example (without feature_name - returns without saving)**:
```python
analyze_project_for_planning(
    project_path="C:/path/to/project"
)
# Returns analysis data WITHOUT _metadata field
# No files are created
```

**Feature-Specific Persistence**:
- When `feature_name` provided: Saves to `coderef/working/{feature_name}/analysis.json`
- When `feature_name` omitted: Returns analysis without saving (backward compatible)
- Creates feature working directory if it doesn't exist
- Returns file path in `_metadata.saved_to` (relative to project root)
- Includes `_metadata.feature_name` and `_metadata.generated_at` timestamp in ISO format
- **Graceful degradation**: Returns analysis data even if file save fails
- On file save failure: `_metadata.saved_to` is null, `_metadata.save_error` contains error message
- Multiple analyses with same `feature_name` overwrite previous file (no timestamps)

**Workflow Structure**:
```
coderef/working/{feature_name}/
├── context.json      # From /gather-context (optional)
├── analysis.json     # From this tool (NEW in v1.4.4)
└── plan.json         # From /create-plan
```

**Performance**:
- Analysis completes in ~80ms for typical projects
- File save adds <100ms overhead
- Feature-specific saves overwrite existing analysis.json (single file per feature)

**Use Cases**:
- Run BEFORE creating implementation plans (provides context for planning)
- Understand project structure and available resources
- Identify gaps and risks before starting feature work
- Audit project documentation and standards coverage
- Save analysis per-feature for implementation workflow

**Related tools**:
- Use results with `/create-plan` to generate context-aware implementation plans
- Compare with `/establish-standards` to ensure standards exist
- Combine with `/gather-context` for comprehensive feature planning workflow

---

#### `create_plan`
**Purpose**: Create implementation plan by synthesizing context, analysis, and template

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `feature_name` (string, required): Feature name (alphanumeric, hyphens, underscores only). Max 100 characters.

**Output**: JSON with plan path, status, and next steps

**Example**:
```python
create_plan(
    project_path="C:/path/to/project",
    feature_name="auth-system"
)
# Returns:
# {
#   "plan_path": "coderef/working/auth-system/plan.json",
#   "feature_name": "auth-system",
#   "sections_completed": ["0_preparation", "1_executive_summary", ..., "9_implementation_checklist"],
#   "has_context": true,
#   "has_analysis": false,
#   "status": "complete",
#   "next_steps": [
#     "Validate plan with /validate-plan",
#     "Review plan score and refine until >= 90",
#     "Generate review report with /generate-plan-review"
#   ],
#   "success": true
# }
```

**How it works:**
1. Loads `context.json` from `coderef/working/{feature_name}/` (if exists from prior `/gather-context`)
2. Loads analysis data (if available from prior `/analyze-for-planning`)
3. Loads AI-optimized template from `coderef/context/planning-template-for-ai.json` (502 lines, 63% smaller than full template)
4. Generates complete 10-section plan in batch mode
5. Saves to `coderef/working/{feature_name}/plan.json`
6. On failure: saves partial plan with TODO markers and retries once

**Status values:**
- `complete`: All 10 sections generated successfully
- `partial`: Generation failed, partial plan saved with TODOs

**Warnings:**
- If `has_context: false`: Best results require context from `/gather-context`
- If `has_analysis: false`: Best results require analysis from `/analyze-for-planning`

**Security:**
- Feature name validated to prevent path traversal
- Only alphanumeric, hyphens, and underscores allowed
- Max length: 100 characters

**Related tools:**
- Use `/gather-context` (optional) to collect feature requirements first
- Use `/analyze-for-planning` (optional) to analyze project structure first
- Use `/validate-plan` next to score plan quality (0-100)
- Use `/generate-plan-review` to create markdown review report

---

### Risk Assessment Tools

#### `assess_risk`
**Purpose**: AI-powered risk assessment tool that evaluates proposed code changes across 5 dimensions with multi-option comparison

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `proposed_change` (dict, required): Details of proposed change
  - `description` (string): What will be changed and why
  - `change_type` (string): Type of change - `create`, `modify`, `delete`, `refactor`, or `migrate`
  - `files_affected` (array): List of file paths that will be changed
- `options` (array, optional): Alternative implementation options (max 4 additional options)
- `threshold` (number, optional): Risk score threshold for go/no-go decision (0-100, default: 50.0)
- `feature_name` (string, optional): Feature name for assessment file naming

**Output**: JSON with risk assessment summary and path to detailed assessment file

**Risk Dimensions Evaluated**:
1. **Breaking Changes** (30% weight) - API changes, deletions, database migrations
2. **Security** (25% weight) - Secrets exposure, injection risks, auth changes
3. **Performance** (15% weight) - Loop complexity, query patterns, caching
4. **Maintainability** (15% weight) - Code complexity, documentation, test coverage
5. **Reversibility** (15% weight) - Rollback difficulty, data migration risks

**Scoring Algorithm**:
- **Dimension Score**: `(severity_weight × likelihood) / 4.0` → 0-100
- **Severity Levels**: low=1, medium=2, high=3, critical=4
- **Likelihood**: 0-100% estimated probability
- **Composite Score**: Weighted average of all 5 dimensions
- **Decision**: `go` (<50), `proceed-with-caution` (50-70), `needs-review` (70-85), `no-go` (>85)

**Single-Option Example**:
```python
assess_risk(
    project_path="C:/path/to/project",
    proposed_change={
        'description': 'Add JWT authentication with refresh token mechanism',
        'change_type': 'create',
        'files_affected': ['src/auth.py', 'src/middleware/auth.js']
    },
    threshold=60.0,
    feature_name='auth-system'
)
# Returns:
# {
#   "assessment_id": "RA-20251023041530",
#   "assessment_path": "coderef/risk-assessments/auth-system-20251023-041530.json",
#   "composite_score": 25.8,
#   "risk_level": "low",
#   "decision": "go",
#   "options_analyzed": 1,
#   "recommended_option": "option_1",
#   "duration_ms": 145.2,
#   "success": true
# }
```

**Multi-Option Comparison Example**:
```python
assess_risk(
    project_path="C:/path/to/project",
    proposed_change={
        'description': 'Add caching layer for API responses',
        'change_type': 'create',
        'files_affected': ['src/cache/redis.py']
    },
    options=[
        {
            'description': 'Use in-memory cache (fastest, limited capacity)',
            'change_type': 'create',
            'files_affected': ['src/cache/memory.py']
        },
        {
            'description': 'Use Redis (scalable, requires infrastructure)',
            'change_type': 'create',
            'files_affected': ['src/cache/redis.py']
        },
        {
            'description': 'Use database caching (simple, slower)',
            'change_type': 'create',
            'files_affected': ['src/cache/db.py']
        }
    ],
    threshold=50.0
)
# Returns comparison with ranked options (lowest risk first)
# Full comparison details saved to assessment file
```

**Assessment File Contents** (saved to `coderef/risk-assessments/`):
```json
{
  "assessment_id": "RA-20251023041530",
  "risk_dimensions": {
    "breaking_changes": {
      "severity": "low",
      "likelihood": 10.0,
      "score": 2.5,
      "findings": ["New functionality - no breaking changes expected"],
      "evidence": ["Creating new files, not modifying existing APIs"]
    },
    "security": {
      "severity": "medium",
      "likelihood": 40.0,
      "score": 20.0,
      "findings": ["Authentication logic requires security review"],
      "evidence": ["JWT token handling detected"]
    },
    // ... other 3 dimensions
  },
  "composite_score": {
    "score": 25.8,
    "level": "low",
    "breakdown": {
      "breaking_changes_contribution": 0.75,
      "security_contribution": 5.0,
      // ... other contributions
    }
  },
  "recommendation": {
    "decision": "go",
    "reasoning": "Low overall risk. Security review recommended but not blocking.",
    "confidence": 0.85,
    "conditions": ["Complete security review before production deployment"]
  },
  "mitigation_strategies": [
    {
      "dimension": "security",
      "strategy": "Implement JWT token rotation",
      "priority": "high",
      "effort": "medium"
    }
  ]
}
```

**Performance**:
- Typical assessment: < 1 second
- Multi-option comparison (4 options): < 2 seconds
- Requirement: < 5 seconds for all scenarios ✅

**When to use**:
- Before implementing significant code changes
- When evaluating multiple implementation approaches
- For go/no-go decisions on risky refactors
- During code review to identify overlooked risks
- In CI/CD pipelines as quality gate

**Key features**:
- **Deterministic scoring** - Same input always produces same output
- **Explainable results** - Clear findings and evidence for each dimension
- **Multi-option ranking** - Compares alternatives automatically
- **Actionable recommendations** - Specific mitigation strategies provided
- **Machine-readable output** - JSON format for automation

---

### Project Inventory Tools

#### `documentation_inventory`
**Purpose**: Discover and analyze documentation files across multiple formats with quality metrics

**Input**:
- `project_path` (string, required): Absolute path to project directory

**Output**: JSON with documentation manifest, format breakdown, and quality metrics

**Example**:
```python
documentation_inventory(
    project_path="C:/path/to/project"
)
# Returns:
# {
#   "manifest_path": "coderef/inventory/documentation.json",
#   "formats_detected": ["markdown", "rst", "asciidoc"],
#   "total_files": 62,
#   "markdown_files": 45,
#   "rst_files": 12,
#   "asciidoc_files": 3,
#   "html_files": 2,
#   "orgmode_files": 0,
#   "quality_score": 100,
#   "freshness_days": 5,
#   "coverage_percentage": 89,
#   "success": true
# }
```

**Supported formats:**
- **Markdown**: `.md`, `.markdown`, `.mdown`, `.mdwn`
- **ReStructuredText**: `.rst`, `.rest`, `.restx`, `.rtxt`
- **AsciiDoc**: `.adoc`, `.asciidoc`, `.asc`
- **HTML**: `.html`, `.htm`
- **Org-mode**: `.org`

**Quality Metrics:**
- **Quality Score (0-100)**:
  - Base: 50 points
  - +10 for ≥5 files found
  - +10 for ≥10 files found
  - +10 for ≥3 markdown files
  - +10 if >50% docs updated within 30 days
  - +10 if important docs (README, CHANGELOG, etc.) present

- **Freshness Days**: Average days since last modification across all docs

- **Coverage Percentage**: % of important documentation files found
  - Expected docs: README, CHANGELOG, CONTRIBUTING, LICENSE, AUTHORS, INSTALLATION, GUIDE, TUTORIAL, FAQ, API, ARCHITECTURE

**Search Locations:**
- Project root directory
- `docs/` subdirectory
- `doc/` subdirectory
- `documentation/` subdirectory
- `.github/` subdirectory

**Manifest Output** (saved to `coderef/inventory/documentation.json`):
```json
{
  "project_name": "my-project",
  "generated_at": "2025-10-15T22:45:50.123456",
  "formats": ["markdown", "rst"],
  "files": [
    {
      "path": "README.md",
      "name": "README.md",
      "format": "markdown",
      "size_bytes": 2048,
      "last_modified": "2025-10-10T14:30:22",
      "days_old": 5,
      "is_important": true,
      "estimated_words": 42
    }
  ],
  "by_format": {
    "markdown": [...],
    "rst": [...]
  },
  "metrics": {
    "total_files": 62,
    "markdown_files": 45,
    "rst_files": 12,
    "asciidoc_files": 3,
    "html_files": 2,
    "orgmode_files": 0,
    "quality_score": 100,
    "freshness_days": 5,
    "coverage_percentage": 89
  }
}
```

**Use cases:**
- Assess documentation quality and completeness
- Identify outdated or missing documentation
- Generate documentation inventory reports
- Track documentation health metrics over time
- Compliance audits for documentation standards
- Planning documentation updates and improvements

**When to use:**
- Starting work on a new project (understand current docs)
- During documentation audits
- Before major releases (ensure docs are current)
- Planning knowledge base improvements
- Generating project health reports

---

#### `config_inventory`
**Purpose**: Discover and analyze configuration files across multiple formats with security masking

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `formats` (array, optional): Which configuration formats to analyze - ["json", "yaml", "toml", "ini", "env", "all"] (default: ["all"])
- `mask_sensitive` (boolean, optional): Whether to mask sensitive values with [REDACTED] (default: true)

**Output**: JSON with configuration manifest, format breakdown, and security analysis

**Example**:
```python
config_inventory(
    project_path="C:/path/to/project",
    formats=["all"],
    mask_sensitive=true
)
# Returns:
# {
#   "manifest_path": "coderef/inventory/config.json",
#   "formats_detected": ["json", "yaml", "env"],
#   "total_files": 12,
#   "files_by_format": {
#     "json": 4,
#     "yaml": 5,
#     "env": 3
#   },
#   "sensitive_values_found": 23,
#   "sensitive_by_type": {
#     "api_keys": 8,
#     "passwords": 6,
#     "tokens": 9
#   },
#   "files_with_secrets": ["config/api.json", ".env.production"],
#   "security_score": 95,
#   "success": true
# }
```

**Supported formats:**
- **JSON**: `.json`, `.jsonc`
- **YAML**: `.yaml`, `.yml`
- **TOML**: `.toml`
- **INI**: `.ini`, `.cfg`, `.conf`
- **Environment**: `.env`, `.env.*`

**Security Features:**
- **Sensitive Value Detection**: Automatically identifies API keys, passwords, tokens, database credentials
- **Value Masking**: Replaces detected secrets with `[REDACTED]` for safe sharing
- **Security Scoring**: Rates configuration security (0-100 based on secrets found)
- **Audit Logging**: Logs all sensitive detections for security review
- **Format-Aware Parsing**: Understands structure and context of each format

**Manifest Output** (saved to `coderef/inventory/config.json`):
```json
{
  "project_name": "my-project",
  "generated_at": "2025-10-15T22:45:50.123456",
  "formats_detected": ["json", "yaml", "env"],
  "files": [
    {
      "path": ".env.example",
      "format": "env",
      "size_bytes": 512,
      "sensitive_values_count": 0,
      "sensitive_types": [],
      "is_example": true,
      "last_modified": "2025-10-15T20:00:00"
    },
    {
      "path": ".env.production",
      "format": "env",
      "size_bytes": 1024,
      "sensitive_values_count": 6,
      "sensitive_types": ["api_keys", "passwords"],
      "is_example": false,
      "last_modified": "2025-10-15T21:30:00",
      "masking_applied": true
    }
  ],
  "security_summary": {
    "total_files": 12,
    "files_with_secrets": 7,
    "total_secrets_found": 23,
    "secrets_by_type": {
      "api_keys": 8,
      "passwords": 6,
      "database_credentials": 5,
      "tokens": 4
    },
    "security_score": 85,
    "risk_level": "medium"
  },
  "recommendations": [
    "Move .env.production to secure secret management system",
    "Remove hardcoded database passwords from config files",
    "Use environment variables for API keys instead of config files"
  ]
}
```

**Use cases:**
- Audit project configuration for exposed secrets
- Identify hardcoded credentials before commits
- Generate configuration inventory reports
- Security compliance audits
- CI/CD pipeline secret scanning
- Configuration management analysis

**When to use:**
- Before committing code (check for secrets)
- During security audits
- Setting up CI/CD pipelines
- Configuration management and deployment
- Compliance verification

**Security Best Practices:**
- Always mask sensitive values before sharing reports
- Review recommendations for secret rotation
- Move secrets to environment variables or secret vaults
- Audit logged detections for unauthorized access

---

#### `test_inventory`
**Purpose**: Discover test files, detect frameworks, analyze coverage, and identify untested code

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `frameworks` (array, optional): Which test frameworks to detect - ["pytest", "unittest", "jest", "mocha", "vitest", "all"] (default: ["all"])
- `include_coverage` (boolean, optional): Whether to analyze coverage data if available (default: true)

**Output**: JSON with test infrastructure manifest, framework breakdown, and coverage analysis

**Example**:
```python
test_inventory(
    project_path="C:/path/to/project",
    frameworks=["all"],
    include_coverage=true
)
# Returns:
# {
#   "manifest_path": "coderef/inventory/tests.json",
#   "frameworks_detected": ["pytest", "jest"],
#   "total_test_files": 42,
#   "total_test_cases": 287,
#   "frameworks_breakdown": {
#     "pytest": {
#       "count": 28,
#       "test_cases": 156,
#       "config_file": "pytest.ini"
#     },
#     "jest": {
#       "count": 14,
#       "test_cases": 131,
#       "config_file": "jest.config.js"
#     }
#   },
#   "coverage_metrics": {
#     "overall_coverage": 78.5,
#     "statements": 78.5,
#     "branches": 72.1,
#     "functions": 81.2,
#     "lines": 79.3,
#     "coverage_file": ".coverage/coverage.json"
#   },
#   "untested_files": 12,
#   "test_readiness_score": 82,
#   "success": true
# }
```

**Supported frameworks:**
- **Python**: `pytest`, `unittest`
- **JavaScript**: `jest`, `mocha`, `vitest`
- **Ruby**: `rspec`
- **Go**: `go test`
- **Java**: `junit`

**Coverage Analysis:**
- **Overall Coverage**: Aggregate coverage percentage
- **Statements**: Code lines executed
- **Branches**: Conditional branches tested
- **Functions**: Functions with test coverage
- **Lines**: Physical lines tested

**Manifest Output** (saved to `coderef/inventory/tests.json`):
```json
{
  "project_name": "my-project",
  "generated_at": "2025-10-15T22:45:50.123456",
  "frameworks_detected": ["pytest", "jest"],
  "test_files": [
    {
      "path": "tests/unit/test_auth.py",
      "framework": "pytest",
      "test_count": 12,
      "last_modified": "2025-10-15T20:00:00",
      "file_size_bytes": 3456
    },
    {
      "path": "src/__tests__/components.test.js",
      "framework": "jest",
      "test_count": 24,
      "last_modified": "2025-10-15T21:00:00",
      "file_size_bytes": 5678
    }
  ],
  "source_files_without_tests": [
    {
      "path": "src/utils/helpers.js",
      "file_size_bytes": 1024,
      "complexity_estimated": "low",
      "recommendation": "Add unit tests"
    }
  ],
  "coverage_data": {
    "overall": 78.5,
    "by_file": [
      {
        "path": "src/auth.py",
        "coverage": 95.2
      },
      {
        "path": "src/api.py",
        "coverage": 62.1
      }
    ],
    "coverage_report_file": ".coverage/htmlcov/status.json"
  },
  "test_summary": {
    "total_test_files": 42,
    "total_test_cases": 287,
    "passing_ratio": 0.982,
    "estimated_run_time_seconds": 45,
    "test_readiness_score": 82
  },
  "frameworks": [
    {
      "name": "pytest",
      "version": "7.0.0",
      "config_file": "pytest.ini",
      "test_count": 156
    },
    {
      "name": "jest",
      "version": "28.0.0",
      "config_file": "jest.config.js",
      "test_count": 131
    }
  ],
  "recommendations": [
    "Add tests for src/utils/helpers.js (coverage gap)",
    "Integration tests missing for API endpoints",
    "E2E test coverage recommended for critical paths"
  ]
}
```

**Quality Metrics:**
- **Test Readiness Score (0-100)**:
  - Base: 50 points
  - +15 for >70% code coverage
  - +15 for >100 test cases
  - +10 for multiple test frameworks
  - +10 if coverage trending upward
  - Deductions for untested critical files

**Use cases:**
- Assess project test coverage and readiness
- Identify gaps in test coverage
- Detect available test frameworks
- Planning test expansion
- CI/CD integration verification
- Quality assurance metrics tracking

**When to use:**
- Before major releases (ensure test coverage)
- During code reviews (verify test additions)
- Planning refactoring (understand current coverage)
- Quality audits and compliance
- CI/CD pipeline validation

**Recommendations:**
- Maintain minimum 80% code coverage
- Add tests before refactoring
- Focus on critical path testing first
- Use coverage trends to track improvements

---

### Workorder Tracking Tools

#### `log_workorder`
**Purpose**: Log a new workorder entry to the global workorder log file

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `workorder_id` (string, required): Workorder ID (format: WO-FEATURE-NAME-001, e.g., "WO-AUTH-001")
- `project_name` (string, required): Project name (short identifier)
- `description` (string, required): Brief description of the workorder (max 50 chars recommended, auto-truncated)
- `timestamp` (string, optional): ISO 8601 timestamp (auto-generated if not provided)

**Output**: Success response with log entry confirmation

**Example**:
```python
log_workorder(
    project_path="C:/path/to/project",
    workorder_id="WO-WORKORDER-LOG-001",
    project_name="docs-mcp",
    description="Implement workorder logging system"
)
# Returns:
# {
#   "workorder_id": "WO-WORKORDER-LOG-001",
#   "project_name": "docs-mcp",
#   "description": "Implement workorder logging system (2 tools, pr...",
#   "timestamp": "2025-10-21T02:08:51.983188+00:00",
#   "log_file": "coderef/workorder-log.txt",
#   "success": true
# }
```

**Log file format**:
```
WO-ID | Project | Description | Timestamp
```

**Example log entries**:
```
WO-WORKORDER-LOG-001 | docs-mcp | Implement workorder logging system (2 tools, pr... | 2025-10-21T02:08:51+00:00
WO-AUTH-001 | personas-mcp | Auth system workorder | 2025-10-21T01:45:20+00:00
```

**Key features**:
- **Latest entries at top** (prepend, reverse chronological order)
- **Simple one-line format** for quick visibility
- **Saved to**: `coderef/workorder-log.txt`
- **Auto-truncation**: Descriptions >50 chars truncated with "..."
- **Validation**: Workorder ID must match pattern `^WO-[A-Z0-9-]+-\d{3}$`

**Use cases**:
- Log workorder completion for traceability
- Track project activity across features
- Maintain global activity log
- Quick glance at recent work

**When to use**:
- After completing a workorder/feature
- When archiving features (auto-logging)
- For manual activity tracking
- Integration with planning workflows

---

#### `get_workorder_log`
**Purpose**: Read and query the global workorder log file

**Input**:
- `project_path` (string, required): Absolute path to project directory
- `project_name` (string, optional): Filter by project name (partial match, case-insensitive)
- `workorder_pattern` (string, optional): Filter by workorder ID pattern (e.g., "WO-AUTH")
- `limit` (integer, optional): Maximum number of entries to return

**Output**: JSON with workorder entries and metadata

**Examples**:
```python
# Get all entries
get_workorder_log(project_path="C:/path/to/project")

# Filter by project
get_workorder_log(
    project_path="C:/path/to/project",
    project_name="personas"  # Matches "personas-mcp"
)

# Filter by workorder pattern
get_workorder_log(
    project_path="C:/path/to/project",
    workorder_pattern="WO-AUTH"  # Matches WO-AUTH-001, WO-AUTH-002, etc.
)

# Limit results
get_workorder_log(
    project_path="C:/path/to/project",
    limit=10  # Return latest 10 entries only
)
```

**Response format**:
```json
{
  "entries": [
    {
      "workorder_id": "WO-WORKORDER-LOG-001",
      "project": "docs-mcp",
      "description": "Implement workorder logging system (2 tools, pr...",
      "timestamp": "2025-10-21T02:08:51.983188+00:00"
    }
  ],
  "total_count": 50,
  "filtered_count": 1,
  "log_file": "coderef/workorder-log.txt",
  "filters_applied": {
    "project_name": "docs",
    "workorder_pattern": null,
    "limit": null
  },
  "success": true
}
```

**Use cases**:
- View recent workorder activity
- Find workorders for specific projects
- Search workorder history by pattern
- Quick project status overview
- Generate activity reports

**When to use**:
- Checking recent project activity
- Finding specific workorders
- Generating status reports
- Auditing project history
- Traceability checks

**Slash command shortcuts**:
- `/log-workorder` - Interactive prompt for logging new entry
- `/get-workorder-log` - Interactive query with optional filters

---

## Adding New Tools

### Process

1. **Define in `server.py` `list_tools()`**
   ```python
   Tool(
       name="my_new_tool",
       description="Clear description of what it does",
       inputSchema={
           "type": "object",
           "properties": {
               "project_path": {
                   "type": "string",
                   "description": "Absolute path to project directory"
               },
               "param2": {
                   "type": "string",
                   "description": "Description of param2"
               }
           },
           "required": ["project_path", "param2"]
       }
   )
   ```

2. **Create handler in `tool_handlers.py`**
   ```python
   async def handle_my_new_tool(arguments: dict) -> list[TextContent]:
       """Handle my_new_tool tool call."""
       try:
           # Validate inputs
           project_path = validate_project_path_input(arguments.get("project_path"))

           # Do work
           result = do_work(project_path)

           # Return response
           return [TextContent(type="text", text=result)]
       except ValueError as e:
           return ErrorResponse.invalid_input(str(e))
       except Exception as e:
           return ErrorResponse.generic_error(str(e))
   ```

3. **Register in `TOOL_HANDLERS` dict**
   ```python
   TOOL_HANDLERS = {
       # ... existing handlers
       'my_new_tool': handle_my_new_tool,
   }
   ```

4. **Create slash command (optional)**
   ```bash
   # Create command file in .claude/commands/
   cat > .claude/commands/my-new-tool.md <<'EOF'
   Execute my_new_tool for the current project.

   Call the `mcp__docs-mcp__my_new_tool` tool with the current working directory as the project_path.
   EOF

   # Update commands.json registry
   # Add entry to "commands" array with name, description, category
   ```

5. **Deploy slash command globally** ⚠️ **CRITICAL STEP**
   ```bash
   # Copy command to global directory
   cp .claude/commands/my-new-tool.md ~/.claude/commands/

   # Update global registry
   cp .claude/commands.json ~/.claude/

   # Verify deployment
   ls ~/.claude/commands/my-new-tool.md
   ```

6. **Document the change**
   ```python
   # Use MCP tool (not direct Python!)
   mcp__docs_mcp__add_changelog_entry(
       project_path="C:/Users/willh/.mcp-servers/docs-mcp",
       version="1.0.10",
       change_type="feature",
       severity="minor",
       title="Added my_new_tool for XYZ functionality",
       description="Implemented my_new_tool to provide...",
       files=["server.py", "tool_handlers.py", ".claude/commands/my-new-tool.md"],
       reason="Users needed ability to...",
       impact="Users can now..."
   )
   ```

7. **Update documentation**
   - Add tool to CLAUDE.md "Slash Commands" section
   - Update deployment status in "Deploying Slash Commands Globally" section
   - Update README.md if user-facing
   - Reload Claude Code to discover new command

### Ideas for New Tools

**Based on existing patterns, here are expansion opportunities:**

1. **`validate_documentation`**
   - Check if docs are up-to-date with code
   - Compare API docs against actual function signatures
   - Meta-tool pattern: instructs AI to review and report discrepancies

2. **`update_docs`** (Meta-Tool)
   - Instructs AI to regenerate docs after code changes
   - Similar to `update_changelog` but for documentation
   - Guides AI through: analyze changes → identify affected docs → regenerate

3. **`get_template_variables`**
   - Returns list of variables/sections in a template
   - Helps AI understand what information to gather
   - Useful for custom template creation

4. **`search_changelog`**
   - Full-text search across changelog entries
   - Find all changes related to a specific feature/file
   - More flexible than `change_type` filter

5. **`generate_release_notes`**
   - Compile changelog entries for a version into release notes format
   - Transform structured data → user-friendly markdown
   - Optional filters: include/exclude certain change types

6. **`compare_versions`**
   - Show diff between two versions in changelog
   - Useful for understanding what changed between releases
   - Returns structured comparison

7. **`create_custom_template`**
   - Allow users to add their own templates
   - Store in `templates/custom/` directory
   - Extend beyond POWER framework

---

## Working Plan Status: 83% Complete

### ✅ Completed
- SEC-001: Path traversal protection
- SEC-002: JSON schema validation
- SEC-003: Smart output routing
- SEC-005: Template sanitization
- DEP-001: Dependency management
- REF-002: Constants extraction
- REF-003: Input validation layer
- ARCH-001: ErrorResponse factory
- ARCH-003: Structured logging
- QUA-001: TypedDict coverage
- QUA-002: Handler registry
- QUA-003: Enum constants

### ⏭️ Skipped/Low Priority
- SEC-006: Rate limiting (unnecessary - MCP host controls invocation)
- REF-001: [Marked as skipped]

### 🎯 Recommendation
Consider this server **production-ready at v1.0.9**. The 83% represents completionist items that aren't essential for operation.

---

## Critical Pitfalls to Avoid

### When Using the Server
1. ❌ Using relative paths → ✅ Always use absolute paths
2. ❌ Expecting tools to write files → ✅ Tools return templates, AI generates content
3. ❌ Forgetting required changelog fields → ✅ Provide all 9 required fields
4. ❌ Invalid version format (`v1.0.3`) → ✅ Use `1.0.3` (X.Y.Z)
5. ❌ Not reading changelog before adding → ✅ Call `get_changelog` first for context

### When Developing the Server
1. ❌ Direct Python access to generators → ✅ Use MCP tool handlers
2. ❌ Hardcoded strings → ✅ Use constants and enums
3. ❌ Skipping input validation → ✅ Validate all inputs at MCP boundaries
4. ❌ Missing error logging → ✅ Log all operations (tool calls, errors, security)
5. ❌ Inconsistent error responses → ✅ Use ErrorResponse factory
6. ❌ Updating changelog via Python → ✅ Use `add_changelog_entry` MCP tool

---

## Testing

### Test Suite Overview

docs-mcp includes a comprehensive test suite with **200+ tests** covering:

- **Unit tests** for all 6 generators
- **Integration tests** for MCP workflows and planning pipeline
- **Performance tests** for large projects (100+ files) and query operations

**Test Structure:**
```
tests/
├── conftest.py                 # Shared fixtures for all tests
├── unit/
│   ├── test_foundation_generator.py      # Foundation docs tests
│   ├── test_planning_generator.py        # Planning workflow tests
│   ├── test_server.py                    # Server initialization tests
│   ├── test_changelog_generator.py       # Changelog CRUD tests
│   └── test_inventory_generators.py      # Inventory tools tests
├── integration/
│   ├── test_mcp_workflows.py             # End-to-end MCP tool tests
│   └── test_planning_workflow.py         # Full planning pipeline tests
└── performance/
    ├── test_large_projects.py            # 100+ file project tests
    └── test_query_performance.py         # Query and filter benchmarks
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/performance/             # Performance tests only
pytest -m performance                 # Tests marked @performance

# Run specific test file
pytest tests/unit/test_foundation_generator.py

# Run with verbose output
pytest -v --tb=short

# Run slow tests (marked @slow)
pytest -m slow
```

### Coverage Targets

| Module | Target | Description |
|--------|--------|-------------|
| `generators/foundation_generator.py` | 80%+ | Documentation generation |
| `generators/planning_generator.py` | 80%+ | Planning workflow |
| `generators/changelog_generator.py` | 80%+ | Changelog operations |
| `generators/inventory_generators.py` | 80%+ | Inventory tools |
| `tool_handlers.py` | 70%+ | MCP handler layer |

### Writing Tests

**Use shared fixtures from conftest.py:**
```python
import pytest
from pathlib import Path

def test_example(mock_project: Path):
    """Test using mock project fixture."""
    # mock_project provides:
    # - src/ with Python, TypeScript files
    # - tests/ with pytest tests
    # - docs/ with README.md
    # - coderef/ structure with changelog, experts
    # - Initialized git repo with initial commit

    assert (mock_project / "src" / "main.py").exists()
```

**Use mock_project_with_history for git operations:**
```python
def test_git_analysis(mock_project_with_history: Path):
    """Test with git commit history."""
    # Has 3+ commits for git history analysis testing
    pass
```

**Use large_mock_project for performance tests:**
```python
@pytest.mark.performance
def test_large_scale(large_mock_project: Path):
    """Test with 100+ files."""
    # 10 modules × 10 files = 100 Python files
    pass
```

### Test Patterns

**1. Tool Functionality (via MCP handlers):**
```python
import tool_handlers

async def test_tool_success(mock_project):
    result = await tool_handlers.handle_list_templates({})
    assert "Available POWER Framework Templates" in result[0].text

async def test_tool_error(mock_project):
    result = await tool_handlers.handle_get_template({"template_name": "invalid"})
    assert "not found" in result[0].text.lower()
```

**2. Security Tests:**
```python
async def test_path_traversal_blocked():
    result = await tool_handlers.handle_get_template({
        "template_name": "../../../etc/passwd"
    })
    assert "invalid" in result[0].text.lower()

async def test_version_format_validated():
    result = await tool_handlers.handle_add_changelog_entry({
        "project_path": "/valid/path",
        "version": "v1.0.3",  # Invalid: must be X.Y.Z
    })
    assert "version format" in result[0].text.lower()
```

**3. Performance Tests:**
```python
import time

@pytest.mark.performance
def test_operation_speed(large_mock_project):
    start = time.time()
    # Run operation
    elapsed = time.time() - start
    assert elapsed < 2.0, f"Took {elapsed:.2f}s, expected < 2s"
```

### Test Markers

Available pytest markers (defined in pyproject.toml):

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.asyncio` - Async tests (auto-applied)

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: pip install -e ".[dev]"
    - run: pytest --cov=. --cov-report=xml
    - uses: codecov/codecov-action@v4
```

---

## Version Information

**Current Version**: 2.9.0
**Last Updated**: 2025-12-06
**Maintainers**: willh, Claude Code AI

**Change History** (Recent):
- 2.9.0: LLM Workflow - Multi-LLM prompt generation (/llm-prompt) and response consolidation (/consolidate) for code reviews, architecture, security audits. Files stored in coderef/working/{feature}/ folder.
- 1.0.4: Synced commands.json registry with 8 missing slash commands (config-inventory, documentation-inventory, test-inventory, execute-plan, generate-deliverables, update-deliverables, log-workorder, get-workorder-log). Added new deliverables and workorder categories. Updated COMPREHENSIVE-review.md to mark all improvements complete.
- 1.1.0: Schema-First Design for planning workflow - Added plan.schema.json as single source of truth, schema_validator.py with helper functions for safe data extraction, and updated generate_deliverables_template to use normalized format handling. Implements three-layer defense: Producer (create_plan shows schema), Validator (normalizes formats), Consumer (uses helpers).
- 1.0.4: Fixed /create-plan to automatically generate DELIVERABLES.md after plan.json creation - aligns code with existing documentation claims
- 1.1.0: Integrated automatic workorder logging with archive feature workflow - completes workorder lifecycle by auto-logging to workorder-log.txt when features are archived
- 1.11.0: Global Workorder Logging System - 2 new tools (log_workorder, get_workorder_log) for tracking feature completion
- 1.10.0: Feature Archive System - Automated archiving tool with status checking and index tracking
- 1.9.0: Multi-Agent Coordination System - 5 tools for parallel agent workflows
- 2.3.0: Multi-Agent Coordination System - 5 tools for parallel agent workflows
- 2.2.0: Deliverables Tracking System - Automatic DELIVERABLES.md generation with git metrics
- 2.1.0: Workorder Tracking System - Automatic unique ID assignment for all features in MCP planning workflow
- 2.0.0: Complete documentation and inventory system - All 23 tools now documented (Phase 5D + 6 complete)
- 1.3.0: Consistency Management expansion (establish_standards + audit_codebase tools)
- 1.0.9: Added comprehensive CLAUDE.md for dual-audience (development + usage)
- 1.0.8: Demonstrated proper MCP changelog workflow
- 1.0.7: Architecture refactor (modular handlers, logging, type safety, error factory)
- 1.0.6: Phase 2 refactor (constants extraction, input validation layer)
- 1.0.5: JSON schema validation, README routing fix

See [CHANGELOG.json](coderef/changelog/CHANGELOG.json) for complete history.

---

## Resources

- **[README.md](README.md)** - User-facing documentation
- **[user-guide.md](user-guide.md)** - Comprehensive usage guide
- **[coderef/quickref.md](coderef/quickref.md)** - Quick reference for all tools
- **[coderef/changelog/CHANGELOG.json](coderef/changelog/CHANGELOG.json)** - Structured changelog
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official MCP documentation

---

## MCP Compatibility & Cross-Agent Access

### Can other AI agents (Codex, Copilot, etc.) access this MCP server?

**Short answer**: Theoretically yes, but practically depends on MCP client support.

**Technical details:**

**What is MCP?**
- MCP (Model Context Protocol) is an open standard by Anthropic
- Universal protocol for connecting LLMs to external tools and data
- Similar to how HTTP standardizes web communication

**Current MCP Support (as of October 2025):**

✅ **Full Support:**
- **Claude Code** (Anthropic) - Native first-class MCP support
- **Claude Desktop** (Anthropic) - Native MCP support
- **Custom implementations** - Any application can implement MCP client

❓ **Unknown/Limited Support:**
- **GitHub Copilot** - No public MCP support announced
- **GitHub Codex** (deprecated) - No MCP support
- **Cursor** - Custom tool integration, not MCP-based (as of now)
- **Windsurf** - Custom tool integration, not MCP-based
- **Other IDEs** - Depends on vendor adoption

**How to make this accessible to other agents:**

1. **MCP-Compatible Clients**: Any tool implementing MCP client protocol can connect
   ```bash
   # Standard MCP connection (stdio transport)
   python server.py
   ```

2. **REST API Wrapper**: Create HTTP wrapper around MCP tools
   ```python
   # Expose MCP tools via REST API
   # Then any agent with HTTP access can use it
   ```

3. **Agent-Specific Adapters**: Create adapters for specific platforms
   ```python
   # Copilot: Convert to GitHub Actions
   # Cursor: Convert to Cursor rules
   # etc.
   ```

**Why MCP matters:**
- **Standardization**: One tool server works across all MCP clients
- **No vendor lock-in**: Tools aren't tied to specific AI platforms
- **Ecosystem growth**: More MCP servers = more capabilities for all agents
- **Future-proof**: As more vendors adopt MCP, your tools work everywhere

**Current best practice:**
- Use docs-mcp with **Claude Code** for full MCP experience
- For other agents, consider creating REST API wrapper
- Monitor vendor announcements for MCP adoption

**Resources:**
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official protocol docs
- [MCP GitHub](https://github.com/anthropics/mcp) - Reference implementations
- [MCP Servers Repository](https://github.com/anthropics/mcp-servers) - Community servers

---

**🤖 This document is optimized for AI assistant consumption**
**📚 For human-readable docs, see README.md and user-guide.md**
