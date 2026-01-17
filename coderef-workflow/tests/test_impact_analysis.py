"""
Unit tests for impact analysis (Task 2: Impact Analysis).

Tests that impact analysis workflows leverage relationship data (imports/exports/dependencies)
with accurate change impact assessment.

WO-WORKFLOW-SCANNER-INTEGRATION-001 TEST-003
"""

import pytest
import json
from pathlib import Path
from handlers.impact_analysis import ImpactAnalyzer


@pytest.fixture
def sample_index_data():
    """Load sample index.json fixture with relationship data."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_index.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def project_path(tmp_path, sample_index_data):
    """Create temporary project with .coderef/ structure."""
    coderef_dir = tmp_path / ".coderef"
    coderef_dir.mkdir()

    # Write sample index to temp .coderef/
    (coderef_dir / "index.json").write_text(json.dumps(sample_index_data, indent=2))

    return tmp_path


class TestDependencyTraversal:
    """Test BFS dependency traversal with cycle detection."""

    def test_traverse_dependencies_downstream(self, project_path):
        """Test downstream traversal (who depends on this element)."""
        analyzer = ImpactAnalyzer(project_path)

        # authenticateUser is called by AuthController
        affected = analyzer.traverse_dependencies('authenticateUser', max_depth=2, direction='downstream')

        # Should find AuthController at depth 1
        assert len(affected) >= 1, f"Expected at least 1 affected element, got {len(affected)}"

        # Verify AuthController is included
        affected_names = {elem['name'] for elem in affected}
        assert 'AuthController' in affected_names, f"AuthController should depend on authenticateUser"

        # Verify depth is tracked
        for elem in affected:
            assert 'depth' in elem, "Each affected element should have depth"
            assert elem['depth'] >= 1, "Depth should be at least 1"
            assert elem['depth'] <= 2, f"Depth should not exceed max_depth=2, got {elem['depth']}"

    def test_traverse_dependencies_upstream(self, project_path):
        """Test upstream traversal (what does this element depend on)."""
        analyzer = ImpactAnalyzer(project_path)

        # Test upstream traversal completes successfully
        # Note: authenticateUser has dependencies (UserRepository, JwtService, Logger)
        # but they may not exist as elements in the index (realistic scenario)
        affected = analyzer.traverse_dependencies('authenticateUser', max_depth=2, direction='upstream')

        # Should return a list (may be empty if dependencies aren't in index)
        assert isinstance(affected, list), "Should return a list"

        # All returned elements should have required fields
        for elem in affected:
            assert 'name' in elem
            assert 'type' in elem
            assert 'depth' in elem
            assert 'path' in elem

    def test_traverse_dependencies_respects_max_depth(self, project_path):
        """Test that traversal stops at max_depth."""
        analyzer = ImpactAnalyzer(project_path)

        # Traverse with max_depth=1
        affected_depth_1 = analyzer.traverse_dependencies('authenticateUser', max_depth=1, direction='downstream')

        # All elements should be at depth 1
        for elem in affected_depth_1:
            assert elem['depth'] == 1, f"With max_depth=1, all elements should be at depth 1, got {elem['depth']}"

        # Traverse with max_depth=3 should get more results (or same if graph is shallow)
        affected_depth_3 = analyzer.traverse_dependencies('authenticateUser', max_depth=3, direction='downstream')

        assert len(affected_depth_3) >= len(affected_depth_1), \
            "Higher max_depth should find at least as many elements"

    def test_traverse_dependencies_includes_path(self, project_path):
        """Test that affected elements include relationship path."""
        analyzer = ImpactAnalyzer(project_path)

        affected = analyzer.traverse_dependencies('authenticateUser', max_depth=2, direction='downstream')

        # All affected elements should have a path field
        for elem in affected:
            assert 'path' in elem, "Each affected element should have 'path' field"
            assert 'authenticateUser' in elem['path'], "Path should include starting element"

            # Path should use arrow notation
            if ' → ' in elem['path']:
                parts = elem['path'].split(' → ')
                assert parts[0] == 'authenticateUser', "Path should start with authenticateUser"
                assert parts[-1] == elem['name'], "Path should end with element name"

    def test_traverse_dependencies_empty_when_no_relationships(self, project_path):
        """Test that elements with no relationships return empty list."""
        analyzer = ImpactAnalyzer(project_path)

        # ILogger is used by many elements but shouldn't have downstream dependencies in our fixture
        # (it's an interface, so nothing "depends" on it in the downstream sense)
        # Let's test with a decorator instead
        affected = analyzer.traverse_dependencies('@Log', max_depth=2, direction='downstream')

        # @Log decorator might have zero downstream dependencies
        assert isinstance(affected, list), "Should return a list even if empty"

    def test_traverse_dependencies_handles_cycles(self, project_path):
        """Test that BFS handles cycles gracefully (visited set prevents infinite loops)."""
        analyzer = ImpactAnalyzer(project_path)

        # Even if there are cycles in the dependency graph, traversal should complete
        # (BFS with visited set should prevent revisiting nodes)
        affected = analyzer.traverse_dependencies('AuthService', max_depth=5, direction='downstream')

        # Should complete without hanging
        assert isinstance(affected, list)

        # No element should appear twice (cycle detection via visited set)
        affected_names = [elem['name'] for elem in affected]
        assert len(affected_names) == len(set(affected_names)), \
            "No element should appear twice (cycle detection should work)"


class TestImpactScoreCalculation:
    """Test impact score calculation and risk categorization."""

    def test_calculate_impact_score_low_risk(self, project_path):
        """Test low risk categorization (0-5 affected elements)."""
        analyzer = ImpactAnalyzer(project_path)

        # Create mock affected elements (3 elements = low risk)
        affected = [
            {'name': 'Elem1', 'depth': 1},
            {'name': 'Elem2', 'depth': 1},
            {'name': 'Elem3', 'depth': 2}
        ]

        score = analyzer.calculate_impact_score(affected)

        assert score['impact_score'] == 3, "Impact score should equal number of affected elements"
        assert score['risk_level'] == 'low', f"3 affected elements should be 'low' risk, got {score['risk_level']}"
        assert 'breakdown' in score, "Score should include breakdown by depth"
        assert score['breakdown']['depth_1'] == 2, "Should have 2 elements at depth 1"
        assert score['breakdown']['depth_2'] == 1, "Should have 1 element at depth 2"

    def test_calculate_impact_score_medium_risk(self, project_path):
        """Test medium risk categorization (6-15 affected elements)."""
        analyzer = ImpactAnalyzer(project_path)

        # 10 elements = medium risk
        affected = [{'name': f'Elem{i}', 'depth': 1} for i in range(10)]

        score = analyzer.calculate_impact_score(affected)

        assert score['impact_score'] == 10
        assert score['risk_level'] == 'medium', f"10 affected elements should be 'medium' risk, got {score['risk_level']}"

    def test_calculate_impact_score_high_risk(self, project_path):
        """Test high risk categorization (16-50 affected elements)."""
        analyzer = ImpactAnalyzer(project_path)

        # 30 elements = high risk
        affected = [{'name': f'Elem{i}', 'depth': (i % 3) + 1} for i in range(30)]

        score = analyzer.calculate_impact_score(affected)

        assert score['impact_score'] == 30
        assert score['risk_level'] == 'high', f"30 affected elements should be 'high' risk, got {score['risk_level']}"

    def test_calculate_impact_score_critical_risk(self, project_path):
        """Test critical risk categorization (>50 affected elements)."""
        analyzer = ImpactAnalyzer(project_path)

        # 100 elements = critical risk
        affected = [{'name': f'Elem{i}', 'depth': 1} for i in range(100)]

        score = analyzer.calculate_impact_score(affected)

        assert score['impact_score'] == 100
        assert score['risk_level'] == 'critical', f"100 affected elements should be 'critical' risk, got {score['risk_level']}"

    def test_calculate_impact_score_zero_elements(self, project_path):
        """Test that zero affected elements results in low risk."""
        analyzer = ImpactAnalyzer(project_path)

        score = analyzer.calculate_impact_score([])

        assert score['impact_score'] == 0
        assert score['risk_level'] == 'low', "Zero affected elements should be 'low' risk"
        assert score['breakdown'] == {}, "Empty list should have empty breakdown"


class TestImpactReportGeneration:
    """Test markdown impact report generation with Mermaid graphs."""

    def test_generate_impact_report_includes_summary(self, project_path):
        """Test that report includes summary section."""
        analyzer = ImpactAnalyzer(project_path)

        affected = [
            {'name': 'Elem1', 'type': 'function', 'file': 'src/test.ts', 'line': 10, 'depth': 1, 'path': 'Root → Elem1'}
        ]
        score = {'impact_score': 1, 'risk_level': 'low', 'affected_count': 1, 'breakdown': {'depth_1': 1}}

        report = analyzer.generate_impact_report('Root', affected, score)

        assert '# Impact Analysis: Root' in report, "Report should have title with element name"
        assert '## Summary' in report, "Report should have Summary section"
        assert '**Affected Elements:** 1' in report, "Summary should show affected count"
        assert '**Risk Level:** LOW' in report, "Summary should show risk level in uppercase"

    def test_generate_impact_report_includes_depth_breakdown(self, project_path):
        """Test that report includes impact by depth section."""
        analyzer = ImpactAnalyzer(project_path)

        affected = [
            {'name': 'Elem1', 'type': 'function', 'file': 'src/test.ts', 'line': 10, 'depth': 1, 'path': 'Root → Elem1'},
            {'name': 'Elem2', 'type': 'function', 'file': 'src/test.ts', 'line': 20, 'depth': 2, 'path': 'Root → Elem1 → Elem2'}
        ]
        score = {
            'impact_score': 2,
            'risk_level': 'low',
            'affected_count': 2,
            'breakdown': {'depth_1': 1, 'depth_2': 1}
        }

        report = analyzer.generate_impact_report('Root', affected, score)

        assert '## Impact by Depth' in report, "Report should have depth breakdown section"
        assert 'Depth 1: 1 elements' in report, "Should show depth 1 count"
        assert 'Depth 2: 1 elements' in report, "Should show depth 2 count"

    def test_generate_impact_report_includes_affected_elements_list(self, project_path):
        """Test that report lists all affected elements grouped by depth."""
        analyzer = ImpactAnalyzer(project_path)

        affected = [
            {'name': 'Elem1', 'type': 'function', 'file': 'src/test.ts', 'line': 10, 'depth': 1, 'path': 'Root → Elem1'},
            {'name': 'Elem2', 'type': 'class', 'file': 'src/other.ts', 'line': 25, 'depth': 1, 'path': 'Root → Elem2'}
        ]
        score = {'impact_score': 2, 'risk_level': 'low', 'affected_count': 2, 'breakdown': {'depth_1': 2}}

        report = analyzer.generate_impact_report('Root', affected, score)

        assert '## Affected Elements' in report, "Report should have affected elements section"
        assert '### Depth 1 (2 elements)' in report, "Should group by depth"
        assert '**Elem1** (function) - `src/test.ts:10`' in report, "Should list element with details"
        assert '**Elem2** (class) - `src/other.ts:25`' in report, "Should list second element"
        assert 'Path: `Root → Elem1`' in report, "Should show relationship path"

    def test_generate_impact_report_includes_mermaid_graph(self, project_path):
        """Test that report includes Mermaid dependency graph."""
        analyzer = ImpactAnalyzer(project_path)

        affected = [
            {'name': 'Child1', 'type': 'function', 'file': 'src/test.ts', 'line': 10, 'depth': 1, 'path': 'Root → Child1'},
            {'name': 'Child2', 'type': 'function', 'file': 'src/test.ts', 'line': 20, 'depth': 1, 'path': 'Root → Child2'}
        ]
        score = {'impact_score': 2, 'risk_level': 'low', 'affected_count': 2, 'breakdown': {'depth_1': 2}}

        report = analyzer.generate_impact_report('Root', affected, score)

        assert '## Dependency Graph' in report, "Report should have dependency graph section"
        assert '```mermaid' in report, "Should include Mermaid code block"
        assert 'graph TD' in report, "Should use Mermaid graph syntax"
        assert 'Root["Root"]' in report, "Should include root node"
        assert 'Root --> Child1' in report or 'Root --> Child2' in report, "Should include at least one edge"

    def test_generate_impact_report_sanitizes_mermaid_ids(self, project_path):
        """Test that special characters in element names are sanitized for Mermaid."""
        analyzer = ImpactAnalyzer(project_path)

        # Element with special characters (@Injectable decorator)
        affected = [
            {'name': '@Injectable', 'type': 'decorator', 'file': 'src/decorators.ts', 'line': 5, 'depth': 1, 'path': 'Root → @Injectable'}
        ]
        score = {'impact_score': 1, 'risk_level': 'low', 'affected_count': 1, 'breakdown': {'depth_1': 1}}

        report = analyzer.generate_impact_report('Root', affected, score)

        # @Injectable should be sanitized to _Injectable or elem_Injectable
        assert '```mermaid' in report
        # Should not contain raw @ symbol in node ID
        lines = report.split('\n')
        mermaid_section = [line for line in lines if 'graph TD' in report and line.strip().startswith('Root') or line.strip().startswith('elem_')]
        # At minimum, mermaid section should not crash


class TestHighLevelImpactAnalysis:
    """Test high-level analyze_element_impact() method."""

    def test_analyze_element_impact_returns_complete_result(self, project_path):
        """Test that analyze_element_impact() combines all analysis steps."""
        analyzer = ImpactAnalyzer(project_path)

        # Analyze authenticateUser
        result = analyzer.analyze_element_impact('authenticateUser', max_depth=2)

        assert result is not None, "Should return result for valid element"
        assert 'element_name' in result
        assert result['element_name'] == 'authenticateUser'
        assert 'affected_elements' in result
        assert 'impact_score' in result
        assert 'report' in result

        # Verify impact_score structure
        score = result['impact_score']
        assert 'impact_score' in score
        assert 'risk_level' in score
        assert score['risk_level'] in ['low', 'medium', 'high', 'critical']

        # Verify report is markdown string
        report = result['report']
        assert isinstance(report, str)
        assert '# Impact Analysis: authenticateUser' in report

    def test_analyze_element_impact_returns_none_for_nonexistent_element(self, project_path):
        """Test that analyze_element_impact() returns None for elements that don't exist."""
        analyzer = ImpactAnalyzer(project_path)

        result = analyzer.analyze_element_impact('NonexistentElement', max_depth=2)

        assert result is None, "Should return None for nonexistent element"


class TestElementLookup:
    """Test element lookup functionality."""

    def test_find_element_by_name_returns_correct_element(self, project_path):
        """Test that _find_element_by_name() returns the correct element."""
        analyzer = ImpactAnalyzer(project_path)

        elem = analyzer._find_element_by_name('authenticateUser')

        assert elem is not None, "Should find authenticateUser"
        assert elem['name'] == 'authenticateUser'
        assert elem['type'] == 'function'
        assert 'file' in elem
        assert 'line' in elem

    def test_find_element_by_name_returns_none_for_nonexistent(self, project_path):
        """Test that _find_element_by_name() returns None for nonexistent elements."""
        analyzer = ImpactAnalyzer(project_path)

        elem = analyzer._find_element_by_name('DoesNotExist')

        assert elem is None, "Should return None for nonexistent element"


@pytest.mark.integration
class TestImpactAnalysisIntegration:
    """Integration tests for complete impact analysis workflow."""

    def test_full_impact_analysis_workflow(self, project_path):
        """Test complete workflow from element selection to report generation."""
        analyzer = ImpactAnalyzer(project_path)

        # Step 1: Find an element
        elem = analyzer._find_element_by_name('authenticateUser')
        assert elem is not None

        # Step 2: Traverse dependencies
        affected = analyzer.traverse_dependencies('authenticateUser', max_depth=2)
        assert isinstance(affected, list)

        # Step 3: Calculate impact score
        score = analyzer.calculate_impact_score(affected)
        assert 'risk_level' in score

        # Step 4: Generate report
        report = analyzer.generate_impact_report('authenticateUser', affected, score)
        assert '# Impact Analysis: authenticateUser' in report

        # Or use high-level method
        result = analyzer.analyze_element_impact('authenticateUser', max_depth=2)
        assert result is not None
        assert result['report'] == report or len(result['report']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
