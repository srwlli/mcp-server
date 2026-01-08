# Documentation Catalog - coderef-docs MCP Server

**Complete list of all documentation types this server can generate**

---

## Foundation Documentation (Technical)

**Location:** `coderef/foundation-docs/`

### 1. README.md
- **Purpose:** Project overview and quick start guide
- **Tool:** `generate_foundation_docs` or `generate_individual_doc`
- **Template:** `templates/power/readme.txt`
- **Audience:** Developers, new contributors
- **Contents:**
  - Project summary
  - Installation instructions
  - Quick start examples
  - Key features
  - Links to detailed docs

### 2. ARCHITECTURE.md
- **Purpose:** System architecture and design decisions
- **Tool:** `generate_foundation_docs` or `generate_individual_doc`
- **Template:** `templates/power/architecture.txt`
- **Audience:** Developers, architects
- **Contents:**
  - Component overview
  - Design patterns
  - Data flow diagrams
  - Technology stack
  - Integration points
- **Context Injection:** ✅ Real code structure from @coderef/core CLI

### 3. SCHEMA.md
- **Purpose:** Data models and database schemas
- **Tool:** `generate_foundation_docs` or `generate_individual_doc`
- **Template:** `templates/power/schema.txt`
- **Audience:** Developers, database admins
- **Contents:**
  - Entity definitions
  - Relationships (ERD)
  - Constraints and validations
  - Migrations
- **Context Injection:** ✅ Real schemas extracted from @coderef/core CLI

### 4. API.md
- **Purpose:** API endpoints and usage documentation
- **Tool:** `generate_foundation_docs` or `generate_individual_doc`
- **Template:** `templates/power/api.txt`
- **Audience:** API consumers, developers
- **Contents:**
  - Endpoint catalog
  - Request/response formats
  - Authentication
  - Error codes
  - Rate limits
- **Context Injection:** ✅ Real endpoints extracted from @coderef/core CLI

### 5. COMPONENTS.md
- **Purpose:** Component hierarchy and props documentation
- **Tool:** `generate_foundation_docs` or `generate_individual_doc`
- **Template:** `templates/power/components.txt`
- **Audience:** Frontend developers
- **Contents:**
  - Component tree
  - Props and state
  - Usage examples
  - Styling guidelines
- **Context Injection:** ✅ Real components extracted from @coderef/core CLI
- **Note:** Only generated for UI/frontend projects

### 6. project-context.json
- **Purpose:** Structured project metadata for agents
- **Tool:** `generate_foundation_docs` (auto-generated alongside docs)
- **Audience:** AI agents, automation tools
- **Contents:**
  - Project metadata
  - Dependencies
  - File structure
  - Code statistics

---

## User-Facing Documentation

**Location:** `coderef/user/`

### 7. USER-GUIDE.md
- **Purpose:** End-user manual for application features
- **Tool:** `generate_individual_doc`
- **Template:** `templates/power/user-guide.txt`
- **Audience:** End users, product managers
- **Contents:**
  - Getting started
  - Feature walkthroughs
  - Troubleshooting
  - FAQs

### 8. my-guide.md
- **Purpose:** Tool-specific command reference for developers
- **Tool:** `generate_individual_doc`
- **Template:** `templates/power/my-guide.txt`
- **Audience:** Developers using the tool
- **Contents:**
  - Command catalog
  - Usage examples
  - Configuration options
  - Best practices

### 9. FEATURES.md
- **Purpose:** Feature changelog and roadmap
- **Tool:** `generate_individual_doc`
- **Template:** `templates/power/features.txt`
- **Audience:** Product managers, stakeholders
- **Contents:**
  - Completed features
  - In-progress work
  - Planned features
  - Feature metrics

### 10. quickref.md
- **Purpose:** Scannable quick reference card
- **Tool:** `generate_quickref_interactive`
- **Template:** Interactive workflow (no static template)
- **Audience:** All users (developers, end-users)
- **Contents:**
  - Essential commands (top 10-15)
  - Common workflows (3-5 steps each)
  - Quick troubleshooting
  - Key concepts
- **Modes:** CLI, Web, API, Desktop, Library
- **Target:** 150-250 lines, 30-60 second scan time

---

## Resource Sheets (NEW in v3.4.0)

**Location:** `coderef/reference-sheets/{element-name}/`

### 11. Resource Sheet - Markdown
- **Purpose:** Human-readable element documentation
- **Tool:** `generate_resource_sheet`
- **Format:** Markdown
- **Audience:** Developers
- **Sections (Universal):**
  - Architecture & Design
  - Integration Points
  - Testing
  - Performance
- **Sections (Conditional, Phase 2):**
  - Props & Events (React/UI components)
  - State Management (stateful components)
  - Lifecycle (components with lifecycle)
  - Authentication (auth-aware code)
  - Error Handling (error boundary code)
  - Endpoints (API/network code)
  - Accessibility (a11y-aware components)
  - Hooks Side Effects (React hooks)

### 12. Resource Sheet - JSON Schema
- **Purpose:** Machine-readable schema for tooling
- **Tool:** `generate_resource_sheet`
- **Format:** JSON Schema
- **Audience:** IDEs, linters, validators
- **Contents:**
  - Type definitions
  - Property schemas
  - Validation rules
  - Examples

### 13. Resource Sheet - JSDoc
- **Purpose:** Inline code documentation
- **Tool:** `generate_resource_sheet`
- **Format:** JSDoc comments
- **Audience:** Developers (for copying into code)
- **Contents:**
  - Function signatures
  - Parameter descriptions
  - Return types
  - Usage examples

**Modes:**
- `reverse-engineer`: Analyze existing code
- `template`: Scaffold new element
- `refresh`: Update existing docs

---

## Standards & Compliance

**Location:** `coderef/standards/`

### 14. UI-STANDARDS.md
- **Purpose:** UI component patterns and conventions
- **Tool:** `establish_standards`
- **Audience:** Frontend developers
- **Contents:**
  - Button patterns
  - Modal styles
  - Form layouts
  - Color schemes
  - Typography
- **Source:** Extracted from codebase via pattern analysis

### 15. BEHAVIOR-STANDARDS.md
- **Purpose:** Behavioral patterns and conventions
- **Tool:** `establish_standards`
- **Audience:** All developers
- **Contents:**
  - Error handling patterns
  - Loading states
  - Validation rules
  - State management
- **Source:** Extracted from codebase via pattern analysis

### 16. UX-PATTERNS.md
- **Purpose:** User experience flows and conventions
- **Tool:** `establish_standards`
- **Audience:** UX designers, developers
- **Contents:**
  - Navigation patterns
  - Permission flows
  - Onboarding sequences
  - Feedback mechanisms
- **Source:** Extracted from codebase via pattern analysis

### 17. COMPONENT-INDEX.md
- **Purpose:** Component inventory and usage tracking
- **Tool:** `establish_standards`
- **Audience:** Developers
- **Contents:**
  - Component catalog
  - Usage frequency
  - Dependencies
  - Reusability metrics
- **Source:** Extracted from codebase via pattern analysis

### 18. Compliance Audit Report
- **Purpose:** Standards compliance score and violations
- **Tool:** `audit_codebase`
- **Format:** Markdown report
- **Audience:** Tech leads, code reviewers
- **Contents:**
  - Overall score (0-100)
  - Violations by severity (critical/major/minor)
  - File-level issues
  - Remediation suggestions
- **Output:** Console or saved to `coderef/standards/audit-report-{timestamp}.md`

---

## Changelog & Change Management

**Location:** `coderef/changelog/`

### 19. CHANGELOG.json
- **Purpose:** Structured changelog with version history
- **Tool:** `record_changes` (agentic) or `add_changelog_entry` (manual)
- **Audience:** All stakeholders
- **Contents:**
  - Version entries
  - Change types (feature/bugfix/breaking/security)
  - Severity levels
  - Workorder tracking
  - File changes
  - Migration guides
- **Schema:** `coderef/changelog/schema.json`

---

## Workorder Documentation (UDS-compliant)

**Location:** `coderef/workorder/{feature-name}/`

### 20. plan.json
- **Purpose:** 10-section implementation plan
- **Tool:** Generated by `coderef-workflow` MCP, not this server
- **Audience:** Agents, developers
- **Contents:**
  - Meta documentation (workorder ID, status)
  - Preparation summary
  - Executive summary
  - Risk assessment
  - Current state analysis
  - Key features
  - Task breakdown
  - Testing strategy
  - Success criteria
- **UDS:** ✅ Metadata in META_DOCUMENTATION.uds section

### 21. context.json
- **Purpose:** Feature requirements and constraints
- **Tool:** Generated by `coderef-workflow` MCP, not this server
- **Audience:** Agents, planning workflows
- **Contents:**
  - Feature description
  - Requirements
  - Constraints
  - Success criteria
- **UDS:** ✅ Metadata in _uds section

### 22. analysis.json
- **Purpose:** Project analysis and discovered patterns
- **Tool:** Generated by `coderef-workflow` MCP, not this server
- **Audience:** Agents, planning workflows
- **Contents:**
  - Foundation docs discovered
  - Coding standards
  - Reference components
  - Dependencies
- **UDS:** ✅ Metadata in _uds section

### 23. DELIVERABLES.md
- **Purpose:** Feature completion metrics and checklist
- **Tool:** Generated by `coderef-workflow` MCP, not this server
- **Audience:** Agents, project managers
- **Contents:**
  - Phase completion checklist
  - Git metrics (LOC, commits, time)
  - Contributors
  - Status
- **UDS:** ✅ YAML frontmatter headers/footers

### 24. claude.md
- **Purpose:** Agent handoff context for feature work
- **Tool:** `generate_handoff_context` (moved to coderef-workflow)
- **Audience:** AI agents
- **Contents:**
  - Feature summary
  - Current state
  - Next steps
  - Code locations
  - Decisions made
- **UDS:** ✅ YAML frontmatter headers/footers
- **Modes:** `full` (comprehensive) or `minimal` (quick summary)

---

## Summary Statistics

### By Category
- **Foundation Docs:** 6 types (README, ARCHITECTURE, SCHEMA, API, COMPONENTS, project-context)
- **User Docs:** 4 types (USER-GUIDE, my-guide, FEATURES, quickref)
- **Resource Sheets:** 3 formats × N elements (Markdown, JSON Schema, JSDoc)
- **Standards:** 4 types + audit reports (UI, Behavior, UX, Component Index)
- **Changelog:** 1 type (CHANGELOG.json)
- **Workorder Docs:** 5 types (plan, context, analysis, DELIVERABLES, claude.md)

### By Tool
- `generate_foundation_docs`: 6 docs (sequential generation)
- `generate_individual_doc`: 9 docs (any single doc)
- `generate_quickref_interactive`: 1 doc (interactive workflow)
- `generate_resource_sheet`: 3 formats per element (composable modules)
- `establish_standards`: 4 docs (standards extraction)
- `audit_codebase`: 1 doc (audit report)
- `record_changes` / `add_changelog_entry`: 1 doc (CHANGELOG.json)

### Total: 24+ Document Types

---

## Output Locations

```
project-root/
├── README.md                              # Foundation: Project overview
├── coderef/
│   ├── foundation-docs/
│   │   ├── ARCHITECTURE.md                # Foundation: Architecture
│   │   ├── SCHEMA.md                      # Foundation: Data models
│   │   ├── API.md                         # Foundation: API reference
│   │   ├── COMPONENTS.md                  # Foundation: Component docs
│   │   └── project-context.json           # Foundation: Structured metadata
│   ├── user/
│   │   ├── USER-GUIDE.md                  # User: End-user manual
│   │   ├── my-guide.md                    # User: Developer tool reference
│   │   ├── FEATURES.md                    # User: Feature changelog
│   │   └── quickref.md                    # User: Quick reference card
│   ├── reference-sheets/
│   │   └── {element-name}/
│   │       ├── {element}.md               # Resource: Markdown docs
│   │       ├── {element}.schema.json      # Resource: JSON Schema
│   │       └── {element}.jsdoc.txt        # Resource: JSDoc comments
│   ├── standards/
│   │   ├── UI-STANDARDS.md                # Standards: UI patterns
│   │   ├── BEHAVIOR-STANDARDS.md          # Standards: Behavior patterns
│   │   ├── UX-PATTERNS.md                 # Standards: UX flows
│   │   ├── COMPONENT-INDEX.md             # Standards: Component inventory
│   │   └── audit-report-{date}.md         # Standards: Compliance audit
│   ├── changelog/
│   │   └── CHANGELOG.json                 # Changelog: Version history
│   └── workorder/
│       └── {feature-name}/
│           ├── plan.json                  # Workorder: Implementation plan
│           ├── context.json               # Workorder: Requirements
│           ├── analysis.json              # Workorder: Project analysis
│           ├── DELIVERABLES.md            # Workorder: Metrics
│           └── claude.md                  # Workorder: Agent handoff
```

---

## Template System

### POWER Framework
All foundation and user docs follow the **POWER** structure:
- **P**urpose - Why this exists
- **O**verview - What's included
- **W**hat/Why/When - Detailed content
- **E**xamples - Concrete illustrations
- **R**eferences - Related documentation

### Universal Document Standard (UDS)
Workorder documents include YAML frontmatter/JSON metadata:
- Workorder tracking
- Lifecycle status
- Provenance
- Review scheduling
- AI attribution

---

## Quick Reference: Which Tool Generates What?

| Tool | Generates | Count |
|------|-----------|-------|
| `generate_foundation_docs` | README, ARCHITECTURE, SCHEMA, API, COMPONENTS, project-context | 6 |
| `generate_individual_doc` | Any single foundation or user doc | 9 |
| `generate_quickref_interactive` | quickref.md | 1 |
| `generate_resource_sheet` | Element docs (MD + Schema + JSDoc) | 3 per element |
| `establish_standards` | UI/Behavior/UX/Component standards | 4 |
| `audit_codebase` | Compliance audit report | 1 |
| `record_changes` | CHANGELOG.json entries | 1 |
| `add_changelog_entry` | CHANGELOG.json entries (manual) | 1 |

---

**Generated:** 2026-01-08
**Server Version:** 3.4.0
**Total Document Types:** 24+
