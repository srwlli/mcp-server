# Phase 2 Quick Start - Framework Detection & Execution

**Status:** Phase 1 Complete ✅ | Phase 2 Ready to Start
**Tasks:** 13 (5 detection + 8 execution)
**Duration:** 8-10 hours
**Next Task:** DETECT-001 (pytest detection)

---

## The 13 Tasks Ahead

### Detection (5 tasks, ~4.25 hours)
1. **DETECT-001** - Implement pytest detection (1h)
2. **DETECT-002** - Add jest/vitest detection (1h)
3. **DETECT-003** - Add cargo/mocha detection (0.75h)
4. **DETECT-004** - Implement caching/validation (0.5h)
5. **DETECT-TEST-001** - Unit tests for detection (1h)

### Execution (8 tasks, ~8.75 hours)
6. **RUN-001** - pytest execution (1.5h)
7. **RUN-002** - jest/vitest execution (1h)
8. **RUN-003** - cargo/mocha execution (0.75h)
9. **RUN-004** - async/parallel execution (1.5h)
10. **RUN-005** - timeout/error handling (1h)
11. **RUN-TEST-001** - test_runner unit tests (1h)
12. **RUN-TEST-002** - pytest integration tests (1h)
13. **RUN-TEST-003** - jest integration tests (1h)

---

## What You Need to Build

### NEW Files (Create These)

**1. src/framework_detector.py**
```python
async def detect_frameworks(project_path: str) -> FrameworkDetectionResult
async def detect_pytest(project_path: str) -> Optional[FrameworkInfo]
async def detect_jest(project_path: str) -> Optional[FrameworkInfo]
async def detect_vitest(project_path: str) -> Optional[FrameworkInfo]
async def detect_cargo(project_path: str) -> Optional[FrameworkInfo]
async def detect_mocha(project_path: str) -> Optional[FrameworkInfo]
```

**2. src/test_runner.py**
```python
async def run_tests(request: TestRunRequest) -> UnifiedTestResults
async def run_pytest(project_path: str, **kwargs) -> UnifiedTestResults
async def run_jest(project_path: str, **kwargs) -> UnifiedTestResults
async def run_vitest(project_path: str, **kwargs) -> UnifiedTestResults
async def run_cargo(project_path: str, **kwargs) -> UnifiedTestResults
async def run_mocha(project_path: str, **kwargs) -> UnifiedTestResults
```

**3. tests/test_framework_detector.py**
- Test each framework detection
- Test version extraction
- Test caching

**4. tests/test_runner.py**
- Mock test execution
- Verify schema compliance
- Test error handling

**5. tests/integration/test_pytest.py**
- Real pytest execution test

**6. tests/integration/test_jest.py**
- Real jest execution test

**7. tests/__init__.py** (empty)
**8. tests/integration/__init__.py** (empty)

### EXISTING Files (Modify These)

**server.py** - Replace placeholder handlers with real implementations
- `handle_discover_tests()` → call framework_detector
- `handle_list_frameworks()` → call framework_detector
- `handle_run_all_tests()` → call test_runner
- `handle_run_test_file()` → call test_runner
- `handle_run_test_category()` → call test_runner
- `handle_run_tests_parallel()` → call test_runner

---

## How Frameworks Work (Quick Reference)

### pytest
```
Detection: pyproject.toml [tool.pytest], tests/ dir, conftest.py
CLI: pytest --json-report=report.json
Output: JSON format with test results
```

### jest
```
Detection: package.json (jest field), jest.config.js
CLI: jest --json --listTests
Output: JSON format with test results
```

### vitest
```
Detection: vitest.config.ts, package.json (vitest)
CLI: vitest run --reporter=json
Output: JSON format with test results
```

### cargo
```
Detection: Cargo.toml [dev-dependencies]
CLI: cargo test -- --test-threads=1 --format json
Output: Custom format, must parse
```

### mocha
```
Detection: .mocharc.*, package.json (mocha)
CLI: mocha --reporter json
Output: JSON format with test results
```

---

## Key Implementation Patterns

### Pattern 1: Framework Detection
```python
# Check if pytest exists
has_pyproject = Path(project_path) / "pyproject.toml"
has_tests = Path(project_path) / "tests"
has_conftest = (Path(project_path) / "tests").glob("**/conftest.py")

if has_pyproject.exists() or has_tests.exists():
    # It's pytest - get version and return FrameworkInfo
```

### Pattern 2: Test Execution
```python
# Run framework's native CLI
cmd = ["pytest", "--json-report=report.json"]
stdout, stderr, returncode = await execute_with_timeout(cmd, timeout=300)

# Parse output
results = parse_pytest_json(stdout)

# Return normalized UnifiedTestResults
return UnifiedTestResults(
    project=project_path,
    framework=FrameworkInfo(framework=TestFramework.PYTEST, ...),
    summary=TestSummary(...),
    tests=[TestResult(...) for ...],
    timestamp=datetime.utcnow()
)
```

### Pattern 3: Error Handling
```python
try:
    result = await run_tests(request)
except TimeoutError:
    return UnifiedTestResults(..., summary=TestSummary(failed=1))
except Exception as e:
    logger.error(f"Test execution failed: {e}")
    return error_result
```

---

## Checklist for Phase 2

### DETECT Tasks
- [ ] DETECT-001: pytest detection (check pyproject.toml, tests/, conftest.py)
- [ ] DETECT-002: jest/vitest detection (check package.json, config files)
- [ ] DETECT-003: cargo/mocha detection (check Cargo.toml, mocha config)
- [ ] DETECT-004: Add caching (1 hour cache, thread-safe)
- [ ] DETECT-TEST-001: Create unit tests (mock framework indicators)

### RUN Tasks
- [ ] RUN-001: pytest execution (pytest --json-report)
- [ ] RUN-002: jest/vitest execution (jest --json, vitest run)
- [ ] RUN-003: cargo/mocha execution (cargo test, mocha --json)
- [ ] RUN-004: async/parallel execution (asyncio worker pool)
- [ ] RUN-005: timeout/error handling (300s default timeout)
- [ ] RUN-TEST-001: test_runner unit tests
- [ ] RUN-TEST-002: pytest integration (real pytest project)
- [ ] RUN-TEST-003: jest integration (real jest project)

### Testing
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Type checking with mypy passes
- [ ] Code style with black/ruff passes

---

## Start Here (Next Steps)

1. **Mark task as in_progress:**
   ```bash
   mcp__coderef_workflow__update_task_status(
     project_path="C:\Users\willh\.mcp-servers",
     feature_name="coeref-testing",
     task_id="DETECT-001",
     status="in_progress"
   )
   ```

2. **Create src/framework_detector.py** (~200 lines)
   - Implement detect_pytest(), detect_jest(), etc.
   - Add get_version() for version extraction
   - Add caching with 1-hour TTL
   - Return FrameworkDetectionResult

3. **Update server.py handlers** for discovery
   - handle_discover_tests() → call framework_detector
   - handle_list_frameworks() → call framework_detector

4. **Mark DETECT-001 as completed:**
   ```bash
   mcp__coderef_workflow__update_task_status(
     project_path="C:\Users\willh\.mcp-servers",
     feature_name="coeref-testing",
     task_id="DETECT-001",
     status="completed"
   )
   ```

5. **Continue to DETECT-002** → DETECT-003 → ... → DETECT-TEST-001

6. **Then RUN tasks** → Implementation of test_runner.py

---

## Reference Files in This Project

| File | Purpose | Lines |
|------|---------|-------|
| CLAUDE.md | Project overview | 347 |
| TESTING_GUIDE.md | Vision & architecture | 502 |
| plan.json | Full 37-task plan | ~1,200 |
| AGENT_IMPLEMENTATION_STATUS.md | Phase breakdown | ~365 |
| AGENT_CONTINUATION_INSTRUCTIONS.md | Detailed next steps | ~300 |
| server.py | MCP server skeleton | 350 |
| src/models.py | Pydantic schemas | 622 |
| pyproject.toml | Dependencies | 87 |

**Total Phase 1 code:** ~1,400 lines of foundation

---

## Success = All 13 Tasks Complete

When Phase 2 is done:
- ✅ All 5 frameworks detected correctly
- ✅ Tests execute with normalized results
- ✅ Parallel execution works
- ✅ All 13 tests passing
- ✅ Ready for Phase 3 (Result Processing)

**Estimated Time:** 8-10 hours of focused implementation

Now go create DETECT-001! 🚀
