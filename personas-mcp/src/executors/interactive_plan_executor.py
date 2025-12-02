"""
InteractivePlanExecutor - Guided implementation with live tracking

Part of docs-expert v2.0 Phase 1: Lloyd Integration
"""

import json
from pathlib import Path
from typing import Dict, List, Literal, Optional
from datetime import datetime, UTC

from src.generators.todo_list_generator import TodoListGenerator
from src.trackers.plan_execution_tracker import PlanExecutionTracker


class InteractivePlanExecutor:
    """
    Provides guided step-by-step execution of implementation plans
    with real-time progress tracking.
    """

    def __init__(self):
        self.todo_generator = TodoListGenerator()
        self.tracker = PlanExecutionTracker()
        self.current_task = None
        self.execution_started_at = None

    def execute_plan_interactive(
        self,
        plan_path: str,
        workorder_id: str,
        mode: Literal["step-by-step", "batch"] = "step-by-step"
    ) -> Dict:
        """
        Execute plan with guided interaction.

        Args:
            plan_path: Path to plan.json or quick-plan.json
            workorder_id: Workorder ID (e.g., WO-AUTH-001)
            mode: "step-by-step" (interactive) or "batch" (all todos at once)

        Returns:
            Dict with execution details and next steps

        Raises:
            FileNotFoundError: Plan file not found
            ValueError: Invalid plan format or workorder ID
        """
        # Validate inputs
        if not workorder_id:
            raise ValueError("Workorder ID is required")

        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        # Read plan
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        # Verify workorder ID
        plan_workorder = plan.get('workorder_id')
        if plan_workorder != workorder_id:
            raise ValueError(
                f"Workorder ID mismatch: expected {workorder_id}, "
                f"found {plan_workorder}"
            )

        # Generate todos
        if 'task_breakdown' in plan:
            # Full plan format
            todo_result = self.todo_generator.generate_todo_list(
                plan_path, workorder_id, mode="all"
            )
        else:
            # Quick plan format
            todo_result = self.todo_generator.generate_from_quick_plan(
                plan_path, workorder_id
            )

        todos = todo_result['todos']
        self.execution_started_at = datetime.now(UTC).isoformat()

        if mode == "batch":
            return self._execute_batch_mode(
                plan_path, workorder_id, todos
            )
        else:
            return self._execute_step_by_step_mode(
                plan_path, workorder_id, todos
            )

    def _execute_batch_mode(
        self,
        plan_path: str,
        workorder_id: str,
        todos: List[Dict]
    ) -> Dict:
        """
        Batch mode: Generate all todos, Lloyd executes independently.

        Args:
            plan_path: Path to plan file
            workorder_id: Workorder ID
            todos: List of generated todos

        Returns:
            Dict with all todos and execution info
        """
        return {
            "workorder_id": workorder_id,
            "mode": "batch",
            "todos": todos,
            "total_tasks": len(todos),
            "execution_started_at": self.execution_started_at,
            "instructions": {
                "what_to_do": "Execute todos independently using TodoWrite",
                "how_to_track": "Use track_plan_execution periodically to sync progress",
                "completion": "All todos → completed status = workorder complete"
            },
            "summary": f"Generated {len(todos)} todos for {workorder_id}. Execute independently."
        }

    def _execute_step_by_step_mode(
        self,
        plan_path: str,
        workorder_id: str,
        todos: List[Dict]
    ) -> Dict:
        """
        Step-by-step mode: Present first task with guidance.

        Args:
            plan_path: Path to plan file
            workorder_id: Workorder ID
            todos: List of generated todos

        Returns:
            Dict with current task details and guidance
        """
        # Find first incomplete task
        current_task_index = 0
        for i, todo in enumerate(todos):
            if todo['status'] != 'completed':
                current_task_index = i
                break

        current_todo = todos[current_task_index]
        metadata = current_todo['metadata']

        # Check dependencies
        dependencies = metadata.get('dependencies', [])
        dependency_status = self._check_dependencies(
            plan_path, dependencies
        )

        # Generate guidance
        guidance = self._generate_guidance(current_todo, dependency_status)

        # Calculate progress
        completed_count = sum(1 for t in todos if t['status'] == 'completed')
        progress_percent = (completed_count / len(todos) * 100) if len(todos) > 0 else 0

        self.current_task = {
            "task_index": current_task_index + 1,
            "task_id": metadata['task_id'],
            "workorder_id": workorder_id
        }

        return {
            "workorder_id": workorder_id,
            "mode": "step-by-step",
            "current_task": {
                "task_id": metadata['task_id'],
                "task_number": current_task_index + 1,
                "description": current_todo['content'],
                "acceptance_criteria": metadata.get('acceptance_criteria', []),
                "files": metadata.get('files', []),
                "estimated_time": metadata.get('estimated_time'),
                "dependencies": dependencies,
                "dependency_status": dependency_status
            },
            "guidance": guidance,
            "progress": {
                "total_tasks": len(todos),
                "completed": completed_count,
                "current": current_task_index + 1,
                "remaining": len(todos) - completed_count,
                "percent": progress_percent
            },
            "actions": {
                "mark_complete": f"Mark todo {current_task_index + 1} as completed in TodoWrite",
                "skip": "Skip to next task (not recommended)",
                "get_next": "Call execute_plan_interactive again to get next task"
            },
            "summary": f"Task {current_task_index + 1}/{len(todos)}: {current_todo['content']}"
        }

    def _check_dependencies(
        self,
        plan_path: str,
        dependencies: List[int]
    ) -> Dict:
        """
        Check if task dependencies are met.

        Args:
            plan_path: Path to plan file
            dependencies: List of task IDs that must be completed

        Returns:
            Dict with dependency status
        """
        if not dependencies:
            return {
                "all_met": True,
                "blocking": [],
                "message": "No dependencies"
            }

        # Read plan to check task statuses
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        task_breakdown = plan.get('task_breakdown', [])
        if not task_breakdown:
            # Quick plan format
            task_breakdown = plan.get('plan', {}).get('tasks', [])

        # Check each dependency
        blocking = []
        for dep_id in dependencies:
            dep_task = next(
                (t for t in task_breakdown if t.get('task_id') == dep_id),
                None
            )
            if dep_task:
                status = dep_task.get('execution_status', {}).get('status', 'pending')
                if status != 'completed':
                    blocking.append({
                        "task_id": dep_id,
                        "description": dep_task.get('description'),
                        "status": status
                    })

        all_met = len(blocking) == 0

        return {
            "all_met": all_met,
            "blocking": blocking,
            "message": "All dependencies met" if all_met else f"{len(blocking)} dependencies incomplete"
        }

    def _generate_guidance(
        self,
        todo: Dict,
        dependency_status: Dict
    ) -> Dict:
        """
        Generate implementation guidance for current task.

        Args:
            todo: Current todo object
            dependency_status: Dependency check results

        Returns:
            Dict with guidance information
        """
        metadata = todo['metadata']
        content = todo['content']
        acceptance_criteria = metadata.get('acceptance_criteria', [])
        files = metadata.get('files', [])

        # Build what-to-do guidance
        what_to_do = content
        if files:
            what_to_do += f" (modify: {', '.join(files)})"

        # Build how-to-do guidance
        how_to_do_steps = []

        # Check dependencies first
        if not dependency_status['all_met']:
            how_to_do_steps.append(
                f"⚠️ WARNING: {len(dependency_status['blocking'])} dependencies not complete. "
                "Complete blocking tasks first."
            )
            for blocker in dependency_status['blocking']:
                how_to_do_steps.append(
                    f"  - Task {blocker['task_id']}: {blocker['description']} "
                    f"(status: {blocker['status']})"
                )
        else:
            # Normal implementation steps
            if files:
                if len(files) == 1:
                    how_to_do_steps.append(f"1. Open and modify {files[0]}")
                else:
                    how_to_do_steps.append(f"1. Open and modify these files:")
                    for i, file in enumerate(files, 2):
                        how_to_do_steps.append(f"   {i}. {file}")

            if acceptance_criteria:
                how_to_do_steps.append("2. Implement to meet acceptance criteria:")
                for i, criteria in enumerate(acceptance_criteria, 1):
                    how_to_do_steps.append(f"   - {criteria}")

            how_to_do_steps.append("3. Test implementation")
            how_to_do_steps.append("4. Mark todo as completed")

        # Build acceptance test guidance
        acceptance_test = "Verify acceptance criteria met:"
        if acceptance_criteria:
            for criteria in acceptance_criteria:
                acceptance_test += f"\n  ✓ {criteria}"
        else:
            acceptance_test += "\n  ✓ Task completed successfully"

        return {
            "what_to_do": what_to_do,
            "how_to_do_it": "\n".join(how_to_do_steps),
            "acceptance_test": acceptance_test,
            "estimated_time": metadata.get('estimated_time', 'Not specified'),
            "dependencies_met": dependency_status['all_met']
        }

    def get_next_task(
        self,
        plan_path: str,
        workorder_id: str
    ) -> Dict:
        """
        Get next incomplete task (convenience method).

        Args:
            plan_path: Path to plan file
            workorder_id: Workorder ID

        Returns:
            Dict with next task details
        """
        return self.execute_plan_interactive(
            plan_path, workorder_id, mode="step-by-step"
        )

    def get_execution_summary(
        self,
        plan_path: str,
        workorder_id: str
    ) -> Dict:
        """
        Get overall execution summary (read-only).

        Args:
            plan_path: Path to plan file
            workorder_id: Workorder ID

        Returns:
            Dict with execution summary
        """
        # Get current progress
        progress = self.tracker.get_plan_progress(plan_path)

        # Get blockers
        blockers = self.tracker.identify_blockers(plan_path, workorder_id)

        # Calculate estimated time remaining
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        task_breakdown = plan.get('task_breakdown', [])
        if not task_breakdown:
            task_breakdown = plan.get('plan', {}).get('tasks', [])

        # Sum estimated time for incomplete tasks
        # (This is a simple implementation; could be enhanced)
        remaining_tasks = [
            t for t in task_breakdown
            if t.get('execution_status', {}).get('status', 'pending') != 'completed'
        ]

        return {
            "workorder_id": workorder_id,
            "progress": progress,
            "blockers": blockers,
            "remaining_tasks": len(remaining_tasks),
            "execution_started_at": self.execution_started_at,
            "is_complete": progress.get('progress_percent') == 100.0,
            "summary": (
                f"{progress.get('completed')}/{progress.get('total_tasks')} tasks completed "
                f"({progress.get('progress_percent'):.1f}%)"
            )
        }
