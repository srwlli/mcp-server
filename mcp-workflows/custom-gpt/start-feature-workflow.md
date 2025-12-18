# Start Feature Workflow

Complete planning workflow that orchestrates: gather context, analyze project, create plan, and validate.

## Workflow Overview

```
/start-feature
    |
    v
1. Get Feature Name
    |
    v
2. Gather Context (interactive Q&A)
    |
    v
3. Analyze Project (automatic)
    |
    v
4. Create Plan (automatic)
    |
    v
5. Multi-Agent Decision (based on phase count)
    |
    v
6. Validate Plan (automatic)
    |
    v
7. Validation Loop (if score < 90, fix and re-validate)
    |
    v
8. Output Summary
```

## Step-by-Step Instructions

### Step 1: Get Feature Name

Ask for the feature name using alphanumeric characters, hyphens, or underscores only.

Example: "user-authentication", "dark-mode-toggle"

### Step 2: Gather Context

Execute interactive Q&A flow:
- Get feature goal and description
- Gather requirements (multi-select)
- Identify out-of-scope items
- Gather constraints

Creates `context.json` with requirements.

### Step 3: Analyze Project

Automatically discovers:
- Foundation docs available/missing
- Coding standards
- Technology stack
- Key patterns identified
- Project structure
- Gaps and risks

Creates `analysis.json`.

### Step 4: Create Plan

Generates 10-section implementation plan:
- Preparation (section 0)
- Executive Summary (section 1)
- Risk Assessment (section 2)
- Current State Analysis (section 3)
- Key Features (section 4)
- Task ID System (section 5)
- Implementation Phases (section 6)
- Testing Strategy (section 7)
- Success Criteria (section 8)
- Implementation Checklist (section 9)

Creates `plan.json` and `DELIVERABLES.md`.

### Step 5: Multi-Agent Decision

Count implementation phases and ask:
- "Yes, use N agents" - 1 agent per phase
- "Yes, fewer agents" - Specify count
- "No, single agent" - Sequential execution

### Step 6: Validate Plan

Score plan quality (0-100):
- Critical issues: -10 points each
- Major issues: -5 points each
- Minor issues: -1 point each

Must score >= 90 to pass.

### Step 7: Validation Loop

If score < 90:
1. Review issues by severity
2. Fix critical issues first
3. Re-validate
4. Repeat until >= 90 or max 3 iterations

### Step 8: Output Summary

Present completion summary with:
- Workorder ID
- Files created
- Validation score
- Next steps

## Files Created

```
coderef/working/{feature_name}/
├── context.json      (requirements)
├── analysis.json     (project analysis)
├── plan.json         (implementation plan)
└── DELIVERABLES.md   (tracking template)
```

## Benefits

- **One command** - Full planning pipeline
- **Automatic flow** - Each step feeds into the next
- **Quality gate** - Validation ensures standards
- **Self-healing** - Auto-fixes through iteration
- **Complete output** - All planning artifacts generated
