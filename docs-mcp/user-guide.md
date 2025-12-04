# docs-mcp User Guide

> **Automatically generate professional documentation for your code projects**
> Uses the POWER framework to create comprehensive, AI-optimized documentation

---

## Table of Contents

- [What is docs-mcp?](#what-is-docs-mcp)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Usage](#usage)
  - [Generate All 5 Foundation Docs](#generate-all-5-foundation-docs-new-project)
  - [Generate Single Doc](#generate-single-doc-update)
- [Output Structure](#output-structure)
- [Documentation Contents](#documentation-contents)
- [Planning Workflow Guide (Step-by-Step)](#planning-workflow-guide-step-by-step)
- [Slash Commands Quick Reference](#slash-commands-quick-reference)
- [Common Use Cases](#common-use-cases)
- [Best Practices](#best-practices)
- [Changelog Best Practices](#changelog-best-practices)
- [Troubleshooting](#troubleshooting)
- [Quick Reference](#quick-reference)

---

## What is docs-mcp?

**docs-mcp** is a Model Context Protocol (MCP) server that integrates with Claude Code to automatically generate foundation documentation for software projects.

### Key Features

✅ **5 Foundation Documents**: README, ARCHITECTURE, API, COMPONENTS, SCHEMA
✅ **Optional**: USER-GUIDE (generated separately, not part of foundation docs)
✅ **Planning Workflow System**: 4 tools for AI-assisted implementation planning
✅ **Structured Changelog**: JSON-based changelog with schema validation and MCP tools
✅ **Consistency Management**: Extract standards and audit codebase compliance
✅ **Template-Driven**: Uses POWER framework (Purpose, Output, Work, Examples, Requirements)
✅ **AI-Optimized**: Generated docs include context for AI assistants
✅ **Flexible**: Generate all docs or update individual files
✅ **Smart**: Analyzes your codebase to create specific, accurate documentation

### What Gets Generated

**Foundation Documentation (5 core files):**

1. **README.md** - Project overview, installation, usage
2. **ARCHITECTURE.md** - System design, topology, tech stack
3. **API.md** - Endpoints, interfaces, integration patterns
4. **COMPONENTS.md** - Reusable components with examples
5. **SCHEMA.md** - Data structures, types, validation rules

**Optional Documentation:**

6. **USER-GUIDE.md** - User onboarding, step-by-step tutorials
   *(Generated separately using `generate_individual_doc`, not part of foundation docs workflow)*

### Changelog System (NEW in v1.0.2)

docs-mcp includes a structured changelog system for tracking project changes:

- **`get_changelog`** - Query changelog history by version, type, or breaking changes
- **`add_changelog_entry`** - Programmatically add new changelog entries
- **JSON Schema Validation** - Ensures changelog data integrity
- **Agent-Friendly** - AI assistants can track project evolution and document their own changes

**Use cases:**
- Track all code changes with structured metadata
- Query project history to understand past decisions
- Automatically document changes as agents make them
- Filter by version, change type, or breaking changes

### Standards System (NEW in v1.2.0)

docs-mcp now includes a consistency management system for discovering and documenting codebase standards:

- **`establish_standards`** - Scan codebase to discover UI/UX/behavior patterns and generate standards documentation
- **Pattern Discovery** - Automated regex-based pattern analysis
- **4 Standards Documents** - UI-STANDARDS.md, BEHAVIOR-STANDARDS.md, UX-PATTERNS.md, COMPONENT-INDEX.md
- **Security Hardening** - Path traversal protection, symlink validation, file size limits

**Use cases:**
- Automatically discover existing UI/UX patterns in your codebase
- Document component standards without manual effort
- Establish baseline for consistency validation (Tools #9 and #10)
- Generate single source of truth for design patterns

**Scan Depths:**
- **quick** (~1-2 min) - Common patterns only
- **standard** (~3-5 min) - Comprehensive analysis (recommended)
- **deep** (~10-15 min) - Exhaustive with edge cases

**Focus Areas:**
- **ui_components** - Buttons, modals, forms, colors, typography
- **behavior_patterns** - Error handling, loading states, notifications
- **ux_flows** - Navigation, permissions, accessibility
- **all** - Complete analysis (recommended)

### Schema-First Planning (NEW in v1.1.0)

docs-mcp enforces **schema-first design** for implementation plans:

**Three-Layer Defense:**

| Layer | Tool | Action | On Failure |
|-------|------|--------|------------|
| Producer | `create_plan` | Shows schema contract to AI | N/A (preventive) |
| Validator | `schema_validator.py` | Normalizes any format | Logs warning, proceeds |
| Consumer | `generate_deliverables_template` | Uses helper functions | Graceful fallback |

**Schema Contract (Critical Structures):**
- `6_implementation_phases` - Use `phases: []` array (not `phase_1`, `phase_2` keys)
- `5_task_id_system` - Use `tasks: []` array (not `task_breakdown` dict)
- `files_to_create` - Use `[{path, purpose}]` objects (not strings)

**Helper Functions** (`schema_validator.py`):
- `get_phases(plan)` - Extracts phases from either format
- `get_tasks(plan)` - Extracts tasks from either format
- `get_files_to_create(plan)` - Normalizes strings to objects
- `get_workorder_id(plan)` - Safe extraction with fallback

### Planning Workflow System (NEW in v1.4.0)

docs-mcp now includes a comprehensive planning workflow system for AI-assisted implementation planning:

- **`gather_context`** - Interactive requirements gathering (saves to feature folder)
- **`get_planning_template`** - Get planning template sections for AI reference
- **`analyze_project_for_planning`** - Automated project analysis (discovers foundation docs, standards, patterns; optional: save to feature folder)
- **`create_plan`** - Generate implementation plan from context and analysis
- **`validate_implementation_plan`** - Validate plan quality with 0-100 scoring algorithm
- **`generate_plan_review_report`** - Format validation results into markdown reports

**Use cases:**
- Create high-quality implementation plans with automated preparation
- Validate plan completeness and quality before execution
- Iterative review loops to refine plans until quality threshold reached
- Mandatory user approval gate ensures control over implementation decisions

**Workflow Pattern:**
1. **Gather** - `gather_context` collects requirements (saves to `coderef/working/{feature}/context.json`)
2. **Analyze** - `analyze_project_for_planning` discovers context (~80ms, saves to `coderef/working/{feature}/analysis.json`)
3. **Plan** - `create_plan` generates implementation plan (saves to `coderef/working/{feature}/plan.json`)
4. **Validate** - `validate_implementation_plan` scores plan 0-100 (~18ms)
5. **Review** - `generate_plan_review_report` formats results (~5ms)
6. **Iterate** - Refine plan until score ≥ 90 (max 5 iterations)
7. **Approve** - User reviews and approves plan (MANDATORY)
8. **Execute** - AI implements approved plan

**Performance:**
- Analysis: ~80ms (750x faster than 60s target)
- Validation: ~18ms (111x faster than 2s target)
- Report generation: ~5ms (600x faster than 3s target)

**Impact:**
- Planning time reduced: 6-9 hours → 2-3 hours (60-67% reduction)
- Quality maintained: 90+ scores through automated validation
- User control: Mandatory approval gate before execution

### Workorder Tracking System (NEW in v1.5.0)

docs-mcp now includes automatic workorder tracking for all features using the planning workflow:

- **Automatic Assignment** - Every feature gets a unique workorder ID (WO-{FEATURE-NAME}-001)
- **Workflow Integration** - Workorder assigned when any planning tool is invoked
- **Cross-File Persistence** - Workorder ID tracked across context.json → analysis.json → plan.json → DELIVERABLES.md
- **Plan Validation** - Workorder format and task references validated automatically

**How it works:**
1. **gather_context** - Assigns workorder on first invocation (e.g., WO-AUTH-SYSTEM-001)
2. **analyze_for_planning** - Reads and preserves workorder from context
3. **create_plan** - Embeds workorder in section 5, assigns to all tasks
4. **validate_plan** - Validates workorder format and task references

**Workorder Format:**
- Pattern: `WO-{FEATURE-NAME}-001`
- Example: `auth-system` → `WO-AUTH-SYSTEM-001`
- Uppercase, hyphens preserved, ends with `-001`

**Feature Directory Structure:**
```
coderef/working/{feature-name}/
├── context.json       # Contains workorder in _metadata
├── analysis.json      # Contains workorder in _metadata
├── plan.json          # Contains workorder in section 5
└── DELIVERABLES.md    # References workorder in header (NEW in v1.6.0)
```

**Benefits:**
- Zero configuration - fully automatic
- Unique identification for every feature
- Progress tracking across workflow stages
- Cross-file traceability
- Backward compatible (existing plans continue working)

### Deliverables Tracking System (NEW in v1.6.0)

docs-mcp now includes automatic deliverables tracking with git-based metrics:

- **Automatic Template Generation** - `/create-plan` generates DELIVERABLES.md with phase structure
- **Git Metrics Integration** - Parse commit history to calculate LOC, commits, time spent
- **Zero Manual Tracking** - Metrics automatically populated from git history
- **Professional Documentation** - Track what was built, how much code, how long it took

**Deliverables Workflow:**

1. **Planning Phase**: `/create-plan` generates both plan.json and DELIVERABLES.md template
   - Template includes phases from plan.json
   - Task checklists with [ ] checkboxes
   - Metric placeholders (TBD) for LOC, commits, time
   - Status: 🚧 Not Started

2. **Implementation Phase**: Code your feature
   - Include feature name in commit messages for git tracking
   - Example: "feat: implement auth-system with JWT tokens"

3. **Completion Phase**: `/update-deliverables` calculates actual metrics
   - Parses git log to find feature commits (case-insensitive)
   - Calculates LOC from `git diff --stat`
   - Counts commits and contributors
   - Measures time from first to last commit
   - Replaces TBD with actual values
   - Updates status to ✅ Complete

**Git Integration:**
- Searches commit messages for feature name (case-insensitive)
- Example commits found for "auth-system":
  - "feat: implement auth-system"
  - "fix: AUTH-SYSTEM validation"
  - "docs: update auth system docs"

**DELIVERABLES.md Contents:**
```markdown
# DELIVERABLES: auth-system

**Workorder**: WO-AUTH-SYSTEM-001
**Status**: ✅ Complete

## Metrics

### Code Changes
- **Lines of Code Added**: 450
- **Lines of Code Deleted**: 120
- **Net LOC**: 330

### Commit Activity
- **Total Commits**: 8
- **Contributors**: willh, Claude

### Time Investment
- **Days Elapsed**: 3
- **Hours Spent (Wall Clock)**: 72

## Task Completion Checklist
- [x] [F1.1] Create JWT authentication middleware
- [x] [F1.2] Implement user login endpoint
...
```

**Commands:**
- `/generate-deliverables` - Manually generate template (usually automatic)
- `/update-deliverables` - Update with git metrics after implementation

### Workorder Logging Integration (NEW in v1.1.0)

docs-mcp now includes **automatic workorder logging** when archiving features:

- **Seamless Integration** - `/archive-feature` automatically logs workorders to `workorder-log.txt`
- **Complete Lifecycle** - Closes the loop: create → execute → complete → **auto-log** → archive
- **Non-Fatal Logging** - Archive succeeds even if logging fails (graceful degradation)
- **Global Activity Log** - Simple one-line format for quick visibility across all projects

**How it works:**

1. **Feature Implementation**: Complete your feature work
2. **Update Deliverables**: Run `/update-deliverables` to calculate metrics
3. **Archive Feature**: Run `/archive-feature` to move feature to `coderef/archived/`
4. **Auto-Log**: Workorder is automatically extracted from `plan.json` and logged
5. **Confirmation**: Response includes `workorder_logged: true` and `workorder_id`

**Workorder Log Format:**
```
WO-ID | Project | Description | Timestamp
```

**Example Entry:**
```
WO-AUTH-SYSTEM-001 | docs-mcp | Archived feature: Auth System | 2025-10-23T05:30:00+00:00
```

**Benefits:**
- Zero manual intervention - fully automatic
- Complete traceability from creation to archiving
- Quick glance at recent project activity
- Cross-project workorder tracking

**Commands:**
- `/archive-feature` - Archive feature and auto-log workorder
- `/log-workorder` - Manually log workorder (rarely needed)
- `/get-workorder-log` - View workorder activity log

---

## Prerequisites

Before using docs-mcp, ensure you have:

### Required

- ✅ **Claude Code CLI** installed and configured
- ✅ **Python 3.10+** installed on your system
- ✅ **Working project** with actual code files to document

### Verify Requirements

```bash
# Check Claude Code CLI
claude --version

# Check Python version
python --version
# Should show: Python 3.10.x or higher

# Check MCP capability
claude mcp list
```

> 💡 **What is MCP?**
> Model Context Protocol allows AI assistants (like Claude) to access external tools and data sources. docs-mcp is an MCP server that provides documentation generation tools.

---

## Installation

### Step 1: Install the MCP Server

```bash
# Navigate to your MCP servers directory
cd C:\Users\willh\.mcp-servers\docs-mcp

# Install Python dependencies (if not already installed)
pip install mcp>=1.0.0
```

### Step 2: Register with Claude Code

```bash
# Add docs-mcp as a user-scoped MCP server
claude mcp add docs-mcp --scope user --command python --args "C:\Users\willh\.mcp-servers\docs-mcp\server.py"
```

**Expected Output:**
```
✓ docs-mcp added successfully
```

### Step 3: Verify Installation

```bash
# List all MCP servers
claude mcp list
```

**Expected Output:**
```
MCP Servers:
✓ docs-mcp - Connected
```

> ⚠️ **Important**: If docs-mcp shows as "Not Connected", restart Claude Code and try again.

---

## How It Works

### Architecture Overview

```
┌──────────────────┐
│   Your Project   │
│   (Source Code)  │
└────────┬─────────┘
         │
         │ Claude Code analyzes
         │
         ▼
┌──────────────────┐
│  docs-mcp Server │
│  (MCP Protocol)  │
└────────┬─────────┘
         │
         │ Uses POWER templates
         │
         ▼
┌──────────────────┐
│  Generated Docs  │
│   coderef/       │
│   foundation-    │
│   docs/          │
└──────────────────┘
```

### Process Flow

1. **You invoke** a natural language command in Claude Code
2. **Claude Code calls** the appropriate MCP tool (`generate_foundation_docs` or `generate_individual_doc`)
3. **docs-mcp analyzes** your project structure, code files, and configuration
4. **Templates guide** the generation using the POWER framework
5. **Claude creates** the documentation based on template structure and code analysis
6. **Files are saved** to `your-project/coderef/foundation-docs/`

---

## Usage

### Generate All 5 Foundation Docs (New Project)

**When to use:** Starting documentation from scratch or doing a complete refresh

#### Command Format

In Claude Code, type:

```
Generate foundation documentation for my project at <absolute-path-to-project>
```

#### Real Example

```
Generate foundation documentation for my project at C:\Users\willh\Desktop\projects - current-location\sidebar-app
```

#### What Happens

1. **Directory Created**: `sidebar-app/coderef/foundation-docs/`
2. **Files Generated** (5 foundation docs):
   - ✅ README.md
   - ✅ ARCHITECTURE.md
   - ✅ API.md
   - ✅ COMPONENTS.md
   - ✅ SCHEMA.md
3. **Time**: 6-15 minutes (depends on project size)
4. **Process**: Sequential generation (each doc references previous docs)
5. **Note**: USER-GUIDE.md is optional and generated separately

#### Behind the Scenes

**MCP Tool Used**: `generate_foundation_docs`

**Tool Schema**:
```json
{
  "name": "generate_foundation_docs",
  "inputSchema": {
    "properties": {
      "project_path": {
        "type": "string",
        "description": "Absolute path to the project directory"
      }
    },
    "required": ["project_path"]
  }
}
```

---

### Generate Single Doc (Update)

**When to use:** Updating documentation after code changes

#### Command Format

In Claude Code, type:

```
Generate individual doc for my project at <absolute-path-to-project> using template <template-name>
```

#### Template Options

| Template Name | Document | Use When |
|---------------|----------|----------|
| `readme` | README.md | Changed setup, added features, updated overview |
| `architecture` | ARCHITECTURE.md | Refactored structure, changed tech stack, updated design |
| `api` | API.md | Added/changed endpoints, updated integration patterns |
| `components` | COMPONENTS.md | Added/modified components, changed patterns |
| `schema` | SCHEMA.md | Changed data structures, updated database schema |
| `user-guide` | USER-GUIDE.md | Updated onboarding flow, added tutorials, changed UX |

#### Real Examples

**Update API Documentation:**
```
Generate individual doc for my project at C:\Users\willh\Desktop\projects - current-location\sidebar-app using template api
```

**Update Components Documentation:**
```
Generate individual doc for my project at C:\Users\willh\Desktop\projects - current-location\sidebar-app using template components
```

**Update Schema Documentation:**
```
Generate individual doc for my project at C:\Users\willh\Desktop\projects - current-location\sidebar-app using template schema
```

**Update User Guide Documentation:**
```
Generate individual doc for my project at C:\Users\willh\Desktop\projects - current-location\sidebar-app using template user-guide
```

#### What Happens

1. **Single File Updated**: Only the specified document is regenerated
2. **Time**: 1-3 minutes per document
3. **Context Preserved**: References to other docs remain intact

#### Behind the Scenes

**MCP Tool Used**: `generate_individual_doc`

**Tool Schema**:
```json
{
  "name": "generate_individual_doc",
  "inputSchema": {
    "properties": {
      "project_path": {
        "type": "string",
        "description": "Absolute path to the project directory"
      },
      "template_name": {
        "type": "string",
        "enum": ["readme", "architecture", "api", "components", "schema", "user-guide"]
      }
    },
    "required": ["project_path", "template_name"]
  }
}
```

---

## Output Structure

### Default Location

> 📁 **Output Directory**: `coderef/foundation-docs/`

This is the **new default location** (changed from `docs/` to `coderef/foundation-docs/` for better organization).

### Project Structure After Generation

```
your-project/
├── src/                      # Your source code
├── public/                   # Your assets
├── package.json              # Your config
├── coderef/                  # ← NEW: Documentation root
│   └── foundation-docs/      # ← All generated docs here
│       ├── README.md         # Project overview & setup
│       ├── ARCHITECTURE.md   # System design & topology
│       ├── API.md            # Endpoints & integrations
│       ├── COMPONENTS.md     # Reusable components
│       ├── SCHEMA.md         # Data structures & types
│       └── USER-GUIDE.md     # User onboarding & tutorials
└── ...
```

### Why `coderef/foundation-docs/`?

- **Organized**: Separates documentation from source code
- **Scalable**: Room for other doc types (e.g., `coderef/api-docs/`, `coderef/guides/`)
- **Clear Purpose**: "foundation-docs" indicates these are base reference documents
- **Git-Friendly**: Easy to add to `.gitignore` if desired

---

## Documentation Contents

### README.md

**Purpose**: Entry point for understanding the project

**Includes**:
- Project overview and purpose
- Prerequisites and dependencies
- Installation steps with commands
- Usage examples
- Available scripts
- Troubleshooting guide
- Environment variables
- Development workflow

**Example Sections**:
```markdown
# Project Name
## Overview
## Prerequisites
## Installation
## Usage
## Troubleshooting
```

---

### ARCHITECTURE.md

**Purpose**: System design and technical decisions

**Includes**:
- System topology with ASCII diagrams
- Module boundaries and responsibilities
- Technology stack with rationale
- Data flow diagrams
- Design decisions and trade-offs
- Security considerations
- Extension points

**Example Sections**:
```markdown
# ARCHITECTURE.md
## System Topology
## Module Boundaries
## Technology Stack
## Data Flow
## Design Rationale
```

---

### API.md

**Purpose**: Technical interface reference

**Includes**:
- All endpoints/routes
- Request/response formats
- Authentication patterns
- Error handling
- Rate limiting
- Code examples with cURL
- Integration patterns
- Testing approaches

**Example Sections**:
```markdown
# API.md
## Authentication
## Endpoints
## Error Handling
## Usage Examples
## Rate Limits
```

---

### COMPONENTS.md

**Purpose**: Reusable code component library

**Includes**:
- Component inventory
- Props/interfaces for each component
- Usage patterns
- Copy-paste examples
- State management patterns
- Styling patterns
- Accessibility considerations
- Extension guidelines

**Example Sections**:
```markdown
# COMPONENTS.md
## Component Inventory
## UI Components
## Usage Patterns
## Code Examples
## Best Practices
```

---

### SCHEMA.md

**Purpose**: Data structure and validation reference

**Includes**:
- TypeScript type definitions
- Database schemas
- Zod validation schemas
- Data relationships
- Migration strategies
- Constraints and rules
- Future schema plans

**Example Sections**:
```markdown
# SCHEMA.md
## Type Definitions
## Database Schema
## Validation Rules
## Relationships
## Migration Guide
```

---

### USER-GUIDE.md

**Purpose**: User onboarding and reference documentation

**Includes**:
- Table of contents with anchor links
- Prerequisites with verification commands
- Step-by-step installation instructions
- Architecture explanation with diagrams
- Explicit command examples
- Common use cases and workflows
- Best practices (Do/Don't/Tips)
- Troubleshooting guide
- Quick reference tables

**Example Sections**:
```markdown
# USER-GUIDE.md
## Prerequisites
## Installation
## How It Works
## Usage Examples
## Best Practices
## Troubleshooting
## Quick Reference
```

---

## Planning Workflow Guide (Step-by-Step)

> **Complete beginner's guide to creating implementation plans with docs-mcp**

### Overview

The planning workflow system helps you create high-quality implementation plans before writing code. It consists of 4 MCP tools that work together to automate preparation, validate quality, and ensure plans are complete before execution.

**Why use planning workflow:**
- Reduces planning time by 60-67% (6-9 hours → 2-3 hours)
- Automated project analysis (~80ms vs 60-70 minutes manual)
- Quality validation ensures score ≥ 90 before implementation
- Mandatory user approval gate keeps you in control

---

### Step 1: Tell AI What You Want to Build

**You provide:**
- Feature description: "I want to add user authentication"
- Any specific requirements: "with OAuth2 support for Google and GitHub"
- Any constraints: "must work with our existing Express backend"

**What to expect:**
- AI acknowledges and starts the planning process

**Example:**
```
You: "Create an implementation plan for adding user authentication
      with OAuth2 support for Google and GitHub logins"
```

---

### Step 2: Analyze Your Project (`/analyze-for-planning`)

**You provide:**
- Just type: `/analyze-for-planning`
- That's it! (uses current directory automatically)

**AI provides back to you:**
```json
{
  "foundation_docs": {
    "available": ["API.md", "ARCHITECTURE.md", "README.md"],
    "missing": ["COMPONENTS.md"]
  },
  "coding_standards": {
    "available": ["UI-STANDARDS.md", "BEHAVIOR-STANDARDS.md"],
    "missing": []
  },
  "reference_components": {
    "primary": "src/components/LoginForm.tsx",
    "secondary": ["src/utils/api.ts"]
  },
  "technology_stack": {
    "frontend": "React + TypeScript",
    "backend": "Express + Node.js"
  },
  "gaps_and_risks": [
    "No existing OAuth implementation",
    "Security patterns need review"
  ]
}
```

**What to expect:**
- Takes ~80ms (very fast)
- Lists what docs exist in your project
- Identifies reference code to follow
- Flags any risks/gaps

**Behind the Scenes:**
- MCP Tool: `analyze_project_for_planning`
- Scans: `coderef/foundation-docs/`, `coderef/standards/`
- Identifies: Tech stack, reference components, patterns
- Performance: ~80ms (750x faster than manual 60s target)

---

### Step 3: Get Planning Template (`/get-planning-template`)

**You provide:**
- Just type: `/get-planning-template`
- (optional) Can specify section like: `/get-planning-template section=1_executive_summary`

**AI provides back to you:**
- Complete JSON template structure
- All required fields explained
- Quality standards (how long descriptions should be, etc.)
- Examples of good vs bad entries

**What to expect:**
- Returns the empty template structure
- Shows you what sections are required (0-9)
- This is the "form" that will be filled out

**Template sections:**
```
0. Preparation (context from Step 2)
1. Executive Summary
2. Risk Assessment
3. Current State Analysis
4. Key Features
5. Task ID System
6. Implementation Phases
7. Testing Strategy
8. Success Criteria
9. Implementation Checklist
```

**Behind the Scenes:**
- MCP Tool: `get_planning_template`
- Returns: JSON structure with all 10 sections
- Includes: Quality checklist, common mistakes, usage instructions
- Performance: ~5ms

---

### Step 4: AI Creates the Plan

**You provide:**
- Nothing! Just wait.

**AI does:**
- Reads the discovered docs from Step 2
- Fills in all 10 sections of the template from Step 3
- Uses your feature requirements from Step 1
- Saves file as `feature-{name}-plan.json`

**What to expect:**
- AI creates a JSON file in your project
- File contains all 10 sections filled out
- This takes a few moments while AI reads and writes

**Example filename:**
```
feature-auth-plan.json
feature-payment-plan.json
feature-dashboard-plan.json
```

**What AI fills in:**
- **Section 0**: Copies preparation summary from analyze_project_for_planning
- **Section 1**: Executive summary of what will be built
- **Section 2**: Risk assessment (technical, timeline, security risks)
- **Section 3**: Current state analysis (what exists now)
- **Section 4**: Key features broken down into capabilities
- **Section 5**: Task ID system (AUTH-001, AUTH-002, etc.)
- **Section 6**: Implementation phases with dependencies
- **Section 7**: Testing strategy (unit, integration, E2E)
- **Section 8**: Success criteria (PASS conditions)
- **Section 9**: Implementation checklist

---

### Step 5: Validate the Plan (`/validate-plan`)

**You provide:**
- Type: `/validate-plan`
- When asked, enter filename: `feature-auth-plan.json`

**AI provides back to you:**
```json
{
  "score": 75,
  "result": "NEEDS_REVISION",
  "issues": {
    "critical": [
      "Section 2: Missing risk assessment for OAuth token storage"
    ],
    "major": [
      "Section 6: Task AUTH-003 description too short (8 words, need ≥20)"
    ],
    "minor": [
      "Section 7: Only 3 edge cases listed, recommend 5-10"
    ]
  }
}
```

**What to expect:**
- Score from 0-100
- Result type: PASS (≥90), PASS_WITH_WARNINGS (≥85), NEEDS_REVISION (≥70), FAIL (<70)
- List of specific issues to fix, grouped by severity

**Scoring algorithm:**
```
Score = 100 - (10 × critical + 5 × major + 1 × minor)

Example:
100 - (10×2 + 5×1 + 1×3) = 100 - 28 = 72 (NEEDS_REVISION)
```

**Behind the Scenes:**
- MCP Tool: `validate_implementation_plan`
- Validates: Structure, completeness, quality, autonomy
- Checks: Task descriptions ≥20 words, 5-10 edge cases, no placeholders
- Performance: ~18ms (111x faster than 2s target)

---

### Step 6: Fix Issues & Re-Validate

**You provide:**
- If score < 90: "Please fix the issues and re-validate"

**AI does:**
- Fixes critical issues first (most important)
- Fixes major issues second
- Fixes minor issues third (polish)
- Runs `/validate-plan` again automatically

**What to expect:**
- AI iterates through fixes
- Re-validates after each round
- Continues until score ≥ 90 or max 5 attempts
- Shows you progress: "Score: 75 → 82 → 91 ✓"

**Example iteration:**
```
Iteration 1: Score 75 (2 critical, 1 major, 3 minor) → Fix critical
Iteration 2: Score 82 (0 critical, 1 major, 3 minor) → Fix major
Iteration 3: Score 91 (0 critical, 0 major, 4 minor) → PASS!
```

**Quality thresholds:**
- **90-100**: PASS - Ready for implementation
- **85-89**: PASS_WITH_WARNINGS - Acceptable with minor improvements
- **70-84**: NEEDS_REVISION - Requires refinement
- **0-69**: FAIL - Critical issues, significant rework needed

---

### Step 7: Generate Review Report (`/generate-plan-review`)

**You provide:**
- Type: `/generate-plan-review`
- When asked, enter filename: `feature-auth-plan.json`

**AI provides back to you:**
- JSON report saved to same directory as plan: `coderef/working/{feature}/review.json`
- Report shows:
  - Executive Summary (Score: 92/100, Grade: A, Status: APPROVED)
  - Critical Issues: (none)
  - Major Issues: (none)
  - Minor Issues: (2 polish items)
  - Recommendations

**What to expect:**
- Structured JSON report
- Easy to review and understand
- File saved alongside context.json and plan.json

**Example report:**
```json
{
  "score": 92,
  "grade": "A",
  "result": "PASS",
  "status": "APPROVED",
  "issues": {
    "critical": [],
    "major": [],
    "minor": [
      "Section 7: Edge case 'concurrent login attempts' could be more specific",
      "Section 8: Add performance benchmark (login response time < 200ms)"
    ]
  },
  "strengths": [
    "Complete preparation section with all required context",
    "Detailed risk assessment covering security and timeline",
    "Well-structured task breakdown with clear dependencies"
  ],
  "recommendations": [
    "Add performance success criteria to section 8",
    "Expand edge case descriptions in section 7",
    "Plan is ready for implementation with minor polish items"
  ],
  "metadata": {
    "generated": "2025-10-11T14:30:22",
    "plan_file": "coderef/working/user-authentication/plan.json",
    "validation_time_ms": 18
  }
}
```

**Behind the Scenes:**
- MCP Tool: `generate_plan_review_report`
- Formats: Validation results → JSON report
- Includes: Score, issues by severity, recommendations
- Saves to: Same directory as plan file (review.json)
- Performance: ~5ms (600x faster than 3s target)

---

### Step 8: Review & Approve ⚠️ **MANDATORY**

**You provide:**
- Read the plan and review report
- Decide: approve or request changes
- Say: "Approved, proceed with implementation" or "Please revise section 6"

**AI does:**
- Waits for your explicit approval
- Will NOT start coding without permission
- Can make revisions if you request changes

**What to expect:**
- AI presents the plan for YOUR decision
- You are in control - nothing happens without approval
- Can request changes to any section

**Example approval:**
```
You: "The plan looks good. I'd like you to add more detail about
      error handling in section 6, then proceed with implementation."

AI: "I'll update section 6 with detailed error handling strategies
     and re-validate. Once you approve, I'll begin implementation."
```

**Why this step is mandatory:**
- Ensures you understand what will be built
- Gives you control over implementation decisions
- Allows you to catch issues before coding starts
- Provides opportunity to adjust scope or approach

---

### Step 9: Execute the Plan

**You provide:**
- After approval: "Please implement phase 1"
- Or: "Start implementation"

**AI does:**
- Follows the plan step-by-step
- Implements tasks in order from the plan
- References the plan's task IDs
- Updates you on progress

**What to expect:**
- AI codes according to the approved plan
- Follows the phases and tasks defined
- Can track progress by task IDs (AUTH-001, AUTH-002, etc.)
- May pause between phases to show progress

**Example progress:**
```
Phase 1: Foundation Setup
✅ AUTH-001: Set up OAuth configuration files
✅ AUTH-002: Install OAuth dependencies
🔄 AUTH-003: Create authentication middleware

Phase 2: OAuth Integration
⏳ AUTH-004: Implement Google OAuth flow
⏳ AUTH-005: Implement GitHub OAuth flow
...
```

---

### Complete Workflow Example

**Scenario:** Adding user authentication to a React/Express app

```bash
# Step 1: User request
You: "Create an implementation plan for adding user authentication
      with OAuth2 support for Google and GitHub logins"

# Step 2: Analyze project
You: /analyze-for-planning
AI: Returns project context (foundation docs, standards, tech stack)

# Step 3: Get template
You: /get-planning-template
AI: Returns planning template structure

# Step 4: AI creates plan
AI: Creates feature-auth-plan.json with all 10 sections filled

# Step 5: Validate (first attempt)
You: /validate-plan
AI: Score: 75 - NEEDS_REVISION (2 critical, 1 major, 3 minor)

# Step 6: Fix and re-validate
You: "Fix the issues and re-validate"
AI: Iteration 1 → Score: 82
AI: Iteration 2 → Score: 91 - PASS!

# Step 7: Generate review report
You: /generate-plan-review
AI: Saves review.json to coderef/working/user-authentication/

# Step 8: User approves
You: "Approved, proceed with implementation"

# Step 9: AI implements
AI: Phase 1 - Foundation Setup...
AI: Phase 2 - OAuth Integration...
AI: Phase 3 - Testing & Documentation...
AI: ✅ Implementation complete!
```

---

### Quick Reference Card

| Step | You Type | You Get | Time |
|------|----------|---------|------|
| 1 | "Create plan for [feature]" | AI starts process | instant |
| 2 | `/analyze-for-planning` | Project context JSON | ~80ms |
| 3 | `/get-planning-template` | Empty template structure | ~5ms |
| 4 | (wait) | Filled plan JSON file | ~30s |
| 5 | `/validate-plan` + filename | Score + issues | ~18ms |
| 6 | "Fix and re-validate" | Improved score | ~1-2min |
| 7 | `/generate-plan-review` + filename | Markdown report | ~5ms |
| 8 | "Approved" or request changes | AI waits or revises | instant |
| 9 | "Implement" | AI codes the plan | varies |

---

### Planning Workflow Best Practices

#### ✅ Do

- **Be specific in Step 1**: Clear feature requirements help AI create better plans
- **Review Step 2 output**: Verify discovered docs and standards are current
- **Wait for score ≥ 90**: Higher quality plans lead to better implementations
- **Read the review report**: Understand what will be built before approval
- **Request changes freely**: Better to refine the plan than fix code later
- **Save plans**: Keep `feature-*-plan.json` files for reference

#### 🚫 Don't

- **Don't skip validation**: Always run `/validate-plan` before approval
- **Don't approve score < 90**: Quality matters - let AI refine first
- **Don't skip user approval**: Never let AI implement without your permission
- **Don't delete plan files**: Keep them for tracking and reference
- **Don't rush**: Planning time saves implementation time

#### 💡 Tips

- **Run `/establish-standards` first**: Gives better planning context
- **Use planning for complex features**: Simple features may not need full planning
- **Review dependencies**: Check task dependencies in section 6 make sense
- **Verify edge cases**: Section 7 should cover realistic edge cases
- **Keep plans updated**: If scope changes, update and re-validate plan

---

### When to Use Planning Workflow

**✅ Use planning workflow for:**
- New features with multiple components
- Architectural changes affecting multiple modules
- Integration with external services
- Security-sensitive implementations
- Features with complex state management
- Any work taking > 4 hours

**❌ Skip planning workflow for:**
- Simple bug fixes
- Typo corrections
- Trivial UI adjustments
- Single-file changes
- Refactoring within single function

---

### Planning Workflow Troubleshooting

#### Problem: analyze_project_for_planning returns empty results

**Cause:** No foundation docs or standards in project

**Solution:**
```bash
# Generate foundation docs first
Generate foundation documentation for my project at C:\path\to\project

# Extract standards
/establish-standards

# Then analyze for planning
/analyze-for-planning
```

---

#### Problem: Validation score stuck below 90

**Cause:** Complex issues or insufficient detail in plan

**Solution:**
1. Read the validation issues carefully
2. Focus on critical issues first
3. Add more detail to task descriptions (≥20 words each)
4. List 5-10 realistic edge cases
5. Remove any placeholder text like "TBD" or "TODO"
6. If stuck after 5 iterations, request manual review

---

#### Problem: AI won't start implementation after approval

**Cause:** Ambiguous approval message

**Solution:**
```bash
# ❌ Unclear
"Looks good"
"OK"
"Sure"

# ✅ Clear approval
"Approved, proceed with implementation"
"Start implementing phase 1"
"Begin implementation of the plan"
```

---

### Planning vs. Direct Implementation

| Aspect | Planning Workflow | Direct Implementation |
|--------|-------------------|----------------------|
| **Time** | 2-3 hours planning + implementation | Immediate coding |
| **Quality** | Validated plan (score ≥ 90) | Varies |
| **User Control** | Mandatory approval gate | Continuous oversight needed |
| **Best For** | Complex features, architectural changes | Simple fixes, small updates |
| **Risk** | Low (plan reviewed first) | Medium (discover issues during coding) |
| **Documentation** | Plan document + review report | Code comments only |

---

## Slash Commands Quick Reference

> **Quick access to common workflows using natural language shortcuts**

### What are Slash Commands?

Slash commands are shortcuts that make docs-mcp tools easier to use. Instead of typing long MCP tool names, you can type short commands like `/generate-docs` or `/validate-plan`.

**When to use slash commands:**
- Faster than full MCP tool invocations
- Pre-configured with sensible defaults
- Automatically use current working directory
- Perfect for common workflows

**When to use MCP tools directly:**
- Need custom parameters (scan depth, filters, etc.)
- Programmatic access from other tools
- Building automation workflows

---

### Available Slash Commands (40 Total)

#### Documentation Commands (4)

##### `/generate-docs`
Generate foundation documentation for current project.

**What it does:**
- Calls `generate_foundation_docs` with current directory
- Returns 5 foundation document templates
- AI fills templates and saves documents
- (USER-GUIDE is optional and generated separately)

**When to use:**
- Starting documentation from scratch
- Complete documentation refresh

**Example:**
```
You: /generate-docs
AI: Analyzing project and generating 5 foundation documents...
```

---

##### `/generate-user-guide`
Generate USER-GUIDE documentation for current project.

**What it does:**
- Calls `generate_individual_doc` with current directory
- Returns USER-GUIDE template
- AI fills template and saves document
- Creates comprehensive user onboarding documentation

**When to use:**
- After completing foundation docs
- When you need user-facing documentation
- For onboarding new users or team members

**What gets created:**
- Prerequisites with verification commands
- Step-by-step installation guide
- Usage examples and workflows
- Best practices and tips
- Troubleshooting guide
- Quick reference tables

**Example:**
```
You: /generate-user-guide
AI: Generating USER-GUIDE documentation for current project...
AI: Created comprehensive user guide at coderef/foundation-docs/USER-GUIDE.md
```

---

##### `/generate-my-guide`
Generate my-guide quick reference documentation for current project.

**What it does:**
- Calls `generate_individual_doc` with current directory
- Returns my-guide template
- AI fills template and saves document
- Creates concise 60-80 line quick reference listing MCP tools and slash commands by category

**When to use:**
- When you need a lightweight tool reference (vs comprehensive USER-GUIDE.md)
- Quick lookup of available MCP tools and slash commands
- Compact reference that fits on one screen

**What gets created:**
- MCP tools organized by category (Documentation, Changelog, Standards, Planning)
- Slash commands organized by category
- One-line descriptions per tool/command
- Bullet-list format for quick scanning
- Saved to project root as my-guide.md

**Example:**
```
You: /generate-my-guide
AI: Generating my-guide quick reference for current project...
AI: Created concise tool reference at my-guide.md (69 lines)
```

---

##### `/generate-quickref`
Generate scannable quickref guide for ANY application via interactive interview.

**What it does:**
- Calls `generate_quickref_interactive` with current directory
- AI conducts 9-step interview to gather app information
- User answers in plain English about their application
- AI generates scannable quickref.md (150-250 lines)
- Works for CLI, Web, API, Desktop, and Library applications

**When to use:**
- After completing foundation docs
- When you need a quick reference guide for your application
- To provide scannable documentation for users or team members
- For any application type (CLI, Web, API, Desktop, Library)

**Interview topics:**
1. Basic app information (name, description, type)
2. Core capabilities (4-5 main things the app does)
3. Primary actions/commands users perform
4. Key features/tools available
5. Common workflows (3-4 step-by-step processes)
6. Reference formats (data structures, configs)
7. Output locations (where app creates/saves files)
8. Key concepts (5-7 core ideas users need to understand)

**Output structure (8 sections):**
1. At a Glance - Quick overview
2. Actions/Commands - Main user actions
3. Features/Tools - Available capabilities
4. Common Workflows - Step-by-step processes
5. Reference Format - Data structures/configs
6. Output Locations - Where files are created
7. Key Concepts - Core ideas to understand
8. Summary - Quick recap

**Example:**
```
You: /generate-quickref
AI: Let's create a quickref guide for your application.

AI: Step 1/9: What's your application name and brief description?
You: "docs-mcp - An MCP server for generating project documentation"

AI: Step 2/9: What are the 4-5 core capabilities of docs-mcp?
You: "Generate foundation docs, manage changelogs, extract standards, audit compliance, create implementation plans"

... (AI continues through 9 steps)

AI: Generated scannable quickref at coderef/quickref.md (187 lines)
```

---

#### Consistency Commands (3)

##### `/establish-standards`
Extract coding standards from current project.

**What it does:**
- Calls `establish_standards` with current directory
- Scans codebase for UI/behavior/UX patterns
- Creates 4 standards documents in `coderef/standards/`

**When to use:**
- **Run ONCE per project** to establish baseline
- Starting consistency management
- After major architectural changes

**Output files:**
- `UI-STANDARDS.md` - Visual component standards
- `BEHAVIOR-STANDARDS.md` - Interaction patterns
- `UX-PATTERNS.md` - User experience patterns
- `COMPONENT-INDEX.md` - Component catalog

**Example:**
```
You: /establish-standards
AI: Scanning codebase for patterns...
AI: Created 4 standards documents with 47 patterns discovered
```

---

##### `/audit-codebase`
Audit current project for standards compliance.

**What it does:**
- Calls `audit_codebase` with current directory
- Compares code against established standards
- Generates compliance report with score (0-100)

**When to use:**
- After running `/establish-standards`
- Before merging code
- Regular consistency checks
- CI/CD pipeline integration

**Output:**
- Compliance score (0-100) and grade (A-F)
- Violations by severity (critical/major/minor)
- Violations by file (hotspot analysis)
- Fix recommendations

**Example:**
```
You: /audit-codebase
AI: Auditing codebase against established standards...
AI: Compliance Score: 82/100 (Grade: B)
AI: Found 18 violations: 0 critical, 4 major, 14 minor
```

---

##### `/check-consistency`
Quick consistency check on modified files (pre-commit gate).

**What it does:**
- Calls `check_consistency` with current directory
- Auto-detects git changes (staged files)
- Only scans modified files (fast!)
- Reports violations at or above severity threshold

**When to use:**
- Before committing code
- Pre-push hooks
- Quick validation during development
- CI/CD pre-merge checks

**Example:**
```
You: /check-consistency
AI: Checking modified files: src/Button.tsx, src/Modal.tsx
AI: ✅ No violations found in modified files
```

---

#### Context Gathering Command (1)

##### `/gather-context`
Gather feature requirements before planning implementation.

**What it does:**
- Conducts interactive Q&A to capture requirements
- Creates `<feature-name>-context.json` in project root
- Captures WHAT user wants before planning HOW
- Structures requirements, constraints, and scope

**When to use:**
- **Before creating implementation plans** (optional but recommended)
- When requirements are not yet fully defined
- To clarify feature scope and boundaries
- To separate requirements gathering from implementation planning

**What gets created:**
- Feature working directory: `coderef/working/<feature-name>/`
- Context file: `context.json` with structured requirements:
  - feature_name (kebab-case identifier)
  - description (what user wants in plain language)
  - goal (why they want this feature)
  - requirements (list of must-haves)
  - out_of_scope (explicitly not included)
  - constraints (technical/business limitations)

**Workflow:**
1. AI asks for feature name
2. AI creates working directory `coderef/working/<feature-name>/`
3. AI creates initial outline based on user's request
4. AI conducts Q&A with numbered choices or y/n questions (easy to answer!)
5. AI saves context file to `coderef/working/<feature-name>/context.json`
6. Context feeds into `/analyze-for-planning` and plan creation

**Example:**
```
You: /gather-context
AI: What's the feature name? (Choose or specify)
    1. landing-page
    2. user-authentication
    3. outdoor-gear-category
    4. Custom name
You: "outdoor-gear-category"

AI: What sections should the category page include? (Choose numbers, e.g., "1,2,4")
    1. Banner image
    2. Featured products
    3. Product grid
    4. Filter options
    5. Sort controls
    6. Pagination
You: "1,2,3,4,5"

AI: What's explicitly NOT included? (Choose numbers for exclusions)
    1. Wishlist/favorites
    2. Size/color selectors on grid
    3. Video in banner
    4. Subcategories/taxonomy
    5. Email notifications
You: "1,3,4"

AI: Any technical constraints? (y/n)
You: "y"

AI: Which constraints apply? (Choose numbers)
    1. Must use existing framework (Bootstrap, etc.)
    2. Performance requirements
    3. Browser compatibility
    4. File size limits
    5. Launch deadline
You: "1,2,5"

AI: ✅ Context saved to coderef/working/outdoor-gear-category/context.json
AI: You can now run /analyze-for-planning to create implementation plan
```

**Output location:** `<project-root>/coderef/working/<feature-name>/context.json`

---

#### Planning Commands (6)

##### `/start-feature` ⭐ RECOMMENDED
**Primary entry point for feature planning.** Orchestrates the full workflow in one command.

**What it does:**
- Asks for feature name
- Runs gather-context (interactive Q&A)
- Runs analyze-project-for-planning (automatic)
- Runs create-plan (automatic)
- Runs validate-plan (auto-fixes until score >= 90)
- Commits planning artifacts to git

**When to use:**
- **Always start here** for new features
- Single command replaces 4 separate commands
- Best for complete planning workflow

**Workflow:**
```
/start-feature → /execute-plan → implement → /update-deliverables → /archive-feature
```

**Example:**
```
You: /start-feature
AI: What feature would you like to plan? auth-system
AI: [Runs full planning pipeline automatically]
AI: Created: context.json, analysis.json, plan.json, DELIVERABLES.md
```

---

##### `/analyze-for-planning` (Advanced)
Analyze project for implementation planning context.

**What it does:**
- Calls `analyze_project_for_planning` with current directory
- Discovers foundation docs, standards, patterns
- Identifies tech stack and reference components
- Flags gaps and risks

**When to use:**
- **Run BEFORE creating implementation plans**
- Starting any planning workflow
- Understanding project structure

**Performance:** ~80ms (very fast!)

**Example:**
```
You: /analyze-for-planning
AI: Discovered 5 foundation docs, 4 standards documents
AI: Tech stack: React + TypeScript + Express
AI: Reference components: Button.tsx, Modal.tsx
```

---

##### `/get-planning-template`
Get planning template structure for AI reference.

**What it does:**
- Calls `get_planning_template`
- Returns JSON template with all required fields
- Shows quality standards and best practices

**When to use:**
- Before creating implementation plans
- Understanding planning structure
- Reference during plan creation

**Example:**
```
You: /get-planning-template
AI: Returns complete planning template with 10 sections
```

---

##### `/validate-plan`
Validate implementation plan quality.

**What it does:**
- Asks for plan file path
- Calls `validate_implementation_plan`
- Scores plan 0-100 based on completeness/quality
- Identifies issues by severity with fix suggestions

**When to use:**
- After creating implementation plan
- Iterative review loop until score ≥ 90
- Before presenting plan to user

**Performance:** ~18ms (very fast!)

**Example:**
```
You: /validate-plan
AI: Enter filename: feature-auth-plan.json
AI: Score: 75/100 - NEEDS_REVISION
AI: Issues: 2 critical, 1 major, 3 minor
```

---

##### `/generate-plan-review`
Generate markdown review report from validation results.

**What it does:**
- Asks for plan file path
- Calls `generate_plan_review_report`
- Formats validation results into markdown report
- Saves to `coderef/reviews/`

**When to use:**
- After running `/validate-plan`
- Creating documentation for plan review
- Generating reports for team review

**Performance:** ~5ms (very fast!)

**Example:**
```
You: /generate-plan-review
AI: Enter plan path: coderef/working/user-authentication/plan.json
AI: Generated review report: coderef/working/user-authentication/review.json
```

---

##### `/execute-plan` **NEW in v2.5.0**
Generate TodoWrite task list from plan.json for organized execution.

**What it does:**
- Asks for feature name
- Calls `execute_plan` with current directory and feature name
- Reads plan.json from `coderef/working/{feature}/`
- Extracts workorder_id and all tasks from section 9
- Generates TodoWrite format: `TASK-ID: Description`
- Creates activeForm with gerund conversion (Install → Installing)
- Logs execution to execution-log.json with timestamp

**When to use:**
- **Run AFTER `/create-plan`** to generate task list for execution
- Before starting implementation
- To get organized checklist in Lloyd's CLI

**Output format:**
```
Workorder: WO-AUTH-001 - Authentication System

☐ SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1
☐ SETUP-002: Create auth/ directory structure
☐ PARSER-001: Implement load_plan() function
☐ PARSER-002: Implement extract_workorder_id() function
```

**Features:**
- TASK-ID displayed first for easy scanning
- Workorder name shown at top of list
- Active form shows progress: "SETUP-001: Installing dependencies"
- Status preserved from plan (☐/☑/⏳/🚫)
- Execution history logged for audit trail

**Example:**
```
You: /execute-plan
AI: Enter feature name: auth-system
AI: Generated 17 tasks for auth-system [WO-AUTH-001]
AI: Workorder: WO-AUTH-001 - Authentication System
AI: [Displays formatted task list with TASK-ID first]
```

---

#### Inventory Commands (8)

##### `/quick-inventory` ⭐ RECOMMENDED
**Run all 7 inventory tools in one command.** Best entry point for project analysis.

**What it does:**
- Runs all 7 inventory tools in sequence:
  1. `inventory_manifest` - File catalog
  2. `dependency_inventory` - Dependencies + security
  3. `api_inventory` - API endpoints
  4. `database_inventory` - Database schemas
  5. `config_inventory` - Configuration files
  6. `test_inventory` - Test infrastructure
  7. `documentation_inventory` - Documentation files
- Saves all manifests to `coderef/inventory/`
- Provides combined summary

**When to use:**
- **First time exploring a project**
- Complete project analysis
- Before major refactoring

**Example:**
```
You: /quick-inventory
AI: Running all 7 inventory tools...
AI: Created: manifest.json, dependencies.json, api.json, database.json, config.json, tests.json, documentation.json
AI: Summary: 245 files, 32 dependencies (2 outdated), 15 API endpoints, 8 tables
```

---

##### `/inventory-manifest`
Generate comprehensive project file inventory.

##### `/dependency-inventory`
Analyze dependencies with security vulnerability scanning.

##### `/api-inventory`
Discover API endpoints across multiple frameworks.

##### `/database-inventory`
Generate database schema inventory from ORM models.

##### `/config-inventory`
Discover configuration files with security masking.

##### `/test-inventory`
Discover test files and analyze coverage.

##### `/documentation-inventory`
Discover documentation files with quality metrics.

---

#### Reference Commands (2)

##### `/list-tools`
Display all 54 MCP tools across all 3 servers in formatted CLI output.

**What it does:**
- Lists tools from docs-mcp (38 tools)
- Lists tools from personas-mcp (8 tools)
- Lists tools from coderef-mcp (8 tools)
- Displays in Unicode box art format

**When to use:**
- Quick reference for available tools
- Finding the right tool for a task

---

##### `/list-commands`
Display all slash commands organized by category.

**What it does:**
- Lists all 40 slash commands
- Organized by category (Documentation, Planning, Inventory, etc.)
- Shows recommended entry points

**When to use:**
- Quick reference for available commands
- Finding the right command for a task

---

### Slash Commands vs MCP Tools

| Slash Command | MCP Tool | Parameters |
|---------------|----------|------------|
| `/generate-docs` | `generate_foundation_docs` | Uses current directory |
| `/generate-user-guide` | `generate_individual_doc` | Uses current directory, template_name="user-guide" |
| `/generate-my-guide` | `generate_individual_doc` | Uses current directory, template_name="my-guide" |
| `/establish-standards` | `establish_standards` | Uses defaults (standard depth, all focus areas) |
| `/audit-codebase` | `audit_codebase` | Uses defaults (all severity, all scope) |
| `/check-consistency` | `check_consistency` | Uses defaults (major threshold, auto-detect files) |
| `/gather-context` | (Workflow only, no MCP tool) | Interactive Q&A, saves to project root |
| `/analyze-for-planning` | `analyze_project_for_planning` | Uses current directory |
| `/get-planning-template` | `get_planning_template` | Returns all sections |
| `/validate-plan` | `validate_implementation_plan` | Prompts for filename |
| `/generate-plan-review` | `generate_plan_review_report` | Prompts for filename |
| `/handoff` | `generate_handoff_context` | Prompts for feature name and mode |
| `/start-feature` ⭐ | (Workflow) | Orchestrates full planning pipeline |
| `/execute-plan` | `execute_plan` | Prompts for feature name |
| `/quick-inventory` ⭐ | (Runs all 7 inventory tools) | Uses current directory |
| `/list-tools` | (Reference only) | Displays all MCP tools |
| `/list-commands` | (Reference only) | Displays all slash commands |

**Key difference:** Slash commands use sensible defaults. MCP tools allow full parameter control.

---

### Complete Workflow with Slash Commands

**Scenario:** Analyze project, plan feature, implement, and archive

```bash
# 1. Explore the project (one command runs all inventory tools)
You: /quick-inventory
AI: Runs 7 inventory tools, creates manifest.json, dependencies.json, api.json, etc.
AI: Summary: 245 files, 32 dependencies, 15 API endpoints

# 2. Generate documentation (if not already present)
You: /generate-docs
AI: Creates 5 foundation docs: README, ARCHITECTURE, API, COMPONENTS, SCHEMA

# 3. Plan a new feature (one command runs full planning pipeline)
You: /start-feature
AI: What feature? "auth-system"
AI: [Runs gather-context, analyze, create-plan, validate automatically]
AI: Created: context.json, analysis.json, plan.json, DELIVERABLES.md
AI: Plan score: 91/100 - PASS!

# 4. Execute the plan (generates task checklist)
You: /execute-plan
AI: Feature name? "auth-system"
AI: Generated 17 tasks for WO-AUTH-001
AI: [Displays organized TodoWrite checklist]

# 5. Implement the feature
AI: Implements according to plan with task tracking

# 6. Update deliverables after implementation
You: /update-deliverables
AI: Feature name? "auth-system"
AI: Updated metrics: 12 commits, 450 LOC, 3 days

# 7. Archive completed feature
You: /archive-feature
AI: Feature name? "auth-system"
AI: Archived to coderef/archived/auth-system/
```

**Key insight:** `/start-feature` + `/execute-plan` replaces 6-8 manual steps!

---

## Common Use Cases

### Use Case 1: Brand New Project

**Scenario**: You've built a new project and need documentation

**Steps**:
1. Complete your initial code
2. Run: `Generate foundation documentation for my project at C:\path\to\project`
3. Review generated docs in `coderef/foundation-docs/`
4. Commit to git

**Result**: Complete foundation documentation suite

---

### Use Case 2: Added API Endpoints

**Scenario**: You added new routes or changed API patterns

**Steps**:
1. Implement your API changes
2. Test the new endpoints
3. Run: `Generate individual doc for my project at C:\path\to\project using template api`
4. Review updated API.md
5. Commit changes

**Result**: API.md reflects new endpoints and patterns

---

### Use Case 3: Component Refactor

**Scenario**: You refactored components or added new ones

**Steps**:
1. Complete your component changes
2. Test components work correctly
3. Run: `Generate individual doc for my project at C:\path\to\project using template components`
4. Review updated COMPONENTS.md
5. Commit changes

**Result**: COMPONENTS.md documents new/changed components

---

### Use Case 4: Database Schema Changes

**Scenario**: You modified your database schema or TypeScript types

**Steps**:
1. Update database migrations
2. Update TypeScript types
3. Run: `Generate individual doc for my project at C:\path\to\project using template schema`
4. Review updated SCHEMA.md
5. Commit changes

**Result**: SCHEMA.md reflects new data structures

---

### Use Case 5: Major Refactor

**Scenario**: You did a major rewrite affecting multiple areas

**Steps**:
1. Complete your refactor
2. Test everything works
3. Run: `Generate foundation documentation for my project at C:\path\to\project`
4. Review all 6 regenerated docs
5. Commit changes

**Result**: All 5 foundation documents refreshed to match new architecture

---

### Use Case 6: Legacy Project Documentation

**Scenario**: You inherited a project with no documentation

**Steps**:
1. Familiarize yourself with the codebase
2. Run: `Generate foundation documentation for my project at C:\path\to\project`
3. Review generated docs for accuracy
4. Fill in any gaps manually (if needed)
5. Commit documentation

**Result**: Legacy project now has complete documentation

---

## Best Practices

### ✅ Do

- **Run on complete code**: Ensure your project has actual code files before generating docs
- **Use absolute paths**: Always provide full paths like `C:\Users\...\project`
- **Update incrementally**: Use single doc generation after small changes
- **Regenerate after major changes**: Use full generation after significant refactors
- **Review generated docs**: Check for accuracy and completeness
- **Commit docs with code**: Keep documentation in sync with code changes
- **Use as AI context**: Generated docs are optimized for AI assistant consumption

### 🚫 Don't

- **Don't edit manually**: Generated docs will be overwritten on next generation
- **Don't run on empty projects**: Need actual code to document
- **Don't use relative paths**: Always use absolute paths
- **Don't skip verification**: Always check that docs match your code
- **Don't ignore errors**: If generation fails, investigate and fix

### 💡 Tips

- **For custom content**: Create separate manual docs (e.g., `CONTRIBUTING.md`)
- **For project-specific notes**: Use inline code comments or separate `.notes/` directory
- **For temporary docs**: Create in a different location to avoid conflicts
- **For versioning**: Consider creating `docs/v1.0/`, `docs/v2.0/` for version-specific docs

---

## Changelog Best Practices

### When to Add Changelog Entries

✅ **Always document:**
- Bug fixes (any severity)
- New features
- Breaking changes
- Security patches
- Performance improvements
- Deprecations

❌ **Don't document:**
- Typo fixes in comments
- Code formatting changes
- Internal refactors with no external impact
- Development dependency updates

### Semantic Versioning

Follow **semver** (MAJOR.MINOR.PATCH):

```
1.0.0 → Initial release
1.0.1 → Patch (bug fixes, non-breaking)
1.1.0 → Minor (new features, non-breaking)
2.0.0 → Major (breaking changes)
```

**Version Bumping Rules:**
- **PATCH** (x.x.1): Bug fixes, minor improvements
- **MINOR** (x.1.0): New features, backwards compatible
- **MAJOR** (2.0.0): Breaking changes, API changes

### Change Types & Severity

**Change Types:**
| Type | When to Use | Example |
|------|------------|---------|
| `bugfix` | Fixing broken functionality | "Fixed crash when..." |
| `enhancement` | Improving existing features | "Improved performance of..." |
| `feature` | Adding new capabilities | "Added support for..." |
| `breaking_change` | Incompatible changes | "Changed API signature..." |
| `deprecation` | Marking features for removal | "Deprecated X in favor of Y" |
| `security` | Security fixes | "Patched vulnerability..." |

**Severity Levels:**
| Severity | Impact | Example |
|----------|--------|---------|
| `critical` | System broken, data loss | "Fixed data corruption bug" |
| `major` | Significant feature impact | "Added new MCP tool" |
| `minor` | Small improvements | "Improved error messages" |
| `patch` | Cosmetic, docs-only | "Fixed typo in template" |

### Writing Good Changelog Entries

#### Title (Short & Clear)
✅ **Good:**
- "Added structured changelog system with MCP tools"
- "Fixed AttributeError in generate_individual_doc"
- "Removed framework documentation - templates are self-documenting"

❌ **Bad:**
- "Updated server.py"
- "Fixed bug"
- "Changes"

#### Description (What Changed)
✅ **Good:**
```
Implemented JSON-based changelog with schema validation,
ChangelogGenerator helper class, and two MCP tools
(get_changelog and add_changelog_entry) for reading and
writing changelog entries.
```

❌ **Bad:**
```
Added changelog stuff.
```

#### Reason (Why)
✅ **Good:**
```
Enable agents to track project evolution, understand past
decisions, avoid duplicate work, and programmatically
document their own changes
```

❌ **Bad:**
```
Because we needed it.
```

#### Impact (User/System Effect)
✅ **Good:**
```
Agents can now query changelog history and add new entries
via MCP tools. Provides structured change tracking for better
project maintainability.
```

❌ **Bad:**
```
Now works.
```

### Breaking Changes

**When to mark `breaking: true`:**
- Changed function signatures
- Removed public APIs
- Changed data formats
- Altered expected behavior
- Modified configuration schema

**Always include migration guide:**
```python
add_changelog_entry(
    version="2.0.0",
    change_type="breaking_change",
    breaking=True,
    migration="""
    Old: generate_docs(path)
    New: generate_docs(path, options)

    Migration:
    1. Update all calls to include options parameter
    2. Use {} for default options
    """
)
```

### Files Array

**Be specific:**
✅ **Good:**
```python
files=[
    "server.py",
    "generators/changelog_generator.py",
    "changelog/CHANGELOG.json"
]
```

❌ **Bad:**
```python
files=["*"]  # Only use for initial release
files=["src/"]  # Too broad
```

### Contributors

**Always credit:**
```python
contributors=["willh", "Claude Code AI"]
```

**For external contributors:**
```python
contributors=["willh", "jane-smith", "Claude Code AI"]
```

### Workflow Example

**Scenario:** You just added a new feature

1. **Make code changes** → Implement feature
2. **Test thoroughly** → Ensure it works
3. **Determine version bump:**
   - New feature = MINOR bump (1.0.1 → 1.0.2)
   - Breaking change = MAJOR bump (1.0.1 → 2.0.0)
4. **Add changelog entry:**
   ```python
   add_changelog_entry(
       project_path="C:/Users/willh/.mcp-servers/docs-mcp",
       version="1.0.2",
       change_type="feature",
       severity="major",
       title="Added X feature",
       description="Implemented Y with Z capabilities...",
       files=["server.py", "lib/feature.py"],
       reason="Users requested ability to...",
       impact="Users can now...",
       contributors=["willh", "Claude Code AI"]
   )
   ```
5. **Commit together:**
   ```bash
   git add .
   git commit -m "Add X feature (v1.0.2)"
   git push
   ```

### Query Changelog

**View specific version:**
```
get_changelog(
    project_path="C:/Users/willh/.mcp-servers/docs-mcp",
    version="1.0.2"
)
```

**Find all breaking changes:**
```
get_changelog(
    project_path="C:/Users/willh/.mcp-servers/docs-mcp",
    breaking_only=true
)
```

**Filter by type:**
```
get_changelog(
    project_path="C:/Users/willh/.mcp-servers/docs-mcp",
    change_type="feature"
)
```

---

## Troubleshooting

### Problem: "Tool not found" or "No such tool available"

**Symptom**: Claude Code says it can't find the docs-mcp tools

**Cause**: MCP server not connected or not registered

**Solution**:
```bash
# 1. Check if docs-mcp is registered
claude mcp list

# 2. If not listed, register it
claude mcp add docs-mcp --scope user --command python --args "C:\Users\willh\.mcp-servers\docs-mcp\server.py"

# 3. Restart Claude Code

# 4. Verify connection
claude mcp list
# Should show: ✓ docs-mcp - Connected
```

---

### Problem: "Project path does not exist"

**Symptom**: Error says the project path doesn't exist

**Cause**: Using relative path or incorrect path

**Solution**:
```bash
# ❌ Wrong: Relative path
Generate foundation documentation for my project at ./my-project

# ❌ Wrong: Missing drive letter
Generate foundation documentation for my project at Users\willh\Desktop\project

# ✅ Correct: Absolute path
Generate foundation documentation for my project at C:\Users\willh\Desktop\my-project

# ✅ Correct: Path with spaces (quotes not needed in command)
Generate foundation documentation for my project at C:\Users\willh\Desktop\projects - current-location\sidebar-app
```

---

### Problem: Generated docs are too generic

**Symptom**: Documentation doesn't mention specific features or components

**Cause**: Project has minimal code or generic structure

**Solution**:
1. Ensure your project has actual implementation code (not just boilerplate)
2. Check that files are in expected locations (`src/`, `lib/`, etc.)
3. Try running on a specific module first
4. Review generated docs and manually enhance if needed

---

### Problem: Only got README, not all 5 foundation docs

**Symptom**: Generation stopped after creating only one document

**Cause**: Agent hit token limit or encountered an error

**Solution**:
1. Run the command again - it will continue where it left off
2. Or generate missing docs individually:
   ```
   Generate individual doc for my project at C:\path\to\project using template architecture
   Generate individual doc for my project at C:\path\to\project using template api
   ```
3. Check Claude Code logs for errors

---

### Problem: Generation takes too long

**Symptom**: Documentation generation exceeds expected time

**Cause**: Large project with many files or complex structure

**Solution**:
1. Be patient - large projects take longer (10-20 minutes possible)
2. Generate docs individually instead of all at once
3. Consider documenting modules separately
4. Check if Claude Code is responsive (not frozen)

---

### Problem: Docs reference old/removed code

**Symptom**: Generated documentation mentions features you removed

**Cause**: Documentation was generated before code changes

**Solution**:
```bash
# Regenerate all docs after major changes
Generate foundation documentation for my project at C:\path\to\project

# Or update specific doc
Generate individual doc for my project at C:\path\to\project using template architecture
```

---

### Problem: Python version error

**Symptom**: Error about Python version or module imports

**Cause**: Python 3.10+ not installed or wrong Python version active

**Solution**:
```bash
# 1. Check Python version
python --version

# 2. If < 3.10, upgrade Python

# 3. Verify docs-mcp uses correct Python
claude mcp list  # Check command path

# 4. Update MCP server with correct Python path if needed
claude mcp remove docs-mcp
claude mcp add docs-mcp --scope user --command python --args "C:\Users\willh\.mcp-servers\docs-mcp\server.py"
```

---

## Quick Reference

### Command Templates

| Goal | Command Pattern |
|------|-----------------|
| **All 5 foundation docs** | `Generate foundation documentation for my project at <path>` |
| **README only** | `Generate individual doc for my project at <path> using template readme` |
| **ARCHITECTURE only** | `Generate individual doc for my project at <path> using template architecture` |
| **API only** | `Generate individual doc for my project at <path> using template api` |
| **COMPONENTS only** | `Generate individual doc for my project at <path> using template components` |
| **SCHEMA only** | `Generate individual doc for my project at <path> using template schema` |
| **USER-GUIDE only** | `Generate individual doc for my project at <path> using template user-guide` |

### Template Reference

| Template | Output File | Typical Size | Generation Time |
|----------|-------------|--------------|-----------------|
| `readme` | README.md | 5-15KB | 1-3 min |
| `architecture` | ARCHITECTURE.md | 10-25KB | 2-4 min |
| `api` | API.md | 8-20KB | 2-4 min |
| `components` | COMPONENTS.md | 15-40KB | 3-6 min |
| `schema` | SCHEMA.md | 10-30KB | 2-4 min |
| `user-guide` | USER-GUIDE.md | 20-50KB | 4-8 min |

### MCP Tools

| Tool Name | Purpose | Parameters |
|-----------|---------|------------|
| **Documentation Generation** | | |
| `generate_foundation_docs` | Generate all 6 foundation documents | `project_path` (string) |
| `generate_individual_doc` | Generate single document | `project_path` (string), `template_name` (enum) |
| `list_templates` | List available templates | None |
| `get_template` | Get template content | `template_name` (enum) |
| **Changelog Management** | | |
| `get_changelog` | Get project changelog | `project_path`, `version` (optional), `change_type` (optional), `breaking_only` (optional) |
| `add_changelog_entry` | Add new changelog entry | `project_path`, `version`, `change_type`, `severity`, `title`, `description`, `files`, `reason`, `impact`, `breaking` (optional), `migration` (optional), `summary` (optional), `contributors` (optional) |
| `update_changelog` | Agentic workflow guide for updating changelog | `project_path`, `version` |
| **Consistency Management** | | |
| `establish_standards` | Extract UI/behavior/UX standards from codebase | `project_path`, `scan_depth` (optional), `focus_areas` (optional) |
| `audit_codebase` | Audit codebase for standards compliance | `project_path`, `standards_dir` (optional), `severity_filter` (optional), `scope` (optional), `generate_fixes` (optional) |
| **Planning Workflow** | | |
| `get_planning_template` | Get planning template sections for reference | `section` (optional, default: "all") |
| `analyze_project_for_planning` | Analyze project for planning context (optional: save to feature folder) | `project_path`, `feature_name` (optional) |
| `validate_implementation_plan` | Validate plan quality with 0-100 scoring | `project_path`, `plan_file_path` |
| `generate_plan_review_report` | Generate markdown review report | `project_path`, `plan_file_path`, `output_path` |

### Output Locations

| Project Type | Output Directory |
|--------------|------------------|
| **Default** | `<project>/coderef/foundation-docs/` |
| **Custom** | Pass `subdir` parameter (advanced usage) |

---

## Additional Resources

### Related Files

- **`README.md`** - docs-mcp project overview
- **`ARCHITECTURE.md`** - docs-mcp system design
- **`templates/power/`** - POWER framework templates
- **`generators/`** - Generator implementation

### External Links

- [POWER Framework Documentation](https://github.com/srwlli/docs-mcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)

---

**Last Updated**: 2025-10-16
**Version**: 2.0.0
**Maintainer**: willh

---

> 💡 **Pro Tip**: Generated documentation is optimized for both human readers and AI assistants. Use these docs as context when working with Claude Code on your projects!