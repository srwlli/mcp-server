# Quick Configuration Reference Card

## Three Types of Things (Don't Confuse!)

### 1. mcp.json (Configuration)
```
Location:  ~/.mcp.json  (GLOBAL - HOME DIRECTORY)
What:      Tells Claude where the 4 MCP servers are
How many:  1 FILE ONLY
Content:   4 server definitions (coderef-context, coderef-workflow, coderef-docs, coderef-personas)

❌ NEVER create local mcp.json files
❌ NEVER create coderef-context/mcp.json
❌ NEVER create per-project mcp.json
```

### 2. Slash Commands (User Interface)
```
Location:  ~/.claude/commands/  (GLOBAL - HOME DIRECTORY)
What:      Markdown files that define /stub, /create-workorder, etc.
How many:  26+ files
Examples:  /stub → stub.md
           /create-workorder → create-workorder.md
           /execute-plan → execute-plan.md

❌ NEVER create local command directories
❌ NEVER create per-project .claude/commands/
```

### 3. MCP Servers (Python Implementation)
```
Location:  ~/.mcp-servers/{server-name}/  (HOME DIRECTORY)
What:      Python servers that provide tools
Examples:  coderef-context/server.py → provides 10 tools
           coderef-workflow/server.py → provides 23 tools
           coderef-docs/server.py → provides 11 tools
           coderef-personas/server.py → provides persona tools

❌ DO NOT add mcp.json inside these directories
✅ DO keep implementation details (server.py, tool_handlers.py, etc.)
```

---

## The Directory Structure (Correct)

```
C:\Users\willh\
├── .mcp.json                           ← GLOBAL CONFIG (1 file)
├── .claude\
│   └── commands\                       ← GLOBAL COMMANDS (26+ files)
│       ├── stub.md
│       ├── create-workorder.md
│       ├── execute-plan.md
│       └── ... more commands
│
└── .mcp-servers\                       ← SERVER IMPLEMENTATIONS
    ├── coderef-context\
    │   ├── server.py                   (provides 10 tools)
    │   ├── tool_handlers.py
    │   └── ... other files
    │
    ├── coderef-workflow\
    │   ├── server.py                   (provides 23 tools)
    │   ├── tool_handlers.py
    │   └── ... other files
    │
    ├── coderef-docs\
    │   ├── server.py                   (provides 11 tools)
    │   ├── tool_handlers.py
    │   └── ... other files
    │
    └── coderef-personas\
        ├── server.py                   (provides persona tools)
        └── ... other files
```

---

## How It Works (Simple Flow)

```
YOU TYPE:     /create-workorder my-feature
              ↓
CLAUDE READS: ~/.claude/commands/create-workorder.md
              ↓
COMMAND SAYS: "Call gather_context tool"
              ↓
CLAUDE CHECKS: ~/.mcp.json
               "Where is gather_context? → coderef-workflow"
               ↓
CLAUDE STARTS: ~/.mcp-servers/coderef-workflow/server.py
               ↓
SERVER RUNS: Python server launches, registers all 23 tools
             ↓
TOOL EXECUTES: gather_context(project_path, feature_name, ...)
               ↓
OUTPUT: Creates context.json in coderef/workorder/my-feature/
```

---

## The Three Questions Answered

### ❓ "Where do I put tools?"
**Answer:** Inside `server.py` files in `~/.mcp-servers/`

```python
# ~/.mcp-servers/coderef-workflow/server.py
@app.call_tool()
async def handle_tools(name: str, arguments: dict):
    if name == "gather_context":
        # Tool implementation here
```

### ❓ "Where do I put commands?"
**Answer:** As markdown files in `~/.claude/commands/`

```
~/.claude/commands/stub.md            → /stub command
~/.claude/commands/create-workorder.md → /create-workorder command
~/.claude/commands/execute-plan.md     → /execute-plan command
```

### ❓ "Where do I configure servers?"
**Answer:** In `~/.mcp.json` (ONE file)

```json
{
  "mcpServers": {
    "coderef-workflow": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-workflow/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-workflow"
    }
  }
}
```

---

## Key Rules (Remember These!)

### ✅ DO
- ✅ Keep ~/.mcp.json as your ONLY mcp.json
- ✅ Keep ~/.claude/commands/ as your ONLY commands directory
- ✅ Put tools inside server.py (in ~/.mcp-servers/)
- ✅ Use environment variables in ~/.mcp.json for paths
- ✅ Keep global artifacts in coderef/ directory

### ❌ DON'T
- ❌ Create coderef-context/mcp.json
- ❌ Create coderef-workflow/mcp.json
- ❌ Create local .claude/commands/ directories
- ❌ Mix server configs (one ~/.mcp.json only)
- ❌ Put project data in server directories

---

## Your Current Setup (Summary)

| Item | Status | Location |
|------|--------|----------|
| ~/.mcp.json | ✅ Correct | `C:\Users\willh\.mcp.json` |
| ~/.claude/commands/ | ✅ Correct | `C:\Users\willh\.claude\commands\` |
| Server implementations | ✅ Correct | `C:\Users\willh\.mcp-servers\{name}\` |
| Global artifacts | ✅ Correct | `C:\Users\willh\coderef\` |

**Verdict:** Your configuration is correctly set up! ✅

---

## Most Important Insight

```
Don't think of mcp.json as being "inside" each server.

Think of it as being in ONE place, pointing TO each server.

~/.mcp.json says:
  "When you need coderef_scan, run Python at ~/.mcp-servers/coderef-context/server.py"
  "When you need gather_context, run Python at ~/.mcp-servers/coderef-workflow/server.py"

Each server.py file then says:
  "I have these tools: coderef_scan, coderef_query, etc."
  "I have these tools: gather_context, create_plan, etc."

Simple!
```

---

## If You're Still Confused

Ask yourself these questions:

1. **"Is this a configuration file?"**
   - YES → Put it in ~/.mcp.json or ~/.claude/
   - NO → Put it in ~/.mcp-servers/ or coderef/

2. **"Does this belong to ONE project?"**
   - YES → Put it in coderef/workorder/{feature}/
   - NO → Keep it global

3. **"Is this a tool definition?"**
   - YES → Put it inside server.py (in ~/.mcp-servers/)
   - NO → Put it in ~/.mcp.json or ~/.claude/commands/

4. **"Do other projects need this?"**
   - YES → Keep it global (~/ or ~/.mcp-servers/)
   - NO → Keep it project-specific (coderef/workorder/)

---

**Bottom Line:** One ~/.mcp.json, one ~/.claude/commands/, four independent servers. Done!

