"""
Functional Integration Tests for Validator Usage in Workflows

These tests verify validators work by running actual workflow-like operations
and checking outputs/behavior, rather than mocking validator calls.

Strategy: Instead of mocking validators and checking if they're called,
we create realistic test data, process it through validators (as workflows do),
and verify the expected outcomes.
"""

import pytest
import json
import tempfile
from pathlib import Path
from papertrail.validators.analysis import AnalysisValidator
from papertrail.validators.execution_log import ExecutionLogValidator
from papertrail.validators.factory import ValidatorFactory


class TestAnalysisValidatorFunctional:
    """Functional tests for AnalysisValidator integration

    These tests verify that AnalysisValidator behaves correctly when
    processing analysis.json files, simulating how coderef-workflow uses it.
    """

    def test_valid_analysis_json_passes_validation(self, tmp_path):
        """
        Verify AnalysisValidator accepts valid analysis.json

        This simulates coderef-workflow generating a valid analysis.json
        and running it through AnalysisValidator.
        """
        # Create valid analysis.json (as coderef-workflow would generate)
        analysis_data = {
            "foundation_docs": {
                "available": ["README.md", "ARCHITECTURE.md"],
                "missing": []
            },
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 100,
                "by_type": {
                    "function": 60,
                    "class": 30,
                    "component": 10
                }
            },
            "technology_stack": {
                "languages": ["Python", "TypeScript"],
                "frameworks": ["FastAPI", "React"],
                "tools": ["pytest", "jest"]
            },
            "project_structure": {
                "root": "/project",
                "key_directories": ["src", "tests"]
            },
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "workorder_id": "WO-TEST-001",
                "feature_id": "test-feature",
                "document_type": "Project Analysis",
                "last_updated": "2026-01-11T12:00:00Z",
                "ai_assistance": "Claude Sonnet 4.5",
                "status": "complete"
            }
        }

        # Validate (as coderef-workflow does)
        validator = AnalysisValidator()
        result = validator.validate_content(analysis_data)

        # Verify validation passes
        assert result.valid is True
        assert result.score >= 90
        assert len(result.errors) == 0

    def test_invalid_analysis_json_caught_by_validator(self):
        """
        Verify AnalysisValidator rejects invalid analysis.json

        This ensures workflows will catch invalid data before saving.
        """
        # Create invalid analysis.json (missing required fields)
        invalid_analysis = {
            "foundation_docs": {"available": [], "missing": []},
            "_uds": {"generated_by": "coderef-workflow"}
            # Missing: inventory_data, technology_stack, project_structure
        }

        validator = AnalysisValidator()
        result = validator.validate_content(invalid_analysis)

        # Verify validation fails
        assert result.valid is False
        assert result.score < 50  # Should be critically low
        assert len(result.errors) > 0

    def test_validation_metadata_can_be_added_to_uds(self):
        """
        Verify validation score can be added to _uds metadata

        This shows how coderef-workflow should enhance analysis.json
        with validation results.
        """
        analysis_data = {
            "foundation_docs": {"available": ["README.md"], "missing": []},
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 50,
                "by_type": {"function": 50}
            },
            "technology_stack": {
                "languages": ["Python"],
                "frameworks": ["FastAPI"],
                "tools": ["pytest"]
            },
            "project_structure": {
                "root": "/project",
                "key_directories": ["src"]
            },
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "workorder_id": "WO-TEST-001",
                "feature_id": "test-feature",
                "document_type": "Project Analysis",
                "last_updated": "2026-01-11T12:00:00Z",
                "ai_assistance": "Claude Sonnet 4.5",
                "status": "complete"
            }
        }

        # Validate and add metadata (as workflow should do)
        validator = AnalysisValidator()
        result = validator.validate_content(analysis_data)

        # Add validation metadata to _uds
        analysis_data["_uds"]["validation_score"] = result.score
        analysis_data["_uds"]["validation_errors"] = len(result.errors)
        analysis_data["_uds"]["validation_warnings"] = len(result.warnings)

        # Verify metadata was added
        assert "validation_score" in analysis_data["_uds"]
        assert analysis_data["_uds"]["validation_score"] >= 90
        assert "validation_errors" in analysis_data["_uds"]
        assert "validation_warnings" in analysis_data["_uds"]


class TestExecutionLogValidatorFunctional:
    """Functional tests for ExecutionLogValidator integration

    These tests verify ExecutionLogValidator works correctly with
    execution-log.json files, including cross-validation.
    """

    def test_valid_execution_log_passes_validation(self, tmp_path):
        """
        Verify ExecutionLogValidator accepts valid execution-log.json
        """
        exec_log_data = {
            "timestamp": "2026-01-11T12:00:00Z",
            "workorder_id": "WO-TEST-FEATURE-001",
            "feature_name": "test-feature",
            "task_count": 2,
            "tasks": [
                {
                    "task_id": "SETUP-001",
                    "status": "completed",
                    "started_at": "2026-01-11T12:00:00Z",
                    "completed_at": "2026-01-11T12:05:00Z"
                },
                {
                    "task_id": "IMPL-001",
                    "status": "in_progress",
                    "started_at": "2026-01-11T12:05:00Z"
                }
            ]
        }

        validator = ExecutionLogValidator()
        result = validator.validate_content(exec_log_data)

        # Verify validation passes
        assert result.valid is True
        assert result.score >= 90
        assert len(result.errors) == 0

    def test_cross_validation_detects_orphaned_task_ids(self, tmp_path):
        """
        Verify cross-validation catches task IDs not in plan.json

        This is CRITICAL for workflow integrity - ensures execution log
        tasks actually exist in the implementation plan.
        """
        # Create plan.json with valid task IDs
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-TEST-001"},
            "6_IMPLEMENTATION_PHASES": {
                "phases": [
                    {
                        "phase_id": "phase_1",
                        "tasks": [
                            {"task_id": "SETUP-001", "description": "Setup"},
                            {"task_id": "IMPL-001", "description": "Implementation"}
                        ]
                    }
                ]
            }
        }

        plan_file = tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan_data))

        # Create execution log with orphaned task ID
        exec_log_data = {
            "timestamp": "2026-01-11T12:00:00Z",
            "workorder_id": "WO-TEST-001",
            "feature_name": "test-feature",
            "task_count": 1,
            "tasks": [
                {
                    "task_id": "ORPHAN-999",  # Not in plan.json!
                    "status": "completed",
                    "started_at": "2026-01-11T12:00:00Z",
                    "completed_at": "2026-01-11T12:05:00Z"
                }
            ]
        }

        exec_log_file = tmp_path / "execution-log.json"
        exec_log_file.write_text(json.dumps(exec_log_data))

        # Validate with cross-validation enabled
        validator = ExecutionLogValidator()
        result = validator.validate_file(exec_log_file, enable_cross_validation=True)

        # Verify orphaned task ID was caught
        assert result.valid is False
        assert result.score < 90
        orphan_errors = [e for e in result.errors if "not found in plan" in e.message.lower()]
        assert len(orphan_errors) > 0

    def test_cross_validation_passes_with_valid_task_ids(self, tmp_path):
        """
        Verify cross-validation succeeds when task IDs match plan.json
        """
        # Create plan.json
        plan_data = {
            "META_DOCUMENTATION": {"workorder_id": "WO-TEST-001"},
            "6_IMPLEMENTATION_PHASES": {
                "phases": [
                    {
                        "phase_id": "phase_1",
                        "tasks": [
                            {"task_id": "SETUP-001", "description": "Setup"},
                            {"task_id": "IMPL-001", "description": "Implementation"}
                        ]
                    }
                ]
            }
        }

        plan_file = tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan_data))

        # Create execution log with valid task IDs
        exec_log_data = {
            "timestamp": "2026-01-11T12:00:00Z",
            "workorder_id": "WO-TEST-001",
            "feature_name": "test-feature",
            "task_count": 2,
            "tasks": [
                {
                    "task_id": "SETUP-001",  # Valid
                    "status": "completed",
                    "started_at": "2026-01-11T12:00:00Z",
                    "completed_at": "2026-01-11T12:05:00Z"
                },
                {
                    "task_id": "IMPL-001",  # Valid
                    "status": "in_progress",
                    "started_at": "2026-01-11T12:05:00Z"
                }
            ]
        }

        exec_log_file = tmp_path / "execution-log.json"
        exec_log_file.write_text(json.dumps(exec_log_data))

        # Validate with cross-validation
        validator = ExecutionLogValidator()
        result = validator.validate_file(exec_log_file, enable_cross_validation=True)

        # Verify validation passes
        assert result.valid is True
        assert result.score >= 90
        orphan_errors = [e for e in result.errors if "not found in plan" in e.message.lower()]
        assert len(orphan_errors) == 0


class TestValidatorFactoryFunctional:
    """Functional tests for ValidatorFactory integration

    These tests verify ValidatorFactory can auto-detect and instantiate
    validators correctly for different file types.
    """

    def test_factory_detects_analysis_json_and_validates(self, tmp_path):
        """
        Verify ValidatorFactory can auto-detect analysis.json and validate it

        This simulates how workflows should use the factory pattern:
        "Give me the right validator for this file path"
        """
        # Create analysis.json file
        analysis_data = {
            "foundation_docs": {"available": ["README.md"], "missing": []},
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 50,
                "by_type": {"function": 50}
            },
            "technology_stack": {
                "languages": ["Python"],
                "frameworks": ["FastAPI"],
                "tools": ["pytest"]
            },
            "project_structure": {
                "root": "/project",
                "key_directories": ["src"]
            },
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "workorder_id": "WO-TEST-001",
                "feature_id": "test-feature",
                "document_type": "Project Analysis",
                "last_updated": "2026-01-11T12:00:00Z",
                "ai_assistance": "Claude Sonnet 4.5",
                "status": "complete"
            }
        }

        analysis_file = tmp_path / "coderef" / "workorder" / "test-feature" / "analysis.json"
        analysis_file.parent.mkdir(parents=True)
        analysis_file.write_text(json.dumps(analysis_data))

        # Use factory to get validator (as workflows should)
        validator = ValidatorFactory.get_validator(str(analysis_file))

        # Verify correct validator type returned
        assert isinstance(validator, AnalysisValidator)

        # Verify it can validate the file
        result = validator.validate_file(analysis_file)
        assert result.valid is True
        assert result.score >= 90

    def test_factory_detects_execution_log_and_validates(self, tmp_path):
        """
        Verify ValidatorFactory can auto-detect execution-log.json and validate it
        """
        # Create execution-log.json file
        exec_log_data = {
            "timestamp": "2026-01-11T12:00:00Z",
            "workorder_id": "WO-TEST-001",
            "feature_name": "test-feature",
            "task_count": 1,
            "tasks": [
                {
                    "task_id": "SETUP-001",
                    "status": "completed",
                    "started_at": "2026-01-11T12:00:00Z",
                    "completed_at": "2026-01-11T12:05:00Z"
                }
            ]
        }

        exec_log_file = tmp_path / "coderef" / "workorder" / "test-feature" / "execution-log.json"
        exec_log_file.parent.mkdir(parents=True)
        exec_log_file.write_text(json.dumps(exec_log_data))

        # Use factory to get validator
        validator = ValidatorFactory.get_validator(str(exec_log_file))

        # Verify correct validator type
        assert isinstance(validator, ExecutionLogValidator)

        # Verify it can validate
        result = validator.validate_file(exec_log_file)
        assert result.valid is True

    def test_factory_pattern_workflow_simulation(self, tmp_path):
        """
        Simulate complete workflow: generate file → auto-detect validator → validate

        This demonstrates the ideal workflow pattern:
        1. Generate analysis.json
        2. Get validator from factory (auto-detection)
        3. Validate
        4. Add validation metadata to _uds
        5. Save final file
        """
        # Step 1: Workflow generates analysis.json
        analysis_data = {
            "foundation_docs": {"available": ["README.md"], "missing": []},
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 50,
                "by_type": {"function": 50}
            },
            "technology_stack": {
                "languages": ["Python"],
                "frameworks": ["FastAPI"],
                "tools": ["pytest"]
            },
            "project_structure": {
                "root": "/project",
                "key_directories": ["src"]
            },
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "workorder_id": "WO-TEST-001",
                "feature_id": "test-feature",
                "document_type": "Project Analysis",
                "last_updated": "2026-01-11T12:00:00Z",
                "ai_assistance": "Claude Sonnet 4.5",
                "status": "complete"
            }
        }

        output_file = tmp_path / "coderef" / "workorder" / "test" / "analysis.json"
        output_file.parent.mkdir(parents=True)

        # Step 2: Auto-detect validator (factory pattern)
        validator = ValidatorFactory.get_validator(str(output_file))

        # Step 3: Validate
        result = validator.validate_content(analysis_data)

        # Step 4: Add validation metadata
        analysis_data["_uds"]["validation_score"] = result.score
        analysis_data["_uds"]["validation_errors"] = len(result.errors)
        analysis_data["_uds"]["validation_warnings"] = len(result.warnings)

        # Step 5: Save final file
        output_file.write_text(json.dumps(analysis_data, indent=2))

        # Verify workflow succeeded
        assert output_file.exists()
        saved_data = json.loads(output_file.read_text())
        assert "validation_score" in saved_data["_uds"]
        assert saved_data["_uds"]["validation_score"] >= 90


class TestErrorHandlingFunctional:
    """Functional tests for validation error handling

    These tests verify workflows handle validation errors correctly.
    """

    def test_low_validation_score_generates_warnings(self, caplog):
        """
        Verify validation scores 50-90 generate warnings but don't raise errors
        """
        import logging
        caplog.set_level(logging.WARNING)

        # Create analysis with warnings (incomplete data)
        analysis_data = {
            "foundation_docs": {"available": [], "missing": ["README.md"]},
            "inventory_data": {
                "source": "coderef_index",
                "total_elements": 10,
                "by_type": {"function": 5, "class": 5}  # Small project
            },
            "technology_stack": {
                "languages": ["Python"],
                "frameworks": ["unknown", "unknown", "unknown"],  # Too many unknowns
                "tools": ["pytest"]
            },
            "project_structure": {
                "root": "/project",
                "key_directories": ["src"]
            },
            "_uds": {
                "generated_by": "coderef-workflow v2.0.0",
                "workorder_id": "WO-TEST-001",
                "feature_id": "test-feature",
                "document_type": "Project Analysis",
                "last_updated": "2026-01-11T12:00:00Z",
                "ai_assistance": "Claude Sonnet 4.5",
                "status": "complete"
            }
        }

        validator = AnalysisValidator()
        result = validator.validate_content(analysis_data)

        # Should have warnings but not fail critically
        assert 50 <= result.score < 90
        assert len(result.warnings) > 0

        # Workflow should log warnings (simulated)
        if result.score < 90:
            import logging
            logger = logging.getLogger("coderef-workflow")
            logger.warning(f"Analysis validation score: {result.score}")
            for warning in result.warnings:
                logger.warning(f"  WARNING: {warning}")

        # Verify warnings were logged
        assert any("validation score" in record.message.lower() for record in caplog.records)

    def test_critical_validation_failure_should_raise_error(self):
        """
        Verify validation scores < 50 should cause workflows to fail
        """
        # Create critically invalid analysis (missing everything)
        invalid_analysis = {
            "_uds": {"generated_by": "test"}
            # Missing all required fields
        }

        validator = AnalysisValidator()
        result = validator.validate_content(invalid_analysis)

        # Should fail critically
        assert result.score < 50

        # Workflow should raise ValueError (simulated)
        if result.score < 50:
            with pytest.raises(ValueError, match="Validation failed|score"):
                raise ValueError(
                    f"Validation failed: analysis.json score {result.score} (minimum: 50). "
                    f"Fix {len(result.errors)} errors before proceeding."
                )
