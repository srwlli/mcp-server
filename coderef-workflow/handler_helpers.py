"""
Handler helper functions for MCP tool handlers (QUA-004).

Provides utility functions for common handler operations like response formatting.
These helpers ensure consistency across all tool handlers.

Usage:
    from handler_helpers import format_success_response

    result = format_success_response(
        data={'files': files_list, 'count': len(files_list)},
        message="✅ Operation completed successfully"
    )
"""

from mcp.types import TextContent
import json
from datetime import datetime, timezone
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


# Workorder ID Generation Helper
def generate_workorder_id(feature_name: str) -> str:
    """
    Generate workorder ID from feature name.

    Format: WO-{FEATURE-NAME}-001
    - Converts feature name to uppercase
    - Preserves hyphens
    - Appends -001 suffix

    Args:
        feature_name: Feature directory name (e.g., 'auth-system', 'deliverables-generator')

    Returns:
        Formatted workorder ID (e.g., 'WO-AUTH-SYSTEM-001', 'WO-DELIVERABLES-GENERATOR-001')

    Example:
        >>> generate_workorder_id('auth-system')
        'WO-AUTH-SYSTEM-001'
        >>> generate_workorder_id('deliverables-generator')
        'WO-DELIVERABLES-GENERATOR-001'
    """
    # Convert to uppercase and append WO- prefix and -001 suffix
    return f"WO-{feature_name.upper()}-001"


def get_workorder_timestamp() -> str:
    """
    Get current timestamp in ISO 8601 format for workorder metadata.

    Returns:
        ISO 8601 formatted timestamp with UTC timezone

    Example:
        >>> get_workorder_timestamp()
        '2025-10-18T15:30:00.123456+00:00'
    """
    return datetime.now(timezone.utc).isoformat()


# STUB-036: Timestamp Enforcement Helper
def add_response_timestamp(data: dict) -> dict:
    """
    Add ISO 8601 timestamp to response data (STUB-036).

    Adds 'timestamp' field to any response dictionary.
    Used to ensure all workflow outputs include timestamps.

    Args:
        data: Response dictionary to add timestamp to

    Returns:
        Same dictionary with 'timestamp' field added

    Example:
        >>> result = add_response_timestamp({'success': True, 'files': []})
        >>> 'timestamp' in result
        True
        >>> result['timestamp']
        '2025-12-17T20:15:00.123456+00:00'
    """
    data['timestamp'] = get_workorder_timestamp()
    return data


# QUA-004: Success Response Helper
def format_success_response(data: dict, message: str = None, include_timestamp: bool = True) -> list[TextContent]:
    """
    Helper function for formatting consistent success responses (QUA-004, STUB-036).

    Formats handler success responses as JSON-formatted TextContent.
    Provides consistent structure across all tool handlers.

    STUB-036: Automatically adds ISO 8601 timestamp to all responses
    unless explicitly disabled via include_timestamp=False.

    Args:
        data: Dictionary containing response data
        message: Optional success message to prepend
        include_timestamp: Whether to add timestamp (default: True, STUB-036)

    Returns:
        List containing single TextContent with JSON-formatted response

    Example:
        return format_success_response(
            data={'files': files_list, 'count': len(files_list)},
            message="✅ Operation completed successfully"
        )
        # Response will include 'timestamp': '2025-12-17T20:15:00+00:00'
    """
    # STUB-036: Add timestamp to all responses by default
    if include_timestamp:
        data = add_response_timestamp(data)

    if message:
        # Prepend message to JSON data
        result = f"{message}\n\n{json.dumps(data, indent=2)}"
    else:
        # Just format as JSON
        result = json.dumps(data, indent=2)

    return [TextContent(type="text", text=result)]


# Git Utility Helpers for Deliverables Generator

def git_parse_history(project_path: Path, feature_name: str) -> List[Dict[str, str]]:
    """
    Parse git commit history to discover commits related to a feature.

    Searches commit messages for feature name (case-insensitive, fuzzy match).
    Returns commit hash, author, date, and message for matching commits.

    Args:
        project_path: Absolute path to project directory (must be git repo)
        feature_name: Feature name to search for in commit messages

    Returns:
        List of commit dictionaries with keys: hash, author, date, message
        Returns empty list if no commits found or git fails

    Example:
        >>> commits = git_parse_history(Path('/path/to/repo'), 'auth-system')
        >>> len(commits)
        5
        >>> commits[0]['message']
        'feat: implement auth-system with JWT tokens'
    """
    try:
        # Use git log with format: hash|author|date|message
        cmd = [
            'git', 'log',
            '--all',  # Search all branches
            '--format=%H|%an|%ai|%s',  # hash|author|ISO date|subject
            f'--grep={feature_name}',  # Search for feature name
            '--regexp-ignore-case'  # Case-insensitive search
        ]

        result = subprocess.run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    'hash': parts[0][:8],  # Short hash
                    'author': parts[1],
                    'date': parts[2],
                    'message': parts[3]
                })

        return commits

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return []


def git_calculate_loc(project_path: Path, feature_name: str) -> Dict[str, int]:
    """
    Calculate lines of code changed for a feature using git diff.

    Sums LOC changes from all commits related to the feature.
    Uses git diff --stat to count insertions and deletions.

    Args:
        project_path: Absolute path to project directory (must be git repo)
        feature_name: Feature name to search for in commit messages

    Returns:
        Dictionary with keys: added, deleted, net
        Returns {added: 0, deleted: 0, net: 0} if no commits or git fails

    Example:
        >>> loc = git_calculate_loc(Path('/path/to/repo'), 'auth-system')
        >>> loc
        {'added': 450, 'deleted': 120, 'net': 330}
    """
    try:
        # Get commit hashes for the feature
        commits = git_parse_history(project_path, feature_name)
        if not commits:
            return {'added': 0, 'deleted': 0, 'net': 0}

        total_added = 0
        total_deleted = 0

        # For each commit, get diff stats
        for commit in commits:
            cmd = [
                'git', 'show',
                commit['hash'],
                '--numstat',
                '--format='
            ]

            result = subprocess.run(
                cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        try:
                            added = int(parts[0]) if parts[0] != '-' else 0
                            deleted = int(parts[1]) if parts[1] != '-' else 0
                            total_added += added
                            total_deleted += deleted
                        except ValueError:
                            continue

        return {
            'added': total_added,
            'deleted': total_deleted,
            'net': total_added - total_deleted
        }

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return {'added': 0, 'deleted': 0, 'net': 0}


def git_calculate_time_spent(project_path: Path, feature_name: str) -> Dict[str, any]:
    """
    Calculate time spent on a feature from first to last commit.

    Uses commit timestamps to calculate elapsed time.
    Returns days and hours spent (wall clock time, not actual work time).

    Args:
        project_path: Absolute path to project directory (must be git repo)
        feature_name: Feature name to search for in commit messages

    Returns:
        Dictionary with keys: days, hours, first_commit, last_commit
        Returns zeros if less than 2 commits found

    Example:
        >>> time = git_calculate_time_spent(Path('/path/to/repo'), 'auth-system')
        >>> time
        {'days': 3, 'hours': 72, 'first_commit': '2025-10-15', 'last_commit': '2025-10-18'}
    """
    try:
        commits = git_parse_history(project_path, feature_name)
        if len(commits) < 2:
            return {'days': 0, 'hours': 0, 'first_commit': None, 'last_commit': None}

        # Parse dates (ISO format: 2025-10-18 14:30:22 -0400)
        dates = [datetime.fromisoformat(c['date'].rsplit(' ', 1)[0]) for c in commits]
        first_date = min(dates)
        last_date = max(dates)

        # Calculate elapsed time
        elapsed = last_date - first_date
        days = elapsed.days
        hours = days * 24 + elapsed.seconds // 3600

        return {
            'days': days,
            'hours': hours,
            'first_commit': first_date.strftime('%Y-%m-%d'),
            'last_commit': last_date.strftime('%Y-%m-%d')
        }

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
        return {'days': 0, 'hours': 0, 'first_commit': None, 'last_commit': None}


def check_git_available(project_path: Path) -> bool:
    """
    Check if git is available and project_path is a git repository.

    Args:
        project_path: Absolute path to project directory

    Returns:
        True if git is available and path is a git repo, False otherwise

    Example:
        >>> check_git_available(Path('/path/to/repo'))
        True
        >>> check_git_available(Path('/tmp'))
        False
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=str(project_path),
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


# Agent Communication Helpers (Phase 0)

def generate_agent_workorder_id(workorder_id: str, agent_number: int) -> str:
    """
    Generate agent-scoped workorder ID for multi-agent coordination.

    Creates unique workorder ID for each agent working on the same feature.
    Format: WO-{FEATURE-NAME}-{AGENT_NUMBER:03d}

    Args:
        workorder_id: Base workorder ID (e.g., 'WO-AUTH-SYSTEM-001')
        agent_number: Agent number (1, 2, 3, etc.)

    Returns:
        Agent-scoped workorder ID (e.g., 'WO-AUTH-SYSTEM-002', 'WO-AUTH-SYSTEM-003')

    Example:
        >>> generate_agent_workorder_id('WO-AUTH-SYSTEM-001', 2)
        'WO-AUTH-SYSTEM-002'
        >>> generate_agent_workorder_id('WO-AUTH-SYSTEM-001', 3)
        'WO-AUTH-SYSTEM-003'

    Raises:
        ValueError: If workorder_id format is invalid or agent_number < 1
    """
    if agent_number < 1:
        raise ValueError(f"Agent number must be >= 1, got {agent_number}")

    # Parse base workorder ID: WO-FEATURE-NAME-001
    if not workorder_id.startswith('WO-'):
        raise ValueError(f"Invalid workorder ID format: {workorder_id}")

    parts = workorder_id.rsplit('-', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid workorder ID format: {workorder_id}")

    base = parts[0]  # WO-FEATURE-NAME
    return f"{base}-{agent_number:03d}"


def validate_forbidden_files(project_path: Path, forbidden_files: List[str]) -> Dict[str, any]:
    """
    Validate that forbidden files have not been modified using git diff.

    Checks git working directory for any uncommitted changes to forbidden files.
    Returns validation results with details of any modifications found.

    Args:
        project_path: Absolute path to project directory (must be git repo)
        forbidden_files: List of file paths relative to project_path

    Returns:
        Dictionary with keys:
            - passed: bool - True if all forbidden files unchanged
            - violations: List[Dict] - Files that were modified
            - checked: List[str] - Files that were checked

    Example:
        >>> result = validate_forbidden_files(Path('/repo'), ['src/core.py', 'src/api.py'])
        >>> result['passed']
        True
        >>> result['checked']
        ['src/core.py', 'src/api.py']

    Raises:
        ValueError: If project_path is not a git repository
    """
    if not check_git_available(project_path):
        raise ValueError(f"Not a git repository: {project_path}")

    result = {
        'passed': True,
        'violations': [],
        'checked': []
    }

    for file_path in forbidden_files:
        # Extract just the file path (strip " - DO NOT MODIFY ..." comments)
        clean_path = file_path.split(' - ')[0].strip()
        result['checked'].append(clean_path)

        try:
            # Check if file has uncommitted changes
            cmd = ['git', 'diff', '--name-only', clean_path]
            diff_result = subprocess.run(
                cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            # If file appears in diff output, it was modified
            if diff_result.returncode == 0 and diff_result.stdout.strip():
                result['passed'] = False
                result['violations'].append({
                    'file': clean_path,
                    'status': 'modified',
                    'reason': 'Uncommitted changes detected'
                })

            # Also check staged changes
            cmd_staged = ['git', 'diff', '--cached', '--name-only', clean_path]
            staged_result = subprocess.run(
                cmd_staged,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if staged_result.returncode == 0 and staged_result.stdout.strip():
                result['passed'] = False
                # Avoid duplicates
                if not any(v['file'] == clean_path for v in result['violations']):
                    result['violations'].append({
                        'file': clean_path,
                        'status': 'staged',
                        'reason': 'Staged changes detected'
                    })

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            result['passed'] = False
            result['violations'].append({
                'file': clean_path,
                'status': 'error',
                'reason': f'Git check failed: {str(e)}'
            })

    return result


def aggregate_agent_metrics(deliverables_paths: List[Path]) -> Dict[str, any]:
    """
    Aggregate metrics from multiple agent DELIVERABLES.md files.

    Parses multiple deliverables files and combines metrics:
    - LOC: Sums added, deleted, net lines
    - Commits: Total count across all agents
    - Contributors: Unique set of contributors
    - Time: Min first commit to max last commit

    Args:
        deliverables_paths: List of paths to DELIVERABLES.md files

    Returns:
        Dictionary with aggregated metrics:
            - loc_added: int - Total lines added
            - loc_deleted: int - Total lines deleted
            - loc_net: int - Net lines changed
            - total_commits: int - Total commits
            - contributors: List[str] - Unique contributors
            - days_elapsed: int - Days from first to last commit
            - hours_elapsed: int - Hours from first to last commit
            - agents_count: int - Number of agents

    Example:
        >>> paths = [Path('agent1/DELIVERABLES.md'), Path('agent2/DELIVERABLES.md')]
        >>> metrics = aggregate_agent_metrics(paths)
        >>> metrics['loc_added']
        850
        >>> metrics['total_commits']
        12
        >>> metrics['contributors']
        ['Agent 1', 'Agent 2', 'willh']
    """
    aggregated = {
        'loc_added': 0,
        'loc_deleted': 0,
        'loc_net': 0,
        'total_commits': 0,
        'contributors': set(),
        'first_commit_date': None,
        'last_commit_date': None,
        'days_elapsed': 0,
        'hours_elapsed': 0,
        'agents_count': len(deliverables_paths)
    }

    for path in deliverables_paths:
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding='utf-8')

            # Parse LOC metrics (look for "Lines Added**: 450" or "Lines Added: 450")
            import re
            loc_added = re.search(r'Lines Added\*?\*?[:\s]+(\d+)', content)
            loc_deleted = re.search(r'Lines Deleted\*?\*?[:\s]+(\d+)', content)
            loc_net = re.search(r'Net LOC\*?\*?[:\s]+(-?\d+)', content)
            commits = re.search(r'Total Commits\*?\*?[:\s]+(\d+)', content)
            contributors_match = re.search(r'Contributors\*?\*?[:\s]+(.+)', content)

            if loc_added:
                aggregated['loc_added'] += int(loc_added.group(1))
            if loc_deleted:
                aggregated['loc_deleted'] += int(loc_deleted.group(1))
            if loc_net:
                aggregated['loc_net'] += int(loc_net.group(1))
            if commits:
                aggregated['total_commits'] += int(commits.group(1))
            if contributors_match:
                # Parse comma-separated contributors
                contrib_list = [c.strip() for c in contributors_match.group(1).split(',')]
                aggregated['contributors'].update(contrib_list)

            # Parse dates for time calculation
            first_commit = re.search(r'\*?\*?first_commit\*?\*?[:\s]+(\d{4}-\d{2}-\d{2})', content)
            last_commit = re.search(r'\*?\*?last_commit\*?\*?[:\s]+(\d{4}-\d{2}-\d{2})', content)

            if first_commit:
                date = datetime.fromisoformat(first_commit.group(1))
                if not aggregated['first_commit_date'] or date < aggregated['first_commit_date']:
                    aggregated['first_commit_date'] = date

            if last_commit:
                date = datetime.fromisoformat(last_commit.group(1))
                if not aggregated['last_commit_date'] or date > aggregated['last_commit_date']:
                    aggregated['last_commit_date'] = date

        except (IOError, ValueError) as e:
            # Skip files that can't be parsed
            continue

    # Calculate elapsed time
    if aggregated['first_commit_date'] and aggregated['last_commit_date']:
        elapsed = aggregated['last_commit_date'] - aggregated['first_commit_date']
        aggregated['days_elapsed'] = elapsed.days
        aggregated['hours_elapsed'] = elapsed.days * 24 + elapsed.seconds // 3600

    # Convert contributors set to sorted list
    aggregated['contributors'] = sorted(list(aggregated['contributors']))

    return aggregated


def parse_agent_status(communication_json_path: Path) -> Dict[str, any]:
    """
    Parse agent status from communication.json file.

    Extracts current status of all agents working on a feature:
    - Agent assignments
    - Current status (null, IN_PROGRESS, COMPLETE, VERIFIED)
    - Completion timestamps
    - Blockers and dependencies

    Args:
        communication_json_path: Path to communication.json file

    Returns:
        Dictionary with agent status information:
            - feature: str - Feature name
            - workorder_id: str - Workorder ID
            - agents: List[Dict] - Agent status details
            - overall_status: str - Overall workflow status

    Example:
        >>> status = parse_agent_status(Path('coderef/workorder/auth/communication.json'))
        >>> status['overall_status']
        'IN_PROGRESS'
        >>> len(status['agents'])
        2
        >>> status['agents'][0]['status']
        'COMPLETE'

    Raises:
        FileNotFoundError: If communication.json doesn't exist
        ValueError: If JSON is malformed
    """
    if not communication_json_path.exists():
        raise FileNotFoundError(f"Communication file not found: {communication_json_path}")

    try:
        content = communication_json_path.read_text(encoding='utf-8')
        data = json.loads(content)

        result = {
            'feature': data.get('feature', 'UNKNOWN'),
            'workorder_id': data.get('workorder_id', 'UNKNOWN'),
            'agents': [],
            'overall_status': 'UNKNOWN'
        }

        # Find all agent status fields
        agent_statuses = {}
        for key, value in data.items():
            if key.startswith('agent_') and key.endswith('_status'):
                # Extract agent number from key (e.g., 'agent_2_status' -> '2')
                agent_num = key.replace('agent_', '').replace('_status', '')
                agent_statuses[agent_num] = value

        # Build agent list
        for agent_num in sorted(agent_statuses.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            status = agent_statuses[agent_num]
            agent_info = {
                'agent_number': agent_num,
                'status': status if status else 'NOT_ASSIGNED',
                'completion_time': None,
                'blockers': []
            }

            # Look for completion details
            completion_key = f'agent_{agent_num}_completion'
            if completion_key in data:
                completion = data[completion_key]
                if isinstance(completion, dict):
                    agent_info['completion_time'] = completion.get('timestamp')
                    # Check for blockers
                    if completion.get('verification', {}).get('forbidden_files_unchanged') is False:
                        agent_info['blockers'].append('FORBIDDEN_FILES_MODIFIED')
                    if completion.get('verification', {}).get('tests_passing') is False:
                        agent_info['blockers'].append('TESTS_FAILING')

            result['agents'].append(agent_info)

        # Determine overall status
        statuses = [a['status'] for a in result['agents']]
        if all(s == 'NOT_ASSIGNED' or s is None or 'READY' in str(s) for s in statuses):
            result['overall_status'] = 'READY'
        elif any('VERIFIED' in str(s) for s in statuses):
            result['overall_status'] = 'VERIFIED'
        elif all('COMPLETE' in str(s) for s in statuses if s and s != 'NOT_ASSIGNED'):
            result['overall_status'] = 'COMPLETE'
        elif any('IN_PROGRESS' in str(s) or 'ASSIGNED' in str(s) for s in statuses):
            result['overall_status'] = 'IN_PROGRESS'
        else:
            result['overall_status'] = 'READY'

        return result

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in communication file: {e}")


# Archive Feature Helpers (ARCHIVE-001, ARCHIVE-002)

def update_archive_index(project_path: Path, feature_name: str, folder_name: str, archived_at: str) -> None:
    """
    Update archive index.json with new archived feature entry.

    Creates index.json if it doesn't exist. Appends new entry to archived_features array.
    Updates total_archived count and last_updated timestamp.
    Validates JSON schema before writing to prevent corruption.

    Args:
        project_path: Absolute path to project directory
        feature_name: Display name of the feature (e.g., 'Archive Feature Tool')
        folder_name: Folder name in coderef/archived/ (e.g., 'archive-feature')
        archived_at: ISO 8601 timestamp of archival (e.g., '2025-10-18T15:30:00+00:00')

    Raises:
        ValueError: If JSON is malformed or validation fails
        IOError: If file operations fail

    Example:
        >>> update_archive_index(
        ...     Path('/path/to/project'),
        ...     'Archive Feature Tool',
        ...     'archive-feature',
        ...     '2025-10-18T15:30:00+00:00'
        ... )
        # Creates/updates coderef/archived/index.json
    """
    archived_dir = project_path / 'coderef' / 'archived'
    index_path = archived_dir / 'index.json'

    # Ensure archived directory exists
    archived_dir.mkdir(parents=True, exist_ok=True)

    # Load existing index or create new one
    if index_path.exists():
        try:
            content = index_path.read_text(encoding='utf-8')
            index_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted index.json: {e}")
    else:
        index_data = {
            'archived_features': [],
            'total_archived': 0,
            'last_updated': None
        }

    # Validate structure
    if not isinstance(index_data.get('archived_features'), list):
        raise ValueError("Invalid index.json: 'archived_features' must be an array")

    # Create new entry
    new_entry = {
        'feature_name': feature_name,
        'folder_name': folder_name,
        'archived_at': archived_at
    }

    # Append to archived_features
    index_data['archived_features'].append(new_entry)
    index_data['total_archived'] = len(index_data['archived_features'])
    index_data['last_updated'] = archived_at

    # Write back to file with indentation
    try:
        index_path.write_text(
            json.dumps(index_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    except IOError as e:
        raise IOError(f"Failed to write index.json: {e}")


def parse_deliverables_status(deliverables_path: Path) -> str:
    """
    Parse DELIVERABLES.md file to extract completion status.

    Reads DELIVERABLES.md and extracts status line:
    - "Status: ✅ Complete" -> "Complete"
    - "Status: 🚧 In Progress" -> "In Progress"
    - "Status: 🚧 Not Started" -> "Not Started"

    Returns "UNKNOWN" if file is missing or status line is not found.
    Handles various status line formats and emojis.

    Args:
        deliverables_path: Path to DELIVERABLES.md file

    Returns:
        Status string: "Complete", "In Progress", "Not Started", or "UNKNOWN"

    Example:
        >>> status = parse_deliverables_status(Path('coderef/workorder/auth/DELIVERABLES.md'))
        >>> status
        'Complete'

        >>> status = parse_deliverables_status(Path('coderef/workorder/auth/DELIVERABLES.md'))
        >>> status
        'In Progress'

        >>> status = parse_deliverables_status(Path('missing.md'))
        >>> status
        'UNKNOWN'
    """
    if not deliverables_path.exists():
        return 'UNKNOWN'

    try:
        content = deliverables_path.read_text(encoding='utf-8')

        # Search for status line using regex
        # Supports:
        # - Status: ✅ Complete
        # - **Status**: ✅ Complete
        # - Status: 🚧 In Progress
        # - Status: 🚧 Not Started
        import re
        status_match = re.search(
            r'^\*?\*?Status\*?\*?[:\s]+(?:✅|🚧|❌)?\s*([^\n]+)',
            content,
            re.IGNORECASE | re.MULTILINE
        )

        if status_match:
            status_text = status_match.group(1).strip()

            # Normalize status text
            if 'complete' in status_text.lower() or '✅' in status_text:
                return 'Complete'
            elif 'in progress' in status_text.lower() or 'in-progress' in status_text.lower():
                return 'In Progress'
            elif 'not started' in status_text.lower() or 'not-started' in status_text.lower():
                return 'Not Started'
            else:
                # Return raw status if doesn't match known patterns
                return status_text

        return 'UNKNOWN'

    except (IOError, UnicodeDecodeError):
        return 'UNKNOWN'


# Documentation Update Helpers (DOC-002, DOC-003, DOC-004, DOC-005, DOC-006)

def parse_version_from_docs(project_path: Path) -> Optional[str]:
    """
    Parse current version from README.md or CLAUDE.md.

    Searches for version string in format: "Version: 1.2.3" or "**Version**: 1.2.3"
    Tries README.md first, falls back to CLAUDE.md.

    Args:
        project_path: Absolute path to project directory

    Returns:
        Version string (e.g., "1.2.3") or None if not found

    Example:
        >>> parse_version_from_docs(Path('/path/to/project'))
        '1.10.0'
    """
    import re

    # Try README.md first
    readme_path = project_path / 'README.md'
    if readme_path.exists():
        try:
            content = readme_path.read_text(encoding='utf-8')
            version_match = re.search(r'\*?\*?Version\*?\*?[:\s]+(\d+\.\d+\.\d+)', content, re.IGNORECASE)
            if version_match:
                return version_match.group(1)
        except (IOError, UnicodeDecodeError):
            pass

    # Fall back to CLAUDE.md
    claude_path = project_path / 'CLAUDE.md'
    if claude_path.exists():
        try:
            content = claude_path.read_text(encoding='utf-8')
            version_match = re.search(r'\*?\*?Version\*?\*?[:\s]+(\d+\.\d+\.\d+)', content, re.IGNORECASE)
            if version_match:
                return version_match.group(1)
        except (IOError, UnicodeDecodeError):
            pass

    return None


def increment_version(current_version: str, change_type: str) -> str:
    """
    Auto-increment version using semantic versioning rules.

    Rules:
    - breaking_change -> major bump (1.x.x -> 2.0.0)
    - feature -> minor bump (1.0.x -> 1.1.0)
    - bugfix/enhancement -> patch bump (1.0.0 -> 1.0.1)

    Args:
        current_version: Current version string (e.g., "1.10.0")
        change_type: One of: breaking_change, feature, enhancement, bugfix, security, deprecation

    Returns:
        New version string

    Raises:
        ValueError: If current_version or change_type is invalid

    Example:
        >>> increment_version("1.10.0", "feature")
        '1.11.0'
        >>> increment_version("1.10.0", "breaking_change")
        '2.0.0'
        >>> increment_version("1.10.0", "bugfix")
        '1.10.1'
    """
    import re

    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', current_version):
        raise ValueError(f"Invalid version format: {current_version} (expected X.Y.Z)")

    # Parse version
    major, minor, patch = map(int, current_version.split('.'))

    # Apply semantic versioning rules
    if change_type == 'breaking_change':
        # Major bump: reset minor and patch to 0
        major += 1
        minor = 0
        patch = 0
    elif change_type in ['feature', 'deprecation']:
        # Minor bump: reset patch to 0
        minor += 1
        patch = 0
    elif change_type in ['bugfix', 'enhancement', 'security']:
        # Patch bump
        patch += 1
    else:
        raise ValueError(f"Invalid change_type: {change_type}")

    return f"{major}.{minor}.{patch}"


def detect_change_type_from_deliverables(deliverables_path: Path) -> str:
    """
    Detect change type from DELIVERABLES.md content.

    Analyzes deliverables content for keywords:
    - "breaking", "API change", "removed" -> breaking_change
    - "new feature", "added", "implement" -> feature
    - "fix", "bug", "issue" -> bugfix
    - Default -> enhancement

    Args:
        deliverables_path: Path to DELIVERABLES.md file

    Returns:
        Change type: breaking_change, feature, bugfix, or enhancement

    Example:
        >>> detect_change_type_from_deliverables(Path('DELIVERABLES.md'))
        'feature'
    """
    if not deliverables_path.exists():
        return 'enhancement'

    try:
        content = deliverables_path.read_text(encoding='utf-8').lower()

        # Check for breaking changes
        if any(keyword in content for keyword in ['breaking', 'api change', 'removed feature', 'incompatible']):
            return 'breaking_change'

        # Check for new features
        if any(keyword in content for keyword in ['new feature', 'new tool', 'added', 'implement']):
            return 'feature'

        # Check for bug fixes
        if any(keyword in content for keyword in ['fix', 'bug', 'issue', 'patch']):
            return 'bugfix'

        # Default to enhancement
        return 'enhancement'

    except (IOError, UnicodeDecodeError):
        return 'enhancement'


def detect_change_type_from_git(project_path: Path, feature_name: Optional[str] = None) -> str:
    """
    Detect change type from git commit messages.

    Analyzes recent commit messages for conventional commit prefixes:
    - "feat!", "BREAKING CHANGE" -> breaking_change
    - "feat:", "feature:" -> feature
    - "fix:", "bugfix:" -> bugfix
    - Default -> enhancement

    Args:
        project_path: Absolute path to project directory
        feature_name: Optional feature name to filter commits

    Returns:
        Change type: breaking_change, feature, bugfix, or enhancement

    Example:
        >>> detect_change_type_from_git(Path('/repo'), 'auth-system')
        'feature'
    """
    if not check_git_available(project_path):
        return 'enhancement'

    try:
        # Get recent commits (last 10)
        cmd = ['git', 'log', '-10', '--format=%s']
        if feature_name:
            cmd.extend([f'--grep={feature_name}', '--regexp-ignore-case'])

        result = subprocess.run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return 'enhancement'

        messages = result.stdout.lower()

        # Check for breaking changes
        if 'breaking change' in messages or 'feat!' in messages or 'breaking:' in messages:
            return 'breaking_change'

        # Check for features
        if 'feat:' in messages or 'feature:' in messages:
            return 'feature'

        # Check for fixes
        if 'fix:' in messages or 'bugfix:' in messages:
            return 'bugfix'

        return 'enhancement'

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return 'enhancement'


def update_readme_version(project_path: Path, old_version: str, new_version: str, feature_description: Optional[str] = None) -> bool:
    """
    Update README.md with new version number and optionally add feature to What's New.

    Args:
        project_path: Absolute path to project directory
        old_version: Current version (e.g., "1.10.0")
        new_version: New version (e.g., "1.11.0")
        feature_description: Optional description to add to What's New

    Returns:
        True if updated successfully, False otherwise
    """
    import re

    readme_path = project_path / 'README.md'
    if not readme_path.exists():
        return False

    try:
        content = readme_path.read_text(encoding='utf-8')

        # Update version number
        content = re.sub(
            r'(\*\*Version\*\*:[^\d]*)' + re.escape(old_version),
            r'\g<1>' + new_version,
            content,
            flags=re.IGNORECASE
        )

        # Add to What's New if feature description provided
        if feature_description:
            # Find What's New or Key Features section
            whats_new_pattern = r'(## What\'s New.*?\n)'
            if re.search(whats_new_pattern, content):
                content = re.sub(
                    whats_new_pattern,
                    rf'\1- {feature_description} (NEW in v{new_version})\n',
                    content
                )

        readme_path.write_text(content, encoding='utf-8')

        # GAP-010: Validate README.md after update (UDS compliance)
        try:
            from papertrail.validators.foundation import FoundationDocValidator
            validator = FoundationDocValidator()
            result = validator.validate_file(str(readme_path))

            if not result['valid']:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"README.md update validation failed (score: {result.get('score', 0)})")
                for error in result.get('errors', []):
                    logger.warning(f"  - {error}")
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"README.md update validated successfully (score: {result.get('score', 100)})")
        except ImportError:
            pass  # Papertrail not available - skip validation
        except Exception:
            pass  # Validation error - continue without validation

        return True

    except (IOError, UnicodeDecodeError):
        return False


def update_claude_md_version(project_path: Path, old_version: str, new_version: str, feature_description: Optional[str] = None) -> bool:
    """
    Update CLAUDE.md with new version number and add version history entry.

    Args:
        project_path: Absolute path to project directory
        old_version: Current version (e.g., "2.4.0")
        new_version: New version (e.g., "2.5.0")
        feature_description: Optional description for version history

    Returns:
        True if updated successfully, False otherwise
    """
    import re

    claude_path = project_path / 'CLAUDE.md'
    if not claude_path.exists():
        return False

    try:
        content = claude_path.read_text(encoding='utf-8')

        # Update version number
        content = re.sub(
            r'(\*\*Version\*\*:[^\d]*)' + re.escape(old_version),
            r'\g<1>' + new_version,
            content,
            flags=re.IGNORECASE
        )

        # Add version history entry if description provided
        if feature_description:
            # Find version history section
            history_pattern = r'(## Version Information.*?Change History.*?\(Recent\):?\s*\n)'
            if re.search(history_pattern, content, re.DOTALL):
                content = re.sub(
                    history_pattern,
                    rf'\1- {new_version}: {feature_description}\n',
                    content,
                    flags=re.DOTALL
                )

        claude_path.write_text(content, encoding='utf-8')
        return True

    except (IOError, UnicodeDecodeError):
        return False


# Git Automation Helpers (WO-POST-IMPLEMENTATION-GIT-AUTOMATION-001)

def git_commit_and_push(
    project_path: Path,
    files: List[str],
    commit_message: str,
    workorder_id: Optional[str] = None
) -> Dict[str, any]:
    """
    Commit and push specified files to git with error handling.

    Stages files, creates commit with provided message, and pushes to remote.
    Non-blocking: returns success/failure status without raising exceptions.
    Logs all operations and errors for debugging.

    Args:
        project_path: Absolute path to project directory (must be git repo)
        files: List of file paths to stage and commit (relative to project_path)
        commit_message: Commit message
        workorder_id: Optional workorder ID to include in commit body

    Returns:
        Dictionary with keys:
            - success: bool - True if all operations succeeded
            - commit_hash: Optional[str] - Short commit hash (8 chars)
            - pushed: bool - True if push succeeded
            - error: Optional[str] - Error message if failed
            - operations: List[str] - Log of operations performed

    Example:
        >>> result = git_commit_and_push(
        ...     Path('/repo'),
        ...     ['DELIVERABLES.md', 'plan.json'],
        ...     'chore(deliverables): Mark auth-system complete',
        ...     'WO-AUTH-SYSTEM-001'
        ... )
        >>> result['success']
        True
        >>> result['commit_hash']
        'abc12345'
        >>> result['pushed']
        True
    """
    from logger_config import logger

    result = {
        'success': False,
        'commit_hash': None,
        'pushed': False,
        'error': None,
        'operations': []
    }

    # Check git availability
    if not check_git_available(project_path):
        result['error'] = 'Not a git repository or git not available'
        logger.warning(f"Git automation skipped: {result['error']}", extra={'project_path': str(project_path)})
        return result

    try:
        # Stage files
        for file_path in files:
            cmd_add = ['git', 'add', file_path]
            add_result = subprocess.run(
                cmd_add,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            if add_result.returncode == 0:
                result['operations'].append(f'Staged: {file_path}')
                logger.debug(f"Staged file: {file_path}", extra={'project_path': str(project_path)})
            else:
                result['error'] = f"Failed to stage {file_path}: {add_result.stderr}"
                logger.error(f"Git add failed: {result['error']}", extra={'file': file_path})
                return result

        # Build commit message with optional workorder ID
        full_message = commit_message
        if workorder_id:
            full_message = f"{commit_message}\n\nWorkorder: {workorder_id}"

        # Create commit
        cmd_commit = ['git', 'commit', '-m', full_message]
        commit_result = subprocess.run(
            cmd_commit,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10
        )

        if commit_result.returncode == 0:
            # Extract commit hash from output (format: [branch hash] message)
            import re
            hash_match = re.search(r'\[[\w-]+ ([a-f0-9]+)\]', commit_result.stdout)
            if hash_match:
                result['commit_hash'] = hash_match.group(1)[:8]

            result['operations'].append(f'Committed: {result["commit_hash"] or "unknown"}')
            logger.info(f"Git commit created: {result['commit_hash']}", extra={
                'project_path': str(project_path),
                'files': files
            })
        else:
            # Check if "nothing to commit" - not an error
            if 'nothing to commit' in commit_result.stdout.lower():
                result['success'] = True
                result['operations'].append('No changes to commit')
                logger.info("No changes to commit", extra={'project_path': str(project_path)})
                return result

            result['error'] = f"Commit failed: {commit_result.stderr}"
            logger.error(f"Git commit failed: {result['error']}", extra={'files': files})
            return result

        # Push to remote
        cmd_push = ['git', 'push']
        push_result = subprocess.run(
            cmd_push,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=30
        )

        if push_result.returncode == 0:
            result['pushed'] = True
            result['operations'].append('Pushed to remote')
            logger.info("Git push succeeded", extra={'project_path': str(project_path)})
        else:
            # Push failure is non-blocking - commit still succeeded locally
            result['pushed'] = False
            result['error'] = f"Push failed (commit succeeded locally): {push_result.stderr}"
            logger.warning(f"Git push failed: {result['error']}", extra={'project_path': str(project_path)})

        # Success if we got this far (commit succeeded, push optional)
        result['success'] = True
        return result

    except subprocess.TimeoutExpired as e:
        result['error'] = f'Git operation timed out: {e}'
        logger.error(f"Git timeout: {result['error']}", extra={'project_path': str(project_path)})
        return result
    except subprocess.SubprocessError as e:
        result['error'] = f'Git subprocess error: {e}'
        logger.error(f"Git subprocess error: {result['error']}", extra={'project_path': str(project_path)})
        return result
    except Exception as e:
        result['error'] = f'Unexpected error: {e}'
        logger.error(f"Git automation error: {result['error']}", extra={'project_path': str(project_path)})
        return result


def format_deliverables_commit_message(feature_name: str, workorder_id: str) -> str:
    """
    Format commit message for DELIVERABLES.md updates.

    Args:
        feature_name: Feature name (e.g., 'auth-system')
        workorder_id: Workorder ID (e.g., 'WO-AUTH-SYSTEM-001')

    Returns:
        Formatted commit message

    Example:
        >>> format_deliverables_commit_message('auth-system', 'WO-AUTH-SYSTEM-001')
        'chore(deliverables): Mark auth-system complete'
    """
    return f"chore(deliverables): Mark {feature_name} complete"


def format_docs_commit_message(feature_name: str, version: str, change_description: str) -> str:
    """
    Format commit message for documentation updates.

    Args:
        feature_name: Feature name (e.g., 'auth-system')
        version: New version (e.g., '1.11.0')
        change_description: Brief description of change

    Returns:
        Formatted commit message with body

    Example:
        >>> format_docs_commit_message('auth-system', '1.11.0', 'Added JWT authentication')
        'docs(auth-system): Update documentation to v1.11.0\\n\\nAdded JWT authentication'
    """
    return f"docs({feature_name}): Update documentation to v{version}\n\n{change_description}"


def format_archive_commit_message(feature_name: str, workorder_id: str) -> str:
    """
    Format commit message for feature archival.

    Args:
        feature_name: Feature name (e.g., 'auth-system')
        workorder_id: Workorder ID (e.g., 'WO-AUTH-SYSTEM-001')

    Returns:
        Formatted commit message

    Example:
        >>> format_archive_commit_message('auth-system', 'WO-AUTH-SYSTEM-001')
        'chore(archive): Archive auth-system'
    """
    return f"chore(archive): Archive {feature_name}"
