# Features: coderef-workflow

**What can coderef-workflow do for you?**

This document provides a comprehensive overview of coderef-workflow capabilities organized by feature category.

---

## Table of Contents

1. [Planning & Context Intelligence](#planning--context-intelligence)
2. [Execution & Progress Tracking](#execution--progress-tracking)
3. [Multi-Agent Coordination](#multi-agent-coordination)
4. [Risk Assessment & Impact Analysis](#risk-assessment--impact-analysis)
5. [Documentation Automation](#documentation-automation)
6. [Feature Lifecycle Management](#feature-lifecycle-management)
7. [Quality Assurance](#quality-assurance)
8. [Workorder Audit Trail](#workorder-audit-trail)
9. [Feature Comparison](#feature-comparison)

---

## Planning & Context Intelligence

### What You Can Do

✅ **Gather Feature Requirements** - Interactive workflow collects description, goals, requirements, constraints
✅ **Analyze Project Structure** - Scans codebase for architecture patterns, coding standards, tech stack
✅ **Generate Implementation Plans** - Creates 10-section plan.json with phased task breakdown
✅ **Validate Plan Quality** - AI-powered scoring (0-100) with automated issue detection
✅ **Integrate Code Intelligence** - Calls coderef-context for AST analysis, dependency graphs, pattern detection

### Use Cases

**For Developers:**
- Plan complex features before writing code
- Understand existing codebase patterns
- Avoid breaking changes with dependency analysis

**For Team Leads:**
- Review implementation plans before approval
- Estimate effort from task breakdown
- Ensure consistency with coding standards

**For AI Agents:**
- Get structured context before autonomous coding
- Access full dependency awareness
- Follow established project patterns

### Example

**Input:** "Add user authentication with JWT tokens"

**Output:**
```json
{
  "META_DOCUMENTATION": {
    "workorder_id": "WO-AUTH-SYSTEM-001",
    "feature_name": "jwt-authentication",
    "status": "planning",
    "task_count": 47
  },
  "6_IMPLEMENTATION_PHASES": {
    "phase_1": {
      "name": "Setup & Foundation",
      "tasks": [
        {"id": "SETUP-001", "title": "Install JWT library"},
        {"id": "SETUP-002", "title": "Create auth service skeleton"}
      ]
    }
  }
}
```

**Time:** 5-10 minutes for complete planning workflow

---

## Execution & Progress Tracking

### What You Can Do

✅ **Align Plan with TodoWrite** - Generate CLI task checklist from plan.json
✅ **Track Task Progress** - Update individual task status (pending → in_progress → completed)
✅ **Dashboard for Agents** - View agent assignments and progress across all features
✅ **Generate Handoff Context** - Create claude.md for smooth agent transitions

### Use Cases

**For Solo Developers:**
- Visual task checklist in CLI terminal
- Mark tasks complete as you work
- Never lose track of implementation progress

**For Multi-Agent Teams:**
- Coordinate parallel work streams
- Prevent duplicate effort
- Track which agent owns which tasks

**For Project Managers:**
- Real-time progress visibility
- Identify blocked tasks
- Estimate remaining work

### Example

**Command:**
```bash
/align-plan jwt-authentication
```

**Output (printed to CLI):**
```
**Workorder: WO-AUTH-SYSTEM-001 - jwt-authentication**

### Phase 1: Setup & Foundation (5 tasks)
☐ SETUP-001: Install JWT library (pyjwt>=2.8.0)
☐ SETUP-002: Create auth service skeleton
☐ SETUP-003: Define token schemas (access + refresh)
☐ SETUP-004: Set up environment variables (JWT_SECRET)
☐ SETUP-005: Create authentication middleware

### Phase 2: Implementation (12 tasks)
☐ IMPL-001: Implement token generation
...
```

**Time:** < 1 minute to generate checklist

---

## Multi-Agent Coordination

### What You Can Do

✅ **Enable Parallel Execution** - Split features into independent phases for simultaneous work
✅ **Assign Tasks to Agents** - Explicit agent-to-phase mapping (Agent 1 → Frontend, Agent 2 → Backend)
✅ **Prevent File Conflicts** - communication.json defines "forbidden files" per agent
✅ **Verify Completion** - Automated git diff checks against success criteria
✅ **Aggregate Metrics** - Combine deliverables from all agents into unified report

### Use Cases

**For Large Features:**
- Reduce wall-clock time by 50-70%
- Frontend + Backend + Tests in parallel
- Independent deployment pipelines

**For Distributed Teams:**
- Timezone-independent work
- Clear ownership boundaries
- Automated conflict prevention

**For AI Agent Swarms:**
- Coordinate 2-10 specialized agents
- Each agent has unique workorder ID (WO-FEATURE-001, WO-FEATURE-002)
- Automatic progress synchronization

### Example

**Setup:**
```bash
/create-workorder
# → Multi-agent mode: Yes (3 agents)
```

**Assign:**
```bash
/assign-agent-task user-dashboard 1  # Frontend (Ava)
/assign-agent-task user-dashboard 2  # Backend (Marcus)
/assign-agent-task user-dashboard 3  # Tests (Quinn)
```

**Track:**
```bash
/track-agent-status user-dashboard
```

**Output:**
```
Agent 1 (Ava): IN_PROGRESS - Phase 1: Frontend Components
  Forbidden: src/backend/*, tests/*

Agent 2 (Marcus): COMPLETED - Phase 2: API Endpoints
  Forbidden: src/frontend/*, tests/*

Agent 3 (Quinn): PENDING - Phase 3: Integration Tests
  Forbidden: src/frontend/*, src/backend/*
```

**Time Saved:** Feature that takes 6 hours sequentially → ~2-3 hours with 3 agents

---

## Risk Assessment & Impact Analysis

### What You Can Do

✅ **Score Proposed Changes** - AI evaluates risk (0-100) across 5 dimensions
✅ **Identify Breaking Changes** - Dependency analysis shows ripple effects
✅ **Security Impact** - Detects auth, input validation, sensitive data changes
✅ **Performance Impact** - Identifies database queries, loops, network calls
✅ **Reversibility Check** - Estimates rollback difficulty
✅ **Mitigation Suggestions** - Concrete steps to reduce risk

### Use Cases

**Before Refactoring:**
- Rename AuthService → AuthenticationService (risk score: 45)
- Split auth module into separate files (risk score: 60)
- Move database queries to service layer (risk score: 30)

**Before Breaking Changes:**
- Change API response format (risk score: 85 - STOP)
- Remove deprecated function (risk score: 70 - CAUTION)
- Upgrade framework version (risk score: 55 - PROCEED WITH CARE)

**For Code Reviews:**
- Automated risk assessment before merge
- Compare risk across implementation options
- Justify high-risk changes with mitigation plan

### Example

**Input:**
```json
{
  "proposed_change": {
    "description": "Rename getUserById → fetchUserByIdentifier",
    "change_type": "refactor",
    "files_affected": ["src/user_service.py"]
  }
}
```

**Output:**
```json
{
  "overall_score": 42,
  "recommendation": "PROCEED_WITH_CAUTION",
  "risk_breakdown": {
    "breaking_changes": {
      "score": 55,
      "details": "18 files import getUserById",
      "affected_modules": ["auth", "profile", "permissions"]
    },
    "security": {
      "score": 15,
      "details": "No security logic changes"
    },
    "performance": {
      "score": 10,
      "details": "Rename only, no performance impact"
    },
    "maintainability": {
      "score": 25,
      "details": "Improves naming clarity"
    },
    "reversibility": {
      "score": 20,
      "details": "Simple git revert"
    }
  },
  "mitigation": [
    "Use IDE refactor tool for safe rename across all files",
    "Add deprecation warning for 1 release cycle",
    "Run full test suite after rename"
  ]
}
```

**Decision Guide:**
- 0-30: ✅ **GO** - Low risk, proceed
- 31-60: ⚠️ **CAUTION** - Moderate risk, follow mitigation
- 61-100: 🛑 **STOP** - High risk, redesign approach

**Time:** < 5 seconds for risk assessment

---

## Documentation Automation

### What You Can Do

✅ **Update README** - Auto-bump version number, update "What's New" section
✅ **Update CHANGELOG** - Add structured entries with workorder tracking
✅ **Update CLAUDE.md** - Version history, workorder IDs, architectural changes
✅ **Generate DELIVERABLES** - Git metrics (LOC, commits, time, contributors)
✅ **Generate Foundation Docs** - ARCHITECTURE.md, SCHEMA.md, API.md, COMPONENTS.md

### Use Cases

**After Feature Completion:**
- One command updates all 3 docs (README, CHANGELOG, CLAUDE.md)
- Auto-detects git changes, calculates version bump
- Captures workorder ID for audit trail

**For Release Notes:**
- CHANGELOG.json provides structured change history
- Filter by version, change type, breaking changes only
- Export to markdown for user-facing release notes

**For New Contributors:**
- Foundation docs generated from actual code
- Real API endpoints, schemas, component structure
- Always up-to-date with implementation

### Example

**Command:**
```bash
/update-docs jwt-authentication 1.1.0
```

**What Happens:**
1. **README.md** - Version badge updated, "What's New" section added
2. **CHANGELOG.json** - New entry with workorder tracking:
   ```json
   {
     "version": "1.1.0",
     "changes": [{
       "type": "feature",
       "title": "Add JWT authentication",
       "workorder_id": "WO-AUTH-SYSTEM-001",
       "files": ["src/auth.py", "tests/test_auth.py"]
     }]
   }
   ```
3. **CLAUDE.md** - Recent Changes section updated with workorder reference

**Time:** < 1 minute for all 3 documents

---

## Feature Lifecycle Management

### What You Can Do

✅ **Complete Lifecycle** - Planning → Execution → Documentation → Archive
✅ **Archive Completed Features** - Move to coderef/archived/ with index
✅ **Features Inventory** - List all active & archived features with status
✅ **Audit Plans** - Health check on all plans (stale, incomplete, broken)
✅ **Recover Archived Features** - Historical reference for similar future features

### Use Cases

**Keep Workspace Clean:**
- Archive completed features to reduce noise
- Active features only in coderef/workorder/
- Search archived features by name, date, workorder ID

**Learn from History:**
- Review similar past features before planning new ones
- Reuse successful implementation patterns
- Avoid repeating past mistakes

**Audit Compliance:**
- Complete audit trail from idea → archive
- Workorder log tracks all features ever created
- DELIVERABLES.md captures exact metrics

### Example

**Archive Feature:**
```bash
/archive-feature jwt-authentication
```

**Output:**
```
✅ Feature archived successfully!

Moved to: coderef/archived/jwt-authentication/
Archive index updated with:
- Workorder ID: WO-AUTH-SYSTEM-001
- Completion date: 2025-12-28
- Status: Complete
- Metrics: 247 LOC, 12 commits, 3.5 hours
```

**Time:** < 1 minute to archive

---

## Quality Assurance

### What You Can Do

✅ **Validate Plans** - Score quality (0-100) with issue breakdown
✅ **Auto-Fix Issues** - Iterative refinement (max 3 iterations)
✅ **Generate Review Reports** - Markdown reports for stakeholder approval
✅ **Detect Plan Drift** - Compare plan vs actual implementation
✅ **Consistency Checks** - Ensure naming conventions, dependencies, test coverage

### Use Cases

**Before Implementation:**
- Validate plan scores >= 90 (recommended threshold)
- Fix critical issues (missing workorder_id, placeholder text, circular dependencies)
- Get stakeholder sign-off with review report

**During Implementation:**
- Update task status to track progress vs plan
- Detect deviation from planned architecture
- Ensure test coverage meets criteria

**After Implementation:**
- Verify all success criteria met
- Audit deliverables match plan estimates
- Check for technical debt introduced

### Example

**Validate:**
```bash
/validate-plan jwt-authentication
```

**Output:**
```json
{
  "score": 75,
  "grade": "C",
  "issues": [
    {
      "severity": "critical",
      "section": "META_DOCUMENTATION",
      "issue": "Missing workorder_id field",
      "fix": "Add workorder_id: WO-AUTH-SYSTEM-001"
    },
    {
      "severity": "major",
      "section": "6_IMPLEMENTATION_PHASES",
      "issue": "Task AUTH-003 has circular dependency",
      "fix": "Remove dependency on AUTH-010 (comes later)"
    }
  ]
}
```

**After Fixes:**
```bash
/validate-plan jwt-authentication
→ Score: 95 ✅ Ready for implementation!
```

**Review Report:**
```bash
/generate-plan-review jwt-authentication
```

**Output:** `coderef/reviews/review-jwt-authentication-20251228.md` with detailed analysis

**Time:** < 1 minute per validation, < 3 iterations to reach 90+

---

## Feature Comparison

### coderef-workflow vs Manual Planning

| Aspect | Manual Planning | coderef-workflow |
|--------|----------------|------------------|
| **Time to Plan** | 2-4 hours | 5-10 minutes |
| **Code Intelligence** | Manual code review | Automated AST analysis |
| **Dependency Awareness** | Guesswork | Complete dependency graph |
| **Risk Assessment** | Subjective | AI-scored (0-100) |
| **Task Breakdown** | 10-20 tasks | 40-60 detailed tasks |
| **Multi-Agent Support** | Manual coordination | Automated conflict prevention |
| **Documentation** | Manual, often incomplete | Automated, always current |
| **Audit Trail** | Git commits only | Workorder IDs + DELIVERABLES |
| **Historical Learning** | Memory | Archived features searchable |

### coderef-workflow vs Other Planning Tools

| Feature | Jira/Linear | GitHub Issues | coderef-workflow |
|---------|-------------|---------------|------------------|
| **Code Intelligence** | ❌ None | ❌ None | ✅ AST-based |
| **AI Planning** | ❌ Manual | ❌ Manual | ✅ Automated |
| **Risk Scoring** | ❌ Manual | ❌ Manual | ✅ AI-powered |
| **Multi-Agent Coordination** | ⚠️ Manual assignment | ⚠️ Manual assignment | ✅ Automated |
| **Git Integration** | ⚠️ Via plugins | ✅ Native | ✅ Native |
| **Documentation Sync** | ❌ Separate | ❌ Separate | ✅ Automatic |
| **Workorder Audit Trail** | ✅ Full history | ⚠️ Issue numbers | ✅ Full history |
| **Plan Validation** | ❌ None | ❌ None | ✅ 0-100 score |

### When to Use coderef-workflow

✅ **Use When:**
- Planning complex features with many dependencies
- Working with AI agents (needs structured context)
- Multi-team or multi-agent parallel work
- Risk assessment before refactoring
- Compliance requires complete audit trail
- Need automated documentation updates

⚠️ **Consider Alternatives When:**
- Simple bug fixes (< 30 minutes work)
- No git repository (coderef-workflow assumes git)
- Team doesn't use MCP protocol
- No Python 3.10+ environment available

---

## Benefits by User Type

### For Individual Developers

✅ Structured planning reduces implementation time
✅ TodoWrite checklist keeps you focused
✅ Risk assessment prevents costly mistakes
✅ Automated documentation (no manual updates)
✅ Archive completed work (clean workspace)

**Time Saved:** 2-4 hours per feature (planning + documentation)

### For Team Leads

✅ Plan validation before implementation approval
✅ Real-time progress visibility across agents
✅ Quality gate with automated checks
✅ Historical data for velocity estimation
✅ Complete audit trail for compliance

**Value:** Reduced rework, faster approvals, better estimates

### For AI Agents

✅ Structured context for autonomous coding
✅ Full dependency awareness (avoid breaking changes)
✅ Multi-agent coordination (parallel work)
✅ Code intelligence (patterns, standards, architecture)
✅ Validation loop (refine until plan scores 90+)

**Capability:** Implement complex features autonomously with high quality

### For Project Managers

✅ Workorder audit trail for compliance
✅ Features inventory (active + archived)
✅ Deliverables metrics (LOC, time, contributors)
✅ Risk assessment reports for stakeholders
✅ Historical data for planning future work

**Insight:** Complete visibility from idea to completion

---

**Documentation Version:** 1.1.0
**Last Updated:** December 28, 2025
**Maintained by:** willh, Claude Code AI
