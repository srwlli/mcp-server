# coderef-docs Output Inventory

**Agent:** coderef-docs
**Phase:** Phase 1 - Inventory (Self-Audit)
**Timestamp:** 2026-01-10T10:30:00Z
**Workorder:** WO-PAPERTRAIL-UDS-ALIGNMENT-001

---

## Summary

- **Total tools:** 13
- **Total outputs generated:** 18 distinct output types
- **Validated outputs:** 4 (CHANGELOG.json, audit reports, Papertrail UDS validation)
- **Unvalidated outputs:** 14 (foundation docs, quickref, resource sheets, standards)

---

## Tool Inventory

### Tool #1: list_templates
**Location:** tool_handlers.py:71
**Generates:** No file outputs (lists available templates only)

---

### Tool #2: get_template
**Location:** tool_handlers.py:100
**Generates:** No file outputs (reads template content only)

---

### Tool #3: generate_foundation_docs
**Location:** tool_handlers.py:127
**Generates:**

1. **README.md** (markdown)
   - Structure: POWER framework (Purpose, Overview, What/Why/When, Examples, References)
   - Location: Project root
   - Uses .coderef/context.md and patterns.json for code intelligence
   - Validation: No

2. **ARCHITECTURE.md** (markdown)
   - Structure: POWER framework
   - Location: coderef/foundation-docs/
   - Uses .coderef/context.json (structure), graph.json (dependencies), diagrams/ (visual representations)
   - Validation: No

3. **API.md** (markdown)
   - Structure: POWER framework
   - Location: coderef/foundation-docs/
   - Uses .coderef/index.json (filters for HTTP decorators, API patterns), patterns.json (API conventions)
   - Validation: No

4. **SCHEMA.md** (markdown)
   - Structure: POWER framework
   - Location: coderef/foundation-docs/
   - Uses .coderef/index.json (filters for ORM patterns, models/entities), context.json (entity relationships)
   - Validation: No

5. **COMPONENTS.md** (markdown)
   - Structure: POWER framework
   - Location: coderef/foundation-docs/
   - Uses .coderef/index.json (filters for React/Vue components), patterns.json (component conventions)
   - Validation: No

**Notes:**
- Sequential generation (5 calls to generate_individual_doc)
- NO SCANNING during doc generation - .coderef/ files must pre-exist
- Performance: < 50ms per file (file reads only)
- Warns user to run coderef_scan if .coderef/ resources missing

---

### Tool #4: generate_individual_doc
**Location:** tool_handlers.py:242
**Generates:**

1. **README.md | ARCHITECTURE.md | API.md | SCHEMA.md | COMPONENTS.md | USER-GUIDE.md | my-guide.md** (markdown)
   - Structure: POWER framework with .coderef/ code intelligence
   - Location: Variable based on template (README → root, others → coderef/foundation-docs/ or coderef/user/)
   - Optional Papertrail UDS integration when PAPERTRAIL_ENABLED=true and workorder_id provided
   - Papertrail adds YAML frontmatter header/footer with metadata: generated_by, workorder_id, feature_id, status, timestamp, next_review
   - Validation: Optional (Papertrail UDS validation when enabled, lines 270-317)

**Notes:**
- Variable output based on template_name parameter
- Graceful degradation if .coderef/ unavailable (uses placeholders)

---

### Tool #5: add_changelog_entry
**Location:** tool_handlers.py:352
**Generates:**

1. **CHANGELOG.json** (json)
   - Structure:
     ```json
     {
       "$schema": "./schema.json",
       "project": "string",
       "changelog_version": "1.0",
       "current_version": "X.Y.Z",
       "entries": [
         {
           "version": "X.Y.Z",
           "change_type": "feature|bugfix|enhancement|breaking_change|deprecation|security",
           "severity": "critical|major|minor|patch",
           "title": "string",
           "description": "string",
           "files": ["array"],
           "reason": "string",
           "impact": "string",
           "breaking": boolean,
           "migration": "string",
           "summary": "string",
           "contributors": ["array"]
         }
       ]
     }
     ```
   - Location: coderef/changelog/
   - Validation: **YES** (jsonschema validation via ChangelogGenerator)

**Notes:**
- Creates initial CHANGELOG.json if doesn't exist
- Supports workorder tracking (workorder_id field)

---

### Tool #6: record_changes
**Location:** tool_handlers.py:509
**Generates:** No direct file output (agentic workflow tool)

**Notes:**
- Auto-detects git changes (staged files)
- Suggests change_type from commit messages (feat/fix/BREAKING CHANGE patterns)
- Calculates severity from scope (file count)
- Generates preview for agent confirmation
- Agent must call add_changelog_entry to complete
- Returns instructions, not files

---

### Tool #7: generate_quickref_interactive
**Location:** tool_handlers.py:652
**Generates:**

1. **quickref.md** (markdown)
   - Structure: Universal quickref guide (150-250 lines scannable reference)
   - Location: coderef/user/
   - Sections: Purpose, Core Concepts, Essential Commands/Endpoints, Common Workflows, Troubleshooting, Quick Reference Tables
   - Supports 5 app types: CLI, Web, API, Desktop, Library
   - Interactive workflow: AI interviews user → generates quickref
   - Validation: No

---

### Tool #8: generate_resource_sheet
**Location:** tool_handlers.py:1191
**Generates:**

1. **{element_name}-RESOURCE-SHEET.md** (markdown)
   - Structure: Composable module-based documentation (WO-RESOURCE-SHEET-MCP-TOOL-001)
   - Detection engine reads .coderef/index.json to identify code characteristics
   - Selects appropriate modules (universal: architecture, integration, testing, performance + conditional modules)
   - Auto-fill rate: ~50% in Phase 1 (architecture + integration fully populated)
   - Validation: Optional (validate_against_code parameter, default true)

2. **{element_name}-schema.json** (json)
   - Structure: JSON Schema format generated from same code analysis as markdown
   - Synchronized with markdown output (same modules, same auto-fill)
   - Validation: Optional (validate_against_code parameter, default true)

3. **{element_name}-jsdoc.js** (text)
   - Structure: JSDoc format generated from same code analysis as markdown
   - Synchronized with markdown output (same modules, same auto-fill)
   - Validation: Optional (validate_against_code parameter, default true)

**Notes:**
- 3 synchronized output formats from single analysis
- Replaces 20 rigid templates with composable modules

---

### Tool #9: establish_standards
**Location:** tool_handlers.py:717
**Generates:**

1. **ui-patterns.md** (markdown)
   - Structure: UI patterns (buttons: allowed_sizes/variants, colors: allowed_hex_codes, modals, forms, inputs)
   - Location: coderef/standards/
   - Includes pattern definitions, examples, violation detection rules
   - Uses .coderef/index.json fast path (~50ms) if available, otherwise scans codebase (~5-60s)
   - Validation: No (but reads .coderef/ for intelligence when available)

2. **behavior-patterns.md** (markdown)
   - Structure: Behavior patterns (error handling: expected_patterns, loading states, validation, data fetching)
   - Location: coderef/standards/
   - Defines expected patterns and anti-patterns
   - Validation: No

3. **ux-patterns.md** (markdown)
   - Structure: UX patterns (navigation, permission checks, user workflows, accessibility)
   - Location: coderef/standards/
   - Documents user experience conventions
   - Validation: No

**Notes:**
- 10x performance boost with .coderef/ fast path
- Required for audit_codebase and check_consistency tools

---

### Tool #10: audit_codebase
**Location:** tool_handlers.py:791
**Generates:**

1. **audit-report-{timestamp}.md** (markdown)
   - Structure:
     - Compliance score (0-100, grade A-F)
     - Violations breakdown by severity (critical/major/minor)
     - File locations and pattern violations
     - Fix suggestions (if generate_fixes=true)
     - Scan metadata (duration, files_scanned, standards_files)
   - Location: coderef/audits/
   - Status: PASSING (score >= 70) or FAILING (score < 70)
   - Validation: **YES** (validates code against established standards from coderef/standards/*.md)

**Notes:**
- Requires establish_standards to be run first
- Filters by severity (critical/major/minor/all)
- Scope filter (ui_patterns/behavior_patterns/ux_patterns/all)

---

### Tool #11: check_consistency
**Location:** tool_handlers.py:955
**Generates:** No file output (terminal summary only)

**Structure:**
- Pre-commit quality gate
- Auto-detects changed files from git (staged) or accepts explicit file list
- Checks files against standards, filters by severity threshold
- Returns terminal-friendly summary: [PASS]/[FAIL] status, violations count, files checked, duration
- Exit code 1 if violations found and fail_on_violations=true
- Validation: **YES** (validates changed files against established standards)

**Notes:**
- Designed for CI/CD pipelines
- No files written - terminal output only

---

### Tool #12: validate_document
**Location:** tool_handlers.py:1065
**Generates:** No file output (JSON response only)

**Structure:**
- Papertrail UDS validation (Phase 3 integration)
- Returns JSON:
  ```json
  {
    "valid": boolean,
    "errors": [{"severity": string, "message": string, "location": string}],
    "warnings": [...],
    "validation_score": number,
    "success": boolean
  }
  ```
- Validation: **YES** (Papertrail UDS schema validation)

**Notes:**
- Requires Papertrail package installed (pip install papertrail>=1.0.0)

---

### Tool #13: check_document_health
**Location:** tool_handlers.py:1130
**Generates:** No file output (JSON response only)

**Structure:**
- Papertrail document health check (Phase 3 integration)
- Returns JSON:
  ```json
  {
    "score": number (0-100),
    "grade": string,
    "breakdown": {
      "traceability": number,
      "completeness": number,
      "freshness": number,
      "validation": number
    },
    "issues": [...],
    "recommendations": [...],
    "success": boolean
  }
  ```
- Validation: **YES** (Papertrail health scoring)

**Notes:**
- Requires Papertrail package installed

---

## Integration Notes

### .coderef/ Integration (WO-CODEREF-CONTEXT-MCP-INTEGRATION-001)

6 tools leverage .coderef/ resources:

1. **generate_foundation_docs** - Uses template-specific context files:
   - README: context.md, patterns.json
   - ARCHITECTURE: context.json, graph.json, diagrams/
   - API: index.json, patterns.json
   - SCHEMA: index.json, context.json
   - COMPONENTS: index.json, patterns.json

2. **generate_individual_doc** - Same .coderef/ integration as foundation_docs

3. **generate_resource_sheet** - Reads index.json for detection engine

4. **establish_standards** - Fast path reads index.json (~50ms vs ~5-60s full scan)

**Key Principle:** NO SCANNING during doc generation - .coderef/ files must pre-exist or user gets actionable warning to run coderef_scan first.

### Papertrail UDS Integration (Phase 3 & 4)

3 tools support Papertrail UDS:

1. **generate_individual_doc** - Optional YAML frontmatter when PAPERTRAIL_ENABLED=true (lines 270-317)
2. **validate_document** - UDS schema validation
3. **check_document_health** - Document health scoring

Requires: `pip install papertrail>=1.0.0`

### Workorder Tracking

- **CHANGELOG.json** entries support workorder_id field
- **generate_individual_doc** accepts workorder_id, feature_id, version parameters when Papertrail enabled
- Enables feature lifecycle tracking from planning → implementation → documentation → archive

---

## Validation Summary

**Validated Outputs (4):**
1. CHANGELOG.json (jsonschema validation)
2. audit-report-{timestamp}.md (standards validation)
3. validate_document response (Papertrail UDS validation)
4. check_document_health response (Papertrail health scoring)

**Optional Validation (3):**
1. generate_individual_doc (Papertrail UDS if PAPERTRAIL_ENABLED=true)
2. generate_resource_sheet (validate_against_code if enabled)
3. check_consistency (standards validation, terminal only)

**Unvalidated Outputs (14):**
- Foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
- quickref.md
- Resource sheet outputs (when validation disabled)
- Standards files (ui-patterns.md, behavior-patterns.md, ux-patterns.md)

---

## Recommendations for Phase 2 (Alignment)

Based on this inventory, the following areas may need alignment with Papertrail UDS standards:

1. **Foundation Docs** (5 files) - Currently no validation
   - Consider: Add UDS metadata to foundation docs?
   - Consider: Validate structure against document schemas?

2. **Resource Sheets** (3 files per element) - Optional validation
   - Current: validate_against_code checks code consistency
   - Gap: No UDS schema validation

3. **Standards Files** (3 files) - Currently no validation
   - Consider: Define schema for standards documents?
   - Consider: Validate patterns format consistency?

4. **Quickref** (1 file) - Currently no validation
   - Consider: Define quickref schema?
   - Consider: Validate completeness (required sections present)?

5. **Changelog** (1 file) - Has jsonschema validation
   - Question: Does jsonschema align with Papertrail UDS requirements?
   - Action: Compare existing schema with Papertrail standards

6. **Audit Reports** (1 file per audit) - Validates against standards
   - Question: Should audit reports have UDS metadata?
   - Action: Review if audit reports need workorder tracking

---

**Phase 1 Complete:** All outputs inventoried and documented.

**Next Step:** Wait for papertrail agent and coderef-workflow agent to complete their Phase 1 inventories, then orchestrator will aggregate all findings.
