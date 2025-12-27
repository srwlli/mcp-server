# CodeRef Ecosystem - Complete Tool Matrix

**Generated:** 2025-12-27
**Status:** ✅ All 4 servers mapped (63 total tools, 10 shared)

---

## Overview

| Server | Unique Tools | Shared Tools | Total |
|--------|--------------|--------------|-------|
| **coderef-context** | 10 | 0 | 10 |
| **coderef-docs** | 1 | 10 | 11 |
| **coderef-workflow** | 23 | 10 | 33 |
| **coderef-personas** | 8 | 0 | 8 |
| **TOTAL** | 42 | 10 | 52 |

---

## coderef-context (10 tools)

**Purpose:** Code Intelligence - AST-based analysis and dependency tracking

| Tool | Function | Input | Output |
|------|----------|-------|--------|
| `coderef_scan` | Discover all code elements (functions, classes, components) | project_path, languages | Inventory with AST analysis |
| `coderef_query` | Query code relationships (calls, imports, depends-on) | project_path, query_type, target | Dependency relationships |
| `coderef_impact` | Analyze impact of modifying/deleting a code element | project_path, element, operation | Ripple effect analysis |
| `coderef_complexity` | Get complexity metrics for code elements | project_path, element | Complexity scores |
| `coderef_patterns` | Discover code patterns and test coverage gaps | project_path, pattern_type, limit | Pattern list with locations |
| `coderef_coverage` | Analyze test coverage in codebase | project_path, format | Coverage report (summary/detailed) |
| `coderef_diagram` | Generate visual dependency diagrams | project_path, diagram_type, format, depth | Mermaid or Graphviz output |
| `coderef_drift` | Detect drift between CodeRef index and current code | project_path, index_path | Drift report |
| `coderef_validate` | Validate CodeRef2 references in codebase | project_path, pattern | Validation results |
| `coderef_context` | Generate comprehensive codebase context | project_path, languages, output_format | JSON + Markdown context |

---

## coderef-docs (11 tools)

**Purpose:** Documentation Generation & Standards Management

### Unique to coderef-docs (1)

| Tool | Function |
|------|----------|
| `record_changes` | Auto-detect git changes and update changelog |

### Shared with coderef-workflow (10)

| Tool | Function | Purpose |
|------|----------|---------|
| `list_templates` | List available documentation templates | Template discovery |
| `get_template` | Retrieve specific template content | Template viewing |
| `generate_foundation_docs` | Generate README/ARCHITECTURE/SCHEMA/API | Foundation doc generation |
| `generate_individual_doc` | Generate single documentation file | Individual doc creation |
| `generate_quickref_interactive` | Interactive quickref guide generator | Quick reference creation |
| `establish_standards` | Scan codebase for UI/UX/behavior patterns | Standards discovery |
| `audit_codebase` | Audit codebase against standards | Standards compliance |
| `check_consistency` | Check code changes for consistency violations | Pre-commit validation |
| `add_changelog_entry` | Add new changelog entry | Changelog management |
| `get_changelog` | Get changelog history | Changelog retrieval |

---

## coderef-workflow (33 tools)

**Purpose:** Feature Planning, Execution Tracking, Multi-Agent Orchestration

### Planning Phase (6 unique)

| Tool | Function |
|------|----------|
| `gather_context` | Collect feature requirements and constraints |
| `analyze_project_for_planning` | Scan codebase for architecture/patterns (uses coderef-context) |
| `get_planning_template` | Retrieve 10-section plan template |
| `create_plan` | Generate comprehensive implementation plan |
| `validate_implementation_plan` | Score plan quality (0-100) |
| `generate_plan_review_report` | Create markdown review report |

### Execution & Tracking (5 unique)

| Tool | Function | Related Command |
|------|----------|-----------------|
| `execute_plan` | Align plan with todo list for tracking | `/align-plan` |
| `update_task_status` | Track individual task progress | `/update-task-status` |
| `update_deliverables` | Update metrics from git history | `/update-deliverables` |
| `generate_deliverables_template` | Create DELIVERABLES.md structure | `/generate-deliverables` |
| `track_agent_status` | Dashboard for agent assignments | `/track-agent-status` |

### Multi-Agent Coordination (5 unique)

| Tool | Function |
|------|----------|
| `generate_agent_communication` | Create coordination file for parallel agents |
| `assign_agent_task` | Assign task to specific agent (1-10) |
| `verify_agent_completion` | Validate agent work with git diffs |
| `generate_handoff_context` | Create claude.md for agent handoffs |
| `aggregate_agent_deliverables` | Combine metrics from multi-agent runs |

### Archival & Inventory (5 unique)

| Tool | Function |
|------|----------|
| `archive_feature` | Move completed feature to archive |
| `generate_features_inventory` | List all active & archived features |
| `audit_plans` | Health check on all plans in coderef/workorder |
| `log_workorder` | Add entry to global workorder log |
| `get_workorder_log` | Query workorder history |

### Risk Assessment (1 unique)

| Tool | Function |
|------|----------|
| `assess_risk` | AI-powered risk scoring (0-100) for code changes |

### Documentation Management (4 unique)

| Tool | Function |
|------|----------|
| `update_changelog` | Update changelog from git diff (agentic) |
| `update_all_documentation` | Update README/CHANGELOG/CLAUDE.md simultaneously |
| `coderef_foundation_docs` | Unified foundation docs generator (wraps coderef-docs) |
| `generate_foundation_docs` | Generate foundation docs (orchestrates) |

### Shared with coderef-docs (10)

See coderef-docs section above.

---

## coderef-personas (8 tools)

**Purpose:** Expert AI Persona Management - 9 domain specialists

| Tool | Function | Use Case |
|------|----------|----------|
| `use_persona` | Activate expert persona (Ava, Marcus, Quinn, etc.) | Switch to specialized agent |
| `get_active_persona` | Get currently active persona info | Check current context |
| `clear_persona` | Deactivate persona, return to default | Reset to general mode |
| `list_personas` | List all available personas with descriptions | Discover experts |
| `create_custom_persona` | Create new custom persona through guided workflow | Extend expertise |
| `execute_plan_interactive` | Execute plan with guided step-by-step or batch mode | Interactive execution |
| `generate_todo_list` | Convert plan task breakdown to TodoWrite format | Task list generation |
| `track_plan_execution` | Sync plan progress with todo status in real-time | Progress tracking |

### Built-in Personas (9)
1. **Ava** - Frontend Specialist (React, Vue, Angular)
2. **Marcus** - Backend Specialist (Python, Node, databases)
3. **Quinn** - DevOps Specialist (infrastructure, deployment)
4. **Taylor** - General Purpose Agent
5. **Devon** - Project Setup & Bootstrap Specialist
6. **Lloyd** - Project Coordinator (orchestration)
7. **CodeRef Assistant** - CodeRef expert
8. **Docs Expert** - Documentation specialist
9. **MCP Expert** - MCP integration specialist

---

## Shared Tools (10 tools)

These tools are implemented in **both coderef-docs and coderef-workflow**:

| Tool | Purpose | Why Shared |
|------|---------|-----------|
| `list_templates` | List documentation templates | Both generate docs |
| `get_template` | Retrieve template content | Both generate docs |
| `generate_foundation_docs` | Generate foundation documentation | Core doc capability |
| `generate_individual_doc` | Generate single doc file | Core doc capability |
| `generate_quickref_interactive` | Interactive quickref generation | Core doc capability |
| `establish_standards` | Discover UI/UX/behavior standards | Standards for both |
| `audit_codebase` | Audit against standards | Standards for both |
| `check_consistency` | Pre-commit consistency checks | Quality gate for both |
| `add_changelog_entry` | Add changelog entry | Changelog for both |
| `get_changelog` | Get changelog history | Changelog for both |

**Rationale:** Documentation tools are shared because both servers need to generate and manage documentation. Workflow orchestrates document generation and changelog management during feature development.

---

## Tool Integration Map

```
coderef-context
├─ Provides code intelligence to:
│  ├─ coderef-workflow (planning & impact analysis)
│  └─ coderef-docs (used for standards discovery)
│
coderef-docs
├─ Tools for document generation & changelog
├─ Shared with coderef-workflow (doc tools)
└─ Provides foundation docs to all servers
│
coderef-workflow
├─ Orchestrates complete feature lifecycle
├─ Uses coderef-context for planning intelligence
├─ Uses coderef-docs tools for documentation
├─ Calls coderef-personas for expert execution
└─ Coordinates multi-agent implementations
│
coderef-personas
├─ Provides expert personas for all servers
├─ Supports coderef-workflow execution
└─ Enables specialized agent behaviors
```

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total unique tools** | 42 |
| **Shared tools** | 10 |
| **Total tool count** | 52 |
| **coderef-context coverage** | Code intelligence only |
| **coderef-docs coverage** | Documentation + shared |
| **coderef-workflow coverage** | Planning + execution + docs (shared) |
| **coderef-personas coverage** | Persona + execution management |

---

## Access Patterns

### Direct Tool Usage
- Use coderef-context tools directly for code analysis
- Use coderef-personas tools directly for persona management

### Via Slash Commands
- Use `/create-workorder` to access workflow tools
- Use `/align-plan` to track plan execution
- Use `/establish-standards` for standards management

### Multi-Server Coordination
- coderef-workflow calls coderef-context for planning
- coderef-workflow calls coderef-docs for documentation
- coderef-personas integrates with any server for execution

---

**Last Updated:** 2025-12-27
**Status:** ✅ Production - All 4 servers integrated and mapped
