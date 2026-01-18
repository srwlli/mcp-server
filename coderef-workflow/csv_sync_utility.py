"""
CSV Sync Utility - Automatic Drift Detection and Reconciliation

Scans project directories for resources (tools, commands, scripts) and compares
against CSV to detect and fix discrepancies.

Part of WO-CSV-ECOSYSTEM-SYNC-001 Phase 3 Task 2 Enhancement.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import re

from csv_manager import (
    read_csv,
    add_csv_entry,
    update_csv_entry,
    update_csv_status,
    check_csv_exists,
    find_csv_entry,
    CSV_PATH
)


class ResourceScanner:
    """Scans project directories to discover resources"""

    def __init__(self, project_path: Path, server_name: str):
        self.project_path = Path(project_path)
        self.server_name = server_name

    def scan_tools_from_server_py(self) -> List[Dict[str, str]]:
        """Scan server.py for MCP tool definitions"""
        tools = []
        server_py = self.project_path / "server.py"

        if not server_py.exists():
            return tools

        content = server_py.read_text(encoding='utf-8')

        # Parse @app.list_tools() to extract tool definitions
        # Look for Tool(name="...", description="...")
        tool_pattern = r'Tool\s*\(\s*name\s*=\s*["\']([^"\']+)["\'].*?description\s*=\s*["\']([^"\']+)["\']'
        matches = re.finditer(tool_pattern, content, re.DOTALL)

        for match in matches:
            tool_name = match.group(1)
            description = match.group(2)

            # Clean up description (truncate if too long)
            if len(description) > 100:
                description = description[:97] + "..."

            tools.append({
                'Type': 'Tool',
                'Server': self.server_name,
                'Category': self._infer_category_from_name(tool_name),
                'Name': tool_name,
                'Description': description,
                'Status': 'active',
                'Path': str(server_py),
                'Created': '',
                'LastUpdated': ''
            })

        return tools

    def scan_commands_from_claude_dir(self) -> List[Dict[str, str]]:
        """Scan .claude/commands/ for slash commands"""
        commands = []
        commands_dir = self.project_path / ".claude" / "commands"

        if not commands_dir.exists():
            return commands

        for cmd_file in commands_dir.glob("*.md"):
            cmd_name = f"/{cmd_file.stem}"

            # Read frontmatter or first line for description
            content = cmd_file.read_text(encoding='utf-8')
            description = self._extract_description_from_md(content, cmd_file.stem)

            commands.append({
                'Type': 'Command',
                'Server': self.server_name,
                'Category': self._infer_category_from_name(cmd_name),
                'Name': cmd_name,
                'Description': description,
                'Status': 'active',
                'Path': str(cmd_file),
                'Created': '',
                'LastUpdated': ''
            })

        return commands

    def scan_scripts(self) -> List[Dict[str, str]]:
        """Scan scripts/ directory for automation scripts"""
        scripts = []
        scripts_dir = self.project_path / "scripts"

        if not scripts_dir.exists():
            return scripts

        for script_file in scripts_dir.rglob("*.py"):
            if script_file.name.startswith('_'):
                continue  # Skip private/internal scripts

            # Extract description from docstring
            content = script_file.read_text(encoding='utf-8')
            description = self._extract_docstring(content, script_file.name)

            scripts.append({
                'Type': 'Script',
                'Server': self.server_name,
                'Category': 'Automation',
                'Name': script_file.stem,
                'Description': description,
                'Status': 'active',
                'Path': str(script_file),
                'Created': '',
                'LastUpdated': ''
            })

        return scripts

    def _infer_category_from_name(self, name: str) -> str:
        """Infer category from resource name"""
        name_lower = name.lower()

        if any(kw in name_lower for kw in ['plan', 'workorder', 'gather', 'analyze']):
            return 'Planning'
        elif any(kw in name_lower for kw in ['execute', 'track', 'status', 'task']):
            return 'Execution & Tracking'
        elif any(kw in name_lower for kw in ['doc', 'changelog', 'template', 'readme']):
            return 'Documentation'
        elif any(kw in name_lower for kw in ['archive', 'feature', 'inventory']):
            return 'Archival & Inventory'
        elif any(kw in name_lower for kw in ['agent', 'communication', 'assign', 'verify']):
            return 'Multi-Agent Coordination'
        elif any(kw in name_lower for kw in ['test', 'coverage', 'report']):
            return 'Testing'
        elif any(kw in name_lower for kw in ['risk', 'assess', 'audit']):
            return 'Standards & Quality'
        else:
            return 'Workflow'

    def _extract_description_from_md(self, content: str, filename: str) -> str:
        """Extract description from markdown file"""
        lines = content.split('\n')

        # Check for frontmatter description
        if lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    break
                if line.startswith('description:'):
                    desc = line.split('description:', 1)[1].strip()
                    return desc if len(desc) <= 100 else desc[:97] + "..."

        # Fallback: use first non-empty, non-header line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                return line[:97] + "..." if len(line) > 100 else line

        # Last resort: use filename
        return f"{filename.replace('-', ' ').title()}"

    def _extract_docstring(self, content: str, filename: str) -> str:
        """Extract docstring from Python file"""
        # Look for module-level docstring
        match = re.search(r'^\s*"""(.+?)"""', content, re.MULTILINE | re.DOTALL)
        if match:
            docstring = match.group(1).strip()
            # Take first line only
            first_line = docstring.split('\n')[0].strip()
            return first_line[:97] + "..." if len(first_line) > 100 else first_line

        return f"{filename.replace('_', ' ').replace('.py', '').title()}"


class CSVSyncUtility:
    """Main CSV sync utility for drift detection and reconciliation"""

    def __init__(self, project_path: Path, server_name: str):
        self.project_path = Path(project_path)
        self.server_name = server_name
        self.scanner = ResourceScanner(project_path, server_name)

    def scan_project_resources(self) -> List[Dict[str, str]]:
        """Scan project for all resources"""
        all_resources = []

        all_resources.extend(self.scanner.scan_tools_from_server_py())
        all_resources.extend(self.scanner.scan_commands_from_claude_dir())
        all_resources.extend(self.scanner.scan_scripts())

        return all_resources

    def detect_drift(self) -> Dict[str, List[Dict]]:
        """
        Detect discrepancies between project and CSV.

        Returns:
            Dict with keys: 'missing_from_csv', 'missing_from_project', 'metadata_mismatch'
        """
        # Get current CSV state
        csv_entries = read_csv()
        csv_resources = {
            (entry['Name'], entry['Server']): entry
            for entry in csv_entries
        }

        # Get project state
        project_resources = self.scan_project_resources()
        project_dict = {
            (res['Name'], res['Server']): res
            for res in project_resources
        }

        # Find discrepancies
        drift = {
            'missing_from_csv': [],
            'missing_from_project': [],
            'metadata_mismatch': []
        }

        # Resources in project but not in CSV
        for key, resource in project_dict.items():
            if key not in csv_resources:
                drift['missing_from_csv'].append(resource)

        # Resources in CSV but not in project (only check this server's entries)
        server_csv_entries = [e for e in csv_entries if e['Server'] == self.server_name]
        for entry in server_csv_entries:
            key = (entry['Name'], entry['Server'])
            if key not in project_dict and entry['Status'] == 'active':
                drift['missing_from_project'].append(entry)

        # Resources with mismatched metadata
        for key in set(csv_resources.keys()) & set(project_dict.keys()):
            csv_res = csv_resources[key]
            proj_res = project_dict[key]

            # Compare key fields (Type, Category, Description, Path)
            mismatches = []
            if csv_res['Type'] != proj_res['Type']:
                mismatches.append(('Type', csv_res['Type'], proj_res['Type']))
            if csv_res['Category'] != proj_res['Category']:
                mismatches.append(('Category', csv_res['Category'], proj_res['Category']))
            if csv_res['Path'] != proj_res['Path']:
                mismatches.append(('Path', csv_res['Path'], proj_res['Path']))

            # Description changes are minor (don't flag)

            if mismatches:
                drift['metadata_mismatch'].append({
                    'resource': key,
                    'csv_entry': csv_res,
                    'project_resource': proj_res,
                    'mismatches': mismatches
                })

        return drift

    def reconcile_drift(
        self,
        add_missing: bool = True,
        mark_deleted: bool = True,
        fix_metadata: bool = True,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Reconcile drift between project and CSV.

        Args:
            add_missing: Add resources found in project but not in CSV
            mark_deleted: Mark resources in CSV but not in project as 'deleted'
            fix_metadata: Update CSV metadata to match project
            dry_run: Preview changes without making them

        Returns:
            Dict with counts: 'added', 'marked_deleted', 'updated', 'errors'
        """
        drift = self.detect_drift()
        stats = {'added': 0, 'marked_deleted': 0, 'updated': 0, 'errors': 0}

        # Add missing resources
        if add_missing:
            for resource in drift['missing_from_csv']:
                try:
                    if not dry_run:
                        add_csv_entry(**resource)
                    stats['added'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"Error adding {resource['Name']}: {e}")

        # Mark deleted resources
        if mark_deleted:
            for entry in drift['missing_from_project']:
                try:
                    if not dry_run:
                        update_csv_status(
                            resource_name=entry['Name'],
                            new_status='deleted',
                            server=entry['Server']
                        )
                    stats['marked_deleted'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"Error marking {entry['Name']} as deleted: {e}")

        # Fix metadata mismatches
        if fix_metadata:
            for mismatch in drift['metadata_mismatch']:
                resource_name = mismatch['resource'][0]
                server = mismatch['resource'][1]
                proj_res = mismatch['project_resource']

                try:
                    if not dry_run:
                        updates = {
                            'Type': proj_res['Type'],
                            'Category': proj_res['Category'],
                            'Path': proj_res['Path']
                        }
                        update_csv_entry(resource_name, server, updates)
                    stats['updated'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"Error updating {resource_name}: {e}")

        return stats

    def generate_drift_report(self) -> str:
        """Generate human-readable drift report"""
        drift = self.detect_drift()

        report = []
        report.append("=" * 60)
        report.append(f"CSV DRIFT REPORT - {self.server_name}")
        report.append("=" * 60)
        report.append("")

        # Summary
        total_drift = (
            len(drift['missing_from_csv']) +
            len(drift['missing_from_project']) +
            len(drift['metadata_mismatch'])
        )

        if total_drift == 0:
            report.append("✅ NO DRIFT DETECTED - CSV is synchronized with project")
            report.append("")
            return "\n".join(report)

        report.append(f"⚠️  DRIFT DETECTED: {total_drift} discrepancies found")
        report.append("")

        # Missing from CSV
        if drift['missing_from_csv']:
            report.append(f"📊 MISSING FROM CSV ({len(drift['missing_from_csv'])} resources)")
            report.append("-" * 60)
            for res in drift['missing_from_csv']:
                report.append(f"  • {res['Type']}: {res['Name']}")
                report.append(f"    Category: {res['Category']}")
                report.append(f"    Path: {res['Path']}")
                report.append("")

        # Missing from project
        if drift['missing_from_project']:
            report.append(f"⚠️  MISSING FROM PROJECT ({len(drift['missing_from_project'])} resources)")
            report.append("-" * 60)
            for entry in drift['missing_from_project']:
                report.append(f"  • {entry['Type']}: {entry['Name']}")
                report.append(f"    Status: {entry['Status']} (should be 'deleted')")
                report.append("")

        # Metadata mismatches
        if drift['metadata_mismatch']:
            report.append(f"🔄 METADATA MISMATCHES ({len(drift['metadata_mismatch'])} resources)")
            report.append("-" * 60)
            for mismatch in drift['metadata_mismatch']:
                name = mismatch['resource'][0]
                report.append(f"  • {name}")
                for field, csv_val, proj_val in mismatch['mismatches']:
                    report.append(f"    {field}:")
                    report.append(f"      CSV:     {csv_val}")
                    report.append(f"      Project: {proj_val}")
                report.append("")

        # Recommendations
        report.append("=" * 60)
        report.append("RECOMMENDATIONS")
        report.append("=" * 60)
        if drift['missing_from_csv']:
            report.append("• Run reconcile_drift(add_missing=True) to add missing resources")
        if drift['missing_from_project']:
            report.append("• Run reconcile_drift(mark_deleted=True) to mark deleted resources")
        if drift['metadata_mismatch']:
            report.append("• Run reconcile_drift(fix_metadata=True) to fix metadata")
        report.append("")

        return "\n".join(report)


def sync_csv_for_server(
    project_path: Path,
    server_name: str,
    add_missing: bool = True,
    mark_deleted: bool = True,
    fix_metadata: bool = True,
    dry_run: bool = False
) -> Tuple[Dict[str, int], str]:
    """
    Convenience function to sync CSV for a specific server.

    Returns:
        Tuple of (stats dict, drift report string)
    """
    utility = CSVSyncUtility(project_path, server_name)

    # Generate drift report
    report = utility.generate_drift_report()

    # Reconcile drift
    stats = utility.reconcile_drift(
        add_missing=add_missing,
        mark_deleted=mark_deleted,
        fix_metadata=fix_metadata,
        dry_run=dry_run
    )

    return stats, report
