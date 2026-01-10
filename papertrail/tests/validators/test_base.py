"""
Unit tests for BaseUDSValidator

Tests:
- YAML frontmatter extraction
- JSON schema validation
- Base UDS field validation (agent, date, task)
- Score calculation
- Validation result structure
"""

import pytest
from pathlib import Path
from papertrail.validators.base import BaseUDSValidator
from papertrail.validator import ValidationResult, ValidationError, ValidationSeverity


class TestBaseUDSValidator:
    """Test suite for BaseUDSValidator"""

    def test_extract_frontmatter_valid(self):
        """Test extraction of valid YAML frontmatter"""
        content = """---
agent: Claude Sonnet 4.5
date: '2026-01-10'
task: CREATE
---

# Document Content
"""
        validator = BaseUDSValidator()
        frontmatter = validator._extract_frontmatter(content)

        assert frontmatter is not None
        assert frontmatter['agent'] == 'Claude Sonnet 4.5'
        assert frontmatter['date'] == '2026-01-10'
        assert frontmatter['task'] == 'CREATE'

    def test_extract_frontmatter_missing(self):
        """Test extraction when frontmatter is missing"""
        content = "# Document without frontmatter\n\nContent here."

        validator = BaseUDSValidator()
        frontmatter = validator._extract_frontmatter(content)

        assert frontmatter is None

    def test_extract_frontmatter_invalid_yaml(self):
        """Test extraction with invalid YAML syntax"""
        content = """---
agent: Claude Sonnet 4.5
date: '2026-01-10
task: CREATE
---

# Document Content
"""
        validator = BaseUDSValidator()
        frontmatter = validator._extract_frontmatter(content)

        assert frontmatter is None

    def test_validate_content_missing_frontmatter(self):
        """Test validation when frontmatter is missing"""
        content = "# Document without frontmatter"

        validator = BaseUDSValidator()
        result = validator.validate_content(content)

        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].severity == ValidationSeverity.CRITICAL
        assert "Missing or invalid YAML frontmatter" in result.errors[0].message
        assert result.score == 0

    def test_validate_content_valid_minimal(self):
        """Test validation with valid minimal Base UDS frontmatter"""
        content = """---
agent: Claude Sonnet 4.5
date: 2026-01-10
task: CREATE
---

# Document Content
"""
        validator = BaseUDSValidator()
        result = validator.validate_content(content)

        # Should have no schema errors (no schema loaded in base validator)
        # Should have no specific errors (validate_specific returns empty)
        assert result.valid is True
        assert len(result.errors) == 0
        assert result.score == 100

    def test_calculate_score_no_errors(self):
        """Test score calculation with no errors"""
        validator = BaseUDSValidator()
        score = validator._calculate_score([], [])

        assert score == 100

    def test_calculate_score_critical_error(self):
        """Test score calculation with CRITICAL error"""
        errors = [
            ValidationError(
                severity=ValidationSeverity.CRITICAL,
                message="Missing required field"
            )
        ]

        validator = BaseUDSValidator()
        score = validator._calculate_score(errors, [])

        assert score == 50  # 100 - 50 = 50

    def test_calculate_score_major_error(self):
        """Test score calculation with MAJOR error"""
        errors = [
            ValidationError(
                severity=ValidationSeverity.MAJOR,
                message="Invalid format"
            )
        ]

        validator = BaseUDSValidator()
        score = validator._calculate_score(errors, [])

        assert score == 80  # 100 - 20 = 80

    def test_calculate_score_minor_error(self):
        """Test score calculation with MINOR error"""
        errors = [
            ValidationError(
                severity=ValidationSeverity.MINOR,
                message="Typo detected"
            )
        ]

        validator = BaseUDSValidator()
        score = validator._calculate_score(errors, [])

        assert score == 90  # 100 - 10 = 90

    def test_calculate_score_warning_severity(self):
        """Test score calculation with WARNING severity"""
        errors = [
            ValidationError(
                severity=ValidationSeverity.WARNING,
                message="Deprecation warning"
            )
        ]

        validator = BaseUDSValidator()
        score = validator._calculate_score(errors, [])

        assert score == 95  # 100 - 5 = 95

    def test_calculate_score_warning_messages(self):
        """Test score calculation with warning messages"""
        warnings = ["Warning 1", "Warning 2", "Warning 3"]

        validator = BaseUDSValidator()
        score = validator._calculate_score([], warnings)

        assert score == 94  # 100 - (3 * 2) = 94

    def test_calculate_score_multiple_errors(self):
        """Test score calculation with multiple errors"""
        errors = [
            ValidationError(severity=ValidationSeverity.CRITICAL, message="Error 1"),
            ValidationError(severity=ValidationSeverity.MAJOR, message="Error 2"),
            ValidationError(severity=ValidationSeverity.MINOR, message="Error 3"),
        ]

        validator = BaseUDSValidator()
        score = validator._calculate_score(errors, [])

        assert score == 20  # 100 - 50 - 20 - 10 = 20

    def test_calculate_score_floor_at_zero(self):
        """Test that score floors at 0 (never negative)"""
        errors = [
            ValidationError(severity=ValidationSeverity.CRITICAL, message="Error 1"),
            ValidationError(severity=ValidationSeverity.CRITICAL, message="Error 2"),
            ValidationError(severity=ValidationSeverity.CRITICAL, message="Error 3"),
        ]

        validator = BaseUDSValidator()
        score = validator._calculate_score(errors, [])

        assert score == 0  # Would be -50, but floors at 0

    def test_validate_file_not_found(self):
        """Test validation when file doesn't exist"""
        validator = BaseUDSValidator()
        result = validator.validate_file("/nonexistent/file.md")

        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].severity == ValidationSeverity.CRITICAL
        assert "File not found" in result.errors[0].message
        assert result.score == 0

    def test_validate_specific_override(self):
        """Test that validate_specific can be overridden"""
        class CustomValidator(BaseUDSValidator):
            def validate_specific(self, frontmatter, content, file_path=None):
                errors = []
                warnings = []

                if 'custom_field' not in frontmatter:
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message="Missing custom_field"
                    ))

                return (errors, warnings)

        content = """---
agent: Claude Sonnet 4.5
date: 2026-01-10
task: CREATE
---

# Document
"""
        validator = CustomValidator()
        result = validator.validate_content(content)

        # Should have error from custom validation
        assert result.valid is True  # No CRITICAL errors
        assert len(result.errors) == 1
        assert result.errors[0].message == "Missing custom_field"
        assert result.score == 80  # 100 - 20 (MAJOR) = 80
