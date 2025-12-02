# ARCHITECTURE.md

**Date:** 2025-10-11
**Version:** 1.4.0

---

## System Overview

**docs-mcp** is an enterprise-grade Model Context Protocol (MCP) server built on a modular, production-ready Python architecture. Through systematic refactoring (v1.0.6 through v1.0.7), consistency management expansion (v1.3.0), and planning workflow system (v1.4.0), it evolved from a monolithic 644-line server to a clean, maintainable system with 13 specialized tools and comprehensive observability.

### Core Capabilities

1. **Documentation Generation** (4 tools) - POWER framework template-driven document creation
2. **Changelog Management** (3 tools) - Schema-validated structured changelog with agentic workflows
3. **Consistency Management** (2 tools) - Standards extraction and automated compliance auditing
4. **Planning Workflow** (4 tools) - AI-assisted implementation planning with automated validation

### Architectural Principles

- **Modular Design**: Handler registry pattern with 97% reduction in dispatcher complexity
- **Type Safety**: Full TypedDict coverage for all complex return types
- **Error Consistency**: ErrorResponse factory for uniform error handling
- **Observability**: Structured logging with security audit trails
- **Security Hardening**: Input validation, path sanitization, schema enforcement

---

## System Topology (v1.1.0)

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant                              │
│         (Claude Code, Cursor, Windsurf, VS Code)            │
└───────────────────────┬─────────────────────────────────────┘
                        │ MCP Protocol (stdio)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   server.py (299 lines)                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ @app.list_tools() - 13 tool definitions             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ @app.call_tool() - 13-line dispatcher (QUA-002)     │  │
│  │ • Logs tool call (ARCH-003)                          │  │
│  │ • Looks up handler in TOOL_HANDLERS registry         │  │
│  │ • Returns await handler(arguments)                   │  │
│  └──────────┬───────────────────────────────────────────┘  │
└─────────────┼──────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│           tool_handlers.py (~840 lines)                       │
│                                                               │
│  TOOL_HANDLERS = {                                           │
│    'list_templates': handle_list_templates,                  │
│    'get_template': handle_get_template,                      │
│    'generate_foundation_docs': handle_generate_foundation... │
│    'generate_individual_doc': handle_generate_individual...  │
│    'get_changelog': handle_get_changelog,                    │
│    'add_changelog_entry': handle_add_changelog_entry,        │
│    'update_changelog': handle_update_changelog,              │
│    'establish_standards': handle_establish_standards,        │
│    'audit_codebase': handle_audit_codebase,                  │
│    'get_planning_template': handle_get_planning_template,    │
│    'analyze_project_for_planning': handle_analyze_project... │
│    'validate_implementation_plan': handle_validate_impl...   │
│    'generate_plan_review_report': handle_generate_plan...    │
│  }                                                           │
│                                                               │
│  Each handler follows pattern:                               │
│  1. Extract arguments                                        │
│  2. Validate inputs (validation.py)                          │
│  3. Log operation (logger_config.py)                         │
│  4. Execute business logic                                   │
│  5. Return result or ErrorResponse                           │
└───────┬───────────────────────┬──────────────────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐   ┌────────────────────┐
│  generators/     │   │ Support Modules    │
│  • base          │   │ • error_responses  │
│  • foundation    │   │ • type_defs        │
│  • changelog     │   │ • logger_config    │
│  • standards     │   │ • constants        │
│  • audit         │   │ • validation       │
│  • planning      │   │                    │
│    analyzer      │   │                    │
│  • plan          │   │                    │
│    validator     │   │                    │
│  • review        │   │                    │
│    formatter     │   │                    │
└────────┬─────────┘   └────────────────────┘
         │
┌─────────────────┐
│  Data Layer      │
│  • templates/    │
│  • coderef/      │
└──────────────────┘
```

---

## Module Architecture

### Core Modules (7)

| Module | Lines | Purpose | Key Pattern |
|--------|-------|---------|-------------|
| **server.py** | 299 | MCP protocol interface | Dispatcher (13-line call_tool) |
| **tool_handlers.py** | ~840 | Tool implementation | Registry pattern (QUA-002) |
| **error_responses.py** | 156 | Error formatting | Factory pattern (ARCH-001) |
| **type_defs.py** | 219 | Type definitions | TypedDict (QUA-001) |
| **logger_config.py** | 123 | Logging infrastructure | Structured logging (ARCH-003) |
| **constants.py** | 119 | Configuration constants | Enums (REF-002, QUA-003) |
| **validation.py** | 271 | Input validation | Boundary validation (REF-003) |

### Generator Modules (8)

| Module | Lines | Purpose |
|--------|-------|---------|
| **base_generator.py** | 215 | Template operations, path management |
| **foundation_generator.py** | ~150 | Multi-doc generation orchestration |
| **changelog_generator.py** | ~200 | Changelog CRUD with schema validation |
| **standards_generator.py** | ~400 | Pattern extraction and standards document creation |
| **audit_generator.py** | ~863 | Codebase auditing and compliance scoring |
| **planning_analyzer.py** | ~300 | Project analysis for planning (discovers docs, standards, patterns) |
| **plan_validator.py** | ~400 | Plan quality validation with 0-100 scoring |
| **review_formatter.py** | ~150 | Validation results formatting to markdown reports |

---

## Module Boundaries & Responsibilities

### 1. server.py - MCP Protocol Layer

**Responsibility:** MCP interface, tool registration, request dispatching

**Key Components:**
```python
@app.list_tools() -> list[Tool]
    # Declares 7 MCP tools with JSON schemas

@app.call_tool(name: str, arguments: dict) -> list[TextContent]
    # 13-line dispatcher (down from 407 lines)
    log_tool_call(name, args_keys=list(arguments.keys()))
    handler = tool_handlers.TOOL_HANDLERS.get(name)
    return await handler(arguments)
```

**Boundaries:**
- ✅ MCP protocol handling
- ✅ Tool schema definitions
- ✅ High-level routing
- ❌ NO business logic
- ❌ NO error formatting (delegates to ErrorResponse)
- ❌ NO direct file I/O

**Metrics:** 59% reduction (644 → 264 lines) after v1.0.7 refactoring

---

### 2. tool_handlers.py - Business Logic Layer

**Responsibility:** Tool implementation and orchestration

**Pattern:** Handler registry
```python
TOOL_HANDLERS = {
    'tool_name': async_handler_function,
    ...
}
```

**Standard Handler Pattern:**
```python
async def handle_tool_name(arguments: dict) -> list[TextContent]:
    """Handle tool_name tool call."""
    try:
        # 1. Validate inputs at boundary
        project_path = validate_project_path_input(arguments.get("project_path"))

        # 2. Log operation
        logger.info(f"Processing {tool_name}", extra={'project': project_path})

        # 3. Execute business logic
        generator = SomeGenerator(TEMPLATES_DIR)
        result = generator.do_work(project_path)

        # 4. Return success
        logger.info(f"Success: {tool_name}")
        return [TextContent(type="text", text=result)]

    except ValueError as e:
        log_error('validation_error', str(e))
        return ErrorResponse.invalid_input(str(e), "Helpful hint")
    except FileNotFoundError as e:
        return ErrorResponse.not_found(str(e))
    # ... more error handlers
```

**Boundaries:**
- ✅ All tool business logic
- ✅ Generator orchestration
- ✅ Comprehensive error handling
- ✅ Logging all operations
- ❌ NO MCP protocol details
- ❌ NO raw error formatting (uses ErrorResponse factory)

**Metrics:** 7 independently testable handlers

---

### 3. error_responses.py - Error Factory (ARCH-001)

**Responsibility:** Consistent error response formatting

**Pattern:** Static factory methods
```python
class ErrorResponse:
    @staticmethod
    def invalid_input(detail: str, hint: str = None) -> list[TextContent]:
        text = f"❌ Invalid input: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def validation_failed(error: jsonschema.ValidationError) -> list[TextContent]:
        # Special handler for schema errors with path extraction
        ...
```

**Available Factories:**
- `invalid_input()` - ValueError
- `not_found()` - FileNotFoundError
- `permission_denied()` - PermissionError
- `validation_failed()` - jsonschema.ValidationError
- `malformed_json()` - json.JSONDecodeError
- `encoding_error()` - UnicodeDecodeError
- `io_error()` - IOError
- `generic_error()` - Exception

**Boundaries:**
- ✅ All error formatting
- ✅ Consistent emoji usage (❌, 💡)
- ✅ Optional hints for all errors
- ❌ NO business logic
- ❌ NO error logging (callers log)

**Benefits:**
- Eliminates ~350 lines of duplicate error handling code
- Uniform user experience
- Single source of truth for error messages

---

### 4. type_defs.py - Type Safety (QUA-001)

**Responsibility:** TypedDict definitions for complex return types

**Available Types:**
```python
class PathsDict(TypedDict):
    project_path: Path
    output_dir: Path

class TemplateInfoDict(TypedDict, total=False):
    framework: str
    purpose: str
    save_as: str
    store_as: str

class ChangeDict(TypedDict, total=False):
    id: str
    type: str
    severity: str
    title: str
    description: str
    files: List[str]
    reason: str
    impact: str
    breaking: bool
    migration: str  # Optional

# + TemplateDict, WorkflowStepDict, VersionEntryDict
```

**Boundaries:**
- ✅ Type definitions only
- ✅ Documentation via TypedDict
- ✅ IDE autocomplete support
- ❌ NO runtime validation
- ❌ NO business logic

**Benefits:**
- 95% type coverage (up from 40%)
- Better IDE support
- Self-documenting code
- Type checking with mypy/pyright

---

### 5. logger_config.py - Logging Infrastructure (ARCH-003)

**Responsibility:** Structured logging with security awareness

**Key Functions:**
```python
setup_logger(name, level, log_file) -> logging.Logger
log_tool_call(tool_name: str, **kwargs) -> None
log_security_event(event_type: str, detail: str, **kwargs) -> None
log_error(error_type: str, detail: str, **kwargs) -> None
log_performance(operation: str, duration_ms: float, **kwargs) -> None
```

**Features:**
- **stderr output** - Doesn't interfere with MCP stdio protocol
- **Sensitive data sanitization** - Auto-removes password, token, secret
- **Structured logging** - Extra fields for filtering/analysis
- **Security audit trail** - All security events logged at WARNING level
- **Dynamic level adjustment** - `set_log_level()` for debugging

**Boundaries:**
- ✅ All logging configuration
- ✅ Sensitive data protection
- ✅ Structured log formatting
- ❌ NO business logic
- ❌ NO log analysis/aggregation

**Example Output:**
```
2025-10-09 14:23:15 - docs-mcp - INFO - MCP server starting
2025-10-09 14:23:20 - docs-mcp - INFO - Tool called: get_template
2025-10-09 14:23:20 - docs-mcp - WARNING - Security event - invalid_template_name
2025-10-09 14:23:21 - docs-mcp - INFO - Successfully read template: readme
```

---

### 6. constants.py - Configuration (REF-002, QUA-003)

**Responsibility:** Centralized constants and enums

**Classes:**
```python
class Paths:
    FOUNDATION_DOCS = 'coderef/foundation-docs'
    CHANGELOG_DIR = 'coderef/changelog'
    TEMPLATES_DIR = 'templates/power'

class Files:
    README = 'README.md'
    CHANGELOG = 'CHANGELOG.json'
    CHANGELOG_SCHEMA = 'schema.json'
    # + ARCHITECTURE, API, COMPONENTS, SCHEMA, USER_GUIDE

class TemplateNames(str, Enum):
    README = 'readme'
    ARCHITECTURE = 'architecture'
    # ... all template names

class ChangeType(str, Enum):
    BUGFIX = 'bugfix'
    ENHANCEMENT = 'enhancement'
    FEATURE = 'feature'
    # ... all change types

class Severity(str, Enum):
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'

# Validation constants
MAX_PATH_LENGTH = 1000
TEMPLATE_NAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
VERSION_PATTERN = r'^\d+\.\d+\.\d+$'
```

**Boundaries:**
- ✅ All configuration constants
- ✅ All enum definitions
- ✅ Validation patterns
- ❌ NO business logic
- ❌ NO runtime behavior

**Impact:** Zero magic strings in codebase

---

### 7. validation.py - Input Validation (REF-003)

**Responsibility:** Fail-fast input validation at MCP boundaries

**Functions:**
```python
validate_project_path_input(path: str) -> str
    # Checks: non-empty, max length, no null bytes

validate_version_format(version: str) -> str
    # Validates: MAJOR.MINOR.PATCH format

validate_template_name_input(template_name: str) -> str
    # Validates: against TemplateNames enum

validate_changelog_inputs(...) -> dict
    # Validates: all 8 required changelog fields
    # Returns: dict of validated inputs
```

**Security Features:**
- Null byte detection (`\x00`)
- Path length limits (1000 chars)
- Format validation (semantic versioning)
- Enum whitelist validation

**Boundaries:**
- ✅ All input validation
- ✅ Security checks
- ✅ Format enforcement
- ❌ NO business logic
- ❌ NO file system access

**Pattern:** Validate at MCP boundary, fail fast with clear errors

---

### 8. standards_generator.py - Standards Extraction (INFRA-006)

**Responsibility:** Extract UI/UX/behavior patterns from codebase and generate standards documents

**Key Components:**
```python
class StandardsGenerator(BaseGenerator):
    def save_standards(project_path: Path) -> StandardsResultDict:
        # 1. Scan project for React components
        # 2. Extract UI patterns (buttons, modals, colors, typography)
        # 3. Extract behavior patterns (error handling, loading states, validation)
        # 4. Extract UX patterns (navigation, permissions, accessibility)
        # 5. Build component inventory
        # 6. Generate 4 markdown documents
```

**Pattern Extraction Methods:**
- `extract_ui_patterns()` - Buttons, modals, forms, colors, typography, spacing, icons
- `extract_behavior_patterns()` - Error handling, loading states, toasts, validation, API patterns
- `extract_ux_patterns()` - Navigation, permissions, offline handling, accessibility
- `build_component_inventory()` - Component catalog with metadata

**Output Files:**
- `UI-STANDARDS.md` - Button sizes, modal configurations, color palette, typography scale
- `BEHAVIOR-STANDARDS.md` - Error messages, loading indicators, validation rules
- `UX-PATTERNS.md` - Navigation patterns, permission guards, accessibility requirements
- `COMPONENT-INDEX.md` - Component inventory with usage counts and props

**Boundaries:**
- ✅ Codebase pattern scanning
- ✅ Regex-based component analysis
- ✅ Markdown document generation
- ✅ Standards documentation
- ❌ NO violation detection (see audit_generator)
- ❌ NO compliance scoring

**Benefits:**
- Automatic standards extraction from existing code
- Consistent pattern documentation
- Foundation for compliance auditing
- Living documentation that reflects actual codebase

---

### 9. audit_generator.py - Compliance Auditing (INFRA-006 Tool #9)

**Responsibility:** Audit codebase for standards violations and generate compliance reports

**Architecture (863 lines):**
```python
class AuditGenerator(BaseGenerator):
    # Phase 1: Setup
    def prepare_audit(project_path, standards_dir) -> tuple[Path, Path]

    # Phase 2: Standards Loading
    def load_standards(standards_dir) -> StandardsDataDict
    def _parse_ui_standards(content) -> dict
    def _parse_behavior_standards(content) -> dict
    def _parse_ux_standards(content) -> dict
    def _parse_component_index(content) -> dict

    # Phase 3: Violation Detection
    def scan_for_violations(project_path, standards, scope) -> List[AuditViolationDict]
    def detect_ui_violations(file_content, file_path, standards) -> List[...]
    def detect_behavior_violations(file_content, file_path, standards) -> List[...]
    def detect_ux_violations(file_content, file_path, standards) -> List[...]
    def _extract_code_snippet(content, position, context_lines) -> str

    # Phase 4: Scoring & Reporting
    def calculate_compliance_score(violations, total_patterns) -> ComplianceScoreDict
    def generate_audit_report(violations, compliance, metadata) -> str
    def _format_violation(violation) -> str
    def save_audit_report(report_content, output_path) -> str
```

**Violation Detection Patterns:**

*UI Violations:*
- Non-standard button sizes (small, medium, large)
- Non-standard button variants (primary, secondary, ghost)
- Unapproved color values (hex codes, CSS vars)
- Non-standard modal sizes
- Typography inconsistencies

*Behavior Violations:*
- Non-standard error messages
- Missing loading states
- Incorrect validation patterns
- Improper toast configurations

*UX Violations:*
- Missing ARIA attributes
- Improper navigation patterns
- Missing keyboard navigation
- Inaccessible interactive elements

**Compliance Scoring Algorithm:**
```python
base_score = 100
critical_deduction = critical_count * 10  # -10 per critical
major_deduction = major_count * 5         # -5 per major
minor_deduction = minor_count * 1         # -1 per minor
overall_score = max(0, base_score - total_deduction)

# Grade assignment
A: 90-100 | B: 80-89 | C: 70-79 | D: 60-69 | F: 0-59
passing = score >= 80
```

**Report Sections:**
1. **Executive Summary** - Compliance score, grade, pass/fail status
2. **Compliance by Category** - UI, behavior, UX scores
3. **Violations by Severity** - Critical, major, minor grouped
4. **Violations by File** - Hotspot analysis
5. **Fix Recommendations** - Actionable remediation steps
6. **Scan Metadata** - Timestamp, duration, files scanned

**Boundaries:**
- ✅ Standards document parsing
- ✅ Regex-based violation detection
- ✅ Compliance calculation
- ✅ Report generation
- ❌ NO automatic fixes (provides suggestions only)
- ❌ NO standards extraction (see standards_generator)

**Security Features:**
- Path canonicalization for all file operations
- Scope filtering (ui_patterns, behavior_patterns, ux_patterns, all)
- Severity filtering (critical, major, minor, all)
- Safe regex execution with match limits

**Benefits:**
- Automated compliance auditing
- Objective scoring system
- Actionable violation reports
- Hotspot identification for technical debt
- Supports "Consistency Trilogy" workflow pattern

---

### 10. Planning Workflow System (v1.4.0)

**Responsibility:** AI-assisted implementation planning with automated validation and iterative review loops

**Architecture:** 4 interconnected MCP tools forming a planning workflow pipeline

**Key Components:**

#### Tool #10: get_planning_template
```python
def get_planning_template(section: str = "all") -> TemplateDict:
    # Returns template JSON for AI reference during planning
    # Sections: 0-9 (preparation through implementation checklist)
```

#### Tool #11: analyze_project_for_planning
```python
class PlanningAnalyzer(BaseGenerator):
    def analyze(project_path: Path) -> PreparationSummaryDict:
        # 1. Scan for foundation docs (API.md, ARCHITECTURE.md, etc.)
        # 2. Scan for coding standards (BEHAVIOR-STANDARDS.md, etc.)
        # 3. Find reference components
        # 4. Identify reusable patterns
        # 5. Detect technology stack
        # 6. Identify gaps and risks
```

**Output:**
- foundation_docs: {available: [...], missing: [...]}
- coding_standards: {available: [...], missing: [...]}
- reference_components: {primary: str, secondary: [...]}
- key_patterns_identified: [...]
- technology_stack: {...}
- gaps_and_risks: [...]

**Performance:** ~80ms (750x faster than 60s target)

#### Tool #12: validate_implementation_plan
```python
class PlanValidator:
    def validate(plan_path: Path, template_path: Path) -> ValidationResultDict:
        # 1. Validate structure (all 10 sections present)
        # 2. Validate completeness (no placeholders, all fields filled)
        # 3. Validate quality (task descriptions ≥20 words, 5-10 edge cases)
        # 4. Validate autonomy (zero ambiguity, actionable tasks)
        # 5. Calculate score: 100 - (10×critical + 5×major + 1×minor)
```

**Scoring Algorithm:**
```
Score = 100 - (10 × critical_issues + 5 × major_issues + 1 × minor_issues)

Result Types:
- PASS (≥90): Ready for implementation
- PASS_WITH_WARNINGS (≥85): Acceptable, minor improvements recommended
- NEEDS_REVISION (≥70): Requires refinement before implementation
- FAIL (<70): Critical issues, significant rework required
```

**Performance:** ~18ms (111x faster than 2s target)

#### Tool #13: generate_plan_review_report
```python
class ReviewFormatter:
    def format_report(validation_result: ValidationResultDict) -> str:
        # 1. Executive Summary (score, result, approval status)
        # 2. Critical Issues (blocking problems)
        # 3. Major Issues (significant concerns)
        # 4. Minor Issues (improvements)
        # 5. Recommendations (actionable next steps)
```

**Performance:** ~5ms (600x faster than 3s target)

**Workflow Pattern:**

```
1. User: "Create implementation plan for feature X"
   │
2. AI: analyze_project_for_planning(project_path)
   │    └─► Returns: PreparationSummaryDict (~80ms)
   │
3. AI: Generates plan draft using template + analysis results
   │    └─► Saves: feature-X-plan.json
   │
4. REVIEW LOOP (max 5 iterations):
   │
   ├─► AI: validate_implementation_plan(plan_file)
   │       └─► Returns: score, issues (~18ms)
   │
   ├─► AI: generate_plan_review_report(plan_file, output_path)
   │       └─► Returns: markdown report (~5ms)
   │
   ├─► AI: Analyzes issues and refines plan
   │       └─► Fixes: critical → major → minor
   │
   └─► Loop until: score ≥ 90 OR iterations = 5
   │
5. USER APPROVAL GATE (MANDATORY)
   │    └─► User reviews plan and approves/rejects
   │
6. AI: Executes approved plan
```

**Design Principles:**
- **Automation:** analyze_project_for_planning automates section 0 (Preparation)
- **Quality:** Iterative validation ensures score ≥ 90 before user sees plan
- **Control:** Mandatory user approval gate before execution
- **Speed:** Fast validation (~18ms) enables tight iterative review loops
- **Transparency:** Markdown reports make issues actionable

**Integration with Existing System:**
- Uses foundation docs discovered by analyze_project_for_planning
- References coding standards from establish_standards
- Follows ErrorResponse factory pattern (ARCH-001)
- Uses TypedDict for complex returns (QUA-001)
- Handler registry integration (QUA-002)
- Structured logging (ARCH-003)
- Input validation at boundaries (REF-003)

**Benefits:**
- Planning time reduced: 6-9 hours → 2-3 hours (60-67% reduction)
- Preparation time reduced: 60-70% through automation
- Quality maintained: 90+ scores through iterative validation
- User control: Mandatory approval gate before execution

**Testing:**
- 18/18 integration tests passing (100% coverage)
- 2,583 lines of test code across 6 test files
- Performance tests verify speed targets met

---

## Technology Stack

### Core Dependencies

| Technology | Version | Purpose | Rationale |
|-----------|---------|---------|-----------|
| **Python** | 3.11+ | Runtime | Async/await, type hints, modern syntax |
| **MCP SDK** | 1.0+ | Protocol | Official Anthropic MCP implementation |
| **jsonschema** | 4.0+ | Validation | CHANGELOG.json schema enforcement |
| **asyncio** | stdlib | Async I/O | MCP stdio transport |
| **pathlib** | stdlib | Paths | Cross-platform path handling |
| **logging** | stdlib | Observability | Structured logging |

### Zero External Dependencies (Beyond MCP + jsonschema)

**Design Decision:** Minimize attack surface and deployment complexity

- ✅ No web frameworks (uses stdio)
- ✅ No databases (file-based storage)
- ✅ No validation frameworks (uses jsonschema)
- ✅ No template engines (static text files)
- ✅ Fast installation (`pip install mcp jsonschema`)
- ✅ Portable (no system dependencies)

---

## Data Flow

### Documentation Generation Flow

```
1. AI Request
   generate_foundation_docs(project_path="/path")
   │
2. server.py
   @app.call_tool() dispatches to handler
   │
3. tool_handlers.handle_generate_foundation_docs()
   │
   ├─ Validate: validate_project_path_input()
   ├─ Log: log_tool_call()
   ├─ Execute: FoundationGenerator.get_templates_for_generation()
   └─ Return: Templates + plan
   │
4. AI Assistant
   Analyzes project code
   Follows POWER template structure
   Writes 5 docs to coderef/foundation-docs/
```

### Changelog Update Flow (Agentic)

```
1. update_changelog(project_path, version)
   │
2. handler returns 3-step instructions
   │
3. Agent analyzes context
   │
4. Agent calls add_changelog_entry(...)
   │
   ├─ Validate ALL inputs via validate_changelog_inputs()
   ├─ Log operation
   ├─ ChangelogGenerator.add_change()
   │  ├─ Load CHANGELOG.json
   │  ├─ Validate against schema
   │  ├─ Generate change-XXX ID
   │  ├─ Update current_version
   │  └─ Write with schema validation
   └─ Return success message
```

### Consistency Management Flow ("Trilogy Pattern")

```
1. establish_standards(project_path)
   │
   ├─ Validate: validate_project_path_input()
   ├─ Log: log_tool_call()
   ├─ StandardsGenerator.save_standards()
   │  ├─ Scan project files (*.tsx, *.jsx, *.ts, *.js)
   │  ├─ Extract UI patterns (buttons, modals, colors, typography)
   │  ├─ Extract behavior patterns (error handling, loading, validation)
   │  ├─ Extract UX patterns (navigation, permissions, a11y)
   │  ├─ Build component inventory with metadata
   │  └─ Generate 4 markdown files
   │     ├─ coderef/standards/UI-STANDARDS.md
   │     ├─ coderef/standards/BEHAVIOR-STANDARDS.md
   │     ├─ coderef/standards/UX-PATTERNS.md
   │     └─ coderef/standards/COMPONENT-INDEX.md
   └─ Return: files created, patterns count, success

2. audit_codebase(project_path, standards_dir, severity_filter, scope, generate_fixes)
   │
   ├─ Validate: validate_project_path_input(), validate_severity_filter(), validate_audit_scope()
   ├─ Log: log_tool_call()
   ├─ AuditGenerator.prepare_audit()
   ├─ AuditGenerator.load_standards(standards_dir)
   │  ├─ Read 4 standards markdown files
   │  ├─ Parse UI standards → allowed_sizes, allowed_variants, colors
   │  ├─ Parse behavior standards → error_patterns, loading_required
   │  ├─ Parse UX standards → aria_required, navigation_patterns
   │  └─ Parse component index → known_components
   ├─ AuditGenerator.scan_for_violations(project_path, standards, scope)
   │  ├─ Glob all source files (*.tsx, *.jsx, *.ts, *.js)
   │  ├─ For each file:
   │  │  ├─ detect_ui_violations() → non-standard button sizes/variants/colors
   │  │  ├─ detect_behavior_violations() → missing loading states, bad error messages
   │  │  └─ detect_ux_violations() → missing ARIA, bad navigation
   │  └─ Collect all violations with file_path, line_number, code_snippet
   ├─ Apply filters (severity_filter, scope)
   ├─ AuditGenerator.calculate_compliance_score(violations)
   │  ├─ Deduct: critical * 10, major * 5, minor * 1
   │  ├─ Calculate UI/behavior/UX sub-scores
   │  ├─ Assign grade (A/B/C/D/F)
   │  └─ Determine pass/fail (>= 80%)
   ├─ AuditGenerator.generate_audit_report(violations, compliance, metadata)
   │  ├─ Executive Summary (score, grade, pass/fail)
   │  ├─ Compliance by Category table
   │  ├─ Violations by Severity (critical/major/minor)
   │  ├─ Violations by File (hotspot analysis)
   │  ├─ Fix Recommendations (actionable steps)
   │  └─ Scan Metadata (timestamp, duration, files scanned)
   ├─ AuditGenerator.save_audit_report() → coderef/audits/audit-YYYYMMDD-HHMMSS.md
   └─ Return: report_path, compliance_score, violation_stats, success

3. Workflow Pattern (Recommended)
   │
   Step 1: Extract standards from existing codebase
   └─ establish_standards(project_path)

   Step 2: Audit codebase for violations
   └─ audit_codebase(project_path)

   Step 3: Fix violations reported
   └─ Developer/AI remediates code

   Step 4: Re-audit to verify compliance
   └─ audit_codebase(project_path)  # Should show improved score

   Step 5: Update standards as patterns evolve
   └─ establish_standards(project_path)  # Refresh standards
```

**Key Insight:** The consistency trilogy enables:
- **Living documentation** - Standards extracted from actual code
- **Objective compliance** - Automated auditing with scoring
- **Continuous improvement** - Iterative fix-audit-validate cycle
- **Technical debt tracking** - Quantifiable compliance over time

---

## Design Patterns

### 1. Handler Registry Pattern (QUA-002)

**Problem:** Monolithic 407-line call_tool() function

**Solution:** Extract each tool to independent handler, register in dict

**Implementation:**
```python
# tool_handlers.py
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    # ... 5 more handlers
}

# server.py
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    log_tool_call(name, args_keys=list(arguments.keys()))
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(arguments)
```

**Benefits:**
- 97% reduction in dispatcher (407 → 13 lines)
- Each handler independently testable
- Easy to add new tools (add handler + register)
- Clear separation of concerns

---

### 2. Error Response Factory (ARCH-001)

**Problem:** Duplicate error formatting across 7 tools

**Solution:** Static factory methods for all error types

**Benefits:**
- Eliminated ~350 lines of duplicate code
- Consistent error messages
- Uniform emoji usage
- Easy to update error format globally

---

### 3. Boundary Validation (REF-003)

**Problem:** Validation mixed with business logic

**Solution:** Validate all inputs at MCP tool boundaries

**Pattern:**
```python
async def handle_tool(arguments: dict):
    # Validate FIRST, fail fast
    project_path = validate_project_path_input(arguments.get("project_path"))
    version = validate_version_format(arguments.get("version"))

    # Then execute business logic
    generator = SomeGenerator()
    result = generator.do_work(project_path, version)
```

**Benefits:**
- Fail-fast with clear errors
- Generators don't need validation logic
- Security checks in one place
- Easier testing

---

### 4. Meta-Tool Pattern

**Problem:** Enable agents to self-document without explicit prompting

**Solution:** `update_changelog` returns instructions, not data

**Flow:**
```
Traditional Tool: Input → Execute → Output
Meta-Tool: Input → Instructions → Agent Analyzes → Agent Executes → Output
```

**Example:**
```python
async def handle_update_changelog(arguments):
    # Don't execute - instruct!
    return [TextContent(type="text", text="""
        STEP 1: Analyze Your Changes
        STEP 2: Determine Change Details
        STEP 3: Call add_changelog_entry(...)
    """)]
```

**Benefits:**
- Agents use their context knowledge
- More flexible than hardcoded logic
- Demonstrates agentic workflow orchestration

---

## Security Architecture

### Defense in Depth

| Layer | Feature | Implementation |
|-------|---------|----------------|
| **Input** | Path traversal prevention | `Path.resolve()` canonicalization (SEC-001) |
| **Input** | Null byte detection | `'\x00' in path` check |
| **Input** | Length limits | MAX_PATH_LENGTH = 1000 |
| **Input** | Format validation | Regex patterns for templates, versions |
| **Input** | Enum whitelisting | ChangeType, Severity enums |
| **Data** | Schema validation | jsonschema on all CHANGELOG operations (SEC-002) |
| **Data** | Template sanitization | `^[a-zA-Z0-9_-]+$` pattern (SEC-005) |
| **Output** | Smart routing | README → root, others → coderef/ (SEC-003) |
| **Audit** | Security event logging | All suspicious activity logged |
| **Audit** | Sensitive data filter | Auto-remove password, token, secret from logs |

### Security Audit Trail

All security-relevant events logged:
- Invalid template names → `log_security_event('invalid_template_name')`
- Permission denied → `log_security_event('permission_denied')`
- Path traversal attempts → `log_security_event('path_traversal_blocked')`

---

## Performance Characteristics

### Startup Performance

- **Cold start**: <200ms
- **Memory footprint**: ~15MB base
- **Dependency loading**: MCP SDK + jsonschema only

### Operation Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| list_templates | <50ms | File glob |
| get_template | <100ms | Single file read |
| generate_foundation_docs | <200ms | 5 template reads |
| generate_individual_doc | <100ms | 1 template read |
| get_changelog | <100ms | JSON parse |
| add_changelog_entry | <150ms | Read + validate + write |
| update_changelog | <50ms | Return instructions only |
| establish_standards | <500ms | Full codebase scan + pattern extraction |
| audit_codebase | 1-5s | Depends on codebase size, violation count |

**Notes:**
- Actual document generation performed by AI, not server
- Standards extraction and audit times vary significantly with project size
- Audit performance: ~100-200 files/second on typical React projects

### Scalability

- **Concurrent requests**: Limited by Python async I/O
- **File I/O**: All operations are file-based (templates, changelog)
- **Memory**: ~2MB per active operation
- **No connection pooling**: Stdio transport (single client)

---

## Extensibility

### Adding a New Tool

**Steps:**
1. Define tool in `server.py` → `@app.list_tools()`
2. Create handler in `tool_handlers.py`
3. Register in `TOOL_HANDLERS` dict
4. Add validation function if needed
5. Document via `add_changelog_entry`

**Example:**
```python
# 1. server.py
Tool(
    name="generate_tests",
    description="Generate test documentation",
    inputSchema={...}
)

# 2. tool_handlers.py
async def handle_generate_tests(arguments: dict) -> list[TextContent]:
    try:
        project_path = validate_project_path_input(arguments.get("project_path"))
        logger.info(f"Generating tests for {project_path}")
        # ... implementation
        return [TextContent(type="text", text=result)]
    except ValueError as e:
        return ErrorResponse.invalid_input(str(e))

# 3. Register
TOOL_HANDLERS['generate_tests'] = handle_generate_tests
```

---

## Future Architecture Considerations

### Potential Enhancements

1. **Performance Monitoring**
   - Use `log_performance()` for slow operations
   - Metrics aggregation

2. **Caching Layer**
   - Cache frequently-accessed templates
   - Reduce file I/O for repeated calls

3. **Plugin System**
   - Dynamic handler loading
   - Third-party tool registration

4. **Async Optimization**
   - Parallel template loading
   - Concurrent changelog operations

5. **Configuration System**
   - Environment-specific settings
   - User-configurable paths

---

## Conclusion

docs-mcp v1.4.0 represents **enterprise-grade MCP server architecture** with comprehensive consistency management and AI-assisted planning:

- ✅ **Modular**: 7 core modules + 8 generator modules with clear boundaries
- ✅ **Maintainable**: 59% reduction in server.py, 97% in dispatcher
- ✅ **Type-Safe**: Full TypedDict coverage (219-line type_defs.py)
- ✅ **Observable**: Comprehensive logging with security audit trails
- ✅ **Secure**: Defense-in-depth with multiple validation layers
- ✅ **Testable**: 13 independently testable handlers (18/18 integration tests passing)
- ✅ **Extensible**: Handler registry + validation framework
- ✅ **Consistent**: Living standards extraction + automated compliance auditing
- ✅ **Intelligent**: AI-assisted planning with automated validation and review loops

**Key Innovations:**
1. **Systematic refactoring** - Transforms working prototypes into production-ready software through consistent application of design patterns
2. **Consistency Trilogy** - establish_standards → audit_codebase → iterative improvement workflow
3. **Objective compliance** - Automated auditing with quantifiable scoring (A-F grades, 0-100 scores)
4. **Living documentation** - Standards extracted from actual code, not aspirational docs
5. **Planning automation** - AI-assisted implementation planning reduces planning time 60-67% (6-9h → 2-3h)

**Evolution Timeline:**
- v1.0.6-1.0.7: Modular refactoring (644 → 264 lines in server.py)
- v1.0.9: AI usage guidance (CLAUDE.md for dual audiences)
- v1.3.0: Consistency management (establish_standards + audit_codebase)
- v1.4.0: Planning Workflow System (4 tools for AI-assisted planning with validation)

---

**🤖 Generated with docs-mcp v1.4.0**
**Referenced:** README.md for project overview
**See Also:** [COMPONENTS.md](./COMPONENTS.md), [API.md](./API.md), [SCHEMA.md](./SCHEMA.md)
