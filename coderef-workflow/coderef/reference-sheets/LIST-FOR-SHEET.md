# Resource Sheet Candidate List - coderef-workflow

**Generated:** 2026-01-02
**Source:** File system scan (59 Python files discovered)
**Purpose:** Prioritized list of files needing authoritative resource sheet documentation

---

## Priority Legend

- **P0 - Critical:** Core orchestration files (server, handlers, main workflows)
- **P1 - High:** Key generators and validators
- **P2 - Medium:** Supporting utilities and helpers
- **P3 - Low:** Test fixtures and internal utilities

---

## P0 - Critical (6 files)

### 1. server.py
- **Category:** infrastructure/core
- **Type:** MCP Server Entry Point
- **Complexity:** High (1,123 lines, 54 tool definitions)
- **Why Critical:** Main entry point, tool registry, MCP server lifecycle
- **Modules Needed:** architecture, integration, endpoints, performance, testing
- **Status:** ⏳ Needs resource sheet

### 2. tool_handlers.py
- **Category:** infrastructure/core
- **Type:** Tool Handler Registry
- **Complexity:** Very High (2,000+ lines, 24 handler functions)
- **Why Critical:** All tool implementations, error handling, logging decorators
- **Modules Needed:** architecture, integration, events, errors, performance, testing
- **Status:** ⏳ Needs resource sheet

### 3. generators/planning_analyzer.py
- **Category:** generators/analysis
- **Type:** Project Analysis Engine
- **Complexity:** High (920 lines, async analysis with .coderef/ integration)
- **Why Critical:** Core planning workflow, .coderef/ utilization, coderef-context MCP integration
- **Modules Needed:** architecture, integration, state, lifecycle, performance, endpoints
- **Status:** ⏳ Needs resource sheet

### 4. generators/planning_generator.py
- **Category:** generators/scaffolding
- **Type:** Plan Synthesis Engine
- **Complexity:** High (10-section plan generation)
- **Why Critical:** Orchestrates plan.json creation from context + analysis
- **Modules Needed:** architecture, integration, validation, performance, testing
- **Status:** ⏳ Needs resource sheet

### 5. generators/plan_validator.py
- **Category:** data/validators
- **Type:** Plan Quality Scorer
- **Complexity:** Medium (0-100 scoring with severity tracking)
- **Why Critical:** Quality gate for plan approval, prevents bad plans
- **Modules Needed:** architecture, validation, errors, testing
- **Status:** ⏳ Needs resource sheet

### 6. mcp_client.py
- **Category:** services/api-clients
- **Type:** MCP Tool Client
- **Complexity:** Medium (async MCP tool calling)
- **Why Critical:** Integration layer for coderef-context, enables code intelligence
- **Modules Needed:** architecture, integration, endpoints, errors, performance
- **Status:** ⏳ Needs resource sheet

---

## P1 - High (12 files)

### 7. type_defs.py
- **Category:** data/schemas
- **Type:** TypedDict Definitions
- **Complexity:** High (830 lines, 90 type definitions)
- **Why High:** Single source of truth for all data structures
- **Modules Needed:** architecture, validation
- **Status:** ⏳ Needs resource sheet

### 8. constants.py
- **Category:** data/schemas
- **Type:** Constants & Enums
- **Complexity:** Medium (382 lines, 18 enums)
- **Why High:** Centralized configuration, path constants
- **Modules Needed:** architecture
- **Status:** ⏳ Needs resource sheet

### 9. validation.py
- **Category:** data/validators
- **Type:** Input Validation Functions
- **Complexity:** Medium (15+ validation functions)
- **Why High:** Security boundary, prevents malformed inputs
- **Modules Needed:** architecture, validation, errors, security
- **Status:** ⏳ Needs resource sheet

### 10. error_responses.py
- **Category:** infrastructure/utilities
- **Type:** Error Response Factory
- **Complexity:** Low (ErrorResponse class)
- **Why High:** Standardized error handling across all tools
- **Modules Needed:** architecture, errors
- **Status:** ⏳ Needs resource sheet

### 11. handler_decorators.py
- **Category:** infrastructure/utilities
- **Type:** Decorator Functions
- **Complexity:** Medium (@mcp_error_handler, @log_invocation)
- **Why High:** Cross-cutting concerns (logging, error handling)
- **Modules Needed:** architecture, integration, lifecycle
- **Status:** ⏳ Needs resource sheet

### 12. handler_helpers.py
- **Category:** tools/utilities
- **Type:** Helper Functions
- **Complexity:** Medium (format_success_response, generate_workorder_id)
- **Why High:** Shared utilities across all tool handlers
- **Modules Needed:** architecture, integration
- **Status:** ⏳ Needs resource sheet

### 13. logger_config.py
- **Category:** infrastructure/utilities
- **Type:** Logging Configuration
- **Complexity:** Low (structured logging setup)
- **Why High:** Observability foundation
- **Modules Needed:** architecture, monitoring
- **Status:** ⏳ Needs resource sheet

### 14. generators/review_formatter.py
- **Category:** generators/templates
- **Type:** Markdown Report Generator
- **Complexity:** Medium (validation results → markdown)
- **Why High:** Plan review workflow
- **Modules Needed:** architecture, integration, validation
- **Status:** ⏳ Needs resource sheet

### 15. generators/risk_generator.py
- **Category:** generators/analysis
- **Type:** Risk Assessment Engine
- **Complexity:** High (5-dimension risk scoring)
- **Why High:** Go/no-go decisions for code changes
- **Modules Needed:** architecture, integration, validation, performance
- **Status:** ⏳ Needs resource sheet

### 16. generators/foundation_generator.py
- **Category:** generators/scaffolding
- **Type:** Foundation Doc Generator
- **Complexity:** High (POWER framework templates)
- **Why High:** Documentation automation
- **Modules Needed:** architecture, integration, validation
- **Status:** ⏳ Needs resource sheet

### 17. generators/changelog_generator.py
- **Category:** generators/scaffolding
- **Type:** Changelog Manager
- **Complexity:** Medium (CHANGELOG.json CRUD)
- **Why High:** Version history tracking
- **Modules Needed:** architecture, persistence, validation
- **Status:** ⏳ Needs resource sheet

### 18. generators/standards_generator.py
- **Category:** generators/analysis
- **Type:** Standards Discovery Engine
- **Complexity:** High (codebase scanning for UI/UX/behavior patterns)
- **Why High:** Establishes consistency baseline
- **Modules Needed:** architecture, integration, performance
- **Status:** ⏳ Needs resource sheet

---

## P2 - Medium (18 files)

### 19. generators/base_generator.py
- **Category:** generators/scaffolding
- **Type:** Base Generator Class
- **Complexity:** Medium (shared generator logic)
- **Modules Needed:** architecture, integration
- **Status:** ⏳ Needs resource sheet

### 20. generators/audit_generator.py
- **Category:** generators/analysis
- **Type:** Codebase Auditor
- **Complexity:** High (standards violation detection)
- **Modules Needed:** architecture, integration, validation
- **Status:** ⏳ Needs resource sheet

### 21. generators/consistency_checker.py
- **Category:** generators/analysis
- **Type:** Pre-Commit Quality Gate
- **Complexity:** Medium (git diff + standards check)
- **Modules Needed:** architecture, integration, validation
- **Status:** ⏳ Needs resource sheet

### 22. generators/features_inventory_generator.py
- **Category:** generators/analysis
- **Type:** Feature Inventory Scanner
- **Complexity:** Medium (scans workorder/ + archived/)
- **Modules Needed:** architecture, integration
- **Status:** ⏳ Needs resource sheet

### 23. generators/handoff_generator.py
- **Category:** generators/scaffolding
- **Type:** Agent Handoff Context Generator
- **Complexity:** High (claude.md generation from plan + git)
- **Modules Needed:** architecture, integration, validation
- **Status:** ⏳ Needs resource sheet

### 24. generators/mermaid_formatter.py
- **Category:** tools/utilities
- **Type:** Mermaid Diagram Formatter
- **Complexity:** Low (text formatting)
- **Modules Needed:** architecture
- **Status:** ⏳ Needs resource sheet

### 25. generators/quickref_generator.py
- **Category:** generators/scaffolding
- **Type:** Quickref Guide Generator
- **Complexity:** Medium (interactive interview workflow)
- **Modules Needed:** architecture, integration, validation
- **Status:** ⏳ Needs resource sheet

### 26. generators/coderef_foundation_generator.py
- **Category:** generators/scaffolding
- **Type:** Unified Foundation Doc Generator
- **Complexity:** Very High (replaces 7 inventory tools)
- **Modules Needed:** architecture, integration, performance, validation
- **Status:** ⏳ Needs resource sheet

### 27. plan_format_validator.py
- **Category:** data/validators
- **Type:** Plan Format Validator
- **Complexity:** Medium (JSON schema validation)
- **Modules Needed:** architecture, validation
- **Status:** ⏳ Needs resource sheet

### 28. schema_validator.py
- **Category:** data/validators
- **Type:** Schema Validator
- **Complexity:** Low (jsonschema wrapper)
- **Modules Needed:** architecture, validation
- **Status:** ⏳ Needs resource sheet

### 29-36. generators/__init__.py + other small modules
- **Category:** Various
- **Type:** Init files, small utilities
- **Complexity:** Low
- **Modules Needed:** architecture
- **Status:** ⏳ Needs resource sheet (low priority)

---

## P3 - Low (23 files)

### Test Files (tests/)
- conftest.py
- fixtures/mock_mcp_client.py
- fixtures/__init__.py
- FIX_get_checklist.py
- All test files (test_*.py)

**Category:** testing/test-helpers
**Type:** Test infrastructure
**Complexity:** Low to Medium
**Modules Needed:** architecture, testing
**Status:** ⏳ Needs resource sheet (batch documentation)

---

## Summary Statistics

| Priority | Count | % Total |
|----------|-------|---------|
| P0 - Critical | 6 | 10% |
| P1 - High | 12 | 20% |
| P2 - Medium | 18 | 31% |
| P3 - Low | 23 | 39% |
| **Total** | **59** | **100%** |

---

## Recommended Sequencing

### Phase 1: Core Infrastructure (P0)
Document these 6 files first to establish foundation understanding:

1. server.py - MCP server lifecycle
2. tool_handlers.py - Tool implementation patterns
3. mcp_client.py - External integration
4. planning_analyzer.py - Core analysis engine
5. planning_generator.py - Plan synthesis
6. plan_validator.py - Quality gate

**Estimated Effort:** 6-8 hours (1 hour per file × 6 files)

### Phase 2: Data Layer (P1 subset)
Document type system and validation:

7. type_defs.py - All data structures
8. constants.py - Configuration constants
9. validation.py - Input validation
10. error_responses.py - Error handling

**Estimated Effort:** 4-5 hours

### Phase 3: Generators (P1 + P2)
Document all generator classes:

11-26. All generators/ files

**Estimated Effort:** 16-20 hours

### Phase 4: Testing Infrastructure (P3)
Batch document test utilities:

27-59. All test files

**Estimated Effort:** 4-6 hours

---

## Resource Sheet Template Selection

For each file, use these module combinations:

### For MCP Server Files (server.py, tool_handlers.py)
- ✅ architecture (universal)
- ✅ integration (universal)
- ✅ testing (universal)
- ✅ performance (universal)
- ✅ endpoints (24 MCP tools = API endpoints)
- ✅ events (tool callbacks, decorators)
- ✅ errors (error handling patterns)

### For Generator Classes
- ✅ architecture (universal)
- ✅ integration (universal)
- ✅ testing (universal)
- ✅ performance (universal)
- ✅ state (manages analysis state)
- ✅ validation (validates inputs/outputs)

### For Validator Classes
- ✅ architecture (universal)
- ✅ integration (universal)
- ✅ testing (universal)
- ✅ performance (universal)
- ✅ validation (core purpose)
- ✅ errors (validation failures)

### For Utility Functions
- ✅ architecture (universal)
- ✅ integration (universal)
- ✅ testing (universal)
- ✅ performance (universal)

---

## Output Locations

All resource sheets will be saved to:

```
coderef-workflow/
├── coderef/
│   ├── reference-sheets/
│   │   ├── SERVER.md                           # server.py
│   │   ├── TOOL-HANDLERS.md                    # tool_handlers.py
│   │   ├── PLANNING-ANALYZER.md                # planning_analyzer.py
│   │   ├── PLANNING-GENERATOR.md               # planning_generator.py
│   │   ├── PLAN-VALIDATOR.md                   # plan_validator.py
│   │   ├── MCP-CLIENT.md                       # mcp_client.py
│   │   ├── TYPE-DEFS.md                        # type_defs.py
│   │   ├── CONSTANTS.md                        # constants.py
│   │   ├── VALIDATION.md                       # validation.py
│   │   ├── ... (50 more)
│   │   └── LIST-FOR-SHEET.md                   # This file
│   └── schemas/
│       ├── server-schema.json                  # JSON schemas
│       ├── tool-handlers-schema.json
│       └── ... (50 more)
```

---

## Completion Tracking

**Completed:** 1/59 (1.7%)

- ✅ RESOURCE-SHEET.md (coderef-workflow system overview) - Created 2026-01-02

**In Progress:** 0/59

**Remaining:** 58/59 (98.3%)

---

## Notes

1. **Batch vs Individual:** Consider batching similar files (e.g., all validators together)
2. **Auto-generation:** Use `.coderef/index.json` when populated (currently empty)
3. **Manual sections:** All resource sheets require human input for rationale, pitfalls, design decisions
4. **3-output requirement:** Every file needs .md + .json + .txt (JSDoc suggestions)

---

**Maintained by:** willh, Claude Code AI
**Updated:** 2026-01-02
**Next Review:** After Phase 1 completion (6 P0 files documented)
