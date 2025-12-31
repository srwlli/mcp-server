"""
Pytest configuration and shared fixtures for bug-fixes-testing.

Workorder: WO-BUG-FIXES-TESTING-001
"""
import os
import tempfile
import shutil
from pathlib import Path
import pytest
import json


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_workorder_")
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_git_repo(temp_project_dir):
    """Create a mock git repository."""
    git_dir = temp_project_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n\trepositoryformatversion = 0\n")
    return temp_project_dir


@pytest.fixture
def non_git_repo(temp_project_dir):
    """Create a non-git directory."""
    return temp_project_dir


@pytest.fixture
def mock_context_json():
    """Return a valid context.json structure."""
    return {
        "feature_name": "test-feature",
        "description": "Test feature description",
        "goal": "Test goal",
        "requirements": ["Requirement 1", "Requirement 2"],
        "out_of_scope": [],
        "constraints": []
    }


@pytest.fixture
def mock_context_json_invalid():
    """Return an invalid context.json (missing required fields)."""
    return {
        "feature_name": "test-feature",
        "description": "",
        "goal": "",
        "requirements": [],
        "out_of_scope": [],
        "constraints": []
    }


@pytest.fixture
def mock_plan_json():
    """Return a valid plan.json structure."""
    return {
        "META_DOCUMENTATION": {
            "feature_name": "test-feature",
            "workorder_id": "WO-TEST-001",
            "version": "1.0.0",
            "status": "planning"
        },
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "6_implementation_phases": {
                "phases": [
                    {
                        "phase": 1,
                        "name": "Phase 1",
                        "title": "Test Phase",
                        "tasks": ["TASK-001"],
                        "deliverables": ["deliverable1"]
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_workorder_log_path(temp_project_dir):
    """Create and return path to mock workorder-log.txt."""
    log_file = temp_project_dir / "coderef" / "workorder-log.txt"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("")
    return log_file


@pytest.fixture
def create_context_file(temp_project_dir):
    """Factory fixture to create context.json files."""
    def _create(content):
        workorder_dir = temp_project_dir / "coderef" / "workorder" / "test-feature"
        workorder_dir.mkdir(parents=True, exist_ok=True)
        context_file = workorder_dir / "context.json"
        context_file.write_text(json.dumps(content, indent=2))
        return context_file
    return _create


@pytest.fixture
def create_plan_file(temp_project_dir):
    """Factory fixture to create plan.json files."""
    def _create(content):
        workorder_dir = temp_project_dir / "coderef" / "workorder" / "test-feature"
        workorder_dir.mkdir(parents=True, exist_ok=True)
        plan_file = workorder_dir / "plan.json"
        plan_file.write_text(json.dumps(content, indent=2))
        return plan_file
    return _create


@pytest.fixture
def large_codebase(temp_project_dir):
    """Create a mock large codebase (>50k LOC)."""
    src_dir = temp_project_dir / "src"
    src_dir.mkdir()

    # Create 100 files with 600 lines each = 60k LOC
    for i in range(100):
        file_path = src_dir / f"module_{i}.py"
        content = "\n".join([f"# Line {j}" for j in range(600)])
        file_path.write_text(content)

    return temp_project_dir


@pytest.fixture
def mock_validation_result_low_score():
    """Return a validation result with score < 90."""
    return {
        "validation_result": "FAIL",
        "score": 65,
        "issues": [
            {"severity": "major", "issue": "Missing field X"},
            {"severity": "minor", "issue": "Incomplete description"}
        ],
        "approved": False
    }


@pytest.fixture
def mock_validation_result_high_score():
    """Return a validation result with score >= 90."""
    return {
        "validation_result": "PASS",
        "score": 95,
        "issues": [],
        "approved": True
    }
