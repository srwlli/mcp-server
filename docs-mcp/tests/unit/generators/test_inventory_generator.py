"""
Unit tests for InventoryGenerator.

Tests inventory generation, file discovery, categorization, risk assessment,
dependency analysis, and project metrics calculation.

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import jsonschema

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from generators.inventory_generator import InventoryGenerator


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def inventory_dir(tmp_path: Path) -> Path:
    """Create a project with inventory directory structure."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create coderef/inventory directory
    inventory_path = project_dir / "coderef" / "inventory"
    inventory_path.mkdir(parents=True)

    return project_dir


@pytest.fixture
def valid_schema() -> dict:
    """Return a valid inventory manifest schema."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["project_name", "files"],
        "properties": {
            "project_name": {"type": "string"},
            "project_path": {"type": "string"},
            "generated_at": {"type": "string"},
            "analysis_depth": {"type": "string"},
            "metrics": {"type": "object"},
            "files": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "name": {"type": "string"},
                        "extension": {"type": "string"},
                        "size": {"type": "integer"},
                        "lines": {"type": "integer"},
                        "category": {"type": "string"},
                        "risk_level": {"type": "string"}
                    }
                }
            }
        }
    }


@pytest.fixture
def inventory_with_schema(inventory_dir: Path, valid_schema: dict) -> Path:
    """Create inventory directory with schema file."""
    schema_path = inventory_dir / "coderef" / "inventory" / "schema.json"
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(valid_schema, f, indent=2)
    return inventory_dir


@pytest.fixture
def sample_project(inventory_with_schema: Path) -> Path:
    """Create a sample project with various file types for testing."""
    project_dir = inventory_with_schema

    # Create source files
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Python files
    (src_dir / "main.py").write_text('''"""Main module."""
import os
from pathlib import Path
from typing import List

def main():
    """Entry point."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')

    (src_dir / "utils.py").write_text('''"""Utility functions."""
import json
import re

def helper():
    return "helper"
''')

    # TypeScript file
    (src_dir / "api.ts").write_text('''import express from 'express';
import { Router } from 'express';

export const handler = () => {};
''')

    # Create test files
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    (tests_dir / "test_main.py").write_text('''import pytest
from src.main import main

def test_main():
    assert True
''')

    # Create config files
    (project_dir / "pyproject.toml").write_text('''[project]
name = "test-project"
version = "1.0.0"
''')

    (project_dir / ".env.example").write_text('''API_KEY=your_key_here
SECRET=your_secret_here
''')

    # Create docs
    docs_dir = project_dir / "docs"
    docs_dir.mkdir()

    (docs_dir / "README.md").write_text('''# Test Project

This is a test project.
''')

    # Create template files
    templates_dir = project_dir / "templates"
    templates_dir.mkdir()

    (templates_dir / "index.html").write_text('''<!DOCTYPE html>
<html>
<body>Hello</body>
</html>
''')

    return project_dir


@pytest.fixture
def inventory_generator(sample_project: Path) -> InventoryGenerator:
    """Create InventoryGenerator instance for testing."""
    return InventoryGenerator(sample_project)


# ============================================================================
# TEST: __init__
# ============================================================================

class TestInventoryGeneratorInit:
    """Tests for InventoryGenerator initialization."""

    def test_init_sets_project_path(self, sample_project: Path):
        """Test that __init__ sets project_path correctly."""
        gen = InventoryGenerator(sample_project)
        assert gen.project_path == sample_project

    def test_init_sets_inventory_dir(self, sample_project: Path):
        """Test that __init__ sets inventory_dir correctly."""
        gen = InventoryGenerator(sample_project)
        assert gen.inventory_dir == sample_project / "coderef" / "inventory"

    def test_init_sets_schema_path(self, sample_project: Path):
        """Test that __init__ sets schema_path correctly."""
        gen = InventoryGenerator(sample_project)
        assert gen.schema_path == sample_project / "coderef" / "inventory" / "schema.json"

    def test_init_loads_schema(self, sample_project: Path):
        """Test that __init__ loads schema if available."""
        gen = InventoryGenerator(sample_project)
        assert gen.schema is not None
        assert isinstance(gen.schema, dict)

    def test_init_without_schema(self, inventory_dir: Path):
        """Test __init__ when no schema file exists."""
        gen = InventoryGenerator(inventory_dir)
        assert gen.schema is None


# ============================================================================
# TEST: _load_schema
# ============================================================================

class TestLoadSchema:
    """Tests for _load_schema method."""

    def test_load_schema_success(self, inventory_with_schema: Path, valid_schema: dict):
        """Test loading schema from file."""
        gen = InventoryGenerator(inventory_with_schema)
        assert gen.schema == valid_schema

    def test_load_schema_file_not_found(self, inventory_dir: Path):
        """Test loading schema when file doesn't exist."""
        gen = InventoryGenerator(inventory_dir)
        assert gen.schema is None

    def test_load_schema_malformed_json(self, inventory_dir: Path):
        """Test loading malformed schema file."""
        schema_path = inventory_dir / "coderef" / "inventory" / "schema.json"
        with open(schema_path, 'w', encoding='utf-8') as f:
            f.write("{invalid json content")

        with pytest.raises(json.JSONDecodeError):
            InventoryGenerator(inventory_dir)


# ============================================================================
# TEST: validate_manifest
# ============================================================================

class TestValidateManifest:
    """Tests for validate_manifest method."""

    def test_validate_valid_manifest(self, inventory_generator: InventoryGenerator):
        """Test validating a valid manifest."""
        valid_manifest = {
            "project_name": "test-project",
            "project_path": "/path/to/project",
            "generated_at": datetime.now().isoformat(),
            "analysis_depth": "standard",
            "metrics": {},
            "files": []
        }
        # Should not raise
        inventory_generator.validate_manifest(valid_manifest)

    def test_validate_invalid_manifest_missing_required(self, inventory_generator: InventoryGenerator):
        """Test validating manifest missing required fields."""
        invalid_manifest = {
            "project_path": "/path/to/project"
            # Missing required: project_name, files
        }
        with pytest.raises(jsonschema.ValidationError):
            inventory_generator.validate_manifest(invalid_manifest)

    def test_validate_invalid_manifest_wrong_type(self, inventory_generator: InventoryGenerator):
        """Test validating manifest with wrong type."""
        invalid_manifest = {
            "project_name": 123,  # Should be string
            "files": []
        }
        with pytest.raises(jsonschema.ValidationError):
            inventory_generator.validate_manifest(invalid_manifest)

    def test_validate_skips_when_no_schema(self, inventory_dir: Path):
        """Test validation skips when no schema available."""
        gen = InventoryGenerator(inventory_dir)
        # Should not raise even with invalid data
        gen.validate_manifest({"invalid": "data"})


# ============================================================================
# TEST: discover_files
# ============================================================================

class TestDiscoverFiles:
    """Tests for discover_files method."""

    def test_discover_files_returns_list(self, inventory_generator: InventoryGenerator):
        """Test that discover_files returns a list."""
        files = inventory_generator.discover_files()
        assert isinstance(files, list)

    def test_discover_files_finds_expected_files(self, inventory_generator: InventoryGenerator):
        """Test that discover_files finds expected project files."""
        files = inventory_generator.discover_files()
        file_paths = [f["path"] for f in files]

        # Check expected files exist
        assert any("main.py" in p for p in file_paths)
        assert any("utils.py" in p for p in file_paths)
        assert any("test_main.py" in p for p in file_paths)

    def test_discover_files_includes_metadata(self, inventory_generator: InventoryGenerator):
        """Test that discovered files include required metadata."""
        files = inventory_generator.discover_files()

        for file_meta in files:
            assert "path" in file_meta
            assert "name" in file_meta
            assert "extension" in file_meta
            assert "size" in file_meta
            assert "lines" in file_meta
            assert "last_modified" in file_meta

    def test_discover_files_excludes_directories(self, sample_project: Path):
        """Test that discover_files respects exclude_dirs."""
        # Create node_modules directory
        node_modules = sample_project / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.json").write_text('{}')

        gen = InventoryGenerator(sample_project)
        files = gen.discover_files(exclude_dirs=["node_modules"])
        file_paths = [f["path"] for f in files]

        # Should not include node_modules files
        assert not any("node_modules" in p for p in file_paths)

    def test_discover_files_respects_max_file_size(self, sample_project: Path):
        """Test that discover_files respects max_file_size."""
        # Create a large file
        large_file = sample_project / "large_file.txt"
        large_file.write_text("x" * 10000)  # 10KB

        gen = InventoryGenerator(sample_project)
        files = gen.discover_files(max_file_size=5000)  # 5KB limit
        file_paths = [f["path"] for f in files]

        # Should not include large file
        assert "large_file.txt" not in file_paths

    def test_discover_files_uses_forward_slashes(self, inventory_generator: InventoryGenerator):
        """Test that file paths use forward slashes."""
        files = inventory_generator.discover_files()

        for file_meta in files:
            assert "\\" not in file_meta["path"]


# ============================================================================
# TEST: _count_lines
# ============================================================================

class TestCountLines:
    """Tests for _count_lines method."""

    def test_count_lines_text_file(self, sample_project: Path):
        """Test counting lines in a text file."""
        gen = InventoryGenerator(sample_project)
        main_py = sample_project / "src" / "main.py"
        lines = gen._count_lines(main_py)
        assert lines > 0

    def test_count_lines_empty_file(self, sample_project: Path):
        """Test counting lines in an empty file."""
        empty_file = sample_project / "empty.txt"
        empty_file.write_text("")

        gen = InventoryGenerator(sample_project)
        lines = gen._count_lines(empty_file)
        assert lines == 0

    def test_count_lines_binary_file(self, sample_project: Path):
        """Test counting lines in a binary file."""
        binary_file = sample_project / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03')

        gen = InventoryGenerator(sample_project)
        lines = gen._count_lines(binary_file)
        # Should return count based on how bytes are interpreted
        assert isinstance(lines, int)


# ============================================================================
# TEST: categorize_file
# ============================================================================

class TestCategorizeFile:
    """Tests for categorize_file method."""

    def test_categorize_test_file_by_directory(self, inventory_generator: InventoryGenerator):
        """Test categorizing test file by directory."""
        category = inventory_generator.categorize_file(Path("tests/test_main.py"))
        assert category == "test"

    def test_categorize_test_file_by_prefix(self, inventory_generator: InventoryGenerator):
        """Test categorizing test file by test_ prefix."""
        category = inventory_generator.categorize_file(Path("test_utils.py"))
        assert category == "test"

    def test_categorize_test_file_by_suffix(self, inventory_generator: InventoryGenerator):
        """Test categorizing test file by _test suffix."""
        category = inventory_generator.categorize_file(Path("utils_test.py"))
        assert category == "test"

    def test_categorize_js_spec_file(self, inventory_generator: InventoryGenerator):
        """Test categorizing JavaScript spec file."""
        category = inventory_generator.categorize_file(Path("component.spec.js"))
        assert category == "test"

    def test_categorize_documentation_by_extension(self, inventory_generator: InventoryGenerator):
        """Test categorizing documentation by .md extension."""
        category = inventory_generator.categorize_file(Path("README.md"))
        assert category == "docs"

    def test_categorize_documentation_by_directory(self, inventory_generator: InventoryGenerator):
        """Test categorizing documentation by docs directory."""
        category = inventory_generator.categorize_file(Path("docs/guide.html"))
        assert category == "docs"

    def test_categorize_config_by_name(self, inventory_generator: InventoryGenerator):
        """Test categorizing config by known names."""
        assert inventory_generator.categorize_file(Path("package.json")) == "config"
        assert inventory_generator.categorize_file(Path("pyproject.toml")) == "config"
        assert inventory_generator.categorize_file(Path(".gitignore")) == "config"

    def test_categorize_config_by_directory(self, inventory_generator: InventoryGenerator):
        """Test categorizing config by config directory."""
        category = inventory_generator.categorize_file(Path("config/settings.json"))
        assert category == "config"

    def test_categorize_template_by_extension(self, inventory_generator: InventoryGenerator):
        """Test categorizing template by extension."""
        assert inventory_generator.categorize_file(Path("index.html")) == "template"
        assert inventory_generator.categorize_file(Path("base.jinja")) == "template"
        assert inventory_generator.categorize_file(Path("component.hbs")) == "template"

    def test_categorize_template_by_directory(self, inventory_generator: InventoryGenerator):
        """Test categorizing template by templates directory."""
        category = inventory_generator.categorize_file(Path("templates/email.txt"))
        assert category == "template"

    def test_categorize_core_files(self, inventory_generator: InventoryGenerator):
        """Test categorizing core infrastructure files."""
        assert inventory_generator.categorize_file(Path("server.py")) == "core"
        assert inventory_generator.categorize_file(Path("main.py")) == "core"
        assert inventory_generator.categorize_file(Path("app.py")) == "core"

    def test_categorize_source_code(self, inventory_generator: InventoryGenerator):
        """Test categorizing source code files."""
        assert inventory_generator.categorize_file(Path("src/utils.py")) == "source"
        assert inventory_generator.categorize_file(Path("lib/helper.js")) == "source"
        assert inventory_generator.categorize_file(Path("api/routes.ts")) == "source"

    def test_categorize_unknown_file(self, inventory_generator: InventoryGenerator):
        """Test categorizing unknown file type."""
        category = inventory_generator.categorize_file(Path("random.xyz"))
        assert category == "unknown"


# ============================================================================
# TEST: calculate_risk_level
# ============================================================================

class TestCalculateRiskLevel:
    """Tests for calculate_risk_level method."""

    def test_risk_low_for_docs(self, inventory_generator: InventoryGenerator):
        """Test that documentation files have low risk."""
        file_meta = {
            "name": "README.md",
            "path": "docs/README.md",
            "category": "docs",
            "size": 1000,
            "lines": 50
        }
        risk = inventory_generator.calculate_risk_level(file_meta)
        assert risk == "low"

    def test_risk_higher_for_core(self, inventory_generator: InventoryGenerator):
        """Test that core files have higher risk."""
        file_meta = {
            "name": "server.py",
            "path": "server.py",
            "category": "core",
            "size": 5000,
            "lines": 200
        }
        risk = inventory_generator.calculate_risk_level(file_meta)
        assert risk in ["medium", "high"]

    def test_risk_critical_for_sensitive_files(self, inventory_generator: InventoryGenerator):
        """Test that sensitive files are marked critical."""
        file_meta = {
            "name": ".env",
            "path": ".env",
            "category": "config",
            "size": 500,
            "lines": 10
        }
        risk = inventory_generator.calculate_risk_level(file_meta)
        assert risk == "critical"

    def test_risk_increases_with_file_size(self, inventory_generator: InventoryGenerator):
        """Test that risk increases with file size."""
        small_file = {
            "name": "small.py",
            "path": "src/small.py",
            "category": "source",
            "size": 100,
            "lines": 10
        }
        large_file = {
            "name": "large.py",
            "path": "src/large.py",
            "category": "source",
            "size": 2_000_000,
            "lines": 10
        }

        small_risk = inventory_generator.calculate_risk_level(small_file)
        large_risk = inventory_generator.calculate_risk_level(large_file)

        # Larger file should have higher or equal risk
        risk_order = ["low", "medium", "high", "critical"]
        assert risk_order.index(large_risk) >= risk_order.index(small_risk)

    def test_risk_increases_with_lines(self, inventory_generator: InventoryGenerator):
        """Test that risk increases with line count."""
        short_file = {
            "name": "short.py",
            "path": "src/short.py",
            "category": "source",
            "size": 100,
            "lines": 10
        }
        long_file = {
            "name": "long.py",
            "path": "src/long.py",
            "category": "source",
            "size": 100,
            "lines": 2000
        }

        short_risk = inventory_generator.calculate_risk_level(short_file)
        long_risk = inventory_generator.calculate_risk_level(long_file)

        risk_order = ["low", "medium", "high", "critical"]
        assert risk_order.index(long_risk) >= risk_order.index(short_risk)

    def test_risk_detects_sensitive_patterns(self, inventory_generator: InventoryGenerator):
        """Test detection of various sensitive file patterns."""
        sensitive_names = [
            "secrets.json", "credentials.yaml", "password.txt",
            "api_key.json", "private_key.pem", "auth_token.txt"
        ]

        for name in sensitive_names:
            file_meta = {
                "name": name,
                "path": f"config/{name}",
                "category": "config",
                "size": 100,
                "lines": 10
            }
            risk = inventory_generator.calculate_risk_level(file_meta)
            assert risk in ["high", "critical"], f"Expected {name} to be high/critical risk"


# ============================================================================
# TEST: analyze_dependencies
# ============================================================================

class TestAnalyzeDependencies:
    """Tests for analyze_dependencies method."""

    def test_analyze_python_imports(self, sample_project: Path):
        """Test analyzing Python import statements."""
        gen = InventoryGenerator(sample_project)
        main_py = sample_project / "src" / "main.py"
        deps = gen.analyze_dependencies(main_py)

        assert "os" in deps
        assert "pathlib" in deps
        assert "typing" in deps

    def test_analyze_python_from_imports(self, sample_project: Path):
        """Test analyzing Python from...import statements."""
        gen = InventoryGenerator(sample_project)
        utils_py = sample_project / "src" / "utils.py"
        deps = gen.analyze_dependencies(utils_py)

        assert "json" in deps
        assert "re" in deps

    def test_analyze_typescript_imports(self, sample_project: Path):
        """Test analyzing TypeScript import statements."""
        gen = InventoryGenerator(sample_project)
        api_ts = sample_project / "src" / "api.ts"
        deps = gen.analyze_dependencies(api_ts)

        assert "express" in deps

    def test_analyze_empty_file(self, sample_project: Path):
        """Test analyzing file with no imports."""
        empty_file = sample_project / "empty.py"
        empty_file.write_text("# No imports here")

        gen = InventoryGenerator(sample_project)
        deps = gen.analyze_dependencies(empty_file)
        assert deps == []

    def test_analyze_nonexistent_file(self, sample_project: Path):
        """Test analyzing non-existent file."""
        gen = InventoryGenerator(sample_project)
        nonexistent = sample_project / "nonexistent.py"
        deps = gen.analyze_dependencies(nonexistent)
        assert deps == []

    def test_analyze_returns_sorted_list(self, sample_project: Path):
        """Test that dependencies are returned sorted."""
        gen = InventoryGenerator(sample_project)
        main_py = sample_project / "src" / "main.py"
        deps = gen.analyze_dependencies(main_py)

        assert deps == sorted(deps)


# ============================================================================
# TEST: calculate_project_metrics
# ============================================================================

class TestCalculateProjectMetrics:
    """Tests for calculate_project_metrics method."""

    def test_metrics_includes_total_files(self, inventory_generator: InventoryGenerator):
        """Test that metrics include total file count."""
        files = [
            {"size": 100, "lines": 10, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 200, "lines": 20, "category": "test", "risk_level": "low", "extension": ".py"},
        ]
        metrics = inventory_generator.calculate_project_metrics(files)
        assert metrics["total_files"] == 2

    def test_metrics_includes_total_size(self, inventory_generator: InventoryGenerator):
        """Test that metrics include total size."""
        files = [
            {"size": 100, "lines": 10, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 200, "lines": 20, "category": "test", "risk_level": "low", "extension": ".py"},
        ]
        metrics = inventory_generator.calculate_project_metrics(files)
        assert metrics["total_size"] == 300

    def test_metrics_includes_total_lines(self, inventory_generator: InventoryGenerator):
        """Test that metrics include total lines."""
        files = [
            {"size": 100, "lines": 10, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 200, "lines": 20, "category": "test", "risk_level": "low", "extension": ".py"},
        ]
        metrics = inventory_generator.calculate_project_metrics(files)
        assert metrics["total_lines"] == 30

    def test_metrics_includes_category_breakdown(self, inventory_generator: InventoryGenerator):
        """Test that metrics include file category breakdown."""
        files = [
            {"size": 100, "lines": 10, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 200, "lines": 20, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 150, "lines": 15, "category": "test", "risk_level": "low", "extension": ".py"},
        ]
        metrics = inventory_generator.calculate_project_metrics(files)
        assert metrics["file_categories"]["source"] == 2
        assert metrics["file_categories"]["test"] == 1

    def test_metrics_includes_risk_distribution(self, inventory_generator: InventoryGenerator):
        """Test that metrics include risk distribution."""
        files = [
            {"size": 100, "lines": 10, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 200, "lines": 20, "category": "core", "risk_level": "high", "extension": ".py"},
            {"size": 150, "lines": 15, "category": "config", "risk_level": "critical", "extension": ".py"},
        ]
        metrics = inventory_generator.calculate_project_metrics(files)
        assert metrics["risk_distribution"]["low"] == 1
        assert metrics["risk_distribution"]["high"] == 1
        assert metrics["risk_distribution"]["critical"] == 1

    def test_metrics_includes_language_breakdown(self, inventory_generator: InventoryGenerator):
        """Test that metrics include language breakdown."""
        files = [
            {"size": 100, "lines": 10, "category": "source", "risk_level": "low", "extension": ".py"},
            {"size": 200, "lines": 20, "category": "source", "risk_level": "low", "extension": ".js"},
            {"size": 150, "lines": 15, "category": "source", "risk_level": "low", "extension": ".py"},
        ]
        metrics = inventory_generator.calculate_project_metrics(files)
        assert metrics["language_breakdown"]["Python"] == 2
        assert metrics["language_breakdown"]["JavaScript"] == 1

    def test_metrics_empty_files_list(self, inventory_generator: InventoryGenerator):
        """Test metrics calculation with empty files list."""
        metrics = inventory_generator.calculate_project_metrics([])
        assert metrics["total_files"] == 0
        assert metrics["total_size"] == 0
        assert metrics["total_lines"] == 0


# ============================================================================
# TEST: _infer_language
# ============================================================================

class TestInferLanguage:
    """Tests for _infer_language method."""

    def test_infer_python(self, inventory_generator: InventoryGenerator):
        """Test inferring Python language."""
        assert inventory_generator._infer_language(".py") == "Python"

    def test_infer_javascript(self, inventory_generator: InventoryGenerator):
        """Test inferring JavaScript language."""
        assert inventory_generator._infer_language(".js") == "JavaScript"
        assert inventory_generator._infer_language(".jsx") == "JavaScript"

    def test_infer_typescript(self, inventory_generator: InventoryGenerator):
        """Test inferring TypeScript language."""
        assert inventory_generator._infer_language(".ts") == "TypeScript"
        assert inventory_generator._infer_language(".tsx") == "TypeScript"

    def test_infer_various_languages(self, inventory_generator: InventoryGenerator):
        """Test inferring various programming languages."""
        assert inventory_generator._infer_language(".java") == "Java"
        assert inventory_generator._infer_language(".go") == "Go"
        assert inventory_generator._infer_language(".rs") == "Rust"
        assert inventory_generator._infer_language(".rb") == "Ruby"
        assert inventory_generator._infer_language(".php") == "PHP"

    def test_infer_markup_languages(self, inventory_generator: InventoryGenerator):
        """Test inferring markup/data languages."""
        assert inventory_generator._infer_language(".html") == "HTML"
        assert inventory_generator._infer_language(".css") == "CSS"
        assert inventory_generator._infer_language(".json") == "JSON"
        assert inventory_generator._infer_language(".yaml") == "YAML"
        assert inventory_generator._infer_language(".md") == "Markdown"

    def test_infer_unknown_extension(self, inventory_generator: InventoryGenerator):
        """Test inferring unknown extension."""
        assert inventory_generator._infer_language(".xyz") == ""
        assert inventory_generator._infer_language("") == ""


# ============================================================================
# TEST: generate_manifest
# ============================================================================

class TestGenerateManifest:
    """Tests for generate_manifest method."""

    def test_generate_manifest_returns_dict(self, inventory_generator: InventoryGenerator):
        """Test that generate_manifest returns a dictionary."""
        manifest = inventory_generator.generate_manifest()
        assert isinstance(manifest, dict)

    def test_generate_manifest_includes_project_name(self, inventory_generator: InventoryGenerator):
        """Test that manifest includes project name."""
        manifest = inventory_generator.generate_manifest()
        assert "project_name" in manifest
        assert manifest["project_name"] == inventory_generator.project_path.name

    def test_generate_manifest_includes_timestamp(self, inventory_generator: InventoryGenerator):
        """Test that manifest includes generation timestamp."""
        manifest = inventory_generator.generate_manifest()
        assert "generated_at" in manifest
        # Should be ISO format
        datetime.fromisoformat(manifest["generated_at"])

    def test_generate_manifest_includes_files(self, inventory_generator: InventoryGenerator):
        """Test that manifest includes files list."""
        manifest = inventory_generator.generate_manifest()
        assert "files" in manifest
        assert isinstance(manifest["files"], list)
        assert len(manifest["files"]) > 0

    def test_generate_manifest_includes_metrics(self, inventory_generator: InventoryGenerator):
        """Test that manifest includes metrics."""
        manifest = inventory_generator.generate_manifest()
        assert "metrics" in manifest
        assert "total_files" in manifest["metrics"]

    def test_generate_manifest_quick_depth(self, inventory_generator: InventoryGenerator):
        """Test manifest generation with quick depth."""
        manifest = inventory_generator.generate_manifest(analysis_depth="quick")
        assert manifest["analysis_depth"] == "quick"
        # Quick depth should not include dependencies
        for file_meta in manifest["files"]:
            assert file_meta.get("dependencies", []) == []

    def test_generate_manifest_standard_depth(self, inventory_generator: InventoryGenerator):
        """Test manifest generation with standard depth."""
        manifest = inventory_generator.generate_manifest(analysis_depth="standard")
        assert manifest["analysis_depth"] == "standard"
        # Standard depth should include dependencies
        has_deps = any(file_meta.get("dependencies", []) for file_meta in manifest["files"])
        # Note: Some files may not have deps, but at least one should
        assert has_deps or len(manifest["files"]) == 0

    def test_generate_manifest_deep_depth(self, inventory_generator: InventoryGenerator):
        """Test manifest generation with deep depth."""
        manifest = inventory_generator.generate_manifest(analysis_depth="deep")
        assert manifest["analysis_depth"] == "deep"

    def test_generate_manifest_invalid_depth(self, inventory_generator: InventoryGenerator):
        """Test manifest generation with invalid depth."""
        with pytest.raises(ValueError) as exc_info:
            inventory_generator.generate_manifest(analysis_depth="invalid")
        assert "Invalid analysis_depth" in str(exc_info.value)

    def test_generate_manifest_respects_exclude_dirs(self, sample_project: Path):
        """Test that generate_manifest respects exclude_dirs."""
        # Create excluded directory
        excluded = sample_project / "excluded"
        excluded.mkdir()
        (excluded / "file.py").write_text("# excluded")

        gen = InventoryGenerator(sample_project)
        manifest = gen.generate_manifest(exclude_dirs=["excluded"])

        file_paths = [f["path"] for f in manifest["files"]]
        assert not any("excluded" in p for p in file_paths)


# ============================================================================
# TEST: save_manifest
# ============================================================================

class TestSaveManifest:
    """Tests for save_manifest method."""

    def test_save_manifest_creates_file(self, inventory_generator: InventoryGenerator):
        """Test that save_manifest creates a file."""
        manifest = inventory_generator.generate_manifest()
        output_path = inventory_generator.save_manifest(manifest)

        assert output_path.exists()
        assert output_path.name == "manifest.json"

    def test_save_manifest_creates_valid_json(self, inventory_generator: InventoryGenerator):
        """Test that save_manifest creates valid JSON."""
        manifest = inventory_generator.generate_manifest()
        output_path = inventory_generator.save_manifest(manifest)

        with open(output_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        assert loaded["project_name"] == manifest["project_name"]

    def test_save_manifest_custom_path(self, inventory_generator: InventoryGenerator, tmp_path: Path):
        """Test saving manifest to custom path."""
        manifest = inventory_generator.generate_manifest()
        custom_path = tmp_path / "custom_manifest.json"
        output_path = inventory_generator.save_manifest(manifest, output_file=custom_path)

        assert output_path == custom_path
        assert custom_path.exists()

    def test_save_manifest_creates_directory(self, sample_project: Path):
        """Test that save_manifest creates inventory directory if needed."""
        # Remove inventory directory
        import shutil
        inventory_dir = sample_project / "coderef" / "inventory"
        if inventory_dir.exists():
            shutil.rmtree(inventory_dir)

        gen = InventoryGenerator(sample_project)
        gen.schema = None  # Disable validation since schema is gone
        manifest = {"project_name": "test", "files": []}
        output_path = gen.save_manifest(manifest)

        assert output_path.parent.exists()

    def test_save_manifest_validates_before_save(self, inventory_generator: InventoryGenerator):
        """Test that save_manifest validates before saving."""
        invalid_manifest = {"invalid": "data"}  # Missing required fields

        with pytest.raises(jsonschema.ValidationError):
            inventory_generator.save_manifest(invalid_manifest)


# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_project_directory(self, inventory_dir: Path):
        """Test handling empty project directory."""
        gen = InventoryGenerator(inventory_dir)
        files = gen.discover_files()
        # Should only find the schema.json if it exists
        assert len(files) <= 1

    def test_deeply_nested_files(self, sample_project: Path):
        """Test handling deeply nested directory structure."""
        # Create deeply nested file
        deep_path = sample_project / "a" / "b" / "c" / "d" / "e"
        deep_path.mkdir(parents=True)
        (deep_path / "deep.py").write_text("# deep file")

        gen = InventoryGenerator(sample_project)
        files = gen.discover_files()

        file_paths = [f["path"] for f in files]
        assert any("a/b/c/d/e/deep.py" in p for p in file_paths)

    def test_special_characters_in_filename(self, sample_project: Path):
        """Test handling files with special characters in name."""
        # Create file with special characters (that are valid on filesystem)
        special_file = sample_project / "file-with_special.chars.py"
        special_file.write_text("# special")

        gen = InventoryGenerator(sample_project)
        files = gen.discover_files()

        file_paths = [f["path"] for f in files]
        assert any("file-with_special.chars.py" in p for p in file_paths)

    def test_unicode_in_file_content(self, sample_project: Path):
        """Test handling Unicode content in files."""
        unicode_file = sample_project / "unicode.py"
        unicode_file.write_text("# 你好世界 🌍\nprint('Hello')")

        gen = InventoryGenerator(sample_project)
        lines = gen._count_lines(unicode_file)
        assert lines == 2


# ============================================================================
# TEST: Integration
# ============================================================================

class TestInventoryGeneratorIntegration:
    """Integration tests for InventoryGenerator."""

    def test_full_workflow(self, sample_project: Path):
        """Test complete inventory generation workflow."""
        gen = InventoryGenerator(sample_project)

        # Generate manifest
        manifest = gen.generate_manifest(analysis_depth="standard")

        # Verify structure
        assert "project_name" in manifest
        assert "files" in manifest
        assert "metrics" in manifest

        # Save manifest
        output_path = gen.save_manifest(manifest)

        # Verify saved file
        assert output_path.exists()

        # Reload and verify
        with open(output_path, 'r', encoding='utf-8') as f:
            reloaded = json.load(f)

        assert reloaded["project_name"] == manifest["project_name"]
        assert len(reloaded["files"]) == len(manifest["files"])

    def test_categorization_consistency(self, sample_project: Path):
        """Test that categorization is consistent across runs."""
        gen = InventoryGenerator(sample_project)

        # Generate manifest twice
        manifest1 = gen.generate_manifest()
        manifest2 = gen.generate_manifest()

        # Categories should be identical
        for f1, f2 in zip(
            sorted(manifest1["files"], key=lambda x: x["path"]),
            sorted(manifest2["files"], key=lambda x: x["path"])
        ):
            assert f1["category"] == f2["category"]


# ============================================================================
# TEST: Performance
# ============================================================================

class TestPerformance:
    """Performance tests for InventoryGenerator."""

    @pytest.mark.slow
    def test_large_project_performance(self, tmp_path: Path):
        """Test performance with larger project (100+ files)."""
        import time

        project_dir = tmp_path / "large-project"
        project_dir.mkdir()
        (project_dir / "coderef" / "inventory").mkdir(parents=True)

        # Create 100 files
        src_dir = project_dir / "src"
        src_dir.mkdir()
        for i in range(100):
            (src_dir / f"file_{i}.py").write_text(f"# File {i}\n" * 10)

        gen = InventoryGenerator(project_dir)

        start_time = time.time()
        manifest = gen.generate_manifest(analysis_depth="quick")
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        assert len(manifest["files"]) >= 100

    def test_manifest_generation_time(self, inventory_generator: InventoryGenerator):
        """Test that manifest generation completes in reasonable time."""
        import time

        start_time = time.time()
        inventory_generator.generate_manifest()
        elapsed = time.time() - start_time

        # Should complete quickly for small projects
        assert elapsed < 2.0
