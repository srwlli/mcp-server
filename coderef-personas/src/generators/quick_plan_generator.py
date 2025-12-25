"""
QuickPlanGenerator - Lightweight planning for simple tasks

Part of docs-expert v2.0 Phase 2: Planning Flexibility

Generates 3-section plans (context, tasks, validation) for simple tasks
without the full planning workflow overhead.
"""

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Literal, Optional

from src.generators.todo_list_generator import TodoListGenerator


class QuickPlanGenerator:
    """
    Generate lightweight plans for simple tasks.

    Features:
    - 3 sections: context, tasks, validation (not 10 sections)
    - 3-5 tasks (not 10+)
    - Skip gathering, analysis, full validation
    - Auto-generate todos
    - Complexity-based task breakdown
    """

    def __init__(self):
        self.todo_generator = TodoListGenerator()

    def generate_quick_plan(
        self,
        feature_name: str,
        description: str,
        complexity: Literal["trivial", "simple", "moderate"] = "simple",
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Generate a quick plan for a simple task.

        Args:
            feature_name: Short feature name (e.g., "add-persona-field")
            description: Brief description (1-3 sentences)
            complexity: Task complexity level
            output_dir: Optional output directory (default: coderef/working/{feature_name}/)

        Returns:
            Quick plan with workorder ID, tasks, and todos
        """
        # Generate workorder ID
        workorder_id = self._generate_workorder_id(feature_name)

        # Determine task count based on complexity
        task_count = self._get_task_count_for_complexity(complexity)

        # Generate tasks
        tasks = self._generate_tasks(
            feature_name=feature_name,
            description=description,
            complexity=complexity,
            task_count=task_count
        )

        # Estimate total time
        estimated_time = self._estimate_total_time(tasks)

        # Build quick plan
        quick_plan = {
            "workorder_id": workorder_id,
            "feature_name": feature_name,
            "description": description,
            "complexity": complexity,
            "created_at": datetime.now(UTC).isoformat(),
            "plan": {
                "context": {
                    "what": self._extract_what(description),
                    "why": self._extract_why(description),
                    "estimated_time": estimated_time
                },
                "tasks": tasks,
                "validation": {
                    "tests": self._generate_validation_tests(tasks),
                    "estimated_time": self._estimate_validation_time(tasks)
                }
            },
            "skipped_steps": [
                "gather_context",
                "analyze_project",
                "full_validation",
                "ten_section_plan"
            ]
        }

        # Determine output path
        if output_dir is None:
            output_dir = f"coderef/working/{feature_name}"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        plan_file = output_path / "quick-plan.json"

        # Save quick plan
        with open(plan_file, 'w') as f:
            json.dump(quick_plan, f, indent=2)

        # Auto-generate todos
        todos_result = self.todo_generator.generate_todo_list(
            plan_path=str(plan_file),
            workorder_id=workorder_id,
            mode="all"
        )

        # Return result
        return {
            "workorder_id": workorder_id,
            "feature_name": feature_name,
            "complexity": complexity,
            "total_tasks": len(tasks),
            "estimated_time": estimated_time,
            "plan": quick_plan,
            "todos": todos_result['todos'],
            "output_path": str(plan_file),
            "summary": f"Quick plan generated: {len(tasks)} tasks, ~{estimated_time}",
            "generated_at": datetime.now(UTC).isoformat()
        }

    def _generate_workorder_id(self, feature_name: str) -> str:
        """Generate workorder ID from feature name."""
        # Convert feature-name → FEATURE-NAME
        workorder_base = feature_name.upper().replace("-", "-")
        return f"WO-{workorder_base}-001"

    def _get_task_count_for_complexity(self, complexity: str) -> int:
        """Determine task count based on complexity."""
        return {
            "trivial": 2,
            "simple": 3,
            "moderate": 5
        }[complexity]

    def _generate_tasks(
        self,
        feature_name: str,
        description: str,
        complexity: str,
        task_count: int
    ) -> List[Dict]:
        """
        Generate task breakdown based on complexity.

        Uses heuristics to create appropriate tasks:
        - Trivial: 2 tasks (implement + test/doc)
        - Simple: 3 tasks (implement + test + doc)
        - Moderate: 5 tasks (implement + test + doc + review + integration)
        """
        tasks = []

        # Task 1: Always implement the feature
        tasks.append({
            "task_id": 1,
            "description": self._generate_implementation_description(description),
            "files": self._infer_files(feature_name, "implementation"),
            "acceptance_criteria": self._generate_acceptance_criteria(description, "implementation"),
            "estimated_time": self._estimate_task_time(complexity, "implementation"),
            "dependencies": []
        })

        # Task 2: Tests (for simple and moderate) or docs (for trivial)
        if complexity == "trivial":
            tasks.append({
                "task_id": 2,
                "description": f"Update documentation for {feature_name}",
                "files": self._infer_files(feature_name, "documentation"),
                "acceptance_criteria": [
                    "Documentation updated with new changes",
                    "Examples provided if applicable"
                ],
                "estimated_time": self._estimate_task_time(complexity, "documentation"),
                "dependencies": [1]
            })
        else:
            # Add tests for simple/moderate
            tasks.append({
                "task_id": 2,
                "description": f"Write unit tests for {feature_name}",
                "files": self._infer_files(feature_name, "tests"),
                "acceptance_criteria": [
                    "Unit tests cover main functionality",
                    "All tests passing",
                    "Edge cases tested"
                ],
                "estimated_time": self._estimate_task_time(complexity, "tests"),
                "dependencies": [1]
            })

            # Task 3: Documentation (for simple/moderate)
            tasks.append({
                "task_id": 3,
                "description": f"Update documentation for {feature_name}",
                "files": self._infer_files(feature_name, "documentation"),
                "acceptance_criteria": [
                    "Documentation updated with new changes",
                    "Examples provided",
                    "README updated if needed"
                ],
                "estimated_time": self._estimate_task_time(complexity, "documentation"),
                "dependencies": [1]
            })

        # Additional tasks for moderate complexity
        if complexity == "moderate":
            tasks.append({
                "task_id": 4,
                "description": f"Code review and refinement for {feature_name}",
                "files": self._infer_files(feature_name, "implementation"),
                "acceptance_criteria": [
                    "Code reviewed for quality",
                    "Edge cases handled",
                    "Error handling implemented"
                ],
                "estimated_time": "10 minutes",
                "dependencies": [1, 2]
            })

            tasks.append({
                "task_id": 5,
                "description": f"Integration testing for {feature_name}",
                "files": self._infer_files(feature_name, "integration_tests"),
                "acceptance_criteria": [
                    "Integration tests written",
                    "Feature works end-to-end",
                    "All tests passing"
                ],
                "estimated_time": "15 minutes",
                "dependencies": [1, 2, 4]
            })

        return tasks[:task_count]

    def _generate_implementation_description(self, description: str) -> str:
        """Generate implementation task description."""
        # Simple heuristic: if description starts with action verb, use it
        # Otherwise, add "Implement"
        action_verbs = ["add", "update", "fix", "remove", "refactor", "create", "implement"]

        first_word = description.lower().split()[0] if description else ""

        if first_word in action_verbs:
            return description
        else:
            return f"Implement {description}"

    def _infer_files(self, feature_name: str, task_type: str) -> List[str]:
        """Infer likely files to modify based on feature name and task type."""
        if task_type == "implementation":
            # Try to guess implementation files
            if "persona" in feature_name.lower():
                return ["src/models.py", "src/persona_manager.py"]
            elif "test" in feature_name.lower():
                return [f"tests/test_{feature_name.replace('-', '_')}.py"]
            elif "doc" in feature_name.lower():
                return ["README.md", "CLAUDE.md"]
            else:
                return [f"src/{feature_name.replace('-', '_')}.py"]

        elif task_type == "tests":
            return [f"tests/test_{feature_name.replace('-', '_')}.py"]

        elif task_type == "documentation":
            return ["README.md", "CLAUDE.md", "my-guide.md"]

        elif task_type == "integration_tests":
            return [f"tests/integration/test_{feature_name.replace('-', '_')}.py"]

        else:
            return []

    def _generate_acceptance_criteria(self, description: str, task_type: str) -> List[str]:
        """Generate acceptance criteria based on task type."""
        if task_type == "implementation":
            return [
                "Implementation complete",
                "Code follows project patterns",
                "No breaking changes"
            ]
        elif task_type == "tests":
            return [
                "Unit tests passing",
                "Code coverage adequate",
                "Edge cases tested"
            ]
        elif task_type == "documentation":
            return [
                "Documentation updated",
                "Examples provided",
                "Clear and concise"
            ]
        else:
            return ["Task completed successfully"]

    def _estimate_task_time(self, complexity: str, task_type: str) -> str:
        """Estimate time for a task based on complexity and type."""
        time_matrix = {
            "trivial": {
                "implementation": "5 minutes",
                "tests": "5 minutes",
                "documentation": "5 minutes"
            },
            "simple": {
                "implementation": "10 minutes",
                "tests": "8 minutes",
                "documentation": "7 minutes"
            },
            "moderate": {
                "implementation": "20 minutes",
                "tests": "15 minutes",
                "documentation": "10 minutes"
            }
        }

        return time_matrix.get(complexity, {}).get(task_type, "15 minutes")

    def _estimate_total_time(self, tasks: List[Dict]) -> str:
        """Calculate total estimated time from tasks."""
        total_minutes = 0

        for task in tasks:
            time_str = task.get("estimated_time", "0 minutes")
            # Parse "X minutes" or "X hours"
            if "minute" in time_str:
                minutes = int(time_str.split()[0])
                total_minutes += minutes
            elif "hour" in time_str:
                hours = int(time_str.split()[0])
                total_minutes += hours * 60

        # Add validation time (approximately 25% of implementation time)
        validation_minutes = int(total_minutes * 0.25)
        total_minutes += validation_minutes

        # Format output
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"

    def _extract_what(self, description: str) -> str:
        """Extract 'what' from description."""
        # Simple heuristic: use the description as-is for "what"
        return description

    def _extract_why(self, description: str) -> str:
        """Extract 'why' from description (or provide generic reason)."""
        # If description contains "to" or "for", extract the reason
        if " to " in description.lower():
            parts = description.lower().split(" to ", 1)
            return f"To {parts[1]}"
        elif " for " in description.lower():
            parts = description.lower().split(" for ", 1)
            return f"For {parts[1]}"
        else:
            return "To improve the codebase"

    def _generate_validation_tests(self, tasks: List[Dict]) -> List[str]:
        """Generate validation test descriptions."""
        tests = []

        # Check if there are test tasks
        has_tests = any("test" in task["description"].lower() for task in tasks)

        if has_tests:
            tests.append("All unit tests passing")
            tests.append("Code coverage meets project standards")

        # Always include basic validation
        tests.append("Feature works as expected")
        tests.append("No breaking changes introduced")

        return tests

    def _estimate_validation_time(self, tasks: List[Dict]) -> str:
        """Estimate validation time (approximately 25% of implementation time)."""
        total_minutes = 0

        for task in tasks:
            time_str = task.get("estimated_time", "0 minutes")
            if "minute" in time_str:
                minutes = int(time_str.split()[0])
                total_minutes += minutes

        validation_minutes = int(total_minutes * 0.25)

        if validation_minutes < 60:
            return f"{validation_minutes} minutes"
        else:
            hours = validation_minutes // 60
            minutes = validation_minutes % 60
            if minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"
