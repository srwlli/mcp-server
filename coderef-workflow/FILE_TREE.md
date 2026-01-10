# coderef-workflow File Tree

```
coderef-workflow/
├── .claude/
│   └── settings.local.json
│
├── .coderef/                           # Code intelligence outputs
│   ├── index.json                      # Scanned code inventory
│   ├── graph.json                      # Dependency graph
│   ├── context.md                      # Human-readable context
│   ├── doc_generation_data.json        # Documentation metadata
│   ├── diagrams/                       # Visual dependency diagrams
│   │   ├── calls.mmd                   # Call graph (Mermaid)
│   │   ├── dependencies.dot            # Dependencies (Graphviz)
│   │   ├── dependencies.mmd            # Dependencies (Mermaid)
│   │   └── imports.mmd                 # Import graph (Mermaid)
│   ├── exports/                        # Export formats
│   │   ├── diagram-wrapped.md          # Diagram with usage notes
│   │   ├── graph.json                  # Graph data (JSON)
│   │   └── graph.jsonld                # Graph data (JSON-LD)
│   └── reports/                        # Analysis reports
│       ├── complexity/
│       │   └── README.md
│       ├── coverage.json               # Test coverage
│       ├── drift.json                  # Code drift detection
│       ├── patterns.json               # Code patterns
│       └── validation.json             # Validation results
│
├── coderef/                            # Feature workspaces
│   ├── workorder/                      # Active features
│   │   └── workflow-command-simplification/
│   │       ├── context.json
│   │       ├── analysis.json
│   │       ├── plan.json
│   │       └── DELIVERABLES.md
│   ├── archived/                       # Completed features
│   │   └── index.json
│   └── workorder-log.txt              # Global audit trail
│
├── generators/                         # Plan & analysis generators
│   ├── __init__.py
│   ├── analysis_generator.py          # Project analysis
│   ├── plan_generator.py              # Plan.json creation
│   └── planning_analyzer.py           # Planning intelligence
│
├── src/                               # Core tool implementations
│   ├── __init__.py
│   ├── archiver.py                    # Feature archival
│   ├── context_gatherer.py            # Context collection
│   ├── deliverables_manager.py        # Deliverables tracking
│   ├── mcp_client.py                  # MCP client for coderef-context
│   ├── plan_executor.py               # Plan execution
│   ├── tool_handlers.py               # MCP tool handlers (24 tools)
│   └── validators.py                  # Input validation
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_plan_executor.py
│   ├── test_planning_analyzer.py
│   └── test_mcp_client.py
│
├── server.py                          # MCP server entry point
├── pyproject.toml                     # Project metadata & dependencies
├── uv.lock                            # Dependency lockfile
│
├── README.md                          # User documentation
├── CLAUDE.md                          # AI context (this file)
├── SETUP_GUIDE.md                     # Installation guide
├── FILE_TREE.md                       # This file
│
└── Documentation/                     # Reference docs
    ├── CODEREF_INTEGRATION_GUIDE.md   # Integration with coderef-context
    ├── CODEREF_TYPE_REFERENCE.md      # Type definitions
    └── CODEREF_CONTEXT_MCP_VISION.md  # Architecture vision
```

## Key Directories

### `/src/` - Core Tool Implementations
Contains the 24 MCP tool handlers and supporting modules:
- **tool_handlers.py** - All 24 MCP tool implementations
- **mcp_client.py** - Async client for calling coderef-context
- **plan_executor.py** - Executes implementation plans
- **validators.py** - Schema validation

### `/generators/` - Planning Intelligence
- **planning_analyzer.py** - Reads .coderef/ for fast planning
- **analysis_generator.py** - Generates project analysis
- **plan_generator.py** - Creates 10-section plan.json

### `/coderef/workorder/` - Active Features
Each feature gets a directory with:
- `context.json` - Requirements & constraints
- `analysis.json` - Project analysis
- `plan.json` - 10-section implementation plan
- `DELIVERABLES.md` - Progress tracking

### `/.coderef/` - Code Intelligence
Pre-scanned code intelligence data for 5-10x faster planning:
- `index.json` - Complete code inventory
- `reports/patterns.json` - Coding conventions
- `reports/coverage.json` - Test coverage gaps

## Files by Purpose

### Planning Workflow
- `src/tool_handlers.py:gather_context()` - UC-1: Collect requirements
- `generators/planning_analyzer.py` - UC-1: Analyze project
- `generators/plan_generator.py` - UC-1: Create plan.json
- `src/validators.py` - UC-1: Validate plan quality

### Execution Tracking
- `src/plan_executor.py` - UC-2: Execute tasks
- `src/deliverables_manager.py` - UC-2: Track progress
- `src/tool_handlers.py:update_task_status()` - UC-2: Update status

### Documentation
- `src/tool_handlers.py:update_all_documentation()` - UC-3: Update docs
- `src/deliverables_manager.py` - UC-3: Git metrics

### Archival
- `src/archiver.py` - UC-4: Archive features
- `coderef/archived/` - UC-4: Historical storage

## Recent Additions (v1.4.0)
- Simplified `/create-workorder` workflow (11 steps → 9 steps)
- User provides context directly (no interactive Q&A)
- Uses .coderef/ exclusively (no fallbacks)
- Removed DELIVERABLES.md from planning step
- Removed multi-agent decision step

## Stats
- **24 MCP Tools** across 6 categories
- **40+ Slash Commands** (in coderef-docs)
- **10-Section Plan Format** (standard structure)
- **5-10x Faster Planning** (with .coderef/ integration)
```
