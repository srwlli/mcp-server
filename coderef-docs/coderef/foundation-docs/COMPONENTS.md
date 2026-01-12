# Components Reference - coderef-docs

**Project:** coderef-docs (MCP Server)
**Version:** 3.7.0
**Last Updated:** 2026-01-11
**Architecture:** Modular Python MCP Server

---

## Purpose

This document catalogs the software components (modules, generators, handlers, utilities) that make up the coderef-docs MCP server, with emphasis on the direct validation integration (v3.7.0) and modular architecture.

## Overview

The coderef-docs server is organized into 9 main component categories with clear separation of concerns. The v3.7.0 release introduced direct validation integration where tools execute validation at runtime (not Claude).

**Component Hierarchy:**
```
server.py (MCP entry point)
├── tool_handlers.py (13 tool handlers with direct validation)
├── generators/ (12+ document generators)
├── utils/ (validation_helpers.py for direct validation)
├── validation.py (input validation)
├── error_responses.py (error handling)
├── logger_config.py (logging)
├── constants.py (centralized constants)
└── mcp_integration.py (.coderef/ file reading)
```

---

## 1. Core Server Components

### server.py

**Purpose:** MCP server entry point and tool registration

**Location:** `server.py` (498 lines)

**Responsibilities:**
- Initialize MCP server with stdio transport
- Register 13 tools with JSON schemas
- Route tool calls to handlers via registry pattern
- Set TEMPLATES_DIR for generators

**Key Functions:**
- `list_tools()` - Returns 13 tool schemas (list_templates, get_template, generate_foundation_docs, generate_individual_doc, add_changelog_entry, record_changes, generate_quickref_interactive, generate_resource_sheet, establish_standards, audit_codebase, check_consistency, validate_document, check_document_health)
- `call_tool()` - Dispatches to tool_handlers.TOOL_HANDLERS registry
- `main()` - Runs MCP server loop

**Dependencies:** mcp.server, tool_handlers, constants

**Version:** v2.0.0 (schema version 1.0.0, MCP 1.0)

---

### tool_handlers.py

**Purpose:** MCP tool handler implementations with **direct validation integration** (v3.7.0)

**Location:** `tool_handlers.py` (925+ lines, modified in rework)

**Responsibilities:**
- Handle all 13 MCP tool calls
- **NEW (v3.7.0):** Execute validation at runtime for foundation + standards docs
- Save files directly (not via Claude)
- Write validation metadata to frontmatter `_uds` sections
- Return simple result messages (NO instruction blocks)

**Key Handlers:**
- `handle_generate_individual_doc()` - Foundation doc generation with direct validation (lines 242-395)
- `handle_establish_standards()` - Standards generation with direct validation (lines 760-879)
- `handle_generate_foundation_docs()` - Sequential foundation doc orchestration (lines 158-237)
- `handle_record_changes()` - Smart changelog with git auto-detection
- `handle_generate_resource_sheet()` - Composable module-based docs
- `handle_audit_codebase()` - Standards compliance auditing
- `handle_check_consistency()` - Pre-commit quality gate

**Direct Validation Pattern (v3.7.0):**
```python
# Foundation docs (lines 320-395)
output_path.write_text(doc_content, encoding='utf-8')  # Tool saves file

from papertrail.validators.foundation import FoundationDocValidator
from utils.validation_helpers import write_validation_metadata_to_frontmatter

validator = FoundationDocValidator()
validation_result = validator.validate_file(output_path)  # Tool runs validator
write_validation_metadata_to_frontmatter(output_path, validation_result)  # Tool writes metadata

return [TextContent(type="text", text=f"✅ Generated and saved {template_name}.md\n📊 Validation: {validation_score}/100")]
```

**TOOL_HANDLERS Registry:**
```python
TOOL_HANDLERS = {
    "list_templates": handle_list_templates,
    "get_template": handle_get_template,
    "generate_foundation_docs": handle_generate_foundation_docs,
    "generate_individual_doc": handle_generate_individual_doc,
    "add_changelog_entry": handle_add_changelog_entry,
    "record_changes": handle_record_changes,
    "generate_quickref_interactive": handle_generate_quickref_interactive,
    "generate_resource_sheet": handle_generate_resource_sheet,
    "establish_standards": handle_establish_standards,
    "audit_codebase": handle_audit_codebase,
    "check_consistency": handle_check_consistency,
    "validate_document": handle_validate_document,
    "check_document_health": handle_check_document_health,
}
```

**Dependencies:** generators.*, validation, error_responses, papertrail.validators, utils.validation_helpers

---

## 2. Generator Components

### BaseGenerator

**Purpose:** Abstract base class for all document generators

**Location:** `generators/base_generator.py`

**Responsibilities:**
- Template loading and preparation
- Project path validation
- Output path determination
- Common generation utilities

**Key Methods:**
- `prepare_generation()` - Validates project, returns context
- `read_template()` - Loads POWER framework template
- `get_doc_output_path()` - Determines save location (README.md in root, others in coderef/foundation-docs/)

**Subclasses:** FoundationGenerator, StandardsGenerator, QuickrefGenerator, ResourceSheetGenerator

---

### FoundationGenerator

**Purpose:** Generate foundation documentation (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)

**Location:** `generators/foundation_generator.py`

**Responsibilities:**
- Sequential foundation doc generation workflow
- Integration with .coderef/ for code intelligence
- Template rendering with POWER framework
- **NEW (v3.7.0):** Direct validation integration for 5 foundation docs

**Key Methods:**
- `generate_with_uds()` - Generate doc with UDS frontmatter (optional workorder tracking)
- `get_template_info()` - Returns template metadata and save location

**Templates:**
- readme.txt
- architecture.txt
- api.txt
- schema.txt
- components.txt

**Output Paths:**
- README.md → project root
- All others → coderef/foundation-docs/

---

### StandardsGenerator

**Purpose:** Extract and document coding standards from codebase

**Location:** `generators/standards_generator.py`

**Responsibilities:**
- Scan codebase for UI/behavior/UX patterns
- Leverage .coderef/index.json for 10x performance (v3.3.0)
- Generate 3 markdown files with discovered patterns
- **NEW (v3.7.0):** Direct validation integration for all 3 standards files

**Key Methods:**
- `save_standards()` - Generates and saves all 3 standards files
- `_read_coderef_index()` - Fast path using .coderef/ structure
- `_analyze_patterns()` - Pattern detection and categorization

**Output Files:**
- ui-patterns.md
- behavior-patterns.md
- ux-patterns.md

**Scan Depths:**
- quick: ~1-2 min (common patterns)
- standard: ~3-5 min (comprehensive, default)
- deep: ~10-15 min (exhaustive)

---

### ChangelogGenerator

**Purpose:** Manage CHANGELOG.json entries with git auto-detection

**Location:** `generators/changelog_generator.py`

**Responsibilities:**
- Add manual changelog entries
- Smart agentic recording with git auto-detection
- Suggest change_type and severity from git history
- JSON schema validation

**Key Methods:**
- `add_entry()` - Manual entry with full details
- `record_changes()` - Smart agentic recording (recommended)
- `suggest_change_type()` - Analyzes commit messages
- `calculate_severity()` - Determines severity from file scope

**Schema Validation:**
```python
{
  "version": "^\d+\.\d+\.\d+$",
  "change_type": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"],
  "severity": ["critical", "major", "minor", "patch"]
}
```

---

### QuickrefGenerator

**Purpose:** Interactive quickref guide generation for any app type

**Location:** `generators/quickref_generator.py`

**Responsibilities:**
- Interview-based workflow (Q&A with user)
- Universal quickref pattern (150-250 lines)
- Supports 5 app types (CLI, Web, API, Desktop, Library)
- Generates scannable, copy-paste friendly documentation

**Output:** quickref.md (coderef/user/)

---

### ResourceSheetGenerator

**Purpose:** Composable module-based technical documentation

**Location:** `generators/resource_sheet_generator.py` (WO-RESOURCE-SHEET-MCP-TOOL-001)

**Responsibilities:**
- Auto-detect code characteristics (~20+ traits)
- Select appropriate modules from ~30-40 composable modules
- Generate 3 synchronized formats: Markdown + JSON Schema + JSDoc
- 50% auto-fill rate (Phase 1 target)

**Modes:**
- reverse-engineer: Analyze existing code (default)
- template: Scaffold new code
- refresh: Update existing docs

**Modules (Phase 1):**
- Universal modules (4): architecture, integration, testing stub, performance stub
- Conditional modules (11+): Planned for Phase 2

---

### PlanningGenerator

**Purpose:** Generate 10-section implementation plans

**Location:** `generators/planning_generator.py`

**Responsibilities:**
- Create plan.json with META_DOCUMENTATION + 9 content sections
- Workorder ID generation and tracking
- Integration with analysis.json and context.json
- Plan validation (score 0-100)

**Output:** plan.json (coderef/workorder/{feature}/)

**Sections:**
1. META_DOCUMENTATION
2. 0_PREPARATION
3. 1_EXECUTIVE_SUMMARY
4. 2_RISK_ASSESSMENT
5. 3_CURRENT_STATE_ANALYSIS
6. 4_KEY_FEATURES
7. 5_TASK_ID_SYSTEM
8. 6_IMPLEMENTATION_PHASES
9. 7_TESTING_STRATEGY
10. 8_SUCCESS_CRITERIA

---

### HandoffGenerator

**Purpose:** Generate agent handoff context files (claude.md)

**Location:** `generators/handoff_generator.py`

**Responsibilities:**
- Auto-populate 80%+ of claude.md from plan.json, analysis.json, git history
- Reduce handoff time from 20-30 min to < 5 min
- Support full and minimal modes
- UDS frontmatter integration

**Output:** claude.md (coderef/workorder/{feature}/)

---

### AuditGenerator

**Purpose:** Audit codebase for standards violations

**Location:** `generators/audit_generator.py`

**Responsibilities:**
- Compare code against established standards
- Generate compliance reports with 0-100 score
- Identify violations by severity (critical/major/minor)
- Suggest automated fixes

**Output:** Audit report (JSON format)

---

## 3. Utility Components

### validation_helpers.py (NEW in v3.7.0)

**Purpose:** Helper functions for direct validation integration

**Location:** `utils/validation_helpers.py` (205 lines)

**Responsibilities:**
- Write validation metadata to markdown frontmatter
- Extract existing frontmatter
- Add `_uds` validation section
- Preserve file content while updating metadata

**Key Function:**
```python
def write_validation_metadata_to_frontmatter(
    file_path: Path,
    validation_result: Any
) -> None:
    """
    Write validation metadata to frontmatter _uds section.

    Reads file, extracts frontmatter, adds:
    - validation_score
    - validation_errors
    - validation_warnings
    - validated_at
    - validator

    Preserves all existing content.
    """
```

**Frontmatter Format:**
```yaml
---
generated_by: coderef-docs
template: readme
date: 2026-01-11T18:30:00Z
_uds:
  validation_score: 95
  validation_errors: []
  validation_warnings: ["Minor issue"]
  validated_at: 2026-01-11T18:30:00Z
  validator: FoundationDocValidator
---
```

**Usage:**
- Foundation docs (5 templates)
- Standards docs (3 files)
- Future: User docs, workorder MD docs

---

### validation.py

**Purpose:** Input validation for MCP tool parameters

**Location:** `validation.py`

**Responsibilities:**
- Validate project paths (security: prevent path traversal)
- Validate template names (enum checking)
- Validate version format (semver pattern)
- Validate changelog inputs (required fields)

**Key Functions:**
- `validate_project_path_input()` - Path validation + security
- `validate_template_name_input()` - Enum validation
- `validate_version_format()` - Regex pattern matching
- `validate_changelog_inputs()` - Required field checking

**Security Features:**
- Path traversal prevention
- Maximum path length (4096 chars)
- Allowed file extensions checking
- Directory exclusion (node_modules, .git, etc.)

---

### error_responses.py

**Purpose:** Standardized error response factory

**Location:** `error_responses.py`

**Responsibilities:**
- Create consistent MCP error responses
- Map Python exceptions to JSON-RPC error codes
- Provide user-friendly error messages

**Error Codes:**
- -32600: Invalid Request
- -32601: Method not found
- -32602: Invalid params
- -32603: Internal error

---

### logger_config.py

**Purpose:** Structured logging configuration

**Location:** `logger_config.py`

**Responsibilities:**
- Configure Python logging with structured output
- JSON logging for production
- Tool invocation logging (@log_invocation decorator)
- Error tracking with context

**Key Features:**
- Automatic tool call logging
- Request/response tracking
- Error context preservation
- Configurable log levels

---

### constants.py

**Purpose:** Centralized configuration constants

**Location:** `constants.py`

**Responsibilities:**
- Define all hardcoded paths and file names
- Centralize magic strings
- Provide enums for validation

**Key Constants:**
- `Paths.TEMPLATES_DIR` = "templates/power"
- `Paths.FOUNDATION_DOCS` = "coderef/foundation-docs"
- `Paths.USER_DOCS` = "coderef/user"
- `Paths.STANDARDS_DIR` = "coderef/standards"
- `Files.README` = "README.md"
- Template names, change types, severity levels

---

### mcp_integration.py

**Purpose:** .coderef/ file reading integration

**Location:** `mcp_integration.py`

**Responsibilities:**
- Check .coderef/ resource availability
- Map templates to required .coderef/ files
- Provide context instructions for Claude
- Format missing resource warnings

**Key Functions:**
- `check_coderef_resources()` - Validates file existence
- `get_template_context_files()` - Template-to-file mapping
- `get_context_instructions()` - Template-specific guidance

**Template Mappings:**
- README: context.md, patterns.json
- ARCHITECTURE: context.json, graph.json, diagrams/
- API: index.json, patterns.json
- SCHEMA: index.json, context.json
- COMPONENTS: index.json, patterns.json

---

## 4. Validator Components

### Papertrail Validators (External Package)

**Purpose:** UDS-compliant document validation

**Package:** papertrail (external dependency)

**Validators:**
- `FoundationDocValidator` - Validates README, ARCHITECTURE, API, SCHEMA, COMPONENTS
- `StandardsDocValidator` - Validates ui-patterns, behavior-patterns, ux-patterns

**Integration (v3.7.0):**
- Imported by tool_handlers.py
- Called at tool runtime (not by Claude)
- Results written to frontmatter `_uds` section via validation_helpers.py

**Validation Threshold:** Score >= 90

---

### plan_validator.py

**Purpose:** Validate implementation plans against quality checklist

**Location:** `generators/plan_validator.py`

**Responsibilities:**
- Score plans 0-100 based on completeness
- Identify issues by severity (critical/major/minor)
- Provide fix suggestions
- Enable iterative refinement

**Output:** Validation result with score, errors, warnings

---

### schema_validator.py

**Purpose:** JSON schema validation for structured documents

**Location:** `schema_validator.py`

**Responsibilities:**
- Validate JSON documents against schemas
- Used by changelog, planning, context files
- Standard jsonschema library integration

---

## 5. Templates

### POWER Framework Templates

**Location:** `templates/power/`

**Templates:**
- readme.txt
- architecture.txt
- api.txt
- schema.txt
- components.txt
- user-guide.txt
- my-guide.txt
- features.txt

**Structure:**
```
framework: POWER
purpose: [Document purpose]
output: [Required format]
work: [What to analyze]
examples: [Sample content]
requirements: [Must-have sections]
save_as: [Output filename]
store_as: [Summary variable]
```

---

## 6. Test Components

### Direct Validation Tests (v3.7.0)

**Location:** `tests/test_direct_validation.py` (356 lines, 6 tests)

**Test Classes:**
1. **TestFoundationDocDirectValidation** - Verifies tool saves files and runs validators
2. **TestStandardsDocDirectValidation** - Verifies all 3 standards files validated
3. **TestNoInstructionBlocks** - CRITICAL: Ensures NO instruction blocks in output
4. **TestValidationRunsAtToolRuntime** - Verifies call order (save → validate → metadata)

**Test Results:** 6/6 passing (100%)

---

### Unit Tests

**Location:** `tests/unit/`

**Coverage:**
- `test_changelog_generator.py` - Changelog functionality
- `test_foundation_generator.py` - Foundation doc generation
- `test_planning_generator.py` - Planning workflows

---

## 7. Configuration Files

### .mcp.json

**Purpose:** MCP server configuration

**Location:** `C:\Users\willh\.mcp.json`

**Configuration:**
```json
{
  "coderef-docs": {
    "command": "python",
    "args": ["C:/Users/willh/.mcp-servers/coderef-docs/server.py"],
    "cwd": "C:/Users/willh/.mcp-servers/coderef-docs"
  }
}
```

---

### pyproject.toml

**Purpose:** Python project configuration

**Dependencies:**
- mcp >= 1.0
- jsonschema >= 4.0
- papertrail (for validators)
- pytest >= 8.0 (dev)

---

## 8. Data Structures

### CHANGELOG.json

**Purpose:** Structured version history

**Location:** `coderef/CHANGELOG.json`

**Schema:**
```json
{
  "version": "3.7.0",
  "date": "2026-01-11",
  "changes": [
    {
      "type": "feature",
      "severity": "major",
      "title": "Direct validation integration",
      "description": "Tool executes validation at runtime",
      "files": ["tool_handlers.py"],
      "workorder_id": "WO-CODEREF-DOCS-DIRECT-VALIDATION-001"
    }
  ]
}
```

---

### plan.json

**Purpose:** 10-section implementation plan

**Location:** `coderef/workorder/{feature}/plan.json`

**Sections:** META_DOCUMENTATION + 9 content sections

**Validation:** plan_validator.py (scores 0-100)

---

## 9. Architecture Patterns

### Direct Validation Pattern (v3.7.0)

**Pattern:**
1. Tool generates content
2. Tool saves file to disk
3. Tool runs validator (FoundationDocValidator or StandardsDocValidator)
4. Tool writes `_uds` metadata to frontmatter
5. Tool returns simple result (NO instruction blocks)

**Benefits:**
- Fast (validation at tool runtime)
- No Claude execution needed
- Machine-readable metadata
- Simple user feedback

**Coverage:** Foundation docs (5) + Standards docs (3) = 8 validated outputs

---

### Registry Pattern

**Pattern:** Tool handlers registered in TOOL_HANDLERS dict

**Benefits:**
- Clean separation of concerns
- Easy to test handlers independently
- Maintainable routing logic

---

### Template-Based Generation

**Pattern:** POWER framework templates + context injection

**Benefits:**
- Consistent documentation structure
- Reusable across projects
- AI-friendly format

---

## Component Dependencies

```
server.py
├─ tool_handlers.py
│  ├─ generators/*
│  │  ├─ base_generator.py
│  │  ├─ foundation_generator.py
│  │  ├─ standards_generator.py
│  │  └─ ...
│  ├─ utils/validation_helpers.py (NEW v3.7.0)
│  ├─ papertrail.validators (external)
│  └─ validation.py
├─ constants.py
├─ error_responses.py
├─ logger_config.py
└─ mcp_integration.py
```

---

## Version History

- v3.7.0 (2026-01-11): Direct validation integration (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)
- v3.6.0 (2026-01-10): Papertrail validators integration (instruction-based, deprecated)
- v3.5.0: .coderef/ integration for foundation docs
- v3.4.0: Resource sheet MCP tool
- v3.3.0: .coderef/ fast path for standards

---

## References

- **API.md** - MCP tool endpoints
- **ARCHITECTURE.md** - System design
- **SCHEMA.md** - Data structures
- **README.md** - User guide

---

**Maintained by:** willh, Claude Code AI
**Last Updated:** 2026-01-11 (v3.7.0 - Direct Validation Integration)
**Status:** ✅ Production Ready
