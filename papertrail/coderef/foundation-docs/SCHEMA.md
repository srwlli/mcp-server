---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-FOUNDATION-DOCS-001
generated_by: Claude Code
feature_id: foundation-documentation
doc_type: schema
---

# Papertrail Validation Schemas

## Data Models

### Base Frontmatter Schema
**File:** `base-frontmatter-schema.json`
**Purpose:** Universal fields required for all markdown documents

**Fields:**
- agent: string (Creator/updater name)
- date: string (YYYY-MM-DD format)
- task: enum (CREATE, UPDATE, REVIEW, etc.)

### Foundation Doc Schema
**File:** `foundation-doc-frontmatter-schema.json`  
**Purpose:** Foundation documentation (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)

**Additional Fields:**
- workorder_id: string (WO-{CATEGORY}-###)
- generated_by: string (MCP server attribution)
- feature_id: string (Feature identifier)
- doc_type: enum (readme, architecture, api, schema, components)

### Resource Sheet Schema  
**File:** `resource-sheet-metadata-schema.json`
**Purpose:** RSMS v2.0 compliant resource sheets

**Additional Fields:**
- subject: string (Component name)
- parent_project: string (Project name)
- category: enum (service, controller, model, etc.)
- version: string (Semver format)

### User-Facing Doc Schema
**File:** `user-facing-doc-frontmatter-schema.json`
**Purpose:** User guides, tutorials, FAQs

**Additional Fields:**
- audience: string (Target audience)
- doc_type: enum (guide, tutorial, faq, quickstart, reference, troubleshooting)
- difficulty: enum (beginner, intermediate, advanced)

## Field Descriptions

### Common Fields
- agent: Who created/updated the document
- date: When it was created/updated (quoted string in YAML)
- task: What action was performed

### Workorder Fields  
- workorder_id: Links to implementation workorder
- feature_id: Feature being implemented
- generated_by: Which MCP server generated the doc

## Validation Rules

### Date Format
Must be quoted string in YAML frontmatter: `date: "2026-01-13"`

### Workorder ID Format
Pattern: `WO-{CATEGORY}-{ID}-###`
Example: `WO-AUTH-SYSTEM-001`

### Version Format (RSMS)
Must be valid semver: `1.0.0`, `2.1.3`, etc.

## Relationships

**Schema Inheritance:**
- All schemas extend base-frontmatter-schema.json
- Category-specific schemas add required fields
- Type-specific fields are optional

---

**Last Updated:** 2026-01-13
**Maintained by:** Papertrail Team
