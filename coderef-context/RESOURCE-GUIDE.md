# coderef-context Resource Guide

**Project:** coderef-context MCP Server
**Version:** 2.0.0
**Status:** ✅ Production
**Last Updated:** 2026-01-08

---

## Purpose

This resource guide provides a comprehensive catalog of all documentation, tools, scripts, configuration files, and learning resources available in the coderef-context MCP server. Use this guide to quickly locate the right resource for your task.

---

## Overview

The coderef-context server provides:
- **12 MCP Tools** for code intelligence
- **16 Output Types** in `.coderef/` structure
- **Complete Test Suite** (98% coverage)
- **Export Processor** (4 formats)
- **Integration** with 4 other MCP servers

This guide organizes all resources by category with direct links and use case descriptions.

---

## Quick Navigation

| I need to... | Resource | Location |
|--------------|----------|----------|
| **Understand the system** | README.md | Root |
| **Configure for AI agents** | CLAUDE.md | Root |
| **Browse file structure** | FILE_TREE.md | Root |
| **Learn MCP API** | API.md | coderef/foundation-docs/ |
| **Understand architecture** | ARCHITECTURE.md | coderef/foundation-docs/ |
| **Run tests** | pytest.ini + tests/ | Root + tests/ |
| **Install & configure** | README.md (Installation) | Root |
| **Troubleshoot issues** | README.md (Troubleshooting) | Root |
| **Use CLI wrapper** | server.py | Root |
| **Process exports** | export_processor.py | processors/ |

---

## Core Documentation

### 1. README.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\README.md`
**Lines:** 611
**Version:** 1.1.0
**Purpose:** User-facing documentation for the coderef-context MCP server

**Contents:**
- Purpose and overview
- What the server does (11 MCP tools)
- Why it exists (eliminate blind coding)
- Use cases (safe refactoring, avoiding duplication, understanding dependencies)
- Integration points (workflow, personas, docs)
- Prerequisites & installation
- Quick start guide
- Troubleshooting (CLI path, timeouts, tool discovery)
- Configuration (environment variables, .mcp.json)
- Performance benchmarks
- Development guide

**When to use:**
- First-time setup
- Understanding tool capabilities
- Installation and configuration
- Troubleshooting common issues
- Performance expectations

---

### 2. CLAUDE.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\CLAUDE.md`
**Lines:** 392
**Version:** 2.0.0
**Purpose:** AI agent context documentation - persona definition and operational guidelines

**Contents:**
- Quick summary (dual role: MCP server + scan lead)
- Responsibilities (expose tools, execute scans, validate outputs)
- .coderef/ structure (16 output types)
- 12 MCP tools reference
- 6-phase setup workflow (code intelligence → docs → validation)
- Ecosystem dependencies (workflow, docs, personas, testing)
- Technical architecture (subprocess flow, AST accuracy)
- Communication style (proactive, precise, educational)
- Common issues & solutions
- Quick reference commands
- Tool examples
- Configuration

**When to use:**
- AI agents activating coderef-context-agent persona
- Understanding scan lead responsibilities
- Learning 6-phase workflow
- Understanding ecosystem integration
- Quick command reference

---

### 3. FILE_TREE.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\FILE_TREE.md`
**Lines:** 275
**Version:** 2.0.0
**Purpose:** Complete directory structure and file organization

**Contents:**
- Root structure visualization
- Key directories explained (`.coderef/`, `coderef/`, `processors/`, `tests/`)
- File counts by category
- Important files table
- Output utilization metrics (90% achieved)
- Integration points across servers
- Maintenance notes and health checks

**When to use:**
- Navigating the codebase
- Understanding project organization
- Finding specific files
- Learning .coderef/ structure
- Project maintenance

---

## Foundation Documentation (AI-Readable)

### 4. API.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\foundation-docs\API.md`
**Lines:** 625
**Version:** 1.1.0
**Purpose:** Complete MCP API reference with schemas and examples

**Contents:**
- 11 tool specifications:
  - coderef_scan (discovery)
  - coderef_query (relationships)
  - coderef_impact (change analysis)
  - coderef_complexity (metrics)
  - coderef_patterns (pattern discovery)
  - coderef_coverage (test coverage)
  - coderef_context (comprehensive context)
  - coderef_validate (reference validation)
  - coderef_drift (drift detection)
  - coderef_diagram (visualization)
  - coderef_tag (CodeRef2 tagging)
- Input schemas (JSON)
- Response schemas (JSON)
- Timeout specifications
- CLI command mappings
- Use case examples
- Integration points
- Error handling patterns
- Performance benchmarks

**When to use:**
- Understanding tool input/output
- Building integrations
- Debugging API calls
- Learning tool capabilities
- Performance planning

---

### 5. ARCHITECTURE.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\foundation-docs\ARCHITECTURE.md`
**Lines:** Comprehensive
**Purpose:** System architecture, design decisions, and technical patterns

**Contents:**
- High-level architecture
- Data flow (Agent → MCP → CLI → Codebase)
- Tool handler pattern
- Subprocess management
- Error handling strategy
- Performance considerations
- Design decisions (why 4 servers, workorder-centric, etc.)
- Integration architecture

**When to use:**
- Understanding system design
- Making architectural decisions
- Troubleshooting complex issues
- Contributing to codebase
- Learning design patterns

---

### 6. SCHEMA.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\foundation-docs\SCHEMA.md`
**Lines:** Comprehensive
**Purpose:** Data schema definitions for all inputs and outputs

**Contents:**
- Tool input schemas
- Response schemas
- Error response formats
- .coderef/ file schemas
- Export format schemas

**When to use:**
- Validating data structures
- Building type definitions
- Understanding data models
- Debugging serialization issues

---

### 7. COMPONENTS.md
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\foundation-docs\COMPONENTS.md`
**Lines:** Comprehensive
**Purpose:** Component architecture and implementation patterns

**Contents:**
- Core components (server, handlers, processors)
- Component relationships
- Implementation patterns
- Extension points

**When to use:**
- Understanding code organization
- Adding new tools
- Extending functionality
- Code review

---

## Generated Documentation (.coderef/)

### 8. .coderef/ Output Structure
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\.coderef\`
**Purpose:** Generated code intelligence outputs (16 types)

**Core Files:**
- `index.json` - All code elements catalog (247 elements)
- `context.json` - Structured project context
- `context.md` - Human-readable overview
- `graph.json` - Dependency graph

**Reports:**
- `reports/patterns.json` - Code patterns discovered
- `reports/coverage.json` - Test coverage analysis
- `reports/validation.json` - Reference validation
- `reports/drift.json` - Drift detection results
- `reports/complexity/README.md` - Complexity metrics

**Diagrams:**
- `diagrams/dependencies.mmd` - Dependency graph (Mermaid)
- `diagrams/dependencies.dot` - Dependency graph (GraphViz)
- `diagrams/calls.mmd` - Call graph
- `diagrams/imports.mmd` - Import graph

**Exports:**
- `exports/graph.json` - Graph export (JSON)
- `exports/graph.jsonld` - Graph export (JSON-LD)
- `exports/diagram-wrapped.md` - Diagram with usage notes

**Generated Docs:**
- `generated-docs/README.md` - Project overview
- `generated-docs/ARCHITECTURE.md` - Architecture
- `generated-docs/API.md` - API documentation

**When to use:**
- Project context during planning
- Understanding code structure
- Embedding diagrams in docs
- Impact analysis preparation
- Pattern discovery

**Refresh when:**
- Major code changes
- Before planning workflows
- After feature completion
- Drift > 10%

---

## Testing Resources

### 9. Test Suite
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\tests\`
**Coverage:** 98% (30/30 tests passing)

**Test Files:**
- `test_tools.py` - Unit tests for all 12 tools
- `test_tools_integration.py` - Integration tests
- `test_workflow_integration.py` - Workflow integration
- `test_export_processor.py` - Export processor tests (24 tests)
- `test_export_edge_cases.py` - Edge case tests
- `test_coderef_usage_trace.py` - Usage tracing tests
- `conftest.py` - pytest configuration & fixtures

**Test Documentation:**
- `tests/RUN_INTEGRATION_TESTS.md` - Integration test guide
- `tests/TEST_EXPORT_PROCESSOR_SUMMARY.md` - Export test summary

**When to use:**
- Verifying functionality
- Regression testing
- Learning tool behavior
- Contributing code
- Debugging issues

**Run tests:**
```bash
pytest tests/ -v                    # All tests
pytest tests/test_tools.py -v      # Tool tests only
pytest tests/test_export_processor.py -v  # Export tests
```

---

### 10. Test Configuration
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\pytest.ini`
**Purpose:** pytest configuration

**Contents:**
- Test discovery patterns
- Coverage settings
- Marker definitions
- Output formatting

---

### 11. Test Reports
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\testing\results\`

**Available Reports:**
- `2025-12-27/TEST_EXECUTION_REPORT.md` - Detailed test execution
- `2025-12-27/EXECUTION_SUMMARY.md` - Summary of results
- `2025-12-27/FULL_TEST_RUN.log` - Complete test logs
- `TEST_SUITE_SUMMARY.md` - Overall test suite status
- `TESTING_COMPLETE.md` - Completion report
- `INTEGRATION_TEST_SUMMARY.md` - Integration test summary
- `CLI_INTEGRATION_TEST_RESULTS.md` - CLI integration results

**When to use:**
- Reviewing test history
- Debugging test failures
- Tracking coverage trends
- Validation reporting

---

## Source Code Resources

### 12. MCP Server Implementation
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\server.py`
**Lines:** ~1073
**Purpose:** Main MCP server entry point

**Contents:**
- Tool schema definitions
- Handler implementations (12 tools)
- CLI subprocess management
- Error handling
- JSON parsing logic
- Timeout management

**When to use:**
- Understanding implementation
- Debugging tool behavior
- Adding new tools
- Performance optimization
- Error investigation

---

### 13. Export Processor
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\processors\export_processor.py`
**Version:** 1.2.0
**Purpose:** Convert .coderef/ data to multiple formats

**Capabilities:**
- JSON export (raw graph)
- JSON-LD export (semantic web)
- Mermaid export (diagrams)
- DOT export (GraphViz)

**When to use:**
- Exporting dependency graphs
- Creating documentation diagrams
- Semantic web integration
- Custom visualization

**Usage:**
```python
from processors.export_processor import ExportProcessor

processor = ExportProcessor(project_path="/path/to/project")
result = processor.export("mermaid")  # or "json", "jsonld", "dot"
```

---

### 14. Utility Modules
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\utils\`
**Purpose:** Shared utility functions

**When to use:**
- Common operations
- Helper functions
- Shared logic

---

## Configuration Resources

### 15. Python Package Configuration
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\pyproject.toml`
**Purpose:** Python project metadata and dependencies

**Contents:**
- Package metadata
- Dependencies (mcp, asyncio)
- Build system configuration
- Project URLs

**When to use:**
- Installing package
- Managing dependencies
- Publishing (future)

---

### 16. MCP Configuration (.mcp.json)
**Path:** `~/.mcp.json` (global) or project-specific
**Purpose:** MCP server registration

**Example:**
```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-context/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-context",
      "env": {
        "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
      },
      "description": "Code intelligence MCP server",
      "tools": ["coderef_scan", "coderef_query", "coderef_impact", ...]
    }
  }
}
```

**When to use:**
- Initial setup
- Updating CLI path
- Debugging tool discovery
- Multi-environment configuration

---

### 17. Environment Variables
**Variable:** `CODEREF_CLI_PATH`
**Purpose:** Override default @coderef/core CLI path
**Default:** `C:\Users\willh\Desktop\projects\coderef-system\packages\cli`

**Setup:**
```bash
# Windows
set CODEREF_CLI_PATH=C:/path/to/coderef-system/packages/cli

# Unix/Mac
export CODEREF_CLI_PATH=/path/to/coderef-system/packages/cli

# Verify
echo $CODEREF_CLI_PATH
```

---

## Scripts & Automation

### 18. Scan Scripts
**Purpose:** Generate .coderef/ structure

**populate-coderef.py** (Complete scan, 16 outputs, 30-60s):
```bash
python scripts/populate-coderef.py /path/to/project
```

**scan-all.py** (Quick scan, 2-3 files, 5-10s):
```bash
./scripts/scan-all.py /path/to/project
```

**When to use:**
- Initial project setup
- After major code changes
- Before planning workflows
- After feature completion

---

### 19. Integration Test Runner
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\run_integration_tests.py`
**Purpose:** Run end-to-end integration tests

```bash
python run_integration_tests.py
```

**When to use:**
- Full system validation
- Pre-release testing
- Debugging integration issues

---

## Workorder & Planning Resources

### 20. Workorder Log
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\workorder-log.txt`
**Purpose:** Global audit trail of all workorders

**Format:**
```
WO-ID | Project | Description | Timestamp
```

**When to use:**
- Tracking feature history
- Audit trail
- Progress monitoring

---

### 21. Active Workorders
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\workorder\`
**Purpose:** Active feature implementations

**Structure per feature:**
- `context.json` - Feature requirements
- `plan.json` - Implementation plan (10 sections)
- `DELIVERABLES.md` - Progress tracking

**When to use:**
- Current feature status
- Task coordination
- Progress reporting

---

### 22. Archived Workorders
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\archived\`
**Purpose:** Completed features (historical reference)

**When to use:**
- Learning from past implementations
- Recovery if needed
- Pattern discovery

---

## Standards & Conventions

### 23. Behavior Standards
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\standards\BEHAVIOR-STANDARDS.md`
**Purpose:** Behavioral patterns and error handling standards

**When to use:**
- Implementing consistent error handling
- Following established patterns
- Code review

---

### 24. Component Index
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\standards\COMPONENT-INDEX.md`
**Purpose:** Registry of all components

**When to use:**
- Finding existing components
- Avoiding duplication
- Component discovery

---

### 25. UI Standards
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\standards\UI-STANDARDS.md`
**Purpose:** UI/UX consistency guidelines

**When to use:**
- Building user interfaces
- Maintaining consistency
- Design decisions

---

### 26. UX Patterns
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\standards\UX-PATTERNS.md`
**Purpose:** Common UX interaction patterns

**When to use:**
- Implementing interactions
- User experience design
- Pattern reuse

---

## Learning Resources

### 27. Implementation Guides
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\docs\guides\`

**Available Guides:**
- `IMPLEMENTATION_PLAN.md` - Feature implementation guide
- `ASYNC_CONVERSION_SUMMARY.md` - Async programming patterns

**When to use:**
- Implementing new features
- Understanding async patterns
- Development workflow

---

### 28. Tools Reference
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef\docs\reference\TOOLS_REFERENCE.md`
**Purpose:** Complete tool usage reference

**When to use:**
- Tool parameter reference
- Usage examples
- Quick lookup

---

### 29. Integration Proof
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\INTEGRATION_PROOF.md`
**Purpose:** Evidence of successful ecosystem integration

**Contents:**
- Integration test results
- Cross-server communication examples
- Validation reports

**When to use:**
- Verifying integrations
- Debugging cross-server issues
- Documentation

---

### 30. Usage Instances
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\CODEREF_USAGE_INSTANCES.md`
**Purpose:** Real-world usage examples

**When to use:**
- Learning by example
- Understanding patterns
- Best practices

---

## Issue Tracking & Debugging

### 31. Known Issues
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\ISSUES_AND_BUGS_IDENTIFIED.md`
**Purpose:** Catalog of known issues and workarounds

**When to use:**
- Troubleshooting
- Before reporting bugs
- Understanding limitations

---

### 32. Document Audit
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\coderef-document-audit-reply.md`
**Purpose:** Documentation quality audit results

**When to use:**
- Improving documentation
- Identifying gaps
- Quality assurance

---

### 33. Document I/O Inventory
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\document-io-inventory.json`
**Purpose:** Catalog of all document inputs/outputs

**When to use:**
- Understanding data flow
- Documentation generation
- System analysis

---

## Communication & Coordination

### 34. Communication Schema
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\communication.json`
**Purpose:** Multi-agent communication protocol

**Contents:**
- Agent roles
- Communication channels
- Status updates
- Task coordination

**When to use:**
- Multi-agent workflows
- Coordination between agents
- Status tracking

---

## External Dependencies

### 35. @coderef/core CLI
**Repository:** https://github.com/coderef-system
**Language:** TypeScript
**Purpose:** AST-based code analysis engine

**Installation:**
```bash
# Global
npm install -g @coderef/core

# Local
cd /path/to/coderef-system/packages/cli
npm install
npm run build
```

**Verify:**
```bash
coderef --version
# or
node /path/to/cli/dist/cli.js --version
```

**When to use:**
- Initial setup
- CLI debugging
- Performance tuning
- Understanding analysis engine

---

## Quick Reference Tables

### Resource by Task

| Task | Primary Resource | Secondary Resources |
|------|------------------|---------------------|
| **First-time setup** | README.md | .mcp.json, CLAUDE.md |
| **Understanding tools** | API.md | TOOLS_REFERENCE.md |
| **Planning features** | .coderef/index.json | patterns.json, context.md |
| **Implementing features** | CLAUDE.md | COMPONENTS.md, ARCHITECTURE.md |
| **Testing** | pytest.ini + tests/ | TEST_SUITE_SUMMARY.md |
| **Debugging** | ISSUES_AND_BUGS_IDENTIFIED.md | API.md, server.py |
| **Integration** | ARCHITECTURE.md | API.md, INTEGRATION_PROOF.md |
| **Exporting data** | export_processor.py | .coderef/exports/ |
| **Documentation** | FILE_TREE.md | README.md, CLAUDE.md |
| **Maintenance** | .coderef/reports/drift.json | populate-coderef.py |

---

### Resource by Role

| Role | Essential Resources | Optional Resources |
|------|---------------------|-------------------|
| **AI Agent** | CLAUDE.md, API.md | TOOLS_REFERENCE.md |
| **Developer** | README.md, ARCHITECTURE.md | COMPONENTS.md, SCHEMA.md |
| **Tester** | pytest.ini, tests/ | TEST_SUITE_SUMMARY.md |
| **User** | README.md | CLAUDE.md |
| **Coordinator** | communication.json, workorder-log.txt | DELIVERABLES.md |
| **Documenter** | FILE_TREE.md, API.md | generated-docs/ |

---

### Resource by Type

| Type | Count | Location | Purpose |
|------|-------|----------|---------|
| **Core Docs** | 3 | Root | README, CLAUDE, FILE_TREE |
| **Foundation Docs** | 4 | coderef/foundation-docs/ | API, ARCHITECTURE, SCHEMA, COMPONENTS |
| **Generated Docs** | 16 | .coderef/ | Intelligence outputs |
| **Test Files** | 7 | tests/ | Unit + integration tests |
| **Test Reports** | 8 | coderef/testing/results/ | Test execution history |
| **Standards** | 4 | coderef/standards/ | Behavior, component, UI, UX |
| **Guides** | 2 | coderef/docs/guides/ | Implementation guides |
| **Scripts** | 2 | scripts/ | Scan automation |
| **Config Files** | 3 | Root | pyproject.toml, pytest.ini, .mcp.json |
| **Source Code** | 2 | Root + processors/ | server.py, export_processor.py |

---

## Maintenance Schedule

### Daily
- Review workorder-log.txt for new activity
- Check test suite status (.coverage)

### Weekly
- Run drift detection (coderef drift)
- Review ISSUES_AND_BUGS_IDENTIFIED.md
- Update documentation if needed

### After Code Changes
- Run populate-coderef.py
- Run test suite (pytest tests/ -v)
- Update DELIVERABLES.md

### After Feature Completion
- Archive workorder
- Update CHANGELOG.json (if using coderef-docs)
- Regenerate .coderef/ if major changes

---

## Getting Help

### Troubleshooting Order
1. Check **README.md** (Troubleshooting section)
2. Review **ISSUES_AND_BUGS_IDENTIFIED.md**
3. Verify CLI path: `echo $CODEREF_CLI_PATH`
4. Test CLI directly: `coderef --version`
5. Check MCP cache: Delete and restart Claude Code
6. Review server logs: `python server.py` (watch for errors)
7. Run test suite: `pytest tests/ -v`

### Common Issues Quick Links
- **CLI not found:** README.md:350-369
- **Scan timeout:** README.md:373-386
- **Tool not found:** README.md:389-407
- **JSON parse error:** README.md:410-425

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-08 | Complete resource guide created |
| 1.2.0 | 2025-12-31 | Export processor + 90% .coderef/ utilization |
| 1.1.0 | 2025-12-30 | Tag tool added |
| 1.0.0 | 2025-12-25 | Initial production release |

---

## Related Resources

### Other MCP Servers
- **coderef-workflow:** Planning and orchestration (`C:\Users\willh\.mcp-servers\coderef-workflow\`)
- **coderef-docs:** Documentation generation (`C:\Users\willh\.mcp-servers\coderef-docs\`)
- **coderef-personas:** Expert agents (`C:\Users\willh\.mcp-servers\coderef-personas\`)
- **coderef-testing:** Test automation (`C:\Users\willh\.mcp-servers\coderef-testing\`)

### Ecosystem Documentation
- **Ecosystem CLAUDE.md:** `C:\Users\willh\.mcp-servers\CLAUDE.md`
- **Ecosystem README.md:** `C:\Users\willh\.mcp-servers\README.md`

---

## Summary

This resource guide catalogs **35+ resources** across:
- ✅ 10 core documentation files
- ✅ 16 .coderef/ intelligence outputs
- ✅ 7 test files + 8 test reports
- ✅ 4 foundation docs (API, ARCHITECTURE, SCHEMA, COMPONENTS)
- ✅ 4 standards documents
- ✅ 2 implementation guides
- ✅ 2 scan scripts
- ✅ 3 configuration files
- ✅ Communication & coordination files

**Status:** ✅ 100% resource coverage, production-ready

---

**Generated:** 2026-01-08
**Maintained by:** willh, Claude Code AI
**For:** Developers, AI agents, testers, coordinators, users

---

**Quick Start for New Users:**
1. Read **README.md** for overview
2. Review **CLAUDE.md** for AI agent context
3. Check **FILE_TREE.md** for navigation
4. Explore **API.md** for tool reference
5. Run tests with **pytest tests/ -v**

**Quick Start for AI Agents:**
1. Load **CLAUDE.md** for persona activation
2. Reference **API.md** for tool schemas
3. Use **.coderef/index.json** for project context
4. Call tools following **TOOLS_REFERENCE.md**
5. Report issues via **communication.json**
