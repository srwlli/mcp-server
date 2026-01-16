# Testing Integration Guide

**Purpose:** How to integrate coderef-testing into multi-agent sessions and workorder workflows for comprehensive QA coverage.

**Created:** 2026-01-16
**Version:** 1.0.0
**Status:** Active Reference

---

## Why Integrate Testing?

**Problem:** Project agents implement features but don't validate their changes systematically. Tests may be skipped, incomplete, or run inconsistently.

**Solution:** Add coderef-testing as a dedicated testing agent in sessions to:
- ✅ Validate implementation against test fixtures
- ✅ Run full test suites after code changes
- ✅ Detect regressions and flaky tests
- ✅ Generate test coverage reports
- ✅ Offload testing work from implementation agents

**Result:** Project agents focus on implementation, coderef-testing handles validation. Clear separation of concerns, comprehensive QA coverage.

---

## Integration Pattern: 4-Agent Session Structure

### Standard Pattern (Without Testing)
```
Session: WO-FEATURE-001
├── Agent 1 (Implementation) → implements code
├── Agent 2 (Documentation) → documents changes
└── Orchestrator → synthesizes results
```

### Enhanced Pattern (With Testing)
```
Session: WO-FEATURE-001
├── Agent 1 (Implementation) → implements code + basic validation
├── Agent 2 (Testing) → runs full test suite, generates reports ⭐
├── Agent 3 (Documentation) → documents changes + test results
└── Orchestrator → synthesizes results + validates all tests pass
```

**Key Benefit:** Agent 1 can focus on implementation, Agent 2 (coderef-testing) handles comprehensive testing.

---

## When to Include coderef-testing

### ✅ Include Testing Agent When:
1. **Code Changes** - Any feature that modifies source code
2. **Refactoring** - Structural changes that need regression testing
3. **Performance Improvements** - Need to validate performance gains
4. **Bug Fixes** - Verify fix works and doesn't break existing tests
5. **API Changes** - Ensure backward compatibility via tests
6. **Multi-Framework Projects** - Testing across pytest/jest/cargo/vitest

### ❌ Skip Testing Agent When:
1. **Documentation Only** - No code changes to validate
2. **Planning/Analysis** - Pre-implementation phase
3. **Proof of Concept** - Exploratory work without tests
4. **Non-Code Projects** - Configuration/deployment changes only

---

## Session Integration: Step-by-Step

### Step 1: Add coderef-testing to Agent Roster

**In session-level `communication.json`:**

```json
{
  "agents": [
    {
      "agent_id": "coderef-core",
      "agent_path": "C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core",
      "role": "Implement scanner improvements",
      "phases": ["phase_1"],
      "status": "not_started"
    },
    {
      "agent_id": "coderef-testing",
      "agent_path": "C:\\Users\\willh\\.mcp-servers\\coderef-testing",
      "role": "Validate scanner improvements via test execution",
      "phases": ["phase_1"],
      "status": "not_started"
    }
  ]
}
```

**Key Fields:**
- `agent_id`: Always "coderef-testing"
- `agent_path`: Always "C:\\Users\\willh\\.mcp-servers\\coderef-testing"
- `role`: Describe what testing validates (specific to session)
- `phases`: Same phase(s) as implementation agent(s)

### Step 2: Create coderef-testing Subdirectory (Hierarchical Sessions)

**Structure:**
```
sessions/{session-name}/coderef-testing/
├── communication.json      # Task tracking
├── instructions.json       # Testing workflow
├── resources/
│   └── index.md           # Links to test specs
└── outputs/
    └── test-results.md    # Test report
```

### Step 3: Define Testing Tasks

**In `coderef-testing/communication.json`:**

```json
{
  "workorder_id": "WO-SCANNER-COMPLETE-INTEGRATION-001-CODEREF-TESTING",
  "parent_session": "WO-SCANNER-COMPLETE-INTEGRATION-001",
  "agent_id": "coderef-testing",
  "agent_path": "C:\\Users\\willh\\.mcp-servers\\coderef-testing",
  "phase": "phase_1",
  "role": "Validate scanner improvements via comprehensive test execution",
  "status": "not_started",

  "tasks": [
    {
      "task_id": "task_1",
      "description": "Run TypeScript compilation tests on scanner.ts and ast-element-scanner.ts",
      "status": "not_started",
      "test_command": "npm run build",
      "expected_result": "TypeScript compiles with 0 errors"
    },
    {
      "task_id": "task_2",
      "description": "Run scanner unit tests with test fixtures (interfaces, decorators, properties)",
      "status": "not_started",
      "test_command": "npm test -- scanner.test.ts",
      "expected_result": "All tests pass, accuracy >= 95%"
    },
    {
      "task_id": "task_3",
      "description": "Run performance benchmarks (500-file scan)",
      "status": "not_started",
      "test_command": "npm run benchmark",
      "expected_result": "Scan completes in 300-400ms (3-5x faster than 1185ms baseline)"
    },
    {
      "task_id": "task_4",
      "description": "Run full test suite to verify no regressions",
      "status": "not_started",
      "test_command": "npm test",
      "expected_result": "All existing tests pass"
    },
    {
      "task_id": "task_5",
      "description": "Generate test coverage report",
      "status": "not_started",
      "test_command": "npm run coverage",
      "expected_result": "Coverage >= 80%"
    }
  ],

  "success_metrics": {
    "compilation": {
      "baseline": "Unknown",
      "target": "0 TypeScript errors",
      "status": "Not started"
    },
    "accuracy": {
      "baseline": "85%",
      "target": "95%+",
      "status": "Not started"
    },
    "performance": {
      "baseline": "1185ms (500 files)",
      "target": "300-400ms (3-5x faster)",
      "status": "Not started"
    },
    "regression": {
      "baseline": "All tests passing",
      "target": "All tests still passing",
      "status": "Not started"
    }
  },

  "outputs": {
    "primary_output": "outputs/coderef-testing-phase1-validation.md",
    "format": "markdown"
  },

  "phase_gate": {
    "required_for_phase_2": true,
    "criteria": [
      "All 5 tasks status='complete'",
      "TypeScript compilation passes (0 errors)",
      "Scanner accuracy >= 95%",
      "Performance benchmark: 300-400ms",
      "All regression tests pass",
      "Test coverage >= 80%",
      "Output created: outputs/coderef-testing-phase1-validation.md"
    ]
  }
}
```

### Step 4: Write Testing Instructions

**In `coderef-testing/instructions.json`:**

```json
{
  "workorder_id": "WO-SCANNER-COMPLETE-INTEGRATION-001-CODEREF-TESTING",
  "agent_id": "coderef-testing",
  "phase": "phase_1",
  "role": "Validate scanner improvements",

  "context": {
    "problem": "Scanner improvements need validation to ensure accuracy, performance, and no regressions",
    "solution": "Run compilation tests, unit tests, benchmarks, regression suite, and coverage analysis",
    "impact": "Ensures scanner improvements meet quality gates before downstream integration in Phase 2/3"
  },

  "execution_steps": {
    "step_1": "WAIT for coderef-core Phase 1 completion - check ../coderef-core/communication.json status='complete'",
    "step_2": "READ resources/index.md to access test fixtures and benchmark specifications",
    "step_3": "ACTIVATE testing-expert persona: use_persona('testing-expert')",
    "step_4": "FOR EACH TASK: Run test command → Capture results → UPDATE communication.json task.status='complete' → REPEAT",
    "step_5": "AFTER ALL TASKS: Aggregate results, calculate success metrics, update communication.json status='complete'",
    "step_6": "CREATE outputs/coderef-testing-phase1-validation.md with test results, metrics, and recommendations",
    "step_7": "VALIDATE phase_gate_checklist - all criteria must be met"
  },

  "tasks": {
    "task_1": {
      "description": "TypeScript Compilation Validation",
      "implementation": {
        "command": "cd C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core && npm run build",
        "success_criteria": "Exit code 0, no TypeScript errors in scanner.ts or ast-element-scanner.ts"
      }
    },
    "task_2": {
      "description": "Scanner Unit Tests with Fixtures",
      "implementation": {
        "command": "npm test -- scanner.test.ts",
        "fixtures": [
          "test-fixtures/interface-detection.ts",
          "test-fixtures/decorator-detection.ts",
          "test-fixtures/class-properties.ts"
        ],
        "success_criteria": "All tests pass, accuracy >= 95% on fixtures"
      }
    },
    "task_3": {
      "description": "Performance Benchmarks",
      "implementation": {
        "command": "npm run benchmark -- --files=500",
        "success_criteria": "Scan completes in 300-400ms (vs 1185ms baseline)"
      }
    },
    "task_4": {
      "description": "Regression Test Suite",
      "implementation": {
        "command": "npm test",
        "success_criteria": "All existing tests pass, no new failures"
      }
    },
    "task_5": {
      "description": "Coverage Analysis",
      "implementation": {
        "command": "npm run coverage",
        "success_criteria": "Coverage >= 80% for scanner.ts and ast-element-scanner.ts"
      }
    }
  },

  "success_criteria": {
    "task_1": "TypeScript compiles successfully with 0 errors",
    "task_2": "Unit tests pass with 95%+ accuracy on fixtures",
    "task_3": "Performance benchmark shows 3-5x improvement",
    "task_4": "Regression suite passes, no new failures",
    "task_5": "Test coverage meets 80% threshold"
  },

  "output_requirements": {
    "file": "outputs/coderef-testing-phase1-validation.md",
    "format": "markdown",
    "sections": [
      "## Executive Summary",
      "## Test Results (5/5 tasks)",
      "## Compilation Validation",
      "## Unit Test Results (accuracy, fixtures)",
      "## Performance Benchmarks (before/after)",
      "## Regression Analysis",
      "## Coverage Report",
      "## Success Metrics Achieved",
      "## Recommendations for Phase 2/3"
    ]
  },

  "phase_gate_checklist": [
    "All 5 tasks status='complete' in communication.json",
    "TypeScript compilation passes",
    "Scanner accuracy >= 95%",
    "Performance: 300-400ms (3-5x improvement)",
    "No regressions in existing tests",
    "Test coverage >= 80%",
    "Output created: outputs/coderef-testing-phase1-validation.md",
    "communication.json updated with status='complete'"
  ]
}
```

### Step 5: Update Phase Gate Criteria

**In session-level `communication.json`, update phase gate:**

```json
{
  "phases": {
    "phase_1": {
      "gate_criteria": [
        "All 7 scanner improvements implemented (coderef-core)",
        "All 5 validation tasks complete (coderef-testing)", // ⭐ Added
        "TypeScript compilation passes (0 errors)",
        "Scanner accuracy >= 95%",
        "Performance: 300-400ms (3-5x faster)",
        "All regression tests pass", // ⭐ Added
        "Test coverage >= 80%", // ⭐ Added
        "All outputs validated"
      ]
    }
  }
}
```

---

## Workorder Integration

### Pattern: Testing Task in plan.json

When using `/create-workorder`, include testing tasks in the implementation plan:

**In `coderef/workorder/{feature-name}/plan.json`:**

```json
{
  "implementation_plan": {
    "phases": [
      {
        "phase_id": "IMPL",
        "tasks": [
          {
            "task_id": "IMPL-001",
            "description": "Implement AST scanner integration"
          },
          {
            "task_id": "IMPL-002",
            "description": "Add interface detection to AST scanner"
          }
        ]
      },
      {
        "phase_id": "TEST",
        "phase_name": "Testing & Validation",
        "tasks": [
          {
            "task_id": "TEST-001",
            "description": "Run TypeScript compilation tests",
            "validation_criteria": "0 compilation errors"
          },
          {
            "task_id": "TEST-002",
            "description": "Run unit tests with interface/decorator fixtures",
            "validation_criteria": "All tests pass, 95%+ accuracy"
          },
          {
            "task_id": "TEST-003",
            "description": "Run performance benchmarks",
            "validation_criteria": "300-400ms for 500 files"
          },
          {
            "task_id": "TEST-004",
            "description": "Run full regression suite",
            "validation_criteria": "No new test failures"
          }
        ]
      }
    ]
  }
}
```

### Delegation Pattern

**Option A: Project Agent Runs Tests Locally**
- Project agent (e.g., coderef-core) runs tests themselves using test commands in plan.json
- Suitable for: Simple validation, quick smoke tests, CI/CD integration

**Option B: Delegate to coderef-testing Agent**
- Project agent completes implementation, updates status='ready_for_testing'
- coderef-testing agent picks up testing tasks, runs comprehensive suite
- Suitable for: Complex testing, multi-framework projects, comprehensive QA

**Example Delegation:**

```json
// coderef-core/communication.json
{
  "status": "ready_for_testing",
  "notes": "Implementation complete, awaiting validation from coderef-testing"
}

// coderef-testing/communication.json
{
  "status": "in_progress",
  "tasks": [
    {
      "task_id": "task_1",
      "description": "Validate coderef-core scanner improvements",
      "status": "in_progress"
    }
  ]
}
```

---

## Testing Persona: testing-expert

**Activate in coderef-testing agent:**

```python
# In coderef-testing execution steps
use_persona('testing-expert')
```

**Persona Capabilities:**
- 15 expertise areas (test strategy, frameworks, coverage, performance, flaky detection)
- 7 use cases (plan strategy, debug failures, analyze coverage, optimize speed, CI/CD setup, fix flaky tests, generate reports)
- 1500+ line system prompt with patterns for pytest, jest, cargo, mocha, vitest

**When to Use:**
- Debugging test failures
- Optimizing test performance
- Setting up test infrastructure
- Analyzing coverage gaps
- Planning test strategy

---

## Real-World Example: scanner-complete-integration

### Current Structure (Without Testing)
```
sessions/scanner-complete-integration/
├── communication.json (3 agents: core, docs, workflow)
├── coderef-core/ (Phase 1: Implementation)
├── coderef-docs/ (Phase 2: Docs integration)
└── coderef-workflow/ (Phase 3: Workflow integration)
```

### Enhanced Structure (With Testing)
```
sessions/scanner-complete-integration/
├── communication.json (4 agents: core, testing, docs, workflow)
├── coderef-core/ (Phase 1: Implementation)
├── coderef-testing/ (Phase 1: Validation) ⭐ NEW
├── coderef-docs/ (Phase 2: Docs integration)
└── coderef-workflow/ (Phase 3: Workflow integration)
```

**Phase 1 Flow:**
1. coderef-core implements 7 scanner improvements → status='complete'
2. coderef-testing validates all improvements → status='complete'
3. Phase 1 gate check: Both agents complete, all tests pass
4. Phase 2 begins: coderef-docs can safely leverage Phase 1 outputs

**Benefits:**
- ✅ Clear separation: coderef-core focuses on implementation, coderef-testing on validation
- ✅ Comprehensive QA: 5 testing tasks (compilation, unit, benchmarks, regression, coverage)
- ✅ Quality gate: Phase 2 can't start until tests pass
- ✅ Documentation: Test results captured in outputs/coderef-testing-phase1-validation.md

---

## Quick Reference: Testing Checklist

When creating a session with code changes:

- [ ] Add coderef-testing to agent roster in communication.json
- [ ] Create coderef-testing subdirectory with communication.json + instructions.json
- [ ] Define 3-5 testing tasks (compilation, unit, benchmarks, regression, coverage)
- [ ] Specify test commands and success criteria
- [ ] Add testing criteria to phase gate checklist
- [ ] Include testing-expert persona activation in instructions
- [ ] Document expected outputs (test-results.md or validation.md)
- [ ] Ensure testing runs AFTER implementation agent completes

---

## Tools & Commands Reference

### MCP Tools (coderef-testing)
```python
# Discovery
discover_tests(project_path)
list_test_frameworks(project_path)

# Execution
run_all_tests(project_path, framework)
run_test_file(project_path, test_file)
run_tests_in_parallel(project_path, workers=4)

# Analysis
analyze_coverage(project_path)
detect_flaky_tests(project_path)
analyze_test_performance(project_path)
validate_test_health(project_path)

# Reporting
generate_test_report(project_path, format='markdown')
```

### Slash Commands
```bash
/run-tests              # Run full test suite
/test-results           # View latest results
/test-coverage          # Show coverage
/test-performance       # Analyze speed
/detect-flaky           # Find flaky tests
/test-health            # Overall health check
```

---

## Summary

**Key Principle:** When a session includes code changes, include coderef-testing as a dedicated testing agent.

**Integration Steps:**
1. Add to agent roster
2. Create testing subdirectory
3. Define testing tasks
4. Activate testing-expert persona
5. Update phase gate criteria

**Benefits:**
- Clear separation of concerns (implementation vs validation)
- Comprehensive QA coverage
- Offloads testing from project agents
- Quality gates prevent bad code from advancing to next phase
- Centralized testing expertise via testing-expert persona

---

**Maintained by:** willh, Claude Code AI
**Reference:** [coderef-testing CLAUDE.md](C:\Users\willh\.mcp-servers\coderef-testing\CLAUDE.md)
