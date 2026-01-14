# Components Reference - coderef-docs

**Project:** coderef-docs (MCP Server)
**Version:** 4.0.0
**Last Updated:** 2026-01-13
**Architecture:** Modular Python MCP Server with MCP Orchestration

---

## Purpose

This document catalogs the software components (modules, generators, handlers, utilities, orchestrators) that make up the coderef-docs MCP server, with emphasis on the MCP integration layer (v4.0.0), user docs automation, and modular architecture.

## Overview

The coderef-docs server is organized into 11 main component categories with clear separation of concerns. The v4.0.0 release introduced:
- **MCP Orchestration Layer** - Centralized MCP tool calling with caching
- **User Docs Automation** - 3 new generators with 75%+ auto-fill rate
- **Standards Enhancement** - Semantic pattern analysis with frequency tracking
- **Tool Consolidation** - Clear hierarchy with [INTERNAL] and [DEPRECATED] markings

**Component Hierarchy:**
```
server.py (MCP entry point)
├── tool_handlers.py (16 tool handlers with MCP integration)
├── mcp_orchestrator.py (MCP tool calling layer - NEW v4.0.0)
├── mcp_integration.py (.coderef/ resource reading)
├── generators/ (14+ document generators)
│   ├── user_guide_generator.py (NEW v4.0.0)
│   └── {13 other generators}
├── utils/ (validation_helpers.py)
├── validation.py (input validation)
├── error_responses.py (error handling)
├── logger_config.py (logging)
└── constants.py (centralized constants)
```

---

## 1. Core Server Components

### server.py

**Purpose:** MCP server entry point and tool registration

**Location:** `server.py` (543 lines, updated v4.0.0)

**Responsibilities:**
- Initialize MCP server with stdio transport
- Register 16 tools with JSON schemas (up from 13 in v3.7.0)
- Route tool calls to handlers via registry pattern
- Set TEMPLATES_DIR for generators

**Key Functions:**
- `list_tools()` - Returns 16 tool schemas:
  - **Utility:** list_templates, get_template
  - **Foundation Docs:** generate_foundation_docs, generate_individual_doc (INTERNAL), coderef_foundation_docs (DEPRECATED)
  - **User Docs (NEW v4.0.0):** generate_my_guide, generate_user_guide, generate_features
  - **Changelog:** add_changelog_entry, record_changes
  - **Advanced:** generate_quickref_interactive, generate_resource_sheet
  - **Standards:** establish_standards, audit_codebase, check_consistency
  - **Validation:** validate_document, check_document_health
- `call_tool()` - Dispatches to tool_handlers.TOOL_HANDLERS registry
- `main()` - Runs MCP server loop

**Dependencies:** mcp.server, tool_handlers, constants

**Version:** v2.0.0 (schema version 1.0.0, MCP 1.0)

---

### tool_handlers.py

**Purpose:** MCP tool handler implementations with MCP orchestration integration (v4.0.0)

**Location:** `tool_handlers.py` (1,200+ lines, enhanced v4.0.0)

**Responsibilities:**
- Handle all 16 MCP tool calls
- Orchestrate MCP tool calling via mcp_orchestrator.py (NEW v4.0.0)
- Perform drift detection before foundation doc generation (NEW v4.0.0)
- Extract tools/commands for user docs automation (NEW v4.0.0)
- Execute validation at runtime for foundation + standards docs
- Save files directly (not via Claude)
- Write validation metadata to frontmatter `_uds` sections

**Key Handlers:**

**Foundation Documentation (3 tools):**
- `handle_generate_foundation_docs()` - Orchestrates sequential generation with drift detection
  - NEW v4.0.0: Checks drift severity (none ≤10%, standard >10-50%, severe >50%)
  - Warns user if index is stale
  - Calls generate_individual_doc 5 times sequentially
- `handle_generate_individual_doc()` - [INTERNAL] Foundation doc generation with validation
  - Called by generate_foundation_docs orchestrator
  - Not recommended for direct use
- `handle_coderef_foundation_docs()` - [DEPRECATED] Old foundation docs tool
  - Replaced by generate_foundation_docs in v4.0.0
  - Will be removed in v5.0.0

**User Documentation (4 tools - NEW v4.0.0):**
- `handle_generate_my_guide()` - Auto-generated developer quick-start
  - Extracts MCP tools from .coderef/index.json (handle_* functions)
  - Scans slash commands from .claude/commands/
  - Categorizes tools (Documentation, Changelog, Standards, Testing)
  - 75%+ auto-fill rate
  - Output: my-guide.md (60-80 lines)
- `handle_generate_user_guide()` - Comprehensive 10-section onboarding guide
  - Leverages .coderef/ data for Prerequisites, Architecture, Tools
  - Auto-generates Examples and Best Practices
  - 75%+ auto-fill rate
  - Output: USER-GUIDE.md (200+ lines)
- `handle_generate_features()` - Feature inventory documentation
  - Scans coderef/workorder/ and coderef/archived/
  - Extracts workorder IDs and status from plan.json
  - Generates executive summary with metrics
  - 75%+ auto-fill rate
  - Output: FEATURES.md (100+ lines)
- `handle_generate_quickref_interactive()` - Interactive quickref generation
  - Interview-based workflow for any app type (CLI, Web, API, Desktop, Library)
  - Universal quickref pattern (150-250 lines)
  - Output: quickref.md

**Changelog (2 tools):**
- `handle_record_changes()` - Smart agentic recording with git auto-detection
- `handle_add_changelog_entry()` - Manual changelog entry

**Standards (3 tools):**
- `handle_establish_standards()` - Standards extraction with MCP semantic patterns
  - NEW v4.0.0: Uses mcp_orchestrator.call_coderef_patterns()
  - Pattern frequency tracking (e.g., "async_function: 45 occurrences")
  - Consistency violation detection
  - Quality improvement: 55% (regex-only) → 80%+ (with MCP patterns)
- `handle_audit_codebase()` - Standards compliance auditing (0-100 score)
- `handle_check_consistency()` - Pre-commit quality gate

**Advanced (1 tool):**
- `handle_generate_resource_sheet()` - Composable module-based docs

**Validation (2 tools):**
- `handle_validate_document()` - UDS validation
- `handle_check_document_health()` - Doc health score

**Utility (2 tools):**
- `handle_list_templates()` - Shows templates + MCP status (NEW v4.0.0)
  - Displays "✅ MCP Available" or "⚠️ MCP Unavailable"
  - Health check < 100ms
- `handle_get_template()` - Get specific template by name

**MCP Orchestration Pattern (v4.0.0):**
```python
from mcp_orchestrator import call_coderef_patterns, check_drift

# Drift detection before doc generation
drift_result = await check_drift(project_path)
if drift_result["severity"] == "severe":
    return [TextContent(text=f"⚠️ Warning: Severe drift ({drift_result['drift_percentage']}%)")]

# Semantic pattern analysis for standards
patterns = await call_coderef_patterns(project_path)
frequency = patterns.get("frequency", {})  # {"async_function": 45}
violations = patterns.get("violations", [])
```

**TOOL_HANDLERS Registry:**
```python
TOOL_HANDLERS = {
    "list_templates": handle_list_templates,
    "get_template": handle_get_template,
    "generate_foundation_docs": handle_generate_foundation_docs,
    "generate_individual_doc": handle_generate_individual_doc,  # [INTERNAL]
    "coderef_foundation_docs": handle_coderef_foundation_docs,  # [DEPRECATED]
    "add_changelog_entry": handle_add_changelog_entry,
    "record_changes": handle_record_changes,
    "generate_my_guide": handle_generate_my_guide,  # NEW v4.0.0
    "generate_user_guide": handle_generate_user_guide,  # NEW v4.0.0
    "generate_features": handle_generate_features,  # NEW v4.0.0
    "generate_quickref_interactive": handle_generate_quickref_interactive,
    "generate_resource_sheet": handle_generate_resource_sheet,
    "establish_standards": handle_establish_standards,
    "audit_codebase": handle_audit_codebase,
    "check_consistency": handle_check_consistency,
    "validate_document": handle_validate_document,
    "check_document_health": handle_check_document_health,
}
```

**Dependencies:** generators.*, mcp_orchestrator, mcp_integration, validation, error_responses, papertrail.validators, utils.validation_helpers

---

## 2. MCP Orchestration Layer (NEW v4.0.0)

### mcp_orchestrator.py

**Purpose:** Centralized MCP tool calling with caching for external MCP servers

**Location:** `mcp_orchestrator.py` (210 lines, NEW v4.0.0)

**Responsibilities:**
- Call coderef-context MCP tools (coderef_patterns)
- Cache MCP responses for 15 minutes (pattern analysis expensive)
- Check drift severity (none/standard/severe)
- Resource availability checking
- Graceful degradation if MCP unavailable

**Key Functions:**

```python
async def call_coderef_patterns(
    project_path: str,
    pattern_type: Optional[str] = None,
    use_cache: bool = True
) -> PatternAnalysisResult:
    """
    Call coderef-context coderef_patterns tool with caching.

    Returns:
        {
            "success": True,
            "patterns": [...],
            "frequency": {"async_function": 45, "class_component": 12},
            "violations": [...],
            "cached": False
        }
    """

async def check_drift(
    project_path: str
) -> DriftResult:
    """
    Check .coderef/index.json drift vs current codebase.

    Returns:
        {
            "success": True,
            "drift_percentage": 15.0,
            "severity": "standard",  # none ≤10%, standard >10-50%, severe >50%
            "added": 10,
            "removed": 5,
            "modified": 8,
            "total": 100,
            "message": "⚠️ Warning: Index has moderate drift (15%)..."
        }
    """

async def check_coderef_resources(
    project_path: str,
    template_name: str
) -> ResourceCheckResult:
    """
    Check if .coderef/ resources exist for template.

    Returns:
        {
            "available": True,
            "missing": ["patterns.json"],
            "template_files": ["index.json", "context.md"],
            "message": "✅ All resources available"
        }
    """
```

**Cache Strategy:**
- Pattern analysis cached 15 min (expensive operation)
- Drift checks NOT cached (must be real-time)
- Cache key: `f"{project_path}:{pattern_type}"`

**Error Handling:**
- Graceful fallback if coderef-context unavailable
- Returns `{"success": False, "error": "..."}` instead of throwing
- Allows tools to continue with reduced functionality

**Performance:**
- First call: ~2-5 seconds (actual MCP call)
- Cached calls: < 50ms (in-memory lookup)
- Health check: < 100ms

---

## 3. Generator Components

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

**Subclasses:** FoundationGenerator, UserGuideGenerator (NEW), StandardsGenerator, QuickrefGenerator, ResourceSheetGenerator

---

### FoundationGenerator

**Purpose:** Generate foundation documentation (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)

**Location:** `generators/foundation_generator.py`

**Responsibilities:**
- Sequential foundation doc generation workflow
- Integration with .coderef/ for code intelligence
- Template rendering with POWER framework
- Direct validation integration for 5 foundation docs

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

### UserGuideGenerator (NEW v4.0.0)

**Purpose:** Generate user-facing documentation with 75%+ auto-fill rate

**Location:** `generators/user_guide_generator.py` (420 lines, NEW v4.0.0)

**Responsibilities:**
- Extract MCP tools from .coderef/index.json
- Scan slash commands from .claude/commands/
- Auto-generate examples and workflows
- Create comprehensive onboarding guides
- Feature inventory documentation

**Key Methods:**

```python
def extract_mcp_tools(project_path: Path) -> List[ToolInfo]:
    """
    Extract MCP tools from .coderef/index.json.

    Looks for handle_* functions in tool_handlers.py.
    Categorizes by function (Documentation, Changelog, Standards, Testing).

    Returns:
        [
            {
                "name": "handle_generate_foundation_docs",
                "category": "Documentation",
                "description": "Generate 5 foundation docs"
            }
        ]
    """

def scan_slash_commands(project_path: Path) -> List[CommandInfo]:
    """
    Scan .claude/commands/ directory for slash commands.

    Returns:
        [
            {
                "name": "/generate-docs",
                "file": "generate-docs.txt",
                "description": "Generate foundation docs"
            }
        ]
    """

def generate_my_guide(project_path: Path) -> str:
    """
    Generate my-guide.md (60-80 lines developer quick-start).

    Auto-fill rate: 75%+
    Sections: MCP Tools, Slash Commands, Quick Reference
    """

def generate_user_guide(project_path: Path) -> str:
    """
    Generate USER-GUIDE.md (10-section comprehensive guide).

    Auto-fill rate: 75%+
    Sections: Prerequisites, Installation, Architecture, Tools Reference,
              Commands, Workflows, Best Practices, Troubleshooting, Quick Reference
    """

def generate_features_doc(project_path: Path) -> str:
    """
    Generate FEATURES.md (feature inventory).

    Auto-fill rate: 75%+
    Scans coderef/workorder/ and coderef/archived/
    Extracts workorder IDs, status, completion dates
    Generates executive summary with metrics
    """
```

**Output Files:**
- my-guide.md (coderef/user/)
- USER-GUIDE.md (coderef/user/)
- FEATURES.md (coderef/user/)
- quickref.md (coderef/user/)

**Auto-Fill Strategy:**
- Tools: 100% auto-filled from .coderef/index.json
- Commands: 100% auto-filled from .claude/commands/
- Examples: 50-60% auto-generated from patterns
- Overall: 75%+ auto-fill rate

---

### StandardsGenerator

**Purpose:** Extract and document coding standards from codebase

**Location:** `generators/standards_generator.py` (enhanced v4.0.0)

**Responsibilities:**
- Scan codebase for UI/behavior/UX patterns
- Leverage .coderef/index.json for 10x performance (v3.3.0)
- **NEW v4.0.0:** Use MCP semantic pattern analysis for 80%+ quality
- Generate 3 markdown files with discovered patterns
- Track pattern frequency (e.g., "async_function: 45 occurrences")
- Detect consistency violations (files not following patterns)

**Key Methods:**
- `save_standards()` - Generates and saves all 3 standards files
- `_read_coderef_index()` - Fast path using .coderef/ structure
- `_analyze_patterns()` - Pattern detection and categorization
- **NEW v4.0.0:** `_analyze_patterns_with_mcp()` - Enhanced pattern analysis using coderef_patterns tool
  - Pattern frequency tracking
  - Consistency violation detection
  - Graceful fallback to regex if MCP unavailable

**MCP Integration Pattern (v4.0.0):**
```python
from mcp_orchestrator import call_coderef_patterns

# Try MCP semantic analysis first
patterns = await call_coderef_patterns(project_path, pattern_type="ui_components")

if patterns["success"]:
    # Use semantic patterns with frequency data
    frequency = patterns["frequency"]  # {"async_function": 45}
    violations = patterns["violations"]
    quality_score = 80  # 80%+ quality with MCP
else:
    # Fallback to regex patterns
    patterns = self._regex_fallback_patterns()
    quality_score = 55  # 55% quality without MCP
```

**Output Files:**
- ui-patterns.md (coderef/standards/)
- behavior-patterns.md (coderef/standards/)
- ux-patterns.md (coderef/standards/)

**Scan Depths:**
- quick: ~1-2 min (common patterns)
- standard: ~3-5 min (comprehensive, default)
- deep: ~10-15 min (exhaustive)

**Quality Metrics:**
- With MCP patterns: 80%+ quality
- Without MCP (regex only): 55% quality
- Improvement: +25 percentage points

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

## 4. Utility Components

### validation_helpers.py

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
generated_by: coderef-docs v4.0.0
template: readme
date: 2026-01-13T18:30:00Z
_uds:
  validation_score: 95
  validation_errors: []
  validation_warnings: ["Minor issue"]
  validated_at: 2026-01-13T18:30:00Z
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

**Location:** `mcp_integration.py` (enhanced v4.0.0)

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

## 5. Validator Components

### Papertrail Validators (External Package)

**Purpose:** UDS-compliant document validation

**Package:** papertrail (external dependency)

**Validators:**
- `FoundationDocValidator` - Validates README, ARCHITECTURE, API, SCHEMA, COMPONENTS
- `StandardsDocValidator` - Validates ui-patterns, behavior-patterns, ux-patterns

**Integration:**
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

## 6. Templates

### POWER Framework Templates

**Location:** `templates/power/`

**Templates:**
- readme.txt
- architecture.txt
- api.txt
- schema.txt
- components.txt
- user-guide.txt (NEW v4.0.0)
- my-guide.txt (NEW v4.0.0)
- features.txt (NEW v4.0.0)

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

## 7. Test Components

### MCP Integration Tests (NEW v4.0.0)

**Location:** `tests/test_mcp_orchestrator.py` (16 tests)

**Test Coverage:**
1. **TestMCPCalling** - MCP tool invocation
2. **TestCaching** - 15-minute cache behavior
3. **TestErrorHandling** - Graceful degradation

---

### Drift Detection Tests (NEW v4.0.0)

**Location:** `tests/test_drift_detection.py` (20 tests)

**Test Coverage:**
1. **TestDriftSeverity** - Severity level calculation (none/standard/severe)
2. **TestDriftBoundaries** - Edge cases (10%, 50% thresholds)

---

### User Docs Tests (NEW v4.0.0)

**Location:** `tests/test_user_docs_integration.py` (20 tests)

**Test Coverage:**
1. **TestToolExtraction** - MCP tool discovery from .coderef/index.json
2. **TestCommandScanning** - Slash command discovery from .claude/commands/
3. **TestAutoFillRate** - Verify 75%+ auto-fill quality

---

### Standards Tests (NEW v4.0.0)

**Location:** `tests/test_standards_semantic.py` (20 tests)

**Test Coverage:**
1. **TestMCPPatterns** - Semantic pattern analysis integration
2. **TestFrequencyTracking** - Pattern occurrence counting
3. **TestViolationDetection** - Consistency violation identification

---

### Tool Consolidation Tests (NEW v4.0.0)

**Location:** `tests/test_tool_consolidation.py` (20 tests)

**Test Coverage:**
1. **TestInternalMarking** - [INTERNAL] tools properly marked
2. **TestDeprecatedMarking** - [DEPRECATED] tools properly marked
3. **TestMigrationPaths** - Backward compatibility

---

### Health Check Tests (NEW v4.0.0)

**Location:** `tests/test_health_check.py` (20 tests)

**Test Coverage:**
1. **TestMCPStatus** - MCP availability display in list_templates
2. **TestPerformance** - Health check < 100ms

---

### Edge Case Tests (NEW v4.0.0)

**Location:** `tests/test_edge_cases.py` (20 tests)

**Test Coverage:**
1. **TestEmptyFiles** - Graceful handling of empty resources
2. **TestMalformedJSON** - Error handling for invalid JSON
3. **TestUnicode** - International character support
4. **TestLargeCodebases** - Performance with >100k LOC

---

### Full Workflow Tests (NEW v4.0.0)

**Location:** `tests/test_full_workflow_integration.py` (5 tests)

**Test Coverage:**
1. **TestEndToEnd** - Complete workflows (plan → generate → validate)

---

### Direct Validation Tests

**Location:** `tests/test_direct_validation.py` (8 tests)

**Test Classes:**
1. **TestFoundationDocDirectValidation** - Verifies tool saves files and runs validators
2. **TestStandardsDocDirectValidation** - Verifies all 3 standards files validated
3. **TestNoInstructionBlocks** - CRITICAL: Ensures NO instruction blocks in output
4. **TestValidationRunsAtToolRuntime** - Verifies call order (save → validate → metadata)

**Test Results:** 8/8 passing (100%)

---

### Unit Tests

**Location:** `tests/unit/`

**Coverage:**
- `test_changelog_generator.py` - Changelog functionality
- `test_foundation_generator.py` - Foundation doc generation
- `test_planning_generator.py` - Planning workflows

---

## 8. Configuration Files

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
- pytest-asyncio (dev, NEW v4.0.0)

---

## 9. Data Structures

### CHANGELOG.json

**Purpose:** Structured version history

**Location:** `coderef/CHANGELOG.json`

**Schema:**
```json
{
  "version": "4.0.0",
  "date": "2026-01-13",
  "changes": [
    {
      "type": "feature",
      "severity": "major",
      "title": "MCP integration and user docs automation",
      "description": "Complete v4.0.0 transformation",
      "files": ["mcp_orchestrator.py", "user_guide_generator.py"],
      "workorder_id": "WO-GENERATION-ENHANCEMENT-001"
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

## 10. Architecture Patterns

### MCP Orchestration Pattern (NEW v4.0.0)

**Pattern:**
1. Check MCP server availability via mcp_orchestrator
2. Call MCP tools with caching (15 min cache for patterns)
3. Use semantic results if available
4. Graceful fallback to regex/templates if MCP unavailable
5. Return enhanced results

**Benefits:**
- Centralized MCP calling logic
- Caching reduces redundant expensive calls
- Graceful degradation maintains functionality
- Clear separation between MCP and non-MCP code paths

**Coverage:**
- Drift detection (generate_foundation_docs)
- Pattern analysis (establish_standards)
- Resource checking (all generators)
- Health status (list_templates)

---

### Sequential Generation Pattern

**Pattern:**
1. Check drift before starting generation
2. Generate docs one at a time (not all at once)
3. Show progress markers [1/5], [2/5], etc.
4. Save each doc before moving to next
5. Validate after each save

**Benefits:**
- Avoids timeout errors (~250-350 lines per call)
- Clear progress visibility
- Early failure detection
- Manageable context size

---

### Direct Validation Pattern

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
│  ├─ mcp_orchestrator.py (NEW v4.0.0)
│  │  └─ {calls coderef-context MCP tools}
│  ├─ mcp_integration.py
│  ├─ generators/*
│  │  ├─ base_generator.py
│  │  ├─ foundation_generator.py
│  │  ├─ user_guide_generator.py (NEW v4.0.0)
│  │  ├─ standards_generator.py (enhanced v4.0.0)
│  │  └─ {...13 other generators}
│  ├─ utils/validation_helpers.py
│  ├─ papertrail.validators (external)
│  └─ validation.py
├─ constants.py
├─ error_responses.py
├─ logger_config.py
└─ mcp_integration.py
```

---

## Component Metrics (v4.0.0)

| Component Category | Count | Lines of Code | Status |
|--------------------|-------|---------------|--------|
| Core Server | 2 | 1,743 | ✅ Production |
| MCP Orchestration | 1 | 210 | ✅ NEW v4.0.0 |
| Generators | 14 | 3,500+ | ✅ Production |
| Utilities | 6 | 1,200+ | ✅ Production |
| Validators | 3 | 800+ | ✅ Production |
| Templates | 8 | N/A | ✅ Production |
| Tests | 10 files | 2,000+ | ✅ 185 tests (95%+ pass) |
| **Total** | **44** | **9,453+** | **✅ v4.0.0** |

---

## Version History

- **v4.0.0 (2026-01-13)**: MCP orchestration, user docs automation, standards enhancement, tool consolidation (WO-GENERATION-ENHANCEMENT-001)
  - NEW: mcp_orchestrator.py (210 lines)
  - NEW: user_guide_generator.py (420 lines)
  - ENHANCED: standards_generator.py (MCP patterns)
  - ENHANCED: tool_handlers.py (16 tools, drift detection)
  - 185 tests across 10 files (95%+ pass rate)
- v3.7.0 (2026-01-11): Direct validation integration (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)
- v3.6.0 (2026-01-10): Papertrail validators integration (instruction-based, deprecated)
- v3.5.0: .coderef/ integration for foundation docs
- v3.4.0: Resource sheet MCP tool
- v3.3.0: .coderef/ fast path for standards

---

## References

- **API.md** - MCP tool endpoints (v4.0.0)
- **ARCHITECTURE.md** - System design (v4.0.0)
- **SCHEMA.md** - Data structures (v4.0.0)
- **README.md** - User guide (v4.0.0)
- **INTEGRATION.md** - MCP integration guide (NEW v4.0.0)

---

**Maintained by:** willh, Claude Code AI
**Last Updated:** 2026-01-13 (v4.0.0 - MCP Integration & User Docs Automation)
**Status:** ✅ Production Ready
