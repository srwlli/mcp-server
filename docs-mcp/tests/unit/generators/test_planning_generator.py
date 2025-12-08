"""
Unit tests for PlanningGenerator.

Tests the planning generator including:
- Feature name validation and sanitization
- Context and analysis loading
- Template loading
- Plan generation (complete and partial)
- Plan saving

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import pytest
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from generators.planning_generator import PlanningGenerator


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestPlanningGeneratorInit:
    """Tests for PlanningGenerator initialization."""

    def test_init_with_valid_path(self, mock_project):
        """Test initialization with valid project path."""
        generator = PlanningGenerator(mock_project)

        assert generator.project_path == mock_project

    def test_init_sets_template_path(self, mock_project):
        """Test that initialization sets template path correctly."""
        generator = PlanningGenerator(mock_project)

        assert generator.template_file is not None
        assert "planning-template-for-ai.json" in str(generator.template_file)

    def test_init_context_dir_in_server_root(self, mock_project):
        """Test that context_dir points to server root, not project."""
        generator = PlanningGenerator(mock_project)

        # Should NOT be in mock_project directory
        assert mock_project not in generator.context_dir.parents


# ============================================================================
# FEATURE NAME VALIDATION TESTS
# ============================================================================

class TestValidateFeatureName:
    """Tests for validate_feature_name method."""

    def test_valid_simple_name(self, planning_generator):
        """Test validation of simple valid name."""
        assert planning_generator.validate_feature_name("feature") == "feature"

    def test_valid_name_with_hyphen(self, planning_generator):
        """Test validation of name with hyphens."""
        assert planning_generator.validate_feature_name("auth-system") == "auth-system"

    def test_valid_name_with_underscore(self, planning_generator):
        """Test validation of name with underscores."""
        assert planning_generator.validate_feature_name("user_profile") == "user_profile"

    def test_valid_name_with_numbers(self, planning_generator):
        """Test validation of name with numbers."""
        assert planning_generator.validate_feature_name("feature123") == "feature123"
        assert planning_generator.validate_feature_name("v2") == "v2"

    def test_valid_alphanumeric_mix(self, planning_generator):
        """Test validation of mixed alphanumeric names."""
        assert planning_generator.validate_feature_name("API-v2") == "API-v2"
        assert planning_generator.validate_feature_name("create-plan") == "create-plan"

    def test_invalid_path_traversal_parent(self, planning_generator):
        """Test rejection of parent directory traversal."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("../parent")

    def test_invalid_path_traversal_deep(self, planning_generator):
        """Test rejection of deep path traversal."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("../../etc/passwd")

    def test_invalid_path_traversal_mixed(self, planning_generator):
        """Test rejection of mixed path traversal."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("feature/../secret")

    def test_invalid_dot_only(self, planning_generator):
        """Test rejection of dot-only names."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name(".")
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("..")

    def test_invalid_forward_slash(self, planning_generator):
        """Test rejection of forward slash."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("feature/name")

    def test_invalid_backslash(self, planning_generator):
        """Test rejection of backslash."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("feature\\name")

    def test_invalid_space(self, planning_generator):
        """Test rejection of space."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("feature name")

    def test_invalid_special_characters(self, planning_generator):
        """Test rejection of special characters."""
        invalid_names = ["feature@name", "feature$name", "feature!name", "feature#name"]
        for name in invalid_names:
            with pytest.raises(ValueError, match="Invalid feature name"):
                planning_generator.validate_feature_name(name)

    def test_invalid_empty_string(self, planning_generator):
        """Test rejection of empty string."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.validate_feature_name("")

    def test_invalid_none(self, planning_generator):
        """Test rejection of None."""
        with pytest.raises(ValueError):
            planning_generator.validate_feature_name(None)


# ============================================================================
# LOAD CONTEXT TESTS
# ============================================================================

class TestLoadContext:
    """Tests for load_context method."""

    def test_load_context_missing_file(self, planning_generator):
        """Test loading context when file doesn't exist."""
        result = planning_generator.load_context("nonexistent-feature")
        assert result is None

    def test_load_context_valid_file(self, mock_project):
        """Test loading valid context.json."""
        generator = PlanningGenerator(mock_project)

        # Create context file
        feature_name = "test-feature"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)

        test_context = {
            "feature_name": feature_name,
            "description": "Test feature description",
            "requirements": ["req1", "req2"]
        }
        (working_dir / "context.json").write_text(json.dumps(test_context))

        result = generator.load_context(feature_name)

        assert result is not None
        assert result["feature_name"] == feature_name
        assert "requirements" in result

    def test_load_context_malformed_json(self, mock_project):
        """Test loading malformed context.json raises error."""
        generator = PlanningGenerator(mock_project)

        # Create malformed context file
        feature_name = "malformed-feature"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)
        (working_dir / "context.json").write_text("{invalid json}")

        with pytest.raises(ValueError, match="malformed JSON"):
            generator.load_context(feature_name)


# ============================================================================
# LOAD ANALYSIS TESTS
# ============================================================================

class TestLoadAnalysis:
    """Tests for load_analysis method."""

    def test_load_analysis_no_feature_name(self, planning_generator):
        """Test load_analysis returns None when no feature name."""
        result = planning_generator.load_analysis()
        assert result is None

    def test_load_analysis_missing_file(self, planning_generator):
        """Test load_analysis returns None when file doesn't exist."""
        result = planning_generator.load_analysis("nonexistent-feature")
        assert result is None

    def test_load_analysis_valid_file(self, mock_project):
        """Test loading valid analysis.json."""
        generator = PlanningGenerator(mock_project)

        # Create analysis file
        feature_name = "test-feature"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)

        test_analysis = {
            "foundation_docs": {"available": ["README.md"]},
            "technology_stack": {"language": "Python"}
        }
        (working_dir / "analysis.json").write_text(json.dumps(test_analysis))

        result = generator.load_analysis(feature_name)

        assert result is not None
        assert "foundation_docs" in result
        assert "technology_stack" in result

    def test_load_analysis_malformed_json(self, mock_project):
        """Test load_analysis returns None for malformed JSON."""
        generator = PlanningGenerator(mock_project)

        # Create malformed analysis file
        feature_name = "malformed-analysis"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)
        (working_dir / "analysis.json").write_text("{bad json")

        result = generator.load_analysis(feature_name)
        # Should return None, not raise error
        assert result is None


# ============================================================================
# LOAD TEMPLATE TESTS
# ============================================================================

class TestLoadTemplate:
    """Tests for load_template method."""

    def test_load_template_returns_dict(self, planning_generator):
        """Test that load_template returns a dictionary."""
        try:
            template = planning_generator.load_template()
            assert isinstance(template, dict)
        except FileNotFoundError:
            pytest.skip("AI template not found in test environment")

    def test_load_template_has_structure(self, planning_generator):
        """Test that template has expected structure."""
        try:
            template = planning_generator.load_template()
            # Should have AI instructions or required sections
            has_expected_keys = '_AI_INSTRUCTIONS' in template or 'REQUIRED_SECTIONS' in template
            assert has_expected_keys
        except FileNotFoundError:
            pytest.skip("AI template not found in test environment")

    def test_load_template_missing_file(self, mock_project):
        """Test load_template raises error when file doesn't exist."""
        generator = PlanningGenerator(mock_project)
        # Override template path to non-existent file
        generator.template_file = mock_project / "nonexistent-template.json"

        with pytest.raises(FileNotFoundError):
            generator.load_template()


# ============================================================================
# GENERATE PLAN TESTS
# ============================================================================

class TestGeneratePlan:
    """Tests for generate_plan method."""

    def test_generate_plan_validates_feature_name(self, planning_generator):
        """Test that generate_plan validates feature name."""
        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.generate_plan("../invalid")

    def test_generate_plan_structure(self, planning_generator):
        """Test generated plan has correct structure."""
        try:
            plan = planning_generator.generate_plan("test-feature")

            assert "META_DOCUMENTATION" in plan
            assert "UNIVERSAL_PLANNING_STRUCTURE" in plan
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise

    def test_generate_plan_meta_documentation(self, planning_generator):
        """Test META_DOCUMENTATION section."""
        try:
            plan = planning_generator.generate_plan("test-feature")

            meta = plan["META_DOCUMENTATION"]
            assert "feature_name" in meta
            assert meta["feature_name"] == "test-feature"
            assert "status" in meta
            assert "generated_by" in meta
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise

    def test_generate_plan_all_sections_present(self, planning_generator):
        """Test all 10 sections are present."""
        try:
            plan = planning_generator.generate_plan("test-feature")

            sections = plan["UNIVERSAL_PLANNING_STRUCTURE"]
            expected_sections = [
                "0_preparation",
                "1_executive_summary",
                "2_risk_assessment",
                "3_current_state_analysis",
                "4_key_features",
                "5_task_id_system",
                "6_implementation_phases",
                "7_testing_strategy",
                "8_success_criteria",
                "9_implementation_checklist"
            ]

            for section in expected_sections:
                assert section in sections, f"Missing section: {section}"
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise

    def test_generate_plan_with_context(self, mock_project, sample_context_json):
        """Test plan generation with provided context."""
        generator = PlanningGenerator(mock_project)

        # Create context file
        feature_name = sample_context_json["feature_name"]
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)
        (working_dir / "context.json").write_text(json.dumps(sample_context_json))

        try:
            plan = generator.generate_plan(feature_name)

            meta = plan["META_DOCUMENTATION"]
            assert meta.get("has_context") is True
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise


# ============================================================================
# INTERNAL SECTION GENERATION TESTS
# ============================================================================

class TestGeneratePreparationSection:
    """Tests for _generate_preparation_section method."""

    def test_with_analysis(self, planning_generator):
        """Test preparation section with analysis data."""
        analysis = {
            "preparation_summary": {
                "foundation_docs": {"available": ["README.md"]}
            }
        }

        result = planning_generator._generate_preparation_section(None, analysis)

        assert result == analysis["preparation_summary"]

    def test_without_analysis(self, planning_generator):
        """Test preparation section without analysis."""
        result = planning_generator._generate_preparation_section(None, None)

        assert "foundation_docs" in result
        assert "coding_standards" in result
        assert "gaps_and_risks" in result


class TestGenerateExecutiveSummary:
    """Tests for _generate_executive_summary method."""

    def test_with_context(self, planning_generator, sample_context_json):
        """Test executive summary with context."""
        result = planning_generator._generate_executive_summary(
            "test-feature",
            sample_context_json
        )

        assert "purpose" in result
        assert sample_context_json["description"] in result["purpose"]

    def test_without_context(self, planning_generator):
        """Test executive summary without context."""
        result = planning_generator._generate_executive_summary("test-feature", None)

        assert "purpose" in result
        assert "test-feature" in result["purpose"]
        assert "TODO" in result.get("value_proposition", "")


class TestGenerateRiskAssessment:
    """Tests for _generate_risk_assessment method."""

    def test_returns_dict(self, planning_generator):
        """Test risk assessment returns dictionary."""
        result = planning_generator._generate_risk_assessment(None, None)

        assert isinstance(result, dict)
        assert "overall_risk" in result
        assert "complexity" in result

    def test_with_context_constraints(self, planning_generator, sample_context_json):
        """Test risk assessment includes context constraints."""
        result = planning_generator._generate_risk_assessment(sample_context_json, None)

        assert "dependencies" in result
        assert result["dependencies"] == sample_context_json["constraints"]


class TestGenerateKeyFeatures:
    """Tests for _generate_key_features method."""

    def test_with_requirements(self, planning_generator, sample_context_json):
        """Test key features extracts requirements."""
        result = planning_generator._generate_key_features(sample_context_json)

        assert "primary_features" in result
        # Should contain requirements
        assert len(result["primary_features"]) > 0

    def test_without_context(self, planning_generator):
        """Test key features without context has TODOs."""
        result = planning_generator._generate_key_features(None)

        assert "primary_features" in result
        assert any("TODO" in str(item) for item in result["primary_features"])


class TestGenerateTasks:
    """Tests for _generate_tasks method."""

    def test_returns_task_structure(self, planning_generator):
        """Test tasks returns proper structure."""
        result = planning_generator._generate_tasks(None, None)

        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) > 0


class TestGeneratePhases:
    """Tests for _generate_phases method."""

    def test_returns_phases_list(self, planning_generator):
        """Test phases returns list of phases."""
        result = planning_generator._generate_phases()

        assert "phases" in result
        assert isinstance(result["phases"], list)
        assert len(result["phases"]) >= 3  # At least 3 phases

    def test_phases_have_required_fields(self, planning_generator):
        """Test each phase has required fields."""
        result = planning_generator._generate_phases()

        for phase in result["phases"]:
            assert "title" in phase
            assert "purpose" in phase
            assert "tasks" in phase


class TestGenerateTestingStrategy:
    """Tests for _generate_testing_strategy method."""

    def test_returns_testing_sections(self, planning_generator):
        """Test testing strategy has expected sections."""
        result = planning_generator._generate_testing_strategy()

        assert "unit_tests" in result
        assert "integration_tests" in result
        assert "edge_case_scenarios" in result


class TestGenerateSuccessCriteria:
    """Tests for _generate_success_criteria method."""

    def test_returns_requirements(self, planning_generator):
        """Test success criteria has requirement categories."""
        result = planning_generator._generate_success_criteria(None)

        assert "functional_requirements" in result
        assert "quality_requirements" in result

    def test_quality_requirements_has_coverage(self, planning_generator):
        """Test quality requirements include coverage target."""
        result = planning_generator._generate_success_criteria(None)

        quality_reqs = result["quality_requirements"]
        assert len(quality_reqs) > 0
        coverage_req = quality_reqs[0]
        assert "coverage" in coverage_req.get("requirement", "").lower() or \
               "coverage" in coverage_req.get("metric", "").lower()


class TestGenerateChecklist:
    """Tests for _generate_checklist method."""

    def test_returns_checklist_sections(self, planning_generator):
        """Test checklist has phase sections."""
        result = planning_generator._generate_checklist()

        assert "pre_implementation" in result
        assert "phase_1" in result
        assert "finalization" in result

    def test_checklist_items_are_lists(self, planning_generator):
        """Test checklist items are lists."""
        result = planning_generator._generate_checklist()

        for key, value in result.items():
            assert isinstance(value, list)


# ============================================================================
# PARTIAL PLAN TESTS
# ============================================================================

class TestCreatePartialPlan:
    """Tests for _create_partial_plan method."""

    def test_creates_partial_structure(self, planning_generator):
        """Test partial plan has correct structure."""
        result = planning_generator._create_partial_plan("test-feature", "Test error")

        assert "META_DOCUMENTATION" in result
        assert "UNIVERSAL_PLANNING_STRUCTURE" in result

    def test_partial_status_is_partial(self, planning_generator):
        """Test partial plan has 'partial' status."""
        result = planning_generator._create_partial_plan("test-feature", "Test error")

        assert result["META_DOCUMENTATION"]["status"] == "partial"

    def test_partial_includes_error(self, planning_generator):
        """Test partial plan includes error message."""
        error_msg = "Generation failed: test error"
        result = planning_generator._create_partial_plan("test-feature", error_msg)

        assert result["META_DOCUMENTATION"]["error"] == error_msg

    def test_partial_sections_have_todo(self, planning_generator):
        """Test partial plan sections have TODO markers."""
        result = planning_generator._create_partial_plan("test-feature", "error")

        sections = result["UNIVERSAL_PLANNING_STRUCTURE"]
        for section_name, section_data in sections.items():
            assert isinstance(section_data, dict)
            assert "status" in section_data or "note" in section_data


# ============================================================================
# SAVE PLAN TESTS
# ============================================================================

class TestSavePlan:
    """Tests for save_plan method."""

    def test_save_plan_creates_file(self, mock_project):
        """Test save_plan creates plan.json file."""
        generator = PlanningGenerator(mock_project)

        test_plan = {
            "META_DOCUMENTATION": {"feature_name": "test-feature"},
            "UNIVERSAL_PLANNING_STRUCTURE": {}
        }

        result = generator.save_plan("test-feature", test_plan)

        assert Path(result).exists()
        assert Path(result).name == "plan.json"

    def test_save_plan_creates_directory(self, mock_project):
        """Test save_plan creates working directory if needed."""
        generator = PlanningGenerator(mock_project)

        test_plan = {"META_DOCUMENTATION": {}}

        # Remove working dir if exists
        working_dir = mock_project / "coderef" / "working" / "new-feature"
        if working_dir.exists():
            import shutil
            shutil.rmtree(working_dir)

        result = generator.save_plan("new-feature", test_plan)

        assert Path(result).parent.exists()

    def test_save_plan_content_matches(self, mock_project):
        """Test saved plan content matches original."""
        generator = PlanningGenerator(mock_project)

        test_plan = {
            "META_DOCUMENTATION": {
                "feature_name": "test-feature",
                "version": "1.0.0"
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "test_section": {"data": "test"}
            }
        }

        result = generator.save_plan("test-feature", test_plan)

        saved_plan = json.loads(Path(result).read_text())
        assert saved_plan == test_plan

    def test_save_plan_validates_feature_name(self, planning_generator):
        """Test save_plan validates feature name."""
        test_plan = {"META_DOCUMENTATION": {}}

        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.save_plan("../invalid", test_plan)

    def test_save_plan_returns_absolute_path(self, mock_project):
        """Test save_plan returns absolute path."""
        generator = PlanningGenerator(mock_project)

        test_plan = {"META_DOCUMENTATION": {}}

        result = generator.save_plan("test-feature", test_plan)

        assert Path(result).is_absolute()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPlanningGeneratorIntegration:
    """Integration tests for PlanningGenerator."""

    def test_full_workflow_without_context(self, planning_generator):
        """Test full workflow without context files."""
        try:
            # Generate plan
            plan = planning_generator.generate_plan("integration-test")

            # Save plan
            plan_path = planning_generator.save_plan("integration-test", plan)

            # Verify saved file
            assert Path(plan_path).exists()

            # Load and verify content
            saved_plan = json.loads(Path(plan_path).read_text())
            assert saved_plan["META_DOCUMENTATION"]["feature_name"] == "integration-test"
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise

    def test_full_workflow_with_context(self, mock_project, sample_context_json):
        """Test full workflow with context file."""
        generator = PlanningGenerator(mock_project)
        feature_name = "full-workflow-test"

        # Create context file
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)
        sample_context_json["feature_name"] = feature_name
        (working_dir / "context.json").write_text(json.dumps(sample_context_json))

        try:
            # Generate plan (loads context automatically)
            plan = generator.generate_plan(feature_name)

            assert plan["META_DOCUMENTATION"]["has_context"] is True

            # Save plan
            plan_path = generator.save_plan(feature_name, plan)

            # Verify
            saved_plan = json.loads(Path(plan_path).read_text())
            assert saved_plan["META_DOCUMENTATION"]["has_context"] is True
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestPlanningGeneratorSecurity:
    """Security tests for PlanningGenerator."""

    def test_path_traversal_in_validate(self, planning_generator):
        """Test path traversal prevention in validation."""
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "feature/../../../secret",
            "/etc/passwd",
        ]

        for name in dangerous_names:
            with pytest.raises(ValueError, match="Invalid feature name"):
                planning_generator.validate_feature_name(name)

    def test_path_traversal_in_save_plan(self, planning_generator):
        """Test path traversal prevention when saving."""
        test_plan = {"META_DOCUMENTATION": {}}

        with pytest.raises(ValueError, match="Invalid feature name"):
            planning_generator.save_plan("../../malicious", test_plan)

    def test_path_traversal_in_load_context(self, mock_project):
        """Test path traversal prevention when loading context."""
        generator = PlanningGenerator(mock_project)

        # This should just return None (file not found) rather than access parent
        result = generator.load_context("../../../etc/passwd")
        # Should not raise, just return None (path won't exist)
        assert result is None


# ============================================================================
# EDGE CASES
# ============================================================================

class TestPlanningGeneratorEdgeCases:
    """Edge case tests for PlanningGenerator."""

    def test_unicode_in_context(self, mock_project):
        """Test handling of Unicode in context."""
        generator = PlanningGenerator(mock_project)

        feature_name = "unicode-test"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)

        unicode_context = {
            "feature_name": feature_name,
            "description": "Description with 日本語 and émojis"
        }
        (working_dir / "context.json").write_text(
            json.dumps(unicode_context, ensure_ascii=False),
            encoding='utf-8'
        )

        result = generator.load_context(feature_name)
        assert "日本語" in result["description"]

    def test_empty_context_file(self, mock_project):
        """Test handling of empty context file."""
        generator = PlanningGenerator(mock_project)

        feature_name = "empty-context"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)
        (working_dir / "context.json").write_text("")

        with pytest.raises(ValueError, match="malformed JSON"):
            generator.load_context(feature_name)

    def test_large_plan_save(self, mock_project):
        """Test saving large plan."""
        generator = PlanningGenerator(mock_project)

        # Create large plan with many tasks
        large_plan = {
            "META_DOCUMENTATION": {"feature_name": "large-plan"},
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "tasks": [f"TASK-{i:03d}: Task description {i}" for i in range(100)]
                }
            }
        }

        result = generator.save_plan("large-plan", large_plan)

        saved_plan = json.loads(Path(result).read_text())
        assert len(saved_plan["UNIVERSAL_PLANNING_STRUCTURE"]["5_task_id_system"]["tasks"]) == 100


# ============================================================================
# PERFORMANCE TESTS (marked for selective running)
# ============================================================================

@pytest.mark.slow
class TestPlanningGeneratorPerformance:
    """Performance tests for PlanningGenerator."""

    def test_plan_generation_performance(self, planning_generator):
        """Test that plan generation completes quickly."""
        import time

        try:
            start = time.time()
            planning_generator.generate_plan("perf-test")
            duration = time.time() - start

            # Should complete in under 1 second
            assert duration < 1.0
        except (FileNotFoundError, ValueError) as e:
            if "template" in str(e).lower():
                pytest.skip("AI template not found")
            raise

    def test_context_loading_performance(self, mock_project):
        """Test context loading is fast."""
        import time

        generator = PlanningGenerator(mock_project)

        # Create context file
        feature_name = "perf-test"
        working_dir = mock_project / "coderef" / "working" / feature_name
        working_dir.mkdir(parents=True)
        (working_dir / "context.json").write_text(json.dumps({"test": "data"}))

        start = time.time()
        for _ in range(100):
            generator.load_context(feature_name)
        duration = time.time() - start

        # 100 loads should complete in under 1 second
        assert duration < 1.0
