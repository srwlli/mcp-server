# DELIVERABLES: context-experts

**Project**: docs-mcp
**Feature**: context-experts
**Workorder**: WO-CONTEXT-EXPERTS-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-07

---

## Executive Summary

**Goal**: Provide Lloyd with meta-tools to create project-specific context-experts for ANY project. The tool provides infrastructure, Lloyd handles project-specific configuration.

**Description**: Create domain-specific context experts that are onboarded by Lloyd and maintain deep context about their assigned area of the codebase (UI, DB, Script, Docs, API, Core, Test, Infra)

---

## Implementation Phases

### Phase 1: Foundation

**Description**: Constants, data models, and validation

**Estimated Duration**: TBD

**Deliverables**:
- constants.py updates
- context_expert_models.py
- validation.py updates

### Phase 2: Context Engine

**Description**: Generator class with code analysis

**Estimated Duration**: TBD

**Deliverables**:
- generators/context_expert_generator.py

### Phase 3: MCP Tools

**Description**: Handler implementations and registration

**Estimated Duration**: TBD

**Deliverables**:
- tool_handlers.py updates
- server.py updates

### Phase 4: Integration

**Description**: Slash commands and documentation

**Estimated Duration**: TBD

**Deliverables**:
- Slash commands
- CLAUDE.md updates


---

## Metrics

### Code Changes
- **Lines of Code Added**: TBD
- **Lines of Code Deleted**: TBD
- **Net LOC**: TBD
- **Files Modified**: TBD

### Commit Activity
- **Total Commits**: TBD
- **First Commit**: TBD
- **Last Commit**: TBD
- **Contributors**: TBD

### Time Investment
- **Days Elapsed**: TBD
- **Hours Spent (Wall Clock)**: TBD

---

## Task Completion Checklist

- [ ] [CONST-001] Add ContextExpertPaths class to constants.py
- [ ] [CONST-002] Add ContextExpertStatus, ContextExpertCapability, ResourceType, ExpertDomain enums
- [ ] [MODEL-001] Create context_expert_models.py with GitHistoryEntry, CodeStructure TypedDicts
- [ ] [MODEL-002] Add RelationshipContext, UsagePattern, ContextExpertDefinition TypedDicts
- [ ] [MODEL-003] Add ExpertOnboarding TypedDict for Lloyd briefing data
- [ ] [VALID-001] Add validate_resource_path() to validation.py
- [ ] [VALID-002] Add validate_expert_id() with CE-{hash}-NNN format
- [ ] [VALID-003] Add validate_context_expert_inputs() for full validation
- [ ] [GEN-001] Create generators/context_expert_generator.py with ContextExpertGenerator class
- [ ] [GEN-002] Implement analyze_code_structure() with Python AST parsing
- [ ] [GEN-003] Implement analyze_code_structure() JS/TS regex fallback
- [ ] [GEN-004] Implement extract_git_history() using git log
- [ ] [GEN-005] Implement detect_relationships() for imports/exports
- [ ] [GEN-006] Implement calculate_staleness() based on content hash
- [ ] [GEN-007] Implement suggest_candidates() for auto-discovery
- [ ] [TOOL-001] Implement handle_create_context_expert() handler
- [ ] [TOOL-002] Implement handle_list_context_experts() handler
- [ ] [TOOL-003] Implement handle_get_context_expert() handler
- [ ] [TOOL-004] Implement handle_suggest_context_experts() handler
- [ ] [TOOL-005] Implement handle_update_context_expert() handler
- [ ] [TOOL-006] Implement handle_activate_context_expert() handler
- [ ] [REG-001] Register all 6 tools in server.py with input schemas
- [ ] [REG-002] Add handlers to TOOL_HANDLERS registry
- [ ] [CMD-001] Create slash commands in .claude/commands/
- [ ] [CMD-002] Deploy slash commands to ~/.claude/commands/
- [ ] [DOC-001] Update CLAUDE.md with full tool documentation

---

## Files Created/Modified

- **context_expert_models.py** - Pydantic/TypedDict data schemas
- **generators/context_expert_generator.py** - Core generator class
- **.claude/commands/create-context-expert.md** - Slash command
- **.claude/commands/list-context-experts.md** - Slash command
- **.claude/commands/suggest-context-experts.md** - Slash command
- **.claude/commands/activate-context-expert.md** - Slash command
- **constants.py** - TBD
- **validation.py** - TBD
- **tool_handlers.py** - TBD
- **server.py** - TBD
- **CLAUDE.md** - TBD

---

## Success Criteria

- All 6 MCP tools pass validation tests
- Expert creation completes in < 5 seconds
- Code structure analysis accurate for Python/JS/TS

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-07
