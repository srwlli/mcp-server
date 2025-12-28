# Quick Reference: coderef-workflow

**MCP Server for AI-Powered Feature Lifecycle Management**

---

## Installation

```bash
cd C:\Users\willh\.mcp-servers\coderef-workflow
pip install -e .
python server.py
```

**Config:** Add to `~/.mcp.json`:
```json
{"mcpServers": {"coderef-workflow": {"command": "python", "args": ["C:/path/to/server.py"]}}}
```

---

## Quick Workflow

```
/create-workorder → /align-plan → Implement → /update-deliverables → /archive-feature
```

**Time:** 5-10 min (plan) + variable (code) + 3 min (docs) + 1 min (archive)

---

## Essential Commands

### Planning (5-10 min)
```bash
/create-workorder              # Full 11-step workflow
/gather-context                # Requirements only
/analyze-for-planning          # Scan codebase
/create-plan                   # Generate plan.json
/validate-plan {feature}       # Score 0-100
```

### Execution (variable)
```bash
/align-plan {feature}          # Generate TodoWrite checklist
/update-task-status            # Mark tasks complete
/track-agent-status            # View agent progress
```

### Documentation (2-5 min)
```bash
/update-deliverables {feature} # Git metrics (LOC, commits)
/update-docs {feature} 1.1.0   # README/CHANGELOG/CLAUDE.md
```

### Archive (1 min)
```bash
/archive-feature {feature}     # Move to coderef/archived/
/features-inventory            # List all features
```

---

## MCP Tools (23 total)

### Planning & Analysis
```python
gather_context(project_path, feature_name, description, goal, requirements)
analyze_project_for_planning(project_path, feature_name?)
get_planning_template(section?)
create_plan(project_path, feature_name, workorder_id?, multi_agent?)
validate_implementation_plan(project_path, plan_file_path)
generate_plan_review_report(project_path, plan_file_path)
```

### Execution & Tracking
```python
execute_plan(project_path, feature_name)
update_task_status(project_path, feature_name, task_id, status, notes?)
track_agent_status(project_path, feature_name?)
generate_handoff_context(project_path, feature_name, mode?)
assign_agent_task(project_path, feature_name, agent_number, phase_id?)
verify_agent_completion(project_path, feature_name, agent_number)
```

### Deliverables & Documentation
```python
generate_deliverables_template(project_path, feature_name)
update_deliverables(project_path, feature_name)
update_all_documentation(project_path, change_type, feature_description, workorder_id, files_changed?, version?)
aggregate_agent_deliverables(project_path, feature_name)
```

### Risk & Integration
```python
assess_risk(project_path, proposed_change, threshold?, options?)
generate_agent_communication(project_path, feature_name)
```

### Archival & Inventory
```python
archive_feature(project_path, feature_name, force?)
generate_features_inventory(project_path, include_archived?, format?, save_to_file?)
audit_plans(project_path, stale_days?, include_archived?)
```

### Workorder Tracking
```python
log_workorder(project_path, workorder_id, project_name, description, timestamp?)
get_workorder_log(project_path, project_name?, workorder_pattern?, limit?)
```

---

## File Structure

```
coderef/
├── workorder/{feature}/
│   ├── context.json              # Requirements & constraints
│   ├── analysis.json             # Project analysis
│   ├── plan.json                 # 10-section implementation plan
│   ├── DELIVERABLES.md           # Metrics & progress
│   └── communication.json        # Multi-agent coordination
│
├── archived/{feature}/           # Completed features
│   └── (same structure)
│
├── foundation-docs/              # Generated documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── COMPONENTS.md
│   └── SCHEMA.md
│
└── workorder-log.txt             # Global audit trail
```

---

## Plan Structure (plan.json)

```json
{
  "META_DOCUMENTATION": {
    "version": "1.0.0",
    "workorder_id": "WO-{FEATURE}-###",
    "feature_name": "string",
    "status": "planning|in_progress|completed",
    "phase_count": 3,
    "task_count": 47
  },
  "0_PREPARATION": { /* discovery & analysis */ },
  "1_EXECUTIVE_SUMMARY": { /* what & why */ },
  "2_RISK_ASSESSMENT": { /* breaking changes, security */ },
  "3_CURRENT_STATE_ANALYSIS": { /* existing architecture */ },
  "4_KEY_FEATURES": { /* must-have requirements */ },
  "5_TASK_ID_SYSTEM": { /* naming conventions */ },
  "6_IMPLEMENTATION_PHASES": { /* phased breakdown */ },
  "7_TESTING_STRATEGY": { /* unit, integration, e2e */ },
  "8_SUCCESS_CRITERIA": { /* how to verify */ }
}
```

---

## Common Patterns

### Create & Execute Feature Plan
```bash
# Step 1: Plan (5-10 min)
/create-workorder
# → Answer prompts
# → Plan validated (score: 95/100)
# → TodoWrite checklist generated
# → Git commit created

# Step 2: Implement (variable)
# Follow TodoWrite tasks in CLI terminal

# Step 3: Document (3 min)
/update-deliverables my-feature
/update-docs my-feature 1.1.0

# Step 4: Archive (1 min)
/archive-feature my-feature
```

### Multi-Agent Coordination
```bash
# Enable multi-agent mode
/create-workorder
# → Multi-agent: Yes (3 agents)

# Assign agents
/assign-agent-task my-feature 1  # Agent 1 → Phase 1
/assign-agent-task my-feature 2  # Agent 2 → Phase 2
/assign-agent-task my-feature 3  # Agent 3 → Phase 3

# Track progress
/track-agent-status my-feature

# Verify & aggregate
/verify-agent-completion my-feature 1
/aggregate-agent-deliverables my-feature
```

### Risk Assessment
```bash
# Before refactoring
assess_risk({
  "project_path": "/path/to/project",
  "proposed_change": {
    "description": "Rename AuthService",
    "change_type": "refactor",
    "files_affected": ["src/auth.py"]
  }
})

# Returns score 0-100:
# 0-30: GO ✅
# 31-60: CAUTION ⚠️
# 61-100: STOP 🛑
```

---

## Workorder Format

```
WO-{FEATURE}-{CATEGORY}-{SEQUENCE}

Examples:
- WO-AUTH-SYSTEM-001
- WO-DARK-MODE-UI-002
- WO-API-REFACTOR-003
```

**Tracked in:** `coderef/workorder-log.txt`

---

## Task Status Lifecycle

```
pending → in_progress → completed
         ↘ blocked (optional)
```

**Update:**
```bash
/update-task-status my-feature IMPL-001 completed
```

---

## Plan Validation

**Score Meaning:**
- **90-100:** Excellent, ready for implementation
- **70-89:** Good, minor issues to fix
- **50-69:** Needs refinement
- **< 50:** Not ready, critical issues

**Command:**
```bash
/validate-plan my-feature
```

**Auto-fix:** Iterates up to 3 times to reach 90+ score.

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| MCP server won't start | `pip install -e .` |
| `/create-workorder` not found | Check `~/.mcp.json`, restart Claude Code |
| Plan validation fails | `/generate-plan-review {feature}` for details |
| coderef-context unavailable | Normal (graceful fallback to filesystem) |
| Can't archive feature | Status must be "Complete" or use `--force` |

---

## Integration with Ecosystem

```
coderef-workflow → coderef-context  (code intelligence)
coderef-workflow → coderef-docs     (documentation)
coderef-workflow ← coderef-personas (expert agents)
```

**Best Practice:** Install all 4 servers for full functionality.

---

## Key Concepts

### Code Intelligence Integration
- **AST Analysis** - coderef-context scans code during planning
- **Dependency Graphs** - Shows what-calls, what-imports
- **Pattern Detection** - Identifies coding standards
- **Impact Analysis** - Ripple effects of changes

### Workorder-Centric Architecture
- **Unique IDs** - Every feature gets WO-{FEATURE}-### ID
- **Audit Trail** - workorder-log.txt tracks all features
- **Complete History** - From idea → plan → code → archive

### 10-Section Plan
- **META** - Workorder ID, status, version
- **PREP** - Discovery and analysis
- **SUMMARY** - What & why (3-5 bullets)
- **RISK** - Breaking changes, security
- **CURRENT** - Existing architecture
- **FEATURES** - Requirements list
- **TASKS** - Task ID naming (SETUP-001, IMPL-001)
- **PHASES** - Phased breakdown with dependencies
- **TESTING** - Unit, integration, e2e strategy
- **SUCCESS** - Verification criteria

---

## Time Estimates

| Operation | Time |
|-----------|------|
| Create workorder | 5-10 min |
| Validate plan | < 1 min |
| Align plan (TodoWrite) | < 1 min |
| Update deliverables | < 1 min |
| Update docs | < 1 min |
| Archive feature | < 1 min |
| Audit all plans | < 1 min |
| Risk assessment | < 5 sec |
| Multi-agent setup | 2-3 min |

**Total Overhead:** ~10-15 minutes per feature (planning + documentation)

---

## Best Practices

✅ **Do:**
- Run `/create-workorder` before coding
- Use descriptive feature names (`user-authentication` not `feature1`)
- Validate plans (aim for 90+ score)
- Update deliverables after completion
- Archive completed features
- Use workorder IDs in commit messages

🚫 **Don't:**
- Skip plan validation (causes implementation issues)
- Edit plan.json manually during execution
- Forget to commit after `/align-plan`
- Mix coderef-docs and coderef-workflow operations
- Archive incomplete features (without `--force`)

💡 **Tips:**
- Enable coderef-context for better plans
- Use risk assessment before refactoring
- Read ARCHITECTURE.md before planning
- Track progress with TodoWrite
- Tab completion works for feature names

---

## Resources

- **[README.md](../README.md)** - User-facing overview
- **[API.md](../foundation-docs/API.md)** - Complete MCP tool reference
- **[ARCHITECTURE.md](../foundation-docs/ARCHITECTURE.md)** - System design
- **[USER-GUIDE.md](USER-GUIDE.md)** - Comprehensive tutorial
- **[FEATURES.md](FEATURES.md)** - Feature overview
- **[my-guide.md](my-guide.md)** - Concise tool reference

---

**Version:** 1.1.0
**Last Updated:** December 28, 2025
**Maintained by:** willh, Claude Code AI
