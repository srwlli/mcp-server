Start a new feature with the complete planning workflow: gather context, analyze project, create plan, and validate.

This command orchestrates the full planning pipeline in sequence, eliminating the need to run each step manually.

## Workflow Overview

```
/start-feature
    |
    v
1. Get Feature Name (AskUserQuestion)
    |
    v
2. Gather Context (interactive Q&A via /gather-context)
    |
    v
3. Analyze Project (automatic via analyze_project_for_planning)
    |
    v
4. Create Plan (automatic via create_plan)
    |
    v
5. Validate Plan (automatic via validate_implementation_plan)
    |
    v
6. Validation Loop (if score < 90, fix and re-validate, max 3 iterations)
    |
    v
7. Output Summary
    |
    v
8. Commit & Push (pre-execution checkpoint)
```

## Step-by-Step Instructions

### Step 1: Get Feature Name

Use AskUserQuestion to ask for the feature name:

```
Question: "What's the feature name? (Use alphanumeric, hyphens, or underscores only)"
Header: "Feature Name"
multiSelect: false
Options: [
  {"label": "Let me type it", "description": "I'll provide a custom feature name"}
]
```

User will type their feature name in the "Other" field (e.g., "user-authentication", "dark-mode-toggle").

Store this as `feature_name` for use in subsequent steps.

### Step 2: Gather Context

Execute the /gather-context workflow with the feature name from Step 1.

This involves the interactive Q&A flow:
- Get feature goal and description
- Gather requirements (multi-select)
- Identify out-of-scope items
- Gather constraints

After gathering all responses, call:

```python
mcp__docs_mcp__gather_context({
    "project_path": <current_working_directory>,
    "feature_name": <from_step_1>,
    "description": <collected_description>,
    "goal": <collected_goal>,
    "requirements": [<collected_requirements>],
    "out_of_scope": [<collected_exclusions>],
    "constraints": [<collected_constraints>]
})
```

This creates `coderef/working/{feature_name}/context.json`.

### Step 3: Analyze Project

Call the analyze_project_for_planning MCP tool:

```python
mcp__docs_mcp__analyze_project_for_planning({
    "project_path": <current_working_directory>,
    "feature_name": <from_step_1>
})
```

This creates `coderef/working/{feature_name}/analysis.json` with:
- Foundation docs available/missing
- Coding standards
- Technology stack
- Key patterns identified
- Project structure
- Gaps and risks

### Step 4: Create Plan

Call the create_plan MCP tool:

```python
mcp__docs_mcp__create_plan({
    "project_path": <current_working_directory>,
    "feature_name": <from_step_1>
})
```

This creates `coderef/working/{feature_name}/plan.json` with:
- Complete 10-section implementation plan
- Workorder ID embedded in section 5
- DELIVERABLES.md template

### Step 5: Validate Plan

Call the validate_implementation_plan MCP tool:

```python
mcp__docs_mcp__validate_implementation_plan({
    "project_path": <current_working_directory>,
    "plan_file_path": f"coderef/working/{feature_name}/plan.json"
})
```

Returns validation result with:
- Score (0-100)
- Issues by severity (critical, major, minor)
- Checklist results
- Approved status (true if score >= 90)

### Step 6: Validation Loop (if needed)

If validation score < 90:

1. Review issues by severity (fix critical first, then major, then minor)
2. Read the plan.json file
3. Fix the identified issues in plan.json
4. Write the updated plan.json
5. Re-validate with validate_implementation_plan
6. Repeat until score >= 90 OR max 3 iterations reached

**Issue Priority:**
- Critical (-10 points each): Missing sections, circular dependencies, duplicate task IDs
- Major (-5 points each): Placeholders, vague criteria, missing fields
- Minor (-1 point each): Short descriptions, style issues

### Step 7: Output Summary

After validation passes (or max iterations reached), present summary:

```
Feature Planning Complete: {feature_name}

Workorder: {workorder_id}
Location: coderef/working/{feature_name}/

Files Created:
- context.json (requirements)
- analysis.json (project analysis)
- plan.json (implementation plan)
- DELIVERABLES.md (tracking template)

Validation Score: {score}/100
Status: {PASS|PASS_WITH_WARNINGS|NEEDS_REVISION}

Next Steps:
1. Review the plan at coderef/working/{feature_name}/plan.json
2. Run /execute-plan to generate task list
3. Begin implementation following the plan phases
```

If validation failed after 3 iterations:

```
Feature Planning: {feature_name}

Validation Score: {score}/100 (target: 90)
Status: NEEDS_REVISION

Remaining Issues ({count}):
- {list of critical/major issues}

The plan is saved but needs manual review.
Run /validate-plan to see full issue details.
```

### Step 8: Commit & Push (Pre-Execution Checkpoint)

After validation passes, commit and push all planning artifacts:

```bash
# Stage planning artifacts
git add coderef/working/{feature_name}/

# Commit with descriptive message
git commit -m "plan({feature_name}): Add implementation plan

Workorder: {workorder_id}
Validation Score: {score}/100

Files:
- context.json (requirements)
- analysis.json (project analysis)  
- plan.json (implementation plan)
- DELIVERABLES.md (tracking template)

Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push
```

This creates a **pre-execution checkpoint** that:
- Preserves the approved plan before implementation begins
- Enables handoff to other agents or developers
- Provides rollback point if implementation diverges
- Documents the planning phase in git history

## Benefits

- **One command** - No need to remember 4 separate steps
- **Automatic flow** - Each step feeds into the next
- **Quality gate** - Validation ensures plan meets standards
- **Self-healing** - Auto-fixes minor issues through iteration
- **Complete output** - All planning artifacts generated

## When to Use

Use /start-feature when:
- Starting a new feature from scratch
- You want the full planning workflow
- You need a high-quality implementation plan

Use individual commands when:
- You already have partial context
- You want to skip certain steps
- You need fine-grained control

## Related Commands

- `/gather-context` - Step 2 only (requirements gathering)
- `/analyze-for-planning` - Step 3 only (project analysis)
- `/create-plan` - Step 4 only (plan generation)
- `/validate-plan` - Step 5 only (validation)
- `/execute-plan` - Generate task list from plan
