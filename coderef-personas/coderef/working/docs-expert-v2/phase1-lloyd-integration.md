# Phase 1: Lloyd Integration

**Workorder:** WO-DOCS-EXPERT-V2-001
**Phase:** 1 of 4
**Priority:** ⭐⭐⭐ HIGH
**Status:** 📋 Design
**Timeline:** Week 1-2 (16-24 hours)

---

## Overview

Integrate docs-expert with Lloyd (AI Project Coordinator) to enable seamless planning-to-execution workflows. This phase addresses the critical gap where plans are disconnected from todos and execution tracking.

---

## Problems Solved

### Problem 1: Manual Todo Conversion ❌
**Current State:**
```
docs-expert: Creates plan with task breakdown
Lloyd: Receives plan JSON
Lloyd: Manually converts tasks → TodoWrite calls
Result: Manual work, error-prone, time-consuming
```

**Desired State:**
```
docs-expert: Creates plan + generates todo list automatically
Lloyd: Receives ready-to-use todo list
Result: Zero manual conversion, instant execution
```

### Problem 2: No Progress Tracking ❌
**Current State:**
```
docs-expert: Creates static plan.json
Lloyd: Tracks todos (in_progress, completed)
docs-expert: Unaware of execution progress
Result: Plan and reality diverge
```

**Desired State:**
```
docs-expert: Creates living plan
Lloyd: Updates todos as work progresses
docs-expert: Syncs plan status with todo status
Result: Real-time visibility into plan execution
```

### Problem 3: Plan-Execution Gap ❌
**Current State:**
```
docs-expert: Generates plan with workorder WO-AUTH-001
Implementation: Tasks completed
docs-expert: Workorder status unknown
Result: No traceability, can't measure success
```

**Desired State:**
```
docs-expert: Generates plan with workorder
Lloyd: Executes with workorder tracking
docs-expert: Reports workorder completion status
Result: Complete traceability from plan → execution
```

---

## New Tools (3)

### Tool 1: generate_todo_list

**Purpose:** Convert plan task breakdown → TodoWrite format automatically

**Input:**
- `plan_path` (string, required): Path to plan.json file
- `workorder_id` (string, required): Workorder ID (e.g., WO-AUTH-001)
- `mode` (enum, optional): "all" | "remaining" (default: "all")

**Output:**
```json
{
  "todos": [
    {
      "content": "Create authentication middleware",
      "activeForm": "Creating authentication middleware",
      "status": "pending",
      "metadata": {
        "workorder_id": "WO-AUTH-001",
        "task_id": 1,
        "plan_section": "implementation",
        "acceptance_criteria": ["Middleware validates JWT", "Returns 401 on invalid token"]
      }
    },
    {
      "content": "Add login endpoint",
      "activeForm": "Adding login endpoint",
      "status": "pending",
      "metadata": {
        "workorder_id": "WO-AUTH-001",
        "task_id": 2,
        "plan_section": "implementation",
        "acceptance_criteria": ["Returns JWT on success", "Rate limited"]
      }
    }
  ],
  "workorder_id": "WO-AUTH-001",
  "total_tasks": 8,
  "summary": "Generated 8 todos from WO-AUTH-001 implementation plan"
}
```

**Behavior:**
1. Read plan.json from coderef/working/{feature}/plan.json
2. Extract task breakdown section
3. Convert each task to todo format:
   - content: Imperative form (e.g., "Create X")
   - activeForm: Present continuous (e.g., "Creating X")
   - status: "pending" (all start pending)
   - metadata: Preserve workorder, task ID, acceptance criteria
4. Return todo list ready for TodoWrite
5. Log: "Generated {N} todos from {workorder_id}"

**Example Usage:**
```
docs-expert: /create-plan → plan.json created
docs-expert: generate_todo_list(plan_path="coderef/working/auth/plan.json", workorder_id="WO-AUTH-001")
Output: 8 todos ready for Lloyd
Lloyd: Receives todo list, starts execution
```

**Edge Cases:**
- Plan has no task breakdown → Error: "No tasks found in plan"
- Invalid plan path → Error: "Plan file not found"
- Malformed plan.json → Error: "Invalid plan format"
- Missing workorder_id → Error: "Workorder ID required"

**File Changes:**
- New generator: `src/generators/todo_list_generator.py`
- New tool handler: `server.py` (add generate_todo_list tool)

---

### Tool 2: track_plan_execution

**Purpose:** Sync plan progress with todo status in real-time

**Input:**
- `plan_path` (string, required): Path to plan.json
- `workorder_id` (string, required): Workorder ID
- `todo_status` (array, required): Current todo statuses from TodoWrite

**Output:**
```json
{
  "workorder_id": "WO-AUTH-001",
  "plan_status": {
    "total_tasks": 8,
    "completed": 5,
    "in_progress": 1,
    "pending": 2,
    "progress_percent": 62.5
  },
  "task_details": [
    {"task_id": 1, "status": "completed", "completed_at": "2025-10-18T10:30:00Z"},
    {"task_id": 2, "status": "completed", "completed_at": "2025-10-18T11:15:00Z"},
    {"task_id": 3, "status": "in_progress", "started_at": "2025-10-18T12:00:00Z"},
    {"task_id": 4, "status": "pending"},
    {"task_id": 5, "status": "pending"}
  ],
  "updated_plan_path": "coderef/working/auth/plan.json",
  "summary": "5/8 tasks completed (62.5%)"
}
```

**Behavior:**
1. Read plan.json
2. Read todo_status array (from TodoWrite state)
3. Match todos → tasks via metadata.task_id
4. Update plan.json with execution status:
   - Add "execution_status" field to each task
   - Add "progress" section to plan metadata
   - Preserve timestamps (started_at, completed_at)
5. Write updated plan.json
6. Return progress summary

**Example Usage:**
```
Lloyd: Updates todo status (task 1 → completed)
Lloyd: Updates todo status (task 2 → in_progress)
docs-expert: track_plan_execution(plan_path, workorder_id, todo_status)
Output: Plan updated, progress 25% (2/8 tasks)
Result: Plan.json reflects reality
```

**Edge Cases:**
- Todo has no task_id → Warning: "Todo not linked to plan task"
- Task completed out of order → OK (flexible ordering)
- Todo status unknown → Error: "Invalid todo status"
- Plan already completed → Info: "Plan 100% complete"

**File Changes:**
- New tracker: `src/trackers/plan_execution_tracker.py`
- Update plan schema: Add execution_status fields
- New tool handler: `server.py` (add track_plan_execution tool)

---

### Tool 3: execute_plan_interactive

**Purpose:** Guided implementation with progress tracking (Lloyd's workflow automation)

**Input:**
- `plan_path` (string, required): Path to plan.json
- `workorder_id` (string, required): Workorder ID
- `mode` (enum, optional): "step-by-step" | "batch" (default: "step-by-step")

**Output:**
```json
{
  "workorder_id": "WO-AUTH-001",
  "mode": "step-by-step",
  "current_task": {
    "task_id": 1,
    "description": "Create authentication middleware",
    "acceptance_criteria": ["Middleware validates JWT", "Returns 401 on invalid token"],
    "file_changes": ["src/middleware/auth.ts"],
    "dependencies": [],
    "estimated_time": "30 minutes"
  },
  "guidance": {
    "what_to_do": "Implement JWT validation middleware in src/middleware/auth.ts",
    "how_to_do_it": "1. Install jsonwebtoken library, 2. Create middleware function, 3. Validate token from Authorization header",
    "acceptance_test": "Middleware returns 401 when token is invalid"
  },
  "progress": {
    "total_tasks": 8,
    "completed": 0,
    "current": 1,
    "remaining": 7,
    "percent": 0
  },
  "actions": {
    "mark_complete": "Call track_plan_execution with task 1 completed",
    "skip": "Move to next task without completing",
    "get_next": "Get next task in sequence"
  }
}
```

**Behavior:**
1. Read plan.json
2. Generate todo list automatically (calls generate_todo_list)
3. Present first task with guidance
4. Wait for task completion (Lloyd marks todo complete)
5. Track progress (calls track_plan_execution)
6. Present next task
7. Repeat until all tasks complete
8. Return final summary

**Modes:**
- **step-by-step:** Present one task at a time (interactive)
- **batch:** Generate all todos, return immediately (Lloyd executes independently)

**Example Usage:**
```
User: "Let's implement the authentication plan"
Lloyd: execute_plan_interactive(plan_path, workorder_id, mode="step-by-step")

docs-expert: "Task 1/8: Create authentication middleware"
docs-expert: "Acceptance criteria: Middleware validates JWT, Returns 401 on invalid token"
docs-expert: "Files to modify: src/middleware/auth.ts"

Lloyd: [Implements task]
Lloyd: "Task 1 complete"

docs-expert: track_plan_execution (1/8 complete)
docs-expert: "Task 2/8: Add login endpoint"
...
```

**Edge Cases:**
- Task blocked by dependencies → Warn: "Dependency X not complete"
- Task fails acceptance criteria → Suggest: "Review criteria, fix issues"
- User cancels mid-execution → Save progress, allow resume
- Plan already started → Resume from last incomplete task

**File Changes:**
- New executor: `src/executors/interactive_plan_executor.py`
- New tool handler: `server.py` (add execute_plan_interactive tool)

---

## Enhanced Workflows

### Workflow 1: Full Planning with Auto-Todos
```
Step 1: User: "Add authentication feature"
        Lloyd: "Let's plan this. Activating docs-expert..."

Step 2: docs-expert: /gather-context
        Output: context.json, WO-AUTH-001 assigned

Step 3: docs-expert: /analyze-for-planning
        Output: analysis.json

Step 4: docs-expert: /create-plan
        Output: plan.json (8 tasks)

Step 5: docs-expert: generate_todo_list(plan_path, "WO-AUTH-001")
        Output: 8 todos ready for execution

Step 6: Lloyd: Receives todo list, begins execution
        Lloyd: TodoWrite([8 todos])
        Lloyd: Marks task 1 as in_progress

Step 7: docs-expert: track_plan_execution
        Output: Plan updated (1/8 in progress, 0% complete)

Step 8: Lloyd: Completes task 1, marks complete
        docs-expert: track_plan_execution
        Output: Plan updated (1/8 complete, 12.5%)

Step 9-16: Repeat for remaining tasks

Step 17: docs-expert: track_plan_execution
         Output: Plan 100% complete, WO-AUTH-001 DONE ✅

Result: Seamless planning → execution → tracking
```

### Workflow 2: Interactive Guided Execution
```
Step 1: User: "Let's implement the authentication plan"
        Lloyd: "I'll guide you through it step by step"

Step 2: Lloyd: execute_plan_interactive(plan_path, "WO-AUTH-001", "step-by-step")

Step 3: docs-expert: "Task 1/8: Create authentication middleware"
        docs-expert: "Files: src/middleware/auth.ts"
        docs-expert: "Criteria: Validates JWT, Returns 401 on invalid"

Step 4: Lloyd: [Implements middleware]
        Lloyd: "Task 1 complete"

Step 5: docs-expert: track_plan_execution (1/8 complete)
        docs-expert: "Task 2/8: Add login endpoint"
        docs-expert: "Files: src/routes/auth.ts"

Step 6: Repeat until all 8 tasks complete

Step 7: docs-expert: "WO-AUTH-001 complete! 8/8 tasks done ✅"

Result: Guided implementation with real-time progress
```

### Workflow 3: Batch Mode (Lloyd's Independence)
```
Step 1: docs-expert: /create-plan → plan.json
Step 2: docs-expert: generate_todo_list → 8 todos
Step 3: Lloyd: Receives todos, executes independently
Step 4: Lloyd: Updates status (1 → in_progress, 1 → complete)
Step 5: docs-expert: track_plan_execution (periodic sync)
Step 6: Lloyd: Completes all tasks
Step 7: docs-expert: Final sync → WO-AUTH-001 DONE ✅

Result: Lloyd works autonomously, plan stays synced
```

---

## System Prompt Updates

Add to docs-expert system prompt:

### New Section: Lloyd Integration
```markdown
## Lloyd Integration (v2.0.0)

You now have seamless integration with Lloyd, the AI Project Coordinator.

### New Capabilities

1. **Automatic Todo Generation**
   - After creating plans, automatically convert tasks → todos
   - Use generate_todo_list tool
   - Lloyd receives ready-to-use todo list

2. **Real-Time Progress Tracking**
   - Track plan execution status as Lloyd completes tasks
   - Use track_plan_execution tool
   - Plans update dynamically (not static files)

3. **Interactive Guided Execution**
   - Guide implementation step-by-step
   - Use execute_plan_interactive tool
   - Present one task at a time with acceptance criteria

### Updated Workflows

**Planning Workflow (v2.0.0):**
```
/gather-context → /analyze-for-planning → /create-plan → generate_todo_list
↓
Lloyd receives todos + executes
↓
track_plan_execution (real-time sync)
↓
Plan reflects reality (living document)
```

**Execution Modes:**
- **Batch Mode:** Generate todos, Lloyd executes independently
- **Interactive Mode:** Guide step-by-step with live feedback

### Best Practices

✅ **Do:**
- Always generate todo list after creating plan
- Track execution progress regularly (every 2-3 completed tasks)
- Use interactive mode for complex features (10+ tasks)
- Use batch mode for simple features (3-5 tasks)
- Preserve workorder IDs in all todos

🚫 **Don't:**
- Create plans without generating todos (breaks Lloyd workflow)
- Forget to track execution (plan becomes stale)
- Mix workorder IDs (breaks traceability)

### Value Proposition

- **Zero manual todo conversion** (was: 5-10 minutes per plan)
- **Real-time plan visibility** (was: static files)
- **Complete traceability** (workorder → plan → todos → completion)
- **Guided execution** (was: figure it out yourself)
```

---

## Implementation Details

### File Structure
```
src/
├── generators/
│   └── todo_list_generator.py      ← NEW
├── trackers/
│   └── plan_execution_tracker.py   ← NEW
├── executors/
│   └── interactive_plan_executor.py ← NEW
└── models.py                        ← UPDATE (add execution status schema)

server.py                            ← UPDATE (add 3 new tools)
```

### Schema Changes

#### Plan Schema (v2.0.0)
```json
{
  "workorder_id": "WO-AUTH-001",
  "sections": [...],
  "task_breakdown": [
    {
      "task_id": 1,
      "description": "Create authentication middleware",
      "acceptance_criteria": [...],
      "execution_status": {          // NEW
        "status": "completed",
        "started_at": "2025-10-18T10:00:00Z",
        "completed_at": "2025-10-18T10:30:00Z",
        "notes": "Implemented JWT validation"
      }
    }
  ],
  "progress": {                      // NEW
    "total_tasks": 8,
    "completed": 5,
    "in_progress": 1,
    "pending": 2,
    "percent": 62.5
  }
}
```

#### Todo Metadata Schema
```json
{
  "content": "Create authentication middleware",
  "activeForm": "Creating authentication middleware",
  "status": "pending",
  "metadata": {                     // NEW
    "workorder_id": "WO-AUTH-001",
    "task_id": 1,
    "plan_section": "implementation",
    "acceptance_criteria": [...]
  }
}
```

### Dependencies
- Existing: PersonaManager, planning workflow tools
- New: TodoWrite integration (read todo status)
- External: File system access (read/write plan.json)

---

## Testing Strategy

### Unit Tests
1. **TodoListGenerator:**
   - Test conversion accuracy (plan task → todo)
   - Test workorder preservation
   - Test edge cases (empty plan, malformed JSON)

2. **PlanExecutionTracker:**
   - Test status synchronization (todo → plan)
   - Test progress calculation
   - Test timestamp handling

3. **InteractivePlanExecutor:**
   - Test task sequencing
   - Test guidance generation
   - Test mode switching (step-by-step vs batch)

### Integration Tests
1. **Full Workflow:**
   - Create plan → Generate todos → Track execution → Complete
   - Verify workorder traceability end-to-end

2. **Lloyd Coordination:**
   - Lloyd creates todos → Lloyd updates status → Plan syncs
   - Verify real-time progress tracking

3. **Edge Cases:**
   - Out-of-order completion
   - Partial completion (some tasks skipped)
   - Plan updates mid-execution

### Manual Testing
1. Create real feature plan (authentication)
2. Generate todo list
3. Simulate Lloyd execution (mark todos complete)
4. Verify plan updates correctly
5. Test interactive mode with live guidance

---

## Success Metrics

### Quantitative
- ✅ Todo generation time: <2 seconds
- ✅ Progress sync time: <1 second
- ✅ Zero manual todo conversion (100% automated)
- ✅ Plan accuracy: 100% match with todo status
- ✅ Workorder traceability: 100% (all tasks linked)

### Qualitative
- ✅ Lloyd reports "seamless workflow"
- ✅ Users see real-time progress
- ✅ Plans remain accurate throughout execution
- ✅ Zero confusion about "what's next?"

---

## Rollout Plan

### Week 1: Implementation
- Day 1-2: Implement TodoListGenerator
- Day 3-4: Implement PlanExecutionTracker
- Day 5-6: Implement InteractivePlanExecutor
- Day 7: Integration and unit testing

### Week 2: Testing & Deployment
- Day 1-2: Integration testing with real plans
- Day 3-4: Lloyd coordination testing
- Day 5: Update system prompt
- Day 6: Update documentation
- Day 7: Deploy to production, monitor usage

---

## Next Phase

After Phase 1 completion:
- **Phase 2:** Planning Flexibility (quick_plan, update_plan)
- **Phase 3:** Historical Intelligence (plan_history)
- **Phase 4:** Persona Coordination (cross-persona task assignment)

---

**Workorder:** WO-DOCS-EXPERT-V2-001
**Status:** 📋 Phase 1 Design Complete
