# `/create-workorder` Workflow Explained

The `/create-workorder` command is the **primary entry point** for feature planning in docs-mcp. It orchestrates the entire planning pipeline in one command, eliminating manual coordination of multiple steps.

## 🎯 What It Does

Creates a complete, validated implementation plan with automatic workorder tracking in **one command**.

## 📋 10-Step Workflow

```
/create-workorder
    ↓
1. Get Feature Name (interactive)
    ↓
2. Gather Context (Q&A: goal, requirements, constraints)
    ↓
3. Generate Foundation Docs (ARCHITECTURE, SCHEMA, project-context.json)
    ↓
4. Analyze Project (tech stack, patterns, risks)
    ↓
5. Create Plan (10-section implementation plan)
    ↓
6. Multi-Agent Decision (optional parallel execution)
    ↓
7. Validate Plan (score 0-100, must be >=90)
    ↓
8. Validation Loop (auto-fix until score >=90, max 3 iterations)
    ↓
9. Output Summary (next steps guidance)
    ↓
10. Commit & Push (pre-execution checkpoint)
```

## 🔑 Key Features

### 1. **Interactive Context Gathering**
Uses `AskUserQuestion` to collect:
- Feature name (alphanumeric-hyphens-underscores)
- Feature goal and description
- Requirements (multi-select)
- Out-of-scope items
- Constraints

Saves to: `coderef/working/{feature_name}/context.json`

### 2. **Automatic Foundation Docs** (NEW)
Calls `coderef_foundation_docs` tool to generate:
- **ARCHITECTURE.md** - Patterns, decisions, constraints
- **SCHEMA.md** - Database entities/relationships
- **COMPONENTS.md** - Component hierarchy (UI projects only)
- **project-context.json** - API endpoints, dependencies, git activity, code patterns

This **replaces** the old separate inventory commands (api_inventory, database_inventory, etc.) with richer context.

### 3. **Project Analysis**
Analyzes and saves to `analysis.json`:
- Foundation docs available/missing
- Coding standards
- Technology stack
- Key patterns identified
- Gaps and risks

### 4. **Plan Generation**
Creates `plan.json` with:
- 10-section structure (preparation → testing)
- **Workorder ID** (format: WO-FEATURE-NAME-001)
- Implementation phases
- Task breakdown
- Success criteria

Also generates `DELIVERABLES.md` template for tracking.

### 5. **Multi-Agent Mode** (Optional)
After plan creation, asks:
> "Plan has {X} phases. Enable multi-agent mode for parallel execution?"

If **yes**, generates `communication.json` with:
- **Tasks array** (single source of truth for progress tracking)
- Status tracking: `pending` | `in_progress` | `complete` | `blocked`
- Auto-calculated progress summary
- Forbidden files per agent (prevents conflicts)
- Workorder IDs for each agent

**How agents use it:**
```json
"tasks": [
  {"id": "STEP-001", "status": "complete", "completed_at": "2025-12-07T23:15:00Z"},
  {"id": "STEP-002", "status": "in_progress", "completed_at": null},
  {"id": "STEP-003", "status": "pending", "completed_at": null}
]
```

### 6. **Quality Gate: Validation Loop**
Automatically validates plan (target: ≥90/100):

**Scoring:**
- Critical issues: -10 points (missing sections, circular deps)
- Major issues: -5 points (placeholders, vague criteria)
- Minor issues: -1 point (short descriptions, style)

**Auto-healing:**
If score < 90, AI automatically:
1. Reviews issues by severity
2. Fixes the plan
3. Re-validates
4. Repeats up to 3 iterations

### 7. **Pre-Execution Checkpoint**
Commits and pushes planning artifacts to git:
```bash
git add coderef/working/{feature_name}/
git commit -m "plan({feature_name}): Add implementation plan..."
git push
```

This creates a **rollback point** before implementation starts.

## 📁 Files Created

**Single-agent mode:**
- `context.json` - Requirements
- `analysis.json` - Project analysis
- `plan.json` - Implementation plan
- `DELIVERABLES.md` - Tracking template

**Multi-agent mode adds:**
- `communication.json` - Agent coordination + task tracking

## 🎬 Next Steps After `/create-workorder`

### Single-Agent Workflow:
```
/create-workorder → /execute-plan → implement → /update-deliverables
→ /update-docs → /update-foundation-docs → /archive-feature
```

### Multi-Agent Workflow:
```
/create-workorder → /assign-agent-task (for each agent)
→ agents implement (updating communication.json)
→ /verify-agent-completion (for each agent)
→ /track-agent-status → /aggregate-agent-deliverables
→ /update-docs → /update-foundation-docs → /archive-feature
```

## ✨ Benefits

1. **One Command** - No need to remember 4-6 separate steps
2. **Automatic Flow** - Each step feeds into the next
3. **Quality Assurance** - Validation ensures plan meets standards (≥90/100)
4. **Self-Healing** - Auto-fixes issues through iteration
5. **Workorder Tracking** - Automatic ID assignment and logging
6. **Git Checkpoint** - Pre-execution commit for rollback capability
7. **Multi-Agent Ready** - Optional parallel execution support

## 🆚 When to Use Individual Commands

Use `/create-workorder` when:
- ✅ Starting a new feature from scratch
- ✅ Want full planning workflow
- ✅ Need high-quality validated plan

Use individual commands (`/gather-context`, `/create-plan`, etc.) when:
- ❌ Already have partial context
- ❌ Want to skip certain steps
- ❌ Need fine-grained control

## 📊 Example Output

```
Feature Planning Complete: user-authentication

Workorder: WO-USER-AUTHENTICATION-001
Location: coderef/working/user-authentication/

Files Created:
- context.json (requirements)
- analysis.json (project analysis)
- plan.json (implementation plan)
- DELIVERABLES.md (tracking template)

Validation Score: 95/100
Status: PASS

Next Steps:
1. Review plan.json
2. Run /execute-plan to generate task list
3. Implement feature following plan phases
4. Run /update-deliverables to capture metrics
5. Run /update-docs to update changelog
6. Run /archive-feature to complete workflow
```

## 🔄 Complete Feature Lifecycle

```
Planning Phase:
├── /create-workorder (creates plan, validates, commits)
│
Implementation Phase:
├── /execute-plan (generates task list)
├── Implement tasks (follow plan phases)
│
Completion Phase:
├── /update-deliverables (capture git metrics: LOC, commits, time)
├── /update-docs (update README, CHANGELOG, CLAUDE.md)
├── /update-foundation-docs (update API.md, user-guide.md if needed)
└── /archive-feature (move to coderef/archived/)
```

## 📝 Notes

- **Workorder ID Format**: `WO-{FEATURE-NAME}-{NUMBER}` (e.g., WO-USER-AUTHENTICATION-001)
- **Validation Target**: Plans must score ≥90/100 to pass
- **Max Iterations**: 3 auto-fix attempts before manual review required
- **Multi-Agent Support**: Optional for features with 2+ implementation phases
- **Git Integration**: All planning artifacts committed before implementation

This workflow ensures every feature gets a **high-quality, validated plan** before implementation begins! 🚀
