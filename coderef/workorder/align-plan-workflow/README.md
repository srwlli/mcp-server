# Workorder: align-plan-workflow

**WO-ALIGN-PLAN-WORKFLOW-001**

## Quick Summary

Insert `/align-plan` command between plan validation and git commit in the `/create-workorder` workflow.

### The Change

**Current workflow:**
```
Step 8: Validation Loop
    ↓
Step 9: Output Summary
    ↓
Step 10: Commit & Push
```

**New workflow:**
```
Step 8: Validation Loop
    ↓
Step 9: Align Plan (/align-plan) ← NEW
    ↓
Step 10: Output Summary
    ↓
Step 11: Commit & Push ← RENUMBERED
```

### Why?

Ensure plan.json is synchronized with a TodoWrite task list **before** committing planning artifacts. This improves:
- Task tracking clarity
- Execution readiness
- Agent handoff quality

## Files in This Workorder

- **plan.json** - Complete 10-section implementation plan with all details
- **context.json** - Feature requirements and constraints
- **analysis.json** - Project structure and existing patterns
- **DELIVERABLES.md** - Progress tracking and metrics template
- **README.md** - This file

## Implementation Plan

### Phase 1: Document Analysis
Review create-workorder.md and identify all change points.
- Effort: 30 min
- Status: Pending

### Phase 2: Workflow Update
Update the command definition with new step order.
- Tasks: Update diagram, add Step 9, renumber Steps 10-11
- Effort: 45 min
- Status: Pending

### Phase 3: Documentation
Update descriptions and cross-references.
- Tasks: Update command description, related commands section
- Effort: 20 min
- Status: Pending

### Phase 4: Testing
Verify all changes are correct and consistent.
- Tasks: Read-through, validation, syntax check, end-to-end test
- Effort: 30 min
- Status: Pending

## Key Facts

| Aspect | Detail |
|--------|--------|
| **File Modified** | ~/.claude/commands/create-workorder.md |
| **New Steps** | 1 (Step 9: /align-plan) |
| **Renumbered** | 2 (Steps 9→10, 10→11) |
| **Breaking Changes** | None |
| **Tool Changes** | None (uses existing /align-plan) |
| **Complexity** | Low |
| **Estimated Time** | 2-3 hours |

## Next Steps

1. Read `plan.json` for complete details
2. Execute Phase 1 (document analysis)
3. Execute Phase 2 (workflow update)
4. Execute Phase 3 (documentation)
5. Execute Phase 4 (testing)
6. Commit changes
7. Update DELIVERABLES.md with actual metrics

## Tools & References

- **Tool used:** `mcp__coderef_workflow__execute_plan` (calls /align-plan command)
- **Related commands:** `/create-workorder`, `/align-plan`, `/update-task-status`
- **Files:** ~/.claude/commands/create-workorder.md
- **Workorder:** WO-ALIGN-PLAN-WORKFLOW-001
- **Created:** 2025-12-27
- **Status:** Planning (ready for implementation)

---

**Plan Quality:** This is a complete, detailed implementation plan with clear tasks, phases, and success criteria. Ready to execute whenever you're ready!
