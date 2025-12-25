"""
Tests for Lloyd Persona Optimization (WO-SLIM-LLOYD-PERSONA-001)

Verifies:
1. JSON parsing and schema validation
2. Line count within target (< 200 lines, was 1017)
3. No duplicate sections in system_prompt
4. Reference docs exist and are accessible
5. Version updated to 1.2.0
6. Core identity preserved
"""

import json
import os
import pytest
from pathlib import Path


# Paths
PERSONAS_DIR = Path(__file__).parent.parent / "personas" / "base"
DOCS_DIR = Path(__file__).parent.parent / "docs"
LLOYD_JSON = PERSONAS_DIR / "lloyd.json"


class TestLloydJsonStructure:
    """Test lloyd.json structure and schema compliance."""

    @pytest.fixture
    def lloyd_data(self):
        """Load lloyd.json data."""
        with open(LLOYD_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_json_parses_successfully(self):
        """Verify lloyd.json is valid JSON."""
        with open(LLOYD_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data is not None

    def test_required_fields_present(self, lloyd_data):
        """Verify all required PersonaDefinition fields exist."""
        required_fields = [
            'name', 'parent', 'version', 'description',
            'system_prompt', 'expertise', 'preferred_tools',
            'use_cases', 'behavior'
        ]
        for field in required_fields:
            assert field in lloyd_data, f"Missing required field: {field}"

    def test_name_is_lloyd(self, lloyd_data):
        """Verify persona name is 'lloyd'."""
        assert lloyd_data['name'] == 'lloyd'

    def test_version_updated(self, lloyd_data):
        """Verify version is 1.2.0 (post-optimization)."""
        assert lloyd_data['version'] == '1.2.0'

    def test_expertise_is_list(self, lloyd_data):
        """Verify expertise is a non-empty list."""
        assert isinstance(lloyd_data['expertise'], list)
        assert len(lloyd_data['expertise']) > 0

    def test_preferred_tools_is_list(self, lloyd_data):
        """Verify preferred_tools is a non-empty list."""
        assert isinstance(lloyd_data['preferred_tools'], list)
        assert len(lloyd_data['preferred_tools']) > 0

    def test_use_cases_is_list(self, lloyd_data):
        """Verify use_cases is a non-empty list."""
        assert isinstance(lloyd_data['use_cases'], list)
        assert len(lloyd_data['use_cases']) > 0

    def test_behavior_is_dict(self, lloyd_data):
        """Verify behavior is a dictionary with expected keys."""
        assert isinstance(lloyd_data['behavior'], dict)
        expected_keys = ['communication_style', 'problem_solving', 'tool_usage', 'persona_traits']
        for key in expected_keys:
            assert key in lloyd_data['behavior'], f"Missing behavior key: {key}"


class TestLloydOptimization:
    """Test optimization targets were met."""

    @pytest.fixture
    def system_prompt(self):
        """Load system_prompt content."""
        with open(LLOYD_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['system_prompt']

    def test_line_count_under_target(self, system_prompt):
        """Verify system_prompt is under 200 lines (was 1017)."""
        lines = system_prompt.split('\n')
        assert len(lines) < 200, f"System prompt has {len(lines)} lines, expected < 200"

    def test_line_count_reduction_achieved(self, system_prompt):
        """Verify at least 80% reduction from original 1017 lines."""
        original_lines = 1017
        current_lines = len(system_prompt.split('\n'))
        reduction = (original_lines - current_lines) / original_lines * 100
        assert reduction >= 80, f"Only {reduction:.1f}% reduction, expected >= 80%"

    def test_no_duplicate_big_picture(self, system_prompt):
        """Verify 'Big Picture' section is not duplicated."""
        count = system_prompt.count('### The Big Picture')
        assert count <= 1, f"'Big Picture' appears {count} times, expected <= 1"

    def test_no_duplicate_deep_understanding(self, system_prompt):
        """Verify 'Deep Understanding' section is not duplicated."""
        count = system_prompt.count('## Deep Understanding')
        assert count <= 1, f"'Deep Understanding' appears {count} times, expected <= 1"

    def test_reference_pointers_present(self, system_prompt):
        """Verify reference pointers to extracted docs are present."""
        assert 'MCP-ECOSYSTEM-REFERENCE.md' in system_prompt
        assert 'LLOYD-REFERENCE.md' in system_prompt


class TestCoreIdentityPreserved:
    """Test that core Lloyd identity is preserved after optimization."""

    @pytest.fixture
    def system_prompt(self):
        """Load system_prompt content."""
        with open(LLOYD_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['system_prompt']

    def test_identity_statement_present(self, system_prompt):
        """Verify Lloyd identity statement exists."""
        assert 'You are Lloyd' in system_prompt

    def test_coordinator_role_defined(self, system_prompt):
        """Verify coordinator/tech lead role is defined."""
        assert 'coordinator' in system_prompt.lower() or 'tech lead' in system_prompt.lower()

    def test_workflow_steps_present(self, system_prompt):
        """Verify 9-step workflow is summarized."""
        assert '/gather-context' in system_prompt
        assert '/create-plan' in system_prompt
        assert '/validate-plan' in system_prompt

    def test_agent_matrix_present(self, system_prompt):
        """Verify agent assignment matrix is present."""
        agents = ['Ava', 'Marcus', 'Quinn', 'Taylor', 'Devon']
        found_agents = sum(1 for agent in agents if agent in system_prompt)
        assert found_agents >= 4, f"Only {found_agents} agents found, expected >= 4"

    def test_key_principles_present(self, system_prompt):
        """Verify key principles section exists."""
        assert 'Key Principles' in system_prompt or 'Principles' in system_prompt

    def test_todowrite_mentioned(self, system_prompt):
        """Verify TodoWrite tool usage is mentioned."""
        assert 'TodoWrite' in system_prompt


class TestReferenceDocsExist:
    """Test that extracted reference documentation exists."""

    def test_docs_directory_exists(self):
        """Verify docs/ directory exists."""
        assert DOCS_DIR.exists(), f"docs/ directory not found at {DOCS_DIR}"

    def test_ecosystem_reference_exists(self):
        """Verify MCP-ECOSYSTEM-REFERENCE.md exists."""
        ecosystem_doc = DOCS_DIR / "MCP-ECOSYSTEM-REFERENCE.md"
        assert ecosystem_doc.exists(), f"MCP-ECOSYSTEM-REFERENCE.md not found"

    def test_lloyd_reference_exists(self):
        """Verify LLOYD-REFERENCE.md exists."""
        lloyd_doc = DOCS_DIR / "LLOYD-REFERENCE.md"
        assert lloyd_doc.exists(), f"LLOYD-REFERENCE.md not found"

    def test_ecosystem_reference_not_empty(self):
        """Verify MCP-ECOSYSTEM-REFERENCE.md has content."""
        ecosystem_doc = DOCS_DIR / "MCP-ECOSYSTEM-REFERENCE.md"
        content = ecosystem_doc.read_text(encoding='utf-8')
        assert len(content) > 1000, f"MCP-ECOSYSTEM-REFERENCE.md too short ({len(content)} chars)"

    def test_lloyd_reference_not_empty(self):
        """Verify LLOYD-REFERENCE.md has content."""
        lloyd_doc = DOCS_DIR / "LLOYD-REFERENCE.md"
        content = lloyd_doc.read_text(encoding='utf-8')
        assert len(content) > 1000, f"LLOYD-REFERENCE.md too short ({len(content)} chars)"

    def test_ecosystem_reference_has_tool_docs(self):
        """Verify ecosystem reference documents tools."""
        ecosystem_doc = DOCS_DIR / "MCP-ECOSYSTEM-REFERENCE.md"
        content = ecosystem_doc.read_text(encoding='utf-8')
        # Check for key tool domain documentation
        assert 'docs-mcp' in content
        assert 'coderef-mcp' in content
        assert 'personas-mcp' in content

    def test_lloyd_reference_has_workflows(self):
        """Verify Lloyd reference documents workflows."""
        lloyd_doc = DOCS_DIR / "LLOYD-REFERENCE.md"
        content = lloyd_doc.read_text(encoding='utf-8')
        # Check for workflow documentation
        assert 'Workflow' in content or 'workflow' in content
        assert 'Scenario' in content or 'scenario' in content


class TestPreferredTools:
    """Test preferred_tools configuration."""

    @pytest.fixture
    def preferred_tools(self):
        """Load preferred_tools list."""
        with open(LLOYD_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['preferred_tools']

    def test_has_planning_tools(self, preferred_tools):
        """Verify planning tools are in preferred list."""
        planning_tools = [
            'mcp__docs-mcp__gather_context',
            'mcp__docs-mcp__create_plan',
            'mcp__docs-mcp__validate_plan'
        ]
        for tool in planning_tools:
            assert tool in preferred_tools, f"Missing planning tool: {tool}"

    def test_has_coderef_tools(self, preferred_tools):
        """Verify coderef tools are in preferred list."""
        assert any('coderef' in tool for tool in preferred_tools)

    def test_has_todowrite(self, preferred_tools):
        """Verify TodoWrite is in preferred list."""
        assert 'TodoWrite' in preferred_tools


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
