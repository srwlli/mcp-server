# coderef-workflow Root - File Organization Guide

**Date:** December 27, 2025
**Status:** Cleaned and organized

---

## Directory Structure

```
coderef-workflow/
├── README.md                     # Quick start (MASTER)
├── CLAUDE.md                     # Behavior definition (MASTER)
├── pyproject.toml                # Dependencies (MASTER)
├── communication.json            # Workorder tracking (MASTER)
├── uv.lock                       # Dependency lock (MASTER)
│
├── src/                          # Python source files (CORE)
│   ├── server.py                 # MCP server entry (35 tools)
│   ├── tool_handlers.py          # Tool implementations (4,500+ LOC)
│   ├── type_defs.py              # Type definitions (90+ types)
│   ├── constants.py              # Configuration constants
│   ├── error_responses.py        # Error handling
│   ├── handler_decorators.py     # Decorators (@log_invocation, @mcp_error_handler)
│   ├── handler_helpers.py        # Shared utilities
│   ├── logger_config.py          # Logging configuration
│   ├── mcp_client.py             # coderef-context integration
│   ├── plan_format_validator.py  # Plan validation
│   └── schema_validator.py       # General schema validation
│
├── coderef/                      # CodeRef Ecosystem
│   ├── docs/                     # Documentation (ORGANIZED)
│   │   ├── guides/               # Implementation guides (4 files)
│   │   │   ├── SETUP_GUIDE.md
│   │   │   ├── CODEREF_INTEGRATION_GUIDE.md
│   │   │   ├── DIRECT_VS_SUBPROCESS.md
│   │   │   └── STANDALONE_PLAN_GENERATOR_LITE.md
│   │   ├── reports/              # Test & completion reports (4 files)
│   │   │   ├── TEST_SUITE_SUMMARY.md
│   │   │   ├── CREATE_WORKORDER_TEST_SUITE.md
│   │   │   ├── IMPLEMENTATION_COMPLETE.md
│   │   │   └── CODEREF_INJECTION_PROOF.md
│   │   ├── integration/          # Integration documentation (3 files)
│   │   │   ├── CODEREF_CONTEXT_INTEGRATION_REPORT.md
│   │   │   ├── CODEREF_CONTEXT_MCP_VISION.md
│   │   │   └── CODEREF_DOCS_INDEX.md
│   │   └── reference/            # Reference documentation (2 files)
│   │       ├── CODEREF_TYPE_REFERENCE.md
│   │       └── CODEREF_QUICKREF.md
│   ├── foundation-docs/          # Generated foundation documentation
│   │   ├── API.md
│   │   ├── ARCHITECTURE.md
│   │   ├── SCHEMA.md
│   │   └── project-context.json
│   ├── schemas/                  # JSON schemas
│   │   └── plan.schema.json
│   ├── workorder/                # Active workorders (v1.1.0)
│   │   ├── breaking-change-workflow-integration/
│   │   ├── create-workorder-test/
│   │   ├── fix-workflow-bugs-and-rename/
│   │   ├── server-test/
│   │   └── test-coderef-injection/
│   ├── working/                  # Legacy features (deprecated)
│   └── testing/                  # Test fixtures
│
├── generators/                   # Code generation modules (17 files)
│   ├── planning_generator.py
│   ├── planning_analyzer.py
│   ├── plan_validator.py
│   ├── review_formatter.py
│   ├── risk_generator.py
│   ├── coderef_foundation_generator.py
│   ├── handoff_generator.py
│   ├── features_inventory_generator.py
│   └── [9 more generators]
│
├── templates/                    # Template files
│   ├── power/                    # POWER framework templates
│   ├── tools/                    # Tool templates
│   └── handoff/                  # Agent handoff templates
│
└── tests/                        # Test suite
```

---

## Root-Level Files Explained

### 🔵 MASTER CONFIGURATION FILES (Keep in Root)

These are the **source of truth** for the MCP server:

- **README.md**
  - Role: Quick start guide
  - Purpose: Entry point for developers
  - Update: When server setup changes

- **CLAUDE.md**
  - Role: Orchestrator behavior definition
  - Purpose: Core operating instructions
  - Update: When server behavior changes

- **pyproject.toml**
  - Role: Project dependencies and metadata
  - Purpose: Package definition and entry points
  - Update: When dependencies change
  - Critical: Entry point must reference correct module paths

- **communication.json**
  - Role: Server-level workorder tracking
  - Purpose: Orchestration status
  - Update: When delegating work to this server

- **uv.lock**
  - Role: Locked dependency versions
  - Purpose: Reproducible builds
  - Auto-generated: Don't edit manually

### 🟢 PYTHON SOURCE FILES (Keep in Root)

These are **CORE RUNTIME FILES** - do not move to subdirectories:

- **server.py** (54KB, 1,124 LOC)
  - MCP server entry point
  - Registers all 35 tools
  - Critical: Import paths depend on root location

- **tool_handlers.py** (163KB, 4,500+ LOC)
  - All tool implementations
  - Core functionality

- **type_defs.py** (34KB, 1,000 LOC)
  - 90+ TypedDict definitions
  - Type safety and validation

- **constants.py** (13KB)
  - Centralized configuration
  - Path definitions

- **Utility modules** (9 files)
  - error_responses.py - Error handling
  - handler_decorators.py - @log_invocation, @mcp_error_handler
  - handler_helpers.py (46KB) - Shared utilities
  - logger_config.py - Logging setup
  - mcp_client.py - coderef-context integration
  - plan_format_validator.py - Plan validation
  - schema_validator.py - Schema validation

### 📊 ORGANIZED DOCUMENTATION

#### `/coderef/docs/guides/` (4 files)
Implementation and setup documentation:
- SETUP_GUIDE.md - Server installation & configuration
- CODEREF_INTEGRATION_GUIDE.md - How to integrate coderef-context
- DIRECT_VS_SUBPROCESS.md - Technical comparison
- STANDALONE_PLAN_GENERATOR_LITE.md - Standalone generator usage

**Purpose:** Reference for developers implementing or extending the server

#### `/coderef/docs/reports/` (4 files)
Test results and completion reports:
- TEST_SUITE_SUMMARY.md - Test suite overview
- CREATE_WORKORDER_TEST_SUITE.md - Workorder testing
- IMPLEMENTATION_COMPLETE.md - Completion status
- CODEREF_INJECTION_PROOF.md - Injection testing results

**Purpose:** Quality assurance and verification tracking

#### `/coderef/docs/integration/` (3 files)
Integration and architecture documentation:
- CODEREF_CONTEXT_INTEGRATION_REPORT.md - Integration analysis
- CODEREF_CONTEXT_MCP_VISION.md - Vision for MCP ecosystem
- CODEREF_DOCS_INDEX.md - Documentation index

**Purpose:** Strategic integration planning

#### `/coderef/docs/reference/` (2 files)
Reference documentation:
- CODEREF_TYPE_REFERENCE.md - Type definitions reference
- CODEREF_QUICKREF.md - Quick reference guide

**Purpose:** Developer reference materials

### 🏗️ CODE GENERATION & TEMPLATES

- `/generators/` (17 modules)
  - planning_generator.py - Creates plan.json
  - planning_analyzer.py - Project analysis
  - plan_validator.py - Quality scoring (0-100)
  - risk_generator.py - 5-dimension risk assessment
  - handoff_generator.py - Agent handoff automation
  - [12 more generators]

- `/templates/`
  - POWER framework templates
  - Tool-specific templates
  - Handoff templates

### 📋 METADATA & WORKORDERS

- `/coderef/workorder/` (5 active workorders)
  - WO-BREAKING-CHANGE-INTEGRATION-001 - Planned
  - WO-CREATE-WORKORDER-TEST-* - Testing
  - WO-FIX-WORKFLOW-* - Completed (v1.1.0)
  - WO-SERVER-TEST-* - Testing
  - WO-TEST-CODEREF-* - Testing

- `/coderef/foundation-docs/` (Auto-generated)
  - API.md, ARCHITECTURE.md, SCHEMA.md
  - project-context.json

---

## Why This Structure Works

### ✅ Maintains MCP Server Functionality
- Python files stay in root (entry points require this)
- No import path breakage
- pyproject.toml unchanged

### ✅ Organizes Documentation Logically
- guides/ → How to use and integrate
- reports/ → Quality assurance artifacts
- integration/ → Strategic planning
- reference/ → Developer lookup

### ✅ Follows Separation of Concerns
- Master files (README, CLAUDE, pyproject, communication.json) = Configuration
- Python files (server.py, etc.) = Runtime
- Generators = Code generation
- Coderef ecosystem = Metadata & tracking
- Docs = Knowledge base

---

## Best Practices

### Daily Operations
1. Refer to **CLAUDE.md** for server behavior
2. Check **communication.json** for active workorders
3. Review **coderef/workorder/** for current features

### When Adding Documentation
1. Determine category: guides, reports, integration, or reference
2. Add to appropriate `/coderef/docs/{category}/` folder
3. Update this file if adding new category

### When Implementing Features
1. Update `/coderef/docs/guides/` with implementation details
2. Create workorder in `/coderef/workorder/{feature-name}/`
3. Generate reports to `/coderef/docs/reports/` when complete

### When Maintaining Python Code
- Keep all .py files in root (do not move)
- Update imports only if absolutely necessary
- Always test MCP server startup after changes

---

## Root File Maintenance

### When to Update:

**Daily:**
- `communication.json` - Track active workorders

**Weekly:**
- `CLAUDE.md` - Update if server behavior changes
- `pyproject.toml` - Update if dependencies change

**Per Feature:**
- Add to `/coderef/docs/guides/` - Implementation guide
- Add to `/coderef/docs/reports/` - Completion report
- Update `/coderef/workorder/` - Feature tracking

---

## Quick Reference

**What's the entry point?**
→ server.py (in root)

**How do I integrate coderef-context?**
→ Read coderef/docs/guides/CODEREF_INTEGRATION_GUIDE.md

**What are the test results?**
→ Check coderef/docs/reports/ folder

**What's the 35-tool specification?**
→ Read coderef/foundation-docs/API.md

**Are there active features being built?**
→ Check coderef/workorder/ folder

---

*Generated: 2025-12-27*
