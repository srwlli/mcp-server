# coderef-workflow - AI Context Documentation

**Project:** coderef-workflow (MCP Server)
**Version:** 1.1.0
**Status:** ✅ Production - Feature lifecycle management orchestration
**Created:** 2024-12-24
**Last Updated:** 2025-12-25 (WO-WORKFLOW-REFACTOR-001 complete)

---

## Quick Summary

**coderef-workflow** is an enterprise-grade MCP server that orchestrates the complete feature development lifecycle. It handles context gathering, planning, execution tracking, deliverables management, and feature archiving using a **workorder-centric architecture**.

**Core Innovation:** Works in tandem with **coderef-context** (code intelligence) and **coderef-docs** (documentation generation) to provide AI agents with the tools to manage complex, multi-phase feature implementations. **NEW:** Workorder ID tracking for complete audit trail and feature lifecycle management.

**Latest Update (v1.1.0):**
- ✅ Fixed critical bugs in plan generation (status lifecycle, deliverables handling)
- ✅ Implemented workorder_id tracking throughout system
- ✅ Completed coderef/working → coderef/workorder refactoring
- ✅ All 16 tasks in WO-WORKFLOW-REFACTOR-001 complete and tested

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

## Architecture: Context-Based Workflow Planning

### How coderef-workflow Uses coderef-context

The workflow system depends on **coderef-context** for code intelligence during planning:

```
Feature Planning Flow:
├─ gather_context() → Collect requirements
├─ analyze_project_for_planning()
│  └─ Uses coderef-context to scan codebase (coderef_scan)
├─ create_plan()
│  └─ Uses coderef-context for dependency analysis (coderef_query)
│  └─ Uses coderef-context for pattern detection (coderef_patterns)
└─ align_plan() → Align plan with todo list for tracking and progress
```

**Key Integration Points:**
- `analyze_project_for_planning()` calls coderef-context's `coderef_scan` tool to get AST-based inventory
- `create_plan()` uses coderef-context's `coderef_query` for dependency analysis (what-calls, what-imports, etc.)
- Impact assessment uses `coderef_impact` to understand change ripple effects
- Pattern detection uses `coderef_patterns` to identify existing patterns in codebase

### Data Flow Architecture

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

## Workorder System Architecture (v1.1.0+)

**NEW:** All plans now use a workorder-centric system for complete audit trail and feature tracking.

### Workorder ID Format
```
WO-{FEATURE}-{CATEGORY}-{SEQUENCE}
Example: WO-AUTH-SYSTEM-001, WO-API-DESIGN-002
```

### Directory Structure
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

### Workorder ID Tracking
Each plan.json now includes workorder tracking in META_DOCUMENTATION:
```json
{
  "META_DOCUMENTATION": {
    "feature_name": "new-feature",
    "workorder_id": "WO-FEATURE-001",  // NEW in v1.1.0
    "status": "planning",               // NEW: starts as "planning"
    "generated_by": "AI Assistant",
    "has_context": true,
    "has_analysis": true
  }
}
```

### Key Changes in v1.1.0
1. **Bug Fixes:**
   - Fixed deliverables crash in tool_handlers.py (type checking)
   - Fixed plan status lifecycle (now starts as "planning" not "complete")

2. **Enhancements:**
   - workorder_id parameter added to plan generation pipeline
   - workorder_id stored in plan.json for audit trail
   - create_plan tool schema updated to accept workorder_id

3. **Refactoring:**
   - Updated 6 Python files (42 changes)
   - Updated 13 slash commands (35 changes)
   - All paths changed: coderef/working → coderef/workorder

4. **Testing:**
   - All 4 critical tests passed
   - Real plan.json validation complete
   - Zero regressions detected

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

## Key Concepts: Context-Based Workflow

### The 10-Section Plan (plan.json)

Each feature creates a `plan.json` with 10 comprehensive sections:

1. **META_DOCUMENTATION** - Project info, version, timestamps
2. **0_PREPARATION** - Discovery, codebase analysis, existing patterns
3. **1_EXECUTIVE_SUMMARY** - What & why (3-5 bullet points)
4. **2_RISK_ASSESSMENT** - Breaking changes, security, performance risks
5. **3_CURRENT_STATE_ANALYSIS** - Existing code, architecture, patterns
6. **4_KEY_FEATURES** - List of feature requirements (must-have)
7. **5_TASK_ID_SYSTEM** - Task naming (PHASE-###, IMPL-###, TEST-###)
8. **6_IMPLEMENTATION_PHASES** - Phased breakdown with tasks & dependencies
9. **7_TESTING_STRATEGY** - Unit, integration, e2e test plan
10. **8_SUCCESS_CRITERIA** - How to verify feature is complete

### Workorder IDs

Format: `WO-{FEATURE}-{SEQUENCE}`

Example: `WO-AUTH-SYSTEM-001`

Tracked globally in `coderef/workorder-log.txt` for audit trail.

### Context Hierarchy

```
Project Context (coderef/foundation-docs/)
    ↓
Feature Context (coderef/workorder/{feature}/context.json)
    ↓
Workorder Context (WO-ID tracking)
    ↓
Task Context (individual task execution)
```

---

## Integration with coderef-context

### How to Use Code Intelligence in Plans

When creating plans, coderef-workflow automatically:

1. **Scans the codebase** using `coderef_scan`
   - Gets live AST-based inventory
   - Identifies components, functions, classes
   - Maps file structure

2. **Analyzes dependencies** using `coderef_query`
   - Finds what calls the modified code
   - Finds what the code depends on
   - Identifies ripple effects

3. **Detects patterns** using `coderef_patterns`
   - Finds similar implementations
   - Identifies code style patterns
   - Suggests consistent approaches

4. **Assesses impact** using `coderef_impact`
   - Identifies breaking change risks
   - Maps downstream dependencies
   - Estimates change scope

**Example Plan with Code Intelligence:**

```json
{
  "3_CURRENT_STATE_ANALYSIS": {
    "existing_patterns": [
      // Found by coderef_patterns
      "Authentication handled via decorators in src/auth.py",
      "Database queries use SQLAlchemy ORM pattern"
    ],
    "dependencies": [
      // Found by coderef_query
      "AuthService imported by 12 modules",
      "breaking change would affect UserService, TokenService"
    ]
  }
}
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

### UC-3: Refactoring with Impact Analysis
```
Agent: "I want to rename AuthService"
       ↓
coderef-context: /coderef_impact
                 ↓ Returns: "12 files depend on this, here's the ripple"
                 ↓
Agent: "Now I know what breaks. Here's my implementation plan."
       ↓ Safe refactoring with full context
```

### UC-4: Plan Validation & Review
```
User: /create-plan
      → Plan created from context + analysis
      ↓
User: /validate-plan
      ↓ Returns: Score 75/100, 3 critical issues, 5 minor issues
      ↓
Agent: Refines plan based on validation feedback
      ↓
User: /validate-plan
      ↓ Returns: Score 92/100, ready for execution
      ↓
User: /generate-plan-review
      → Creates markdown report for stakeholder review
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

## Code Conventions

- **Language:** Python 3.10+
- **Async:** All tools are async, use `await` for coderef-context calls
- **Naming:** `snake_case` for functions, `PascalCase` for classes
- **Type Hints:** Full type hints required (checked by mypy)
- **Error Handling:** Use try-catch with graceful fallbacks when calling coderef-context
- **Logging:** Use `logger_config.logger` for all logging

### Important MCP Patterns

```python
# Tool definition pattern
Tool(
    name="tool_name",
    description="Human-readable description",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
)

# Async tool handler
@app.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "tool_name":
        result = await async_operation(arguments)
        return [TextContent(type="text", text=result)]
```

---

## Critical Integration: coderef-context

### When coderef-context is REQUIRED
- Creating plans (needs code analysis)
- Assessing risk/impact
- Identifying patterns for consistency
- Dependency mapping

### When coderef-context is OPTIONAL
- Updating existing plans
- Tracking progress
- Generating documentation
- Archiving features

### Error Handling

All coderef-context calls use graceful fallback:

```python
try:
    result = await mcp_client.call_tool("coderef_scan", {
        "project_path": project_path
    })
except Exception as e:
    logger.warning(f"coderef-context unavailable: {e}, using filesystem scan")
    # Fallback: manual filesystem analysis
```

---

## Do Not

- ❌ Edit coderef/archived/ manually (use `/archive-feature` instead)
- ❌ Modify coderef/workorder/{feature}/plan.json directly during execution
- ❌ Create workorders without using `/create-workorder` (breaks tracking)
- ❌ Update deliverables metrics manually (use `/update-deliverables` to auto-extract from git)
- ❌ Forget to call coderef-context when creating plans (defeats purpose of code intelligence)
- ❌ Commit workorder tracking without logging via `/log-workorder`
- ❌ Mix coderef-docs and coderef-workflow operations (use slash commands for coordination)

---

## Important Context

### The Ecosystem

This is part of a 4-server ecosystem:

1. **coderef-personas** (expert AI personas)
2. **coderef-context** (code intelligence via AST analysis)
3. **coderef-docs** (documentation generation + slash commands)
4. **coderef-workflow** (orchestration + planning)

All 4 servers must be running for full functionality.

### MCP Configuration

Configured in `~/.mcp.json` (global) and `.mcp.json` (project):

```json
{
  "mcpServers": {
    "coderef-workflow": {
      "command": "python",
      "args": ["C:/path/to/coderef-workflow/server.py"]
    }
  }
}
```

### Slash Commands

Slash commands are defined in `coderef-docs/.claude/commands/` and orchestrate coderef-workflow tools. Always use slash commands (like `/create-workorder`) rather than calling tools directly, as they provide structured workflows.

---

## Useful Resources

- **CODEREF_INTEGRATION_GUIDE.md** - Deep dive on coderef-context integration
- **CODEREF_TYPE_REFERENCE.md** - Schemas for context.json, plan.json, etc.
- **SETUP_GUIDE.md** - Installation and configuration
- **README.md** - User-facing overview
- **coderef/workorder/README.md** - How features are structured

---

## Recent Changes (v1.1.0)

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

## Previous Changes (v1.0.0)

- ✅ Complete feature lifecycle management
- ✅ Context-based planning with coderef-context integration
- ✅ Multi-agent task coordination
- ✅ Automated deliverables tracking
- ✅ Feature archival system
- ✅ Risk assessment with code intelligence
- ✅ Plan validation and scoring (0-100)

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
