# coderef-context File Tree

**Project:** coderef-context MCP Server
**Generated:** 2026-01-08
**Purpose:** Complete directory structure and file organization

---

## Root Structure

```
coderef-context/
├── .claude/                              # Claude Code configuration
│   ├── commands/                         # Custom slash commands
│   └── settings.local.json               # Local settings
│
├── .coderef/                             # Generated code intelligence outputs
│   ├── context.json                      # Structured project context
│   ├── context.md                        # Human-readable overview
│   ├── index.json                        # All code elements catalog
│   ├── graph.json                        # Dependency graph
│   ├── doc_generation_data.json          # Doc generation metadata
│   ├── generate_docs.py                  # Doc generator script
│   │
│   ├── diagrams/                         # Visual representations
│   │   ├── calls.mmd                     # Call graph (Mermaid)
│   │   ├── dependencies.mmd              # Dependencies (Mermaid)
│   │   ├── dependencies.dot              # Dependencies (GraphViz)
│   │   └── imports.mmd                   # Import graph (Mermaid)
│   │
│   ├── exports/                          # Export formats
│   │   ├── graph.json                    # Graph export (JSON)
│   │   ├── graph.jsonld                  # Graph export (JSON-LD)
│   │   └── diagram-wrapped.md            # Diagram with usage notes
│   │
│   ├── generated-docs/                   # Auto-generated documentation
│   │   ├── README.md                     # Project overview
│   │   ├── ARCHITECTURE.md               # Architecture details
│   │   └── API.md                        # API documentation
│   │
│   └── reports/                          # Analysis reports
│       ├── coverage.json                 # Test coverage analysis
│       ├── drift.json                    # Code drift detection
│       ├── patterns.json                 # Code patterns discovered
│       ├── validation.json               # Reference validation
│       └── complexity/                   # Complexity metrics
│           └── README.md                 # Metrics overview
│
├── coderef/                              # CodeRef ecosystem artifacts
│   ├── docs/                             # Documentation
│   │   ├── guides/                       # Implementation guides
│   │   │   ├── ASYNC_CONVERSION_SUMMARY.md
│   │   │   └── IMPLEMENTATION_PLAN.md
│   │   ├── integration/                  # Integration docs
│   │   ├── reference/                    # Reference materials
│   │   │   └── TOOLS_REFERENCE.md
│   │   └── reports/                      # Project reports
│   │       └── LLOYD_IMPLEMENTATION_WORKORDER.md
│   │
│   ├── foundation-docs/                  # Foundation documentation
│   │   ├── ARCHITECTURE.md               # Architecture overview
│   │   ├── API.md                        # API reference
│   │   ├── COMPONENTS.md                 # Component catalog
│   │   ├── SCHEMA.md                     # Schema documentation
│   │   └── project-context.json          # Project context data
│   │
│   ├── standards/                        # Project standards
│   │   ├── BEHAVIOR-STANDARDS.md         # Behavior patterns
│   │   ├── COMPONENT-INDEX.md            # Component registry
│   │   ├── UI-STANDARDS.md               # UI/UX standards
│   │   └── UX-PATTERNS.md                # UX patterns
│   │
│   ├── testing/                          # Testing artifacts
│   │   ├── README.md                     # Testing overview
│   │   ├── test_framework.md             # Framework documentation
│   │   ├── TEST_PLAN.md                  # Test plan
│   │   ├── TESTING_PACKAGE.md            # Package structure
│   │   ├── INTEGRATION_TEST_NOTE.md      # Integration notes
│   │   └── results/                      # Test results
│   │       ├── 2025-12-26/               # Historical results
│   │       └── 2025-12-27/               # Latest results
│   │           ├── EXECUTION_SUMMARY.md
│   │           ├── FULL_TEST_RUN.log
│   │           ├── README.md
│   │           └── TEST_EXECUTION_REPORT.md
│   │
│   ├── working/                          # Active work-in-progress
│   │   ├── coderef-context-mcp-server/   # Server workorder
│   │   │   ├── analysis.json
│   │   │   ├── claude.md
│   │   │   ├── context.json
│   │   │   ├── DELIVERABLES.md
│   │   │   └── plan.json
│   │   └── test-coderef-context-injection/
│   │       └── analysis.json
│   │
│   ├── workorder/                        # Active workorders
│   │   └── test-coderef-context-injection/
│   │       ├── context.json
│   │       └── plan.json
│   │
│   └── workorder-log.txt                 # Global workorder audit trail
│
├── processors/                           # Data processors
│   ├── __init__.py
│   └── export_processor.py               # Export format processor (v1.2.0)
│
├── scripts/                              # Utility scripts
│   └── (scan and generation scripts)
│
├── src/                                  # Source code
│   └── (core implementation modules)
│
├── tests/                                # Test suite
│   ├── __init__.py
│   ├── conftest.py                       # pytest configuration
│   ├── RUN_INTEGRATION_TESTS.md          # Integration test guide
│   ├── test_coderef_usage_trace.py       # Usage tracing tests
│   ├── test_export_edge_cases.py         # Edge case tests
│   ├── test_export_processor.py          # Export processor tests
│   ├── test_tools.py                     # Tool tests
│   ├── test_tools_integration.py         # Integration tests
│   ├── test_workflow_integration.py      # Workflow tests
│   └── TEST_EXPORT_PROCESSOR_SUMMARY.md  # Test summary
│
├── utils/                                # Utility modules
│   └── __init__.py
│
├── .coverage                             # Coverage report data
├── .pytest_cache/                        # pytest cache
│
├── CLAUDE.md                             # AI agent context (v2.0.0)
├── README.md                             # User-facing documentation
├── pyproject.toml                        # Python project configuration
├── pytest.ini                            # pytest configuration
├── server.py                             # MCP server entry point
│
└── Documentation Files                   # Project documentation
    ├── CLI_INTEGRATION_TEST_RESULTS.md
    ├── CODEREF_USAGE_INSTANCES.md
    ├── coderef-document-audit-reply.md
    ├── communication.json
    ├── document-io-inventory.json
    ├── INTEGRATION_PROOF.md
    ├── INTEGRATION_TEST_SUMMARY.md
    ├── ISSUES_AND_BUGS_IDENTIFIED.md
    ├── ROOT-ORGANIZATION.md
    ├── run_integration_tests.py
    ├── TEST_SUITE_SUMMARY.md
    ├── TESTING_COMPLETE.md
    └── TESTING_SUMMARY.md
```

---

## Key Directories Explained

### `.coderef/` - Code Intelligence Hub
Generated by `populate-coderef.py` or `scan-all.py`. Contains 16 output types:
- **Core:** index.json, context.md, graph.json
- **Reports:** patterns, coverage, validation, drift, complexity
- **Diagrams:** Mermaid and GraphViz visualizations
- **Exports:** JSON, JSON-LD, wrapped markdown
- **Docs:** Auto-generated README, ARCHITECTURE, API

**Refresh when:** Code changes, before planning, after features complete

### `coderef/` - Ecosystem Artifacts
Follows CodeRef global structure:
- **foundation-docs/** - Project documentation templates
- **standards/** - UI/UX/behavior standards
- **testing/** - Test results and reports
- **workorder/** - Active feature plans
- **working/** - Legacy work-in-progress (deprecated in v1.1.0)

### `processors/` - Data Processing
**export_processor.py** (v1.2.0) - Converts .coderef/ data to multiple formats:
- JSON (raw graph)
- JSON-LD (semantic web)
- Mermaid (diagrams)
- DOT (GraphViz)

### `tests/` - Test Suite
**Coverage:** 98% (30/30 tests passing)
- Unit tests for all 12 MCP tools
- Integration tests with coderef-workflow
- Export processor edge cases
- End-to-end workflows

### `src/` - Core Implementation
MCP server implementation wrapping @coderef/core CLI:
- Tool handlers (scan, query, impact, complexity, etc.)
- Subprocess management for TypeScript CLI
- Error handling and validation

---

## File Counts

| Category | Count | Notes |
|----------|-------|-------|
| Python files | ~20 | server.py, processors, tests, utils |
| Documentation | ~30 | Markdown files (guides, reports, summaries) |
| Generated outputs | 16 | .coderef/ structure |
| Test files | 7 | 98% coverage |
| Config files | 3 | pyproject.toml, pytest.ini, .mcp.json |

---

## Important Files

| File | Purpose | Status |
|------|---------|--------|
| `server.py` | MCP server entry point | Production |
| `CLAUDE.md` | AI agent context (v2.0.0) | Current |
| `README.md` | User documentation | Current |
| `processors/export_processor.py` | Export processor | v1.2.0 |
| `.coderef/index.json` | Code element catalog | Generated |
| `coderef/workorder-log.txt` | Audit trail | Active |
| `pyproject.toml` | Python dependencies | Current |
| `pytest.ini` | Test configuration | Current |

---

## Output Utilization (v1.2.0)

**Achievement:** 90% utilization of .coderef/ outputs
- ✅ 12/15 output types actively used
- ✅ 5/5 MCP servers integrated
- ✅ 59,676 total elements discovered
- ✅ 4 workflow integrations complete

**Integration Points:**
- coderef-workflow: Reads index.json, patterns.json
- coderef-docs: Uses context.md, index.json
- coderef-personas: Reads context.md for handoffs
- coderef-testing: Uses coverage.json for test selection

---

## Maintenance Notes

### Regular Tasks
- Run `populate-coderef.py` after major code changes
- Check drift with `coderef drift` if > 7 days old
- Review test coverage with pytest after changes
- Update CLAUDE.md when adding features

### Health Checks
```bash
# Verify CLI path
export CODEREF_CLI_PATH="C:/Users/willh/Desktop/projects/coderef-system/packages/cli"

# Check drift
coderef drift . --json -i .coderef/index.json

# Run tests
pytest tests/ -v

# Validate outputs
ls -lh .coderef/
```

---

**Generated:** 2026-01-08
**Version:** 2.0.0
**Status:** ✅ Production Ready
