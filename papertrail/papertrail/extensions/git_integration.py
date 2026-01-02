"""
Git Extension - Extract git statistics for documentation

Provides template tags for git data:
- {% git.stats workorder_id %} - Git statistics
- {% git.files workorder_id %} - Modified files
- {% git.contributors %} - Contributors list

Enhanced with real git parsing (WO-PAPERTRAIL-EXTENSIONS-001 Phase 1)
"""

from typing import Optional, Dict, Any, List
import subprocess
import re
from datetime import datetime
from pathlib import Path


class GitExtension:
    """
    Template extension for git integration

    Extracts git statistics for DELIVERABLES.md and other docs
    Enhanced with real git data extraction
    """

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git extension

        Args:
            repo_path: Path to git repository (uses cwd if not provided)
        """
        self.repo_path = Path(repo_path) if repo_path else None

    def _run_git_command(self, args: List[str]) -> Optional[str]:
        """
        Run git command safely with error handling

        Args:
            args: Git command arguments (without 'git' prefix)

        Returns:
            str: Command output or None if error
        """
        try:
            cmd = ["git"] + args
            kwargs = {"capture_output": True, "text": True, "check": True}
            if self.repo_path:
                kwargs["cwd"] = str(self.repo_path)

            result = subprocess.run(cmd, **kwargs)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git command failed or git not installed
            return None

    def get_files_changed(self, workorder_id: str) -> List[Dict[str, Any]]:
        """
        Get list of files changed for a workorder with detailed stats

        Args:
            workorder_id: Workorder ID to search (e.g., WO-FEATURE-001)

        Returns:
            list: List of file change records with path, status, additions, deletions

        Example:
            {% set files = git.get_files_changed("WO-AUTH-001") %}
            {% for file in files %}
            - {{ file.path }} ({{ file.status }}): +{{ file.additions }} -{{ file.deletions }}
            {% endfor %}
        """
        # Get commits matching workorder ID
        log_output = self._run_git_command([
            "log", "--all", f"--grep={workorder_id}", "--name-status",
            "--pretty=format:COMMIT:%H"
        ])

        if not log_output:
            return []

        files_dict = {}  # path -> {status, additions, deletions}

        # Parse output
        for line in log_output.split("\n"):
            if line.startswith("COMMIT:"):
                continue

            # Parse status line (e.g., "M    src/auth.py")
            match = re.match(r"^([AMD])\s+(.+)$", line)
            if match:
                status_code, path = match.groups()
                status_map = {"A": "added", "M": "modified", "D": "deleted"}

                if path not in files_dict:
                    files_dict[path] = {
                        "path": path,
                        "status": status_map.get(status_code, "unknown"),
                        "additions": 0,
                        "deletions": 0
                    }

        # Get detailed stats for each file
        for path, file_data in files_dict.items():
            stats_output = self._run_git_command([
                "log", "--all", f"--grep={workorder_id}", "--", path,
                "--numstat", "--pretty=format:"
            ])

            if stats_output:
                # Parse numstat output (format: additions\tdeletions\tpath)
                for stat_line in stats_output.split("\n"):
                    if not stat_line.strip():
                        continue
                    parts = stat_line.split("\t")
                    if len(parts) >= 2:
                        try:
                            adds = int(parts[0]) if parts[0] != '-' else 0
                            dels = int(parts[1]) if parts[1] != '-' else 0
                            file_data["additions"] += adds
                            file_data["deletions"] += dels
                        except ValueError:
                            continue

        return list(files_dict.values())

    def get_commits(self, workorder_id: str) -> List[Dict[str, str]]:
        """
        Get commit history for workorder

        Args:
            workorder_id: Workorder ID to search

        Returns:
            list: List of commit records with hash, author, date, message

        Example:
            {% for commit in git.get_commits("WO-AUTH-001") %}
            - {{ commit.hash[:7] }}: {{ commit.message }} ({{ commit.author }})
            {% endfor %}
        """
        log_output = self._run_git_command([
            "log", "--all", f"--grep={workorder_id}",
            "--pretty=format:%H%x00%an%x00%ai%x00%s"
        ])

        if not log_output:
            return []

        commits = []
        for line in log_output.split("\n"):
            if not line.strip():
                continue

            parts = line.split("\x00")
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],  # ISO 8601 format
                    "message": parts[3]
                })

        return commits

    def stats(self, workorder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get git statistics for workorder

        Args:
            workorder_id: Workorder ID to search (optional)

        Returns:
            dict: Git statistics with commits, additions, deletions, files_changed

        Example:
            {% set stats = git.stats("WO-AUTH-001") %}
            Commits: {{ stats.commits }}
            Insertions: {{ stats.total_additions }}
            Deletions: {{ stats.total_deletions }}
        """
        if not workorder_id:
            # No workorder specified, return empty stats
            return {
                "commits": 0,
                "total_additions": 0,
                "total_deletions": 0,
                "files_changed": 0,
                "workorder_id": None
            }

        files = self.get_files_changed(workorder_id)
        commits = self.get_commits(workorder_id)

        total_additions = sum(f["additions"] for f in files)
        total_deletions = sum(f["deletions"] for f in files)

        return {
            "commits": len(commits),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "files_changed": len(files),
            "workorder_id": workorder_id
        }

    def files(self, workorder_id: Optional[str] = None) -> List[str]:
        """
        Get list of file paths modified for workorder

        Args:
            workorder_id: Workorder ID to search

        Returns:
            list: List of file paths (use get_files_changed for detailed stats)

        Example:
            {% for file in git.files("WO-AUTH-001") %}
            - {{ file }}
            {% endfor %}
        """
        if not workorder_id:
            return []

        files = self.get_files_changed(workorder_id)
        return [f["path"] for f in files]

    def contributors(self) -> List[str]:
        """
        Get list of contributors from git history

        Returns:
            list: Sorted list of unique contributor names

        Example:
            {% for contributor in git.contributors() %}
            - {{ contributor }}
            {% endfor %}
        """
        output = self._run_git_command(["log", "--format=%an"])

        if not output:
            return []

        # Get unique contributors and sort
        contributors = list(set(output.split("\n")))
        return sorted([c for c in contributors if c])  # Filter empty strings

    def last_commit(self) -> Dict[str, Any]:
        """
        Get last commit info from repository

        Returns:
            dict: Last commit details with hash, author, date, message

        Example:
            {% set commit = git.last_commit() %}
            Last updated: {{ commit.date }}
        """
        output = self._run_git_command([
            "log", "-1", "--pretty=format:%H%x00%an%x00%ai%x00%s"
        ])

        if not output:
            return {
                "hash": "",
                "author": "",
                "date": "",
                "message": ""
            }

        parts = output.split("\x00")
        if len(parts) >= 4:
            return {
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3]
            }

        return {
            "hash": "",
            "author": "",
            "date": "",
            "message": ""
        }
