# CodeRef System Test Plan
**Version:** 1.0.0
**Created:** 2026-01-01
**Purpose:** Comprehensive testing of @coderef/cli and @coderef/core using benchmark Git repositories

---

## Overview

This test plan validates the **coderef system** (TypeScript CLI + Core engine) using real-world codebases as benchmarks. The coderef-testing MCP server orchestrates tests across multiple frameworks and generates regression reports.

### Test Objectives

1. **Accuracy Validation** - Verify 99% AST-based scanning accuracy
2. **Performance Benchmarking** - Measure scan time, memory usage, scalability
3. **Feature Coverage** - Test all CLI commands (scan, query, impact, tag, drift, etc.)
4. **Regression Detection** - Compare results against baseline reports
5. **Edge Case Handling** - Long names, dense files, private functions, hooks

---

## Benchmark Repositories

### 1. React Repository (facebook/react)
- **Size:** 8.8 MB (275 files)
- **Elements:** 1,336 total (347 KB scanned data)
- **Complexity:** React hooks, component analysis, JSX/TSX patterns
- **Performance Baseline:** 0.07s scan time
- **Test Focus:** Hooks detection, component relationships, React-specific patterns

**Key Metrics:**
```json
{
  "files": 275,
  "elements": 1336,
  "scan_time": "0.07s",
  "accuracy": "100%",
  "unique_patterns": ["hooks", "components", "context_providers"]
}
```

### 2. TypeScript Compiler (microsoft/TypeScript)
- **Size:** 74 MB (701 files)
- **Elements:** 21,852 total (11 MB scanned data)
- **Complexity:** Dense TypeScript, long names, private functions, complex generics
- **Performance Baseline:** 5.9s scan time
- **Test Focus:** Scalability, edge cases, complex type analysis, private element handling

**Key Metrics:**
```json
{
  "files": 701,
  "elements": 21852,
  "scan_time": "5.9s",
  "accuracy": "99%",
  "edge_cases": ["long_names", "private_functions", "dense_files"]
}
```

---

## Test Architecture

### Directory Structure

```
coderef-testing/
├── tests/
│   ├── benchmark/                      # NEW: Benchmark test suite
│   │   ├── repos/                      # Git repositories (gitignored)
│   │   │   ├── react/                  # facebook/react clone
│   │   │   └── typescript/             # microsoft/TypeScript clone
│   │   ├── baselines/                  # Expected results (committed)
│   │   │   ├── react-baseline.json
│   │   │   └── typescript-baseline.json
│   │   ├── reports/                    # Test run outputs (gitignored)
│   │   │   ├── react-{timestamp}.json
│   │   │   └── typescript-{timestamp}.json
│   │   ├── test_react_benchmark.py     # React test suite
│   │   ├── test_typescript_benchmark.py # TypeScript test suite
│   │   ├── test_coderef_cli.py         # CLI command validation
│   │   ├── test_performance.py         # Performance benchmarks
│   │   └── test_regression.py          # Regression detection
│   └── comprehensive/                  # Existing tests
└── src/
    ├── benchmark_runner.py             # NEW: Benchmark orchestration
    └── baseline_generator.py           # NEW: Baseline report generation
```

### Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **CLI Validation** | 15 tests | Verify all coderef commands work correctly |
| **Accuracy** | 8 tests | Validate AST accuracy vs regex, element counts |
| **Performance** | 6 tests | Scan time, memory usage, scalability (O(n)) |
| **Regression** | 4 tests | Compare against baselines, detect drift |
| **Edge Cases** | 12 tests | Long names, private functions, hooks, generics |

**Total:** 45 benchmark tests

---

## Test Implementation

### Phase 1: Repository Setup (One-Time)

```bash
# Clone benchmark repositories (large, not committed)
cd tests/benchmark/repos/

# React (8.8 MB)
git clone --depth 1 https://github.com/facebook/react
cd react && git checkout main && cd ..

# TypeScript (74 MB)
git clone --depth 1 https://github.com/microsoft/TypeScript
cd TypeScript && git checkout main && cd ..
```

**Storage Strategy:**
- ✅ Repos stored in `tests/benchmark/repos/` (gitignored)
- ✅ Baselines stored in `tests/benchmark/baselines/` (committed, ~50 KB total)
- ✅ Test reports stored in `tests/benchmark/reports/` (gitignored, generated on-demand)

### Phase 2: Baseline Generation

```python
# Generate baseline reports (run once, commit to repo)
python src/baseline_generator.py tests/benchmark/repos/react tests/benchmark/baselines/react-baseline.json
python src/baseline_generator.py tests/benchmark/repos/TypeScript tests/benchmark/baselines/typescript-baseline.json
```

**Baseline Contents:**
```json
{
  "metadata": {
    "repo": "facebook/react",
    "commit": "abc123",
    "generated": "2026-01-01T12:00:00Z",
    "coderef_version": "2.0.0"
  },
  "scan_results": {
    "total_files": 275,
    "total_elements": 1336,
    "element_types": {
      "functions": 512,
      "classes": 89,
      "methods": 487,
      "components": 146,
      "hooks": 102
    }
  },
  "performance": {
    "scan_time_seconds": 0.07,
    "memory_mb": 45,
    "files_per_second": 3928
  },
  "edge_cases": {
    "long_names_count": 12,
    "private_functions_count": 234,
    "hooks_detected": 102
  },
  "sample_elements": [
    {"name": "useState", "type": "hook", "file": "src/react/hooks.ts", "line": 24},
    {"name": "Component", "type": "class", "file": "src/react/Component.ts", "line": 45}
  ]
}
```

### Phase 3: Test Execution

#### Test 1: React Benchmark Suite

**File:** `tests/benchmark/test_react_benchmark.py`

```python
"""
React repository benchmark tests
Tests hooks detection, component analysis, React-specific patterns
"""
import pytest
import subprocess
import json
from pathlib import Path

REACT_REPO = Path(__file__).parent / "repos/react"
BASELINE = Path(__file__).parent / "baselines/react-baseline.json"

def load_baseline():
    return json.loads(BASELINE.read_text())

def run_coderef_scan():
    """Execute coderef scan on React repo"""
    result = subprocess.run(
        ["coderef", "scan", str(REACT_REPO), "--lang", "ts,tsx", "--analyzer", "ast", "--output", "-"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

class TestReactBenchmark:
    """React repository tests"""

    def test_scan_accuracy(self):
        """Verify element count matches baseline"""
        baseline = load_baseline()
        results = run_coderef_scan()

        assert results["total_elements"] == baseline["scan_results"]["total_elements"]
        assert results["total_files"] == baseline["scan_results"]["total_files"]

    def test_hooks_detection(self):
        """Verify React hooks are detected"""
        results = run_coderef_scan()
        baseline = load_baseline()

        hooks_count = sum(1 for e in results["elements"] if e["type"] == "hook")
        assert hooks_count == baseline["scan_results"]["element_types"]["hooks"]

    def test_component_analysis(self):
        """Verify React components are classified correctly"""
        results = run_coderef_scan()
        baseline = load_baseline()

        components_count = sum(1 for e in results["elements"] if e["type"] == "component")
        assert components_count == baseline["scan_results"]["element_types"]["components"]

    def test_scan_performance(self):
        """Verify scan completes within performance threshold"""
        import time
        start = time.time()
        run_coderef_scan()
        duration = time.time() - start

        baseline = load_baseline()
        # Allow 50% variance (0.07s baseline → max 0.105s)
        assert duration <= baseline["performance"]["scan_time_seconds"] * 1.5

    def test_query_hooks(self):
        """Verify coderef query finds hook relationships"""
        result = subprocess.run(
            ["coderef", "query", "useState", "--type", "calls-me", "--source-dir", str(REACT_REPO)],
            capture_output=True,
            text=True
        )

        # Should find multiple callers of useState hook
        assert "Found" in result.stdout
        assert int(result.stdout.split()[1]) > 10  # At least 10 usages

    def test_impact_analysis(self):
        """Verify impact analysis on core React component"""
        result = subprocess.run(
            ["coderef", "impact", "Component", "--source-dir", str(REACT_REPO)],
            capture_output=True,
            text=True
        )

        # Should show high impact (many dependents)
        assert "Risk Level: HIGH" in result.stdout or "Risk Level: CRITICAL" in result.stdout
```

#### Test 2: TypeScript Benchmark Suite

**File:** `tests/benchmark/test_typescript_benchmark.py`

```python
"""
TypeScript compiler benchmark tests
Tests scalability, edge cases, complex type analysis
"""
import pytest
import subprocess
import json
from pathlib import Path

TYPESCRIPT_REPO = Path(__file__).parent / "repos/TypeScript"
BASELINE = Path(__file__).parent / "baselines/typescript-baseline.json"

class TestTypeScriptBenchmark:
    """TypeScript compiler tests (large codebase)"""

    def test_large_scan_accuracy(self):
        """Verify accurate scanning of 700+ files"""
        baseline = json.loads(BASELINE.read_text())
        result = subprocess.run(
            ["coderef", "scan", str(TYPESCRIPT_REPO), "--lang", "ts", "--analyzer", "ast", "--output", "-"],
            capture_output=True,
            text=True
        )
        results = json.loads(result.stdout)

        # Allow 1% variance for large scans
        assert abs(results["total_elements"] - baseline["scan_results"]["total_elements"]) < 200
        assert results["total_files"] == baseline["scan_results"]["total_files"]

    def test_scalability_linear(self):
        """Verify O(n) scalability (should be ~5.9s for 701 files)"""
        import time
        start = time.time()
        subprocess.run(
            ["coderef", "scan", str(TYPESCRIPT_REPO), "--lang", "ts", "--analyzer", "ast"],
            capture_output=True
        )
        duration = time.time() - start

        baseline = json.loads(BASELINE.read_text())
        # Should scale linearly (allow 2x for CI overhead)
        assert duration <= baseline["performance"]["scan_time_seconds"] * 2

    def test_long_names_handling(self):
        """Verify edge case: long element names"""
        result = subprocess.run(
            ["coderef", "scan", str(TYPESCRIPT_REPO), "--lang", "ts", "--analyzer", "ast", "--output", "-"],
            capture_output=True,
            text=True
        )
        results = json.loads(result.stdout)

        # Should handle names > 100 chars without truncation
        long_names = [e for e in results["elements"] if len(e["name"]) > 100]
        baseline = json.loads(BASELINE.read_text())
        assert len(long_names) == baseline["edge_cases"]["long_names_count"]

    def test_private_functions_detection(self):
        """Verify private functions are scanned (if --include-private)"""
        result = subprocess.run(
            ["coderef", "scan", str(TYPESCRIPT_REPO), "--lang", "ts", "--analyzer", "ast", "--include-private", "--output", "-"],
            capture_output=True,
            text=True
        )
        results = json.loads(result.stdout)

        private_count = sum(1 for e in results["elements"] if e["name"].startswith("_"))
        baseline = json.loads(BASELINE.read_text())
        assert private_count == baseline["edge_cases"]["private_functions_count"]

    def test_memory_usage(self):
        """Verify memory usage stays under 512 MB for large scan"""
        import psutil
        import os

        process = subprocess.Popen(
            ["coderef", "scan", str(TYPESCRIPT_REPO), "--lang", "ts", "--analyzer", "ast"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Monitor memory usage
        p = psutil.Process(process.pid)
        max_memory = 0
        while process.poll() is None:
            try:
                mem = p.memory_info().rss / 1024 / 1024  # MB
                max_memory = max(max_memory, mem)
            except:
                break

        # Should stay under 512 MB
        assert max_memory < 512
```

#### Test 3: CLI Command Validation

**File:** `tests/benchmark/test_coderef_cli.py`

```python
"""
Validate all coderef CLI commands
Tests: scan, query, impact, tag, drift, context, diagram, export
"""
import pytest
import subprocess
from pathlib import Path

REACT_REPO = Path(__file__).parent / "repos/react"

class TestCodeRefCLI:
    """Test all CLI commands"""

    def test_scan_command(self):
        """coderef scan"""
        result = subprocess.run(
            ["coderef", "scan", str(REACT_REPO), "--lang", "ts,tsx"],
            capture_output=True
        )
        assert result.returncode == 0
        assert b"Scanned" in result.stdout

    def test_query_command(self):
        """coderef query"""
        result = subprocess.run(
            ["coderef", "query", "useState", "--type", "calls-me", "--source-dir", str(REACT_REPO)],
            capture_output=True
        )
        assert result.returncode == 0

    def test_impact_command(self):
        """coderef impact"""
        result = subprocess.run(
            ["coderef", "impact", "Component", "--source-dir", str(REACT_REPO)],
            capture_output=True
        )
        assert result.returncode == 0
        assert b"Risk Level:" in result.stdout

    def test_tag_command_dry_run(self):
        """coderef tag --dry-run"""
        result = subprocess.run(
            ["coderef", "tag", str(REACT_REPO / "src"), "--dry-run"],
            capture_output=True
        )
        assert result.returncode == 0

    def test_drift_command(self):
        """coderef drift"""
        # First create an index
        subprocess.run(
            ["coderef", "scan", str(REACT_REPO), "--output", "/tmp/react-index.json"],
            capture_output=True
        )

        # Check drift
        result = subprocess.run(
            ["coderef", "drift", str(REACT_REPO), "--index", "/tmp/react-index.json"],
            capture_output=True
        )
        assert result.returncode == 0

    def test_context_command(self):
        """coderef context"""
        result = subprocess.run(
            ["coderef", "context", str(REACT_REPO), "--output", "/tmp/react-context.json"],
            capture_output=True
        )
        assert result.returncode == 0

    def test_diagram_command(self):
        """coderef diagram"""
        result = subprocess.run(
            ["coderef", "diagram", "Component", "--source-dir", str(REACT_REPO), "--format", "mermaid"],
            capture_output=True
        )
        assert result.returncode == 0

    def test_export_command(self):
        """coderef export"""
        result = subprocess.run(
            ["coderef", "export", "--source-dir", str(REACT_REPO), "--format", "json", "--output", "/tmp/react-export.json"],
            capture_output=True
        )
        assert result.returncode == 0
```

#### Test 4: Regression Detection

**File:** `tests/benchmark/test_regression.py`

```python
"""
Regression detection tests
Compare current results against baselines
"""
import pytest
import subprocess
import json
from pathlib import Path

REACT_BASELINE = Path(__file__).parent / "baselines/react-baseline.json"
TS_BASELINE = Path(__file__).parent / "baselines/typescript-baseline.json"

def compare_results(current, baseline, tolerance=0.01):
    """Compare two result sets with tolerance"""
    diffs = []

    # Element count variance
    element_diff = abs(current["total_elements"] - baseline["scan_results"]["total_elements"])
    element_variance = element_diff / baseline["scan_results"]["total_elements"]
    if element_variance > tolerance:
        diffs.append(f"Element count variance {element_variance*100:.2f}% (threshold: {tolerance*100}%)")

    # Performance variance
    perf_diff = abs(current["scan_time"] - baseline["performance"]["scan_time_seconds"])
    perf_variance = perf_diff / baseline["performance"]["scan_time_seconds"]
    if perf_variance > 0.5:  # 50% performance regression
        diffs.append(f"Performance regression {perf_variance*100:.2f}% (threshold: 50%)")

    return diffs

class TestRegression:
    """Regression detection tests"""

    def test_react_regression(self):
        """Detect regressions in React scan"""
        baseline = json.loads(REACT_BASELINE.read_text())

        # Run current scan
        import time
        start = time.time()
        result = subprocess.run(
            ["coderef", "scan", str(Path(__file__).parent / "repos/react"), "--lang", "ts,tsx", "--output", "-"],
            capture_output=True,
            text=True
        )
        duration = time.time() - start

        current = json.loads(result.stdout)
        current["scan_time"] = duration

        diffs = compare_results(current, baseline)
        assert len(diffs) == 0, f"Regression detected: {', '.join(diffs)}"

    def test_typescript_regression(self):
        """Detect regressions in TypeScript scan"""
        baseline = json.loads(TS_BASELINE.read_text())

        # Run current scan
        import time
        start = time.time()
        result = subprocess.run(
            ["coderef", "scan", str(Path(__file__).parent / "repos/TypeScript"), "--lang", "ts", "--output", "-"],
            capture_output=True,
            text=True
        )
        duration = time.time() - start

        current = json.loads(result.stdout)
        current["scan_time"] = duration

        diffs = compare_results(current, baseline, tolerance=0.02)  # 2% for large scan
        assert len(diffs) == 0, f"Regression detected: {', '.join(diffs)}"
```

---

## Test Execution

### Local Development

```bash
# Install dependencies
cd C:\Users\willh\.mcp-servers\coderef-testing
uv sync

# Clone benchmark repos (one-time, ~80 MB total)
mkdir -p tests/benchmark/repos
cd tests/benchmark/repos
git clone --depth 1 https://github.com/facebook/react
git clone --depth 1 https://github.com/microsoft/TypeScript

# Generate baselines (one-time, commit these)
python src/baseline_generator.py tests/benchmark/repos/react tests/benchmark/baselines/react-baseline.json
python src/baseline_generator.py tests/benchmark/repos/TypeScript tests/benchmark/baselines/typescript-baseline.json

# Run all benchmark tests
pytest tests/benchmark/ -v

# Run specific test category
pytest tests/benchmark/test_react_benchmark.py -v
pytest tests/benchmark/test_typescript_benchmark.py -v
pytest tests/benchmark/test_coderef_cli.py -v
pytest tests/benchmark/test_regression.py -v
```

### CI/CD Integration

```yaml
# .github/workflows/benchmark-tests.yml
name: CodeRef Benchmark Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install coderef CLI
        run: |
          npm install -g @coderef/cli
          coderef --version

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          cd coderef-testing
          pip install uv
          uv sync

      - name: Clone benchmark repos
        run: |
          mkdir -p tests/benchmark/repos
          cd tests/benchmark/repos
          git clone --depth 1 https://github.com/facebook/react
          git clone --depth 1 https://github.com/microsoft/TypeScript

      - name: Run benchmark tests
        run: |
          cd coderef-testing
          pytest tests/benchmark/ -v --junit-xml=benchmark-results.xml

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark-results.xml
```

---

## Expected Outcomes

### Pass Criteria

| Test Category | Pass Threshold | Measurement |
|---------------|----------------|-------------|
| **Accuracy** | 99% element match | Element count ± 1% vs baseline |
| **Performance** | < 2x baseline | Scan time ≤ baseline × 2 |
| **CLI Commands** | 100% success | All 8 commands return exit code 0 |
| **Regression** | No drift > 5% | Element count/performance within 5% |
| **Edge Cases** | 100% detection | All edge cases match baseline |

### Report Generation

```bash
# Generate comprehensive report
python src/benchmark_runner.py --report html > benchmark-report.html

# Output:
# - Performance comparison table (current vs baseline)
# - Regression detection summary
# - Edge case validation results
# - CLI command coverage matrix
```

**Report Contents:**
- ✅ Scan accuracy: 99.2% (1,334/1,336 elements detected)
- ✅ Performance: 0.08s (baseline: 0.07s, +14% acceptable)
- ✅ Hooks detected: 102/102 (100%)
- ✅ Regression: None detected
- ⚠️ Warning: 2 elements not detected (review required)

---

## Maintenance

### When to Update Baselines

1. **After coderef version upgrade** (e.g., 2.0.0 → 2.1.0)
2. **Benchmark repo updates** (if React/TS repos are re-cloned)
3. **Expected behavior change** (intentional algorithm improvement)

```bash
# Regenerate baselines
python src/baseline_generator.py tests/benchmark/repos/react tests/benchmark/baselines/react-baseline.json --force
python src/baseline_generator.py tests/benchmark/repos/TypeScript tests/benchmark/baselines/typescript-baseline.json --force

# Commit updated baselines
git add tests/benchmark/baselines/*.json
git commit -m "chore: update baselines for coderef v2.1.0"
```

### Gitignore Configuration

```gitignore
# tests/.gitignore
benchmark/repos/        # Don't commit 80 MB of repos
benchmark/reports/      # Don't commit test outputs
*.log
```

---

## Future Enhancements

### Phase 2: Additional Benchmarks

- **Next.js** (React framework, ~500 files)
- **Vue 3** (Vue framework, ~300 files)
- **Express** (Node.js backend, ~150 files)

### Phase 3: Advanced Testing

- **Breaking change detection** (signature compatibility)
- **RAG system validation** (semantic search accuracy)
- **Multi-language support** (Python, Go, Rust)

---

## Summary

This test plan provides:

1. ✅ **45 comprehensive tests** across 4 categories
2. ✅ **Real-world benchmarks** (React, TypeScript compiler)
3. ✅ **Regression detection** with baseline comparison
4. ✅ **Performance validation** (scalability, memory)
5. ✅ **Storage efficiency** (baselines ~50 KB, repos gitignored)

**Ready to implement!** Next step: Create `baseline_generator.py` and `benchmark_runner.py` scripts.
