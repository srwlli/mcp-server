# CodeRef Ecosystem: Professional Testing Architecture

**Version:** 1.0.0
**Created:** 2025-12-26
**Status:** ✅ Production Standard
**Purpose:** Centralized testing strategy for all 4 MCP servers with proof artifacts

---

## Executive Summary

This document establishes the **professional testing framework** for the CodeRef Ecosystem. It defines:
- ✅ Unified test structure across all 4 servers
- ✅ Test categories and what each proves
- ✅ Proof artifact management (real data vs mocks)
- ✅ CI/CD integration standards
- ✅ Test documentation requirements
- ✅ Coverage and quality gates

**Goal:** Use tests not just for validation, but as **living proof** of functionality.

---

## Test Directory Structure (Standard Template)

```
{server}/
├── src/                                # Source code
│   ├── server.py
│   ├── mcp_client.py (if using coderef-context)
│   └── generators/
│
├── tests/                              # ← CENTRALIZED TEST FOLDER
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration (shared fixtures)
│   ├── pytest.ini                      # Pytest settings
│   │
│   ├── fixtures/                       # ← MOCKS & SHARED TEST DATA
│   │   ├── __init__.py
│   │   ├── mock_mcp_client.py          # Mock responses for testing
│   │   ├── mock_responses.py           # Response builders
│   │   └── test_data.py                # Static test data
│   │
│   ├── unit/                           # ← UNIT TESTS (Fast, Isolated)
│   │   ├── __init__.py
│   │   ├── test_subprocess_lifecycle.py
│   │   ├── test_json_rpc_protocol.py
│   │   ├── test_failure_modes.py
│   │   └── test_*.py                   # Feature-specific unit tests
│   │
│   ├── integration/                    # ← INTEGRATION TESTS (Component interaction)
│   │   ├── __init__.py
│   │   ├── test_tool_invocation.py     # Prove tools actually called
│   │   ├── test_data_flow.py           # Prove data flows through pipeline
│   │   ├── test_end_to_end.py          # Complete workflow validation
│   │   └── test_*.py                   # Feature-specific integration tests
│   │
│   ├── smoke/                          # ← SMOKE TESTS (Quick sanity checks)
│   │   ├── __init__.py
│   │   ├── test_imports.py             # Can import all modules
│   │   ├── test_server_startup.py      # Server starts without errors
│   │   └── test_basic_health.py        # Health check endpoints
│   │
│   ├── performance/                    # ← PERFORMANCE TESTS (Speed, memory)
│   │   ├── __init__.py
│   │   ├── test_tool_latency.py        # Tool response time < threshold
│   │   └── test_memory_usage.py        # Memory doesn't leak
│   │
│   ├── security/                       # ← SECURITY TESTS (Validation, injection)
│   │   ├── __init__.py
│   │   ├── test_input_validation.py    # Reject malformed input
│   │   └── test_injection_prevention.py # Prevent code/SQL injection
│   │
│   └── proofs/                         # ← PROOF ARTIFACTS (Real data evidence)
│       ├── __init__.py
│       ├── test_proofs.py              # Load and verify real proof data
│       └── README.md                   # How to interpret proofs
│
├── coderef/workorder/                  # ← TEST WORKORDERS (Real feature proofs)
│   └── {feature-name}/
│       ├── context.json                # Requirements
│       ├── analysis.json               # Real coderef-context output
│       ├── plan.json                   # Real planning with injections
│       └── PROOF_DOCUMENT.md           # Proof of concept
│
├── coderef/proofs/                     # ← CENTRALIZED PROOFS (Ecosystem-wide)
│   ├── README.md
│   ├── 2025-12-26_coderef_injection_proof.md
│   └── {proof_name}.md
│
├── .pytest.ini                         # Pytest configuration
├── pytest.ini                          # Pytest settings
├── tox.ini                             # Test automation config
├── .coveragerc                         # Coverage requirements
└── TEST_DOCUMENTATION.md               # This server's test strategy
```

---

## Test Categories & What Each Proves

### **Category 1: Unit Tests** (Fast, Isolated, Mocked)
**Location:** `tests/unit/`
**Runtime:** < 100ms per test
**Mocks:** YES (use mocks, don't call external services)

**Purpose:** Prove individual components work in isolation

**Example Tests:**
- `test_json_rpc_request_format` - JSON-RPC 2.0 compliance
- `test_subprocess_initialization` - Process spawning works
- `test_error_response_parsing` - Error handling logic

**What They Prove:**
- ✅ Code logic is correct
- ✅ Error cases are handled
- ✅ Data structures are valid
- ❌ NOT how components interact
- ❌ NOT real coderef-context behavior

**Assertion Style:**
```python
def test_something_works():
    """
    WHAT IT PROVES:
    - Component X does task Y
    - Input validation works
    - Error case handled

    ASSERTION:
    - Result matches expected
    """
    # Setup
    component = Component()

    # Execute
    result = component.do_something(input_data)

    # Assert
    assert result == expected, "Should compute correctly"
    assert component.state == valid_state, "State should update"
```

---

### **Category 2: Integration Tests** (Medium speed, Real interactions)
**Location:** `tests/integration/`
**Runtime:** 0.5-2 seconds per test
**Mocks:** YES, but mock at module boundaries (not internal logic)

**Purpose:** Prove components work together correctly

**Key Tests for coderef-context Injection:**

#### **TEST 1: Tool Invocation** (Prove tools are called)
```python
async def test_analyze_project_calls_coderef_scan():
    """
    WHAT IT PROVES:
    - analyze_project_for_planning() calls coderef_scan
    - coderef_scan receives correct arguments
    - Results are captured and used
    """
    # Setup: Mock coderef-context
    mock_client = MockMCPClient()
    mock_client.configure_response("coderef_scan", {...})

    # Execute: Call planning analyzer
    result = await analyze_project_for_planning()

    # Assert: Tool was called
    assert mock_client.get_call_count("coderef_scan") == 1
    assert mock_client.get_calls_for_tool("coderef_scan")[0]["arguments"]["project_path"]
```

#### **TEST 2: Data Flow** (Prove data flows through pipeline)
```python
async def test_scan_results_appear_in_plan():
    """
    WHAT IT PROVES:
    - coderef_scan → analysis.json → plan.json (data flows)
    - Components are preserved (no data loss)
    - File paths are intact
    """
    # Execute full pipeline
    analysis = await create_analysis()
    plan = await create_plan_from_analysis(analysis)

    # Assert: Data flows
    assert "components" in analysis["inventory"]
    assert analysis["components"] == plan["components"]
```

**What They Prove:**
- ✅ Components communicate correctly
- ✅ Data flows through pipeline
- ✅ Integrations work as designed
- ❌ NOT real external service behavior
- ❌ NOT production performance

---

### **Category 3: Smoke Tests** (Very fast, Basic sanity)
**Location:** `tests/smoke/`
**Runtime:** < 50ms
**Mocks:** YES (don't test logic, just presence)

**Purpose:** Quick sanity check before running full suite

**Examples:**
```python
def test_imports():
    """Can import all modules without errors"""
    from src import server, mcp_client, generators
    assert server is not None

def test_server_startup():
    """Server instantiates without errors"""
    server = MCPServer()
    assert server is not None

def test_tools_registered():
    """All expected tools are registered"""
    server = MCPServer()
    tools = server.get_tools()
    assert len(tools) >= expected_count
```

**What They Prove:**
- ✅ No import errors
- ✅ No syntax errors
- ✅ Basic structure intact
- ❌ NOT functionality
- ❌ NOT correctness

---

### **Category 4: Performance Tests** (Baseline measurements)
**Location:** `tests/performance/`
**Runtime:** 1-5 seconds
**Mocks:** YES (but measure real code paths)

**Purpose:** Track performance baselines, catch regressions

**Examples:**
```python
@pytest.mark.benchmark
def test_tool_call_latency(benchmark):
    """
    Tool calls should complete < 1 second
    (excluding coderef-context which has 120s timeout)
    """
    def call_tool():
        return client.call_tool("tool_name", {})

    result = benchmark(call_tool)
    assert result.stats.mean < 1.0  # seconds

@pytest.mark.memory
def test_no_memory_leak():
    """Memory usage should not grow with repeated calls"""
    import tracemalloc
    tracemalloc.start()

    for _ in range(100):
        result = client.call_tool("tool", {})

    current, peak = tracemalloc.get_traced_memory()
    assert peak < 50_000_000  # 50MB limit
```

**What They Prove:**
- ✅ Performance meets baseline
- ✅ No memory leaks
- ✅ Scalability limits known
- ❌ NOT real-world performance
- ❌ NOT production load capacity

---

### **Category 5: Security Tests** (Input validation, injection prevention)
**Location:** `tests/security/`
**Runtime:** < 200ms
**Mocks:** YES (test validation logic)

**Purpose:** Prevent security vulnerabilities

**Examples:**
```python
def test_rejects_malformed_json():
    """Invalid JSON should be rejected"""
    with pytest.raises(ValueError):
        parse_request(b"not valid json")

def test_prevents_code_injection():
    """Arbitrary code in params should not execute"""
    dangerous_input = "__import__('os').system('rm -rf /')"
    result = process_tool_call(dangerous_input)
    # Should treat as literal string, not execute

def test_validates_project_path():
    """Project path should not escape sandbox"""
    bad_path = "../../../../etc/passwd"
    with pytest.raises(ValueError):
        validate_project_path(bad_path)
```

**What They Prove:**
- ✅ Input validation works
- ✅ No injection vulnerabilities
- ✅ Boundary enforcement
- ❌ NOT real attack resistance
- ❌ NOT production security posture

---

### **Category 6: Proof Tests** (Real data validation)
**Location:** `tests/proofs/`
**Runtime:** < 500ms
**Mocks:** NO (load and validate REAL data)

**Purpose:** Prove real functionality works (not mocked)

**Examples:**
```python
def test_real_coderef_injection_proof():
    """
    Validate that test-coderef-injection workorder contains
    real coderef-context output (not mock data)
    """
    proof_data = load_proof("test-coderef-injection")

    # ASSERTION 1: Real coderef_scan output
    assert proof_data["analysis"]["coderef_scan_results"]["total_files"] == 45
    assert proof_data["analysis"]["coderef_scan_results"]["total_components"] == 127
    assert len(proof_data["analysis"]["coderef_scan_results"]["components"]) > 0

    # ASSERTION 2: Real coderef_query output
    assert proof_data["analysis"]["coderef_query_results"]["tool_invoked"] == "coderef_query"

    # ASSERTION 3: Marked as proof
    assert "proof_of_injection" in proof_data["analysis"]["coderef_scan_results"]

    # ASSERTION 4: Data flows to plan
    assert proof_data["plan"]["0_PREPARATION"]["code_inventory"] is not None
```

**What They Prove:**
- ✅ Real coderef-context output is present
- ✅ Data can be traced from tool to output
- ✅ Proof artifacts are valid
- ✅ Functionality works in practice (not just unit test)

---

## Test Configuration Files

### **conftest.py** (Shared fixtures)
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
async def mock_mcp_client():
    """Shared mock MCP client for integration tests"""
    from tests.fixtures.mock_mcp_client import MockMCPClient
    return MockMCPClient()

@pytest.fixture
def test_project_path():
    """Standard project path for tests"""
    return "/test/project"

@pytest.fixture
def sample_code_inventory():
    """Sample coderef_scan output"""
    return {
        "inventory": {
            "components": [
                {"type": "class", "name": "Service", "file": "src/service.py"},
                {"type": "function", "name": "process", "file": "src/utils.py"},
            ],
            "total_files": 2,
            "total_components": 2
        }
    }
```

### **pytest.ini** (Configuration)
```ini
[pytest]
# Pytest configuration for all tests

# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for categorizing tests
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (component interaction)
    smoke: Smoke tests (sanity checks)
    performance: Performance benchmarks
    security: Security validation
    proof: Real data proof tests
    asyncio: Async tests

# Output options
addopts =
    -v
    --tb=short
    --strict-markers
    -ra
    --capture=no

# Timeout for tests (seconds)
timeout = 30
asyncio_mode = auto
```

### **.coveragerc** (Coverage requirements)
```ini
[run]
source = src
omit =
    */tests/*
    */fixtures/*

[report]
# Minimum coverage threshold
fail_under = 85
precision = 2

# Exclude lines from coverage
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:

[html]
directory = htmlcov
```

---

## Running Tests Professionally

### **Full Test Suite**
```bash
# Run all tests with coverage
cd C:\Users\willh\.mcp-servers\{server}
python -m pytest tests/ -v --cov=src --cov-report=html

# Output: htmlcov/index.html (open in browser for coverage report)
```

### **Category-Specific**
```bash
# Run only unit tests (fast)
python -m pytest tests/unit/ -v -m unit

# Run only integration tests
python -m pytest tests/integration/ -v -m integration

# Run only smoke tests (quick sanity check)
python -m pytest tests/smoke/ -v -m smoke

# Run proof tests (real data validation)
python -m pytest tests/proofs/ -v -m proof
```

### **CI/CD Integration**
```bash
# Quick smoke test (before commit)
python -m pytest tests/smoke/ tests/unit/ -v

# Full test suite (before merge)
python -m pytest tests/ -v --cov=src --cov-report=term

# With benchmarking (before release)
python -m pytest tests/ -v --benchmark-only
```

### **Watch Mode** (Development)
```bash
# Requires pytest-watch: pip install pytest-watch
ptw tests/ -- -v -m "not performance"
```

---

## Test Documentation Template

Each server should have `TEST_DOCUMENTATION.md`:

```markdown
# {Server} Test Strategy

## Overview
What this server does and how tests validate it.

## Test Categories & Coverage

### Unit Tests (tests/unit/)
- test_*.py - Description of what's tested
- Coverage: 85%+

### Integration Tests (tests/integration/)
- test_*.py - How components work together
- Coverage: Integration points

### Proof Tests (tests/proofs/)
- test_*.py - Real data validation
- Evidence: [Workorder link]

## Running Tests

### All Tests
\`\`\`bash
pytest tests/ -v --cov=src
\`\`\`

### Specific Category
\`\`\`bash
pytest tests/unit/ -v
\`\`\`

## Coverage Requirements
- Unit: 90%+
- Integration: 80%+
- Overall: 85%+

## Proof Artifacts
- Location: `coderef/proofs/`
- Latest: [proof name]
- How to interpret: [link]
```

---

## Centralized Proof Management

### **Proof Storage** (Global Ecosystem)
```
C:\Users\willh\.mcp-servers\coderef\proofs/
├── README.md                           # How to use proofs
├── 2025-12-26_coderef_injection.md    # Latest proof
├── 2025-12-25_workflow_planning.md
└── index.json                          # Proof registry
```

### **Proof Document Structure**
```markdown
# Proof: [Feature Name]

**Date:** YYYY-MM-DD
**Server:** [server name]
**Evidence:** [Real data source]
**Status:** ✅ VERIFIED

## What This Proves
- Claim 1: [Assertion with evidence]
- Claim 2: [Assertion with evidence]

## Evidence
### 1. Real Data From [Tool]
\`\`\`json
{
  "tool_invoked": "coderef_scan",
  "timestamp": "ISO8601",
  "proof_of_injection": "Explanation"
}
\`\`\`

### 2. Data Flow
coderef_scan → analysis.json → plan.json

### 3. Test Validation
All tests pass: `pytest tests/proofs/ -v`

## How to Verify
1. Read this document
2. Run: `pytest tests/proofs/test_this_proof.py -v`
3. Inspect real files in: [workorder location]

## References
- Workorder: [link]
- Related proofs: [links]
```

### **Proof Registry** (index.json)
```json
{
  "proofs": [
    {
      "id": "coderef-injection-001",
      "name": "CodeRef-Context Injection",
      "date": "2025-12-26",
      "server": "coderef-workflow",
      "status": "verified",
      "file": "2025-12-26_coderef_injection.md",
      "workorder": "WO-TEST-INJECTION-001",
      "test_file": "tests/proofs/test_coderef_injection_proof.py",
      "claims": [
        "coderef_scan is invoked",
        "coderef_query provides dependencies",
        "Data flows to planning output"
      ]
    }
  ]
}
```

---

## Quality Gates & Coverage Requirements

### **Before Commit**
```bash
# Must pass
python -m pytest tests/unit/ -v
python -m pytest tests/smoke/ -v
python -m pytest tests/security/ -v

# Must have coverage >= 85%
python -m pytest tests/ --cov=src --cov-report=term
```

### **Before Merge (Pull Request)**
```bash
# All tests must pass
python -m pytest tests/ -v

# Coverage must be >= 85%
python -m pytest tests/ --cov=src --cov-fail-under=85

# No performance regressions
python -m pytest tests/performance/ -v
```

### **Before Release**
```bash
# Full suite including proofs
python -m pytest tests/ -v --benchmark-only

# Proof validation
python -m pytest tests/proofs/ -v

# Coverage report
python -m pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Best Practices

### **DO ✅**
- Use descriptive test names: `test_analyze_project_calls_coderef_scan()`
- Include docstrings explaining what the test proves
- Mock at module boundaries (don't mock internals)
- Use fixtures for common setup
- Categorize tests by purpose (unit/integration/proof)
- Document proof artifacts with real data markers
- Keep unit tests < 100ms
- Use parametrize for testing multiple cases

### **DON'T ❌**
- Mix unit and integration tests in same file
- Make tests dependent on each other
- Use sleep() for synchronization (use async/await)
- Mock internal implementation details
- Ignore test failures
- Leave TODO comments in tests
- Create tests that access external services directly
- Use hardcoded paths (use fixtures)

### **Proof-Specific ✅**
- Mark real data with `"source_tool"` field
- Include `"proof_of_injection"` explanations
- Store workorder alongside test
- Document data lineage (tool → file → assertion)
- Run proof tests separate from unit tests
- Update proof registry after creating new proofs

---

## Rollout Plan for All 4 Servers

### **Phase 1: coderef-workflow** (Already done)
✅ Complete test suite with proofs

### **Phase 2: coderef-docs** (Next)
- Create `tests/` directory
- Copy `conftest.py` template
- Add unit tests for doc generation
- Add integration tests for data flow
- Create proof workorder
- Update to this standard

### **Phase 3: coderef-context** (Next)
- Create `tests/` directory
- Add subprocess/CLI tests
- Add mock response fixtures
- Create proof workorder for real code analysis
- Update to this standard

### **Phase 4: coderef-personas** (Next)
- Create `tests/` directory
- Add persona activation tests
- Add behavior validation tests
- Create proof workorder
- Update to this standard

---

## Summary: Professional Testing Checklist

For each server, ensure:

- [ ] `tests/` directory exists with standard structure
- [ ] `conftest.py` with shared fixtures
- [ ] `pytest.ini` with markers and settings
- [ ] `.coveragerc` with 85% threshold
- [ ] Unit tests in `tests/unit/`
- [ ] Integration tests in `tests/integration/`
- [ ] Smoke tests in `tests/smoke/`
- [ ] Performance tests in `tests/performance/`
- [ ] Security tests in `tests/security/`
- [ ] Proof tests in `tests/proofs/`
- [ ] Proof workorder in `coderef/workorder/`
- [ ] TEST_DOCUMENTATION.md for server
- [ ] All tests passing locally
- [ ] Coverage >= 85%
- [ ] CI/CD integration ready

---

**This is the professional standard. Tests serve as living documentation and proof of functionality.** 🎯

