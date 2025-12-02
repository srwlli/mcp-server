"""
Unit tests for TodoListGenerator

Part of docs-expert v2.0 Phase 1: Lloyd Integration
"""

import json
import pytest
from pathlib import Path
from src.generators.todo_list_generator import TodoListGenerator


@pytest.fixture
def sample_plan():
    """Sample implementation plan for testing"""
    return {
        "workorder_id": "WO-AUTH-001",
        "feature_name": "authentication",
        "task_breakdown": [
            {
                "task_id": 1,
                "description": "Create authentication middleware",
                "files": ["src/middleware/auth.ts"],
                "acceptance_criteria": [
                    "Middleware validates JWT",
                    "Returns 401 on invalid token"
                ],
                "estimated_time": "3 hours",
                "dependencies": []
            },
            {
                "task_id": 2,
                "description": "Add login endpoint",
                "files": ["src/routes/auth.ts"],
                "acceptance_criteria": [
                    "Returns JWT on success",
                    "Rate limited to 10 req/min"
                ],
                "estimated_time": "2 hours",
                "dependencies": []
            },
            {
                "task_id": 3,
                "description": "Write unit tests",
                "files": ["tests/auth.test.ts"],
                "acceptance_criteria": [
                    "90% code coverage",
                    "All edge cases tested"
                ],
                "estimated_time": "2 hours",
                "dependencies": [1, 2]
            }
        ]
    }


@pytest.fixture
def sample_plan_with_completion(sample_plan):
    """Sample plan with some tasks completed"""
    plan = sample_plan.copy()
    plan['task_breakdown'][0]['execution_status'] = {
        'status': 'completed',
        'completed_at': '2025-10-18T10:30:00Z'
    }
    return plan


@pytest.fixture
def sample_quick_plan():
    """Sample quick plan for testing"""
    return {
        "workorder_id": "WO-ADD-FIELD-001",
        "feature_name": "add-field",
        "plan": {
            "context": {
                "what": "Add tags field",
                "why": "Enable categorization"
            },
            "tasks": [
                {
                    "task_id": 1,
                    "description": "Update schema",
                    "files": ["src/models.py"],
                    "acceptance_criteria": ["Schema valid"]
                },
                {
                    "task_id": 2,
                    "description": "Update docs",
                    "files": ["README.md"],
                    "acceptance_criteria": ["Docs complete"]
                }
            ]
        }
    }


@pytest.fixture
def temp_plan_file(tmp_path, sample_plan):
    """Create temporary plan file for testing"""
    plan_file = tmp_path / "plan.json"
    with open(plan_file, 'w') as f:
        json.dump(sample_plan, f)
    return plan_file


class TestTodoListGenerator:
    """Test suite for TodoListGenerator"""

    def test_generate_todo_list_all_mode(self, temp_plan_file):
        """Test generating todos for all tasks"""
        generator = TodoListGenerator()
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-AUTH-001",
            mode="all"
        )

        assert result['workorder_id'] == "WO-AUTH-001"
        assert result['total_tasks'] == 3
        assert len(result['todos']) == 3
        assert result['mode'] == "all"
        assert 'generated_at' in result
        assert 'summary' in result

    def test_generate_todo_list_remaining_mode(self, tmp_path, sample_plan_with_completion):
        """Test generating todos for remaining tasks only"""
        plan_file = tmp_path / "plan.json"
        with open(plan_file, 'w') as f:
            json.dump(sample_plan_with_completion, f)

        generator = TodoListGenerator()
        result = generator.generate_todo_list(
            str(plan_file),
            "WO-AUTH-001",
            mode="remaining"
        )

        # Only 2 tasks remaining (task 1 is completed)
        assert result['total_tasks'] == 2
        assert len(result['todos']) == 2

    def test_todo_format(self, temp_plan_file):
        """Test todo format is correct"""
        generator = TodoListGenerator()
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-AUTH-001"
        )

        todo = result['todos'][0]

        # Check required fields
        assert 'content' in todo
        assert 'activeForm' in todo
        assert 'status' in todo
        assert 'metadata' in todo

        # Check metadata
        assert todo['metadata']['workorder_id'] == "WO-AUTH-001"
        assert todo['metadata']['task_id'] == 1
        assert isinstance(todo['metadata']['acceptance_criteria'], list)
        assert len(todo['metadata']['acceptance_criteria']) == 2

    def test_imperative_to_active_conversion(self, temp_plan_file):
        """Test conversion of imperative to active form"""
        generator = TodoListGenerator()
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-AUTH-001"
        )

        todo = result['todos'][0]

        # "Create authentication middleware" → "Creating authentication middleware"
        assert todo['content'] == "Create authentication middleware"
        assert todo['activeForm'] == "Creating authentication middleware"

    def test_workorder_id_required(self, temp_plan_file):
        """Test that workorder ID is required"""
        generator = TodoListGenerator()

        with pytest.raises(ValueError, match="Workorder ID is required"):
            generator.generate_todo_list(str(temp_plan_file), "")

    def test_plan_file_not_found(self):
        """Test handling of missing plan file"""
        generator = TodoListGenerator()

        with pytest.raises(FileNotFoundError):
            generator.generate_todo_list("/nonexistent/plan.json", "WO-TEST-001")

    def test_invalid_json(self, tmp_path):
        """Test handling of invalid JSON"""
        plan_file = tmp_path / "invalid.json"
        with open(plan_file, 'w') as f:
            f.write("{ invalid json }")

        generator = TodoListGenerator()

        with pytest.raises(ValueError, match="Invalid JSON"):
            generator.generate_todo_list(str(plan_file), "WO-TEST-001")

    def test_workorder_id_mismatch(self, temp_plan_file):
        """Test handling of workorder ID mismatch"""
        generator = TodoListGenerator()

        with pytest.raises(ValueError, match="Workorder ID mismatch"):
            generator.generate_todo_list(str(temp_plan_file), "WO-WRONG-001")

    def test_no_task_breakdown(self, tmp_path):
        """Test handling of plan with no task breakdown"""
        plan_file = tmp_path / "no_tasks.json"
        with open(plan_file, 'w') as f:
            json.dump({"workorder_id": "WO-TEST-001"}, f)

        generator = TodoListGenerator()

        with pytest.raises(ValueError, match="No task breakdown found"):
            generator.generate_todo_list(str(plan_file), "WO-TEST-001")

    def test_imperative_form_conversion(self):
        """Test imperative form conversions"""
        generator = TodoListGenerator()

        test_cases = [
            ("Implementing JWT validation", "Implement JWT validation"),
            ("Creating middleware", "Create middleware"),
            ("Adding tests", "Add tests"),
            ("Writing docs", "Write docs"),
            ("Updating schema", "Update schema"),
            ("Testing endpoints", "Test endpoints"),
            ("Already imperative", "Already imperative")
        ]

        for input_desc, expected in test_cases:
            result = generator._to_imperative_form(input_desc)
            assert result == expected, f"Failed for: {input_desc}"

    def test_active_form_conversion(self):
        """Test active form conversions"""
        generator = TodoListGenerator()

        test_cases = [
            ("Implement JWT validation", "Implementing JWT validation"),
            ("Create middleware", "Creating middleware"),
            ("Add tests", "Adding tests"),
            ("Write docs", "Writing docs"),
            ("Update schema", "Updating schema"),
            ("Test endpoints", "Testing endpoints"),
            ("Fix bug", "Fixing bug"),
            ("Remove feature", "Removing feature"),
            ("Refactor code", "Refactoring code")
        ]

        for input_desc, expected in test_cases:
            result = generator._to_active_form(input_desc)
            assert result == expected, f"Failed for: {input_desc}"

    def test_generate_from_quick_plan(self, tmp_path, sample_quick_plan):
        """Test generating todos from quick plan format"""
        plan_file = tmp_path / "quick-plan.json"
        with open(plan_file, 'w') as f:
            json.dump(sample_quick_plan, f)

        generator = TodoListGenerator()
        result = generator.generate_from_quick_plan(
            str(plan_file),
            "WO-ADD-FIELD-001"
        )

        assert result['workorder_id'] == "WO-ADD-FIELD-001"
        assert result['total_tasks'] == 2
        assert len(result['todos']) == 2
        assert result['mode'] == "quick_plan"

    def test_todo_preserves_all_metadata(self, temp_plan_file):
        """Test that all task metadata is preserved in todo"""
        generator = TodoListGenerator()
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-AUTH-001"
        )

        todo = result['todos'][2]  # Third task with dependencies
        metadata = todo['metadata']

        assert metadata['task_id'] == 3
        assert metadata['files'] == ["tests/auth.test.ts"]
        assert metadata['estimated_time'] == "2 hours"
        assert metadata['dependencies'] == [1, 2]
        assert len(metadata['acceptance_criteria']) == 2
