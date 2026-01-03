# error_responses.py - Resource Sheet

**Module:** `error_responses.py`
**Category:** Error Handling / User Feedback
**Lines:** 158
**Version:** 1.3.0
**Status:** ✅ Production

---

## Purpose & Scope

Centralized error response factory (ARCH-001) that provides **consistent, user-friendly error formatting** across all 40+ MCP tools. Converts Python exceptions into formatted TextContent responses with optional hints for fixing issues.

**Key Responsibilities:**
- **Standardized Error Format** - All errors use ❌ prefix + optional 💡 hints
- **Exception → TextContent Mapping** - Converts Python exceptions to MCP responses
- **User-Friendly Messages** - Clear error descriptions with actionable hints
- **Consistent UX** - Same error format across all 40+ tools

**Design Philosophy:** Single source of truth for error formatting. All tool handlers use ErrorResponse.* methods instead of creating their own error messages.

---

## State Ownership

**100% Stateless** - Pure static methods, no class state, no instance variables.

| State Type | Ownership | Persistence |
|------------|-----------|-------------|
| Error messages | Factory methods | Request-scoped (returned immediately) |
| Hints | Optional parameter | Request-scoped |
| Exception objects | Caller-provided | Request-scoped |

**Design Pattern:** Factory pattern with static methods. No instantiation required.

---

## Architecture & Data Flow

```
Python Exception (ValueError, FileNotFoundError, etc.)
    ↓
tool_handler try/except block
    ↓
ErrorResponse.{error_type}(detail, hint)
    ↓
Format message with ❌ prefix + optional 💡 hint
    ↓
Return [TextContent(type="text", text=formatted)]
    ↓
MCP Protocol → Claude Code UI
```

### Error Flow Example

```python
# Step 1: Exception occurs in validation layer
try:
    validate_feature_name_input(feature_name)
except ValueError as e:
    # Step 2: Tool handler catches exception
    # Step 3: Call appropriate ErrorResponse method
    return ErrorResponse.invalid_input(
        str(e),
        hint="Use only alphanumeric characters, hyphens, and underscores"
    )
    # Step 4: Returns formatted TextContent
    # → "❌ Invalid input: Feature name contains invalid characters\n\n💡 Use only alphanumeric..."
```

---

## Error Response Catalog

### 1. invalid_input (ValueError)

**Purpose:** Handle validation failures from validation.py functions

**Usage:**
```python
def my_tool_handler(feature_name: str) -> list[TextContent]:
    try:
        validated = validate_feature_name_input(feature_name)
    except ValueError as e:
        return ErrorResponse.invalid_input(
            str(e),
            hint="Use only alphanumeric characters, hyphens, and underscores"
        )
```

**Output Format:**
```
❌ Invalid input: {detail}

💡 {hint}
```

**Common Use Cases:**
- Validation failures (feature_name, workorder_id, version)
- Enum validation errors (change_type, severity)
- Format validation errors (regex mismatch)

---

### 2. not_found (FileNotFoundError)

**Purpose:** Handle missing files, directories, or features

**Usage:**
```python
def get_plan(feature_name: str) -> list[TextContent]:
    plan_path = Path(f"coderef/workorder/{feature_name}/plan.json")
    if not plan_path.exists():
        return ErrorResponse.not_found(
            f"Plan for feature '{feature_name}'",
            hint="Run /create-plan first to generate implementation plan"
        )
```

**Output Format:**
```
❌ {resource} not found

💡 {hint}
```

**Common Use Cases:**
- Missing plan.json files
- Missing project directories
- Missing template files
- Missing archived features

---

### 3. permission_denied (PermissionError)

**Purpose:** Handle file system permission errors

**Usage:**
```python
def write_deliverables(path: Path) -> list[TextContent]:
    try:
        path.write_text(content)
    except PermissionError as e:
        return ErrorResponse.permission_denied(
            f"Cannot write to {path}",
            hint="Check file permissions or run as administrator"
        )
```

**Output Format:**
```
❌ Permission denied: {detail}

💡 {hint}
```

**Common Use Cases:**
- Write permission failures
- Directory creation failures
- Archive operation failures

---

### 4. validation_failed (jsonschema.ValidationError)

**Purpose:** Handle JSON schema validation failures for CHANGELOG.json

**Usage:**
```python
import jsonschema

def validate_changelog(data: dict) -> list[TextContent]:
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        return ErrorResponse.validation_failed(e)
```

**Output Format:**
```
❌ Changelog validation failed

Error: {error.message}
Path: {path} → {to} → {field}

💡 Check CHANGELOG.json against schema at coderef/changelog/schema.json
```

**Special Features:**
- Automatically extracts error path from jsonschema.ValidationError
- Formats path as breadcrumb: "0 → changes → 0 → type"
- Always includes schema location hint

---

### 5. malformed_json (json.JSONDecodeError)

**Purpose:** Handle JSON syntax errors when parsing files

**Usage:**
```python
import json

def read_plan(path: Path) -> list[TextContent]:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return ErrorResponse.malformed_json(
            f"{path.name}: {str(e)}",
            hint="Check for missing commas, quotes, or brackets"
        )
```

**Output Format:**
```
❌ Malformed JSON: {detail}

💡 {hint or "Validate JSON syntax"}
```

**Common Use Cases:**
- plan.json syntax errors
- context.json syntax errors
- CHANGELOG.json syntax errors
- analysis.json syntax errors

**Default Hint:** "Validate JSON syntax" (if no custom hint provided)

---

### 6. encoding_error (UnicodeDecodeError)

**Purpose:** Handle file encoding issues

**Usage:**
```python
def read_file(path: Path) -> list[TextContent]:
    try:
        content = path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        return ErrorResponse.encoding_error(
            f"{path.name} contains invalid UTF-8 characters",
            hint="Try opening with different encoding or check for binary data"
        )
```

**Output Format:**
```
❌ Encoding error: {detail}

💡 {hint or "File may be corrupted or not UTF-8 encoded"}
```

**Common Use Cases:**
- Non-UTF-8 files
- Corrupted files
- Binary files mistaken for text

**Default Hint:** "File may be corrupted or not UTF-8 encoded"

---

### 7. io_error (IOError)

**Purpose:** Handle generic file I/O errors

**Usage:**
```python
def copy_file(src: Path, dst: Path) -> list[TextContent]:
    try:
        dst.write_bytes(src.read_bytes())
    except IOError as e:
        return ErrorResponse.io_error(
            f"Failed to copy {src.name} to {dst}",
            hint="Check disk space and file permissions"
        )
```

**Output Format:**
```
❌ File operation failed: {detail}

💡 {hint}
```

**Common Use Cases:**
- Disk full errors
- Network drive disconnections
- File lock conflicts

---

### 8. generic_error (Exception)

**Purpose:** Catch-all for unexpected errors

**Usage:**
```python
def my_tool_handler() -> list[TextContent]:
    try:
        # Complex operation
        pass
    except ValueError as e:
        return ErrorResponse.invalid_input(str(e))  # Specific error
    except FileNotFoundError as e:
        return ErrorResponse.not_found(str(e))      # Specific error
    except Exception as e:
        return ErrorResponse.generic_error(
            str(e),
            hint="Please report this issue if it persists"
        )  # Catch-all
```

**Output Format:**
```
❌ Error: {detail}

💡 {hint}
```

**Best Practice:** Use specific error methods first, generic_error as final fallback.

---

## Integration Points

### With MCP Protocol

```python
from mcp.types import TextContent

# ErrorResponse methods return list[TextContent]
# Compatible with MCP tool return type
@server.call_tool()
async def handle_tool(name: str, args: dict) -> list[TextContent]:
    try:
        result = execute_tool(name, args)
        return [TextContent(type="text", text=result)]
    except ValueError as e:
        return ErrorResponse.invalid_input(str(e))  # Returns list[TextContent]
```

### With Validation Layer (validation.py)

```python
from validation import validate_feature_name_input

def create_feature(feature_name: str) -> list[TextContent]:
    try:
        validated = validate_feature_name_input(feature_name)
    except ValueError as e:
        # validation.py raises ValueError
        # ErrorResponse formats it for UI
        return ErrorResponse.invalid_input(
            str(e),
            hint="Use only alphanumeric characters, hyphens, and underscores"
        )
```

### With Tool Handlers (tool_handlers.py)

All 40+ tool handlers in tool_handlers.py follow this pattern:

```python
async def gather_context_handler(args: dict) -> list[TextContent]:
    try:
        # Validate inputs
        project_path = validate_project_path_input(args["project_path"])
        # Execute business logic
        result = gather_context(project_path, ...)
        return [TextContent(type="text", text=result)]
    except ValueError as e:
        return ErrorResponse.invalid_input(str(e))
    except FileNotFoundError as e:
        return ErrorResponse.not_found(str(e))
    except PermissionError as e:
        return ErrorResponse.permission_denied(str(e))
    except Exception as e:
        return ErrorResponse.generic_error(str(e))
```

---

## Best Practices

### 1. Always Include Hints for Common Errors

```python
# ✅ GOOD: Include actionable hint
return ErrorResponse.not_found(
    f"Plan for feature '{feature_name}'",
    hint="Run /create-plan first to generate implementation plan"
)

# ❌ BAD: No hint for user
return ErrorResponse.not_found(f"Plan for feature '{feature_name}'")
```

### 2. Use Specific Error Methods Over Generic

```python
# ✅ GOOD: Use specific method
except FileNotFoundError as e:
    return ErrorResponse.not_found(str(e), hint="...")

# ❌ BAD: Use generic for specific error
except FileNotFoundError as e:
    return ErrorResponse.generic_error(str(e))  # Less specific
```

### 3. Catch Exceptions in Order (Specific → General)

```python
try:
    # Business logic
    pass
except ValueError as e:           # Most specific
    return ErrorResponse.invalid_input(str(e))
except FileNotFoundError as e:    # Specific
    return ErrorResponse.not_found(str(e))
except IOError as e:              # Broader
    return ErrorResponse.io_error(str(e))
except Exception as e:            # Catch-all (last resort)
    return ErrorResponse.generic_error(str(e))
```

### 4. Format Resource Names Clearly

```python
# ✅ GOOD: Clear resource description
return ErrorResponse.not_found(
    f"Plan for feature '{feature_name}'",  # Clear what's missing
    hint="Run /create-plan first"
)

# ❌ BAD: Vague resource description
return ErrorResponse.not_found(f"{feature_name}")  # Unclear
```

### 5. Provide Contextual Hints

```python
# ✅ GOOD: Hint specific to operation
return ErrorResponse.permission_denied(
    f"Cannot write to {path}",
    hint="Check file permissions or close other programs using this file"
)

# ❌ BAD: Generic unhelpful hint
return ErrorResponse.permission_denied(
    f"Cannot write to {path}",
    hint="Fix permissions"  # Too vague
)
```

---

## Design Decisions

### Why Static Methods?

**Chosen:** Static factory methods (no instance required)
**Rejected:** Instance methods with state

**Rationale:**
- No state needed (errors are request-scoped)
- Simpler API (`ErrorResponse.invalid_input()` vs `error_factory.invalid_input()`)
- Prevents accidental state pollution
- Easier to test (no setup/teardown)

### Why list[TextContent] Return Type?

**Chosen:** Return `list[TextContent]` directly
**Rejected:** Return `TextContent` or `str`

**Rationale:**
- Compatible with MCP tool return type signature
- No unwrapping needed in tool handlers
- Consistent with success responses
- Future-proof for multi-part responses

### Why Optional Hints?

**Chosen:** `hint: str = None` (optional parameter)
**Rejected:** Always require hints

**Rationale:**
- Some errors are self-explanatory ("File not found")
- Allows default hints (malformed_json, encoding_error)
- Flexibility for different contexts
- Encourages hints but doesn't force them

### Why Emoji Prefixes?

**Chosen:** ❌ for errors, 💡 for hints
**Rejected:** Plain text or ANSI colors

**Rationale:**
- Cross-platform (works in all terminals)
- Visually distinct (errors stand out)
- Unicode-safe (UTF-8 everywhere)
- Friendly UX (less intimidating than "ERROR:")

---

## Testing Strategy

### Unit Tests

```python
import pytest
from error_responses import ErrorResponse
from mcp.types import TextContent

def test_invalid_input_with_hint():
    """Test invalid_input formats message correctly with hint."""
    result = ErrorResponse.invalid_input(
        "Feature name contains spaces",
        hint="Use hyphens instead of spaces"
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "❌ Invalid input: Feature name contains spaces" in result[0].text
    assert "💡 Use hyphens instead of spaces" in result[0].text

def test_invalid_input_without_hint():
    """Test invalid_input formats message correctly without hint."""
    result = ErrorResponse.invalid_input("Feature name too long")

    assert "❌ Invalid input: Feature name too long" in result[0].text
    assert "💡" not in result[0].text  # No hint section

def test_validation_failed_with_path():
    """Test validation_failed formats path correctly."""
    import jsonschema

    # Create mock validation error
    schema = {"type": "object", "properties": {"type": {"enum": ["feature"]}}}
    data = {"type": "bugfix"}  # Invalid

    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        result = ErrorResponse.validation_failed(e)

        assert "❌ Changelog validation failed" in result[0].text
        assert "Path:" in result[0].text
        assert "💡 Check CHANGELOG.json" in result[0].text
```

### Integration Tests

```python
from validation import validate_feature_name_input

def test_validation_error_flow():
    """Test full validation → error response flow."""
    feature_name = "../../../etc/passwd"  # Invalid

    try:
        validate_feature_name_input(feature_name)
    except ValueError as e:
        result = ErrorResponse.invalid_input(
            str(e),
            hint="Use only alphanumeric characters"
        )

        assert "❌ Invalid input" in result[0].text
        assert "💡 Use only alphanumeric" in result[0].text
```

---

## Performance Characteristics

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Format error message | O(1) | String concatenation |
| Format path (validation_failed) | O(n) | n = path depth (~2-5 typically) |
| Return TextContent | O(1) | Object construction |

**Bottlenecks:** None (formatting is negligible overhead)

**Optimization Opportunities:** None needed (already optimal)

---

## Error Method Selection Guide

**Need to handle validation errors?**
→ `ErrorResponse.invalid_input(str(e), hint="...")`

**Need to handle missing files/features?**
→ `ErrorResponse.not_found(resource, hint="...")`

**Need to handle permission errors?**
→ `ErrorResponse.permission_denied(detail, hint="...")`

**Need to handle JSON schema validation?**
→ `ErrorResponse.validation_failed(validation_error)`

**Need to handle JSON syntax errors?**
→ `ErrorResponse.malformed_json(detail, hint="...")`

**Need to handle encoding errors?**
→ `ErrorResponse.encoding_error(detail, hint="...")`

**Need to handle file I/O errors?**
→ `ErrorResponse.io_error(detail, hint="...")`

**Need to handle unexpected errors?**
→ `ErrorResponse.generic_error(detail, hint="...")`

---

## Related Resources

### Internal Dependencies
- **validation.py** - Raises ValueError exceptions that ErrorResponse.invalid_input handles
- **tool_handlers.py** - All 40+ tools use ErrorResponse methods
- **mcp.types** - TextContent type for MCP protocol

### External Documentation
- **MCP Protocol Spec** - TextContent format requirements
- **jsonschema** - ValidationError object structure

### Code References
- **ARCH-001** - Architecture decision for centralized error factory
- **tool_handlers.py:L50-L2500** - All tool handlers use ErrorResponse

---

## Version History

### v1.3.0 (Current)
- ✅ 8 error response methods covering all exception types
- ✅ Consistent ❌ + 💡 format across all tools
- ✅ Optional hints with sensible defaults
- ✅ jsonschema.ValidationError path formatting

### v1.0.0 (Initial)
- Basic error response factory with 4 methods

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P1-001
**Task:** SHEET-010
**Timestamp:** 2026-01-02
