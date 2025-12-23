Create a new workorder with the complete planning workflow: gather context, analyze project, create plan, and validate.

This command orchestrates the full planning pipeline in sequence, eliminating the need to run each step manually. Workorders are automatically logged to both local and orchestrator workorder-log.txt for central tracking.

## Workflow Overview

```
/create-workorder
    |
    v
1. Get Feature Name (AskUserQuestion)
    |
    v
2. Gather Context (interactive Q&A)
    |
    v
3. Generate Foundation Docs (automatic via coderef_foundation_docs) [NEW]
    |
    v
4. Analyze Project (automatic via analyze_project_for_planning)
    |
    v
5. Create Plan (automatic via create_plan)
    |
    v
6. Multi-Agent Decision (AskUserQuestion - based on phase count)
    |
    v
7. Validate Plan (automatic via validate_implementation_plan)
    |
    v
8. Validation Loop (if score < 90, fix and re-validate, max 3 iterations)
    |
    v
9. Output Summary
    |
    v
10. Commit & Push (pre-execution checkpoint)
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
mcp__coderef_workflow__gather_context({
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

### Step 3: Generate Foundation Docs [NEW]

Call the coderef_foundation_docs MCP tool to generate comprehensive project context:

```python
mcp__coderef_workflow__coderef_foundation_docs({
    "project_path": <current_working_directory>
})
```

This generates:
- **ARCHITECTURE.md** - Patterns, decisions, constraints (deep extraction from existing docs)
- **SCHEMA.md** - Database entities and relationships
- **COMPONENTS.md** - Component hierarchy (for UI projects only)
- **project-context.json** - Structured context with:
  - API endpoints (auto-detected from code)
  - Database schema (from models/migrations)
  - Dependencies (from package.json/requirements.txt)
  - Git activity (recent commits, active files, contributors)
  - Code patterns (handlers, decorators, error handling)
  - Similar features (from coderef/archived/)

Files are saved to `coderef/foundation-docs/`.

This step replaces the need for separate inventory commands (api_inventory, database_inventory, dependency_inventory, etc.) and provides much richer context for planning.

### Step 4: Analyze Project

Call the analyze_project_for_planning MCP tool:

```python
mcp__coderef_workflow__analyze_project_for_planning({
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

### Step 5: Create Plan

Call the create_plan MCP tool:

```python
mcp__coderef_workflow__create_plan({
    "project_path": <current_working_directory>,
    "feature_name": <from_step_1>
})
```

This creates `coderef/working/{feature_name}/plan.json` with:
- Complete 10-section implementation plan
- Workorder ID embedded in section 5
- DELIVERABLES.md template

### Step 6: Multi-Agent Decision

After the plan is created, count the number of implementation phases and ask the user about multi-agent mode:

1. Read plan.json and count phases in `UNIVERSAL_PLANNING_STRUCTURE.6_implementation_phases`
2. Use AskUserQuestion:

```
Question: "Plan has {phase_count} phases. Enable multi-agent mode for parallel execution?"
Header: "Multi-Agent"
multiSelect: false
Options: [
  {"label": "Yes, use {phase_count} agents", "description": "1 agent per phase (recommended for parallel work)"},
  {"label": "Yes, fewer agents", "description": "I'll specify how many agents to use"},
  {"label": "No, single agent", "description": "Sequential execution (default)"}
]
```

3. If user selects "Yes, use {phase_count} agents":
   - Store `agent_count = phase_count`
   - Set `multi_agent = true`

4. If user selects "Yes, fewer agents":
   - Ask follow-up: "How many agents? (1-{phase_count})"
   - Store user's response as `agent_count`
   - Set `multi_agent = true`

5. If user selects "No, single agent":
   - Set `multi_agent = false`
   - Skip communication.json generation

6. If `multi_agent = true`, call generate_agent_communication:

```python
mcp__coderef_workflow__generate_agent_communication({
    "project_path": <current_working_directory>,
    "feature_name": <from_step_1>
})
```

This creates `coderef/working/{feature_name}/communication.json` with:
- **`tasks` array** - Single source of truth for task tracking (status: pending/in_progress/complete/blocked)
- **`progress` summary** - Auto-calculated totals (complete/pending/percent)
- Forbidden files per agent (prevents conflicts)
- Success criteria per phase
- Workorder IDs for each agent

**Agent Task Tracking:**
Agents update communication.json directly as they work:
```json
"tasks": [
  {"id": "STEP-001", "description": "Read plan.json", "status": "complete", "completed_at": "2025-12-07T23:15:00Z"},
  {"id": "STEP-002", "description": "Create conftest.py", "status": "in_progress", "completed_at": null},
  {"id": "STEP-003", "description": "Update pyproject.toml", "status": "pending", "completed_at": null}
]
```

### Step 7: Validate Plan

Call the validate_implementation_plan MCP tool:

```python
mcp__coderef_workflow__validate_implementation_plan({
    "project_path": <current_working_directory>,
    "plan_file_path": f"coderef/working/{feature_name}/plan.json"
})
```

Returns validation result with:
- Score (0-100)
- Issues by severity (critical, major, minor)
- Checklist results
- Approved status (true if score >= 90)

### Step 8: Validation Loop (if needed)

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

### Step 9: Output Summary

After validation passes (or max iterations reached), present summary:

**For single-agent mode:**
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
3. Implement the feature following the plan phases
4. Run /update-deliverables to capture git metrics (LOC, commits, time)
5. Run /update-docs to update changelog and documentation
6. Run /update-foundation-docs to update API.md, user-guide.md, etc. if needed
7. Run /archive-feature to complete the workflow
```

**For multi-agent mode:**
```
Feature Planning Complete: {feature_name}

Workorder: {workorder_id}
Location: coderef/working/{feature_name}/
Mode: Multi-Agent ({agent_count} agents)

Files Created:
- context.json (requirements)
- analysis.json (project analysis)
- plan.json (implementation plan)
- DELIVERABLES.md (tracking template)
- communication.json (agent coordination + task tracking)

Validation Score: {score}/100
Status: {PASS|PASS_WITH_WARNINGS|NEEDS_REVISION}

Next Steps:
1. Review communication.json for agent assignments and task list
2. Assign agents: /assign-agent-task (for each agent 1-{agent_count})
3. Each agent implements their phase, updating communication.json tasks:
   - Set task status to "in_progress" when starting
   - Set status to "complete" with timestamp when done
   - Lloyd can check progress anytime via communication.json
4. Verify each agent: /verify-agent-completion
5. Track progress: /track-agent-status (reads from communication.json)
6. Aggregate results: /aggregate-agent-deliverables
7. Run /update-docs to update changelog and documentation
8. Run /update-foundation-docs to update API.md, user-guide.md, etc. if needed
9. Run /archive-feature to complete the workflow
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

### Step 10: Commit & Push (Pre-Execution Checkpoint)

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

Use /create-workorder when:
- Starting a new feature from scratch
- You want the full planning workflow
- You need a high-quality implementation plan
- You want workorder logged to orchestrator for central tracking

Use individual commands when:
- You already have partial context
- You want to skip certain steps
- You need fine-grained control

## Related Commands

- `/gather-context` - Step 2 only (requirements gathering)
- `/coderef-foundation-docs` - Step 3 only (foundation docs generation) [NEW]
- `/analyze-for-planning` - Step 4 only (project analysis)
- `/create-plan` - Step 5 only (plan generation)
- `/validate-plan` - Step 7 only (validation)
- `/execute-plan` - Generate task list from plan
