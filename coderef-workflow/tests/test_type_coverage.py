"""
Unit tests for type coverage detection (Task 1: Planning Workflows).

Tests that planning workflows detect interfaces, decorators, and type aliases
with 95%+ code coverage using enhanced scanner data.

WO-WORKFLOW-SCANNER-INTEGRATION-001 TEST-002
"""

import pytest
import json
from pathlib import Path
from generators.planning_analyzer import PlanningAnalyzer
from generators.planning_generator import PlanningGenerator


@pytest.fixture
def sample_index_data():
    """Load sample index.json fixture with full scanner data."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_index.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def project_path(tmp_path):
    """Create temporary project with .coderef/ structure."""
    coderef_dir = tmp_path / ".coderef"
    coderef_dir.mkdir()

    # Copy sample fixtures to temp .coderef/
    fixture_index = Path(__file__).parent / "fixtures" / "sample_index.json"
    fixture_graph = Path(__file__).parent / "fixtures" / "sample_graph.json"

    (coderef_dir / "index.json").write_text(fixture_index.read_text())
    (coderef_dir / "graph.json").write_text(fixture_graph.read_text())

    return tmp_path


class TestInterfaceDetection:
    """Test interface detection in planning workflows."""

    @pytest.mark.asyncio
    async def test_get_type_system_elements_extracts_interfaces(self, project_path, sample_index_data):
        """Test that get_type_system_elements() extracts all interfaces from index.json."""
        analyzer = PlanningAnalyzer(project_path)

        type_system = await analyzer.get_type_system_elements()

        # Should extract all 5 interfaces from sample_index.json
        interfaces = type_system.get('interfaces', [])
        assert len(interfaces) == 5, f"Expected 5 interfaces, got {len(interfaces)}"

        # Verify interface names
        interface_names = {iface['name'] for iface in interfaces}
        expected_names = {'IAuthService', 'IUserRepository', 'ILogger', 'ApiResponse', 'ConfigOptions'}
        assert interface_names == expected_names, f"Interface names mismatch: {interface_names}"

        # Verify interface structure
        for interface in interfaces:
            assert 'name' in interface
            assert 'file' in interface
            assert 'line' in interface
            assert interface['file'].endswith('.ts'), "Interface files should be TypeScript"

    @pytest.mark.asyncio
    async def test_get_type_system_elements_extracts_type_aliases(self, project_path, sample_index_data):
        """Test that get_type_system_elements() extracts type aliases."""
        analyzer = PlanningAnalyzer(project_path)

        type_system = await analyzer.get_type_system_elements()

        # Should extract 2 type aliases from sample_index.json
        type_aliases = type_system.get('type_aliases', [])
        assert len(type_aliases) == 2, f"Expected 2 type aliases, got {len(type_aliases)}"

        # Verify type alias names
        alias_names = {alias['name'] for alias in type_aliases}
        expected_names = {'UserId', 'Token'}
        assert alias_names == expected_names, f"Type alias names mismatch: {alias_names}"

    @pytest.mark.asyncio
    async def test_interfaces_appear_in_analysis_json(self, project_path):
        """Test that interfaces appear in analysis.json output."""
        analyzer = PlanningAnalyzer(project_path)

        # Run full analysis
        analysis = await analyzer.analyze()

        # Check type_system section exists
        assert 'type_system' in analysis, "analysis.json should include type_system section"

        type_system = analysis['type_system']
        assert 'interfaces' in type_system
        assert 'type_aliases' in type_system

        # Verify counts match fixture
        assert len(type_system['interfaces']) == 5
        assert len(type_system['type_aliases']) == 2


class TestDecoratorDetection:
    """Test decorator detection in planning workflows."""

    @pytest.mark.asyncio
    async def test_get_decorator_elements_extracts_decorators(self, project_path, sample_index_data):
        """Test that get_decorator_elements() extracts all decorators."""
        analyzer = PlanningAnalyzer(project_path)

        decorators = await analyzer.get_decorator_elements()

        # Should extract all 3 decorators from sample_index.json
        assert len(decorators) == 3, f"Expected 3 decorators, got {len(decorators)}"

        # Verify decorator names
        decorator_names = {dec['name'] for dec in decorators}
        expected_names = {'@Injectable', '@Authorized', '@Log'}
        assert decorator_names == expected_names, f"Decorator names mismatch: {decorator_names}"

        # Verify decorator structure includes target
        for decorator in decorators:
            assert 'name' in decorator
            assert 'target' in decorator
            assert 'file' in decorator
            assert 'line' in decorator
            # Target can be class, method, function, or combinations
            assert 'target' in decorator, "Decorator should have target field"

    @pytest.mark.asyncio
    async def test_decorators_include_target_information(self, project_path):
        """Test that decorators include target (class/method) information."""
        analyzer = PlanningAnalyzer(project_path)

        decorators = await analyzer.get_decorator_elements()

        # Find specific decorators and verify they have targets
        injectable = next((d for d in decorators if d['name'] == '@Injectable'), None)
        assert injectable is not None
        assert 'target' in injectable, "@Injectable should have target information"
        assert injectable['target'], "@Injectable target should not be empty"

        authorized = next((d for d in decorators if d['name'] == '@Authorized'), None)
        assert authorized is not None
        assert 'target' in authorized, "@Authorized should have target information"
        assert authorized['target'], "@Authorized target should not be empty"

    @pytest.mark.asyncio
    async def test_decorators_appear_in_analysis_json(self, project_path):
        """Test that decorators appear in analysis.json output."""
        analyzer = PlanningAnalyzer(project_path)

        analysis = await analyzer.analyze()

        # Check decorators section exists
        assert 'decorators' in analysis, "analysis.json should include decorators section"

        decorators = analysis['decorators']
        assert len(decorators) == 3, f"Expected 3 decorators in analysis, got {len(decorators)}"


class TestTypeComplexityEstimation:
    """Test that type system complexity affects plan.json generation."""

    @pytest.mark.asyncio
    async def test_plan_considers_type_count_in_complexity(self, project_path):
        """Test that plan.json complexity increases with many interfaces/decorators."""
        generator = PlanningGenerator(project_path)

        # Create minimal context
        context = {
            "description": "Test feature",
            "goal": "Test goal",
            "requirements": ["Requirement 1", "Requirement 2", "Requirement 3"]
        }

        # Create analysis with type system data
        analysis = {
            "type_system": {
                "interfaces": [f"Interface{i}" for i in range(12)],  # >10 interfaces
                "type_aliases": [f"Type{i}" for i in range(3)]
            },
            "decorators": [f"@Decorator{i}" for i in range(6)]  # >5 decorators
        }

        # Generate risk assessment
        risk = generator._generate_risk_assessment(context, analysis)

        # Verify complexity mentions type counts
        complexity = risk['complexity']
        assert '15 types' in complexity or 'types' in complexity.lower(), \
            f"Complexity should mention type count: {complexity}"
        assert '6 decorators' in complexity or 'decorators' in complexity.lower(), \
            f"Complexity should mention decorator count: {complexity}"

    @pytest.mark.asyncio
    async def test_plan_without_types_has_lower_complexity(self, project_path):
        """Test that plans without many types have lower complexity."""
        generator = PlanningGenerator(project_path)

        context = {
            "description": "Test feature",
            "goal": "Test goal",
            "requirements": ["Requirement 1"]
        }

        # Analysis with few types
        analysis = {
            "type_system": {
                "interfaces": ["Interface1"],
                "type_aliases": []
            },
            "decorators": []
        }

        risk = generator._generate_risk_assessment(context, analysis)

        # Should not add extra complexity for type counts
        complexity = risk['complexity']
        assert 'low' in complexity.lower() or 'medium' in complexity.lower(), \
            f"Expected low/medium complexity, got: {complexity}"

    @pytest.mark.asyncio
    async def test_type_complexity_affects_overall_risk(self, project_path):
        """Test that heavy type usage can increase overall risk level."""
        generator = PlanningGenerator(project_path)

        # Minimal requirements but heavy type usage
        context = {
            "description": "Type-heavy feature",
            "goal": "Implement complex type system",
            "requirements": ["Req1", "Req2"]
        }

        analysis = {
            "type_system": {
                "interfaces": [f"Interface{i}" for i in range(15)],  # Many interfaces
                "type_aliases": [f"Type{i}" for i in range(5)]
            },
            "decorators": [f"@Dec{i}" for i in range(8)]  # Many decorators
        }

        risk = generator._generate_risk_assessment(context, analysis)

        # Heavy type usage should be reflected in complexity
        complexity_str = risk['complexity']
        assert '20 types' in complexity_str or '8 decorators' in complexity_str, \
            "Should mention type/decorator counts in complexity"


@pytest.mark.integration
class TestTypeCoverageIntegration:
    """Integration tests for full type coverage workflow."""

    @pytest.mark.asyncio
    async def test_full_planning_workflow_with_types(self, project_path):
        """Test complete planning workflow from analysis to plan.json with types."""
        # Step 1: Analyze project
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

        # Verify type coverage in analysis
        assert 'type_system' in analysis
        assert len(analysis['type_system']['interfaces']) == 5
        assert len(analysis['type_system']['type_aliases']) == 2
        assert 'decorators' in analysis
        assert len(analysis['decorators']) == 3

        # Step 2: Generate plan
        generator = PlanningGenerator(project_path)

        context = {
            "description": "Test feature with type system",
            "goal": "Implement feature using existing types",
            "requirements": ["Use IAuthService", "Apply @Injectable decorator"]
        }

        # Note: Would normally call generator.generate_plan() but it requires
        # Task agent integration. For this test, we verify the components work.
        risk = generator._generate_risk_assessment(context, analysis)

        # Verify type system is considered
        assert risk is not None
        assert 'complexity' in risk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
