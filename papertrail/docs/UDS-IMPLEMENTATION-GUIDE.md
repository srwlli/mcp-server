---
agent: 'Lloyd (Planning Assistant)'
date: '2026-01-10'
task: CREATE
audience: Developers
doc_type: guide
difficulty: intermediate
title: 'UDS Implementation Guide'
---

# UDS Implementation Guide

**Audience:** Developers implementing new document types or validators
**Version:** 1.0.0
**Last Updated:** 2026-01-10

---

## Purpose

This guide shows developers how to extend the Universal Documentation Standards (UDS) system by creating new document types, schemas, and validators.

---

## When to Create a New Validator

Create a new validator when:

1. **New document category emerges** - You have a distinct document type with unique metadata requirements (e.g., API docs, testing docs, security docs)
2. **Category-specific validation needed** - The document type requires custom validation beyond base UDS fields (e.g., checking for required sections, format validation)
3. **Consistent document structure** - Multiple documents share the same structure and should be validated the same way

**Don't create a new validator if:**
- Document is one-off or unique → Use GeneralMarkdownValidator
- Validation needs are already covered by existing validator → Extend existing schema instead
- Only base UDS fields needed → Use GeneralMarkdownValidator

---

## Implementation Steps

### Step 1: Create JSON Schema

**Location:** `schemas/documentation/{category}-doc-frontmatter-schema.json`

**Template:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://papertrail/schemas/documentation/{category}-doc-frontmatter-schema.json",
  "title": "{Category} Document YAML Front Matter Schema",
  "version": "1.0.0",
  "allOf": [
    {
      "$ref": "./base-frontmatter-schema.json"
    },
    {
      "type": "object",
      "required": ["category_field_1", "category_field_2"],
      "properties": {
        "category_field_1": {
          "type": "string",
          "description": "Description of field 1",
          "minLength": 1,
          "maxLength": 100
        },
        "category_field_2": {
          "type": "string",
          "description": "Description of field 2",
          "enum": ["value1", "value2", "value3"]
        },
        "optional_field": {
          "type": "array",
          "description": "Optional field (not in required)",
          "items": {
            "type": "string"
          }
        }
      }
    }
  ]
}
```

**Key Points:**
- Always use `allOf` pattern with `$ref` to `base-frontmatter-schema.json`
- List category-specific required fields in `required` array
- Use JSON Schema Draft-07 syntax
- Add clear descriptions for each field
- Use appropriate types: `string`, `number`, `boolean`, `array`, `object`
- Use validation constraints: `minLength`, `maxLength`, `pattern`, `enum`, `minimum`, `maximum`

**Example (API Documentation):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://papertrail/schemas/documentation/api-doc-frontmatter-schema.json",
  "title": "API Document YAML Front Matter Schema",
  "version": "1.0.0",
  "allOf": [
    {
      "$ref": "./base-frontmatter-schema.json"
    },
    {
      "type": "object",
      "required": ["api_version", "endpoint_count", "authentication"],
      "properties": {
        "api_version": {
          "type": "string",
          "description": "API version (semver)",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "endpoint_count": {
          "type": "number",
          "description": "Number of documented endpoints",
          "minimum": 1
        },
        "authentication": {
          "type": "string",
          "description": "Authentication method",
          "enum": ["OAuth2", "JWT", "API Key", "None"]
        },
        "rate_limits": {
          "type": "object",
          "description": "Optional rate limit configuration",
          "properties": {
            "requests_per_minute": {
              "type": "number"
            },
            "requests_per_hour": {
              "type": "number"
            }
          }
        }
      }
    }
  ]
}
```

### Step 2: Create Validator Class

**Location:** `papertrail/validators/{category}.py`

**Template:**
```python
"""
{Category} Document Validator

Validates {category} documentation against UDS schema.
{Brief description of document type}.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class {Category}DocValidator(BaseUDSValidator):
    """
    Validator for {category} documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - {Category} fields (list required fields)
    - Recommended sections for {category} docs
    """

    schema_name = "{category}-doc-frontmatter-schema.json"
    doc_category = "{category}"

    # Recommended sections (optional)
    {CATEGORY}_SECTIONS = [
        "Section 1",
        "Section 2",
        "Section 3"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        {Category}-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Add your validation logic here
        # Example: Check for recommended sections
        missing_sections = self._check_{category}_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended {category} sections: {', '.join(missing_sections)}"
            )

        # Example: Validate enum field
        field_value = frontmatter.get('category_field_2')
        if field_value and field_value not in ['value1', 'value2', 'value3']:
            errors.append(
                ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"Invalid field value '{field_value}'. Must be one of: value1, value2, value3",
                    field='category_field_2'
                )
            )

        return (errors, warnings)

    def _check_{category}_sections(self, content: str) -> list[str]:
        """Check for recommended {category} documentation sections."""
        missing = []
        for section in self.{CATEGORY}_SECTIONS:
            if f"# {section}" not in content and f"## {section}" not in content:
                missing.append(section)
        return missing
```

**Example (API Documentation):**
```python
"""
API Document Validator

Validates API documentation against UDS schema.
API docs describe endpoints, authentication, and usage.
"""

from pathlib import Path
from typing import Optional
import re

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class ApiDocValidator(BaseUDSValidator):
    """
    Validator for API documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - API fields (api_version, endpoint_count, authentication)
    - Recommended sections for API docs
    """

    schema_name = "api-doc-frontmatter-schema.json"
    doc_category = "api"

    API_SECTIONS = [
        "Authentication",
        "Endpoints",
        "Rate Limits",
        "Error Handling",
        "Examples"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        API-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check for recommended API sections
        missing_sections = self._check_api_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended API sections: {', '.join(missing_sections)}"
            )

        # Validate endpoint_count matches actual documented endpoints
        endpoint_count = frontmatter.get('endpoint_count', 0)
        actual_count = self._count_endpoints(content)
        if actual_count > 0 and endpoint_count != actual_count:
            warnings.append(
                f"endpoint_count ({endpoint_count}) doesn't match documented endpoints ({actual_count})"
            )

        # Check authentication is specified for non-public APIs
        authentication = frontmatter.get('authentication')
        if authentication == 'None':
            warnings.append(
                "API uses no authentication - consider if this is intended for public access"
            )

        return (errors, warnings)

    def _check_api_sections(self, content: str) -> list[str]:
        """Check for recommended API documentation sections."""
        missing = []
        for section in self.API_SECTIONS:
            if f"# {section}" not in content and f"## {section}" not in content:
                missing.append(section)
        return missing

    def _count_endpoints(self, content: str) -> int:
        """Count documented API endpoints (lines starting with method verbs)."""
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        count = 0
        for line in content.split('\n'):
            line = line.strip()
            if any(line.startswith(method) for method in methods):
                count += 1
        return count
```

### Step 3: Add to ValidatorFactory

**Location:** `papertrail/validators/factory.py`

**Add import:**
```python
from .{category} import {Category}DocValidator
```

**Add path patterns to `get_validator()` method:**
```python
# {Category} docs
if file_name.endswith('-api.md') or file_name == 'API.md':
    return ApiDocValidator()
```

**Add frontmatter-based detection (if applicable):**
```python
# Check frontmatter for category-specific fields
frontmatter = BaseUDSValidator._extract_frontmatter_static(content)
if frontmatter:
    if 'api_version' in frontmatter:
        return ApiDocValidator()
```

**Example (API Documentation):**
```python
class ValidatorFactory:
    """Factory for creating appropriate validator based on file type."""

    @staticmethod
    def get_validator(file_path: Path) -> BaseUDSValidator:
        """
        Auto-detect document type and return appropriate validator.
        """
        file_name = file_path.name.lower()

        # ... existing patterns ...

        # API docs
        if file_name.endswith('-api.md') or file_name == 'API.md':
            return ApiDocValidator()

        # ... rest of patterns ...

        # Frontmatter-based detection
        if file_path.suffix in ['.md', '.markdown']:
            try:
                content = file_path.read_text(encoding='utf-8')
                frontmatter = BaseUDSValidator._extract_frontmatter_static(content)
                if frontmatter:
                    # API docs
                    if 'api_version' in frontmatter:
                        return ApiDocValidator()

                    # ... other frontmatter checks ...

            except Exception:
                pass

        # Default fallback
        return GeneralMarkdownValidator()
```

### Step 4: Write Tests

**Location:** `papertrail/tests/test_{category}_validator.py`

**Template:**
```python
"""
Tests for {Category} Document Validator
"""

import pytest
from pathlib import Path
from papertrail.validators.{category} import {Category}DocValidator


VALID_{CATEGORY}_DOC = """---
agent: 'Test Agent'
date: '2026-01-10'
task: CREATE
category_field_1: 'value'
category_field_2: 'value1'
---

# Test {Category} Document

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""

INVALID_{CATEGORY}_DOC = """---
agent: 'Test Agent'
date: '2026-01-10'
task: CREATE
category_field_2: 'invalid_value'
---

# Invalid Document

Missing required field and has invalid enum value.
"""


def test_valid_{category}_document(tmp_path):
    """Test validator with valid {category} document."""
    test_file = tmp_path / "test-{category}.md"
    test_file.write_text(VALID_{CATEGORY}_DOC, encoding='utf-8')

    validator = {Category}DocValidator()
    result = validator.validate_file(test_file)

    assert result.valid is True
    assert result.score >= 90
    assert len(result.errors) == 0


def test_invalid_{category}_document(tmp_path):
    """Test validator with invalid {category} document."""
    test_file = tmp_path / "invalid-{category}.md"
    test_file.write_text(INVALID_{CATEGORY}_DOC, encoding='utf-8')

    validator = {Category}DocValidator()
    result = validator.validate_file(test_file)

    assert result.valid is False
    assert result.score < 90
    assert len(result.errors) > 0


def test_missing_sections(tmp_path):
    """Test that missing recommended sections generate warnings."""
    doc = """---
agent: 'Test Agent'
date: '2026-01-10'
task: CREATE
category_field_1: 'value'
category_field_2: 'value1'
---

# Test Document

Only has title, missing all recommended sections.
"""

    test_file = tmp_path / "test.md"
    test_file.write_text(doc, encoding='utf-8')

    validator = {Category}DocValidator()
    result = validator.validate_file(test_file)

    # Should still be valid but have warnings
    assert result.valid is True
    assert len(result.warnings) > 0
    assert any('Missing recommended' in w for w in result.warnings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run tests:**
```bash
pytest papertrail/tests/test_{category}_validator.py -v
```

### Step 5: Update Documentation

**Add to CLAUDE.md:**

1. Update "Validator Hierarchy" section with new validator
2. Update "ValidatorFactory" section with new path patterns
3. Update "Metadata Standards Comparison" table if needed

**Add to README.md:**

1. Add new document category to list of supported types
2. Add example frontmatter for new category

---

## Validation Best Practices

### 1. Use Appropriate Severity Levels

```python
# CRITICAL - Missing required field, invalid schema
errors.append(
    ValidationError(
        severity=ValidationSeverity.CRITICAL,
        message="Required field 'workorder_id' is missing",
        field='workorder_id'
    )
)

# MAJOR - Invalid enum value, format violation
errors.append(
    ValidationError(
        severity=ValidationSeverity.MAJOR,
        message=f"Invalid status '{status}'. Must be one of: ...",
        field='status'
    )
)

# MINOR - Recommended field missing
errors.append(
    ValidationError(
        severity=ValidationSeverity.MINOR,
        message="Recommended field 'description' is missing",
        field='description'
    )
)

# WARNING - Style issue, optional section missing
warnings.append(
    "Consider adding 'Prerequisites' section for infrastructure docs"
)
```

### 2. Check Content Structure

```python
def _check_required_sections(self, content: str, sections: list[str]) -> list[str]:
    """Check for required sections (returns missing sections)."""
    missing = []
    for section in sections:
        # Check both H1 and H2 variants
        if f"# {section}" not in content and f"## {section}" not in content:
            missing.append(section)
    return missing
```

### 3. Validate Format Patterns

```python
import re

# Validate semver
def _is_valid_semver(version: str) -> bool:
    """Check if version string matches semver format."""
    return bool(re.match(r'^\d+\.\d+\.\d+$', version))

# Validate kebab-case
def _is_kebab_case(text: str) -> bool:
    """Check if text is kebab-case."""
    return bool(re.match(r'^[a-z0-9-]+$', text))

# Validate date format
def _is_valid_date(date_str: str) -> bool:
    """Check if date string matches YYYY-MM-DD format."""
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_str))
```

### 4. Provide Context in Error Messages

```python
# BAD - Vague error
errors.append(
    ValidationError(
        severity=ValidationSeverity.MAJOR,
        message="Invalid value",
        field='status'
    )
)

# GOOD - Specific with context
errors.append(
    ValidationError(
        severity=ValidationSeverity.MAJOR,
        message=f"Invalid status '{status}'. Must be one of: Production, Development, Deprecated, Archived",
        field='status'
    )
)
```

### 5. Use Warnings for Recommendations

```python
# Use warnings for:
# - Missing optional sections
# - Style recommendations
# - Potential improvements
# - Non-blocking issues

warnings.append(
    "Consider adding 'Examples' section to improve documentation clarity"
)

warnings.append(
    f"endpoint_count ({endpoint_count}) doesn't match documented endpoints ({actual_count})"
)
```

---

## Common Patterns

### Pattern 1: Enum Validation

```python
def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
    errors = []
    warnings = []

    VALID_VALUES = ['value1', 'value2', 'value3']
    field_value = frontmatter.get('my_field')

    if field_value and field_value not in VALID_VALUES:
        errors.append(
            ValidationError(
                severity=ValidationSeverity.MAJOR,
                message=f"Invalid my_field '{field_value}'. Must be one of: {', '.join(VALID_VALUES)}",
                field='my_field'
            )
        )

    return (errors, warnings)
```

### Pattern 2: Format Validation

```python
import re

def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
    errors = []
    warnings = []

    version = frontmatter.get('version')
    if version and not re.match(r'^\d+\.\d+\.\d+$', version):
        errors.append(
            ValidationError(
                severity=ValidationSeverity.MAJOR,
                message=f"version '{version}' must be semver format (e.g., 1.0.0)",
                field='version'
            )
        )

    return (errors, warnings)
```

### Pattern 3: Conditional Requirements

```python
def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
    errors = []
    warnings = []

    doc_type = frontmatter.get('doc_type')
    prerequisites = frontmatter.get('prerequisites')

    # If doc_type is 'deployment', prerequisites should be specified
    if doc_type == 'deployment' and not prerequisites:
        warnings.append(
            "Deployment docs should specify 'prerequisites' field"
        )

    return (errors, warnings)
```

### Pattern 4: Cross-Field Validation

```python
def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
    errors = []
    warnings = []

    from_version = frontmatter.get('from_version')
    to_version = frontmatter.get('to_version')

    if from_version and to_version:
        if from_version == to_version:
            errors.append(
                ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message="from_version and to_version cannot be the same",
                    field='to_version'
                )
            )

    return (errors, warnings)
```

### Pattern 5: Content Analysis

```python
def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
    errors = []
    warnings = []

    # Count code blocks
    code_block_count = content.count('```')

    # Warn if no code examples in tutorial
    if frontmatter.get('doc_type') == 'tutorial' and code_block_count == 0:
        warnings.append(
            "Tutorial docs should include code examples (use ``` code blocks)"
        )

    return (errors, warnings)
```

---

## Testing Checklist

Before submitting your validator:

- [ ] Schema file created in `schemas/documentation/`
- [ ] Schema extends `base-frontmatter-schema.json` via allOf
- [ ] Validator class created in `papertrail/validators/`
- [ ] Validator extends BaseUDSValidator
- [ ] `validate_specific()` method implemented
- [ ] Added to ValidatorFactory path patterns
- [ ] Added to ValidatorFactory frontmatter detection (if applicable)
- [ ] Test file created with valid/invalid test cases
- [ ] All tests passing (pytest)
- [ ] CLAUDE.md updated with new validator
- [ ] README.md updated with new category

---

## Example: Complete Implementation

See `papertrail/validators/infrastructure.py` for a complete example implementation including:

- Schema definition with required and optional fields
- Validator class with section checking
- Conditional validation (platform for deployment docs)
- Comprehensive error messages
- Warning generation for recommendations

---

## Resources

- **Base Validator**: `papertrail/validators/base.py`
- **Base Schema**: `schemas/documentation/base-frontmatter-schema.json`
- **Factory**: `papertrail/validators/factory.py`
- **JSON Schema Docs**: https://json-schema.org/draft-07/json-schema-release-notes.html
- **UDS Architecture**: See CLAUDE.md "UDS System Architecture" section

---

**Maintained by:** CodeRef Ecosystem
**Version:** 1.0.0
**Last Updated:** 2026-01-10
