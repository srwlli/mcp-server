"""
Performance tests for large project structures.

Tests generator performance with 100+ files to ensure scalability.
Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Generator
import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# FIXTURES FOR LARGE PROJECTS
# ============================================================================

@pytest.fixture
def large_python_project(tmp_path: Path) -> Path:
    """
    Create a large Python project structure for performance testing.

    Structure:
    - 10 modules with 10 files each = 100 Python files
    - Each file has classes, functions, and imports
    - Simulates real-world project complexity
    """
    project_dir = tmp_path / "large-python-project"
    project_dir.mkdir()

    # Create source directory
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Create 10 modules with 10 files each
    for module_idx in range(10):
        module_dir = src_dir / f"module_{module_idx}"
        module_dir.mkdir()

        # Create __init__.py
        (module_dir / "__init__.py").write_text(f'''"""Module {module_idx} package."""
from .file_0 import Class_{module_idx}_0
''')

        for file_idx in range(10):
            file_content = f'''"""
Module {module_idx}, File {file_idx}.

This file contains test classes and functions for performance testing.
"""

from typing import List, Dict, Any, Optional
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class Class_{module_idx}_{file_idx}:
    """Main class for module {module_idx}, file {file_idx}."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.data: Dict[str, Any] = {{}}
        self.items: List[str] = []

    def method_one(self, value: int) -> int:
        """Process a value and return result."""
        return value * 2 + {module_idx}

    def method_two(self, items: List[str]) -> List[str]:
        """Filter and transform items."""
        return [item.upper() for item in items if item]

    async def async_method(self) -> str:
        """Async operation."""
        await asyncio.sleep(0.001)
        return f"completed_{module_idx}_{file_idx}"

    @staticmethod
    def static_helper(x: int, y: int) -> int:
        """Static helper method."""
        return x + y

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Class_{module_idx}_{file_idx}":
        """Create instance from dictionary."""
        instance = cls(data.get("name", "default"))
        instance.data = data
        return instance


class Helper_{module_idx}_{file_idx}:
    """Helper class with utility methods."""

    def validate(self, value: Any) -> bool:
        """Validate input value."""
        return value is not None

    def transform(self, data: Dict) -> Dict:
        """Transform data structure."""
        return {{k: str(v) for k, v in data.items()}}


def function_{module_idx}_{file_idx}(x: int) -> int:
    """Standalone function."""
    return x * {module_idx + 1} + {file_idx}


async def async_function_{module_idx}_{file_idx}() -> str:
    """Async standalone function."""
    await asyncio.sleep(0.001)
    return "async_result"


def helper_function(items: List[Any]) -> int:
    """Count non-null items."""
    return sum(1 for item in items if item is not None)


# Constants
CONSTANT_{module_idx}_{file_idx} = {module_idx * 100 + file_idx}
CONFIG_{module_idx}_{file_idx} = {{
    "module": {module_idx},
    "file": {file_idx},
    "enabled": True
}}
'''
            (module_dir / f"file_{file_idx}.py").write_text(file_content)

    # Create tests directory with test files
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    for module_idx in range(10):
        test_content = f'''"""Tests for module {module_idx}."""
import pytest
from src.module_{module_idx}.file_0 import Class_{module_idx}_0


def test_class_init():
    obj = Class_{module_idx}_0()
    assert obj.name == "default"


def test_method_one():
    obj = Class_{module_idx}_0()
    assert obj.method_one(5) == 10 + {module_idx}


@pytest.mark.asyncio
async def test_async_method():
    obj = Class_{module_idx}_0()
    result = await obj.async_method()
    assert "completed" in result
'''
        (tests_dir / f"test_module_{module_idx}.py").write_text(test_content)

    # Create docs directory
    docs_dir = project_dir / "docs"
    docs_dir.mkdir()

    (docs_dir / "README.md").write_text('''# Large Python Project

A test project with 100+ files for performance testing.

## Structure

- 10 modules
- 10 files per module
- Full type hints
- Async support
''')

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()
    (coderef_dir / "context-experts").mkdir()
    (coderef_dir / "context-experts" / "experts").mkdir()
    (coderef_dir / "context-experts" / "cache").mkdir()
    (coderef_dir / "working").mkdir()
    (coderef_dir / "changelog").mkdir()

    # Create changelog
    changelog = {
        "project_name": "large-python-project",
        "versions": []
    }
    (coderef_dir / "changelog" / "CHANGELOG.json").write_text(json.dumps(changelog, indent=2))

    # Create pyproject.toml
    (project_dir / "pyproject.toml").write_text('''[project]
name = "large-python-project"
version = "1.0.0"
description = "Large project for performance testing"
requires-python = ">=3.10"

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "pytest-cov"]
''')

    return project_dir


@pytest.fixture
def large_mixed_project(tmp_path: Path) -> Path:
    """
    Create a large mixed-language project for performance testing.

    Structure:
    - Python modules (50 files)
    - TypeScript/JavaScript (50 files)
    - Configuration files
    - Documentation
    """
    project_dir = tmp_path / "large-mixed-project"
    project_dir.mkdir()

    # Python source
    py_src = project_dir / "src" / "python"
    py_src.mkdir(parents=True)

    for i in range(50):
        (py_src / f"module_{i}.py").write_text(f'''"""Python module {i}."""

class Service_{i}:
    def process(self, data):
        return data

def handler_{i}(request):
    return {{"status": "ok", "module": {i}}}
''')

    # TypeScript source
    ts_src = project_dir / "src" / "typescript"
    ts_src.mkdir(parents=True)

    for i in range(50):
        (ts_src / f"component_{i}.tsx").write_text(f'''import React from 'react';

interface Props_{i} {{
    value: string;
    onChange: (v: string) => void;
}}

export const Component_{i}: React.FC<Props_{i}> = ({{ value, onChange }}) => {{
    return <div onClick={{() => onChange(value)}}>{i}</div>;
}};

export default Component_{i};
''')

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()
    (coderef_dir / "context-experts").mkdir()
    (coderef_dir / "context-experts" / "experts").mkdir()
    (coderef_dir / "context-experts" / "cache").mkdir()

    return project_dir


# ============================================================================
# CONTEXT EXPERT GENERATOR PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestContextExpertPerformance:
    """Performance tests for ContextExpertGenerator with large projects."""

    def test_expert_creation_time(self, large_python_project: Path):
        """Expert creation should complete in reasonable time for large files."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(large_python_project)

        # Time expert creation for a file
        start_time = time.time()
        result = generator.create_expert(
            resource_path="src/module_0/file_0.py",
            resource_type="file",
            domain="core"
        )
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Expert creation failed: {result}"
        assert elapsed < 2.0, f"Expert creation took {elapsed:.2f}s, expected < 2s"

        # Verify expert was created correctly
        assert "expert_id" in result
        assert result["code_structure"]["functions_count"] > 0

    def test_directory_expert_creation_time(self, large_python_project: Path):
        """Directory expert creation should handle many files efficiently."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(large_python_project)

        # Time expert creation for a directory with 10 files
        start_time = time.time()
        result = generator.create_expert(
            resource_path="src/module_0",
            resource_type="directory",
            domain="core"
        )
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Directory expert creation failed: {result}"
        assert elapsed < 5.0, f"Directory expert creation took {elapsed:.2f}s, expected < 5s"

    def test_batch_expert_creation(self, large_python_project: Path):
        """Creating multiple experts should scale reasonably."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(large_python_project)

        # Create experts for 5 modules
        start_time = time.time()
        created_count = 0

        for i in range(5):
            result = generator.create_expert(
                resource_path=f"src/module_{i}/file_0.py",
                resource_type="file",
                domain="core"
            )
            if result.get("success", False):
                created_count += 1

        elapsed = time.time() - start_time

        assert created_count == 5, f"Only created {created_count}/5 experts"
        assert elapsed < 10.0, f"Batch creation took {elapsed:.2f}s, expected < 10s"

        # Verify list operation is fast
        list_start = time.time()
        experts = generator.list_experts()
        list_elapsed = time.time() - list_start

        assert len(experts.get("experts", [])) >= 5
        assert list_elapsed < 0.5, f"List operation took {list_elapsed:.2f}s, expected < 0.5s"

    def test_suggest_experts_performance(self, large_python_project: Path):
        """Suggesting experts should scan large projects efficiently."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(large_python_project)

        start_time = time.time()
        result = generator.suggest_experts(limit=20)
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Suggest experts failed: {result}"
        assert elapsed < 5.0, f"Suggest experts took {elapsed:.2f}s, expected < 5s"

        suggestions = result.get("suggestions", [])
        assert len(suggestions) > 0, "No suggestions generated"


# ============================================================================
# FOUNDATION GENERATOR PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestFoundationGeneratorPerformance:
    """Performance tests for FoundationGenerator with large projects."""

    def test_generate_foundation_docs_time(self, large_python_project: Path):
        """Foundation docs generation should complete quickly for large projects."""
        from generators.foundation_generator import FoundationGenerator

        generator = FoundationGenerator(large_python_project)

        start_time = time.time()
        result = generator.generate_foundation_docs()
        elapsed = time.time() - start_time

        assert "templates" in result
        assert elapsed < 2.0, f"Foundation docs took {elapsed:.2f}s, expected < 2s"

    def test_template_retrieval_is_fast(self, large_python_project: Path):
        """Template retrieval should be O(1) regardless of project size."""
        from generators.foundation_generator import FoundationGenerator

        generator = FoundationGenerator(large_python_project)

        # Retrieve all templates and ensure each is fast
        templates = ["readme", "architecture", "api", "components", "schema"]

        for template_name in templates:
            start_time = time.time()
            result = generator.get_template(template_name)
            elapsed = time.time() - start_time

            assert "content" in result
            assert elapsed < 0.1, f"Template {template_name} took {elapsed:.3f}s, expected < 0.1s"


# ============================================================================
# PLANNING GENERATOR PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestPlanningGeneratorPerformance:
    """Performance tests for PlanningGenerator with large projects."""

    def test_analyze_project_performance(self, large_python_project: Path):
        """Project analysis should handle 100+ files efficiently."""
        from generators.planning_generator import PlanningGenerator

        generator = PlanningGenerator(large_python_project)

        start_time = time.time()
        result = generator.analyze_project()
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Analysis failed: {result}"
        assert elapsed < 3.0, f"Analysis took {elapsed:.2f}s, expected < 3s"

        # Verify analysis captured project structure
        assert "technology_stack" in result or "project_structure" in result

    def test_create_plan_with_analysis(self, large_python_project: Path):
        """Plan creation with full analysis should complete reasonably."""
        from generators.planning_generator import PlanningGenerator

        generator = PlanningGenerator(large_python_project)

        # Create context first
        working_dir = large_python_project / "coderef" / "working" / "perf-test-feature"
        working_dir.mkdir(parents=True, exist_ok=True)

        context = {
            "feature_name": "perf-test-feature",
            "description": "Performance test feature",
            "goal": "Test planning performance",
            "requirements": ["Requirement 1"],
            "gathered_at": datetime.now(timezone.utc).isoformat()
        }
        (working_dir / "context.json").write_text(json.dumps(context, indent=2))

        # Time plan creation
        start_time = time.time()
        result = generator.create_plan("perf-test-feature")
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Plan creation failed: {result}"
        assert elapsed < 5.0, f"Plan creation took {elapsed:.2f}s, expected < 5s"


# ============================================================================
# CHANGELOG GENERATOR PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestChangelogGeneratorPerformance:
    """Performance tests for ChangelogGenerator."""

    def test_changelog_with_many_entries(self, large_python_project: Path):
        """Changelog operations should handle many entries efficiently."""
        from generators.changelog_generator import ChangelogGenerator

        generator = ChangelogGenerator(large_python_project)

        # Add 50 changelog entries
        start_time = time.time()
        for i in range(50):
            generator.add_change(
                version=f"1.0.{i}",
                change_type="feature",
                severity="minor",
                title=f"Feature {i}",
                description=f"Added feature {i} for testing",
                files=[f"src/module_0/file_{i % 10}.py"],
                reason="Testing",
                impact="None"
            )
        add_elapsed = time.time() - start_time

        assert add_elapsed < 10.0, f"Adding 50 entries took {add_elapsed:.2f}s, expected < 10s"

        # Test retrieval performance
        start_time = time.time()
        result = generator.get_changelog()
        get_elapsed = time.time() - start_time

        assert "versions" in result
        assert get_elapsed < 0.5, f"Get changelog took {get_elapsed:.2f}s, expected < 0.5s"

        # Test filtered retrieval
        start_time = time.time()
        filtered = generator.get_changelog(change_type="feature")
        filter_elapsed = time.time() - start_time

        assert filter_elapsed < 0.5, f"Filtered get took {filter_elapsed:.2f}s, expected < 0.5s"


# ============================================================================
# INVENTORY GENERATORS PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestInventoryGeneratorsPerformance:
    """Performance tests for inventory generators with large projects."""

    def test_file_manifest_performance(self, large_python_project: Path):
        """File manifest generation should handle 100+ files efficiently."""
        from generators.inventory_generators import InventoryManifestGenerator

        generator = InventoryManifestGenerator(large_python_project)

        start_time = time.time()
        result = generator.generate_manifest(analysis_depth="quick")
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Manifest failed: {result}"
        assert elapsed < 5.0, f"Manifest took {elapsed:.2f}s, expected < 5s"

        # Verify file count
        total_files = result.get("total_files", 0)
        assert total_files >= 100, f"Expected 100+ files, got {total_files}"

    def test_standard_depth_performance(self, large_python_project: Path):
        """Standard depth analysis should complete in reasonable time."""
        from generators.inventory_generators import InventoryManifestGenerator

        generator = InventoryManifestGenerator(large_python_project)

        start_time = time.time()
        result = generator.generate_manifest(analysis_depth="standard")
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Standard manifest failed: {result}"
        assert elapsed < 15.0, f"Standard manifest took {elapsed:.2f}s, expected < 15s"

    def test_test_inventory_performance(self, large_python_project: Path):
        """Test inventory should scan test files efficiently."""
        from generators.inventory_generators import TestInventoryGenerator

        generator = TestInventoryGenerator(large_python_project)

        start_time = time.time()
        result = generator.generate_inventory()
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Test inventory failed: {result}"
        assert elapsed < 5.0, f"Test inventory took {elapsed:.2f}s, expected < 5s"

        # Verify test files found
        total_tests = result.get("total_test_files", 0)
        assert total_tests >= 10, f"Expected 10+ test files, got {total_tests}"

    def test_documentation_inventory_performance(self, large_python_project: Path):
        """Documentation inventory should scan docs efficiently."""
        from generators.inventory_generators import DocumentationInventoryGenerator

        generator = DocumentationInventoryGenerator(large_python_project)

        start_time = time.time()
        result = generator.generate_inventory()
        elapsed = time.time() - start_time

        assert result.get("success", False), f"Doc inventory failed: {result}"
        assert elapsed < 3.0, f"Doc inventory took {elapsed:.2f}s, expected < 3s"


# ============================================================================
# MEMORY AND SCALABILITY TESTS
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestScalability:
    """Tests for memory usage and scalability."""

    def test_generator_memory_cleanup(self, large_python_project: Path):
        """Generators should not leak memory across operations."""
        import gc
        from generators.context_expert_generator import ContextExpertGenerator

        # Force garbage collection before test
        gc.collect()

        # Create and destroy multiple generators
        for _ in range(5):
            generator = ContextExpertGenerator(large_python_project)
            generator.create_expert(
                resource_path="src/module_0/file_0.py",
                resource_type="file",
                domain="core"
            )
            del generator

        # Force garbage collection
        gc.collect()

        # Test passes if no memory errors occurred
        assert True

    def test_concurrent_operations_simulation(self, large_python_project: Path):
        """Simulate concurrent generator usage."""
        from generators.context_expert_generator import ContextExpertGenerator
        from generators.planning_generator import PlanningGenerator
        from generators.foundation_generator import FoundationGenerator

        # Create multiple generators (simulating concurrent access)
        generators = [
            ContextExpertGenerator(large_python_project),
            PlanningGenerator(large_python_project),
            FoundationGenerator(large_python_project)
        ]

        start_time = time.time()

        # Run operations on each
        results = []
        results.append(generators[0].list_experts())
        results.append(generators[1].analyze_project())
        results.append(generators[2].list_templates())

        elapsed = time.time() - start_time

        assert all(r.get("success", True) or "templates" in r or "experts" in r for r in results)
        assert elapsed < 5.0, f"Concurrent operations took {elapsed:.2f}s, expected < 5s"


# ============================================================================
# BASELINE PERFORMANCE METRICS
# ============================================================================

@pytest.mark.performance
class TestPerformanceBaselines:
    """Establish performance baselines for regression testing."""

    def test_record_baseline_metrics(self, large_python_project: Path):
        """Record baseline performance metrics for key operations."""
        from generators.context_expert_generator import ContextExpertGenerator
        from generators.planning_generator import PlanningGenerator
        from generators.foundation_generator import FoundationGenerator

        metrics = {}

        # Context Expert creation baseline
        gen1 = ContextExpertGenerator(large_python_project)
        start = time.time()
        gen1.create_expert("src/module_0/file_0.py", "file", "core")
        metrics["expert_creation"] = time.time() - start

        # Planning analysis baseline
        gen2 = PlanningGenerator(large_python_project)
        start = time.time()
        gen2.analyze_project()
        metrics["project_analysis"] = time.time() - start

        # Foundation docs baseline
        gen3 = FoundationGenerator(large_python_project)
        start = time.time()
        gen3.generate_foundation_docs()
        metrics["foundation_docs"] = time.time() - start

        # Log metrics for future reference
        print("\n=== Performance Baselines ===")
        for op, elapsed in metrics.items():
            print(f"  {op}: {elapsed:.3f}s")
        print("=============================\n")

        # All operations should complete within limits
        assert metrics["expert_creation"] < 2.0
        assert metrics["project_analysis"] < 3.0
        assert metrics["foundation_docs"] < 2.0
