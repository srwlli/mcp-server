# Workorder ID Tracking System - Design Proposal

**Version**: 1.0.0
**Date**: 2025-10-14
**Status**: Proposal
**Author**: AI Assistant + User Feedback

---

## Executive Summary

Propose adding **workorder IDs** as parent identifiers to the existing task ID system in the feature implementation planning standard. This creates a hierarchical task tracking system that enables:

- **Parent-child relationships**: Group related tasks under work orders
- **Multi-feature tracking**: Track sub-features within a larger feature
- **Progress rollup**: Aggregate task completion by work order
- **Cross-phase organization**: Work orders can span multiple implementation phases

---

## Current State: Task ID System

### Current Structure (v1.1.0)

From `feature-implementation-planning-standard.json` (lines 533-674):

```json
{
  "5_task_id_system": {
    "purpose": "Task IDs provide traceability, progress tracking, and clear references",
    "format": "PREFIX-NNN (e.g., SETUP-001, API-002, TEST-003)",

    "universal_prefixes": {
      "SETUP": "Initial setup, scaffolding, configuration, dependencies",
      "DB": "Database schema, migrations, seeds, queries",
      "API": "HTTP endpoints, request/response handling, API contracts",
      "LOGIC": "Business logic, algorithms, data processing, validation",
      "UI": "User interface components, screens, forms, styling",
      "TEST": "Unit tests, integration tests, E2E tests, test data",
      "SEC": "Security implementations, validations, access control",
      "DOC": "Documentation, API specs, user guides, inline comments",
      "DEPLOY": "Deployment scripts, CI/CD, environment configuration",
      "REFACTOR": "Code cleanup, restructuring (for refactoring projects)"
    },

    "numbering_conventions": {
      "sequential": "001, 002, 003 (not 1, 2, 3)",
      "unique": "Each task ID must be unique within the plan",
      "execution_order": "Numbers roughly reflect execution order",
      "gaps_acceptable": "If tasks removed, gaps in sequence are OK"
    }
  }
}
```

### Current Usage Examples

**Example 1: analysis-persistence/plan.json**
```json
{
  "5_task_id_system": {
    "prefix": "AP",
    "description": "Analysis Persistence",
    "tasks": [
      {
        "id": "AP-001",
        "description": "Import datetime module at top of tool_handlers.py"
      },
      {
        "id": "AP-002",
        "description": "Add analysis cache directory creation logic"
      }
      // ... AP-003 through AP-012
    ]
  }
}
```

**Example 2: mcp-http-server/plan.json**
```json
{
  "5_task_id_system": {
    "tasks": [
      "SETUP-001: Initial setup task",
      "LOGIC-001: Core logic task",
      "TEST-001: Testing task",
      "DOC-001: Documentation task"
    ]
  }
}
```

### Current Limitations

1. **Flat hierarchy**: All tasks are at the same level - no grouping mechanism
2. **No parent tracking**: Can't associate related tasks across prefixes
3. **Feature scope blur**: Large features with sub-features lack clear boundaries
4. **Cross-phase tracking**: Hard to track work orders that span multiple phases
5. **Reporting gaps**: Can't generate progress reports by work order

---

## Proposed Enhancement: Workorder IDs

### Concept

Add a **workorder ID** as a **parent identifier** for task groups:

```
WORKORDER-001: User Authentication System
  ├── SETUP-001: Install authentication libraries
  ├── SETUP-002: Create authentication module structure
  ├── DB-001: Create users table migration
  ├── DB-002: Add indexes on email and username
  ├── API-001: Create POST /auth/register endpoint
  ├── API-002: Create POST /auth/login endpoint
  ├── LOGIC-001: Implement password hashing with bcrypt
  ├── LOGIC-002: Implement JWT token generation
  └── TEST-001: Unit tests for password hashing

WORKORDER-002: Session Management
  ├── DB-003: Create sessions table migration
  ├── API-003: Create POST /auth/refresh endpoint
  ├── API-004: Create POST /auth/logout endpoint
  ├── LOGIC-003: Implement token refresh logic
  └── TEST-002: Integration tests for session lifecycle
```

### Format Specification

**Workorder ID Format**: `WORKORDER-NNN` or `WO-NNN`

- **Prefix**: `WORKORDER` (verbose) or `WO` (compact)
- **Number**: Sequential 3-digit number (001, 002, 003)
- **Scope**: Within a single implementation plan
- **Uniqueness**: Each workorder ID unique within plan

**Task ID Enhancement**: No change to task ID format, but add **parent field**

```json
{
  "id": "API-001",
  "workorder_id": "WO-001",
  "description": "Create POST /auth/register endpoint"
}
```

---

## Detailed Design

### Schema Addition to Section 5

**Proposed structure** for `5_task_id_system`:

```json
{
  "5_task_id_system": {
    "purpose": "Task IDs provide traceability, progress tracking, and clear references",
    "format": "PREFIX-NNN (e.g., SETUP-001, API-002, TEST-003)",

    "workorder_tracking": {
      "enabled": true,
      "workorder_id_format": "WO-NNN",
      "purpose": "Group related tasks under parent work orders for hierarchical tracking",
      "when_to_use": [
        "Large features with multiple sub-features (e.g., auth system = login + registration + 2FA)",
        "Cross-cutting concerns spanning multiple phases",
        "Features requiring coordinated work across multiple technical domains",
        "When you need progress rollup by feature area"
      ],
      "when_not_needed": [
        "Simple features with < 10 tasks",
        "Single-domain features (e.g., only UI or only API)",
        "Features where tasks are naturally sequential without grouping"
      ]
    },

    "workorders": [
      {
        "id": "WO-001",
        "name": "User Authentication System",
        "description": "Core authentication functionality including registration and login",
        "scope": "Foundation for all user-related features",
        "tasks": ["SETUP-001", "SETUP-002", "DB-001", "DB-002", "API-001", "API-002", "LOGIC-001", "LOGIC-002", "TEST-001"],
        "phases": ["phase_1_foundation", "phase_2_core_implementation", "phase_4_testing"],
        "completion_criteria": "Users can register and login successfully with password hashing and JWT tokens",
        "dependencies": [],
        "priority": "critical"
      },
      {
        "id": "WO-002",
        "name": "Session Management",
        "description": "Token refresh and logout functionality",
        "scope": "Extends authentication with session lifecycle management",
        "tasks": ["DB-003", "API-003", "API-004", "LOGIC-003", "TEST-002"],
        "phases": ["phase_2_core_implementation", "phase_3_edge_cases", "phase_4_testing"],
        "completion_criteria": "Users can refresh tokens and logout, invalidating sessions",
        "dependencies": ["WO-001"],
        "priority": "high"
      }
    ],

    "universal_prefixes": {
      // ... existing prefix definitions unchanged
    },

    "tasks": [
      {
        "id": "SETUP-001",
        "workorder_id": "WO-001",
        "description": "Install authentication libraries (bcrypt, pyjwt)",
        "phase": "phase_1_foundation"
      },
      {
        "id": "SETUP-002",
        "workorder_id": "WO-001",
        "description": "Create authentication module structure",
        "phase": "phase_1_foundation"
      },
      {
        "id": "DB-001",
        "workorder_id": "WO-001",
        "description": "Create users table migration",
        "phase": "phase_1_foundation"
      }
      // ... etc
    ]
  }
}
```

### Backward Compatibility

**Approach**: Make workorder tracking **optional**

```json
{
  "5_task_id_system": {
    "workorder_tracking": {
      "enabled": false  // Default: false for backward compatibility
    },
    "tasks": [
      // If enabled: false, tasks don't need workorder_id field
      {
        "id": "SETUP-001",
        "description": "Setup task"
      }
    ]
  }
}
```

**Migration path**:
- Existing plans: Add `"workorder_tracking": { "enabled": false }` automatically
- New plans: AI asks if workorder tracking needed based on complexity
- Validation: Only require `workorder_id` field if `enabled: true`

---

## Use Cases

### Use Case 1: Multi-Feature Authentication System

**Scenario**: Building complete authentication with login, registration, 2FA, password reset

**Work Orders**:
- `WO-001`: Core Authentication (login + registration)
- `WO-002`: Two-Factor Authentication
- `WO-003`: Password Reset Flow
- `WO-004`: Session Management

**Benefits**:
- Clear feature boundaries
- Can implement WO-001 first, defer WO-002 and WO-003
- Progress tracking: "Core Auth 100% complete, 2FA 60% complete"

### Use Case 2: Cross-Cutting Security Hardening

**Scenario**: Adding security features across multiple modules

**Work Orders**:
- `WO-001`: Input Validation (spans API, UI, DB)
- `WO-002`: Rate Limiting (spans API, middleware)
- `WO-003`: Audit Logging (spans all layers)

**Benefits**:
- Group security tasks by concern, not by layer
- Track security implementation progress holistically

### Use Case 3: Large Refactoring Project

**Scenario**: Refactoring monolith to microservices

**Work Orders**:
- `WO-001`: Extract User Service
- `WO-002`: Extract Payment Service
- `WO-003`: Extract Notification Service
- `WO-004`: API Gateway Setup
- `WO-005`: Database Migration

**Benefits**:
- Each service extraction is independently trackable
- Can parallelize work orders across team members
- Clear service boundaries

---

## Implementation Impact

### Files to Modify

1. **`mcp-specific-context/feature-implementation-planning-standard.json`**
   - Add `workorder_tracking` section to `5_task_id_system`
   - Add `workorders` array definition
   - Update task structure to include optional `workorder_id` field
   - Add usage guidelines and examples

2. **`generators/plan_validator.py`**
   - Add validation for workorder ID format (`WO-\d{3}`)
   - Validate all `workorder_id` references point to defined work orders
   - Validate workorder dependencies (no circular dependencies)
   - Check completion criteria defined for each work order

3. **`generators/planning_generator.py`**
   - Add workorder generation logic in `create_plan` tool
   - Ask AI if workorder tracking needed based on complexity
   - Generate workorder structure if enabled

4. **`CLAUDE.md`**
   - Document workorder tracking feature
   - Add examples of when to use vs when not to use
   - Update planning workflow examples

5. **`coderef/context/planning-template-for-ai.json`**
   - Add workorder section (AI-optimized template)

### New Features Required

#### 1. Workorder Progress Tracking

```python
def calculate_workorder_progress(plan: dict, workorder_id: str) -> dict:
    """
    Calculate completion percentage for a work order.

    Returns:
    {
        "workorder_id": "WO-001",
        "total_tasks": 9,
        "completed_tasks": 5,
        "in_progress_tasks": 2,
        "pending_tasks": 2,
        "completion_percentage": 55.6,
        "status": "in_progress"
    }
    """
```

#### 2. Workorder Dependency Validation

```python
def validate_workorder_dependencies(workorders: list) -> list[str]:
    """
    Validate workorder dependency graph has no cycles.

    Returns list of validation errors:
    [
        "Circular dependency: WO-001 → WO-002 → WO-001",
        "WO-003 depends on non-existent WO-999"
    ]
    """
```

#### 3. Workorder Rollup Report Generation

Add new MCP tool: `generate_workorder_report`

```python
@app.call_tool()
async def generate_workorder_report(plan_file_path: str) -> dict:
    """
    Generate progress report grouped by work order.

    Returns markdown report with:
    - Overall progress
    - Progress by work order
    - Critical path analysis
    - Blocked work orders (dependencies not met)
    """
```

---

## Validation Requirements

### Workorder Validation Rules

1. **Format validation**: Workorder IDs match `WO-\d{3}` pattern
2. **Uniqueness**: No duplicate workorder IDs within plan
3. **Reference integrity**: All `workorder_id` in tasks reference defined work orders
4. **Dependency validation**: No circular dependencies between work orders
5. **Task coverage**: All tasks assigned to exactly one work order (if tracking enabled)
6. **Completion criteria**: Each work order has defined completion criteria
7. **Phase consistency**: Tasks in work order reference valid phases

### Enhanced Quality Checklist

Add to `QUALITY_CHECKLIST_FOR_PLANS`:

```json
{
  "workorder_tracking": [
    "☐ Workorder tracking enabled only if feature complexity warrants it (>20 tasks or multi-domain)",
    "☐ Each workorder has clear name, description, and completion criteria",
    "☐ All tasks assigned to exactly one workorder (no orphaned tasks)",
    "☐ Workorder dependencies form valid DAG (no cycles)",
    "☐ Workorder scope boundaries are clear and non-overlapping",
    "☐ Critical path work orders identified with priority=critical",
    "☐ Work orders align with phase structure (not conflicting)"
  ]
}
```

---

## Benefits Analysis

### Benefits

1. **Better organization**: Clear feature boundaries in complex plans
2. **Improved tracking**: Progress rollup by work order
3. **Flexible execution**: Can defer or parallelize work orders
4. **Dependency management**: Explicit work order dependencies
5. **Team coordination**: Work orders can be assigned to different team members
6. **Reporting**: Generate progress reports by feature area
7. **Scope control**: Clear boundaries prevent scope creep within work orders

### Costs

1. **Increased complexity**: More structure in task ID system
2. **Validation overhead**: More rules to validate
3. **Planning time**: Additional time to define work orders
4. **Tool complexity**: Tools must handle hierarchical structure
5. **Learning curve**: Users must understand when to use work orders

### When to Use vs Not Use

**Use workorder tracking when**:
- Plan has >20 tasks
- Feature spans multiple technical domains (API + UI + DB + Security)
- Multiple sub-features that could be implemented independently
- Team parallelization needed
- Clear feature boundaries benefit progress tracking

**Don't use workorder tracking when**:
- Simple feature with <10 tasks
- Single-domain feature (e.g., only adding one API endpoint)
- Tasks are naturally sequential without logical grouping
- Overhead of work order structure exceeds benefit

---

## Alternatives Considered

### Alternative 1: Task Prefixes for Grouping

**Approach**: Use task prefixes to indicate work order

```
AUTH-SETUP-001
AUTH-DB-001
AUTH-API-001
SESSION-DB-001
SESSION-API-001
```

**Pros**: No schema changes, simpler

**Cons**:
- Prefix namespace pollution
- Harder to parse and validate
- Doesn't support cross-prefix work orders

**Decision**: Rejected - less flexible than explicit workorder_id field

### Alternative 2: Tags/Labels

**Approach**: Add tags array to tasks

```json
{
  "id": "API-001",
  "tags": ["auth", "core", "critical"]
}
```

**Pros**: Flexible, multi-dimensional grouping

**Cons**:
- No structure (free-form tags)
- Can't define work order metadata (completion criteria, dependencies)
- Harder to validate

**Decision**: Rejected - too unstructured

### Alternative 3: Phase-Based Grouping Only

**Approach**: Use existing phases as grouping mechanism

**Pros**: No new structure needed

**Cons**:
- Phases are time-based, not feature-based
- Can't represent features spanning multiple phases
- Limits flexibility

**Decision**: Rejected - phases serve different purpose (time-based vs feature-based)

---

## Migration Strategy

### For Existing Plans

**Option 1: Automatic migration (conservative)**
```json
{
  "workorder_tracking": {
    "enabled": false  // Keep existing behavior
  }
}
```

**Option 2: Assisted migration**
- AI analyzes existing plan complexity
- If >20 tasks, suggests enabling workorder tracking
- Proposes work order structure based on task prefixes and phases
- User reviews and approves

### For New Plans

**Workflow**:
1. AI analyzes feature description and context
2. If complexity indicators present (>20 tasks, multi-domain), suggests workorder tracking
3. User confirms or declines
4. If enabled, AI generates work order structure based on feature breakdown

**Complexity indicators**:
- Task count estimate >20
- Multiple technical domains (API + UI + DB)
- Multiple sub-features mentioned in context
- Cross-cutting concerns (security, logging)

---

## Recommendations

### Short-term (v1.2.0 - MVP)

1. **Add workorder tracking to planning standard** (optional, disabled by default)
2. **Update plan validator** to support workorder validation
3. **Update documentation** with workorder usage guidelines
4. **Test with 2-3 complex plans** to validate structure

**Scope**: Schema definition + validation only (no reporting tools yet)

**Rationale**: Validate concept before building reporting/tracking tools

### Medium-term (v1.3.0 - Tooling)

1. **Add `generate_workorder_report` MCP tool**
2. **Enhance `/validate-plan` to check workorder quality**
3. **Add workorder progress tracking to plan review reports**
4. **Build workorder dependency graph visualization**

**Scope**: Reporting and analysis tools

### Long-term (v1.4.0 - Advanced Features)

1. **Workorder templates** (reusable patterns for common work orders)
2. **AI-assisted work order generation** (analyze context → propose work orders)
3. **Multi-plan work order tracking** (track work orders across multiple plans)
4. **Workorder-based task assignment** (for team collaboration)

---

## Questions for Discussion

1. **Naming**: Should we use `WORKORDER-NNN` or `WO-NNN`? (Recommend `WO-NNN` for brevity)

2. **Granularity**: Should work orders map 1:1 with phases, or be independent?
   - **Recommendation**: Independent - work orders are feature-based, phases are time-based

3. **Validation strictness**: Should workorder tracking be validated if enabled, or just recommended?
   - **Recommendation**: Strict validation if enabled (prevents broken hierarchies)

4. **Default behavior**: Should complex plans automatically enable workorder tracking?
   - **Recommendation**: Suggest but don't force (let AI + user decide)

5. **Task assignment**: Can a task belong to multiple work orders?
   - **Recommendation**: No - 1:1 relationship (keeps hierarchy simple)

6. **Workorder nesting**: Should work orders support sub-work orders?
   - **Recommendation**: Not initially (defer to v1.4.0 if needed)

---

## Success Criteria

### MVP Success (v1.2.0)

- [ ] Workorder tracking schema defined in planning standard
- [ ] Plan validator supports workorder validation
- [ ] Documentation updated with usage guidelines
- [ ] 3 test plans created with workorder tracking enabled
- [ ] Validation passes for all test plans
- [ ] No breaking changes to existing plans

### Tooling Success (v1.3.0)

- [ ] `generate_workorder_report` MCP tool implemented
- [ ] Workorder progress tracking accurate
- [ ] Dependency validation catches circular dependencies
- [ ] Review reports include workorder-level analysis
- [ ] Users can track feature progress by work order

### Adoption Success (Long-term)

- [ ] >50% of complex plans (>20 tasks) use workorder tracking
- [ ] Users report improved progress visibility
- [ ] Reduced scope creep in large features
- [ ] Team coordination improved with workorder assignment

---

## Appendix: Full Example

### Before (Current System)

```json
{
  "5_task_id_system": {
    "tasks": [
      "SETUP-001: Install authentication libraries",
      "SETUP-002: Create auth module structure",
      "DB-001: Create users table",
      "DB-002: Add indexes",
      "DB-003: Create sessions table",
      "API-001: Create /register endpoint",
      "API-002: Create /login endpoint",
      "API-003: Create /refresh endpoint",
      "API-004: Create /logout endpoint",
      "LOGIC-001: Password hashing",
      "LOGIC-002: JWT generation",
      "LOGIC-003: Token refresh logic",
      "TEST-001: Password tests",
      "TEST-002: Session tests"
    ]
  }
}
```

**Problems**:
- Unclear boundaries between auth and session features
- Can't track "core auth complete, session 60% done"
- Hard to defer session management without manual task filtering

### After (With Workorder Tracking)

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
        "description": "User registration and login with password hashing and JWT tokens",
        "tasks": ["SETUP-001", "SETUP-002", "DB-001", "DB-002", "API-001", "API-002", "LOGIC-001", "LOGIC-002", "TEST-001"],
        "completion_criteria": "Users can register and login, passwords hashed, JWTs issued",
        "dependencies": [],
        "priority": "critical"
      },
      {
        "id": "WO-002",
        "name": "Session Management",
        "description": "Token refresh and logout functionality",
        "tasks": ["DB-003", "API-003", "API-004", "LOGIC-003", "TEST-002"],
        "completion_criteria": "Users can refresh tokens and logout, sessions invalidated",
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
        "id": "SETUP-002",
        "workorder_id": "WO-001",
        "description": "Create auth module structure",
        "phase": "phase_1_foundation"
      },
      {
        "id": "DB-001",
        "workorder_id": "WO-001",
        "description": "Create users table migration",
        "phase": "phase_1_foundation"
      }
      // ... etc
    ]
  }
}
```

**Benefits**:
- Clear feature boundaries
- Progress tracking: "WO-001 100%, WO-002 60%"
- Can defer WO-002 if needed
- Explicit dependency: WO-002 depends on WO-001

---

## Next Steps

1. **Review this proposal** with stakeholders
2. **Decide on MVP scope** (v1.2.0 features)
3. **Update planning standard schema** with workorder structure
4. **Implement validation logic** in plan_validator.py
5. **Create test plans** using workorder tracking
6. **Validate usability** with real-world complex features
7. **Iterate based on feedback**

---

**End of Proposal**
