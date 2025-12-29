"""Handoff context generator for automated agent handoffs."""

from pathlib import Path
from typing import Dict, Optional, List
import json
import subprocess
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from generators.base_generator import BaseGenerator
from logger_config import logger, log_error
from constants import PlanningPaths
from uds_helpers import generate_uds_header, generate_uds_footer


class HandoffGenerator(BaseGenerator):
    """Generator for creating agent handoff context files (claude.md)."""

    def __init__(self, project_path: Path):
        """
        Initialize handoff generator.

        Args:
            project_path: Path to project root directory
        """
        templates_dir = Path(__file__).parent.parent / "templates" / "handoff"
        super().__init__(templates_dir)
        self.project_path = project_path

    def generate_handoff_context(
        self,
        feature_name: str,
        mode: str = "full"
    ) -> Dict:
        """
        Generate agent handoff context file (claude.md).

        Args:
            feature_name: Feature name (e.g., "auth-system")
            mode: Template mode - "full" or "minimal" (default: "full")

        Returns:
            Dict with output_path, mode, auto_populated_fields, success status

        Raises:
            ValueError: If feature_name invalid or mode not recognized
            FileNotFoundError: If feature directory doesn't exist
        """
        # Validate inputs
        if not feature_name or not feature_name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"Invalid feature name: {feature_name}")

        if mode not in ["full", "minimal"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'full' or 'minimal'")

        # Locate feature directory
        feature_dir = self.project_path / PlanningPaths.WORKING_DIR / feature_name
        if not feature_dir.exists():
            raise FileNotFoundError(f"Feature directory not found: {feature_dir}")

        logger.info(f"Generating handoff context for feature: {feature_name}, mode: {mode}")

        # Parse data sources
        plan_data = self._parse_plan_json(feature_dir)
        analysis_data = self._parse_analysis_json(feature_dir)
        git_data = self._parse_git_history(feature_name)

        # Render template
        template_name = f"claude-{mode}"  # read_template adds .txt extension
        template_content = self.read_template(template_name)

        # Populate template
        context = self._populate_template(
            template_content,
            feature_name,
            mode,
            plan_data,
            analysis_data,
            git_data
        )

        # Inject UDS YAML frontmatter if workorder_id exists
        if plan_data and 'META_DOCUMENTATION' in plan_data:
            workorder_id = plan_data['META_DOCUMENTATION'].get('workorder_id')
            status = plan_data['META_DOCUMENTATION'].get('status', 'DRAFT')

            if workorder_id:
                # Generate UDS header and footer
                uds_header = generate_uds_header(
                    title=f"Agent Handoff Context - {feature_name}",
                    workorder_id=workorder_id,
                    feature_name=feature_name,
                    status=status,
                    doc_version="1.0"
                )
                uds_footer = generate_uds_footer(
                    workorder_id=workorder_id,
                    feature_name=feature_name,
                    status=status
                )

                # Wrap content with UDS frontmatter
                context = f"{uds_header}\n\n{context}\n\n{uds_footer}"
                logger.info(f"UDS YAML frontmatter added to claude.md for workorder: {workorder_id}")

        # Handle existing claude.md
        output_path = feature_dir / "claude.md"
        if output_path.exists():
            self._backup_existing_file(output_path)

        # Write output
        output_path.write_text(context, encoding="utf-8")
        logger.info(f"Handoff context written to: {output_path}")

        # Calculate auto-population percentage
        auto_populated = self._calculate_auto_population(plan_data, analysis_data, git_data)

        return {
            "output_path": str(output_path.relative_to(self.project_path)),
            "mode": mode,
            "feature_name": feature_name,
            "auto_populated_fields": auto_populated,
            "data_sources": {
                "plan_json": plan_data is not None,
                "analysis_json": analysis_data is not None,
                "git_history": git_data is not None
            },
            "success": True
        }

    def _parse_plan_json(self, feature_dir: Path) -> Optional[Dict]:
        """
        Parse plan.json to extract project goals, phases, and task status.

        Args:
            feature_dir: Path to feature directory

        Returns:
            Parsed plan data or None if file missing/malformed
        """
        plan_file = feature_dir / "plan.json"
        if not plan_file.exists():
            logger.warning(f"plan.json not found: {plan_file}")
            return None

        try:
            plan_data = json.loads(plan_file.read_text(encoding="utf-8"))
            logger.debug(f"Successfully parsed plan.json: {plan_file}")
            return plan_data
        except json.JSONDecodeError as e:
            log_error("plan_json_parse_error", str(e), file=str(plan_file))
            return None

    def _parse_analysis_json(self, feature_dir: Path) -> Optional[Dict]:
        """
        Parse analysis.json to extract tech stack and project structure.

        Args:
            feature_dir: Path to feature directory

        Returns:
            Parsed analysis data or None if file missing/malformed
        """
        analysis_file = feature_dir / "analysis.json"
        if not analysis_file.exists():
            logger.warning(f"analysis.json not found: {analysis_file}")
            return None

        try:
            analysis_data = json.loads(analysis_file.read_text(encoding="utf-8"))
            logger.debug(f"Successfully parsed analysis.json: {analysis_file}")
            return analysis_data
        except json.JSONDecodeError as e:
            log_error("analysis_json_parse_error", str(e), file=str(analysis_file))
            return None

    def _parse_git_history(self, feature_name: str) -> Optional[Dict]:
        """
        Parse git commit history to extract feature-related commits.

        Args:
            feature_name: Feature name to search for in commits

        Returns:
            Dict with recent commits and file changes, or None if git unavailable
        """
        try:
            # Get recent commits matching feature name (case-insensitive)
            result = subprocess.run(
                ["git", "log", f"--grep={feature_name}", "--oneline", "-5", "-i"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning(f"git log failed: {result.stderr}")
                return None

            commits = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

            # Get uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            uncommitted = []
            if status_result.returncode == 0:
                uncommitted = [line.strip() for line in status_result.stdout.strip().split("\n") if line.strip()]

            logger.debug(f"Git history parsed: {len(commits)} commits, {len(uncommitted)} uncommitted files")

            return {
                "recent_commits": commits,
                "uncommitted_changes": uncommitted,
                "commit_count": len(commits)
            }

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Git not available: {e}")
            return None

    def _populate_template(
        self,
        template: str,
        feature_name: str,
        mode: str,
        plan_data: Optional[Dict],
        analysis_data: Optional[Dict],
        git_data: Optional[Dict]
    ) -> str:
        """
        Populate template with extracted data.

        Args:
            template: Template content with {{placeholders}}
            feature_name: Feature name
            mode: Template mode
            plan_data: Parsed plan.json data
            analysis_data: Parsed analysis.json data
            git_data: Parsed git history data

        Returns:
            Populated template content
        """
        # Basic substitutions
        context = template
        context = context.replace("{{feature_name}}", feature_name)
        context = context.replace("{{timestamp}}", datetime.now().isoformat())
        context = context.replace("{{mode}}", mode)

        # Plan data substitutions
        if plan_data:
            workorder = plan_data.get("META_DOCUMENTATION", {}).get("workorder_id", "[NO WORKORDER]")
            context = context.replace("{{workorder_id}}", workorder)

            exec_summary = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get("1_executive_summary", {})
            context = context.replace("{{project_overview}}", exec_summary.get("description", "[DATA NOT AVAILABLE]"))

            # Extract task status
            checklist = plan_data.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get("9_implementation_checklist", {})
            completed, total = self._count_tasks(checklist)
            context = context.replace("{{completed_tasks}}", str(completed))
            context = context.replace("{{total_tasks}}", str(total))

            # Current phase detection
            current_phase = self._detect_current_phase(checklist)
            context = context.replace("{{current_phase}}", current_phase)

            # Next steps (first 3 pending tasks)
            next_steps = self._extract_next_steps(checklist, limit=3)
            context = context.replace("{{next_steps}}", next_steps)

        else:
            context = context.replace("{{workorder_id}}", "[DATA NOT AVAILABLE]")
            context = context.replace("{{project_overview}}", "[DATA NOT AVAILABLE - plan.json missing]")
            context = context.replace("{{completed_tasks}}", "?")
            context = context.replace("{{total_tasks}}", "?")
            context = context.replace("{{current_phase}}", "[UNKNOWN]")
            context = context.replace("{{next_steps}}", "[DATA NOT AVAILABLE]")

        # Analysis data substitutions
        if analysis_data:
            tech_stack = analysis_data.get("technology_stack", {})
            tech_summary = f"Language: {tech_stack.get('language', 'Unknown')}, Framework: {tech_stack.get('framework', 'Unknown')}"
            context = context.replace("{{tech_stack}}", tech_summary)
        else:
            context = context.replace("{{tech_stack}}", "[DATA NOT AVAILABLE]")

        # Git data substitutions
        if git_data:
            commits_text = "\n".join(git_data.get("recent_commits", [])) or "[No commits found]"
            context = context.replace("{{recent_commits}}", commits_text)

            uncommitted_text = "\n".join(git_data.get("uncommitted_changes", [])) or "[No uncommitted changes]"
            context = context.replace("{{uncommitted_changes}}", uncommitted_text)
        else:
            context = context.replace("{{recent_commits}}", "[Git not available]")
            context = context.replace("{{uncommitted_changes}}", "[Git not available]")

        return context

    def _count_tasks(self, checklist: Dict) -> tuple:
        """Count completed vs total tasks in implementation checklist."""
        completed = 0
        total = 0

        for phase_tasks in checklist.values():
            if isinstance(phase_tasks, list):
                for task in phase_tasks:
                    if isinstance(task, str):
                        total += 1
                        if task.startswith("☑"):
                            completed += 1

        return completed, total

    def _detect_current_phase(self, checklist: Dict) -> str:
        """Detect current phase based on task completion status."""
        for phase_key, tasks in checklist.items():
            if phase_key.startswith("phase_") and isinstance(tasks, list):
                for task in tasks:
                    if isinstance(task, str) and (task.startswith("☐") or task.startswith("⏳")):
                        # Extract phase number and name
                        return phase_key.replace("_", " ").title()

        return "All phases complete"

    def _extract_next_steps(self, checklist: Dict, limit: int = 3) -> str:
        """Extract next N pending tasks as numbered list."""
        next_tasks = []

        for phase_tasks in checklist.values():
            if isinstance(phase_tasks, list):
                for task in phase_tasks:
                    if isinstance(task, str) and task.startswith("☐"):
                        # Extract task description (remove checkbox)
                        task_desc = task[2:].strip()  # Remove "☐ "
                        next_tasks.append(task_desc)
                        if len(next_tasks) >= limit:
                            break
                if len(next_tasks) >= limit:
                    break

        if not next_tasks:
            return "[No pending tasks]"

        return "\n".join([f"{i+1}. {task}" for i, task in enumerate(next_tasks)])

    def _backup_existing_file(self, file_path: Path) -> None:
        """Create backup of existing file before overwriting."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = file_path.with_suffix(f".backup-{timestamp}.md")
        backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        logger.info(f"Created backup: {backup_path}")

    def _calculate_auto_population(
        self,
        plan_data: Optional[Dict],
        analysis_data: Optional[Dict],
        git_data: Optional[Dict]
    ) -> int:
        """Calculate percentage of auto-populated fields."""
        available = sum([plan_data is not None, analysis_data is not None, git_data is not None])
        total = 3
        return int((available / total) * 100)
