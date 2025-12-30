"""
Unit tests for UDS validation
"""

import pytest
from papertrail.validator import (
    validate_uds,
    validate_workorder_id,
    validate_feature_id,
    ValidationSeverity,
    UDSValidator
)


class TestWorkorderIDValidation:
    """Test workorder ID format validation"""

    def test_valid_workorder_ids(self):
        """Test valid workorder ID formats"""
        valid_ids = [
            "WO-AUTH-SYSTEM-001",
            "WO-TEST-FEATURE-999",
            "WO-A-B-000",
            "WO-MULTI-WORD-FEATURE-123"
        ]

        for wid in valid_ids:
            assert validate_workorder_id(wid), f"Should accept {wid}"

    def test_invalid_workorder_ids(self):
        """Test invalid workorder ID formats"""
        invalid_ids = [
            "invalid-format",
            "WO-AUTH-001",  # Missing category
            "wo-auth-system-001",  # Lowercase
            "WO-AUTH-SYSTEM-01",  # Only 2 digits
            "WO-AUTH-SYSTEM-1000",  # 4 digits
            ""
        ]

        for wid in invalid_ids:
            assert not validate_workorder_id(wid), f"Should reject {wid}"


class TestFeatureIDValidation:
    """Test feature ID format validation"""

    def test_valid_feature_ids(self):
        """Test valid feature ID formats"""
        valid_ids = [
            "auth-system",
            "test_feature",
            "feature123",
            "a",
            "multi-word-feature"
        ]

        for fid in valid_ids:
            assert validate_feature_id(fid), f"Should accept {fid}"

    def test_invalid_feature_ids(self):
        """Test invalid feature ID formats"""
        invalid_ids = [
            "Auth-System",  # Uppercase
            "feature name",  # Space
            "feature!",  # Special char
            ""
        ]

        for fid in invalid_ids:
            assert not validate_feature_id(fid), f"Should reject {fid}"


class TestUDSValidation:
    """Test UDS document validation"""

    def test_valid_document_with_all_sections(self):
        """Test validation of complete, valid document"""
        document = """---
workorder_id: WO-TEST-DOCS-001
generated_by: coderef-docs v1.0.0
feature_id: test-feature
timestamp: '2025-12-29T10:00:00Z'
version: 1.0.0
---

# Purpose

This is the purpose section.

# Overview

This is the overview section.

# What/Why/When

Details about what, why, and when.

# Examples

```python
example_code()
```

# References

- Link 1
- Link 2
"""

        result = validate_uds(document, "architecture")

        assert result.valid, "Document should be valid"
        assert result.score > 80, "Score should be high for valid document"

    def test_missing_header(self):
        """Test validation with missing UDS header"""
        document = """# Architecture

No header here!
"""

        result = validate_uds(document, "architecture")

        assert not result.valid, "Should be invalid without header"
        assert any(e.severity == ValidationSeverity.CRITICAL for e in result.errors)

    def test_missing_required_metadata(self):
        """Test validation with missing required metadata"""
        document = """---
feature_id: test
---

# Purpose
...
"""

        result = validate_uds(document, "architecture")

        assert not result.valid, "Should be invalid without required metadata"
        # Should have errors for missing workorder_id, generated_by
        error_messages = [e.message for e in result.errors]
        assert any("workorder_id" in msg for msg in error_messages)

    def test_invalid_workorder_id_format(self):
        """Test validation with invalid workorder ID format"""
        document = """---
workorder_id: invalid-format
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '2025-12-29T10:00:00Z'
---

# Purpose
...
"""

        result = validate_uds(document, "architecture")

        # Should have error about invalid workorder_id format
        error_messages = [e.message for e in result.errors]
        assert any("workorder_id" in msg and "pattern" in msg for msg in error_messages)

    def test_workorder_id_missing_category(self):
        """Test that WO-AUTH-001 (missing category) is rejected"""
        document = """---
workorder_id: WO-AUTH-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '2025-12-29T10:00:00Z'
---

# Purpose
...
"""

        result = validate_uds(document, "architecture")

        # Should have error about invalid workorder_id format (missing category)
        error_messages = [e.message for e in result.errors]
        assert any("workorder_id" in msg and "pattern" in msg for msg in error_messages)

    def test_missing_required_sections(self):
        """Test validation with missing required sections"""
        document = """---
workorder_id: WO-TEST-DOCS-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '2025-12-29T10:00:00Z'
---

# Purpose

Only purpose section, missing others.
"""

        result = validate_uds(document, "architecture")

        # Should have errors for missing sections
        section_errors = [e for e in result.errors if e.section is not None]
        assert len(section_errors) > 0, "Should have missing section errors"

    def test_unknown_document_type(self):
        """Test validation with unknown document type"""
        document = """---
workorder_id: WO-TEST-DOCS-001
---
"""

        result = validate_uds(document, "unknown_type")

        assert not result.valid
        assert result.score == 0


class TestValidationScoring:
    """Test validation score calculation"""

    def test_perfect_document_score(self):
        """Test that perfect document gets score of 100"""
        document = """---
workorder_id: WO-TEST-DOCS-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '2025-12-29T10:00:00Z'
version: 1.0.0
---

# Purpose
Purpose section

# Overview
Overview section

# What/Why/When
Details

# Examples
Examples

# References
References
"""

        result = validate_uds(document, "architecture")
        assert result.score == 100

    def test_critical_error_reduces_score(self):
        """Test that CRITICAL errors significantly reduce score"""
        document = """No header at all!"""

        result = validate_uds(document, "architecture")
        assert result.score <= 50  # CRITICAL error = -50 points
