"""Features inventory generator for scanning and cataloging project features."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger, log_error


class FeaturesInventoryGenerator:
    """Generator for creating feature inventory from coderef/workorder and coderef/archived."""

    def __init__(self, project_path: Path):
        """
        Initialize features inventory generator.

        Args:
            project_path: Path to project root directory
        """
        self.project_path = project_path
        self.working_dir = project_path / "coderef" / "workorder"
        self.archived_dir = project_path / "coderef" / "archived"

    def scan_working_features(self) -> List[Dict[str, Any]]:
        """
        Scan coderef/workorder/ for active features.

        Returns:
            List of feature dictionaries with status 'active'
        """
        features = []

        if not self.working_dir.exists():
            logger.debug(f"Working directory not found: {self.working_dir}")
            return features

        for feature_dir in self.working_dir.iterdir():
            if not feature_dir.is_dir():
                continue

            # Skip README.md and other non-feature items
            if feature_dir.name.startswith('.') or feature_dir.name == 'README.md':
                continue

            feature = self._extract_feature_info(feature_dir, status='active')
            if feature:
                features.append(feature)

        return features

    def scan_archived_features(self) -> List[Dict[str, Any]]:
        """
        Scan coderef/archived/ for archived features.

        Returns:
            List of feature dictionaries with status 'archived'
        """
        features = []

        if not self.archived_dir.exists():
            logger.debug(f"Archived directory not found: {self.archived_dir}")
            return features

        # Try to use index.json for archived features metadata
        index_file = self.archived_dir / "index.json"
        archived_metadata = {}

        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    for entry in index_data.get('archived_features', []):
                        folder = entry.get('folder_name')
                        if folder:
                            archived_metadata[folder] = entry
            except (json.JSONDecodeError, IOError) as e:
                log_error('index_read_error', str(e), path=str(index_file))

        for feature_dir in self.archived_dir.iterdir():
            if not feature_dir.is_dir():
                continue

            # Skip index.json and other files
            if feature_dir.name.startswith('.'):
                continue

            feature = self._extract_feature_info(feature_dir, status='archived')
            if feature:
                # Enrich with index.json metadata if available
                if feature_dir.name in archived_metadata:
                    meta = archived_metadata[feature_dir.name]
                    feature['archived_at'] = meta.get('archived_at')
                    if not feature.get('display_name'):
                        feature['display_name'] = meta.get('feature_name')
                features.append(feature)

        return features

    def _extract_feature_info(self, feature_dir: Path, status: str) -> Optional[Dict[str, Any]]:
        """
        Extract feature information from a feature directory.

        Args:
            feature_dir: Path to feature directory
            status: Either 'active' or 'archived'

        Returns:
            Feature dictionary or None if extraction fails
        """
        feature = {
            'name': feature_dir.name,
            'display_name': feature_dir.name.replace('-', ' ').title(),
            'status': status,
            'path': str(feature_dir.relative_to(self.project_path)),
            'has_plan': False,
            'has_context': False,
            'has_deliverables': False,
            'has_communication': False,
        }

        # Check for plan.json
        plan_file = feature_dir / "plan.json"
        if plan_file.exists():
            feature['has_plan'] = True
            plan_data = self._read_json_safely(plan_file)
            if plan_data:
                feature.update(self._extract_plan_info(plan_data))

        # Check for context.json
        context_file = feature_dir / "context.json"
        if context_file.exists():
            feature['has_context'] = True
            context_data = self._read_json_safely(context_file)
            if context_data:
                feature.update(self._extract_context_info(context_data))

        # Check for DELIVERABLES.md
        deliverables_file = feature_dir / "DELIVERABLES.md"
        if deliverables_file.exists():
            feature['has_deliverables'] = True

        # Check for communication.json
        comm_file = feature_dir / "communication.json"
        if comm_file.exists():
            feature['has_communication'] = True

        return feature

    def _read_json_safely(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Safely read JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data or None on error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log_error('json_read_error', str(e), path=str(file_path))
            return None

    def _extract_plan_info(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant info from plan.json.

        Args:
            plan_data: Parsed plan.json data

        Returns:
            Dictionary with extracted plan info
        """
        info = {}

        # Extract from META_DOCUMENTATION
        meta = plan_data.get('META_DOCUMENTATION', {})
        info['workorder_id'] = None
        info['plan_status'] = meta.get('status', 'unknown')
        info['schema_version'] = meta.get('schema_version')
        info['created_at'] = meta.get('created_at') or meta.get('generated_at')

        # Extract from UNIVERSAL_PLANNING_STRUCTURE
        structure = plan_data.get('UNIVERSAL_PLANNING_STRUCTURE', {})

        # Executive summary
        summary = structure.get('1_executive_summary', {})
        info['display_name'] = summary.get('feature_name') or info.get('display_name')
        info['goal'] = summary.get('goal')
        info['complexity'] = summary.get('estimated_complexity')

        # Task ID system for workorder
        task_system = structure.get('5_task_id_system', {})
        workorder = task_system.get('workorder', {})
        info['workorder_id'] = workorder.get('id')

        # Count tasks and progress
        tasks = task_system.get('tasks', [])
        if tasks:
            total = len(tasks)
            # Handle both object and string task formats
            completed = sum(1 for t in tasks if isinstance(t, dict) and t.get('status') == 'completed')
            in_progress = sum(1 for t in tasks if isinstance(t, dict) and t.get('status') == 'in_progress')
            info['task_count'] = total
            info['tasks_completed'] = completed
            info['tasks_in_progress'] = in_progress
            info['progress_percent'] = round((completed / total) * 100) if total > 0 else 0

        return info

    def _extract_context_info(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant info from context.json.

        Args:
            context_data: Parsed context.json data

        Returns:
            Dictionary with extracted context info
        """
        info = {}

        # Use context description as fallback for goal
        if not info.get('goal'):
            info['goal'] = context_data.get('description') or context_data.get('goal')

        # Requirements count
        requirements = context_data.get('requirements', [])
        if requirements:
            info['requirements_count'] = len(requirements)

        return info

    def generate_inventory(self, include_archived: bool = True) -> Dict[str, Any]:
        """
        Generate complete features inventory.

        Args:
            include_archived: Whether to include archived features

        Returns:
            Complete inventory dictionary
        """
        logger.info("Generating features inventory", extra={'project_path': str(self.project_path)})

        working_features = self.scan_working_features()
        archived_features = self.scan_archived_features() if include_archived else []

        inventory = {
            'generated_at': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'summary': {
                'active_count': len(working_features),
                'archived_count': len(archived_features),
                'total_count': len(working_features) + len(archived_features),
            },
            'active_features': working_features,
        }

        if include_archived:
            inventory['archived_features'] = archived_features

        # Calculate statistics
        all_features = working_features + archived_features
        with_workorder = [f for f in all_features if f.get('workorder_id')]
        with_plan = [f for f in all_features if f.get('has_plan')]

        inventory['statistics'] = {
            'features_with_workorder': len(with_workorder),
            'features_with_plan': len(with_plan),
            'features_with_context': len([f for f in all_features if f.get('has_context')]),
            'features_with_deliverables': len([f for f in all_features if f.get('has_deliverables')]),
        }

        logger.info(f"Features inventory generated: {len(working_features)} active, {len(archived_features)} archived")
        return inventory

    def generate_markdown(self, include_archived: bool = True) -> str:
        """
        Generate markdown representation of features inventory.

        Args:
            include_archived: Whether to include archived features

        Returns:
            Markdown formatted string
        """
        inventory = self.generate_inventory(include_archived)

        lines = [
            "# Features Inventory",
            "",
            f"**Generated:** {inventory['generated_at']}",
            f"**Project:** {inventory['project_path']}",
            "",
            "## Summary",
            "",
            f"| Metric | Count |",
            f"|--------|-------|",
            f"| Active Features | {inventory['summary']['active_count']} |",
            f"| Archived Features | {inventory['summary']['archived_count']} |",
            f"| Total Features | {inventory['summary']['total_count']} |",
            f"| With Workorder | {inventory['statistics']['features_with_workorder']} |",
            f"| With Plan | {inventory['statistics']['features_with_plan']} |",
            "",
        ]

        # Active features section
        lines.extend([
            "## Active Features",
            "",
        ])

        if inventory['active_features']:
            lines.append("| Feature | Status | Progress | Workorder |")
            lines.append("|---------|--------|----------|-----------|")
            for f in inventory['active_features']:
                progress = f"{f.get('progress_percent', 0)}%" if f.get('task_count') else "N/A"
                workorder = f.get('workorder_id') or '-'
                status = f.get('plan_status', 'unknown')
                lines.append(f"| {f['display_name']} | {status} | {progress} | {workorder} |")
        else:
            lines.append("*No active features*")

        lines.append("")

        # Archived features section
        if include_archived and inventory.get('archived_features'):
            lines.extend([
                "## Archived Features",
                "",
                "| Feature | Archived At | Workorder |",
                "|---------|-------------|-----------|",
            ])
            for f in inventory['archived_features']:
                archived_at = f.get('archived_at', '-')
                if archived_at and archived_at != '-':
                    # Format timestamp for readability
                    try:
                        dt = datetime.fromisoformat(archived_at.replace('Z', '+00:00'))
                        archived_at = dt.strftime('%Y-%m-%d')
                    except (ValueError, AttributeError):
                        pass
                workorder = f.get('workorder_id') or '-'
                lines.append(f"| {f['display_name']} | {archived_at} | {workorder} |")

        lines.append("")
        lines.append("---")
        lines.append("*Generated by docs-mcp features_inventory_generator*")

        return "\n".join(lines)

    def save_inventory(self, output_path: Optional[Path] = None, format: str = 'json') -> Path:
        """
        Save features inventory to file.

        Args:
            output_path: Optional custom output path
            format: Output format ('json' or 'markdown')

        Returns:
            Path to saved file
        """
        if output_path is None:
            ext = '.json' if format == 'json' else '.md'
            output_path = self.project_path / "coderef" / f"features-inventory{ext}"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'json':
            inventory = self.generate_inventory()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)
                f.write('\n')
        else:
            content = self.generate_markdown()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        logger.info(f"Features inventory saved to {output_path}")
        return output_path
