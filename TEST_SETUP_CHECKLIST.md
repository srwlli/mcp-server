# Test Setup Checklist: Step-by-Step Implementation

**Purpose:** Quick reference for setting up professional tests in any server

---

## Quick Start (5 minutes)

### Step 1: Create Test Directory Structure
```bash
cd {server}

# Create directories
mkdir -p tests/{unit,integration,smoke,performance,security,proofs,fixtures}
mkdir -p coderef/proofs

# Create __init__.py files
touch tests/__init__.py
touch tests/fixtures/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/smoke/__init__.py
touch tests/performance/__init__.py
touch tests/security/__init__.py
touch tests/proofs/__init__.py
```

### Step 2: Copy Configuration Files

**Copy from coderef-workflow (best example):**

```bash
# Copy conftest.py
cp ..\coderef-workflow\tests\conftest.py tests\conftest.py

# Copy pytest.ini
cat > pytest.ini << 'EOF'
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (component interaction)
    smoke: Smoke tests (sanity checks)
    performance: Performance benchmarks
    security: Security validation
    proof: Real data proof tests
    asyncio: Async tests

addopts = -v --tb=short --strict-markers -ra
timeout = 30
asyncio_mode = auto
EOF

# Copy coverage config
cat > .coveragerc << 'EOF'
[run]
source = src
omit = */tests/*, */fixtures/*

[report]
fail_under = 85
precision = 2

[html]
directory = htmlcov
EOF
```

### Step 3: Create Test Documentation
```bash
cat > TEST_DOCUMENTATION.md << 'EOF'
# {Server Name} Test Strategy

## Test Categories

### Unit Tests (tests/unit/)
- Fast, isolated, mocked
- Coverage: 90%+

### Integration Tests (tests/integration/)
- Component interaction
- Coverage: 80%+

### Smoke Tests (tests/smoke/)
- Sanity checks
- Run before full suite

### Proof Tests (tests/proofs/)
- Real data validation
- Evidence of functionality

## Running Tests

# All tests
pytest tests/ -v --cov=src

# Specific category
pytest tests/unit/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
EOF
```

---

## Detailed Setup (20 minutes)

### Step 1: Unit Test Template
Create `tests/unit/test_basic.py`:

```python
"""
Unit tests for {server name}.

Category: Unit (Fast, Isolated, Mocked)
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestBasicFunctionality:
    """Unit tests for basic functionality."""

    def test_module_imports(self):
        """WHAT IT PROVES: Module can be imported without errors"""
        from src import server
        assert server is not None

    def test_class_instantiation(self):
        """WHAT IT PROVES: Main class instantiates correctly"""
        from src.server import MainClass
        obj = MainClass()
        assert obj is not None

    def test_method_exists(self):
        """WHAT IT PROVES: Expected methods exist with correct signatures"""
        from src.server import MainClass
        obj = MainClass()
        assert hasattr(obj, 'method_name')
        assert callable(obj.method_name)
```

### Step 2: Integration Test Template
Create `tests/integration/test_workflow.py`:

```python
"""
Integration tests for {server name}.

Category: Integration (Component Interaction)
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
class TestComponentInteraction:
    """Integration tests for component interaction."""

    @pytest.mark.asyncio
    async def test_components_work_together(self):
        """
        WHAT IT PROVES:
        - Component A calls Component B
        - Data flows from A to B
        - Result is correct

        ASSERTION:
        - Result matches expected output
        """
        # Setup
        component_a = ComponentA()
        component_b = ComponentB()

        # Execute
        result = await component_a.process(component_b)

        # Assert
        assert result is not None
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_data_flow_through_pipeline(self):
        """
        WHAT IT PROVES:
        - Data flows from input → process → output
        - Data is preserved (no loss)
        - Transformations are correct

        ASSERTION:
        - Output contains input data
        - Transformations applied correctly
        """
        # Setup
        input_data = {"key": "value"}
        pipeline = Pipeline()

        # Execute
        output = await pipeline.process(input_data)

        # Assert
        assert "key" in output
        assert output["key"] == "value"
```

### Step 3: Smoke Test Template
Create `tests/smoke/test_health.py`:

```python
"""
Smoke tests for {server name}.

Category: Smoke (Quick Sanity Checks)
"""

import pytest


@pytest.mark.smoke
class TestServerHealth:
    """Quick sanity checks."""

    def test_imports(self):
        """Can import all main modules"""
        from src import server, utils
        assert server is not None
        assert utils is not None

    def test_server_startup(self):
        """Server starts without errors"""
        from src.server import Server
        server = Server()
        assert server is not None

    def test_tools_registered(self):
        """All expected tools are registered"""
        from src.server import Server
        server = Server()
        tools = server.get_tools()
        assert len(tools) > 0
```

### Step 4: Create Mock Fixtures
Create `tests/fixtures/mock_responses.py`:

```python
"""
Mock response factories for testing.
"""

from typing import Dict, Any


class MockResponse:
    """Base mock response."""

    @staticmethod
    def success(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create successful response"""
        return {
            "status": "success",
            "data": data
        }

    @staticmethod
    def error(message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "message": message
        }


class Mock{ToolName}Response:
    """Mock responses for {tool name}."""

    @staticmethod
    def with_data(count: int = 5) -> Dict[str, Any]:
        """Generate mock response with N items"""
        return {
            "items": [{"id": i, "name": f"item_{i}"} for i in range(count)],
            "total": count
        }

    @staticmethod
    def empty() -> Dict[str, Any]:
        """Generate empty response"""
        return {"items": [], "total": 0}
```

### Step 5: Create Proof Test Template
Create `tests/proofs/test_proof.py`:

```python
"""
Proof tests - validate real functionality with real data.

Category: Proof (Real Data Validation)
"""

import pytest
import json
from pathlib import Path


@pytest.mark.proof
class TestRealFunctionality:
    """Tests that validate real proof artifacts."""

    @pytest.fixture
    def proof_data(self):
        """Load real proof data from workorder"""
        proof_path = Path(__file__).parent.parent.parent / "coderef/workorder/test-feature/plan.json"
        with open(proof_path) as f:
            return json.load(f)

    def test_proof_artifact_exists(self, proof_data):
        """WHAT IT PROVES: Proof artifact is present and valid"""
        assert proof_data is not None
        assert "META_DOCUMENTATION" in proof_data

    def test_real_data_present(self, proof_data):
        """
        WHAT IT PROVES:
        - Real coderef-context output present
        - Data is marked as from real tool
        - Proof of injection evident

        ASSERTION:
        - source_tool field identifies tool
        - timestamp shows when invoked
        - proof_of_injection explains what happened
        """
        section_0 = proof_data.get("0_PREPARATION", {})
        assert "code_inventory" in section_0
        assert section_0.get("source_tool") == "coderef_scan"
        assert "timestamp" in section_0
        assert "proof_of_injection" in section_0

    def test_data_integrity(self, proof_data):
        """WHAT IT PROVES: Data flows from tool to output unchanged"""
        # Check section 2 (Risk Assessment)
        section_2 = proof_data.get("2_RISK_ASSESSMENT", {})
        assert "breaking_changes" in section_2
        assert section_2.get("source_tool") == "coderef_impact"
```

---

## Performance Test Template
Create `tests/performance/test_speed.py`:

```python
"""
Performance tests for {server name}.

Category: Performance (Baseline Measurements)
"""

import pytest


@pytest.mark.performance
class TestPerformance:
    """Performance benchmarks."""

    @pytest.mark.benchmark
    def test_tool_call_latency(self, benchmark):
        """Tool calls should be fast (excluding coderef-context)"""
        from src.client import Client

        def call_tool():
            client = Client()
            return client.call_tool("tool_name", {})

        result = benchmark(call_tool)
        # Assert under 1 second (excluding coderef timeout)
        assert result.stats.mean < 1.0
```

---

## Security Test Template
Create `tests/security/test_validation.py`:

```python
"""
Security tests for {server name}.

Category: Security (Validation & Injection Prevention)
"""

import pytest


@pytest.mark.security
class TestSecurity:
    """Security validation."""

    def test_input_validation(self):
        """Malformed input is rejected"""
        from src.server import validate_input

        with pytest.raises(ValueError):
            validate_input(None)

        with pytest.raises(ValueError):
            validate_input({})

    def test_path_validation(self):
        """Path traversal attacks are prevented"""
        from src.server import validate_path

        # Should reject paths that escape sandbox
        with pytest.raises(ValueError):
            validate_path("../../../../etc/passwd")
```

---

## Running Tests in CI/CD

### GitHub Actions Example
Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-asyncio pytest-cov pytest-benchmark

    - name: Smoke tests
      run: pytest tests/smoke/ -v

    - name: Unit tests
      run: pytest tests/unit/ -v

    - name: Integration tests
      run: pytest tests/integration/ -v

    - name: Coverage report
      run: pytest tests/ --cov=src --cov-report=xml --cov-fail-under=85

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

---

## Creating a Proof Workorder

### Create Test Feature
```bash
# Create workorder directory
mkdir -p coderef/workorder/test-feature-proof
cd coderef/workorder/test-feature-proof

# Create context.json
cat > context.json << 'EOF'
{
  "feature_name": "test-feature-proof",
  "goal": "Demonstrate real {server name} functionality",
  "description": "Test workorder to capture real tool outputs",
  "requirements": [
    "Run complete workflow",
    "Capture real tool outputs",
    "Mark with proof_of_injection"
  ],
  "constraints": [
    "Planning phase only - no execution"
  ]
}
EOF

# After running workflow, you'll have:
# - analysis.json (real tool outputs)
# - plan.json (plan with real data)
# Create PROOF_DOCUMENT.md describing the proof
```

### Create Proof Validation Test
Create `tests/proofs/test_feature_proof.py`:

```python
@pytest.mark.proof
def test_feature_proof():
    """Validate proof artifact for feature"""
    import json
    from pathlib import Path

    proof = json.loads(
        Path("coderef/workorder/test-feature-proof/plan.json").read_text()
    )

    # Proof assertions
    assert proof["META_DOCUMENTATION"]["feature_name"] == "test-feature-proof"
    assert "0_PREPARATION" in proof
    assert proof["0_PREPARATION"]["source_tool"] == "real_tool"
```

---

## Quick Command Reference

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-benchmark

# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/smoke/ -v
pytest tests/proofs/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw tests/ -- -v

# Specific test
pytest tests/unit/test_basic.py::TestBasicFunctionality::test_module_imports -v

# With markers
pytest -m unit -v
pytest -m "integration and not slow" -v

# Benchmark
pytest tests/performance/ -v --benchmark-only

# Parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto
```

---

## Troubleshooting

### Tests won't run
```
# Make sure __init__.py exists in all test directories
find tests -name "__init__.py" -size 0
# Touch empty __init__.py files where missing
```

### Import errors
```
# Make sure src/ has __init__.py
touch src/__init__.py

# Add to conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Async tests fail
```
# Make sure pytest.ini has asyncio_mode = auto
# Make sure tests have @pytest.mark.asyncio
# Make sure conftest.py has asyncio fixture
```

### Coverage too low
```
# Run with detailed report
pytest tests/ --cov=src --cov-report=html

# Open htmlcov/index.html to see what's not covered
# Add tests for uncovered lines

# Check specific file
pytest tests/ --cov=src.specific_module --cov-report=term-missing
```

---

## Completion Checklist

For each server:

- [ ] `tests/` directory created with 7 subdirectories
- [ ] `__init__.py` files in all test directories
- [ ] `conftest.py` with shared fixtures
- [ ] `pytest.ini` with configuration
- [ ] `.coveragerc` with 85% threshold
- [ ] At least 5 unit tests written and passing
- [ ] At least 3 integration tests written and passing
- [ ] 1 smoke test written and passing
- [ ] TEST_DOCUMENTATION.md created
- [ ] First proof test written (loads real data)
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage >= 85%: `pytest tests/ --cov=src --cov-fail-under=85`
- [ ] Ready for CI/CD integration

---

**Once complete, you have professional, enterprise-grade testing setup! 🎯**

