# Multi-Agent Workflow Pattern

**Version:** 1.0.0
**Date:** 2025-10-18
**Status:** Production Pattern (Validated)
**Source:** ast-analyzer-fixes task (communication.json)

---

## Overview

This document defines the **Multi-Agent Workflow Pattern** - a structured collaboration model for decomposing complex tasks into precise, verifiable subtasks executed by specialized agents with clear handoff protocols and comprehensive verification.

**Key Principle:** One agent plans, another executes, original agent verifies.

---

## Pattern Components

### 1. Communication File Structure

**Location:** `coderef/working/{task-name}/communication.json`

**Required Sections:**

```json
{
  "feature": "TASK NAME IN CAPS",
  "from": "Agent 1",
  "to": "Agent 4",
  "date": "YYYY-MM-DD",
  "task": "One-line task summary",

  "instruction": "Single sentence directive",

  "precise_steps": [
    "Step 1: Specific action with file path and line numbers",
    "Step 2: Next action with exact requirements",
    "Step N: Final action with verification"
  ],

  "details": {
    "context": "path/to/context.json",
    "work_area": "specific/directory/",
    "forbidden_files": [
      "file1.ts - DO NOT MODIFY (reason)",
      "file2.ts - DO NOT MODIFY (reason)"
    ],
    "allowed_files": [
      "file1.ts - What to change",
      "file2.ts - What to add"
    ]
  },

  "{task}_implementation": {
    "file": "path/to/file.ts",
    "line": 123,
    "current": "Current state (TODO comment, etc.)",
    "requirements": [
      "Requirement 1 with specifics",
      "Requirement 2 with constraints",
      "Requirement N with acceptance criteria"
    ]
  },

  "testing_checklist": [
    "1. Test step 1",
    "2. Test step 2",
    "3. Verification step"
  ],

  "documentation_requirements": {
    "file": "OUTPUT-FILE.md",
    "sections": [
      "Section 1 - Purpose",
      "Section 2 - Content"
    ]
  },

  "success_criteria": [
    "✅ Criterion 1 - Specific outcome",
    "✅ Criterion 2 - Verification method",
    "✅ Criterion N - Acceptance test"
  ],

  "agent_1_status": "Initial planning complete",
  "agent_4_status": null
}
```

---

## Workflow Phases

### Phase 1: Planning (Agent 1)

**Responsibilities:**
1. Decompose complex task into atomic steps
2. Identify constraints and boundaries
3. Define success criteria
4. Create communication.json
5. Set `agent_1_status`: "Ready for execution"

**Deliverables:**
- ✅ communication.json with all required sections
- ✅ Context file (if needed)
- ✅ Clear forbidden/allowed file boundaries

**Quality Checklist:**
- [ ] Steps are specific (file paths, line numbers)
- [ ] Success criteria are measurable
- [ ] Forbidden files clearly marked
- [ ] Testing checklist comprehensive
- [ ] No ambiguity in requirements

---

### Phase 2: Execution (Agent 4)

**Responsibilities:**
1. Read communication.json
2. Execute each step precisely
3. Respect forbidden file boundaries
4. Run all tests from checklist
5. Create required documentation
6. Update communication.json with completion status

**Execution Protocol:**

```javascript
// 1. Read communication
const comm = readJSON('communication.json');

// 2. Create todo list from precise_steps
createTodoList(comm.precise_steps);

// 3. Execute steps sequentially
for (const step of comm.precise_steps) {
  markInProgress(step);
  executeStep(step);
  verifyStep(step);
  markComplete(step);
}

// 4. Update communication
comm.agent_4_status = "COMPLETE - All tasks executed";
comm.completion_details = {
  timestamp: now(),
  changes_made: [...],
  verification: {...},
  commit: "abc123f"
};
```

**Deliverables:**
- ✅ All implementation files modified as specified
- ✅ All tests passing
- ✅ Documentation created
- ✅ Git commit with clear message
- ✅ communication.json updated with status

**Quality Checklist:**
- [ ] All precise_steps completed
- [ ] All success_criteria met
- [ ] No forbidden files modified (verify with git diff)
- [ ] All tests in checklist passing
- [ ] Documentation includes all required sections
- [ ] Commit message descriptive

---

### Phase 3: Verification (Agent 1)

**Responsibilities:**
1. Review Agent 4's implementation
2. Run independent tests
3. Verify forbidden files unchanged
4. Test integration with broader system
5. Update communication.json with verification

**Verification Protocol:**

```javascript
// 1. Code review
reviewImplementation(comm.changes_made);

// 2. Independent testing
runTests(comm.testing_checklist);

// 3. Verify boundaries
verifyForbiddenFilesUnchanged(comm.forbidden_files);

// 4. Integration testing
testWithProductionSystem();

// 5. Update communication
comm.agent_1_status = "✅ VERIFIED COMPLETE - Details...";
comm.agent_1_verification = {
  test_results: {...},
  boundary_checks: {...},
  verified_by: "Agent 1",
  verified_date: "YYYY-MM-DD"
};
```

**Deliverables:**
- ✅ Independent test results
- ✅ Boundary verification (git diff checks)
- ✅ Integration test results
- ✅ communication.json with final verification
- ✅ Sign-off on task completion

**Quality Checklist:**
- [ ] All Agent 4 changes reviewed
- [ ] Independent tests run and passing
- [ ] Forbidden files verified unchanged (git diff)
- [ ] Production system still works
- [ ] No regressions introduced
- [ ] Documentation accurate

---

## Communication.json Update Pattern

### Agent 4 Update (After Execution)

```json
{
  "agent_4_status": "✅ COMPLETE - All tasks executed successfully",
  "completion_details": {
    "timestamp": "2025-10-18T04:30:00Z",
    "changes_made": [
      "file.ts:266-281 - What was implemented",
      "file2.ts:248-285 - What was added"
    ],
    "verification": {
      "scanner_unchanged": true,
      "cli_unchanged": true,
      "core_builds": true,
      "no_todos_remaining": true
    },
    "commit": "abc123f - Commit message"
  }
}
```

### Agent 1 Update (After Verification)

```json
{
  "agent_1_status": "✅ VERIFIED COMPLETE - Personally tested Agent 4's work. All tests pass.",
  "agent_1_verification": {
    "test_file_1": "✅ All 5 tests pass",
    "test_file_2": "✅ All 5 tests pass",
    "production_system": "✅ Verified with 3 scans",
    "boundary_check_1": "✅ file1.ts unchanged",
    "boundary_check_2": "✅ file2.ts unchanged",
    "integration": "✅ No errors",
    "verified_by": "Agent 1",
    "verified_date": "2025-10-18"
  }
}
```

---

## File Organization Pattern

### Directory Structure

```
coderef/working/{task-name}/
├── communication.json          # Main handoff document
├── context.json               # Additional context (optional)
├── AGENT-BRIEFING.md          # Task background (optional)
└── deliverables/              # Output artifacts (optional)
    ├── implementation/
    ├── tests/
    └── documentation/
```

### Communication File Naming

- **Main:** `communication.json`
- **Backup:** `communication-{version}.json.bak`
- **Template:** `communication-template.json`

---

## Success Criteria Pattern

### Format

```json
"success_criteria": [
  "✅ {Outcome} - {Verification method}",
  "✅ {Feature} implemented and {test method}",
  "✅ {File} unchanged (git diff shows no changes)",
  "✅ {System} still works: {command to verify}"
]
```

### Examples

```json
[
  "✅ loadGraph() implemented and working",
  "✅ test-ast-analyzer.js passes with save/load test",
  "✅ AST-ANALYZER-API.md created with examples",
  "✅ No TODOs remain in packages/core/src/analyzer/",
  "✅ packages/core builds without errors",
  "✅ packages/core/scanner.ts unchanged (git diff shows no changes)",
  "✅ Regex scanner still works: cd packages/cli && pnpm start scan ../core",
  "✅ All changes committed with clear message"
]
```

---

## Precise Steps Pattern

### Format

```
"Step {N}: {Action verb} {specific target} {location} {optional: constraint}"
```

### Examples

```json
[
  "Step 1: Read packages/core/src/analyzer/analyzer-service.ts:266-273",
  "Step 2: Implement loadGraph() to reconstruct DependencyGraph from JSON",
  "Step 3: Add importGraphFromJSON() helper to graph-builder.ts if needed",
  "Step 4: Update test-ast-analyzer.js to test save/load cycle",
  "Step 5: Run test: node test-ast-analyzer.js",
  "Step 6: Create AST-ANALYZER-API.md with usage examples",
  "Step 7: Verify packages/core/scanner.ts unchanged (git diff)",
  "Step 8: Rebuild core: pnpm --filter @coderef/core build",
  "Step 9: Commit: 'Fix AST analyzer loadGraph() and add documentation'"
]
```

### Best Practices

**DO:**
- ✅ Include file paths with line numbers
- ✅ Specify exact commands to run
- ✅ Include verification steps (git diff, tests)
- ✅ Order steps logically (read → implement → test → verify → commit)
- ✅ Use action verbs (Read, Implement, Add, Update, Verify, Commit)

**DON'T:**
- ❌ Use vague language ("update some files")
- ❌ Skip verification steps
- ❌ Omit file paths or line numbers
- ❌ Leave steps open-ended ("figure out how to...")

---

## Forbidden/Allowed Files Pattern

### Forbidden Files

**Purpose:** Protect production code, prevent regressions

**Format:**
```json
"forbidden_files": [
  "path/to/file.ts - DO NOT MODIFY (reason: production code)",
  "path/to/cli.ts - DO NOT MODIFY (reason: working CLI)",
  "path/to/commands/* - DO NOT MODIFY (reason: stable commands)"
]
```

**Verification:**
```bash
# Agent 4 runs before commit
git diff packages/core/scanner.ts  # Should show no changes

# Agent 1 runs during verification
git diff packages/cli/src/cli.ts   # Should show no changes
```

### Allowed Files

**Purpose:** Define scope, prevent scope creep

**Format:**
```json
"allowed_files": [
  "path/to/analyzer-service.ts - Fix loadGraph() method",
  "path/to/graph-builder.ts - Add importGraphFromJSON() helper",
  "test-ast-analyzer.js - Add save/load test",
  "AST-ANALYZER-API.md - Create documentation"
]
```

---

## Testing Checklist Pattern

### Format

```json
"testing_checklist": [
  "1. {Setup step}",
  "2. {Action step}",
  "3. {Verification step}",
  "4. {Assert expected outcome}",
  "5. {Cleanup or final check}"
]
```

### Example

```json
[
  "1. Create small test graph with 3-4 nodes",
  "2. Call analyzer.saveGraph('test.json')",
  "3. Create new AnalyzerService instance",
  "4. Call analyzer.loadGraph('test.json')",
  "5. Verify loaded graph matches original",
  "6. Test query operations on loaded graph",
  "7. Confirm no errors thrown"
]
```

---

## Git Commit Pattern

### Message Format

```
{Action verb} {component} and {additional work}

- Implementation detail 1
- Implementation detail 2
- Test update
- Documentation added

✅ {Key success criterion}
✅ {Boundary verification}
✅ {Build status}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Example

```
Fix AST analyzer loadGraph() and add documentation

- Implement loadGraph() in analyzer-service.ts to reconstruct DependencyGraph from JSON
- Add importGraphFromJSON() helper to graph-builder.ts for graph reconstruction
- Update test-ast-analyzer.js with save/load cycle test
- Add .js extensions to ES module imports for compatibility
- Create comprehensive AST-ANALYZER-API.md documentation

✅ loadGraph() working correctly
✅ No changes to scanner.ts (regex scanner intact)
✅ No changes to cli.ts (production CLI intact)
✅ Core package builds without errors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Agent Responsibilities Matrix

| Responsibility | Agent 1 (Planner) | Agent 4 (Executor) | Agent 1 (Verifier) |
|----------------|-------------------|--------------------|--------------------|
| Task decomposition | ✅ Primary | ❌ | ❌ |
| Create communication.json | ✅ Primary | ❌ | ❌ |
| Execute steps | ❌ | ✅ Primary | ❌ |
| Update code | ❌ | ✅ Primary | ❌ |
| Run tests | ❌ | ✅ Primary | ✅ Secondary |
| Create documentation | ❌ | ✅ Primary | ❌ |
| Verify boundaries | ❌ | ✅ Primary | ✅ Secondary |
| Code review | ❌ | ❌ | ✅ Primary |
| Integration testing | ❌ | ❌ | ✅ Primary |
| Final sign-off | ❌ | ❌ | ✅ Primary |

---

## Quality Gates

### Gate 1: Planning Quality (Before Execution)

**Criteria:**
- [ ] All precise_steps are specific with file paths
- [ ] Success criteria are measurable
- [ ] Forbidden files clearly marked
- [ ] Testing checklist covers all scenarios
- [ ] Documentation requirements defined
- [ ] No ambiguity in instructions

**Reviewer:** Agent 1 self-review or peer review

---

### Gate 2: Execution Quality (Before Verification)

**Criteria:**
- [ ] All precise_steps completed
- [ ] All success_criteria met
- [ ] No forbidden files modified (git diff clean)
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Commit message clear and descriptive
- [ ] communication.json updated

**Reviewer:** Agent 4 self-check

---

### Gate 3: Verification Quality (Before Closure)

**Criteria:**
- [ ] Independent tests run and passing
- [ ] Forbidden files verified unchanged
- [ ] Production system tested
- [ ] No regressions detected
- [ ] Documentation accuracy verified
- [ ] Integration tests passing
- [ ] communication.json fully updated

**Reviewer:** Agent 1

---

## Common Patterns

### Pattern 1: Implementation Task

```json
{
  "feature": "IMPLEMENT {FEATURE NAME}",
  "task": "Implement {specific feature} in {component}",
  "precise_steps": [
    "Step 1: Read {file}:{lines} to understand current state",
    "Step 2: Implement {feature} with {requirements}",
    "Step 3: Add {helper} to {file} if needed",
    "Step 4: Update tests to cover {scenario}",
    "Step 5: Run test: {command}",
    "Step 6: Create {documentation}",
    "Step 7: Verify {boundary file} unchanged",
    "Step 8: Rebuild: {build command}",
    "Step 9: Commit: '{message}'"
  ]
}
```

### Pattern 2: Bug Fix Task

```json
{
  "feature": "FIX {BUG NAME}",
  "task": "Fix {specific bug} in {component}",
  "precise_steps": [
    "Step 1: Reproduce bug with {test case}",
    "Step 2: Read {file}:{lines} to find root cause",
    "Step 3: Fix {issue} in {location}",
    "Step 4: Add regression test for {scenario}",
    "Step 5: Verify fix: {verification method}",
    "Step 6: Verify {boundary file} unchanged",
    "Step 7: Run full test suite",
    "Step 8: Commit: '{message}'"
  ]
}
```

### Pattern 3: Refactoring Task

```json
{
  "feature": "REFACTOR {COMPONENT}",
  "task": "Refactor {component} to {improvement}",
  "precise_steps": [
    "Step 1: Document current behavior with tests",
    "Step 2: Refactor {component} to {new structure}",
    "Step 3: Verify all existing tests still pass",
    "Step 4: Update documentation to reflect changes",
    "Step 5: Run performance benchmarks",
    "Step 6: Verify {boundary files} unchanged",
    "Step 7: Commit: '{message}'"
  ]
}
```

---

## Anti-Patterns (Avoid These)

### ❌ Anti-Pattern 1: Vague Steps

**Bad:**
```json
"precise_steps": [
  "Fix the bug",
  "Update some tests",
  "Make documentation better"
]
```

**Good:**
```json
"precise_steps": [
  "Step 1: Fix null pointer error in analyzer-service.ts:142",
  "Step 2: Add null check test to test-analyzer.js:85-92",
  "Step 3: Update API.md section 3.2 with null handling behavior"
]
```

---

### ❌ Anti-Pattern 2: Missing Verification

**Bad:**
```json
"success_criteria": [
  "Feature implemented",
  "Tests added"
]
```

**Good:**
```json
"success_criteria": [
  "✅ loadGraph() implemented and working",
  "✅ test-ast-analyzer.js passes with save/load test",
  "✅ packages/core builds without errors",
  "✅ scanner.ts unchanged (git diff shows no changes)"
]
```

---

### ❌ Anti-Pattern 3: No Boundaries

**Bad:**
```json
"details": {
  "work_area": "packages/"
}
```

**Good:**
```json
"details": {
  "work_area": "packages/core/src/analyzer/",
  "forbidden_files": [
    "packages/core/scanner.ts - DO NOT MODIFY (production regex scanner)",
    "packages/cli/src/cli.ts - DO NOT MODIFY (production CLI)"
  ],
  "allowed_files": [
    "packages/core/src/analyzer/analyzer-service.ts - Fix loadGraph()"
  ]
}
```

---

### ❌ Anti-Pattern 4: No Agent Updates

**Bad:**
```json
{
  "agent_1_status": "Ready",
  "agent_4_status": null
  // No completion_details or verification
}
```

**Good:**
```json
{
  "agent_1_status": "✅ VERIFIED COMPLETE - All tests pass",
  "agent_4_status": "✅ COMPLETE - All tasks executed",
  "agent_1_verification": {
    "test_results": "✅ All 5 tests pass",
    "verified_by": "Agent 1",
    "verified_date": "2025-10-18"
  },
  "completion_details": {
    "timestamp": "2025-10-18T04:30:00Z",
    "commit": "abc123f"
  }
}
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────┐
│                  AGENT 1 (PLANNER)                  │
│                                                     │
│  1. Analyze complex task                           │
│  2. Decompose into precise steps                   │
│  3. Define boundaries (forbidden/allowed)          │
│  4. Create success criteria                        │
│  5. Write communication.json                       │
│  6. Set agent_1_status = "Ready for execution"    │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ communication.json
                   ▼
┌─────────────────────────────────────────────────────┐
│                  AGENT 4 (EXECUTOR)                 │
│                                                     │
│  1. Read communication.json                        │
│  2. Create todo list from precise_steps           │
│  3. Execute each step                              │
│  4. Respect forbidden file boundaries              │
│  5. Run all tests                                  │
│  6. Create documentation                           │
│  7. Commit changes                                 │
│  8. Update agent_4_status = "COMPLETE"            │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ Updated communication.json
                   ▼
┌─────────────────────────────────────────────────────┐
│               AGENT 1 (VERIFIER)                    │
│                                                     │
│  1. Code review Agent 4's work                     │
│  2. Run independent tests                          │
│  3. Verify forbidden files unchanged (git diff)    │
│  4. Test integration with production               │
│  5. Update agent_1_verification                    │
│  6. Sign off: agent_1_status = "VERIFIED"         │
└─────────────────────────────────────────────────────┘
```

---

## Template: communication.json

```json
{
  "feature": "{FEATURE NAME IN CAPS}",
  "from": "Agent 1",
  "to": "Agent 4",
  "date": "YYYY-MM-DD",
  "task": "{One-line task summary}",

  "instruction": "{Single sentence directive}",

  "precise_steps": [
    "Step 1: {Action} {target} {location}",
    "Step 2: {Action} {target} {location}",
    "Step 3: {Action} {target} {location}",
    "Step N: Commit: '{message}'"
  ],

  "details": {
    "context": "coderef/working/{task-name}/context.json",
    "work_area": "{specific/directory/}",
    "forbidden_files": [
      "{file1.ts} - DO NOT MODIFY ({reason})",
      "{file2.ts} - DO NOT MODIFY ({reason})"
    ],
    "allowed_files": [
      "{file1.ts} - {What to change}",
      "{file2.ts} - {What to add}"
    ]
  },

  "{task}_implementation": {
    "file": "{path/to/file.ts}",
    "line": 123,
    "current": "{Current state}",
    "requirements": [
      "{Requirement 1}",
      "{Requirement 2}"
    ]
  },

  "testing_checklist": [
    "1. {Test step 1}",
    "2. {Test step 2}",
    "3. {Verification step}"
  ],

  "documentation_requirements": {
    "file": "{OUTPUT-FILE.md}",
    "sections": [
      "{Section 1}",
      "{Section 2}"
    ]
  },

  "success_criteria": [
    "✅ {Criterion 1} - {Verification method}",
    "✅ {Criterion 2} - {Test method}",
    "✅ {File} unchanged (git diff shows no changes)",
    "✅ {Command} still works: {verification command}"
  ],

  "agent_1_status": "Ready for Agent 4 execution",
  "agent_4_status": null
}
```

---

## Real-World Example

See: `coderef/working/ast-analyzer-fixes/communication.json`

**Task:** Fix AST analyzer loadGraph() method

**Success Factors:**
- ✅ Precise 10-step execution plan
- ✅ Clear forbidden files (scanner.ts, cli.ts)
- ✅ 9 measurable success criteria
- ✅ Agent 4 executed all steps
- ✅ Agent 1 verified with independent tests
- ✅ Production code protected (git diff verified)
- ✅ Both agents signed off

**Outcome:** Perfect execution, zero regressions, production safe

---

## Adoption Checklist

### For New Tasks

- [ ] Create `coderef/working/{task-name}/` directory
- [ ] Copy `communication-template.json`
- [ ] Fill in all required sections
- [ ] Define precise_steps (minimum 5, maximum 15)
- [ ] Define success_criteria (minimum 5)
- [ ] Mark forbidden files
- [ ] Create testing_checklist
- [ ] Review for ambiguity
- [ ] Hand off to Agent 4

### For Execution

- [ ] Read communication.json fully
- [ ] Create TodoWrite list from precise_steps
- [ ] Execute steps sequentially
- [ ] Mark each step complete
- [ ] Run all tests from checklist
- [ ] Verify forbidden files unchanged (git diff)
- [ ] Update communication.json
- [ ] Commit with clear message

### For Verification

- [ ] Code review all changes
- [ ] Run independent tests
- [ ] Verify git diff on forbidden files
- [ ] Test integration
- [ ] Update agent_1_verification
- [ ] Sign off agent_1_status
- [ ] Archive communication.json

---

## Benefits

### 1. Clear Accountability
- Agent 1 owns planning and verification
- Agent 4 owns execution
- Both sign off on completion

### 2. Production Safety
- Forbidden files protected
- Git diff verification enforced
- Regression prevention built-in

### 3. Traceability
- Every change documented
- Line numbers tracked
- Commit referenced

### 4. Quality Assurance
- Independent verification
- Comprehensive testing
- Multi-agent review

### 5. Knowledge Transfer
- Communication file serves as documentation
- Future agents can understand task history
- Patterns emerge for similar tasks

---

## Version History

- **1.0.0** (2025-10-18): Initial pattern extracted from ast-analyzer-fixes task

---

## References

- Source Task: `coderef/working/ast-analyzer-fixes/communication.json`
- Git Commit: `f617b5f - Fix AST analyzer loadGraph() and add documentation`
- Verification Date: 2025-10-18
- Pattern Validated: ✅ Production-ready

---

**Last Updated:** 2025-10-18
**Pattern Status:** ✅ Validated in Production
**Recommended:** Use for all multi-step tasks requiring agent handoff
