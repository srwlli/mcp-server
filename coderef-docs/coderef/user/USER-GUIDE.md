# coderef-docs User Guide

**Project:** coderef-docs MCP Server
**Version:** 3.4.0
**Last Updated:** 2026-01-10
**Author:** willh, Claude Code AI

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [How It Works](#how-it-works)
4. [Getting Started](#getting-started)
5. [Use Cases](#use-cases)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Prerequisites

**Required:**
- Python 3.10 or higher
- MCP-compatible AI client (Claude Code, etc.)

**Verification:**
```bash
python --version
# Expected: Python 3.10+ or Python 3.11+ or Python 3.12+ or Python 3.13+
```

**Optional:**
- Git (for changelog auto-detection)
- coderef-context MCP server (for enhanced code intelligence)

---

## Installation

### Step 1: Install Dependencies

```bash
cd ~/.mcp-servers/coderef-docs
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed mcp-1.0.0 jsonschema-4.0.0 packaging-21.0
```

### Step 2: Configure MCP

Add to `~/.mcp.json`:

```json
{
  "mcpServers": {
    "coderef-docs": {
      "command": "python",
      "args": ["C:/Users/willh/.mcp-servers/coderef-docs/server.py"],
      "cwd": "C:/Users/willh/.mcp-servers/coderef-docs"
    }
  }
}
```

### Step 3: Verify Installation

Restart your MCP client and check:

```
Available tools should include:
- list_templates
- generate_foundation_docs
- generate_resource_sheet
- record_changes
- establish_standards
... (13 total tools)
```

---

## How It Works

### Architecture Overview

```
┌─────────────┐
│   Claude    │  ← MCP Client (your AI assistant)
└──────┬──────┘
       │ stdio (JSON-RPC 2.0)
       ↓
┌─────────────────────────────┐
│  coderef-docs MCP Server    │
│  ┌──────────────────────┐   │
│  │  13 MCP Tools        │   │
│  ├──────────────────────┤   │
│  │  POWER Templates     │   │
│  ├──────────────────────┤   │
│  │  Standards Engine    │   │
│  └──────────────────────┘   │
└──────────┬──────────────────┘
           │
           ↓
    ┌──────────────┐
    │  .coderef/   │  ← Code intelligence data
    │  Project     │
    │  Files       │
    └──────────────┘
```

### Key Components

1. **MCP Tools** - 13 specialized tools for documentation, changelog, and standards
2. **POWER Framework** - Template system (Purpose, Overview, What/Why/When, Examples, References)
3. **Standards Engine** - Extract and enforce coding standards
4. **UDS Integration** - Universal Document Standard for workorder tracking

---

## Getting Started

### Tutorial 1: Generate Foundation Documentation

**Time:** ~2-5 minutes

**Step 1:** Call the foundation docs tool
```
/generate-docs
```

**What happens behind the scenes:**
1. Tool scans project for `.coderef/` data
2. Reads existing foundation docs (if any)
3. Auto-detects APIs, schemas, components via regex
4. Generates 5 documents sequentially

**Step 2:** Documents created
- `README.md` (project root)
- `coderef/foundation-docs/API.md`
- `coderef/foundation-docs/SCHEMA.md`
- `coderef/foundation-docs/COMPONENTS.md`
- `coderef/foundation-docs/ARCHITECTURE.md`

**Result:** Complete technical documentation suite following POWER framework

---

### Tutorial 2: Record Code Changes

**Time:** ~30 seconds

**Step 1:** Make changes to your code
```bash
# Edit some files
git add .
```

**Step 2:** Record changes with smart detection
```
/record-changes
```

**What happens:**
1. Tool auto-detects git changes (staged files)
2. Analyzes diff to suggest change_type (feature/bugfix/breaking)
3. Calculates severity based on files changed
4. Asks for your confirmation
5. Updates CHANGELOG.json

**Result:** Professional changelog entry with workorder tracking

---

### Tutorial 3: Establish Coding Standards

**Time:** ~5-10 seconds (with .coderef/) or ~1-2 minutes (without)

**Step 1:** Extract standards from your codebase
```
/establish-standards
```

**Behind the scenes:**
1. Checks for `.coderef/index.json` (fast path: ~50ms)
2. Falls back to full scan if missing (~5-60 seconds)
3. Analyzes UI patterns, behavior patterns, UX flows
4. Generates 4 standards files

**Step 2:** Review generated standards
- `coderef/standards/UI-STANDARDS.md`
- `coderef/standards/BEHAVIOR-STANDARDS.md`
- `coderef/standards/UX-PATTERNS.md`
- `coderef/standards/COMPONENT-INDEX.md`

**Step 3:** Enforce standards on future code
```
/check-consistency
```

**Result:** Automated standards compliance checking

---

## Use Cases

### Use Case 1: New Project Documentation

**Scenario:** You've built a new MCP server and need complete documentation

**Workflow:**
```bash
# 1. Generate foundation docs
/generate-docs

# 2. Generate user-facing docs
/generate-user-docs

# 3. Extract coding standards
/establish-standards

# Total time: ~5-10 minutes
# Result: 9 professional documents ready to publish
```

---

### Use Case 2: Feature Implementation Tracking

**Scenario:** You implemented a new feature and need to document it

**Workflow:**
```bash
# 1. Complete your feature implementation
git add .

# 2. Record changes
/record-changes

# 3. Update affected documentation
/generate-docs  # Regenerate if API/schema changed

# Total time: ~2-3 minutes
# Result: Feature tracked in CHANGELOG, docs updated
```

---

### Use Case 3: Pre-Commit Quality Gate

**Scenario:** You want to enforce coding standards before committing

**Workflow:**
```bash
# 1. Make code changes
git add modified_files.py

# 2. Check consistency
/check-consistency

# 3. Fix violations if any
# ... make fixes ...

# 4. Re-check
/check-consistency  # Should pass

# 5. Commit
git commit -m "feat: new feature"

# Result: Only standards-compliant code gets committed
```

---

## Best Practices

### ✅ Do

- **Run `/establish-standards` once per project** to create baseline standards
- **Use `/generate-docs` when APIs/schemas change** to keep documentation current
- **Call `/record-changes` after feature completion** for professional changelog tracking
- **Check `.coderef/` data exists** for faster standards generation (10x speedup)
- **Use specific template names** with `generate_individual_doc` for targeted updates

### 🚫 Don't

- **Don't skip `/establish-standards`** before using `/audit-codebase` or `/check-consistency`
- **Don't manually edit CHANGELOG.json** - use `/record-changes` for consistency
- **Don't generate docs without `.coderef/` data** if accuracy matters (use coderef-context first)
- **Don't ignore validation warnings** - they indicate real issues

### 💡 Tips

- **Tip 1:** Use `.coderef/` data for 10x faster standards generation
- **Tip 2:** Run `/check-consistency` in pre-commit hooks for automatic enforcement
- **Tip 3:** Combine with coderef-context for enhanced code intelligence
- **Tip 4:** Use workorder IDs in changelog entries for full traceability

---

## Troubleshooting

### Problem: "Template not found" error

**Symptom:**
```
ERROR - Template 'readme' not found
```

**Cause:** Trying to use invalid template name

**Solution:**
```bash
# List valid templates
/list-templates

# Valid names: readme, architecture, api, components, schema, user-guide, my-guide
```

---

### Problem: Standards audit fails

**Symptom:**
```
ERROR - No standards found
```

**Cause:** Standards haven't been established yet

**Solution:**
```bash
# Run establish-standards first
/establish-standards

# Then audit
/audit-codebase
```

---

### Problem: Slow standards generation

**Symptom:** `/establish-standards` takes 30-60 seconds

**Cause:** No `.coderef/` data available (using slow full scan)

**Solution:**
```bash
# Option 1: Generate .coderef/ data first (recommended)
# Call mcp__coderef_context__coderef_scan
# Then run /establish-standards  (now takes ~50ms)

# Option 2: Accept slower scan (still works fine)
```

---

### Problem: "Invalid request parameters" error

**Symptom:**
```
ERROR - Invalid request parameters
```

**Cause:** Missing required parameters or invalid values

**Solution:** Check tool schema:
```bash
# Get template to see required params
/get-template api

# Verify parameter names match exactly
```

---

## Quick Reference

### Common Commands

| Task | Command | Time |
|------|---------|------|
| Generate all foundation docs | `/generate-docs` | 2-5 min |
| Generate all user docs | `/generate-user-docs` | 3-7 min |
| Record code changes | `/record-changes` | 30 sec |
| Extract standards | `/establish-standards` | 5-10 sec (with .coderef/) |
| Check compliance | `/audit-codebase` | 1-2 min |
| Pre-commit check | `/check-consistency` | 10-30 sec |

### MCP Tool Quick Reference

| Tool | Purpose | Required Params |
|------|---------|-----------------|
| `list_templates` | Show available templates | None |
| `get_template` | Get template content | template_name |
| `generate_foundation_docs` | Generate 5 foundation docs | project_path |
| `generate_individual_doc` | Generate single doc | project_path, template_name |
| `generate_resource_sheet` | Create module-based docs | project_path, element_name |
| `record_changes` | Smart changelog recording | project_path, feature_description |
| `establish_standards` | Extract coding standards | project_path |
| `audit_codebase` | Check standards compliance | project_path |
| `check_consistency` | Pre-commit validation | project_path |

### File Locations

| Document Type | Location |
|---------------|----------|
| Foundation docs | `coderef/foundation-docs/` |
| User docs | `coderef/user/` |
| Standards | `coderef/standards/` |
| Changelog | `coderef/CHANGELOG.json` |
| README | Project root |

---

## AI Integration Notes

This MCP server is designed to work seamlessly with AI assistants like Claude:

- **Automatic context injection** - Tools provide templates + extracted code data
- **Smart defaults** - Sensible parameter defaults for common use cases
- **Progress indicators** - [1/5], [2/5] markers for sequential operations
- **Error guidance** - Helpful error messages with resolution steps
- **MCP orchestration** - Works with other MCP servers (coderef-context, etc.)

---

**Need Help?** Check [API.md](../foundation-docs/API.md) for detailed tool schemas or [my-guide.md](my-guide.md) for quick tool lookup.
