# Slash Commands for docs-mcp

This directory contains **22 slash commands** for quick access to docs-mcp MCP tools.

## How Slash Commands Work

Each `.md` file in this directory defines a slash command that can be invoked by typing `/command-name` in Claude Code.

## Complete Command List (22 total)

### Changelog Management (3 commands)

| Command | Description |
|---------|-------------|
| `/add-changelog` | Add a new entry to the project changelog |
| `/get-changelog` | Get changelog entries for current project with optional filters |
| `/update-changelog` | Agentic workflow to analyze recent changes and update changelog automatically |

### Documentation Generation (6 commands)

| Command | Description |
|---------|-------------|
| `/generate-docs` | Generate foundation documentation for current project |
| `/generate-user-guide` | Generate USER-GUIDE documentation for current project |
| `/generate-quickref` | Generate scannable quickref guide for any application |
| `/generate-my-guide` | Generate my-guide quick reference documentation |
| `/list-templates` | List all available POWER framework documentation templates |
| `/get-template` | Get the content of a specific POWER framework documentation template |

### Project Inventory (4 commands)

| Command | Description |
|---------|-------------|
| `/inventory-manifest` | Generate comprehensive project file inventory manifest |
| `/dependency-inventory` | Generate comprehensive project dependency inventory |
| `/api-inventory` | Generate comprehensive API endpoint inventory |
| `/database-inventory` | Generate comprehensive database schema inventory |

### Implementation Planning (6 commands)

| Command | Description |
|---------|-------------|
| `/gather-context` | Gather feature requirements and context before planning implementation |
| `/analyze-for-planning` | Analyze project for implementation planning (discovers docs, standards, patterns) |
| `/get-planning-template` | Get feature implementation planning template for AI reference |
| `/create-plan` | Create implementation plan by synthesizing context, analysis, and template |
| `/validate-plan` | Validate implementation plan quality (scores 0-100, identifies issues) |
| `/generate-plan-review` | Generate markdown review report from validation results |

### Code Standards & Consistency (3 commands)

| Command | Description |
|---------|-------------|
| `/establish-standards` | Extract UI/UX/behavior standards from current project |
| `/audit-codebase` | Audit current project for standards compliance |
| `/check-consistency` | Quick consistency check on modified files (pre-commit gate) |

## Usage

### Basic Usage
```
/command-name
```

### With Parameters (prompts will appear)
Some commands like `/add-changelog` will prompt you for required information.

### Natural Language Alternative
If a command doesn't appear in autocomplete, you can still use it by asking naturally:
```
"Please run the get-changelog command"
"Can you add a changelog entry?"
```

## Command File Format

Each `.md` file contains:
1. **First line**: Short description (used in autocomplete)
2. **Body**: Detailed instructions for AI on how to execute the command
3. **Tool calls**: References to MCP tools (e.g., `mcp__docs-mcp__get_changelog`)

Example:
```markdown
Get changelog entries for the current project with optional filters.

Call the `mcp__docs-mcp__get_changelog` tool with the current working directory as the project_path.

Optional filters:
- version: Get specific version
- change_type: Filter by type
- breaking_only: Show only breaking changes
```

## Adding New Commands

1. Create a new `.md` file in this directory
2. Use kebab-case naming (e.g., `my-new-command.md`)
3. Follow the format above
4. Update this README
5. Update `.claude/commands.json`
6. Commit changes

## Troubleshooting

### Command doesn't appear in autocomplete
1. Reload Claude Code window: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Ensure you're in the docs-mcp project directory
3. Check file permissions: `ls -la .claude/commands/`
4. Try typing the full command manually

### Command exists but doesn't work
1. Check the `.md` file syntax
2. Verify MCP tool name is correct
3. Check tool is registered in `server.py`
4. Review error logs in Claude Code

## Registry File

`.claude/commands.json` contains a structured registry of all commands with categories and metadata. This file helps Claude Code discover and organize commands.

## Related Documentation

- **README.md** - Main project documentation
- **CLAUDE.md** - AI assistant context documentation
- **my-guide.md** - Concise tool reference
- **coderef/quickref.md** - Quick reference guide

---

**Last Updated**: 2025-10-15
**Version**: 1.8.0
**Total Commands**: 22
