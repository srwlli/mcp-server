# Phase 2: Planning Flexibility

**Workorder:** WO-DOCS-EXPERT-V2-001
**Phase:** 2 of 4
**Priority:** ⭐⭐ MEDIUM
**Status:** 📋 Design
**Timeline:** Week 3-4 (12-16 hours)
**Dependencies:** Phase 1 (Lloyd Integration)

---

## Overview

Add lightweight planning options and adaptive capabilities to reduce overhead for simple tasks and support changing requirements. This phase makes docs-expert more flexible and efficient for the 80% of tasks that don't need full planning rigor.

---

## Problems Solved

### Problem 1: Heavy Workflow Overhead ⚠️
**Current State:**
```
Simple task: "Add a field to persona JSON"
docs-expert: /gather-context (5 min) → /analyze-for-planning (3 min) → /create-plan (2 min) → /validate-plan (1 min)
Total time: 11 minutes for a 2-minute task
Result: Overkill, frustrating for users
```

**Desired State:**
```
Simple task: "Add a field to persona JSON"
docs-expert: /quick-plan (1 min) → 3 todos generated
Total time: 1 minute for a 2-minute task
Result: Appropriate planning for task complexity
```

### Problem 2: Static Plans ❌
**Current State:**
```
Plan created: "Add JWT authentication"
Mid-implementation: "Actually, use OAuth instead"
docs-expert: Must regenerate entire plan (gather → analyze → create → validate)
Total time: 10+ minutes
Result: Frustrating, slow adaptation
```

**Desired State:**
```
Plan created: "Add JWT authentication"
Mid-implementation: "Actually, use OAuth instead"
docs-expert: /update-plan (modify auth sections only)
Total time: 2 minutes
Result: Fast adaptation to changing requirements
```

### Problem 3: Manual Refinement ❌
**Current State:**
```
docs-expert: /validate-plan → Score: 72/100
Feedback: "Missing error handling in task 3, unclear acceptance criteria in task 5"
User: Manually edits plan.json
docs-expert: /validate-plan → Score: 85/100
Feedback: "Add rollback procedure to deployment section"
User: Manually edits plan.json again
docs-expert: /validate-plan → Score: 92/100 ✅
Total rounds: 3, Total time: 15+ minutes
Result: Manual iteration is slow and tedious
```

**Desired State:**
```
docs-expert: /validate-plan → Score: 72/100
docs-expert: /refine-plan-automated (auto-applies feedback)
docs-expert: /validate-plan → Score: 92/100 ✅
Total rounds: 1, Total time: 5 minutes
Result: Automated refinement, faster to 90+ score
```

---

## New Tools (3)

### Tool 1: quick_plan

**Purpose:** Lightweight planning for simple tasks (skip full workflow)

**Input:**
- `feature_name` (string, required): Short feature name (e.g., "add-persona-field")
- `description` (string, required): Brief description (1-3 sentences)
- `complexity` (enum, optional): "trivial" | "simple" | "moderate" (default: "simple")

**Output:**
```json
{
  "workorder_id": "WO-ADD-PERSONA-FIELD-001",
  "feature_name": "add-persona-field",
  "description": "Add 'tags' field to persona JSON schema for categorization",
  "complexity": "trivial",
  "plan": {
    "context": {
      "what": "Add tags array field to PersonaDefinition schema",
      "why": "Enable persona categorization and filtering",
      "estimated_time": "15 minutes"
    },
    "tasks": [
      {
        "task_id": 1,
        "description": "Update PersonaDefinition schema in models.py",
        "files": ["src/models.py"],
        "acceptance_criteria": ["tags field is optional array of strings"]
      },
      {
        "task_id": 2,
        "description": "Add tags field to existing personas",
        "files": ["personas/base/*.json"],
        "acceptance_criteria": ["All 4 personas have relevant tags"]
      },
      {
        "task_id": 3,
        "description": "Update documentation",
        "files": ["PERSONAS-CREATED.md", "my-guide.md"],
        "acceptance_criteria": ["Tags field documented with examples"]
      }
    ],
    "validation": {
      "tests": ["Schema validation passes", "All personas load successfully"],
      "estimated_time": "5 minutes"
    }
  },
  "skipped_steps": ["gather_context", "analyze_project", "full_validation"],
  "output_path": "coderef/working/add-persona-field/quick-plan.json",
  "summary": "Quick plan generated: 3 tasks, ~20 minutes total"
}
```

**Behavior:**
1. Generate workorder ID (WO-{FEATURE}-001)
2. Create lightweight plan (3 sections: context, tasks, validation)
3. Skip full workflow steps (no interactive gathering, no project analysis, no 10-section plan)
4. Generate 3-5 tasks (not 10+)
5. Skip validation scoring (assume good enough)
6. Save to quick-plan.json (not plan.json)
7. Auto-generate todos (call generate_todo_list from Phase 1)
8. Return ready-to-execute plan

**Complexity Levels:**
- **trivial:** 1-2 tasks, <15 min (e.g., add field, fix typo)
- **simple:** 3-5 tasks, 15-30 min (e.g., add feature flag, update docs)
- **moderate:** 6-8 tasks, 30-60 min (e.g., add new endpoint, refactor component)

**When to Use:**
- Add/remove field to schema
- Update documentation
- Fix bug with known solution
- Add configuration option
- Refactor single file/function

**When NOT to Use:**
- New complex features (use full planning)
- Cross-cutting changes (use full planning)
- Breaking changes (use full planning)
- Multi-file refactors (use full planning)

**Example Usage:**
```
User: "Add a tags field to persona schema"
Lloyd: "This is a simple task, let me quick-plan it"
docs-expert: quick_plan(feature_name="add-persona-field", description="Add tags array for categorization", complexity="trivial")
Output: 3 tasks, ~20 min, ready to execute
Lloyd: Receives todos, executes immediately
```

**Edge Cases:**
- Complexity underestimated (trivial → actually complex) → Suggest: "Use full planning for this"
- Feature name too vague → Error: "Provide more specific feature name"
- Description too long → Warning: "Quick plans work best with brief descriptions"

**File Changes:**
- New generator: `src/generators/quick_plan_generator.py`
- New tool handler: `server.py` (add quick_plan tool)

---

### Tool 2: update_plan

**Purpose:** Incremental plan updates without full regeneration

**Input:**
- `plan_path` (string, required): Path to plan.json or quick-plan.json
- `workorder_id` (string, required): Workorder ID
- `updates` (object, required): Sections to update
- `reason` (string, optional): Why the update is needed

**Output:**
```json
{
  "workorder_id": "WO-AUTH-001",
  "updated_sections": ["implementation_strategy", "task_breakdown"],
  "changes": [
    {
      "section": "implementation_strategy",
      "field": "approach",
      "old_value": "Use JWT for authentication",
      "new_value": "Use OAuth 2.0 for authentication",
      "reason": "Client requirement changed"
    },
    {
      "section": "task_breakdown",
      "task_id": 3,
      "field": "description",
      "old_value": "Implement JWT validation",
      "new_value": "Implement OAuth token validation",
      "reason": "Adapting to OAuth approach"
    }
  ],
  "impact": {
    "tasks_modified": 3,
    "tasks_added": 2,
    "tasks_removed": 1,
    "total_tasks": 9
  },
  "validation": {
    "score_before": 92,
    "score_after": 88,
    "recommendation": "Re-validate plan after updates"
  },
  "output_path": "coderef/working/auth/plan.json",
  "summary": "Updated 2 sections, modified 3 tasks, added 2 tasks"
}
```

**Behavior:**
1. Read existing plan.json
2. Apply updates to specified sections
3. Preserve workorder ID continuity
4. Track changes (old → new values)
5. Update affected tasks automatically
6. Recalculate dependencies
7. Save updated plan.json
8. Return change summary

**Update Types:**
- **Section replacement:** Replace entire section (e.g., new technical design)
- **Task modification:** Update specific task(s)
- **Task addition:** Add new tasks to breakdown
- **Task removal:** Remove tasks (with dependency check)
- **Metadata update:** Change estimates, priorities, assignments

**Example Usage:**
```
User: "Actually, use OAuth instead of JWT"
Lloyd: "Let me update the plan"
docs-expert: update_plan(
  plan_path="coderef/working/auth/plan.json",
  workorder_id="WO-AUTH-001",
  updates={
    "implementation_strategy.approach": "Use OAuth 2.0",
    "task_breakdown[3].description": "Implement OAuth token validation"
  },
  reason="Client requirement changed to OAuth"
)
Output: 2 sections updated, 3 tasks modified
Lloyd: "Plan updated, continuing execution with OAuth"
```

**Edge Cases:**
- Update breaks dependencies → Error: "Task 5 depends on removed task 3"
- Update invalidates completed work → Warning: "3 tasks already completed may need rework"
- Conflicting updates → Error: "Cannot update completed task without reopening"
- Plan not found → Error: "Plan file not found"

**File Changes:**
- New updater: `src/updaters/plan_updater.py`
- New tool handler: `server.py` (add update_plan tool)

---

### Tool 3: refine_plan_automated

**Purpose:** Auto-apply validation feedback to improve plan quality

**Input:**
- `plan_path` (string, required): Path to plan.json
- `workorder_id` (string, required): Workorder ID
- `validation_feedback` (object, required): Feedback from validate_implementation_plan
- `mode` (enum, optional): "conservative" | "aggressive" (default: "conservative")

**Output:**
```json
{
  "workorder_id": "WO-AUTH-001",
  "refinement_applied": true,
  "changes": [
    {
      "issue": "Missing error handling in task 3",
      "section": "task_breakdown",
      "task_id": 3,
      "fix": "Added error handling acceptance criteria",
      "details": "Added criteria: 'Returns 401 on invalid token', 'Logs authentication failures'"
    },
    {
      "issue": "Unclear acceptance criteria in task 5",
      "section": "task_breakdown",
      "task_id": 5,
      "fix": "Clarified acceptance criteria",
      "details": "Changed 'Works correctly' → 'Returns user profile with email and roles'"
    },
    {
      "issue": "Missing rollback procedure",
      "section": "deployment_plan",
      "fix": "Added rollback steps",
      "details": "Added 3-step rollback procedure with database migration revert"
    }
  ],
  "validation": {
    "score_before": 72,
    "score_after": 91,
    "improvement": 19,
    "target_met": true
  },
  "iterations": 1,
  "output_path": "coderef/working/auth/plan.json",
  "summary": "Applied 3 fixes, score improved 72 → 91 (target 90+ met)"
}
```

**Behavior:**
1. Read plan.json
2. Read validation feedback (from validate_implementation_plan)
3. Analyze feedback for actionable fixes:
   - Missing criteria → Add criteria
   - Unclear language → Clarify language
   - Missing sections → Add sections
   - Incomplete details → Add details
4. Apply fixes automatically (AI-powered)
5. Validate refined plan (call validate_implementation_plan)
6. If score < 90, iterate (max 3 rounds)
7. Save refined plan.json
8. Return refinement summary

**Modes:**
- **conservative:** Only apply high-confidence fixes (safe, may need manual refinement)
- **aggressive:** Apply all suggested fixes (faster, may over-correct)

**Example Usage:**
```
docs-expert: /validate-plan
Output: Score 72/100
Feedback: Missing error handling (task 3), unclear criteria (task 5), missing rollback

docs-expert: refine_plan_automated(
  plan_path="coderef/working/auth/plan.json",
  workorder_id="WO-AUTH-001",
  validation_feedback={...},
  mode="conservative"
)
Output: 3 fixes applied, score 72 → 91 ✅

Result: Automatic improvement, no manual editing
```

**Edge Cases:**
- Feedback ambiguous → Warn: "Cannot auto-apply ambiguous feedback, manual refinement needed"
- Fix conflicts with existing content → Conservative: Skip fix, Aggressive: Override
- Max iterations reached (3) → Return: "Best score after 3 iterations: 88/100"
- Already at target (90+) → Info: "Plan already meets quality target"

**File Changes:**
- New refiner: `src/refiners/plan_refiner.py`
- New AI integration: Use LLM to interpret feedback and generate fixes
- New tool handler: `server.py` (add refine_plan_automated tool)

---

## Enhanced Workflows

### Workflow 1: Quick Planning for Simple Tasks
```
Step 1: User: "Add tags field to persona schema"
        Lloyd: "This is a simple task"

Step 2: docs-expert: quick_plan(feature_name="add-persona-field", complexity="trivial")
        Output: 3 tasks, ~20 min

Step 3: docs-expert: generate_todo_list (auto)
        Output: 3 todos ready

Step 4: Lloyd: Executes 3 tasks (15 min actual)
        Lloyd: All complete ✅

Step 5: docs-expert: track_plan_execution
        Output: WO-ADD-PERSONA-FIELD-001 DONE ✅

Result: 1 minute planning for 15 minute task (vs 11 min full planning)
```

### Workflow 2: Adaptive Planning (Requirements Change)
```
Step 1: docs-expert: /create-plan (JWT authentication)
        Output: 8 tasks, WO-AUTH-001

Step 2: Lloyd: Completes tasks 1-2

Step 3: User: "Actually, use OAuth instead"
        Lloyd: "Let me update the plan"

Step 4: docs-expert: update_plan(updates={"approach": "OAuth"})
        Output: 3 tasks modified, 2 tasks added

Step 5: docs-expert: generate_todo_list (regenerate for new tasks)
        Output: 8 todos (2 complete, 6 remaining, 2 new)

Step 6: Lloyd: Continues with updated plan
        Lloyd: Completes remaining tasks

Step 7: docs-expert: track_plan_execution
        Output: WO-AUTH-001 DONE ✅ (with OAuth)

Result: 2 minute adaptation vs 10 minute full regeneration
```

### Workflow 3: Automated Plan Refinement
```
Step 1: docs-expert: /create-plan
        Output: plan.json

Step 2: docs-expert: /validate-plan
        Output: Score 72/100, 5 issues identified

Step 3: docs-expert: refine_plan_automated(mode="conservative")
        Output: 3 fixes applied, score 72 → 88

Step 4: docs-expert: refine_plan_automated (iteration 2)
        Output: 2 more fixes, score 88 → 92 ✅

Step 5: docs-expert: generate_todo_list
        Lloyd: Begins execution

Result: 5 minute automated refinement vs 15 minute manual editing
```

---

## Decision Rules

### When to Use Quick Plan vs Full Plan

**Use quick_plan when:**
- Task is trivial or simple (1-5 tasks, <30 min)
- Requirements are clear and stable
- No breaking changes involved
- Single file or small scope
- Documentation updates
- Bug fixes with known solution

**Use full planning when:**
- Task is complex (10+ tasks, >1 hour)
- Requirements are unclear or evolving
- Breaking changes or migrations
- Cross-cutting changes (multiple systems)
- New features with unknowns
- High-risk changes (data loss potential)

### Automatic Complexity Detection

docs-expert can suggest the appropriate planning approach:

```python
def suggest_planning_approach(description: str) -> str:
    signals_complex = [
        "migration", "breaking change", "refactor", "redesign",
        "multiple systems", "cross-cutting", "architecture",
        "database", "API change", "authentication", "security"
    ]

    signals_simple = [
        "add field", "update docs", "fix typo", "rename",
        "config change", "add test", "update comment"
    ]

    if any(signal in description.lower() for signal in signals_complex):
        return "full_planning"
    elif any(signal in description.lower() for signal in signals_simple):
        return "quick_plan"
    else:
        return "ask_user"  # Ambiguous, let user decide
```

---

## System Prompt Updates

Add to docs-expert system prompt:

### New Section: Planning Flexibility (v2.0.0)
```markdown
## Planning Flexibility (v2.0.0)

You now have flexible planning capabilities to match task complexity.

### Planning Modes

1. **Full Planning (Complex Tasks)**
   - Use for: Complex features, breaking changes, cross-cutting work
   - Workflow: /gather-context → /analyze-for-planning → /create-plan → /validate-plan
   - Time: 10-15 minutes
   - Output: 10-section plan with 90+ quality score

2. **Quick Planning (Simple Tasks)**
   - Use for: Simple changes, bug fixes, documentation updates
   - Workflow: /quick-plan → generate_todo_list
   - Time: 1-2 minutes
   - Output: 3-section lightweight plan

3. **Adaptive Planning (Changing Requirements)**
   - Use for: Mid-implementation requirement changes
   - Workflow: /update-plan (modify sections without full regeneration)
   - Time: 2-3 minutes
   - Output: Updated plan with change tracking

### New Tools

#### quick_plan
- Generate lightweight plan for simple tasks
- 3 sections: context, tasks, validation
- 3-5 tasks (not 10+)
- Skip gathering, analysis, scoring
- Auto-generate todos

#### update_plan
- Modify existing plan without regeneration
- Update specific sections or tasks
- Preserve workorder continuity
- Track changes (old → new)
- Recalculate dependencies

#### refine_plan_automated
- Auto-apply validation feedback
- Conservative or aggressive mode
- Iterate until 90+ score
- Zero manual editing

### Decision Framework

**Complexity Indicators:**

**Use Full Planning if:**
- Breaking changes or migrations
- Cross-cutting changes (multiple systems)
- High-risk (data loss, security)
- Unclear requirements
- Complex features (>10 tasks, >1 hour)

**Use Quick Planning if:**
- Simple changes (add field, update docs)
- Clear requirements
- Low risk
- Single file or small scope
- <30 minutes estimated time

**Ask User if Ambiguous**

### Best Practices

✅ **Do:**
- Match planning rigor to task complexity
- Use quick_plan for 80% of tasks (simple)
- Use full planning for 20% of tasks (complex)
- Update plans when requirements change (don't regenerate)
- Auto-refine plans to reach 90+ score

🚫 **Don't:**
- Use full planning for simple tasks (overkill)
- Use quick planning for complex tasks (insufficient)
- Regenerate entire plan for small changes
- Manually edit plans (use refine_plan_automated)

### Value Proposition

- **10x faster planning for simple tasks** (1 min vs 11 min)
- **5x faster plan adaptation** (2 min vs 10 min)
- **3x faster refinement** (5 min vs 15 min)
- **Better UX** (right tool for the job)
```

---

## Implementation Details

### File Structure
```
src/
├── generators/
│   ├── todo_list_generator.py
│   └── quick_plan_generator.py          ← NEW
├── updaters/
│   └── plan_updater.py                  ← NEW
├── refiners/
│   └── plan_refiner.py                  ← NEW
└── models.py                            ← UPDATE (add quick plan schema)

server.py                                ← UPDATE (add 3 new tools)
```

### Schema Changes

#### Quick Plan Schema
```json
{
  "workorder_id": "WO-{FEATURE}-001",
  "feature_name": "string",
  "description": "string",
  "complexity": "trivial|simple|moderate",
  "plan": {
    "context": {
      "what": "string",
      "why": "string",
      "estimated_time": "string"
    },
    "tasks": [
      {
        "task_id": 1,
        "description": "string",
        "files": ["string"],
        "acceptance_criteria": ["string"]
      }
    ],
    "validation": {
      "tests": ["string"],
      "estimated_time": "string"
    }
  },
  "skipped_steps": ["string"]
}
```

#### Plan Update Record Schema
```json
{
  "updated_at": "timestamp",
  "updated_by": "user or persona",
  "reason": "string",
  "changes": [
    {
      "section": "string",
      "field": "string",
      "old_value": "any",
      "new_value": "any"
    }
  ]
}
```

---

## Testing Strategy

### Unit Tests
1. **QuickPlanGenerator:**
   - Test plan generation for trivial/simple/moderate complexity
   - Test task breakdown (3-5 tasks)
   - Test workorder assignment

2. **PlanUpdater:**
   - Test section updates
   - Test task modifications
   - Test dependency recalculation
   - Test change tracking

3. **PlanRefiner:**
   - Test feedback interpretation
   - Test fix application
   - Test iterative refinement
   - Test conservative vs aggressive modes

### Integration Tests
1. **Quick Planning Workflow:**
   - quick_plan → generate_todo_list → track_plan_execution

2. **Adaptive Planning Workflow:**
   - create_plan → update_plan → generate_todo_list → track_plan_execution

3. **Automated Refinement Workflow:**
   - create_plan → validate_plan → refine_plan_automated → validate_plan (90+)

### Performance Tests
1. **Quick Plan Speed:** <2 seconds
2. **Update Plan Speed:** <1 second
3. **Refine Plan Speed:** <5 seconds per iteration

---

## Success Metrics

### Quantitative
- ✅ Quick plan generation: <2 seconds
- ✅ 80% of tasks use quick_plan (not full planning)
- ✅ Plan updates: <1 second
- ✅ Automated refinement reaches 90+ in 2-3 iterations
- ✅ Time savings: 10x for simple tasks, 5x for updates, 3x for refinement

### Qualitative
- ✅ Users report "planning feels fast now"
- ✅ Lloyd adapts to changing requirements easily
- ✅ Plans stay relevant throughout execution
- ✅ No manual plan editing required

---

## Next Phase

After Phase 2 completion:
- **Phase 3:** Historical Intelligence (plan_history, suggest_plan_improvements)
- **Phase 4:** Persona Coordination (cross-persona task assignment)

---

**Workorder:** WO-DOCS-EXPERT-V2-001
**Status:** 📋 Phase 2 Design Complete
