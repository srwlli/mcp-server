# Document Report - coderef-docs

**Agent:** coderef-docs
**Workorder:** WO-CODEREF-IO-INVENTORY-002
**Date:** 2026-01-02
**Status:** Complete

---

## Complete Document List

| Filename | Type | I/O | Source/Destination | Notes |
|----------|------|-----|-------------------|-------|
| CLAUDE.md | foundation_doc | input | Project root | Architecture context for doc generation |
| README.md | foundation_doc | both | Project root | Read existing, update version |
| coderef/foundation-docs/README.md | foundation_doc | both | Generated | Generate project README |
| coderef/foundation-docs/ARCHITECTURE.md | foundation_doc | both | Generated | Generate architecture docs |
| coderef/foundation-docs/API.md | foundation_doc | both | Generated | Generate API documentation |
| coderef/foundation-docs/COMPONENTS.md | foundation_doc | both | Generated | Generate component inventory |
| coderef/foundation-docs/SCHEMA.md | foundation_doc | both | Generated | Generate schema documentation |
| coderef/user/my-guide.md | foundation_doc | output | Generated | Generate tool guide |
| coderef/user/USER-GUIDE.md | foundation_doc | output | Generated | Generate user guide |
| coderef/user/FEATURES.md | foundation_doc | output | Generated | Generate features list |
| coderef/user/quickref.md | foundation_doc | output | Generated | Generate quick reference guide |
| coderef/standards/ui-patterns.md | standard_doc | both | Generated | Generate/audit UI patterns |
| coderef/standards/behavior-patterns.md | standard_doc | both | Generated | Generate/audit behavior patterns |
| coderef/standards/ux-patterns.md | standard_doc | both | Generated | Generate/audit UX patterns |
| coderef/standards/standards-overview.md | standard_doc | both | Generated | Generate/audit standards summary |
| coderef/standards/audit-report-{timestamp}.md | standard_doc | output | Generated | Generate audit reports |
| coderef/workorder/{feature-name}/context.json | workflow_doc | input | coderef-workflow | Read feature context for changelog |
| coderef/workorder/{feature-name}/plan.json | workflow_doc | input | coderef-workflow | Read plan details for changelog |
| coderef/CHANGELOG.json | workflow_doc | both | Project root | Read/update changelog entries |
| .coderef/index.json | coderef_output | input | coderef-context | Extract APIs/schemas/components |
| .coderef/context.md | coderef_output | input | coderef-context | Read codebase overview |
| .coderef/graph.json | coderef_output | input | coderef-context | Dependency graph analysis |
| .coderef/reports/patterns.json | coderef_output | input | coderef-context | Read code patterns for standards |
| .coderef/reports/coverage.json | coderef_output | input | coderef-context | Test coverage analysis |
| .coderef/reports/complexity.json | coderef_output | input | coderef-context | Complexity metrics |
| .coderef/diagrams/dependencies.mmd | coderef_output | input | coderef-context | Dependency diagrams for docs |
| templates/power/readme.md | config | input | coderef-docs | POWER framework template |
| templates/power/architecture.md | config | input | coderef-docs | POWER framework template |
| templates/power/api.md | config | input | coderef-docs | POWER framework template |
| templates/power/components.md | config | input | coderef-docs | POWER framework template |
| templates/power/schema.md | config | input | coderef-docs | POWER framework template |
| templates/power/user-guide.md | config | input | coderef-docs | POWER framework template |
| templates/power/my-guide.md | config | input | coderef-docs | POWER framework template |
| templates/quickref/{app_type}-template.md | config | input | coderef-docs | Quickref generation templates |
| package.json | config | input | Project root | Read project metadata |
| pyproject.toml | config | input | Project root | Read Python project metadata |

---

## Cross-Agent Dependencies

### Consumes From:

- **coderef-context**: All .coderef/ outputs (index.json, context.md, graph.json, reports/, diagrams/)
  - Used for context injection during foundation doc generation
  - Used for fast standards pattern detection (v3.3.0+)

- **coderef-workflow**: Workflow docs (context.json, plan.json)
  - Read during changelog recording to link changes to features
  - Used by record_changes and update_all_documentation tools

### Produces For:

- **All agents**: Foundation docs (README, ARCHITECTURE, API, COMPONENTS, SCHEMA)
  - Consumed by agents for project context understanding
  - Referenced during planning and implementation

- **Users**: User-facing docs (my-guide.md, USER-GUIDE.md, FEATURES.md, quickref.md)
  - End-user documentation for tool usage

- **All agents**: Standards docs (ui-patterns, behavior-patterns, ux-patterns)
  - Consumed for consistency checking and implementation guidance

- **coderef-workflow**: CHANGELOG.json updates
  - Workflow orchestrator uses changelog for release tracking

---

## External Sources

### @coderef/core CLI
- **Location**: C:/Users/willh/Desktop/projects/coderef-system/packages/cli
- **Purpose**: Extracts APIs, schemas, components from .coderef/index.json
- **Integration**: extractors.py calls CLI via subprocess (v3.2.0+)
- **Fallback**: Graceful degradation to template-only if unavailable

### Git Repository
- **Purpose**: Auto-detect changed files for changelog recording
- **Integration**: record_changes tool runs git diff commands
- **Tools**: git diff, git log, git status

---

## Summary

- **Total Documents**: 36 unique files
- **Inputs**: 30 files (foundation docs, standards, workflow docs, .coderef/ outputs, templates, configs)
- **Outputs**: 16 files (foundation docs, user docs, standards, audit reports, changelog)
- **Both (Read/Write)**: 10 files (foundation docs, standards, changelog)

---

**Generated by:** coderef-docs
**Workorder:** WO-CODEREF-IO-INVENTORY-002
**Date:** 2026-01-02
