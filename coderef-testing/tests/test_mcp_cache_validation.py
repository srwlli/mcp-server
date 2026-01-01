"""
MCP Cache Validation Test

Detects when Claude Code's MCP cache (mcp-cache.json) needs clearing due to:
- Stale tool definitions
- Duplicate commands
- Modified server configurations
- Added/removed MCP servers
- Updated tool schemas

Based on: CLAUDE.md cache clearing guide from coderef-testing server
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# ANSI colors for output
COLORS = {
    'reset': '\x1b[0m',
    'red': '\x1b[31m',
    'green': '\x1b[32m',
    'yellow': '\x1b[33m',
    'blue': '\x1b[34m',
    'cyan': '\x1b[36m'
}


def colorize(text: str, color: str) -> str:
    """Colorize text for terminal output"""
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


class MCPCacheValidator:
    """Validate MCP cache freshness and detect staleness"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.username = Path.home().name
        self.cache_issues: List[str] = []
        self.warnings: List[str] = []

    def get_project_id_hash(self) -> str:
        """
        Calculate project ID hash used by Claude Code.
        Format: Replace backslashes/colons with hyphens, lowercase.
        """
        # Convert path to string and normalize
        path_str = str(self.project_path.resolve())

        # Replace Windows path separators
        normalized = path_str.replace('\\', '-').replace(':', '-').replace('/', '-')

        # Remove leading hyphens and lowercase
        normalized = normalized.strip('-').lower()

        return normalized

    def find_cache_file(self) -> Optional[Path]:
        """
        Find the mcp-cache.json file for current project.

        Location: C:\Users\{USERNAME}\.cursor\projects\{PROJECT_ID}\mcp-cache.json
        """
        project_id = self.get_project_id_hash()
        cache_dir = Path.home() / ".cursor" / "projects" / project_id

        cache_file = cache_dir / "mcp-cache.json"

        if cache_file.exists():
            return cache_file

        # Try to find any mcp-cache.json files
        cursor_projects = Path.home() / ".cursor" / "projects"
        if cursor_projects.exists():
            for cache in cursor_projects.glob("*/mcp-cache.json"):
                # Check if this cache might be for our project
                return cache

        return None

    def read_mcp_config(self) -> Dict:
        """Read .mcp.json configuration"""
        mcp_config = Path.home() / ".mcp.json"

        if not mcp_config.exists():
            self.warnings.append("Global .mcp.json not found")
            return {}

        try:
            return json.loads(mcp_config.read_text())
        except json.JSONDecodeError as e:
            self.cache_issues.append(f".mcp.json is invalid JSON: {e}")
            return {}

    def read_cache(self, cache_file: Path) -> Dict:
        """Read mcp-cache.json file"""
        try:
            return json.loads(cache_file.read_text())
        except json.JSONDecodeError as e:
            self.cache_issues.append(f"Cache file is corrupted: {e}")
            return {}

    def check_server_definitions(self, cache_file: Path) -> bool:
        """
        Check if server definitions in cache match current .mcp.json.

        Returns True if cache needs clearing.
        """
        mcp_config = self.read_mcp_config()
        cache_data = self.read_cache(cache_file)

        if not mcp_config or not cache_data:
            return False

        # Get server definitions from config
        config_servers = mcp_config.get("mcpServers", {})
        cache_servers = cache_data.get("servers", {})

        # Check if server count matches
        if len(config_servers) != len(cache_servers):
            self.cache_issues.append(
                f"Server count mismatch: config has {len(config_servers)}, "
                f"cache has {len(cache_servers)}"
            )
            return True

        # Check each server exists in cache
        for server_name in config_servers:
            if server_name not in cache_servers:
                self.cache_issues.append(f"Server '{server_name}' in config but not in cache")
                return True

        return False

    def check_tool_definitions(self, cache_file: Path) -> bool:
        """
        Check for duplicate or stale tool definitions.

        Returns True if cache needs clearing.
        """
        cache_data = self.read_cache(cache_file)

        if not cache_data:
            return False

        # Extract tools from cache
        tools = cache_data.get("tools", [])
        tool_names = [t.get("name") for t in tools if t.get("name")]

        # Check for duplicates
        duplicates = set([name for name in tool_names if tool_names.count(name) > 1])

        if duplicates:
            self.cache_issues.append(
                f"Duplicate tools found in cache: {', '.join(duplicates)}"
            )
            return True

        return False

    def check_command_definitions(self, cache_file: Path) -> bool:
        """
        Check for duplicate or stale command definitions.

        Returns True if cache needs clearing.
        """
        cache_data = self.read_cache(cache_file)

        if not cache_data:
            return False

        # Extract commands from cache
        commands = cache_data.get("commands", [])
        command_names = [c.get("name") for c in commands if c.get("name")]

        # Check for duplicates
        duplicates = set([name for name in command_names if command_names.count(name) > 1])

        if duplicates:
            self.cache_issues.append(
                f"Duplicate commands found in cache: {', '.join(duplicates)}"
            )
            return True

        return False

    def check_cache_age(self, cache_file: Path) -> bool:
        """
        Check if cache is very old (>7 days).

        Returns True if cache is stale.
        """
        if not cache_file.exists():
            return False

        # Get file modification time
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_days = (datetime.now() - mtime).days

        if age_days > 7:
            self.warnings.append(
                f"Cache is {age_days} days old (last modified: {mtime.strftime('%Y-%m-%d')})"
            )
            return True

        return False

    def check_local_commands_deleted(self) -> bool:
        """
        Check if local .claude/commands/ directory exists.
        If it doesn't but cache has commands, cache may be stale.

        Returns True if suspicious.
        """
        local_commands = self.project_path / ".claude" / "commands"

        # If directory doesn't exist, that's fine (using global commands only)
        if not local_commands.exists():
            return False

        # Directory exists - check if it's empty
        command_files = list(local_commands.glob("*"))

        if len(command_files) == 0:
            self.warnings.append(
                ".claude/commands/ directory exists but is empty - "
                "may indicate deleted commands"
            )

        return False

    def validate(self) -> Dict:
        """
        Run all validation checks.

        Returns validation report.
        """
        report = {
            "cache_file": None,
            "needs_clearing": False,
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        # Find cache file
        cache_file = self.find_cache_file()

        if not cache_file:
            report["warnings"].append("No mcp-cache.json found - cache will be created on next run")
            return report

        report["cache_file"] = str(cache_file)

        # Run checks
        needs_clearing = False

        if self.check_server_definitions(cache_file):
            needs_clearing = True

        if self.check_tool_definitions(cache_file):
            needs_clearing = True

        if self.check_command_definitions(cache_file):
            needs_clearing = True

        if self.check_cache_age(cache_file):
            # Age alone doesn't require clearing, just warning
            pass

        self.check_local_commands_deleted()

        # Compile report
        report["needs_clearing"] = needs_clearing
        report["issues"] = self.cache_issues
        report["warnings"] = self.warnings

        # Add recommendations
        if needs_clearing:
            report["recommendations"] = [
                f"Delete cache file: {cache_file}",
                "Restart Claude Code",
                "Cache will be automatically rebuilt"
            ]

        return report


def test_mcp_cache_validation():
    """
    Test MCP cache validation for current project.

    Run this test when:
    - Tools don't appear in autocomplete
    - Seeing duplicate commands
    - After modifying .mcp.json
    - After adding/removing MCP servers
    """
    import os

    # Get current working directory (project root)
    project_path = os.getcwd()

    print(colorize(f"\n{'='*70}", 'blue'))
    print(colorize("MCP Cache Validation Test", 'cyan'))
    print(colorize(f"{'='*70}\n", 'blue'))

    print(f"Project: {project_path}\n")

    # Run validation
    validator = MCPCacheValidator(project_path)
    report = validator.validate()

    # Display results
    if report["cache_file"]:
        print(colorize(f" Cache file found:", 'green'))
        print(f"  {report['cache_file']}\n")
    else:
        print(colorize("� Cache file not found", 'yellow'))
        print("  Cache will be created automatically on next Claude Code start\n")

    # Display issues
    if report["issues"]:
        print(colorize(f" Issues Found ({len(report['issues']}):", 'red'))
        for issue in report["issues"]:
            print(colorize(f"  " {issue}", 'red'))
        print()

    # Display warnings
    if report["warnings"]:
        print(colorize(f"� Warnings ({len(report['warnings']}):", 'yellow'))
        for warning in report["warnings"]:
            print(colorize(f"  " {warning}", 'yellow'))
        print()

    # Final verdict
    if report["needs_clearing"]:
        print(colorize("=4 RECOMMENDATION: Clear MCP Cache", 'red'))
        print(colorize("\nSteps to Clear Cache:", 'yellow'))
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        print()
        print(colorize("Commands:", 'cyan'))
        if report["cache_file"]:
            print(f"  rm \"{report['cache_file']}\"")
            print(f"  # Then restart Claude Code")
        print()
        return False  # Test fails - action needed
    else:
        print(colorize(" MCP Cache is healthy", 'green'))
        print()
        return True  # Test passes


if __name__ == "__main__":
    # Run as standalone script
    result = test_mcp_cache_validation()
    exit(0 if result else 1)
