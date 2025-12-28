# coderef-docs Features

**What can coderef-docs do for you?**

---

## Overview

coderef-docs provides **11 specialized tools** across 3 core capabilities:

1. **Documentation Generation** (5 tools)
2. **Changelog Management** (3 tools)
3. **Standards Enforcement** (3 tools)

All tools integrate with Claude Code via the Model Context Protocol (MCP).

---

## Feature 1: Auto-Generate Foundation Documentation

### What It Does

Automatically creates 5 comprehensive documentation files from your codebase:

- **README.md** - Project overview, installation, usage
- **ARCHITECTURE.md** - System design, components, data flow
- **API.md** - Complete API/tool reference
- **SCHEMA.md** - Data structures and schemas
- **COMPONENTS.md** - Component architecture

### How It Works

**With Code Intelligence** (@coderef/core CLI installed):
- Scans your codebase for real API endpoints
- Extracts actual data models
- Discovers UI components
- Populates templates with real code structure

**Without CLI:**
- Uses POWER framework templates
- Provides structured placeholders
- Still creates useful documentation

### Use Cases

✅ **New Project** - Get docs in 2 minutes instead of 2 hours
✅ **Code Handoff** - Comprehensive docs for new team members
✅ **Open Source** - Professional docs that attract contributors
✅ **Documentation Refresh** - Update all docs after major refactoring

### Tools

- `generate_foundation_docs` - Generate all 5 docs
- `generate_individual_doc` - Generate/update single doc
- `list_templates` - See available templates
- `get_template` - Get template content
- `generate_quickref_interactive` - Create scannable quickref

---

## Feature 2: Smart Changelog Management

### What It Does

Maintains a structured, searchable changelog with:

- Semantic versioning (x.y.z)
- Change type tracking (feature/bugfix/breaking/etc)
- Severity levels (critical/major/minor/patch)
- Workorder tracking (WO-XXX-###)
- Git auto-detection

### How It Works

**Auto-Detection Mode:**
1. Detects changed files via `git diff`
2. Suggests change type from commit messages
3. Calculates severity from scope
4. Shows preview
5. Creates entry after confirmation

**Manual Mode:**
- Provide all metadata yourself
- Complete control over entry details
- No git required

### Use Cases

✅ **Release Notes** - Auto-generate from changelog entries
✅ **Version Tracking** - See what changed in each version
✅ **Breaking Changes** - Filter for breaking changes only
✅ **Compliance** - Audit trail for all changes
✅ **Team Communication** - Share what changed and why

### Tools

- `record_changes` - Smart recording with git auto-detection
- `add_changelog_entry` - Manual entry with full control

---

## Feature 3: Code Standards Enforcement

### What It Does

Establishes and enforces coding standards by:

- Extracting patterns from existing code
- Documenting standards (UI, behavior, UX)
- Auditing codebase for violations
- Providing pre-commit gates
- Generating fix suggestions

### How It Works

**Phase 1: Extract Standards**
- Scans codebase for patterns
- Creates 4 standards docs:
  - `ui-patterns.md`
  - `behavior-patterns.md`
  - `ux-patterns.md`
  - `standards-index.md`

**Phase 2: Audit Compliance**
- Compares code against standards
- Calculates score (0-100)
- Lists violations by severity
- Suggests fixes

**Phase 3: Pre-commit Check**
- Checks only staged changes
- Fast (< 10 seconds)
- Pass/fail result
- Blocks commit on violations (optional)

### Use Cases

✅ **Onboarding** - New developers learn team standards
✅ **Code Review** - Automated first-pass review
✅ **Tech Debt** - Identify inconsistencies
✅ **Quality Gates** - Enforce standards in CI/CD
✅ **Refactoring** - Ensure consistency during rewrites

### Tools

- `establish_standards` - Extract patterns from code
- `audit_codebase` - Full compliance check (0-100 score)
- `check_consistency` - Fast pre-commit gate

---

## Feature Comparison

### When to Use What

| Need | Feature | Tools | Time | Output |
|------|---------|-------|------|--------|
| **Start new project** | Documentation Generation | `generate_foundation_docs` | ~2 min | 5 docs |
| **Update after refactor** | Documentation Generation | `generate_foundation_docs` | ~2 min | Refreshed docs |
| **Quick tool lookup** | Documentation Generation | `generate_quickref_interactive` | ~5 min | quickref.md |
| **Track feature completion** | Changelog Management | `record_changes` | ~30 sec | CHANGELOG entry |
| **Setup team standards** | Standards Enforcement | `establish_standards` | ~5 min | 4 standards docs |
| **Check code quality** | Standards Enforcement | `audit_codebase` | ~10 min | Compliance report |
| **Pre-commit check** | Standards Enforcement | `check_consistency` | ~10 sec | Pass/fail |

---

## Integration Features

### MCP Protocol

- **Seamless integration** with Claude Code
- **No manual installation** - configure once, use everywhere
- **Cross-project** - works on any codebase
- **AI-optimized** - designed for AI agent workflows

### Git Integration

- Auto-detects staged changes
- Reads commit messages
- Calculates file diffs
- Works with any git repository

### CLI Integration (Optional)

- **@coderef/core** for code intelligence
- Real API/schema/component extraction
- AST-based analysis
- Graceful fallback if unavailable

---

## Benefits

### For Individual Developers

✅ **Save time** - 2 minutes vs 2 hours for docs
✅ **Stay consistent** - Automated standards checking
✅ **Track changes** - Never forget what you did
✅ **Professional output** - POWER framework templates

### For Teams

✅ **Onboard faster** - Comprehensive docs for new members
✅ **Maintain quality** - Automated compliance checking
✅ **Reduce reviews** - Standards enforced pre-commit
✅ **Improve communication** - Structured changelogs

### For Open Source

✅ **Attract contributors** - Professional documentation
✅ **Maintain standards** - Automated enforcement
✅ **Track history** - Complete changelog
✅ **Scale easily** - Automated workflows

---

## Limitations

### What coderef-docs CANNOT do

🚫 **Generate code** - Only documentation
🚫 **Execute tests** - Only document test strategy
🚫 **Deploy projects** - Only document deployment
🚫 **Manage databases** - Only document schema

### Current Constraints

⚠️ **Context injection** requires @coderef/core CLI
⚠️ **Git operations** require git repository
⚠️ **Standards audit** requires established standards first
⚠️ **Changelog** requires manual version numbers

---

## Roadmap

### Planned Features

🔮 **REST API wrapper** for ChatGPT integration
🔮 **Extended templates** for specialized docs
🔮 **Multi-language support** for generated docs
🔮 **Enhanced semantic search** with RAG

### Under Consideration

💭 **Diagram generation** (Mermaid/PlantUML)
💭 **Code coverage integration** 
💭 **Automated version bumping**
💭 **GitHub Actions integration**

---

## Getting Started

**Ready to try it?** Check out:

- **Installation:** [USER-GUIDE.md](USER-GUIDE.md#installation)
- **Your First Doc:** [USER-GUIDE.md](USER-GUIDE.md#getting-started)
- **Tool Reference:** [my-guide.md](my-guide.md)
- **Complete API:** [API.md](../foundation-docs/API.md)

---

*Last Updated: 2025-12-27*
