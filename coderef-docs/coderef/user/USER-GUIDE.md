# coderef-docs User Guide

**Project:** coderef-docs
**Date:** 2025-12-27
**For:** Human users and AI agents

> Comprehensive guide to using coderef-docs MCP server for documentation generation, changelog management, and standards enforcement.

---

## Table of Contents

- [What is coderef-docs?](#what-is-coderef-docs)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Use Cases](#use-cases)
- [Tool Reference](#tool-reference)
- [Workflows](#workflows)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Quick Reference](#quick-reference)

---

## What is coderef-docs?

**coderef-docs** is an MCP server that makes documentation easy by providing 11 specialized tools for:

✅ **Generating foundation docs** (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
✅ **Managing changelogs** with git auto-detection
✅ **Enforcing coding standards** across your codebase
✅ **Creating quick reference guides** for any app type

### Why Use It?

**Problem:** Documentation is tedious and gets out of date
**Solution:** Auto-generate comprehensive docs from your codebase

**Problem:** Changelogs are manual and inconsistent
**Solution:** Auto-detect changes from git and create structured entries

**Problem:** Code standards drift over time
**Solution:** Extract patterns from existing code and audit for violations

---

## Prerequisites

### Required

✅ **Claude Code** or **ChatGPT with MCP support**
✅ **Python 3.10+**

```bash
python --version
# Expected: Python 3.10+
```

### Optional

🔹 **@coderef/core CLI** for code intelligence (recommended)

```bash
npm install -g @coderef/core
coderef --version
# Expected: @coderef/core v1.x.x
```

💡 **Tip:** Without the CLI, docs use placeholders instead of real code extraction

---

## Installation

### Step 1: Configure MCP

Add to `~/.mcp.json` or `.claude/settings.json`:

```json
{
  "mcpServers": {
    "coderef-docs": {
      "command": "python",
      "args": ["-m", "coderef-docs.server"],
      "env": {}
    }
  }
}
```

### Step 2: Restart Claude Code

Close and reopen Claude Code to load the MCP server.

### Step 3: Verify Installation

Type `/` and look for:
- `/generate-docs`
- `/record-changes`
- `/establish-standards`

✅ **You're ready!**

---

## How It Works

### Behind the Scenes

```
Your Request
    ↓
Claude Code (MCP Client)
    ↓
coderef-docs (MCP Server)
    ↓
┌─────────────┬──────────────┬─────────────┐
│  Templates  │  Extractors  │  Generators │
│  (POWER)    │  (Optional)  │             │
└─────────────┴──────────────┴─────────────┘
    ↓
Generated Docs (Markdown/JSON)
```

### Context Injection (Optional)

If `@coderef/core` CLI is installed:
1. **API.md** gets real API endpoints from your code
2. **SCHEMA.md** gets real data models
3. **COMPONENTS.md** gets real UI components

Otherwise: Uses template placeholders (still useful!)

---

## Getting Started

### Your First Documentation Generation

**Goal:** Generate complete foundation docs for your project

**Time:** ~2 minutes

**Steps:**

1. **Open your project in Claude Code**

2. **Run the command:**
   ```
   /generate-docs
   ```

3. **Watch the magic happen:**
   ```
   [1/5] Generating API.md...
   [2/5] Generating SCHEMA.md...
   [3/5] Generating COMPONENTS.md...
   [4/5] Generating ARCHITECTURE.md...
   [5/5] Generating README.md...
   ```

4. **Check the results:**
   - `README.md` → Project root
   - Other docs → `coderef/foundation-docs/`

✅ **Done!** You now have 5 comprehensive documentation files.

---

## Use Cases

### Use Case 1: New Project Documentation

**Scenario:** You just started a project and need docs fast

**Command:**
```
/generate-docs
```

**Result:** 5 complete docs in ~2 minutes

**Behind the Scenes:**
- Scans your codebase
- Extracts structure
- Generates POWER-formatted docs
- Saves to correct locations

---

### Use Case 2: Tracking Feature Changes

**Scenario:** You just finished a feature and need to update the changelog

**Command:**
```
/record-changes
```

**What Happens:**
1. Auto-detects changed files via `git diff`
2. Suggests change type (feature/bugfix/etc)
3. Calculates severity
4. Shows preview
5. Creates CHANGELOG entry after confirmation

**Example Interaction:**
```
User: /record-changes

Agent: I detected these changes:
  - tool_handlers.py (modified)
  - extractors.py (new file)

Suggested type: feature
Suggested severity: minor

Create changelog entry?

User: Yes

Agent: ✅ Added to CHANGELOG.json v3.2.0
```

---

### Use Case 3: Enforcing Code Standards

**Scenario:** Your team wants consistent code patterns

**Step 1: Extract Standards**
```
/establish-standards
```

**Result:** 4 files in `coderef/standards/`
- `ui-patterns.md`
- `behavior-patterns.md`
- `ux-patterns.md`
- `standards-index.md`

**Step 2: Audit Compliance**
```
/audit-codebase
```

**Result:** Compliance report with score (0-100)

**Step 3: Pre-commit Check**
```
/check-consistency
```

**Result:** Pass/fail for staged changes

---

## Tool Reference

### Documentation Tools

#### `/generate-docs`
Generates 5 foundation docs with code intelligence

**When to use:**
- New project
- Major refactoring
- Documentation refresh

**Time:** ~2 minutes
**Output:** README, ARCHITECTURE, API, SCHEMA, COMPONENTS

---

#### `/generate-quickref`
Interactive quickref guide generation

**When to use:**
- Need scannable reference
- Different app types (CLI, Web, API, etc.)

**Time:** ~5 minutes (interactive)
**Output:** `coderef/quickref.md` (150-250 lines)

---

### Changelog Tools

#### `/record-changes`
Smart changelog with git auto-detection

**When to use:**
- After completing a feature
- Before merging PR
- Automated changelog updates

**Time:** ~30 seconds
**Output:** CHANGELOG.json entry

💡 **Best Practice:** Run this before `/archive-feature`

---

### Standards Tools

#### `/establish-standards`
Extract coding standards from codebase

**When to use:**
- First time setting up standards
- After major code style changes
- New team members onboarding

**Time:** ~3-5 minutes
**Output:** 4 standards files

---

#### `/audit-codebase`
Check compliance with standards

**When to use:**
- Before release
- Periodic code quality checks
- Technical debt assessment

**Time:** ~5-10 minutes
**Output:** Compliance report with score

---

#### `/check-consistency`
Pre-commit gate for staged changes

**When to use:**
- In pre-commit hooks
- Before git commit
- Quick quality check

**Time:** ~10 seconds
**Output:** Pass/fail + violations

---

## Workflows

### Workflow 1: Complete Documentation from Scratch

```
Step 1: Generate docs
  /generate-docs
  → README, ARCHITECTURE, API, SCHEMA, COMPONENTS

Step 2: Add user guide
  /generate-quickref
  → quickref.md

Step 3: Set up standards
  /establish-standards
  → Extract patterns from code

Done! ✅
```

**Time:** ~10 minutes total

---

### Workflow 2: Feature Completion

```
Step 1: Code your feature
  [Your work here]

Step 2: Record changes
  /record-changes
  → Auto-detects changes, creates changelog

Step 3: Update docs (if needed)
  /generate-docs
  → Refresh documentation

Step 4: Check standards
  /check-consistency
  → Verify no violations

Done! ✅
```

**Time:** ~3 minutes (documentation part)

---

### Workflow 3: Pre-commit Quality Gate

```
Step 1: Stage your changes
  git add .

Step 2: Check consistency
  /check-consistency
  → Pass/fail for staged files

Step 3: If violations found
  Fix issues
  → Re-run check

Step 4: Commit
  git commit -m "message"

Done! ✅
```

**Time:** ~30 seconds per check

---

## Best Practices

### ✅ Do

**Generate docs early**
- Run `/generate-docs` at project start
- Easier to maintain than create later

**Use record_changes for changelogs**
- Auto-detection saves time
- Consistent format
- Workorder tracking

**Establish standards once**
- Run `/establish-standards` early
- Use `/audit-codebase` periodically
- Add `/check-consistency` to pre-commit hooks

**Keep docs in sync**
- Re-run `/generate-docs` after major changes
- Update README when adding features

---

### 🚫 Don't

**Don't skip changelogs**
- Future you will thank you
- Essential for version tracking

**Don't ignore standards violations**
- Fix critical violations immediately
- Plan fixes for major/minor

**Don't generate docs repeatedly**
- They're expensive (time/tokens)
- Update specific sections manually for small changes

---

### 💡 Tips

**Tip 1:** Use `/generate-quickref` for user-facing docs, API.md for technical reference

**Tip 2:** Run `/check-consistency` before every commit (add to pre-commit hook)

**Tip 3:** If context injection fails, install `@coderef/core`:
```bash
npm install -g @coderef/core
```

**Tip 4:** README.md goes in project root, all others in `coderef/foundation-docs/`

---

## Troubleshooting

### Issue: "Context Injection: DISABLED"

**Symptom:** Docs show `[FALLBACK] Using template placeholders`

**Cause:** `@coderef/core` CLI not installed or not in PATH

**Solution:**
```bash
npm install -g @coderef/core
# Restart Claude Code
```

**Verification:**
```bash
coderef --version
# Should show: @coderef/core v1.x.x
```

---

### Issue: "File already exists" Error

**Symptom:** Can't generate docs because files exist

**Cause:** Protection against overwriting

**Solution:**
- **Option A:** Delete existing docs first
- **Option B:** Use `/generate-individual-doc` to update specific files

---

### Issue: Standards Audit Fails

**Symptom:** `/audit-codebase` returns errors

**Cause:** No standards files exist

**Solution:**
1. Run `/establish-standards` first
2. Then run `/audit-codebase`

---

### Issue: Changelog Entry Fails

**Symptom:** `/record-changes` fails validation

**Cause:** Missing required fields or invalid format

**Solution:** Use `/add-changelog` for manual entry with all required fields

---

## Quick Reference

| Need | Command | Time | Output |
|------|---------|------|--------|
| Complete docs | `/generate-docs` | ~2 min | 5 files |
| User docs | `/generate-user-docs` | ~5 min | 4 user docs |
| Update changelog | `/record-changes` | ~30 sec | CHANGELOG entry |
| Set standards | `/establish-standards` | ~5 min | 4 standards files |
| Check compliance | `/audit-codebase` | ~10 min | Score + report |
| Pre-commit check | `/check-consistency` | ~10 sec | Pass/fail |

---

## More Resources

- **Complete API Reference:** [API.md](../foundation-docs/API.md)
- **Tool Quick Lookup:** [my-guide.md](my-guide.md)
- **Architecture Details:** [ARCHITECTURE.md](../foundation-docs/ARCHITECTURE.md)
- **Fast Reference:** [quickref.md](quickref.md)

---

**Need help?** Check the troubleshooting section or consult the API reference for detailed tool specifications.

**Found a bug?** Report at https://github.com/anthropics/claude-code/issues

*Generated: 2025-12-27*
