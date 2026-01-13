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
