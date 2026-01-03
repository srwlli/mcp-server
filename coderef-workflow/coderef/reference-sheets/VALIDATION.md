# VALIDATION.md - validation.py Authoritative Reference

**File:** `validation.py`
**Category:** Security / Input Validation
**Lines:** 775
**Functions:** 24 validation functions
**Version:** 1.2.0
**Status:** ✅ Production - Critical Security Boundary
**Generated:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-P1-001

---

## 1. Purpose & Scope

**What It Does:**
`validation.py` provides input validation functions at MCP tool boundaries. Validates all external inputs before passing to generators, enabling fail-fast error handling with clear error messages and preventing security vulnerabilities.

**Key Innovation:**
Security-first design with fail-fast validation at trust boundaries. Prevents path traversal, null byte injection, and invalid enum values from reaching internal code.

**What It Returns:**
- Validated input (if valid)
- Raises `ValueError` with descriptive message (if invalid)

**Dependencies:**
- **re** - Regex pattern matching for format validation
- **constants** - Enum values, regex patterns, security constants
- **pathlib.Path** - Path validation and traversal detection

**Core Validation Categories (7 domains):**
```
1. Project Path Validation (1 function)
   └─ validate_project_path_input

2. Documentation Validation (3 functions)
   └─ validate_version_format, validate_template_name_input, validate_changelog_inputs

3. Standards & Audit Validation (5 functions)
   └─ validate_scan_depth, validate_focus_areas, validate_severity_filter, validate_audit_scope, validate_severity_threshold

4. Consistency Check Validation (1 function)
   └─ validate_file_list

5. Planning Workflow Validation (4 functions + 1 constant)
   └─ VALID_TEMPLATE_SECTIONS, validate_section_name, validate_plan_file_path, validate_plan_json_structure, validate_feature_name_input

6. Workorder Validation (1 function)
   └─ validate_workorder_id

7. Risk Assessment Validation (1 function)
   └─ validate_risk_inputs

8. Context Expert Validation (6 functions)
   └─ validate_resource_path, validate_expert_id, validate_resource_type, validate_expert_domain, validate_expert_capabilities, validate_context_expert_inputs
```

**Performance:**
- Typical validation: <1ms (regex match + enum check)
- Path validation: <10ms (filesystem check + path resolution)
- Zero performance impact on valid inputs

---

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **Validation rules** | Module | Static functions | N/A | `validation.py` function logic |
| **Enum values** | constants.py | Static enums | N/A | `constants.py` (imported) |
| **Regex patterns** | constants.py | Static strings | N/A | `constants.py` (imported) |
| **Valid sections** | Module | Static list | N/A | `VALID_TEMPLATE_SECTIONS` constant |

**Key Insight:** validation.py is **100% stateless** - pure validation functions with zero side effects. All validation rules are static and deterministic.

---

## 3. Architecture & Data Flow

### Validation Flow

```
MCP Tool Boundary
    ↓
Tool Handler (tool_handlers.py)
    ↓
Validation Function (validation.py)
├─ Type check (isinstance)
├─ Format check (regex, enum)
├─ Security check (path traversal, null bytes)
└─ Return validated input OR raise ValueError
    ↓
Generator/Service Layer (generators/*.py)
    ↓
Business Logic (safe - already validated)
```

### Error Handling Pattern

```python
def some_mcp_tool(project_path: str):
    """MCP tool with validation at boundary."""
    try:
        # Validate at boundary
        validated_path = validate_project_path_input(project_path)

        # Safe to use - validation passed
        generator = SomeGenerator(Path(validated_path))
        result = generator.generate()
        return result

    except ValueError as e:
        # Return MCP error response
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 4. Validation Function Catalog

### Category 1: Project Path Validation

**validate_project_path_input(path: str) → str**
- **Purpose:** Validate project path at tool boundary
- **Security Checks:**
  1. Non-empty string
  2. Length <= 1000 chars (MAX_PATH_LENGTH)
  3. No null bytes (\x00) - prevents injection
- **Returns:** Validated path string
- **Raises:** ValueError if invalid
- **Performance:** <1ms
- **Example:**
  ```python
  validate_project_path_input("/path/to/project")  # ✅ Valid
  validate_project_path_input("")  # ❌ ValueError: must be non-empty
  validate_project_path_input("/path\x00/attack")  # ❌ ValueError: null bytes
  ```

---

### Category 2: Documentation Validation

**validate_version_format(version: str) → str**
- **Purpose:** Validate semantic version format (X.Y.Z)
- **Pattern:** `^\d+\.\d+\.\d+$` (from constants.VERSION_PATTERN)
- **Returns:** Validated version string
- **Raises:** ValueError if format invalid
- **Example:**
  ```python
  validate_version_format("1.2.3")  # ✅ Valid
  validate_version_format("1.2")  # ❌ ValueError: invalid format
  ```

**validate_template_name_input(template_name: str) → str**
- **Purpose:** Validate template name against TemplateNames enum
- **Allowed:** readme, architecture, api, components, my-guide, schema, user-guide
- **Returns:** Validated template name
- **Raises:** ValueError if not in enum
- **Example:**
  ```python
  validate_template_name_input("readme")  # ✅ Valid
  validate_template_name_input("unknown")  # ❌ ValueError: invalid template
  ```

**validate_changelog_inputs(...) → dict**
- **Purpose:** Validate all changelog entry inputs at once
- **Parameters:** version, change_type, severity, title, description, files, reason, impact
- **Validations:**
  1. Version format (semantic versioning)
  2. change_type in ChangeType enum
  3. severity in Severity enum
  4. All string fields non-empty
  5. files is non-empty list of strings
- **Returns:** Dict of validated inputs
- **Raises:** ValueError on first invalid field
- **Example:**
  ```python
  inputs = validate_changelog_inputs(
      version="1.2.3",
      change_type="feature",
      severity="major",
      title="Add dark mode",
      description="Dark mode toggle in settings",
      files=["src/components/Settings.tsx"],
      reason="User request",
      impact="No breaking changes"
  )  # ✅ Valid
  ```

---

### Category 3: Standards & Audit Validation

**validate_scan_depth(scan_depth: str) → str**
- **Purpose:** Validate scan depth using ScanDepth enum
- **Allowed:** quick, standard, deep
- **Returns:** Validated scan depth
- **Raises:** ValueError if not in enum

**validate_focus_areas(focus_areas: list) → list**
- **Purpose:** Validate focus areas using FocusArea enum
- **Allowed:** ui_components, behavior_patterns, ux_flows, all
- **Returns:** Validated focus areas list
- **Raises:** ValueError if any area invalid

**validate_severity_filter(severity: str) → str**
- **Purpose:** Validate severity filter using AuditSeverity enum
- **Allowed:** critical, major, minor, all
- **Returns:** Validated severity
- **Raises:** ValueError if not in enum

**validate_audit_scope(scope: list) → list**
- **Purpose:** Validate audit scope using AuditScope enum
- **Allowed:** ui_patterns, behavior_patterns, ux_patterns, all
- **Returns:** Validated scope list
- **Raises:** ValueError if any scope invalid

**validate_severity_threshold(threshold: str) → str**
- **Purpose:** Validate severity threshold using SeverityThreshold enum
- **Allowed:** critical, major, minor
- **Uses:** SeverityThreshold.values() classmethod
- **Returns:** Validated threshold
- **Raises:** ValueError if not in enum

---

### Category 4: Consistency Check Validation

**validate_file_list(files: list) → list**
- **Purpose:** Validate file list for consistency checker
- **Security Checks:**
  1. All items are strings
  2. No absolute paths (security - SEC-001)
  3. No path traversal (..) (security - SEC-001)
- **Returns:** Validated files list
- **Raises:** ValueError if security check fails
- **Example:**
  ```python
  validate_file_list(["src/App.tsx", "src/Button.tsx"])  # ✅ Valid
  validate_file_list(["/absolute/path"])  # ❌ ValueError: absolute path
  validate_file_list(["../../../etc/passwd"])  # ❌ ValueError: path traversal
  ```

---

### Category 5: Planning Workflow Validation

**VALID_TEMPLATE_SECTIONS (constant)**
- **Purpose:** Single source of truth for valid plan sections
- **Values:** all, META_DOCUMENTATION, 0_preparation through 9_implementation_checklist, QUALITY_CHECKLIST_FOR_PLANS, COMMON_MISTAKES_TO_AVOID, USAGE_INSTRUCTIONS
- **Count:** 15 valid sections
- **Usage:** Exported for reuse in multiple validators

**validate_section_name(section: str) → str**
- **Purpose:** Validate template section name
- **Allowed:** Values in VALID_TEMPLATE_SECTIONS
- **Returns:** Validated section name
- **Raises:** ValueError if not in list

**validate_plan_file_path(project_path, plan_file: str) → Path**
- **Purpose:** Validate plan file path prevents traversal
- **Security Checks:**
  1. Resolves to absolute path
  2. Must be within project directory (is_relative_to check)
- **Returns:** Resolved absolute path
- **Raises:** ValueError if outside project
- **Example:**
  ```python
  validate_plan_file_path(project, "coderef/workorder/feature/plan.json")  # ✅ Valid
  validate_plan_file_path(project, "../../etc/passwd")  # ❌ ValueError: outside project
  ```

**validate_plan_json_structure(plan_data: dict) → dict**
- **Purpose:** Validate plan JSON has required structure
- **Required Keys:** META_DOCUMENTATION, UNIVERSAL_PLANNING_STRUCTURE
- **Returns:** Validated plan dict
- **Raises:** ValueError if missing keys

**validate_feature_name_input(feature_name: str) → str**
- **Purpose:** Validate feature name to prevent path traversal
- **Security Checks:**
  1. Non-empty string
  2. Max 100 characters
  3. Only alphanumeric, hyphens, underscores (regex: `^[a-zA-Z0-9_-]+$`)
- **Returns:** Validated feature name
- **Raises:** ValueError if invalid characters or too long
- **Example:**
  ```python
  validate_feature_name_input("dark-mode-toggle")  # ✅ Valid
  validate_feature_name_input("dark mode")  # ❌ ValueError: space not allowed
  validate_feature_name_input("../../../attack")  # ❌ ValueError: invalid chars
  ```

---

### Category 6: Workorder Validation

**validate_workorder_id(workorder_id: str) → str**
- **Purpose:** Validate workorder ID format
- **Format:** `WO-{FEATURE-NAME}-{3-DIGITS}` (uppercase)
- **Pattern:** `^WO-[A-Z0-9-]+-\d{3}$`
- **Returns:** Validated workorder ID
- **Raises:** ValueError if format invalid
- **Example:**
  ```python
  validate_workorder_id("WO-AUTH-001")  # ✅ Valid
  validate_workorder_id("WO-UPDATE-DOCS-002")  # ✅ Valid
  validate_workorder_id("wo-auth-001")  # ❌ ValueError: lowercase not allowed
  validate_workorder_id("WO-AUTH-1")  # ❌ ValueError: must be 3 digits
  ```

---

### Category 7: Risk Assessment Validation

**validate_risk_inputs(arguments: dict) → dict**
- **Purpose:** Validate risk assessment tool inputs at MCP boundary
- **Required Fields:**
  - project_path (str)
  - proposed_change (dict with description, change_type, files_affected)
- **Optional Fields:**
  - options (list, max 5)
  - threshold (float, 0-100, default 50.0)
- **Validations:**
  1. project_path via validate_project_path_input
  2. proposed_change is dict
  3. change_type in ['create', 'modify', 'delete', 'refactor', 'migrate']
  4. files_affected is list
  5. description is non-empty string
  6. options (if provided) max 5, each with description + files_affected
  7. threshold (if provided) between 0-100
- **Returns:** Validated arguments dict with defaults
- **Raises:** ValueError on first invalid field

---

### Category 8: Context Expert Validation

**validate_resource_path(project_path, resource_path: str) → str**
- **Purpose:** Validate resource path exists within project
- **Security Checks:**
  1. Non-empty string
  2. No path traversal (..)
  3. Resolves within project (is_relative_to)
  4. Path exists on filesystem
- **Returns:** Validated resource path
- **Raises:** ValueError if invalid or outside project

**validate_expert_id(expert_id: str) → str**
- **Purpose:** Validate context expert ID format
- **Format:** `CE-{resource-slug}-{3-DIGITS}`
- **Pattern:** From constants.EXPERT_ID_PATTERN
- **Returns:** Validated expert ID
- **Raises:** ValueError if format invalid
- **Example:**
  ```python
  validate_expert_id("CE-src-auth-001")  # ✅ Valid
  validate_expert_id("CE-components-ui-002")  # ✅ Valid
  validate_expert_id("invalid")  # ❌ ValueError: invalid format
  ```

**validate_resource_type(resource_type: str) → str**
- **Purpose:** Validate resource type parameter
- **Allowed:** file, directory (from ResourceType enum)
- **Returns:** Validated resource type
- **Raises:** ValueError if not in enum

**validate_expert_domain(domain: str) → str**
- **Purpose:** Validate expert domain parameter
- **Allowed:** ui, db, script, docs, api, core, test, infra (from ExpertDomain enum)
- **Returns:** Validated domain
- **Raises:** ValueError if not in enum

**validate_expert_capabilities(capabilities: list) → list**
- **Purpose:** Validate expert capabilities list
- **Allowed:** answer_questions, review_changes, generate_docs (from ContextExpertCapability enum)
- **Returns:** Validated capabilities list
- **Raises:** ValueError if any capability invalid

**validate_context_expert_inputs(arguments: dict) → dict**
- **Purpose:** Validate context expert tool inputs at MCP boundary
- **Composite Validation:** Calls validate_project_path_input, validate_resource_path, validate_resource_type, validate_expert_id, validate_expert_domain, validate_expert_capabilities as needed
- **Returns:** Validated arguments dict
- **Raises:** ValueError on first invalid field

---

## 5. Security Design

### Security Boundaries

```
Untrusted Input (MCP tool boundary)
    ↓
Validation Layer (validation.py)
├─ Type checking
├─ Format validation (regex)
├─ Enum validation (constants.py)
├─ Path traversal detection
├─ Null byte injection prevention
└─ Length limits
    ↓
Trusted Input (generator layer)
```

### Attack Prevention

**Path Traversal Prevention:**
```python
# Check for .. in paths
if '..' in resource_path:
    raise ValueError("Path traversal detected")

# Resolve and check is_relative_to
full_path = (project_path / resource_path).resolve()
if not full_path.is_relative_to(project_path):
    raise ValueError("Path outside project")
```

**Null Byte Injection Prevention:**
```python
# Prevents null byte attacks
if '\x00' in path:
    raise ValueError("Path contains null bytes")
```

**Absolute Path Prevention:**
```python
# Prevent absolute paths in relative file lists
if Path(file_path).is_absolute():
    raise ValueError("File paths must be relative")
```

---

## 6. Integration Points

### 6.1 Called By (Consumers)

**All Tool Handlers:**
- `tool_handlers.py` - Calls validation functions at tool boundary before invoking generators

**Example Integration:**
```python
# In tool_handlers.py
async def create_plan(arguments):
    """Create implementation plan with validation."""
    # Validate at boundary
    feature_name = validate_feature_name_input(arguments['feature_name'])
    project_path = Path(validate_project_path_input(arguments['project_path']))

    if 'workorder_id' in arguments:
        workorder_id = validate_workorder_id(arguments['workorder_id'])

    # Safe to proceed - inputs validated
    generator = PlanningGenerator(project_path)
    plan = generator.generate_plan(feature_name, workorder_id=workorder_id)
    return plan
```

### 6.2 Calls (Dependencies)

**constants.py:**
- Imports enums (TemplateNames, ChangeType, Severity, ScanDepth, etc.)
- Imports regex patterns (VERSION_PATTERN, EXPERT_ID_PATTERN)
- Imports security constants (MAX_PATH_LENGTH, EXCLUDE_DIRS)

**pathlib.Path:**
- Used for path resolution and traversal detection
- Methods: resolve(), is_relative_to(), is_absolute(), exists()

**re module:**
- Used for regex pattern matching
- Method: re.match()

---

## 7. Best Practices

### 7.1 Using Validation Functions

**DO:**
```python
# ✅ Validate at MCP boundary
def some_mcp_tool(project_path: str, feature_name: str):
    validated_path = validate_project_path_input(project_path)
    validated_name = validate_feature_name_input(feature_name)
    # ... proceed with validated inputs

# ✅ Let ValueError propagate to MCP layer
try:
    validated = validate_project_path_input(path)
except ValueError as e:
    return {"success": False, "error": str(e)}
```

**DON'T:**
```python
# ❌ Skip validation
def some_mcp_tool(project_path: str):
    generator = SomeGenerator(Path(project_path))  # Unsafe!

# ❌ Catch and ignore validation errors
try:
    validated = validate_project_path_input(path)
except ValueError:
    pass  # Don't swallow errors!
```

---

### 7.2 Error Handling

**DO:**
```python
# ✅ Clear error messages
raise ValueError(
    f"Invalid feature_name: '{feature_name}'. "
    "Only alphanumeric characters, hyphens, and underscores are allowed."
)

# ✅ Include valid options in error
raise ValueError(
    f"Invalid severity: {severity}. "
    f"Must be one of: {', '.join(valid_severities)}"
)
```

**DON'T:**
```python
# ❌ Vague error messages
raise ValueError("Invalid input")

# ❌ No guidance for user
raise ValueError("Bad value")
```

---

## 8. Testing Strategy

```python
import pytest
from validation import (
    validate_project_path_input,
    validate_feature_name_input,
    validate_workorder_id
)

def test_project_path_validation():
    """Test project path validation."""
    # Valid paths
    assert validate_project_path_input("/path/to/project") == "/path/to/project"

    # Empty path
    with pytest.raises(ValueError, match="must be a non-empty string"):
        validate_project_path_input("")

    # Null bytes
    with pytest.raises(ValueError, match="null bytes"):
        validate_project_path_input("/path\x00/attack")

def test_feature_name_validation():
    """Test feature name validation."""
    # Valid names
    assert validate_feature_name_input("dark-mode") == "dark-mode"
    assert validate_feature_name_input("auth_system") == "auth_system"

    # Invalid characters
    with pytest.raises(ValueError, match="Only alphanumeric"):
        validate_feature_name_input("dark mode")  # Space

    with pytest.raises(ValueError, match="Only alphanumeric"):
        validate_feature_name_input("../../../attack")  # Path traversal

def test_workorder_id_validation():
    """Test workorder ID validation."""
    # Valid IDs
    assert validate_workorder_id("WO-AUTH-001") == "WO-AUTH-001"
    assert validate_workorder_id("WO-UPDATE-DOCS-123") == "WO-UPDATE-DOCS-123"

    # Invalid format
    with pytest.raises(ValueError, match="Expected format"):
        validate_workorder_id("wo-auth-001")  # Lowercase

    with pytest.raises(ValueError, match="Expected format"):
        validate_workorder_id("WO-AUTH-1")  # Only 1 digit
```

---

## 9. Performance Characteristics

### Latency Breakdown

| Validation Type | Time | Bottleneck |
|-----------------|------|------------|
| Type check | <0.1ms | isinstance() |
| Regex match | <1ms | re.match() |
| Enum check | <1ms | List comprehension |
| Path resolution | <10ms | Filesystem check |
| Null byte check | <0.1ms | String search |

### Optimization Strategies

**Caching Enum Values:**
```python
# Cache enum values to avoid repeated list comprehension
_VALID_CHANGE_TYPES = [t.value for t in ChangeType]

def validate_change_type(change_type: str) -> str:
    if change_type not in _VALID_CHANGE_TYPES:
        raise ValueError(...)
```

---

## 10. Related Resources

### 10.1 Related Files

- **constants.py** - Provides enums, regex patterns, security constants
- **tool_handlers.py** - Primary consumer (calls validation at tool boundary)
- **generators/*.py** - Consumers (receive validated inputs)

### 10.2 Generated Artifacts

- **coderef/schemas/validation-schema.json** - JSON Schema for validation functions
- **coderef/.jsdoc/validation-jsdoc.txt** - JSDoc usage examples

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P1-001
**Task:** SHEET-009
**Timestamp:** 2026-01-02
**Maintained by:** willh, Claude Code AI
