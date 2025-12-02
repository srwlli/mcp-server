# docs-expert v2.0 - Upgrade Plan

**Project:** docs-expert persona enhancement
**Version:** 1.0.0 → 2.0.0
**Workorder:** WO-DOCS-EXPERT-V2-001
**Status:** 📋 Planning
**Created:** 2025-10-18

---

## Executive Summary

Upgrade docs-expert persona from v1.0.0 to v2.0.0 with focus on **Lloyd integration**, planning flexibility, historical intelligence, and persona coordination.

**Key Goals:**
1. ✅ Seamless Lloyd + docs-expert workflow integration
2. ✅ Faster planning for simple tasks (quick_plan)
3. ✅ Living plans that track execution progress
4. ✅ Historical learning from past plans
5. ✅ Persona-aware multi-agent coordination

**Approach:** 4-phase implementation with incremental rollout

---

## Current State (v1.0.0)

### Strengths
- ✅ Comprehensive 6,000-line system prompt
- ✅ 30 tools across 6 categories (Documentation, Changelog, Standards, Planning, Inventory, Multi-Agent)
- ✅ Excellent planning workflow (gather → analyze → create → validate)
- ✅ POWER framework mastery (6 document types)
- ✅ Workorder tracking system (WO-{FEATURE}-001)
- ✅ Consistency Trilogy (establish → audit → check)

### Gaps Identified
1. ❌ No TodoWrite integration - plans don't convert to todos
2. ❌ No progress tracking - can't see "which tasks are done?"
3. ❌ Static plans - disconnected from execution reality
4. ❌ Heavy workflow - overkill for simple tasks
5. ❌ Manual refinement - validation feedback requires manual application
6. ❌ No historical context - can't learn from past plans
7. ❌ No persona coordination - unaware of other personas (Lloyd, coderef-expert, etc.)

### Usage Context
- **Primary User:** Lloyd (AI Project Coordinator)
- **Relationship:** Lloyd's #2 persona (most important complement)
- **Use Cases:** Planning complex features, breaking down work, maintaining docs, coordinating agents

---

## Proposed Enhancements (v2.0.0)

### New Tools (8)

#### Phase 1: Lloyd Integration
1. **generate_todo_list** - Convert plan task breakdown → TodoWrite format
2. **track_plan_execution** - Sync plan progress with todo status
3. **execute_plan_interactive** - Guided implementation with progress tracking

#### Phase 2: Planning Flexibility
4. **quick_plan** - Lightweight planning (3 sections, no validation, 2-5 min)
5. **update_plan** - Incremental plan updates without full regeneration
6. **refine_plan_automated** - Auto-apply validation feedback

#### Phase 3: Historical Intelligence
7. **plan_history** - Review past workorders, outcomes, lessons learned
8. **suggest_plan_improvements** - AI learns from project history

#### Phase 4: Persona Coordination
- Persona-aware coordination (assign tasks to Lloyd, coderef-expert, etc.)
- Track which persona completed which task
- Cross-persona workorder tracking

### Enhanced Workflows

#### Workflow 1: Lloyd + docs-expert Planning
```
User: "Add persona stacking feature"
↓
Lloyd: "Let's plan this properly. Activating docs-expert..."
↓
docs-expert: /gather-context (interactive questions, WO assignment)
docs-expert: /analyze-for-planning (discover context)
docs-expert: /create-plan (10-section plan)
docs-expert: /generate-todo-list (convert to todos)
↓
Lloyd: Receives todo list, tracks execution, marks progress
↓
docs-expert: /track-plan-execution (syncs todos → plan status)
↓
Result: Living plan tracked in real-time by Lloyd
```

#### Workflow 2: Quick Planning for Simple Tasks
```
User: "Add a new field to persona JSON schema"
↓
docs-expert: /quick-plan
  - 3 sections: Context, Tasks, Validation
  - No gather/analyze steps (too heavy)
  - 2-minute planning vs 10-minute full workflow
↓
Lloyd: Executes 3 simple tasks
↓
Result: Fast planning for 80% of tasks
```

#### Workflow 3: Adaptive Plans
```
User: "Requirements changed - add OAuth instead of JWT"
↓
docs-expert: /update-plan
  - Modifies affected sections only
  - Preserves workorder continuity
  - No full regeneration
↓
Lloyd: Sees updated tasks, continues execution
↓
Result: Plans adapt to changing requirements
```

#### Workflow 4: Learning from History
```
docs-expert: /create-plan for "Add authentication"
↓
docs-expert: Checks /plan-history
  - Found: WO-AUTH-001 from 3 months ago
  - Lesson: "Forgot to update API docs"
  - Lesson: "Missing rate limiting consideration"
↓
docs-expert: Includes lessons in new plan
↓
Result: Continuous improvement, reduced repeated mistakes
```

---

## Implementation Phases

### Phase 1: Lloyd Integration (Priority 1) ⭐⭐⭐
**Timeline:** Week 1-2
**Effort:** 16-24 hours
**Tools:** 3 new tools (generate_todo_list, track_plan_execution, execute_plan_interactive)
**Impact:** HIGH - Seamless Lloyd coordination

### Phase 2: Planning Flexibility (Priority 2) ⭐⭐
**Timeline:** Week 3-4
**Effort:** 12-16 hours
**Tools:** 3 new tools (quick_plan, update_plan, refine_plan_automated)
**Impact:** MEDIUM - Faster workflows

### Phase 3: Historical Intelligence (Priority 3) ⭐
**Timeline:** Week 5-6
**Effort:** 16-20 hours
**Tools:** 2 new tools (plan_history, suggest_plan_improvements)
**Impact:** MEDIUM - Learning over time

### Phase 4: Persona Coordination (Future) 🔮
**Timeline:** TBD (after persona stacking implemented)
**Effort:** 20-24 hours
**Dependencies:** Persona stacking system must exist first
**Impact:** HIGH - Full persona ecosystem

---

## Success Criteria

### Phase 1 Success
- ✅ Lloyd can activate docs-expert and receive todo lists automatically
- ✅ Plan progress syncs with todo status in real-time
- ✅ Workorder tracking maintained throughout execution
- ✅ Zero manual conversion from plan → todos

### Phase 2 Success
- ✅ Simple tasks complete planning in <5 minutes
- ✅ Plans can be updated incrementally without regeneration
- ✅ Validation feedback auto-applied (no manual refinement)
- ✅ 80% of tasks use quick_plan, 20% use full workflow

### Phase 3 Success
- ✅ Historical context available for all past workorders
- ✅ Plans reference similar past plans automatically
- ✅ Measurable reduction in repeated mistakes
- ✅ Lessons learned database grows over time

### Phase 4 Success
- ✅ Tasks assigned to specific personas (Lloyd, coderef-expert, etc.)
- ✅ Cross-persona progress tracking
- ✅ Workorder ownership by persona
- ✅ Coordinated multi-persona workflows

---

## Files in This Directory

- **README.md** - This file (overview and plan)
- **current-state.md** - Detailed v1.0.0 analysis
- **phase1-lloyd-integration.md** - Phase 1 design and implementation
- **phase2-planning-flexibility.md** - Phase 2 design and implementation
- **phase3-historical-intelligence.md** - Phase 3 design and implementation
- **phase4-persona-coordination.md** - Phase 4 design and implementation
- **implementation-plan.md** - Complete technical implementation plan
- **system-prompt-v2.md** - Updated system prompt for v2.0.0

---

## Next Steps

1. ✅ Review and approve this upgrade plan
2. ⏳ Implement Phase 1 (Lloyd Integration)
3. ⏳ Test Phase 1 with real Lloyd workflows
4. ⏳ Iterate and refine based on usage
5. ⏳ Implement Phase 2 (Planning Flexibility)
6. ⏳ Continue through Phase 3, 4

---

**Workorder:** WO-DOCS-EXPERT-V2-001
**Owner:** Lloyd + docs-expert (meta!)
**Status:** 📋 Planning Complete, Ready for Implementation
