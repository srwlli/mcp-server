"""
Comprehensive tests for Lloyd persona (personas/base/lloyd.json).

Tests cover:
1. Schema validation (structure, types, required fields)
2. Content quality (depth, completeness, no placeholders)
3. Versioning & metadata (semver, timestamps)
4. Workflow completeness (11-step planning workflow)
5. Tool references (valid MCP tool names)
6. Regression (v1.5.0 enhancements)
7. Behavior patterns (communication, problem-solving, tool usage)
8. Integration (persona loading via MCP)
"""

import json
import re
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def lloyd_persona() -> Dict[str, Any]:
    """Load Lloyd persona JSON from file."""
    persona_path = Path(__file__).parent.parent / "personas" / "base" / "lloyd.json"

    if not persona_path.exists():
        pytest.skip(f"Lloyd persona not found at {persona_path}")

    with open(persona_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def lloyd_system_prompt(lloyd_persona: Dict[str, Any]) -> str:
    """Extract system prompt for easier testing."""
    return lloyd_persona["system_prompt"]


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

class TestLloydSchema:
    """Test Lloyd persona JSON schema and structure."""

    def test_required_top_level_fields(self, lloyd_persona):
        """Test all required top-level fields are present."""
        required_fields = [
            "name",
            "parent",
            "version",
            "created_at",
            "updated_at",
            "description",
            "config",
            "system_prompt",
            "expertise",
            "preferred_tools",
            "use_cases",
            "behavior"
        ]

        for field in required_fields:
            assert field in lloyd_persona, f"Missing required field: {field}"

    def test_field_types(self, lloyd_persona):
        """Test all fields have correct data types."""
        assert isinstance(lloyd_persona["name"], str)
        assert lloyd_persona["parent"] is None or isinstance(lloyd_persona["parent"], str)
        assert isinstance(lloyd_persona["version"], str)
        assert isinstance(lloyd_persona["created_at"], str)
        assert isinstance(lloyd_persona["updated_at"], str)
        assert isinstance(lloyd_persona["description"], str)
        assert isinstance(lloyd_persona["config"], dict)
        assert isinstance(lloyd_persona["system_prompt"], str)
        assert isinstance(lloyd_persona["expertise"], list)
        assert isinstance(lloyd_persona["preferred_tools"], list)
        assert isinstance(lloyd_persona["use_cases"], list)
        assert isinstance(lloyd_persona["behavior"], dict)

    def test_config_structure(self, lloyd_persona):
        """Test config object has required fields with correct types."""
        config = lloyd_persona["config"]

        assert "strict_mode" in config
        assert isinstance(config["strict_mode"], bool)

        assert "enforce_plan_json" in config
        assert isinstance(config["enforce_plan_json"], bool)

        assert "validate_workorder_id" in config
        assert isinstance(config["validate_workorder_id"], bool)

    def test_config_strict_mode_enabled(self, lloyd_persona):
        """Test Lloyd has strict mode enabled for workorder enforcement."""
        config = lloyd_persona["config"]

        assert config["strict_mode"] is True, "strict_mode should be enabled"
        assert config["enforce_plan_json"] is True, "enforce_plan_json should be enabled"
        assert config["validate_workorder_id"] is True, "validate_workorder_id should be enabled"

    def test_behavior_structure(self, lloyd_persona):
        """Test behavior object has required fields."""
        behavior = lloyd_persona["behavior"]

        required_behavior_fields = [
            "communication_style",
            "problem_solving",
            "tool_usage"
        ]

        for field in required_behavior_fields:
            assert field in behavior, f"Missing behavior field: {field}"
            assert isinstance(behavior[field], str)

    def test_lists_not_empty(self, lloyd_persona):
        """Test that list fields are not empty."""
        assert len(lloyd_persona["expertise"]) > 0, "expertise list is empty"
        assert len(lloyd_persona["preferred_tools"]) > 0, "preferred_tools list is empty"
        assert len(lloyd_persona["use_cases"]) > 0, "use_cases list is empty"


# ============================================================================
# CONTENT QUALITY TESTS
# ============================================================================

class TestLloydContentQuality:
    """Test Lloyd persona has substantial, quality content."""

    def test_system_prompt_length(self, lloyd_system_prompt):
        """Test system prompt is comprehensive (>2000 characters)."""
        assert len(lloyd_system_prompt) > 2000, \
            f"System prompt too short: {len(lloyd_system_prompt)} chars"

    def test_expertise_count(self, lloyd_persona):
        """Test Lloyd has 10+ areas of expertise."""
        expertise = lloyd_persona["expertise"]
        assert len(expertise) >= 10, \
            f"Too few expertise areas: {len(expertise)}"

    def test_use_cases_count(self, lloyd_persona):
        """Test Lloyd has 5+ use cases."""
        use_cases = lloyd_persona["use_cases"]
        assert len(use_cases) >= 5, \
            f"Too few use cases: {len(use_cases)}"

    def test_preferred_tools_count(self, lloyd_persona):
        """Test Lloyd has 8+ preferred tools."""
        tools = lloyd_persona["preferred_tools"]
        assert len(tools) >= 8, \
            f"Too few preferred tools: {len(tools)}"

    def test_no_placeholder_text(self, lloyd_persona):
        """Test persona has no placeholder or TODO text."""
        full_text = json.dumps(lloyd_persona, indent=2)

        placeholders = ["TODO", "FIXME", "PLACEHOLDER", "XXX", "HACK"]
        for placeholder in placeholders:
            assert placeholder not in full_text, \
                f"Found placeholder text: {placeholder}"

    def test_description_quality(self, lloyd_persona):
        """Test description is meaningful and specific."""
        description = lloyd_persona["description"]

        assert len(description) > 50, "Description too short"
        assert "Lloyd" in description, "Description doesn't mention Lloyd"
        assert "coordinator" in description.lower(), "Description doesn't mention coordination"

    def test_expertise_specificity(self, lloyd_persona):
        """Test expertise entries are specific and detailed."""
        expertise = lloyd_persona["expertise"]

        # Each expertise should be reasonably detailed
        for item in expertise:
            assert len(item) > 10, f"Expertise too vague: {item}"
            assert not item.endswith("..."), f"Incomplete expertise: {item}"

    def test_use_cases_specificity(self, lloyd_persona):
        """Test use cases are specific scenarios, not generic."""
        use_cases = lloyd_persona["use_cases"]

        for use_case in use_cases:
            assert len(use_case) > 15, f"Use case too generic: {use_case}"


# ============================================================================
# VERSIONING & METADATA TESTS
# ============================================================================

class TestLloydVersioning:
    """Test Lloyd version follows semver and metadata is valid."""

    def test_version_format(self, lloyd_persona):
        """Test version follows semantic versioning (major.minor.patch)."""
        version = lloyd_persona["version"]

        # Should match semver pattern (e.g., "1.5.0")
        assert re.match(r"^\d+\.\d+\.\d+$", version), \
            f"Invalid version format: {version}"

    def test_version_is_v1_5_0_or_later(self, lloyd_persona):
        """Test Lloyd is at least version 1.5.0."""
        version = lloyd_persona["version"]
        major, minor, patch = map(int, version.split("."))

        assert major >= 1, "Major version should be >= 1"
        assert (major, minor) >= (1, 5), \
            f"Version {version} is older than required 1.5.0"

    def test_created_timestamp_valid(self, lloyd_persona):
        """Test created_at is valid ISO 8601 timestamp."""
        created_at = lloyd_persona["created_at"]

        # Should parse successfully
        try:
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid created_at timestamp: {created_at}")

    def test_updated_timestamp_valid(self, lloyd_persona):
        """Test updated_at is valid ISO 8601 timestamp."""
        updated_at = lloyd_persona["updated_at"]

        # Should parse successfully
        try:
            datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid updated_at timestamp: {updated_at}")

    def test_updated_after_created(self, lloyd_persona):
        """Test updated_at timestamp >= created_at timestamp."""
        created_str = lloyd_persona["created_at"]
        updated_str = lloyd_persona["updated_at"]

        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))

        assert updated >= created, \
            f"updated_at ({updated}) is before created_at ({created})"

    def test_name_is_lloyd(self, lloyd_persona):
        """Test persona name is exactly 'lloyd' (lowercase)."""
        assert lloyd_persona["name"] == "lloyd", \
            f"Expected name 'lloyd', got '{lloyd_persona['name']}'"

    def test_parent_is_null(self, lloyd_persona):
        """Test Lloyd has no parent (is a base persona)."""
        assert lloyd_persona["parent"] is None, \
            "Lloyd should not have a parent persona"


# ============================================================================
# WORKFLOW VALIDATION TESTS
# ============================================================================

class TestLloydWorkflowCompleteness:
    """Test Lloyd's documented workflows are complete."""

    def test_11_step_planning_workflow(self, lloyd_system_prompt):
        """Test all 11 planning steps are documented."""
        # Steps 1-11 should all be mentioned
        for step_num in range(1, 12):
            assert f"Step {step_num}" in lloyd_system_prompt, \
                f"Missing Step {step_num} in planning workflow"

    def test_execution_phase_steps(self, lloyd_system_prompt):
        """Test execution phase steps (12-15) are documented."""
        # Steps 12-15 (post-planning)
        for step_num in range(12, 16):
            assert f"Step {step_num}" in lloyd_system_prompt, \
                f"Missing Step {step_num} in execution workflow"

    def test_create_workorder_mentioned(self, lloyd_system_prompt):
        """Test /create-workorder command is documented."""
        assert "/create-workorder" in lloyd_system_prompt, \
            "/create-workorder not mentioned in system prompt"

    def test_key_workflow_commands(self, lloyd_system_prompt):
        """Test key workflow commands are documented."""
        key_commands = [
            "/gather-context",
            "/create-plan",
            "/validate-plan",
            "/align-plan",
            "/update-deliverables",
            "/archive-feature"
        ]

        for command in key_commands:
            assert command in lloyd_system_prompt, \
                f"Key command {command} not mentioned"

    def test_multi_agent_coordination_documented(self, lloyd_system_prompt):
        """Test multi-agent coordination is documented."""
        # Should mention multi-agent somewhere
        prompt_lower = lloyd_system_prompt.lower()
        assert "multi-agent" in prompt_lower or "multi agent" in prompt_lower, \
            "Multi-agent coordination not documented"

    def test_workorder_format_documented(self, lloyd_system_prompt):
        """Test workorder ID format is documented."""
        # Should mention WO-{FEATURE}-{CATEGORY}-###
        assert "WO-" in lloyd_system_prompt, \
            "Workorder ID format not documented"
        assert "{FEATURE}" in lloyd_system_prompt or "FEATURE" in lloyd_system_prompt
        assert "{CATEGORY}" in lloyd_system_prompt or "CATEGORY" in lloyd_system_prompt

    def test_plan_json_enforcement(self, lloyd_system_prompt):
        """Test plan.json format enforcement is documented."""
        assert "plan.json" in lloyd_system_prompt, \
            "plan.json format not mentioned"
        assert "JSON" in lloyd_system_prompt or "json" in lloyd_system_prompt

        # Should reject markdown plans
        prompt_lower = lloyd_system_prompt.lower()
        assert "reject" in prompt_lower or "invalid" in prompt_lower

    def test_todowrite_usage_documented(self, lloyd_system_prompt):
        """Test TodoWrite usage is documented."""
        assert "TodoWrite" in lloyd_system_prompt, \
            "TodoWrite not mentioned in system prompt"


# ============================================================================
# TOOL REFERENCE TESTS
# ============================================================================

class TestLloydToolReferences:
    """Test Lloyd's preferred tools are valid MCP tools."""

    def test_tool_naming_convention(self, lloyd_persona):
        """Test all preferred tools follow MCP naming convention."""
        tools = lloyd_persona["preferred_tools"]

        for tool in tools:
            # Built-in tools (TodoWrite) or MCP tools (mcp__server__tool)
            if tool == "TodoWrite":
                continue  # Built-in tool, skip

            assert tool.startswith("mcp__"), \
                f"Tool doesn't follow MCP convention: {tool}"

    def test_mcp_tool_format(self, lloyd_persona):
        """Test MCP tools have valid format: mcp__server__tool_name."""
        tools = lloyd_persona["preferred_tools"]

        for tool in tools:
            if tool == "TodoWrite":
                continue

            parts = tool.split("__")
            assert len(parts) == 3, \
                f"Invalid MCP tool format (expected 3 parts): {tool}"

            assert parts[0] == "mcp", f"Tool doesn't start with 'mcp': {tool}"
            assert len(parts[1]) > 0, f"Empty server name: {tool}"
            assert len(parts[2]) > 0, f"Empty tool name: {tool}"

    def test_key_tools_included(self, lloyd_persona):
        """Test essential Lloyd tools are in preferred_tools."""
        tools = lloyd_persona["preferred_tools"]

        # Essential tools Lloyd needs
        essential_tools = [
            "TodoWrite",
            "mcp__coderef-docs__gather_context",
            "mcp__coderef-docs__create_plan",
            "mcp__coderef-workflow__execute_plan"
        ]

        for essential in essential_tools:
            assert essential in tools, \
                f"Essential tool missing from preferred_tools: {essential}"

    def test_coderef_tools_included(self, lloyd_persona):
        """Test coderef-mcp tools are included for code intelligence."""
        tools = lloyd_persona["preferred_tools"]

        # Should have at least one coderef-mcp tool
        coderef_tools = [t for t in tools if "coderef-mcp" in t]
        assert len(coderef_tools) > 0, \
            "No coderef-mcp tools in preferred_tools"

    def test_no_duplicate_tools(self, lloyd_persona):
        """Test no duplicate tools in preferred_tools."""
        tools = lloyd_persona["preferred_tools"]

        assert len(tools) == len(set(tools)), \
            f"Duplicate tools found: {[t for t in tools if tools.count(t) > 1]}"


# ============================================================================
# REGRESSION TESTS (v1.5.0)
# ============================================================================

class TestLloydV15Enhancements:
    """Test Lloyd v1.5.0 has documented enhancements."""

    def test_step_3_foundation_docs(self, lloyd_system_prompt):
        """Test Step 3 foundation docs generation is documented."""
        # Should mention Step 3 with foundation docs
        assert "Step 3" in lloyd_system_prompt

        # Should mention key foundation docs
        assert "ARCHITECTURE.md" in lloyd_system_prompt
        assert "SCHEMA.md" in lloyd_system_prompt

        # Should mention project-context.json
        assert "project-context.json" in lloyd_system_prompt

    def test_step_10_enhanced(self, lloyd_system_prompt):
        """Test Step 10 enhanced with execute_plan."""
        assert "Step 10" in lloyd_system_prompt

        # Should mention execute_plan tool
        prompt_lower = lloyd_system_prompt.lower()
        assert "execute_plan" in prompt_lower

    def test_step_11_git_checkpoint(self, lloyd_system_prompt):
        """Test Step 11 pre-execution git checkpoint is documented."""
        assert "Step 11" in lloyd_system_prompt

        # Should mention git checkpoint or commit
        prompt_lower = lloyd_system_prompt.lower()
        assert "git" in prompt_lower
        assert "checkpoint" in prompt_lower or "commit" in prompt_lower

    def test_coderef_foundation_docs_tool(self, lloyd_system_prompt):
        """Test coderef_foundation_docs tool is mentioned."""
        assert "coderef_foundation_docs" in lloyd_system_prompt or \
               "foundation_docs" in lloyd_system_prompt

    def test_v15_features_in_system_prompt(self, lloyd_system_prompt):
        """Test v1.5.0 features are mentioned in system prompt."""
        # Key v1.5.0 additions
        features = [
            "foundation docs",
            "ARCHITECTURE.md",
            "SCHEMA.md",
            "COMPONENTS.md"
        ]

        prompt_lower = lloyd_system_prompt.lower()
        for feature in features:
            assert feature.lower() in prompt_lower, \
                f"v1.5.0 feature not mentioned: {feature}"


# ============================================================================
# BEHAVIOR PATTERN TESTS
# ============================================================================

class TestLloydBehaviorPatterns:
    """Test Lloyd's behavior configuration matches documented patterns."""

    def test_communication_style_traits(self, lloyd_persona):
        """Test communication style mentions key traits."""
        comm_style = lloyd_persona["behavior"]["communication_style"].lower()

        # Should mention clarity/conciseness
        assert any(word in comm_style for word in ["clear", "concise", "action"]), \
            "Communication style missing key traits"

    def test_problem_solving_approach(self, lloyd_persona):
        """Test problem-solving approach mentions breaking down tasks."""
        problem_solving = lloyd_persona["behavior"]["problem_solving"].lower()

        # Should mention breaking down complexity
        assert "break" in problem_solving or "step" in problem_solving, \
            "Problem-solving doesn't mention task breakdown"

    def test_tool_usage_mentions_todowrite(self, lloyd_persona):
        """Test tool usage mentions TodoWrite (core Lloyd tool)."""
        tool_usage = lloyd_persona["behavior"]["tool_usage"]

        assert "TodoWrite" in tool_usage, \
            "Tool usage doesn't mention TodoWrite"

    def test_tool_usage_mentions_planning_tools(self, lloyd_persona):
        """Test tool usage mentions planning/docs-mcp tools."""
        tool_usage = lloyd_persona["behavior"]["tool_usage"].lower()

        assert "planning" in tool_usage or "docs-mcp" in tool_usage, \
            "Tool usage doesn't mention planning tools"

    def test_expertise_covers_coordination(self, lloyd_persona):
        """Test expertise includes project coordination."""
        expertise_text = " ".join(lloyd_persona["expertise"]).lower()

        assert "coordination" in expertise_text or "coordinator" in expertise_text, \
            "Expertise doesn't mention coordination"

    def test_expertise_covers_multi_agent(self, lloyd_persona):
        """Test expertise includes multi-agent coordination."""
        expertise_text = " ".join(lloyd_persona["expertise"]).lower()

        assert "multi-agent" in expertise_text or "multi agent" in expertise_text, \
            "Expertise doesn't mention multi-agent coordination"

    def test_use_cases_cover_planning(self, lloyd_persona):
        """Test use cases include planning scenarios."""
        use_cases_text = " ".join(lloyd_persona["use_cases"]).lower()

        assert "planning" in use_cases_text or "plan" in use_cases_text, \
            "Use cases don't mention planning"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestLloydIntegration:
    """Integration tests requiring actual persona loading."""

    @pytest.mark.integration
    def test_lloyd_json_parses_successfully(self, lloyd_persona):
        """Test Lloyd JSON parses without errors."""
        # If we got here, JSON parsing succeeded
        assert lloyd_persona is not None
        assert isinstance(lloyd_persona, dict)

    @pytest.mark.integration
    def test_lloyd_can_be_serialized(self, lloyd_persona):
        """Test Lloyd persona can be serialized back to JSON."""
        try:
            json_str = json.dumps(lloyd_persona, indent=2)
            assert len(json_str) > 0
        except Exception as e:
            pytest.fail(f"Failed to serialize Lloyd persona: {e}")

    @pytest.mark.integration
    def test_lloyd_roundtrip_serialization(self, lloyd_persona):
        """Test Lloyd persona survives JSON roundtrip."""
        # Serialize to JSON string
        json_str = json.dumps(lloyd_persona, indent=2)

        # Parse back to dict
        roundtrip = json.loads(json_str)

        # Should match original
        assert roundtrip == lloyd_persona


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestLloydPerformance:
    """Performance tests for Lloyd persona."""

    def test_system_prompt_not_too_large(self, lloyd_system_prompt):
        """Test system prompt is comprehensive but not excessively large."""
        # Should be substantial but not >20k chars (context limit concerns)
        assert len(lloyd_system_prompt) < 20000, \
            f"System prompt too large: {len(lloyd_system_prompt)} chars"

    def test_total_persona_size_reasonable(self, lloyd_persona):
        """Test total persona JSON size is reasonable."""
        json_str = json.dumps(lloyd_persona, indent=2)
        size = len(json_str)

        # Should be <50KB for reasonable loading times
        assert size < 50000, \
            f"Persona JSON too large: {size} bytes"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestLloydEdgeCases:
    """Edge case and defensive tests."""

    def test_no_null_values_in_required_fields(self, lloyd_persona):
        """Test required fields are not null."""
        required_not_null = [
            "name",
            "version",
            "system_prompt",
            "expertise",
            "preferred_tools",
            "use_cases"
        ]

        for field in required_not_null:
            assert lloyd_persona[field] is not None, \
                f"Required field is null: {field}"

    def test_no_empty_strings_in_required_fields(self, lloyd_persona):
        """Test required string fields are not empty."""
        required_string_fields = ["name", "version", "system_prompt", "description"]

        for field in required_string_fields:
            value = lloyd_persona[field]
            assert isinstance(value, str) and len(value) > 0, \
                f"Required string field is empty: {field}"

    def test_no_duplicate_expertise(self, lloyd_persona):
        """Test no duplicate entries in expertise list."""
        expertise = lloyd_persona["expertise"]

        assert len(expertise) == len(set(expertise)), \
            f"Duplicate expertise entries: {[e for e in expertise if expertise.count(e) > 1]}"

    def test_no_duplicate_use_cases(self, lloyd_persona):
        """Test no duplicate entries in use_cases list."""
        use_cases = lloyd_persona["use_cases"]

        assert len(use_cases) == len(set(use_cases)), \
            f"Duplicate use cases: {[u for u in use_cases if use_cases.count(u) > 1]}"

    def test_special_characters_handled(self, lloyd_persona):
        """Test persona handles special characters in text."""
        # Should be able to serialize/deserialize without issues
        json_str = json.dumps(lloyd_persona)
        roundtrip = json.loads(json_str)

        assert roundtrip == lloyd_persona
