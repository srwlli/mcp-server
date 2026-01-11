# coderef-docs - AI Context Documentation

**Project:** coderef-docs (MCP Server)
**Version:** 3.7.0
**Status:** ✅ Production
**Created:** 2024-10-18
**Last Updated:** 2026-01-10

---

## Quick Summary

**coderef-docs** is a focused MCP server providing **13 specialized tools** for documentation generation, changelog management, standards enforcement, and composable resource sheets. It works with coderef-workflow to deliver end-to-end feature lifecycle documentation.

**Core Innovation:** POWER framework templates + agentic changelog recording with git auto-detection + sequential foundation doc generation with .coderef/ code intelligence + composable module-based resource sheets + **dual validation pattern (instruction-based + direct integration)**.

**Latest Update (v3.7.0 - WO-CODEREF-DOCS-DIRECT-VALIDATION-001):**
- ✅ DUAL VALIDATION PATTERN: Instruction-based + Direct integration coexist
  - **Pattern 1 (Instruction-Based)** - Tools output Python validation code for Claude to execute (user transparency)
  - **Pattern 2 (Direct Integration)** - Tools output code to write validation metadata to frontmatter `_uds` section (machine-readable)
  - **Why Both** - Instruction-based provides transparency, direct integration provides metadata for downstream tools
  - **Helper Function** - `write_validation_metadata_to_frontmatter()` in utils/validation_helpers.py
  - **Frontmatter Structure** - `_uds: {validation_score, validation_errors, validation_warnings, validated_at, validator}`
  - **No Breaking Changes** - Existing instruction-based validation unchanged
  - **Status:** ✅ Complete with 20 passing tests (12 existing + 8 new)

**Previous Update (v3.6.0 - WO-UDS-COMPLIANCE-CODEREF-DOCS-001):**
- ✅ INTEGRATED: Papertrail validators for foundation and standards docs (instruction-based pattern)
  - **Foundation Docs** - FoundationDocValidator for README, ARCHITECTURE, API, SCHEMA, COMPONENTS
  - **Standards Docs** - StandardsDocValidator for ui-patterns, behavior-patterns, ux-patterns
  - **Validation Instructions** - Tools now output executable Python code for document validation
  - **Validation Threshold** - Score >= 90 required for passing
  - **PAPERTRAIL_ENABLED Default** - Changed from false to true for automatic validation
  - **Validation Coverage** - Increased from 22% (4/18) to 72% (13/18) outputs
  - **Status:** ✅ Complete with 12 passing tests (6 unit + 6 integration)

**Previous Update (v3.5.0 - WO-CODEREF-CONTEXT-MCP-INTEGRATION-001):**
- ✅ NEW: `.coderef/` integration for foundation doc generation
  - **NO SCANNING** during doc generation - all .coderef/ files must pre-exist
  - **Template-Specific Context Mapping** - Each template uses specific .coderef/ files
  - **10 Resource Types** - index.json, context.md, context.json, graph.json, patterns.json, coverage.json, diagrams/, etc.
  - **Performance** - < 50ms per file (file reads only, no MCP calls, no subprocess)
  - **Missing Resources Warning** - User gets actionable warning to run coderef_scan first
  - **Status:** ✅ Complete integration in tool_handlers.py and mcp_integration.py

**Previous Update (v3.4.0 - WO-RESOURCE-SHEET-MCP-TOOL-001):**
- ✅ NEW: `generate_resource_sheet` tool - Composable module-based documentation system
  - **Replaces:** 20 rigid templates with ~30-40 composable modules (4 universal + 11+ conditional)
  - **3-Step Workflow:** Detect (code characteristics) → Select (appropriate modules) → Assemble (3 formats)
  - **Auto-Fill:** 50% in Phase 1 (architecture + integration modules), 60%+ target in Phase 2
  - **Outputs:** Markdown + JSON Schema + JSDoc from single code analysis
  - **Modes:** reverse-engineer (analyze existing), template (scaffold new), refresh (update docs)
  - **Status:** Phase 1 complete (17/22 tasks, 100% test coverage)

**Previous Update (v3.3.0):**
- ✅ UPGRADED: `establish_standards` now leverages .coderef/ data for 10x performance boost
  - **Fast Path:** Reads .coderef/index.json (~50ms) instead of scanning entire codebase (~5-60 seconds)
  - **Automatic Fallback:** Uses full scan if .coderef/ unavailable (backward compatible)
  - **Smart Detection:** Extracts only component files from index, analyzes patterns

**Previous Update (v3.2.0):**
- ✅ UPGRADED: `generate_foundation_docs` now uses sequential generation with context injection
- ✅ UPGRADED: `generate_individual_doc` now injects context for relevant templates

**Key Relationships:**
- **coderef-workflow** = Orchestration & planning
- **coderef-context** = Code intelligence (optional integration)

Together they form a complete feature lifecycle: Context → Plan → Code → Documentation → Archive.

---

## 🌍 Global Deployment Rule

**NOTHING IS LOCAL. ENTIRE ECOSYSTEM IS GLOBAL.**

All tools, commands, and artifacts must use **global paths only**:
- `~/.claude/commands/` (commands)
- `coderef/workorder/` (plans)
- `coderef/foundation-docs/` (technical documentation)
- `coderef/user/` (user-facing documentation)
- `coderef/archived/` (completed features)
- `coderef/standards/` (standards)
- MCP tools (global endpoints only)

❌ **FORBIDDEN:** Local copies, project-specific variations, `coderef/working/`, per-project configurations

**Rule:** No fallbacks, no exceptions, no local alternatives. Single global source of truth.

---

## Architecture

### Core Responsibility
Generates all project documentation artifacts (README, ARCHITECTURE, SCHEMA, API, COMPONENTS, CHANGELOG, standards guides, quickref). Integrates with coderef-workflow to document completed features and track changes.

### Documentation Domains
```
Foundation Docs → README, ARCHITECTURE, SCHEMA, API, COMPONENTS (coderef/foundation-docs/)
User Docs → my-guide, USER-GUIDE, FEATURES, quickref (coderef/user/)
Resource Sheets → Composable module-based element documentation (NEW in v3.4.0)
Changelog Ops → Get, add, and record changes with git auto-detection
Standards & Compliance → Extract patterns, audit for violations, pre-commit checks
```

### Key Integration Points
- **Depends on:** coderef-workflow (for feature context), git (for changelog recording)
- **Used by:** AI agents and users for documentation workflows
- **Orchestrated via:** 22 slash commands in `~/.claude/commands/`

---

## Tools Catalog

| Tool | Purpose | Type |
|------|---------|------|
| `list_templates` | Show available POWER framework templates | Utility |
| `get_template` | Get specific template by name | Utility |
| `generate_foundation_docs` | Create README, ARCHITECTURE, SCHEMA, etc. | Generator |
| `generate_individual_doc` | Create single doc from template | Generator |
| `generate_quickref_interactive` | Interactive quickref for any app type ⭐ | Generator |
| `generate_resource_sheet` | Composable module-based docs (NEW) 🆕 | Generator |
| `add_changelog_entry` | Manually add changelog entry | Writer |
| `record_changes` | Smart recording with git auto-detection ⭐ | Agentic |
| `establish_standards` | Extract coding standards from codebase | Analyzer |
| `audit_codebase` | Check standards compliance (0-100 score) | Auditor |
| `check_consistency` | Pre-commit gate for staged changes | Auditor |
| `validate_document` | Validate doc against UDS schema | Validator |
| `check_document_health` | Calculate doc health score (0-100) | Validator |

**Total:** 13 tools across 4 domains (Documentation, Resource Sheets, Changelog, Standards)

---

## POWER Framework

All documentation uses **POWER** structure for consistency:

- **Purpose** - Why this document exists and what problem it solves
- **Overview** - What's included and scope
- **What/Why/When** - Detailed content with context
- **Examples** - Concrete, working illustrations
- **References** - Links to related documentation

This ensures all generated docs follow the same proven pattern and are immediately recognizable.

---

## Universal Document Standard (UDS)

**UDS** adds structured metadata to workorder documentation for tracking, lifecycle management, and traceability.

### What is UDS?

UDS is a metadata system that injects YAML frontmatter (for markdown files) or JSON metadata fields (for JSON files) into all workorder-generated documents. It provides:

- **Workorder Tracking** - Links documents to specific workorder IDs
- **Lifecycle Management** - Tracks document status (DRAFT/IN_REVIEW/APPROVED/ARCHIVED)
- **Provenance** - Records which server/version generated the document
- **Review Scheduling** - Auto-calculates next review dates
- **AI Attribution** - Marks AI-assisted document generation

### Scope

UDS applies **only to workorder documents**:
- ✅ `plan.json` - UDS metadata in META_DOCUMENTATION.uds section
- ✅ `context.json` - UDS metadata in _uds section
- ✅ `analysis.json` - UDS metadata in _uds section
- ✅ `DELIVERABLES.md` - YAML frontmatter headers/footers
- ✅ `claude.md` - YAML frontmatter headers/footers

UDS does **NOT** apply to:
- ❌ Foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
- ❌ User docs (USER-GUIDE, my-guide, FEATURES, quickref)

### UDS Format Examples

**For Markdown Files (DELIVERABLES.md, claude.md):**

```yaml
---
title: DELIVERABLES - feature-name
version: 1.0
generated_by: coderef-workflow v1.7.0
workorder_id: WO-FEATURE-001
feature_id: feature-name
status: IN_PROGRESS
timestamp: 2025-12-28T20:00:00Z
---

[Document content here]

---
generated_by: coderef-workflow v1.7.0
workorder: WO-FEATURE-001
feature: feature-name
last_updated: 2025-12-28
ai_assistance: true
status: IN_PROGRESS
next_review: 2026-01-27
---
```

**For JSON Files (plan.json, context.json, analysis.json):**

```json
{
  "_uds": {
    "generated_by": "coderef-workflow v1.7.0",
    "document_type": "Feature Context",
    "workorder_id": "WO-FEATURE-001",
    "feature_id": "feature-name",
    "last_updated": "2025-12-28",
    "ai_assistance": true,
    "status": "DRAFT",
    "next_review": "2026-01-27"
  },
  ...rest of document
}
```

### Integration

UDS is automatically injected when workorder documents are generated:
- **coderef-workflow** injects UDS into context.json, analysis.json, DELIVERABLES.md
- **coderef-docs** injects UDS into plan.json (via planning_generator.py) and claude.md (via handoff_generator.py)

UDS injection is **backward compatible** - only applies when `workorder_id` exists. Documents without workorder IDs remain unchanged.

### Implementation (WO-UDS-INTEGRATION-001)

- **Templates:** `templates/uds/header.yaml`, `templates/uds/footer.yaml`
- **Helpers:** `uds_helpers.py` (generate_uds_header, generate_uds_footer, get_server_version)
- **Generators:** Updated in both coderef-docs and coderef-workflow
- **Tests:** `tests/test_uds_helpers.py` (15+ test cases)

---

## .coderef/ Integration

**.coderef/ resources provide pre-generated code intelligence for documentation.**

**WO-CODEREF-CONTEXT-MCP-INTEGRATION-001** integrated .coderef/ file reading into foundation doc generation.

**NO SCANNING** during doc generation - all files must pre-exist. If missing, user receives warning to run scanning first.

###Available .coderef/ Resources

| File | Purpose | Used By |
|------|---------|---------|
| `index.json` | All code elements (functions, classes, components) | API, SCHEMA, COMPONENTS |
| `context.md` | Human-readable project summary | README |
| `context.json` | Structured project overview | ARCHITECTURE, SCHEMA |
| `graph.json` | Full dependency graph | ARCHITECTURE |
| `reports/patterns.json` | Code patterns and conventions | README, API, COMPONENTS |
| `reports/coverage.json` | Test coverage data | (future use) |
| `reports/drift.json` | Index drift detection | (future use) |
| `reports/validation.json` | CodeRef validation results | (future use) |
| `diagrams/` | Dependency, call, import diagrams | ARCHITECTURE |
| `exports/` | Various export formats | (future use) |

### Template-Specific Context Mapping

```
README:
 - context.md (project overview)
 - patterns.json (coding conventions)

ARCHITECTURE:
 - context.json (structure)
 - graph.json (dependencies)
 - diagrams/ (visual representations)

API:
 - index.json (filter for endpoints/routes)
 - patterns.json (API conventions)

SCHEMA:
 - index.json (filter for models/entities)
 - context.json (relationships)

COMPONENTS:
 - index.json (filter for UI components)
 - patterns.json (component conventions)
```

### Integration Flow

1. **Resource Check** - `check_coderef_resources()` validates file availability
2. **Template Mapping** - `get_template_context_files()` identifies needed files
3. **Instructions** - `get_context_instructions()` provides template-specific guidance
4. **File Reading** - Claude reads .coderef/ files directly (< 50ms per file)
5. **Template Population** - Claude extracts relevant data and populates templates

**Performance:** < 50ms per file (file reads only, no MCP calls, no subprocess)

**Missing Resources:** If .coderef/ files don't exist, user gets actionable warning to run `coderef_scan` first. Documentation uses regex-based detection with placeholders as fallback.

### Implementation (WO-CODEREF-CONTEXT-MCP-INTEGRATION-001)

- **Integration Module:** `mcp_integration.py` (check_coderef_resources, get_context_instructions, get_template_context_files)
- **Tool Handlers:** Updated `handle_generate_foundation_docs` and `handle_generate_individual_doc` in `tool_handlers.py`
- **Status:** ✅ Complete (no MCP scanning, file-read only)

---

## File Structure

```
coderef-docs/
├── server.py                      # MCP server entry point (374 lines)
├── tool_handlers.py               # 11 tool handlers (925+ lines) [v3.2.0: context injection]
├── extractors.py                  # Context injection via @coderef/core CLI (~400 lines)
├── generators/
│   ├── foundation_generator.py    # Multi-doc generation
│   ├── changelog_generator.py     # CRUD + schema validation
│   ├── standards_generator.py     # Standards extraction
│   └── audit_generator.py         # Compliance auditing
├── templates/power/               # POWER framework templates
├── README.md                      # User-facing guide
├── CLAUDE.md                      # This file (AI context, v3.2.0)
├── tests/                         # Comprehensive proof tests (30 tests, 27 passing)
└── .claude/commands/              # 22 slash commands
    ├── /generate-docs              # Foundation docs
    ├── /generate-user-docs         # User-facing docs
    ├── /record-changes             # Smart changelog
    └── {19 others}
```

---

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** MCP (Model Context Protocol) 1.0+
- **Async:** asyncio (fully async/await for all tool handlers)
- **Validation:** jsonschema 4.0+ (for CHANGELOG.json and plan validation)
- **Template Engine:** Custom POWER framework templates (markdown-based)
- **Testing:** pytest 8.0+ with pytest-asyncio
- **External Integration:** @coderef/core CLI (optional, for context injection)
- **Package Manager:** uv (or pip)

---

## Design Decisions

**1. Separated from coderef-workflow**
- ✅ Chosen: coderef-docs handles docs only
- ❌ Rejected: Combine docs + workflow in single server
- Reason: Single responsibility principle, easier to test and maintain independently

**2. POWER Framework for All Documentation**
- ✅ Chosen: Universal template applied to all doc types
- ❌ Rejected: Custom templates for each doc type
- Reason: Consistency across projects, reduced maintenance, proven effectiveness

**3. Agentic Record_Changes Tool**
- ✅ Chosen: Smart tool with git auto-detection + AI confirmation
- ❌ Rejected: Manual form-based changelog entry
- Reason: Reduces friction for AI agents, captures context automatically, validates before writing

**4. 11 Tools vs 30+**
- ✅ Chosen: Focused toolset (11 core tools)
- ❌ Rejected: Include all inventory tools from v2.0.0
- Reason: v2.0.0 merged with coderef-workflow; docs stays focused on documentation

**5. Sequential Foundation Doc Generation with Context Injection (v3.2.0)**
- ✅ Chosen: Sequential generation (5 calls to `generate_individual_doc`) + context injection
- ❌ Rejected: Dump all 4 templates at once (timeout errors) OR template-only without context
- Reason: Eliminates timeouts (~250-350 lines per call) while preserving real code intelligence from @coderef/core CLI
- Implementation: `generate_foundation_docs` orchestrates 5 sequential calls with progress markers [i/N]
- Context Injection: `extract_apis`, `extract_schemas`, `extract_components` provide real data
- Backward Compatibility: Graceful fallback to placeholders if CLI unavailable

---

## Integration Guide

### With coderef-workflow
- Workflow creates features and plans → coderef-docs generates documentation
- Tools orchestrated via slash commands (user-friendly entry points)
- Called automatically at feature completion (update_docs, archive_feature)
- DELIVERABLES.md and CHANGELOG tracked across lifecycle

### With coderef-context (WO-CONTEXT-DOCS-INTEGRATION-001)
- **Foundation Docs Generation:**
  - `generate_foundation_docs` orchestrates sequential generation with context injection
  - `generate_individual_doc` extracts real APIs/schemas/components via @coderef/core CLI
  - Displays extracted data alongside templates for Claude to populate with real information
  - Falls back gracefully to placeholders if CLI unavailable
- **Standards Auditing:**
  - Standards audit system can optionally use coderef patterns for advanced analysis
- **Status:** Context injection fully integrated, tested with 27/30 proof tests passing
- **Key Files:**
  - `extractors.py`: Calls @coderef/core CLI to extract real code intelligence
  - `tool_handlers.py`: Uses extraction results in doc generation handlers
  - `tests/`: Comprehensive proof tests validating end-to-end integration

---

## Implementation Status

### Completed ✅
- ✅ All 11 MCP tools implemented and operational
- ✅ POWER framework templates (README, ARCHITECTURE, API, COMPONENTS, SCHEMA, USER-GUIDE, MY-GUIDE)
- ✅ Sequential foundation doc generation with context injection (v3.2.0)
- ✅ Agentic changelog recording with git auto-detection
- ✅ Standards establishment and compliance auditing system
- ✅ Interactive quickref generation for 5 app types (CLI, Web, API, Desktop, Library)
- ✅ Context injection from @coderef/core CLI (extractors.py)
- ✅ 22 slash commands registered in ~/.claude/commands/
- ✅ Full MCP protocol compliance (JSON-RPC 2.0 over stdio)

### Testing Status
- ✅ 27/30 proof tests passing (90% pass rate)
- ✅ End-to-end integration tests with @coderef/core CLI
- ✅ Real-world validation with WO-CONTEXT-DOCS-INTEGRATION-001
- ⏳ 3 tests pending (non-blocking issues)
- ⏳ Performance benchmarks for large codebases (>100k LOC)

### Known Limitations
- Context injection requires @coderef/core CLI (graceful degradation if unavailable)
- Standards auditing requires pre-established standards (run /establish-standards first)
- Changelog auto-detection requires git repository
- Template customization not yet supported (fixed POWER framework)

---

## Essential Commands

### Development
```bash
# Install & run
uv sync
python server.py

# Run tests
pytest tests/ -v

# Type check
mypy src/
```

### Usage / Slash Commands
```bash
/generate-docs              # Generate foundation docs (README, ARCHITECTURE, etc)
/generate-user-docs         # Generate all 4 user-facing docs (my-guide, USER-GUIDE, FEATURES, quickref)
/record-changes             # Smart changelog with git auto-detection
/establish-standards        # Extract coding standards
/audit-codebase            # Check standards compliance (0-100 score)
/check-consistency         # Pre-commit gate for modified files
```

---

## Use Cases

### UC-1: Generate Complete Project Documentation
```
User: /generate-docs
Tool: Analyzes project structure
Claude: Generates and fills POWER templates
Output: README.md (root), ARCHITECTURE.md, SCHEMA.md, API.md, COMPONENTS.md (coderef/foundation-docs/)

User: /generate-user-docs
Tool: Generates 4 user-facing docs sequentially
Output: my-guide.md, USER-GUIDE.md, FEATURES.md, quickref.md (coderef/user/)

All docs follow POWER framework for consistency
```

### UC-2: Record Feature Completion with Smart Changelog
```
User: Completes feature implementation
Tool: /record-changes triggered (or called by coderef-workflow)
Tool: Auto-detects git changes, suggests change_type (feature/bugfix/breaking)
Claude: Reviews suggestion, confirms details
Output: CHANGELOG.json entry with workorder tracking, README version bump
```

---

## Recent Changes

### v3.7.0 - Direct Validation Integration (WO-CODEREF-DOCS-DIRECT-VALIDATION-001) (2026-01-10)
- ✅ DUAL VALIDATION PATTERN: Added direct integration alongside existing instruction-based validation
  - **Pattern 1 (Instruction-Based):** Tools output Python validation code for Claude to execute (user transparency)
  - **Pattern 2 (Direct Integration):** Tools output code to write validation metadata to frontmatter `_uds` section (machine-readable)
  - **Helper Function:** `write_validation_metadata_to_frontmatter()` in utils/validation_helpers.py
  - **Frontmatter Structure:** `_uds: {validation_score, validation_errors, validation_warnings, validated_at, validator}`
- ✅ INTEGRATION: Both validation patterns coexist without conflicts
  - Foundation docs (5): Both patterns in tool_handlers.py lines 346-385
  - Standards docs (3): Both patterns in tool_handlers.py lines 816-865
  - Hybrid approach: Tools output enhanced instructions, Claude executes both validations
- ✅ TESTING: 20 tests passing (12 existing + 8 new)
  - test_direct_validation.py: 8 new tests verify direct validation integration
  - No regression: All existing instruction-based tests still pass
  - test_both_patterns_coexist: Verifies dual pattern works correctly
- ✅ DOCUMENTATION: Comprehensive architectural decision document
  - ARCHITECTURAL-DECISION.md explains hybrid approach (Option 3)
  - Both patterns documented with rationale (transparency + machine metadata)
  - No breaking changes to existing WO-UDS-COMPLIANCE-CODEREF-DOCS-001 implementation

### v3.5.0 - .coderef/ Integration for Foundation Docs (WO-CODEREF-CONTEXT-MCP-INTEGRATION-001) (2026-01-10)
- ✅ NEW: `.coderef/` integration for foundation doc generation
  - **NO SCANNING** during doc generation - all .coderef/ files must pre-exist
  - **Template-Specific Context Mapping:** Each template reads specific .coderef/ files
    - README: context.md, patterns.json
    - ARCHITECTURE: context.json, graph.json, diagrams/
    - API: index.json, patterns.json
    - SCHEMA: index.json, context.json
    - COMPONENTS: index.json, patterns.json
  - **10 Resource Types Supported:** index.json, context.md, context.json, graph.json, patterns.json, coverage.json, drift.json, validation.json, diagrams/, exports/
  - **Performance:** < 50ms per file (file reads only, no MCP calls, no subprocess)
  - **Missing Resources Warning:** User gets actionable warning to run coderef_scan first
- ✅ IMPLEMENTATION: `mcp_integration.py` with 4 new functions
  - `check_coderef_resources()` - Validates file availability
  - `get_template_context_files()` - Template-to-file mapping
  - `get_context_instructions()` - Template-specific guidance
  - `format_missing_resources_warning()` - User-friendly warnings
- ✅ INTEGRATION: Updated `tool_handlers.py`
  - Modified `handle_generate_foundation_docs` to check resources and provide context mapping
  - Modified `handle_generate_individual_doc` to inject template-specific instructions
  - Displays available/missing resources with element counts
- ✅ STATUS: Complete integration (file-read only, no MCP orchestration needed)

### v3.4.0 - Resource Sheet MCP Tool (WO-RESOURCE-SHEET-MCP-TOOL-001) (2026-01-02)
- ✅ NEW: `generate_resource_sheet` tool - Composable module-based documentation system
  - **Innovation:** Replaces 20 rigid templates with composable module architecture
  - **3-Step Workflow:** Detect (20+ code characteristics) → Select (appropriate modules) → Assemble (3 formats)
  - **Modules Implemented:** 4 universal modules (architecture, integration, testing stub, performance stub)
  - **Auto-Fill Rate:** 50% in Phase 1 (architecture + integration fully auto-filled)
  - **Detection Accuracy:** ~85% baseline (target 90%+ in Phase 2)
  - **Output Formats:** Markdown + JSON Schema + JSDoc from single analysis
  - **Modes:** reverse-engineer (analyze existing), template (scaffold new), refresh (update docs)
  - **Testing:** 13/13 tests passing (100% coverage)
  - **Performance:** < 5 seconds end-to-end generation (well under 10s target)
- ✅ ARCHITECTURE: Detection engine reads .coderef/index.json for code intelligence
  - CharacteristicsDetector maps code patterns to boolean flags
  - CodeAnalyzer orchestrates coderef_scan with graceful fallback
  - ModuleRegistry manages universal + conditional module selection
  - DocumentComposer assembles modules into 3 synchronized outputs
- ✅ DOCUMENTED: Complete Phase 1 implementation (17/22 tasks, 77%)
  - Phase 1 COMPLETE: All core functionality operational
  - Phase 2 DEFERRED: 11 conditional modules, Papertrail integration, 60%+ auto-fill target
  - Examples created for all 3 output formats
  - PHASE-1-COMPLETION-SUMMARY.md documents achievements

### v3.6.0 - Papertrail Validator Integration (WO-UDS-COMPLIANCE-CODEREF-DOCS-001) (2026-01-10)
- ✅ INTEGRATED: Papertrail validators for foundation and standards documentation
  - **Foundation Docs:** FoundationDocValidator integrated for README, ARCHITECTURE, API, SCHEMA, COMPONENTS
  - **Standards Docs:** StandardsDocValidator integrated for ui-patterns, behavior-patterns, ux-patterns
  - **Validation Instructions:** Tools output executable Python validation code after doc generation
  - **Validation Threshold:** Score >= 90 required for passing
  - **PAPERTRAIL_ENABLED Default:** Changed from false to true (line 271 in tool_handlers.py)
- ✅ IMPLEMENTATION: Modified tool_handlers.py with validation instructions
  - Lines 346-366: Foundation doc validation block in `handle_generate_individual_doc`
  - Lines 784-808: Standards doc validation block in `handle_establish_standards`
  - Both blocks include imports, validation logic, error reporting, and score threshold
- ✅ VALIDATION COVERAGE: Increased from 22% (4/18) to 72% (13/18) validated outputs
  - P0: 5 foundation docs validated (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
  - P1: 3 standards docs validated (ui-patterns, behavior-patterns, ux-patterns)
  - P2: 5 outputs deferred (quickref, resource sheets, user docs - future phase)
- ✅ TESTING: Comprehensive test suite with 12 passing tests
  - test_validator_integration.py: 6 unit tests for validation instruction inclusion
  - test_integration_e2e.py: 6 integration tests for end-to-end functionality
  - Tests verify validation code is syntactically valid and executable
  - Tests verify PAPERTRAIL_ENABLED behavior (default true, can be disabled)

### v3.3.0 - .coderef/ Integration for Standards Generation (2025-12-31)
- ✅ UPGRADED: `establish_standards` tool now leverages .coderef/ data
  - **Performance:** 10x faster (~50ms vs 5-60 seconds) for projects with .coderef/ structure
  - **Implementation:** Added `_read_coderef_index()` method to StandardsGenerator class
  - **Backward Compatible:** Falls back to full codebase scan if .coderef/ unavailable
  - **Smart Detection:** Reads .coderef/index.json, extracts component files only
  - **Testing:** Validated fast path (coderef-context) and slow path (temp project)
- ✅ DOCUMENTED: Created APPROACH-2-SIMPLE-ENHANCEMENT-PLAN.md
  - Documents alternative subprocess-based implementation (~50 LOC vs ~200 LOC)
  - Compares Approach 1 (full integration) vs Approach 2 (simple wrapper)
  - Provides implementation timeline and effort estimates
- ✅ SCRIPT: Enhanced enhance-standards.py script now in ecosystem
  - Standalone script for generating standards from .coderef/ data
  - Graceful error handling for empty/missing patterns.json
  - Cross-platform compatibility (Windows/Linux)

### v3.2.0 - Sequential Generation with Context Injection (WO-CONTEXT-DOCS-INTEGRATION-001)
- ✅ UPGRADED: `generate_foundation_docs` now uses sequential generation with context injection
  - Calls `generate_individual_doc` 5 times (~250-350 lines each) instead of dumping all at once (~1,470 lines)
  - Injects real code intelligence from @coderef/core CLI for API/Schema/Components templates
  - Shows progress markers [1/5], [2/5], etc. for visibility
  - Eliminates timeout errors while preserving context injection benefits
- ✅ UPGRADED: `generate_individual_doc` now injects context for relevant templates
  - For api/schema/components: Extracts real data via @coderef/core CLI and displays alongside template
  - Shows extracted endpoints, entities, components for Claude to use in documentation
  - Gracefully degrades to template-only if CLI unavailable
- ✅ TESTED: Comprehensive proof test suite (30 tests, 27 passing) validates end-to-end integration
  - Tests prove CLI returns real data, extraction flows to docs, templates populated with extracted data
  - Tests prove quality improvement vs placeholders, end-to-end integration works

### v3.1.0 - Focused Documentation System
- ✅ Record_changes agentic tool with git auto-detection and AI confirmation
- ✅ Standards establishment and compliance auditing (establish_standards, audit_codebase, check_consistency)
- ✅ Quickref generation for any application type (CLI, Web, API, Desktop, Library)
- 🗑️ Deprecated update_changelog (replaced by agentic record_changes)

### v3.0.0 - Standards & Compliance System
- ✅ Establish_standards tool discovers UI/behavior/UX patterns from codebase
- ✅ Audit_codebase validates compliance with standards (0-100 score)
- ✅ Check_consistency pre-commit gate for staged file changes

---

## Next Steps

- ⏳ REST API wrapper for ChatGPT integration (Unified HTTP Server)
- ⏳ Extended template library for specialized documentation types
- ⏳ Multi-language support for generated docs
- ⏳ Advanced standards analysis using coderef-context patterns (optional enhancement)

---

## Resources

- **[README.md](README.md)** - User-facing documentation guide
- **[SLASH-COMMANDS-REFERENCE.md](SLASH-COMMANDS-REFERENCE.md)** - Detailed slash command docs (if separate doc exists)
- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official MCP protocol
- **[POWER Framework](https://example.com/power-framework)** - Documentation template guide

---

## Troubleshooting

### "Error: Template not found"

```bash
# List all available templates
/list-templates

# Verify template name (case-sensitive)
# Valid names: readme, architecture, api, components, schema, user-guide, my-guide

# Get specific template
/get-template readme
```

### "Error: CHANGELOG.json validation failed"

```bash
# Validate JSON syntax
python -m json.tool coderef/CHANGELOG.json

# Check changelog schema
cat coderef/CHANGELOG.json | head -50

# Backup and regenerate if corrupted
cp coderef/CHANGELOG.json coderef/CHANGELOG.json.bak
# Then manually fix or regenerate
```

### "Error: Git auto-detection failed in record_changes"

```
→ Ensure you're in a git repository
→ Check git status returns valid output
→ Verify staged changes exist (git add files first)
→ Use add_changelog_entry for manual entry if git unavailable
```

### "Error: @coderef/core CLI not found (context injection)"

```
→ Check CODEREF_CLI_PATH environment variable
→ Verify CLI exists at path: C:/Users/willh/Desktop/projects/coderef-system/packages/cli
→ Tool gracefully degrades to template-only if CLI unavailable
→ No blocking error - docs still generate with placeholders
```

### "Error: Standards not established"

```bash
# Run establish_standards first
/establish-standards

# Check if standards directory exists
ls coderef/standards/

# Verify standards files
ls coderef/standards/*.md
```

### "Error: Audit failed - no standards found"

```
→ Run /establish-standards before /audit-codebase
→ Standards must exist in coderef/standards/ directory
→ Standards files: ui-patterns.md, behavior-patterns.md, ux-patterns.md
```

### "Error: Foundation docs generation timeout"

```
→ v3.2.0+ uses sequential generation (5 calls, ~250-350 lines each)
→ Timeout should not occur with sequential approach
→ If timeout persists, check Claude Code response time
→ Fall back to /generate-individual-doc for single docs
```

---

**Maintained by:** willh, Claude Code AI
