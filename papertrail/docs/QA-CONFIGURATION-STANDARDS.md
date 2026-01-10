# QA Configuration Standards

**Purpose:** Reusable QA patterns extracted from coderef ecosystem projects
**Audience:** MCP server developers, Python package maintainers
**Source:** Extracted from coderef-context (Phase 8 migration)

---

## Overview

This document captures proven QA configuration patterns from production MCP servers. Use these templates when creating new projects or standardizing existing ones.

---

## pytest Configuration Template

### Recommended `pytest.ini` Structure

```ini
[pytest]
# Test discovery - standard Python test patterns
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Async test support - critical for MCP servers
asyncio_mode = auto

# Output options - strict validation, readable failures
addopts =
    -v                    # Verbose output
    --strict-markers      # Fail on unregistered markers
    --tb=short            # Short traceback format
    --disable-warnings    # Hide deprecation warnings

# Markers for test categorization
markers =
    asyncio: marks tests as async (deselect with '-m "not asyncio"')
    unit: unit tests (fast, no external dependencies)
    integration: integration tests (require real CLI/services)
    performance: performance/stress tests (slow, optional)
    skip_without_cli: skip if CLI unavailable

# Timeout - prevent hanging tests
timeout = 300           # 5 minutes max per test
timeout_method = thread

# Coverage options (if using pytest-cov)
# --cov=src --cov-report=html --cov-report=term-missing
```

### Key Patterns

1. **Async Support**: `asyncio_mode = auto` - Essential for MCP servers (async tool handlers)
2. **Test Categorization**: Use markers to separate fast unit tests from slow integration tests
3. **Timeout Protection**: 300s timeout prevents hanging in CI/CD pipelines
4. **Strict Markers**: `--strict-markers` catches typos in test decorators

---

## Python Project Configuration Template

### Recommended `pyproject.toml` Dev Dependencies

```toml
[project.optional-dependencies]
dev = [
    # Testing framework
    "pytest>=8.0.0",           # Latest pytest with improved async support
    "pytest-asyncio>=0.23.0",  # Async test support for MCP servers

    # Code quality
    "black>=23.0.0",           # Code formatter (PEP 8 compliant)
    "ruff>=0.1.0",             # Fast linter (replaces flake8, isort, pylint)

    # Optional but recommended
    # "pytest-cov>=4.1.0",     # Coverage reporting
    # "pytest-timeout>=2.1.0", # Timeout support
    # "mypy>=1.5.0",           # Type checking
]
```

### Minimum Version Rationale

| Package | Minimum Version | Why |
|---------|----------------|-----|
| pytest | 8.0.0 | Improved async support, better error messages |
| pytest-asyncio | 0.23.0 | Auto mode support, fixture scope improvements |
| black | 23.0.0 | Stable formatting rules, consistent across projects |
| ruff | 0.1.0 | Fast linting, replaces multiple tools |

---

## Test Marker Usage Patterns

### Marker Definitions

```python
import pytest

# Unit tests - fast, no external dependencies
@pytest.mark.unit
def test_validator_schema_loading():
    """Unit test: Pure logic, no I/O"""
    pass

# Integration tests - requires real services
@pytest.mark.integration
def test_mcp_server_tool_handler():
    """Integration test: Tests full MCP server workflow"""
    pass

# Async tests - MCP tool handlers
@pytest.mark.asyncio
async def test_async_tool_execution():
    """Async test: MCP servers use async handlers"""
    pass

# Performance tests - optional, slow
@pytest.mark.performance
def test_large_codebase_scan():
    """Performance test: Benchmarking, stress testing"""
    pass

# Conditional skip - requires CLI
@pytest.mark.skip_without_cli
def test_cli_integration():
    """Skip if CLI not available (CI environments)"""
    pass
```

### Running Specific Test Categories

```bash
# Run only fast unit tests
pytest -m unit

# Run everything except performance tests
pytest -m "not performance"

# Run integration tests only
pytest -m integration

# Run async tests
pytest -m asyncio
```

---

## Coverage Standards

### Target Metrics

- **Minimum coverage**: 80% for production code
- **Critical validators**: 100% coverage required
- **Test infrastructure**: 90% coverage recommended

### Coverage Configuration

Add to `pytest.ini`:
```ini
[pytest]
# ... other config ...

# Coverage reporting
addopts =
    --cov=papertrail
    --cov=validators
    --cov=test-infrastructure
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

Or run manually:
```bash
pytest --cov=papertrail --cov-report=html --cov-report=term-missing
```

---

## CI/CD Integration Pattern

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run tests
      run: |
        pytest -v --cov=src --cov-report=term-missing

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Linting and Formatting Standards

### Black Configuration

Black is opinionated (no config needed), but you can set line length:

```toml
[tool.black]
line-length = 100
target-version = ['py310']
```

### Ruff Configuration

Ruff replaces flake8, isort, pylint, and more:

```toml
[tool.ruff]
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (black handles this)
]
```

### Running Linters

```bash
# Format code
black papertrail/ validators/ test-infrastructure/

# Lint code
ruff check papertrail/ validators/ test-infrastructure/

# Fix auto-fixable issues
ruff check --fix papertrail/
```

---

## MCP Server Specific Patterns

### Async Test Fixture Pattern

```python
import pytest
from mcp.server import Server

@pytest.fixture
async def mcp_server():
    """Fixture for testing MCP server tools"""
    server = Server("test-server")
    # Setup
    yield server
    # Teardown

@pytest.mark.asyncio
async def test_tool_handler(mcp_server):
    """Test MCP tool handler execution"""
    result = await mcp_server.call_tool("validate_plan", {"plan": {}})
    assert result is not None
```

### Integration Test Pattern (CLI Required)

```python
import pytest
import subprocess
import shutil

@pytest.mark.integration
@pytest.mark.skip_without_cli
def test_cli_integration():
    """Test integration with external CLI"""
    if not shutil.which("coderef"):
        pytest.skip("coderef CLI not available")

    result = subprocess.run(
        ["coderef", "scan", "/path/to/project"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
```

---

## Applying These Standards to New Projects

### Checklist

- [ ] Copy `pytest.ini` template to project root
- [ ] Add dev dependencies to `pyproject.toml`
- [ ] Define test markers (`unit`, `integration`, `asyncio`, etc.)
- [ ] Set up coverage reporting (80% minimum)
- [ ] Configure Black and Ruff for code quality
- [ ] Add GitHub Actions workflow for CI/CD
- [ ] Document project-specific markers in `README.md`

### Quick Setup Commands

```bash
# Create pytest.ini from template
cp /path/to/this/template pytest.ini

# Install dev dependencies
pip install -e ".[dev]"

# Run full test suite
pytest -v

# Check coverage
pytest --cov=src --cov-report=html

# Format and lint
black .
ruff check .
```

---

## Pattern Evolution

These patterns are **living standards** - they should evolve as the ecosystem grows.

**How to propose changes:**
1. Test pattern in your project
2. Document results (coverage improvement, CI speed, etc.)
3. Update this document with new recommendations
4. Notify other MCP server maintainers

---

## References

- **Source project**: coderef-context (production MCP server)
- **Extracted**: 2026-01-04 (Phase 8 migration)
- **pytest docs**: https://docs.pytest.org/
- **Black docs**: https://black.readthedocs.io/
- **Ruff docs**: https://docs.astral.sh/ruff/

---

**Last Updated:** 2026-01-04
**Maintained by:** Papertrail QA Team
**Version:** 1.0.0
