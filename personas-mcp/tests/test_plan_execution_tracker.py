"""
Unit tests for PlanExecutionTracker

Part of docs-expert v2.0 Phase 1: Lloyd Integration
"""

import json
import pytest
from pathlib import Path
from src.trackers.plan_execution_tracker import PlanExecutionTracker


@pytest.fixture
def sample_plan():
    """Sample plan for testing"""
    return {
        "workorder_id": "WO-AUTH-001",
        "feature_name": "authentication",
        "task_breakdown": [
            {
                "task_id": 1,
                "description": "Create middleware",
                "dependencies": []
            },
            {
                "task_id": 2,
                "description": "Add endpoint",
                "dependencies": [1]
            },
            {
                "task_id": 3,
                "description": "Write tests",
                "dependencies": [1, 2]
            }
        ]
    }


@pytest.fixture
def sample_todos():
    """Sample todo status for testing"""
    return [
        {
            "content": "Create middleware",
            "status": "completed",
            "metadata": {"task_id": 1, "workorder_id": "WO-AUTH-001"}
        },
        {
            "content": "Add endpoint",
            "status": "in_progress",
            "metadata": {"task_id": 2, "workorder_id": "WO-AUTH-001"}
        },
        {
            "content": "Write tests",
            "status": "pending",
            "metadata": {"task_id": 3, "workorder_id": "WO-AUTH-001"}
        }
    ]


@pytest.fixture
def temp_plan_file(tmp_path, sample_plan):
    """Create temporary plan file"""
    plan_file = tmp_path / "plan.json"
    with open(plan_file, 'w') as f:
        json.dump(sample_plan, f)
    return plan_file


class TestPlanExecutionTracker:
    """Test suite for PlanExecutionTracker"""

    def test_track_plan_execution_basic(self, temp_plan_file, sample_todos):
        """Test basic progress tracking"""
        tracker = PlanExecutionTracker()
        result = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-AUTH-001",
            sample_todos
        )

        assert result['workorder_id'] == "WO-AUTH-001"
        assert result['plan_status']['total_tasks'] == 3
        assert result['plan_status']['completed'] == 1
        assert result['plan_status']['in_progress'] == 1
        assert result['plan_status']['pending'] == 1
        assert result['plan_status']['progress_percent'] == pytest.approx(33.33, rel=0.1)

    def test_track_updates_plan_file(self, temp_plan_file, sample_todos):
        """Test that plan file is updated with progress"""
        tracker = PlanExecutionTracker()
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-AUTH-001",
            sample_todos
        )

        # Read updated plan
        with open(temp_plan_file, 'r') as f:
            updated_plan = json.load(f)

        assert 'progress' in updated_plan
        assert updated_plan['progress']['completed'] == 1
        assert 'last_synced_at' in updated_plan

    def test_task_execution_status_updated(self, temp_plan_file, sample_todos):
        """Test that task execution_status is updated"""
        tracker = PlanExecutionTracker()
        tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-AUTH-001",
            sample_todos
        )

        # Read updated plan
        with open(temp_plan_file, 'r') as f:
            updated_plan = json.load(f)

        tasks = updated_plan['task_breakdown']

        # Task 1 should be completed
        assert tasks[0]['execution_status']['status'] == 'completed'
        assert 'completed_at' in tasks[0]['execution_status']

        # Task 2 should be in_progress
        assert tasks[1]['execution_status']['status'] == 'in_progress'
        assert 'started_at' in tasks[1]['execution_status']

        # Task 3 should be pending
        assert tasks[2]['execution_status']['status'] == 'pending'

    def test_all_tasks_completed(self, temp_plan_file):
        """Test 100% completion"""
        todos = [
            {"content": "Task 1", "status": "completed", "metadata": {"task_id": 1}},
            {"content": "Task 2", "status": "completed", "metadata": {"task_id": 2}},
            {"content": "Task 3", "status": "completed", "metadata": {"task_id": 3}}
        ]

        tracker = PlanExecutionTracker()
        result = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-AUTH-001",
            todos
        )

        assert result['plan_status']['completed'] == 3
        assert result['plan_status']['progress_percent'] == 100.0
        assert "3/3 tasks completed" in result['summary']

    def test_workorder_id_required(self, temp_plan_file, sample_todos):
        """Test that workorder ID is required"""
        tracker = PlanExecutionTracker()

        with pytest.raises(ValueError, match="Workorder ID is required"):
            tracker.track_plan_execution(str(temp_plan_file), "", sample_todos)

    def test_todo_status_required(self, temp_plan_file):
        """Test that todo_status is required"""
        tracker = PlanExecutionTracker()

        with pytest.raises(ValueError, match="todo_status must be a non-empty list"):
            tracker.track_plan_execution(str(temp_plan_file), "WO-AUTH-001", [])

    def test_plan_file_not_found(self, sample_todos):
        """Test handling of missing plan file"""
        tracker = PlanExecutionTracker()

        with pytest.raises(FileNotFoundError):
            tracker.track_plan_execution("/nonexistent/plan.json", "WO-AUTH-001", sample_todos)

    def test_workorder_id_mismatch(self, temp_plan_file, sample_todos):
        """Test handling of workorder ID mismatch"""
        tracker = PlanExecutionTracker()

        with pytest.raises(ValueError, match="Workorder ID mismatch"):
            tracker.track_plan_execution(str(temp_plan_file), "WO-WRONG-001", sample_todos)

    def test_get_plan_progress(self, temp_plan_file, sample_todos):
        """Test getting current progress without syncing"""
        tracker = PlanExecutionTracker()

        # First sync to create progress
        tracker.track_plan_execution(str(temp_plan_file), "WO-AUTH-001", sample_todos)

        # Get progress (read-only)
        progress = tracker.get_plan_progress(str(temp_plan_file))

        assert progress['total_tasks'] == 3
        assert progress['completed'] == 1
        assert progress['in_progress'] == 1
        assert progress['pending'] == 1

    def test_identify_blockers_no_blockers(self, temp_plan_file, sample_todos):
        """Test blocker detection when no tasks are blocked"""
        tracker = PlanExecutionTracker()

        # Sync with status where dependencies are met
        tracker.track_plan_execution(str(temp_plan_file), "WO-AUTH-001", sample_todos)

        blockers = tracker.identify_blockers(str(temp_plan_file), "WO-AUTH-001")

        # Task 2 depends on task 1 (completed), so not blocked
        # Task 3 depends on tasks 1 and 2, but task 2 is in_progress, so task 3 IS blocked
        assert len(blockers) == 1
        assert blockers[0]['task_id'] == 3
        assert 2 in blockers[0]['blocked_by']

    def test_identify_blockers_with_blockers(self, temp_plan_file):
        """Test blocker detection when tasks are blocked"""
        todos = [
            {"content": "Task 1", "status": "pending", "metadata": {"task_id": 1}},
            {"content": "Task 2", "status": "in_progress", "metadata": {"task_id": 2}},
            {"content": "Task 3", "status": "pending", "metadata": {"task_id": 3}}
        ]

        tracker = PlanExecutionTracker()
        tracker.track_plan_execution(str(temp_plan_file), "WO-AUTH-001", todos)

        blockers = tracker.identify_blockers(str(temp_plan_file), "WO-AUTH-001")

        # Task 2 depends on task 1 (pending), so blocked
        # Task 3 depends on tasks 1 and 2 (both incomplete), so blocked
        assert len(blockers) == 2

        blocker_task_ids = [b['task_id'] for b in blockers]
        assert 2 in blocker_task_ids
        assert 3 in blocker_task_ids

    def test_todo_without_task_id(self, temp_plan_file):
        """Test handling todos without task_id in metadata"""
        todos = [
            {"content": "Task 1", "status": "completed", "metadata": {"task_id": 1}},
            {"content": "Task 2", "status": "completed", "metadata": {}},  # No task_id
        ]

        tracker = PlanExecutionTracker()
        result = tracker.track_plan_execution(
            str(temp_plan_file),
            "WO-AUTH-001",
            todos
        )

        # Should still work, just warn about unlinked tasks
        assert result['plan_status']['completed'] == 1
        warnings = [t for t in result['task_details'] if 'warning' in t]
        assert len(warnings) == 2  # Tasks 2 and 3 not linked

    def test_progress_calculation_empty_tasks(self):
        """Test progress calculation with empty task list"""
        tracker = PlanExecutionTracker()
        progress = tracker._calculate_progress([])

        assert progress['total_tasks'] == 0
        assert progress['completed'] == 0
        assert progress['progress_percent'] == 0

    def test_timestamps_preserved_on_resync(self, temp_plan_file, sample_todos):
        """Test that timestamps are preserved across multiple syncs"""
        tracker = PlanExecutionTracker()

        # First sync
        tracker.track_plan_execution(str(temp_plan_file), "WO-AUTH-001", sample_todos)

        # Read plan to get original timestamp
        with open(temp_plan_file, 'r') as f:
            plan_after_first = json.load(f)

        original_completed_at = plan_after_first['task_breakdown'][0]['execution_status']['completed_at']

        # Second sync (no changes)
        tracker.track_plan_execution(str(temp_plan_file), "WO-AUTH-001", sample_todos)

        # Read plan again
        with open(temp_plan_file, 'r') as f:
            plan_after_second = json.load(f)

        # Timestamp should be preserved (not updated)
        assert plan_after_second['task_breakdown'][0]['execution_status']['completed_at'] == original_completed_at
