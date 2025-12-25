"""
Integration tests for Phase 1: Lloyd Integration

Tests complete workflows from plan creation → todo generation →
execution tracking → completion.
"""

import json
import pytest
from pathlib import Path

from src.generators.todo_list_generator import TodoListGenerator
from src.trackers.plan_execution_tracker import PlanExecutionTracker
from src.executors.interactive_plan_executor import InteractivePlanExecutor


@pytest.fixture
def sample_plan():
    """Sample implementation plan for integration testing"""
    return {
        "workorder_id": "WO-INTEGRATION-001",
        "feature_name": "integration-test",
        "task_breakdown": [
            {
                "task_id": 1,
                "description": "Create authentication middleware",
                "files": ["src/middleware/auth.ts"],
                "acceptance_criteria": [
                    "Middleware validates JWT",
                    "Returns 401 on invalid token"
                ],
                "estimated_time": "2 hours",
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
                "estimated_time": "1 hour",
                "dependencies": [1]
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
def temp_plan_file(tmp_path, sample_plan):
    """Create temporary plan file for testing"""
    plan_file = tmp_path / "plan.json"
    with open(plan_file, 'w') as f:
        json.dump(sample_plan, f)
    return plan_file


class TestFullPlanningWorkflow:
    """
    Test complete planning workflow:
    plan.json → generate todos → execute → track progress → complete
    """

    def test_full_workflow_batch_mode(self, temp_plan_file):
        """
        Test full workflow in batch mode:
        1. Generate todos from plan
        2. Simulate Lloyd executing tasks
        3. Track progress after each task
        4. Verify 100% completion
        """
        # Initialize components
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        # Step 1: Generate todos
        todo_result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            mode="all"
        )

        assert todo_result['total_tasks'] == 3
        todos = todo_result['todos']

        # Step 2: Simulate Lloyd completing task 1
        todos[0]['status'] = 'completed'

        # Track progress after task 1
        track_result_1 = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        assert track_result_1['plan_status']['completed'] == 1
        assert track_result_1['plan_status']['progress_percent'] == pytest.approx(33.33, rel=0.1)

        # Step 3: Simulate Lloyd completing task 2
        todos[1]['status'] = 'completed'

        # Track progress after task 2
        track_result_2 = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        assert track_result_2['plan_status']['completed'] == 2
        assert track_result_2['plan_status']['progress_percent'] == pytest.approx(66.66, rel=0.1)

        # Step 4: Simulate Lloyd completing task 3
        todos[2]['status'] = 'completed'

        # Track progress after task 3
        track_result_3 = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        assert track_result_3['plan_status']['completed'] == 3
        assert track_result_3['plan_status']['progress_percent'] == 100.0

        # Step 5: Verify plan file has been updated
        with open(temp_plan_file, 'r') as f:
            final_plan = json.load(f)

        assert 'progress' in final_plan
        assert final_plan['progress']['completed'] == 3
        assert all(
            task.get('execution_status', {}).get('status') == 'completed'
            for task in final_plan['task_breakdown']
        )

    def test_full_workflow_step_by_step(self, temp_plan_file):
        """
        Test full workflow in step-by-step mode:
        1. Execute plan interactively
        2. Get first task
        3. Complete task, get next
        4. Repeat until all tasks done
        """
        executor = InteractivePlanExecutor()
        tracker = PlanExecutionTracker()

        # Step 1: Start interactive execution
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            mode="step-by-step"
        )

        # Should present first task
        assert result['current_task']['task_id'] == 1
        assert result['progress']['completed'] == 0
        assert result['progress']['current'] == 1

        # Step 2: Simulate completing task 1
        # Read plan to get todos
        generator = TodoListGenerator()
        todo_result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = todo_result['todos']
        todos[0]['status'] = 'completed'

        # Track progress
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        # Step 3: Get next task
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            mode="step-by-step"
        )

        # Should present task 2
        assert result['current_task']['task_id'] == 2
        assert result['progress']['completed'] == 1

    def test_workflow_with_remaining_mode(self, temp_plan_file):
        """
        Test generating todos for remaining tasks only
        """
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        # Step 1: Generate all todos and complete first task
        todo_result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = todo_result['todos']
        todos[0]['status'] = 'completed'

        # Track progress
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        # Step 2: Generate todos for remaining tasks only
        remaining_result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            mode="remaining"
        )

        # Should only have 2 remaining tasks
        assert remaining_result['total_tasks'] == 2
        remaining_todos = remaining_result['todos']
        assert remaining_todos[0]['metadata']['task_id'] == 2
        assert remaining_todos[1]['metadata']['task_id'] == 3


class TestLloydCoordination:
    """
    Test scenarios specific to Lloyd coordination
    """

    def test_lloyd_receives_ready_todos(self, temp_plan_file):
        """
        Test that Lloyd receives todos in correct format with all metadata
        """
        generator = TodoListGenerator()

        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )

        todos = result['todos']

        # Verify all todos have required fields for TodoWrite
        for todo in todos:
            assert 'content' in todo
            assert 'activeForm' in todo
            assert 'status' in todo
            assert 'metadata' in todo

            # Verify metadata completeness
            metadata = todo['metadata']
            assert metadata['workorder_id'] == "WO-INTEGRATION-001"
            assert 'task_id' in metadata
            assert 'acceptance_criteria' in metadata

    def test_lloyd_tracks_progress_incrementally(self, temp_plan_file):
        """
        Test Lloyd tracking progress task by task
        """
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        # Generate todos
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = result['todos']

        # Lloyd completes tasks one by one
        progress_snapshots = []

        for i in range(len(todos)):
            # Mark task as completed
            todos[i]['status'] = 'completed'

            # Track progress
            track_result = tracker.track_plan_execution(
                str(temp_plan_file),
                "WO-INTEGRATION-001",
                todos
            )

            progress_snapshots.append(track_result['plan_status']['progress_percent'])

        # Verify progress increases monotonically
        assert progress_snapshots == pytest.approx([33.33, 66.66, 100.0], rel=0.1)

    def test_lloyd_sees_real_time_plan_updates(self, temp_plan_file):
        """
        Test that plan file updates in real-time as Lloyd works
        """
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = result['todos']

        # Complete first task
        todos[0]['status'] = 'completed'
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        # Read plan file
        with open(temp_plan_file, 'r') as f:
            plan_after_task1 = json.load(f)

        # Verify task 1 is marked completed in plan
        assert plan_after_task1['task_breakdown'][0]['execution_status']['status'] == 'completed'
        assert 'completed_at' in plan_after_task1['task_breakdown'][0]['execution_status']

        # Complete second task
        todos[1]['status'] = 'completed'
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        # Read plan file again
        with open(temp_plan_file, 'r') as f:
            plan_after_task2 = json.load(f)

        # Verify both tasks are completed
        assert plan_after_task2['task_breakdown'][0]['execution_status']['status'] == 'completed'
        assert plan_after_task2['task_breakdown'][1]['execution_status']['status'] == 'completed'


class TestEdgeCases:
    """
    Test edge cases and error scenarios
    """

    def test_out_of_order_completion(self, temp_plan_file):
        """
        Test completing tasks out of dependency order
        """
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = result['todos']

        # Complete task 2 before task 1 (out of order)
        todos[1]['status'] = 'completed'

        # Should still track correctly
        track_result = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        assert track_result['plan_status']['completed'] == 1

        # Check blockers - task 3 should be blocked by task 1
        blockers = tracker.identify_blockers(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )

        # Task 3 depends on both 1 and 2, but task 1 is not complete
        assert len(blockers) > 0
        task_3_blocked = any(b['task_id'] == 3 for b in blockers)
        assert task_3_blocked

    def test_partial_completion(self, temp_plan_file):
        """
        Test tracking when only some tasks are completed
        """
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = result['todos']

        # Complete only first task
        todos[0]['status'] = 'completed'
        todos[1]['status'] = 'in_progress'
        todos[2]['status'] = 'pending'

        track_result = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )

        # Verify partial completion
        assert track_result['plan_status']['completed'] == 1
        assert track_result['plan_status']['in_progress'] == 1
        assert track_result['plan_status']['pending'] == 1
        assert track_result['plan_status']['progress_percent'] == pytest.approx(33.33, rel=0.1)

    def test_workorder_traceability(self, temp_plan_file):
        """
        Test that workorder ID is preserved throughout workflow
        """
        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()
        executor = InteractivePlanExecutor()

        # Generate todos
        todo_result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )

        # Check workorder in todos
        assert todo_result['workorder_id'] == "WO-INTEGRATION-001"
        for todo in todo_result['todos']:
            assert todo['metadata']['workorder_id'] == "WO-INTEGRATION-001"

        # Track progress
        track_result = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todo_result['todos']
        )

        # Check workorder in tracking
        assert track_result['workorder_id'] == "WO-INTEGRATION-001"

        # Execute interactively
        exec_result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            mode="step-by-step"
        )

        # Check workorder in execution
        assert exec_result['workorder_id'] == "WO-INTEGRATION-001"


class TestPerformance:
    """
    Test performance requirements
    """

    def test_todo_generation_performance(self, temp_plan_file):
        """
        Test that todo generation completes in <2 seconds
        """
        import time

        generator = TodoListGenerator()

        start = time.time()
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        duration = time.time() - start

        assert duration < 2.0, f"Todo generation took {duration:.2f}s (target: <2s)"

    def test_progress_tracking_performance(self, temp_plan_file):
        """
        Test that progress tracking completes in <1 second
        """
        import time

        generator = TodoListGenerator()
        tracker = PlanExecutionTracker()

        # Generate todos first
        result = generator.generate_todo_list(
            str(temp_plan_file),
            "WO-INTEGRATION-001"
        )
        todos = result['todos']
        todos[0]['status'] = 'completed'

        # Measure tracking performance
        start = time.time()
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            todos
        )
        duration = time.time() - start

        assert duration < 1.0, f"Progress tracking took {duration:.2f}s (target: <1s)"

    def test_interactive_execution_performance(self, temp_plan_file):
        """
        Test that interactive execution starts quickly
        """
        import time

        executor = InteractivePlanExecutor()

        start = time.time()
        result = executor.execute_plan_interactive(
            str(temp_plan_file),
            "WO-INTEGRATION-001",
            mode="step-by-step"
        )
        duration = time.time() - start

        assert duration < 2.0, f"Interactive execution took {duration:.2f}s (target: <2s)"
