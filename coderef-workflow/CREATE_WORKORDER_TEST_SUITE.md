# /create-workorder Testing Suite

**Purpose:** Verify the 10-step planning workflow executes correctly, context flows between steps, and workflow documentation is generated accurately.

---

## Test Categories

### A. Step Execution Tests
### B. Context Flow Tests
### C. Documentation Generation Tests
### D. Validation Tests
### E. Multi-Agent Tests
### F. Error Handling Tests
### G. Integration Tests

---

## A. Step Execution Tests

### A1: Step 1 - Get Feature Name
```
Test: Feature name collection
Expected:
  ✓ AskUserQuestion triggered with alphanumeric validation
  ✓ Feature name stored in context
  ✓ Invalid names rejected (special chars except - and _)
  ✓ Name used in all subsequent steps

Verify:
  - feature_name variable contains user input
  - feature_name matches pattern: ^[a-zA-Z0-9_-]+$
  - feature_name used in all file paths
```

### A2: Step 2 - Gather Context
```
Test: Context gathering and storage
Expected:
  ✓ gather_context MCP tool called with feature_name
  ✓ context.json created in coderef/working/{feature_name}/
  ✓ All required fields present: description, goal, requirements, constraints, out_of_scope
  ✓ Requirements stored as array (multi-select)
  ✓ Constraints stored as array

Verify:
  - File exists: coderef/working/{feature_name}/context.json
  - JSON is valid and contains all fields
  - All user inputs present in context.json
```

### A3: Step 3 - Generate Foundation Docs
```
Test: Foundation docs generation
Expected:
  ✓ coderef_foundation_docs MCP tool called
  ✓ ARCHITECTURE.md created
  ✓ SCHEMA.md created
  ✓ project-context.json created
  ✓ COMPONENTS.md created only for UI projects

Verify:
  - Files exist in coderef/foundation-docs/
  - ARCHITECTURE.md contains patterns, decisions, constraints
  - SCHEMA.md contains entity relationships
  - project-context.json is valid JSON with: api_endpoints, database_schema, dependencies, git_activity, code_patterns, similar_features
```

### A4: Step 4 - Analyze Project
```
Test: Project analysis
Expected:
  ✓ analyze_project_for_planning MCP tool called
  ✓ analysis.json created in coderef/working/{feature_name}/
  ✓ Analysis includes: foundation_docs_status, coding_standards, tech_stack, patterns, project_structure, gaps, risks
  ✓ References foundation docs created in step 3

Verify:
  - File exists: coderef/working/{feature_name}/analysis.json
  - JSON contains all expected sections
  - tech_stack from analysis matches foundation docs
  - patterns identified are actionable
```

### A5: Step 5 - Create Plan
```
Test: Plan generation
Expected:
  ✓ create_plan MCP tool called
  ✓ plan.json created in coderef/working/{feature_name}/
  ✓ plan.json contains all 10 sections (or 5 for lightweight)
  ✓ Workorder ID generated and stored in META_DOCUMENTATION
  ✓ DELIVERABLES.md template created
  ✓ plan.json references context.json and analysis.json data

Verify:
  - File exists: coderef/working/{feature_name}/plan.json
  - plan.json is valid JSON
  - All sections present with content (not empty)
  - Workorder ID format: WO-{FEATURE}-{SEQUENCE}
  - Task IDs follow naming convention: PREP-###, IMPL-###, etc.
```

### A6: Step 6 - Multi-Agent Decision
```
Test: Agent mode decision
Expected Single-Agent Mode:
  ✓ AskUserQuestion presented
  ✓ multi_agent = false set in context
  ✓ Skip communication.json generation
  ✓ Proceed to validation

Expected Multi-Agent Mode:
  ✓ AskUserQuestion presented
  ✓ Phase count extracted from plan.json
  ✓ User selects agent count
  ✓ multi_agent = true set in context
  ✓ agent_count stored in context
  ✓ Proceed to generate_agent_communication

Verify:
  - Context variable multi_agent is boolean
  - If multi_agent=true, agent_count is integer >= 1
  - agent_count <= phase_count in plan
```

### A7: Step 7 - Validate Plan
```
Test: Plan validation
Expected:
  ✓ validate_implementation_plan MCP tool called
  ✓ Validation score returned (0-100)
  ✓ Issues identified by severity (critical, major, minor)
  ✓ Approved status determined (>= 90 = pass)
  ✓ Validation result stored in context

Verify:
  - Validation score is numeric 0-100
  - Issues array contains severity field
  - Approved = true if score >= 90, false otherwise
  - Issue descriptions are actionable
```

### A8: Step 8 - Validation Loop
```
Test: Iteration and fix (if needed)
Expected (if score >= 90):
  ✓ Skip loop, proceed to output

Expected (if score < 90):
  ✓ Read plan.json
  ✓ Parse issues by severity (critical first)
  ✓ Apply fixes to plan.json
  ✓ Re-validate with validate_implementation_plan
  ✓ Increment iteration counter
  ✓ Repeat until score >= 90 OR iteration >= 3

Verify:
  - Iteration counter increments correctly
  - Each iteration score improves or stabilizes
  - Max 3 iterations enforced
  - plan.json updated between iterations
  - Final validation score recorded
```

### A9: Step 9 - Output Summary
```
Test: Results presentation
Expected (Single-Agent):
  ✓ Summary shows: feature_name, workorder_id, location
  ✓ Files listed: context.json, analysis.json, plan.json, DELIVERABLES.md
  ✓ Validation score and status displayed
  ✓ Next steps provided (7 steps for execution)

Expected (Multi-Agent):
  ✓ Summary shows: feature_name, workorder_id, location, agent_count
  ✓ communication.json listed in files
  ✓ Next steps mention agent assignment and task tracking
  ✓ Communication.json task tracking explained

Verify:
  - Summary is human-readable
  - All file paths are correct
  - Next steps are sequential and actionable
```

### A10: Step 10 - Commit & Push
```
Test: Git operations
Expected:
  ✓ git add coderef/working/{feature_name}/ executed
  ✓ git commit with descriptive message created
  ✓ Commit message includes: feature_name, workorder_id, validation_score
  ✓ git push executed
  ✓ Pre-execution checkpoint created

Verify:
  - Git log shows new commit
  - Commit message format: "plan({feature_name}): ..."
  - Workorder ID in commit message
  - Validation score in commit message
  - Remote has latest commit
```

---

## B. Context Flow Tests

### B1: Context Persistence
```
Test: Context carries through all steps
Expected:
  ✓ feature_name from Step 1 used in Steps 2-10
  ✓ context.json from Step 2 available to Steps 4-5
  ✓ analysis.json from Step 4 available to Step 5
  ✓ plan.json from Step 5 available to Steps 6-8
  ✓ validation_score from Step 7 used in Steps 8-9

Verify:
  - No context loss between steps
  - Each step uses output from previous steps
  - No hard-coded assumptions about file locations
```

### B2: Context Integration
```
Test: Context data flows into generated files
Expected:
  ✓ context.json data appears in plan.json 1_EXECUTIVE_SUMMARY
  ✓ analysis.json patterns appear in plan.json 3_CURRENT_STATE_ANALYSIS
  ✓ foundation docs data referenced in plan.json 2_RISK_ASSESSMENT
  ✓ project-context.json tech_stack appears in plan.json

Verify:
  - Goal from context.json in plan.json why field
  - Requirements from context.json in plan.json 4_KEY_FEATURES
  - Tech stack from analysis.json in plan.json
  - No duplicate or conflicting information
```

### B3: Multi-Agent Context
```
Test: Agent-specific context passed correctly
Expected (Multi-Agent Mode):
  ✓ communication.json generated with plan context
  ✓ Each agent assigned specific phases/tasks
  ✓ Agent constraints derived from plan.json must_not_break modules
  ✓ Success criteria from plan.json copied to communication.json

Verify:
  - communication.json lists all agents with task_ids
  - Forbidden files per agent are specific and useful
  - Success criteria match plan.json
  - No overlap in task assignments between agents
```

---

## C. Documentation Generation Tests

### C1: Workflow Documentation Accuracy
```
Test: Generated docs match planned workflow
Expected:
  ✓ plan.json 6_IMPLEMENTATION_PHASES match DELIVERABLES.md phases
  ✓ Task IDs in plan.json match DELIVERABLES.md checklist
  ✓ Phase durations in plan.json reflected in DELIVERABLES.md
  ✓ Success criteria in plan.json match DELIVERABLES.md metrics

Verify:
  - DELIVERABLES.md has section for each phase
  - All task IDs from plan.json listed in DELIVERABLES.md
  - Phase descriptions match plan.json
```

### C2: Documentation Completeness
```
Test: All required sections present
Expected:
  ✓ plan.json: META_DOCUMENTATION, EXECUTIVE_SUMMARY, KEY_FEATURES, IMPLEMENTATION_PHASES, SUCCESS_CRITERIA
  ✓ DELIVERABLES.md: Phases, Task Checklist, Metrics section
  ✓ analysis.json: All inventory sections populated
  ✓ context.json: All requirement sections populated

Verify:
  - No empty or null sections
  - No placeholder text (e.g., "TODO", "...")
  - All fields have meaningful content
```

### C3: Documentation Consistency
```
Test: No contradictions between generated docs
Expected:
  ✓ Feature goal same in context.json, plan.json, DELIVERABLES.md
  ✓ Tech stack consistent across analysis.json, foundation docs, plan.json
  ✓ Task IDs unique across all files
  ✓ Dates/timestamps consistent

Verify:
  - Cross-reference docs for consistency
  - No duplicate or conflicting task IDs
  - No contradicting requirements
```

---

## D. Validation Tests

### D1: Validation Rules Enforcement
```
Test: Validation correctly scores plan quality
Expected:
  ✓ Missing sections detected (critical issue)
  ✓ Circular task dependencies detected (critical issue)
  ✓ Duplicate task IDs detected (critical issue)
  ✓ Vague acceptance criteria detected (major issue)
  ✓ Missing task dependencies detected (major issue)
  ✓ Short descriptions detected (minor issue)

Verify:
  - Score penalties applied correctly
  - Critical issues: -10 points each
  - Major issues: -5 points each
  - Minor issues: -1 point each
```

### D2: Validation Pass/Fail
```
Test: Score determines approval
Expected (score >= 90):
  ✓ approved = true
  ✓ Skip validation loop
  ✓ Proceed to output

Expected (score < 90):
  ✓ approved = false
  ✓ Issues listed with severity
  ✓ Enter validation loop

Verify:
  - Pass threshold is consistent (90)
  - Status correctly reflects score
```

### D3: Iteration Improvement
```
Test: Fixes improve validation score
Expected:
  ✓ Issue severity drives fix priority
  ✓ Each iteration resolves at least one critical/major issue
  ✓ Score improves after each fix
  ✓ No infinite loops (max 3 iterations)

Verify:
  - Score increases iteration 1 → 2 → 3
  - Issues list shrinks each iteration
  - Final state (pass or max iterations) documented
```

---

## E. Multi-Agent Tests

### E1: Communication.json Structure
```
Test: Multi-agent coordination file format
Expected:
  ✓ communication.json contains: tasks array, progress summary, agents array
  ✓ tasks array has: id, description, status (pending/in_progress/complete/blocked)
  ✓ progress calculated: complete_count, pending_count, percent_complete
  ✓ agents array lists all agents with task_ids and constraints

Verify:
  - JSON structure matches expected schema
  - All agents represented
  - All tasks from plan.json in tasks array
  - Progress math is correct: percent = complete_count / total_tasks * 100
```

### E2: Agent Constraints
```
Test: Agent-specific constraints properly set
Expected:
  ✓ Each agent has unique task_id list
  ✓ forbidden_files per agent prevents conflicts
  ✓ success_criteria specific to agent's tasks
  ✓ No task assigned to multiple agents

Verify:
  - Task IDs don't overlap between agents
  - Forbidden files are module-specific (e.g., src/auth/ for auth agents)
  - Constraints are restrictive enough to prevent conflicts
```

### E3: Task Status Tracking
```
Test: Agents can update task status
Expected:
  ✓ Initial status for all tasks: pending
  ✓ Agent can set task status: in_progress
  ✓ Agent can set task status: complete with timestamp
  ✓ Agent can set task status: blocked with reason
  ✓ Progress automatically recalculates

Verify:
  - Status transitions are valid
  - Timestamps recorded for completed tasks
  - Progress % updates correctly as tasks complete
```

---

## F. Error Handling Tests

### F1: Invalid Feature Names
```
Test: Feature name validation
Expected:
  ✓ Empty name rejected
  ✓ Special characters rejected (except - and _)
  ✓ Spaces rejected
  ✓ Valid names accepted: "feature-name", "feature_name", "feature123"

Verify:
  - Error message clear and actionable
  - User prompted to retry
```

### F2: Missing Context
```
Test: Handle missing required inputs
Expected:
  ✓ If gather_context fails, error message shown
  ✓ If analysis fails, validation catches it
  ✓ If plan generation fails, clear error message
  ✓ Partial results saved for debugging

Verify:
  - No silent failures
  - Error messages include file path and resolution
```

### F3: Validation Loop Max Iterations
```
Test: Validation loop termination
Expected:
  ✓ After 3 iterations, exit loop regardless of score
  ✓ Final score < 90 shows warning
  ✓ Incomplete plan saved and documented
  ✓ User can run /validate-plan to see details

Verify:
  - Loop doesn't run more than 3 times
  - Final state documented in output
```

### F4: Git Operations Failure
```
Test: Handle git failures gracefully
Expected:
  ✓ If git add fails, error shown
  ✓ If git commit fails, error shown
  ✓ If git push fails, fallback provided
  ✓ Planning artifacts never lost

Verify:
  - Files preserved even if git fails
  - Error message explains issue
  - Next steps clear user can manually git push later
```

---

## G. Integration Tests

### G1: End-to-End Single-Agent
```
Test: Complete workflow with single agent
Setup:
  1. Feature: "user-authentication"
  2. Goal: "Secure user login"
  3. Requirements: [login, logout, password-reset]
  4. Constraints: [must-use-jwt]

Expected:
  ✓ All 10 steps execute in order
  ✓ context.json created with input
  ✓ analysis.json created and populated
  ✓ plan.json created with unambiguous tasks
  ✓ Validation score >= 90
  ✓ Summary shows single-agent next steps
  ✓ Git commit created

Verify:
  - All files exist in coderef/working/user-authentication/
  - plan.json has clear phases and task IDs
  - No circular dependencies in tasks
  - Commit hash in git log
```

### G2: End-to-End Multi-Agent
```
Test: Complete workflow with multiple agents
Setup:
  1. Feature: "payment-processing"
  2. Select: Multi-Agent mode with 3 agents

Expected:
  ✓ All 10 steps execute
  ✓ communication.json generated
  ✓ 3 agents assigned with distinct task_ids
  ✓ Forbidden files prevent conflicts
  ✓ communication.json has task tracking
  ✓ Summary shows multi-agent next steps
  ✓ Git commit created

Verify:
  - communication.json lists 3 agents
  - Each agent has 2-3 tasks
  - No task overlap
  - Progress calculation correct
```

### G3: End-to-End Validation Loop
```
Test: Complete workflow with validation iteration
Setup:
  1. Feature with complex requirements
  2. Expected: Initial validation score < 90

Expected:
  ✓ First validation returns issues
  ✓ Issues fixed automatically or prompt user
  ✓ Re-validate improves score
  ✓ Eventually reach score >= 90 or max iterations
  ✓ Summary reflects final state

Verify:
  - Score improves each iteration
  - Iteration count accurate
  - Final plan is usable
```

---

## Test Execution Script

```bash
#!/bin/bash
# Test runner for /create-workorder

echo "=== CREATE-WORKORDER TEST SUITE ==="
echo ""

# Run each test category
echo "A. Step Execution Tests..."
run_tests A1 A2 A3 A4 A5 A6 A7 A8 A9 A10

echo ""
echo "B. Context Flow Tests..."
run_tests B1 B2 B3

echo ""
echo "C. Documentation Generation Tests..."
run_tests C1 C2 C3

echo ""
echo "D. Validation Tests..."
run_tests D1 D2 D3

echo ""
echo "E. Multi-Agent Tests..."
run_tests E1 E2 E3

echo ""
echo "F. Error Handling Tests..."
run_tests F1 F2 F3 F4

echo ""
echo "G. Integration Tests..."
run_tests G1 G2 G3

echo ""
echo "=== TEST SUITE COMPLETE ==="
```

---

## Success Criteria

The /create-workorder workflow is working correctly when:

✅ All 10 steps execute in sequence without error
✅ Context flows correctly between steps (no data loss)
✅ All generated files contain context-aware content
✅ Documentation is consistent and complete
✅ Validation score reflects plan quality
✅ Validation loop improves scores
✅ Single-agent and multi-agent modes both work
✅ Error handling is graceful
✅ Git operations complete successfully
✅ All integration tests pass

---

**Test Coverage: 37 test cases covering all 10 steps + 3 integration tests**
