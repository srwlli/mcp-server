# coderef-testing Components

## Purpose

This document provides detailed technical documentation for each component in the coderef-testing system, including implementation details, design decisions, and integration points.

## Overview

coderef-testing consists of 6 core components plus an MCP server layer:

1. **server.py** - MCP protocol handler
2. **framework_detector.py** - Test framework auto-detection
3. **test_runner.py** - Test execution engine
4. **test_aggregator.py** - Result normalization and archival
5. **result_analyzer.py** - Analysis and metrics
6. **test_coordinator.py** - Multi-project orchestration
7. **models.py** - Data schemas

---

## 1. MCP Server (server.py)

### Purpose
Entry point for MCP protocol, registers and routes tool calls to appropriate handlers.

### Responsibilities
- Register 14 MCP tools across 4 categories
- Parse incoming tool requests
- Route to handler functions
- Return formatted responses

### Implementation

**Tool Registration:**
```python
DISCOVERY_TOOLS = [
    {"name": "discover_tests", "description": "...", "inputSchema": {...}},
    {"name": "list_test_frameworks", "description": "...", "inputSchema": {...}}
]

EXECUTION_TOOLS = [
    {"name": "run_all_tests", ...},
    {"name": "run_test_file", ...},
    {"name": "run_test_category", ...},
    {"name": "run_tests_in_parallel", ...}
]

MANAGEMENT_TOOLS = [
    {"name": "get_test_results", ...},
    {"name": "aggregate_results", ...},
    {"name": "generate_test_report", ...},
    {"name": "compare_test_runs", ...}
]

ANALYSIS_TOOLS = [
    {"name": "analyze_coverage", ...},
    {"name": "detect_flaky_tests", ...},
    {"name": "analyze_test_performance", ...},
    {"name": "validate_test_health", ...}
]

ALL_TOOLS = DISCOVERY_TOOLS + EXECUTION_TOOLS + MANAGEMENT_TOOLS + ANALYSIS_TOOLS
```

**Request Routing:**
```python
@server.call_tool()
async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "discover_tests":
            return await handle_discover_tests(arguments)
        elif name == "run_all_tests":
            return await handle_run_all_tests(arguments)
        # ... 12 more handlers
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### Design Decisions

**Why async handlers?**
- Test execution can take minutes
- Async prevents blocking on long-running tests
- Enables concurrent tool calls

**Why separate DISCOVERY/EXECUTION/MANAGEMENT/ANALYSIS?**
- Clear separation of concerns
- Easier to maintain and extend
- Logical grouping for users

### Integration Points
- **Imports:** FrameworkDetector, TestRunner, TestAggregator, ResultAnalyzer, TestCoordinator
- **Outputs:** JSON responses via MCP TextContent
- **Configuration:** Logging level, server name

### Testing
```bash
# Manual testing
python server.py

# Integration tests (via MCP client)
pytest tests/integration/test_mcp_tools.py -v
```

---

## 2. Framework Detector (framework_detector.py)

### Purpose
Auto-detect test frameworks (pytest, jest, vitest, cargo, mocha) by scanning project structure.

### Responsibilities
- Scan project for framework indicators
- Extract framework versions
- Return FrameworkDetectionResult with metadata

### Implementation

**Detection Strategy:**

**Pytest Detection:**
```python
def detect_pytest(project_path: Path) -> Optional[FrameworkInfo]:
    # Check for pyproject.toml with [tool.pytest] section
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if "[tool.pytest" in content or "pytest" in content:
            version = extract_pytest_version(project_path)
            return FrameworkInfo(
                framework=TestFramework.PYTEST,
                version=version,
                config_file=str(pyproject),
                detected_at=datetime.utcnow()
            )

    # Check for tests/ directory with conftest.py
    tests_dir = project_path / "tests"
    if tests_dir.exists() and (tests_dir / "conftest.py").exists():
        return FrameworkInfo(framework=TestFramework.PYTEST, ...)

    return None
```

**Jest/Vitest Detection:**
```python
def detect_jest_vitest(project_path: Path) -> Optional[FrameworkInfo]:
    # Check package.json for jest/vitest dependencies
    package_json = project_path / "package.json"
    if not package_json.exists():
        return None

    data = json.loads(package_json.read_text())
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

    if "jest" in deps or "@jest/globals" in deps:
        return FrameworkInfo(framework=TestFramework.JEST, ...)
    if "vitest" in deps:
        return FrameworkInfo(framework=TestFramework.VITEST, ...)

    # Check for config files
    if (project_path / "jest.config.js").exists():
        return FrameworkInfo(framework=TestFramework.JEST, ...)
    if (project_path / "vitest.config.ts").exists():
        return FrameworkInfo(framework=TestFramework.VITEST, ...)

    return None
```

**Cargo Detection:**
```python
def detect_cargo(project_path: Path) -> Optional[FrameworkInfo]:
    cargo_toml = project_path / "Cargo.toml"
    if not cargo_toml.exists():
        return None

    content = cargo_toml.read_text()

    # Check for [dev-dependencies] or tests/ directory
    if "[dev-dependencies]" in content or (project_path / "tests").exists():
        version = extract_cargo_version()
        return FrameworkInfo(
            framework=TestFramework.CARGO,
            version=version,
            config_file=str(cargo_toml)
        )

    return None
```

**Version Extraction:**
```python
def extract_pytest_version(project_path: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--version"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Parse "pytest 7.4.3" from output
        match = re.search(r"pytest\s+([\d.]+)", result.stdout)
        return match.group(1) if match else None
    except Exception:
        return None
```

### Design Decisions

**Why multiple detection methods?**
- Projects may have unconventional setups
- Increases detection accuracy
- Fallback strategies prevent false negatives

**Why extract versions?**
- Version-specific behavior (e.g., pytest JSON format changed in 7.x)
- Compatibility checks
- Debugging framework issues

**Why detect_at timestamp?**
- Track when framework was detected
- Useful for caching (re-detect if project modified)

### Integration Points
- **Called by:** server.py (discover_tests, list_test_frameworks)
- **Used by:** test_runner.py (auto-detect before execution)
- **Returns:** FrameworkDetectionResult

### Testing
```bash
# Unit tests
pytest tests/unit/test_framework_detector.py -v

# Test coverage: 27+ tests for all frameworks
```

---

## 3. Test Runner (test_runner.py)

### Purpose
Execute tests using detected framework with async/parallel support.

### Responsibilities
- Build framework-specific test commands
- Execute subprocess with timeout
- Capture stdout/stderr
- Parse framework-native output
- Return UnifiedTestResults

### Implementation

**Core Execution Flow:**
```python
class TestRunner:
    async def run_tests(self, request: TestRunRequest) -> UnifiedTestResults:
        # 1. Detect framework if not specified
        if not request.framework:
            detection = await self.detect_framework(request.project_path)
            framework = detection.frameworks[0].framework
        else:
            framework = request.framework

        # 2. Build command
        command = self.build_command(framework, request)

        # 3. Execute with timeout
        stdout, stderr, returncode = await self.execute_subprocess(
            command, request.project_path, request.timeout
        )

        # 4. Parse results
        raw_results = self.parse_output(framework, stdout, stderr)

        # 5. Normalize to UnifiedTestResults
        return self.normalize_results(framework, raw_results, request.project_path)
```

**Command Building:**

**Pytest:**
```python
def build_pytest_command(self, request: TestRunRequest) -> List[str]:
    cmd = ["python", "-m", "pytest"]

    # Add parallel workers
    if request.parallel_workers and request.parallel_workers > 1:
        cmd.extend(["-n", str(request.parallel_workers)])

    # Add JSON output
    cmd.extend(["--json-report", "--json-report-file=.pytest-results.json"])

    # Add test pattern if specified
    if request.test_pattern:
        cmd.append(f"-k {request.test_pattern}")
    else:
        cmd.append("tests/")

    return cmd
```

**Jest/Vitest:**
```python
def build_jest_command(self, request: TestRunRequest) -> List[str]:
    cmd = ["npm", "test", "--"]

    # Add parallel workers
    if request.parallel_workers:
        cmd.extend(["--maxWorkers", str(request.parallel_workers)])

    # Add JSON output
    cmd.append("--json")

    # Add test pattern
    if request.test_pattern:
        cmd.append(request.test_pattern)

    return cmd
```

**Cargo:**
```python
def build_cargo_command(self, request: TestRunRequest) -> List[str]:
    cmd = ["cargo", "test"]

    # Cargo doesn't support parallelization flag (always parallel by default)

    # Add JSON output
    cmd.extend(["--message-format=json"])

    # Add test pattern
    if request.test_pattern:
        cmd.append(request.test_pattern)

    return cmd
```

**Async Subprocess Execution:**
```python
async def execute_subprocess(
    self, command: List[str], cwd: Path, timeout: int
) -> Tuple[str, str, int]:
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait with timeout
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        return (
            stdout.decode("utf-8"),
            stderr.decode("utf-8"),
            process.returncode
        )

    except asyncio.TimeoutError:
        process.kill()
        raise TimeoutError(f"Test execution exceeded {timeout}s timeout")
```

**Result Parsing:**

**Pytest JSON:**
```python
def parse_pytest_json(self, stdout: str) -> List[TestResult]:
    results_file = Path(".pytest-results.json")
    if not results_file.exists():
        raise ParseError("pytest JSON report not generated")

    data = json.loads(results_file.read_text())

    tests = []
    for test in data.get("tests", []):
        tests.append(TestResult(
            name=test["nodeid"],
            status=TestStatus(test["outcome"]),  # passed/failed/skipped
            duration=test["duration"],
            file=test.get("file"),
            line=test.get("lineno"),
            error_message=test.get("call", {}).get("longrepr")
        ))

    return tests
```

**Jest JSON:**
```python
def parse_jest_json(self, stdout: str) -> List[TestResult]:
    data = json.loads(stdout)

    tests = []
    for test_result in data.get("testResults", []):
        for assertion in test_result.get("assertionResults", []):
            tests.append(TestResult(
                name=assertion["fullName"],
                status=TestStatus(assertion["status"]),
                duration=assertion["duration"] / 1000.0,  # ms → s
                file=test_result["name"],
                error_message=assertion.get("failureMessages", [None])[0]
            ))

    return tests
```

### Design Decisions

**Why async execution?**
- Non-blocking during long test runs
- Enables concurrent test execution across multiple projects
- Better resource utilization

**Why subprocess instead of direct imports?**
- Framework agnostic (works with any language)
- Isolation prevents dependency conflicts
- Matches actual CI/CD execution

**Why JSON output?**
- Structured, parseable results
- All major frameworks support JSON
- Easier than parsing text output

**Why timeout enforcement?**
- Prevents hung tests
- Ensures predictable execution
- Configurable per use case

### Integration Points
- **Called by:** server.py (run_all_tests, run_test_file, etc.)
- **Uses:** FrameworkDetector (for auto-detection)
- **Returns:** UnifiedTestResults
- **Writes:** Temporary result files (.pytest-results.json)

### Testing
```bash
# Unit tests
pytest tests/unit/test_test_runner.py -v

# Integration tests (pytest)
pytest tests/integration/test_pytest_execution.py -v

# Integration tests (jest)
pytest tests/integration/test_jest_execution.py -v
```

---

## 4. Test Aggregator (test_aggregator.py)

### Purpose
Normalize framework-specific results into unified schema and archive with timestamps.

### Responsibilities
- Normalize TestResult lists → UnifiedTestResults
- Calculate summary statistics
- Archive results with ISO 8601 timestamps
- Support export (JSON/CSV/HTML)

### Implementation

**Normalization:**
```python
def aggregate_results(
    self,
    tests: List[TestResult],
    framework: FrameworkInfo,
    project_path: str
) -> UnifiedTestResults:
    # Calculate summary
    summary = self.calculate_summary(tests)

    # Extract coverage if available
    coverage = self.extract_coverage(tests)

    # Build unified result
    return UnifiedTestResults(
        project=project_path,
        framework=framework,
        summary=summary,
        tests=tests,
        coverage=coverage,
        timestamp=datetime.utcnow(),
        environment=self.get_environment_info()
    )
```

**Summary Calculation:**
```python
def calculate_summary(self, tests: List[TestResult]) -> TestSummary:
    total = len(tests)
    passed = sum(1 for t in tests if t.status == TestStatus.PASSED)
    failed = sum(1 for t in tests if t.status == TestStatus.FAILED)
    skipped = sum(1 for t in tests if t.status == TestStatus.SKIPPED)
    errors = sum(1 for t in tests if t.status == TestStatus.ERROR)
    duration = sum(t.duration for t in tests)

    # Calculate success rate
    runnable = total - skipped
    success_rate = (passed / runnable * 100.0) if runnable > 0 else 100.0

    return TestSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration=duration,
        success_rate=success_rate
    )
```

**Archival:**
```python
def archive_results(self, results: UnifiedTestResults) -> Path:
    # Create directory: coderef/testing/results/{date}/
    date_str = results.timestamp.strftime("%Y-%m-%d")
    time_str = results.timestamp.strftime("%H-%M-%S")

    archive_dir = Path("coderef/testing/results") / date_str
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON file
    result_file = archive_dir / f"{time_str}.json"
    result_file.write_text(results.model_dump_json(indent=2))

    logger.info(f"Archived results to {result_file}")
    return result_file
```

**Export Formats:**

**JSON Export:**
```python
def export_json(self, results: UnifiedTestResults) -> str:
    return results.model_dump_json(indent=2)
```

**CSV Export:**
```python
def export_csv(self, results: UnifiedTestResults) -> str:
    rows = [["name", "status", "duration", "file", "line"]]

    for test in results.tests:
        rows.append([
            test.name,
            test.status.value,
            f"{test.duration:.3f}",
            test.file or "",
            str(test.line) if test.line else ""
        ])

    return "\n".join(",".join(row) for row in rows)
```

**HTML Export:**
```python
def export_html(self, results: UnifiedTestResults) -> str:
    template = """
    <html>
    <head><title>Test Report</title></head>
    <body>
        <h1>Test Report: {{project}}</h1>
        <p>Framework: {{framework}}</p>
        <p>Success Rate: {{success_rate}}%</p>
        <table>
            <tr><th>Test</th><th>Status</th><th>Duration</th></tr>
            {% for test in tests %}
            <tr>
                <td>{{test.name}}</td>
                <td>{{test.status}}</td>
                <td>{{test.duration}}s</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    # Render with Jinja2 or simple string replacement
    return render_template(template, results)
```

### Design Decisions

**Why ISO 8601 timestamps?**
- International standard
- Sortable chronologically
- Avoids timezone ambiguity

**Why archive by date?**
- Easier to find results (browse by day)
- Automatic cleanup (delete old date directories)
- Supports multiple runs per day

**Why Pydantic models?**
- Automatic validation
- Type safety
- JSON serialization built-in

### Integration Points
- **Called by:** test_runner.py (after parsing)
- **Uses:** UnifiedTestResults model
- **Writes:** coderef/testing/results/{date}/{time}.json

### Testing
```bash
pytest tests/unit/test_aggregator.py -v
```

---

## 5. Result Analyzer (result_analyzer.py)

### Purpose
Analyze test results for coverage, performance, flakiness, and overall health.

### Responsibilities
- Coverage analysis (identify gaps)
- Performance analysis (find slow tests)
- Flaky test detection (track intermittent failures)
- Health scoring (0-100 grade)

### Implementation

**Coverage Analysis:**
```python
def analyze_coverage(self, results: UnifiedTestResults) -> TestAnalysisResult:
    if not results.coverage:
        return TestAnalysisResult(
            analysis_type="coverage",
            result_key="coverage_percent",
            result_value=0.0,
            details={"error": "No coverage data available"}
        )

    coverage_percent = results.coverage.coverage_percent
    missing_lines = results.coverage.missing_lines or []

    recommendations = []
    if coverage_percent < 80:
        recommendations.append(f"Improve coverage from {coverage_percent}% to 80%")
    if missing_lines:
        recommendations.append(f"Cover {len(missing_lines)} missing lines")

    return TestAnalysisResult(
        analysis_type="coverage",
        result_key="coverage_percent",
        result_value=coverage_percent,
        details={
            "covered_lines": results.coverage.covered_lines,
            "total_lines": results.coverage.total_lines,
            "missing_lines": missing_lines
        },
        recommendations=recommendations
    )
```

**Performance Analysis:**
```python
def analyze_performance(
    self, results: UnifiedTestResults, threshold: float = 1.0
) -> TestAnalysisResult:
    durations = [t.duration for t in results.tests]

    # Calculate percentiles
    p50 = percentile(durations, 50)
    p95 = percentile(durations, 95)
    p99 = percentile(durations, 99)

    # Find slow tests
    slow_tests = [
        {"name": t.name, "duration": t.duration, "file": t.file}
        for t in results.tests
        if t.duration > threshold
    ]

    recommendations = []
    for test in slow_tests[:5]:  # Top 5
        recommendations.append(
            f"Optimize {test['name']} ({test['duration']:.2f}s)"
        )

    return TestAnalysisResult(
        analysis_type="performance",
        result_key="avg_duration",
        result_value=sum(durations) / len(durations),
        details={
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "slow_tests": slow_tests,
            "total_duration": results.summary.duration
        },
        recommendations=recommendations
    )
```

**Flaky Test Detection:**
```python
def detect_flaky(
    self, historical_results: List[UnifiedTestResults]
) -> TestAnalysisResult:
    # Track pass/fail patterns per test
    test_patterns: Dict[str, List[TestStatus]] = {}

    for result in historical_results:
        for test in result.tests:
            if test.name not in test_patterns:
                test_patterns[test.name] = []
            test_patterns[test.name].append(test.status)

    # Calculate flakiness (failures / total runs)
    flaky_tests = []
    for test_name, statuses in test_patterns.items():
        failures = sum(1 for s in statuses if s == TestStatus.FAILED)
        total_runs = len(statuses)
        flakiness_score = failures / total_runs

        if flakiness_score > 0.1 and flakiness_score < 1.0:  # 10%-99%
            flaky_tests.append({
                "name": test_name,
                "flakiness_score": flakiness_score,
                "failures": failures,
                "total_runs": total_runs
            })

    recommendations = []
    for test in sorted(flaky_tests, key=lambda t: t["flakiness_score"], reverse=True)[:5]:
        recommendations.append(
            f"Fix {test['name']} - fails {test['flakiness_score']*100:.0f}% of time"
        )

    return TestAnalysisResult(
        analysis_type="flaky",
        result_key="flaky_test_count",
        result_value=len(flaky_tests),
        details={"flaky_tests": flaky_tests},
        recommendations=recommendations
    )
```

**Health Scoring:**
```python
def validate_health(self, results: UnifiedTestResults) -> TestAnalysisResult:
    # Score components (0-100 each)
    success_rate = results.summary.success_rate
    coverage = results.coverage.coverage_percent if results.coverage else 0.0

    # Speed score (inverted - faster is better)
    avg_duration = results.summary.duration / results.summary.total
    speed_score = max(0, 100 - (avg_duration * 100))  # 1s = 0 score, 0s = 100 score

    # Stability score (assume 100% if no historical data)
    stability = 100.0

    # Weighted average
    health_score = (
        0.4 * success_rate +
        0.3 * coverage +
        0.2 * speed_score +
        0.1 * stability
    )

    # Assign grade
    if health_score >= 90:
        grade = "A"
    elif health_score >= 80:
        grade = "B"
    elif health_score >= 70:
        grade = "C"
    elif health_score >= 60:
        grade = "D"
    else:
        grade = "F"

    recommendations = []
    if success_rate < 100:
        recommendations.append(f"Fix {results.summary.failed} failing tests")
    if coverage < 80:
        recommendations.append(f"Improve coverage to 80% (currently {coverage:.1f}%)")
    if avg_duration > 0.1:
        recommendations.append(f"Optimize slow tests (avg {avg_duration:.2f}s)")

    return TestAnalysisResult(
        analysis_type="health",
        result_key="health_score",
        result_value=health_score,
        details={
            "grade": grade,
            "success_rate": success_rate,
            "coverage": coverage,
            "avg_speed": avg_duration,
            "stability": stability,
            "breakdown": {
                "correctness": 0.4 * success_rate,
                "coverage": 0.3 * coverage,
                "speed": 0.2 * speed_score,
                "stability": 0.1 * stability
            }
        },
        recommendations=recommendations
    )
```

### Design Decisions

**Why weighted health scoring?**
- Correctness (40%) is most important
- Coverage (30%) prevents regressions
- Speed (20%) improves developer experience
- Stability (10%) reduces flakiness

**Why percentile metrics (p50, p95, p99)?**
- Average can be skewed by outliers
- p95/p99 show worst-case performance
- Industry standard for performance analysis

**Why 10% flakiness threshold?**
- < 10%: Likely environment issues (tolerable)
- > 10%: Indicates test design problem (needs fixing)
- 100%: Always fails (not flaky, just broken)

### Integration Points
- **Called by:** server.py (analyze_coverage, detect_flaky_tests, etc.)
- **Uses:** UnifiedTestResults, historical results from archive
- **Returns:** TestAnalysisResult

### Testing
```bash
pytest tests/unit/test_analyzer.py -v
```

---

## 6. Test Coordinator (test_coordinator.py)

### Purpose
Orchestrate test execution across multiple projects with resource management.

### Responsibilities
- Run tests on multiple projects simultaneously
- Manage resource allocation (CPU, memory)
- Aggregate results across projects
- Handle cross-project dependencies

### Implementation

**Multi-Project Execution:**
```python
class TestCoordinator:
    async def run_multi_project(
        self, project_paths: List[str], max_concurrent: int = 4
    ) -> Dict[str, UnifiedTestResults]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_single_project(path: str) -> Tuple[str, UnifiedTestResults]:
            async with semaphore:
                runner = TestRunner()
                request = TestRunRequest(project_path=path)
                result = await runner.run_tests(request)
                return (path, result)

        tasks = [run_single_project(path) for path in project_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {path: result for path, result in results if not isinstance(result, Exception)}
```

**Resource Management:**
```python
def allocate_workers(
    self, total_workers: int, project_count: int
) -> Dict[str, int]:
    # Distribute workers evenly across projects
    base_workers = total_workers // project_count
    remainder = total_workers % project_count

    allocation = {}
    for i, project in enumerate(projects):
        # Give extra workers to first projects
        workers = base_workers + (1 if i < remainder else 0)
        allocation[project] = max(1, workers)  # At least 1 worker per project

    return allocation
```

### Design Decisions

**Why semaphore for concurrency control?**
- Prevents resource exhaustion
- Configurable max concurrent projects
- Graceful degradation under load

**Why aggregate across projects?**
- Single view of entire codebase health (monorepos, multi-server systems)
- Compare test quality across projects
- Identify cross-project issues

### Integration Points
- **Called by:** server.py (for multi-project operations)
- **Uses:** TestRunner (one per project)
- **Returns:** Dictionary of UnifiedTestResults per project

### Testing
```bash
pytest tests/unit/test_coordinator.py -v
```

---

## 7. Data Models (models.py)

### Purpose
Define Pydantic schemas for all data structures used across components.

### Key Models

**UnifiedTestResults:**
- Main result container
- Framework-agnostic schema
- Used by all components

**TestResult:**
- Individual test result
- Status, duration, file, line, error message

**TestSummary:**
- Aggregated statistics
- Total, passed, failed, skipped, success rate

**FrameworkInfo:**
- Framework metadata
- Framework type, version, config file, detected_at

**TestRunRequest:**
- Test execution parameters
- Project path, framework, workers, timeout

**TestAnalysisResult:**
- Analysis output
- Type, key metric, value, details, recommendations

### Design Decisions

**Why Pydantic?**
- Automatic validation
- JSON serialization
- Type hints for IDE support
- Field descriptions for documentation

**Why enums for status/framework?**
- Type safety
- Prevents invalid values
- Clear contract for consumers

### Testing
```bash
pytest tests/unit/test_models.py -v
```

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) - High-level architecture
- [API.md](API.md) - MCP tool reference
- [SCHEMA.md](SCHEMA.md) - Data model schemas
- [README.md](../../README.md) - User guide

---

*Generated: 2025-12-27*
*Version: 1.0.0*
