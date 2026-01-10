# CODEREF-WORKFLOW MCP Server

**Resource Sheet**
**Version:** 1.4.0
**Type:** MCP Server (Model Context Protocol)
**Status:** ✅ Production
**Generated:** 2026-01-08

---

## Architecture & Design

### Overview

`coderef-workflow` is an enterprise-grade Model Context Protocol (MCP) server providing **24 specialized tools** for feature lifecycle orchestration. It handles context gathering, planning, execution tracking, deliverables management, and feature archiving using a workorder-centric architecture with full code intelligence integration.

### Core Innovation

- **Workorder-Centric Architecture**: Complete audit trail with `WO-{FEATURE}-{CATEGORY}-{SEQ}` format
- **10-Section Plan Format**: Structured implementation plans with task breakdown, dependencies, testing strategy
- **Code Intelligence Integration**: Leverages `.coderef/` pre-scanned data for 5-10x faster planning
- **Multi-Agent Coordination**: Parallel agent execution with communication.json orchestration
- **Agentic Documentation**: Auto-increments versions, updates README/CHANGELOG/CLAUDE.md

### Component Type

**Server Type:** MCP Protocol Server (JSON-RPC 2.0 over stdio)
- Asynchronous Python implementation (asyncio)
- Tool-based architecture with 24 exposed tools
- Stateless request/response model (state persisted to filesystem)

### Design Pattern

**Architecture Pattern:** Orchestration Layer with Generator Factory
- **Orchestrator**: Central coordination of feature lifecycle
- **Generator Factory**: Specialized generators for plan, analysis, risk assessment
- **Integration Hub**: Connects coderef-context, coderef-docs, coderef-personas
- **State Machine**: 9-step lifecycle from initialization → archival

### Dependencies

**Core Dependencies:**
- `mcp` (1.0+) - Model Context Protocol SDK
- `asyncio` - Async/await support
- `jsonschema` (4.0+) - Schema validation
- `pathlib` - Path manipulation
- `gitpython` - Git integration

**External Integration:**
- `coderef-context` MCP - Code intelligence (scan, query, impact, patterns)
- `coderef-docs` MCP - Documentation generation (foundation docs, changelog)
- `coderef-personas` MCP - Domain expert activation
- `coderef-testing` MCP - Test automation
- Git - Change tracking and metrics

**Development Dependencies:**
- `pytest` (8.0+) - Testing framework
- `pytest-asyncio` - Async test support
- `mypy` - Type checking
- `ruff` - Linting

### Code Organization

```
coderef-workflow/
├── server.py                          # MCP entry point (24 tool definitions)
├── src/                               # Core tool implementations
│   ├── tool_handlers.py               # 24 MCP tool handlers (2,500+ lines)
│   ├── mcp_client.py                  # Async client for coderef-context
│   ├── plan_executor.py               # Plan execution engine
│   ├── context_gatherer.py            # Context collection
│   ├── deliverables_manager.py        # Metrics tracking
│   ├── archiver.py                    # Feature archival
│   └── validators.py                  # Input validation
├── generators/                        # Plan & analysis generators
│   ├── planning_analyzer.py           # PlanningAnalyzer (reads .coderef/)
│   ├── plan_generator.py              # 10-section plan synthesis
│   ├── analysis_generator.py          # Project analysis
│   ├── plan_validator.py              # Quality scoring (0-100)
│   ├── review_formatter.py            # Markdown reports
│   └── risk_generator.py              # 5-dimension risk assessment
├── coderef/                           # Feature workspaces
│   ├── workorder/                     # Active features
│   │   └── {feature-name}/
│   │       ├── context.json
│   │       ├── analysis.json
│   │       ├── plan.json
│   │       ├── communication.json     # Multi-agent (optional)
│   │       └── DELIVERABLES.md
│   ├── archived/                      # Completed features
│   │   └── index.json
│   └── workorder-log.txt             # Global audit trail
├── tests/                             # Test suite
│   ├── test_plan_executor.py
│   ├── test_planning_analyzer.py
│   └── test_mcp_client.py
└── Documentation/
    ├── CLAUDE.md                      # AI context (comprehensive)
    ├── README.md                      # User-facing docs
    ├── SETUP_GUIDE.md                 # Installation
    └── FILE_TREE.md                   # Project structure
```

---

## Integration Points

### Integrates With

**Upstream Dependencies:**

1. **coderef-context** (MCP Server)
   - **Purpose:** Code intelligence for planning
   - **Tools Called:** `coderef_scan`, `coderef_query`, `coderef_patterns`, `coderef_coverage`, `coderef_impact`
   - **Data Source:** Reads `.coderef/index.json`, `.coderef/reports/patterns.json`, `.coderef/reports/coverage.json`
   - **Integration Point:** `planning_analyzer.py` lines 215, 397, 445

2. **coderef-docs** (MCP Server)
   - **Purpose:** Documentation generation
   - **Tools Called:** `coderef_foundation_docs`, `add_changelog_entry`, `update_all_documentation`
   - **Integration Point:** Post-implementation documentation updates
   - **Shared State:** Workorder tracking via `workorder_id`

3. **Git Repository**
   - **Purpose:** Change tracking and metrics
   - **Operations:** `git log --grep`, `git diff`, `git status`
   - **Integration Point:** `deliverables_manager.py`, `verify_agent_completion`

4. **.coderef/ Structure** (NEW in v1.3.0)
   - **Purpose:** Pre-scanned code intelligence
   - **Files Read:** `index.json`, `reports/patterns.json`, `reports/coverage.json`, `reports/drift.json`
   - **Performance:** 5-10x faster planning vs live scanning
   - **Fallback:** Calls coderef_scan if .coderef/ missing

**Downstream Consumers:**

1. **AI Agents** (Primary users)
   - Call tools via MCP protocol
   - Receive plan structure and TodoWrite task lists
   - Update task status during implementation

2. **User Workflows**
   - Execute via slash commands in `~/.claude/commands/`
   - `/create-workorder` - Full planning workflow
   - `/align-plan` - Align with todo list
   - `/update-deliverables` - Capture git metrics
   - `/archive-feature` - Complete lifecycle

3. **coderef-personas**
   - **Integration:** Personas activate before execution
   - **Pattern:** User calls `/create-workorder` → AI recommends persona (Ava, Marcus, Quinn) → `/execute-plan`

### Data Flow

```mermaid
graph TB
    A[User Request] --> B[/create-workorder]
    B --> C[gather_context]
    C --> D[analyze_project_for_planning]
    D --> E{.coderef/ exists?}
    E -->|Yes| F[Read index/patterns/coverage - 5s]
    E -->|No| G[Call coderef_scan - 30-60s]
    F --> H[create_plan]
    G --> H
    H --> I[10-Section plan.json]
    I --> J[/align-plan]
    J --> K[execute_plan - TodoWrite]
    K --> L[Agent Implementation]
    L --> M[update_task_status]
    M --> N[update_deliverables]
    N --> O[update_all_documentation]
    O --> P[archive_feature]
    P --> Q[coderef/archived/]
```

### API Surface

**MCP Tools Exposed (24 total):**

**Planning & Analysis (6):**
- `gather_context` - Collect feature requirements
- `analyze_project_for_planning` - Scan codebase (uses .coderef/)
- `get_planning_template` - Get 10-section template
- `create_plan` - Generate implementation plan
- `validate_implementation_plan` - Score quality (0-100)
- `generate_plan_review_report` - Markdown review

**Execution & Tracking (6):**
- `execute_plan` - Align with todo list (v1.4.0 simplified)
- `update_task_status` - Track task progress
- `track_agent_status` - Multi-agent dashboard
- `generate_handoff_context` - Create claude.md
- `assign_agent_task` - Assign to agent (1-10)
- `verify_agent_completion` - Validate work

**Deliverables & Documentation (4):**
- `generate_deliverables_template` - Create DELIVERABLES.md
- `update_deliverables` - Git metrics
- `update_all_documentation` - Auto-increment version
- `aggregate_agent_deliverables` - Combine metrics

**Risk & Integration (2):**
- `assess_risk` - 5-dimension scoring
- `generate_agent_communication` - Multi-agent coordination

**Archival & Inventory (4):**
- `archive_feature` - Move to archive
- `generate_features_inventory` - List all features
- `audit_plans` - Health check
- `coderef_foundation_docs` - Unified generator

**Workorder Tracking (2):**
- `log_workorder` - Add to global log
- `get_workorder_log` - Query history

### Configuration

**Global Paths:**
- Workorder: `coderef/workorder/` (active features)
- Archive: `coderef/archived/` (completed features)
- Log: `coderef/workorder-log.txt` (audit trail)
- Intelligence: `.coderef/` (pre-scanned data)

**Environment Variables:**
- `CODEREF_CLI_PATH` - Path to @coderef/core CLI (for coderef-context)
- `LOG_LEVEL` - Logging verbosity (default: INFO)

**MCP Configuration (`~/.mcp.json`):**
```json
{
  "mcpServers": {
    "coderef-workflow": {
      "command": "python",
      "args": ["-m", "coderef-workflow.server"],
      "env": {}
    },
    "coderef-context": {
      "command": "python",
      "args": ["-m", "coderef-context.server"],
      "env": {"CODEREF_CLI_PATH": "C:/path/to/coderef-system/packages/cli"}
    }
  }
}
```

---

## State Management

### State Ownership

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **context.json** | gather_context | Requirements | `coderef/workorder/{feature}/` | Filesystem JSON |
| **analysis.json** | analyze_project_for_planning | Analysis | `coderef/workorder/{feature}/` | Filesystem JSON |
| **plan.json** | create_plan | Implementation Plan | `coderef/workorder/{feature}/` | Filesystem JSON |
| **task.status** | update_task_status | Task Progress | Embedded in plan.json | `plan.json` phases[].tasks[] |
| **communication.json** | generate_agent_communication | Multi-Agent | `coderef/workorder/{feature}/` | Filesystem JSON |
| **DELIVERABLES.md** | generate_deliverables_template | Metrics | `coderef/workorder/{feature}/` | Filesystem Markdown |
| **workorder-log.txt** | log_workorder | Audit Trail | `coderef/` | Plain Text |

### Data Schemas

**plan.json Schema (10-section structure):**

```json
{
  "META_DOCUMENTATION": {
    "feature_name": "string",
    "workorder_id": "WO-{FEATURE}-{CATEGORY}-{SEQ}",
    "status": "planning | in_progress | completed | archived",
    "version": "1.0",
    "created_at": "ISO 8601",
    "updated_at": "ISO 8601"
  },
  "0_PREPARATION": {
    "foundation_docs": {},
    "coding_standards": {},
    "reference_components": {},
    "key_patterns": [],
    "technology_stack": {},
    "gaps_and_risks": []
  },
  "1_EXECUTIVE_SUMMARY": {
    "what": "Brief description",
    "why": "Rationale",
    "how": "Approach"
  },
  "2_RISK_ASSESSMENT": {
    "breaking_changes": {"severity": "low | medium | high | critical"},
    "security": {},
    "performance": {}
  },
  "3_CURRENT_STATE_ANALYSIS": {},
  "4_KEY_FEATURES": [],
  "5_TASK_ID_SYSTEM": {
    "format": "CATEGORY-NNN",
    "categories": {}
  },
  "6_IMPLEMENTATION_PHASES": [
    {
      "phase_id": "phase_1",
      "tasks": [
        {
          "task_id": "SETUP-001",
          "description": "string",
          "status": "pending | in_progress | completed | blocked",
          "dependencies": []
        }
      ]
    }
  ],
  "7_TESTING_STRATEGY": {},
  "8_SUCCESS_CRITERIA": {}
}
```

### State Lifecycle

```
1. INITIALIZATION → server.py loads
2. CONTEXT GATHERING → gather_context saves context.json
3. ANALYSIS → analyze_project_for_planning reads .coderef/, saves analysis.json
4. PLANNING → create_plan generates plan.json (10 sections)
5. VALIDATION → validate_implementation_plan scores 0-100
6. EXECUTION → execute_plan generates TodoWrite tasks
7. TRACKING → update_task_status updates plan.json
8. DELIVERABLES → update_deliverables parses git log
9. DOCUMENTATION → update_all_documentation bumps version
10. ARCHIVAL → archive_feature moves to coderef/archived/
```

---

## Testing

### Test Coverage

**Test Suite Statistics:**
- **Total Tests:** 15+
- **Pass Rate:** 100% (4 critical tests validated)
- **Coverage:** 75%+ (core workflow)

**Test Categories:**
1. **Integration Tests** (4)
   - Feature creation → execution → archival
   - Multi-agent coordination
   - .coderef/ integration
   - Workorder ID auto-generation

2. **Unit Tests** (11)
   - Tool handler validation
   - Plan generator
   - Analysis generator
   - MCP client

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_plan_executor.py -v

# With coverage
pytest --cov=src --cov=generators --cov-report=html tests/

# Integration tests only
pytest tests/test_*integration*.py -v
```

### Known Issues

**Resolved in v1.4.0:**
- ✅ Fixed deliverables crash (tool_handlers.py:1607)
- ✅ Fixed plan status lifecycle (starts "planning" not "complete")

**Current Gaps:**
- Plan status not auto-updated (requires manual update_task_status)
- TodoWrite task list drift (UI-only, plan.json is canonical)
- No real-time multi-agent locking (sequential coordination only)

---

## Performance

### Metrics

**Tool Performance Benchmarks:**

| Tool | Typical Latency | Notes |
|------|----------------|-------|
| `gather_context` | 1-2s | JSON validation + write |
| `analyze_project_for_planning` | **5-10s** | With .coderef/ (v1.3.0) |
| `analyze_project_for_planning` | 30-60s | Without .coderef/ (fallback) |
| `create_plan` | 10-20s | AI synthesis of 10 sections |
| `validate_implementation_plan` | 2-5s | Quality scoring |
| `execute_plan` | 1-2s | TodoWrite generation |
| `update_deliverables` | 3-8s | Git log parsing (500 commits) |
| `archive_feature` | 1-2s | Filesystem move |

### Optimization Strategies

**1. .coderef/ Integration (v1.3.0) - 5-10x Speedup**
- **Before:** Live `coderef_scan` → 30-60 seconds
- **After:** Read `.coderef/index.json` → 5-10 seconds
- **Benefit:** Removes redundant scanning, uses pre-computed data
- **Trade-off:** Requires `coderef scan` run before planning

**2. Removed Foundation Docs Generation (v1.3.0)**
- **Before:** Step 3 of `/create-workorder` generated 5 docs → 30-60s overhead
- **After:** Removed from workflow, now optional post-implementation
- **Benefit:** Reduced `/create-workorder` from 11 steps to 10 steps

**3. Simplified Workflow (v1.4.0)**
- **Before:** 11 steps with interactive Q&A, multi-agent decision
- **After:** 9 steps, user provides context directly, single-agent only
- **Benefit:** Faster onboarding, clearer workflow

### Bottlenecks

1. **AI Synthesis** (create_plan)
   - 10-20 seconds for plan generation
   - Depends on LLM latency
   - Not parallelizable (sequential sections)

2. **Git Log Parsing** (update_deliverables)
   - Linear growth with commit count
   - 500 commits = 3-8 seconds
   - Bottleneck: subprocess git log --numstat

3. **Pattern Identification** (planning_analyzer.py)
   - Fallback regex analysis: 15-30 seconds (200 files)
   - Mitigated by .coderef/reports/patterns.json

### Scalability

**Project Size Support:**
- Small (<1k LOC): All operations < 5s
- Medium (1k-10k LOC): Planning < 20s (with .coderef/)
- Large (10k-100k LOC): Planning < 30s (requires .coderef/)
- Very Large (>100k LOC): Analysis benefits from pre-scanning

**Resource Usage:**
- **Memory:** ~100MB base, ~300MB peak (large project analysis)
- **CPU:** Single-threaded asyncio, CPU-bound during plan generation
- **Disk:** 10-500KB per feature directory

---

## Usage Examples

### Example 1: Create Feature Workorder (v1.4.0 Simplified)

```bash
# User workflow
/create-workorder

# Steps:
# 1. User provides context directly (no Q&A)
# 2. System uses .coderef/ exclusively (errors if missing)
# 3. Creates plan.json only (DELIVERABLES.md removed)
# 4. Aligns with TodoWrite (Step 8)
# 5. Git commit (Step 9)

# Output:
# ✓ Context saved: coderef/workorder/dark-mode-toggle/context.json
# ✓ Analysis saved: coderef/workorder/dark-mode-toggle/analysis.json
# ✓ Plan created: coderef/workorder/dark-mode-toggle/plan.json
# ✓ Workorder ID: WO-DARK-MODE-UI-001
# ✓ TodoWrite aligned with 12 tasks
```

### Example 2: Execute Plan with TodoWrite

```bash
# Align plan with todo list
/align-plan dark-mode-toggle

# Output: TodoWrite task list
# ☐ WO-DARK-MODE-UI-001 | SETUP-001: Initialize dark mode context
# ☐ WO-DARK-MODE-UI-001 | IMPL-001: Create ThemeProvider component
# ☐ WO-DARK-MODE-UI-001 | IMPL-002: Add dark mode toggle to settings
# ... (12 tasks total)

# Agent implements task
# AI: "I'm marking SETUP-001 as in_progress"
await call_tool("update_task_status", {
  "feature_name": "dark-mode-toggle",
  "task_id": "SETUP-001",
  "status": "in_progress"
})

# After completion
await call_tool("update_task_status", {
  "feature_name": "dark-mode-toggle",
  "task_id": "SETUP-001",
  "status": "completed"
})
```

### Example 3: Multi-Agent Coordination

```bash
# Create plan with multi-agent support
/create-workorder --multi-agent

# System generates communication.json
# Lloyd (coordinator) assigns tasks
await call_tool("assign_agent_task", {
  "feature_name": "dark-mode-toggle",
  "agent_number": 1,
  "phase_id": "phase_1"
})

# Agent 1 works on phase_1
# ...

# Lloyd verifies completion
await call_tool("verify_agent_completion", {
  "feature_name": "dark-mode-toggle",
  "agent_number": 1
})

# Output:
# ✓ Git diff shows 5 files changed
# ✓ Forbidden files unchanged: server.py, critical.py
# ✓ Success criteria met: All tests pass
# ✓ Agent 1 status → VERIFIED
```

### Example 4: Update Deliverables and Documentation

```bash
# Update deliverables with git metrics
/update-deliverables dark-mode-toggle

# Output:
# ✓ Commits: 12 (filtered by WO-DARK-MODE-UI-001)
# ✓ Lines Changed: +345 -67 = 412 total
# ✓ Contributors: willh, claude-agent
# ✓ Time Elapsed: 2.5 hours

# Auto-update documentation with version bump
await call_tool("update_all_documentation", {
  "project_path": "/path/to/project",
  "change_type": "feature",
  "feature_description": "Added dark mode toggle",
  "workorder_id": "WO-DARK-MODE-UI-001",
  "files_changed": ["src/theme.ts", "src/Settings.tsx"]
})

# Output:
# ✓ Version bumped: 1.0.0 → 1.1.0 (feature = minor bump)
# ✓ Updated README.md (version + What's New)
# ✓ Updated CLAUDE.md (version history)
# ✓ Updated CHANGELOG.json (structured entry)
```

### Example 5: Archive Completed Feature

```bash
/archive-feature dark-mode-toggle

# System checks DELIVERABLES.md status
# If status = "Complete" → archives immediately
# If status != "Complete" → prompts user

# Output:
# ✓ Moved: coderef/workorder/dark-mode-toggle → coderef/archived/
# ✓ Updated archive index.json
# ✓ Feature archived with workorder WO-DARK-MODE-UI-001
```

---

## Related Documentation

### Internal References

- **AI Context:** `CLAUDE.md` - Comprehensive AI agent documentation (1,000+ lines)
- **User Guide:** `README.md` - User-facing overview
- **Setup Guide:** `SETUP_GUIDE.md` - Installation and configuration
- **Integration Guide:** `CODEREF_INTEGRATION_GUIDE.md` - coderef-context integration
- **Type Reference:** `CODEREF_TYPE_REFERENCE.md` - TypedDict schemas
- **File Tree:** `FILE_TREE.md` - Project structure

### External Resources

- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **CodeRef Ecosystem:** `C:\Users\willh\.mcp-servers\CLAUDE.md`
- **coderef-context:** `C:\Users\willh\.mcp-servers\coderef-context\CLAUDE.md`
- **coderef-docs:** `C:\Users\willh\.mcp-servers\coderef-docs\CLAUDE.md`
- **coderef-personas:** `C:\Users\willh\.mcp-servers\coderef-personas\CLAUDE.md`
- **@coderef/core:** `C:\Users\willh\Desktop\projects\coderef-system\packages\cli`

### Workorder History

**Active:**
- None (all workorders complete for v1.4.0)

**Recent Completed:**
- **WO-WORKFLOW-COMMAND-SIMPLIFICATION-001** (v1.4.0) - Simplified /create-workorder workflow
- **WO-CODEREF-OUTPUT-UTILIZATION-001** (v1.3.0) - .coderef/ integration for faster planning
- **WO-COMPLETE-WORKORDER-CMD-001** (v1.2.0) - Autonomous implementation command
- **WO-WORKFLOW-REFACTOR-001** (v1.1.0) - Workorder system implementation

**Full History:** `coderef/workorder-log.txt` (100+ archived workorders)

---

## Development

### Setup

```bash
# Clone and install
cd C:\Users\willh\.mcp-servers\coderef-workflow
uv sync

# Or with pip
pip install -e .

# Run server
python server.py

# Run tests
pytest tests/ -v

# Type check
mypy src/ generators/

# Lint
ruff check src/ generators/
```

### Contributing

**Code Style:**
- PEP 8 compliant
- Type hints required for public APIs
- Docstrings for all modules, classes, functions
- Async/await for all I/O operations
- Use TypedDict for structured data (see type_defs.py)

**Testing Requirements:**
- All new tools require integration tests
- Test both happy path and error cases
- Mock external MCP calls (coderef-context)
- Coverage > 75% for new code

**Documentation:**
- Update CLAUDE.md for architectural changes
- Update README.md for user-facing changes
- Add entries to workorder-log.txt
- Update version history in this resource sheet

### Key Files for Modification

**Adding New Tools:**
1. Define handler in `src/tool_handlers.py`
2. Register in `server.py` tool list
3. Add TypedDict schema in `type_defs.py` (if needed)
4. Add tests in `tests/`
5. Update CLAUDE.md and this resource sheet

**Modifying Plan Structure:**
1. Update `generators/plan_generator.py`
2. Update template in `feature-implementation-planning-standard.json`
3. Update validation in `generators/plan_validator.py`
4. Bump plan.json version in META_DOCUMENTATION
5. Update migration guide

**Adding New Generators:**
1. Create new file in `generators/`
2. Inherit from base class if applicable
3. Add tests
4. Register in tool handler
5. Update documentation

---

## Version History

**v1.4.0 (2025-01-04)** - Simplified Workflow
- Simplified `/create-workorder` (11 steps → 9 steps)
- User provides context directly (no interactive Q&A)
- Uses `.coderef/` exclusively (errors if missing)
- Removed DELIVERABLES.md from planning step
- Removed multi-agent decision step

**v1.3.0 (2025-01-02)** - .coderef/ Integration
- Integrated `.coderef/` pre-scanned data
- 5-10x faster planning (5-10s vs 30-60s)
- Automatic drift detection (warns if >10% stale)
- Removed redundant foundation docs generation from Step 3
- 3-tier fallback: .coderef/ → MCP tools → regex analysis

**v1.2.0 (2025-12-28)** - Autonomous Implementation
- Created `/complete-workorder` slash command
- Automatic task execution from plan.json
- Real-time TodoWrite progress tracking
- Integrated testing and deliverables updates

**v1.1.0 (2025-12-25)** - Workorder System
- Implemented workorder-centric architecture
- `WO-{FEATURE}-{CATEGORY}-{SEQ}` format
- Global audit trail in `workorder-log.txt`
- Path migration: `coderef/working/` → `coderef/workorder/`
- Fixed deliverables crash and plan status lifecycle

**v1.0.0 (2024-12-24)** - Initial Release
- Complete feature lifecycle management
- Context-based planning with coderef-context integration
- Multi-agent task coordination
- Automated deliverables tracking
- Feature archival system

---

## Known Issues & Sharp Edges

### Current Limitations

1. **Plan status not auto-updated**
   - `create_plan` sets status="planning", never auto-transitions
   - Workaround: Agents manually update plan.json or ignore status field

2. **TodoWrite task list drift**
   - TodoWrite shows UI state, plan.json is canonical
   - Workaround: Always trust plan.json status, sync after update_task_status

3. **Missing .coderef/ causes slow planning**
   - Falls back to regex analysis (30-60 seconds)
   - Mitigation: Always run `coderef scan {project_path}` before `/create-workorder`

4. **No real-time multi-agent locking**
   - communication.json assumes sequential coordination
   - No file locking or concurrency control
   - Mitigation: Manual agent coordination via Lloyd orchestrator

### Integration Gotchas

1. **coderef-context MCP server must be running**
   - If unavailable, falls back to regex analysis (slow)
   - Check: `python -m coderef-context.server` in separate terminal

2. **Workorder ID format strict validation**
   - Must be `WO-{FEATURE}-{CATEGORY}-{SEQ}` with 3-digit sequence
   - Rejects "WO-AUTH-1" (missing zero-padding)
   - Workaround: Omit workorder_id to auto-generate

3. **Git log requires workorder mentions**
   - `update_deliverables` searches `git log --grep="WO-{ID}"`
   - If developers don't include workorder ID in commits → 0 results
   - Recovery: Manual DELIVERABLES.md update

---

**Generated:** 2026-01-08
**Maintainer:** willh, Claude Code AI
**Status:** ✅ Production Ready
**License:** MIT
