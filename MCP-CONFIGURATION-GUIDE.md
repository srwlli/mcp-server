# MCP Configuration Guide

## Understanding User-Level vs Project-Level Configurations

This guide explains the different configuration scopes for MCP (Model Context Protocol) servers in Claude Code.

---

## Configuration Scopes

There are **3 scopes** where MCP servers can be configured:

### 1. User-Level Configuration (`-s user`)

**Simple analogy**: Like installing an app for ALL users on your computer.

- **Location**: Stored in your Windows user profile (`~/.config/claude/` or similar)
- **Availability**: Works in **EVERY project** across your entire system
- **Persistence**: Always available, no matter what folder you're in
- **Best for**: General-purpose tools you use daily (documentation generators, code analyzers)

**Example:**
```bash
claude mcp add -s user docs-mcp ...
```

**To check:**
```bash
claude mcp get docs-mcp
# Output: Scope: User config (available in all your projects)
```

---

### 2. Project-Level Configuration (`-s project`)

**Simple analogy**: Like putting a portable app in just one folder.

- **Location**: Stored in `.mcp.json` in the current project directory
- **Availability**: Only works when you're **in that specific project folder**
- **Persistence**: Tied to that project directory
- **Best for**: Project-specific integrations (project API, database tools) that the whole team needs
- **Git**: Can be committed to share with team, or added to `.gitignore`

**Example:**
```bash
cd /path/to/my-project
claude mcp add -s project my-project-api ...
```

---

### 3. Local-Level Configuration (`-s local`) [default]

**Simple analogy**: Like a personal app just for you in one project folder.

- **Location**: Stored in `.claude/mcp.json` in the current project directory
- **Availability**: Only in this project, only for you (not shared)
- **Persistence**: Tied to that project directory
- **Best for**: Personal development tools you don't want to share (experimental servers)
- **Git**: Usually in `.gitignore` (stays personal)

**Example:**
```bash
cd /path/to/my-project
claude mcp add -s local experimental-tool ...
# Or just:
claude mcp add experimental-tool ...
```

---

## Visual Comparison

```
User Level (~/.config/claude/)
├── docs-mcp           ✓ Available EVERYWHERE
├── coderef-mcp        ✓ Available EVERYWHERE
├── personas-mcp       ✓ Available EVERYWHERE
└── hello-world-mcp    ✓ Available EVERYWHERE

Project Level (/path/to/project-a/.mcp.json)
└── project-a-api      ✓ Only when in project-a folder

Local Level (/path/to/project-a/.claude/mcp.json)
└── my-personal-tool   ✓ Only when in project-a folder (not in git)
```

---

## Current Setup (This System)

All MCP servers in this repository are configured at **user-level**:

```bash
claude mcp list
```

Output:
```
docs-mcp: ✓ Connected (User config)
coderef-mcp: ✓ Connected (User config)
personas-mcp: ✓ Connected (User config)
hello-world-mcp: ✓ Connected (User config)
```

**Configuration format:**
```json
{
  "command": "python",
  "args": ["C:/Users/willh/.mcp-servers/{server-name}/server.py"]
}
```

### Slash Commands

Slash commands are shortcuts that execute MCP tools. They must be deployed **globally** to work across all projects.

**Location**: `~/.claude/commands/` (or `C:/Users/willh/.claude/commands/` on Windows)

**Currently deployed** (36 total slash commands):

**From docs-mcp** (25 commands):
- `/generate-docs` - Generate foundation documentation
- `/generate-user-guide` - Generate user guide
- `/generate-quickref` - Generate quick reference
- `/establish-standards` - Extract coding standards
- `/audit-codebase` - Audit for standards compliance
- `/check-consistency` - Quick consistency check
- `/analyze-for-planning` - Analyze project for planning
- `/create-plan` - Create implementation plan
- `/validate-plan` - Validate plan quality
- `/generate-plan-review` - Generate plan review report
- `/generate-deliverables` - Generate deliverables template
- `/update-deliverables` - Update deliverables with git metrics
- `/update-docs` - Update all documentation
- `/add-changelog` - Add changelog entry
- `/get-changelog` - Get changelog entries
- `/update-changelog` - Update changelog (agentic)
- `/inventory-manifest` - Generate file inventory
- `/dependency-inventory` - Analyze dependencies
- `/api-inventory` - Discover API endpoints
- `/database-inventory` - Discover database schemas
- `/config-inventory` - Analyze config files
- `/test-inventory` - Discover test infrastructure
- `/documentation-inventory` - Analyze documentation
- `/archive-feature` - Archive completed features
- And more...

**From personas-mcp** (5 commands):
- `/lloyd` - Activate Lloyd persona (task executor)
- `/use-persona` - Activate any persona
- `/coderef-expert` - Activate CodeRef expert
- `/docs-expert` - Activate docs expert
- `/nfl-scraper-expert` - Activate NFL scraper expert

**From coderef-mcp** (6 commands):
- `/coderef-query` - Query CodeRef elements
- `/coderef-analyze` - Deep analysis on CodeRef elements
- `/coderef-validate` - Validate CodeRef references
- `/coderef-batch-validate` - Batch validate references
- `/coderef-docs` - Generate documentation for CodeRef
- `/coderef-audit` - Audit CodeRef elements

**How to deploy slash commands globally:**

```bash
# Deploy docs-mcp slash commands
cp C:/Users/willh/.mcp-servers/docs-mcp/.claude/commands/*.md ~/.claude/commands/

# Deploy personas-mcp slash commands
cp C:/Users/willh/.mcp-servers/personas-mcp/.claude/commands/*.md ~/.claude/commands/

# Deploy coderef-mcp slash commands
cp C:/Users/willh/.mcp-servers/coderef-mcp/.claude/commands/*.md ~/.claude/commands/

# Verify deployment (should show 36 files)
ls ~/.claude/commands/ | wc -l
```

**After deployment:**
1. Reload Claude Code window (Ctrl+Shift+P → "Developer: Reload Window")
2. Type `/` in chat to see autocomplete list
3. All slash commands should appear

---

## When to Use Each Level

| Level | Use Case | Example |
|-------|----------|---------|
| **User** | General tools you use everywhere | Documentation generators, code formatters, linters |
| **Project** | Project-specific integrations shared with team | Project's REST API server, database query tool |
| **Local** | Personal experiments not ready to share | Beta/experimental servers, personal dev tools |

---

## Quick Reference Commands

### Check a server's scope
```bash
claude mcp get <server-name>
```

### Add server at different scopes
```bash
# User level (available everywhere)
claude mcp add -s user my-server -- python server.py

# Project level (this project only)
claude mcp add -s project my-server -- python server.py

# Local level (personal, not shared)
claude mcp add -s local my-server -- python server.py
```

### Remove server from specific scope
```bash
claude mcp remove <server-name> -s user
claude mcp remove <server-name> -s project
claude mcp remove <server-name> -s local
```

### List all servers
```bash
claude mcp list
```

---

## Where Everything Lives

Understanding where MCP configurations and slash commands are stored:

### MCP Server Configurations

**User-level config** (available everywhere):
```
Windows: C:\Users\willh\.claude\mcp.json
Linux/Mac: ~/.claude/mcp.json
```
This file contains all your user-level MCP servers (docs-mcp, coderef-mcp, etc.)

**Project-level config** (only in that project):
```
/path/to/your-project/.mcp.json
```
This file only exists if you have project-specific MCP servers

**Local-level config** (personal, not shared):
```
/path/to/your-project/.claude/mcp.json
```
This file only exists if you have personal MCP servers for that project

### Slash Command Files

**Global slash commands** (available everywhere):
```
Windows: C:\Users\willh\.claude\commands\
Linux/Mac: ~/.claude/commands/
```
**All 36 slash commands live here**:
- generate-docs.md
- lloyd.md
- coderef-query.md
- etc.

**Project slash commands** (only in that project):
```
/path/to/your-project/.claude/commands/
```
Only exists if you have project-specific slash commands

### MCP Server Source Code

**Your MCP servers live here:**
```
C:\Users\willh\.mcp-servers\
├── docs-mcp\
│   ├── server.py              ← The actual server code
│   └── .claude\
│       └── commands\          ← Slash commands (must be copied to ~/.claude/commands/)
│           ├── generate-docs.md
│           ├── create-plan.md
│           └── ... (25 total)
├── coderef-mcp\
│   ├── server.py
│   └── .claude\
│       └── commands\
│           ├── coderef-query.md
│           └── ... (6 total)
├── personas-mcp\
│   ├── server.py
│   └── .claude\
│       └── commands\
│           ├── lloyd.md
│           └── ... (5 total)
└── hello-world-mcp\
    └── server.py
```

### Visual Map

```
Your Computer
│
├── C:\Users\willh\.claude\
│   ├── mcp.json                    ← User-level MCP configs (4 servers)
│   └── commands\                   ← Global slash commands (36 files)
│       ├── generate-docs.md        ✓ Deployed from docs-mcp
│       ├── lloyd.md                ✓ Deployed from personas-mcp
│       └── coderef-query.md        ✓ Deployed from coderef-mcp
│
├── C:\Users\willh\.mcp-servers\    ← MCP server source code
│   ├── docs-mcp\
│   │   ├── server.py               ← Server runs from here
│   │   └── .claude\commands\       ← Source of slash commands
│   ├── coderef-mcp\
│   │   ├── server.py
│   │   └── .claude\commands\
│   ├── personas-mcp\
│   │   ├── server.py
│   │   └── .claude\commands\
│   └── hello-world-mcp\
│       └── server.py
│
└── C:\Users\willh\some-project\    ← Your actual work projects
    └── .mcp.json                   ← Project-level configs (if any)
```

### Key Takeaways

1. **MCP servers run from**: `C:\Users\willh\.mcp-servers\{server-name}\server.py`
2. **MCP servers configured in**: `C:\Users\willh\.claude\mcp.json` (user-level)
3. **Slash commands stored in**: `C:\Users\willh\.claude\commands\` (must be copied here)
4. **Slash commands source**: `C:\Users\willh\.mcp-servers\{server-name}\.claude\commands\`

**Remember**: Slash commands in `.mcp-servers/{server}/.claude/commands/` are just templates. They **must be copied** to `~/.claude/commands/` to work globally.

---

## Troubleshooting

### Server shows "Failed to connect"

**Check the scope:**
```bash
claude mcp get <server-name>
```

**Common issues:**
1. Server configured at project-level but you're in wrong folder
2. Incorrect Python path (Windows requires absolute paths)
3. Missing dependencies (`pip install mcp`)

**Solution**: Configure at user-level for general tools
```bash
claude mcp remove <server-name> -s project
claude mcp add-json -s user <server-name> '{"command":"python","args":["C:/full/path/to/server.py"]}'
```

### Multiple Python installations

If you have multiple Python installations:
1. Remove Windows Store Python stubs (Settings > Apps > App execution aliases)
2. Use absolute path to your main Python installation in MCP config

---

## Best Practices

1. **Use user-level for general tools** - If you use it in multiple projects, put it at user-level
2. **Use absolute paths** - Especially on Windows: `C:/Users/...` not relative paths
3. **Don't use `cmd /c`** - Direct Python command works better: `"command": "python"`
4. **Test after changes** - Run `claude mcp list` to verify connection status
5. **Clean up conflicts** - Remove old project-level configs if moving to user-level

---

## Additional Resources

- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/anthropics/mcp)

---

**Last Updated**: 2025-10-19
**System**: Windows 11, Python 3.13.2
