"""
TodoListGenerator - Convert plan task breakdown to TodoWrite format

Part of docs-expert v2.0 Phase 1: Lloyd Integration
"""

import json
from pathlib import Path
from typing import Dict, List, Literal, Optional
from datetime import datetime, UTC


class TodoListGenerator:
    """
    Converts implementation plan task breakdowns into TodoWrite-compatible format
    for seamless Lloyd integration.
    """

    def __init__(self):
        self.generated_at = None

    def generate_todo_list(
        self,
        plan_path: str,
        workorder_id: str,
        mode: Literal["all", "remaining"] = "all"
    ) -> Dict:
        """
        Generate todo list from plan task breakdown.

        Args:
            plan_path: Path to plan.json file
            workorder_id: Workorder ID (e.g., WO-AUTH-001)
            mode: "all" = all tasks, "remaining" = only incomplete tasks

        Returns:
            Dict with todos array and metadata

        Raises:
            FileNotFoundError: Plan file not found
            ValueError: Invalid plan format or missing workorder ID
        """
        # Validate inputs
        if not workorder_id:
            raise ValueError("Workorder ID is required")

        # Read plan file
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in plan file: {plan_path}")

        # Verify workorder ID matches
        plan_workorder = plan.get('workorder_id')
        if plan_workorder != workorder_id:
            raise ValueError(
                f"Workorder ID mismatch: expected {workorder_id}, "
                f"found {plan_workorder}"
            )

        # Extract task breakdown
        task_breakdown = plan.get('task_breakdown')
        if not task_breakdown:
            raise ValueError("No task breakdown found in plan")

        # Generate todos
        todos = []
        for task in task_breakdown:
            # Skip completed tasks if mode is "remaining"
            if mode == "remaining":
                execution_status = task.get('execution_status', {})
                if execution_status.get('status') == 'completed':
                    continue

            todo = self._convert_task_to_todo(task, workorder_id)
            todos.append(todo)

        self.generated_at = datetime.now(UTC).isoformat()

        return {
            "todos": todos,
            "workorder_id": workorder_id,
            "total_tasks": len(todos),
            "mode": mode,
            "generated_at": self.generated_at,
            "plan_path": str(plan_path),
            "summary": f"Generated {len(todos)} todos from {workorder_id} implementation plan"
        }

    def _convert_task_to_todo(self, task: Dict, workorder_id: str) -> Dict:
        """
        Convert a single plan task to todo format.

        Args:
            task: Task object from plan
            workorder_id: Workorder ID for metadata

        Returns:
            Todo dict compatible with TodoWrite
        """
        description = task.get('description', 'No description')
        task_id = task.get('task_id')

        # Generate imperative form (content)
        content = self._to_imperative_form(description)

        # Generate present continuous form (activeForm)
        active_form = self._to_active_form(description)

        # Extract acceptance criteria
        acceptance_criteria = task.get('acceptance_criteria', [])

        # Determine initial status
        execution_status = task.get('execution_status', {})
        status = execution_status.get('status', 'pending')

        # Build todo
        todo = {
            "content": content,
            "activeForm": active_form,
            "status": status,
            "metadata": {
                "workorder_id": workorder_id,
                "task_id": task_id,
                "plan_section": "implementation",
                "acceptance_criteria": acceptance_criteria,
                "files": task.get('files', []),
                "estimated_time": task.get('estimated_time'),
                "dependencies": task.get('dependencies', [])
            }
        }

        return todo

    def _to_imperative_form(self, description: str) -> str:
        """
        Convert description to imperative form (command).

        Examples:
            "Implementing JWT validation" → "Implement JWT validation"
            "Create middleware" → "Create middleware"
        """
        # Remove common present continuous patterns
        description = description.strip()

        # Handle "Implementing X" → "Implement X"
        if description.lower().startswith('implementing '):
            return 'Implement ' + description[13:]

        # Handle "Creating X" → "Create X"
        if description.lower().startswith('creating '):
            return 'Create ' + description[9:]

        # Handle "Adding X" → "Add X"
        if description.lower().startswith('adding '):
            return 'Add ' + description[7:]

        # Handle "Writing X" → "Write X"
        if description.lower().startswith('writing '):
            return 'Write ' + description[8:]

        # Handle "Updating X" → "Update X"
        if description.lower().startswith('updating '):
            return 'Update ' + description[9:]

        # Handle "Testing X" → "Test X"
        if description.lower().startswith('testing '):
            return 'Test ' + description[8:]

        # If already imperative, return as-is
        return description

    def _to_active_form(self, description: str) -> str:
        """
        Convert description to present continuous form (active).

        Examples:
            "Implement JWT validation" → "Implementing JWT validation"
            "Create middleware" → "Creating middleware"
        """
        description = description.strip()

        # Handle "Implement X" → "Implementing X"
        if description.lower().startswith('implement '):
            return 'Implementing ' + description[10:]

        # Handle "Create X" → "Creating X"
        if description.lower().startswith('create '):
            return 'Creating ' + description[7:]

        # Handle "Add X" → "Adding X"
        if description.lower().startswith('add '):
            return 'Adding ' + description[4:]

        # Handle "Write X" → "Writing X"
        if description.lower().startswith('write '):
            return 'Writing ' + description[6:]

        # Handle "Update X" → "Updating X"
        if description.lower().startswith('update '):
            return 'Updating ' + description[7:]

        # Handle "Test X" → "Testing X"
        if description.lower().startswith('test '):
            return 'Testing ' + description[5:]

        # Handle "Fix X" → "Fixing X"
        if description.lower().startswith('fix '):
            return 'Fixing ' + description[4:]

        # Handle "Remove X" → "Removing X"
        if description.lower().startswith('remove '):
            return 'Removing ' + description[7:]

        # Handle "Refactor X" → "Refactoring X"
        if description.lower().startswith('refactor '):
            return 'Refactoring ' + description[9:]

        # If already in active form, return as-is
        if description.lower().endswith('ing'):
            return description

        # Default: add "ing" to first word
        words = description.split(' ', 1)
        if len(words) > 1:
            return words[0] + 'ing ' + words[1]
        else:
            return description + 'ing'

    def generate_from_quick_plan(
        self,
        plan_path: str,
        workorder_id: str
    ) -> Dict:
        """
        Generate todo list from quick plan format.

        Quick plans have simplified structure with "tasks" array
        instead of "task_breakdown".

        Args:
            plan_path: Path to quick-plan.json
            workorder_id: Workorder ID

        Returns:
            Dict with todos array and metadata
        """
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)

        # Quick plans have tasks under plan.tasks
        plan_data = plan.get('plan', {})
        tasks = plan_data.get('tasks', [])

        if not tasks:
            raise ValueError("No tasks found in quick plan")

        todos = []
        for task in tasks:
            todo = self._convert_task_to_todo(task, workorder_id)
            todos.append(todo)

        return {
            "todos": todos,
            "workorder_id": workorder_id,
            "total_tasks": len(todos),
            "mode": "quick_plan",
            "generated_at": datetime.now(UTC).isoformat(),
            "plan_path": str(plan_path),
            "summary": f"Generated {len(todos)} todos from {workorder_id} quick plan"
        }
