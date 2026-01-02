"""
Workflow Extension - Integration with coderef-workflow

Provides template tags for workflow data:
- {% workflow.get_plan_phases(plan_path) %} - Get plan phases
- {% workflow.get_priority_checklist(plan_path) %} - Get priority-sorted tasks
- {% workflow.plan(feature_name) %} - Get plan metadata (legacy)

Enhanced with plan.json parsing (WO-PAPERTRAIL-EXTENSIONS-001 Phase 3)
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import json


class WorkflowExtension:
    """
    Template extension for coderef-workflow integration

    Enhanced with direct plan.json parsing for phases and priority tasks
    """

    def __init__(self, workorder_dir: Optional[Path] = None):
        """
        Initialize Workflow extension

        Args:
            workorder_dir: Path to coderef/workorder/ directory
        """
        self.workorder_dir = workorder_dir or Path("coderef/workorder")

    def _load_plan(self, plan_path: Path) -> Dict[str, Any]:
        """
        Load plan.json file safely

        Args:
            plan_path: Path to plan.json

        Returns:
            dict: Plan data or empty dict if file doesn't exist
        """
        try:
            if not plan_path.exists():
                return {}

            with open(plan_path, "r") as f:
                return json.load(f)

        except (json.JSONDecodeError, OSError):
            return {}

    def get_plan_phases(self, plan_path: str) -> List[Dict[str, Any]]:
        """
        Extract implementation phases from plan.json

        Args:
            plan_path: Path to plan.json file

        Returns:
            list: List of phases with name, status, duration, deliverables
        """
        plan = self._load_plan(Path(plan_path))

        phases_section = plan.get("6_implementation_phases", {})
        phases_list = phases_section.get("phases", [])

        extracted_phases = []
        for phase in phases_list:
            extracted_phases.append({
                "name": phase.get("name", ""),
                "status": phase.get("status", "pending"),
                "duration": phase.get("estimated_duration", ""),
                "deliverables": phase.get("deliverables", [])
            })

        return extracted_phases

    def get_priority_checklist(self, plan_path: str) -> List[Dict[str, Any]]:
        """
        Extract tasks sorted by priority from plan.json

        Args:
            plan_path: Path to plan.json file

        Returns:
            list: List of tasks sorted by priority (critical > high > medium > low)
        """
        plan = self._load_plan(Path(plan_path))

        # Extract tasks from all phases
        phases_section = plan.get("6_implementation_phases", {})
        phases_list = phases_section.get("phases", [])

        all_tasks = []
        for phase in phases_list:
            tasks = phase.get("tasks", [])
            for task in tasks:
                # Tasks can be strings (task IDs) or dicts (full task objects)
                if isinstance(task, dict):
                    all_tasks.append({
                        "task_id": task.get("id", task.get("task_id", "")),
                        "description": task.get("description", task.get("title", "")),
                        "priority": task.get("priority", "medium"),
                        "status": task.get("status", "pending")
                    })
                else:
                    # Task is just an ID string
                    all_tasks.append({
                        "task_id": task,
                        "description": task,
                        "priority": "medium",
                        "status": "pending"
                    })

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_tasks.sort(key=lambda t: priority_order.get(t["priority"], 2))

        return all_tasks

    # Legacy methods (kept for backward compatibility)

    def plan(self, feature_name: str) -> Dict[str, Any]:
        """
        Get plan metadata for feature (legacy method)

        Args:
            feature_name: Feature name

        Returns:
            dict: Plan metadata
        """
        plan_path = self.workorder_dir / feature_name / "plan.json"

        if plan_path.exists():
            plan_data = self._load_plan(plan_path)
            return plan_data.get("META_DOCUMENTATION", {})

        return {
            "workorder_id": f"WO-{feature_name.upper()}-001",
            "feature_name": feature_name,
            "status": "in_progress",
            "message": "(Mock plan data)"
        }

    def tasks(self, feature_name: str) -> List[Dict[str, str]]:
        """
        Get task list for feature (legacy method)

        Args:
            feature_name: Feature name

        Returns:
            list: List of tasks
        """
        plan_path = self.workorder_dir / feature_name / "plan.json"

        if plan_path.exists():
            plan_data = self._load_plan(plan_path)
            phases = plan_data.get("6_implementation_phases", {}).get("phases", [])

            tasks = []
            for phase in phases:
                for task in phase.get("tasks", []):
                    if isinstance(task, dict):
                        tasks.append({
                            "id": task.get("id", task.get("task_id", "")),
                            "title": task.get("description", task.get("title", "")),
                            "status": task.get("status", "pending")
                        })
                    else:
                        tasks.append({
                            "id": task,
                            "title": task,
                            "status": "pending"
                        })
            return tasks

        return [
            {"id": "TASK-001", "title": "Setup", "status": "completed"},
            {"id": "TASK-002", "title": "Implementation", "status": "in_progress"},
            {"id": "TASK-003", "title": "Testing", "status": "pending"}
        ]

    def progress(self, feature_name: str) -> int:
        """
        Get progress percentage for feature (legacy method)

        Args:
            feature_name: Feature name

        Returns:
            int: Progress percentage (0-100)
        """
        tasks = self.tasks(feature_name)

        if not tasks:
            return 0

        completed = sum(1 for t in tasks if t.get("status") == "completed")
        return int((completed / len(tasks)) * 100)
