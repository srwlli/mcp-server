# User Guide: coderef-workflow

**Generated:** December 28, 2025
**Author:** Claude Code AI
**Version:** 1.1.0

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [How It Works](#how-it-works)
5. [Getting Started](#getting-started)
6. [Core Workflows](#core-workflows)
7. [Use Cases](#use-cases)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Quick Reference](#quick-reference)
11. [AI Integration Notes](#ai-integration-notes)

---

## Introduction

**coderef-workflow** is an enterprise-grade MCP (Model Context Protocol) server that orchestrates the complete feature development lifecycle for AI agents and human developers. It provides:

- **Structured Planning** - 10-section implementation plans with code intelligence
- **Workorder Tracking** - Complete audit trail with WO-{FEATURE}-### IDs
- **Multi-Agent Coordination** - Parallel execution with conflict prevention
- **Automated Documentation** - README/CHANGELOG/CLAUDE.md updates
- **Feature Archival** - Complete lifecycle from planning to archive

**Key Innovation:** Integrates with **coderef-context** MCP server for AST-based code intelligence, enabling AI agents to plan features with full dependency awareness.

---

## Prerequisites

### Required

| Requirement | Verification Command | Expected Output |
|-------------|---------------------|-----------------|
| **Python 3.10+** | `python --version` | Python 3.10.0 or higher |
| **Git** | `git --version` | git version 2.30+ |
| **Claude Code or MCP Client** | Check application installed | Application running |

### Optional (Recommended)

| Component | Purpose | Verification |
|-----------|---------|--------------|
| **coderef-context** | Code intelligence (AST analysis) | `ls C:\Users\willh\.mcp-servers\coderef-context` |
| **coderef-docs** | Documentation generation | `ls C:\Users\willh\.mcp-servers\coderef-docs` |
| **coderef-personas** | Expert AI agents | `ls C:\Users\willh\.mcp-servers\coderef-personas` |

**Verification:**
```bash
# Check Python version
python --version
→ Expected: Python 3.10.11 (or higher)

# Check Git installed
git --version
→ Expected: git version 2.43.0 (or higher)

# Verify pip
pip --version
→ Expected: pip 23.0+ from Python 3.10+
```

---

## Installation

### Step 1: Install Dependencies

```bash
cd C:\Users\willh\.mcp-servers\coderef-workflow
pip install -e .
```

**Expected Output:**
```
Successfully installed mcp-1.0.0 coderef-workflow-1.1.0
```

**Alternative (using uv):**
```bash
uv sync
→ Expected: Resolved 15 packages in 1.2s
```

### Step 2: Configure MCP

Add to `~/.mcp.json` (global) or `.mcp.json` (project):

```json
{
  "mcpServers": {
    "coderef-workflow": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-workflow/server.py"]
    }
  }
}
```

**Path Note:** Use forward slashes (/) on Windows, not backslashes.

### Step 3: Verify Installation

```bash
# Start MCP server
python server.py
```

**Expected Output:**
```
INFO: MCP server starting - version=1.1.0 mcp_version=1.0
INFO: Server listening on stdio
```

**In Claude Code:**
```bash
/create-workorder
```

**Expected:** Interactive prompts asking for feature name.

✅ **Installation Successful!**

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code CLI                          │
│                  (MCP Client - User)                        │
└───────────────────┬─────────────────────────────────────────┘
                    │ MCP Protocol (JSON-RPC over stdio)
                    ↓
┌─────────────────────────────────────────────────────────────┐
│              coderef-workflow MCP Server                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ server.py (Tool Registration)                       │   │
│  │   ├─ 23 MCP Tools                                   │   │
│  │   └─ Tool Handler Dispatcher                        │   │
│  └───────────┬─────────────────────────────────────────┘   │
│              ↓                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ tool_handlers.py (Processing Logic)                 │   │
│  │   ├─ gather_context                                 │   │
│  │   ├─ create_plan                                    │   │
│  │   ├─ execute_plan                                   │   │
│  │   └─ ... (20 more handlers)                         │   │
│  └───────────┬─────────────────────────────────────────┘   │
│              ↓                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Generators & Analyzers                              │   │
│  │   ├─ plan_generator.py                              │   │
│  │   ├─ analysis_generator.py                          │   │
│  │   ├─ plan_executor.py                               │   │
│  │   └─ planning_analyzer.py                           │   │
│  └───────────┬─────────────────────────────────────────┘   │
└──────────────┼─────────────────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────────────────┐
│              File System (Git Repository)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ coderef/workorder/{feature}/                        │   │
│  │   ├─ context.json                                   │   │
│  │   ├─ analysis.json                                  │   │
│  │   ├─ plan.json                                      │   │
│  │   ├─ DELIVERABLES.md                                │   │
│  │   └─ communication.json (multi-agent)               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
               │ (Optional MCP calls for code intelligence)
               ↓
┌─────────────────────────────────────────────────────────────┐
│            coderef-context MCP Server                       │
│              (AST Analysis, Dependencies)                   │
└─────────────────────────────────────────────────────────────┘
```

### Behind the Scenes

**When you run `/create-workorder`:**

1. **Slash Command Expansion** - Claude Code reads `~/.claude/commands/create-workorder.md` and expands to full prompt
2. **Interactive Prompts** - AI asks questions, collects user input
3. **MCP Tool Calls** - AI calls tools in sequence:
   ```
   gather_context() → analyze_project_for_planning() → create_plan() →
   validate_implementation_plan() → execute_plan() → git commit
   ```
4. **JSON Files Created** - context.json, analysis.json, plan.json saved to `coderef/workorder/{feature}/`
5. **TodoWrite Integration** - Task list displayed in Claude Code CLI
6. **Git Checkpoint** - Pre-execution commit created

**Time Estimate:** 5-10 minutes for complete planning workflow.

---

## Getting Started

### Your First Feature Plan

**Goal:** Create an implementation plan for a dark mode toggle feature.

**Step 1: Navigate to your project**
```bash
cd /path/to/your/project
```

**Step 2: Run create-workorder**
```bash
/create-workorder
```

**Step 3: Answer the interactive prompts**

| Prompt | Your Answer | Example |
|--------|-------------|---------|
| Feature name? | `dark-mode-toggle` | Must be alphanumeric, hyphens, underscores |
| What does it do? | `Toggle between light and dark themes` | Brief description |
| Why is it needed? | `Improve user accessibility` | Primary goal |
| Must-have requirements? | `Theme context, CSS variables, Toggle button` | Comma-separated list |
| Technical constraints? | `Must work with existing CSS framework` | Optional |
| Out of scope? | `Theme customization, Color picker` | Optional |

**Step 4: Wait for plan generation**

Behind the scenes:
- ✅ Context saved to `coderef/workorder/dark-mode-toggle/context.json`
- ✅ Project analyzed (foundation docs, coding standards, tech stack)
- ✅ Plan created with 10 sections, ~50 tasks
- ✅ Plan validated (score: 95/100)
- ✅ TodoWrite task list generated
- ✅ Git commit created

**Step 5: Review the plan**

```bash
# View plan structure
cat coderef/workorder/dark-mode-toggle/plan.json | grep -A 3 "META_DOCUMENTATION"

# Output:
{
  "META_DOCUMENTATION": {
    "version": "1.0.0",
    "workorder_id": "WO-DARK-MODE-TOGGLE-001",
    "feature_name": "dark-mode-toggle",
    "status": "planning"
  }
}
```

**Step 6: View TodoWrite task list (already printed to CLI)**

Example output:
```
**Workorder: WO-DARK-MODE-TOGGLE-001 - dark-mode-toggle**

### Phase 1: Setup & Foundation (5 tasks)
☐ SETUP-001: Create theme context with light/dark state
☐ SETUP-002: Define CSS variables for colors
☐ SETUP-003: Implement theme provider component
...
```

✅ **You're ready to start implementing!**

---

## Core Workflows

### Workflow 1: Complete Feature Lifecycle

**Use when:** Implementing a new feature from scratch.

**Time estimate:** 5-10 min (planning) + variable (implementation) + 2-5 min (documentation)

**Steps:**

1. **Plan** (5-10 min)
   ```bash
   /create-workorder
   ```

2. **Implement** (variable time)
   - Follow TodoWrite task list printed to CLI
   - Mark tasks complete as you go
   - Use code intelligence from coderef-context if available

3. **Document** (2-5 min)
   ```bash
   # Update deliverables with git metrics
   /update-deliverables dark-mode-toggle

   # Update README/CHANGELOG/CLAUDE.md
   /update-docs dark-mode-toggle 1.1.0
   ```

4. **Archive** (1 min)
   ```bash
   /archive-feature dark-mode-toggle
   ```

**Result:** Complete feature with full documentation and audit trail.

---

### Workflow 2: Multi-Agent Parallel Execution

**Use when:** Feature has independent phases that can be parallelized.

**Time estimate:** Same total time, but wall-clock time reduced by ~50-70%.

**Steps:**

1. **Create plan with multi-agent mode**
   ```bash
   /create-workorder
   # → Answer prompts
   # → When asked "Enable multi-agent mode?": Yes
   # → Number of agents: 3
   ```

2. **Assign agents to phases**
   ```bash
   # Agent 1 works on Phase 1 (frontend)
   /assign-agent-task dark-mode-toggle 1

   # Agent 2 works on Phase 2 (backend)
   /assign-agent-task dark-mode-toggle 2

   # Agent 3 works on Phase 3 (tests)
   /assign-agent-task dark-mode-toggle 3
   ```

3. **Track progress**
   ```bash
   /track-agent-status dark-mode-toggle
   ```

   Output shows agent status:
   ```
   Agent 1: IN_PROGRESS (Phase 1: Frontend)
   Agent 2: COMPLETED (Phase 2: Backend)
   Agent 3: PENDING (Phase 3: Tests)
   ```

4. **Verify completion**
   ```bash
   /verify-agent-completion dark-mode-toggle 1
   /verify-agent-completion dark-mode-toggle 2
   /verify-agent-completion dark-mode-toggle 3
   ```

5. **Aggregate metrics**
   ```bash
   /aggregate-agent-deliverables dark-mode-toggle
   ```

**Behind the Scenes:** `communication.json` prevents file conflicts with "forbidden files" lists per agent.

---

### Workflow 3: Risk Assessment Before Refactoring

**Use when:** Making changes to critical code paths.

**Time estimate:** < 1 minute

**Example:**
```bash
# Assess risk of renaming AuthService class
mcp__coderef_workflow__assess_risk({
  "project_path": "/path/to/project",
  "proposed_change": {
    "description": "Rename AuthService to AuthenticationService",
    "change_type": "refactor",
    "files_affected": ["src/auth/service.py"]
  }
})
```

**Output:**
```json
{
  "overall_score": 45,
  "recommendation": "PROCEED_WITH_CAUTION",
  "risk_breakdown": {
    "breaking_changes": {"score": 60, "details": "12 files import AuthService"},
    "security": {"score": 20, "details": "No auth logic changes"},
    "performance": {"score": 10, "details": "Rename only, no perf impact"},
    "maintainability": {"score": 30, "details": "Improves naming clarity"},
    "reversibility": {"score": 15, "details": "Simple git revert"}
  },
  "mitigation": [
    "Use IDE refactor tool for safe rename",
    "Run full test suite after rename",
    "Check for string literal references"
  ]
}
```

**Decision:** Score < 50 means proceed, but follow mitigation steps.

---

## Use Cases

### UC-1: New Feature Implementation

**Scenario:** Add JWT authentication to existing API.

**Workflow:**
```bash
# Step 1: Plan
/create-workorder
# → Feature: "jwt-authentication"
# → Requirements: ["JWT tokens", "Refresh tokens", "Password hashing"]

# Step 2: Review generated plan
cat coderef/workorder/jwt-authentication/plan.json

# Step 3: Implement following TodoWrite checklist
# (Tasks printed to CLI terminal)

# Step 4: Document
/update-deliverables jwt-authentication
/update-docs jwt-authentication 1.1.0

# Step 5: Archive
/archive-feature jwt-authentication
```

**Time:** ~1-2 hours total (10 min planning, 1.5 hours implementation, 5 min documentation)

---

### UC-2: Codebase Refactoring

**Scenario:** Refactor authentication module structure.

**Workflow:**
```bash
# Step 1: Assess risk first
mcp__coderef_workflow__assess_risk({
  "proposed_change": {
    "description": "Split auth module into separate files",
    "change_type": "refactor",
    "files_affected": ["src/auth.py"]
  }
})

# Step 2: If risk acceptable, create plan
/create-workorder
# → Feature: "auth-module-refactor"

# Step 3: Implement with code intelligence
# (coderef-context provides dependency analysis)

# Step 4: Document
/update-docs auth-module-refactor 1.1.1
```

---

### UC-3: Multi-Team Collaboration

**Scenario:** Frontend + Backend + QA teams working on same feature.

**Workflow:**
```bash
# Coordinator creates plan
/create-workorder
# → Multi-agent mode: Yes (3 agents)

# Assign teams
/assign-agent-task user-dashboard 1  # Frontend (Ava)
/assign-agent-task user-dashboard 2  # Backend (Marcus)
/assign-agent-task user-dashboard 3  # QA (Quinn)

# Each team implements their phase independently
# communication.json prevents file conflicts

# Track progress
/track-agent-status user-dashboard

# Verify and aggregate
/verify-agent-completion user-dashboard 1
/verify-agent-completion user-dashboard 2
/verify-agent-completion user-dashboard 3
/aggregate-agent-deliverables user-dashboard
```

---

## Best Practices

### ✅ Do

- **Run `/create-workorder` before starting implementation** - Structured planning saves time
- **Use descriptive feature names** - `user-authentication` not `feature1`
- **Enable multi-agent mode for independent phases** - Reduces wall-clock time
- **Update deliverables after completion** - Captures accurate metrics
- **Archive completed features** - Keeps workspace clean
- **Review plan validation score** - Aim for 90+ before execution
- **Use workorder IDs in commit messages** - Complete audit trail

### 🚫 Don't

- **Don't skip plan validation** - Low-quality plans cause implementation issues
- **Don't edit plan.json manually during execution** - Use `/update-task-status` instead
- **Don't create workorders without `/create-workorder`** - Breaks tracking
- **Don't forget to commit after `/align-plan`** - Pre-execution checkpoint is critical
- **Don't mix coderef-docs and coderef-workflow operations** - Use slash commands for coordination
- **Don't archive features with status != "Complete"** - Unless using `--force` flag

### 💡 Tips

- **Use tab completion for feature names** - Claude Code autocompletes from `coderef/workorder/`
- **Enable coderef-context integration** - Dramatically improves plan quality
- **Use risk assessment for critical changes** - Catches breaking changes early
- **Read ARCHITECTURE.md first** - Understand existing patterns before planning
- **Track progress with TodoWrite** - Visual feedback keeps you focused

---

## Troubleshooting

### Symptom: MCP server won't start

**Error Message:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Cause:** Dependencies not installed.

**Solution:**
```bash
cd C:\Users\willh\.mcp-servers\coderef-workflow
pip install -e .
```

---

### Symptom: `/create-workorder` not recognized

**Error Message:**
```
Command not found: /create-workorder
```

**Cause:** MCP cache stale or `.mcp.json` misconfigured.

**Solution:**
1. Check `~/.mcp.json` has coderef-workflow configured
2. Delete MCP cache:
   ```bash
   rm "C:\Users\{USERNAME}\.cursor\projects\{PROJECT_ID}\mcp-cache.json"
   ```
3. Restart Claude Code

---

### Symptom: Plan validation fails repeatedly

**Error Message:**
```
Plan validation failed: Score 65/100 (3 critical issues)
```

**Cause:** Missing required fields or placeholder text in plan.json.

**Solution:**
```bash
# View detailed report
/generate-plan-review

# Common fixes:
# - Ensure workorder_id in META_DOCUMENTATION
# - Replace all "TODO" placeholders with real content
# - Fix duplicate task IDs
# - Remove circular dependencies
```

---

### Symptom: coderef-context tools unavailable

**Warning Message:**
```
Warning: coderef-context unavailable, using filesystem analysis
```

**Cause:** coderef-context MCP server not running (this is normal, graceful fallback).

**Solution (optional):**
To enable code intelligence:
```bash
cd C:\Users\willh\.mcp-servers\coderef-context
pip install -e .
python server.py
```

Add to `~/.mcp.json`:
```json
{
  "mcpServers": {
    "coderef-context": {
      "command": "python",
      "args": ["C:/path/to/coderef-context/server.py"]
    }
  }
}
```

---

### Symptom: Archive operation fails

**Error Message:**
```
Error: Cannot archive feature with status 'in_progress'
```

**Cause:** Feature not marked complete in DELIVERABLES.md.

**Solution:**
```bash
# Option 1: Complete the feature first
/update-deliverables feature-name
# Edit DELIVERABLES.md status to "Complete"

# Option 2: Force archive (skip confirmation)
/archive-feature feature-name --force
```

---

## Quick Reference

### Common Commands

| Command | Purpose | Time |
|---------|---------|------|
| `/create-workorder` | Full planning workflow | 5-10 min |
| `/align-plan` | Generate TodoWrite task list | < 1 min |
| `/update-deliverables` | Capture git metrics | < 1 min |
| `/archive-feature` | Move to archive | < 1 min |
| `/validate-plan` | Score plan quality | < 1 min |

### MCP Tool Patterns

All tools follow this async pattern:

```python
result = await mcp__coderef_workflow__{tool_name}({
  "project_path": "/absolute/path",
  "feature_name": "my-feature",
  # ... other parameters
})
```

### File Structure

```
coderef/
├── workorder/              # Active features
│   └── {feature-name}/
│       ├── context.json
│       ├── analysis.json
│       ├── plan.json
│       ├── DELIVERABLES.md
│       └── communication.json  (multi-agent)
├── archived/               # Completed features
│   └── index.json
└── foundation-docs/        # Generated docs
    ├── README.md
    ├── ARCHITECTURE.md
    ├── API.md
    ├── COMPONENTS.md
    └── SCHEMA.md
```

### Workorder ID Format

```
WO-{FEATURE}-{CATEGORY}-{SEQUENCE}

Examples:
- WO-AUTH-SYSTEM-001
- WO-DARK-MODE-UI-002
- WO-API-REFACTOR-003
```

### Plan Status Lifecycle

```
planning → in_progress → completed → archived
```

---

## AI Integration Notes

### For AI Agents

**coderef-workflow is designed for AI-to-AI communication:**

1. **Tools are async** - Always use `await` when calling MCP tools
2. **Use slash commands** - They provide structured workflows, not just individual tools
3. **TodoWrite integration** - Task lists print to CLI terminal for user visibility
4. **Code intelligence available** - Call coderef-context during planning for dependency analysis
5. **Graceful fallbacks** - Works without coderef-context (filesystem analysis instead)
6. **Validation-first** - Always validate plans before execution (score >= 90 recommended)

### Key MCP Patterns

**Sequential Tool Calls:**
```python
# When steps depend on each other
context = await gather_context(...)
analysis = await analyze_project_for_planning(...)
plan = await create_plan(...)  # Uses context + analysis
```

**Parallel Tool Calls (via communication.json):**
```python
# Multi-agent coordination
await assign_agent_task(agent_number=1, phase_id="phase_1")
await assign_agent_task(agent_number=2, phase_id="phase_2")
await assign_agent_task(agent_number=3, phase_id="phase_3")
```

**Error Handling:**
```python
try:
    result = await create_plan(...)
except Exception as e:
    logger.error(f"Plan creation failed: {e}")
    # Fallback: manual plan creation or error report
```

### Integration with Other Servers

```
coderef-workflow → coderef-context  (code intelligence)
coderef-workflow → coderef-docs     (documentation generation)
coderef-workflow ← coderef-personas (expert agents)
```

**Best Practice:** Always use coderef-context during planning for maximum plan quality.

---

**Documentation Version:** 1.1.0
**Last Updated:** December 28, 2025
**Maintained by:** willh, Claude Code AI
