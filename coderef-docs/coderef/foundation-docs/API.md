# API Reference - coderef-docs

**Project:** coderef-docs (MCP Server)
**Version:** 4.0.0
**Last Updated:** 2026-01-13
**Protocol:** MCP (Model Context Protocol) 1.0

---

## Purpose

This document provides the complete MCP tool interface reference for coderef-docs, a documentation generation server that provides **16 specialized tools** for foundation docs, changelog management, standards enforcement, user documentation automation, and composable resource sheets with optional MCP integration for enhanced code intelligence.

## Overview

**What's Included:**
- 16 MCP tool endpoints with complete schemas (13 active, 1 internal, 1 deprecated)
- MCP integration details (drift detection, semantic pattern analysis)
- Request/response examples with v4.0.0 features
- Error handling patterns
- Tool orchestration workflows
- Health check system

**Not Included:**
- Internal implementation details (see ARCHITECTURE.md)
- Setup/deployment (see README.md in project root)
- MCP integration architecture (see INTEGRATION.md)

---

## Authentication & Transport

**Protocol:** JSON-RPC 2.0 over stdio
**Authentication:** None (local MCP server)
**Content-Type:** application/json

### Connection

The server runs as a subprocess and communicates via standard input/output:

```python
# From ~/.mcp.json configuration
{
  "coderef-docs": {
    "command": "python",
    "args": ["C:/Users/willh/.mcp-servers/coderef-docs/server.py"],
    "cwd": "C:/Users/willh/.mcp-servers/coderef-docs"
  }
}
```

---

## Tool Categories

### 1. Utility (2 tools)
- `list_templates` - Show templates + MCP status ✅
- `get_template` - Get specific template ✅

### 2. Foundation Documentation (3 tools)
- `generate_foundation_docs` - Generate 5 docs + drift check ✅
- `generate_individual_doc` - Single doc generation [INTERNAL]
- `coderef_foundation_docs` - Old tool [DEPRECATED]

### 3. User Documentation (4 tools - NEW in v4.0.0)
- `generate_my_guide` - Developer quick-start (80% auto-fill) ✅
- `generate_user_guide` - 10-section guide (75% auto-fill) ✅
- `generate_features` - Feature inventory (75% auto-fill) ✅
- `generate_quickref_interactive` - Interactive quickref ✅

### 4. Changelog (2 tools)
- `add_changelog_entry` - Manual entry ✅
- `record_changes` - Smart git recording ⭐

### 5. Standards (3 tools)
- `establish_standards` - Extract standards (80%+ quality with MCP) ✅
- `audit_codebase` - Compliance check (0-100 score) ✅
- `check_consistency` - Pre-commit gate ⭐

### 6. Validation (2 tools)
- `validate_document` - UDS validation ✅
- `check_document_health` - Health score (0-100) ✅

### 7. Advanced (1 tool)
- `generate_resource_sheet` - Composable module-based docs ✅

**Total:** 16 tools (13 active ✅, 1 internal, 1 deprecated, 1 removed in v5.0.0)

---

## API Endpoints

### 1. list_templates

**Status:** ✅ Active
**Category:** Utility
**New in v4.0.0:** MCP health check display

Lists all available POWER framework templates with MCP integration status.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_templates",
    "arguments": {}
  }
}
```

**Response (v4.0.0):**
```
Available Templates:

1. readme - Project README with POWER framework
2. architecture - System architecture documentation
3. api - API reference with endpoint documentation
4. components - UI components catalog
5. schema - Data models and schemas
6. user-guide - Comprehensive user onboarding
7. my-guide - Developer quick-start reference

============================================================

🔧 MCP INTEGRATION STATUS:

  • coderef-context MCP: ✅ Available
  • Enhanced Features: Drift detection, pattern analysis, semantic insights

============================================================
```

**Features (v4.0.0):**
- Shows MCP status (✅ Available / ⚠️ Unavailable)
- Lists enhanced features when MCP available
- Shows fallback mode description when unavailable
- Performance: < 100ms

---

### 2. get_template

**Status:** ✅ Active
**Category:** Utility

Retrieves a specific POWER framework template by name.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_template",
    "arguments": {
      "template_name": "readme"
    }
  }
}
```

**Parameters:**
- `template_name` (string, required): One of: readme, architecture, api, components, schema, user-guide, my-guide

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "# README Template (POWER Framework)\n\n## Purpose\n\n[Why this project exists...]\n\n## Overview\n\n[What's included...]\n\n..."
    }
  ]
}
```

**Performance:** < 10ms (direct file read)

---

### 3. generate_foundation_docs

**Status:** ✅ Active
**Category:** Foundation Documentation
**Enhanced in v4.0.0:** Drift detection + sequential generation

Generates 5 foundation documents sequentially with drift detection and resource checking.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_foundation_docs",
    "arguments": {
      "project_path": "/path/to/project",
      "auto_validate": true
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project directory
- `auto_validate` (boolean, optional): Auto-validate with Papertrail (default: true)

**Response (v4.0.0):**
```
📋 Foundation Documentation Generation Plan

✅ Drift Check: Index is up to date (drift: 5%, severity: none)

.coderef/ Resource Check:
  ✅ index.json (21,344 elements)
  ✅ context.md
  ✅ patterns.json
  ⚠️  diagrams/ (not found - optional)

Generating 5 documents sequentially:

[1/5] readme → Uses: context.md, patterns.json
[2/5] architecture → Uses: context.json, graph.json
[3/5] api → Uses: index.json, patterns.json
[4/5] schema → Uses: index.json, context.json
[5/5] components → Uses: index.json, patterns.json

Each document will be generated by calling generate_individual_doc with template-specific context...
```

**Features (v4.0.0):**
- **Drift detection:** Checks .coderef/index.json staleness before generation
  - none: ≤10% drift (OK to proceed)
  - standard: >10%, ≤50% drift (warning, consider re-scan)
  - severe: >50% drift (error, must re-scan)
- **Resource checking:** Validates .coderef/ file availability
- **Template mapping:** Each template uses specific .coderef/ files
- **Sequential generation:** Calls `generate_individual_doc` 5 times (~300 lines each)
- **Progress markers:** [1/5], [2/5], etc. for visibility

**Outputs:**
- README.md → project root
- ARCHITECTURE.md, API.md, SCHEMA.md, COMPONENTS.md → coderef/foundation-docs/

**Performance:** ~8-10 seconds (sequential generation prevents timeout)

---

### 4. generate_individual_doc

**Status:** [INTERNAL] - Orchestrated by generate_foundation_docs only
**Category:** Foundation Documentation
**Enhanced in v4.0.0:** Template-specific context mapping

Generates a single foundation document. **Not recommended for direct use** - use `generate_foundation_docs` instead for orchestrated workflow.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_individual_doc",
    "arguments": {
      "project_path": "/path/to/project",
      "template_name": "api",
      "version": "1.0.0",
      "workorder_id": "WO-FEATURE-001",
      "feature_id": "feature-name",
      "auto_validate": true
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `template_name` (string, required): readme, architecture, api, components, schema, user-guide, my-guide
- `version` (string, optional): Document version (default: 1.0.0)
- `workorder_id` (string, optional): Workorder ID for UDS tracking
- `feature_id` (string, optional): Feature ID (defaults to template_name)
- `auto_validate` (boolean, optional): Papertrail validation (default: true)

**Features (v4.0.0):**
- Template-specific context mapping (each template reads specific .coderef/ files)
- Resource availability checking with warnings
- Template-specific instructions for AI agents

**Why [INTERNAL]:**
- Called automatically by `generate_foundation_docs`
- Sequential orchestration prevents timeouts
- Context injection handled by orchestrator
- Direct use bypasses drift detection and resource checking

---

### 5. coderef_foundation_docs

**Status:** [DEPRECATED] - Replaced by generate_foundation_docs
**Category:** Foundation Documentation
**Will be removed in:** v5.0.0

**Deprecation Notice:**
This tool is deprecated and will be removed in v5.0.0. Use `generate_foundation_docs` instead.

**Why deprecated:**
- No drift detection
- No MCP integration
- No sequential generation (timeout issues)
- No resource checking

**Migration:**
```python
# Old (deprecated - don't use)
coderef_foundation_docs(project_path="/path/to/project")

# New (recommended)
generate_foundation_docs(
    project_path="/path/to/project",
    auto_validate=True  # NEW: Papertrail validation
)
```

---

### 6. generate_my_guide

**Status:** ✅ Active (NEW in v4.0.0)
**Category:** User Documentation
**Auto-fill:** 80%

Auto-generates my-guide.md - concise 60-80 line developer quick-start with MCP tools and slash commands.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_my_guide",
    "arguments": {
      "project_path": "/path/to/project"
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project directory

**Response:**
```
✅ Generated my-guide.md (80% auto-fill)

Auto-discovered content:
  • 16 MCP tools (from .coderef/index.json)
    - handle_generate_foundation_docs
    - handle_generate_my_guide
    - handle_establish_standards
    ... (13 more)

  • 22 slash commands (from .claude/commands/)
    - /generate-docs
    - /generate-user-docs
    - /establish-standards
    ... (19 more)

  • Tool categories:
    - Documentation: 7 tools
    - Changelog: 2 tools
    - Standards: 3 tools
    - Validation: 2 tools

Output: coderef/user/my-guide.md (~60-80 lines)
```

**Features:**
- **80% auto-fill rate** (Tools, Commands, Quickstart sections fully automated)
- **MCP tool extraction:** Reads .coderef/index.json for handle_* functions
- **Command scanning:** Reads .claude/commands/ directory
- **Tool categorization:** Groups by function (Documentation, Changelog, Standards, etc.)
- **Auto-examples:** Generates usage snippets from tool schemas
- **Performance:** ~2 seconds

**Output:** coderef/user/my-guide.md

---

### 7. generate_user_guide

**Status:** ✅ Active (NEW in v4.0.0)
**Category:** User Documentation
**Auto-fill:** 75%

Generates USER-GUIDE.md - comprehensive 10-section onboarding guide (200-300 lines).

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_user_guide",
    "arguments": {
      "project_path": "/path/to/project"
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project directory

**10 Sections:**
1. Prerequisites
2. Installation
3. Architecture Overview
4. Tools Reference (75% auto-filled)
5. Commands Reference (75% auto-filled)
6. Common Workflows
7. Best Practices
8. Troubleshooting
9. FAQ
10. Quick Reference

**Features:**
- **75% auto-fill rate** (Overview, Installation, Tools, Commands sections)
- **Leverages .coderef/ data** for automatic population
- **Tool extraction:** Same as my-guide but with detailed descriptions
- **Command extraction:** Full command documentation with examples
- **Performance:** ~3 seconds

**Output:** coderef/user/USER-GUIDE.md (~200-300 lines)

---

### 8. generate_features

**Status:** ✅ Active (NEW in v4.0.0)
**Category:** User Documentation
**Auto-fill:** 75%

Generates FEATURES.md - feature inventory with workorder tracking (150-250 lines).

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_features",
    "arguments": {
      "project_path": "/path/to/project"
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project directory

**Response:**
```
✅ Generated FEATURES.md (75% auto-fill)

Feature inventory:
  • Active features: 12 (from coderef/workorder/)
  • Archived features: 8 (from coderef/archived/)
  • Total workorders: 20

Workorder tracking:
  • WO-GENERATION-ENHANCEMENT-001: Complete (v4.0.0)
  • WO-CONTEXT-DOCS-INTEGRATION-001: Complete (v3.2.0)
  • WO-RESOURCE-SHEET-MCP-TOOL-001: Complete (v3.4.0)
  ... (17 more)

Output: coderef/user/FEATURES.md (~150-250 lines)
```

**Features:**
- **75% auto-fill rate** (MCP tools, feature list, workorder status)
- **Workorder scanning:** Scans coderef/workorder/ and coderef/archived/
- **Status extraction:** Extracts workorder IDs and completion status from plan.json
- **Executive summary:** Metrics and feature lifecycle documentation
- **Performance:** ~2 seconds

**Output:** coderef/user/FEATURES.md

---

### 9. generate_quickref_interactive

**Status:** ✅ Active
**Category:** User Documentation

Interactive workflow to generate quickref.md for any application type.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_quickref_interactive",
    "arguments": {
      "project_path": "/path/to/project",
      "app_type": "cli",
      "auto_validate": true
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `app_type` (string, optional): cli, web, api, desktop, library (can be inferred from user responses)
- `auto_validate` (boolean, optional): Papertrail validation (default: true)

**Supported Application Types:**
- **CLI** - Command-line tools
- **Web** - Web applications
- **API** - REST/GraphQL APIs
- **Desktop** - Desktop applications
- **Library** - NPM/PyPI packages

**Workflow:**
1. AI asks interview questions (app type, key features, commands, etc.)
2. User answers in plain English
3. AI generates scannable quickref.md (150-250 lines)

**Output:** coderef/user/quickref.md

---

### 10. add_changelog_entry

**Status:** ✅ Active
**Category:** Changelog Operations

Adds a manual changelog entry with full workorder tracking.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_changelog_entry",
    "arguments": {
      "project_path": "/path/to/project",
      "version": "1.0.2",
      "change_type": "feature",
      "severity": "minor",
      "title": "Add dark mode toggle",
      "description": "Users can now toggle between light and dark themes",
      "files": ["src/components/ThemeToggle.tsx"],
      "reason": "User request for improved accessibility",
      "impact": "Visual changes only, no breaking changes",
      "breaking": false
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `version` (string, required): Version number (e.g., "1.0.2")
- `change_type` (string, required): bugfix, enhancement, feature, breaking_change, deprecation, security
- `severity` (string, required): critical, major, minor, patch
- `title` (string, required): Short title
- `description` (string, required): Detailed description
- `files` (array, required): Affected files
- `reason` (string, required): Why this change was made
- `impact` (string, required): Impact on users/system
- `breaking` (boolean, optional): Breaking change (default: false)
- `migration` (string, optional): Migration guide (if breaking)
- `contributors` (array, optional): Contributors list
- `summary` (string, optional): Version summary

**Output:** Updates coderef/CHANGELOG.json

---

### 11. record_changes

**Status:** ✅ Active (Agentic Tool) ⭐
**Category:** Changelog Operations
**New in v3.1.0**

Smart changelog recording with git auto-detection and AI confirmation.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "record_changes",
    "arguments": {
      "project_path": "/path/to/project",
      "version": "1.0.3",
      "context": {}
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `version` (string, required): Version number for this change
- `context` (object, optional): Optional context for git-less environments

**Agentic Workflow:**
1. **Auto-detects:** Tool runs `git diff --staged` and reads commit messages
2. **Suggests:** change_type (feature/bugfix/breaking), severity, title, description
3. **Shows preview:** Agent reviews auto-generated details
4. **Confirms:** Agent confirms or modifies before creating entry
5. **Creates:** Entry written to CHANGELOG.json

**Example Auto-Detection:**
```
🔍 Auto-detected changes:

Files changed: 3
  • tool_handlers.py (+150 lines)
  • generators/user_guide_generator.py (new file)
  • README.md (+50 lines)

Commit messages:
  • "feat: add user docs automation"
  • "feat: 75% auto-fill for my-guide"

Suggested entry:
  change_type: feature
  severity: minor
  title: "Add user documentation automation"
  description: "3 new tools with 75%+ auto-fill from code intelligence"

👉 Confirm or modify details...
```

**Features:**
- Git auto-detection (works in repos)
- Context parameter (works without git)
- AI confirmation workflow
- Prevents accidental entries

**Output:** Updates coderef/CHANGELOG.json

---

### 12. establish_standards

**Status:** ✅ Active (ENHANCED in v4.0.0)
**Category:** Standards & Compliance
**Quality:** 80%+ with MCP patterns (vs 55% regex-only)

Extracts coding standards from codebase with MCP semantic pattern analysis.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "establish_standards",
    "arguments": {
      "project_path": "/path/to/project",
      "focus_areas": ["all"],
      "scan_depth": "standard",
      "auto_validate": true
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `focus_areas` (array, optional): ui_components, behavior_patterns, ux_flows, or all (default: ["all"])
- `scan_depth` (string, optional): quick (~1-2 min), standard (~3-5 min), deep (~10-15 min) (default: "standard")
- `auto_validate` (boolean, optional): Papertrail validation (default: true)

**Response (v4.0.0):**
```
✅ Standards extracted with MCP semantic patterns

Pattern frequency tracking:
  • async_function: 45 occurrences
  • class_definition: 23 occurrences
  • test_function: 67 occurrences
  • mcp_handler: 12 occurrences

Consistency violations detected: 3 files
  • handlers.py:150 - Not following async_function pattern
  • utils.py:75 - Missing class docstring
  • tests/test_api.py:200 - Inconsistent naming convention

Quality: 85% (MCP patterns) vs 55% (regex-only fallback)

Output:
  • coderef/standards/ui-patterns.md
  • coderef/standards/behavior-patterns.md
  • coderef/standards/ux-patterns.md
```

**Features (v4.0.0):**
- **MCP semantic patterns:** Uses `call_coderef_patterns()` for 90%+ detection accuracy
- **Pattern frequency tracking:** Quantifies pattern usage across codebase
- **Consistency violations:** Detects files not following established patterns
- **Quality improvement:** 55% → 80%+ with MCP patterns
- **Graceful fallback:** Uses regex-only if MCP unavailable
- **Performance:** ~100ms with .coderef/ (vs 5-60s full scan)

**Outputs:** 3 markdown files in coderef/standards/

---

### 13. audit_codebase

**Status:** ✅ Active
**Category:** Standards & Compliance

Full compliance audit with 0-100 score and fix suggestions.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "audit_codebase",
    "arguments": {
      "project_path": "/path/to/project",
      "scope": ["all"],
      "severity_filter": "all",
      "generate_fixes": true,
      "standards_dir": "coderef/standards"
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `scope` (array, optional): ui_patterns, behavior_patterns, ux_patterns, or all (default: ["all"])
- `severity_filter` (string, optional): critical, major, minor, or all (default: "all")
- `generate_fixes` (boolean, optional): Include fix suggestions (default: true)
- `standards_dir` (string, optional): Standards directory path (default: "coderef/standards")

**Response:**
```
📊 Compliance Audit Report

Overall Score: 85/100 (Good)

Violations Found: 12
  • Critical: 0
  • Major: 3
  • Minor: 9

Top Violations:
  1. Inconsistent naming convention (5 files)
  2. Missing error handling (3 files)
  3. Outdated patterns (4 files)

Automated Fixes Available: 9/12

Output: coderef/standards/audit-report.md
```

**Features:**
- Scans all source files against established standards
- Severity classification (critical/major/minor)
- Automated fix suggestions
- Compliance score (0-100)

**Output:** coderef/standards/audit-report.md

---

### 14. check_consistency

**Status:** ✅ Active ⭐
**Category:** Standards & Compliance
**Use Case:** Pre-commit hook, CI/CD quality gate

Lightweight pre-commit gate for modified files only.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "check_consistency",
    "arguments": {
      "project_path": "/path/to/project",
      "files": [],
      "scope": ["all"],
      "severity_threshold": "major",
      "fail_on_violations": true,
      "standards_dir": "coderef/standards"
    }
  }
}
```

**Parameters:**
- `project_path` (string, required): Absolute path to project
- `files` (array, optional): Files to check (auto-detects git changes if empty)
- `scope` (array, optional): ui_patterns, behavior_patterns, ux_patterns, or all (default: ["all"])
- `severity_threshold` (string, optional): critical, major, or minor (default: "major")
- `fail_on_violations` (boolean, optional): Return error if violations found (default: true)
- `standards_dir` (string, optional): Standards directory (default: "coderef/standards")

**Features:**
- **Auto-detects git changes:** Scans staged files by default
- **Lightweight:** Only modified files (fast for CI/CD)
- **Exit codes:** Returns error status if violations found
- **Threshold control:** Fail on critical only, major+, or all violations

**CI/CD Integration:**
```bash
# Pre-commit hook
.git/hooks/pre-commit:
  mcp-call check_consistency --fail-on-violations

# GitHub Actions
- run: mcp-call check_consistency --severity-threshold critical
```

**Performance:** ~1-3 seconds (modified files only)

---

### 15. validate_document

**Status:** ✅ Active
**Category:** Validation

Validates document against UDS (Universal Documentation Standards) schema.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "validate_document",
    "arguments": {
      "document_path": "/path/to/document.md",
      "doc_type": "plan"
    }
  }
}
```

**Parameters:**
- `document_path` (string, required): Absolute path to document
- `doc_type` (string, required): plan, deliverables, architecture, readme, api

**Response:**
```
✅ Validation Passed

Score: 95/100

Errors: 0
Warnings: 2
  • Missing optional section: Examples
  • Timestamp format could be improved

Validation Details:
  ✅ Required sections present
  ✅ Metadata format valid
  ✅ Workorder ID format correct
  ⚠️  Optional sections missing: 1
```

**Features:**
- Checks required sections
- Validates metadata format (workorder_id, timestamps)
- Returns errors/warnings with severity levels
- Score-based validation (0-100)

---

### 16. check_document_health

**Status:** ✅ Active
**Category:** Validation

Calculates document health score (0-100) based on 4 factors.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "check_document_health",
    "arguments": {
      "document_path": "/path/to/document.md",
      "doc_type": "plan"
    }
  }
}
```

**Parameters:**
- `document_path` (string, required): Absolute path to document
- `doc_type` (string, required): plan, deliverables, architecture, readme, api

**Response:**
```
📊 Document Health: 92/100 (Excellent)

Breakdown:
  • Traceability: 40/40 ✅
    - Has workorder_id: WO-GENERATION-ENHANCEMENT-001
    - Has feature_id: generation-enhancement-001
    - MCP attribution present

  • Completeness: 28/30 ⚠️
    - Required sections: 10/10
    - Optional sections: 8/10
    - Missing: 2 optional sections

  • Freshness: 18/20 ✅
    - Document age: 2 weeks
    - Last updated: 2026-01-13

  • Validation: 10/10 ✅
    - Passes UDS schema validation
    - No errors, 2 warnings
```

**Health Factors:**
- **Traceability (40%):** Has workorder_id, feature_id, MCP attribution
- **Completeness (30%):** Required + optional sections present
- **Freshness (20%):** Document age (<1 month = 100%, >6 months = 0%)
- **Validation (10%):** Passes schema validation

**Health Grades:**
- 90-100: Excellent
- 80-89: Good
- 70-79: Fair
- < 70: Poor

---

### 17. generate_resource_sheet

**Status:** ✅ Active
**Category:** Advanced Documentation
**New in v3.4.0**

Generates composable module-based documentation for code elements.

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_resource_sheet",
    "arguments": {
      "element_name": "AuthService",
      "project_path": "/path/to/project",
      "element_type": "service",
      "mode": "reverse-engineer",
      "auto_analyze": true,
      "validate_against_code": true,
      "auto_validate": true,
      "output_path": "coderef/foundation-docs/"
    }
  }
}
```

**Parameters:**
- `element_name` (string, required): Name of code element (e.g., "AuthService", "Button", "useAuth")
- `project_path` (string, required): Absolute path to project root
- `element_type` (string, optional): component, hook, service, class, function (auto-detected if not provided)
- `mode` (string, optional): reverse-engineer (analyze existing), template (new code scaffold), refresh (update docs) (default: "reverse-engineer")
- `auto_analyze` (boolean, optional): Use coderef_scan for auto-fill (default: true)
- `output_path` (string, optional): Custom output directory (default: coderef/foundation-docs/)
- `validate_against_code` (boolean, optional): Drift detection (default: true)
- `auto_validate` (boolean, optional): Papertrail validation (default: true)

**Features:**
- **Composable modules:** ~30-40 modules vs 20 rigid templates
- **3-step workflow:** Detect (code characteristics) → Select (appropriate modules) → Assemble (3 formats)
- **50% auto-fill rate** (architecture + integration modules fully auto-filled)
- **3 output formats:** Markdown + JSON Schema + JSDoc from single analysis
- **Drift detection:** Compares docs against actual code for accuracy
- **Performance:** < 5 seconds end-to-end generation

**3 Output Files:**
```
coderef/foundation-docs/
  AuthService-RESOURCE-SHEET.md     # Human-readable markdown
  AuthService-RESOURCE-SHEET.json   # Machine-readable JSON Schema
  AuthService-RESOURCE-SHEET.jsdoc  # JSDoc comments for code
```

---

## Error Handling

### Common Error Codes

**400 - Bad Request**
```json
{
  "error": {
    "code": "INVALID_ARGUMENTS",
    "message": "project_path is required",
    "details": "The project_path parameter must be provided and point to a valid directory"
  }
}
```

**404 - Not Found**
```json
{
  "error": {
    "code": "TEMPLATE_NOT_FOUND",
    "message": "Template 'invalid-name' does not exist",
    "details": "Valid template names: readme, architecture, api, components, schema, user-guide, my-guide"
  }
}
```

**500 - Server Error**
```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Failed to generate document: File write error",
    "details": "Permission denied: coderef/foundation-docs/API.md"
  }
}
```

### Error Response Format

All errors follow this structure:
```json
{
  "content": [
    {
      "type": "text",
      "text": "❌ Error: {error_message}\n\nDetails: {error_details}\n\nSuggested Fix: {suggestion}"
    }
  ],
  "isError": true
}
```

---

## Tool Orchestration Workflows

### Workflow 1: Complete Documentation Suite

```python
# Step 1: Health check
list_templates()
# Shows: MCP ✅ Available

# Step 2: Foundation docs (with drift check)
generate_foundation_docs(
    project_path="/path/to/project",
    auto_validate=True
)
# Generates: README, ARCHITECTURE, API, SCHEMA, COMPONENTS

# Step 3: User docs (75%+ auto-fill)
generate_my_guide(project_path="/path/to/project")
generate_user_guide(project_path="/path/to/project")
generate_features(project_path="/path/to/project")
# Generates: my-guide, USER-GUIDE, FEATURES
```

### Workflow 2: Standards Compliance Pipeline

```python
# Step 1: Extract standards (with MCP patterns)
establish_standards(
    project_path="/path/to/project",
    scan_depth="standard",
    auto_validate=True
)
# Output: 80%+ quality standards

# Step 2: Full compliance audit
audit_codebase(
    project_path="/path/to/project",
    generate_fixes=True
)
# Output: Compliance score + fix suggestions

# Step 3: Pre-commit gate (CI/CD)
check_consistency(
    project_path="/path/to/project",
    fail_on_violations=True,
    severity_threshold="major"
)
# Exit code: 0 (pass) or 1 (fail)
```

### Workflow 3: Feature Completion Workflow

```python
# After completing feature implementation

# Step 1: Record changes (agentic, git auto-detect)
record_changes(
    project_path="/path/to/project",
    version="1.0.3"
)
# Auto-detects: files, commits, suggests entry

# Step 2: Update foundation docs (with drift check)
generate_foundation_docs(
    project_path="/path/to/project",
    auto_validate=True
)
# Checks drift, generates 5 docs

# Step 3: Validate outputs
validate_document(
    document_path="/path/to/project/coderef/foundation-docs/API.md",
    doc_type="api"
)
# Score: 95/100
```

---

## MCP Integration (v4.0.0)

### Drift Detection

Automatic staleness checking before documentation generation:

```
✅ Drift Check: Index is up to date (drift: 5%, severity: none)
⚠️  Drift Check: Moderate drift detected (drift: 25%, severity: standard)
❌ Drift Check: Severe drift detected (drift: 75%, severity: severe)
```

**Severity Levels:**
- **none:** ≤10% drift → OK to proceed
- **standard:** >10%, ≤50% drift → Warning, consider re-scanning
- **severe:** >50% drift → Error, must re-scan

**Action Required:**
```bash
# If drift detected, re-scan project:
coderef_scan /path/to/project

# Then retry documentation generation
generate_foundation_docs /path/to/project
```

### Health Check System

`list_templates` displays MCP integration status:

```
🔧 MCP INTEGRATION STATUS:

  • coderef-context MCP: ✅ Available
  • Enhanced Features: Drift detection, pattern analysis, semantic insights

Performance:
  • Drift check: < 50ms
  • Pattern fetch: ~500ms
  • Cache hit rate: 70%+
```

**When MCP Unavailable:**
```
🔧 MCP INTEGRATION STATUS:

  ⚠️  coderef-context MCP: Unavailable

  Running in template-only mode:
  • No drift detection
  • No semantic pattern analysis
  • Reduced standards quality (55% vs 80%+)

  To enable MCP features:
  1. Ensure coderef-context MCP server is running
  2. Check ~/.mcp.json configuration
  3. Restart Claude Code
```

### Semantic Pattern Analysis

`establish_standards` uses MCP for 80%+ quality:

```
📊 Pattern Analysis Results (MCP)

Frequency Tracking:
  • async_function: 45 occurrences ✅ Common pattern
  • class_definition: 23 occurrences ✅ Established
  • test_function: 67 occurrences ✅ Well-tested
  • mcp_handler: 12 occurrences ⚠️  Emerging pattern

Consistency Violations (3):
  1. handlers.py:150
     Pattern: async_function
     Issue: Missing await keyword
     Fix: Add await to Promise-returning call

  2. utils.py:75
     Pattern: class_definition
     Issue: Missing docstring
     Fix: Add class-level docstring

  3. tests/test_api.py:200
     Pattern: test_function
     Issue: Inconsistent naming (uses snake_case, expected camelCase)
     Fix: Rename test_myFunction → testMyFunction

Quality: 85% (with MCP patterns) vs 55% (regex-only fallback)
```

---

## Performance Benchmarks

| Operation | Performance | Target | Status |
|-----------|-------------|--------|--------|
| list_templates | < 50ms | < 100ms | ✅ Exceeded |
| get_template | < 10ms | < 50ms | ✅ Exceeded |
| Drift check | < 50ms | < 100ms | ✅ Exceeded |
| generate_foundation_docs | ~8-10s | < 15s | ✅ Met |
| generate_my_guide | ~2s | < 5s | ✅ Exceeded |
| generate_user_guide | ~3s | < 5s | ✅ Met |
| generate_features | ~2s | < 5s | ✅ Exceeded |
| establish_standards (MCP) | ~3s | < 5s | ✅ Met |
| establish_standards (fallback) | 5-60s | N/A | ⚠️  Slow |
| audit_codebase | ~5-15s | < 30s | ✅ Met |
| check_consistency | ~1-3s | < 5s | ✅ Met |
| generate_resource_sheet | < 5s | < 10s | ✅ Exceeded |

**Test Environment:**
- Project: coderef-docs (21,344 elements)
- Hardware: Standard development machine
- .coderef/ availability: Present

---

## Examples

### Example 1: Generate Complete Documentation

```bash
# Check MCP status
mcp-call list_templates

# Output:
# 🔧 MCP INTEGRATION STATUS:
#   • coderef-context MCP: ✅ Available

# Generate all foundation docs
mcp-call generate_foundation_docs \
  --project-path /path/to/project \
  --auto-validate true

# Generate all user docs
mcp-call generate_my_guide --project-path /path/to/project
mcp-call generate_user_guide --project-path /path/to/project
mcp-call generate_features --project-path /path/to/project
```

### Example 2: Establish & Audit Standards

```bash
# Extract standards with MCP patterns
mcp-call establish_standards \
  --project-path /path/to/project \
  --scan-depth standard \
  --auto-validate true

# Full compliance audit
mcp-call audit_codebase \
  --project-path /path/to/project \
  --generate-fixes true

# Pre-commit consistency check
mcp-call check_consistency \
  --project-path /path/to/project \
  --severity-threshold major \
  --fail-on-violations true
```

### Example 3: Record Feature Completion

```bash
# Smart changelog recording (agentic)
mcp-call record_changes \
  --project-path /path/to/project \
  --version 1.0.3

# AI will:
# 1. Detect: git diff --staged
# 2. Suggest: change_type, severity, title
# 3. Confirm: Show preview for approval
# 4. Create: Write to CHANGELOG.json
```

---

## References

- **[README.md](../../README.md)** - User-facing guide (v4.0.0)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[INTEGRATION.md](../../INTEGRATION.md)** - MCP integration guide (NEW in v4.0.0)
- **[CLAUDE.md](../../CLAUDE.md)** - AI context documentation (v4.0.0)
- **[DELIVERABLES.md](../../DELIVERABLES.md)** - WO-GENERATION-ENHANCEMENT-001 completion report
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official MCP protocol

---

**Generated by:** coderef-docs v4.0.0
**Last Updated:** 2026-01-13
**Workorder:** WO-GENERATION-ENHANCEMENT-001
**MCP Integration:** ✅ Enabled (drift detection, semantic patterns, health check)
