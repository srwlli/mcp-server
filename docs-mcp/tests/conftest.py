"""
Shared pytest fixtures for docs-mcp test suite.

Provides common fixtures for:
- Temporary project structures
- Mock project with sample files
- Async event loop configuration
- Generator instances
- Path helpers

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Generator, List
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# PATH FIXTURES
# ============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return the docs-mcp project root directory."""
    return Path(__file__).parent.parent


# ============================================================================
# TEMPORARY PROJECT FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary directory for each test."""
    return tmp_path


@pytest.fixture
def mock_project(tmp_path: Path) -> Path:
    """
    Create a mock project structure for testing.

    Structure:
    - src/
      - main.py (Python with classes, functions, async)
      - utils.py (Python utilities)
      - api.ts (TypeScript API)
      - components/
        - Button.tsx (React component)
    - tests/
      - test_main.py
    - docs/
      - README.md
    - coderef/
      - changelog/
        - CHANGELOG.json
        - schema.json
      - working/
      - context-experts/
        - experts/
        - cache/
    - pyproject.toml
    - .git/ (initialized)
    """
    project_dir = tmp_path / "mock-project"
    project_dir.mkdir()

    # Create source directory
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Python main file
    (src_dir / "main.py").write_text('''"""
Main application module.

Provides core functionality for the application.
"""

import asyncio
from typing import List, Optional

class Application:
    """Main application class."""

    def __init__(self, name: str = "TestApp"):
        self.name = name
        self.config: dict = {}

    def run(self) -> None:
        """Run the application."""
        print(f"Running {self.name}...")

    async def async_run(self) -> str:
        """Async run method."""
        await asyncio.sleep(0.1)
        return "completed"

async def main() -> None:
    """Entry point."""
    app = Application()
    await app.async_run()

def helper_function(x: int) -> int:
    """Simple helper function."""
    return x * 2

if __name__ == "__main__":
    asyncio.run(main())
''')

    # Python utils file
    (src_dir / "utils.py").write_text('''"""
Utility functions module.
"""

from typing import List, Dict, Any

def format_string(text: str) -> str:
    """Format a string."""
    return text.strip().upper()

def calculate_total(items: List[int]) -> int:
    """Calculate sum of items."""
    return sum(items)

class Validator:
    """Input validator class."""

    @staticmethod
    def is_valid(value: Any) -> bool:
        """Check if value is valid."""
        return value is not None
''')

    # TypeScript API file
    (src_dir / "api.ts").write_text('''import { Request, Response } from 'express';

export interface ApiResponse {
    status: string;
    data?: any;
    error?: string;
}

export class ApiHandler {
    async handleRequest(req: Request, res: Response): Promise<void> {
        res.json({ status: 'ok' });
    }

    async handleError(error: Error): Promise<ApiResponse> {
        return { status: 'error', error: error.message };
    }
}

export const getHealth = (): ApiResponse => ({ status: 'healthy' });

export default ApiHandler;
''')

    # React component directory
    components_dir = src_dir / "components"
    components_dir.mkdir()

    (components_dir / "Button.tsx").write_text('''import React from 'react';

interface ButtonProps {
    label: string;
    onClick: () => void;
    disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, disabled }) => {
    return (
        <button onClick={onClick} disabled={disabled}>
            {label}
        </button>
    );
};

export default Button;
''')

    # Tests directory
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    (tests_dir / "test_main.py").write_text('''import pytest
from src.main import Application, helper_function

def test_application_init():
    app = Application()
    assert app.name == "TestApp"

def test_application_custom_name():
    app = Application(name="CustomApp")
    assert app.name == "CustomApp"

def test_helper_function():
    assert helper_function(5) == 10
    assert helper_function(0) == 0

@pytest.mark.asyncio
async def test_async_run():
    app = Application()
    result = await app.async_run()
    assert result == "completed"
''')

    # Docs directory
    docs_dir = project_dir / "docs"
    docs_dir.mkdir()

    (docs_dir / "README.md").write_text('''# Mock Project

A test project for docs-mcp test suite.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install mock-project
```
''')

    # Coderef directory structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()

    changelog_dir = coderef_dir / "changelog"
    changelog_dir.mkdir()

    # Create empty changelog
    changelog_data = {
        "project_name": "mock-project",
        "versions": []
    }
    (changelog_dir / "CHANGELOG.json").write_text(json.dumps(changelog_data, indent=2))

    # Create changelog schema
    schema_data = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["project_name", "versions"],
        "properties": {
            "project_name": {"type": "string"},
            "versions": {"type": "array"}
        }
    }
    (changelog_dir / "schema.json").write_text(json.dumps(schema_data, indent=2))

    # Working directory
    working_dir = coderef_dir / "working"
    working_dir.mkdir()

    # Context experts directories
    experts_root = coderef_dir / "context-experts"
    experts_root.mkdir()
    (experts_root / "experts").mkdir()
    (experts_root / "cache").mkdir()

    # Foundation docs directory
    foundation_dir = coderef_dir / "foundation-docs"
    foundation_dir.mkdir()

    # Standards directory
    standards_dir = coderef_dir / "standards"
    standards_dir.mkdir()

    # Inventory directory
    inventory_dir = coderef_dir / "inventory"
    inventory_dir.mkdir()

    # Create pyproject.toml
    (project_dir / "pyproject.toml").write_text('''[project]
name = "mock-project"
version = "1.0.0"
description = "Mock project for testing"
requires-python = ">=3.10"

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]
''')

    # Initialize git repo
    _init_git_repo(project_dir)

    return project_dir


@pytest.fixture
def mock_project_with_history(mock_project: Path) -> Path:
    """
    Extend mock_project with git commit history.

    Adds 3 commits with file changes for testing git history analysis.
    """
    git_env = {
        **os.environ,
        'GIT_AUTHOR_NAME': 'Test Author',
        'GIT_AUTHOR_EMAIL': 'test@test.com',
        'GIT_COMMITTER_NAME': 'Test Author',
        'GIT_COMMITTER_EMAIL': 'test@test.com'
    }

    # Commit 1: Add new feature
    (mock_project / "src" / "feature.py").write_text('''"""New feature module."""

def new_feature():
    return "feature"
''')
    subprocess.run(["git", "add", "."], cwd=str(mock_project), capture_output=True, env=git_env)
    subprocess.run(
        ["git", "commit", "-m", "Add new feature module"],
        cwd=str(mock_project), capture_output=True, env=git_env
    )

    # Commit 2: Update main
    main_path = mock_project / "src" / "main.py"
    content = main_path.read_text()
    content += "\n# Updated with new functionality\n"
    main_path.write_text(content)
    subprocess.run(["git", "add", "."], cwd=str(mock_project), capture_output=True, env=git_env)
    subprocess.run(
        ["git", "commit", "-m", "Update main module"],
        cwd=str(mock_project), capture_output=True, env=git_env
    )

    # Commit 3: Fix bug
    utils_path = mock_project / "src" / "utils.py"
    content = utils_path.read_text()
    content += "\n# Bug fix applied\n"
    utils_path.write_text(content)
    subprocess.run(["git", "add", "."], cwd=str(mock_project), capture_output=True, env=git_env)
    subprocess.run(
        ["git", "commit", "-m", "Fix bug in utils"],
        cwd=str(mock_project), capture_output=True, env=git_env
    )

    return mock_project


def _init_git_repo(project_dir: Path) -> bool:
    """Initialize a git repository in the project directory."""
    git_env = {
        **os.environ,
        'GIT_AUTHOR_NAME': 'Test Author',
        'GIT_AUTHOR_EMAIL': 'test@test.com',
        'GIT_COMMITTER_NAME': 'Test Author',
        'GIT_COMMITTER_EMAIL': 'test@test.com'
    }

    try:
        subprocess.run(["git", "init"], cwd=str(project_dir), capture_output=True, check=True)
        subprocess.run(["git", "add", "."], cwd=str(project_dir), capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(project_dir), capture_output=True, check=True, env=git_env
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@pytest.fixture
def large_mock_project(tmp_path: Path) -> Path:
    """
    Create a larger mock project for performance testing.

    Contains 100+ files across multiple directories.
    """
    project_dir = tmp_path / "large-project"
    project_dir.mkdir()

    # Create multiple source directories
    for i in range(10):
        module_dir = project_dir / "src" / f"module_{i}"
        module_dir.mkdir(parents=True)

        # Create multiple files per module
        for j in range(10):
            (module_dir / f"file_{j}.py").write_text(f'''"""Module {i}, File {j}."""

def function_{i}_{j}():
    """Function in module {i}, file {j}."""
    return {i * 10 + j}

class Class_{i}_{j}:
    """Class in module {i}, file {j}."""

    def method(self):
        return "method"
''')

    # Create test files
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()
    for i in range(5):
        (tests_dir / f"test_module_{i}.py").write_text(f'''import pytest

def test_function_{i}():
    assert True
''')

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()
    (coderef_dir / "context-experts").mkdir()
    (coderef_dir / "context-experts" / "experts").mkdir()
    (coderef_dir / "context-experts" / "cache").mkdir()

    # Initialize git
    _init_git_repo(project_dir)

    return project_dir


# ============================================================================
# GENERATOR FIXTURES
# ============================================================================

@pytest.fixture
def context_expert_generator(mock_project: Path):
    """Create a ContextExpertGenerator instance for testing."""
    from generators.context_expert_generator import ContextExpertGenerator
    return ContextExpertGenerator(mock_project)


@pytest.fixture
def foundation_generator(mock_project: Path):
    """Create a FoundationGenerator instance for testing."""
    from generators.foundation_generator import FoundationGenerator
    return FoundationGenerator(mock_project)


@pytest.fixture
def changelog_generator(mock_project: Path):
    """Create a ChangelogGenerator instance for testing."""
    from generators.changelog_generator import ChangelogGenerator
    return ChangelogGenerator(mock_project)


@pytest.fixture
def planning_generator(mock_project: Path):
    """Create a PlanningGenerator instance for testing."""
    from generators.planning_generator import PlanningGenerator
    return PlanningGenerator(mock_project)


# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_changelog_entry() -> Dict[str, Any]:
    """Provide a valid changelog entry for testing."""
    return {
        "version": "1.0.1",
        "change_type": "feature",
        "severity": "minor",
        "title": "Add new feature",
        "description": "Added a new feature to improve functionality",
        "files": ["src/main.py", "src/utils.py"],
        "reason": "User requested this feature",
        "impact": "Users can now do more things",
        "breaking": False,
        "contributors": ["Test User"]
    }


@pytest.fixture
def sample_context_json() -> Dict[str, Any]:
    """Provide a sample context.json for planning workflow testing."""
    return {
        "feature_name": "test-feature",
        "description": "A test feature for testing purposes",
        "goal": "Test the planning workflow",
        "requirements": [
            "Requirement 1: Must do something",
            "Requirement 2: Must do something else"
        ],
        "constraints": ["Must be fast", "Must be secure"],
        "out_of_scope": ["Advanced features"],
        "success_criteria": {
            "functional": ["All tests pass"],
            "quality": ["80%+ coverage"]
        },
        "gathered_at": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def sample_plan_json() -> Dict[str, Any]:
    """Provide a sample plan.json for testing."""
    return {
        "META_DOCUMENTATION": {
            "feature_name": "test-feature",
            "schema_version": "1.0.0",
            "version": "1.0.0",
            "status": "complete",
            "generated_by": "Test",
            "generated_at": datetime.now(timezone.utc).isoformat()
        },
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "1_executive_summary": {
                "feature_name": "Test Feature",
                "description": "A test feature",
                "goal": "Testing",
                "scope": "Unit tests"
            },
            "5_task_id_system": {
                "workorder": {
                    "id": "WO-TEST-001",
                    "name": "Test Workorder",
                    "feature_dir": "coderef/working/test-feature"
                },
                "tasks": [
                    {
                        "id": "TASK-001",
                        "description": "First task",
                        "priority": "P0"
                    }
                ]
            },
            "9_implementation_checklist": {
                "phase_1_checklist": ["[ ] Task 1", "[ ] Task 2"]
            }
        }
    }


# ============================================================================
# ASYNC FIXTURES
# ============================================================================

@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(request):
    """Cleanup fixture that runs after each test."""
    yield
    # Add any cleanup logic here if needed


# ============================================================================
# MARKER HELPERS
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
