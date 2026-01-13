"""User documentation generator for my-guide, user-guide, and features docs.

USER-003, USER-004, USER-005 (WO-GENERATION-ENHANCEMENT-001):
Enhanced generators that leverage .coderef/ data for tool/command extraction.
"""

from pathlib import Path
from typing import Dict, List, Optional
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger
from .base_generator import BaseGenerator


class UserGuideGenerator(BaseGenerator):
    """
    Generator for user-facing documentation.

    Generates three types of user docs:
    1. my-guide.md - Concise quick reference (60-80 lines)
    2. USER-GUIDE.md - Comprehensive tutorials and onboarding
    3. FEATURES.md - Feature showcase with examples

    USER-003, USER-004, USER-005: Leverages .coderef/index.json for tool discovery.
    """

    USER_TEMPLATES = [
        'my-guide',
        'user-guide',
        'features'
    ]

    def __init__(self, templates_dir: Path):
        """
        Initialize user guide generator.

        Args:
            templates_dir: Path to templates directory
        """
        super().__init__(templates_dir)

    def extract_mcp_tools(self, project_path: Path) -> Dict[str, List[Dict]]:
        """
        USER-003: Extract MCP tools from .coderef/index.json.

        Reads .coderef/index.json to discover MCP tool handlers. Looks for:
        - Functions named handle_* (MCP tool handlers)
        - Functions with @mcp_tool decorator patterns
        - Tool registration patterns

        Args:
            project_path: Absolute path to project directory

        Returns:
            Dictionary with categorized MCP tools
        """
        coderef_index = project_path / ".coderef" / "index.json"

        if not coderef_index.exists():
            logger.warning(f".coderef/index.json not found at {coderef_index}")
            return {
                'tools': [],
                'available': False
            }

        try:
            with open(coderef_index, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            tools = []

            for element in index_data:
                element_type = element.get('type', '')
                name = element.get('name', '')
                file_path = element.get('file', '')

                # Extract MCP tool handlers
                if element_type == 'function':
                    # Look for handle_* pattern (MCP tool handlers)
                    if name.startswith('handle_'):
                        tool_name = name.replace('handle_', '')
                        tools.append({
                            'name': tool_name,
                            'handler': name,
                            'file': file_path,
                            'category': self._categorize_tool(tool_name)
                        })

            logger.info(f"Extracted {len(tools)} MCP tools from .coderef/index.json")

            return {
                'tools': tools,
                'available': True,
                'total_tools': len(tools)
            }

        except Exception as e:
            logger.error(f"Failed to extract MCP tools: {e}", exc_info=True)
            return {
                'tools': [],
                'available': False,
                'error': str(e)
            }

    def _categorize_tool(self, tool_name: str) -> str:
        """
        Categorize tool based on name patterns.

        Args:
            tool_name: Tool name (without handle_ prefix)

        Returns:
            Category string
        """
        if any(kw in tool_name for kw in ['doc', 'readme', 'architecture', 'api', 'schema', 'component']):
            return 'Documentation'
        elif any(kw in tool_name for kw in ['changelog', 'record', 'entry']):
            return 'Changelog'
        elif any(kw in tool_name for kw in ['standard', 'audit', 'consistency', 'compliance']):
            return 'Standards'
        elif any(kw in tool_name for kw in ['plan', 'workflow', 'workorder']):
            return 'Planning'
        elif any(kw in tool_name for kw in ['quickref', 'guide', 'user']):
            return 'User Docs'
        elif any(kw in tool_name for kw in ['validate', 'check', 'health']):
            return 'Validation'
        else:
            return 'Utility'

    def extract_slash_commands(self, project_path: Path) -> Dict[str, List[Dict]]:
        """
        USER-003: Extract slash commands from .claude/commands directory.

        Scans .claude/commands/ for command files (.md or other).

        Args:
            project_path: Absolute path to project directory

        Returns:
            Dictionary with slash commands
        """
        commands_dir = project_path / ".claude" / "commands"

        if not commands_dir.exists():
            logger.warning(f".claude/commands/ not found at {commands_dir}")
            return {
                'commands': [],
                'available': False
            }

        try:
            commands = []

            for cmd_file in commands_dir.glob('*'):
                if cmd_file.is_file():
                    # Command name from filename (without extension)
                    cmd_name = cmd_file.stem

                    # Read first line for description
                    try:
                        with open(cmd_file, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            # Strip markdown comment if present
                            description = first_line.lstrip('#').strip()
                    except Exception:
                        description = "No description available"

                    commands.append({
                        'name': f"/{cmd_name}",
                        'description': description,
                        'file': str(cmd_file)
                    })

            logger.info(f"Extracted {len(commands)} slash commands from .claude/commands/")

            return {
                'commands': sorted(commands, key=lambda x: x['name']),
                'available': True,
                'total_commands': len(commands)
            }

        except Exception as e:
            logger.error(f"Failed to extract slash commands: {e}", exc_info=True)
            return {
                'commands': [],
                'available': False,
                'error': str(e)
            }

    def generate_my_guide(
        self,
        project_path: Path,
        mcp_tools: Optional[Dict] = None,
        slash_commands: Optional[Dict] = None
    ) -> str:
        """
        USER-003: Generate my-guide.md content with real tool/command data.

        Args:
            project_path: Project root directory
            mcp_tools: Optional extracted MCP tools (will auto-extract if None)
            slash_commands: Optional extracted slash commands (will auto-extract if None)

        Returns:
            Generated my-guide.md content
        """
        # Extract if not provided
        if mcp_tools is None:
            mcp_tools = self.extract_mcp_tools(project_path)
        if slash_commands is None:
            slash_commands = self.extract_slash_commands(project_path)

        # Start building content
        content = []
        content.append(f"# {project_path.name} - Quick Reference")
        content.append("")
        content.append("## MCP Tools")
        content.append("")

        # Group tools by category
        if mcp_tools['available'] and mcp_tools['tools']:
            categories = {}
            for tool in mcp_tools['tools']:
                cat = tool['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(tool)

            for category in sorted(categories.keys()):
                content.append(f"### {category}")
                content.append("")
                for tool in sorted(categories[category], key=lambda x: x['name']):
                    # Generate brief description from tool name
                    desc = self._generate_tool_description(tool['name'])
                    content.append(f"- `{tool['name']}` - {desc}")
                content.append("")
        else:
            content.append("*(No MCP tools found - run coderef_scan to discover tools)*")
            content.append("")

        content.append("## Slash Commands")
        content.append("")

        if slash_commands['available'] and slash_commands['commands']:
            for cmd in slash_commands['commands']:
                content.append(f"- `{cmd['name']}` - {cmd['description']}")
        else:
            content.append("*(No slash commands found)*")

        content.append("")
        content.append("---")
        content.append(f"*Generated by coderef-docs • {len(mcp_tools.get('tools', []))} tools, {len(slash_commands.get('commands', []))} commands*")

        return "\n".join(content)

    def _generate_tool_description(self, tool_name: str) -> str:
        """
        Generate brief description from tool name.

        Args:
            tool_name: Tool name

        Returns:
            Brief description string
        """
        # Convert snake_case to words
        words = tool_name.replace('_', ' ').split()

        # Capitalize and create phrase
        if 'generate' in words:
            return f"Generate {' '.join(words[1:])}"
        elif 'create' in words:
            return f"Create {' '.join(words[1:])}"
        elif 'get' in words:
            return f"Get {' '.join(words[1:])}"
        elif 'list' in words:
            return f"List {' '.join(words[1:])}"
        elif 'record' in words:
            return f"Record {' '.join(words[1:])}"
        elif 'establish' in words:
            return f"Establish {' '.join(words[1:])}"
        elif 'audit' in words:
            return f"Audit {' '.join(words[1:])}"
        elif 'check' in words:
            return f"Check {' '.join(words[1:])}"
        elif 'validate' in words:
            return f"Validate {' '.join(words[1:])}"
        else:
            return ' '.join(words).capitalize()

    def save_my_guide(self, content: str, project_path: Path) -> str:
        """
        USER-003: Save my-guide.md to project directory.

        Args:
            content: Generated content
            project_path: Project root directory

        Returns:
            Path to saved file

        Raises:
            IOError: If file cannot be written
        """
        # Create coderef/user directory if needed
        user_docs_dir = project_path / Paths.USER_DOCS
        user_docs_dir.mkdir(parents=True, exist_ok=True)

        # Save my-guide.md
        my_guide_path = user_docs_dir / "my-guide.md"
        try:
            with open(my_guide_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"my-guide.md saved to: {my_guide_path}")
            return str(my_guide_path)
        except Exception as e:
            raise IOError(f"Error saving my-guide.md to {my_guide_path}: {str(e)}")

    def generate_user_guide(
        self,
        project_path: Path,
        mcp_tools: Optional[Dict] = None,
        slash_commands: Optional[Dict] = None
    ) -> str:
        """
        USER-004: Generate USER-GUIDE.md content with comprehensive onboarding.

        Args:
            project_path: Project root directory
            mcp_tools: Optional extracted MCP tools (will auto-extract if None)
            slash_commands: Optional extracted slash commands (will auto-extract if None)

        Returns:
            Generated USER-GUIDE.md content
        """
        # Extract if not provided
        if mcp_tools is None:
            mcp_tools = self.extract_mcp_tools(project_path)
        if slash_commands is None:
            slash_commands = self.extract_slash_commands(project_path)

        project_name = project_path.name
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # Start building comprehensive user guide
        content = []
        content.append(f"# {project_name} User Guide")
        content.append("")
        content.append(f"**Last Updated:** {today}")
        content.append(f"**Generated by:** coderef-docs")
        content.append("")
        content.append("---")
        content.append("")

        # Table of Contents
        content.append("## Table of Contents")
        content.append("")
        content.append("1. [Introduction](#introduction)")
        content.append("2. [Prerequisites](#prerequisites)")
        content.append("3. [Installation](#installation)")
        content.append("4. [Architecture](#architecture)")
        content.append("5. [MCP Tools Reference](#mcp-tools-reference)")
        content.append("6. [Slash Commands](#slash-commands)")
        content.append("7. [Common Workflows](#common-workflows)")
        content.append("8. [Best Practices](#best-practices)")
        content.append("9. [Troubleshooting](#troubleshooting)")
        content.append("10. [Quick Reference](#quick-reference)")
        content.append("")
        content.append("---")
        content.append("")

        # Introduction
        content.append("## Introduction")
        content.append("")
        content.append(f"Welcome to {project_name}! This guide provides comprehensive onboarding ")
        content.append("and reference documentation for using this MCP server.")
        content.append("")
        content.append("### What is this?")
        content.append("")
        content.append(f"{project_name} is an MCP (Model Context Protocol) server that provides ")
        content.append("tools for AI-assisted development workflows.")
        content.append("")
        content.append("---")
        content.append("")

        # Prerequisites
        content.append("## Prerequisites")
        content.append("")
        content.append("Before getting started, ensure you have:")
        content.append("")
        content.append("- ✅ **Python 3.10+**")
        content.append("  ```bash")
        content.append("  python --version  # Expected: Python 3.10.x or higher")
        content.append("  ```")
        content.append("")
        content.append("- ✅ **Git** (for version control)")
        content.append("  ```bash")
        content.append("  git --version  # Expected: git version 2.x+")
        content.append("  ```")
        content.append("")
        content.append("- ✅ **Claude Code or MCP-compatible client**")
        content.append("")
        content.append("---")
        content.append("")

        # Installation
        content.append("## Installation")
        content.append("")
        content.append("### Step 1: Install Dependencies")
        content.append("")
        content.append("```bash")
        content.append("# Using uv (recommended)")
        content.append("uv sync")
        content.append("")
        content.append("# Or using pip")
        content.append("pip install -r requirements.txt")
        content.append("```")
        content.append("")
        content.append("### Step 2: Configure MCP Server")
        content.append("")
        content.append("Add to your `.mcp.json`:")
        content.append("")
        content.append("```json")
        content.append("{")
        content.append(f'  "{project_name}": {{')
        content.append(f'    "command": "python",')
        content.append(f'    "args": ["{project_path}/server.py"]')
        content.append("  }")
        content.append("}")
        content.append("```")
        content.append("")
        content.append("### Step 3: Verify Installation")
        content.append("")
        content.append("```bash")
        content.append("python server.py  # Server should start without errors")
        content.append("```")
        content.append("")
        content.append("---")
        content.append("")

        # Architecture
        content.append("## Architecture")
        content.append("")
        content.append("### How It Works")
        content.append("")
        content.append("```")
        content.append("┌─────────────────┐")
        content.append("│  Claude Code    │")
        content.append("└────────┬────────┘")
        content.append("         │ MCP Protocol (JSON-RPC)")
        content.append("         ▼")
        content.append("┌─────────────────┐")
        content.append(f"│  {project_name:^15} │")
        content.append("└────────┬────────┘")
        content.append("         │")
        content.append("         ├─► MCP Tools (")
        if mcp_tools['available']:
            content.append(f"{mcp_tools['total_tools']} tools)")
        else:
            content.append("N/A)")
        content.append("         └─► Slash Commands (")
        if slash_commands['available']:
            content.append(f"{slash_commands['total_commands']} commands)")
        else:
            content.append("N/A)")
        content.append("```")
        content.append("")
        content.append("---")
        content.append("")

        # MCP Tools Reference
        content.append("## MCP Tools Reference")
        content.append("")

        if mcp_tools['available'] and mcp_tools['tools']:
            # Group by category
            categories = {}
            for tool in mcp_tools['tools']:
                cat = tool['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(tool)

            for category in sorted(categories.keys()):
                content.append(f"### {category}")
                content.append("")
                content.append("| Tool | Description | Handler |")
                content.append("|------|-------------|---------|")
                for tool in sorted(categories[category], key=lambda x: x['name']):
                    desc = self._generate_tool_description(tool['name'])
                    content.append(f"| `{tool['name']}` | {desc} | `{tool['handler']}` |")
                content.append("")
        else:
            content.append("*(No MCP tools discovered - run coderef_scan to analyze project)*")
            content.append("")

        content.append("---")
        content.append("")

        # Slash Commands
        content.append("## Slash Commands")
        content.append("")

        if slash_commands['available'] and slash_commands['commands']:
            content.append("| Command | Description |")
            content.append("|---------|-------------|")
            for cmd in slash_commands['commands']:
                content.append(f"| `{cmd['name']}` | {cmd['description']} |")
        else:
            content.append("*(No slash commands found in .claude/commands/)*")

        content.append("")
        content.append("---")
        content.append("")

        # Common Workflows
        content.append("## Common Workflows")
        content.append("")
        content.append("### Workflow 1: Quick Setup")
        content.append("")
        content.append("```bash")
        content.append("1. Install dependencies: uv sync")
        content.append("2. Configure MCP: Add server to .mcp.json")
        content.append("3. Start server: python server.py")
        content.append("4. Verify: Check Claude Code sees the tools")
        content.append("```")
        content.append("")
        content.append("**Time estimate:** 2-5 minutes")
        content.append("")

        # Best Practices
        content.append("---")
        content.append("")
        content.append("## Best Practices")
        content.append("")
        content.append("### ✅ Do")
        content.append("")
        content.append("- Run `coderef_scan` before generating documentation")
        content.append("- Keep `.coderef/` data fresh for accurate results")
        content.append("- Use absolute paths when calling MCP tools")
        content.append("- Review generated docs before committing")
        content.append("")
        content.append("### 🚫 Don't")
        content.append("")
        content.append("- Don't generate docs from stale `.coderef/` data (>10% drift)")
        content.append("- Don't modify generated files directly (regenerate instead)")
        content.append("- Don't skip validation steps")
        content.append("")
        content.append("### 💡 Tips")
        content.append("")
        content.append("- Use drift detection to know when to re-scan")
        content.append("- Leverage code intelligence for accurate documentation")
        content.append("- Combine multiple tools for complete workflows")
        content.append("")

        # Troubleshooting
        content.append("---")
        content.append("")
        content.append("## Troubleshooting")
        content.append("")
        content.append("### Problem: MCP server not responding")
        content.append("")
        content.append("**Symptoms:**")
        content.append("- Tools don't appear in Claude Code")
        content.append("- Server process exits immediately")
        content.append("")
        content.append("**Cause:** Missing dependencies or configuration error")
        content.append("")
        content.append("**Solution:**")
        content.append("```bash")
        content.append("# Check dependencies")
        content.append("uv sync")
        content.append("")
        content.append("# Verify .mcp.json configuration")
        content.append("cat ~/.mcp.json")
        content.append("")
        content.append("# Check server logs")
        content.append("python server.py 2>&1 | tee server.log")
        content.append("```")
        content.append("")

        # Quick Reference
        content.append("---")
        content.append("")
        content.append("## Quick Reference")
        content.append("")
        content.append("| Operation | Command | Time |")
        content.append("|-----------|---------|------|")
        content.append("| Install | `uv sync` | 30s |")
        content.append("| Start server | `python server.py` | <1s |")
        if mcp_tools['available']:
            content.append(f"| Total tools | {mcp_tools['total_tools']} | - |")
        if slash_commands['available']:
            content.append(f"| Total commands | {slash_commands['total_commands']} | - |")
        content.append("")

        # Footer
        content.append("---")
        content.append("")
        content.append("**Questions?** Check the troubleshooting section or consult the README.")
        content.append("")
        content.append(f"*Generated by coderef-docs • Last updated: {today}*")

        return "\n".join(content)

    def save_user_guide(self, content: str, project_path: Path) -> str:
        """
        USER-004: Save USER-GUIDE.md to project directory.

        Args:
            content: Generated content
            project_path: Project root directory

        Returns:
            Path to saved file

        Raises:
            IOError: If file cannot be written
        """
        # Create coderef/user directory if needed
        user_docs_dir = project_path / Paths.USER_DOCS
        user_docs_dir.mkdir(parents=True, exist_ok=True)

        # Save USER-GUIDE.md
        user_guide_path = user_docs_dir / "USER-GUIDE.md"
        try:
            with open(user_guide_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"USER-GUIDE.md saved to: {user_guide_path}")
            return str(user_guide_path)
        except Exception as e:
            raise IOError(f"Error saving USER-GUIDE.md to {user_guide_path}: {str(e)}")

    def generate_features(self, project_path: Path) -> str:
        """
        USER-005: Generate FEATURES.md inventory with workorder tracking.

        Args:
            project_path: Project root directory

        Returns:
            Generated FEATURES.md content
        """
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # Scan for active features
        workorder_dir = project_path / "coderef" / "workorder"
        archived_dir = project_path / "coderef" / "archived"

        active_features = []
        archived_features = []

        # Scan workorder directory
        if workorder_dir.exists():
            for feature_dir in workorder_dir.iterdir():
                if feature_dir.is_dir():
                    feature_info = self._extract_feature_info(feature_dir)
                    if feature_info:
                        active_features.append(feature_info)

        # Scan archived directory
        if archived_dir.exists():
            for feature_dir in archived_dir.iterdir():
                if feature_dir.is_dir():
                    feature_info = self._extract_feature_info(feature_dir, archived=True)
                    if feature_info:
                        archived_features.append(feature_info)

        # Calculate statistics
        total_count = len(active_features) + len(archived_features)
        workorder_count = sum(1 for f in active_features + archived_features if f.get('workorder_id'))
        plan_count = sum(1 for f in active_features + archived_features if f.get('has_plan'))

        # Build content
        content = []
        content.append("# Features Inventory")
        content.append("")
        content.append(f"**Generated:** {today}")
        content.append(f"**Project:** {project_path.name}")
        content.append("")
        content.append("## Executive Summary")
        content.append("")
        content.append("| Metric | Count |")
        content.append("|--------|-------|")
        content.append(f"| Active Features | {len(active_features)} |")
        content.append(f"| Archived Features | {len(archived_features)} |")
        content.append(f"| Total Features | {total_count} |")
        content.append(f"| With Workorder | {workorder_count} |")
        content.append(f"| With Plan | {plan_count} |")
        content.append("")
        content.append("---")
        content.append("")

        # Active Features
        content.append("## Active Features")
        content.append("")
        content.append("Features currently in development (coderef/workorder/).")
        content.append("")

        if active_features:
            content.append("| Feature | Status | Workorder | Has Plan |")
            content.append("|---------|--------|-----------|----------|")
            for feature in sorted(active_features, key=lambda x: x['name']):
                status = feature.get('status', 'unknown')
                workorder = feature.get('workorder_id', 'N/A')
                has_plan = '✓' if feature.get('has_plan') else '✗'
                content.append(f"| {feature['name']} | {status} | {workorder} | {has_plan} |")
            content.append("")
        else:
            content.append("*(No active features)*")
            content.append("")

        content.append("---")
        content.append("")

        # Archived Features
        content.append("## Archived Features")
        content.append("")
        content.append("Completed features (coderef/archived/).")
        content.append("")

        if archived_features:
            content.append("| Feature | Workorder | Has Plan |")
            content.append("|---------|-----------|----------|")
            for feature in sorted(archived_features, key=lambda x: x['name']):
                workorder = feature.get('workorder_id', 'N/A')
                has_plan = '✓' if feature.get('has_plan') else '✗'
                content.append(f"| {feature['name']} | {workorder} | {has_plan} |")
            content.append("")
        else:
            content.append("*(No archived features)*")
            content.append("")

        content.append("---")
        content.append("")

        # Usage Notes
        content.append("## Usage Notes")
        content.append("")
        content.append("### Finding Features by Workorder")
        content.append("")
        content.append("Search for features using their workorder ID pattern:")
        content.append("```")
        content.append("WO-{FEATURE-NAME}-{CATEGORY}-{NUMBER}")
        content.append("```")
        content.append("")
        content.append("Example: `WO-AUTH-SYSTEM-001`")
        content.append("")
        content.append("### Feature Lifecycle")
        content.append("")
        content.append("```")
        content.append("/create-workorder → context.json + analysis.json + plan.json")
        content.append("       ↓")
        content.append("/execute-plan → implementation (progress tracked in plan.json)")
        content.append("       ↓")
        content.append("/update-deliverables → DELIVERABLES.md with metrics")
        content.append("       ↓")
        content.append("/update-docs → changelog, README, CLAUDE.md updates")
        content.append("       ↓")
        content.append("/archive-feature → moves to coderef/archived/")
        content.append("```")
        content.append("")
        content.append("---")
        content.append("")
        content.append(f"*Generated by coderef-docs • Last updated: {today}*")

        return "\n".join(content)

    def _extract_feature_info(self, feature_dir: Path, archived: bool = False) -> Optional[Dict]:
        """
        Extract feature information from feature directory.

        Args:
            feature_dir: Path to feature directory
            archived: Whether feature is archived

        Returns:
            Dictionary with feature info or None if invalid
        """
        plan_file = feature_dir / "plan.json"
        context_file = feature_dir / "context.json"

        feature_info = {
            'name': feature_dir.name,
            'has_plan': plan_file.exists(),
            'has_context': context_file.exists(),
            'archived': archived
        }

        # Try to extract workorder ID and status from plan.json
        if plan_file.exists():
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                    meta = plan_data.get('META_DOCUMENTATION', {})
                    feature_info['workorder_id'] = meta.get('workorder_id', 'N/A')
                    feature_info['status'] = meta.get('status', 'unknown')
            except Exception as e:
                logger.warning(f"Failed to read plan.json for {feature_dir.name}: {e}")

        return feature_info

    def save_features(self, content: str, project_path: Path) -> str:
        """
        USER-005: Save FEATURES.md to project directory.

        Args:
            content: Generated content
            project_path: Project root directory

        Returns:
            Path to saved file

        Raises:
            IOError: If file cannot be written
        """
        # Create coderef/user directory if needed
        user_docs_dir = project_path / Paths.USER_DOCS
        user_docs_dir.mkdir(parents=True, exist_ok=True)

        # Save FEATURES.md
        features_path = user_docs_dir / "FEATURES.md"
        try:
            with open(features_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"FEATURES.md saved to: {features_path}")
            return str(features_path)
        except Exception as e:
            raise IOError(f"Error saving FEATURES.md to {features_path}: {str(e)}")
