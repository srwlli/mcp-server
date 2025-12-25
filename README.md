# CodeRef Ecosystem - AI-Native Code Intelligence & Feature Lifecycle Management

**Version:** 1.0.0 | **Status:** ✅ Production | **Last Updated:** 2025-12-25

---

## What This Ecosystem Does

**CodeRef** is a complete system that enables AI agents to plan, understand, implement, and document software features safely and efficiently. It solves the "agent blind coding" problem by providing code intelligence, semantic context, and structured planning throughout the entire feature lifecycle.

### Core Problem

- ❌ **Before:** Agents generate code without knowing dependencies → runtime failures, breaking changes, regressions
- ✅ **After:** Agents get complete context (dependencies, impact, tests, risks, architecture) → safe, confident implementations

---

## System Architecture

The ecosystem consists of 4 specialized MCP servers that work together:

```
Input: Feature Idea
    ↓
coderef-workflow (Planning)
    ├─ Gathers context (requirements, constraints)
    ├─ Analyzes project (code intelligence from coderef-context)
    ├─ Creates plan (10-section JSON with tasks)
    └─ Validates plan (quality scoring)
    ↓
Agent + Personas (Implementation)
    ├─ Uses expert personas for domain knowledge
    ├─ Queries coderef-context for code intelligence
    ├─ Implements features with dependency context
    └─ Updates DELIVERABLES.md with progress
    ↓
coderef-docs (Documentation)
    ├─ Records changes (auto-detects git diffs)
    ├─ Generates foundation docs (README, ARCHITECTURE, etc)
    ├─ Updates CHANGELOG (with workorder tracking)
    └─ Archives feature (for historical reference)
    ↓
Output: Complete, documented, safe feature
```

---

## The 4 MCP Servers

| Server | Purpose | Key Tools | Location |
|--------|---------|-----------|----------|
| **coderef-context** | Code Intelligence | scan, query, impact, complexity, patterns, coverage, drift | Python wrapper for @coderef/core |
| **coderef-workflow** | Planning & Orchestration | gather_context, analyze, create_plan, validate, execute, verify, archive | Feature lifecycle management |
| **coderef-docs** | Documentation | generate_foundation_docs, quickref, record_changes, establish_standards, audit, check_consistency | Generate all project docs |
| **coderef-personas** | Expert Agents | use_persona, list_personas, create_custom_persona | 9 domain experts (Lloyd, Ava, Marcus, Quinn, Taylor, Devon, + 3 more) |

### How They Work Together

**1. Planning Phase** (coderef-workflow)
```
/create-workorder → Gathers context + Analyzes project + Creates plan
                 ↓ Uses coderef-context for code intelligence
                 → Outputs: plan.json (10-section structure)
```

**2. Intelligence Phase** (coderef-context)
```
Agents query: "What will break if I change this?"
             ↓
coderef-context wraps @coderef/core CLI
             ↓
Returns: Dependencies, impact radius, affected files, risk level
```

**3. Implementation Phase** (Agent + Personas)
```
Agent executes plan tasks
    ├─ Uses Ava for frontend work (CSS, React, accessibility)
    ├─ Uses Marcus for backend work (API, database, auth)
    ├─ Uses Quinn for testing (test generation, coverage)
    └─ Calls coderef-context for code context
```

**4. Documentation Phase** (coderef-docs)
```
After implementation:
    ├─ /record-changes → Auto-detects git diffs → Updates CHANGELOG
    ├─ /generate-docs → Creates README, ARCHITECTURE, SCHEMA
    └─ /archive-feature → Moves to coderef/archived/ for reference
```

---

## Complete Feature Lifecycle

```
PLAN (5-10 min)
├─ /create-workorder
├─ Gathers requirements
├─ Analyzes project structure
├─ Creates implementation plan
└─ Output: coderef/workorder/{feature}/plan.json

EXECUTE (varies)
├─ /execute-plan → TodoWrite task list
├─ Agent works through tasks using personas + code context
├─ Updates task status as progress
└─ Output: Code implementation + DELIVERABLES.md

DOCUMENT (2-5 min)
├─ /update-deliverables → Captures git metrics (LOC, commits, time)
├─ /record-changes → Smart changelog recording
├─ /update-docs → Bumps version, updates README/CHANGELOG
└─ Output: Updated documentation

ARCHIVE (1 min)
├─ /archive-feature
├─ Move to coderef/archived/
└─ Update archive index

Total: Feature from idea → documented & archived in ~1-2 hours
```

---

## Key Concepts

### Workorder System
**Format:** `WO-{FEATURE}-{CATEGORY}-###`

Example: `WO-AUTH-SYSTEM-001`
- Tracked in `coderef/workorder-log.txt` (audit trail)
- Stored in plan.json META_DOCUMENTATION
- Enables multi-agent work with unique IDs per agent

### Plan.json Structure
**10 sections** covering everything from discovery to success criteria:

1. META_DOCUMENTATION (project info, version, workorder_id)
2. 0_PREPARATION (discovery, analysis, existing patterns)
3. 1_EXECUTIVE_SUMMARY (what & why)
4. 2_RISK_ASSESSMENT (breaking changes, security, performance)
5. 3_CURRENT_STATE_ANALYSIS (existing code, architecture)
6. 4_KEY_FEATURES (requirements)
7. 5_TASK_ID_SYSTEM (task naming conventions)
8. 6_IMPLEMENTATION_PHASES (phased breakdown)
9. 7_TESTING_STRATEGY (test plan)
10. 8_SUCCESS_CRITERIA (completion verification)

### POWER Framework
All documentation follows **POWER** for consistency:
- **P**urpose - Why this exists
- **O**verview - What it covers
- **W**hat/Why/When - Detailed content
- **E**xamples - Concrete illustrations
- **R**eferences - Related docs

---

## Getting Started

### Installation
```bash
# All 4 MCP servers pre-installed in .mcp-servers/
# Verify configuration in ~/.mcp.json

# Test connection (in any project)
/stub                          # Quick idea capture
/create-workorder              # Full planning workflow
/generate-docs                 # Generate project docs
```

### Common Workflows

**Capture an idea:**
```
/stub
→ Feature name: "dark-mode-toggle"
→ Description: "Add dark mode theme toggle to UI"
→ stub.json saved to: C:\Users\willh\Desktop\assistant\coderef\working\{feature}/
```

**Plan a feature:**
```
/create-workorder
→ Gathers context (interactive)
→ Analyzes project (with code intelligence)
→ Creates & validates plan
→ Output: coderef/workorder/{feature}/plan.json
```

**Implement with help:**
```
/execute-plan
→ Generate TodoWrite task list
→ Agent works through tasks
→ Uses personas for domain expertise
→ Calls coderef-context for code context
```

**Record completion:**
```
/record-changes
→ Auto-detects git changes
→ Suggests change_type (feature/fix/breaking)
→ Updates CHANGELOG.json + README version
```

---

## Directory Structure

```
.mcp-servers/                                # All MCP servers
├── coderef-context/                        # Code intelligence (Python)
│   ├── server.py                           # Wraps @coderef/core CLI
│   └── README.md                           # Details
├── coderef-workflow/                       # Planning (Python)
│   ├── generators/                         # plan.json, analysis generation
│   ├── .claude/commands/                   # 26 slash commands
│   └── CLAUDE.md                           # Architecture
├── coderef-docs/                           # Documentation (Python)
│   ├── generators/                         # doc generation
│   ├── templates/power/                    # POWER framework templates
│   └── .claude/commands/                   # 26 slash commands
├── coderef-personas/                       # Expert personas (Python)
│   ├── personas/base/                      # 9 personas
│   └── .claude/commands/                   # Persona activation
├── CLAUDEMD-TEMPLATE.json                  # Universal doc template
├── coderef/                                # Global artifacts
│   ├── workorder/                          # Active features
│   ├── archived/                           # Completed features
│   └── workorder-log.txt                   # Audit trail
└── README.md                               # This file
```

---

## Design Philosophy

**1. Separation of Concerns**
- coderef-context = Code intelligence ONLY
- coderef-workflow = Planning & orchestration ONLY
- coderef-docs = Documentation ONLY
- coderef-personas = Expertise & behavior ONLY

**2. Agent-First Design**
- Tools designed for AI-to-AI communication
- No manual interactive forms
- Structured JSON throughout
- Complete context provided upfront

**3. Safety & Confidence**
- Full dependency context before implementation
- Impact analysis before refactoring
- Validation at each stage (plan scoring, agent verification)
- Complete audit trails

**4. Lean & Efficient**
- 530-600 line CLAUDE.md per server (using CLAUDEMD-TEMPLATE.json)
- No repetition (link instead)
- Version history trimmed to last 2 versions
- One source of truth per concern

---

## Resources

- **[coderef-context/README.md](coderef-context/README.md)** - Code intelligence details
- **[coderef-workflow/CLAUDE.md](coderef-workflow/CLAUDE.md)** - Planning architecture
- **[coderef-docs/CLAUDE.md](coderef-docs/CLAUDE.md)** - Documentation system
- **[coderef-personas/CLAUDE.md](coderef-personas/CLAUDE.md)** - Persona system
- **[CLAUDEMD-TEMPLATE.json](CLAUDEMD-TEMPLATE.json)** - Documentation template
- **[coderef-system](../Desktop/projects/coderef-system/)** - TypeScript @coderef/core

---

**Maintained by:** willh, Claude Code AI

**System Status:** ✅ Production Ready - All 4 servers operational, full feature lifecycle tested and working