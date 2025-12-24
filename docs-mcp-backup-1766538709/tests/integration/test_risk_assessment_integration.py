"""
Integration tests for risk assessment workflow.

Tests full MCP tool workflow from input validation through risk evaluation
to JSON output and file persistence.
"""

import pytest
import json
from pathlib import Path
import time

# Import MCP components
import tool_handlers


def extract_json_from_response(response_text: str) -> dict:
    """Extract JSON data from formatted MCP response."""
    json_start = response_text.find('{')
    if json_start == -1:
        raise ValueError(f"No JSON found in response: {response_text}")
    json_text = response_text[json_start:]
    return json.loads(json_text)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory with minimal structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create minimal project structure
    (project_dir / "src").mkdir()
    (project_dir / "src" / "auth.py").write_text("# Auth module")
    (project_dir / "src" / "api.py").write_text("# API module")
    (project_dir / "tests").mkdir()
    (project_dir / "tests" / "test_auth.py").write_text("# Auth tests")
    (project_dir / "package.json").write_text('{"dependencies": {"express": "^4.18.0"}}')

    return project_dir


@pytest.mark.asyncio
class TestRiskAssessmentIntegration:
    """Integration tests for full risk assessment workflow."""

    async def test_end_to_end_single_option_workflow(self, temp_project_dir):
        """Test complete workflow: input → validation → evaluation → output."""
        # Arrange: Prepare MCP tool arguments
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Add JWT authentication with token refresh mechanism',
                'change_type': 'create',
                'files_affected': ['src/auth.py', 'src/middleware/auth.js']
            },
            'threshold': 60.0,
            'feature_name': 'auth-system'
        }

        # Act: Call MCP tool handler
        start_time = time.time()
        result = await tool_handlers.handle_assess_risk(arguments)
        elapsed = time.time() - start_time

        # Assert: Verify MCP response structure
        assert len(result) == 1
        response_data = extract_json_from_response(result[0].text)

        # Verify summary response fields
        assert 'assessment_id' in response_data
        assert 'assessment_path' in response_data
        assert 'composite_score' in response_data
        assert 'risk_level' in response_data
        assert 'decision' in response_data
        assert 'success' in response_data

        # Verify composite score
        assert 0 <= response_data['composite_score'] <= 100
        assert response_data['risk_level'] in ['low', 'medium', 'high', 'critical']
        assert response_data['decision'] in ['go', 'no-go', 'proceed-with-caution', 'needs-review']

        # Verify performance
        assert elapsed < 5.0, f"Assessment took {elapsed:.2f}s (expected < 5s)"

        # Verify file was saved
        assessment_file = Path(response_data['assessment_path'])
        assert assessment_file.exists()
        assert assessment_file.suffix == '.json'

        # Verify saved file contains full assessment
        saved_assessment = json.loads(assessment_file.read_text(encoding='utf-8'))
        assert 'risk_dimensions' in saved_assessment
        assert 'composite_score' in saved_assessment
        assert 'recommendation' in saved_assessment
        assert saved_assessment['assessment_id'] == response_data['assessment_id']

        # Verify all 5 dimensions present in saved file
        dimensions = saved_assessment['risk_dimensions']
        assert 'breaking_changes' in dimensions
        assert 'security' in dimensions
        assert 'performance' in dimensions
        assert 'maintainability' in dimensions
        assert 'reversibility' in dimensions

    async def test_multi_option_comparison_workflow(self, temp_project_dir):
        """Test multi-option comparison with ranking."""
        # Arrange: Multiple implementation options
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Add caching layer for API responses',
                'change_type': 'create',
                'files_affected': ['src/cache/redis.py']
            },
            'options': [
                {
                    'description': 'Use in-memory cache (fastest, but limited capacity)',
                    'change_type': 'create',
                    'files_affected': ['src/cache/memory.py']
                },
                {
                    'description': 'Use Redis (scalable, requires infrastructure)',
                    'change_type': 'create',
                    'files_affected': ['src/cache/redis.py']
                },
                {
                    'description': 'Use database caching (simple, slower)',
                    'change_type': 'create',
                    'files_affected': ['src/cache/db.py']
                }
            ],
            'threshold': 50.0
        }

        # Act: Call handler
        result = await tool_handlers.handle_assess_risk(arguments)
        response_data = extract_json_from_response(result[0].text)

        # Assert: Verify multi-option structure
        assert 'options_analyzed' in response_data
        assert response_data['options_analyzed'] == 4  # proposed + 3 options
        assert 'recommended_option' in response_data

        # Read saved file to verify comparison details
        assessment_file = Path(response_data['assessment_path'])
        saved_assessment = json.loads(assessment_file.read_text(encoding='utf-8'))

        assert 'comparison' in saved_assessment
        comparison = saved_assessment['comparison']
        assert 'options' in comparison
        assert len(comparison['options']) == 4

        # Verify ranking
        for option in comparison['options']:
            assert 'rank' in option
            assert 'composite_score' in option  # Changed from risk_score to composite_score
            assert 'description' in option

    async def test_high_risk_threshold_decision(self, temp_project_dir):
        """Test that high-risk changes trigger appropriate decision."""
        # Arrange: High-risk change (database deletion)
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Delete user authentication table and remove all user accounts',
                'change_type': 'delete',
                'files_affected': ['migrations/drop_users_table.sql']
            },
            'threshold': 40.0  # Lower threshold for testing
        }

        # Act
        result = await tool_handlers.handle_assess_risk(arguments)
        response_data = extract_json_from_response(result[0].text)

        # Assert: High risk should trigger warning decision
        composite_score = response_data['composite_score']
        decision = response_data['decision']

        assert composite_score > 30.0  # Should have elevated score
        assert decision in ['no-go', 'needs-review', 'proceed-with-caution']

        # Verify mitigation strategies in saved file
        assessment_file = Path(response_data['assessment_path'])
        saved_assessment = json.loads(assessment_file.read_text(encoding='utf-8'))
        assert 'mitigation_strategies' in saved_assessment
        assert len(saved_assessment['mitigation_strategies']) > 0

    async def test_invalid_input_error_handling(self, temp_project_dir):
        """Test error handling for invalid inputs."""
        # Arrange: Missing required field
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Test change',
                # Missing 'change_type'
                'files_affected': ['test.py']
            }
        }

        # Act
        result = await tool_handlers.handle_assess_risk(arguments)
        response_text = result[0].text

        # Assert: Should return error response
        assert 'error' in response_text.lower() or 'missing' in response_text.lower() or 'required' in response_text.lower()

    async def test_security_dimension_detection(self, temp_project_dir):
        """Test that security patterns are properly detected."""
        # Arrange: Change with security implications
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Store user passwords and API keys in config.json file',
                'change_type': 'modify',
                'files_affected': ['config/settings.json']
            }
        }

        # Act
        result = await tool_handlers.handle_assess_risk(arguments)
        response_data = extract_json_from_response(result[0].text)

        # Assert: Read saved assessment for detailed validation
        assessment_file = Path(response_data['assessment_path'])
        saved_assessment = json.loads(assessment_file.read_text(encoding='utf-8'))

        # Security dimension should flag this
        security_dim = saved_assessment['risk_dimensions']['security']
        assert security_dim['severity'] in ['medium', 'high', 'critical']
        assert any('secret' in finding.lower() or 'password' in finding.lower() or 'api' in finding.lower()
                   for finding in security_dim['findings'])

    async def test_breaking_changes_detection(self, temp_project_dir):
        """Test that breaking changes are properly flagged."""
        # Arrange: Breaking API change
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Remove deprecated API endpoint /api/v1/users',
                'change_type': 'delete',
                'files_affected': ['src/routes/users.py']
            }
        }

        # Act
        result = await tool_handlers.handle_assess_risk(arguments)
        response_data = extract_json_from_response(result[0].text)

        # Assert: Read saved assessment
        assessment_file = Path(response_data['assessment_path'])
        saved_assessment = json.loads(assessment_file.read_text(encoding='utf-8'))

        # Breaking changes dimension should be flagged
        breaking_dim = saved_assessment['risk_dimensions']['breaking_changes']
        assert breaking_dim['severity'] in ['medium', 'high', 'critical']
        assert breaking_dim['score'] > 20.0  # Should have elevated score


@pytest.mark.asyncio
class TestRiskAssessmentPerformance:
    """Performance-focused integration tests."""

    async def test_performance_under_load(self, temp_project_dir):
        """Test performance with multiple sequential assessments."""
        # Arrange: Multiple changes to assess
        changes = [
            {
                'description': f'Refactor module {i}',
                'change_type': 'refactor',
                'files_affected': [f'src/module_{i}.py']
            }
            for i in range(10)
        ]

        # Act: Run multiple assessments
        start_time = time.time()
        results = []

        for change in changes:
            arguments = {
                'project_path': str(temp_project_dir),
                'proposed_change': change
            }
            result = await tool_handlers.handle_assess_risk(arguments)
            results.append(result)

        elapsed = time.time() - start_time

        # Assert: Total time should be reasonable
        assert len(results) == 10
        avg_time = elapsed / 10
        assert avg_time < 2.0, f"Average assessment time {avg_time:.2f}s (expected < 2s)"

    async def test_large_project_context_analysis(self, temp_project_dir):
        """Test performance with larger project structure."""
        # Arrange: Create larger project structure (100+ files)
        for i in range(50):
            (temp_project_dir / "src" / f"module_{i}.py").write_text(f"# Module {i}")
            (temp_project_dir / "tests" / f"test_module_{i}.py").write_text(f"# Test {i}")

        # Act
        arguments = {
            'project_path': str(temp_project_dir),
            'proposed_change': {
                'description': 'Add new feature across multiple modules',
                'change_type': 'create',
                'files_affected': [f'src/module_{i}.py' for i in range(10)]
            }
        }

        start_time = time.time()
        result = await tool_handlers.handle_assess_risk(arguments)
        elapsed = time.time() - start_time

        # Assert: Should still complete quickly
        assert elapsed < 5.0, f"Large project assessment took {elapsed:.2f}s (expected < 5s)"
        assert len(result) == 1
        response_data = extract_json_from_response(result[0].text)

        # Verify file was saved and contains project context info
        assessment_file = Path(response_data['assessment_path'])
        saved_assessment = json.loads(assessment_file.read_text(encoding='utf-8'))
        # Verify assessment completed successfully (indicates large project was processed)
        assert saved_assessment['assessment_id'] is not None
        assert 'composite_score' in saved_assessment
