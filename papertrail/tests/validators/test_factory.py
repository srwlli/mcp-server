"""
Unit tests for ValidatorFactory

Tests:
- Path pattern detection for all document types
- Frontmatter inspection detection
- Validator type detection
- Validator instance creation
- Edge cases and error handling
"""

import pytest
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory


class TestValidatorFactory:
    """Test suite for ValidatorFactory"""

    def test_detect_resource_sheet_from_path(self):
        """Test detection of resource sheet from filename pattern"""
        paths = [
            "docs/AUTH-SERVICE-RESOURCE-SHEET.md",
            "/path/to/USER-CONTROLLER-RESOURCE-SHEET.md",
            "C:/Users/test/PAPERTRAIL-RESOURCE-SHEET.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "resource_sheet", f"Failed for {path}"

    def test_detect_foundation_from_path(self):
        """Test detection of foundation docs from path pattern"""
        paths = [
            "coderef/foundation-docs/README.md",
            "coderef/foundation-docs/ARCHITECTURE.md",
            "coderef/foundation-docs/API.md",
            "coderef/foundation-docs/SCHEMA.md",
            "coderef/foundation-docs/COMPONENTS.md",
            "README.md",  # Root README
            "/project/README.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "foundation", f"Failed for {path}"

    def test_detect_workorder_from_path(self):
        """Test detection of workorder docs from path pattern"""
        paths = [
            "coderef/workorder/auth-system/context.json",
            "coderef/workorder/feature-x/analysis.json",
            "coderef/workorder/uds-system/DELIVERABLES.md",
        ]

        expected = ["workorder", "workorder", "workorder"]

        for path, exp in zip(paths, expected):
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == exp, f"Failed for {path}: got {vtype}, expected {exp}"

    def test_detect_plan_from_path(self):
        """Test detection of plan.json (special case)"""
        path = "coderef/workorder/auth-system/plan.json"
        vtype = ValidatorFactory.detect_validator_type(path)
        assert vtype == "plan"

    def test_detect_system_from_path(self):
        """Test detection of system docs from path pattern"""
        paths = [
            "CLAUDE.md",
            "papertrail/CLAUDE.md",
            "coderef/sessions/SESSION-INDEX.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "system", f"Failed for {path}"

    def test_detect_standards_from_path(self):
        """Test detection of standards docs from path pattern"""
        paths = [
            "standards/documentation/global-documentation-standards.md",
            "standards/resource-sheet-standards.md",
            "standards/coding-standards.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "standards", f"Failed for {path}"

    def test_detect_session_from_path(self):
        """Test detection of session docs from path pattern"""
        paths = [
            "coderef/sessions/session-1/communication.json",
            "coderef/sessions/multi-agent/instructions.json",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "session", f"Failed for {path}"

    def test_detect_infrastructure_from_path(self):
        """Test detection of infrastructure docs from path pattern"""
        paths = [
            "FILE-TREE.md",
            "coderef/user/VALIDATOR-INVENTORY.md",
            "docs/COMPONENT-INDEX.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "infrastructure", f"Failed for {path}"

    def test_detect_migration_from_path(self):
        """Test detection of migration/audit docs from path pattern"""
        paths = [
            "MIGRATION-TO-PYTHON.md",
            "AUDIT-REPORT.md",
            "COMPLETION-SUMMARY.md",
            "WO-AUTH-001-SUMMARY.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "migration", f"Failed for {path}"

    def test_detect_user_facing_from_path(self):
        """Test detection of user-facing docs from path pattern"""
        paths = [
            "USER-GUIDE.md",
            "docs/TUTORIAL-GETTING-STARTED.md",
            "docs/HOW-TO-DEPLOY.md",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "user_facing", f"Failed for {path}"

    def test_detect_general_markdown_fallback(self):
        """Test fallback to general markdown for unmatched .md files"""
        path = "docs/some-random-document.md"
        vtype = ValidatorFactory.detect_validator_type(path)
        assert vtype == "general"

    def test_detect_from_path_windows_paths(self):
        """Test detection works with Windows-style backslash paths"""
        path = r"C:\Users\test\coderef\foundation-docs\README.md"
        vtype = ValidatorFactory.detect_validator_type(path)
        assert vtype == "foundation"

    def test_detect_from_path_case_insensitive(self):
        """Test detection is case-insensitive"""
        paths = [
            "DOCS/AUTH-SERVICE-RESOURCE-SHEET.MD",
            "Coderef/Foundation-Docs/README.MD",
        ]

        expected = ["resource_sheet", "foundation"]

        for path, exp in zip(paths, expected):
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == exp, f"Failed for {path}"

    def test_get_validator_raises_for_unknown_type(self):
        """Test that get_validator raises ValueError for unknown file types"""
        with pytest.raises(ValueError, match="Cannot determine validator type"):
            ValidatorFactory.get_validator("file.txt")

    def test_get_validator_raises_for_unimplemented(self):
        """Test that get_validator raises NotImplementedError for placeholder validators"""
        # Foundation validator is not yet implemented (placeholder)
        with pytest.raises(NotImplementedError, match="Phase 2"):
            ValidatorFactory.get_validator("README.md")

    def test_path_pattern_priority(self):
        """Test that more specific patterns take priority over general ones"""
        # Resource sheet pattern should match before README pattern
        path = "docs/README-RESOURCE-SHEET.md"
        vtype = ValidatorFactory.detect_validator_type(path)
        assert vtype == "resource_sheet"

        # Foundation-specific README should match foundation
        path = "coderef/foundation-docs/README.md"
        vtype = ValidatorFactory.detect_validator_type(path)
        assert vtype == "foundation"

    def test_detect_validator_type_consistency(self):
        """Test that detect_validator_type is consistent with get_validator logic"""
        test_paths = [
            ("docs/AUTH-RESOURCE-SHEET.md", "resource_sheet"),
            ("README.md", "foundation"),
            ("CLAUDE.md", "system"),
            ("standards/global-standards.md", "standards"),
        ]

        for path, expected in test_paths:
            detected = ValidatorFactory.detect_validator_type(path)
            assert detected == expected, f"Detection mismatch for {path}"

    def test_factory_path_patterns_coverage(self):
        """Test that factory covers all major document types"""
        # Ensure we have patterns for all 9 validator types
        pattern_types = set()

        for pattern, vtype in ValidatorFactory.PATH_PATTERNS.items():
            pattern_types.add(vtype)

        # Should have patterns for most types (not all are path-detectable)
        expected_types = {
            "resource_sheet",
            "foundation",
            "workorder",
            "plan",
            "system",
            "standards",
            "session",
            "infrastructure",
            "migration",
            "user_facing",
        }

        assert pattern_types.issuperset(expected_types), \
            f"Missing patterns for: {expected_types - pattern_types}"
