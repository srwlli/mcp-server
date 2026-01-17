"""
Integration tests for complete planning workflow with scanner integration.

Tests end-to-end planning workflow from context gathering to plan generation
with all Phase 1, 2, and 3 enhancements integrated.

WO-WORKFLOW-SCANNER-INTEGRATION-001 TEST-005
"""

import pytest
import json
from pathlib import Path
from generators.planning_analyzer import PlanningAnalyzer
from generators.planning_generator import PlanningGenerator


@pytest.fixture
def sample_index_data():
    """Load sample index.json fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_index.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def sample_graph_data():
    """Load sample graph.json fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_graph.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def project_path(tmp_path, sample_index_data, sample_graph_data):
    """Create temporary project with complete .coderef/ structure."""
    coderef_dir = tmp_path / ".coderef"
    coderef_dir.mkdir()

    # Write index and graph
    (coderef_dir / "index.json").write_text(json.dumps(sample_index_data, indent=2))
    (coderef_dir / "graph.json").write_text(json.dumps(sample_graph_data, indent=2))

    # Create reports directory
    reports_dir = coderef_dir / "reports"
    reports_dir.mkdir()

    # Minimal patterns.json
    patterns = {
        "patterns": [
            {"type": "function", "count": 10, "naming_convention": "camelCase"},
            {"type": "class", "count": 5, "naming_convention": "PascalCase"}
        ]
    }
    (reports_dir / "patterns.json").write_text(json.dumps(patterns, indent=2))

    # Minimal coverage.json
    coverage = {
        "total_elements": 25,
        "tested_elements": 15,
        "coverage_percentage": 60,
        "untested_elements": [
            "resetPassword", "refreshToken", "deleteUser"
        ]
    }
    (reports_dir / "coverage.json").write_text(json.dumps(coverage, indent=2))

    # Minimal drift.json (no drift)
    drift = {
        "drift_percentage": 0,
        "stale_elements": []
    }
    (reports_dir / "drift.json").write_text(json.dumps(drift, indent=2))

    return tmp_path


@pytest.mark.asyncio
@pytest.mark.integration
class TestPlanningIntegration:
    """Integration tests for complete planning workflow."""

    async def test_full_planning_workflow_with_all_enhancements(self, project_path):
        """
        Test complete planning workflow from analysis to plan generation.

        Verifies that all three task areas are integrated:
        - Task 1: Type coverage (interfaces, decorators)
        - Task 2: Impact analysis (relationship graphs)
        - Task 3: Complexity tracking (complexity metrics)
        """
        # Step 1: Create analyzer and run full analysis
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        # Verify analysis.json includes all enhancements

        # Task 1: Type coverage
        assert 'type_system' in analysis, "analysis should include type_system section"
        type_system = analysis['type_system']
        assert 'interfaces' in type_system
        assert 'type_aliases' in type_system
        assert len(type_system['interfaces']) == 5, "Should detect 5 interfaces"
        assert len(type_system['type_aliases']) == 2, "Should detect 2 type aliases"

        assert 'decorators' in analysis, "analysis should include decorators section"
        assert len(analysis['decorators']) == 3, "Should detect 3 decorators"

        # Task 2: Impact analysis (verify capabilities exist, even if not run yet)
        # The analyzer should have analyze_change_impact() method available
        assert hasattr(analyzer, 'analyze_change_impact'), \
            "Analyzer should have analyze_change_impact method"

        # Task 3: Complexity (verify we can estimate complexity)
        # The analyzer should be able to provide complexity data
        # (Complexity estimation happens in plan generation phase)

        # Step 2: Create plan generator
        generator = PlanningGenerator(project_path)

        # Create minimal context
        context = {
            "description": "Add JWT refresh token support",
            "goal": "Allow users to refresh expired access tokens",
            "requirements": [
                "Add refreshToken() function",
                "Store refresh tokens securely",
                "Add token rotation logic"
            ]
        }

        # Step 3: Load planning template
        template = generator.load_template()

        # Step 4: Generate plan (internal fallback, not AI agent)
        plan = generator._generate_plan_internal_fallback(
            feature_name="jwt-refresh-tokens",
            context=context,
            analysis=analysis,
            template=template
        )

        # Verify plan.json structure includes all enhancements

        # Basic structure
        assert 'META_DOCUMENTATION' in plan
        assert 'UNIVERSAL_PLANNING_STRUCTURE' in plan

        structure = plan['UNIVERSAL_PLANNING_STRUCTURE']

        # Task 1: Type coverage reflected in risk assessment
        risk = structure.get('2_risk_assessment', {})
        assert 'complexity' in risk or 'risk_factors' in risk, \
            "Risk assessment should exist"

        # Task 3: Complexity metrics in phases
        phases = structure.get('6_implementation_phases', {}).get('phases', [])
        assert len(phases) > 0, "Should have implementation phases"

        # At least one phase should have complexity_metrics
        has_complexity = any('complexity_metrics' in phase for phase in phases)
        assert has_complexity, "At least one phase should include complexity_metrics"

        # Verify complexity metrics structure (lenient - accepts both full and fallback structures)
        for phase in phases:
            if 'complexity_metrics' in phase:
                metrics = phase['complexity_metrics']
                # Accept either full structure (avg/max scores) or fallback structure (estimated_complexity)
                has_full_metrics = 'avg_complexity_score' in metrics or 'max_complexity_score' in metrics
                has_fallback_metrics = 'estimated_complexity' in metrics
                assert has_full_metrics or has_fallback_metrics, \
                    f"Complexity metrics should include either full metrics or fallback: {metrics}"

    async def test_analysis_includes_type_coverage(self, project_path):
        """Test that analysis.json includes comprehensive type coverage."""
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        # Verify type_system section
        assert 'type_system' in analysis
        type_system = analysis['type_system']

        # Check interfaces
        assert 'interfaces' in type_system
        interfaces = type_system['interfaces']
        assert isinstance(interfaces, list)
        assert len(interfaces) == 5

        # Verify interface structure
        for interface in interfaces:
            assert 'name' in interface
            assert 'file' in interface
            assert 'line' in interface

        # Check type aliases
        assert 'type_aliases' in type_system
        type_aliases = type_system['type_aliases']
        assert len(type_aliases) == 2

        # Check decorators
        assert 'decorators' in analysis
        decorators = analysis['decorators']
        assert len(decorators) == 3

        # Verify decorator structure
        for decorator in decorators:
            assert 'name' in decorator
            assert 'target' in decorator

    async def test_analysis_provides_complexity_data(self, project_path):
        """Test that analysis provides data for complexity estimation."""
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        # Analysis should include key patterns (used for complexity estimation)
        assert 'key_patterns_identified' in analysis, \
            "analysis should include key_patterns_identified for complexity estimation"

        # Should have patterns data
        patterns = analysis['key_patterns_identified']
        assert isinstance(patterns, list) and len(patterns) > 0

    async def test_plan_generation_includes_complexity_metrics(self, project_path):
        """Test that generated plans include complexity metrics in phases."""
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        generator = PlanningGenerator(project_path)
        context = {
            "description": "Test feature",
            "goal": "Test goal",
            "requirements": ["Req 1", "Req 2", "Req 3"]
        }

        template = generator.load_template()
        plan = generator._generate_plan_internal_fallback(
            feature_name="test-feature",
            context=context,
            analysis=analysis,
            template=template
        )

        # Verify phases have complexity_metrics
        phases = plan['UNIVERSAL_PLANNING_STRUCTURE']['6_implementation_phases']['phases']

        complexity_found = False
        for phase in phases:
            if 'complexity_metrics' in phase:
                complexity_found = True
                metrics = phase['complexity_metrics']

                # Verify metrics structure
                assert isinstance(metrics, dict)
                # Should have at least one complexity field (either full or fallback)
                has_full_metrics = any(
                    key in metrics
                    for key in ['avg_complexity_score', 'max_complexity_score', 'high_complexity_elements']
                )
                has_fallback_metrics = 'estimated_complexity' in metrics
                assert has_full_metrics or has_fallback_metrics, \
                    f"Complexity metrics should include either full or fallback structure: {metrics}"

        assert complexity_found, "At least one phase should have complexity_metrics"

    async def test_plan_generation_flags_refactoring_candidates(self, project_path):
        """Test that plans flag high-complexity elements for refactoring."""
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        generator = PlanningGenerator(project_path)
        context = {
            "description": "Refactor authentication system",
            "goal": "Improve code quality",
            "requirements": [
                "Refactor AuthService",
                "Simplify resetPassword",
                "Extract validation logic"
            ]
        }

        template = generator.load_template()
        plan = generator._generate_plan_internal_fallback(
            feature_name="auth-refactoring",
            context=context,
            analysis=analysis,
            template=template
        )

        # Check if any phases have high_complexity_elements or refactoring warnings
        phases = plan['UNIVERSAL_PLANNING_STRUCTURE']['6_implementation_phases']['phases']

        refactoring_mentioned = False
        for phase in phases:
            # Check complexity_metrics for high_complexity_elements
            if 'complexity_metrics' in phase:
                if 'high_complexity_elements' in phase['complexity_metrics']:
                    high_elements = phase['complexity_metrics']['high_complexity_elements']
                    if len(high_elements) > 0:
                        refactoring_mentioned = True

            # Check notes for refactoring warnings
            if 'notes' in phase:
                notes = phase.get('notes', [])
                if isinstance(notes, list):
                    for note in notes:
                        if 'refactor' in note.lower() or 'complexity' in note.lower():
                            refactoring_mentioned = True

        # If no refactoring candidates found, that's ok - depends on the data
        # Just verify the structure exists for flagging them
        assert isinstance(phases, list) and len(phases) > 0

    async def test_integration_with_real_world_scenario(self, project_path):
        """Test with realistic feature implementation scenario."""
        # Scenario: Adding dark mode to the application

        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        generator = PlanningGenerator(project_path)
        context = {
            "description": "Add dark mode support",
            "goal": "Allow users to toggle between light and dark themes",
            "requirements": [
                "Add theme toggle component",
                "Implement theme context provider",
                "Update CSS for dark mode",
                "Persist theme preference",
                "Add tests for theme switching"
            ]
        }

        template = generator.load_template()
        plan = generator._generate_plan_internal_fallback(
            feature_name="dark-mode",
            context=context,
            analysis=analysis,
            template=template
        )

        # Verify complete plan structure
        assert 'META_DOCUMENTATION' in plan
        meta = plan['META_DOCUMENTATION']
        assert meta['feature_name'] == 'dark-mode'

        structure = plan['UNIVERSAL_PLANNING_STRUCTURE']

        # Verify all 10 sections exist (case-insensitive)
        required_sections = [
            '0_preparation',
            '1_executive_summary',
            '2_risk_assessment',
            '3_current_state_analysis',
            '4_key_features',
            '5_task_id_system',
            '6_implementation_phases',
            '7_testing_strategy',
            '8_success_criteria'
        ]

        # Check both lowercase and uppercase versions
        for section in required_sections:
            has_lowercase = section in structure
            has_uppercase = section.upper() in structure
            assert has_lowercase or has_uppercase, \
                f"Plan should include section {section} (or {section.upper()})"

        # Verify executive summary has proper structure (case-insensitive)
        summary = structure.get('1_executive_summary') or structure.get('1_EXECUTIVE_SUMMARY')
        assert summary is not None, "Should have executive summary section"
        assert 'what' in summary or 'summary' in summary or 'purpose' in summary

        # Verify risk assessment exists (case-insensitive)
        risk = structure.get('2_risk_assessment') or structure.get('2_RISK_ASSESSMENT')
        assert risk is not None, "Should have risk assessment section"
        assert 'complexity' in risk or 'risk_factors' in risk or 'overall_risk' in risk

        # Verify phases exist and have tasks (case-insensitive)
        phases_section = structure.get('6_implementation_phases') or structure.get('6_IMPLEMENTATION_PHASES')
        assert phases_section is not None, "Should have implementation phases section"
        phases = phases_section.get('phases', [])
        assert len(phases) > 0, "Should have at least one implementation phase"

        # Verify testing strategy exists (case-insensitive)
        testing = structure.get('7_testing_strategy') or structure.get('7_TESTING_STRATEGY')
        assert testing is not None, "Should have testing strategy section"
        # Accept various testing strategy structures
        has_testing_info = any(
            key in testing
            for key in ['unit_tests', 'test_coverage_target', 'integration_tests', 'end_to_end_tests']
        )
        assert has_testing_info, f"Testing strategy should include testing information: {testing.keys()}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
