"""
Tests for ResourceSheetValidator

Validates RSMS v2.0 compliant resource sheets with frontmatter metadata.
"""

import pytest
from pathlib import Path
from papertrail.validators.resource_sheet import ResourceSheetValidator
from papertrail.validator import ValidationSeverity


class TestResourceSheetValidator:
    """Test suite for ResourceSheetValidator"""

    def test_valid_resource_sheet(self, tmp_path):
        """Test validation of a valid resource sheet"""
        content = """---
agent: coderef-assistant
date: "2026-01-10"
task: CONSOLIDATE
subject: AuthService
parent_project: backend-api
category: service
version: "1.0.0"
related_files:
  - src/auth/auth.service.ts
  - src/auth/token.service.ts
related_docs:
  - UserController-RESOURCE-SHEET.md
workorder: WO-AUTH-SYSTEM-001
status: APPROVED
---

# AuthService Resource Sheet

## Executive Summary
Authentication service handling JWT tokens.

## Audience & Intent
For backend developers working on authentication.

## Quick Reference
- **Purpose:** JWT authentication
- **Dependencies:** bcrypt, jsonwebtoken

## Architecture
Service follows hexagonal architecture.

## Dependencies
- bcrypt for password hashing
- jsonwebtoken for token generation

## Usage
```typescript
const authService = new AuthService();
```

## Testing
Unit tests cover 95% of code.
"""

        test_file = tmp_path / "AuthService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        assert result.valid, f"Expected valid, got errors: {result.errors}"
        assert result.score >= 90, f"Expected score >= 90, got {result.score}"
        assert len(result.errors) == 0

    def test_invalid_missing_required(self, tmp_path):
        """Test validation fails when required fields are missing"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
---

# Test Resource Sheet

Content here.
"""

        test_file = tmp_path / "Test-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        assert not result.valid
        assert result.score < 90
        # Should have errors for missing required fields: subject, parent_project, category
        assert any("subject" in str(error) or "required" in str(error).lower() for error in result.errors)

    def test_invalid_category_enum(self, tmp_path):
        """Test validation fails for invalid category"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: invalid-category
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        assert not result.valid
        # Should have error about invalid category
        assert any("category" in str(error).lower() and "invalid" in str(error).lower() for error in result.errors)

    def test_version_format_validation(self, tmp_path):
        """Test version format validation (semver)"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
version: 1.0
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have error about invalid version format
        assert any("version" in str(error).lower() and "semver" in str(error).lower() for error in result.errors)

    def test_related_files_validation(self, tmp_path):
        """Test related_files array validation"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
related_files:
  - src/test.service.ts
  - invalid_file_without_extension
  - "../../../etc/passwd"
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have errors about invalid file paths
        file_errors = [e for e in result.errors if "related_files" in str(e.field)]
        assert len(file_errors) >= 1  # At least one invalid file path

    def test_related_docs_validation(self, tmp_path):
        """Test related_docs array validation (must be .md files)"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
related_docs:
  - UserController-RESOURCE-SHEET.md
  - API-Guide.txt
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have error about .txt file (not .md)
        doc_errors = [e for e in result.errors if "related_docs" in str(e.field)]
        assert len(doc_errors) >= 1

    def test_workorder_format_validation(self, tmp_path):
        """Test workorder ID format validation"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
workorder: INVALID-FORMAT
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have error about invalid workorder format
        assert any("workorder" in str(error).lower() and "format" in str(error).lower() for error in result.errors)

    def test_legacy_component_field_warning(self, tmp_path):
        """Test warning for deprecated 'component' field"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
component: TestService
parent_project: test-project
category: service
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have warning about deprecated component field
        assert any("component" in warning.lower() and "deprecated" in warning.lower() for warning in result.warnings)

    def test_missing_recommended_sections(self, tmp_path):
        """Test warning for missing recommended sections"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
---

# TestService Resource Sheet

Some basic content without recommended sections.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have warning about missing sections
        assert any("missing recommended sections" in warning.lower() for warning in result.warnings)

    def test_filename_convention_warning(self, tmp_path):
        """Test warning when filename doesn't follow convention"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "wrong-filename.md"  # Not following {Subject}-RESOURCE-SHEET.md
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have warning about filename convention
        assert any("filename" in warning.lower() and "convention" in warning.lower() for warning in result.warnings)

    def test_draft_status_warning(self, tmp_path):
        """Test warning for DRAFT status"""
        content = """---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: service
status: DRAFT
---

# TestService Resource Sheet

Content here.
"""

        test_file = tmp_path / "TestService-RESOURCE-SHEET.md"
        test_file.write_text(content)

        validator = ResourceSheetValidator()
        result = validator.validate_file(test_file)

        # Should have warning about DRAFT status
        assert any("draft" in warning.lower() for warning in result.warnings)

    def test_all_valid_categories(self, tmp_path):
        """Test that all valid categories pass validation"""
        valid_categories = [
            "service", "controller", "model", "utility", "integration",
            "component", "middleware", "validator", "schema", "config", "other"
        ]

        for category in valid_categories:
            content = f"""---
agent: coderef-assistant
date: 2026-01-10
task: CONSOLIDATE
subject: TestService
parent_project: test-project
category: {category}
---

# TestService Resource Sheet

Content here.
"""

            test_file = tmp_path / f"Test-{category}-RESOURCE-SHEET.md"
            test_file.write_text(content)

            validator = ResourceSheetValidator()
            result = validator.validate_file(test_file)

            # Should not have category-related errors
            category_errors = [e for e in result.errors if "category" in str(e).lower()]
            assert len(category_errors) == 0, f"Category '{category}' should be valid"
