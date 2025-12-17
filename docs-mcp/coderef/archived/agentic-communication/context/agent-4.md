Multi-Agent Workflow Pattern - Complete Model

  Core Principle

  One agent plans, another executes, original agent verifies.

  ---
  3-Phase Workflow

  Phase 1: Planning (Agent 1)

  Creates: communication.json with:

  1. Feature identification - CAPS task name
  2. Precise steps (5-15 steps) - File paths + line numbers + exact actions
  3. Boundaries - Forbidden files (DO NOT MODIFY) vs Allowed files
  4. Success criteria (5+ criteria) - Measurable outcomes with verification methods
  5. Testing checklist - Step-by-step validation
  6. Documentation requirements - What docs to create

  Example Precise Step:
  "Step 2: Implement loadGraph() to reconstruct DependencyGraph from JSON"

  Quality Check:
  - ✅ All steps have file paths/line numbers
  - ✅ Success criteria are measurable
  - ✅ Forbidden files clearly marked
  - ✅ No ambiguity

  ---
  Phase 2: Execution (Agent 4)

  Process:

  1. Read communication.json
  2. Create TodoWrite list from precise_steps
  3. Execute each step sequentially
  4. Respect forbidden file boundaries
  5. Run all tests from checklist
  6. Create documentation
  7. Verify forbidden files unchanged: git diff
  8. Commit with descriptive message
  9. Update communication.json:

  "agent_4_status": "✅ COMPLETE - All tasks executed",
  "completion_details": {
    "timestamp": "2025-10-18T04:30:00Z",
    "changes_made": [
      "file.ts:266-281 - What was implemented"
    ],
    "verification": {
      "scanner_unchanged": true,
      "core_builds": true
    },
    "commit": "abc123f - Message"
  }

  Quality Check:
  - ✅ All precise_steps completed
  - ✅ All success_criteria met
  - ✅ git diff shows no forbidden file changes
  - ✅ All tests passing
  - ✅ Documentation complete

  ---
  Phase 3: Verification (Agent 1)

  Process:

  1. Code review Agent 4's changes
  2. Run independent tests
  3. Verify forbidden files: git diff {file} = no changes
  4. Test integration with production system
  5. Update communication.json:

  "agent_1_status": "✅ VERIFIED COMPLETE - All tests pass",
  "agent_1_verification": {
    "test_file_1": "✅ All 5 tests pass",
    "boundary_check_1": "✅ scanner.ts unchanged",
    "production_system": "✅ Verified with 3 scans",
    "verified_by": "Agent 1",
    "verified_date": "2025-10-18"
  }

  Quality Check:
  - ✅ Independent tests passing
  - ✅ Forbidden files verified unchanged
  - ✅ Production system tested
  - ✅ No regressions
  - ✅ Final sign-off complete

  ---
  communication.json Structure

  Required Sections

  {
    "feature": "TASK NAME IN CAPS",
    "from": "Agent 1",
    "to": "Agent 4",
    "date": "YYYY-MM-DD",
    "task": "One-line summary",

    "instruction": "Single sentence directive",

    "precise_steps": [
      "Step 1: Read file.ts:123-456",
      "Step 2: Implement feature X",
      "Step 3: Add helper to file2.ts",
      "Step 4: Update tests",
      "Step 5: Run test: command",
      "Step 6: Create docs",
      "Step 7: Verify file.ts unchanged (git diff)",
      "Step 8: Rebuild: build command",
      "Step 9: Commit: 'message'"
    ],

    "details": {
      "work_area": "specific/directory/",
      "forbidden_files": [
        "file1.ts - DO NOT MODIFY (reason)"
      ],
      "allowed_files": [
        "file2.ts - What to change"
      ]
    },

    "testing_checklist": [
      "1. Create test case",
      "2. Run test",
      "3. Verify output"
    ],

    "success_criteria": [
      "✅ Feature implemented and working",
      "✅ Tests pass",
      "✅ file.ts unchanged (git diff)",
      "✅ Builds without errors"
    ],

    "agent_1_status": "Ready for execution",
    "agent_4_status": null
  }

  ---
  Key Patterns

  Precise Steps Pattern

  Format: "Step N: {Action} {target} {location} {constraint}"

  Examples:
  - ✅ "Step 1: Read packages/core/src/analyzer/analyzer-service.ts:266-273"
  - ✅ "Step 7: Verify packages/core/scanner.ts unchanged (git diff)"
  - ❌ "Fix the bug" (too vague)
  - ❌ "Update some files" (no specifics)

  ---
  Forbidden/Allowed Files Pattern

  Purpose: Protect production, prevent scope creep

  "forbidden_files": [
    "scanner.ts - DO NOT MODIFY (production regex scanner)",
    "cli.ts - DO NOT MODIFY (working CLI)"
  ],
  "allowed_files": [
    "analyzer-service.ts - Fix loadGraph() method",
    "graph-builder.ts - Add helper"
  ]

  Verification:
  git diff packages/core/scanner.ts  # Must show no changes

  ---
  Success Criteria Pattern

  Format: "✅ {Outcome} - {Verification method}"

  Examples:
  - "✅ loadGraph() implemented and working"
  - "✅ test-ast-analyzer.js passes with save/load test"
  - "✅ scanner.ts unchanged (git diff shows no changes)"
  - "✅ Regex scanner still works: cd packages/cli && pnpm start scan ../core"

  ---
  Git Commit Pattern

  {Action} {component} and {additional work}

  - Implementation detail 1
  - Implementation detail 2
  - Test update
  - Documentation

  ✅ Key success criterion
  ✅ Boundary verification
  ✅ Build status

  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>

  ---
  Agent Responsibilities Matrix

  | Task                      | Agent 1 (Plan) | Agent 4 (Execute) | Agent 1 (Verify) |
  |---------------------------|----------------|-------------------|------------------|
  | Decompose task            | ✅              | ❌                 | ❌                |
  | Create communication.json | ✅              | ❌                 | ❌                |
  | Execute code changes      | ❌              | ✅                 | ❌                |
  | Run tests                 | ❌              | ✅                 | ✅ (independent)  |
  | Verify boundaries         | ❌              | ✅                 | ✅ (double-check) |
  | Code review               | ❌              | ❌                 | ✅                |
  | Integration test          | ❌              | ❌                 | ✅                |
  | Final sign-off            | ❌              | ❌                 | ✅                |

  ---
  Quality Gates

  Gate 1: Before Execution

  - Steps specific with file paths
  - Success criteria measurable
  - Forbidden files marked
  - No ambiguity

  Gate 2: Before Verification

  - All steps completed
  - All criteria met
  - No forbidden files modified
  - Tests passing
  - Docs complete

  Gate 3: Before Closure

  - Independent tests pass
  - Boundaries verified (git diff)
  - Production tested
  - No regressions
  - Sign-off complete

  ---
  Benefits

  1. Clear Accountability - Each agent owns their phase
  2. Production Safety - Forbidden files protected via git diff
  3. Traceability - Line numbers, commits, dates tracked
  4. Quality Assurance - Multi-agent verification
  5. Knowledge Transfer - communication.json documents everything

  ---
  Real Example: AST Analyzer Fixes

  Task: Fix loadGraph() method

  Phase 1: Agent 1 created 10-step plan with forbidden files
  Phase 2: Agent 4 executed, added 16 lines to analyzer-service.ts:266-281
  Phase 3: Agent 1 verified with independent tests, confirmed scanner.ts unchanged

  Result:
  - ✅ All 9 success criteria met
  - ✅ 0 regressions
  - ✅ Production safe
  - ✅ Both agents signed off

  File: coderef/working/ast-analyzer-fixes/communication.json
  Commit: f617b5f

  ---
  Quick Start Template

  {
    "feature": "{YOUR TASK}",
    "from": "Agent 1",
    "to": "Agent 4",
    "date": "2025-10-18",
    "task": "{summary}",
    "instruction": "{directive}",
    "precise_steps": [
      "Step 1: Read {file}:{lines}",
      "Step 2: Implement {feature}",
      "Step N: Commit: '{message}'"
    ],
    "details": {
      "forbidden_files": ["{file} - DO NOT MODIFY ({reason})"],
      "allowed_files": ["{file} - {what to change}"]
    },
    "success_criteria": [
      "✅ {outcome} - {verification}"
    ],
    "agent_1_status": "Ready",
    "agent_4_status": null
  }

  ---
  Pattern Status: ✅ Validated in Production (2025-10-18)
  Use For: All multi-step tasks requiring agent handoff
  Source: coderef/working/ast-analyzer-fixes/communication.json