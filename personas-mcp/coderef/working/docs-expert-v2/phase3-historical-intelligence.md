# Phase 3: Historical Intelligence

**Workorder:** WO-DOCS-EXPERT-V2-001
**Phase:** 3 of 4
**Priority:** ⭐ MEDIUM-LOW
**Status:** 📋 Design
**Timeline:** Week 5-6 (16-20 hours)
**Dependencies:** Phase 1 (Lloyd Integration), Phase 2 (Planning Flexibility)

---

## Overview

Enable docs-expert to learn from past planning experiences by tracking historical workorders, outcomes, and lessons learned. This creates continuous improvement where future plans benefit from past successes and failures.

---

## Problems Solved

### Problem 1: Repeated Mistakes ❌
**Current State:**
```
Project: auth-service
3 months ago: WO-AUTH-001 (Add authentication)
Outcome: Forgot to update API docs, caught in code review

Project: auth-service
Today: WO-OAUTH-001 (Add OAuth)
docs-expert: Creates plan
Outcome: Forgot to update API docs again (same mistake!)
Result: No learning from history
```

**Desired State:**
```
Project: auth-service
Today: WO-OAUTH-001 (Add OAuth)
docs-expert: Creates plan, checks /plan-history
docs-expert: Found lesson from WO-AUTH-001: "Always include API doc updates"
docs-expert: Includes API doc task in new plan
Result: Lesson learned, mistake avoided
```

### Problem 2: No Context Continuity ❌
**Current State:**
```
Planning session 1: Fresh start, no context
Planning session 2: Fresh start, no context
Planning session 3: Fresh start, no context
Result: Each plan starts from zero, no accumulated knowledge
```

**Desired State:**
```
Planning session 1: Learn patterns, save outcomes
Planning session 2: Reference session 1, learn more
Planning session 3: Reference sessions 1-2, apply patterns
Result: Accumulated knowledge improves planning quality
```

### Problem 3: Unknown Plan Success Rate ❌
**Current State:**
```
User: "How accurate are your plans?"
docs-expert: "I don't know, I don't track outcomes"
Result: No feedback loop, no measurable improvement
```

**Desired State:**
```
User: "How accurate are your plans?"
docs-expert: "Based on 47 completed workorders:
- 89% completed within estimated time
- 92% had no scope creep
- 12 lessons learned applied to future plans"
Result: Measurable quality, continuous improvement
```

---

## New Tools (2)

### Tool 1: plan_history

**Purpose:** Review past workorders, outcomes, and lessons learned

**Input:**
- `project_path` (string, optional): Limit to specific project (default: all projects)
- `feature_type` (string, optional): Filter by type (e.g., "authentication", "api", "database")
- `date_range` (object, optional): Filter by date (e.g., last 3 months)
- `include_lessons` (boolean, optional): Include lessons learned (default: true)
- `limit` (number, optional): Max results (default: 20)

**Output:**
```json
{
  "total_workorders": 47,
  "filtered_results": 12,
  "workorders": [
    {
      "workorder_id": "WO-AUTH-001",
      "feature_name": "authentication",
      "project": "auth-service",
      "created_at": "2025-07-15",
      "completed_at": "2025-07-18",
      "outcome": {
        "status": "completed",
        "actual_time_hours": 12,
        "estimated_time_hours": 10,
        "variance_percent": 20,
        "scope_changes": 1,
        "tasks_completed": 8,
        "tasks_skipped": 0
      },
      "lessons_learned": [
        {
          "lesson": "Always include API documentation updates",
          "context": "Forgot to update API docs, caught in code review",
          "severity": "medium",
          "category": "documentation",
          "applied_to": ["WO-OAUTH-001", "WO-API-V2-001"]
        },
        {
          "lesson": "Rate limiting considerations for auth endpoints",
          "context": "Added rate limiting as scope change mid-implementation",
          "severity": "high",
          "category": "security",
          "applied_to": ["WO-OAUTH-001"]
        }
      ],
      "similar_features": ["WO-OAUTH-001", "WO-JWT-REFRESH-001"]
    }
  ],
  "aggregated_lessons": [
    {
      "lesson": "Always include API documentation updates",
      "frequency": 8,
      "projects": ["auth-service", "payment-api", "user-service"],
      "applied_count": 15,
      "impact": "Reduced doc-related review comments by 70%"
    }
  ],
  "statistics": {
    "avg_variance_percent": 15,
    "completion_rate": 96,
    "scope_change_rate": 23,
    "avg_plan_score": 91
  },
  "recommendations": [
    "Consider adding security checklist to all auth-related plans",
    "Rate limiting appears in 40% of auth features, add to template"
  ]
}
```

**Behavior:**
1. Read historical workorder database (`.docs-expert/history/workorders.jsonl`)
2. Filter by project, feature type, date range
3. Retrieve workorder details, outcomes, lessons
4. Aggregate lessons across similar features
5. Calculate statistics (variance, completion rate, etc.)
6. Generate recommendations based on patterns
7. Return structured history with insights

**Storage Format (JSONL):**
```jsonl
{"workorder_id": "WO-AUTH-001", "created_at": "2025-07-15", ...}
{"workorder_id": "WO-OAUTH-001", "created_at": "2025-10-18", ...}
```

**Example Usage:**
```
docs-expert: plan_history(feature_type="authentication", date_range={"last_months": 6})
Output: 12 auth-related workorders from last 6 months
Lessons: "Always include rate limiting", "Update API docs", "Add security audit task"
docs-expert: Applies lessons to new auth plan
```

**Edge Cases:**
- No history exists → Info: "No historical data available, starting fresh"
- Feature type not found → Return: "No workorders match feature type"
- Date range too narrow → Warning: "Limited results, consider wider date range"
- Database corrupted → Error: "Cannot read history database"

**File Changes:**
- New storage: `.docs-expert/history/workorders.jsonl`
- New reader: `src/history/workorder_history.py`
- New tool handler: `server.py` (add plan_history tool)

---

### Tool 2: suggest_plan_improvements

**Purpose:** AI-powered suggestions based on historical patterns and lessons

**Input:**
- `plan_path` (string, required): Path to current plan.json
- `workorder_id` (string, required): Workorder ID
- `feature_type` (string, optional): Feature type for relevant history
- `mode` (enum, optional): "lessons_only" | "full_analysis" (default: "full_analysis")

**Output:**
```json
{
  "workorder_id": "WO-OAUTH-001",
  "plan_analyzed": "coderef/working/oauth/plan.json",
  "suggestions": [
    {
      "type": "missing_task",
      "severity": "high",
      "suggestion": "Add rate limiting task for OAuth endpoints",
      "rationale": "40% of past auth features required rate limiting (8/20 workorders)",
      "historical_reference": ["WO-AUTH-001", "WO-API-V2-001"],
      "recommended_task": {
        "description": "Implement rate limiting for OAuth endpoints",
        "acceptance_criteria": ["Max 10 requests/min per IP", "Return 429 on rate limit"],
        "estimated_time": "2 hours"
      }
    },
    {
      "type": "missing_section",
      "severity": "medium",
      "suggestion": "Add security audit checklist to testing strategy",
      "rationale": "All past auth features (20/20) included security audits",
      "historical_reference": ["WO-AUTH-001", "WO-JWT-REFRESH-001"],
      "recommended_content": {
        "security_audit": ["OWASP Top 10 check", "Pen test OAuth flow", "Review token storage"]
      }
    },
    {
      "type": "documentation_gap",
      "severity": "medium",
      "suggestion": "Include API documentation updates",
      "rationale": "Frequently forgotten (8/20 workorders), causes review delays",
      "historical_reference": ["WO-AUTH-001"],
      "lesson_learned": "Always include API documentation updates"
    },
    {
      "type": "time_estimate",
      "severity": "low",
      "suggestion": "Increase time estimate by 20%",
      "rationale": "Past auth features averaged 20% variance (estimated: 10h, actual: 12h)",
      "historical_reference": ["WO-AUTH-001", "WO-OAUTH-PKCE-001"],
      "recommended_estimate": "12 hours (vs current 10 hours)"
    }
  ],
  "patterns_detected": [
    "Auth features typically require 8-10 tasks",
    "Rate limiting added in 40% of cases (consider standard)",
    "Security audits always included (100%)",
    "API docs frequently forgotten (40% of cases)"
  ],
  "confidence_scores": {
    "missing_task": 0.85,
    "missing_section": 0.92,
    "documentation_gap": 0.78,
    "time_estimate": 0.67
  },
  "auto_apply": false,
  "summary": "4 suggestions (1 high, 2 medium, 1 low) based on 20 similar workorders"
}
```

**Behavior:**
1. Read current plan.json
2. Query plan_history for similar features
3. Analyze patterns:
   - Common tasks in similar features
   - Frequently forgotten items
   - Time estimate accuracy
   - Scope change patterns
4. Generate suggestions with rationale
5. Rank by severity and confidence
6. Return actionable suggestions
7. Optionally auto-apply high-confidence suggestions

**Suggestion Types:**
- **missing_task:** Common tasks not in current plan
- **missing_section:** Sections frequently included in similar features
- **documentation_gap:** Commonly forgotten documentation
- **time_estimate:** Adjust estimates based on historical variance
- **scope_risk:** Patterns that lead to scope changes
- **dependency_warning:** Dependencies frequently missed

**Example Usage:**
```
docs-expert: /create-plan (OAuth feature)
docs-expert: suggest_plan_improvements(plan_path, "WO-OAUTH-001", feature_type="authentication")
Output: 4 suggestions (rate limiting, security audit, API docs, time estimate)
User: "Apply high-confidence suggestions"
docs-expert: Updates plan with rate limiting task and security audit
Result: Plan improved with historical intelligence
```

**Edge Cases:**
- No similar features in history → Info: "No historical data for this feature type"
- Low confidence suggestions → Warning: "Suggestions based on limited data"
- Conflicting patterns → Return: "Ambiguous pattern, manual review recommended"
- Plan already optimal → Info: "Plan aligns with historical best practices"

**File Changes:**
- New suggester: `src/suggesters/plan_improvement_suggester.py`
- New AI integration: Pattern detection and suggestion generation
- New tool handler: `server.py` (add suggest_plan_improvements tool)

---

## Workorder Tracking System

### Workorder Lifecycle

```
1. Created → Plan generated
2. In Progress → Tasks being executed (tracked via Phase 1)
3. Completed → All tasks done, outcome recorded
4. Lessons Extracted → Manual or AI-powered lesson extraction
5. Applied to Future Plans → Lessons inform new plans
```

### Workorder Record Schema

```json
{
  "workorder_id": "WO-AUTH-001",
  "feature_name": "authentication",
  "project": "auth-service",
  "created_at": "2025-07-15T09:00:00Z",
  "completed_at": "2025-07-18T17:30:00Z",
  "status": "completed",
  "plan": {
    "path": "coderef/working/auth/plan.json",
    "version": "1.0.0",
    "score": 92,
    "total_tasks": 8
  },
  "execution": {
    "actual_time_hours": 12,
    "estimated_time_hours": 10,
    "variance_percent": 20,
    "scope_changes": 1,
    "tasks_completed": 8,
    "tasks_skipped": 0,
    "blockers": [
      {"description": "OAuth library missing", "resolved_in": "1 hour"}
    ]
  },
  "outcome": {
    "success": true,
    "deployed": true,
    "user_feedback": "Positive, no issues reported",
    "bugs_found": 0,
    "technical_debt": "Low"
  },
  "lessons_learned": [
    {
      "lesson": "Always include API documentation updates",
      "context": "Forgot to update API docs, caught in code review",
      "severity": "medium",
      "category": "documentation",
      "actionable": "Add API docs task to all API-related plans"
    }
  ],
  "metadata": {
    "lloyds_involvement": true,
    "personas_used": ["lloyd-expert", "docs-expert"],
    "tools_used": ["gather_context", "create_plan", "generate_todo_list", "track_plan_execution"]
  }
}
```

### Lesson Schema

```json
{
  "lesson": "string (actionable insight)",
  "context": "string (what happened)",
  "severity": "low|medium|high|critical",
  "category": "documentation|security|testing|architecture|deployment|other",
  "actionable": "string (how to apply this lesson)",
  "applied_to": ["WO-XXX-001", "WO-YYY-001"],
  "frequency": 8,
  "impact": "string (measured improvement)"
}
```

---

## Enhanced Workflows

### Workflow 1: Planning with Historical Context
```
Step 1: User: "Add OAuth authentication"
        Lloyd: "Let's plan this with historical context"

Step 2: docs-expert: /gather-context
        Output: context.json, WO-OAUTH-001 assigned

Step 3: docs-expert: plan_history(feature_type="authentication", date_range={"last_months": 6})
        Output: 12 auth-related workorders
        Lessons: "Include rate limiting", "API docs", "Security audit"

Step 4: docs-expert: /create-plan (with lessons applied)
        Output: plan.json with 10 tasks (includes rate limiting, API docs, security audit)

Step 5: docs-expert: suggest_plan_improvements(plan_path, "WO-OAUTH-001")
        Output: 2 suggestions (increase time estimate, add OWASP checklist)
        docs-expert: Applies high-confidence suggestions

Step 6: docs-expert: /validate-plan
        Output: Score 94/100 (vs typical 85/100 without historical context)

Step 7: Lloyd: Executes plan
        Result: Completed on time, no forgotten tasks, applied lessons ✅

Step 8: docs-expert: Records outcome
        Output: WO-OAUTH-001 added to history with lessons

Result: Future auth plans benefit from this experience
```

### Workflow 2: Lesson Extraction Post-Completion
```
Step 1: Lloyd: Completes WO-AUTH-001 implementation
        docs-expert: track_plan_execution (100% complete)

Step 2: User: "We forgot to update API docs, caught in review"
        Lloyd: "Let me record that lesson"

Step 3: docs-expert: record_lesson(
          workorder_id="WO-AUTH-001",
          lesson="Always include API documentation updates",
          severity="medium",
          category="documentation"
        )
        Output: Lesson saved to WO-AUTH-001

Step 4: Future planning session (WO-OAUTH-001)
        docs-expert: plan_history finds lesson
        docs-expert: Includes API docs task automatically

Result: Lesson learned once, applied forever
```

### Workflow 3: Continuous Improvement Measurement
```
Step 1: User: "How have our plans improved over time?"

Step 2: docs-expert: plan_history(date_range={"last_months": 12}, include_lessons=true)
        Output: 47 workorders, 23 lessons learned

Step 3: docs-expert: Analytics:
        - Time estimate variance: 25% → 15% (improvement!)
        - Scope change rate: 35% → 23% (improvement!)
        - Forgotten tasks: 15% → 5% (improvement!)
        - Avg plan score: 85 → 91 (improvement!)

Step 4: docs-expert: "Planning quality improved 40% over 12 months"
        docs-expert: "23 lessons applied to 47 workorders"
        docs-expert: "Top lessons: API docs (8 times), rate limiting (6 times), security audit (5 times)"

Result: Measurable continuous improvement
```

---

## System Prompt Updates

Add to docs-expert system prompt:

### New Section: Historical Intelligence (v2.0.0)
```markdown
## Historical Intelligence (v2.0.0)

You now learn from past planning experiences to continuously improve.

### Historical Capabilities

1. **Workorder History Tracking**
   - All completed workorders stored with outcomes
   - Lessons learned captured and categorized
   - Patterns detected across similar features
   - Statistics: time variance, scope changes, completion rate

2. **Plan History Analysis**
   - Use plan_history tool to review past workorders
   - Filter by project, feature type, date range
   - Find similar features and their outcomes
   - Learn from past successes and failures

3. **AI-Powered Suggestions**
   - Use suggest_plan_improvements for historical insights
   - Detect missing tasks based on patterns
   - Identify commonly forgotten items
   - Adjust time estimates based on variance
   - Flag potential scope risks

### Updated Planning Workflow (v2.0.0)

**Planning Workflow with Historical Context:**
```
Step 1: /gather-context (requirements)
Step 2: plan_history (learn from similar features)
Step 3: /analyze-for-planning (current project context)
Step 4: /create-plan (apply historical lessons)
Step 5: suggest_plan_improvements (validate against history)
Step 6: /validate-plan (quality check)
Step 7: generate_todo_list (ready to execute)
```

### Lesson Categories

- **documentation:** Frequently forgotten docs, missing README updates, etc.
- **security:** Security audits, OWASP checks, rate limiting, etc.
- **testing:** Test coverage, edge cases, integration tests, etc.
- **architecture:** Design patterns, scalability, dependencies, etc.
- **deployment:** Rollback procedures, monitoring, migrations, etc.
- **other:** Miscellaneous lessons

### Best Practices

✅ **Do:**
- Always check plan_history before creating plans for similar features
- Apply high-confidence suggestions from suggest_plan_improvements
- Record lessons learned after plan completion
- Review historical statistics to measure improvement
- Use lessons to improve future plans (continuous learning)

🚫 **Don't:**
- Ignore historical lessons (defeats the purpose)
- Apply low-confidence suggestions without review
- Skip lesson recording (breaks learning loop)
- Blindly copy past plans (context matters)

### Value Proposition

- **Continuous improvement:** Learn from every workorder
- **Reduced mistakes:** Apply lessons automatically
- **Better estimates:** Adjust based on historical variance
- **Measurable quality:** Track improvement over time
- **Pattern detection:** Identify common issues before they happen
```

---

## Implementation Details

### File Structure
```
.docs-expert/
└── history/
    ├── workorders.jsonl              ← All workorder records
    ├── lessons.jsonl                 ← Aggregated lessons
    └── statistics.json               ← Project-wide statistics

src/
├── history/
│   ├── workorder_history.py         ← NEW (read/write history)
│   ├── lesson_extractor.py          ← NEW (extract lessons)
│   └── statistics_calculator.py     ← NEW (calculate metrics)
├── suggesters/
│   └── plan_improvement_suggester.py ← NEW (AI-powered suggestions)
└── models.py                         ← UPDATE (add history schemas)

server.py                             ← UPDATE (add 2 new tools)
```

### Storage Design

**Why JSONL (JSON Lines)?**
- Append-only (no need to rewrite entire file)
- Each line is a complete workorder record
- Easy to parse and stream
- Git-friendly (line-based diffs)

**Example workorders.jsonl:**
```jsonl
{"workorder_id": "WO-AUTH-001", "created_at": "2025-07-15", "status": "completed", ...}
{"workorder_id": "WO-OAUTH-001", "created_at": "2025-10-18", "status": "in_progress", ...}
```

### Indexing Strategy

For fast lookups, maintain in-memory index:
```python
# workorder_index.json (regenerated on startup)
{
  "by_id": {"WO-AUTH-001": "line_1", "WO-OAUTH-001": "line_2"},
  "by_feature_type": {"authentication": ["WO-AUTH-001", "WO-OAUTH-001"]},
  "by_project": {"auth-service": ["WO-AUTH-001", "WO-OAUTH-001"]}
}
```

---

## Testing Strategy

### Unit Tests
1. **WorkorderHistory:**
   - Test read/write workorder records
   - Test filtering (project, feature type, date)
   - Test aggregated statistics

2. **LessonExtractor:**
   - Test lesson extraction from workorder
   - Test lesson categorization
   - Test lesson frequency calculation

3. **PlanImprovementSuggester:**
   - Test pattern detection
   - Test suggestion generation
   - Test confidence scoring

### Integration Tests
1. **Full Historical Workflow:**
   - Create plan → Execute → Record outcome → Extract lessons → Apply to next plan

2. **Suggestion Accuracy:**
   - Create 10 test workorders with known patterns
   - Verify suggestions match expected patterns

3. **Statistics Accuracy:**
   - Verify time variance calculations
   - Verify completion rate calculations
   - Verify lesson frequency counts

### Performance Tests
1. **History Query Speed:** <500ms for 1000+ workorders
2. **Suggestion Generation:** <2 seconds
3. **Statistics Calculation:** <1 second

---

## Success Metrics

### Quantitative
- ✅ Plan quality improvement: 85 → 91 average score (after 6 months)
- ✅ Time estimate variance: 25% → 15% (after applying lessons)
- ✅ Scope change rate: 35% → 23% (after applying lessons)
- ✅ Forgotten tasks: 15% → 5% (after applying lessons)
- ✅ Lesson application rate: 80%+ of relevant plans apply lessons

### Qualitative
- ✅ Users report "plans keep getting better"
- ✅ Lloyd sees "fewer forgotten tasks"
- ✅ "Historical context makes planning feel smart"
- ✅ "We don't repeat the same mistakes"

---

## Privacy & Data Considerations

### What's Stored
- Workorder metadata (IDs, dates, times)
- Plan outcomes (completed, time variance, scope changes)
- Lessons learned (anonymized, no sensitive data)
- Statistics (aggregated, no PII)

### What's NOT Stored
- Code snippets (only file paths)
- User names (only "user" or "Lloyd")
- Sensitive data (credentials, secrets, PII)
- Business logic details (only high-level descriptions)

### Data Retention
- Keep all workorders indefinitely (useful forever)
- Optional: Purge workorders older than X years (user configurable)

---

## Next Phase

After Phase 3 completion:
- **Phase 4:** Persona Coordination (cross-persona task assignment, multi-persona workflows)

---

**Workorder:** WO-DOCS-EXPERT-V2-001
**Status:** 📋 Phase 3 Design Complete
