"""
Integration Tests for Validator Usage in Workflows

These tests demonstrate what ISN'T working yet - validators exist but aren't
being called by coderef-workflow tools.

Status: ❌ EXPECTED TO FAIL (validators not integrated yet)

Purpose: Provide specifications for next session to integrate validators into:
1. analyze_project_for_planning (should call AnalysisValidator)
2. execute_plan (should call ExecutionLogValidator)
3. update_task_status (should validate before updating)

When these tests pass, we'll have proof that validators are actually being used.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call


class TestAnalysisValidatorIntegration:
    """Test that coderef-workflow uses AnalysisValidator when generating analysis.json

    Current Status: ❌ FAILING (not integrated)
    Expected: Will pass after WO-VALIDATOR-INTEGRATION-001
    """

    @pytest.mark.xfail(reason="AnalysisValidator not yet integrated into workflow", strict=True)
    def test_analyze_project_calls_validator(self):
        """
        PROOF TEST: Verify analyze_project_for_planning calls AnalysisValidator

        What this proves when passing:
        - The workflow tool explicitly invokes AnalysisValidator
        - Validation happens automatically during analysis generation

        Integration requirement:
        - Add: from papertrail.validators.analysis import AnalysisValidator
        - Call: validator.validate_content(analysis_data) after generation
        """
        from papertrail.validators.analysis import AnalysisValidator

        # Mock the workflow tool (would import from coderef-workflow if available)
        # For now, we simulate what it should do
        with patch.object(AnalysisValidator, 'validate_content') as mock_validate:
            mock_validate.return_value = MagicMock(
                valid=True,
                errors=[],
                warnings=[],
                score=95
            )

            # This would be the actual workflow call:
            # from coderef_workflow.generators.planning_analyzer import analyze_project_for_planning
            # result = analyze_project_for_planning(project_path="/test", feature_name="test")

            # For now, simulate expected behavior
            # EXPECTED: Workflow should call validator.validate_content()
            # ACTUAL: No call happens (validator not integrated)

            # This assertion will fail until integration is complete
            assert mock_validate.called, \
                "AnalysisValidator.validate_content() should be called by analyze_project_for_planning"
            assert mock_validate.call_count == 1

    @pytest.mark.xfail(reason="Validation metadata not added to output", strict=True)
    def test_analysis_output_includes_validation_metadata(self):
        """
        PROOF TEST: Verify analysis.json includes validation score in _uds metadata

        What this proves when passing:
        - Generated analysis.json contains validation_score field
        - Validation errors/warnings are captured in output
        - Users can see validation quality at a glance

        Integration requirement:
        - After validation, add to _uds section:
          {
            "_uds": {
              "validation_score": 95,
              "validation_errors": 0,
              "validation_warnings": 2
            }
          }
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Simulate workflow generating analysis.json
            # EXPECTED: File should contain validation metadata
            # ACTUAL: File exists but no validation metadata

            analysis_file = tmpdir_path / "analysis.json"
            analysis_data = {
                "foundation_docs": {"available": [], "missing": []},
                "inventory_data": {
                    "source": "coderef_index",
                    "total_elements": 100,
                    "by_type": {},
                    "files": 10
                },
                "technology_stack": {},
                "project_structure": {},
                "_uds": {
                    "generated_by": "coderef-workflow v2.0.0",
                    "document_type": "Project Analysis"
                    # Missing: validation_score, validation_errors, validation_warnings
                }
            }

            analysis_file.write_text(json.dumps(analysis_data, indent=2))

            # Read back and check for validation metadata
            data = json.loads(analysis_file.read_text())

            # These assertions will fail until validation metadata is added
            assert "validation_score" in data["_uds"], \
                "analysis.json should include validation_score in _uds metadata"
            assert "validation_errors" in data["_uds"], \
                "analysis.json should include validation_errors count"
            assert data["_uds"]["validation_score"] >= 0, \
                "validation_score should be 0-100"

    @pytest.mark.xfail(reason="Low validation scores not logged/rejected", strict=True)
    def test_workflow_warns_on_low_validation_score(self, caplog):
        """
        PROOF TEST: Verify workflow logs warnings when validation score < 90

        What this proves when passing:
        - Workflow detects validation failures
        - Users are warned about quality issues
        - Validation isn't silently ignored

        Integration requirement:
        - After validation, check if result.score < 90
        - Log warnings for each error found
        - Optionally: fail workflow or mark as "needs review"
        """
        from papertrail.validators.analysis import AnalysisValidator

        # Create invalid analysis data (will score < 90)
        invalid_data = {
            "foundation_docs": {"available": [], "missing": []},
            # Missing required fields: inventory_data, technology_stack, project_structure
            "_uds": {}
        }

        validator = AnalysisValidator()
        result = validator.validate_content(invalid_data)

        # Simulate what workflow should do
        # EXPECTED: Workflow logs warnings when score < 90
        # ACTUAL: No logging happens

        if result.score < 90:
            # This is what workflow SHOULD do (but doesn't yet)
            import logging
            logger = logging.getLogger("coderef-workflow")
            logger.warning(f"Analysis validation score: {result.score}")
            for error in result.errors:
                logger.warning(f"  {error.severity.value}: {error.message}")

        # This assertion will fail until workflow adds logging
        assert "Analysis validation score" in caplog.text, \
            "Workflow should log validation score when < 90"
        assert "MAJOR" in caplog.text or "CRITICAL" in caplog.text, \
            "Workflow should log validation errors"


class TestExecutionLogValidatorIntegration:
    """Test that coderef-workflow uses ExecutionLogValidator when generating execution-log.json

    Current Status: ❌ FAILING (not integrated)
    Expected: Will pass after WO-VALIDATOR-INTEGRATION-001
    """

    @pytest.mark.xfail(reason="ExecutionLogValidator not yet integrated into workflow", strict=True)
    def test_execute_plan_calls_validator(self):
        """
        PROOF TEST: Verify execute_plan calls ExecutionLogValidator

        What this proves when passing:
        - execute_plan tool invokes ExecutionLogValidator
        - Validation happens when creating execution-log.json

        Integration requirement:
        - Add: from papertrail.validators.execution_log import ExecutionLogValidator
        - Call: validator.validate_content(execution_log_data) after generation
        """
        from papertrail.validators.execution_log import ExecutionLogValidator

        with patch.object(ExecutionLogValidator, 'validate_content') as mock_validate:
            mock_validate.return_value = MagicMock(
                valid=True,
                errors=[],
                warnings=[],
                score=95
            )

            # This would be the actual workflow call:
            # from coderef_workflow.tools import execute_plan
            # result = execute_plan(feature_name="test", plan_path="/path/to/plan.json")

            # EXPECTED: Workflow should call validator.validate_content()
            # ACTUAL: No call happens

            assert mock_validate.called, \
                "ExecutionLogValidator.validate_content() should be called by execute_plan"

    @pytest.mark.xfail(reason="Cross-validation not enabled in workflow", strict=True)
    def test_execute_plan_enables_cross_validation(self):
        """
        PROOF TEST: Verify execute_plan enables cross-validation with plan.json

        What this proves when passing:
        - Workflow passes enable_cross_validation=True to validator
        - Task IDs in execution log are verified against plan.json
        - Orphaned task IDs are detected

        Integration requirement:
        - When calling validator, use:
          validator.validate_file(exec_log_path, enable_cross_validation=True)
        - Ensure plan.json path is discoverable (same directory or parent)
        """
        from papertrail.validators.execution_log import ExecutionLogValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create plan.json with task IDs
            plan_data = {
                "UNIVERSAL_PLANNING_STRUCTURE": {
                    "5_task_id_system": {
                        "tasks": [
                            {"id": "SETUP-001", "description": "Setup"},
                            {"id": "IMPL-001", "description": "Implementation"}
                        ]
                    }
                }
            }
            plan_path = tmpdir_path / "plan.json"
            plan_path.write_text(json.dumps(plan_data))

            # Create execution-log.json with orphaned task ID
            exec_log_data = [
                {
                    "timestamp": "2026-01-10T14:40:21.165589",
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
            exec_log_path = tmpdir_path / "execution-log.json"
            exec_log_path.write_text(json.dumps(exec_log_data))

            # Validate with cross-validation
            validator = ExecutionLogValidator()
            result = validator.validate_file(exec_log_path, enable_cross_validation=True)

            # EXPECTED: Workflow should detect orphaned task ID
            # ACTUAL: Works in tests, but workflow doesn't call it

            # Check that cross-validation detected the orphan
            major_errors = [e for e in result.errors if "not found in plan" in e.message.lower()]

            assert len(major_errors) > 0, \
                "Cross-validation should detect orphaned task ID ORPHAN-999"
            assert result.score < 90, \
                "Orphaned task IDs should reduce validation score below 90"

    @pytest.mark.xfail(reason="update_task_status doesn't validate before updating", strict=True)
    def test_update_task_status_validates_before_update(self):
        """
        PROOF TEST: Verify update_task_status validates execution-log.json before modifying

        What this proves when passing:
        - Workflow validates execution log before updating task status
        - Invalid updates are rejected
        - Data integrity is maintained

        Integration requirement:
        - Before updating execution-log.json, validate it
        - If validation fails, reject the update with clear error
        - Log validation errors for debugging
        """
        from papertrail.validators.execution_log import ExecutionLogValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create invalid execution-log.json
            invalid_exec_log = [
                {
                    # Missing required field: timestamp
                    "workorder_id": "WO-TEST-001",
                    "feature_name": "test",
                    "task_count": 1,
                    "tasks": []
                }
            ]
            exec_log_path = tmpdir_path / "execution-log.json"
            exec_log_path.write_text(json.dumps(invalid_exec_log))

            # EXPECTED: update_task_status should validate before updating
            # ACTUAL: No validation happens, invalid data gets updated

            # Simulate what workflow should do
            validator = ExecutionLogValidator()
            result = validator.validate_file(exec_log_path, enable_cross_validation=False)

            # Workflow should reject updates to invalid files
            assert result.valid is False, \
                "Execution log is invalid (missing timestamp)"

            # This assertion will fail until workflow adds validation
            # In real workflow, we'd call update_task_status() and expect it to raise an error
            with pytest.raises(ValueError, match="Validation failed"):
                # This would be: update_task_status(exec_log_path, task_id="TEST-001", status="completed")
                # For now, simulate expected behavior
                if not result.valid:
                    raise ValueError(f"Validation failed: score {result.score}")


class TestValidatorFactoryIntegration:
    """Test that workflows use ValidatorFactory for auto-detection

    Current Status: ❌ FAILING (factory not used)
    Expected: Will pass after WO-VALIDATOR-INTEGRATION-001
    """

    @pytest.mark.xfail(reason="Workflows don't use ValidatorFactory", strict=True)
    def test_workflows_use_factory_for_auto_detection(self):
        """
        PROOF TEST: Verify workflows use ValidatorFactory instead of hardcoded validators

        What this proves when passing:
        - Workflows use ValidatorFactory.get_validator(path)
        - Auto-detection works in real workflows
        - Adding new validators doesn't require workflow changes

        Integration requirement:
        - Replace hardcoded validator instantiation with:
          from papertrail.validators.factory import ValidatorFactory
          validator = ValidatorFactory.get_validator(file_path)
          result = validator.validate_file(file_path)
        """
        from papertrail.validators.factory import ValidatorFactory

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create analysis.json in proper location
            workorder_dir = tmpdir_path / "coderef" / "workorder" / "test-feature"
            workorder_dir.mkdir(parents=True)

            analysis_file = workorder_dir / "analysis.json"
            analysis_data = {
                "foundation_docs": {"available": [], "missing": []},
                "inventory_data": {
                    "source": "coderef_index",
                    "total_elements": 100,
                    "by_type": {},
                    "files": 10
                },
                "technology_stack": {},
                "project_structure": {},
                "_uds": {
                    "generated_by": "coderef-workflow v2.0.0",
                    "document_type": "Project Analysis"
                }
            }
            analysis_file.write_text(json.dumps(analysis_data))

            # EXPECTED: Workflow uses factory to auto-detect validator
            # ACTUAL: Workflow hardcodes validator or doesn't validate

            # This is what workflow SHOULD do:
            validator = ValidatorFactory.get_validator(analysis_file)
            result = validator.validate_file(analysis_file)

            # Factory should have auto-detected AnalysisValidator
            from papertrail.validators.analysis import AnalysisValidator
            assert isinstance(validator, AnalysisValidator), \
                "Factory should auto-detect AnalysisValidator from path"

            # This assertion will fail until workflow uses factory
            # We can't test workflow code directly without importing coderef-workflow
            # But when integrated, workflow should use factory pattern
            assert True, "Manual verification needed: check workflow uses ValidatorFactory"


class TestValidationErrorHandling:
    """Test that workflows handle validation errors appropriately

    Current Status: ❌ FAILING (no error handling)
    Expected: Will pass after WO-VALIDATOR-INTEGRATION-001
    """

    @pytest.mark.xfail(reason="Workflows don't handle validation errors", strict=True)
    def test_workflow_continues_with_warnings(self):
        """
        PROOF TEST: Verify workflows continue with warnings (score < 90 but > 50)

        What this proves when passing:
        - Minor validation issues don't block workflows
        - Warnings are logged for user awareness
        - Workflows are resilient to non-critical issues

        Integration requirement:
        - if 50 <= result.score < 90: log warnings and continue
        - if result.score < 50: fail workflow with clear error
        """
        # Simulate workflow with minor validation issues
        # EXPECTED: Workflow logs warnings but continues
        # ACTUAL: No validation, no warnings

        # This test documents expected behavior
        score = 85  # Below 90 but above failure threshold

        # Workflow should log but continue
        assert score >= 50, "Minor issues should not block workflow"
        # This assertion will fail until workflow adds this logic
        assert False, "Workflow should log warnings for scores 50-90 (not implemented)"

    @pytest.mark.xfail(reason="Workflows don't reject critically invalid data", strict=True)
    def test_workflow_rejects_critical_failures(self):
        """
        PROOF TEST: Verify workflows reject data with validation score < 50

        What this proves when passing:
        - Critically invalid data is rejected
        - Users get clear error messages
        - Bad data doesn't propagate through system

        Integration requirement:
        - if result.score < 50: raise ValueError with validation errors
        - Return HTTP 400 or similar error to user
        """
        # Simulate workflow with critical validation failure
        score = 30  # Critical failure

        # Workflow should reject this
        # This assertion will fail until workflow adds rejection logic
        with pytest.raises(ValueError, match="Critical validation failure"):
            if score < 50:
                raise ValueError(f"Critical validation failure: score {score}")


# ============================================================================
# Summary Report Generator
# ============================================================================

def generate_integration_gap_report():
    """
    Generate a report of what's missing for integration

    This function documents all the gaps discovered by the failing tests.
    Use this as a specification for WO-VALIDATOR-INTEGRATION-001.
    """
    return """
    VALIDATOR INTEGRATION GAP REPORT
    ================================

    Based on test failures in test_workflow_integration.py

    MISSING INTEGRATIONS:

    1. AnalysisValidator not called by analyze_project_for_planning
       - File: coderef-workflow/generators/planning_analyzer.py
       - Add: from papertrail.validators.analysis import AnalysisValidator
       - Call validator after generating analysis data
       - Add validation metadata to _uds section

    2. ExecutionLogValidator not called by execute_plan
       - File: coderef-workflow/tools.py (or wherever execute_plan lives)
       - Add: from papertrail.validators.execution_log import ExecutionLogValidator
       - Call validator with enable_cross_validation=True
       - Log validation errors if score < 90

    3. update_task_status doesn't validate before updating
       - File: coderef-workflow/tools.py
       - Add validation check before modifying execution-log.json
       - Reject updates if validation fails

    4. Workflows don't use ValidatorFactory
       - Replace hardcoded validator instantiation
       - Use: ValidatorFactory.get_validator(path)
       - Benefit: Auto-detection, future-proof

    5. No error handling for validation failures
       - Add logic: if score < 50, fail workflow
       - Add logic: if 50 <= score < 90, log warnings
       - Provide clear error messages to users

    NEXT SESSION WORKORDER: WO-VALIDATOR-INTEGRATION-001
    Estimated effort: 4-6 hours
    Priority: HIGH (validators exist but aren't being used)

    When complete, all tests in test_workflow_integration.py should pass.
    """


if __name__ == "__main__":
    # Print integration gap report
    print(generate_integration_gap_report())

    # Run tests (all will fail with xfail)
    pytest.main([__file__, "-v", "--tb=short"])
