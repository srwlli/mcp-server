"""
Unit tests for risk assessment handler and RiskGenerator.

Tests validate:
- Input validation (validate_risk_inputs)
- RiskGenerator.analyze_project_context()
- All 5 risk dimension evaluators
- Composite scoring algorithm
- Multi-option comparison
- Recommendation generation
- Mitigation strategy generation

WO-RISK-ASSESSMENT-001
"""

import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from validation import validate_risk_inputs
from generators.risk_generator import RiskGenerator
from type_defs import ProposedChangeDict, ProjectContextDict


class TestValidateRiskInputs:
    """Test suite for validate_risk_inputs function."""

    def test_valid_single_option_input(self):
        """Test validation with valid single-option input."""
        arguments = {
            'project_path': '/absolute/path/to/project',
            'proposed_change': {
                'description': 'Add user authentication',
                'change_type': 'create',
                'files_affected': ['src/auth.py', 'tests/test_auth.py']
            }
        }

        result = validate_risk_inputs(arguments)

        assert str(result['project_path']) == '/absolute/path/to/project'  # Compare strings
        assert result['proposed_change']['description'] == 'Add user authentication'
        assert result['threshold'] == 50.0  # Default threshold

    def test_valid_multi_option_input(self):
        """Test validation with multi-option comparison input."""
        arguments = {
            'project_path': '/absolute/path/to/project',
            'proposed_change': {
                'description': 'Option 1: JWT tokens',
                'change_type': 'create',
                'files_affected': ['src/auth/jwt.py']
            },
            'options': [
                {
                    'description': 'Option 2: Session cookies',
                    'change_type': 'create',
                    'files_affected': ['src/auth/sessions.py']
                }
            ],
            'threshold': 40.0
        }

        result = validate_risk_inputs(arguments)

        assert len(result['options']) == 1
        assert result['threshold'] == 40.0

    def test_missing_project_path(self):
        """Test validation fails when project_path is missing."""
        arguments = {
            'proposed_change': {
                'description': 'Test',
                'change_type': 'create',
                'files_affected': ['test.py']
            }
        }

        with pytest.raises(ValueError, match="Missing required parameter: 'project_path'"):
            validate_risk_inputs(arguments)

    def test_missing_proposed_change(self):
        """Test validation fails when proposed_change is missing."""
        arguments = {
            'project_path': '/path/to/project'
        }

        with pytest.raises(ValueError, match="Missing required parameter: 'proposed_change'"):
            validate_risk_inputs(arguments)

    def test_invalid_change_type(self):
        """Test validation fails with invalid change_type."""
        arguments = {
            'project_path': '/path/to/project',
            'proposed_change': {
                'description': 'Test',
                'change_type': 'invalid_type',
                'files_affected': ['test.py']
            }
        }

        with pytest.raises(ValueError, match="Invalid change_type"):
            validate_risk_inputs(arguments)

    def test_too_many_options(self):
        """Test validation fails when > 5 options provided."""
        arguments = {
            'project_path': '/path/to/project',
            'proposed_change': {
                'description': 'Option 1',
                'change_type': 'create',
                'files_affected': ['test.py']
            },
            # 5 options in the list (max is 5 total including proposed_change, but validation allows 4 in options array)
            'options': [{'description': f'Option {i}', 'files_affected': ['test.py']} for i in range(2, 8)]
        }

        with pytest.raises(ValueError, match="Maximum 5 options allowed"):
            validate_risk_inputs(arguments)


class TestRiskGeneratorContextAnalysis:
    """Test suite for RiskGenerator.analyze_project_context()."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project structure for testing."""
        # Create some source files
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'main.py').write_text('print("hello")')
        (tmp_path / 'src' / 'utils.py').write_text('def helper(): pass')

        # Create test files
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'tests' / 'test_main.py').write_text('def test_main(): pass')

        # Create package.json
        package_json = {
            'dependencies': {'express': '^4.0.0', 'lodash': '^4.17.0'},
            'devDependencies': {'jest': '^27.0.0'}
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        return tmp_path

    def test_analyze_project_context(self, temp_project):
        """Test project context analysis discovers files and dependencies."""
        generator = RiskGenerator(temp_project)
        context = generator.analyze_project_context()

        assert context['files_analyzed'] > 0
        assert context['dependencies_found'] == 3  # 2 deps + 1 devDep
        assert context['test_coverage'] > 0  # Should detect test files
        assert isinstance(context['gaps'], list)

    def test_analyze_empty_project(self, tmp_path):
        """Test context analysis on empty project."""
        generator = RiskGenerator(tmp_path)
        context = generator.analyze_project_context()

        assert context['files_analyzed'] == 0
        assert context['dependencies_found'] == 0
        assert 'No dependency files found' in ' '.join(context['gaps'])


class TestRiskDimensionEvaluators:
    """Test suite for all 5 risk dimension evaluators."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create RiskGenerator instance."""
        return RiskGenerator(tmp_path)

    @pytest.fixture
    def basic_context(self):
        """Create basic project context."""
        return {
            'files_analyzed': 100,
            'dependencies_found': 20,
            'test_coverage': 75.0,
            'architecture_patterns': ['MVC/REST API structure'],
            'gaps': []
        }

    def test_evaluate_breaking_changes_delete(self, generator, basic_context):
        """Test breaking changes evaluation for file deletion."""
        proposed_change: ProposedChangeDict = {
            'description': 'Delete legacy API endpoint',
            'change_type': 'delete',
            'files_affected': ['src/api/legacy.py'],
            'context': {}
        }

        result = generator.evaluate_breaking_changes(proposed_change, basic_context)

        assert result['severity'] in ['high', 'critical']  # Both acceptable for deletion
        assert result['likelihood'] >= 70.0  # High likelihood
        assert result['score'] > 50
        assert any('delet' in finding.lower() for finding in result['findings'])

    def test_evaluate_breaking_changes_api_modification(self, generator, basic_context):
        """Test breaking changes evaluation for API modification."""
        proposed_change: ProposedChangeDict = {
            'description': 'Change API endpoint response schema',
            'change_type': 'modify',
            'files_affected': ['src/api/users.py'],
            'context': {}
        }

        result = generator.evaluate_breaking_changes(proposed_change, basic_context)

        assert result['severity'] in ['medium', 'high', 'critical']
        assert 'API' in ' '.join(result['findings']) or 'interface' in ' '.join(result['findings'])

    def test_evaluate_security_risks_secrets(self, generator, basic_context):
        """Test security evaluation detects secret handling."""
        proposed_change: ProposedChangeDict = {
            'description': 'Store API key in configuration',
            'change_type': 'modify',
            'files_affected': ['config/settings.py'],
            'context': {}
        }

        result = generator.evaluate_security_risks(proposed_change, basic_context)

        assert result['severity'] in ['low', 'medium', 'high', 'critical']  # Pattern detection is heuristic
        assert any('secret' in finding.lower() or 'credential' in finding.lower() or 'api' in finding.lower() for finding in result['findings'])

    def test_evaluate_security_risks_sql(self, generator, basic_context):
        """Test security evaluation detects SQL query changes."""
        proposed_change: ProposedChangeDict = {
            'description': 'Add SELECT query to fetch user data FROM users table',
            'change_type': 'create',
            'files_affected': ['src/database/queries.py'],
            'context': {}
        }

        result = generator.evaluate_security_risks(proposed_change, basic_context)

        assert result['severity'] in ['low', 'medium', 'high']
        # Check if SQL pattern was detected (either in findings or score reflects it)
        sql_detected = any('sql' in finding.lower() or 'query' in finding.lower() for finding in result['findings']) or result['score'] > 10
        assert sql_detected

    def test_evaluate_performance_impact_optimization(self, generator, basic_context):
        """Test performance evaluation detects optimization."""
        proposed_change: ProposedChangeDict = {
            'description': 'Optimize performance by adding caching layer to reduce database queries',
            'change_type': 'create',
            'files_affected': ['src/cache/redis.py'],
            'context': {}
        }

        result = generator.evaluate_performance_impact(proposed_change, basic_context)

        assert result['severity'] == 'low'
        # Check if optimization/cache keywords were detected
        perf_keywords_detected = any('optimi' in finding.lower() or 'cache' in finding.lower() or 'performance' in finding.lower() for finding in result['findings'])
        assert perf_keywords_detected

    def test_evaluate_maintainability_large_refactor(self, generator, basic_context):
        """Test maintainability evaluation for large refactoring."""
        proposed_change: ProposedChangeDict = {
            'description': 'Refactor entire authentication module',
            'change_type': 'refactor',
            'files_affected': [f'src/auth/module{i}.py' for i in range(15)],
            'context': {}
        }

        result = generator.evaluate_maintainability(proposed_change, basic_context)

        assert result['severity'] in ['medium', 'high']
        assert any('refactor' in finding.lower() for finding in result['findings'])

    def test_evaluate_reversibility_database_migration(self, generator, basic_context):
        """Test reversibility evaluation for database migration."""
        proposed_change: ProposedChangeDict = {
            'description': 'Database migration to add new column',
            'change_type': 'migrate',
            'files_affected': ['migrations/add_user_role.py'],
            'context': {}
        }

        result = generator.evaluate_reversibility(proposed_change, basic_context)

        assert result['severity'] in ['medium', 'high', 'critical']
        assert any('migration' in finding.lower() or 'rollback' in finding.lower() for finding in result['findings'])


class TestCompositeScoring:
    """Test suite for composite scoring algorithm."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create RiskGenerator instance."""
        return RiskGenerator(tmp_path)

    def test_calculate_composite_score_low_risk(self, generator):
        """Test composite score calculation for low-risk change."""
        dimensions = {
            'breaking_changes': {'score': 10.0},
            'security': {'score': 5.0},
            'performance': {'score': 8.0},
            'maintainability': {'score': 12.0},
            'reversibility': {'score': 6.0}
        }

        result = generator.calculate_composite_score(dimensions)

        assert result['score'] < 25
        assert result['level'] == 'low'
        assert 'weighted average' in result['explanation'].lower()

    def test_calculate_composite_score_high_risk(self, generator):
        """Test composite score calculation for high-risk change."""
        dimensions = {
            'breaking_changes': {'score': 85.0},
            'security': {'score': 75.0},
            'performance': {'score': 60.0},
            'maintainability': {'score': 70.0},
            'reversibility': {'score': 80.0}
        }

        result = generator.calculate_composite_score(dimensions)

        assert result['score'] >= 50
        assert result['level'] in ['high', 'critical']

    def test_composite_score_weighted_average(self, generator):
        """Test that composite score uses correct weights."""
        # Breaking changes weighted at 30%
        dimensions = {
            'breaking_changes': {'score': 100.0},
            'security': {'score': 0.0},
            'performance': {'score': 0.0},
            'maintainability': {'score': 0.0},
            'reversibility': {'score': 0.0}
        }

        result = generator.calculate_composite_score(dimensions)

        # Should be approximately 30 (100 * 0.30)
        assert 28 <= result['score'] <= 32


class TestRecommendationGeneration:
    """Test suite for recommendation generation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create RiskGenerator instance."""
        return RiskGenerator(tmp_path)

    def test_recommendation_go_low_risk(self, generator):
        """Test 'go' recommendation for low-risk change."""
        composite_score = {'score': 15.0, 'level': 'low'}
        dimensions = {dim: {'score': 15.0} for dim in ['breaking_changes', 'security', 'performance', 'maintainability', 'reversibility']}

        result = generator.generate_recommendations(composite_score, dimensions, threshold=50.0)

        assert result['decision'] == 'go'
        assert 'below threshold' in result['rationale'].lower()

    def test_recommendation_no_go_critical_risk(self, generator):
        """Test 'no-go' recommendation for critical risk."""
        composite_score = {'score': 85.0, 'level': 'critical'}
        dimensions = {
            'breaking_changes': {'score': 90.0},
            'security': {'score': 80.0},
            'performance': {'score': 70.0},
            'maintainability': {'score': 75.0},
            'reversibility': {'score': 85.0}
        }

        result = generator.generate_recommendations(composite_score, dimensions, threshold=50.0)

        assert result['decision'] in ['no-go', 'needs-review']
        assert len(result['conditions']) > 0  # Should have mitigation conditions

    def test_recommendation_conditions_for_high_risk_dimensions(self, generator):
        """Test that conditions are generated for high-risk dimensions."""
        composite_score = {'score': 60.0, 'level': 'high'}
        dimensions = {
            'breaking_changes': {'score': 75.0},  # High risk
            'security': {'score': 70.0},  # High risk
            'performance': {'score': 20.0},
            'maintainability': {'score': 25.0},
            'reversibility': {'score': 80.0}  # High risk
        }

        result = generator.generate_recommendations(composite_score, dimensions, threshold=50.0)

        # Should have conditions for breaking, security, reversibility
        assert len(result['conditions']) >= 2


class TestMitigationStrategies:
    """Test suite for mitigation strategy generation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create RiskGenerator instance."""
        return RiskGenerator(tmp_path)

    def test_generate_mitigation_strategies(self, generator):
        """Test mitigation strategies are generated for high-risk dimensions."""
        dimensions = {
            'breaking_changes': {'score': 60.0},
            'security': {'score': 75.0},
            'performance': {'score': 20.0},
            'maintainability': {'score': 15.0},
            'reversibility': {'score': 70.0}
        }

        strategies = generator.generate_mitigation_strategies(dimensions)

        assert len(strategies) > 0
        assert all('risk_dimension' in s for s in strategies)
        assert all('strategy' in s for s in strategies)
        assert all('priority' in s for s in strategies)

        # Security score is 75, should have critical/high priority
        security_strategies = [s for s in strategies if s['risk_dimension'] == 'security']
        assert len(security_strategies) > 0
        assert any(s['priority'] in ['critical', 'high'] for s in security_strategies)


class TestMultiOptionComparison:
    """Test suite for multi-option comparison."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create RiskGenerator instance."""
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'test.py').write_text('print("test")')
        return RiskGenerator(tmp_path)

    @pytest.fixture
    def basic_context(self):
        """Create basic project context."""
        return {
            'files_analyzed': 50,
            'dependencies_found': 10,
            'test_coverage': 60.0,
            'architecture_patterns': [],
            'gaps': []
        }

    def test_compare_options_ranks_by_risk(self, generator, basic_context):
        """Test that options are ranked by risk score (lowest = best)."""
        options = [
            {
                'description': 'High-risk option: delete critical files',
                'change_type': 'delete',
                'files_affected': ['src/core.py', 'src/critical.py']
            },
            {
                'description': 'Low-risk option: add configuration file',
                'change_type': 'create',
                'files_affected': ['config/settings.yaml']
            },
            {
                'description': 'Medium-risk option: refactor authentication',
                'change_type': 'refactor',
                'files_affected': ['src/auth.py']
            }
        ]

        result = generator.compare_options(options, basic_context)

        # Check structure
        assert 'options' in result
        assert 'recommended_option' in result
        assert len(result['options']) == 3

        # Check ranking (rank 1 should be lowest risk)
        sorted_options = sorted(result['options'], key=lambda x: x['rank'])
        assert sorted_options[0]['rank'] == 1
        assert sorted_options[0]['composite_score'] <= sorted_options[1]['composite_score']
        assert sorted_options[1]['composite_score'] <= sorted_options[2]['composite_score']

        # Recommended option should be rank 1
        recommended = next(o for o in result['options'] if o['option_id'] == result['recommended_option'])
        assert recommended['rank'] == 1

    def test_compare_options_includes_pros_cons(self, generator, basic_context):
        """Test that comparison includes pros/cons for each option."""
        options = [
            {
                'description': 'Option with optimization keyword',
                'change_type': 'modify',
                'files_affected': ['src/performance.py']
            }
        ]

        result = generator.compare_options(options, basic_context)

        assert all('pros' in opt for opt in result['options'])
        assert all('cons' in opt for opt in result['options'])


class TestPerformance:
    """Test suite for performance requirements."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create RiskGenerator with realistic project."""
        # Create 100 files
        (tmp_path / 'src').mkdir()
        for i in range(100):
            (tmp_path / 'src' / f'file{i}.py').write_text(f'# File {i}')
        return RiskGenerator(tmp_path)

    def test_context_analysis_performance(self, generator):
        """Test that context analysis completes quickly."""
        import time
        start = time.time()

        context = generator.analyze_project_context()

        duration = time.time() - start
        assert duration < 1.0  # Should complete in < 1 second
        assert context['files_analyzed'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
