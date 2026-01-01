# coeref-testing - AI Context Documentation

**Project:** coeref-testing (MCP Testing Infrastructure Server)
**Version:** 1.0.0
**Status:** ✅ Production Ready
**Created:** 2025-12-26
**Last Updated:** 2025-12-27

---

## Quick Summary

**coeref-testing** is a universal MCP server for test orchestration, execution, and reporting that works with any project and any test framework (pytest, jest, cargo, mocha, vitest, etc.).

**Core Innovation:** Framework-agnostic architecture that auto-detects test frameworks and executes tests with unified result aggregation, enabling cross-project testing from a single MCP server.

**Latest Update (v1.0.0 - Complete):**
- ✅ All 37 implementation tasks completed across 4 phases
- ✅ 14 MCP tools fully implemented (discovery, execution, management, analysis)
- ✅ 14 slash commands with comprehensive documentation
- ✅ testing-expert persona with 15 expertise areas and 1500+ line system prompt
- ✅ Framework auto-detection and unified result aggregation
- ✅ Async/parallel test execution with configurable workers
- ✅ Complete README.md and USER-GUIDE.md documentation
- ✅ Registered in global .mcp.json configuration

**Key Relationships:**
- **Independent:** No dependencies on coderef-context, coderef-workflow, coderef-docs, coderef-personas
- **Integrable:** Optional hooks to other MCP servers when available
- **Reusable:** Works with CodeRef ecosystem (4 servers), next-scraper, any user project

**Core Constraint:**
- ⚠️ **TEST AND REPORT ONLY** - Do not fix code, refactor tests, or implement missing functionality. Only discover, execute, analyze, and report findings.

Together they form a complete testing ecosystem: Discovery → Execution → Aggregation → Analysis → Reporting.

---

## Problem & Vision

### The Problem
Test infrastructure is scattered. Projects use different frameworks (pytest, jest, cargo). Tests are hard to discover, orchestrate, and report on. No unified view across multiple test frameworks or projects.

### The Solution
Create a universal MCP testing server that: (1) Auto-detects test frameworks, (2) Executes tests uniformly, (3) Aggregates results across frameworks, (4) Analyzes coverage/performance/flakiness, (5) Generates reports in multiple formats.

### How It Works
1. **Discover** - Scan project, detect frameworks (pytest/jest/cargo/mocha/vitest)
2. **Execute** - Run tests using detected framework, async/parallel execution
3. **Aggregate** - Collect results into unified JSON schema
4. **Analyze** - Calculate coverage, detect flaky tests, analyze performance
5. **Report** - Generate markdown/HTML/JSON reports with trends

---

## Architecture

### Core Concepts

**Framework Detection**
Auto-detect test frameworks by scanning project structure:
- Detect pytest (pyproject.toml, tests/ directory, conftest.py)
- Detect jest/vitest (package.json, jest.config.js, vitest.config.ts)
- Detect cargo (Cargo.toml with [dev-dependencies])
- Detect custom runners (shell scripts, make targets)

**Unified Result Schema**
All frameworks output to standard JSON:
```json
{
  "project": "/path", "framework": "pytest",
  "summary": {"total": 247, "passed": 245, "failed": 2},
  "tests": [{"name": "test_X", "status": "passed", "duration": 0.5}]
}
```

**Async/Parallel Execution**
Run tests concurrently with configurable workers, proper isolation, timeout handling.

### Data Flow

```
User Project (any framework)
    ↓
coeref-testing discovers tests
    ↓
Detects framework (pytest/jest/cargo)
    ↓
Executes tests in parallel
    ↓
Collects results → unified JSON
    ↓
Analyzes (coverage/performance/flaky)
    ↓
Generates reports (markdown/HTML/JSON)
    ↓
Archives results with timestamp
```

### Key Integration Points

- **Depends on:** Python async runtime, subprocess execution, git (for result storage)
- **Used by:** Agents (via testing-expert persona), CI/CD pipelines, development workflows
- **Orchestrated via:** MCP tools + slash commands, or direct API calls

---

## Tools Catalog

| Tool | Purpose | Type |
|------|---------|------|
| `discover_tests` | Find tests in project, auto-detect framework | Discovery |
| `list_test_frameworks` | Show detected frameworks + versions | Discovery |
| `run_all_tests` | Execute full test suite | Execution |
| `run_test_file` | Run single test file | Execution |
| `run_test_category` | Run tests matching pattern/tag | Execution |
| `run_tests_in_parallel` | Execute tests with concurrency control | Execution |
| `get_test_results` | Query results (date, status, duration) | Management |
| `aggregate_results` | Summary across all tests | Management |
| `generate_test_report` | Format report (markdown/HTML/JSON) | Management |
| `compare_test_runs` | Diff between two test runs | Management |
| `analyze_coverage` | Code coverage metrics + gaps | Analysis |
| `detect_flaky_tests` | Find intermittently failing tests | Analysis |
| `analyze_test_performance` | Speed analysis, slow tests | Analysis |
| `validate_test_health` | Overall test suite health check | Analysis |

**Total:** 14 tools across 4 categories (Discovery, Execution, Management, Analysis)

---

## Testing Persona: testing-expert

### Specification

**Name:** testing-expert
**Version:** 1.0.0
**Role:** Test Strategy & QA Specialist
**Parent:** null (independent)

**Expertise (15 areas):**
- Test strategy & planning
- Test automation patterns
- Coverage analysis & optimization
- Performance testing & profiling
- Multi-framework testing (pytest, jest, cargo, mocha, vitest)
- CI/CD integration
- Debugging test failures
- Test data management
- Flaky test detection & fixing
- Test reporting & metrics
- Load testing & benchmarking
- Integration & end-to-end testing
- Test optimization techniques
- Regression detection & analysis
- Framework-agnostic testing

**Use Cases (7):**
1. Plan test strategy for new project
2. Debug failing tests across frameworks
3. Analyze coverage gaps
4. Optimize test speed
5. Setup CI/CD testing
6. Detect & fix flaky tests
7. Generate test reports

**System Prompt:** 1500+ lines covering all test patterns for pytest, jest, cargo, mocha, vitest, and custom runners.

### Activation

```bash
use_persona('testing-expert')
```

---

## File Structure

```
coeref-testing/
├── CLAUDE.md                           # This file (AI context)
├── TESTING_GUIDE.md                    # Project vision & implementation roadmap
├── README.md                           # User-facing documentation
├── server.py                           # MCP server entry point
├── pyproject.toml                      # Python package config
├── .claude/commands/                   # Slash commands (12+)
│   ├── /run-tests
│   ├── /test-results
│   ├── /test-report
│   └── ... (9+ more)
├── src/
│   ├── models.py                       # Test result schemas
│   ├── framework_detector.py           # Auto-detect frameworks
│   ├── test_runner.py                  # Test execution
│   ├── test_aggregator.py              # Result aggregation
│   ├── result_analyzer.py              # Coverage/performance/flaky analysis
│   └── test_coordinator.py             # Multi-project orchestration
├── personas/
│   └── testing-expert.json             # testing-expert persona definition
└── coderef/
    ├── testing/
    │   ├── infrastructure/
    │   └── results/2025-12-26/
    └── workorder/
```

---

## Design Decisions

**1. Framework-Agnostic Architecture**
- ✅ Chosen: Support all frameworks (pytest/jest/cargo/mocha/vitest)
- ❌ Rejected: Single-framework focus
- Reason: Maximizes reusability across projects, works with CodeRef + next-scraper + any project

**2. Independent vs Dependent**
- ✅ Chosen: No dependencies on other MCP servers
- ❌ Rejected: Require coderef-context/coderef-workflow
- Reason: Can run standalone, works in any environment, optional integrations when available

**3. Unified Result Schema**
- ✅ Chosen: All frameworks output to standard JSON
- ❌ Rejected: Framework-native result formats
- Reason: Consistent aggregation, easier analysis, framework-agnostic reporting

**4. Async/Parallel Execution**
- ✅ Chosen: Async execution with configurable parallelization
- ❌ Rejected: Sequential test execution
- Reason: Fast feedback, efficient resource use, scales to large test suites

**5. Single Testing Persona**
- ✅ Chosen: testing-expert covers all domains
- ❌ Rejected: Per-framework personas
- Reason: Unified perspective, simpler for users, comprehensive coverage

---

## Integration Guide

### Standalone Usage
coeref-testing works independently. No other MCP servers required.

### With coderef-context (Optional)
Use coderef-context tools to analyze test code dependencies before/after running tests.

### With coderef-workflow (Optional)
Track test suites as workorders in coderef-workflow, use planning tools for test strategy.

### With coderef-docs (Optional)
Generate test reports and documentation using coderef-docs tools.

---

## Essential Commands

### Development

```bash
# Install & run
cd C:\Users\willh\.mcp-servers\coeref-testing
uv sync
python server.py

# Run tests
pytest tests/ -v
mypy src/
```

### Testing / Slash Commands

```bash
/run-tests                    # Run full test suite on project
/run-server-tests             # Run specific test category
/test-results                 # View latest test results
/test-report                  # Generate test report (markdown/HTML/JSON)
/test-coverage                # Show code coverage
/test-trends                  # Show trends & regressions
/test-performance             # Analyze test speed
/detect-flaky                 # Find flaky tests
/test-health                  # Overall health check
/compare-runs                 # Compare two test runs
/discover-tests               # List tests in project
/list-frameworks              # Show detected frameworks
```

---

## Use Cases

### UC-1: Test CodeRef Ecosystem

```
Goal: Run all tests across 4 CodeRef servers
Steps:
1. Use /discover-tests on coderef-context → finds 10 tools to test
2. Use /run-tests on coderef-context → executes all tests
3. Repeat for coderef-workflow, coderef-docs, coderef-personas
4. Use /aggregate-results → summary across all 4 servers
5. Use /test-report → generates ecosystem health report
```

### UC-2: Optimize next-scraper Tests

```
Goal: Make tests faster, fix flaky tests
Steps:
1. Use /test-performance on next-scraper project → identifies slow tests
2. Use /detect-flaky → finds intermittently failing tests
3. Use testing-expert persona → analyze & recommend fixes
4. Run tests again → verify improvements
5. Use /compare-runs → show speed/reliability gains
```

---

## Recent Changes

### v1.0.0 - Complete Implementation (2025-12-27)

**Phase 1: Setup & Architecture (4/4) ✅**
- ✅ Project directory structure (src/, tests/, personas/, .claude/commands/)
- ✅ pyproject.toml with dependencies and metadata
- ✅ server.py MCP server skeleton with tool registration
- ✅ models.py with Pydantic schemas for unified result format

**Phase 2: Framework Detection & Execution (13/13) ✅**
- ✅ framework_detector.py with pytest/jest/vitest/cargo/mocha detection
- ✅ test_runner.py with async/parallel execution (350+ lines)
- ✅ Comprehensive unit tests (27+ tests)
- ✅ Integration tests for pytest and jest

**Phase 3: Result Processing & Analysis (6/6) ✅**
- ✅ test_aggregator.py for result normalization and archival
- ✅ result_analyzer.py for coverage, performance, flaky, health analysis
- ✅ test_coordinator.py for multi-project orchestration

**Phase 4: Tools, Commands, Docs, Release (14/14) ✅**
- ✅ 14 MCP tools implemented (2 discovery, 4 execution, 4 management, 4 analysis)
- ✅ 14 slash commands with full documentation
- ✅ testing-expert.json persona with 15 expertise areas
- ✅ Updated README.md (260+ lines)
- ✅ Created USER-GUIDE.md (500+ lines with examples)
- ✅ Registered in global .mcp.json
- ✅ Final commit to main branch

---

## Resources

- **[README.md](README.md)** - User guide and feature overview
- **[USER-GUIDE.md](USER-GUIDE.md)** - Comprehensive tool documentation with examples
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Architecture and design decisions
- **[.claude/commands/](​.claude/commands/)** - 14 slash command definitions
- **[personas/testing-expert.json](personas/testing-expert.json)** - testing-expert persona
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Protocol reference

---

**Maintained by:** willh, Claude Code AI

**System Status:** ✅ Production Ready - All 37 tasks complete, full implementation delivered, ready for deployment

