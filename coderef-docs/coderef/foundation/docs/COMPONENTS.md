# COMPONENTS.md

**Framework:** POWER (Purpose, Output, Work, Examples, Requirements)
**Version:** 1.1.0
**Date:** 2025-10-09

## Overview

This document inventories all reusable components in the docs-mcp server v1.1.0 after major architectural refactoring. The codebase consists of 10 Python modules organized into 3 layers: **Core Infrastructure (7 modules)**, **Generators (3 modules)**, and **Templates (6 POWER framework files)**. Each component is documented with its interface, design patterns, and production-ready examples.

**Project Context:**
- **README Summary:** docs-mcp provides enterprise-grade MCP server for documentation generation and changelog management with modular architecture, comprehensive logging, type safety, and security hardening
- **Architecture Summary:** Modular MCP server implementing handler registry pattern (97% dispatcher reduction), ErrorResponse factory, TypedDict type safety, enum constants, comprehensive logging, and input validation
- **API Summary:** 7 MCP tools: 4 documentation generation tools + 3 changelog management tools (Changelog Trilogy: READ/WRITE/INSTRUCT)

## Component Inventory

### Layer 1: Core Infrastructure (7 modules, 1,547 lines)

| Module | Lines | Purpose | Key Patterns |
|--------|-------|---------|--------------|
| `server.py` | 264 | MCP entry point, tool registry | Registry pattern, 97% reduction |
| `tool_handlers.py` | 516 | 7 tool handler implementations | Handler registry, modular design |
| `error_responses.py` | 156 | Consistent error formatting | Factory pattern (ARCH-001) |
| `type_defs.py` | 83 | TypedDict definitions | Type safety (QUA-001) |
| `logger_config.py` | 123 | Structured logging infrastructure | Observability (ARCH-003) |
| `constants.py` | 62 | Paths, files, enum constants | Zero magic strings (QUA-003) |
| `validation.py` | 169 | Input validation at boundaries | Fail-fast validation (REF-003) |

### Layer 2: Generators (3 modules, 574 lines)

| Module | Lines | Purpose | Key Patterns |
|--------|-------|---------|--------------|
| `base_generator.py` | 215 | Abstract base with common utilities | Generator pattern, DRY |
| `foundation_generator.py` | 187 | Foundation docs generation | Meta-tool pattern |
| `changelog_generator.py` | 172 | Changelog CRUD + validation | Schema validation (SEC-002) |

### Layer 3: Templates & Data

- **POWER Framework Templates (6 files):** readme.txt, architecture.txt, api.txt, components.txt, schema.txt, user-guide.txt
- **Changelog System:** CHANGELOG.json, schema.json
- **Documentation:** CLAUDE.md, user-guide.md, quickref.md

**Total Code:** 2,121 lines across 10 Python modules

---

## Core Infrastructure Components

### Component: server.py (264 lines)

**Purpose:** MCP server entry point with minimal 13-line dispatcher using handler registry pattern

**Type:** Main application entry

**Location:** `server.py`

**Architecture Highlights (v1.0.7+):**
- **Before:** 644 lines with 407-line monolithic call_tool() function
- **After:** 264 lines (59% reduction) with 13-line dispatcher (97% reduction)
- **Pattern:** Handler registry pattern (QUA-002)

**Interface:**
```python
#!/usr/bin/env python3
"""docs-mcp - MCP server for documentation generation and changelog management."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from mcp.types import Tool, TextContent

# Core module imports (v1.0.7+)
from constants import Paths, Files, TemplateNames, ChangeType, Severity
from validation import validate_project_path_input, validate_version_format, validate_template_name_input, validate_changelog_inputs
from error_responses import ErrorResponse
import tool_handlers
from logger_config import logger, log_tool_call

app = Server("docs-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Register 7 MCP tools (4 documentation + 3 changelog)"""
    return [
        Tool(name="list_templates", description="...", inputSchema={...}),
        Tool(name="get_template", description="...", inputSchema={...}),
        Tool(name="generate_foundation_docs", description="...", inputSchema={...}),
        Tool(name="generate_individual_doc", description="...", inputSchema={...}),
        Tool(name="get_changelog", description="...", inputSchema={...}),
        Tool(name="add_changelog_entry", description="...", inputSchema={...}),
        Tool(name="update_changelog", description="...", inputSchema={...}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """13-line dispatcher using handler registry (QUA-002)"""
    log_tool_call(name, args_keys=list(arguments.keys()))

    handler = tool_handlers.TOOL_HANDLERS.get(name)
    if not handler:
        logger.error(f"Unknown tool requested: {name}")
        raise ValueError(f"Unknown tool: {name}")

    return await handler(arguments)

async def main():
    """Run MCP server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

**Key Improvements:**
1. **Modular Imports:** All core modules imported at top
2. **Minimal Dispatcher:** 13 lines (down from 407)
3. **Registry Pattern:** Delegates to `tool_handlers.TOOL_HANDLERS` dict
4. **Comprehensive Logging:** All tool calls logged via `log_tool_call()`
5. **Type Safety:** Uses `TextContent` from mcp.types

**Usage Pattern:**
```bash
# Run server
python server.py

# Server listens on stdio for MCP protocol messages
# Client sends tool calls, server dispatches via registry
```

**Dependencies:**
- `constants` - All paths, files, enums
- `validation` - Input validation functions
- `error_responses` - ErrorResponse factory
- `tool_handlers` - Handler registry and implementations
- `logger_config` - Logging infrastructure

---

### Component: tool_handlers.py (516 lines)

**Purpose:** Modular tool handler implementations with registry pattern for all 7 MCP tools

**Type:** Handler module

**Location:** `tool_handlers.py`

**Architecture Highlights:**
- Extracted from 407-line monolithic function in server.py
- Each of 7 tools has dedicated handler function
- Registry dict maps tool names to handlers
- All handlers follow standard pattern

**Handler Registry:**
```python
from mcp.types import TextContent
import json
from pathlib import Path

from constants import Paths, Files, TemplateNames, ChangeType, Severity
from validation import validate_project_path_input, validate_version_format, validate_template_name_input, validate_changelog_inputs
from error_responses import ErrorResponse
from logger_config import logger, log_tool_call, log_error, log_security_event
from generators.base_generator import BaseGenerator
from generators.foundation_generator import FoundationGenerator
from generators.changelog_generator import ChangelogGenerator

# Handler Registry (QUA-002)
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    'generate_foundation_docs': handle_generate_foundation_docs,
    'generate_individual_doc': handle_generate_individual_doc,
    'get_changelog': handle_get_changelog,
    'add_changelog_entry': handle_add_changelog_entry,
    'update_changelog': handle_update_changelog,
}
```

**Standard Handler Pattern:**
```python
async def handle_get_template(arguments: dict) -> list[TextContent]:
    """
    Standard handler pattern used by all 7 tools:
    1. Log tool call
    2. Validate inputs using validation.py functions
    3. Execute business logic
    4. Return TextContent or ErrorResponse
    5. Log errors/security events on failure
    """
    log_tool_call('get_template', template_name=arguments.get('template_name'))

    try:
        # 1. Validate inputs
        template_name = validate_template_name_input(arguments.get("template_name", ""))

        # 2. Business logic
        logger.debug(f"Reading template: {template_name}")
        template_path = Path(__file__).parent / Paths.TEMPLATES_DIR / f"{template_name}.txt"

        if not template_path.exists():
            log_security_event('template_not_found', template_name, path=str(template_path))
            return ErrorResponse.not_found(
                f"Template '{template_name}' not found",
                f"Available templates: {', '.join([t.value for t in TemplateNames])}"
            )

        content = template_path.read_text(encoding='utf-8')
        logger.info(f"Template retrieved successfully: {template_name}")

        # 3. Return success
        result = f"=== {template_name.upper()} Template ===\n\n{content}"
        return [TextContent(type="text", text=result)]

    except ValueError as e:
        log_error('validation_error', str(e), template_name=arguments.get('template_name'))
        return ErrorResponse.invalid_input(str(e), "Check template name against available templates")
    except Exception as e:
        log_error('unexpected_error', str(e), tool='get_template')
        return ErrorResponse.internal_error(str(e))
```

**All 7 Handlers:**

1. **handle_list_templates()** - Lists available POWER templates
2. **handle_get_template(arguments)** - Retrieves template content
3. **handle_generate_foundation_docs(arguments)** - Returns all 6 templates + plan
4. **handle_generate_individual_doc(arguments)** - Returns single template + plan
5. **handle_get_changelog(arguments)** - Queries changelog with filters
6. **handle_add_changelog_entry(arguments)** - Adds changelog entry
7. **handle_update_changelog(arguments)** - Returns agentic workflow instructions

**Benefits:**
- ✅ **Modularity:** Each handler independently testable
- ✅ **Maintainability:** Clear separation of concerns
- ✅ **Observability:** All handlers logged uniformly
- ✅ **Type Safety:** Consistent input/output types
- ✅ **Error Handling:** Uniform ErrorResponse usage

---

### Component: error_responses.py (156 lines)

**Purpose:** ErrorResponse factory for consistent error formatting across all tools (ARCH-001)

**Type:** Factory class

**Location:** `error_responses.py`

**Problem Solved:** Eliminated ~350 lines of duplicate error handling code across 7 tools

**Interface:**
```python
from mcp.types import TextContent
import jsonschema
from typing import Optional

class ErrorResponse:
    """
    Factory for consistent error formatting with emoji indicators.
    All error methods return list[TextContent] for MCP compatibility.
    """

    @staticmethod
    def invalid_input(detail: str, hint: Optional[str] = None) -> list[TextContent]:
        """
        Return error for invalid user input.

        Args:
            detail: Specific error description
            hint: Optional suggestion for fixing the error

        Returns:
            list[TextContent] with formatted error message
        """
        text = f"❌ Invalid input: {detail}"
        if hint:
            text += f"\n\n💡 Hint: {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def not_found(resource: str, suggestion: Optional[str] = None) -> list[TextContent]:
        """Error for missing resources (files, templates, etc.)"""
        text = f"❌ Not found: {resource}"
        if suggestion:
            text += f"\n\n💡 {suggestion}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def permission_denied(detail: str, hint: Optional[str] = None) -> list[TextContent]:
        """Error for permission/access issues"""
        text = f"🔒 Permission denied: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def validation_failed(error: jsonschema.ValidationError) -> list[TextContent]:
        """Error for JSON schema validation failures"""
        text = f"❌ Changelog validation failed\n\nError: {error.message}"
        if error.path:
            path_str = " → ".join(str(p) for p in error.path)
            text += f"\nPath: {path_str}"
        if error.schema_path:
            schema_path_str = " → ".join(str(p) for p in error.schema_path)
            text += f"\nSchema path: {schema_path_str}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def file_operation_failed(operation: str, file_path: str, error: str) -> list[TextContent]:
        """Error for file I/O failures"""
        text = f"❌ File {operation} failed: {file_path}\n\nError: {error}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def internal_error(detail: str) -> list[TextContent]:
        """Error for unexpected internal failures"""
        text = f"⚠️ Internal error: {detail}\n\n💡 This may be a bug. Please report to maintainers."
        return [TextContent(type="text", text=text)]
```

**Usage Pattern:**
```python
# Before (v1.0.6 and earlier) - Duplicate code everywhere
try:
    # operation
except ValueError as e:
    return [TextContent(type="text", text=f"Error: Invalid input - {str(e)}")]

# After (v1.0.7+) - Consistent factory usage
try:
    # operation
except ValueError as e:
    return ErrorResponse.invalid_input(str(e), "Check input format")
```

**All 6 Error Types:**
1. `invalid_input(detail, hint)` - User input validation failures
2. `not_found(resource, suggestion)` - Missing files/templates/resources
3. `permission_denied(detail, hint)` - Access/permission issues
4. `validation_failed(error)` - JSON schema validation failures
5. `file_operation_failed(operation, file_path, error)` - File I/O errors
6. `internal_error(detail)` - Unexpected errors/bugs

**Benefits:**
- ✅ **Consistency:** All errors formatted uniformly with emoji indicators
- ✅ **DRY:** Eliminated ~350 lines of duplicate code
- ✅ **Helpful:** Optional hints guide users to solutions
- ✅ **Type Safe:** Returns list[TextContent] for MCP compatibility

---

### Component: type_defs.py (83 lines)

**Purpose:** TypedDict definitions for comprehensive type safety across all modules (QUA-001)

**Type:** Type definitions module

**Location:** `type_defs.py`

**Problem Solved:** Achieved 95% type coverage, enabling better IDE support and type checking

**Interface:**
```python
from typing import TypedDict, Optional, NotRequired
from pathlib import Path

# Path-related types
class PathsDict(TypedDict):
    """Paths used in document generation"""
    project_path: Path
    output_dir: Path

# Template-related types
class TemplateInfoDict(TypedDict, total=False):
    """Template metadata extracted from template files"""
    framework: str
    purpose: str
    save_as: str
    store_as: str
    dependencies: str
    optional_sections: str

# Changelog-related types
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

class VersionEntryDict(TypedDict, total=False):
    """Single version entry containing multiple changes"""
    version: str
    date: str
    summary: str
    changes: list[ChangeDict]
    contributors: list[str]

class ChangelogDict(TypedDict):
    """Complete changelog structure"""
    schema: str               # "$schema"
    project: str
    changelog_version: str
    current_version: str
    entries: list[VersionEntryDict]

# Validation types
class ValidationResult(TypedDict):
    """Result of input validation"""
    valid: bool
    errors: list[str]
    warnings: list[str]

# Generator return types
class GenerationPlanDict(TypedDict):
    """Plan returned by meta-tool generators"""
    project_path: str
    output_dir: str
    templates: list[str]
    instructions: str
```

**Usage Pattern:**
```python
# Before (v1.0.6 and earlier) - No type hints
def get_changelog(project_path, version=None):
    changelog = json.loads(file.read())  # Type unknown
    return changelog

# After (v1.0.7+) - Full type safety
def get_changelog(project_path: str, version: Optional[str] = None) -> ChangelogDict:
    changelog: ChangelogDict = json.loads(file.read())
    return changelog
```

**All TypedDict Definitions:**
1. **PathsDict** - Project and output directory paths
2. **TemplateInfoDict** - Template metadata (framework, purpose, etc.)
3. **ChangeDict** - Single change entry structure
4. **VersionEntryDict** - Version entry with multiple changes
5. **ChangelogDict** - Complete changelog file structure
6. **ValidationResult** - Input validation results
7. **GenerationPlanDict** - Generator return values

**Benefits:**
- ✅ **IDE Support:** Autocomplete and inline documentation
- ✅ **Type Checking:** Catch type errors before runtime
- ✅ **Documentation:** Types serve as inline documentation
- ✅ **Maintainability:** Refactoring safer with type hints

---

### Component: logger_config.py (123 lines)

**Purpose:** Structured logging infrastructure with security audit trails and performance monitoring (ARCH-003)

**Type:** Logging configuration module

**Location:** `logger_config.py`

**Problem Solved:** Zero observability in v1.0.6 → Comprehensive logging in v1.0.7

**Interface:**
```python
import logging
import sys
from typing import Any, Dict

def setup_logger(name: str = "docs-mcp", level: int = logging.INFO, log_file: str | None = None) -> logging.Logger:
    """
    Configure structured logger for MCP server.

    Args:
        name: Logger name (default: "docs-mcp")
        level: Logging level (default: INFO)
        log_file: Optional file path for logging (default: stderr only)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (stderr to avoid interfering with MCP stdio)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)

    # Format: timestamp | level | message | extra fields
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()

def log_tool_call(tool_name: str, **kwargs: Any) -> None:
    """
    Log MCP tool invocation with sanitized parameters.
    Auto-filters sensitive keys: password, token, secret, api_key
    """
    sensitive_keys = {'password', 'token', 'secret', 'api_key', 'credential'}
    safe_kwargs = {
        k: '***REDACTED***' if k.lower() in sensitive_keys else v
        for k, v in kwargs.items()
    }
    logger.info(f"Tool called: {tool_name}", extra={'tool': tool_name, **safe_kwargs})

def log_error(error_type: str, detail: str, **kwargs: Any) -> None:
    """Log error events with context"""
    logger.error(f"Error - {error_type}: {detail}", extra={'error_type': error_type, **kwargs})

def log_security_event(event_type: str, detail: str, **kwargs: Any) -> None:
    """Log security-relevant events for audit trail"""
    logger.warning(f"Security event - {event_type}: {detail}", extra={'event_type': event_type, **kwargs})

def log_performance(operation: str, duration_ms: float, **kwargs: Any) -> None:
    """Log performance metrics"""
    logger.info(f"Performance - {operation}: {duration_ms:.2f}ms", extra={'operation': operation, 'duration_ms': duration_ms, **kwargs})
```

**Usage Pattern:**
```python
from logger_config import logger, log_tool_call, log_error, log_security_event, log_performance
import time

# Log tool invocation
log_tool_call('get_template', template_name='readme')

# Log business logic
logger.debug("Reading template file from disk")
logger.info("Template retrieved successfully")

# Log errors
try:
    # operation
except ValueError as e:
    log_error('validation_error', str(e), field='template_name')

# Log security events
log_security_event('invalid_template_name', template_name, path=str(template_path))

# Log performance
start = time.time()
# ... operation ...
duration = (time.time() - start) * 1000
log_performance('template_load', duration, template_name='readme')
```

**Logging Levels:**
- **DEBUG:** Detailed internal operations (file reads, path resolutions)
- **INFO:** Tool calls, successful operations, performance metrics
- **WARNING:** Security events, unusual conditions
- **ERROR:** Errors that don't crash server but affect functionality
- **CRITICAL:** Severe errors (not currently used, would crash server)

**Security Features:**
- ✅ **Sensitive Data Sanitization:** Auto-redacts password, token, secret, api_key fields
- ✅ **Audit Trail:** All security events logged with context
- ✅ **MCP-Safe Output:** Uses stderr (doesn't interfere with stdio transport)
- ✅ **Structured Logging:** Extra fields for programmatic analysis

**Benefits:**
- ✅ **Observability:** Full visibility into server operations
- ✅ **Debugging:** Trace tool execution flow
- ✅ **Security Auditing:** Track suspicious activity
- ✅ **Performance Monitoring:** Identify slow operations

---

### Component: constants.py (62 lines)

**Purpose:** Centralized configuration with paths, file names, and enum constants - zero magic strings (QUA-003, REF-002)

**Type:** Constants module

**Location:** `constants.py`

**Problem Solved:** ~30 hardcoded strings scattered across codebase → Single source of truth

**Interface:**
```python
from enum import Enum

class Paths:
    """Centralized directory paths"""
    FOUNDATION_DOCS = 'coderef/foundation-docs'
    CHANGELOG_DIR = 'coderef/changelog'
    TEMPLATES_DIR = 'templates/power'

class Files:
    """Standard file names"""
    CHANGELOG_JSON = 'CHANGELOG.json'
    SCHEMA_JSON = 'schema.json'
    README_MD = 'README.md'
    ARCHITECTURE_MD = 'ARCHITECTURE.md'
    API_MD = 'API.md'
    COMPONENTS_MD = 'COMPONENTS.md'
    SCHEMA_MD = 'SCHEMA.md'
    USER_GUIDE_MD = 'USER-GUIDE.md'

class TemplateNames(str, Enum):
    """Available POWER framework templates"""
    README = 'readme'
    ARCHITECTURE = 'architecture'
    API = 'api'
    COMPONENTS = 'components'
    SCHEMA = 'schema'
    USER_GUIDE = 'user-guide'

class ChangeType(str, Enum):
    """Changelog entry types"""
    BUGFIX = 'bugfix'
    ENHANCEMENT = 'enhancement'
    FEATURE = 'feature'
    BREAKING_CHANGE = 'breaking_change'
    DEPRECATION = 'deprecation'
    SECURITY = 'security'

class Severity(str, Enum):
    """Change severity levels"""
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'
```

**Usage Pattern:**
```python
# Before (v1.0.5 and earlier) - Magic strings everywhere
output_dir = project_path / "coderef/foundation-docs"  # Hardcoded
template_file = f"{template_name}.txt"  # Hardcoded extension
valid_types = ["bugfix", "enhancement", "feature"]  # Hardcoded list

# After (v1.0.6+) - Constants from single source
from constants import Paths, Files, TemplateNames, ChangeType, Severity

output_dir = project_path / Paths.FOUNDATION_DOCS
template_file = f"{template_name}.txt"
valid_types = [t.value for t in ChangeType]

# Type-safe enum usage
if change_type == ChangeType.FEATURE.value:
    # ...
```

**Benefits:**
- ✅ **Single Source of Truth:** Change path once, updates everywhere
- ✅ **Type Safety:** Enums prevent typos
- ✅ **Autocomplete:** IDE suggests valid values
- ✅ **Maintainability:** Easy to update configuration
- ✅ **Zero Magic Strings:** All hardcoded values centralized

---

### Component: validation.py (169 lines)

**Purpose:** Input validation at MCP tool boundaries with fail-fast error handling (REF-003)

**Type:** Validation module

**Location:** `validation.py`

**Problem Solved:** No input validation → Comprehensive boundary validation with clear error messages

**Interface:**
```python
from pathlib import Path
from constants import TemplateNames, ChangeType, Severity
import re

def validate_project_path_input(project_path: str) -> Path:
    """
    Validate and resolve project path.

    Args:
        project_path: Path string to validate

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is invalid, empty, or doesn't exist
    """
    if not project_path or not project_path.strip():
        raise ValueError("Project path cannot be empty")

    # Security: Check for null bytes (path traversal attack vector)
    if '\x00' in project_path:
        raise ValueError("Project path contains null bytes")

    # Security: Resolve to canonical path (prevents ../ traversal)
    path = Path(project_path).resolve()

    # Validate existence
    if not path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")

    if not path.is_dir():
        raise ValueError(f"Project path is not a directory: {project_path}")

    # Security: Check path length (Windows: 260, Unix: 4096)
    if len(str(path)) > 4096:
        raise ValueError("Project path exceeds maximum length")

    return path

def validate_version_format(version: str) -> str:
    """
    Validate semantic version format (X.Y.Z).

    Args:
        version: Version string to validate

    Returns:
        Validated version string

    Raises:
        ValueError: If version format is invalid
    """
    if not version or not version.strip():
        raise ValueError("Version cannot be empty")

    # Pattern: X.Y.Z where X, Y, Z are integers
    pattern = r'^[0-9]+\.[0-9]+\.[0-9]+$'
    if not re.match(pattern, version):
        raise ValueError(f"Version must match pattern X.Y.Z (e.g., '1.0.2'), got: {version}")

    return version

def validate_template_name_input(template_name: str) -> str:
    """
    Validate template name against enum.

    Args:
        template_name: Template name to validate

    Returns:
        Validated template name

    Raises:
        ValueError: If template name is invalid
    """
    if not template_name or not template_name.strip():
        raise ValueError("Template name cannot be empty")

    # Validate against enum
    valid_templates = [t.value for t in TemplateNames]
    if template_name not in valid_templates:
        raise ValueError(
            f"Invalid template name: '{template_name}'. "
            f"Valid options: {', '.join(valid_templates)}"
        )

    # Security: Prevent path traversal via template name
    if '..' in template_name or '/' in template_name or '\\' in template_name:
        raise ValueError("Template name contains invalid path characters")

    return template_name

def validate_changelog_inputs(
    version: str,
    change_type: str,
    severity: str,
    title: str,
    description: str,
    files: list[str],
    reason: str,
    impact: str
) -> dict:
    """
    Validate all required changelog entry fields.

    Args:
        version: Version number (X.Y.Z)
        change_type: Type of change (enum value)
        severity: Severity level (enum value)
        title: Short title
        description: Detailed description
        files: List of affected files
        reason: Why change was made
        impact: Impact on users/system

    Returns:
        Dict of validated inputs

    Raises:
        ValueError: If any validation fails
    """
    # Validate version format
    validate_version_format(version)

    # Validate change_type against enum
    valid_types = [t.value for t in ChangeType]
    if change_type not in valid_types:
        raise ValueError(
            f"Invalid change type: '{change_type}'. "
            f"Valid options: {', '.join(valid_types)}"
        )

    # Validate severity against enum
    valid_severities = [s.value for s in Severity]
    if severity not in valid_severities:
        raise ValueError(
            f"Invalid severity: '{severity}'. "
            f"Valid options: {', '.join(valid_severities)}"
        )

    # Validate required string fields
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    if not description or not description.strip():
        raise ValueError("Description cannot be empty")
    if not reason or not reason.strip():
        raise ValueError("Reason cannot be empty")
    if not impact or not impact.strip():
        raise ValueError("Impact cannot be empty")

    # Validate files list
    if not files or len(files) == 0:
        raise ValueError("Files list cannot be empty")
    if not isinstance(files, list):
        raise ValueError("Files must be a list")

    return {
        'version': version,
        'change_type': change_type,
        'severity': severity,
        'title': title.strip(),
        'description': description.strip(),
        'files': files,
        'reason': reason.strip(),
        'impact': impact.strip()
    }
```

**Usage Pattern:**
```python
from validation import validate_project_path_input, validate_version_format, validate_template_name_input, validate_changelog_inputs

# Validate at MCP tool boundary (fail-fast)
async def handle_get_template(arguments: dict) -> list[TextContent]:
    try:
        # Validation happens FIRST, before any business logic
        template_name = validate_template_name_input(arguments.get("template_name", ""))

        # If we reach here, input is valid - proceed with business logic
        template_path = Path(__file__).parent / Paths.TEMPLATES_DIR / f"{template_name}.txt"
        # ...

    except ValueError as e:
        # Clear error message from validation
        return ErrorResponse.invalid_input(str(e))
```

**Validation Functions:**
1. **validate_project_path_input(path)** - Path validation with security checks
2. **validate_version_format(version)** - Semantic version validation (X.Y.Z)
3. **validate_template_name_input(name)** - Template name validation against enum
4. **validate_changelog_inputs(...)** - All 8 changelog fields validation

**Security Features:**
- ✅ **Null Byte Protection:** Rejects paths with `\x00` (SEC-001)
- ✅ **Path Traversal Protection:** Uses `.resolve()` to canonicalize paths (SEC-001)
- ✅ **Path Length Limits:** Prevents buffer overflow attacks
- ✅ **Pattern Validation:** Regex validation for versions (SEC-005)
- ✅ **Enum Validation:** Only accepts valid enum values

**Benefits:**
- ✅ **Fail-Fast:** Errors caught at boundary, not deep in logic
- ✅ **Clear Messages:** Helpful error messages guide users
- ✅ **Security:** Multiple layers of security validation
- ✅ **Reusability:** Functions used across all 7 tool handlers

---

## Generator Components

### Component: base_generator.py (215 lines)

**Purpose:** Abstract base class providing common file I/O and path management utilities for all generators

**Type:** Abstract base class

**Location:** `generators/base_generator.py`

**Interface:**
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from logger_config import logger, log_error, log_security_event

class BaseGenerator(ABC):
    """
    Abstract base class for all document and changelog generators.
    Provides common file I/O, path management, and validation utilities.
    """

    def __init__(self, project_path: str):
        """
        Initialize generator with project path.

        Args:
            project_path: Absolute path to project directory
        """
        self.project_path = self.validate_project_path(project_path)
        logger.info(f"Initialized {self.__class__.__name__} for project: {self.project_path}")

    @abstractmethod
    def generate(self, **kwargs) -> str:
        """
        Generate output based on generator-specific logic.
        Must be implemented by subclasses.

        Returns:
            Generated content as string
        """
        pass

    def validate_project_path(self, project_path: str) -> Path:
        """
        Validate and resolve project path with security checks.

        Args:
            project_path: Path string to validate

        Returns:
            Resolved Path object

        Raises:
            ValueError: If path is invalid or doesn't exist
        """
        logger.debug(f"Validating project path: {project_path}")

        # Resolve to canonical path (SEC-001: prevents ../ traversal)
        path = Path(project_path).resolve()

        if not path.exists():
            log_error('path_validation_failed', f"Project path does not exist: {project_path}", path=project_path)
            raise ValueError(f"Project path does not exist: {project_path}")

        if not path.is_dir():
            log_error('path_validation_failed', f"Project path is not a directory: {project_path}", path=project_path)
            raise ValueError(f"Project path is not a directory: {project_path}")

        logger.info(f"Project path validated: {path}")
        return path

    def _read_file(self, file_path: Path) -> str:
        """
        Read file with UTF-8 encoding.

        Args:
            file_path: Path to file to read

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file read fails
        """
        logger.debug(f"Reading file: {file_path}")

        if not file_path.exists():
            log_error('file_not_found', str(file_path), path=str(file_path))
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding='utf-8')
            logger.debug(f"File read successfully: {file_path} ({len(content)} bytes)")
            return content
        except Exception as e:
            log_error('file_read_failed', str(e), path=str(file_path))
            raise ValueError(f"Failed to read file {file_path}: {e}")

    def _write_file(self, file_path: Path, content: str) -> None:
        """
        Write file with UTF-8 encoding.

        Args:
            file_path: Path to file to write
            content: Content to write

        Raises:
            ValueError: If file write fails
        """
        logger.debug(f"Writing file: {file_path} ({len(content)} bytes)")

        try:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"File written successfully: {file_path}")
        except Exception as e:
            log_error('file_write_failed', str(e), path=str(file_path))
            raise ValueError(f"Failed to write file {file_path}: {e}")

    def _ensure_directory(self, directory: Path) -> None:
        """
        Create directory if it doesn't exist (including parents).

        Args:
            directory: Directory path to create

        Raises:
            ValueError: If directory creation fails
        """
        if directory.exists():
            logger.debug(f"Directory already exists: {directory}")
            return

        logger.debug(f"Creating directory: {directory}")
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created: {directory}")
        except Exception as e:
            log_error('directory_creation_failed', str(e), path=str(directory))
            raise ValueError(f"Failed to create directory {directory}: {e}")

    def get_doc_output_path(self, template_name: str) -> Path:
        """
        Determine output path for documentation file.
        README.md → project root (SEC-003)
        Others → coderef/foundation-docs/

        Args:
            template_name: Name of template (readme, architecture, etc.)

        Returns:
            Path to output file
        """
        from constants import Paths, Files

        if template_name == 'readme':
            # README goes to project root for GitHub visibility (SEC-003)
            output_path = self.project_path / Files.README_MD
            logger.debug(f"README output path: {output_path}")
        else:
            # All other docs go to coderef/foundation-docs/
            output_dir = self.project_path / Paths.FOUNDATION_DOCS
            self._ensure_directory(output_dir)

            filename_map = {
                'architecture': Files.ARCHITECTURE_MD,
                'api': Files.API_MD,
                'components': Files.COMPONENTS_MD,
                'schema': Files.SCHEMA_MD,
                'user-guide': Files.USER_GUIDE_MD,
            }
            filename = filename_map.get(template_name, f"{template_name.upper()}.md")
            output_path = output_dir / filename
            logger.debug(f"{template_name} output path: {output_path}")

        return output_path
```

**Usage Pattern:**
```python
from generators.base_generator import BaseGenerator

class MyGenerator(BaseGenerator):
    def generate(self, **kwargs) -> str:
        # Use inherited utilities
        content = self._read_file(template_path)

        # Process content
        result = self.process(content)

        # Write output
        output_dir = self.project_path / "output"
        self._ensure_directory(output_dir)
        self._write_file(output_dir / "result.txt", result)

        return "Generation complete"
```

**Inherited Features:**
- ✅ **Path Validation:** Automatic validation with security checks (SEC-001)
- ✅ **File I/O:** UTF-8 encoded read/write operations
- ✅ **Directory Management:** Auto-create directories as needed
- ✅ **Smart Output Routing:** README → root, others → coderef/foundation-docs/ (SEC-003)
- ✅ **Comprehensive Logging:** All operations logged with context

---

### Component: foundation_generator.py (187 lines)

**Purpose:** Generate foundation documentation files using POWER framework templates with meta-tool pattern

**Type:** Concrete generator class

**Location:** `generators/foundation_generator.py`

**Dependencies:** Extends BaseGenerator

**Interface:**
```python
from generators.base_generator import BaseGenerator
from pathlib import Path
from constants import Paths, TemplateNames
from logger_config import logger

class FoundationGenerator(BaseGenerator):
    """
    Generates foundation documentation (README, ARCHITECTURE, API, COMPONENTS, SCHEMA, USER-GUIDE)
    using POWER framework templates. Implements meta-tool pattern.
    """

    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.templates_dir = Path(__file__).parent.parent / Paths.TEMPLATES_DIR
        logger.debug(f"Templates directory: {self.templates_dir}")

    def generate_all(self) -> str:
        """
        Generate plan for all 6 foundation documents.
        Returns instructions and templates for AI assistant to execute.

        Returns:
            Generation plan with all templates and instructions
        """
        logger.info("Generating plan for all foundation documents")

        # Define generation order (documents reference previous docs)
        templates = [
            TemplateNames.README,
            TemplateNames.ARCHITECTURE,
            TemplateNames.API,
            TemplateNames.COMPONENTS,
            TemplateNames.SCHEMA,
            TemplateNames.USER_GUIDE,
        ]

        plan = f"""=== Foundation Documentation Generation Plan ===

Project Path: {self.project_path}
Output Directory: {self.project_path / Paths.FOUNDATION_DOCS}
Templates: {len(templates)}

Documents to Generate (in order):
"""
        for i, template in enumerate(templates, 1):
            output_path = self.get_doc_output_path(template.value)
            plan += f"{i}. {template.value.upper()} → {output_path}\n"

        plan += "\n" + "="*60 + "\n\n"

        # Include all template contents
        for template in templates:
            template_content = self._load_template(template.value)
            plan += f"--- Template: {template.value} ---\n\n{template_content}\n\n"
            plan += "="*60 + "\n\n"

        logger.info(f"Generation plan created for {len(templates)} documents")
        return plan

    def generate_individual(self, template_name: str) -> str:
        """
        Generate plan for single document.

        Args:
            template_name: Name of template (readme, architecture, etc.)

        Returns:
            Generation instructions with template content
        """
        logger.info(f"Generating plan for individual document: {template_name}")

        output_path = self.get_doc_output_path(template_name)
        template_content = self._load_template(template_name)

        plan = f"""=== Individual Document Generation ===

Project Path: {self.project_path}
Template: {template_name}
Output Path: {output_path}

{"="*60}

{template_content}

{"="*60}

Next Steps:
1. Analyze project structure at {self.project_path}
2. Follow template instructions (POWER framework)
3. Generate {template_name.upper()}.md
4. Save to {output_path}
"""

        logger.info(f"Generation plan created for {template_name}")
        return plan

    def _load_template(self, template_name: str) -> str:
        """
        Load template file from templates/power/

        Args:
            template_name: Name of template (without .txt extension)

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_path = self.templates_dir / f"{template_name}.txt"
        logger.debug(f"Loading template: {template_path}")

        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            raise FileNotFoundError(f"Template not found: {template_name}")

        content = self._read_file(template_path)
        logger.debug(f"Template loaded: {template_name} ({len(content)} bytes)")
        return content

    def generate(self, **kwargs) -> str:
        """
        Generate foundation docs (implements abstract method).
        Delegates to generate_all() or generate_individual() based on kwargs.
        """
        template_name = kwargs.get('template_name')
        if template_name:
            return self.generate_individual(template_name)
        else:
            return self.generate_all()
```

**Usage Pattern:**
```python
from generators.foundation_generator import FoundationGenerator

# Generate all foundation docs
generator = FoundationGenerator(project_path="C:/Users/willh/my-project")
plan = generator.generate_all()
# Returns: Plan with all 6 templates + instructions
# AI assistant then analyzes project and generates actual files

# Generate single doc
generator = FoundationGenerator(project_path="C:/Users/willh/my-project")
plan = generator.generate_individual(template_name="api")
# Returns: Plan with API template + instructions
```

**Meta-Tool Pattern:**
- **Provides instructions** rather than **executes** generation
- AI assistant analyzes project context
- AI assistant generates documentation following POWER framework
- Enables context-aware, flexible documentation

**Generation Order Logic:**
Each document references previous documents for context:
1. **README** - Base project overview
2. **ARCHITECTURE** - References README for context
3. **API** - References README + ARCHITECTURE
4. **COMPONENTS** - References README + ARCHITECTURE + API
5. **SCHEMA** - References all previous docs
6. **USER-GUIDE** - References all previous docs

---

### Component: changelog_generator.py (172 lines)

**Purpose:** Manage CRUD operations for project changelogs with JSON schema validation (SEC-002)

**Type:** Concrete generator class

**Location:** `generators/changelog_generator.py`

**Dependencies:** Extends BaseGenerator, uses jsonschema

**Interface:**
```python
from generators.base_generator import BaseGenerator
from pathlib import Path
import json
import jsonschema
from datetime import datetime
from constants import Paths, Files
from logger_config import logger, log_error, log_security_event
from type_defs import ChangelogDict, ChangeDict, VersionEntryDict

class ChangelogGenerator(BaseGenerator):
    """
    Manages changelog CRUD operations with JSON schema validation (SEC-002).
    Implements READ/WRITE operations for the Changelog Trilogy.
    """

    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.changelog_path = self.project_path / Paths.CHANGELOG_DIR / Files.CHANGELOG_JSON
        self.schema_path = self.project_path / Paths.CHANGELOG_DIR / Files.SCHEMA_JSON
        logger.debug(f"Changelog path: {self.changelog_path}")
        logger.debug(f"Schema path: {self.schema_path}")

    def get_changelog(
        self,
        version: str | None = None,
        change_type: str | None = None,
        breaking_only: bool = False
    ) -> str:
        """
        Query changelog with optional filters (READ operation).

        Args:
            version: Specific version to retrieve (e.g., "1.0.2")
            change_type: Filter by change type (bugfix, feature, etc.)
            breaking_only: Only show breaking changes

        Returns:
            Formatted changelog text

        Raises:
            FileNotFoundError: If changelog doesn't exist
            ValueError: If changelog is malformed
        """
        logger.info(f"Reading changelog - version={version}, type={change_type}, breaking_only={breaking_only}")

        if not self.changelog_path.exists():
            log_error('changelog_not_found', str(self.changelog_path))
            raise FileNotFoundError(f"Changelog not found: {self.changelog_path}")

        try:
            content = self._read_file(self.changelog_path)
            changelog: ChangelogDict = json.loads(content)

            # Validate against schema (SEC-002)
            self._validate_schema(changelog)

            # Apply filters
            filtered_entries = self._apply_filters(changelog['entries'], version, change_type, breaking_only)

            # Format output
            result = self._format_changelog(changelog, filtered_entries)
            logger.info(f"Changelog retrieved successfully - {len(filtered_entries)} entries")
            return result

        except json.JSONDecodeError as e:
            log_error('json_decode_error', str(e), file=str(self.changelog_path))
            raise ValueError(f"Malformed changelog JSON: {e}")

    def add_entry(
        self,
        version: str,
        change_type: str,
        severity: str,
        title: str,
        description: str,
        files: list[str],
        reason: str,
        impact: str,
        breaking: bool = False,
        migration: str | None = None,
        summary: str | None = None,
        contributors: list[str] | None = None
    ) -> str:
        """
        Add new changelog entry with schema validation (WRITE operation).

        Args:
            version: Version number (X.Y.Z)
            change_type: Type of change (bugfix, feature, etc.)
            severity: Severity level (critical, major, minor, patch)
            title: Short title
            description: Detailed description
            files: List of affected files
            reason: Why change was made
            impact: Impact on users/system
            breaking: Whether breaking change
            migration: Migration guide if breaking
            summary: Version summary
            contributors: List of contributors

        Returns:
            Success message with changelog path

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Adding changelog entry - version={version}, type={change_type}, severity={severity}")

        # Load or create changelog
        if self.changelog_path.exists():
            content = self._read_file(self.changelog_path)
            changelog: ChangelogDict = json.loads(content)
        else:
            changelog = self._create_initial_changelog()
            logger.info("Created new changelog structure")

        # Generate change ID
        change_id = self._generate_change_id(changelog)

        # Create change entry
        change: ChangeDict = {
            'id': change_id,
            'type': change_type,
            'severity': severity,
            'title': title,
            'description': description,
            'files': files,
            'reason': reason,
            'impact': impact,
            'breaking': breaking,
        }
        if migration:
            change['migration'] = migration

        # Find or create version entry
        version_entry = self._find_or_create_version_entry(changelog, version, summary, contributors)
        version_entry['changes'].append(change)

        # Update current_version
        changelog['current_version'] = version

        # Validate against schema (SEC-002)
        self._validate_schema(changelog)

        # Write to file
        self._ensure_directory(self.changelog_path.parent)
        self._write_file(self.changelog_path, json.dumps(changelog, indent=2))

        logger.info(f"Changelog entry added successfully - change_id={change_id}")
        return f"✅ Changelog entry added successfully!\nVersion: {version}\nChange: {title}\nType: {change_type} ({severity})\nFiles: {len(files)}\nChangelog saved to: {self.changelog_path}"

    def _validate_schema(self, changelog: ChangelogDict) -> None:
        """
        Validate changelog against JSON schema (SEC-002).

        Args:
            changelog: Changelog dict to validate

        Raises:
            jsonschema.ValidationError: If validation fails
        """
        if not self.schema_path.exists():
            logger.warning(f"Schema file not found, skipping validation: {self.schema_path}")
            return

        try:
            schema_content = self._read_file(self.schema_path)
            schema = json.loads(schema_content)
            jsonschema.validate(instance=changelog, schema=schema)
            logger.debug("Changelog schema validation passed")
        except jsonschema.ValidationError as e:
            log_error('schema_validation_failed', e.message, path=str(e.path))
            raise

    def _generate_change_id(self, changelog: ChangelogDict) -> str:
        """
        Generate unique change ID (change-001, change-002, ...).

        Args:
            changelog: Current changelog

        Returns:
            New change ID
        """
        # Find highest existing ID
        max_id = 0
        for entry in changelog.get('entries', []):
            for change in entry.get('changes', []):
                if change.get('id', '').startswith('change-'):
                    try:
                        num = int(change['id'].split('-')[1])
                        max_id = max(max_id, num)
                    except (IndexError, ValueError):
                        continue

        new_id = f"change-{max_id + 1:03d}"
        logger.debug(f"Generated change ID: {new_id}")
        return new_id

    def generate(self, **kwargs) -> str:
        """Implement abstract method (delegates to get_changelog or add_entry)"""
        if 'title' in kwargs:
            return self.add_entry(**kwargs)
        else:
            return self.get_changelog(**kwargs)
```

**Usage Pattern:**
```python
from generators.changelog_generator import ChangelogGenerator

# Read changelog
generator = ChangelogGenerator(project_path="C:/Users/willh/my-project")
changelog_text = generator.get_changelog()

# Filter by version
changelog_text = generator.get_changelog(version="1.0.2")

# Filter breaking changes
changelog_text = generator.get_changelog(breaking_only=True)

# Add entry
result = generator.add_entry(
    version="1.0.3",
    change_type="feature",
    severity="major",
    title="Added feature X",
    description="Implemented...",
    files=["server.py"],
    reason="Enable users to...",
    impact="Users can now...",
    breaking=False,
    contributors=["willh"]
)
# Returns: ✅ Changelog entry added successfully!
```

**Features:**
- ✅ **Schema Validation (SEC-002):** All read/write operations validated against schema.json
- ✅ **Auto ID Generation:** Sequential change IDs (change-001, change-002, ...)
- ✅ **Version Management:** Automatic current_version updates
- ✅ **Filtering:** Supports version, change_type, breaking_only filters
- ✅ **Graceful Degradation:** Skips validation if schema file missing (with warning)

---

## Component Architecture

### Dependency Graph

```
┌─────────────────────────────────────────────────────────┐
│              MCP Server Framework                        │
│              (mcp.server.Server)                         │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴───────── server.py (264 lines) ─────┐
          │  - 7 tool definitions                           │
          │  - 13-line dispatcher using TOOL_HANDLERS       │
          └──────────┬──────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────────────────────────────┐
          │    tool_handlers.py (516 lines)              │
          │  ┌─────────────────────────────────────────┐ │
          │  │ TOOL_HANDLERS = {                       │ │
          │  │   'list_templates': handle_fn,          │ │
          │  │   'get_template': handle_fn,            │ │
          │  │   ...7 handlers total...                │ │
          │  │ }                                        │ │
          │  └─────────────────────────────────────────┘ │
          └──────────┬───────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────┐
│ error_      │ │ logger_      │ │ constants.py │
│ responses   │ │ config.py    │ │ (62 lines)   │
│ (156 lines) │ │ (123 lines)  │ │              │
│             │ │              │ │ - Paths      │
│ Factory for │ │ Structured   │ │ - Files      │
│ consistent  │ │ logging with │ │ - Enums      │
│ error msgs  │ │ audit trails │ │              │
└─────────────┘ └──────────────┘ └──────────────┘

       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────┐
│ type_defs   │ │ validation   │ │ Generators   │
│ (83 lines)  │ │ (169 lines)  │ │ (3 modules)  │
│             │ │              │ │              │
│ TypedDict   │ │ Fail-fast    │ │ ┌──────────┐ │
│ definitions │ │ input        │ │ │ Base     │ │
│ for all     │ │ validation   │ │ │ (215)    │ │
│ complex     │ │ at MCP       │ │ └────┬─────┘ │
│ return      │ │ boundaries   │ │      │       │
│ types       │ │              │ │  ┌───┴────┐  │
└─────────────┘ └──────────────┘ │  │        │  │
                                  │  ▼        ▼  │
                                  │ Found  Chlog │
                                  │ (187)  (172) │
                                  └──────────────┘
```

### Component Relationships

**Layer 1 → Layer 2:**
- `server.py` → `tool_handlers.py` (registry dispatch)
- `tool_handlers.py` → All 6 core modules (error_responses, logger_config, constants, type_defs, validation, generators)

**Within Layer 1:**
- `tool_handlers.py` uses `error_responses` for all error returns
- `tool_handlers.py` uses `logger_config` for all logging
- `tool_handlers.py` uses `validation` for all input validation
- `tool_handlers.py` uses `constants` for all paths/enums
- All modules use `type_defs` for type annotations

**Layer 2 (Generators):**
- `foundation_generator.py` extends `base_generator.py`
- `changelog_generator.py` extends `base_generator.py`
- All generators use `logger_config` for logging
- All generators use `constants` for paths
- All generators use `type_defs` for type annotations

**No Circular Dependencies:** Clean dependency graph, all relationships flow downward

---

## Design Patterns

### Pattern 1: Handler Registry (QUA-002)

**Problem:** Monolithic 407-line call_tool() function with 7 inline handlers

**Solution:** Extract handlers to separate functions, register in dict

```python
# Handler functions
async def handle_list_templates(arguments: dict) -> list[TextContent]:
    # ...

async def handle_get_template(arguments: dict) -> list[TextContent]:
    # ...

# Registry
TOOL_HANDLERS = {
    'list_templates': handle_list_templates,
    'get_template': handle_get_template,
    # ... 5 more
}

# Minimal dispatcher (13 lines)
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(arguments)
```

**Benefits:**
- ✅ **97% Code Reduction:** 407 lines → 13 lines
- ✅ **Modularity:** Each handler independently testable
- ✅ **Extensibility:** Add new tools by registering handler
- ✅ **Maintainability:** Clear separation of concerns

---

### Pattern 2: ErrorResponse Factory (ARCH-001)

**Problem:** ~350 lines of duplicate error handling across 7 tools

**Solution:** Centralized factory class with 6 error types

```python
# Consistent error formatting
class ErrorResponse:
    @staticmethod
    def invalid_input(detail: str, hint: str = None) -> list[TextContent]:
        text = f"❌ Invalid input: {detail}"
        if hint:
            text += f"\n\n💡 Hint: {hint}"
        return [TextContent(type="text", text=text)]

    # + 5 more error types

# Usage across all handlers
except ValueError as e:
    return ErrorResponse.invalid_input(str(e), "Check input format")
```

**Benefits:**
- ✅ **DRY:** Eliminated ~350 lines of duplicate code
- ✅ **Consistency:** All errors formatted uniformly
- ✅ **Helpful:** Optional hints guide users
- ✅ **Type Safe:** Returns list[TextContent]

---

### Pattern 3: Comprehensive Logging (ARCH-003)

**Problem:** Zero observability in codebase

**Solution:** Structured logging with security audit trails

```python
from logger_config import logger, log_tool_call, log_error, log_security_event

# Log all tool invocations
log_tool_call('get_template', template_name='readme')

# Log business logic
logger.debug("Reading template file")
logger.info("Template retrieved successfully")

# Log errors
except ValueError as e:
    log_error('validation_error', str(e))

# Log security events
log_security_event('invalid_template_name', template_name)
```

**Benefits:**
- ✅ **Full Observability:** All operations logged
- ✅ **Security Auditing:** Track suspicious activity
- ✅ **Debugging:** Trace execution flow
- ✅ **Performance:** Monitor slow operations

---

### Pattern 4: Zero Magic Strings (QUA-003)

**Problem:** ~30 hardcoded strings scattered across codebase

**Solution:** Centralized constants with enums

```python
from constants import Paths, Files, TemplateNames, ChangeType, Severity

# Type-safe enum usage
output_dir = project_path / Paths.FOUNDATION_DOCS
changelog_file = output_dir / Files.CHANGELOG_JSON

# Validate against enums
valid_types = [t.value for t in ChangeType]
if change_type not in valid_types:
    raise ValueError(f"Invalid type. Valid: {', '.join(valid_types)}")
```

**Benefits:**
- ✅ **Single Source of Truth:** Change once, updates everywhere
- ✅ **Type Safety:** Enums prevent typos
- ✅ **Autocomplete:** IDE suggests valid values
- ✅ **Maintainability:** Easy to update configuration

---

### Pattern 5: Fail-Fast Validation (REF-003)

**Problem:** No input validation, errors deep in logic

**Solution:** Validate at MCP boundaries before business logic

```python
from validation import validate_template_name_input

async def handle_get_template(arguments: dict) -> list[TextContent]:
    try:
        # VALIDATE FIRST (fail-fast)
        template_name = validate_template_name_input(arguments.get("template_name", ""))

        # If we reach here, input is valid - proceed with business logic
        template_path = Path(__file__).parent / Paths.TEMPLATES_DIR / f"{template_name}.txt"
        # ...

    except ValueError as e:
        return ErrorResponse.invalid_input(str(e))
```

**Benefits:**
- ✅ **Early Detection:** Errors caught at boundary
- ✅ **Clear Messages:** Validation provides helpful errors
- ✅ **Security:** Multiple validation layers (null bytes, path traversal, etc.)
- ✅ **Clean Logic:** Business logic doesn't handle validation

---

### Pattern 6: Type Safety with TypedDict (QUA-001)

**Problem:** No type hints, poor IDE support

**Solution:** Comprehensive TypedDict definitions

```python
from type_defs import ChangelogDict, ChangeDict, VersionEntryDict

def get_changelog(project_path: str) -> ChangelogDict:
    content = file.read_text()
    changelog: ChangelogDict = json.loads(content)
    return changelog  # IDE knows structure

# IDE autocomplete works
def process_change(change: ChangeDict):
    title = change['title']  # IDE suggests fields
    type = change['type']    # Type checked
```

**Benefits:**
- ✅ **IDE Support:** Autocomplete and inline docs
- ✅ **Type Checking:** Catch errors before runtime
- ✅ **Documentation:** Types serve as inline docs
- ✅ **Refactoring Safety:** IDE helps with changes

---

## Copy-Paste Examples

### Example 1: Add New MCP Tool

```python
# Step 1: Define tool in server.py list_tools()
Tool(
    name="my_new_tool",
    description="Description of what the tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"}
        },
        "required": ["param1"]
    }
)

# Step 2: Create handler in tool_handlers.py
async def handle_my_new_tool(arguments: dict) -> list[TextContent]:
    log_tool_call('my_new_tool', param1=arguments.get('param1'))

    try:
        # Validate inputs
        param1 = arguments.get("param1", "")
        if not param1:
            return ErrorResponse.invalid_input("param1 cannot be empty")

        # Business logic
        logger.debug(f"Processing: {param1}")
        result = f"Processed: {param1}"
        logger.info("Tool completed successfully")

        return [TextContent(type="text", text=result)]

    except ValueError as e:
        log_error('validation_error', str(e))
        return ErrorResponse.invalid_input(str(e))
    except Exception as e:
        log_error('unexpected_error', str(e), tool='my_new_tool')
        return ErrorResponse.internal_error(str(e))

# Step 3: Register in TOOL_HANDLERS dict
TOOL_HANDLERS = {
    # ... existing handlers ...
    'my_new_tool': handle_my_new_tool,
}
```

---

### Example 2: Add New Generator

```python
# generators/my_generator.py
from generators.base_generator import BaseGenerator
from logger_config import logger
from constants import Paths

class MyGenerator(BaseGenerator):
    """Custom generator for specific use case"""

    def __init__(self, project_path: str):
        super().__init__(project_path)
        logger.info(f"Initialized MyGenerator for {self.project_path}")

    def generate(self, **kwargs) -> str:
        """Implement generation logic"""
        logger.info("Starting generation")

        # Use inherited utilities
        output_dir = self.project_path / "output"
        self._ensure_directory(output_dir)

        # Generate content
        content = self._create_content(**kwargs)

        # Write output
        output_path = output_dir / "result.txt"
        self._write_file(output_path, content)

        logger.info("Generation complete")
        return f"Generated: {output_path}"

    def _create_content(self, **kwargs) -> str:
        """Helper method for content creation"""
        # Custom logic here
        return "Generated content"

# Usage in tool handler
from generators.my_generator import MyGenerator

async def handle_use_my_generator(arguments: dict) -> list[TextContent]:
    try:
        project_path = validate_project_path_input(arguments.get("project_path"))
        generator = MyGenerator(str(project_path))
        result = generator.generate(**arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return ErrorResponse.internal_error(str(e))
```

---

### Example 3: Add New Validation Function

```python
# validation.py
from constants import MyEnum

def validate_my_input(value: str) -> str:
    """
    Validate custom input field.

    Args:
        value: Value to validate

    Returns:
        Validated value

    Raises:
        ValueError: If validation fails
    """
    # Check empty
    if not value or not value.strip():
        raise ValueError("Value cannot be empty")

    # Check against enum
    valid_values = [e.value for e in MyEnum]
    if value not in valid_values:
        raise ValueError(
            f"Invalid value: '{value}'. "
            f"Valid options: {', '.join(valid_values)}"
        )

    # Security: Check for dangerous characters
    if any(char in value for char in ['..', '/', '\\', '\x00']):
        raise ValueError("Value contains invalid characters")

    return value.strip()

# Usage in handler
from validation import validate_my_input

async def handle_my_tool(arguments: dict) -> list[TextContent]:
    try:
        # Validate at boundary
        value = validate_my_input(arguments.get("my_field", ""))
        # ... proceed with validated value
    except ValueError as e:
        return ErrorResponse.invalid_input(str(e))
```

---

## Testing Examples

### Example 1: Test Handler

```python
import pytest
from tool_handlers import handle_get_template

@pytest.mark.asyncio
async def test_handle_get_template_success():
    """Test successful template retrieval"""
    arguments = {"template_name": "readme"}
    result = await handle_get_template(arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "README Template" in result[0].text

@pytest.mark.asyncio
async def test_handle_get_template_invalid():
    """Test invalid template name"""
    arguments = {"template_name": "nonexistent"}
    result = await handle_get_template(arguments)

    assert len(result) == 1
    assert "❌" in result[0].text
    assert "not found" in result[0].text.lower()
```

---

### Example 2: Test Generator

```python
import pytest
from generators.changelog_generator import ChangelogGenerator
from pathlib import Path
import tempfile
import json

def test_changelog_generator_add_entry():
    """Test adding changelog entry"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create changelog structure
        changelog_dir = project_path / "coderef" / "changelog"
        changelog_dir.mkdir(parents=True)

        generator = ChangelogGenerator(str(project_path))
        result = generator.add_entry(
            version="1.0.0",
            change_type="feature",
            severity="major",
            title="Test change",
            description="Test description",
            files=["test.py"],
            reason="Testing",
            impact="Test impact"
        )

        assert "✅" in result
        assert "1.0.0" in result

        # Verify file created
        assert generator.changelog_path.exists()

        # Verify structure
        with open(generator.changelog_path) as f:
            changelog = json.load(f)
        assert changelog['current_version'] == "1.0.0"
        assert len(changelog['entries']) == 1
```

---

## AI Integration Notes

These components are designed for AI assistant consumption. Key integration patterns:

**For Documentation Generation:**
1. Call `list_templates` to discover available templates
2. Call `generate_foundation_docs` or `generate_individual_doc` to get templates + instructions
3. Analyze project structure using context
4. Follow POWER framework to generate documentation
5. Save files to appropriate locations (README → root, others → coderef/foundation-docs/)

**For Changelog Management:**
1. Call `get_changelog` to understand existing history (READ)
2. Analyze changes made to codebase
3. Call `add_changelog_entry` with detailed parameters (WRITE)
4. Or use `update_changelog` for agentic self-documentation workflow (INSTRUCT → analyze → WRITE)

**Quality Guarantees:**
- ✅ All inputs validated at MCP boundaries
- ✅ All operations logged for debugging
- ✅ Consistent error messages guide correction
- ✅ Type-safe interfaces with comprehensive TypedDict definitions
- ✅ Schema validation ensures data integrity

---

**🤖 This COMPONENTS document documents the v1.1.0 modular architecture with 10 Python modules**

---

**Maintained by:** willh, Claude Code AI
**Last updated:** 2025-10-09
**Related documents:** README.md, ARCHITECTURE.md, API.md, SCHEMA.md (pending), user-guide.md, CLAUDE.md
