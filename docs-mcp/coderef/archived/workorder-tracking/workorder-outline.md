# Workorder ID System - Outline

## Concept

Add **parent IDs** (workorder IDs) to group related tasks in implementation plans.

## Current State

**Flat structure:**
```
SETUP-001, SETUP-002
API-001, API-002
DB-001, DB-002
TEST-001, TEST-002
```

## Proposed Structure

**Hierarchical with workorders:**
```
WO-001: Core Authentication
  ├── SETUP-001: Install auth libraries
  ├── DB-001: Create users table
  ├── API-001: Create /register endpoint
  └── TEST-001: Unit tests

WO-002: Session Management
  ├── DB-002: Create sessions table
  ├── API-002: Create /refresh endpoint
  └── TEST-002: Session tests
```

## Format

- **Workorder ID**: `WO-NNN` (e.g., WO-001, WO-002)
- **Task Reference**: Tasks include `workorder_id` field
- **Optional**: Disabled by default for backward compatibility

## When to Use

✅ Use when:
- Plan has >20 tasks
- Multiple sub-features within larger feature
- Cross-cutting concerns spanning multiple phases
- Need progress tracking by feature area

❌ Don't use when:
- Simple features (<10 tasks)
- Single-domain features
- Tasks naturally sequential

## How Workorders Embed in Planning

Workorders integrate into the **existing 10-section planning structure** (sections 0-9):

### Section 5: Task ID System (Primary Location)

**Before (current):**
```json
{
  "5_task_id_system": {
    "tasks": [
      "SETUP-001: Install auth libraries",
      "DB-001: Create users table",
      "API-001: Create /register endpoint",
      "API-002: Create /login endpoint",
      "TEST-001: Unit tests for auth"
    ]
  }
}
```

**After (with workorders):**
```json
{
  "5_task_id_system": {
    "workorder_tracking": {
      "enabled": true,
      "workorder_id_format": "WO-NNN"
    },

    "workorders": [
      {
        "id": "WO-001",
        "name": "Core Authentication",
        "description": "User registration and login with password hashing",
        "scope": "Foundation authentication functionality",
        "tasks": ["SETUP-001", "DB-001", "API-001", "TEST-001"],
        "phases": ["phase_1_foundation", "phase_2_core_implementation"],
        "completion_criteria": "Users can register and login with hashed passwords",
        "dependencies": [],
        "priority": "critical"
      },
      {
        "id": "WO-002",
        "name": "Session Management",
        "description": "Token refresh and logout",
        "scope": "Session lifecycle management",
        "tasks": ["API-002", "LOGIC-001", "TEST-002"],
        "phases": ["phase_2_core_implementation", "phase_3_edge_cases"],
        "completion_criteria": "Users can refresh tokens and logout",
        "dependencies": ["WO-001"],
        "priority": "high"
      }
    ],

    "tasks": [
      {
        "id": "SETUP-001",
        "workorder_id": "WO-001",
        "description": "Install authentication libraries (bcrypt, pyjwt)",
        "phase": "phase_1_foundation"
      },
      {
        "id": "DB-001",
        "workorder_id": "WO-001",
        "description": "Create users table migration",
        "phase": "phase_1_foundation"
      },
      {
        "id": "API-001",
        "workorder_id": "WO-001",
        "description": "Create POST /auth/register endpoint",
        "phase": "phase_2_core_implementation"
      },
      {
        "id": "API-002",
        "workorder_id": "WO-002",
        "description": "Create POST /auth/refresh endpoint",
        "phase": "phase_2_core_implementation"
      },
      {
        "id": "TEST-001",
        "workorder_id": "WO-001",
        "description": "Unit tests for password hashing",
        "phase": "phase_4_testing"
      },
      {
        "id": "LOGIC-001",
        "workorder_id": "WO-002",
        "description": "Implement token refresh logic",
        "phase": "phase_2_core_implementation"
      },
      {
        "id": "TEST-002",
        "workorder_id": "WO-002",
        "description": "Integration tests for session lifecycle",
        "phase": "phase_4_testing"
      }
    ]
  }
}
```

### Section 6: Implementation Phases (Cross-Reference)

Phases can reference workorders to show which features are implemented in each phase:

```json
{
  "6_implementation_phases": {
    "phase_1_foundation": {
      "title": "Foundation Setup",
      "purpose": "Setup infrastructure and scaffolding",
      "tasks": ["SETUP-001", "DB-001"],
      "workorders_active": ["WO-001"],
      "completion_criteria": "All files exist, dependencies installed, users table created"
    },
    "phase_2_core_implementation": {
      "title": "Core Implementation",
      "purpose": "Implement primary features",
      "tasks": ["API-001", "API-002", "LOGIC-001"],
      "workorders_active": ["WO-001", "WO-002"],
      "completion_criteria": "Core auth and session management endpoints functional"
    },
    "phase_3_edge_cases": {
      "title": "Edge Cases & Security",
      "purpose": "Handle errors and secure implementation",
      "tasks": ["SEC-001", "SEC-002"],
      "workorders_active": ["WO-002"],
      "completion_criteria": "All edge cases handled, security validated"
    },
    "phase_4_testing": {
      "title": "Testing",
      "purpose": "Comprehensive testing",
      "tasks": ["TEST-001", "TEST-002"],
      "workorders_active": ["WO-001", "WO-002"],
      "completion_criteria": "All tests pass, both work orders validated"
    }
  }
}
```

### Section 9: Implementation Checklist (Organized by Workorder)

**Option A: Group by workorder (recommended for complex plans)**
```json
{
  "9_implementation_checklist": {
    "pre_implementation": [
      "☐ Review complete plan",
      "☐ Get stakeholder approval"
    ],

    "WO-001_core_authentication": [
      "☐ SETUP-001: Install authentication libraries",
      "☐ DB-001: Create users table migration",
      "☐ API-001: Create POST /auth/register endpoint",
      "☐ TEST-001: Unit tests for password hashing"
    ],

    "WO-002_session_management": [
      "☐ API-002: Create POST /auth/refresh endpoint",
      "☐ LOGIC-001: Implement token refresh logic",
      "☐ TEST-002: Integration tests for session lifecycle"
    ],

    "finalization": [
      "☐ All work orders completed",
      "☐ All tests passing",
      "☐ Documentation updated"
    ]
  }
}
```

**Option B: Group by phase (traditional, show workorder context)**
```json
{
  "9_implementation_checklist": {
    "phase_1_foundation": [
      "☐ SETUP-001 (WO-001): Install authentication libraries",
      "☐ DB-001 (WO-001): Create users table migration"
    ],

    "phase_2_core_implementation": [
      "☐ API-001 (WO-001): Create POST /auth/register endpoint",
      "☐ API-002 (WO-002): Create POST /auth/refresh endpoint",
      "☐ LOGIC-001 (WO-002): Implement token refresh logic"
    ],

    "phase_4_testing": [
      "☐ TEST-001 (WO-001): Unit tests for password hashing",
      "☐ TEST-002 (WO-002): Integration tests for session lifecycle"
    ]
  }
}
```

## Benefits

- Clear feature boundaries
- Progress tracking by work order
- Can defer/parallelize work orders
- Explicit dependencies between feature groups
- Better organization for complex plans

## MCP Server Integration

### Existing Tools (Enhanced)

**`/create-plan`**
- AI asks: "Enable workorder tracking?" (if >20 tasks detected)
- Generates workorder structure based on feature context
- Auto-assigns tasks to work orders

**`/validate-plan`**
- Validates workorder ID format (`WO-\d{3}`)
- Checks all `workorder_id` references are valid
- Validates workorder dependencies (no circular deps)
- Ensures all tasks assigned to exactly one workorder

**`/generate-plan-review`**
- Includes workorder-level analysis
- Shows progress by work order
- Identifies critical path work orders

### New MCP Tools

**`generate_workorder_report`**
```python
mcp__docs_mcp__generate_workorder_report(
    project_path="C:/path/to/project",
    plan_file_path="coderef/working/auth-system/plan.json"
)
```

Returns:
```json
{
  "overall_progress": {
    "total_workorders": 2,
    "completed": 1,
    "in_progress": 1,
    "percentage": 50
  },
  "workorders": [
    {
      "id": "WO-001",
      "name": "Core Authentication",
      "progress": {
        "total_tasks": 9,
        "completed": 9,
        "percentage": 100
      },
      "status": "complete"
    },
    {
      "id": "WO-002",
      "name": "Session Management",
      "progress": {
        "total_tasks": 5,
        "completed": 3,
        "percentage": 60
      },
      "status": "in_progress",
      "blocked_by": []
    }
  ]
}
```

**`update_workorder_status`**
```python
# Mark work order as complete
mcp__docs_mcp__update_workorder_status(
    project_path="C:/path/to/project",
    plan_file_path="plan.json",
    workorder_id="WO-001",
    status="complete"
)
```

**`get_workorder_tasks`**
```python
# Get all tasks for a specific work order
mcp__docs_mcp__get_workorder_tasks(
    project_path="C:/path/to/project",
    plan_file_path="plan.json",
    workorder_id="WO-001"
)
```

### Workflow Example

**1. Create plan with workorder tracking:**
```bash
/create-plan
# AI detects 25 tasks → suggests workorder tracking
# User: "Yes, enable workorder tracking"
# AI generates plan with WO-001, WO-002, WO-003
```

**2. Validate plan:**
```bash
/validate-plan
# Checks workorder structure
# Validates dependencies: WO-002 depends on WO-001
# Score: 92/100 (approved)
```

**3. During implementation, track progress:**
```python
# Check overall progress
mcp__docs_mcp__generate_workorder_report(...)
# Output: WO-001: 100%, WO-002: 60%, WO-003: 0%
```

**4. Mark work order complete:**
```python
mcp__docs_mcp__update_workorder_status(
    workorder_id="WO-001",
    status="complete"
)
```

**5. Generate final report:**
```bash
/generate-plan-review
# Includes workorder completion summary
# Shows critical path: WO-001 → WO-002 → WO-003
```

### Slash Commands

**New slash commands:**

- `/workorder-report` - Generate workorder progress report
- `/workorder-status <WO-ID>` - Get status of specific work order
- `/workorder-tasks <WO-ID>` - List all tasks in work order

### Integration with TodoWrite

Work orders integrate with Claude Code's TodoWrite tool:

```python
# TodoWrite creates hierarchical todos
TodoWrite([
    {
        "content": "WO-001: Core Authentication",
        "status": "in_progress",
        "activeForm": "Implementing Core Authentication"
    },
    {
        "content": "  ├─ SETUP-001: Install auth libraries",
        "status": "completed",
        "activeForm": "Installing auth libraries"
    },
    {
        "content": "  ├─ DB-001: Create users table",
        "status": "in_progress",
        "activeForm": "Creating users table"
    }
])
```

## Implementation

1. Add schema to `feature-implementation-planning-standard.json`
2. Update `plan_validator.py` for workorder validation
3. Add `generate_workorder_report` tool to `tool_handlers.py`
4. Add `update_workorder_status` tool
5. Add `get_workorder_tasks` tool
6. Create slash commands: `/workorder-report`, `/workorder-status`, `/workorder-tasks`
7. Document in `CLAUDE.md`
8. Update `planning_generator.py` to auto-suggest workorder tracking
