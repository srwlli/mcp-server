# Workflow Integration Analysis

## Current Workflow
```
gather-context → create-plan → execute-plan → update-deliverables → archive-feature
```

## Proposed Workflow (with all 12 stubs)
```
gather-context → create-plan → [commit planning artifacts] → execute-plan → update-deliverables → git-workflow → archive-feature
                                                               ↑
                                                    (progress tracking + testing)
```

---

## Stub Integration Map

### **Phase 1: Enforcement & Standards** (Foundation - do first)

| Stub | Integration Point | Implementation |
|------|-------------------|----------------|
| **STUB-032** enforce-plan-json | ALL tools | Validation layer - reject non-standard formats |
| **STUB-039** enforce-plan-json-lloyd | Lloyd persona | Add "strict mode" flag to persona, refuse to work without plan.json |
| **STUB-036** timestamp-enforcement | ALL tool outputs | Add `timestamp` field to every response, use ISO 8601 |

**My take**: These are cross-cutting concerns. We should:
1. Add a `validate_plan_format()` function in docs-mcp
2. Update Lloyd's persona to check for plan.json before executing
3. Add timestamp wrapper to all tool handlers

---

### **Phase 2: Progress Tracking** (Core improvement)

| Stub | Integration Point | Implementation |
|------|-------------------|----------------|
| **STUB-009** plan-progress-tracking | execute-plan, task completion | Add `update_task_status` tool or auto-update on task completion |
| **STUB-028** plan-audit-workflow | New tool: `/audit-plans` | Scan all coderef/working/*/plan.json, report stale/active/blocked |

**My take**: This is the biggest gap. Options:
- **Option A**: New `update_task_status` tool agents call after each task
- **Option B**: Hook into TodoWrite - when todo marked complete, update plan.json
- **Option C**: Instruction-based - tell agents to update plan.json manually

I'd recommend **Option B** - linking TodoWrite to plan.json would be seamless.

---

### **Phase 3: Workflow Enhancements**

| Stub | Integration Point | Implementation |
|------|-------------------|----------------|
| **STUB-040** start-feature-workflow-update | /start-feature | Add git commit after planning artifacts created |
| **STUB-038** git-workflow-mcp | After update-deliverables | New tool or slash command: `/git-release` |
| **STUB-010** incremental-testing | Task schema | Add optional `verify_step` field to each task |

**My take**:
- STUB-040 is easy - just add `git add . && git commit -m "WO-xxx: Planning artifacts"` to /start-feature
- STUB-038 needs a new `/git-release` command (version bump, commit, push, optional tag)
- STUB-010 is optional enhancement - add schema field but don't require it

---

### **Phase 4: Multi-Agent & Handoff**

| Stub | Integration Point | Implementation |
|------|-------------------|----------------|
| **STUB-008** workorder-handoff-protocol | communication.json, agent assignment | Standardize prompt format, enhance existing tools |

**My take**: We already have `generate_agent_communication`, `assign_agent_task`, etc. This stub is about:
1. Documenting the standard handoff prompt format
2. Adding a prompt template to communication.json
3. Possibly a `/handoff` command that generates the prompt

---

### **Phase 5: Tooling & Documentation**

| Stub | Integration Point | Implementation |
|------|-------------------|----------------|
| **STUB-002** tool-inventory-workflow | New tool or workflow | Generate `coderef/user/features.md` per project |
| **STUB-041** rename-workflows | Slash commands | Rename for clarity (e.g., /start-feature → /plan-feature?) |
| **STUB-042** automated-workflows | Future | Collect automation ideas, implement incrementally |

**My take**:
- STUB-002 is a new tool: `generate_features_inventory` → outputs features.md
- STUB-041 needs discussion - what names make more sense?
- STUB-042 is a parking lot for future ideas

---

## Recommended Implementation Order

```
1. STUB-036 (timestamps)        ← Easy win, immediate visibility
2. STUB-032 + STUB-039 (enforce)← Foundation for everything else
3. STUB-009 (progress tracking) ← Core value, biggest impact
4. STUB-040 (start-feature git) ← Quick improvement
5. STUB-028 (plan audit)        ← Enables orchestrator visibility
6. STUB-038 (git-workflow)      ← Completes the lifecycle
7. STUB-008 (handoff protocol)  ← Multi-agent improvement
8. STUB-002 (features.md)       ← Documentation win
9. STUB-010 (testing)           ← Nice-to-have
10. STUB-041 (rename)           ← Polish
11. STUB-042 (automation)       ← Future backlog
```

---

## Open Questions

1. **Progress tracking**: Do you prefer Option A (new tool), B (TodoWrite hook), or C (manual instruction)?

2. **Git workflow**: Should `/git-release` be a new MCP tool or just a slash command that runs bash?

3. **Naming**: Any thoughts on better names for workflows? (STUB-041)

4. **Scope**: Should we implement all 12 in one plan, or split into 2-3 smaller plans?
