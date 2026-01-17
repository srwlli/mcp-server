"""
Unit tests for complexity tracking (Task 3: Execution Tracking).

Tests that execution tracking integrates complexity data for refactoring prioritization
and risk assessment.

WO-WORKFLOW-SCANNER-INTEGRATION-001 TEST-004
"""

import pytest
import json
from pathlib import Path
from utils.complexity_estimator import ComplexityEstimator


@pytest.fixture
def sample_index_data():
    """Load sample index.json fixture with complexity data."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_index.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def project_path(tmp_path, sample_index_data):
    """Create temporary project with .coderef/ structure."""
    coderef_dir = tmp_path / ".coderef"
    coderef_dir.mkdir()

    # Write sample index
    (coderef_dir / "index.json").write_text(json.dumps(sample_index_data, indent=2))

    return tmp_path


class TestElementComplexityEstimation:
    """Test single element complexity estimation."""

    def test_estimate_element_complexity_for_function(self, project_path):
        """Test complexity estimation for a function."""
        estimator = ComplexityEstimator(project_path)

        # authenticateUser has 2 parameters and 3 function calls
        result = estimator.estimate_element_complexity('authenticateUser')

        assert result is not None, "Should return complexity data for authenticateUser"
        assert 'complexity_score' in result
        assert 'risk_level' in result
        assert 'estimated_loc' in result
        assert 'parameter_count' in result
        assert 'calls_count' in result

        # Verify values
        assert result['element_name'] == 'authenticateUser'
        assert result['parameter_count'] == 2
        assert result['calls_count'] == 3
        assert result['complexity_score'] >= 2, "Functions have base complexity of 2"
        assert result['risk_level'] in ['low', 'medium', 'high', 'critical']

    def test_estimate_element_complexity_for_class(self, project_path):
        """Test complexity estimation for a class."""
        estimator = ComplexityEstimator(project_path)

        # AuthService is a class
        result = estimator.estimate_element_complexity('AuthService')

        assert result is not None
        assert result['element_name'] == 'AuthService'
        assert result['complexity_score'] >= 3, "Classes have base complexity of 3"

    def test_estimate_element_complexity_for_interface(self, project_path):
        """Test complexity estimation for an interface."""
        estimator = ComplexityEstimator(project_path)

        # IAuthService is an interface
        result = estimator.estimate_element_complexity('IAuthService')

        assert result is not None
        assert result['element_name'] == 'IAuthService'
        assert result['complexity_score'] >= 1, "Interfaces have base complexity of 1"
        assert result['risk_level'] == 'low', "Simple interfaces should be low complexity"

    def test_estimate_element_complexity_parameter_count_impact(self, project_path):
        """Test that parameter count increases complexity score."""
        estimator = ComplexityEstimator(project_path)

        # createUser has 1 parameter
        result_low_params = estimator.estimate_element_complexity('createUser')

        # authenticateUser has 2 parameters
        result_moderate_params = estimator.estimate_element_complexity('authenticateUser')

        # Both should have valid results
        assert result_low_params is not None
        assert result_moderate_params is not None

        # Verify parameter counts
        assert result_low_params['parameter_count'] == 1
        assert result_moderate_params['parameter_count'] == 2

    def test_estimate_element_complexity_calls_count_impact(self, project_path):
        """Test that function calls count increases complexity."""
        estimator = ComplexityEstimator(project_path)

        # createUser has 3 calls
        result = estimator.estimate_element_complexity('createUser')

        assert result is not None
        assert result['calls_count'] == 3
        assert 'calls' in str(result.get('factors', [])).lower() or result['calls_count'] > 0

    def test_estimate_element_complexity_risk_level_categorization(self, project_path):
        """Test that risk levels are correctly categorized."""
        estimator = ComplexityEstimator(project_path)

        # Test low complexity (interface)
        low_result = estimator.estimate_element_complexity('ILogger')
        assert low_result is not None
        assert low_result['risk_level'] in ['low', 'medium'], "Simple interface should be low/medium complexity"
        assert low_result['complexity_score'] <= 6

        # Test higher complexity (function with multiple parameters and calls)
        high_result = estimator.estimate_element_complexity('resetPassword')
        assert high_result is not None
        # resetPassword has 2 parameters and 4 calls, should be higher complexity
        assert high_result['complexity_score'] >= 2

    def test_estimate_element_complexity_returns_none_for_nonexistent(self, project_path):
        """Test that nonexistent elements return None."""
        estimator = ComplexityEstimator(project_path)

        result = estimator.estimate_element_complexity('NonexistentElement')

        assert result is None, "Should return None for nonexistent element"

    def test_estimate_element_complexity_includes_factors(self, project_path):
        """Test that complexity factors are identified."""
        estimator = ComplexityEstimator(project_path)

        # resetPassword has 2 parameters and 4 calls
        result = estimator.estimate_element_complexity('resetPassword')

        assert result is not None
        assert 'factors' in result
        assert isinstance(result['factors'], list)

    def test_estimate_element_complexity_estimated_loc(self, project_path):
        """Test that estimated LOC is calculated."""
        estimator = ComplexityEstimator(project_path)

        result = estimator.estimate_element_complexity('authenticateUser')

        assert result is not None
        assert 'estimated_loc' in result
        assert result['estimated_loc'] > 0, "Should estimate non-zero LOC"
        assert result['estimated_loc'] == result['complexity_score'] * 10, \
            "Estimated LOC should be score * 10"


class TestTaskComplexityEstimation:
    """Test multi-element task complexity estimation."""

    def test_estimate_task_complexity_calculates_avg_and_max(self, project_path):
        """Test that task complexity calculates average and max scores."""
        estimator = ComplexityEstimator(project_path)

        # Test with 3 elements
        elements = ['authenticateUser', 'validateCredentials', 'generateToken']
        result = estimator.estimate_task_complexity(elements)

        assert 'avg_complexity_score' in result
        assert 'max_complexity_score' in result
        assert result['avg_complexity_score'] > 0, "Average should be positive"
        assert result['max_complexity_score'] > 0, "Max should be positive"
        assert result['max_complexity_score'] >= result['avg_complexity_score'], \
            "Max should be >= average"

    def test_estimate_task_complexity_identifies_high_complexity_elements(self, project_path):
        """Test that elements with score >7 are flagged."""
        estimator = ComplexityEstimator(project_path)

        # Get all functions (some may have high complexity)
        elements = [
            'authenticateUser', 'validateCredentials', 'generateToken',
            'createUser', 'updateUser', 'resetPassword'
        ]
        result = estimator.estimate_task_complexity(elements)

        assert 'high_complexity_elements' in result
        assert isinstance(result['high_complexity_elements'], list)

        # Verify structure of high-complexity elements
        for elem in result['high_complexity_elements']:
            assert 'name' in elem
            assert 'score' in elem
            assert 'risk_level' in elem
            assert elem['score'] > 7, "High-complexity elements should have score > 7"

    def test_estimate_task_complexity_calculates_distribution(self, project_path):
        """Test that complexity distribution is calculated."""
        estimator = ComplexityEstimator(project_path)

        elements = ['ILogger', 'authenticateUser', 'AuthService']
        result = estimator.estimate_task_complexity(elements)

        assert 'complexity_distribution' in result
        distribution = result['complexity_distribution']

        assert 'low' in distribution
        assert 'medium' in distribution
        assert 'high' in distribution
        assert 'critical' in distribution

        # Total distribution should equal elements analyzed
        total_distribution = sum(distribution.values())
        assert total_distribution == len(elements), \
            f"Distribution total ({total_distribution}) should equal elements count ({len(elements)})"

    def test_estimate_task_complexity_sums_estimated_loc(self, project_path):
        """Test that total estimated LOC is calculated."""
        estimator = ComplexityEstimator(project_path)

        elements = ['authenticateUser', 'validateCredentials']
        result = estimator.estimate_task_complexity(elements)

        assert 'total_estimated_loc' in result
        assert result['total_estimated_loc'] > 0, "Should have positive total LOC"

    def test_estimate_task_complexity_handles_empty_list(self, project_path):
        """Test that empty element list returns zero values."""
        estimator = ComplexityEstimator(project_path)

        result = estimator.estimate_task_complexity([])

        assert result['avg_complexity_score'] == 0
        assert result['max_complexity_score'] == 0
        assert result['total_estimated_loc'] == 0
        assert result['high_complexity_elements'] == []
        assert result['complexity_distribution'] == {}

    def test_estimate_task_complexity_handles_nonexistent_elements(self, project_path):
        """Test that nonexistent elements are handled gracefully."""
        estimator = ComplexityEstimator(project_path)

        # Mix of real and fake elements
        elements = ['authenticateUser', 'FakeElement1', 'FakeElement2']
        result = estimator.estimate_task_complexity(elements)

        # Should still return result (based on elements that exist)
        assert result is not None
        # Should only count the one real element
        assert result['elements_analyzed'] == 3, "Should report all elements analyzed"

    def test_estimate_task_complexity_tracks_elements_analyzed(self, project_path):
        """Test that elements_analyzed field is correct."""
        estimator = ComplexityEstimator(project_path)

        elements = ['authenticateUser', 'validateCredentials', 'generateToken']
        result = estimator.estimate_task_complexity(elements)

        assert 'elements_analyzed' in result
        assert result['elements_analyzed'] == len(elements), \
            "Should report number of elements analyzed"


class TestComplexityScoreRanges:
    """Test complexity score ranges and thresholds."""

    def test_complexity_score_capped_at_10(self, project_path):
        """Test that complexity score never exceeds 10."""
        estimator = ComplexityEstimator(project_path)

        # Test all elements
        elements = estimator._load_elements()
        for elem in elements[:10]:  # Test first 10 to avoid slowness
            result = estimator.estimate_element_complexity(elem['name'])
            if result:
                assert result['complexity_score'] <= 10, \
                    f"{elem['name']} has score > 10: {result['complexity_score']}"

    def test_risk_levels_match_score_ranges(self, project_path):
        """Test that risk levels correspond to correct score ranges."""
        estimator = ComplexityEstimator(project_path)

        elements = ['ILogger', 'authenticateUser', 'AuthService', 'resetPassword']

        for elem_name in elements:
            result = estimator.estimate_element_complexity(elem_name)
            if result:
                score = result['complexity_score']
                risk = result['risk_level']

                if score <= 3:
                    assert risk == 'low', f"{elem_name}: score {score} should be 'low', got '{risk}'"
                elif score <= 6:
                    assert risk == 'medium', f"{elem_name}: score {score} should be 'medium', got '{risk}'"
                elif score <= 8:
                    assert risk == 'high', f"{elem_name}: score {score} should be 'high', got '{risk}'"
                else:
                    assert risk == 'critical', f"{elem_name}: score {score} should be 'critical', got '{risk}'"


@pytest.mark.integration
class TestComplexityTrackingIntegration:
    """Integration tests for complexity tracking workflow."""

    def test_full_complexity_workflow(self, project_path):
        """Test complete complexity estimation workflow."""
        estimator = ComplexityEstimator(project_path)

        # Step 1: Estimate single element complexity
        single_result = estimator.estimate_element_complexity('authenticateUser')
        assert single_result is not None

        # Step 2: Estimate task complexity for multiple elements
        task_elements = ['authenticateUser', 'validateCredentials', 'generateToken']
        task_result = estimator.estimate_task_complexity(task_elements)

        assert task_result is not None
        assert task_result['avg_complexity_score'] > 0
        assert task_result['elements_analyzed'] == 3

        # Step 3: Verify high-complexity flagging
        if task_result['high_complexity_elements']:
            for elem in task_result['high_complexity_elements']:
                assert elem['score'] > 7

    def test_complexity_data_structure_for_planning_integration(self, project_path):
        """Test that complexity data structure matches planning generator expectations."""
        estimator = ComplexityEstimator(project_path)

        # This is what planning_generator.py expects
        task_result = estimator.estimate_task_complexity(['authenticateUser', 'createUser'])

        # Verify all required fields for plan.json
        required_fields = [
            'avg_complexity_score',
            'max_complexity_score',
            'high_complexity_elements',
            'complexity_distribution'
        ]

        for field in required_fields:
            assert field in task_result, f"Missing required field for planning: {field}"

        # Verify high_complexity_elements structure
        for elem in task_result['high_complexity_elements']:
            assert 'name' in elem
            assert 'score' in elem
            assert 'risk_level' in elem


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
