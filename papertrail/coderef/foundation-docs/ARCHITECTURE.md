---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-FOUNDATION-DOCS-001
generated_by: Claude Code
feature_id: foundation-documentation
doc_type: architecture
---

# Papertrail System Architecture

## System Overview

Papertrail is a Python library and MCP server providing Universal Documentation Standards (UDS) and Resource Sheet Metadata Standards (RSMS v2.0) enforcement for the CodeRef ecosystem.

**Core Components:**
- MCP Server (stdio/HTTP transport)
- 13 Validator Classes (BaseUDSValidator + 12 specialized)
- Schema Validation Engine (JSON Schema Draft-07)
- ValidatorFactory (auto-detection registry)
- TemplateEngine (Jinja2 with extensions)

## Key Components

### 1. MCP Server Layer
**File:** papertrail/server.py
**Responsibility:** Expose validation tools via Model Context Protocol

**Tools:**
- validate_document
- check_all_docs
- validate_resource_sheet
- check_all_resource_sheets
- validate_schema_completeness
- validate_all_schemas
- validate_stub

### 2. Validator Layer
**Files:** papertrail/validators/*.py
**Responsibility:** Validate documents against UDS/RSMS standards

**Hierarchy:**
- BaseUDSValidator (abstract)
  - FoundationDocValidator
  - WorkorderDocValidator
  - SystemDocValidator
  - StandardsDocValidator
  - UserFacingDocValidator
    - UserGuideValidator
    - QuickrefValidator
  - MigrationDocValidator
  - InfrastructureDocValidator
  - SessionDocValidator
  - PlanValidator
  - ResourceSheetValidator
  - GeneralMarkdownValidator

### 3. Schema Layer
**Directory:** schemas/documentation/
**Responsibility:** Define validation rules via JSON Schema

**Schemas:**
- base-frontmatter-schema.json (universal fields)
- foundation-doc-frontmatter-schema.json
- resource-sheet-metadata-schema.json
- user-facing-doc-frontmatter-schema.json
- (+ 6 more category-specific schemas)

### 4. Factory Layer
**File:** papertrail/validators/factory.py
**Responsibility:** Auto-detect validator type from file path/frontmatter

**Detection Methods:**
- Path pattern matching (30+ patterns)
- Frontmatter field detection
- Fallback to GeneralMarkdownValidator

## Design Decisions

### 1. Schema Inheritance with allOf
**Decision:** Use JSON Schema allOf for schema composition
**Alternative:** Duplicate base fields in each schema
**Rationale:** DRY principle, single source of truth for base fields

### 2. Validator Factory Auto-Detection
**Decision:** Auto-detect validator type from path + frontmatter
**Alternative:** Manual validator selection
**Rationale:** Better UX, reduces errors, enables batch operations

### 3. Score-Based Validation (0-100)
**Decision:** Calculate weighted scores from errors/warnings
**Alternative:** Binary pass/fail
**Rationale:** Actionable quality metrics, gradual quality improvement

**Scoring Formula:**
```
score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
score = max(0, score)
```

### 4. Completeness Metric (Section Coverage)
**Decision:** Calculate 0-100% completeness from required sections
**Alternative:** Boolean section checks
**Rationale:** Progress tracking, prioritize missing sections

## Integration Points

### with coderef-docs
- Real-time validation before doc generation
- Template sync via SchemaSyncTool
- Quality gate: score >= 90

### with coderef-workflow
- Resource sheet validation post-creation
- Workorder doc validation
- Plan.json validation

### with coderef-context
- Code example validation (API/COMPONENTS docs)
- Pattern detection for standards docs

### with Git Workflows
- Pre-commit hooks
- GitHub Actions validation
- PR comment posting

---

**Last Updated:** 2026-01-13
**Maintained by:** Papertrail Team
