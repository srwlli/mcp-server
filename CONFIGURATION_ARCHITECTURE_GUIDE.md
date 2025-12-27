# CodeRef Ecosystem - Configuration Architecture Guide

**Date:** December 26, 2025
**Purpose:** Clarify MCP servers, tools, commands, and their proper placement
**Audience:** Anyone confused about local vs global configuration

---

## The Big Picture (Simplified)

```
Claude Code (Your AI Assistant)
    ↓
~/.mcp.json (GLOBAL CONFIG - Where are the MCP servers?)
    ↓
~/.claude/commands/ (GLOBAL COMMANDS - What can I type as slash commands?)
    ↓
4 MCP Servers (Run Python scripts that provide TOOLS)
    ├─ coderef-context (10 TOOLS: coderef_scan, coderef_query, etc.)
    ├─ coderef-workflow (23 TOOLS: gather_context, create_plan, execute_plan, etc.)
    ├─ coderef-docs (11 TOOLS: generate_docs, record_changes, etc.)
    └─ coderef-personas (USE_PERSONA tool: activate expert personas)
```

---

## Three Different Things (Confused Often)

### 1️⃣ MCP SERVERS (Python Programs)
**What:** Background services that provide tools
**Where:** `C:\Users\willh\.mcp-servers\{server-name}\`
**Examples:**
- `coderef-context/` → Provides 10 code analysis tools
- `coderef-workflow/` → Provides 23 planning/orchestration tools
- `coderef-docs/` → Provides 11 documentation tools
- `coderef-personas/` → Provides persona management

**Key Point:** These are PYTHON SERVERS, not configuration files.

### 2️⃣ MCP.JSON FILES (Configuration)
**What:** Tells Claude Code where to find MCP servers
**Where:**
- **GLOBAL:** `C:\Users\willh\.mcp.json` ✅ (THIS IS WHERE YOU CONFIGURE SERVERS)
- **LOCAL:** ❌ Each server does NOT have its own mcp.json

**Content:**
```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-context/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-context"
    },
    "coderef-workflow": { ... },
    "coderef-docs": { ... },
    "coderef-personas": { ... }
  }
}
```

**Key Point:** ONE mcp.json in your home directory tells Claude where all 4 servers are.

### 3️⃣ SLASH COMMANDS (User Interface)
**What:** Prompts you type as `/stub`, `/create-workorder`, etc.
**Where:** `C:\Users\willh\.claude\commands\` ✅ (GLOBAL)
**Examples:**
- `/stub` → calls stub.md command
- `/create-workorder` → calls create-workorder.md command
- `/execute-plan` → calls execute-plan.md command

**Key Point:** These are MARKDOWN FILES that expand to full prompts. They're like shortcuts.

---

## The Flow: From Command to Tool

```
USER TYPES:
/create-workorder feature-name
    ↓
Claude Code reads:
~/.claude/commands/create-workorder.md
    ↓
Command expansion:
"Create a workorder for feature-name by calling gather_context tool"
    ↓
Claude Code looks in ~/.mcp.json:
"gather_context tool? That's in coderef-workflow server"
    ↓
~/.mcp.json points to:
C:\Users\willh\.mcp-servers\coderef-workflow\server.py
    ↓
Python server starts and provides gather_context tool
    ↓
Tool executes with your arguments
    ↓
Result returned to Claude Code
    ↓
Output to user
```

---

## Critical Clarification: What Goes Where

### ✅ CORRECT ARCHITECTURE

```
YOUR HOME DIRECTORY (~)
├── .mcp.json                               ← GLOBAL CONFIG (Where are the servers?)
├── .claude/
│   └── commands/                           ← GLOBAL COMMANDS (What slash commands exist?)
│       ├── stub.md
│       ├── create-workorder.md
│       ├── execute-plan.md
│       └── ... (26+ more commands)
│
└── .mcp-servers/                           ← MCP SERVER IMPLEMENTATIONS
    ├── coderef-context/
    │   ├── server.py                       ← Provides 10 tools
    │   ├── tool_handlers.py
    │   └── ... (Python implementation)
    │
    ├── coderef-workflow/
    │   ├── server.py                       ← Provides 23 tools
    │   ├── tool_handlers.py
    │   └── ... (Python implementation)
    │
    ├── coderef-docs/
    │   ├── server.py                       ← Provides 11 tools
    │   ├── tool_handlers.py
    │   └── ... (Python implementation)
    │
    └── coderef-personas/
        ├── server.py                       ← Provides persona tools
        ├── personas/
        └── ... (Python implementation)
```

### ❌ WRONG (Don't Do This)

```
❌ Local mcp.json in each server
   coderef-context/mcp.json    ← WRONG
   coderef-workflow/mcp.json   ← WRONG

❌ Commands inside server directories
   coderef-workflow/.claude/commands/   ← WRONG

❌ Per-project configurations
   my-project/.mcp.json        ← WRONG
```

---

## The Actual Files You Have

### ~/.mcp.json (GLOBAL - 49 lines)
**Location:** `C:\Users\willh\.mcp.json`
**Purpose:** Tells Claude Code where to find the 4 MCP servers
**Content:**
```json
{
  "mcpServers": {
    "coderef-personas": { /* points to coderef-personas/server.py */ },
    "coderef-context": { /* points to coderef-context/server.py */ },
    "coderef-docs": { /* points to coderef-docs/server.py */ },
    "coderef-workflow": { /* points to coderef-workflow/server.py */ }
  }
}
```

**Status:** ✅ CORRECT and COMPLETE

### ~/.claude/commands/ (GLOBAL - 26+ files)
**Location:** `C:\Users\willh\.claude\commands\`
**Purpose:** Provides slash commands users can type
**Examples:**
- `stub.md` → /stub command
- `create-workorder.md` → /create-workorder command
- `execute-plan.md` → /execute-plan command
- etc.

**Status:** ✅ CORRECT and COMPLETE

### Server Directories (Implementation Only)
**Location:** `C:\Users\willh\.mcp-servers\{server-name}\`
**Contains:**
- `server.py` → Entry point that provides tools
- `tool_handlers.py` → Implementation of tools
- `generators/` → Supporting code
- etc.

**Status:** ✅ CORRECT (NO local mcp.json, NO local commands)

---

## Understanding MCP.json in Detail

### What Is in ~/.mcp.json?

```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",                    // Run Python
      "args": [                               // With these arguments:
        "C:/Users/willh/.mcp-servers/coderef-context/server.py"  // Run this file
      ],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-context",  // From this directory
      "env": {                                // Environment variables
        "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
      },
      "description": "...",                   // For documentation
      "tools": [                              // Tools this server provides
        "coderef_scan",
        "coderef_query",
        "coderef_impact",
        // ... 7 more tools
      ]
    }
    // ... 3 more servers
  }
}
```

### What Does This Mean?

**When Claude Code needs `coderef_scan` tool:**
1. Claude Code reads ~/.mcp.json
2. Finds "coderef_scan" is in "coderef-context" server
3. Looks up "coderef-context" server config
4. Runs: `python C:/Users/willh/.mcp-servers/coderef-context/server.py`
5. Server registers its tools (including coderef_scan)
6. Tool is available to Claude Code

---

## Where Do Tools Come From?

### Tools Are Defined Inside Servers

**Example: coderef_scan tool**

Location: `C:\Users\willh\.mcp-servers\coderef-context\server.py`

```python
@app.call_tool()
async def handle_tools(name: str, arguments: dict):
    if name == "coderef_scan":
        # Implementation here
        return [TextContent(type="text", text=result)]
```

**Key Points:**
- ✅ Tools are defined INSIDE the server.py file
- ✅ Server registers them with MCP protocol
- ✅ Claude Code can call them via MCP
- ❌ Tools are NOT in mcp.json (mcp.json just lists them for documentation)

### Where Do Slash Commands Come From?

**Example: /stub command**

Location: `C:\Users\willh\.claude\commands\stub.md`

```markdown
Log a quick idea as a stub for future feature work...

## Step 1: Ask User for Feature Details
...
```

**Key Points:**
- ✅ Commands are markdown files in ~/.claude/commands/
- ✅ Each file name becomes a slash command (/stub, /create-workorder, etc.)
- ✅ Contents are instructions for Claude Code to follow
- ✅ Commands can call MCP tools (like gather_context from coderef-workflow)

---

## The Relationship Between MCP.json and Commands

### How /create-workorder Works

**File:** `~/.claude/commands/create-workorder.md`
**Content:**
```markdown
Create a workorder that gathers context, analyzes the project, and creates a plan.

Use the gather_context tool to collect feature requirements...
```

**When you type:** `/create-workorder my-feature`

**Process:**
1. Claude Code reads ~/.claude/commands/create-workorder.md
2. Sees: "Use the gather_context tool"
3. Looks in ~/.mcp.json for "gather_context" tool
4. Finds it's in "coderef-workflow" server
5. Launches coderef-workflow server
6. Calls gather_context tool with arguments
7. Tool executes and returns results

---

## Common Confusion Points (Resolved)

### ❓ "Should I create local mcp.json files?"
**Answer:** NO. Keep ~/.mcp.json only (global).
**Why:** Single source of truth. All servers defined in one place.

### ❓ "Where do tools go?"
**Answer:** Inside server.py (not in mcp.json).
**mcp.json:** Just lists them for documentation.
**server.py:** Actually implements them.

### ❓ "Where do commands go?"
**Answer:** In ~/.claude/commands/ (global).
**One:** /stub → stub.md
**Two:** /create-workorder → create-workorder.md
**Three:** /execute-plan → execute-plan.md

### ❓ "Can I have local project-specific commands?"
**Answer:** No (not recommended). Keep all commands global.
**Why:** Ensures consistent behavior across all projects.
**Better:** Use context files (context.json, plan.json) for project-specific data.

### ❓ "What if I need different tools for different projects?"
**Answer:** Don't create separate servers. Use tool arguments instead.
**How:** Pass project_path as argument to tools.
**Example:** `gather_context(project_path="/my/project")`

### ❓ "Should coderef-context have local config?"
**Answer:** Only environment variables (in ~/.mcp.json).
**Current:** CODEREF_CLI_PATH is in ~/.mcp.json ✅
**Correct:** Don't create coderef-context/mcp.json

---

## Best Practices

### ✅ DO

1. **Keep ~/.mcp.json as single source of truth**
   - All 4 servers defined there
   - One place to manage all configurations

2. **Keep commands in ~/.claude/commands/ global**
   - Consistent /stub, /create-workorder everywhere
   - No per-project command variations

3. **Put project-specific data in artifacts**
   - context.json (in coderef/workorder/)
   - plan.json (in coderef/workorder/)
   - DELIVERABLES.md (in coderef/workorder/)

4. **Use environment variables for paths**
   - CODEREF_CLI_PATH ✅
   - Other tool configs in ~/.mcp.json "env" section

5. **Document tools in mcp.json metadata**
   - coderef-context does this well
   - Consider doing it for other servers

### ❌ DON'T

1. ❌ Create local mcp.json files
   - Don't: coderef-workflow/mcp.json
   - Don't: coderef-context/mcp.json

2. ❌ Create local command directories
   - Don't: coderef-workflow/.claude/commands/
   - Don't: Each project's .claude/commands/

3. ❌ Hardcode paths in servers
   - Don't: server.py has C:\Users\willh\...
   - Do: Use environment variables in ~/.mcp.json

4. ❌ Store project data in server directories
   - Don't: context.json in coderef-context/
   - Do: context.json in coderef/workorder/{feature}/

5. ❌ Create multiple mcp.json files
   - Don't: ~/.mcp.json AND coderef/mcp.json
   - Do: ONE ~/.mcp.json only

---

## Visual Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ USER TYPES: /create-workorder my-feature                     │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Claude Code reads:                                            │
│ ~/.claude/commands/create-workorder.md                       │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Command says: "Call gather_context tool with my-feature"    │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Claude Code checks ~/.mcp.json:                             │
│ "Where is gather_context tool?"                             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ ~/.mcp.json says:                                            │
│ "gather_context is in coderef-workflow server"              │
│ Launch: python ~/.mcp-servers/coderef-workflow/server.py    │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ coderef-workflow/server.py runs                             │
│ Registers all 23 tools including gather_context            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Claude Code calls: gather_context(project_path, feature_...) │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Tool executes, creates context.json in:                     │
│ coderef/workorder/my-feature/context.json                   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Result returned to Claude Code and displayed to user        │
└──────────────────────────────────────────────────────────────┘
```

---

## Your Current Configuration (Analysis)

### ✅ What You Have Right

```
~/.mcp.json                          ✅ CORRECT
  - Defines all 4 servers            ✅ CORRECT
  - Proper entry points              ✅ CORRECT
  - Environment variable for CLI     ✅ CORRECT

~/.claude/commands/                  ✅ CORRECT
  - /stub command                    ✅ CORRECT
  - /create-workorder command        ✅ CORRECT
  - 26+ other commands               ✅ CORRECT

~/.mcp-servers/
  - coderef-context/ (server impl)   ✅ CORRECT
  - coderef-workflow/ (server impl)  ✅ CORRECT
  - coderef-docs/ (server impl)      ✅ CORRECT
  - coderef-personas/ (server impl)  ✅ CORRECT

coderef/ (global artifacts)          ✅ CORRECT
  - coderef/workorder/               ✅ CORRECT
  - coderef/archived/                ✅ CORRECT
  - coderef/standards/               ✅ CORRECT
```

### ⚠️ What Could Be Better

```
No local mcp.json files              ✅ CORRECT (none should exist)
mcp.json metadata inconsistent       ⚠️ FIX: Add metadata to all servers
```

---

## Summary Table

| Item | Type | Location | Quantity | Purpose |
|------|------|----------|----------|---------|
| **mcp.json** | Configuration | `~/.mcp.json` | 1 | Defines where servers are |
| **MCP Servers** | Python | `~/.mcp-servers/{name}/` | 4 | Provide tools |
| **Slash Commands** | Markdown | `~/.claude/commands/` | 26+ | User interface |
| **Tools** | Python code | Inside `server.py` | 49+ | Actual functionality |
| **Artifacts** | JSON | `coderef/workorder/` | Many | Project data |

---

## The Key Insight

Think of it this way:

```
~/.mcp.json
  ↑
  └─ "Where are the MCP servers?"
     Answer: ~/.mcp-servers/coderef-context, ~/.mcp-servers/coderef-workflow, etc.

~/.claude/commands/
  ↑
  └─ "What commands can I type?"
     Answer: /stub, /create-workorder, /execute-plan, etc.

~/.mcp-servers/{server-name}/server.py
  ↑
  └─ "What tools can I call?"
     Answer: gather_context, create_plan, execute_plan, etc. (specific to each server)

coderef/workorder/{feature-name}/
  ↑
  └─ "Where does my project data go?"
     Answer: context.json, plan.json, DELIVERABLES.md, etc.
```

---

## Final Clarity

### There Are No Local mcp.json Files
- ✅ ~/.mcp.json is the ONE global file
- ❌ Do not create coderef-context/mcp.json
- ❌ Do not create coderef-workflow/mcp.json
- ✅ This is intentional and correct

### There Is ONE Commands Directory
- ✅ ~/.claude/commands/ is the ONE global location
- ❌ Do not create per-server command directories
- ❌ Do not create per-project command directories
- ✅ All commands are global

### Servers Provide Tools
- ✅ coderef-context server.py defines coderef_scan, coderef_query, etc.
- ✅ coderef-workflow server.py defines gather_context, create_plan, etc.
- ❌ Tools are not in mcp.json (mcp.json just lists them)
- ✅ mcp.json is configuration, not implementation

---

**You are NOT confused - this IS confusing! But now it should be clear.** ✅

**Bottom Line:** One global mcp.json, one global commands directory, and 4 independent server implementations. Simple and clean.

