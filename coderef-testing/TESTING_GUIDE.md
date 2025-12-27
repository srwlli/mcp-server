# coeref-testing: Universal MCP Testing Server

**Project:** coeref-testing (MCP Testing Infrastructure Server)
**Vision:** General-purpose MCP server for test orchestration, execution, and reporting
**Applies To:** Any project (CodeRef ecosystem, next-scraper, custom projects, etc.)
**Date Created:** 2025-12-26
**Status:** Planning Phase

---

## 🎯 Project Vision

Create a **general-purpose MCP server for test orchestration, execution, and reporting** that works with any project (not specific to CodeRef). Once built, deploy it to:

1. **CodeRef ecosystem** (4 servers: context, workflow, docs, personas)
2. **Other projects** (next-scraper, coderef-dashboard, etc.)
3. **Any user project** that needs comprehensive testing

### Key Capability: Framework-Agnostic

Works with ANY test framework:
- **Python:** pytest, unittest, nose
- **JavaScript:** Jest, Mocha, Vitest, Playwright
- **TypeScript:** Jest, Mocha, Vitest
- **Go:** testing, testify
- **Rust:** cargo test
- **Generic:** Custom test runners, shell scripts

### Critical Constraint: Project Independence

- **Does NOT depend on:** coderef-context, coderef-workflow, coderef-docs, coderef-personas
- **Is independent:** Can run standalone
- **Is integrable:** Optional hooks to other MCP servers (when available)

---

## 📐 Architecture Overview

### Phase 1: Core Testing Server (Universal, Project-Agnostic)

#### 1.1 Server Purpose
- **Discover** tests in any project (pytest, jest, unittest, etc.)
- **Execute** tests with proper isolation & parallelization
- **Aggregate** results across multiple test frameworks
- **Report** on coverage, performance, trends
- **Integrate** with CI/CD pipelines

#### 1.2 Project-Agnostic Detection

```python
def discover_tests(project_path):
    """Auto-detect tests in ANY project"""

    # Detect frameworks present
    if has_pytest_markers(project_path):
        return discover_pytest(project_path)
    elif has_package_json(project_path):
        return discover_jest_or_mocha(project_path)
    elif has_cargo_toml(project_path):
        return discover_cargo_tests(project_path)
    # ... etc for all frameworks

    return None  # No tests found
```

#### 1.3 Flexible Execution

```python
def run_all_tests(project_path, parallel=True):
    """Run tests using detected framework"""

    framework = detect_framework(project_path)

    if framework == 'pytest':
        return subprocess.run(['pytest', '--json', ...])
    elif framework == 'jest':
        return subprocess.run(['npm', 'test', '--json', ...])
    elif framework == 'cargo':
        return subprocess.run(['cargo', 'test', '--format', 'json', ...])
    # ... etc
```

#### 1.4 Unified Result Format

```json
{
  "project": "/path/to/project",
  "framework": "pytest",
  "timestamp": "2025-12-26T19:45:00Z",
  "summary": {
    "total": 247,
    "passed": 245,
    "failed": 2,
    "skipped": 0,
    "duration_seconds": 42.5
  },
  "tests": [
    {
      "name": "test_feature_X",
      "status": "passed",
      "duration": 0.5,
      "file": "tests/test_feature.py",
      "tags": ["unit", "fast"]
    }
  ]
}
```

---

## 🔧 MCP Tools (14 Total - Universal)

### Test Discovery (2 tools)

**1. `discover_tests`**
- **Purpose:** Find tests in project (auto-detect framework)
- **Input:** project_path, include_patterns (optional)
- **Output:** Test inventory with locations, types, framework
- **Framework Support:** Auto-detects pytest, jest, cargo, mocha, vitest, etc.

**2. `list_test_frameworks`**
- **Purpose:** Show detected frameworks + versions
- **Input:** project_path
- **Output:** Detected frameworks, versions, test counts

### Test Execution (4 tools)

**3. `run_all_tests`**
- **Purpose:** Execute full test suite
- **Input:** project_path, parallel (bool), timeout (seconds)
- **Output:** Execution log, results summary, pass/fail count
- **Parallel Support:** Configurable concurrency level

**4. `run_test_file`**
- **Purpose:** Run single test file
- **Input:** project_path, file_path, framework (optional)
- **Output:** Test results for that file only

**5. `run_test_category`**
- **Purpose:** Run tests matching pattern/tag
- **Input:** project_path, pattern (regex), tags (optional)
- **Output:** Results for matching tests

**6. `run_tests_in_parallel`**
- **Purpose:** Execute tests with concurrency control
- **Input:** project_path, workers (number), timeout
- **Output:** Parallel execution results, speed metrics

### Result Management (4 tools)

**7. `get_test_results`**
- **Purpose:** Query test results (date, status, duration)
- **Input:** project_path, filters (date, status, duration_gt)
- **Output:** Filtered test results

**8. `aggregate_results`**
- **Purpose:** Summary across all tests
- **Input:** project_path, group_by (framework/file/tag)
- **Output:** Summary statistics, trends

**9. `generate_test_report`**
- **Purpose:** Format report (markdown/HTML/JSON)
- **Input:** project_path, format (markdown/html/json), include_details (bool)
- **Output:** Formatted report

**10. `compare_test_runs`**
- **Purpose:** Diff between two test runs
- **Input:** run_1_path, run_2_path
- **Output:** Differences (new failures, fixed tests, speed changes)

### Analysis (4 tools)

**11. `analyze_coverage`**
- **Purpose:** Code coverage metrics
- **Input:** project_path, min_threshold (percent)
- **Output:** Coverage metrics, gaps, file breakdown

**12. `detect_flaky_tests`**
- **Purpose:** Find intermittently failing tests
- **Input:** project_path, historical_runs (number), variance_threshold
- **Output:** Flaky tests, failure rate, recommendations

**13. `analyze_test_performance`**
- **Purpose:** Speed analysis, slow tests
- **Input:** project_path, threshold_seconds (optional)
- **Output:** Slow tests, duration trends, optimization suggestions

**14. `validate_test_health`**
- **Purpose:** Overall test suite health check
- **Input:** project_path
- **Output:** Health score (0-100), critical issues, recommendations

---

## 👤 Testing Persona: testing-expert

### Persona Specification

```json
{
  "name": "testing-expert",
  "version": "1.0.0",
  "parent": null,
  "role": "Test Strategy & QA Specialist",

  "expertise": [
    "Test strategy & planning",
    "Test automation patterns",
    "Coverage analysis",
    "Performance testing",
    "Multi-framework testing (pytest, jest, cargo, etc)",
    "CI/CD integration",
    "Debugging test failures",
    "Test data management",
    "Flaky test detection",
    "Test reporting & metrics",
    "Load testing",
    "Integration testing",
    "End-to-end testing",
    "Test optimization",
    "Regression detection"
  ],

  "use_cases": [
    "Plan test strategy for new project",
    "Debug failing tests",
    "Analyze coverage gaps",
    "Optimize test speed",
    "Setup CI/CD testing",
    "Detect & fix flaky tests",
    "Generate test reports"
  ]
}
```

### Persona System Prompt (1500+ lines)
Covers all test patterns for:
- Pytest projects
- Jest/Vitest projects
- Cargo test projects
- Custom test runners
- Multi-framework ecosystems

### Activation
```bash
use_persona('testing-expert')
```

---

## 📁 File Structure

```
coeref-testing/
├── TESTING_GUIDE.md                    ← This file
├── CLAUDE.md                           ← AI context (to be created)
├── README.md                           ← User guide (to be created)
├── server.py                           ← MCP server entry point
├── pyproject.toml                      ← Package config
├── .claude/commands/                   ← 12+ slash commands
│   ├── /run-tests
│   ├── /test-results
│   ├── /test-report
│   ├── /test-coverage
│   ├── /test-trends
│   └── ... (7+ more)
├── src/
│   ├── models.py                       ← Test result schemas
│   ├── framework_detector.py           ← Auto-detect pytest/jest/cargo/etc
│   ├── test_runner.py                  ← Test execution
│   ├── test_aggregator.py              ← Result aggregation
│   ├── result_analyzer.py              ← Coverage/performance/flaky analysis
│   └── test_coordinator.py             ← Multi-project orchestration
├── coderef/
│   ├── testing/
│   │   ├── infrastructure/
│   │   │   ├── framework-support.md    # Supported frameworks & versions
│   │   │   ├── test-matrix.md          # Test execution order
│   │   │   └── detection-logic.md      # Auto-detection algorithm
│   │   └── results/
│   │       ├── 2025-12-26/
│   │       │   ├── coderef-context-tests.json
│   │       │   ├── coderef-workflow-tests.json
│   │       │   ├── next-scraper-tests.json
│   │       │   └── ecosystem-summary.json
│   │       └── LATEST/ → symlink
│   └── workorder/
│       └── WO-COEREF-TESTING-SETUP-001/
│           ├── plan.json
│           └── DELIVERABLES.md
└── personas/
    └── testing-expert.json             ← testing-expert persona definition
```

---

## 🚀 Implementation Roadmap

### Week 1: Foundation
```
Day 1:
  ✅ Create CLAUDE.md with testing persona specification
  ✅ Create server skeleton & pyproject.toml
  ✅ Setup MCP server entry point (server.py)

Day 2-3:
  ✅ Implement framework detection (pytest, jest, cargo, mocha, vitest)
  ✅ Build test discovery tools (discover_tests, list_test_frameworks)
  ✅ Create unified result schema

Day 4:
  ✅ Implement test execution tools (run_all_tests, run_test_file, etc.)
  ✅ Add async/parallel execution support
```

### Week 2: Tools & Integration
```
Day 1:
  ✅ Build result management tools (aggregate, report, compare)
  ✅ Implement analysis tools (coverage, performance, flaky)

Day 2-3:
  ✅ Create slash commands (12+ commands)
  ✅ Add coderef/testing/ artifact storage

Day 4:
  ✅ Write README.md with usage examples
  ✅ Document all 14 tools with examples
```

### Week 3: Testing & Deployment
```
Day 1:
  ✅ Test on CodeRef ecosystem (4 servers)
  ✅ Test on next-scraper project
  ✅ Test on other projects

Day 2-3:
  ✅ Performance optimization
  ✅ Edge case handling
  ✅ Error message improvements

Day 4:
  ✅ Register in global ~/.mcp.json
  ✅ Create deployment guide
  ✅ Final documentation
```

---

## 🎯 Key Design Decisions

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Scope | Universal (any project) | CodeRef-specific | Maximize reusability & applicability |
| Dependencies | Independent | Depend on coderef-* | Can run standalone, works anywhere |
| Framework Support | Auto-detect all | Single framework | Works with pytest AND jest AND cargo |
| Result Format | Unified JSON | Framework-native | Consistent across frameworks |
| Persona | testing-expert | Per-test personas | One unified testing perspective |
| Tool Count | 14 tools | 30+ tools | Core functionality, avoid bloat |
| Execution | Async/parallel | Sequential | Fast feedback, efficient resources |

---

## 📊 Deployment Strategy

### Global Registration

Register once in `~/.mcp.json`:

```json
{
  "mcpServers": {
    "coeref-testing": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coeref-testing/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coeref-testing",
      "description": "Universal test orchestration & reporting server"
    }
  }
}
```

### Usage Across Projects

```bash
# Use on CodeRef ecosystem
project_path = "C:/Users/willh/.mcp-servers/coderef-workflow"
run_all_tests(project_path)

# Use on next-scraper
project_path = "C:/Users/willh/Desktop/projects/next-scraper"
run_all_tests(project_path)

# Use on any user project
project_path = "/any/user/project"
run_all_tests(project_path)
```

### Slash Commands (Global)

Once registered, all commands available everywhere:

```bash
/run-tests                    # Run full suite on current project
/run-server-tests             # Run specific test category
/test-results                 # View latest results
/test-report                  # Generate report
/test-coverage                # Show coverage
/test-trends                  # Trends & regressions
/test-performance             # Speed analysis
/detect-flaky                 # Find flaky tests
/test-health                  # Health check
/compare-runs                 # Compare test runs
/discover-tests               # List tests in project
/list-frameworks              # Show detected frameworks
```

---

## ✅ Success Metrics

- ✅ Works with pytest projects
- ✅ Works with jest projects
- ✅ Works with cargo projects
- ✅ Auto-detects framework
- ✅ Generates reports (markdown/HTML/JSON)
- ✅ Testing persona functional
- ✅ CLAUDE.md complete
- ✅ Can be deployed to CodeRef ecosystem (4 servers)
- ✅ Can be deployed to next-scraper
- ✅ Can be deployed to any user project

---

## 🔗 Integration Patterns (Optional)

### Pattern 1: Standalone Usage
```
User Project → coeref-testing → Test Results
(No dependencies on other MCP servers)
```

### Pattern 2: With coderef-context (Optional)
```
User Project → coeref-testing
                    ↓
              coderef-context (optional)
                    ↓
              Dependency analysis of tests
```

### Pattern 3: With coderef-workflow (Optional)
```
User Project → coeref-testing
                    ↓
              coderef-workflow (optional)
                    ↓
              Track tests as workorders
```

### Pattern 4: With coderef-docs (Optional)
```
User Project → coeref-testing
                    ↓
              coderef-docs (optional)
                    ↓
              Generate test reports/docs
```

---

## 📝 Key Principles

✅ **Project-Agnostic** - Works with ANY project, ANY framework
✅ **Independent** - Can run standalone without dependencies
✅ **Integrable** - Optional hooks to coderef-context, coderef-workflow, coderef-docs
✅ **Framework-Aware** - Auto-detects pytest, jest, cargo, mocha, vitest, etc.
✅ **Unified Results** - All frameworks output to same JSON schema
✅ **Global Deployment** - Registered in ~/.mcp.json, available everywhere
✅ **Reusable** - Deploy once, use across all projects
✅ **Fast Feedback** - Parallel execution, async operations

---

## 🎓 Next Steps

1. **Create CLAUDE.md** with complete AI context and testing-expert persona
2. **Build server skeleton** with framework detection
3. **Implement 14 core tools** (discovery, execution, aggregation, analysis)
4. **Create slash commands** for user-friendly access
5. **Test on CodeRef ecosystem** (4 servers)
6. **Test on other projects** (next-scraper, etc.)
7. **Register globally** in ~/.mcp.json
8. **Deploy and use** across all projects

---

**Document Created:** 2025-12-26
**Maintained by:** willh, Claude Code AI
**Status:** Planning → Implementation Ready

