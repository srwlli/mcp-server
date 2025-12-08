"""
Integration tests for Context Expert workflow.

Tests the full workflow of creating, listing, and managing multiple context experts,
specifically designed to identify loop issues when creating more than 1 expert.

Part of WO-LLOYD-CONTEXT-EXPERT-INTEGRATION-001.
"""

import asyncio
import json
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any
import pytest
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generators.context_expert_generator import ContextExpertGenerator


class TestContextExpertWorkflow:
    """Test suite for context expert creation workflow."""

    @pytest.fixture
    def temp_project(self, tmp_path: Path) -> Path:
        """Create a temporary project structure for testing."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create some source files to analyze
        src_dir = project_dir / "src"
        src_dir.mkdir()

        # Python file
        (src_dir / "main.py").write_text("""
\"\"\"Main application module.\"\"\"

import os
from typing import List

class Application:
    \"\"\"Main application class.\"\"\"

    def __init__(self):
        self.name = "TestApp"

    def run(self):
        \"\"\"Run the application.\"\"\"
        print("Running...")

async def main():
    \"\"\"Entry point.\"\"\"
    app = Application()
    app.run()

if __name__ == "__main__":
    asyncio.run(main())
""")

        # Another Python file
        (src_dir / "utils.py").write_text("""
\"\"\"Utility functions.\"\"\"

def helper_function(x: int) -> int:
    \"\"\"A helper function.\"\"\"
    return x * 2

def another_helper(y: str) -> str:
    \"\"\"Another helper.\"\"\"
    return y.upper()

class UtilityClass:
    \"\"\"A utility class.\"\"\"
    pass
""")

        # TypeScript file
        (src_dir / "api.ts").write_text("""
import { Request, Response } from 'express';

export class ApiHandler {
    async handleRequest(req: Request, res: Response) {
        res.json({ status: 'ok' });
    }
}

export const getHealth = () => ({ healthy: true });
""")

        # Create tests directory
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("""
import pytest
from src.main import Application

def test_application():
    app = Application()
    assert app.name == "TestApp"
""")

        # Initialize git repo (optional but enables git history features)
        import subprocess
        try:
            subprocess.run(["git", "init"], cwd=str(project_dir), capture_output=True, check=True)
            subprocess.run(["git", "add", "."], cwd=str(project_dir), capture_output=True, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=str(project_dir),
                capture_output=True,
                check=True,
                env={**dict(os.environ), 'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@test.com',
                     'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@test.com'}
            )
        except Exception:
            pass  # Git not available, continue without

        return project_dir

    def test_create_single_expert(self, temp_project: Path):
        """Test creating a single context expert."""
        generator = ContextExpertGenerator(temp_project)

        expert = generator.create_expert(
            resource_path="src/main.py",
            resource_type="file",
            capabilities=["answer_questions", "review_changes"],
            domain="core"
        )

        assert expert is not None
        assert expert["expert_id"].startswith("CE-")
        assert expert["resource_path"] == "src/main.py"
        assert expert["domain"] == "core"
        assert "code_structure" in expert
        assert len(expert["code_structure"]["functions"]) > 0
        assert len(expert["code_structure"]["classes"]) > 0

    def test_create_multiple_experts_sequentially(self, temp_project: Path):
        """
        Test creating multiple experts sequentially - this is the core test for the loop issue.

        This test should complete within reasonable time. If it hangs or loops,
        there's an issue with the expert creation workflow.
        """
        generator = ContextExpertGenerator(temp_project)

        files_to_create = [
            ("src/main.py", "core"),
            ("src/utils.py", "core"),
            ("src/api.ts", "api"),
        ]

        created_experts: List[Dict[str, Any]] = []
        creation_times: List[float] = []

        for resource_path, domain in files_to_create:
            start_time = time.time()

            expert = generator.create_expert(
                resource_path=resource_path,
                resource_type="file",
                capabilities=["answer_questions", "review_changes"],
                domain=domain
            )

            elapsed = time.time() - start_time
            creation_times.append(elapsed)
            created_experts.append(expert)

            print(f"Created expert {expert['expert_id']} in {elapsed:.2f}s")

        # Verify all experts were created
        assert len(created_experts) == 3

        # Verify unique IDs
        expert_ids = [e["expert_id"] for e in created_experts]
        assert len(set(expert_ids)) == 3, f"Expected unique IDs, got: {expert_ids}"

        # Verify reasonable creation times (no looping)
        for i, elapsed in enumerate(creation_times):
            assert elapsed < 30.0, f"Expert {i+1} took too long: {elapsed:.2f}s (possible loop)"

        # Total time should be reasonable
        total_time = sum(creation_times)
        assert total_time < 60.0, f"Total creation time too long: {total_time:.2f}s"

        print(f"\nAll {len(created_experts)} experts created successfully in {total_time:.2f}s total")

    def test_create_multiple_experts_with_same_prefix(self, temp_project: Path):
        """
        Test creating multiple experts with similar paths to verify ID generation doesn't loop.
        """
        generator = ContextExpertGenerator(temp_project)

        # Create files with similar names
        src_dir = temp_project / "src"
        (src_dir / "handler.py").write_text("def handle(): pass")
        (src_dir / "handler_auth.py").write_text("def auth_handle(): pass")
        (src_dir / "handler_api.py").write_text("def api_handle(): pass")

        files = [
            "src/handler.py",
            "src/handler_auth.py",
            "src/handler_api.py",
        ]

        experts = []
        for f in files:
            expert = generator.create_expert(
                resource_path=f,
                resource_type="file",
                capabilities=["answer_questions"],
                domain="api"
            )
            experts.append(expert)
            print(f"Created: {expert['expert_id']}")

        # Verify unique IDs
        ids = [e["expert_id"] for e in experts]
        assert len(set(ids)) == 3, f"IDs not unique: {ids}"

    def test_list_experts_after_creation(self, temp_project: Path):
        """Test listing experts after creating multiple."""
        generator = ContextExpertGenerator(temp_project)

        # Create 3 experts
        for resource in ["src/main.py", "src/utils.py", "src/api.ts"]:
            generator.create_expert(
                resource_path=resource,
                resource_type="file",
                capabilities=["answer_questions"],
                domain="core"
            )

        # List all experts
        experts = generator.list_experts()
        assert len(experts) == 3

        # Verify each has required fields
        for expert in experts:
            assert "expert_id" in expert
            assert "name" in expert
            assert "resource_path" in expert
            assert "domain" in expert

    def test_suggest_and_create_workflow(self, temp_project: Path):
        """
        Test the full workflow: suggest → create multiple experts.

        This simulates what /start-feature does after project analysis.
        """
        generator = ContextExpertGenerator(temp_project)

        # Step 1: Get suggestions
        suggestions = generator.suggest_candidates(limit=5)
        print(f"Got {len(suggestions)} suggestions")

        # Step 2: Create experts for suggestions
        created = []
        for suggestion in suggestions[:3]:  # Create first 3
            expert = generator.create_expert(
                resource_path=suggestion["resource_path"],
                resource_type=suggestion["resource_type"],
                capabilities=["answer_questions", "review_changes"],
                domain="core"  # Simplified domain selection
            )
            created.append(expert)
            print(f"Created expert for: {suggestion['resource_path']}")

        # Verify
        assert len(created) == min(3, len(suggestions))

        # Verify index is updated
        all_experts = generator.list_experts()
        assert len(all_experts) == len(created)

    def test_create_expert_idempotency(self, temp_project: Path):
        """
        Test that creating an expert for the same file creates a new expert with different ID.

        Note: Current implementation creates new experts (not idempotent).
        This test documents the behavior.
        """
        generator = ContextExpertGenerator(temp_project)

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

        # Current behavior: creates new expert with incremented ID
        assert expert1["expert_id"] != expert2["expert_id"]
        print(f"Expert 1: {expert1['expert_id']}, Expert 2: {expert2['expert_id']}")

    def test_expert_id_generation_no_infinite_loop(self, temp_project: Path):
        """
        Direct test of ID generation to verify no infinite loops.

        Creates 10 experts for the same file to stress test ID generation.
        """
        generator = ContextExpertGenerator(temp_project)

        ids = []
        start_time = time.time()

        for i in range(10):
            expert = generator.create_expert(
                resource_path="src/main.py",
                resource_type="file",
                capabilities=["answer_questions"],
                domain="core"
            )
            ids.append(expert["expert_id"])

            # Safety check: if we're taking too long, there's a loop
            elapsed = time.time() - start_time
            if elapsed > 30:
                pytest.fail(f"ID generation taking too long ({elapsed:.2f}s) - possible infinite loop")

        # Verify all IDs are unique
        assert len(set(ids)) == 10, f"IDs not unique: {ids}"

        # Verify sequential numbering
        for i, id_ in enumerate(ids, 1):
            assert f"-{i:03d}" in id_, f"Expected sequential numbering, got: {id_}"

        print(f"Created 10 experts with IDs: {ids}")


class TestContextExpertGeneratorPerformance:
    """Performance tests for context expert generator."""

    @pytest.fixture
    def large_project(self, tmp_path: Path) -> Path:
        """Create a larger project for performance testing."""
        project_dir = tmp_path / "large-project"
        project_dir.mkdir()

        # Create many files
        src_dir = project_dir / "src"
        src_dir.mkdir()

        for i in range(20):
            (src_dir / f"module_{i}.py").write_text(f"""
\"\"\"Module {i}.\"\"\"

def function_{i}():
    return {i}

class Class_{i}:
    pass
""")

        return project_dir

    def test_suggest_candidates_performance(self, large_project: Path):
        """Test that suggest_candidates completes in reasonable time."""
        generator = ContextExpertGenerator(large_project)

        start_time = time.time()
        suggestions = generator.suggest_candidates(limit=10)
        elapsed = time.time() - start_time

        print(f"Got {len(suggestions)} suggestions in {elapsed:.2f}s")
        assert elapsed < 30.0, f"suggest_candidates took too long: {elapsed:.2f}s"

    def test_batch_expert_creation_performance(self, large_project: Path):
        """Test creating multiple experts in batch."""
        generator = ContextExpertGenerator(large_project)

        files = [f"src/module_{i}.py" for i in range(5)]

        start_time = time.time()
        for f in files:
            generator.create_expert(
                resource_path=f,
                resource_type="file",
                capabilities=["answer_questions"],
                domain="core"
            )
        elapsed = time.time() - start_time

        print(f"Created 5 experts in {elapsed:.2f}s ({elapsed/5:.2f}s per expert)")
        assert elapsed < 60.0, f"Batch creation took too long: {elapsed:.2f}s"


# Import os for git environment setup
import os


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
