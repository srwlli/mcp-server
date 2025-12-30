# Planning Workflow Guide

**Version:** 1.0.0
**Last Updated:** 2025-12-29
**Audience:** AI Agents, Developers using coderef-workflow

---

## Purpose

This guide explains how to use the **Planning Workflow System** in coderef-workflow to transform feature ideas into validated, execution-ready implementation plans. It covers the end-to-end workflow from context gathering to plan validation.

---

## Overview

The Planning Workflow System consists of **6 MCP tools** organized in a **5-phase pipeline**:

```
gather_context
     ↓
analyze_project_for_planning
     ↓
get_planning_template + create_plan
     ↓
validate_implementation_plan
     ↓
generate_plan_review_report
```

**Total Time:** ~2-3 minutes
**Output:** Validated plan.json + review report + DELIVERABLES.md template

---

## What: The 5 Phases

### Phase 1: Context Gathering

**Goal:** Capture feature requirements, goals, and constraints

**Tool:** `gather_context`

**What You Provide:**
- **feature_name** - Kebab-case name (e.g., `dark-mode-toggle`)
- **description** - What the feature does
- **goal** - Why you need this feature
- **requirements** - Must-have features (array of strings)
- **constraints** (optional) - Technical or business constraints
- **out_of_scope** (optional) - Explicitly excluded features

**Example:**
```python
await mcp_client.call_tool("gather_context", {
    "project_path": "/workspace/my-app",
    "feature_name": "user-authentication",
    "description": "JWT-based authentication system with refresh tokens",
    "goal": "Secure user sessions and prevent unauthorized access",
    "requirements": [
        "JWT access tokens (15min expiry)",
        "Refresh token rotation",
        "bcrypt password hashing",
        "Login/logout endpoints"
    ],
    "constraints": [
        "Must integrate with existing users table",
        "No third-party auth providers (implement in-house)"
    ],
    "out_of_scope": [
        "OAuth integration",
        "Multi-factor authentication (future phase)"
    ]
})
```

**Output:**
- `coderef/workorder/{feature_name}/context.json`

**What's Captured:**
```json
{
  "feature_name": "user-authentication",
  "description": "...",
  "goal": "...",
  "requirements": [...],
  "constraints": [...],
  "out_of_scope": [...],
  "decisions": {}
}
```

---

### Phase 2: Project Analysis

**Goal:** Understand the existing codebase and patterns

**Tool:** `analyze_project_for_planning`

**What It Does:**
1. Scans foundation docs (ARCHITECTURE.md, SCHEMA.md, README.md)
2. Extracts coding standards from existing code
3. Identifies tech stack and dependencies
4. Calls `coderef-context` for dependency graphs (if available)
5. Searches `coderef/archived/` for similar completed features

**Example:**
```python
await mcp_client.call_tool("analyze_project_for_planning", {
    "project_path": "/workspace/my-app",
    "feature_name": "user-authentication"  # Optional: saves to feature folder
})
```

**Output:**
- `coderef/workorder/{feature_name}/analysis.json`

**What's Captured:**
```json
{
  "foundation_docs": ["ARCHITECTURE.md", "SCHEMA.md"],
  "coding_standards": [
    "Python 3.10+",
    "async/await patterns",
    "Type hints required"
  ],
  "tech_stack": {
    "framework": "FastAPI",
    "database": "PostgreSQL",
    "orm": "SQLAlchemy"
  },
  "key_patterns": [
    "Decorator-based route handlers",
    "Pydantic models for validation",
    "Dependency injection for services"
  ],
  "reference_components": [
    "src/auth/models.py - User model example",
    "src/middleware/cors.py - Middleware pattern"
  ],
  "similar_features": [
    "archived/password-reset - Token-based flow example"
  ]
}
```

**Performance:** 30-60 seconds

---

### Phase 3: Plan Generation

**Goal:** Create a comprehensive 10-section implementation plan

**Tools:** `get_planning_template` (optional) + `create_plan`

#### Step 3a: Get Planning Template (Optional)

If you want to review the plan structure first:

```python
template = await mcp_client.call_tool("get_planning_template", {
    "section": "all"  # or specific section like "2_risk_assessment"
})
```

This returns the canonical 10-section structure:
1. `META_DOCUMENTATION` - Version, workorder ID, status
2. `0_preparation` - Foundation docs, standards, patterns
3. `1_executive_summary` - What & why (3-5 bullets)
4. `2_risk_assessment` - Breaking changes, security, performance
5. `3_current_state_analysis` - Existing architecture
6. `4_key_features` - Must-have requirements
7. `5_task_id_system` - Task naming conventions
8. `6_implementation_phases` - Phased breakdown with dependencies
9. `7_testing_strategy` - Unit, integration, e2e tests
10. `8_success_criteria` - How to verify completion

#### Step 3b: Create Plan

```python
result = await mcp_client.call_tool("create_plan", {
    "project_path": "/workspace/my-app",
    "feature_name": "user-authentication",
    "workorder_id": "WO-AUTH-001"  # Optional: auto-generated if omitted
})
```

**What It Does:**
1. Loads `context.json` and `analysis.json`
2. Loads the planning template
3. Synthesizes all inputs into a complete plan
4. Generates phased task breakdown
5. Assigns unique task IDs (e.g., SETUP-001, IMPL-002)
6. Creates DELIVERABLES.md template

**Output:**
- `coderef/workorder/{feature_name}/plan.json` (complete 10-section plan)
- `coderef/workorder/{feature_name}/DELIVERABLES.md` (metrics template)

**Performance:** 10-60 seconds

---

### Phase 4: Validation

**Goal:** Score plan quality and identify issues

**Tool:** `validate_implementation_plan`

**Example:**
```python
validation = await mcp_client.call_tool("validate_implementation_plan", {
    "project_path": "/workspace/my-app",
    "plan_file_path": "coderef/workorder/user-authentication/plan.json"
})
```

**What It Checks (15-point checklist):**
1. All 10 sections present and non-empty
2. Executive summary is 3-5 bullets
3. Risk assessment covers 5 dimensions
4. Tasks have clear descriptions
5. Task IDs follow naming convention
6. Dependencies are explicit
7. Testing strategy is comprehensive
8. Success criteria are measurable
9. ... and 6 more checks

**Output:**
```json
{
  "score": 92,
  "approved": true,
  "grade": "A",
  "issues": {
    "critical": [],
    "major": [],
    "minor": [
      "Task IMPL-003 has short description (< 20 chars)"
    ]
  },
  "checklist_results": {
    "total": 15,
    "passed": 14,
    "failed": 1
  }
}
```

**Approval Criteria:**
- Score >= 85 → **Approved** (ready for execution)
- Score 70-84 → **Needs Revision** (fix major issues)
- Score < 70 → **Rejected** (significant problems)

**Performance:** 2-5 seconds

---

### Phase 5: Review Reporting

**Goal:** Generate human-readable review report

**Tool:** `generate_plan_review_report`

**Example:**
```python
report = await mcp_client.call_tool("generate_plan_review_report", {
    "project_path": "/workspace/my-app",
    "plan_file_path": "coderef/workorder/user-authentication/plan.json",
    "output_path": "coderef/reviews/review-auth.md"  # Optional
})
```

**What It Generates:**
```markdown
# Plan Review Report: user-authentication

**Score:** 92/100
**Grade:** A
**Status:** ✅ Approved

## Summary

The implementation plan for `user-authentication` is comprehensive and well-structured.

## Issue Breakdown

### Critical Issues (0)
None

### Major Issues (0)
None

### Minor Issues (1)
- Task IMPL-003: Description too short (15 chars). Recommended: Expand to clarify purpose.

## Recommendations

1. Expand IMPL-003 description for clarity
2. Consider adding integration tests for token refresh flow

## Next Steps

✅ Plan approved for execution
→ Run `/align-plan` to generate TodoWrite task list
→ Begin implementation
```

**Output:**
- `coderef/reviews/review-{feature_name}-{timestamp}.md`

**Performance:** 1-2 seconds

---

## Why: Design Philosophy

### Why 5 Phases?

1. **Separation of Concerns:** Each phase has a single responsibility
2. **Incremental Refinement:** Each phase adds more detail
3. **Quality Gates:** Validation ensures plan quality before execution
4. **Human Review:** Review reports enable team oversight

### Why Validate Before Execution?

**Problem:** Poor plans lead to:
- Scope creep (missing requirements)
- Implementation blockers (unclear tasks)
- Wasted agent time (vague descriptions)

**Solution:** 15-point validation catches 90% of plan issues before execution

### Why JSON Plans?

- **Machine-Readable:** AI agents can parse and update plans
- **Version Control:** Plans tracked in git
- **Schema Validation:** Enforces consistent structure
- **Tooling Integration:** Easy to integrate with other tools

---

## When: Usage Patterns

### Pattern 1: Solo Developer (Manual Review)

```bash
# Phase 1-3: Generate plan
/create-workorder

# Phase 4-5: Review plan quality
mcp__coderef_workflow__validate_implementation_plan(...)
mcp__coderef_workflow__generate_plan_review_report(...)

# Read review report
cat coderef/reviews/review-auth-20251229.md

# If approved, execute
/align-plan
```

### Pattern 2: AI Agent (Automated Refinement)

```python
# Generate initial plan
plan = await create_plan(...)

# Validate
validation = await validate_implementation_plan(...)

# If score < 85, refine and retry
while validation['score'] < 85:
    issues = validation['issues']
    # Fix issues in plan.json
    await fix_plan_issues(plan, issues)
    # Re-validate
    validation = await validate_implementation_plan(...)

# Generate review report
await generate_plan_review_report(...)
```

### Pattern 3: Team Workflow (Async Review)

```bash
# Agent generates plan
AI Agent: /create-workorder → plan.json created

# Agent validates and creates review
AI Agent: /validate-plan → Score: 88/100
AI Agent: /review-plan → review-auth.md created

# Human reviews markdown report
Developer: cat coderef/reviews/review-auth.md
Developer: "Looks good, approved!"

# Agent executes
AI Agent: /align-plan → Start implementation
```

---

## How: Step-by-Step Examples

### Example 1: Complete Workflow (Dark Mode Feature)

```python
# Phase 1: Gather context
await gather_context({
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode-toggle",
    "description": "Toggle between light and dark UI themes",
    "goal": "Improve accessibility and reduce eye strain",
    "requirements": [
        "Theme toggle button in navbar",
        "Persist theme preference in localStorage",
        "Detect system theme preference",
        "Smooth color transitions"
    ]
})
# → context.json created

# Phase 2: Analyze project
await analyze_project_for_planning({
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode-toggle"
})
# → analysis.json created (found: React, CSS modules, localStorage patterns)

# Phase 3: Create plan
plan = await create_plan({
    "project_path": "/workspace/my-app",
    "feature_name": "dark-mode-toggle"
})
# → plan.json created with 27 tasks across 4 phases

# Phase 4: Validate
validation = await validate_implementation_plan({
    "project_path": "/workspace/my-app",
    "plan_file_path": "coderef/workorder/dark-mode-toggle/plan.json"
})
# → Score: 94/100 (Approved)

# Phase 5: Review report
report = await generate_plan_review_report({
    "project_path": "/workspace/my-app",
    "plan_file_path": "coderef/workorder/dark-mode-toggle/plan.json"
})
# → review-dark-mode-toggle-20251229.md created
```

**Total Time:** ~2.5 minutes
**Result:** Approved plan ready for execution

---

### Example 2: Iterative Refinement

```python
# Generate initial plan
plan = await create_plan({"feature_name": "api-rate-limiting"})

# Validate (first attempt)
v1 = await validate_implementation_plan(...)
# Score: 72/100 (Needs Revision)
# Issues:
#   - Critical: Missing risk assessment for backward compatibility
#   - Major: Task IMPL-005 description unclear

# Fix issues manually or with AI
plan_data = json.load(open("plan.json"))
plan_data["2_risk_assessment"]["breaking_changes"] = {
    "risk": "Medium",
    "details": "Rate limiting headers may break clients expecting unlimited requests",
    "mitigation": "Phase 1: Warn-only mode, Phase 2: Enforce"
}
plan_data["6_implementation_phases"]["phase_2"]["tasks"][4]["description"] = \
    "Implement Redis-backed rate limiter with sliding window algorithm"
json.dump(plan_data, open("plan.json", "w"))

# Re-validate (second attempt)
v2 = await validate_implementation_plan(...)
# Score: 89/100 (Approved!)

# Generate review
await generate_plan_review_report(...)
```

---

## Troubleshooting

### Issue: "Score too low (< 70)"

**Symptoms:** Validation fails with many critical issues

**Common Causes:**
1. Missing required sections in plan.json
2. Empty or placeholder content
3. Malformed JSON structure

**Fix:**
```python
# Re-run create_plan to regenerate from scratch
await create_plan({"feature_name": "...", "workorder_id": "..."})
```

---

### Issue: "Analysis takes > 2 minutes"

**Symptoms:** `analyze_project_for_planning` hangs or times out

**Common Causes:**
1. Very large codebase (> 100k LOC)
2. coderef-context unavailable
3. Network issues (if coderef-context remote)

**Fix:**
```python
# Skip analysis and use manual preparation
context = {
    "foundation_docs": ["ARCHITECTURE.md"],
    "coding_standards": ["TypeScript", "React"],
    "tech_stack": {"framework": "Next.js"}
}
# Save manually to analysis.json
```

---

### Issue: "Validation says 'missing section' but it exists"

**Symptoms:** Validation fails on section that's present in plan.json

**Common Causes:**
1. Section is empty array or empty string
2. Section key name typo (e.g., `4_key_feature` vs `4_key_features`)

**Fix:**
```json
// Bad (empty)
"4_key_features": []

// Good (has content)
"4_key_features": [
    {
        "id": "KF-001",
        "description": "..."
    }
]
```

---

## Best Practices

### 1. Always Validate Before Execution

```python
# ✅ Good
plan = await create_plan(...)
validation = await validate_implementation_plan(...)
if validation['approved']:
    await execute_plan(...)

# ❌ Bad (skipping validation)
plan = await create_plan(...)
await execute_plan(...)  # Might have poor-quality plan
```

### 2. Capture Constraints Explicitly

```python
# ✅ Good
constraints = [
    "Must use existing auth middleware",
    "No breaking changes to public API",
    "Performance: < 50ms latency"
]

# ❌ Bad (vague)
constraints = ["Be fast"]
```

### 3. Use Specific Requirements

```python
# ✅ Good
requirements = [
    "Login endpoint: POST /auth/login",
    "JWT access tokens (15min expiry)",
    "bcrypt password hashing (10 rounds)"
]

# ❌ Bad (vague)
requirements = ["User login", "Secure passwords"]
```

### 4. Review Generated Plans

Even with validation, manually review plans for:
- Missed edge cases
- Overly complex solutions
- Missing tests for critical paths

---

## Integration with Other Tools

### With coderef-context

```python
# Planning workflow automatically calls coderef-context during analysis
analysis = await analyze_project_for_planning({"project_path": "..."})
# Internally calls:
#   - coderef_scan() for dependency graph
#   - coderef_patterns() for code patterns
#   - coderef_complexity() for hotspots
```

### With coderef-docs

```python
# After plan validation, update documentation
await update_all_documentation({
    "project_path": "...",
    "change_type": "feature",
    "feature_description": "Added dark mode toggle",
    "workorder_id": "WO-DARK-MODE-001"
})
```

### With /align-plan Command

```bash
# After plan approved, generate TodoWrite task list
/align-plan

# Loads plan.json, generates:
# - WO-AUTH-001 | SETUP-001: Configure auth middleware
# - WO-AUTH-001 | IMPL-001: Create login endpoint
# - WO-AUTH-001 | IMPL-002: Implement JWT generation
# ... (27 tasks total)
```

---

## Performance Tips

### Parallel Phase Execution (Future)

Currently sequential:
```
gather_context (60s) → analyze_project (60s) → create_plan (30s) = 150s
```

Future optimization:
```
gather_context (60s) → [analyze_project + get_template] (60s parallel) → create_plan (30s) = 90s
```

**Estimated Speedup:** 40% reduction

### Caching Analysis Results

```python
# First run: Full analysis (60s)
await analyze_project_for_planning({"feature_name": "auth"})

# Second run: Reuses cached analysis.json (0s)
await create_plan({"feature_name": "auth"})
```

**Pro Tip:** Only re-run analysis if codebase changes significantly

---

## References

- **API.md** - Complete tool reference for all planning tools
- **ARCHITECTURE.md** - Planning Workflow System architecture
- **feature-implementation-planning-standard.json** - Canonical plan template
- **SCHEMA.md** - Data models for context.json, plan.json, analysis.json

---

## Quick Reference

| Phase | Tool | Input | Output | Duration |
|-------|------|-------|--------|----------|
| 1 | gather_context | Requirements | context.json | 30-60s |
| 2 | analyze_project_for_planning | Project path | analysis.json | 30-60s |
| 3 | create_plan | context + analysis | plan.json | 10-60s |
| 4 | validate_implementation_plan | plan.json | Validation score | 2-5s |
| 5 | generate_plan_review_report | Validation results | Review markdown | 1-2s |

**Total:** ~2-3 minutes from idea to validated plan

---

**For AI Agents:** This workflow is designed for autonomous execution. Start with `gather_context`, proceed sequentially through all 5 phases, and only execute if validation score >= 85. Use the review report to communicate plan quality to human reviewers.
