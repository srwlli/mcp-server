"""
Unit tests for InteractivePlanExecutor

Part of docs-expert v2.0 Phase 1: Lloyd Integration
"""

import json
import pytest
from pathlib import Path
from src.executors.interactive_plan_executor import InteractivePlanExecutor


@pytest.fixture
def sample_plan():
    """Sample plan for testing"""
    return {
        "workorder_id": "WO-TEST-001",
        "feature_name": "test-feature",
        "task_breakdown": [
            {
                "task_id": 1,
                "description": "Create middleware",
                "files": ["src/middleware.ts"],
                "acceptance_criteria": ["Validates input", "Returns 401 on invalid"],
                "estimated_time": "2 hours",
                "dependencies": []
            },
            {
                "task_id": 2,
                "description": "Add endpoint",
                "files": ["src/routes.ts"],
                "acceptance_criteria": ["Returns 200 on success"],
                "estimated_time": "1 hour",
                "dependencies": [1]
            },
            {
                "task_id": 3,
                "description": "Write tests",
                "files": ["tests/test.ts"],
                "acceptance_criteria": ["90% coverage"],
                "estimated_time": "2 hours",
                "dependencies": [1, 2]
            }
        ]
    }


@pytest.fixture
def temp_plan_file(tmp_path, sample_plan):
    """Create temporary plan file"""
    plan_file = tmp_path / "plan.json"
    with open(plan_file, 'w') as f:
        json.dump(sample_plan, f)
    return plan_file


class TestInteractivePlanExecutor:
    """Test suite for InteractivePlanExecutor"""

    def test_execute_batch_mode(self, temp_plan_file):
        """Test batch mode execution"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="batch"
        )

        assert result['mode'] == "batch"
        assert result['workorder_id'] == "WO-TEST-001"
        assert result['total_tasks'] == 3
        assert len(result['todos']) == 3
        assert 'instructions' in result
        assert 'execution_started_at' in result

    def test_execute_step_by_step_mode(self, temp_plan_file):
        """Test step-by-step mode execution"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="step-by-step"
        )

        assert result['mode'] == "step-by-step"
        assert result['workorder_id'] == "WO-TEST-001"
        assert 'current_task' in result
        assert 'guidance' in result
        assert 'progress' in result
        assert 'actions' in result

    def test_current_task_details(self, temp_plan_file):
        """Test current task has all required details"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="step-by-step"
        )

        current = result['current_task']

        assert current['task_id'] == 1
        assert current['task_number'] == 1
        assert current['description'] == "Create middleware"
        assert len(current['acceptance_criteria']) == 2
        assert current['files'] == ["src/middleware.ts"]
        assert current['estimated_time'] == "2 hours"
        assert current['dependencies'] == []

    def test_guidance_generation(self, temp_plan_file):
        """Test guidance is generated correctly"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="step-by-step"
        )

        guidance = result['guidance']

        assert 'what_to_do' in guidance
        assert 'how_to_do_it' in guidance
        assert 'acceptance_test' in guidance
        assert 'estimated_time' in guidance
        assert 'dependencies_met' in guidance

        # First task has no dependencies, should be met
        assert guidance['dependencies_met'] is True

    def test_progress_tracking(self, temp_plan_file):
        """Test progress is tracked correctly"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="step-by-step"
        )

        progress = result['progress']

        assert progress['total_tasks'] == 3
        assert progress['completed'] == 0
        assert progress['current'] == 1
        assert progress['remaining'] == 3
        assert progress['percent'] == 0.0

    def test_dependency_checking_all_met(self, temp_plan_file):
        """Test dependency checking when all dependencies are met"""
        executor = InteractivePlanExecutor()

        # Check dependencies for task with no dependencies
        dep_status = executor._check_dependencies(str(temp_plan_file), [])

        assert dep_status['all_met'] is True
        assert len(dep_status['blocking']) == 0
        assert dep_status['message'] == "No dependencies"

    def test_dependency_checking_not_met(self, temp_plan_file):
        """Test dependency checking when dependencies are not met"""
        executor = InteractivePlanExecutor()

        # Task 2 depends on task 1 (which is not completed yet)
        dep_status = executor._check_dependencies(str(temp_plan_file), [1])

        assert dep_status['all_met'] is False
        assert len(dep_status['blocking']) == 1
        assert dep_status['blocking'][0]['task_id'] == 1
        assert "incomplete" in dep_status['message']

    def test_workorder_id_required(self, temp_plan_file):
        """Test that workorder ID is required"""
        executor = InteractivePlanExecutor()

        with pytest.raises(ValueError, match="Workorder ID is required"):
            executor.execute_plan_interactive(str(temp_plan_file), "")

    def test_plan_file_not_found(self):
        """Test handling of missing plan file"""
        executor = InteractivePlanExecutor()

        with pytest.raises(FileNotFoundError):
            executor.execute_plan_interactive("/nonexistent/plan.json", "WO-TEST-001")

    def test_workorder_id_mismatch(self, temp_plan_file):
        """Test handling of workorder ID mismatch"""
        executor = InteractivePlanExecutor()

        with pytest.raises(ValueError, match="Workorder ID mismatch"):
            executor.execute_plan_interactive(str(temp_plan_file), "WO-WRONG-001")

    def test_get_next_task(self, temp_plan_file):
        """Test getting next task convenience method"""
        executor = InteractivePlanExecutor()

        result = executor.get_next_task(str(temp_plan_file), "WO-TEST-001")

        assert result['mode'] == "step-by-step"
        assert result['current_task']['task_id'] == 1

    def test_get_execution_summary(self, temp_plan_file):
        """Test getting execution summary"""
        executor = InteractivePlanExecutor()

        # First execute to initialize
        executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="batch"
        )

        summary = executor.get_execution_summary(
            str(temp_plan_file),
            "WO-TEST-001"
        )

        assert summary['workorder_id'] == "WO-TEST-001"
        assert 'progress' in summary
        assert 'blockers' in summary
        assert 'remaining_tasks' in summary
        assert summary['is_complete'] is False
        assert "0/3 tasks completed" in summary['summary']

    def test_batch_mode_todos_format(self, temp_plan_file):
        """Test that batch mode todos have correct format"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="batch"
        )

        todos = result['todos']

        # Check first todo
        todo = todos[0]
        assert 'content' in todo
        assert 'activeForm' in todo
        assert 'status' in todo
        assert 'metadata' in todo
        assert todo['metadata']['workorder_id'] == "WO-TEST-001"

    def test_step_by_step_actions(self, temp_plan_file):
        """Test that step-by-step mode provides clear actions"""
        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-TEST-001",
            mode="step-by-step"
        )

        actions = result['actions']

        assert 'mark_complete' in actions
        assert 'skip' in actions
        assert 'get_next' in actions
        assert "Mark todo 1 as completed" in actions['mark_complete']

    def test_guidance_with_multiple_files(self, tmp_path):
        """Test guidance generation with multiple files"""
        plan = {
            "workorder_id": "WO-MULTI-001",
            "task_breakdown": [
                {
                    "task_id": 1,
                    "description": "Update multiple files",
                    "files": ["src/file1.ts", "src/file2.ts", "src/file3.ts"],
                    "acceptance_criteria": ["All files updated"],
                    "dependencies": []
                }
            ]
        }

        plan_file = tmp_path / "plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f)

        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(plan_file),
            "WO-MULTI-001",
            mode="step-by-step"
        )

        guidance = result['guidance']
        how_to = guidance['how_to_do_it']

        # Should mention all files
        assert "file1.ts" in how_to
        assert "file2.ts" in how_to
        assert "file3.ts" in how_to

    def test_guidance_with_blocked_dependencies(self, tmp_path):
        """Test guidance when dependencies are not met"""
        plan = {
            "workorder_id": "WO-BLOCKED-001",
            "task_breakdown": [
                {
                    "task_id": 1,
                    "description": "First task",
                    "dependencies": [],
                    "execution_status": {"status": "pending"}
                },
                {
                    "task_id": 2,
                    "description": "Second task (depends on first)",
                    "dependencies": [1],
                    "acceptance_criteria": ["Works correctly"]
                }
            ]
        }

        plan_file = tmp_path / "plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f)

        executor = InteractivePlanExecutor()

        # Get task 2 (which is blocked by task 1)
        result = executor.execute_plan_interactive(
            str(plan_file),
            "WO-BLOCKED-001",
            mode="step-by-step"
        )

        # Should be showing task 1 first (since it's the first incomplete)
        assert result['current_task']['task_id'] == 1

    def test_progress_percent_calculation(self, tmp_path):
        """Test progress percentage calculation"""
        plan = {
            "workorder_id": "WO-PROGRESS-001",
            "task_breakdown": [
                {
                    "task_id": 1,
                    "description": "Task 1",
                    "dependencies": [],
                    "execution_status": {"status": "completed"}
                },
                {
                    "task_id": 2,
                    "description": "Task 2",
                    "dependencies": [],
                    "execution_status": {"status": "completed"}
                },
                {
                    "task_id": 3,
                    "description": "Task 3",
                    "dependencies": []
                },
                {
                    "task_id": 4,
                    "description": "Task 4",
                    "dependencies": []
                }
            ]
        }

        plan_file = tmp_path / "plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f)

        executor = InteractivePlanExecutor()
        result = executor.execute_plan_interactive(
            str(plan_file),
            "WO-PROGRESS-001",
            mode="step-by-step"
        )

        progress = result['progress']

        # 2 out of 4 completed = 50%
        assert progress['completed'] == 2
        assert progress['total_tasks'] == 4
        assert progress['percent'] == 50.0
