# CodeRef Document Audit - coderef-docs Analysis

**Server:** coderef-docs
**Path:** C:\Users\willh\.mcp-servers\coderef-docs
**Status:** Complete
**Date:** 2026-01-01

---

## Foundation Docs

### How Used
GENERATOR: coderef-docs is the primary generator for foundation docs via `generate_foundation_docs` and `generate_individual_doc` tools. Uses POWER framework templates (Purpose, Overview, What/Why/When, Examples, References) for README, ARCHITECTURE, API, COMPONENTS, SCHEMA. v3.2.0+ integrates with @coderef/core CLI via extractors.py to inject real code intelligence (APIs, schemas, components) into templates during generation. CLAUDE.md is referenced as architecture context when generating docs.

### Strengths
- POWER framework ensures consistency across all foundation docs
- Sequential generation (5 calls, ~250-350 lines each) prevents timeout errors
- Context injection from .coderef/ data provides real code intelligence vs placeholders
- Templates are well-structured and follow proven documentation patterns
- CLAUDE.md provides comprehensive system overview for agents

### Weaknesses
- Foundation docs stored in coderef/foundation-docs/ vs root (inconsistent locations)
- No versioning or timestamps in generated docs
- Context injection requires @coderef/core CLI - graceful degradation to placeholders if unavailable
- COMPONENTS.md may not be relevant for non-UI projects
- No validation of generated docs against schemas

### Add/Remove Recommendations
- **ADD:** Metadata block (version, generated_date, generated_by) to all foundation docs
- **ADD:** Conditional COMPONENTS.md generation (skip for CLI/backend projects)
- **ADD:** Post-generation validation against doc schemas
- **ADD:** Cross-references between foundation docs (e.g., ARCHITECTURE.md references SCHEMA.md)
- **REMOVE:** Duplicate foundation doc locations - standardize to single location
- **ADD:** Foundation doc refresh detection (warn if stale vs codebase)

---

## Standards Docs

### How Used
GENERATOR & AUDITOR: coderef-docs generates standards docs via `establish_standards` tool (v3.3.0+ uses .coderef/index.json for 10x performance boost). Analyzes codebase to extract UI/behavior/UX patterns and creates ui-patterns.md, behavior-patterns.md, ux-patterns.md, standards-overview.md. `audit_codebase` and `check_consistency` tools validate code against established standards and provide 0-100 compliance scores.

### Strengths
- Standards generation is codebase-driven (discovers actual patterns vs theoretical)
- Fast path (.coderef/ integration) reduces generation time from 5-60s to ~50ms
- Compliance auditing provides actionable feedback with severity levels
- Pre-commit check_consistency tool acts as quality gate
- Standards docs follow consistent markdown format

### Weaknesses
- Standards docs are UI/UX focused - not applicable to CLI/backend tools
- No standards for Python code patterns, error handling, or testing conventions
- Standards establishment requires manual trigger - not automated
- No versioning or evolution tracking for standards
- Audit reports lack actionable fix suggestions (only identifies violations)

### Add/Remove Recommendations
- **ADD:** Conditional standards generation (skip ui-patterns/ux-patterns for non-UI projects)
- **ADD:** python-patterns.md for code style, error handling, async patterns
- **ADD:** test-patterns.md for testing conventions
- **ADD:** api-patterns.md for REST/GraphQL endpoint design
- **ADD:** Automated fix suggestions in audit_codebase output
- **ADD:** Standards versioning and changelog
- **ADD:** Auto-trigger standards refresh on major codebase changes

---

## Workflow/Workorder Docs

### How Used
CONSUMER & UPDATER: coderef-docs is called by coderef-workflow at feature completion via `record_changes` and `update_all_documentation` tools. Reads context.json and plan.json to understand feature scope. Updates CHANGELOG.json with workorder tracking. Generates DELIVERABLES.md via coderef-workflow (not coderef-docs directly). Does NOT generate plan.json or communication.json (those are coderef-workflow responsibility).

### Strengths
- Smart changelog recording with git auto-detection reduces manual effort
- CHANGELOG.json is structured (machine-readable) vs plain text
- Workorder tracking links changes to features
- record_changes provides AI confirmation before writing

### Weaknesses
- No direct integration with plan.json validation
- DELIVERABLES.md generation is split between servers (coderef-workflow creates template, coderef-docs updates it)
- No automated cross-referencing between CHANGELOG and archived features
- Missing 'what changed in this workorder' summarization tool
- No support for multi-agent DELIVERABLES aggregation (that's in coderef-workflow)

### Add/Remove Recommendations
- **ADD:** Tool to generate workorder summary from CHANGELOG entries (filter by workorder_id)
- **ADD:** Cross-reference links in CHANGELOG to archived features
- **ADD:** Validation hook for plan.json when referenced in changelog
- **CLARIFY:** Document which server owns which workflow docs (avoid overlap with coderef-workflow)
- **ADD:** Support for 'release notes' generation from multiple changelog entries

---

## CodeRef Analysis Outputs

### How Used
CONSUMER (v3.2.0+): coderef-docs uses .coderef/ outputs for context injection during foundation doc generation. extractors.py calls @coderef/core CLI to extract APIs (index.json → endpoints), schemas (index.json → entities/relationships), components (index.json → React components). Displays extracted data alongside templates for Claude to populate with real information. Standards generation (v3.3.0+) reads .coderef/index.json for fast component discovery.

### Strengths
- Context injection eliminates placeholder docs - generates real, accurate documentation
- .coderef/index.json provides fast lookups (~50ms vs 5-60s full scan)
- Graceful degradation if .coderef/ unavailable
- Integration proven with 27/30 proof tests passing (90% pass rate)

### Weaknesses
- Requires @coderef/core CLI to be installed and configured (CODEREF_CLI_PATH env var)
- Only uses index.json - ignores other rich outputs (patterns.json, coverage.json, complexity.json, diagrams)
- No validation that .coderef/ data is fresh (could be stale vs current code)
- Extraction logic duplicated between foundation_generator.py and standards_generator.py

### Add/Remove Recommendations
- **ADD:** Use reports/patterns.json in standards generation for richer pattern detection
- **ADD:** Use reports/coverage.json to highlight untested code in documentation
- **ADD:** Use diagrams/*.mmd in ARCHITECTURE.md generation (embed dependency diagrams)
- **ADD:** Drift detection before doc generation (warn if .coderef/ stale)
- **ADD:** Centralized extraction helper (avoid duplication in generators)
- **ADD:** Support for reading .coderef/context.md as base for ARCHITECTURE.md
- **ADD:** Metadata validation (.coderef/metadata.json check for freshness)

---

## Additional Comments

### Improvements
- Unify .coderef/ consumption across all generators (single extraction helper)
- Add --validate flag to all generation tools (validate output against schemas)
- Create coderef-docs-specific test suite that validates generated docs (structure, content, cross-references)
- Improve error messages when @coderef/core CLI unavailable
- Add progress indicators for long-running generations
- Support incremental doc updates (only regenerate changed sections vs full rewrites)

### Weaknesses
- Documentation generation lacks validation - no schema checking for output structure
- POWER framework is not formally documented (agents learn by example)
- Context injection requires external dependency (@coderef/core) - should be optional MCP integration
- No 'doc health' scoring (similar to code health)
- Missing user-facing guides for common doc workflows
- Standards audit lacks auto-fix capabilities (only detects issues)

### Other
- Consider creating 'coderef-docs-dev-guide.md' for agents extending doc generators
- Current CLAUDE.md is lean (227 lines, v3.2.0 refactor) but could benefit from more generator implementation examples
- Need clarity on coderef-docs vs coderef-workflow responsibilities (some overlap in deliverables/changelog)
- Explore tighter integration with coderef-context MCP tools (vs CLI wrapper)
- Add support for custom POWER framework sections (beyond the 5 standard sections)

---

**Generated by:** coderef-docs-agent
**Workorder:** WO-DOC-OUTPUT-AUDIT-001
