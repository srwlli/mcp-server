# Configuration Architecture - Visual Guide

## The Mental Model (Correct!)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    CLAUDE CODE (AI)                     ┃
┃                                                         ┃
┃  "I need to gather context. Where can I get that?"    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              ~/.mcp.json (CONFIGURATION)               ┃
┃                                                         ┃
┃  "gather_context tool? Check coderef-workflow"        ┃
┃                                                         ┃
┃  coderef-workflow = python ~/.mcp-servers/...          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           ~/.mcp-servers/coderef-workflow/             ┃
┃                    server.py                           ┃
┃                                                         ┃
┃  Registers tools:                                      ┃
┃  - gather_context ✓                                    ┃
┃  - create_plan                                         ┃
┃  - execute_plan                                        ┃
┃  - ... 20 more                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           gather_context tool executes                 ┃
┃                                                         ┃
┃  Creates: coderef/workorder/{feature}/context.json    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## The Three Layers (Keep Separate!)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: CONFIGURATION                                      │
│  ~~~~~~~~~~~~~~~~~~~~~~~~~                                   │
│                                                              │
│  ~/.mcp.json                                                 │
│  └─ What servers exist?                                      │
│  └─ Where are they located?                                  │
│  └─ What tools do they provide? (metadata)                   │
│                                                              │
│  This is a REGISTRY/DIRECTORY                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: INTERFACE (User-Facing Commands)                  │
│  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~              │
│                                                              │
│  ~/.claude/commands/                                         │
│  ├─ stub.md (→ /stub command)                                │
│  ├─ create-workorder.md (→ /create-workorder command)        │
│  └─ ... 24+ more commands                                    │
│                                                              │
│  These are INSTRUCTIONS/SCRIPTS for Claude Code             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: IMPLEMENTATION (Tool Definitions)                  │
│  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~         │
│                                                              │
│  ~/.mcp-servers/{server-name}/server.py                     │
│  ├─ Defines all tools for that server                        │
│  ├─ Each tool has implementation logic                       │
│  └─ Tools are what actually DO the work                      │
│                                                              │
│  These are the ACTUAL FUNCTIONALITY                         │
└─────────────────────────────────────────────────────────────┘
```

---

## The Flow (Step by Step)

```
STEP 1: USER INPUT
┌─────────────────┐
│  /create-workorder my-feature  │
└─────────────────┘
        ↓

STEP 2: LOOKUP COMMAND
┌──────────────────────────────────────────┐
│ Claude Code looks in:                     │
│ ~/.claude/commands/create-workorder.md   │
│                                           │
│ Reads: "Call gather_context tool"         │
└──────────────────────────────────────────┘
        ↓

STEP 3: LOOKUP TOOL
┌──────────────────────────────────────────┐
│ Claude Code checks ~/.mcp.json:           │
│ "Where is gather_context?"                │
│                                           │
│ Answer: coderef-workflow server           │
│ Run: python ~/.mcp-servers/.../server.py │
└──────────────────────────────────────────┘
        ↓

STEP 4: EXECUTE SERVER
┌──────────────────────────────────────────┐
│ Python server starts:                     │
│ ~/.mcp-servers/coderef-workflow/server.py│
│                                           │
│ Registers 23 tools:                       │
│ - gather_context ✓ (this is the one)     │
│ - create_plan                             │
│ - execute_plan                            │
│ - ... 20 more                             │
└──────────────────────────────────────────┘
        ↓

STEP 5: TOOL EXECUTION
┌──────────────────────────────────────────┐
│ gather_context tool executes:             │
│                                           │
│ Input: project_path, feature_name, ...   │
│ Processing: Collect requirements         │
│ Output: context.json created             │
└──────────────────────────────────────────┘
        ↓

STEP 6: RETURN RESULT
┌──────────────────────────────────────────┐
│ Result returned to Claude Code:           │
│ - context.json created ✓                 │
│ - Workorder ID generated ✓               │
│ - Path: coderef/workorder/my-feature/    │
└──────────────────────────────────────────┘
```

---

## Tool Resolution (The Key Concept)

```
When Claude Code needs a tool, it follows this path:

     ┌─ Check ~/.mcp.json ─┐
     │                     │
     ↓                     ↓
  Tool name in config?   (REGISTRY)
     │ YES
     ↓
  Which server? → coderef-workflow
     │
     ↓
  Where is server? → ~/.mcp-servers/coderef-workflow/
     │
     ↓
  Start: python server.py
     │
     ↓
  Server registers all its tools (23 tools)
     │
     ↓
  Call gather_context tool ✓
     │
     ↓
  Execute implementation
     │
     ↓
  Return result
```

---

## File Relationships (What Points to What)

```
~/.mcp.json
├─ Points to coderef-context server
│  └─ ~/.mcp-servers/coderef-context/server.py
│     └─ Implements 10 tools
│
├─ Points to coderef-workflow server
│  └─ ~/.mcp-servers/coderef-workflow/server.py
│     └─ Implements 23 tools
│
├─ Points to coderef-docs server
│  └─ ~/.mcp-servers/coderef-docs/server.py
│     └─ Implements 11 tools
│
└─ Points to coderef-personas server
   └─ ~/.mcp-servers/coderef-personas/server.py
      └─ Implements persona tools


~/.claude/commands/
├─ stub.md
│  └─ Calls tools like gather_context
│
├─ create-workorder.md
│  └─ Calls tools like gather_context, create_plan
│
├─ execute-plan.md
│  └─ Calls tools like execute_plan, update_task_status
│
└─ ... 23+ more commands
   └─ Each calls various tools from the servers above
```

---

## The Wrong Way (vs Correct Way)

### ❌ WRONG: Local mcp.json

```
Wrong structure:
~/.mcp-servers/
├─ coderef-context/
│  ├─ server.py
│  ├─ mcp.json        ← ❌ DON'T DO THIS
│  └─ ...
│
├─ coderef-workflow/
│  ├─ server.py
│  ├─ mcp.json        ← ❌ DON'T DO THIS
│  └─ ...
│
├─ coderef-docs/
│  ├─ server.py
│  ├─ mcp.json        ← ❌ DON'T DO THIS
│  └─ ...
│
└─ coderef-personas/
   ├─ server.py
   ├─ mcp.json        ← ❌ DON'T DO THIS
   └─ ...

Problem:
- 4 different configs (confusing!)
- Which one is the source of truth?
- Server-specific config locks you in
- Hard to manage updates
```

### ✅ CORRECT: Global mcp.json

```
Correct structure:
~/
├─ .mcp.json          ← ✅ ONE FILE (SOURCE OF TRUTH)
│  ├─ coderef-context
│  ├─ coderef-workflow
│  ├─ coderef-docs
│  └─ coderef-personas
│
└─ .mcp-servers/
   ├─ coderef-context/
   │  ├─ server.py
   │  └─ ... (no mcp.json here!)
   │
   ├─ coderef-workflow/
   │  ├─ server.py
   │  └─ ... (no mcp.json here!)
   │
   ├─ coderef-docs/
   │  ├─ server.py
   │  └─ ... (no mcp.json here!)
   │
   └─ coderef-personas/
      ├─ server.py
      └─ ... (no mcp.json here!)

Benefits:
- Single source of truth
- Easy to manage
- Clear what's configured
- All servers treated equally
```

---

## Information Architecture (What Goes Where)

```
┌─────────────────────────────────────────────────────────────┐
│                     GLOBAL (Home Directory)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ~/.mcp.json → WHERE SERVERS ARE?                          │
│  │  (Configuration: Server locations + environment vars)   │
│  │                                                          │
│  └─ "gather_context tool? → Look in coderef-workflow"      │
│                                                              │
│  ~/.claude/commands/ → WHAT COMMANDS EXIST?                │
│  │  (User Interface: /stub, /create-workorder, etc.)       │
│  │                                                          │
│  └─ /stub → stub.md (markdown instructions)                │
│                                                              │
│  coderef/ → PROJECT DATA                                    │
│  │  (Artifacts that survive across sessions)               │
│  │                                                          │
│  └─ workorder/my-feature/context.json                      │
│  └─ workorder/my-feature/plan.json                         │
│  └─ archived/completed-feature/                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            IMPLEMENTATION (Server Directories)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ~/.mcp-servers/ → SERVER IMPLEMENTATIONS                  │
│  │                                                          │
│  ├─ coderef-context/ → HOW DOES IT WORK? (Python code)   │
│  │  └─ server.py: Defines 10 tools                         │
│  │                                                          │
│  ├─ coderef-workflow/ → HOW DOES IT WORK? (Python code)  │
│  │  └─ server.py: Defines 23 tools                         │
│  │                                                          │
│  ├─ coderef-docs/ → HOW DOES IT WORK? (Python code)      │
│  │  └─ server.py: Defines 11 tools                         │
│  │                                                          │
│  └─ coderef-personas/ → HOW DOES IT WORK? (Python code)  │
│     └─ server.py: Defines persona tools                    │
│                                                              │
│  (NOTE: No mcp.json files here! Implementation only!)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Decision Tree (Where Should This Go?)

```
Question: I have a file/config. Where should it go?

                        START
                          ↓
                  Is it mcp.json?
                    /         \
                  YES          NO
                   ↓            ↓
              ~/.mcp.json    Is it a /command?
                 (1 file)      /        \
                           YES          NO
                            ↓            ↓
                    ~/.claude/    Is it tool code?
                    commands/      /        \
                   (26+ files)   YES        NO
                                  ↓          ↓
                          ~/.mcp-servers/  Is it project
                          {server}/        data?
                          server.py         /        \
                                         YES        NO
                                          ↓          ↓
                                    coderef/    NOT SURE?
                                    workorder/  Probably:
                                    {feature}/  ~/.mcp-servers/
                                               or coderef/
```

---

## Checklist: Is Your Config Correct?

```
✅ ONE ~/.mcp.json file exists?
   Location: C:\Users\willh\.mcp.json
   Count: 1 file

✅ NO local mcp.json in server directories?
   NOT in: C:\Users\willh\.mcp-servers\coderef-context\mcp.json
   NOT in: C:\Users\willh\.mcp-servers\coderef-workflow\mcp.json
   NOT in: C:\Users\willh\.mcp-servers\coderef-docs\mcp.json
   NOT in: C:\Users\willh\.mcp-servers\coderef-personas\mcp.json

✅ ~/.claude/commands/ has all commands?
   Location: C:\Users\willh\.claude\commands\
   Count: 26+ files

✅ Server implementations in ~/.mcp-servers/?
   Location: C:\Users\willh\.mcp-servers\{server-name}\
   Count: 4 directories

✅ Project data in coderef/?
   Location: C:\Users\willh\coderef\
   Subdirs: workorder/, archived/, standards/

If all checkboxes ✅, your configuration is CORRECT!
```

---

**Key Takeaway:** Think of it as a REGISTRY (mcp.json) + INTERFACE (commands) + IMPLEMENTATION (servers). Keep them separate!

