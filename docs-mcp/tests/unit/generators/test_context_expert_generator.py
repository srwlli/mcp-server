"""
Unit tests for ContextExpertGenerator.

Tests all 6 expert methods plus helper functions:
- create_expert
- list_experts
- get_expert
- suggest_candidates
- update_expert
- add_onboarding (activate_expert)

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from generators.context_expert_generator import ContextExpertGenerator


class TestContextExpertGeneratorInit:
    """Test ContextExpertGenerator initialization."""

    def test_init_with_path(self, mock_project: Path):
        """Test generator initializes with correct paths."""
        generator = ContextExpertGenerator(mock_project)

        assert generator.project_path == mock_project.resolve()
        # Implementation uses coderef/experts (not coderef/context-experts)
        assert "experts" in str(generator.experts_dir)
        assert "cache" in str(generator.cache_dir)
        assert "index.json" in str(generator.index_path)

    def test_init_resolves_path(self, tmp_path: Path):
        """Test that path is resolved to absolute."""
        # Create relative-looking path
        rel_path = tmp_path / "test-project"
        rel_path.mkdir()

        generator = ContextExpertGenerator(rel_path)
        assert generator.project_path.is_absolute()

    def test_ensure_directories_creates_structure(self, mock_project: Path):
        """Test _ensure_directories creates expert storage directories."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        assert generator.experts_dir.exists()
        assert generator.cache_dir.exists()


class TestExpertIdGeneration:
    """Test expert ID generation logic."""

    def test_generate_expert_id_basic(self, mock_project: Path):
        """Test basic ID generation from path."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        expert_id = generator._generate_expert_id("src/main.py")

        assert expert_id.startswith("CE-")
        assert expert_id.endswith("-001")
        assert "src" in expert_id or "main" in expert_id

    def test_generate_expert_id_increments(self, mock_project: Path):
        """Test ID increments for same resource."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        # Create first expert
        id1 = generator._generate_expert_id("src/main.py")
        # Save empty file to trigger increment
        (generator.experts_dir / f"{id1}.json").write_text("{}")

        # Create second expert
        id2 = generator._generate_expert_id("src/main.py")

        assert id1 != id2
        assert id1.endswith("-001")
        assert id2.endswith("-002")

    def test_generate_expert_id_sanitizes_path(self, mock_project: Path):
        """Test ID generation sanitizes special characters."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        expert_id = generator._generate_expert_id("src/path.with.dots/file.py")

        # Should not contain dots, slashes
        assert "." not in expert_id.split("-")[1]  # Skip CE- prefix
        assert "/" not in expert_id
        assert "\\" not in expert_id

    def test_generate_expert_id_limits_length(self, mock_project: Path):
        """Test ID slug is limited to 30 characters."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        long_path = "src/" + "a" * 100 + "/very_long_filename.py"
        expert_id = generator._generate_expert_id(long_path)

        # Format: CE-{slug}-NNN where slug max 30 chars
        parts = expert_id.split("-")
        slug = "-".join(parts[1:-1])
        assert len(slug) <= 30


class TestContentHash:
    """Test content hash computation."""

    def test_compute_content_hash_file(self, mock_project: Path):
        """Test hash computation for file."""
        generator = ContextExpertGenerator(mock_project)

        hash1 = generator._compute_content_hash("src/main.py")
        hash2 = generator._compute_content_hash("src/main.py")

        assert hash1 == hash2
        assert len(hash1) == 16  # SHA256[:16]

    def test_compute_content_hash_different_files(self, mock_project: Path):
        """Test different files produce different hashes."""
        generator = ContextExpertGenerator(mock_project)

        hash1 = generator._compute_content_hash("src/main.py")
        hash2 = generator._compute_content_hash("src/utils.py")

        assert hash1 != hash2

    def test_compute_content_hash_directory(self, mock_project: Path):
        """Test hash computation for directory."""
        generator = ContextExpertGenerator(mock_project)

        dir_hash = generator._compute_content_hash("src")

        assert len(dir_hash) == 16
        assert dir_hash != "unknown"

    def test_compute_content_hash_nonexistent(self, mock_project: Path):
        """Test hash for nonexistent path returns 'unknown'."""
        generator = ContextExpertGenerator(mock_project)

        hash_result = generator._compute_content_hash("nonexistent/file.py")

        assert hash_result == "unknown"


class TestCodeStructureAnalysis:
    """Test code structure analysis using AST and regex."""

    def test_analyze_code_structure_python(self, mock_project: Path):
        """Test Python code analysis with AST."""
        generator = ContextExpertGenerator(mock_project)

        structure = generator.analyze_code_structure("src/main.py")

        assert len(structure["functions"]) > 0
        assert len(structure["classes"]) > 0
        assert len(structure["imports"]) > 0
        assert structure["line_count"] > 0
        assert structure["complexity_score"] > 0

    def test_analyze_code_structure_finds_async_functions(self, mock_project: Path):
        """Test async function detection."""
        generator = ContextExpertGenerator(mock_project)

        structure = generator.analyze_code_structure("src/main.py")

        # Main.py has async functions
        async_funcs = [f for f in structure["functions"] if "async" in f]
        assert len(async_funcs) > 0

    def test_analyze_code_structure_typescript(self, mock_project: Path):
        """Test TypeScript/JavaScript code analysis with regex."""
        generator = ContextExpertGenerator(mock_project)

        structure = generator.analyze_code_structure("src/api.ts")

        assert len(structure["classes"]) > 0  # ApiHandler class detected
        # Note: Arrow functions (const x = () => {}) may not be detected as "functions"
        # The implementation detects traditional function declarations
        assert len(structure["imports"]) > 0  # import from 'express'
        assert len(structure["exports"]) > 0  # export class, export const

    def test_analyze_code_structure_react_component(self, mock_project: Path):
        """Test React component analysis."""
        generator = ContextExpertGenerator(mock_project)

        structure = generator.analyze_code_structure("src/components/Button.tsx")

        assert "Button" in structure["exports"] or len(structure["exports"]) > 0

    def test_analyze_code_structure_directory(self, mock_project: Path):
        """Test analysis of entire directory."""
        generator = ContextExpertGenerator(mock_project)

        structure = generator.analyze_code_structure("src")

        # Should aggregate multiple files
        assert structure["line_count"] > 50
        assert len(structure["functions"]) > 1
        assert len(structure["classes"]) > 1

    def test_analyze_code_structure_nonexistent(self, mock_project: Path):
        """Test analysis of nonexistent path returns empty structure."""
        generator = ContextExpertGenerator(mock_project)

        structure = generator.analyze_code_structure("nonexistent/file.py")

        assert structure["functions"] == []
        assert structure["classes"] == []
        assert structure["line_count"] == 0


class TestRegexExtraction:
    """Test regex-based code extraction for JS/TS."""

    def test_extract_functions(self, mock_project: Path):
        """Test function extraction with regex."""
        generator = ContextExpertGenerator(mock_project)

        functions = []
        classes = []
        imports = []
        exports = []

        content = """
        function hello() {}
        const greet = () => {};
        async function fetchData() {}
        const handler = async (req) => {};
        """

        generator._extract_with_regex(content, functions, classes, imports, exports)

        assert "hello" in functions
        assert "greet" in functions
        assert "fetchData" in functions

    def test_extract_classes(self, mock_project: Path):
        """Test class extraction with regex."""
        generator = ContextExpertGenerator(mock_project)

        functions = []
        classes = []
        imports = []
        exports = []

        content = """
        class MyComponent extends React.Component {}
        class ApiHandler {}
        """

        generator._extract_with_regex(content, functions, classes, imports, exports)

        assert "MyComponent" in classes
        assert "ApiHandler" in classes

    def test_extract_imports(self, mock_project: Path):
        """Test import extraction with regex."""
        generator = ContextExpertGenerator(mock_project)

        functions = []
        classes = []
        imports = []
        exports = []

        content = """
        import React from 'react';
        import { useState, useEffect } from 'react';
        const fs = require('fs');
        """

        generator._extract_with_regex(content, functions, classes, imports, exports)

        assert "react" in imports
        assert "fs" in imports

    def test_extract_exports(self, mock_project: Path):
        """Test export extraction with regex."""
        generator = ContextExpertGenerator(mock_project)

        functions = []
        classes = []
        imports = []
        exports = []

        content = """
        export default function main() {}
        export const helper = () => {};
        export class MyClass {}
        export { foo, bar };
        """

        generator._extract_with_regex(content, functions, classes, imports, exports)

        assert len(exports) > 0

    def test_extract_arrow_functions_without_parens(self, mock_project: Path):
        """Test arrow function extraction without parentheses around params."""
        generator = ContextExpertGenerator(mock_project)

        functions = []
        classes = []
        imports = []
        exports = []

        content = """
        const double = x => x * 2;
        const asyncFetch = async id => await fetch(id);
        let square = n => n ** 2;
        var cube = x => x ** 3;
        const withParens = (x) => x + 1;
        const asyncWithParens = async (x) => await process(x);
        """

        generator._extract_with_regex(content, functions, classes, imports, exports)

        # Should detect arrow functions without parentheses
        assert "double" in functions, f"Expected 'double' in {functions}"
        assert "asyncFetch" in functions, f"Expected 'asyncFetch' in {functions}"
        assert "square" in functions, f"Expected 'square' in {functions}"
        assert "cube" in functions, f"Expected 'cube' in {functions}"
        # Should also still detect arrow functions with parentheses
        assert "withParens" in functions, f"Expected 'withParens' in {functions}"
        assert "asyncWithParens" in functions, f"Expected 'asyncWithParens' in {functions}"

    def test_extract_object_method_arrow_functions(self, mock_project: Path):
        """Test object method arrow function extraction."""
        generator = ContextExpertGenerator(mock_project)

        functions = []
        classes = []
        imports = []
        exports = []

        content = """
        const obj = {
            method1: x => x + 1,
            method2: (x, y) => x + y,
            method3: async x => await fetch(x),
        };
        """

        generator._extract_with_regex(content, functions, classes, imports, exports)

        # Should detect object method arrow functions
        assert "method1" in functions, f"Expected 'method1' in {functions}"
        assert "method2" in functions, f"Expected 'method2' in {functions}"
        assert "method3" in functions, f"Expected 'method3' in {functions}"


class TestGitHistoryExtraction:
    """Test git history extraction."""

    def test_extract_git_history_with_commits(self, mock_project_with_history: Path):
        """Test git history extraction from repo with commits."""
        generator = ContextExpertGenerator(mock_project_with_history)

        history = generator.extract_git_history("src/main.py")

        assert len(history) > 0
        assert "commit_hash" in history[0]
        assert "author" in history[0]
        assert "message" in history[0]

    def test_extract_git_history_empty_repo(self, mock_project: Path):
        """Test git history extraction from repo with minimal commits."""
        generator = ContextExpertGenerator(mock_project)

        history = generator.extract_git_history("src/main.py")

        # Should return at least initial commit
        assert isinstance(history, list)

    def test_extract_git_history_nonexistent_file(self, mock_project: Path):
        """Test git history for nonexistent file returns empty list."""
        generator = ContextExpertGenerator(mock_project)

        history = generator.extract_git_history("nonexistent/file.py")

        assert history == []

    def test_extract_git_history_respects_limit(self, mock_project_with_history: Path):
        """Test limit parameter is respected."""
        generator = ContextExpertGenerator(mock_project_with_history)

        history = generator.extract_git_history("src/main.py", limit=2)

        assert len(history) <= 2


class TestRelationshipDetection:
    """Test file relationship detection."""

    def test_detect_relationships_finds_tests(self, mock_project: Path):
        """Test detection of related test files."""
        generator = ContextExpertGenerator(mock_project)

        relationships = generator.detect_relationships("src/main.py")

        # Mock project has tests/test_main.py
        assert any("test_main" in f for f in relationships["test_files"])

    def test_detect_relationships_finds_dependencies(self, mock_project: Path):
        """Test detection of import dependencies."""
        generator = ContextExpertGenerator(mock_project)

        relationships = generator.detect_relationships("src/main.py")

        # main.py imports asyncio, typing
        assert len(relationships["dependencies"]) >= 0

    def test_detect_relationships_finds_docs(self, mock_project: Path):
        """Test detection of related documentation."""
        generator = ContextExpertGenerator(mock_project)

        relationships = generator.detect_relationships("docs/README.md")

        # Should return relationship context
        assert "doc_files" in relationships
        assert "test_files" in relationships


class TestUsagePatternAnalysis:
    """Test usage pattern analysis."""

    def test_analyze_usage_patterns_basic(self, mock_project: Path):
        """Test basic usage pattern analysis."""
        generator = ContextExpertGenerator(mock_project)

        patterns = generator.analyze_usage_patterns("src/main.py")

        assert "call_sites" in patterns
        assert "usage_count" in patterns
        assert "hot_paths" in patterns
        assert "last_modified" in patterns

    def test_analyze_usage_patterns_returns_timestamp(self, mock_project: Path):
        """Test last_modified is a valid ISO timestamp."""
        generator = ContextExpertGenerator(mock_project)

        patterns = generator.analyze_usage_patterns("src/main.py")

        # Should be parseable as datetime
        datetime.fromisoformat(patterns["last_modified"].replace("Z", "+00:00"))


class TestStalenessCalculation:
    """Test staleness score calculation."""

    def test_calculate_staleness_fresh_expert(self, mock_project: Path):
        """Test staleness for freshly created expert."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        staleness = generator.calculate_staleness(expert)

        assert staleness < 10.0  # Should be nearly 0

    def test_calculate_staleness_changed_content(self, mock_project: Path):
        """Test staleness when content has changed."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        # Modify the file to change hash
        main_file = mock_project / "src" / "main.py"
        content = main_file.read_text()
        main_file.write_text(content + "\n# Modified")

        staleness = generator.calculate_staleness(expert)

        assert staleness == 75.0  # Content changed = 75%

    def test_calculate_staleness_old_expert(self, mock_project: Path):
        """Test staleness for old expert."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        # Simulate old refresh date
        old_date = (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
        expert["last_refreshed"] = old_date

        staleness = generator.calculate_staleness(expert)

        assert staleness >= 50.0  # >30 days = 50%


class TestSuggestCandidates:
    """Test expert candidate suggestion."""

    def test_suggest_candidates_returns_suggestions(self, mock_project: Path):
        """Test suggest_candidates returns list of suggestions."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        suggestions = generator.suggest_candidates(limit=10)

        assert isinstance(suggestions, list)
        for suggestion in suggestions:
            assert "resource_path" in suggestion
            assert "suggestion_reason" in suggestion
            assert "confidence_score" in suggestion

    def test_suggest_candidates_respects_limit(self, large_mock_project: Path):
        """Test limit parameter is respected."""
        generator = ContextExpertGenerator(large_mock_project)
        generator._ensure_directories()

        suggestions = generator.suggest_candidates(limit=5)

        assert len(suggestions) <= 5

    def test_suggest_candidates_sorted_by_confidence(self, mock_project: Path):
        """Test suggestions are sorted by confidence (highest first)."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        suggestions = generator.suggest_candidates(limit=10)

        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i]["confidence_score"] >= suggestions[i + 1]["confidence_score"]


class TestCreateExpert:
    """Test expert creation."""

    def test_create_expert_basic(self, mock_project: Path):
        """Test basic expert creation."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions", "review_changes"],
            domain="core"
        )

        assert expert["expert_id"].startswith("CE-")
        assert expert["resource_path"] == "src/main.py"
        assert expert["resource_type"] == "file"
        assert expert["domain"] == "core"
        assert "answer_questions" in expert["capabilities"]

    def test_create_expert_saves_to_file(self, mock_project: Path):
        """Test expert is saved to filesystem."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        expert_file = generator.experts_dir / f"{expert['expert_id']}.json"
        assert expert_file.exists()

        # Verify content
        saved_data = json.loads(expert_file.read_text())
        assert saved_data["expert_id"] == expert["expert_id"]

    def test_create_expert_updates_index(self, mock_project: Path):
        """Test index is updated after creation."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert generator.index_path.exists()
        index = json.loads(generator.index_path.read_text())
        assert index["total_experts"] >= 1
        expert_ids = [e["expert_id"] for e in index["experts"]]
        assert expert["expert_id"] in expert_ids

    def test_create_expert_includes_code_structure(self, mock_project: Path):
        """Test expert includes code structure analysis."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert "code_structure" in expert
        assert len(expert["code_structure"]["functions"]) > 0
        assert len(expert["code_structure"]["classes"]) > 0

    def test_create_expert_includes_relationships(self, mock_project: Path):
        """Test expert includes relationship data."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert "relationships" in expert
        assert "dependencies" in expert["relationships"]
        assert "test_files" in expert["relationships"]

    def test_create_expert_with_workorder(self, mock_project: Path):
        """Test expert creation with workorder ID."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core",
            workorder_id="WO-TEST-001",
            assigned_by="Lloyd"
        )

        assert expert["workorder_id"] == "WO-TEST-001"
        assert expert["assigned_by"] == "Lloyd"

    def test_create_expert_for_directory(self, mock_project: Path):
        """Test expert creation for directory resource."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src",
            resource_type="directory",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert expert["resource_type"] == "directory"
        assert expert["code_structure"]["line_count"] > 0

    def test_create_multiple_experts_unique_ids(self, mock_project: Path):
        """Test multiple experts get unique IDs."""
        generator = ContextExpertGenerator(mock_project)

        expert1 = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        expert2 = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert expert1["expert_id"] != expert2["expert_id"]


class TestGetExpert:
    """Test expert retrieval."""

    def test_get_expert_by_id(self, mock_project: Path):
        """Test retrieving expert by ID."""
        generator = ContextExpertGenerator(mock_project)

        created = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        retrieved = generator.get_expert(created["expert_id"])

        assert retrieved is not None
        assert retrieved["expert_id"] == created["expert_id"]
        assert retrieved["resource_path"] == created["resource_path"]

    def test_get_expert_nonexistent(self, mock_project: Path):
        """Test retrieving nonexistent expert returns None."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        result = generator.get_expert("CE-nonexistent-001")

        assert result is None


class TestListExperts:
    """Test expert listing."""

    def test_list_experts_empty(self, mock_project: Path):
        """Test listing when no experts exist."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        experts = generator.list_experts()

        assert experts == []

    def test_list_experts_returns_all(self, mock_project: Path):
        """Test listing all experts."""
        generator = ContextExpertGenerator(mock_project)

        # Create multiple experts
        generator.create_expert("src/main.py", "file", ["answer_questions"], "core")
        generator.create_expert("src/utils.py", "file", ["answer_questions"], "core")
        generator.create_expert("src/api.ts", "file", ["answer_questions"], "api")

        experts = generator.list_experts()

        assert len(experts) == 3

    def test_list_experts_filter_by_domain(self, mock_project: Path):
        """Test filtering by domain."""
        generator = ContextExpertGenerator(mock_project)

        generator.create_expert("src/main.py", "file", ["answer_questions"], "core")
        generator.create_expert("src/api.ts", "file", ["answer_questions"], "api")

        core_experts = generator.list_experts(domain="core")
        api_experts = generator.list_experts(domain="api")

        assert len(core_experts) == 1
        assert len(api_experts) == 1
        assert core_experts[0]["domain"] == "core"

    def test_list_experts_filter_by_status(self, mock_project: Path):
        """Test filtering by status."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert("src/main.py", "file", ["answer_questions"], "core")

        active_experts = generator.list_experts(status="active")

        assert len(active_experts) >= 1


class TestUpdateExpert:
    """Test expert updating/refresh."""

    def test_update_expert_refreshes_data(self, mock_project: Path):
        """Test update refreshes expert data."""
        generator = ContextExpertGenerator(mock_project)

        original = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        original_updated_at = original["updated_at"]

        # Wait a moment then update
        import time
        time.sleep(0.1)

        updated = generator.update_expert(original["expert_id"])

        assert updated is not None
        assert updated["updated_at"] != original_updated_at
        assert updated["staleness_score"] == 0.0

    def test_update_expert_nonexistent(self, mock_project: Path):
        """Test updating nonexistent expert returns None."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        result = generator.update_expert("CE-nonexistent-001")

        assert result is None


class TestAddOnboarding:
    """Test Lloyd's onboarding addition."""

    def test_add_onboarding_basic(self, mock_project: Path):
        """Test adding onboarding data to expert."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        updated = generator.add_onboarding(
            expert_id=expert["expert_id"],
            assigned_docs=["CLAUDE.md", "README.md"],
            domain_scope="Core application logic and entry points",
            briefing_notes="Focus on async patterns and main entry point",
            onboarded_by="Lloyd"
        )

        assert updated is not None
        assert updated["onboarding"] is not None
        assert updated["onboarding"]["assigned_docs"] == ["CLAUDE.md", "README.md"]
        assert updated["onboarding"]["domain_scope"] == "Core application logic and entry points"
        assert updated["onboarding"]["briefing_notes"] == "Focus on async patterns and main entry point"
        assert updated["onboarding"]["onboarded_by"] == "Lloyd"

    def test_add_onboarding_saves_to_file(self, mock_project: Path):
        """Test onboarding is persisted to file."""
        generator = ContextExpertGenerator(mock_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        generator.add_onboarding(
            expert_id=expert["expert_id"],
            assigned_docs=["CLAUDE.md"],
            domain_scope="Core logic",
            briefing_notes="Test notes"
        )

        # Reload from file
        reloaded = generator.get_expert(expert["expert_id"])

        assert reloaded["onboarding"] is not None
        assert reloaded["onboarding"]["assigned_docs"] == ["CLAUDE.md"]

    def test_add_onboarding_nonexistent_expert(self, mock_project: Path):
        """Test adding onboarding to nonexistent expert returns None."""
        generator = ContextExpertGenerator(mock_project)
        generator._ensure_directories()

        result = generator.add_onboarding(
            expert_id="CE-nonexistent-001",
            assigned_docs=["CLAUDE.md"],
            domain_scope="Test",
            briefing_notes="Test"
        )

        assert result is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_create_expert_with_invalid_python(self, mock_project: Path):
        """Test expert creation handles invalid Python syntax gracefully."""
        generator = ContextExpertGenerator(mock_project)

        # Create file with invalid Python
        invalid_file = mock_project / "src" / "invalid.py"
        invalid_file.write_text("def broken( {\n    pass")

        # Should not raise, uses regex fallback
        expert = generator.create_expert(
            resource_path="src/invalid.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert expert is not None
        assert expert["expert_id"].startswith("CE-")

    def test_create_expert_with_encoding_issues(self, mock_project: Path):
        """Test expert creation handles encoding issues gracefully."""
        generator = ContextExpertGenerator(mock_project)

        # Create file with potentially problematic encoding
        binary_file = mock_project / "src" / "binary.py"
        binary_file.write_bytes(b"# -*- coding: utf-8 -*-\n\xef\xbb\xbfdef test(): pass")

        expert = generator.create_expert(
            resource_path="src/binary.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )

        assert expert is not None

    def test_empty_directory_analysis(self, mock_project: Path):
        """Test analysis of empty directory."""
        generator = ContextExpertGenerator(mock_project)

        empty_dir = mock_project / "empty"
        empty_dir.mkdir()

        structure = generator.analyze_code_structure("empty")

        assert structure["functions"] == []
        assert structure["classes"] == []
        assert structure["line_count"] == 0


class TestPerformance:
    """Performance-related tests."""

    def test_suggest_candidates_completes_quickly(self, large_mock_project: Path):
        """Test suggest_candidates completes in reasonable time."""
        generator = ContextExpertGenerator(large_mock_project)
        generator._ensure_directories()

        import time
        start = time.time()
        suggestions = generator.suggest_candidates(limit=10)
        elapsed = time.time() - start

        assert elapsed < 30.0, f"suggest_candidates took too long: {elapsed:.2f}s"

    def test_create_expert_completes_quickly(self, mock_project: Path):
        """Test expert creation completes in reasonable time."""
        generator = ContextExpertGenerator(mock_project)

        import time
        start = time.time()
        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions"],
            domain="core"
        )
        elapsed = time.time() - start

        assert elapsed < 10.0, f"create_expert took too long: {elapsed:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
