"""
Git Extension - Extract git statistics for documentation

Provides template tags for git data:
- {% git.stats feature_name %} - Git statistics
- {% git.files feature_name %} - Modified files
- {% git.contributors %} - Contributors list
"""

from typing import Optional, Dict, Any, List
import subprocess
import re
from datetime import datetime


class GitExtension:
    """
    Template extension for git integration

    Extracts git statistics for DELIVERABLES.md and other docs
    """

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git extension

        Args:
            repo_path: Path to git repository (uses cwd if not provided)
        """
        self.repo_path = repo_path

    def stats(self, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get git statistics for feature

        Args:
            feature_name: Feature name to search in commit messages

        Returns:
            dict: Git statistics (commits, LOC, etc.)

        Example:
            {% set stats = git.stats("auth-system") %}
            Commits: {{ stats.commits }}
        """
        try:
            # Get commit count
            if feature_name:
                grep_cmd = f'git log --all --grep="{feature_name}" --oneline | wc -l'
            else:
                grep_cmd = 'git log --oneline | wc -l'

            # Note: This is simplified. Full implementation would parse git log
            # For now, return mock data
            return {
                "commits": 15,
                "insertions": 450,
                "deletions": 120,
                "files_changed": 23,
                "feature_name": feature_name,
                "message": "(Mock git stats - Phase 2 implementation)"
            }

        except subprocess.CalledProcessError:
            return {
                "commits": 0,
                "insertions": 0,
                "deletions": 0,
                "files_changed": 0,
                "error": "Git command failed"
            }

    def files(self, feature_name: Optional[str] = None) -> List[str]:
        """
        Get list of files modified for feature

        Args:
            feature_name: Feature name to search

        Returns:
            list: List of file paths

        Example:
            {% for file in git.files("auth-system") %}
            - {{ file }}
            {% endfor %}
        """
        # TODO: Implement actual git file listing
        return [
            "src/auth.py",
            "tests/test_auth.py",
            "docs/AUTH.md"
        ]

    def contributors(self) -> List[str]:
        """
        Get list of contributors

        Returns:
            list: List of contributor names

        Example:
            {% for contributor in git.contributors() %}
            - {{ contributor }}
            {% endfor %}
        """
        try:
            # Get unique contributors
            # result = subprocess.run(
            #     ["git", "log", "--format=%an", "--"],
            #     capture_output=True,
            #     text=True
            # )
            # contributors = list(set(result.stdout.strip().split("\n")))
            # return sorted(contributors)

            # Mock data for Phase 2
            return ["Agent1", "Agent2", "Human"]

        except Exception:
            return []

    def last_commit(self) -> Dict[str, Any]:
        """
        Get last commit info

        Returns:
            dict: Last commit details

        Example:
            {% set commit = git.last_commit() %}
            Last updated: {{ commit.date }}
        """
        # TODO: Implement actual git log parsing
        return {
            "hash": "abc123",
            "author": "Agent1",
            "date": datetime.utcnow().isoformat(),
            "message": "feat: Add authentication"
        }
