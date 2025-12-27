# CodeRef Ecosystem - Configuration Guides Index

**Created:** December 26, 2025
**Last Updated:** December 26, 2025
**Purpose:** Central index of all configuration architecture documentation

---

## Overview

This directory contains comprehensive guides explaining how MCP servers, tools, commands, and configuration work together in the CodeRef Ecosystem.

**Problem Solved:** Confusion about local vs global configuration, where tools/commands go, and how ~/.mcp.json relates to everything else.

**Solution:** Three complementary guides at different levels of detail, with visual diagrams and practical examples.

---

## Available Guides

### 1. 📖 CONFIGURATION_ARCHITECTURE_GUIDE.md
**Timestamp:** 2025-12-26T00:00:00Z
**Size:** 1,200+ lines
**Best For:** Complete understanding and reference

**Contains:**
- Detailed explanation of MCP servers, tools, and configuration
- Clear distinction between 3 different things (mcp.json, commands, servers)
- Best practices and anti-patterns
- Real examples from your current setup
- 10 common confusion points with answers
- Visual flow diagrams
- Directory structure (correct vs wrong)
- Production recommendations

**Read This When:** You want to deeply understand the architecture or troubleshoot configuration issues.

---

### 2. ⚡ QUICK_CONFIG_REFERENCE.md
**Timestamp:** 2025-12-26T00:00:00Z
**Size:** 200 lines
**Best For:** Quick lookups and decision-making

**Contains:**
- One-page summary of three types of things
- Quick answers to 4 key questions
- Decision matrix for file placement
- Key rules (DO and DON'T)
- Your current setup summary
- If-you're-still-confused troubleshooting

**Read This When:** You need a quick answer or reminder.

---

### 3. 🎨 CONFIGURATION_VISUAL_GUIDE.md
**Timestamp:** 2025-12-26T00:00:00Z
**Size:** 400+ lines
**Best For:** Visual learners and conceptual understanding

**Contains:**
- ASCII art diagrams and flowcharts
- Step-by-step execution flow with boxes and arrows
- Tool resolution path (how Claude finds tools)
- File relationship diagrams
- Information architecture visualization
- Decision tree for file placement
- Configuration checklist
- Right way vs wrong way with examples

**Read This When:** You're a visual learner or want to see how everything connects.

---

## Quick Navigation

### I'm Confused About...

**Local vs Global Configuration?**
→ Read: QUICK_CONFIG_REFERENCE.md (2 min)
→ Then: CONFIGURATION_ARCHITECTURE_GUIDE.md section "There Are No Local mcp.json Files"

**Where Tools Go?**
→ Read: QUICK_CONFIG_REFERENCE.md "Where do I put tools?"
→ Then: CONFIGURATION_VISUAL_GUIDE.md "File Relationships"

**Where Commands Go?**
→ Read: QUICK_CONFIG_REFERENCE.md "Where do I put commands?"
→ Then: CONFIGURATION_ARCHITECTURE_GUIDE.md "Understanding MCP.json in Detail"

**How Everything Works Together?**
→ Read: CONFIGURATION_VISUAL_GUIDE.md "The Flow (Step by Step)"
→ Then: CONFIGURATION_ARCHITECTURE_GUIDE.md "Integration Points"

**If I Should Create/Modify Something?**
→ Read: CONFIGURATION_VISUAL_GUIDE.md "Decision Tree"
→ Then: CONFIGURATION_ARCHITECTURE_GUIDE.md "Best Practices"

---

## The Three Things (Quick Reference)

### Thing 1: mcp.json (Configuration)
```
Location:  ~/.mcp.json  (GLOBAL - ONE FILE)
What:      Tells Claude where the 4 MCP servers are
Content:   4 server definitions
Rules:     ✅ Keep global   ❌ Never create local ones
```

### Thing 2: Slash Commands (User Interface)
```
Location:  ~/.claude/commands/  (GLOBAL - 26+ FILES)
What:      Markdown files that define /stub, /create-workorder, etc.
Content:   Instructions for Claude Code
Rules:     ✅ Keep global   ❌ Never create per-project ones
```

### Thing 3: MCP Servers (Implementation)
```
Location:  ~/.mcp-servers/{server-name}/  (4 DIRECTORIES)
What:      Python servers that provide tools
Content:   server.py defines the tools
Rules:     ✅ Keep implementation   ❌ Never add mcp.json here
```

---

## Your Current Setup (Status)

**File Locations Verified:**
- ✅ `C:\Users\willh\.mcp.json` - GLOBAL CONFIG (1 file)
- ✅ `C:\Users\willh\.claude\commands\` - GLOBAL COMMANDS (26+ files)
- ✅ `C:\Users\willh\.mcp-servers\coderef-context\` - SERVER IMPL (no local mcp.json)
- ✅ `C:\Users\willh\.mcp-servers\coderef-workflow\` - SERVER IMPL (no local mcp.json)
- ✅ `C:\Users\willh\.mcp-servers\coderef-docs\` - SERVER IMPL (no local mcp.json)
- ✅ `C:\Users\willh\.mcp-servers\coderef-personas\` - SERVER IMPL (no local mcp.json)

**Verdict:** Your configuration is CORRECT! ✅

---

## Key Insights

### Insight 1: Single Source of Truth
```
~/.mcp.json is your registry/directory of servers.
It tells Claude Code:
  "When you need gather_context → look in coderef-workflow"
  "When you need record_changes → look in coderef-docs"
  "When you need coderef_scan → look in coderef-context"
```

### Insight 2: Tools Are Inside Servers
```
~/.mcp.json doesn't define tools - it just lists them!
Real definition is in:
  ~/.mcp-servers/coderef-workflow/server.py
  ├─ Implements gather_context
  ├─ Implements create_plan
  └─ ... 21 more tools
```

### Insight 3: Commands Bridge Configuration and Tools
```
~/.claude/commands/create-workorder.md says:
  "Call gather_context tool"

Claude Code then:
  1. Checks ~/.mcp.json for gather_context location
  2. Launches the server from ~/.mcp-servers/
  3. Executes the tool
```

---

## Common Questions Answered

### ❓ "Should I create coderef-workflow/mcp.json?"
**No!** Keep everything in global ~/.mcp.json only.

**Why?** Single source of truth. All servers configured in one place.

---

### ❓ "Can I create project-specific .claude/commands/?"
**No!** Keep ~/.claude/commands/ global.

**Why?** Commands should work from any project. Use context.json for project-specific data.

---

### ❓ "Where do tools get defined?"
**Inside server.py files** in ~/.mcp-servers/

**Not in mcp.json** - mcp.json just lists them for documentation.

---

### ❓ "How does Claude Code find tools?"
1. User types `/create-workorder`
2. Claude reads ~/.claude/commands/create-workorder.md
3. Command says "call gather_context tool"
4. Claude checks ~/.mcp.json: "gather_context is in coderef-workflow"
5. Claude launches ~/.mcp-servers/coderef-workflow/server.py
6. Server provides gather_context tool
7. Tool executes

---

### ❓ "What if I need to configure a tool differently?"
**Use environment variables in ~/.mcp.json**

Example (already done):
```json
"coderef-context": {
  "env": {
    "CODEREF_CLI_PATH": "C:/Users/willh/Desktop/projects/coderef-system/packages/cli"
  }
}
```

---

## File Placement Decision Tree

```
Question: I have a file. Where should it go?

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
                   ~/.claude/    Is it tool
                   commands/      implementation?
                  (26+ files)      /        \
                              YES          NO
                               ↓            ↓
                        ~/.mcp-servers/  Is it project
                        {server}/        data?
                        server.py         /        \
                                       YES        NO
                                        ↓          ↓
                                   coderef/    NOT SURE?
                                   workorder/  Ask in guides!
```

---

## Related Documentation

These guides work together with other ecosystem documentation:

**Ecosystem Health & Viability:**
- `ECOSYSTEM_VIABILITY_ASSESSMENT.md` - Is this ecosystem viable? (YES - 8.5/10)
- `ECOSYSTEM_CONSISTENCY_REVIEW.md` - Are servers consistent? (Mostly - minor issues)
- `ECOSYSTEM_QUICK_REFERENCE.md` - Server profiles and comparison

**Other Configuration:**
- `CLAUDE.md` - Root ecosystem overview
- Each server's `CLAUDE.md` - Server-specific documentation

---

## How to Use These Guides

### For Complete Understanding:
1. Start with QUICK_CONFIG_REFERENCE.md (5 min read)
2. Move to CONFIGURATION_VISUAL_GUIDE.md (15 min read)
3. Deep dive into CONFIGURATION_ARCHITECTURE_GUIDE.md (30 min read)
4. Reference as needed

### For Quick Answers:
1. Use QUICK_CONFIG_REFERENCE.md first
2. Cross-reference CONFIGURATION_ARCHITECTURE_GUIDE.md sections

### For Troubleshooting:
1. Check CONFIGURATION_VISUAL_GUIDE.md decision tree
2. Verify against "Your Current Setup" checklist
3. Read relevant section in CONFIGURATION_ARCHITECTURE_GUIDE.md

---

## Document Statistics

| Document | Created | Size | Reading Time | Purpose |
|----------|---------|------|--------------|---------|
| CONFIGURATION_ARCHITECTURE_GUIDE.md | 2025-12-26 | 1,200+ lines | 30-45 min | Complete reference |
| QUICK_CONFIG_REFERENCE.md | 2025-12-26 | 200 lines | 5-10 min | Quick lookup |
| CONFIGURATION_VISUAL_GUIDE.md | 2025-12-26 | 400+ lines | 15-20 min | Visual learning |
| CONFIGURATION_GUIDE_INDEX.md | 2025-12-26 | (this file) | 10 min | Navigation & summary |

**Total Configuration Documentation:** 1,800+ lines
**Total Time to Full Understanding:** 1-1.5 hours

---

## Verification Checklist

Use this to verify your configuration is correct:

```
✅ ~/.mcp.json exists and contains 4 servers?
✅ No local mcp.json in any ~/.mcp-servers/ subdirectory?
✅ ~/.claude/commands/ contains 26+ slash commands?
✅ Each server has server.py (implements tools)?
✅ coderef/ directory has workorder/ and archived/ subdirs?
✅ No per-project mcp.json or commands/ directories?

If ALL checkboxes are ✅, your configuration is CORRECT!
```

---

## Troubleshooting: The 3 Most Common Mistakes

### Mistake 1: Creating Local mcp.json Files
**Wrong:**
```
~/.mcp-servers/coderef-context/mcp.json        ← DON'T DO THIS
```

**Right:**
```
~/.mcp.json                                     ← ONE FILE ONLY
```

**Why?** Single source of truth. All servers configured in one place.

---

### Mistake 2: Creating Per-Project Command Directories
**Wrong:**
```
my-project/.claude/commands/stub.md             ← DON'T DO THIS
```

**Right:**
```
~/.claude/commands/stub.md                      ← GLOBAL
```

**Why?** Commands are global. Use context.json for project-specific data.

---

### Mistake 3: Putting Tools in mcp.json Instead of server.py
**Wrong:**
```json
{
  "mcpServers": {
    "coderef-workflow": {
      "tools": {                              // ← DON'T DEFINE HERE
        "gather_context": { "implementation": "..." }
      }
    }
  }
}
```

**Right:**
```python
# ~/.mcp-servers/coderef-workflow/server.py
@app.call_tool()
async def handle_tools(name: str, arguments: dict):
    if name == "gather_context":
        # Implementation here
```

**Why?** mcp.json is configuration (where things are), server.py is implementation (how they work).

---

## Quick Reference: The Three Layers

### Layer 1: Configuration (Registry)
```
~/.mcp.json
├─ What servers exist?
├─ Where are they located?
└─ What's their configuration?
```

### Layer 2: Interface (User Commands)
```
~/.claude/commands/
├─ What can the user do? (/stub, /create-workorder, etc.)
├─ How are commands invoked?
└─ What tools do they call?
```

### Layer 3: Implementation (Server Tools)
```
~/.mcp-servers/{server}/server.py
├─ What tools are available?
├─ How do tools work?
└─ What do tools return?
```

---

## Final Thoughts

**You're not confused - this IS confusing!**

The CodeRef configuration system is actually very clean and well-designed, but it uses three different concepts (config files, commands, servers) that are related but separate. That's what causes the confusion.

**Key Insight:** Think of ~/.mcp.json as a DIRECTORY or REGISTRY:
- Like a phone book that says "gather_context tool? Look in coderef-workflow"
- Not like a tool definition file

Once you understand that separation, everything clicks into place.

---

## Get Started Now

1. **Quick understanding:** Read QUICK_CONFIG_REFERENCE.md (5 min)
2. **Visual overview:** Read CONFIGURATION_VISUAL_GUIDE.md (15 min)
3. **Deep dive:** Read CONFIGURATION_ARCHITECTURE_GUIDE.md (30 min)

**Total time to full clarity:** 45-60 minutes

**Your configuration is already correct!** These guides just help you understand why it's correct.

---

## Document Index

All files are in: `C:\Users\willh\.mcp-servers\`

| File | Purpose |
|------|---------|
| CONFIGURATION_ARCHITECTURE_GUIDE.md | Complete reference (1,200+ lines) |
| QUICK_CONFIG_REFERENCE.md | Quick lookup (200 lines) |
| CONFIGURATION_VISUAL_GUIDE.md | Visual diagrams (400+ lines) |
| CONFIGURATION_GUIDE_INDEX.md | This file - navigation & summary |

---

**Created:** December 26, 2025, 00:00:00Z
**Status:** ✅ Complete and verified
**Audience:** Anyone confused about MCP configuration
**Maintained By:** Claude Code AI

