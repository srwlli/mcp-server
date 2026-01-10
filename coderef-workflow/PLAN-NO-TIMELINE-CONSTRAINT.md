# No-Timeline Constraint Implementation Plan

## Problem Statement

The current planning system includes time-based fields (`estimated_effort` in hours/minutes, `effort_percentage`, etc.) that contradict the agentic nature of the workflow system. Since all coding is performed autonomously by AI agents, time estimates are:

1. **Meaningless** - Agents don't work on human timelines
2. **Misleading** - Suggests deadlines/schedules that don't apply
3. **Anti-pattern** - Violates "planning without timelines" principle

## Solution

Replace all time-based planning with **complexity-based planning**:
- Focus on WHAT needs to be done and HOW complex it is
- Remove all references to hours, minutes, duration, timelines
- Use complexity levels: `trivial`, `low`, `medium`, `high`, `very_high`
- Track completeness and quality, not time

## Files to Update

### 1. Planning Template (Core Authority)
**File:** `coderef/context/planning-template-for-ai.json`

**Changes:**
- Line 5: ✅ Already has `"no_time_factors": "Plans are agentic..."`
- Line 207: Change `"effort_percentage": "15-25%"` → `"typical_scope": "15-25% of total tasks"`
- Line 214: Change `"effort_percentage": "40-50%"` → `"typical_scope": "40-50% of total tasks"`
- Line 221: Change `"effort_percentage": "20-25%"` → `"typical_scope": "20-25% of total tasks"`
- Line 228: Change `"effort_percentage": "15-20%"` → `"typical_scope": "15-20% of total tasks"`
- Line 235: Change `"effort_percentage": "5-10%"` → `"typical_scope": "5-10% of total tasks"`
- Line 242: Change `"effort_level": "1-5 scale (1=trivial, 5=major)"` → `"complexity_level": "trivial | low | medium | high | very_high"`

### 2. Plan Schema (Validation Contract)
**File:** `coderef/schemas/planning-generator-schema.json`

**Changes:**
- Line 225-228: Replace `"estimated_effort": {"type": "string", "enum": ["low", "medium", "high"]}` with:
```json
"complexity": {
  "type": "string",
  "enum": ["trivial", "low", "medium", "high", "very_high"],
  "description": "Complexity level (NOT time estimate)"
}
```

### 3. Plan Validator (Enforcement)
**File:** `generators/plan_validator.py`

**Changes:**
- Line 156: Remove `estimated_effort` from suggestion
- Add new validation rule: Reject plans with time-based fields
```python
def validate_no_time_estimates(self):
    """Ensure plan contains no time estimates (agentic constraint)."""
    time_keywords = ['hours', 'minutes', 'duration', 'timeline', 'schedule', 'deadline', 'estimated_time']

    plan_str = json.dumps(self.plan_data).lower()
    found_keywords = [kw for kw in time_keywords if kw in plan_str]

    if found_keywords:
        self.issues.append({
            'severity': 'major',
            'section': 'global',
            'message': f'Plan contains time estimates: {", ".join(found_keywords)}',
            'suggestion': 'Remove time references. Use complexity levels instead (trivial/low/medium/high/very_high)'
        })
```

### 4. Type Definitions
**File:** `type_defs.py`

**Changes:**
- Find TaskDict type definition
- Replace `estimated_effort` field with `complexity` field

### 5. Documentation Updates

**File:** `CLAUDE.md`

**Add to Design Decisions section:**
```markdown
**5. No-Timeline Planning (Agentic Constraint)**
- ✅ Chosen: Complexity-based planning (trivial/low/medium/high/very_high)
- ❌ Rejected: Time estimates (hours, minutes, effort percentage)
- Reason: All coding is agentic - agents don't work on human timelines
- Focus on WHAT and HOW COMPLEX, never WHEN or HOW LONG
```

**File:** `RESOURCE-SHEET-WORKORDER-WORKFLOW.md`

**Update Section 11.3:**
```markdown
### 11.3 Configuration Mistakes

**Time Estimates in Plans:**
- **Mistake:** Including "2 hours", "estimated_effort", or timeline references
- **Error:** Plan validation fails with "Plan contains time estimates" (major severity)
- **Fix:** Use complexity levels instead: trivial | low | medium | high | very_high
- **Principle:** Plans describe WHAT and HOW COMPLEX, never WHEN or HOW LONG
```

### 6. Slash Command Documentation

**File:** `.claude/commands/create-workorder.md`

**Add to workflow description (after Step 4):**
```markdown
**Important Constraint:** Plans are complexity-based, NOT time-based:
- No hours, minutes, duration, or timeline references
- Use complexity levels: trivial | low | medium | high | very_high
- Focus on WHAT needs to be done and HOW complex it is
- Agents work autonomously without deadlines
```

## Implementation Sequence

1. **Update planning template** (authority)
2. **Update plan schema** (validation contract)
3. **Update plan validator** (enforcement)
4. **Update type definitions** (runtime contracts)
5. **Update documentation** (CLAUDE.md, resource sheet)
6. **Update slash commands** (user-facing)
7. **Validate with test plan** (create plan, ensure no time refs)

## Success Criteria

✅ Planning template has zero time references (except in bad examples)
✅ Plan schema enforces `complexity` field instead of `estimated_effort`
✅ Plan validator rejects plans with time keywords
✅ Documentation clearly states "no timeline" principle
✅ New plans generated after changes contain only complexity levels
✅ Validation score improves when using complexity vs time estimates

## Testing Plan

1. Generate new plan with `/create-workorder`
2. Verify plan.json contains `"complexity": "medium"` not `"estimated_effort": "2 hours"`
3. Manually add `"estimated_time": "3 hours"` to plan.json
4. Run `/validate-plan` - should fail with "Plan contains time estimates" error
5. Remove time reference, re-validate - should pass

## Rollout Strategy

**Phase 1: Non-Breaking (Template Updates)**
- Update planning template to use complexity terminology
- Plans generated after this are "new format"
- Old plans with `estimated_effort: low/medium/high` still valid

**Phase 2: Validation (Enforce Constraint)**
- Add validator rule to reject time keywords
- Fails on "hours", "minutes", "duration" in plan text
- Old plans with `estimated_effort` still pass (enum values, not time words)

**Phase 3: Schema Migration (Breaking Change)**
- Rename `estimated_effort` → `complexity` in schema
- Old plans fail validation until migrated
- Provide migration script or manual instructions

## Migration Path for Existing Plans

For plans with old `estimated_effort` field:

```python
# migration.py
def migrate_plan(plan_path):
    with open(plan_path) as f:
        plan = json.load(f)

    for phase in plan.get('6_implementation_phases', []):
        for task in phase.get('tasks', []):
            if 'estimated_effort' in task:
                # Map old values to new complexity levels
                effort_to_complexity = {
                    'low': 'low',
                    'medium': 'medium',
                    'high': 'high'
                }
                task['complexity'] = effort_to_complexity.get(task['estimated_effort'], 'medium')
                del task['estimated_effort']

    with open(plan_path, 'w') as f:
        json.dump(plan, f, indent=2)
```

---

**Created:** 2026-01-10
**Workorder:** WO-NO-TIMELINE-CONSTRAINT-001
**Priority:** P1 (Core Design Principle)
