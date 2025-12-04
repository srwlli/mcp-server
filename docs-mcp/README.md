# docs-mcp

**Enterprise-Grade MCP Server for Documentation Generation**

**Version:** 1.11.0 | **Date:** 2025-10-21 | **Maintainers:** willh, Claude Code AI

---

## Overview

**docs-mcp** is a production-ready Model Context Protocol (MCP) server that provides AI assistants with professional documentation generation, changelog management, codebase consistency auditing, universal quickref generation, implementation planning workflow, automatic deliverables tracking, **multi-agent task coordination**, **feature archiving**, **global workorder tracking**, and comprehensive project inventory analysis. Built with enterprise-grade patterns, it offers **36 specialized tools** with comprehensive logging, type safety, and security hardening.

### What It Does

- **Documentation Generation**: Create professional README, ARCHITECTURE, API, COMPONENTS, SCHEMA, and USER-GUIDE documents using POWER framework templates
- **Universal Quickref Generation**: AI-assisted interview workflow to create scannable 150-250 line quickref guides for ANY application (CLI, Web, API, Desktop, Library)
- **Changelog Management**: Maintain structured, schema-validated changelogs with agent-friendly tooling
- **Consistency Management**: Establish baseline standards and audit codebases for UI/UX/behavior violations
- **Planning Workflow**: AI-assisted implementation planning with automated analysis, validation, and iterative review loops
- **Deliverables Tracking**: Automatic DELIVERABLES.md generation with git metrics (LOC, commits, time) - NEW in v1.6.0
- **Multi-Agent Coordination**: Parallel agent execution with automated verification and integrated deliverables tracking - NEW in v1.9.0
- **Agent Handoff Automation**: Auto-generate comprehensive handoff context files in under 5 minutes (vs 20-30 min manual) - **NEW in v1.12.0**
- **Feature Archiving**: Automated archiving of completed features with status checking and searchable index - NEW in v1.10.0
- **Agentic Workflows**: Enable AI agents to self-document changes, maintain code quality, and create high-quality plans
- **Production-Ready**: Full logging, error handling, type hints, and security features

### Key Features

✅ **37 MCP Tools** - Complete toolkit for documentation, changelog, consistency, quickref generation, planning workflow, deliverables tracking, **multi-agent coordination**, **agent handoff automation**, **feature archiving**, **workorder tracking**, and comprehensive project inventory (files, dependencies, APIs, databases, configurations)
✅ **40 Slash Commands** - Quick access to common workflows via `/command` syntax
✅ **Reference Commands** - `/list-tools` (53 tools across 3 servers) and `/list-commands` with Unicode box art display
✅ **Workorder Tracking** - Automatic unique ID assignment for all features in MCP planning workflow (NEW in v1.5.0)
✅ **Deliverables Tracking** - Automatic DELIVERABLES.md generation with git-based metrics (LOC, commits, time) (NEW in v1.6.0)
✅ **Multi-Agent Coordination** - First MCP server with native parallel agent execution and automated verification (NEW in v1.9.0)
✅ **Feature Archive System** - Automated archiving with status checking, user confirmation, and searchable index tracking (NEW in v1.10.0)
✅ **Modular Architecture** - Handler registry pattern with 97% reduction in main dispatcher (407 → 13 lines)
✅ **Enterprise Patterns** - ErrorResponse factory, TypedDict type hints, enum constants, comprehensive logging
✅ **Security Hardened** - Path traversal protection, schema validation, input sanitization, audit trails
✅ **POWER Framework** - Structured templates ensure comprehensive documentation
✅ **Changelog Trilogy** - Read, write, and instruct pattern for changelog management
✅ **Multi-Project Support** - Generic design works with any project

### Architecture Highlights (v1.0.7)

🏗️ **Modular Design**: Tool handlers separated into `tool_handlers.py` with registry pattern
🎯 **Type Safety**: Full TypedDict coverage for all complex return types
📊 **Observability**: Structured logging with security audit trails and performance monitoring
🛡️ **Error Handling**: Consistent ErrorResponse factory for all error scenarios
🔧 **Maintainability**: 59% reduction in server.py size (644 → 264 lines)

### Security & Quality

🔒 **SEC-001**: Path traversal protection - All paths canonicalized with `.resolve()`
🔒 **SEC-002**: JSON schema validation - Automatic validation on all changelog operations
🔒 **SEC-003**: Smart output routing - README → root, others → `coderef/foundation-docs/`
🔒 **SEC-005**: Template sanitization - Regex validation prevents path traversal
📊 **ARCH-003**: Comprehensive logging - All operations logged to stderr (MCP-safe)
🎯 **QUA-001**: Type hints - Full TypedDict coverage for IDE support
🔧 **QUA-002**: Modular handlers - Each tool independently testable
🎨 **QUA-003**: Enum constants - Zero magic strings throughout codebase

---

## Prerequisites

Before using docs-mcp, ensure you have:

- **Python 3.10+** - Required for MCP server
- **MCP-compatible AI client** - Claude Code CLI, Cursor, Windsurf, or VS Code with MCP support
- **pip package manager** - For installing Python dependencies

### Verify Requirements

```bash
# Check Python version
python --version
# Should show: Python 3.10.x or higher

# Check MCP capability
claude mcp list
```

---

## Installation

### Quick Install (Claude Code)

```bash
# Add docs-mcp as a user-scoped MCP server (globally accessible to all CLI instances)
claude mcp add --scope user docs-mcp python "C:\Users\willh\.mcp-servers\docs-mcp\server.py"
```

**Expected Output:**
```
Added stdio MCP server docs-mcp with command: python C:\Users\willh\.mcp-servers\docs-mcp\server.py to user config
```

**Note**: The `--scope user` flag ensures docs-mcp is available globally to all Claude CLI instances, not just the current session.

### Manual Installation (Other IDEs)

**For Cursor:**
Edit `C:\Users\<username>\.cursor\mcp.json`:
```json
{
  "mcpServers": {
    "docs-mcp": {
      "command": "python",
      "args": ["C:\\Users\\willh\\.mcp-servers\\docs-mcp\\server.py"]
    }
  }
}
```

**For Windsurf/VS Code:**
Similar configuration in IDE-specific MCP config file.

### Verify Installation

```bash
claude mcp list
```

**Expected Output:**
```
docs-mcp: python C:\Users\willh\.mcp-servers\docs-mcp\server.py - ✓ Connected
```

---

## Available Tools

### Documentation Generation Tools (4)

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `list_templates` | List available POWER templates | None |
| `get_template` | Get template content | `template_name` |
| `generate_foundation_docs` | Generate 5 foundation docs | `project_path` |
| `generate_individual_doc` | Generate single document | `project_path`, `template_name` |

### Agent Handoff Tool (1) **NEW in v1.12.0**

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `generate_handoff_context` | Auto-generate agent handoff context files from plan.json, analysis.json, and git history | `project_path`, `feature_name`, `mode` (optional: "full" or "minimal") |

**Reduces agent handoff time from 20-30 minutes to under 5 minutes** by automatically extracting context from existing project files.

### Changelog Management Tools (3)

| Tool | Purpose | Pattern | Required Parameters |
|------|---------|---------|---------------------|
| `get_changelog` | Query changelog history | **READ** | `project_path` |
| `add_changelog_entry` | Add changelog entry | **WRITE** | `project_path`, `version`, `change_type`, `severity`, `title`, `description`, `files`, `reason`, `impact` |
| `update_changelog` | Agentic workflow guide | **INSTRUCT** | `project_path`, `version` |

### Universal Quickref Generation (1)

| Tool | Purpose | Pattern | Required Parameters |
|------|---------|---------|---------------------|
| `generate_quickref_interactive` | AI-driven interview to create scannable quickref.md for any app type | **INTERACTIVE** | `project_path` |

**Workflow**: AI asks 9 interview questions → User answers in plain English → AI generates quickref.md (150-250 lines) following universal 8-section pattern → Saves to `coderef/quickref.md`

**Supported App Types**: CLI, Web App, API, Desktop App, Library/Framework

### Consistency Management Tools (3)

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `establish_standards` | Scan codebase and document UI/UX/behavior patterns | **ONCE** per project to create baseline | `project_path` |
| `audit_codebase` | Audit code against established standards | **PERIODICALLY** (weekly/monthly) or before releases | `project_path` |
| `check_consistency` | Quick consistency check on modified files (pre-commit gate) | **BEFORE COMMITS** - Run on staged files only | `project_path` |

**The Consistency Trilogy:**
1. **establish_standards** (Tool #8) - Document what's standard in your codebase
2. **audit_codebase** (Tool #9) - Find violations of those standards
3. **check_consistency** (Tool #10) - Quality gate for new code

### Deliverables Tracking Tools (2)

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `generate_deliverables_template` | Generate DELIVERABLES.md template from plan.json | **AUTOMATIC** - Called by /create-plan workflow | `project_path`, `feature_name` |
| `update_deliverables` | Update DELIVERABLES.md with git metrics (LOC, commits, time) | **AFTER IMPLEMENTATION** - Run after feature completion | `project_path`, `feature_name` |

**Deliverables Workflow**:
1. `/create-plan` - Automatically generates both plan.json and DELIVERABLES.md template
2. **Implement feature** - Code your feature, commit with feature name in messages
3. `/update-deliverables` - Parses git history to calculate actual metrics (LOC, commits, time)

**Git Integration**:
- Searches commit messages for feature name (case-insensitive)
- Calculates LOC from `git diff --stat`
- Counts commits with `git log --grep`
- Measures time from first to last commit timestamp

### Planning Workflow Tools (6)

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `get_planning_template` | Get planning template sections | **REFERENCE** - View template structure before planning | None (or `section` for specific section) |
| `gather_context` | Gather feature requirements and assign workorder ID | **STEP 0** - Before analyzing project | `project_path`, `feature_name` |
| `analyze_project_for_planning` | Analyze project for planning context | **STEP 1** - Before creating implementation plan | `project_path` (optional: `feature_name` to save) |
| `create_plan` | Generate implementation plan from context and analysis | **STEP 2** - After gathering context and analysis | `project_path`, `feature_name` |
| `validate_implementation_plan` | Validate plan quality with 0-100 scoring | **STEP 2** - After creating plan draft | `project_path`, `plan_file_path` |
| `generate_plan_review_report` | Generate markdown review report | **STEP 3** - After validation for review | `project_path`, `plan_file_path`, `output_path` |

**Planning Workflow Pattern:**
1. **gather_context** (optional) - Collect feature requirements → assigns workorder ID (WO-{FEATURE-NAME}-001) → saves to context.json
2. **analyze_project_for_planning** - Discover foundation docs, standards, patterns (optionally save to feature folder) → automates section 0 (Preparation) → preserves workorder
3. **create_plan** - Generate implementation plan → embeds workorder in section 5 → all tasks reference workorder
4. **validate_implementation_plan** - Score plan (0-100) with issue detection → validates workorder consistency → iterate until score ≥ 90
5. **generate_plan_review_report** - Format validation results as markdown for user review
6. **User approval gate** - User must approve plan before execution (MANDATORY)
7. **Execute implementation** - Follow approved plan step-by-step

### Project Inventory Tools (7)

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `inventory_manifest` | Generate comprehensive file inventory with metadata | **ONBOARDING** - Understand project structure, or **ANALYSIS** - Track project evolution | `project_path` |
| `dependency_inventory` | Analyze dependencies across ecosystems with security scanning | **SECURITY AUDIT** - Find vulnerabilities, or **DEPENDENCY REVIEW** - Track outdated packages | `project_path` |
| `api_inventory` | Discover API endpoints across multiple frameworks (FastAPI, Flask, Express, GraphQL) | **API DOCUMENTATION** - Catalog endpoints, or **COVERAGE ANALYSIS** - Track documentation gaps | `project_path` |
| `database_inventory` | Discover database schemas across multiple systems (PostgreSQL, MySQL, MongoDB, SQLite) | **SCHEMA DOCUMENTATION** - Catalog tables/collections, or **MIGRATION AUDIT** - Track schema definitions | `project_path` |
| `config_inventory` | Discover and analyze configuration files with sensitive value detection | **SECURITY AUDIT** - Find exposed credentials, or **CONFIG REVIEW** - Catalog configuration | `project_path` |
| `test_inventory` | Discover test files and analyze coverage metrics | **TEST COVERAGE** - Identify gaps, or **QUALITY AUDIT** - Track test infrastructure | `project_path` |
| `documentation_inventory` | Discover and analyze documentation files with quality metrics | **DOCS AUDIT** - Track freshness and coverage | `project_path` |
| `config_inventory` | Discover and analyze configuration files across formats (JSON, YAML, TOML, INI, ENV) with sensitive value detection | **SECURITY AUDIT** - Find exposed credentials, or **CONFIG REVIEW** - Catalog configuration files | `project_path` |

#### File Inventory (`inventory_manifest`)

**What it captures:**
- **File metadata**: path, name, size, lines, category, risk level, language
- **Project metrics**: total files/size/lines, category distribution, risk distribution, language breakdown
- **Dependencies**: Detected imports for Python and JavaScript/TypeScript files
- **Universal taxonomy**: 7 file categories (core, source, template, config, test, docs, unknown)
- **Risk scoring**: 4 levels (low, medium, high, critical) based on category, size, complexity, sensitivity

**Analysis depth options:**
- `quick` - Basic file enumeration (~1-2 seconds, 500+ files/sec)
- `standard` - Full metadata + dependencies (~3-5 seconds, 200+ files/sec)
- `deep` - Standard + complexity analysis (~10-15 seconds, 50+ files/sec)

**Output**: `coderef/inventory/manifest.json` - JSON manifest with file metadata and project metrics

#### Dependency Inventory (`dependency_inventory`)

**What it captures:**
- **Multi-ecosystem support**: npm (Node.js), pip (Python), cargo (Rust), composer (PHP)
- **Dependency analysis**: Direct, dev, peer, and transitive dependencies
- **Security scanning**: Vulnerability detection via OSV API (all ecosystems)
- **Version tracking**: Current vs latest versions from package registries
- **License detection**: Identify dependency licenses
- **Comprehensive metrics**: Total deps, outdated count, vulnerable count, severity breakdown

**Features:**
- **Security vulnerabilities**: CVE IDs, severity (critical/high/medium/low), CVSS scores, fix versions
- **Outdated detection**: Compare installed vs latest versions
- **Metrics calculation**: Aggregated stats by ecosystem, type, severity
- **Schema validation**: JSON schema ensures manifest integrity

**Output**: `coderef/inventory/dependencies.json` - JSON manifest with dependency metadata and security findings

#### API Inventory (`api_inventory`)

**What it captures:**
- **Multi-framework support**: FastAPI, Flask, Express.js, GraphQL
- **Endpoint metadata**: Path, HTTP method, function name, file location, line number
- **Documentation coverage**: Percentage of documented vs undocumented endpoints
- **OpenAPI/Swagger parsing**: Extracts endpoint docs from spec files
- **Parameter detection**: Function parameters for each endpoint
- **Framework breakdown**: Endpoints by framework type
- **Method distribution**: Endpoints by HTTP method (GET, POST, PUT, DELETE, etc.)

**Detection methods:**
- **AST parsing**: Python decorators (@app.get, @app.route)
- **Regex extraction**: Express.js route definitions (app.get, app.post)
- **GraphQL schema parsing**: Query and Mutation type analysis
- **OpenAPI/Swagger**: YAML/JSON specification parsing

**Output**: `coderef/inventory/api.json` - JSON manifest with endpoint metadata and coverage metrics

#### Database Inventory (`database_inventory`)

**What it captures:**
- **Multi-database support**: PostgreSQL, MySQL, MongoDB, SQLite
- **Schema metadata**: Table/collection name, type (table/collection), database type (sql/nosql)
- **Column/field definitions**: Data types, constraints, defaults
- **ORM detection**: SQLAlchemy, Sequelize, Mongoose models
- **Migration parsing**: Alembic and Knex.js migration files
- **Relationship mapping**: Foreign keys, ORM relationships (one-to-one, one-to-many, many-to-many)
- **Index tracking**: Database indexes with uniqueness flags
- **System breakdown**: Schema count by database system and ORM/source

**Detection methods:**
- **AST parsing**: SQLAlchemy ORM models (Python `class` with `__tablename__`)
- **Regex extraction**: Sequelize models (Node.js), Mongoose schemas (Node.js)
- **Migration parsing**: Alembic migrations (`op.create_table`), Knex.js migrations

**Output**: `coderef/inventory/database.json` - JSON manifest with schema metadata and database metrics

### Workorder Tracking Tools (2) **NEW in v1.11.0**

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `log_workorder` | Log new workorder entry to global log file | **AFTER COMPLETION** - Log finished workorders for traceability | `project_path`, `workorder_id`, `project_name`, `description` |
| `get_workorder_log` | Query global workorder log with filters | **ANYTIME** - View workorder history or search by project/pattern | `project_path` (optional: `project_name`, `workorder_pattern`, `limit`) |

**Global Workorder Log:**
- Simple one-line format: `WO-ID | Project | Description | Timestamp`
- Latest entries at top (reverse chronological)
- Saved to: `coderef/workorder-log.txt`
- Auto-truncation at 50 chars for readability
- Workorder ID validation: `^WO-[A-Z0-9-]+-\d{3}$`

**Example log entries:**
```
WO-WORKORDER-LOG-001 | docs-mcp | Implement workorder logging system (2 tools, pr... | 2025-10-21T02:08:51+00:00
WO-AUTH-001 | personas-mcp | Auth system workorder | 2025-10-21T01:45:20+00:00
```

**Use cases:**
- Track workorder completion across projects
- Maintain global activity log
- Quick visibility into recent work
- Integration with planning workflows
- Traceability for feature implementation

**Slash command shortcuts:**
- `/log-workorder` - Interactive prompt for logging new entry
- `/get-workorder-log` - Interactive query with optional filters

---

### Multi-Agent Coordination Tools (5) **NEW in v1.9.0**

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `generate_agent_communication` | Generate communication.json from plan.json | **AFTER PLANNING** - Create coordination file for parallel agents | `project_path`, `feature_name` |
| `assign_agent_task` | Assign task to specific agent with workorder scoping | **BEFORE WORK** - Assign agent 2, 3, etc. with unique workorder | `project_path`, `feature_name`, `agent_number` (1-10) |
| `verify_agent_completion` | Verify agent work with automated checks | **AFTER WORK** - Validate forbidden files unchanged and success criteria met | `project_path`, `feature_name`, `agent_number` |
| `aggregate_agent_deliverables` | Combine metrics from multiple agent DELIVERABLES.md files | **FINAL STEP** - Generate combined deliverables report | `project_path`, `feature_name` |
| `track_agent_status` | Track agent status across features with real-time dashboard | **ANYTIME** - Monitor agent progress and detect blockers | `project_path` (optional: `feature_name`) |

**Multi-Agent Coordination Workflow:**
1. **create_plan** with `multi_agent=True` - Generates plan.json + communication.json automatically
2. **assign_agent_task** - Assign Agent 2 to phase_0, Agent 3 to phase_1, etc.
   - Each agent gets unique workorder ID (WO-FEATURE-002, WO-FEATURE-003)
   - Agent status: null → ASSIGNED → IN_PROGRESS → COMPLETE
3. **Parallel execution** - Multiple agents work simultaneously on different phases
4. **verify_agent_completion** - Automated verification with git diff on forbidden files
   - Validates success criteria from communication.json
   - Updates status to VERIFIED or VERIFICATION_FAILED
5. **aggregate_agent_deliverables** - Combines metrics (LOC, commits, time) from all agents
6. **track_agent_status** - Real-time dashboard shows overall workflow status

**Key Features:**
- ✅ **Agent-scoped workorder IDs** - WO-FEATURE-001, WO-FEATURE-002, WO-FEATURE-003
- ✅ **Automated verification** - Git diff validation, success criteria checks, blocker detection
- ✅ **Metrics aggregation** - Combines LOC, commits, contributors, time from multiple agents
- ✅ **Real-time tracking** - Dashboard with status counts (available, assigned, in_progress, complete, verified, blocked)
- ✅ **Forbidden files protection** - Prevents agents from modifying production files (server.py, tool_handlers.py)

**Performance:**
- 3x faster implementation through parallel agent execution
- <600ms total coordination overhead per complete workflow
- <100ms per status tracking operation

---

### Feature Management Tools (3) **NEW in v1.10.0+**

| Tool | Purpose | When to Use | Required Parameters |
|------|---------|-------------|---------------------|
| `archive_feature` | Archive completed features from working to archived directory | **AFTER COMPLETION** - Archive feature after running update-deliverables | `project_path`, `feature_name` |
| `update_all_documentation` | Update all docs (README, CLAUDE, CHANGELOG) with auto version bump | **BEFORE ARCHIVING** - Update docs after implementation | `project_path`, `change_type`, `feature_description`, `workorder_id` |
| `execute_plan` | Generate TodoWrite task list from plan.json with TASK-ID first format | **START IMPLEMENTATION** - Convert plan to executable checklist | `project_path`, `feature_name` |

**Feature Lifecycle:**
1. **create_plan** - Generate implementation plan
2. **execute_plan** - Convert to TodoWrite checklist
3. **Implementation** - Complete tasks
4. **update_deliverables** - Calculate metrics from git history
5. **update_all_documentation** - Auto-increment version and update docs
6. **archive_feature** - Move to archive with status checking


## Quick Start

### Generate Documentation for Your Project

```bash
# Ask Claude Code to generate all docs
"Generate foundation documentation for my project at C:\path\to\my-project"
```

This creates 5 foundation documents:
- **README.md** → `my-project/README.md` (project root)
- **ARCHITECTURE.md** → `my-project/coderef/foundation-docs/`
- **API.md** → `my-project/coderef/foundation-docs/`
- **COMPONENTS.md** → `my-project/coderef/foundation-docs/`
- **SCHEMA.md** → `my-project/coderef/foundation-docs/`

**Note:** USER-GUIDE.md is optional and generated separately using `generate_individual_doc`

### Maintain a Changelog

**Basic Workflow:**
```bash
# 1. Make code changes
# 2. Ask agent to document them
"Use update_changelog to document my changes for version 1.0.3"

# Agent will:
# - Analyze changes autonomously
# - Determine change type and severity
# - Call add_changelog_entry with details
# - Update CHANGELOG.json
```

**Manual Entry:**
```bash
# Add specific changelog entry
add_changelog_entry(
    project_path="C:/path/to/project",
    version="1.0.3",
    change_type="feature",
    severity="major",
    title="Added new feature X",
    description="Implemented X with capabilities Y and Z",
    files=["server.py", "lib/feature.py"],
    reason="Users requested ability to...",
    impact="Users can now...",
    contributors=["your_name"]
)
```

---

## Usage Examples

### Example 1: Generate Project Documentation

```python
# List available templates
list_templates()
# Returns: readme, architecture, api, components, schema, user-guide

# Generate all foundation documents
generate_foundation_docs(project_path="C:/Users/willh/my-project")

# Or generate just one document
generate_individual_doc(
    project_path="C:/Users/willh/my-project",
    template_name="api"
)
```

### Example 2: Query Changelog History

```python
# Get full changelog
get_changelog(project_path="C:/Users/willh/my-project")

# Get specific version
get_changelog(
    project_path="C:/Users/willh/my-project",
    version="1.0.2"
)

# Get all breaking changes
get_changelog(
    project_path="C:/Users/willh/my-project",
    breaking_only=true
)

# Filter by type
get_changelog(
    project_path="C:/Users/willh/my-project",
    change_type="feature"
)
```

### Example 3: Agentic Self-Documentation

```python
# Agent calls update_changelog
update_changelog(
    project_path="C:/Users/willh/my-project",
    version="1.0.3"
)

# Tool returns 3-step instructions:
# STEP 1: Analyze Your Changes
# STEP 2: Determine Change Details
# STEP 3: Call add_changelog_entry

# Agent analyzes context autonomously
# Agent executes add_changelog_entry(...)
# Changelog updated!
```

### Example 4: Audit Codebase for Consistency

```python
# Step 1: Establish baseline standards (run once)
establish_standards(
    project_path="C:/Users/willh/my-react-app",
    scan_depth="standard",  # quick | standard | deep
    focus_areas=["all"]      # ui_components, behavior_patterns, ux_flows, all
)
# Creates 4 standards documents in coderef/standards/

# Step 2: Audit codebase against standards (run periodically)
audit_codebase(
    project_path="C:/Users/willh/my-react-app",
    standards_dir="coderef/standards",  # default location
    severity_filter="all",               # critical | major | minor | all
    scope=["all"],                       # ui_patterns, behavior_patterns, ux_patterns, all
    generate_fixes=true                  # include fix suggestions
)

# Returns:
# - Compliance Score: 85/100 (B)
# - Violations: 12 total (0 critical, 5 major, 7 minor)
# - Audit report saved to: coderef/audits/AUDIT-REPORT-YYYY-MM-DD-HHmmss.md

# Step 3: Review report and fix violations
# Step 4: Re-run audit to verify improvements
```

### Example 5: Generate Project Inventory Manifest

```python
# Generate comprehensive file inventory
inventory_manifest(
    project_path="C:/Users/willh/my-project",
    analysis_depth="standard",  # quick | standard | deep
    exclude_dirs=["node_modules", ".git", "__pycache__"],  # Optional
    max_file_size=10485760  # Optional: 10MB limit
)

# Returns:
# {
#   "manifest_path": "coderef/inventory/manifest.json",
#   "files_analyzed": 247,
#   "project_name": "my-project",
#   "analysis_depth": "standard",
#   "metrics": {
#     "total_files": 247,
#     "total_size": 5242880,
#     "total_lines": 12543,
#     "file_categories": {
#       "source": 120,
#       "test": 45,
#       "config": 18,
#       "docs": 12,
#       "core": 8,
#       "template": 3,
#       "unknown": 41
#     },
#     "risk_distribution": {
#       "low": 180,
#       "medium": 45,
#       "high": 18,
#       "critical": 4
#     },
#     "language_breakdown": {
#       "python": 165,
#       "javascript": 35,
#       "markdown": 25,
#       "json": 22
#     }
#   },
#   "success": true
# }

# The manifest.json includes detailed metadata for each file:
# - File path, name, extension, size, lines
# - Category (core, source, template, config, test, docs, unknown)
# - Risk level (low, medium, high, critical)
# - Language and complexity
# - Dependencies (imports detected in Python/JS/TS files)
# - Last modified timestamp
```

**Use cases:**
- **Project Onboarding**: Understand structure and tech stack
- **Dependency Analysis**: Track import relationships
- **Risk Assessment**: Identify high-risk files requiring attention
- **Documentation**: Generate file inventory for documentation
- **Evolution Tracking**: Compare manifests over time to track growth

### Example 6: Analyze Project Dependencies with Security Scanning

```python
# Generate comprehensive dependency inventory with security scanning
dependency_inventory(
    project_path="C:/Users/willh/my-project",
    scan_security=True,          # Enable vulnerability scanning
    ecosystems=["all"],          # Analyze all detected ecosystems (npm, pip, cargo, composer)
    include_transitive=False     # Only direct and dev dependencies
)

# Returns:
# {
#   "manifest_path": "coderef/inventory/dependencies.json",
#   "package_managers": ["npm", "pip"],
#   "total_dependencies": 127,
#   "vulnerable_count": 3,
#   "outdated_count": 18,
#   "metrics": {
#     "total_dependencies": 127,
#     "direct_count": 45,
#     "dev_count": 82,
#     "outdated_count": 18,
#     "vulnerable_count": 3,
#     "critical_vulnerabilities": 0,
#     "high_vulnerabilities": 1,
#     "medium_vulnerabilities": 2,
#     "low_vulnerabilities": 0,
#     "ecosystem_breakdown": {
#       "npm": 85,
#       "pip": 42
#     }
#   },
#   "success": true
# }

# The dependencies.json manifest includes:
# - Complete dependency list by ecosystem and type
# - Security vulnerabilities with CVE IDs and severity levels
# - Latest versions and outdated indicators
# - License information
# - CVSS scores for vulnerabilities
# - Fix versions and references
```

**Use cases:**
- **Security Audits**: Find known vulnerabilities in dependencies
- **Dependency Management**: Track outdated packages
- **License Compliance**: Audit dependency licenses
- **Supply Chain Security**: Monitor dependency health
- **Update Planning**: Prioritize package updates by risk

**Security scanning features:**
- **OSV API Integration**: Queries Open Source Vulnerabilities database
- **Multi-ecosystem**: npm (Node.js), PyPI (Python), crates.io (Rust), Packagist (PHP)
- **Severity levels**: Critical, High, Medium, Low with CVSS scores
- **Fix guidance**: Identifies versions that fix vulnerabilities

### Example 7: Discover API Endpoints Across Multiple Frameworks

```python
# Generate comprehensive API inventory with documentation coverage analysis
api_inventory(
    project_path="C:/Users/willh/my-project",
    frameworks=["all"],          # Detect all frameworks: fastapi, flask, express, graphql
    include_graphql=False,       # Set to True to parse GraphQL schemas
    scan_documentation=True      # Parse OpenAPI/Swagger docs for coverage
)

# Returns:
# {
#   "manifest_path": "coderef/inventory/api.json",
#   "frameworks": ["fastapi", "flask"],
#   "total_endpoints": 48,
#   "documented_endpoints": 32,
#   "documentation_coverage": 67,
#   "metrics": {
#     "total_endpoints": 48,
#     "documented_endpoints": 32,
#     "documentation_coverage": 67,
#     "frameworks_detected": ["fastapi", "flask"],
#     "framework_breakdown": {
#       "fastapi": 35,
#       "flask": 13
#     },
#     "method_breakdown": {
#       "GET": 22,
#       "POST": 15,
#       "PUT": 7,
#       "DELETE": 4
#     },
#     "rest_endpoints": 48,
#     "graphql_endpoints": 0
#   },
#   "success": true
# }

# The api.json manifest includes detailed metadata for each endpoint:
# - Endpoint path (e.g., /api/users/{id})
# - HTTP method (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
# - Framework (fastapi, flask, express, graphql)
# - File location and line number
# - Function name and parameters
# - Documentation status and coverage score (0-100)
# - OpenAPI/Swagger metadata (description, summary, tags, deprecated flag)
```

**Use cases:**
- **API Documentation**: Generate comprehensive endpoint catalog
- **Documentation Coverage**: Track which endpoints lack documentation
- **API Auditing**: Identify undocumented or deprecated endpoints
- **Framework Migration**: Understand endpoint distribution before refactoring
- **OpenAPI Compliance**: Verify all endpoints have OpenAPI/Swagger docs

**Framework detection methods:**
- **AST parsing**: Python decorators (@app.get, @app.route)
- **Regex extraction**: Express.js route definitions (app.get, app.post)
- **GraphQL schema parsing**: Query and Mutation type analysis
- **OpenAPI/Swagger**: YAML/JSON specification parsing

### Example 8: Discover Database Schemas Across Multiple Systems

```python
# Generate comprehensive database schema inventory
database_inventory(
    project_path="C:/Users/willh/my-project",
    database_systems=["all"],      # Detect all systems: postgresql, mysql, mongodb, sqlite
    include_migrations=True         # Parse migration files for schema definitions
)

# Returns:
# {
#   "manifest_path": "coderef/inventory/database.json",
#   "database_systems": ["postgresql", "mongodb"],
#   "total_schemas": 15,
#   "sql_tables": 12,
#   "nosql_collections": 3,
#   "metrics": {
#     "total_schemas": 15,
#     "sql_tables": 12,
#     "nosql_collections": 3,
#     "database_systems_detected": ["postgresql", "mongodb"],
#     "system_breakdown": {
#       "postgresql": 12,
#       "mongodb": 3
#     },
#     "orm_breakdown": {
#       "sqlalchemy": 8,
#       "alembic_migration": 4,
#       "mongoose": 3
#     },
#     "total_columns": 87,
#     "total_relationships": 23
#   },
#   "success": true
# }

# The database.json manifest includes detailed metadata for each schema:
# - Table/collection name and type (table, collection)
# - Database type (sql, nosql)
# - ORM/source (sqlalchemy, sequelize, mongoose, alembic_migration, knex_migration)
# - File location and line number
# - Class name (for ORM models)
# - Columns (for SQL): name, type, nullable, primary_key, unique, foreign_key, default
# - Fields (for NoSQL): name, type, required, default
# - Relationships: name, related_table, type (one-to-one, one-to-many, many-to-many)
# - Indexes: name, columns, unique flag
# - Constraints (SQL): primary_key, foreign_key, unique, check
# - Validators (NoSQL): schema validation rules
```

**Use cases:**
- **Database Documentation**: Generate comprehensive schema catalog
- **Schema Discovery**: Understand database structure across multiple systems
- **Migration Auditing**: Track schema definitions from ORM models and migrations
- **Multi-Database Projects**: Analyze projects using SQL and NoSQL together
- **Schema Validation**: Verify all tables/collections are documented

**Database system support:**
- **PostgreSQL**: SQLAlchemy models, Alembic migrations
- **MySQL**: SQLAlchemy models, Alembic migrations
- **MongoDB**: Mongoose schemas (Node.js)
- **SQLite**: SQLAlchemy models

**ORM detection methods:**
- **AST parsing**: SQLAlchemy models (Python `class` with `__tablename__`)
- **Regex extraction**: Sequelize models (Node.js), Mongoose schemas (Node.js)
- **Migration parsing**: Alembic migrations (`op.create_table`), Knex migrations

---

## Project Structure

```
docs-mcp/
├── server.py                    # MCP server entry (264 lines, -59% from refactor)
├── tool_handlers.py            # 7 tool handlers + registry (516 lines)
├── error_responses.py          # ErrorResponse factory (ARCH-001)
├── type_defs.py                # TypedDict definitions (QUA-001)
├── logger_config.py            # Structured logging (ARCH-003)
├── constants.py                # Paths, Files, enums (REF-002, QUA-003)
├── validation.py               # Input validation layer (REF-003)
├── generators/
│   ├── base_generator.py         # Base template generator
│   ├── foundation_generator.py   # Multi-doc generator
│   ├── changelog_generator.py    # Changelog CRUD with schema validation
│   ├── standards_generator.py    # Codebase standards discovery (Tool #8)
│   └── audit_generator.py        # Standards compliance auditing (Tool #9)
├── templates/power/              # POWER framework templates
│   ├── readme.txt
│   ├── architecture.txt
│   ├── api.txt
│   ├── components.txt
│   ├── schema.txt
│   └── user-guide.txt
├── coderef/
│   ├── changelog/                # Changelog system
│   │   ├── CHANGELOG.json       # Structured changelog data
│   │   └── schema.json          # JSON schema validation
│   ├── standards/                # Codebase standards (Tool #8 output)
│   │   ├── UI-STANDARDS.md      # UI component patterns
│   │   ├── BEHAVIOR-STANDARDS.md # Behavior patterns
│   │   ├── UX-PATTERNS.md       # UX and accessibility patterns
│   │   └── COMPONENT-INDEX.md   # Component inventory
│   ├── audits/                   # Compliance audit reports (Tool #9 output)
│   │   └── AUDIT-REPORT-*.md    # Timestamped audit reports
│   ├── inventory/                # Project inventory (Tool #14 output)
│   │   ├── manifest.json        # Comprehensive file inventory
│   │   └── schema.json          # JSON schema validation
│   ├── foundation-docs/          # Generated documentation
│   └── quickref.md              # Quick reference guide
├── CLAUDE.md                   # AI assistant context documentation
├── user-guide.md               # Comprehensive user guide
└── test_security_fixes.py      # Security test suite
```

---

## Troubleshooting

### Issue: "No such tool available: mcp__docs-mcp__*"

**Symptom:** MCP tools not found after adding server

**Cause:** MCP server not restarted or not properly registered

**Resolution:**
```bash
# 1. Verify server is registered
claude mcp list

# 2. If not listed, re-add with user scope for global access
claude mcp add --scope user docs-mcp python "C:\Users\willh\.mcp-servers\docs-mcp\server.py"

# 3. Restart Claude Code or IDE
```

---

### Issue: "Invalid project path"

**Symptom:** Error when calling tools with project_path parameter

**Cause:** Using relative path instead of absolute path

**Resolution:**
```bash
# ❌ Wrong: Relative path
generate_foundation_docs(project_path="./my-project")

# ✅ Correct: Absolute path
generate_foundation_docs(project_path="C:/Users/willh/my-project")
```

---

### Issue: "Changelog not found"

**Symptom:** get_changelog or add_changelog_entry fails

**Cause:** No changelog exists at `project_path/coderef/changelog/CHANGELOG.json`

**Resolution:**
```bash
# add_changelog_entry automatically creates changelog structure
# Just call it with your first entry:
add_changelog_entry(
    project_path="C:/path/to/project",
    version="1.0.0",
    change_type="feature",
    severity="major",
    title="Initial release",
    description="Created project with...",
    files=["*"],
    reason="Initial development",
    impact="Project created"
)
```

---

### Issue: Generated docs are generic

**Symptom:** Documentation doesn't mention specific project features

**Cause:** Minimal code in project or AI needs more context

**Resolution:**
1. Ensure project has actual implementation code
2. Add code comments explaining key features
3. Provide additional context to AI during generation
4. Manually enhance generated docs if needed

---

## The Changelog Trilogy Pattern

docs-mcp implements a unique **meta-tool pattern** for changelog management:

```
┌─────────────────────────────────────────┐
│ get_changelog (READ)                    │
│ Query changelog history                 │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ add_changelog_entry (WRITE)             │
│ Execute changelog update                │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ update_changelog (INSTRUCT)             │
│ Orchestrate agentic workflow            │
│ → Agent analyzes context                │
│ → Agent determines details              │
│ → Agent calls add_changelog_entry       │
└─────────────────────────────────────────┘
```

**Why This Matters:**
- **Separation of Concerns**: Read/write/orchestrate are distinct operations
- **Agentic Design**: Agents can self-document without explicit prompting
- **Flexibility**: Use WRITE directly or INSTRUCT for autonomous workflows

---

## Additional Resources

- **[user-guide.md](../user-guide.md)** - Comprehensive user guide with best practices
- **[coderef/quickref.md](../coderef/quickref.md)** - Quick reference for all 7 tools
- **[coderef/changelog/CHANGELOG.json](../coderef/changelog/CHANGELOG.json)** - Project changelog
- **[MCP-SETUP-GUIDE.md](../MCP-SETUP-GUIDE.md)** - General MCP server setup
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official MCP docs
- **[MCP Python SDK](https://github.com/anthropics/mcp-python)** - SDK documentation

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.12.0 | 2025-10-23 | **Agent Handoff Automation** - Auto-generate comprehensive agent handoff context files from plan.json, analysis.json, and git history, reducing handoff time from 20-30 minutes to under 5 minutes with 80%+ auto-population |
| 1.11.0 | 2025-10-21 | **Global Workorder Logging** - Simple one-line workorder tracking system for global activity log across projects with 2 new tools (log_workorder, get_workorder_log) |
| 1.10.0 | 2025-10-20 | **Feature Archive System** - Automated archiving of completed features from working to archived directory with status checking and searchable index tracking |
| 1.9.0 | 2025-10-19 | **Multi-Agent Coordination System** - Parallel agent execution with 5 new tools for task assignment, verification, deliverables aggregation, and status tracking |
| 1.6.0 | 2025-10-18 | **Deliverables Tracking System** - Automatic DELIVERABLES.md generation integrated into /create-plan workflow with git-based metrics (LOC, commits, time), template generation, and metrics update tools |
| 1.5.0 | 2025-10-18 | **Workorder Tracking System** - Automatic unique workorder ID assignment for all features in MCP planning workflow, cross-file persistence (context → analysis → plan → deliverables), and validation integration |
| 1.4.0 | 2025-10-11 | **Planning Workflow System** - Added 4 planning tools for AI-assisted implementation planning with automated analysis, validation (0-100 scoring), iterative review loops, and comprehensive integration tests (18/18 passing, 100%) |
| 1.3.0 | 2025-10-10 | **Consistency Trilogy Complete** - Added audit_codebase tool for compliance auditing with weighted scoring, comprehensive reports, and fix suggestions |
| 1.2.0 | 2025-10-10 | **Standards Discovery** - Added establish_standards tool for extracting UI/UX/behavior patterns |
| 1.0.9 | 2025-10-09 | **AI Context Docs** - Added CLAUDE.md for AI assistant guidance |
| 1.0.8 | 2025-10-09 | **Workflow Demo** - Demonstrated proper MCP changelog workflow |
| 1.0.7 | 2025-10-09 | **🏗️ Architecture Refactor** - Modular handlers, logging, type safety, error factory (5 major improvements) |
| 1.0.6 | 2025-10-09 | **Phase 2 Refactor** - Constants extraction, input validation layer |
| 1.0.5 | 2025-10-09 | JSON schema validation, README routing fix (SEC-002, SEC-003) |
| 1.0.4 | 2025-10-09 | **🔒 Security Fixes** - Path traversal protection, jsonschema dependency |
| 1.0.3 | 2025-10-09 | Added update_changelog agentic workflow tool |
| 1.0.2 | 2025-10-09 | Added changelog system (get_changelog, add_changelog_entry) |

See [CHANGELOG.json](coderef/changelog/CHANGELOG.json) for complete change history with detailed entries.

---

## Contributing

We welcome contributions! When making changes:

1. **Make your changes** to the codebase
2. **Test thoroughly** to ensure everything works
3. **Document your changes** using update_changelog:
   ```bash
   update_changelog(
       project_path="C:/Users/willh/.mcp-servers/docs-mcp",
       version="1.0.x"
   )
   ```
4. **Commit with clear message** describing what changed
5. **Submit pull request** with reference to changelog entry

---

## License

[Specify license here - MIT, Apache 2.0, etc.]

---

## AI Integration Footer

This MCP server is **optimized for AI assistant integration**. It provides:

- **Structured templates** that guide documentation generation with consistent quality
- **Decision trees** for content selection embedded in templates
- **Command sequences** for systematic documentation workflows
- **Agent-friendly tools** that enable autonomous self-documentation

**For AI Assistants**: Use the POWER framework templates to ensure comprehensive documentation. Follow the `work` section for systematic analysis and the `requirements` section for mandatory elements. The update_changelog tool demonstrates the meta-tool pattern for orchestrating agent workflows.

---

**🤖 Generated with docs-mcp v1.4.0**
**Maintained by**: willh, Claude Code AI
**Planning Workflow System**: 4/4 Tools Complete (analyze ✓, validate ✓, review ✓, template ✓)
**Integration Tests**: 18/18 Passing (100%)

