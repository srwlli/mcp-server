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

    # ===== NEW INTEGRATION TESTS (TEST-003) =====

    def test_analysis_json_detection(self):
        """Test that analysis.json paths are correctly detected as AnalysisValidator"""
        from papertrail.validators.analysis import AnalysisValidator

        paths = [
            "/path/to/coderef/workorder/my-feature/analysis.json",
            "C:/Users/test/coderef/workorder/auth-system/analysis.json",
            "/project/coderef/workorder/feature-x/analysis.json",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "analysis", f"Failed to detect analysis type for {path}"

            # Verify get_validator returns AnalysisValidator instance
            validator = ValidatorFactory.get_validator(path)
            assert isinstance(validator, AnalysisValidator), \
                f"Expected AnalysisValidator instance for {path}, got {type(validator)}"

    def test_execution_log_detection(self):
        """Test that execution-log.json paths are correctly detected as ExecutionLogValidator"""
        from papertrail.validators.execution_log import ExecutionLogValidator

        paths = [
            "/path/to/coderef/workorder/my-feature/execution-log.json",
            "C:/project/coderef/workorder/auth-system/execution-log.json",
            "/home/user/coderef/workorder/feature-x/execution-log.json",
        ]

        for path in paths:
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == "execution_log", f"Failed to detect execution_log type for {path}"

            # Verify get_validator returns ExecutionLogValidator instance
            validator = ValidatorFactory.get_validator(path)
            assert isinstance(validator, ExecutionLogValidator), \
                f"Expected ExecutionLogValidator instance for {path}, got {type(validator)}"

    def test_path_pattern_matching_edge_cases(self):
        """Test path pattern matching for edge cases (nested dirs, different separators)"""
        import tempfile
        from pathlib import Path

        # Test nested directories
        nested_paths = [
            "/path/to/coderef/workorder/nested/deep/structure/analysis.json",
            "C:/coderef/workorder/windows/path/execution-log.json",  # Windows-style
            "/unix/style/coderef/workorder/feature/analysis.json",
        ]

        expected = ["analysis", "execution_log", "analysis"]

        for path, exp in zip(nested_paths, expected):
            vtype = ValidatorFactory.detect_validator_type(path)
            assert vtype == exp, f"Failed for nested path {path}: got {vtype}, expected {exp}"

    def test_end_to_end_analysis_validation(self):
        """Test end-to-end analysis.json validation using ValidatorFactory auto-detection"""
        import tempfile
        import json

        valid_analysis = {
            "foundation_docs": {
                "available": ["README.md"],
                "missing": []
            },
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 50,
                "by_type": {"function": 30, "class": 20},
                "files": 10
            },
            "technology_stack": {
                "language": "Python",
                "framework": "Flask",
                "database": "PostgreSQL",
                "testing": "pytest",
                "build": "setuptools"
            },
            "project_structure": {
                "main_directories": ["src"],
                "file_counts": {"src": 10},
                "organization_pattern": "modular"
            },
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "document_type": "Project Analysis",
                "workorder_id": "WO-TEST-FEATURE-001",
                "feature_id": "test-feature",
                "last_updated": "2026-01-10",
                "ai_assistance": True,
                "status": "DRAFT",
                "next_review": "2026-02-10"
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create workorder directory structure
            workorder_dir = tmpdir_path / "coderef" / "workorder" / "test-feature"
            workorder_dir.mkdir(parents=True, exist_ok=True)

            # Write analysis.json
            analysis_path = workorder_dir / "analysis.json"
            with open(analysis_path, 'w') as f:
                json.dump(valid_analysis, f)

            # Auto-detect validator and validate
            validator = ValidatorFactory.get_validator(analysis_path)
            result = validator.validate_file(analysis_path)

            # Should pass validation without manual instantiation
            assert result.score >= 90, f"Expected score >= 90, got {result.score}. Errors: {result.errors}"
            assert result.valid is True

    def test_end_to_end_execution_log_validation_with_cross_validation(self):
        """Test end-to-end execution-log.json validation with cross-validation using ValidatorFactory"""
        import tempfile
        import json

        valid_exec_log = [
            {
                "timestamp": "2026-01-10T14:40:21.165589",
                "workorder_id": "WO-TEST-FEATURE-001",
                "feature_name": "test-feature",
                "task_count": 2,
                "tasks": [
                    {
                        "content": "SETUP-001: Setup project",
                        "status": "completed",
                        "activeForm": "Setting up project"
                    },
                    {
                        "content": "IMPL-001: Implement feature",
                        "status": "in_progress",
                        "activeForm": "Implementing feature"
                    }
                ]
            }
        ]

        valid_plan = {
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "tasks": [
                        {"id": "SETUP-001", "description": "Setup"},
                        {"id": "IMPL-001", "description": "Implementation"}
                    ]
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create workorder directory structure
            workorder_dir = tmpdir_path / "coderef" / "workorder" / "test-feature"
            workorder_dir.mkdir(parents=True, exist_ok=True)

            # Write execution-log.json
            exec_log_path = workorder_dir / "execution-log.json"
            with open(exec_log_path, 'w') as f:
                json.dump(valid_exec_log, f)

            # Write plan.json
            plan_path = workorder_dir / "plan.json"
            with open(plan_path, 'w') as f:
                json.dump(valid_plan, f)

            # Auto-detect validator and validate with cross-validation
            validator = ValidatorFactory.get_validator(exec_log_path)
            result = validator.validate_file(exec_log_path, enable_cross_validation=True)

            # Should pass validation with cross-validation
            assert result.score >= 90, f"Expected score >= 90, got {result.score}. Errors: {result.errors}"
            assert result.valid is True

            # Verify no cross-validation errors
            cross_val_errors = [e for e in result.errors if "not found in plan" in e.message.lower()]
            assert len(cross_val_errors) == 0, f"Unexpected cross-validation errors: {cross_val_errors}"
