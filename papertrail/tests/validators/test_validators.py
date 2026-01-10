"""
Unit tests for AnalysisValidator and ExecutionLogValidator

Tests:
- AnalysisValidator: Schema validation, UDS metadata, inventory consistency
- ExecutionLogValidator: Schema validation, cross-validation with plan.json
- Format validation for workorder_id and feature_name
"""

import pytest
import json
import tempfile
from pathlib import Path
from papertrail.validators.analysis import AnalysisValidator
from papertrail.validators.execution_log import ExecutionLogValidator
from papertrail.validator import ValidationSeverity


class TestAnalysisValidator:
    """Test suite for AnalysisValidator"""

    @pytest.fixture
    def schemas_dir(self):
        """Get schemas directory path"""
        return Path(__file__).parent.parent.parent / "schemas" / "workflow"

    @pytest.fixture
    def valid_analysis_data(self):
        """Valid analysis.json structure"""
        return {
            "foundation_docs": {
                "available": ["README.md", "ARCHITECTURE.md"],
                "missing": ["USER-GUIDE.md"]
            },
            "foundation_doc_content": {},
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 100,
                "by_type": {
                    "function": 50,
                    "class": 30,
                    "method": 20
                },
                "files": 25,
                "utilization": "90%"
            },
            "technology_stack": {
                "language": "Python",
                "framework": "Flask",
                "database": "PostgreSQL",
                "testing": "pytest",
                "build": "setuptools"
            },
            "project_structure": {
                "main_directories": ["src", "tests"],
                "file_counts": {"src": 20, "tests": 5},
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
                "next_review": "2026-02-09"
            }
        }

    def test_valid_analysis_json(self, schemas_dir, valid_analysis_data):
        """Test validation of valid analysis.json"""
        validator = AnalysisValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(valid_analysis_data)

        assert result.score >= 90, f"Expected score >= 90, got {result.score}"
        assert result.valid is True
        # No CRITICAL or MAJOR errors
        critical_errors = [e for e in result.errors if e.severity == ValidationSeverity.CRITICAL]
        major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR]
        assert len(critical_errors) == 0, f"Found CRITICAL errors: {critical_errors}"
        assert len(major_errors) == 0, f"Found MAJOR errors: {major_errors}"

    def test_invalid_analysis_missing_required(self, schemas_dir):
        """Test validation with missing required field"""
        invalid_data = {
            # Missing 'foundation_docs' - required field
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 100,
                "by_type": {},
                "files": 25
            },
            "technology_stack": {},
            "project_structure": {},
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "document_type": "Project Analysis"
            }
        }

        validator = AnalysisValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data)

        assert result.score < 90, f"Expected score < 90 for missing required field, got {result.score}"
        # Should have MAJOR error for schema validation failure
        major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR]
        assert len(major_errors) > 0, "Expected MAJOR error for missing required field"

    def test_invalid_analysis_wrong_type(self, schemas_dir, valid_analysis_data):
        """Test validation with invalid enum value"""
        invalid_data = valid_analysis_data.copy()
        invalid_data["inventory_data"]["source"] = "invalid_source"  # Invalid enum

        validator = AnalysisValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data)

        assert result.score < 90, f"Expected score < 90 for invalid enum, got {result.score}"
        # Should have MAJOR error for schema validation
        major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR]
        assert len(major_errors) > 0, "Expected MAJOR error for invalid enum value"

    def test_uds_metadata_validation(self, schemas_dir, valid_analysis_data):
        """Test UDS metadata validation"""
        invalid_data = valid_analysis_data.copy()
        invalid_data["_uds"]["workorder_id"] = "INVALID-FORMAT"  # Invalid workorder_id format

        validator = AnalysisValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data)

        # Should have MAJOR error for invalid workorder_id format
        major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR and "workorder_id" in e.message.lower()]
        assert len(major_errors) > 0, "Expected MAJOR error for invalid workorder_id format"
        assert result.score < 90

    def test_inventory_consistency(self, schemas_dir, valid_analysis_data):
        """Test inventory data consistency check"""
        invalid_data = valid_analysis_data.copy()
        # total_elements (100) doesn't match sum of by_type (50+30+20 = 100), so let's make them inconsistent
        invalid_data["inventory_data"]["total_elements"] = 200  # Mismatch

        validator = AnalysisValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data)

        # Should have WARNING for inventory mismatch (within tolerance)
        warnings = result.warnings
        has_inventory_warning = any("total_elements" in str(w).lower() for w in warnings)
        assert has_inventory_warning, "Expected WARNING for inventory mismatch"

    def test_tech_stack_warnings(self, schemas_dir, valid_analysis_data):
        """Test technology stack completeness warning"""
        invalid_data = valid_analysis_data.copy()
        # Set 3+ fields to 'unknown'
        invalid_data["technology_stack"] = {
            "language": "unknown",
            "framework": "unknown",
            "database": "unknown",
            "testing": "pytest",
            "build": "unknown"
        }

        validator = AnalysisValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data)

        # Should have WARNING for too many unknown values
        warnings = result.warnings
        has_tech_warning = any("unknown" in str(w).lower() and "technology_stack" in str(w).lower() for w in warnings)
        assert has_tech_warning, "Expected WARNING for too many unknown values in tech stack"


class TestExecutionLogValidator:
    """Test suite for ExecutionLogValidator"""

    @pytest.fixture
    def schemas_dir(self):
        """Get schemas directory path"""
        return Path(__file__).parent.parent.parent / "schemas" / "workflow"

    @pytest.fixture
    def valid_execution_log_data(self):
        """Valid execution-log.json structure"""
        return [
            {
                "timestamp": "2026-01-10T14:40:21.165589",
                "workorder_id": "WO-TEST-FEATURE-001",
                "feature_name": "test-feature",
                "task_count": 3,
                "tasks": [
                    {
                        "content": "SETUP-001: Setup project structure",
                        "status": "completed",
                        "activeForm": "Setting up project structure"
                    },
                    {
                        "content": "IMPL-001: Implement core functionality",
                        "status": "in_progress",
                        "activeForm": "Implementing core functionality"
                    },
                    {
                        "content": "TEST-001: Add unit tests",
                        "status": "pending",
                        "activeForm": "Adding unit tests"
                    }
                ]
            }
        ]

    @pytest.fixture
    def valid_plan_data(self):
        """Valid plan.json structure with task IDs"""
        return {
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "tasks": [
                        {"id": "SETUP-001", "description": "Setup"},
                        {"id": "IMPL-001", "description": "Implementation"},
                        {"id": "TEST-001", "description": "Testing"}
                    ]
                }
            }
        }

    def test_valid_execution_log(self, schemas_dir, valid_execution_log_data):
        """Test validation of valid execution-log.json"""
        validator = ExecutionLogValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(valid_execution_log_data, enable_cross_validation=False)

        assert result.score >= 90, f"Expected score >= 90, got {result.score}"
        assert result.valid is True

    def test_invalid_missing_workorder_id(self, schemas_dir):
        """Test validation with missing workorder_id"""
        invalid_data = [
            {
                # Missing workorder_id
                "feature_name": "test-feature",
                "task_count": 1,
                "tasks": []
            }
        ]

        validator = ExecutionLogValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data, enable_cross_validation=False)

        # Should have MAJOR error for schema validation failure
        major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR]
        assert len(major_errors) > 0, "Expected MAJOR error for missing workorder_id"
        assert result.score < 90

    def test_invalid_task_status_enum(self, schemas_dir, valid_execution_log_data):
        """Test validation with invalid task status enum"""
        invalid_data = valid_execution_log_data.copy()
        invalid_data[0]["tasks"][0]["status"] = "invalid_status"  # Invalid enum

        validator = ExecutionLogValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data, enable_cross_validation=False)

        # Should have MAJOR error for invalid enum
        major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR]
        assert len(major_errors) > 0, "Expected MAJOR error for invalid status enum"

    def test_workorder_id_format(self, schemas_dir):
        """Test workorder_id format validation"""
        # Test valid format
        valid_data = [
            {
                "timestamp": "2026-01-10T14:40:21.165589",
                "workorder_id": "WO-AUTH-SYSTEM-001",
                "feature_name": "auth-system",
                "task_count": 0,
                "tasks": []
            }
        ]
        validator = ExecutionLogValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(valid_data, enable_cross_validation=False)
        assert result.score >= 90, "Valid workorder_id should pass"

        # Test invalid formats
        invalid_formats = ["WO-001", "AUTH-001", "invalid-format", "WO-A-001"]
        for invalid_id in invalid_formats:
            invalid_data = [
                {
                    "timestamp": "2026-01-10T14:40:21.165589",
                    "workorder_id": invalid_id,
                    "feature_name": "test",
                    "task_count": 0,
                    "tasks": []
                }
            ]
            result = validator.validate_content(invalid_data, enable_cross_validation=False)
            major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR and "workorder_id" in e.message.lower()]
            assert len(major_errors) > 0, f"Expected error for invalid workorder_id: {invalid_id}"

    def test_feature_name_format(self, schemas_dir):
        """Test feature_name format validation (kebab-case)"""
        # Test valid format
        valid_data = [
            {
                "timestamp": "2026-01-10T14:40:21.165589",
                "workorder_id": "WO-TEST-FEATURE-001",
                "feature_name": "my-feature-name",
                "task_count": 0,
                "tasks": []
            }
        ]
        validator = ExecutionLogValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(valid_data, enable_cross_validation=False)
        assert result.score >= 90, "Valid feature_name should pass"

        # Test invalid formats
        invalid_names = ["MyFeature", "my_feature", "My Feature!", "123Feature"]
        for invalid_name in invalid_names:
            invalid_data = [
                {
                    "timestamp": "2026-01-10T14:40:21.165589",
                    "workorder_id": "WO-TEST-FEATURE-001",
                    "feature_name": invalid_name,
                    "task_count": 0,
                    "tasks": []
                }
            ]
            result = validator.validate_content(invalid_data, enable_cross_validation=False)
            major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR and "feature_name" in e.message.lower()]
            assert len(major_errors) > 0, f"Expected error for invalid feature_name: {invalid_name}"

    def test_task_count_mismatch(self, schemas_dir, valid_execution_log_data):
        """Test task_count mismatch detection"""
        invalid_data = valid_execution_log_data.copy()
        invalid_data[0]["task_count"] = 10  # Mismatch with actual count (3)

        validator = ExecutionLogValidator(schemas_dir=schemas_dir)
        result = validator.validate_content(invalid_data, enable_cross_validation=False)

        # Should have MINOR error for count mismatch
        minor_errors = [e for e in result.errors if e.severity == ValidationSeverity.MINOR and "task_count" in e.message.lower()]
        assert len(minor_errors) > 0, "Expected MINOR error for task_count mismatch"

    def test_cross_validation_valid(self, schemas_dir, valid_execution_log_data, valid_plan_data):
        """Test cross-validation with valid plan.json"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write execution-log.json
            exec_log_path = tmpdir_path / "execution-log.json"
            with open(exec_log_path, 'w') as f:
                json.dump(valid_execution_log_data, f)

            # Write plan.json
            plan_path = tmpdir_path / "plan.json"
            with open(plan_path, 'w') as f:
                json.dump(valid_plan_data, f)

            # Validate with cross-validation enabled
            validator = ExecutionLogValidator(schemas_dir=schemas_dir)
            result = validator.validate_file(exec_log_path, enable_cross_validation=True)

            # Should have no cross-validation errors
            cross_val_errors = [e for e in result.errors if "cross-validation" in e.message.lower() or "not found in plan" in e.message.lower()]
            assert len(cross_val_errors) == 0, f"Expected no cross-validation errors, got: {cross_val_errors}"
            assert result.score >= 90

    def test_cross_validation_invalid(self, schemas_dir, valid_plan_data):
        """Test cross-validation with orphaned task_id"""
        invalid_exec_log = [
            {
                "workorder_id": "WO-TEST-FEATURE-001",
                "feature_name": "test-feature",
                "task_count": 1,
                "tasks": [
                    {
                        "content": "ORPHAN-999: This task doesn't exist in plan.json",
                        "status": "pending",
                        "activeForm": "Working on orphaned task"
                    }
                ]
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write execution-log.json
            exec_log_path = tmpdir_path / "execution-log.json"
            with open(exec_log_path, 'w') as f:
                json.dump(invalid_exec_log, f)

            # Write plan.json
            plan_path = tmpdir_path / "plan.json"
            with open(plan_path, 'w') as f:
                json.dump(valid_plan_data, f)

            # Validate with cross-validation enabled
            validator = ExecutionLogValidator(schemas_dir=schemas_dir)
            result = validator.validate_file(exec_log_path, enable_cross_validation=True)

            # Should have MAJOR error for orphaned task_id
            major_errors = [e for e in result.errors if e.severity == ValidationSeverity.MAJOR and "not found in plan" in e.message.lower()]
            assert len(major_errors) > 0, "Expected MAJOR error for orphaned task_id"
            assert result.score < 90

    def test_cross_validation_missing_plan(self, schemas_dir, valid_execution_log_data):
        """Test cross-validation with missing plan.json (graceful fallback)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write only execution-log.json (no plan.json)
            exec_log_path = tmpdir_path / "execution-log.json"
            with open(exec_log_path, 'w') as f:
                json.dump(valid_execution_log_data, f)

            # Validate with cross-validation enabled
            validator = ExecutionLogValidator(schemas_dir=schemas_dir)
            result = validator.validate_file(exec_log_path, enable_cross_validation=True)

            # Should have WARNING (not CRITICAL) about missing plan.json
            warnings = result.warnings
            has_plan_warning = any("plan.json not found" in str(w).lower() or "cross-validation skipped" in str(w).lower() for w in warnings)
            assert has_plan_warning, "Expected WARNING about missing plan.json"

            # Should not have CRITICAL errors (graceful fallback)
            critical_errors = [e for e in result.errors if e.severity == ValidationSeverity.CRITICAL]
            assert len(critical_errors) == 0, "Expected no CRITICAL errors for missing plan.json (graceful fallback)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
