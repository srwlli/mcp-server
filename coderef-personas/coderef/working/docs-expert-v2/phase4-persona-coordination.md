# Phase 4: Persona Coordination

**Workorder:** WO-DOCS-EXPERT-V2-001
**Phase:** 4 of 4
**Priority:** 🔮 FUTURE
**Status:** 📋 Design
**Timeline:** TBD (after persona stacking implemented)
**Dependencies:** Phase 1-3, Persona Stacking System

---

## Overview

Enable docs-expert to coordinate with other personas (Lloyd, coderef-expert, nfl-scraper-expert, etc.) by assigning tasks to specific personas and tracking cross-persona progress. This creates a true multi-persona ecosystem where docs-expert acts as the planning and coordination hub.

---

## Prerequisites

### Persona Stacking System Must Exist
This phase requires the personas-mcp system to support:
- ✅ `add_persona()` - Stack multiple personas
- ✅ `get_active_personas()` - Get current persona stack
- ✅ Persona composition - Multiple personas active simultaneously
- ✅ Persona communication protocol - Personas can reference each other

**Status:** Not yet implemented (future enhancement to personas-mcp)

### Available Personas (v1.0.0)
1. **lloyd-expert** - Project coordinator + technical leader
2. **docs-expert** - Documentation + planning specialist
3. **coderef-expert** - CodeRef-MCP server building expert
4. **nfl-scraper-expert** - NFL data scraping expert
5. **Future personas** - 20+ planned (see claude-20-personas.md)

---

## Problems Solved

### Problem 1: Generic Task Assignment ❌
**Current State:**
```
docs-expert: Creates plan with 8 tasks
Task 1: "Create authentication middleware" (generic)
Task 2: "Write API documentation" (generic)
Task 3: "Add unit tests" (generic)

Lloyd: Executes all tasks (may not be the best persona for each)
Result: No specialized expertise applied to tasks
```

**Desired State:**
```
docs-expert: Creates plan with 8 tasks
Task 1: "Create authentication middleware" → Assigned to: coderef-expert (code specialist)
Task 2: "Write API documentation" → Assigned to: docs-expert (docs specialist)
Task 3: "Add unit tests" → Assigned to: coderef-expert (testing expert)

Lloyd: Coordinates execution across personas
Result: Right expert for each task
```

### Problem 2: No Cross-Persona Tracking ❌
**Current State:**
```
Lloyd: Tracks todos (all tasks in one list)
docs-expert: Tracks plan (unaware of who does what)
coderef-expert: Executes code tasks (unaware of overall plan)

Result: No visibility into "which persona did what?"
```

**Desired State:**
```
Lloyd: Orchestrates workflow, sees which persona owns which task
docs-expert: Tracks plan with persona assignments
coderef-expert: Sees "my tasks" filtered from overall plan

Result: Clear ownership, coordinated execution
```

### Problem 3: Siloed Personas ❌
**Current State:**
```
User activates: lloyd-expert
User activates: docs-expert (replaces Lloyd)
User activates: coderef-expert (replaces docs-expert)

Result: Only one persona active at a time, no collaboration
```

**Desired State:**
```
User activates: lloyd-expert (coordinator)
User adds: docs-expert (planning)
User adds: coderef-expert (implementation)

Result: All three personas active and collaborating
```

---

## New Capabilities (Persona-Aware)

### Capability 1: Persona-Aware Task Assignment

**Enhanced Task Schema:**
```json
{
  "task_id": 1,
  "description": "Create authentication middleware",
  "assigned_to": "coderef-expert",
  "assignment_rationale": "Code implementation task, best suited for code specialist",
  "dependencies": [],
  "estimated_time": "3 hours",
  "acceptance_criteria": ["Middleware validates JWT", "Returns 401 on invalid token"],
  "status": "pending",
  "completed_by": null,
  "completed_at": null
}
```

**Persona Assignment Logic:**
```python
def assign_task_to_persona(task: Task) -> str:
    """
    Assign task to most appropriate persona based on task type.
    """
    task_type_mapping = {
        "documentation": "docs-expert",
        "code_implementation": "coderef-expert",
        "api_design": "coderef-expert",
        "testing": "coderef-expert",
        "planning": "docs-expert",
        "coordination": "lloyd-expert",
        "nfl_data": "nfl-scraper-expert",
        "database": "coderef-expert",
        "deployment": "lloyd-expert"
    }

    task_type = detect_task_type(task.description)
    return task_type_mapping.get(task_type, "lloyd-expert")  # Default to Lloyd
```

### Capability 2: Persona Progress Tracking

**Multi-Persona Status View:**
```json
{
  "workorder_id": "WO-AUTH-001",
  "total_tasks": 10,
  "persona_breakdown": {
    "lloyd-expert": {
      "assigned_tasks": 2,
      "completed": 2,
      "in_progress": 0,
      "pending": 0,
      "progress_percent": 100
    },
    "docs-expert": {
      "assigned_tasks": 3,
      "completed": 2,
      "in_progress": 1,
      "pending": 0,
      "progress_percent": 67
    },
    "coderef-expert": {
      "assigned_tasks": 5,
      "completed": 3,
      "in_progress": 1,
      "pending": 1,
      "progress_percent": 60
    }
  },
  "overall_progress": 70,
  "blockers": [
    {
      "task_id": 8,
      "assigned_to": "coderef-expert",
      "blocker": "Waiting for docs-expert to finish API docs (task 5)",
      "dependency": "task_5"
    }
  ]
}
```

### Capability 3: Persona Coordination Protocol

**Message Format (Persona-to-Persona):**
```json
{
  "from": "docs-expert",
  "to": "coderef-expert",
  "message_type": "task_assignment",
  "workorder_id": "WO-AUTH-001",
  "content": {
    "task_id": 3,
    "description": "Implement JWT validation middleware",
    "acceptance_criteria": ["Validates JWT from Authorization header", "Returns 401 on invalid"],
    "context": {
      "related_files": ["src/middleware/auth.ts"],
      "dependencies": [],
      "references": ["docs/api.md section 3.2"]
    },
    "deadline": "2025-10-20T17:00:00Z",
    "priority": "high"
  }
}
```

**Response Format:**
```json
{
  "from": "coderef-expert",
  "to": "docs-expert",
  "message_type": "task_completion",
  "workorder_id": "WO-AUTH-001",
  "content": {
    "task_id": 3,
    "status": "completed",
    "completed_at": "2025-10-20T15:30:00Z",
    "deliverables": ["src/middleware/auth.ts", "tests/middleware/auth.test.ts"],
    "notes": "Implemented with jsonwebtoken library, added comprehensive tests",
    "acceptance_criteria_met": [true, true]
  }
}
```

---

## Enhanced Workflows

### Workflow 1: Multi-Persona Feature Implementation
```
Step 1: User: "Add authentication feature with full docs and tests"
        Lloyd: "I'll coordinate this across multiple personas"

Step 2: Lloyd: activate("docs-expert")
        docs-expert: /gather-context → WO-AUTH-001
        docs-expert: /create-plan → 10 tasks

Step 3: docs-expert: assign_tasks_to_personas()
        Task 1-2: Lloyd (setup, coordination)
        Task 3-7: coderef-expert (code, tests)
        Task 8-10: docs-expert (documentation)

Step 4: Lloyd: coordinate_execution()
        Lloyd: "Starting Task 1: Project setup"
        Lloyd: Completes task 1-2

Step 5: Lloyd: handoff_to_persona("coderef-expert", tasks=[3,4,5,6,7])
        coderef-expert: "Received 5 code tasks"
        coderef-expert: Implements tasks 3-7

Step 6: Lloyd: handoff_to_persona("docs-expert", tasks=[8,9,10])
        docs-expert: "Received 3 doc tasks"
        docs-expert: Documents tasks 8-10

Step 7: Lloyd: aggregate_results()
        Lloyd: "All tasks complete across 3 personas"
        Lloyd: "WO-AUTH-001 DONE ✅"

Result: Coordinated multi-persona execution with specialized expertise
```

### Workflow 2: Parallel Persona Execution
```
Step 1: docs-expert: /create-plan → 10 tasks
        docs-expert: assign_tasks_to_personas()
        - Lloyd: Tasks 1-2 (coordination)
        - coderef-expert: Tasks 3-7 (code) [no dependencies on docs]
        - docs-expert: Tasks 8-10 (docs) [no dependencies on code]

Step 2: Lloyd: detect_parallelizable_tasks()
        Lloyd: "Tasks 3-7 and 8-10 can run in parallel"

Step 3: Lloyd: execute_parallel()
        Fork 1: coderef-expert works on tasks 3-7
        Fork 2: docs-expert works on tasks 8-10
        Both run simultaneously

Step 4: Lloyd: wait_for_completion()
        coderef-expert: Completes tasks 3-7 (2 hours)
        docs-expert: Completes tasks 8-10 (1.5 hours)
        Lloyd: Aggregates results

Step 5: Lloyd: "All tasks complete in 2 hours (vs 3.5 hours sequential)"

Result: 75% time savings through parallelization
```

### Workflow 3: Persona Handoffs with Dependency Management
```
Step 1: docs-expert: /create-plan
        Task 5: "Implement API endpoint" (coderef-expert)
        Task 8: "Document API endpoint" (docs-expert, depends on task 5)

Step 2: Lloyd: detect_dependencies()
        Lloyd: "Task 8 depends on task 5"
        Lloyd: "Cannot start task 8 until task 5 complete"

Step 3: Lloyd: assign_to_persona("coderef-expert", task_5)
        coderef-expert: Implements task 5
        coderef-expert: Marks complete

Step 4: Lloyd: check_dependencies(task_8)
        Lloyd: "Task 5 complete, unblocking task 8"
        Lloyd: assign_to_persona("docs-expert", task_8)

Step 5: docs-expert: Documents task 8
        docs-expert: References task 5 deliverables
        docs-expert: Marks complete

Result: Proper dependency management across personas
```

---

## System Prompt Updates

Add to docs-expert system prompt:

### New Section: Persona Coordination (v2.0.0)
```markdown
## Persona Coordination (v2.0.0)

You can now coordinate with other personas for specialized task execution.

### Available Personas

- **lloyd-expert:** Project coordinator, technical leader, progress tracker
- **coderef-expert:** Code implementation, testing, architecture
- **nfl-scraper-expert:** NFL data scraping, sports APIs
- **docs-expert:** You! Documentation, planning, standards

### Task Assignment

When creating plans, assign tasks to appropriate personas:

**Assignment Rules:**
- **Documentation tasks** → docs-expert
- **Code implementation** → coderef-expert
- **Testing** → coderef-expert
- **Coordination/project management** → lloyd-expert
- **NFL data tasks** → nfl-scraper-expert
- **Planning** → docs-expert
- **Ambiguous** → lloyd-expert (default)

**Example:**
```json
{
  "task_id": 3,
  "description": "Implement authentication middleware",
  "assigned_to": "coderef-expert",
  "rationale": "Code implementation task"
}
```

### Coordination Workflow

1. **Create plan with persona assignments**
   - Use /create-plan or /quick-plan
   - Automatically assign tasks to personas
   - Note dependencies between personas

2. **Coordinate execution via Lloyd**
   - Lloyd orchestrates multi-persona workflows
   - Lloyd handles handoffs between personas
   - Lloyd tracks progress per persona

3. **Track cross-persona progress**
   - Use track_plan_execution to see persona breakdown
   - Monitor blockers and dependencies
   - Aggregate results from all personas

### Persona Communication

**Send task to another persona:**
```json
{
  "to": "coderef-expert",
  "task_id": 3,
  "description": "Implement middleware",
  "context": {...},
  "deadline": "2025-10-20"
}
```

**Receive completion notification:**
```json
{
  "from": "coderef-expert",
  "task_id": 3,
  "status": "completed",
  "deliverables": ["src/middleware/auth.ts"]
}
```

### Best Practices

✅ **Do:**
- Assign tasks to personas based on expertise
- Coordinate via Lloyd for complex workflows
- Track persona-specific progress
- Handle dependencies between personas
- Parallelize independent tasks across personas

🚫 **Don't:**
- Assign all tasks to one persona (defeats the purpose)
- Ignore dependencies between personas
- Skip coordination for multi-persona workflows
- Assume personas can see each other's work (explicit handoffs required)

### Value Proposition

- **Specialized expertise:** Right expert for each task
- **Parallel execution:** 50-75% time savings
- **Clear ownership:** Know who does what
- **Coordinated workflows:** Lloyd orchestrates, personas execute
```

---

## Implementation Details

### File Structure
```
src/
├── coordination/
│   ├── persona_assigner.py              ← NEW (assign tasks to personas)
│   ├── persona_communicator.py          ← NEW (persona-to-persona messages)
│   ├── dependency_manager.py            ← NEW (manage task dependencies)
│   └── parallel_executor.py             ← NEW (parallelize tasks)
├── trackers/
│   └── plan_execution_tracker.py        ← UPDATE (add persona tracking)
└── models.py                            ← UPDATE (add persona schemas)

server.py                                ← UPDATE (persona-aware tools)
```

### Schema Changes

#### Persona-Aware Task Schema
```json
{
  "task_id": 1,
  "description": "string",
  "assigned_to": "persona-name",
  "assignment_rationale": "string",
  "dependencies": [2, 3],
  "status": "pending|in_progress|completed",
  "completed_by": "persona-name",
  "completed_at": "timestamp"
}
```

#### Persona Progress Schema
```json
{
  "persona_breakdown": {
    "lloyd-expert": {
      "assigned_tasks": 2,
      "completed": 2,
      "progress_percent": 100
    },
    "coderef-expert": {...}
  }
}
```

---

## Testing Strategy

### Unit Tests
1. **PersonaAssigner:**
   - Test task type detection
   - Test persona assignment logic
   - Test assignment rationale generation

2. **PersonaCommunicator:**
   - Test message formatting (task assignment, completion)
   - Test message routing (from → to)

3. **DependencyManager:**
   - Test dependency detection
   - Test blocking/unblocking logic
   - Test parallel task identification

### Integration Tests
1. **Multi-Persona Workflow:**
   - Create plan → Assign personas → Execute → Track progress

2. **Parallel Execution:**
   - Verify independent tasks run in parallel
   - Verify dependent tasks run sequentially

3. **Persona Handoffs:**
   - Test Lloyd → coderef-expert handoff
   - Test coderef-expert → docs-expert handoff

---

## Success Metrics

### Quantitative
- ✅ Task assignment accuracy: 95%+ correct persona
- ✅ Parallel execution time savings: 50-75%
- ✅ Cross-persona coordination overhead: <10%
- ✅ Dependency resolution accuracy: 100%

### Qualitative
- ✅ Users report "personas work together seamlessly"
- ✅ Lloyd reports "coordinating multiple personas is easy"
- ✅ Specialized expertise applied to each task
- ✅ Clear visibility into who does what

---

## Risks & Mitigations

### Risk 1: Persona Stacking Not Implemented
**Impact:** Phase 4 cannot be built
**Mitigation:** Design Phase 4 now, implement after persona stacking exists
**Timeline:** TBD (depends on personas-mcp roadmap)

### Risk 2: Communication Overhead
**Impact:** Multi-persona workflows slower than single-persona
**Mitigation:** Optimize handoffs, parallelize independent tasks
**Monitoring:** Track coordination overhead, keep <10%

### Risk 3: Incorrect Task Assignment
**Impact:** Wrong persona executes task, suboptimal result
**Mitigation:** Improve task type detection, allow manual override
**Fallback:** Lloyd can reassign tasks mid-execution

---

## Phased Rollout (After Prerequisites Met)

### Phase 4a: Basic Persona Assignment (Week 1-2)
- Implement PersonaAssigner (assign tasks to personas)
- Update plan schema to include assigned_to field
- Test basic assignment logic

### Phase 4b: Progress Tracking (Week 3-4)
- Update PlanExecutionTracker to track per-persona progress
- Add persona breakdown to status views
- Test multi-persona progress tracking

### Phase 4c: Coordination Protocol (Week 5-6)
- Implement PersonaCommunicator (message passing)
- Implement DependencyManager (dependencies between personas)
- Test persona handoffs and communication

### Phase 4d: Parallel Execution (Week 7-8)
- Implement ParallelExecutor (run independent tasks in parallel)
- Optimize coordination overhead
- Test parallel workflows end-to-end

---

## Future Enhancements (Beyond v2.0.0)

### Enhancement 1: Persona Specialization Learning
- Track which personas excel at which task types
- Adapt assignment logic based on historical success
- Measure persona performance (time, quality)

### Enhancement 2: Dynamic Persona Selection
- Auto-discover available personas
- Suggest best persona for ambiguous tasks
- Allow custom persona assignment rules

### Enhancement 3: Persona Negotiation
- Personas can negotiate task assignments
- "I'm busy, can X handle this instead?"
- Load balancing across personas

### Enhancement 4: Persona Expertise Expansion
- Personas learn from completed tasks
- Build expertise profiles over time
- Recommend personas for new task types

---

## Dependencies on personas-mcp Roadmap

This phase requires:
1. ✅ Persona stacking implementation (`add_persona`, `get_active_personas`)
2. ✅ Persona composition (multiple personas active simultaneously)
3. ✅ Persona communication protocol (personas can reference each other)
4. ✅ Persona metadata (expertise areas, capabilities)

**Status:** Not yet implemented (future work for personas-mcp)

**Recommendation:** Document Phase 4 design now, implement after persona stacking exists

---

## Conclusion

Phase 4 represents the future vision of docs-expert: not just a planning specialist, but a **coordination hub** for the entire persona ecosystem. When persona stacking is implemented, docs-expert will orchestrate multi-persona workflows with specialized expertise applied to each task.

**Next Steps:**
1. Complete Phases 1-3 (can be done now)
2. Monitor personas-mcp roadmap for persona stacking
3. Implement Phase 4 when prerequisites are met

---

**Workorder:** WO-DOCS-EXPERT-V2-001
**Status:** 📋 Phase 4 Design Complete (Future Implementation)
