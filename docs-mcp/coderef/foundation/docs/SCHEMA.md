# SCHEMA.md

**Framework:** POWER (Purpose, Output, Work, Examples, Requirements)
**Version:** 1.1.0
**Date:** 2025-10-09

## Overview

This document defines all data schemas, validation rules, type definitions, and formats for the docs-mcp server v1.1.0 after major architectural refactoring. It provides comprehensive documentation of TypedDict definitions, MCP tool interfaces, changelog JSON schema, validation constraints, error response formats, logging structures, enum definitions, and file organization.

**Project Context:**
- **README Summary:** docs-mcp provides enterprise-grade MCP server for documentation generation and changelog management with modular architecture, comprehensive logging, type safety, and security hardening
- **Architecture Summary:** Modular MCP server implementing handler registry pattern (97% dispatcher reduction), ErrorResponse factory, TypedDict type safety, enum constants, comprehensive logging, and input validation
- **API Summary:** 7 MCP tools: 4 documentation generation tools + 3 changelog management tools (Changelog Trilogy: READ/WRITE/INSTRUCT)
- **Components Summary:** 10 Python modules (7 core + 3 generators) organized in 3 layers with comprehensive design patterns

---

## TypedDict Schema Definitions (v1.1.0)

### Overview

All complex data structures use TypedDict for type safety (QUA-001). Defined in `type_defs.py`.

---

### PathsDict

**Purpose:** Paths used in document generation

**Source:** `type_defs.py`

**Schema:**
```python
from typing import TypedDict
from pathlib import Path

class PathsDict(TypedDict):
    """Paths used in document generation"""
    project_path: Path
    output_dir: Path
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_path | Path | Yes | Absolute path to project directory |
| output_dir | Path | Yes | Absolute path to output directory |

**Usage:**
```python
paths: PathsDict = {
    'project_path': Path("C:/Users/willh/my-project"),
    'output_dir': Path("C:/Users/willh/my-project/coderef/foundation-docs")
}
```

---

### TemplateInfoDict

**Purpose:** Template metadata extracted from template files

**Source:** `type_defs.py`

**Schema:**
```python
class TemplateInfoDict(TypedDict, total=False):
    """Template metadata extracted from template files"""
    framework: str
    purpose: str
    save_as: str
    store_as: str
    dependencies: str
    optional_sections: str
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| framework | str | No | Template framework name (e.g., "POWER") |
| purpose | str | No | Document objective and intent |
| save_as | str | No | Default output filename (e.g., "README.md") |
| store_as | str | No | Storage reference name (e.g., "readme_summary") |
| dependencies | str | No | Comma-separated list of template dependencies |
| optional_sections | str | No | Optional sections in template |

**Note:** `total=False` means all fields are optional

---

### ChangeDict

**Purpose:** Single change entry in changelog

**Source:** `type_defs.py`

**Schema:**
```python
from typing import NotRequired

class ChangeDict(TypedDict, total=False):
    """Single change entry in changelog"""
    id: str
    type: str              # bugfix, enhancement, feature, breaking_change, deprecation, security
    severity: str          # critical, major, minor, patch
    title: str
    description: str
    files: list[str]
    reason: str
    impact: str
    breaking: bool
    migration: NotRequired[str]  # Required only if breaking=True
```

**Field Specifications:**

| Field | Type | Required | Valid Values | Description |
|-------|------|----------|--------------|-------------|
| id | str | No | `change-\d{3,}` pattern | Unique change ID (e.g., "change-001") |
| type | str | No | bugfix, enhancement, feature, breaking_change, deprecation, security | Type of change |
| severity | str | No | critical, major, minor, patch | Severity level |
| title | str | No | Min 1 char | Short title |
| description | str | No | Min 1 char | Detailed description |
| files | list[str] | No | Min 1 item | List of affected files |
| reason | str | No | Min 1 char | Why change was made |
| impact | str | No | Min 1 char | Impact on users/system |
| breaking | bool | No | true/false | Whether breaking change |
| migration | str | No | - | Migration guide (required if breaking=True) |

**Usage:**
```python
change: ChangeDict = {
    'id': 'change-001',
    'type': 'feature',
    'severity': 'major',
    'title': 'Added new tool',
    'description': 'Implemented X with capabilities Y and Z',
    'files': ['server.py', 'tool_handlers.py'],
    'reason': 'Enable users to...',
    'impact': 'Users can now...',
    'breaking': False
}
```

---

### VersionEntryDict

**Purpose:** Single version entry containing multiple changes

**Source:** `type_defs.py`

**Schema:**
```python
class VersionEntryDict(TypedDict, total=False):
    """Single version entry containing multiple changes"""
    version: str
    date: str
    summary: str
    changes: list[ChangeDict]
    contributors: list[str]
```

**Field Specifications:**

| Field | Type | Required | Format | Description |
|-------|------|----------|--------|-------------|
| version | str | No | `^\d+\.\d+\.\d+$` | Version number (X.Y.Z) |
| date | str | No | YYYY-MM-DD | Release date (ISO 8601) |
| summary | str | No | Min 1 char | Version summary |
| changes | list[ChangeDict] | No | Min 1 item | Array of changes |
| contributors | list[str] | No | - | List of contributor names |

---

### ChangelogDict

**Purpose:** Complete changelog file structure

**Source:** `type_defs.py`

**Schema:**
```python
class ChangelogDict(TypedDict):
    """Complete changelog structure"""
    schema: str               # "$schema"
    project: str
    changelog_version: str
    current_version: str
    entries: list[VersionEntryDict]
```

**Field Specifications:**

| Field | Type | Required | Format | Description |
|-------|------|----------|--------|-------------|
| schema | str | Yes | - | JSON Schema reference (e.g., "./schema.json") |
| project | str | Yes | - | Project identifier |
| changelog_version | str | Yes | `^\d+\.\d+$` | Changelog schema version (X.Y) |
| current_version | str | Yes | `^\d+\.\d+\.\d+$` | Current project version (X.Y.Z) |
| entries | list[VersionEntryDict] | Yes | - | Array of version entries |

**Usage:**
```python
changelog: ChangelogDict = {
    'schema': './schema.json',
    'project': 'docs-mcp',
    'changelog_version': '1.0',
    'current_version': '1.1.0',
    'entries': [...]
}
```

---

### ValidationResult

**Purpose:** Result of input validation

**Source:** `type_defs.py`

**Schema:**
```python
class ValidationResult(TypedDict):
    """Result of input validation"""
    valid: bool
    errors: list[str]
    warnings: list[str]
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| valid | bool | Yes | Whether validation passed |
| errors | list[str] | Yes | List of validation errors |
| warnings | list[str] | Yes | List of validation warnings |

---

### GenerationPlanDict

**Purpose:** Plan returned by meta-tool generators

**Source:** `type_defs.py`

**Schema:**
```python
class GenerationPlanDict(TypedDict):
    """Plan returned by meta-tool generators"""
    project_path: str
    output_dir: str
    templates: list[str]
    instructions: str
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_path | str | Yes | Absolute path to project |
| output_dir | str | Yes | Output directory path |
| templates | list[str] | Yes | List of templates to generate |
| instructions | str | Yes | Generation instructions for AI assistant |

---

## Constants and Enums Schema (v1.1.0)

### Overview

All constants and enums defined in `constants.py` to eliminate magic strings (QUA-003, REF-002).

---

### Paths Class

**Purpose:** Centralized directory paths

**Source:** `constants.py`

**Schema:**
```python
class Paths:
    """Centralized directory paths"""
    FOUNDATION_DOCS: str = 'coderef/foundation-docs'
    CHANGELOG_DIR: str = 'coderef/changelog'
    TEMPLATES_DIR: str = 'templates/power'
```

**Field Specifications:**

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| FOUNDATION_DOCS | str | `coderef/foundation-docs` | Foundation documentation output directory |
| CHANGELOG_DIR | str | `coderef/changelog` | Changelog storage directory |
| TEMPLATES_DIR | str | `templates/power` | POWER framework templates directory |

---

### Files Class

**Purpose:** Standard file names

**Source:** `constants.py`

**Schema:**
```python
class Files:
    """Standard file names"""
    CHANGELOG_JSON: str = 'CHANGELOG.json'
    SCHEMA_JSON: str = 'schema.json'
    README_MD: str = 'README.md'
    ARCHITECTURE_MD: str = 'ARCHITECTURE.md'
    API_MD: str = 'API.md'
    COMPONENTS_MD: str = 'COMPONENTS.md'
    SCHEMA_MD: str = 'SCHEMA.md'
    USER_GUIDE_MD: str = 'USER-GUIDE.md'
```

**Field Specifications:**

| Field | Type | Value | Purpose |
|-------|------|-------|---------|
| CHANGELOG_JSON | str | `CHANGELOG.json` | Main changelog data file |
| SCHEMA_JSON | str | `schema.json` | JSON schema validation file |
| README_MD | str | `README.md` | Primary project documentation |
| ARCHITECTURE_MD | str | `ARCHITECTURE.md` | System architecture documentation |
| API_MD | str | `API.md` | API reference documentation |
| COMPONENTS_MD | str | `COMPONENTS.md` | Component inventory documentation |
| SCHEMA_MD | str | `SCHEMA.md` | Data schema documentation |
| USER_GUIDE_MD | str | `USER-GUIDE.md` | User guide documentation |

---

### TemplateNames Enum

**Purpose:** Available POWER framework templates

**Source:** `constants.py`

**Schema:**
```python
from enum import Enum

class TemplateNames(str, Enum):
    """Available POWER framework templates"""
    README = 'readme'
    ARCHITECTURE = 'architecture'
    API = 'api'
    COMPONENTS = 'components'
    SCHEMA = 'schema'
    USER_GUIDE = 'user-guide'
```

**Enum Values:**

| Enum Member | Value | File Name | Output File |
|-------------|-------|-----------|-------------|
| README | `readme` | `readme.txt` | `README.md` |
| ARCHITECTURE | `architecture` | `architecture.txt` | `ARCHITECTURE.md` |
| API | `api` | `api.txt` | `API.md` |
| COMPONENTS | `components` | `components.txt` | `COMPONENTS.md` |
| SCHEMA | `schema` | `schema.txt` | `SCHEMA.md` |
| USER_GUIDE | `user-guide` | `user-guide.txt` | `USER-GUIDE.md` |

**Usage:**
```python
from constants import TemplateNames

# Get enum value
template = TemplateNames.README.value  # 'readme'

# Get all valid values
valid_templates = [t.value for t in TemplateNames]
# ['readme', 'architecture', 'api', 'components', 'schema', 'user-guide']

# Validate template name
if template_name in [t.value for t in TemplateNames]:
    # Valid template
    pass
```

---

### ChangeType Enum

**Purpose:** Changelog entry types

**Source:** `constants.py`

**Schema:**
```python
class ChangeType(str, Enum):
    """Changelog entry types"""
    BUGFIX = 'bugfix'
    ENHANCEMENT = 'enhancement'
    FEATURE = 'feature'
    BREAKING_CHANGE = 'breaking_change'
    DEPRECATION = 'deprecation'
    SECURITY = 'security'
```

**Enum Values:**

| Enum Member | Value | When to Use | Example |
|-------------|-------|-------------|---------|
| BUGFIX | `bugfix` | Fixed a bug or error | "Fixed crash when..." |
| ENHANCEMENT | `enhancement` | Improved existing functionality | "Improved performance of..." |
| FEATURE | `feature` | Added new functionality | "Added support for..." |
| BREAKING_CHANGE | `breaking_change` | Incompatible API changes | "Changed API signature..." |
| DEPRECATION | `deprecation` | Marked features for removal | "Deprecated X in favor of Y" |
| SECURITY | `security` | Security patches | "Patched vulnerability..." |

**Usage:**
```python
from constants import ChangeType

# Get enum value
change_type = ChangeType.FEATURE.value  # 'feature'

# Get all valid values
valid_types = [t.value for t in ChangeType]
# ['bugfix', 'enhancement', 'feature', 'breaking_change', 'deprecation', 'security']

# Validate change type
if change_type in [t.value for t in ChangeType]:
    # Valid change type
    pass
```

---

### Severity Enum

**Purpose:** Change severity levels

**Source:** `constants.py`

**Schema:**
```python
class Severity(str, Enum):
    """Change severity levels"""
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'
```

**Enum Values:**

| Enum Member | Value | Impact | Example |
|-------------|-------|--------|---------|
| CRITICAL | `critical` | System broken, data loss risk | "Fixed data corruption bug" |
| MAJOR | `major` | Significant feature impact | "Added new MCP tool" |
| MINOR | `minor` | Small improvements | "Improved error messages" |
| PATCH | `patch` | Cosmetic, docs-only | "Fixed typo in template" |

**Usage:**
```python
from constants import Severity

# Get enum value
severity = Severity.MAJOR.value  # 'major'

# Get all valid values
valid_severities = [s.value for s in Severity]
# ['critical', 'major', 'minor', 'patch']

# Validate severity
if severity in [s.value for s in Severity]:
    # Valid severity
    pass
```

---

## ErrorResponse Schema (v1.1.0)

### Overview

Consistent error formatting factory (ARCH-001). Defined in `error_responses.py`.

---

### ErrorResponse.invalid_input()

**Purpose:** Return error for invalid user input

**Source:** `error_responses.py`

**Schema:**
```python
@staticmethod
def invalid_input(detail: str, hint: Optional[str] = None) -> list[TextContent]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| detail | str | Yes | Specific error description |
| hint | str | No | Optional suggestion for fixing the error |

**Return Type:** `list[TextContent]`

**Output Format:**
```
❌ Invalid input: {detail}

💡 Hint: {hint}
```

**Example:**
```python
ErrorResponse.invalid_input(
    "Template name cannot be empty",
    "Provide one of: readme, architecture, api, components, schema, user-guide"
)
# Returns: [TextContent(type="text", text="❌ Invalid input: Template name cannot be empty\n\n💡 Hint: Provide one of: readme, architecture, api, components, schema, user-guide")]
```

---

### ErrorResponse.not_found()

**Purpose:** Error for missing resources (files, templates, etc.)

**Schema:**
```python
@staticmethod
def not_found(resource: str, suggestion: Optional[str] = None) -> list[TextContent]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| resource | str | Yes | Name/path of missing resource |
| suggestion | str | No | Optional suggestion for finding resource |

**Output Format:**
```
❌ Not found: {resource}

💡 {suggestion}
```

---

### ErrorResponse.permission_denied()

**Purpose:** Error for permission/access issues

**Schema:**
```python
@staticmethod
def permission_denied(detail: str, hint: Optional[str] = None) -> list[TextContent]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| detail | str | Yes | Description of permission issue |
| hint | str | No | Optional hint for resolving issue |

**Output Format:**
```
🔒 Permission denied: {detail}

💡 {hint}
```

---

### ErrorResponse.validation_failed()

**Purpose:** Error for JSON schema validation failures

**Schema:**
```python
@staticmethod
def validation_failed(error: jsonschema.ValidationError) -> list[TextContent]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| error | jsonschema.ValidationError | Yes | Validation error from jsonschema |

**Output Format:**
```
❌ Changelog validation failed

Error: {error.message}
Path: {error.path}
Schema path: {error.schema_path}
```

**Example:**
```python
try:
    jsonschema.validate(instance=changelog, schema=schema)
except jsonschema.ValidationError as e:
    return ErrorResponse.validation_failed(e)
# Returns: [TextContent(type="text", text="❌ Changelog validation failed\n\nError: 'files' is a required property\nPath: entries → 0 → changes → 0")]
```

---

### ErrorResponse.file_operation_failed()

**Purpose:** Error for file I/O failures

**Schema:**
```python
@staticmethod
def file_operation_failed(operation: str, file_path: str, error: str) -> list[TextContent]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| operation | str | Yes | Operation that failed (e.g., "read", "write") |
| file_path | str | Yes | Path to file that failed |
| error | str | Yes | Error message from exception |

**Output Format:**
```
❌ File {operation} failed: {file_path}

Error: {error}
```

---

### ErrorResponse.internal_error()

**Purpose:** Error for unexpected internal failures

**Schema:**
```python
@staticmethod
def internal_error(detail: str) -> list[TextContent]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| detail | str | Yes | Description of internal error |

**Output Format:**
```
⚠️ Internal error: {detail}

💡 This may be a bug. Please report to maintainers.
```

---

## Validation Rules Schema (v1.1.0)

### Overview

Input validation at MCP tool boundaries (REF-003). Defined in `validation.py`.

---

### validate_project_path_input()

**Purpose:** Validate and resolve project path with security checks

**Source:** `validation.py`

**Schema:**
```python
def validate_project_path_input(project_path: str) -> Path
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_path | str | Yes | Path string to validate |

**Return Type:** `Path` (resolved absolute path)

**Validation Rules:**
1. **Empty check:** Path cannot be empty or whitespace-only
2. **Null byte check (SEC-001):** Rejects paths containing `\x00`
3. **Path canonicalization (SEC-001):** Uses `.resolve()` to prevent `../` traversal
4. **Existence check:** Path must exist
5. **Directory check:** Path must be a directory (not a file)
6. **Length limit:** Path must be ≤ 4096 characters

**Raises:** `ValueError` if validation fails

**Example:**
```python
from validation import validate_project_path_input

# Valid path
path = validate_project_path_input("C:/Users/willh/my-project")
# Returns: Path("C:/Users/willh/my-project")

# Invalid: contains null byte
path = validate_project_path_input("C:/Users/willh\x00/my-project")
# Raises: ValueError("Project path contains null bytes")

# Invalid: doesn't exist
path = validate_project_path_input("C:/nonexistent")
# Raises: ValueError("Project path does not exist: C:/nonexistent")
```

---

### validate_version_format()

**Purpose:** Validate semantic version format (X.Y.Z)

**Source:** `validation.py`

**Schema:**
```python
def validate_version_format(version: str) -> str
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version | str | Yes | Version string to validate |

**Return Type:** `str` (validated version)

**Validation Rules:**
1. **Empty check:** Version cannot be empty or whitespace-only
2. **Pattern check (SEC-005):** Must match `^[0-9]+\.[0-9]+\.[0-9]+$`

**Pattern:** `X.Y.Z` where X, Y, Z are non-negative integers

**Raises:** `ValueError` if validation fails

**Example:**
```python
from validation import validate_version_format

# Valid versions
version = validate_version_format("1.0.3")    # Returns: "1.0.3"
version = validate_version_format("10.25.100")  # Returns: "10.25.100"

# Invalid: missing patch
version = validate_version_format("1.0")
# Raises: ValueError("Version must match pattern X.Y.Z (e.g., '1.0.2'), got: 1.0")

# Invalid: contains letters
version = validate_version_format("1.0.3a")
# Raises: ValueError("Version must match pattern X.Y.Z (e.g., '1.0.2'), got: 1.0.3a")
```

---

### validate_template_name_input()

**Purpose:** Validate template name against TemplateNames enum

**Source:** `validation.py`

**Schema:**
```python
def validate_template_name_input(template_name: str) -> str
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| template_name | str | Yes | Template name to validate |

**Return Type:** `str` (validated template name)

**Validation Rules:**
1. **Empty check:** Template name cannot be empty or whitespace-only
2. **Enum check:** Must be one of `[t.value for t in TemplateNames]`
3. **Path traversal check (SEC-005):** Cannot contain `..`, `/`, or `\`

**Valid Values:** `readme`, `architecture`, `api`, `components`, `schema`, `user-guide`

**Raises:** `ValueError` if validation fails

**Example:**
```python
from validation import validate_template_name_input

# Valid template
name = validate_template_name_input("readme")  # Returns: "readme"

# Invalid: not in enum
name = validate_template_name_input("invalid")
# Raises: ValueError("Invalid template name: 'invalid'. Valid options: readme, architecture, api, components, schema, user-guide")

# Invalid: path traversal attempt
name = validate_template_name_input("../readme")
# Raises: ValueError("Template name contains invalid path characters")
```

---

### validate_changelog_inputs()

**Purpose:** Validate all required changelog entry fields

**Source:** `validation.py`

**Schema:**
```python
def validate_changelog_inputs(
    version: str,
    change_type: str,
    severity: str,
    title: str,
    description: str,
    files: list[str],
    reason: str,
    impact: str
) -> dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version | str | Yes | Version number (X.Y.Z) |
| change_type | str | Yes | Type of change (enum value) |
| severity | str | Yes | Severity level (enum value) |
| title | str | Yes | Short title |
| description | str | Yes | Detailed description |
| files | list[str] | Yes | List of affected files |
| reason | str | Yes | Why change was made |
| impact | str | Yes | Impact on users/system |

**Return Type:** `dict` of validated inputs

**Validation Rules:**
1. **version:** Must match `validate_version_format()` rules
2. **change_type:** Must be in `[t.value for t in ChangeType]`
3. **severity:** Must be in `[s.value for s in Severity]`
4. **title:** Cannot be empty or whitespace-only
5. **description:** Cannot be empty or whitespace-only
6. **reason:** Cannot be empty or whitespace-only
7. **impact:** Cannot be empty or whitespace-only
8. **files:** Must be non-empty list

**Raises:** `ValueError` if any validation fails

**Returns:**
```python
{
    'version': str,        # Validated version
    'change_type': str,    # Validated change type
    'severity': str,       # Validated severity
    'title': str,          # Trimmed title
    'description': str,    # Trimmed description
    'files': list[str],    # Validated files list
    'reason': str,         # Trimmed reason
    'impact': str          # Trimmed impact
}
```

---

## Logging Schema (v1.1.0)

### Overview

Structured logging infrastructure (ARCH-003). Defined in `logger_config.py`.

---

### Log Entry Format

**Purpose:** Standard log entry structure

**Source:** `logger_config.py`

**Schema:**
```
{timestamp} | {level} | {message}
```

**Format String:**
```python
'%(asctime)s | %(levelname)-8s | %(message)s'
```

**Timestamp Format:** `YYYY-MM-DD HH:MM:SS`

**Example:**
```
2025-10-09 14:30:45 | INFO     | Tool called: get_template
2025-10-09 14:30:45 | DEBUG    | Reading template: readme
2025-10-09 14:30:45 | INFO     | Template retrieved successfully: readme
```

---

### Log Levels

**Purpose:** Categorize log messages by severity

**Schema:**

| Level | Value | When to Use | Example |
|-------|-------|-------------|---------|
| DEBUG | 10 | Detailed internal operations | "Reading template file from disk" |
| INFO | 20 | Tool calls, successful operations | "Tool called: get_template" |
| WARNING | 30 | Security events, unusual conditions | "Security event - invalid_template_name" |
| ERROR | 40 | Errors that don't crash server | "Error - validation_error: Template name empty" |
| CRITICAL | 50 | Severe errors (not currently used) | N/A |

---

### log_tool_call() Function

**Purpose:** Log MCP tool invocation with sanitized parameters

**Source:** `logger_config.py`

**Schema:**
```python
def log_tool_call(tool_name: str, **kwargs: Any) -> None
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tool_name | str | Yes | Name of tool being called |
| **kwargs | Any | No | Tool parameters (auto-sanitized) |

**Return Type:** `None` (logs to stderr)

**Sensitive Key Filtering:**

Automatically redacts keys matching:
- `password`
- `token`
- `secret`
- `api_key`
- `credential`

**Example:**
```python
log_tool_call('get_template', template_name='readme')
# Logs: "2025-10-09 14:30:45 | INFO | Tool called: get_template"

log_tool_call('auth', username='user', password='secret123')
# Logs: "2025-10-09 14:30:45 | INFO | Tool called: auth" (password redacted)
```

---

### log_error() Function

**Purpose:** Log error events with context

**Source:** `logger_config.py`

**Schema:**
```python
def log_error(error_type: str, detail: str, **kwargs: Any) -> None
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| error_type | str | Yes | Type of error (e.g., "validation_error") |
| detail | str | Yes | Error description |
| **kwargs | Any | No | Additional context |

**Return Type:** `None` (logs to stderr at ERROR level)

**Example:**
```python
log_error('validation_error', "Template name empty", field='template_name')
# Logs: "2025-10-09 14:30:45 | ERROR | Error - validation_error: Template name empty"
```

---

### log_security_event() Function

**Purpose:** Log security-relevant events for audit trail

**Source:** `logger_config.py`

**Schema:**
```python
def log_security_event(event_type: str, detail: str, **kwargs: Any) -> None
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| event_type | str | Yes | Type of security event |
| detail | str | Yes | Event description |
| **kwargs | Any | No | Additional context |

**Return Type:** `None` (logs to stderr at WARNING level)

**Example:**
```python
log_security_event('invalid_template_name', 'readme', path='/path/to/template')
# Logs: "2025-10-09 14:30:45 | WARNING | Security event - invalid_template_name: readme"
```

---

### log_performance() Function

**Purpose:** Log performance metrics

**Source:** `logger_config.py`

**Schema:**
```python
def log_performance(operation: str, duration_ms: float, **kwargs: Any) -> None
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| operation | str | Yes | Name of operation |
| duration_ms | float | Yes | Duration in milliseconds |
| **kwargs | Any | No | Additional context |

**Return Type:** `None` (logs to stderr at INFO level)

**Example:**
```python
log_performance('template_load', 45.23, template_name='readme')
# Logs: "2025-10-09 14:30:45 | INFO | Performance - template_load: 45.23ms"
```

---

## Changelog JSON Schema

### CHANGELOG.json Structure

**File Format:** JSON
**Encoding:** UTF-8
**Location:** `coderef/changelog/CHANGELOG.json`
**Schema File:** `coderef/changelog/schema.json`
**Schema Standard:** JSON Schema Draft 07
**Validation:** Automatic via ChangelogGenerator (SEC-002)

**Complete JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "docs-mcp Changelog Schema",
  "type": "object",
  "required": ["project", "changelog_version", "current_version", "entries"],
  "properties": {
    "project": {
      "type": "string",
      "const": "docs-mcp"
    },
    "changelog_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$"
    },
    "current_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["version", "date", "summary", "changes"],
        "properties": {
          "version": {
            "type": "string",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
          },
          "date": {
            "type": "string",
            "format": "date"
          },
          "summary": {
            "type": "string",
            "minLength": 1
          },
          "changes": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "type", "severity", "title", "description", "files", "reason", "impact", "breaking"],
              "properties": {
                "id": {
                  "type": "string",
                  "pattern": "^change-[0-9]{3,}$"
                },
                "type": {
                  "type": "string",
                  "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
                },
                "severity": {
                  "type": "string",
                  "enum": ["critical", "major", "minor", "patch"]
                },
                "title": {
                  "type": "string",
                  "minLength": 1
                },
                "description": {
                  "type": "string",
                  "minLength": 1
                },
                "files": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  },
                  "minItems": 1
                },
                "reason": {
                  "type": "string",
                  "minLength": 1
                },
                "impact": {
                  "type": "string",
                  "minLength": 1
                },
                "breaking": {
                  "type": "boolean"
                },
                "migration": {
                  "type": "string"
                }
              }
            }
          },
          "contributors": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}
```

**Validation Rules:**
1. Must validate against JSON Schema Draft 07
2. All required fields must be present
3. Version patterns must match `X.Y.Z` format
4. Change IDs must be unique within changelog (enforced by generator)
5. Change type and severity must be valid enum values
6. Date must be valid ISO 8601 date format (YYYY-MM-DD)
7. Files array must have at least 1 item
8. All text fields must have minimum 1 character

---

## MCP Tool Input/Output Schemas

### Category 1: Documentation Generation Tools

#### list_templates Tool

**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

**Input Parameters:** None

**Output Format:**
```
Available POWER Framework Templates:

1. api
2. architecture
3. components
4. readme
5. schema
6. user-guide

Total: 6 templates
```

---

#### get_template Tool

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "template_name": {
      "type": "string",
      "description": "Name of template: readme, architecture, api, components, schema, or user-guide",
      "enum": ["readme", "architecture", "api", "components", "schema", "user-guide"]
    }
  },
  "required": ["template_name"],
  "additionalProperties": false
}
```

**Input Parameters:**

| Parameter | Type | Required | Valid Values |
|-----------|------|----------|--------------|
| template_name | string | Yes | readme, architecture, api, components, schema, user-guide |

**Validation:** See `validate_template_name_input()` schema above

---

#### generate_foundation_docs Tool

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    }
  },
  "required": ["project_path"],
  "additionalProperties": false
}
```

**Input Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_path | string | Yes | Absolute path to project directory |

**Validation:** See `validate_project_path_input()` schema above

---

#### generate_individual_doc Tool

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "template_name": {
      "type": "string",
      "description": "Name of template to generate",
      "enum": ["readme", "architecture", "api", "components", "schema", "user-guide"]
    }
  },
  "required": ["project_path", "template_name"],
  "additionalProperties": false
}
```

---

### Category 2: Changelog Management Tools

#### get_changelog Tool (READ)

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "version": {
      "type": "string",
      "description": "Optional: Specific version to retrieve (e.g., '1.0.2')",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "change_type": {
      "type": "string",
      "description": "Optional: Filter by change type",
      "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
    },
    "breaking_only": {
      "type": "boolean",
      "description": "Optional: Only show breaking changes"
    }
  },
  "required": ["project_path"],
  "additionalProperties": false
}
```

---

#### add_changelog_entry Tool (WRITE)

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {"type": "string"},
    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "change_type": {"type": "string", "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]},
    "severity": {"type": "string", "enum": ["critical", "major", "minor", "patch"]},
    "title": {"type": "string"},
    "description": {"type": "string"},
    "files": {"type": "array", "items": {"type": "string"}},
    "reason": {"type": "string"},
    "impact": {"type": "string"},
    "breaking": {"type": "boolean"},
    "migration": {"type": "string"},
    "summary": {"type": "string"},
    "contributors": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["project_path", "version", "change_type", "severity", "title", "description", "files", "reason", "impact"],
  "additionalProperties": false
}
```

**Validation:** See `validate_changelog_inputs()` schema above

---

#### update_changelog Tool (INSTRUCT)

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "version": {
      "type": "string",
      "description": "Version number (e.g., '1.0.3')",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    }
  },
  "required": ["project_path", "version"],
  "additionalProperties": false
}
```

---

## TextContent Response Format

### MCP TextContent Object Schema

All tool responses use the MCP `TextContent` type for consistent output formatting.

**Type Definition:**
```python
from mcp.types import TextContent

TextContent(
    type: str,      # Always "text"
    text: str       # Response content
)
```

**JSON Representation:**
```json
{
  "type": "text",
  "text": "Response content here"
}
```

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "type": {
      "type": "string",
      "const": "text",
      "description": "Content type identifier"
    },
    "text": {
      "type": "string",
      "description": "Response payload",
      "minLength": 1
    }
  },
  "required": ["type", "text"],
  "additionalProperties": false
}
```

---

## Directory Structure Schema

### File System Layout

**Root Directory:** `{SERVER_DIR}/` (location of server.py)

**Complete Structure:**
```
docs-mcp/                          # SERVER_DIR
├── server.py                      # MCP entry (264 lines)
├── tool_handlers.py               # 7 tool handlers (516 lines)
├── error_responses.py             # ErrorResponse factory (156 lines)
├── type_defs.py                   # TypedDict definitions (83 lines)
├── logger_config.py               # Logging infrastructure (123 lines)
├── constants.py                   # Paths, files, enums (62 lines)
├── validation.py                  # Input validation (169 lines)
├── generators/                    # Generator classes (574 lines total)
│   ├── __init__.py
│   ├── base_generator.py         # Abstract base (215 lines)
│   ├── foundation_generator.py   # Foundation docs (187 lines)
│   └── changelog_generator.py    # Changelog CRUD (172 lines)
├── templates/power/               # POWER framework templates
│   ├── readme.txt
│   ├── architecture.txt
│   ├── api.txt
│   ├── components.txt
│   ├── schema.txt
│   └── user-guide.txt
├── coderef/
│   ├── foundation-docs/          # Generated foundation docs
│   │   ├── ARCHITECTURE.md
│   │   ├── API.md
│   │   ├── COMPONENTS.md
│   │   └── SCHEMA.md
│   ├── changelog/                # Changelog system
│   │   ├── CHANGELOG.json        # Structured changelog
│   │   └── schema.json           # JSON schema
│   └── quickref.md               # Quick reference
├── CLAUDE.md                      # AI assistant context
├── README.md                      # Project documentation
└── user-guide.md                  # User guide
```

**Total Code:** 2,121 lines across 10 Python modules

---

## Schema Versioning

### Version Format

**Schema Version:** `{major}.{minor}.{patch}`

**Current Version:** 1.1.0

**Version Components:**
- **Major:** Breaking changes to data structures or validation rules
- **Minor:** Backward-compatible additions (new TypedDicts, enum values, etc.)
- **Patch:** Documentation fixes, clarifications

**Version History:**
- **1.1.0** (2025-10-09): Major architecture refactoring - Added TypedDict schema, ErrorResponse schema, validation schema, logging schema, constants/enums schema
- **1.0.3** (2025-10-09): Added changelog JSON schema, updated for 7 tools
- **1.0.2** (2025-10-09): Added changelog management schemas
- **1.0.0** (2025-10-08): Initial schema documentation

### Compatibility Rules

**Backward Compatibility:**
1. TypedDict definitions must remain compatible
2. Enum values cannot be removed (only added)
3. Required fields in schemas cannot be removed
4. Validation rules must not become more restrictive
5. Error response formats must remain consistent

**Breaking Changes (require major version bump):**
- Removing TypedDict fields
- Removing enum values
- Adding required fields to existing schemas
- Changing validation patterns
- Modifying error response structure

**Compatible Changes (minor version bump):**
- Adding new TypedDict definitions
- Adding new enum values
- Adding optional fields to schemas
- Adding new validation functions
- Adding new error response types

---

## AI Integration Notes

This schema documentation is optimized for AI assistant integration in the v1.1.0 modular architecture. Key usage patterns:

**For Type Safety:**
1. Reference TypedDict definitions when constructing complex data structures
2. Use type hints from `type_defs.py` for better IDE support
3. Validate data against TypedDict schemas before processing

**For Validation:**
1. Call validation functions from `validation.py` at MCP tool boundaries
2. Use enum values from `constants.py` for type-safe parameter checking
3. Handle `ValueError` exceptions from validation functions

**For Error Handling:**
1. Use `ErrorResponse` factory methods for consistent error formatting
2. Match error patterns to provide context-appropriate messages
3. Include hints when possible to guide users to solutions

**For Logging:**
1. Use `log_tool_call()` for all MCP tool invocations
2. Use `log_error()` for validation and operational errors
3. Use `log_security_event()` for suspicious activity
4. Use `log_performance()` for performance monitoring

**For Changelog Management:**
1. Use changelog schema to validate entries before writing
2. Generate changelog entries that conform to ChangelogDict schema
3. Use ChangeType and Severity enums for type-safe values

---

**🤖 This SCHEMA document documents the v1.1.0 modular architecture data structures**

---

**Maintained by:** willh, Claude Code AI
**Last updated:** 2025-10-09
**Related documents:** README.md, ARCHITECTURE.md, API.md, COMPONENTS.md, user-guide.md, CLAUDE.md
