"""
PlanExecutionTracker - Sync plan progress with todo status

Part of docs-expert v2.0 Phase 1: Lloyd Integration
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, UTC


class PlanExecutionTracker:
    """
    Tracks plan execution progress by syncing with TodoWrite status.
    Updates plan.json with real-time execution status.
    """

    def __init__(self):
        self.last_sync_at = None

    def track_plan_execution(
        self,
        plan_path: str,
        workorder_id: str,
        todo_status: List[Dict]
    ) -> Dict:
        """
        Sync plan progress with todo status.

        Args:
            plan_path: Path to plan.json file
            workorder_id: Workorder ID (e.g., WO-AUTH-001)
            todo_status: Array of todo objects with current status

        Returns:
            Dict with progress summary and updated task details

        Raises:
            FileNotFoundError: Plan file not found
            ValueError: Invalid plan format or workorder ID mismatch
        """
        # Validate inputs
        if not workorder_id:
            raise ValueError("Workorder ID is required")

        if not todo_status or not isinstance(todo_status, list):
            raise ValueError("todo_status must be a non-empty list")

        # Read plan file
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in plan file: {plan_path}")

        # Verify workorder ID
        plan_workorder = plan.get('workorder_id')
        if plan_workorder != workorder_id:
            raise ValueError(
                f"Workorder ID mismatch: expected {workorder_id}, "
                f"found {plan_workorder}"
            )

        # Get task breakdown
        task_breakdown = plan.get('task_breakdown')
        if not task_breakdown:
            raise ValueError("No task breakdown found in plan")

        # Create mapping of task_id → todo status
        todo_map = self._build_todo_map(todo_status)

        # Update task execution status
        task_details = []
        for task in task_breakdown:
            task_id = task.get('task_id')
            if task_id in todo_map:
                todo = todo_map[task_id]
                updated_task = self._update_task_status(task, todo)
                task_details.append({
                    "task_id": task_id,
                    "status": updated_task['execution_status']['status'],
                    "started_at": updated_task['execution_status'].get('started_at'),
                    "completed_at": updated_task['execution_status'].get('completed_at')
                })
            else:
                # Task not found in todos (warning, but continue)
                task_details.append({
                    "task_id": task_id,
                    "status": "pending",
                    "warning": "Task not linked to todo"
                })

        # Calculate progress statistics
        progress = self._calculate_progress(task_breakdown)

        # Update plan with progress metadata
        plan['progress'] = progress
        plan['last_synced_at'] = datetime.now(UTC).isoformat()

        # Write updated plan back to file
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)

        self.last_sync_at = plan['last_synced_at']

        return {
            "workorder_id": workorder_id,
            "plan_status": progress,
            "task_details": task_details,
            "updated_plan_path": str(plan_path),
            "synced_at": self.last_sync_at,
            "summary": f"{progress['completed']}/{progress['total_tasks']} tasks completed ({progress['progress_percent']:.1f}%)"
        }

    def _build_todo_map(self, todo_status: List[Dict]) -> Dict[int, Dict]:
        """
        Build mapping of task_id → todo for quick lookup.

        Args:
            todo_status: Array of todo objects

        Returns:
            Dict mapping task_id to todo object
        """
        todo_map = {}
        for todo in todo_status:
            metadata = todo.get('metadata', {})
            task_id = metadata.get('task_id')
            if task_id is not None:
                todo_map[task_id] = todo
        return todo_map

    def _update_task_status(self, task: Dict, todo: Dict) -> Dict:
        """
        Update task execution status based on todo status.

        Args:
            task: Task object from plan
            todo: Todo object with current status

        Returns:
            Updated task object
        """
        todo_status = todo.get('status', 'pending')
        metadata = todo.get('metadata', {})

        # Initialize or update execution_status
        if 'execution_status' not in task:
            task['execution_status'] = {}

        execution_status = task['execution_status']
        execution_status['status'] = todo_status

        # Track timestamps
        if todo_status == 'in_progress' and 'started_at' not in execution_status:
            execution_status['started_at'] = datetime.now(UTC).isoformat()

        if todo_status == 'completed' and 'completed_at' not in execution_status:
            execution_status['completed_at'] = datetime.now(UTC).isoformat()

        # Store notes if provided
        notes = metadata.get('notes')
        if notes:
            execution_status['notes'] = notes

        return task

    def _calculate_progress(self, task_breakdown: List[Dict]) -> Dict:
        """
        Calculate progress statistics from task breakdown.

        Args:
            task_breakdown: Array of task objects

        Returns:
            Dict with progress statistics
        """
        total = len(task_breakdown)
        completed = 0
        in_progress = 0
        pending = 0

        for task in task_breakdown:
            status = task.get('execution_status', {}).get('status', 'pending')
            if status == 'completed':
                completed += 1
            elif status == 'in_progress':
                in_progress += 1
            else:
                pending += 1

        progress_percent = (completed / total * 100) if total > 0 else 0

        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "progress_percent": progress_percent
        }

    def get_plan_progress(self, plan_path: str) -> Dict:
        """
        Get current progress without syncing (read-only).

        Args:
            plan_path: Path to plan.json file

        Returns:
            Dict with current progress statistics
        """
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        # Return existing progress if available
        if 'progress' in plan:
            return plan['progress']

        # Otherwise calculate from task_breakdown
        task_breakdown = plan.get('task_breakdown', [])
        return self._calculate_progress(task_breakdown)

    def identify_blockers(
        self,
        plan_path: str,
        workorder_id: str
    ) -> List[Dict]:
        """
        Identify blocked tasks (dependencies not complete).

        Args:
            plan_path: Path to plan.json file
            workorder_id: Workorder ID

        Returns:
            List of blocked tasks with dependency info
        """
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        task_breakdown = plan.get('task_breakdown', [])

        # Build task status map
        task_status_map = {}
        for task in task_breakdown:
            task_id = task.get('task_id')
            status = task.get('execution_status', {}).get('status', 'pending')
            task_status_map[task_id] = status

        # Find blockers
        blockers = []
        for task in task_breakdown:
            task_id = task.get('task_id')
            task_status = task_status_map.get(task_id, 'pending')
            dependencies = task.get('dependencies', [])

            # Check if task is pending/in_progress but has incomplete dependencies
            if task_status in ['pending', 'in_progress'] and dependencies:
                incomplete_deps = [
                    dep for dep in dependencies
                    if task_status_map.get(dep) != 'completed'
                ]

                if incomplete_deps:
                    blockers.append({
                        "task_id": task_id,
                        "description": task.get('description'),
                        "status": task_status,
                        "blocked_by": incomplete_deps,
                        "blocker_descriptions": [
                            t.get('description')
                            for t in task_breakdown
                            if t.get('task_id') in incomplete_deps
                        ]
                    })

        return blockers
