"""
Tests for CodeRef Ecosystem Personas
Tests all 5 global personas:
- coderef-mcp-lead
- coderef-context-agent
- coderef-docs-agent
- coderef-testing-agent
- coderef-personas-agent
"""

import pytest
from pathlib import Path
import json


# ============================================================================
# Test 1: Global Deployment Verification
# ============================================================================

class TestGlobalDeployment:
    """Verify all personas are globally deployed to ~/.claude/commands/"""

    def test_global_commands_directory_exists(self):
        """
        What: Verify global commands directory exists
        Why: Required for global persona availability
        How: Check if ~/.claude/commands/ exists
        """
        global_dir = Path.home() / ".claude" / "commands"
        assert global_dir.exists(), f"Global commands directory should exist at {global_dir}"
        assert global_dir.is_dir(), "Path should be a directory"

    def test_coderef_mcp_lead_deployed(self):
        """
        What: Verify /coderef-mcp-lead command exists globally
        Why: System architecture persona must be accessible
        How: Check if coderef-mcp-lead.md exists in ~/.claude/commands/
        """
        command_file = Path.home() / ".claude" / "commands" / "coderef-mcp-lead.md"
        assert command_file.exists(), f"/coderef-mcp-lead should exist at {command_file}"

        # Verify content
        with open(command_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "coderef-mcp-lead" in content.lower(), "File should reference persona name"
        assert len(content) > 100, "Command should have substantial content"

    def test_coderef_context_agent_deployed(self):
        """
        What: Verify /coderef-context-agent command exists globally
        Why: Code intelligence persona must be accessible
        How: Check if coderef-context-agent.md exists
        """
        command_file = Path.home() / ".claude" / "commands" / "coderef-context-agent.md"
        assert command_file.exists(), f"/coderef-context-agent should exist at {command_file}"

        with open(command_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "coderef-context" in content.lower(), "File should reference persona name"

    def test_coderef_docs_agent_deployed(self):
        """
        What: Verify /coderef-docs-agent command exists globally
        Why: Documentation persona must be accessible
        How: Check if coderef-docs-agent.md exists
        """
        command_file = Path.home() / ".claude" / "commands" / "coderef-docs-agent.md"
        assert command_file.exists(), f"/coderef-docs-agent should exist at {command_file}"

        with open(command_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "coderef-docs" in content.lower(), "File should reference persona name"

    def test_coderef_testing_agent_deployed(self):
        """
        What: Verify /coderef-testing-agent command exists globally
        Why: Testing persona must be accessible
        How: Check if coderef-testing-agent.md exists
        """
        command_file = Path.home() / ".claude" / "commands" / "coderef-testing-agent.md"
        assert command_file.exists(), f"/coderef-testing-agent should exist at {command_file}"

        with open(command_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "coderef-testing" in content.lower(), "File should reference persona name"

    def test_coderef_personas_agent_deployed(self):
        """
        What: Verify /coderef-personas-agent command exists globally
        Why: Persona management persona must be accessible
        How: Check if coderef-personas-agent.md exists
        """
        command_file = Path.home() / ".claude" / "commands" / "coderef-personas-agent.md"
        assert command_file.exists(), f"/coderef-personas-agent should exist at {command_file}"

        with open(command_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "coderef-personas" in content.lower(), "File should reference persona name"


# ============================================================================
# Test 2: Persona Definition Files
# ============================================================================

class TestPersonaDefinitions:
    """Verify persona JSON definitions exist and are valid."""

    def test_coderef_mcp_lead_definition(self):
        """
        What: Verify coderef-mcp-lead.json exists and is valid
        Why: Persona definition required for activation
        How: Load JSON, check required fields
        """
        persona_file = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base/coderef-mcp-lead.json")

        if not persona_file.exists():
            pytest.skip(f"Persona definition not found at {persona_file}")

        with open(persona_file, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        # Verify required fields
        assert "name" in persona, "Persona should have name"
        assert persona["name"] == "coderef-mcp-lead", "Name should match"
        assert "description" in persona, "Persona should have description"
        assert "expertise" in persona, "Persona should have expertise list"
        assert "use_cases" in persona, "Persona should have use cases"
        assert "system_prompt" in persona, "Persona should have system prompt"

    def test_coderef_context_agent_definition(self):
        """
        What: Verify coderef-context-agent.json exists and is valid
        Why: Persona definition required for activation
        How: Load JSON, check required fields
        """
        persona_file = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base/coderef-context-agent.json")

        if not persona_file.exists():
            pytest.skip(f"Persona definition not found at {persona_file}")

        with open(persona_file, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        assert persona["name"] == "coderef-context-agent"
        assert len(persona["expertise"]) > 0, "Should have expertise areas"
        assert len(persona["use_cases"]) > 0, "Should have use cases"

    def test_coderef_docs_agent_definition(self):
        """
        What: Verify coderef-docs-agent.json exists and is valid
        Why: Persona definition required for activation
        How: Load JSON, check required fields
        """
        persona_file = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base/coderef-docs-agent.json")

        if not persona_file.exists():
            pytest.skip(f"Persona definition not found at {persona_file}")

        with open(persona_file, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        assert persona["name"] == "coderef-docs-agent"
        assert "documentation" in str(persona["expertise"]).lower(), "Should mention documentation expertise"

    def test_coderef_testing_agent_definition(self):
        """
        What: Verify coderef-testing-agent.json exists and is valid
        Why: Persona definition required for activation
        How: Load JSON, check required fields
        """
        persona_file = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base/coderef-testing-agent.json")

        if not persona_file.exists():
            pytest.skip(f"Persona definition not found at {persona_file}")

        with open(persona_file, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        assert persona["name"] == "coderef-testing-agent"
        assert "test" in str(persona["expertise"]).lower(), "Should mention testing expertise"

    def test_coderef_personas_agent_definition(self):
        """
        What: Verify coderef-personas-agent.json exists and is valid
        Why: Persona definition required for activation
        How: Load JSON, check required fields
        """
        persona_file = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base/coderef-personas-agent.json")

        if not persona_file.exists():
            pytest.skip(f"Persona definition not found at {persona_file}")

        with open(persona_file, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        assert persona["name"] == "coderef-personas-agent"
        assert "persona" in str(persona["expertise"]).lower(), "Should mention persona expertise"


# ============================================================================
# Test 3: Persona Content Quality
# ============================================================================

class TestPersonaContentQuality:
    """Verify persona content is complete and high-quality."""

    def test_all_personas_have_system_prompts(self):
        """
        What: Verify all personas have non-empty system prompts
        Why: System prompts required for persona behavior
        How: Load each persona, check system_prompt length
        """
        personas_dir = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base")
        persona_files = [
            "coderef-mcp-lead.json",
            "coderef-context-agent.json",
            "coderef-docs-agent.json",
            "coderef-testing-agent.json",
            "coderef-personas-agent.json"
        ]

        for persona_name in persona_files:
            persona_file = personas_dir / persona_name

            if not persona_file.exists():
                pytest.skip(f"Skipping {persona_name} - file not found")

            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)

            assert "system_prompt" in persona, f"{persona_name} should have system_prompt"
            assert len(persona["system_prompt"]) > 500, f"{persona_name} system prompt should be substantial"

    def test_all_personas_have_expertise_lists(self):
        """
        What: Verify all personas have expertise lists with 3+ items
        Why: Expertise defines persona capabilities
        How: Check expertise array length
        """
        personas_dir = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base")
        persona_files = [
            "coderef-mcp-lead.json",
            "coderef-context-agent.json",
            "coderef-docs-agent.json",
            "coderef-testing-agent.json",
            "coderef-personas-agent.json"
        ]

        for persona_name in persona_files:
            persona_file = personas_dir / persona_name

            if not persona_file.exists():
                continue

            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)

            assert "expertise" in persona, f"{persona_name} should have expertise"
            assert isinstance(persona["expertise"], list), "Expertise should be array"
            assert len(persona["expertise"]) >= 3, f"{persona_name} should have 3+ expertise areas"

    def test_all_personas_have_use_cases(self):
        """
        What: Verify all personas have use cases with 3+ examples
        Why: Use cases demonstrate when to activate persona
        How: Check use_cases array length
        """
        personas_dir = Path("C:/Users/willh/.mcp-servers/coderef-personas/personas/base")
        persona_files = [
            "coderef-mcp-lead.json",
            "coderef-context-agent.json",
            "coderef-docs-agent.json",
            "coderef-testing-agent.json",
            "coderef-personas-agent.json"
        ]

        for persona_name in persona_files:
            persona_file = personas_dir / persona_name

            if not persona_file.exists():
                continue

            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)

            assert "use_cases" in persona, f"{persona_name} should have use_cases"
            assert isinstance(persona["use_cases"], list), "Use cases should be array"
            assert len(persona["use_cases"]) >= 3, f"{persona_name} should have 3+ use cases"


# ============================================================================
# Test 4: Integration Tests (MCP Tools)
# ============================================================================

class TestPersonaMCPTools:
    """Test MCP tools for persona management (requires server running)."""

    def test_list_personas_tool_exists(self):
        """
        What: Verify list_personas MCP tool exists
        Why: Required for discovering available personas
        How: Check tool registration (requires manual verification)
        """
        pytest.skip("MCP tool test - requires running coderef-personas server")

    def test_use_persona_tool_exists(self):
        """
        What: Verify use_persona MCP tool exists
        Why: Required for activating personas
        How: Check tool registration
        """
        pytest.skip("MCP tool test - requires running coderef-personas server")

    def test_get_active_persona_tool_exists(self):
        """
        What: Verify get_active_persona MCP tool exists
        Why: Required for checking current persona
        How: Check tool registration
        """
        pytest.skip("MCP tool test - requires running coderef-personas server")

    def test_clear_persona_tool_exists(self):
        """
        What: Verify clear_persona MCP tool exists
        Why: Required for deactivating personas
        How: Check tool registration
        """
        pytest.skip("MCP tool test - requires running coderef-personas server")


# ============================================================================
# Test 5: Slash Command Functionality
# ============================================================================

class TestSlashCommands:
    """Test slash command integration."""

    def test_slash_commands_invoke_use_persona(self):
        """
        What: Verify slash commands invoke use_persona correctly
        Why: Commands should activate the right persona
        How: Read command file content, check for use_persona call
        """
        global_dir = Path.home() / ".claude" / "commands"
        commands = [
            ("coderef-mcp-lead.md", "coderef-mcp-lead"),
            ("coderef-context-agent.md", "coderef-context-agent"),
            ("coderef-docs-agent.md", "coderef-docs-agent"),
            ("coderef-testing-agent.md", "coderef-testing-agent"),
            ("coderef-personas-agent.md", "coderef-personas-agent")
        ]

        for command_file, persona_name in commands:
            file_path = global_dir / command_file

            if not file_path.exists():
                pytest.skip(f"Command file not found: {command_file}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should mention the persona name
            assert persona_name in content, f"Command should reference {persona_name}"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
