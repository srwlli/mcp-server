# Schema Reference - coderef-workflow

**Generated:** 2025-12-28
**Version:** 1.1.0
**Schema Version:** 1.0.0

---

## Purpose

This document defines all data schemas used in **coderef-workflow** for feature lifecycle management. All schemas are JSON-based and stored as files in the `coderef/workorder/{feature}/` directory structure.

## Overview

coderef-workflow uses **5 primary data schemas**:

1. **context.json** - Feature requirements and constraints
2. **analysis.json** - Project analysis results
3. **plan.json** - 10-section implementation plan
4. **communication.json** - Multi-agent coordination (optional)
5. **workorder-log.txt** - Global workorder audit trail

All schemas follow strict validation rules and are versioned for backward compatibility.

---

## What: Core Schemas

### 1. context.json

Stores feature requirements gathered during the `/create-workorder` workflow.

**Location:** `coderef/workorder/{feature_name}/context.json`

**Schema:**
```json
{
  "feature_name": "string (required) - Alphanumeric with hyphens/underscores",
  "description": "string (required) - What the feature does",
  "goal": "string (required) - Why this feature is needed",
  "requirements": [
    "string (required) - Must-have requirement 1",
    "string - Must-have requirement 2",
    "..."
  ],
  "out_of_scope": [
    "string (optional) - Explicitly excluded feature 1",
    "string - Explicitly excluded feature 2",
    "..."
  ],
  "constraints": [
    "string (optional) - Technical or business constraint 1",
    "string - Technical or business constraint 2",
    "..."
  ],
  "success_criteria": {
    "functional": [
      "string (optional) - Functional success criterion"
    ],
    "quality": [
      "string (optional) - Quality success criterion"
    ],
    "performance": [
      "string (optional) - Performance success criterion"
    ]
  },
  "decisions": {
    "key": "value (optional) - Key decisions made during gathering"
  }
}
```

**Validation Rules:**
- `feature_name`: Must match `/^[a-z0-9_-]+$/` (max 100 chars)
- `requirements`: Minimum 1 item required
- All string fields: Non-empty, trimmed

**Example:**
```json
{
  "feature_name": "dark-mode-toggle",
  "description": "Add theme toggle between light and dark modes",
  "goal": "Improve accessibility and reduce eye strain for users",
  "requirements": [
    "Theme persistence in localStorage",
    "System preference detection (prefers-color-scheme)",
    "Smooth CSS transitions between themes",
    "Accessible keyboard toggle (Alt+T)"
  ],
  "out_of_scope": [
    "Custom color theme builder",
    "Per-component theme overrides"
  ],
  "constraints": [
    "Must not affect existing inline styles",
    "Total bundle size increase < 5KB"
  ]
}
```

---

### 2. analysis.json

Project analysis results from `analyze_project_for_planning` tool.

**Location:** `coderef/workorder/{feature_name}/analysis.json`

**Schema:**
```json
{
  "project_path": "string (required) - Absolute path to project",
  "analysis_date": "string (required) - ISO 8601 timestamp",
  "foundation_docs": {
    "available": ["string - ARCHITECTURE.md", "SCHEMA.md", "..."],
    "missing": ["string - API.md", "..."]
  },
  "coding_standards": [
    "string - Python 3.10+",
    "string - async/await required",
    "..."
  ],
  "tech_stack": {
    "languages": ["Python", "..."],
    "frameworks": ["FastAPI", "MCP", "..."],
    "testing": ["pytest", "pytest-asyncio", "..."],
    "tools": ["ruff", "mypy", "..."]
  },
  "key_patterns": [
    "string - Decorator-based tool handlers",
    "string - Async/await throughout",
    "..."
  ],
  "project_structure": {
    "src/": "string - Description",
    "generators/": "string - Description",
    "..."
  },
  "similar_features": [
    {
      "name": "string - Similar feature name",
      "path": "string - Path to archived feature",
      "relevance": "string - Why it's similar"
    }
  ],
  "gaps_and_risks": [
    "string - Identified gap or risk 1",
    "string - Identified gap or risk 2",
    "..."
  ]
}
```

**Validation Rules:**
- `analysis_date`: Must be valid ISO 8601 timestamp
- `tech_stack`: All arrays must be non-empty
- `project_structure`: At least 1 key-value pair

**Example:**
```json
{
  "project_path": "/workspace/coderef-workflow",
  "analysis_date": "2025-12-28T10:30:00Z",
  "foundation_docs": {
    "available": ["CLAUDE.md", "ARCHITECTURE.md"],
    "missing": ["API.md", "SCHEMA.md"]
  },
  "coding_standards": [
    "Python 3.10+ required",
    "All tools must be async",
    "Type hints required (mypy validation)"
  ],
  "tech_stack": {
    "languages": ["Python"],
    "frameworks": ["MCP", "asyncio"],
    "testing": ["pytest", "pytest-asyncio"],
    "tools": ["ruff", "mypy", "uv"]
  },
  "key_patterns": [
    "MCP tool handlers use @app.call_tool() decorator",
    "All file operations use Path objects",
    "Error handling with try/except and graceful fallbacks"
  ]
}
```

---

### 3. plan.json

Complete 10-section implementation plan.

**Location:** `coderef/workorder/{feature_name}/plan.json`

**Schema:**
```json
{
  "META_DOCUMENTATION": {
    "version": "string (required) - Semantic version (e.g., 1.0.0)",
    "created": "string (required) - ISO 8601 timestamp",
    "workorder_id": "string (required) - WO-{FEATURE}-{CATEGORY}-###",
    "feature_name": "string (required) - Feature name",
    "project": "string (required) - Project name",
    "status": "string (required) - planning|in_progress|complete|blocked",
    "priority": "string (optional) - P0|P1|P2|P3",
    "phase_count": "number (required) - Number of implementation phases",
    "task_count": "number (required) - Total tasks across all phases",
    "multi_agent": "boolean (required) - Whether multi-agent mode enabled",
    "estimated_duration_hours": "string (optional) - Time estimate",
    "generated_by": "string (required) - AI Assistant name",
    "generated_at": "string (required) - ISO 8601 timestamp",
    "has_context": "boolean (required) - Whether context.json exists",
    "has_analysis": "boolean (required) - Whether analysis.json exists"
  },
  "0_PREPARATION": {
    "analysis_date": "string (required) - ISO 8601 date",
    "audit_methodology": "string (required) - How analysis was performed",
    "key_findings": ["string - Finding 1", "..."],
    "audit_results": {
      "files_affected": "number",
      "total_instances_found": "number",
      "..."
    },
    "scope": "string (required) - What's included in this plan",
    "risks_identified": ["string - Risk 1", "..."]
  },
  "1_EXECUTIVE_SUMMARY": {
    "problem": "string (required) - What problem we're solving",
    "solution": "string (required) - How we're solving it",
    "impact": "string (required) - What changes",
    "scope": "string (required) - Boundaries of this work",
    "deliverables": ["string - Deliverable 1", "..."]
  },
  "2_RISK_ASSESSMENT": {
    "breaking_changes": "string|array - Description or list",
    "security": "string|array - Security risks",
    "performance": "string|array - Performance risks",
    "maintainability": "string - Maintainability impact",
    "reversibility": "string - How easy to revert",
    "overall_risk": "string (required) - LOW|MEDIUM|HIGH + justification"
  },
  "3_CURRENT_STATE_ANALYSIS": {
    "current_situation": {
      "key": "value - Current state description"
    },
    "target_situation": {
      "key": "value - Desired end state"
    },
    "critical_integration_points": ["string - Integration point 1", "..."]
  },
  "4_KEY_FEATURES": {
    "feature_1_name": {
      "name": "string (required) - Feature name",
      "description": "string (required) - What it does",
      "affects": ["string - Affected file/module 1", "..."],
      "instances_count": "number (optional) - How many changes",
      "critical": "boolean (optional) - Whether critical",
      "success_criteria": "string (required) - How to verify completion"
    }
  },
  "5_TASK_ID_SYSTEM": {
    "format": "string (required) - Task ID format (e.g., {PHASE}-{NUMBER})",
    "phases": {
      "PHASE_NAME": "string - Description of this phase prefix"
    },
    "example_task": "string (required) - Example task ID with description",
    "task_dependencies": "string (required) - How dependencies work"
  },
  "6_IMPLEMENTATION_PHASES": {
    "phase_1_name": {
      "name": "string (required) - Phase name",
      "duration_hours": "number (required) - Estimated hours",
      "description": "string (required) - What this phase does",
      "tasks": [
        {
          "id": "string (required) - Task ID (e.g., CORE-001)",
          "file": "string (required) - File to modify",
          "line": "number (optional) - Line number",
          "title": "string (required) - Short task description",
          "current": "string (optional) - Current code/state",
          "new": "string (optional) - New code/state",
          "description": "string (required) - Detailed description",
          "effort_hours": "number (required) - Estimated hours for this task",
          "dependencies": ["string - Task IDs this depends on"],
          "verification": "string (required) - How to verify completion"
        }
      ],
      "success_criteria": ["string - Success criterion 1", "..."]
    }
  },
  "7_TESTING_STRATEGY": {
    "unit_tests": {
      "scope": "string (required) - What unit tests cover",
      "approach": "string (required) - How to write unit tests",
      "coverage_target": "string (required) - Target coverage %"
    },
    "integration_tests": {
      "scope": "string (required) - What integration tests cover",
      "approach": "string (required) - How to write integration tests",
      "coverage_target": "string (required) - Target coverage"
    },
    "regression_tests": {
      "scope": "string (optional) - What regression tests cover",
      "approach": "string (optional) - How to run regression tests",
      "coverage_target": "string (optional) - Target coverage"
    },
    "acceptance_criteria": ["string - Criterion 1", "..."]
  },
  "8_SUCCESS_CRITERIA": {
    "functional": ["string - Functional criterion 1", "..."],
    "quality": ["string - Quality criterion 1", "..."],
    "integration": ["string - Integration criterion 1", "..."],
    "verification": ["string - Verification step 1", "..."]
  },
  "9_implementation_checklist": {
    "phase_1_tasks": ["☐ TASK-001: Description", "..."],
    "verification_checklist": ["☐ Compile check", "..."],
    "post_deployment": ["☐ Clear cache", "..."]
  }
}
```

**Validation Rules:**
- `workorder_id`: Must match `/^WO-[A-Z0-9-]+-\d{3}$/`
- `status`: Must start as "planning", not "complete"
- All task IDs in phase_6: Must be unique across entire plan
- `task_dependencies`: Referenced task IDs must exist in plan
- `phase_count`: Must match actual number of phases in section 6
- `task_count`: Must match total tasks across all phases

**Constraints:**
- Circular task dependencies are forbidden
- Task IDs must follow format defined in section 5
- All phases must have at least 1 task

---

### 4. communication.json

Multi-agent coordination file (generated when `multi_agent: true`).

**Location:** `coderef/workorder/{feature_name}/communication.json`

**Schema:**
```json
{
  "feature_name": "string (required)",
  "workorder_id": "string (required) - WO-{FEATURE}-###",
  "agent_count": "number (required) - Number of agents (1-10)",
  "created_at": "string (required) - ISO 8601 timestamp",
  "tasks": [
    {
      "id": "string (required) - Task ID (e.g., STEP-001)",
      "description": "string (required) - What to do",
      "status": "string (required) - pending|in_progress|complete|blocked",
      "assigned_agent": "number|null - Agent number (1-10) or null if unassigned",
      "completed_at": "string|null - ISO 8601 timestamp when completed"
    }
  ],
  "progress": {
    "total": "number (required) - Total tasks",
    "completed": "number (required) - Completed count",
    "in_progress": "number (required) - In progress count",
    "pending": "number (required) - Pending count",
    "blocked": "number (required) - Blocked count",
    "percent": "number (required) - Completion percentage"
  },
  "agents": {
    "agent_1": {
      "workorder_id": "string (required) - WO-{FEATURE}-AGENT-001",
      "status": "string (required) - idle|working|complete|blocked",
      "assigned_phase": "string|null - Phase ID or null",
      "forbidden_files": ["string - File path 1", "..."],
      "success_criteria": ["string - Criterion 1", "..."]
    }
  },
  "coordination": {
    "parallel_phases": ["string - Phase ID 1", "..."],
    "sequential_phases": ["string - Phase ID 1", "..."],
    "conflict_resolution": "string - How to handle conflicts"
  }
}
```

**Validation Rules:**
- `agent_count`: Must be 1-10
- `tasks`: Each task.id must be unique
- `tasks`: task.status transitions must be valid (pending → in_progress → complete)
- `progress`: All counts must sum to `total`
- `progress.percent`: Must be (completed / total) * 100

---

### 5. workorder-log.txt

Global audit trail of all workorders across all projects.

**Location:** `coderef/workorder-log.txt`

**Format:**
```
WO-ID | Project | Description | Timestamp

WO-AUTH-SYSTEM-001 | coderef-workflow | Implement JWT authentication | 2025-12-28T10:30:00Z
WO-DARK-MODE-002 | my-app | Add dark mode toggle | 2025-12-27T14:20:00Z
```

**Schema (per line):**
- Field 1: `workorder_id` (string, WO-{FEATURE}-### format)
- Field 2: `project_name` (string, short identifier)
- Field 3: `description` (string, max 50 chars recommended)
- Field 4: `timestamp` (string, ISO 8601)

**Separator:** ` | ` (space-pipe-space)

**Ordering:** Newest entries at top (prepend, reverse chronological)

**Validation Rules:**
- Entries are append-only (never deleted)
- File uses UTF-8 encoding
- Thread-safe with file locking for concurrent writes

---

## Why: Design Decisions

### JSON Over Database
**Chosen:** File-based JSON schemas
**Rejected:** SQLite or PostgreSQL database

**Reasons:**
- **Version Control:** JSON files tracked in git for complete history
- **Portability:** Works across all platforms without external dependencies
- **Transparency:** Human-readable for debugging and audits
- **Simplicity:** No database setup, migrations, or connection management
- **Backup:** Automatic via git commits

**Trade-offs:**
- No ACID transactions (mitigated by single-file writes)
- No complex queries (mitigated by targeted file reads)
- Manual validation (mitigated by jsonschema library)

### Workorder ID in META
**Chosen:** Store workorder_id in plan.json META_DOCUMENTATION
**Rejected:** Separate workorder.json file

**Reasons:**
- **Single source of truth:** All plan metadata in one file
- **Atomic updates:** No risk of plan/workorder ID mismatch
- **Simpler API:** One file to read for complete plan context

### Status Lifecycle
**Chosen:** planning → in_progress → complete → [archived]
**Rejected:** Single "complete" status

**Reasons:**
- **Progress tracking:** Distinguish between planned vs active vs done
- **Multi-agent coordination:** Know which features are actively being worked on
- **Bug fix:** Previously plans started as "complete" (incorrect)

---

## When: Schema Lifecycle

### Creation Flow
```
1. gather_context() → Creates context.json
2. analyze_project_for_planning() → Creates analysis.json
3. create_plan() → Creates plan.json (status: "planning")
4. [Optional] generate_agent_communication() → Creates communication.json
```

### Update Flow
```
1. execute_plan() → Reads plan.json, generates TodoWrite list
2. update_task_status() → Updates plan.json task status and section 9 checkboxes
3. update_deliverables() → Updates DELIVERABLES.md with git metrics
4. [Multi-agent] Agents update communication.json.tasks as they work
```

### Archival Flow
```
1. archive_feature() → Moves entire coderef/workorder/{feature}/ to coderef/archived/
2. Updates coderef/archived/index.json with archive metadata
```

---

## Examples

### Example 1: Valid plan.json Snippet

```json
{
  "META_DOCUMENTATION": {
    "version": "1.0.0",
    "created": "2025-12-27T00:00:00Z",
    "workorder_id": "WO-EXECUTE-PLAN-RENAME-001",
    "feature_name": "execute-plan-rename",
    "project": "coderef-workflow",
    "status": "planning",
    "phase_count": 3,
    "task_count": 16,
    "multi_agent": false
  },
  "6_IMPLEMENTATION_PHASES": {
    "phase_1_core": {
      "name": "Core Tool Infrastructure",
      "duration_hours": 0.75,
      "description": "Rename MCP tool registration",
      "tasks": [
        {
          "id": "CORE-001",
          "file": "server.py",
          "line": 778,
          "title": "Rename tool registration name",
          "current": "name='execute_plan',",
          "new": "name='align_plan',",
          "description": "Update MCP tool registration",
          "effort_hours": 0.1,
          "dependencies": [],
          "verification": "Tool shows as 'align_plan' in tool list"
        }
      ]
    }
  }
}
```

### Example 2: Task Status Update

**Before:**
```json
{
  "tasks": [
    {"id": "CORE-001", "status": "pending", "completed_at": null}
  ],
  "progress": {"total": 27, "completed": 0, "percent": 0}
}
```

**After (calling update_task_status):**
```json
{
  "tasks": [
    {"id": "CORE-001", "status": "completed", "completed_at": "2025-12-28T10:45:00Z"}
  ],
  "progress": {"total": 27, "completed": 1, "percent": 3.7}
}
```

---

## Relationships

### Schema Dependencies

```
context.json
    ↓ (referenced by)
plan.json
    ↓ (generates)
DELIVERABLES.md
    ↓ (references)
communication.json (if multi_agent: true)

analysis.json
    ↓ (referenced by)
plan.json

workorder-log.txt
    ↓ (tracks)
All workorder_id values across all plans
```

### Foreign Keys (Conceptual)

- `plan.json.META_DOCUMENTATION.workorder_id` → `workorder-log.txt` entry
- `communication.json.workorder_id` → `plan.json.META_DOCUMENTATION.workorder_id`
- `communication.json.tasks[].id` → `plan.json.6_IMPLEMENTATION_PHASES.*.tasks[].id`

---

## Validation

All schemas are validated using Python `jsonschema` library v4.0+.

### Validation Errors

**Example Error Response:**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid plan.json schema",
  "details": {
    "field": "META_DOCUMENTATION.workorder_id",
    "value": "INVALID-ID",
    "expected": "WO-{FEATURE}-{CATEGORY}-###",
    "pattern": "^WO-[A-Z0-9-]+-\\d{3}$"
  }
}
```

### Common Validation Issues

1. **Invalid workorder_id format**
   - Error: "Workorder ID must match WO-{FEATURE}-###"
   - Fix: Use uppercase, hyphens, and 3-digit sequence

2. **Circular task dependencies**
   - Error: "Task IMPL-002 depends on IMPL-003 which depends on IMPL-002"
   - Fix: Remove circular dependency chain

3. **Duplicate task IDs**
   - Error: "Task ID CORE-001 appears twice in plan"
   - Fix: Ensure all task IDs unique across all phases

4. **Status started as 'complete'**
   - Error: "Plan status cannot start as 'complete'"
   - Fix: Use 'planning' status for new plans

---

## Versioning

**Current Schema Version:** 1.0.0

### Version History

- **1.0.0** (2025-12-25) - Initial schema with workorder_id tracking
- **0.9.0** (2025-12-24) - Pre-workorder schemas (legacy)

### Breaking Changes

When introducing breaking schema changes:
1. Increment major version (e.g., 1.0.0 → 2.0.0)
2. Provide migration guide in CHANGELOG
3. Support old format for 1 minor version (backward compatibility)

---

## References

- **API.md** - Tools that create/update these schemas
- **ARCHITECTURE.md** - How schemas fit into system design
- **CLAUDE.md** - Complete AI context documentation
- **JSON Schema Spec** - https://json-schema.org/

---

**For AI agents:** All data in coderef-workflow is stored as JSON files following these schemas. Always validate inputs before writing. Use `update_task_status` tool to update plan.json safely. Never modify archived features in `coderef/archived/`.
