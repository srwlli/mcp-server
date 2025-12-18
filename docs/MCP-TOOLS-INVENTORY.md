# MCP Tools Inventory

**Generated**: 2025-12-18
**Workorder**: WO-MCP-TOOLS-REVIEW-001
**Status**: Audit Complete

---

## Executive Summary

| Server | Tools | Token Impact | Purpose |
|--------|-------|--------------|---------|
| docs-mcp | 35 | High | Documentation, planning, workflows |
| coderef-mcp | 8 | Medium | Code analysis, querying |
| personas-mcp | 8 | Low | Persona management, plan execution |
| scriptboard-mcp | 8 | Medium | Clipboard, CodeRef integration |
| **Total** | **59** | - | - |

### Redundancy Analysis

- **8 tools identified as redundant** (14% of total)
- **4 tools** in scriptboard-mcp duplicate coderef-mcp functionality
- **3 tools** in personas-mcp duplicate docs-mcp planning tools
- **1 tool** in docs-mcp has newer replacement

---

## Server: docs-mcp (35 tools)

**Purpose**: Documentation generation, changelog management, planning workflows, consistency auditing, multi-agent coordination

### Documentation Tools (6)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `list_templates` | List available POWER framework templates | Keep |
| `get_template` | Retrieve specific template content | Keep |
| `generate_foundation_docs` | Generate all foundation docs | **Deprecate** (use coderef_foundation_docs) |
| `generate_individual_doc` | Generate single documentation file | Keep |
| `generate_quickref_interactive` | Interactive quickref generation | Keep |
| `coderef_foundation_docs` | Unified foundation docs with coderef analysis | Keep |

### Changelog Tools (3)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `get_changelog` | Query changelog with filters | Keep |
| `add_changelog_entry` | Add new changelog entry | Keep |
| `update_changelog` | Meta-tool for AI-driven changelog updates | Keep |

### Planning Tools (9)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `get_planning_template` | Get planning template | Keep |
| `analyze_project_for_planning` | Analyze project for planning context | Keep |
| `gather_context` | Gather feature requirements | Keep |
| `create_plan` | Create implementation plan | Keep |
| `validate_implementation_plan` | Validate plan quality (0-100 score) | Keep |
| `generate_plan_review_report` | Generate markdown review report | Keep |
| `generate_deliverables_template` | Generate DELIVERABLES.md | Keep |
| `update_deliverables` | Update deliverables with git metrics | Keep |
| `execute_plan` | Generate TodoWrite task list from plan | Keep |

### Consistency Tools (3)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `establish_standards` | Extract coding standards from codebase | Keep |
| `audit_codebase` | Audit for standards compliance | Keep |
| `check_consistency` | Quick consistency check (pre-commit) | Keep |

### Multi-Agent Tools (6)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `generate_agent_communication` | Generate communication.json | Keep |
| `assign_agent_task` | Assign task to agent | Keep |
| `verify_agent_completion` | Verify agent completion | Keep |
| `aggregate_agent_deliverables` | Aggregate metrics from agents | Keep |
| `track_agent_status` | Track agent status dashboard | Keep |
| `generate_handoff_context` | Generate handoff context files | Keep |

### Workflow Tools (5)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `update_task_status` | Update task status in plan.json | Keep |
| `audit_plans` | Audit all plans for health | Keep |
| `archive_feature` | Archive completed features | Keep |
| `update_all_documentation` | Update all docs after feature completion | Keep |
| `assess_risk` | AI-powered risk assessment | Keep |

### Workorder Tools (2)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `log_workorder` | Log workorder to activity log | Keep |
| `get_workorder_log` | Query workorder log | Keep |

### Inventory Tools (1)
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `generate_features_inventory` | Generate inventory of all features | Keep |

---

## Server: coderef-mcp (8 tools)

**Purpose**: Code analysis, querying, and indexing using CodeRef system

| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `mcp__coderef__query` | Query CodeRef elements by reference | Keep |
| `mcp__coderef__analyze` | Deep analysis (impact, coverage, complexity) | Keep |
| `mcp__coderef__validate` | Validate CodeRef reference format | Keep |
| `mcp__coderef__batch_validate` | Batch validate multiple references | Keep |
| `mcp__coderef__generate_docs` | Generate documentation for CodeRef elements | Keep |
| `mcp__coderef__audit` | Audit CodeRef elements | Keep |
| `mcp__coderef__nl_query` | Natural language query interface | Keep |
| `mcp__coderef__scan_realtime` | Scan source code and update index | Keep |

**No changes recommended** - coderef-mcp is the dedicated code analysis server

---

## Server: personas-mcp (8 tools)

**Purpose**: Expert persona management, plan execution integration

### Persona Management (5) - Keep
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `use_persona` | Activate expert persona | Keep |
| `get_active_persona` | Get current active persona | Keep |
| `clear_persona` | Deactivate current persona | Keep |
| `list_personas` | List all available personas | Keep |
| `create_custom_persona` | Create custom persona | Keep |

### Plan Execution (3) - **Redundant**
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `generate_todo_list` | Generate todos from plan | **Remove** (use docs-mcp execute_plan) |
| `track_plan_execution` | Sync plan with todo status | **Remove** (use docs-mcp update_task_status) |
| `execute_plan_interactive` | Execute plan step-by-step | **Remove** (unique but belongs in docs-mcp) |

**Recommendation**: Move `execute_plan_interactive` to docs-mcp if needed, remove the other two.

---

## Server: scriptboard-mcp (8 tools)

**Purpose**: Clipboard integration for Scriptboard app, CodeRef integration

### Clipboard Tools (4) - Keep
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `mcp__scriptboard__set_prompt` | Set prompt text in Scriptboard | Keep |
| `mcp__scriptboard__clear_prompt` | Clear current prompt | Keep |
| `mcp__scriptboard__add_attachment` | Add text attachment | Keep |
| `mcp__scriptboard__clear_attachments` | Clear all attachments | Keep |

### CodeRef Tools (4) - **Redundant**
| Tool | Description | Keep/Remove |
|------|-------------|-------------|
| `mcp__scriptboard__coderef_status` | Check CodeRef CLI availability | **Remove** (internal to coderef-mcp) |
| `mcp__scriptboard__coderef_scan` | Scan directory for code elements | **Remove** (use coderef-mcp scan_realtime) |
| `mcp__scriptboard__coderef_query` | Query dependencies and usages | **Remove** (use coderef-mcp query) |
| `mcp__scriptboard__coderef_impact` | Analyze impact of changes | **Remove** (use coderef-mcp analyze) |

**Recommendation**: Remove all CodeRef tools from scriptboard-mcp. Use coderef-mcp for code analysis.

---

## Consolidation Plan

### Phase 1: scriptboard-mcp Cleanup (Priority: High)

**Actions**:
1. Remove `coderef_status`, `coderef_scan`, `coderef_query`, `coderef_impact` from scriptboard-mcp/server.py
2. Update any documentation referencing these tools
3. Test Scriptboard clipboard functionality still works

**Impact**: -4 tools, reduces context tokens significantly

### Phase 2: personas-mcp Cleanup (Priority: Medium)

**Actions**:
1. Remove `generate_todo_list`, `track_plan_execution` from personas-mcp/server.py
2. Evaluate `execute_plan_interactive` - either move to docs-mcp or remove
3. Update Lloyd persona if it references removed tools

**Impact**: -3 tools

### Phase 3: docs-mcp Deprecation (Priority: Low)

**Actions**:
1. Mark `generate_foundation_docs` as deprecated in favor of `coderef_foundation_docs`
2. Add deprecation warning to tool description
3. Remove in future version after migration period

**Impact**: -1 tool (eventually)

---

## Token Impact Analysis

### Current Token Usage (Estimated)

| Server | Tools | Avg Tokens/Tool | Total Tokens |
|--------|-------|-----------------|--------------|
| docs-mcp | 35 | 300 | ~10,500 |
| coderef-mcp | 8 | 250 | ~2,000 |
| personas-mcp | 8 | 200 | ~1,600 |
| scriptboard-mcp | 8 | 200 | ~1,600 |
| **Total** | **59** | - | **~15,700** |

### After Consolidation

| Server | Tools | Avg Tokens/Tool | Total Tokens |
|--------|-------|-----------------|--------------|
| docs-mcp | 34 | 300 | ~10,200 |
| coderef-mcp | 8 | 250 | ~2,000 |
| personas-mcp | 5 | 200 | ~1,000 |
| scriptboard-mcp | 4 | 200 | ~800 |
| **Total** | **51** | - | **~14,000** |

**Savings**: ~1,700 tokens per conversation (-11%)

---

## Tool Usage Recommendations

### For Documentation
Use **docs-mcp** tools:
- `/create-workorder` - Full planning workflow
- `/execute-plan` - Generate task list
- `/update-docs` - Update changelog/README
- `/archive-feature` - Complete workflow

### For Code Analysis
Use **coderef-mcp** tools:
- `mcp__coderef__query` - Find code elements
- `mcp__coderef__analyze` - Impact analysis
- `mcp__coderef__scan_realtime` - Index codebase

### For Personas
Use **personas-mcp** tools:
- `use_persona` - Activate expert persona
- `list_personas` - See available personas

### For Scriptboard (External App)
Use **scriptboard-mcp** tools:
- `set_prompt` - Prepare prompts for export
- `add_attachment` - Attach code files

---

## Appendix: Full Tool List by Server

### docs-mcp (35 tools)
1. list_templates
2. get_template
3. generate_foundation_docs *(deprecated)*
4. generate_individual_doc
5. get_changelog
6. add_changelog_entry
7. update_changelog
8. generate_quickref_interactive
9. establish_standards
10. audit_codebase
11. check_consistency
12. get_planning_template
13. analyze_project_for_planning
14. gather_context
15. validate_implementation_plan
16. generate_plan_review_report
17. create_plan
18. generate_deliverables_template
19. update_deliverables
20. generate_agent_communication
21. assign_agent_task
22. verify_agent_completion
23. aggregate_agent_deliverables
24. track_agent_status
25. archive_feature
26. update_all_documentation
27. execute_plan
28. update_task_status
29. audit_plans
30. log_workorder
31. get_workorder_log
32. generate_handoff_context
33. assess_risk
34. coderef_foundation_docs
35. generate_features_inventory

### coderef-mcp (8 tools)
1. mcp__coderef__query
2. mcp__coderef__analyze
3. mcp__coderef__validate
4. mcp__coderef__batch_validate
5. mcp__coderef__generate_docs
6. mcp__coderef__audit
7. mcp__coderef__nl_query
8. mcp__coderef__scan_realtime

### personas-mcp (8 tools)
1. use_persona
2. get_active_persona
3. clear_persona
4. list_personas
5. generate_todo_list *(redundant)*
6. track_plan_execution *(redundant)*
7. execute_plan_interactive *(redundant)*
8. create_custom_persona

### scriptboard-mcp (8 tools)
1. mcp__scriptboard__set_prompt
2. mcp__scriptboard__clear_prompt
3. mcp__scriptboard__add_attachment
4. mcp__scriptboard__clear_attachments
5. mcp__scriptboard__coderef_status *(redundant)*
6. mcp__scriptboard__coderef_scan *(redundant)*
7. mcp__scriptboard__coderef_query *(redundant)*
8. mcp__scriptboard__coderef_impact *(redundant)*
