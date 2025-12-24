Create implementation plan by synthesizing context, analysis, and template into a complete plan.json file.

Ask the user for the feature name (alphanumeric, hyphens, underscores only), then call the `mcp__coderef-docs__create_plan` tool with:
- project_path: current working directory
- feature_name: the user-provided feature name

This is a **meta-tool** that guides AI through plan generation by:
1. Loading context.json from user's project (from prior `/gather-context` if available)
2. Loading project analysis (from prior `/analyze-for-planning` if available)
3. Loading AI-optimized template from **MCP server's directory** (not user's project)
4. Returning all inputs to AI with synthesis instructions
5. AI generates complete 10-section plan
6. AI saves to coderef/working/{feature_name}/plan.json

Generation process:
- **AI synthesizes**: Tool provides inputs, AI creates the actual plan content
- **Context-aware**: Uses user's requirements and project analysis
- **Template-guided**: Follows planning-template-for-ai.json structure
- **Complete plans**: No placeholder TODOs, real implementation details

Returns:
- Plan file path
- Feature name
- Sections completed (0-10)
- Status: 'complete' | 'partial'
- Has context/analysis indicators
- Next steps recommendations

**Workflow integration**:
1. `/gather-context` - Gather feature requirements (optional but recommended)
2. `/analyze-for-planning` - Analyze project context (optional but recommended)
3. `/create-plan` - **Generate plan** ← You are here

**Important**: Best results require both context.json and project analysis. Tool will warn if either is missing.

## Step-by-Step Workflow

### Step 1: Create Plan

Call the create_plan MCP tool:

```python
mcp__coderef-docs__create_plan({
    "project_path": <current_working_directory>,
    "feature_name": <user_provided_feature_name>
})
```

This creates `coderef/working/{feature_name}/plan.json` with:
- Complete 10-section implementation plan
- Workorder ID embedded in section 5
- DELIVERABLES.md template (auto-generated)

### Step 2: Validate Plan

Call the validate_implementation_plan MCP tool:

```python
mcp__coderef-docs__validate_implementation_plan({
    "project_path": <current_working_directory>,
    "plan_file_path": f"coderef/working/{feature_name}/plan.json"
})
```

Returns validation result with:
- Score (0-100)
- Issues by severity (critical, major, minor)
- Approved status (true if score >= 90)

### Step 3: Validation Loop (if needed)

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

### Step 4: Log Workorder

After validation passes, log the workorder to both local and orchestrator:

```python
mcp__coderef-docs__log_workorder({
    "project_path": <current_working_directory>,
    "workorder_id": <workorder_id_from_plan>,
    "project_name": <project_folder_name>,
    "description": f"{feature_name} implementation plan"
})
```

This logs to:
- Local: `{project}/coderef/workorder-log.txt`
- Orchestrator: `C:\Users\willh\Desktop\assistant\coderef\workorder-log.txt`

### Step 5: Commit & Push

After validation passes, commit and push planning artifacts:

```bash
# Stage planning artifacts
git add coderef/working/{feature_name}/

# Commit with descriptive message
git commit -m "plan({feature_name}): Add implementation plan

Workorder: {workorder_id}
Validation Score: {score}/100

Files:
- plan.json (implementation plan)
- DELIVERABLES.md (tracking template)

Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push
```

### Step 6: Output Summary

Present summary to user:

```
Plan Created: {feature_name}

Workorder: {workorder_id}
Location: coderef/working/{feature_name}/

Files Created:
- plan.json (implementation plan)
- DELIVERABLES.md (tracking template)

Validation Score: {score}/100
Status: {PASS|PASS_WITH_WARNINGS|NEEDS_REVISION}

Workorder logged to local + orchestrator

Next Steps:
1. Run /execute-plan to generate task list
2. Implement the feature following the plan phases
3. Run /update-deliverables to mark complete
4. Run /update-docs to update changelog
5. Run /archive-feature to complete the workflow
```

### Step 7: Archive Feature (Post-Implementation)

After implementation is complete and deliverables/docs are updated, archive the feature:

```python
mcp__coderef-docs__archive_feature({
    "project_path": <current_working_directory>,
    "feature_name": <feature_name>
})
```

This:
- Moves `coderef/working/{feature_name}/` to `coderef/archived/{feature_name}/`
- Updates `coderef/archived/index.json` with metadata
- Logs completion to orchestrator workorder-log.txt

**When to run**: After all implementation tasks are complete and verified.

## Complete Workflow Lifecycle

```
/create-plan
    ↓
/execute-plan (generate task list)
    ↓
[Implementation Phase]
    ↓
/update-deliverables (mark complete)
    ↓
/update-docs (changelog + version)
    ↓
/archive-feature (move to archived)
```

## When to Use

Use `/create-plan` when:
- You already have context.json (from prior `/gather-context`)
- You already have analysis.json (from prior `/analyze-for-planning`)
- You want to regenerate just the plan without re-gathering context
- You need fine-grained control over planning steps

Use `/create-workorder` when:
- Starting a new feature from scratch
- You want the FULL workflow (context + foundation docs + analysis + plan)
- You don't have existing context/analysis

## Comparison with /create-workorder

| Aspect | /create-plan | /create-workorder |
|--------|--------------|-------------------|
| Context Gathering | Assumes exists | Interactive Q&A |
| Foundation Docs | Assumes exists | Auto-generates |
| Project Analysis | Assumes exists | Auto-generates |
| Plan Creation | Yes | Yes |
| Validation | Yes (auto-fix loop) | Yes (auto-fix loop) |
| Git Commit | Yes | Yes |
| Workorder Logging | Yes | Yes |
| Multi-Agent Setup | No | Yes (optional) |

**Key Difference**: `/create-plan` skips context gathering and foundation docs generation - use when you already have those or want to regenerate just the plan.
