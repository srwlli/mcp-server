"""
Workflow Extension - Integration with coderef-workflow

Provides template tags for workflow data:
- {% workflow.plan feature_name %} - Get plan metadata
- {% workflow.tasks feature_name %} - Get task list
- {% workflow.progress feature_name %} - Get progress percentage
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import json


class WorkflowExtension:
    """
    Template extension for coderef-workflow integration

    Provides access to plan.json data and task tracking
    """

    def __init__(self, workorder_dir: Optional[Path] = None):
        """
        Initialize Workflow extension

        Args:
            workorder_dir: Path to coderef/workorder/ directory
        """
        self.workorder_dir = workorder_dir or Path("coderef/workorder")

    def plan(self, feature_name: str) -> Dict[str, Any]:
        """
        Get plan metadata for feature

        Args:
            feature_name: Feature name

        Returns:
            dict: Plan metadata

        Example:
            {% set plan = workflow.plan("auth-system") %}
            Workorder: {{ plan.workorder_id }}
        """
        plan_path = self.workorder_dir / feature_name / "plan.json"

        if plan_path.exists():
            with open(plan_path, 'r') as f:
                data = json.load(f)
                return data.get("META_DOCUMENTATION", {})

        # Mock data if plan doesn't exist
        return {
            "workorder_id": f"WO-{feature_name.upper()}-001",
            "feature_name": feature_name,
            "status": "in_progress",
            "message": "(Mock plan data - Phase 2 implementation)"
        }

    def tasks(self, feature_name: str) -> List[Dict[str, str]]:
        """
        Get task list for feature

        Args:
            feature_name: Feature name

        Returns:
            list: List of tasks

        Example:
            {% for task in workflow.tasks("auth-system") %}
            - {{ task.id }}: {{ task.title }}
            {% endfor %}
        """
        plan_path = self.workorder_dir / feature_name / "plan.json"

        if plan_path.exists():
            with open(plan_path, 'r') as f:
                data = json.load(f)
                # Extract tasks from phases
                tasks = []
                phases = data.get("6_implementation_phases", {}).get("phases", [])
                for phase in phases:
                    for task_id in phase.get("tasks", []):
                        tasks.append({
                            "id": task_id,
                            "title": task_id,  # Simplified
                            "status": "pending"
                        })
                return tasks

        # Mock data
        return [
            {"id": "TASK-001", "title": "Setup", "status": "completed"},
            {"id": "TASK-002", "title": "Implementation", "status": "in_progress"},
            {"id": "TASK-003", "title": "Testing", "status": "pending"}
        ]

    def progress(self, feature_name: str) -> int:
        """
        Get progress percentage for feature

        Args:
            feature_name: Feature name

        Returns:
            int: Progress percentage (0-100)

        Example:
            Progress: {% workflow.progress("auth-system") %}%
        """
        tasks = self.tasks(feature_name)

        if not tasks:
            return 0

        completed = sum(1 for t in tasks if t.get("status") == "completed")
        return int((completed / len(tasks)) * 100)
