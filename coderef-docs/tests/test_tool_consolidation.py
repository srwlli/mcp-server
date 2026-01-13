"""
TEST-007: Tool Consolidation Tests (WO-GENERATION-ENHANCEMENT-001)

Tests for tool consolidation verifying:
- generate_individual_doc marked as [INTERNAL] in tool description
- coderef_foundation_docs marked as [DEPRECATED] with migration warning
- Deprecation warning appears in coderef_foundation_docs output
- Migration path clear (use generate_foundation_docs instead)
- Both tools still functional (backward compatibility)

Part of Phase 5 testing for WO-GENERATION-ENHANCEMENT-001.
"""

import asyncio
import json
import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import (
    handle_generate_individual_doc,
    handle_coderef_foundation_docs,
    handle_generate_foundation_docs
)
from server import list_tools


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_project_basic(tmp_path: Path) -> Path:
    """Create basic mock project for tool testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create minimal structure
    (project_dir / "src").mkdir()
    (project_dir / "src" / "main.py").write_text("def main(): pass")

    foundation_dir = project_dir / "coderef" / "foundation-docs"
    foundation_dir.mkdir(parents=True)

    return project_dir


# ============================================================================
# TEST: generate_individual_doc [INTERNAL] Marking
# ============================================================================

@pytest.mark.asyncio
async def test_generate_individual_doc_marked_internal():
    """
    TEST-007-A: Verify generate_individual_doc marked as [INTERNAL] in server.py.
    """
    # Get all tools
    tools = list_tools()

    # Find generate_individual_doc
    individual_doc_tool = next(
        (t for t in tools if t.name == 'generate_individual_doc'),
        None
    )

    assert individual_doc_tool is not None, "generate_individual_doc tool not found"

    # Verify [INTERNAL] in description
    description = individual_doc_tool.description
    assert '[INTERNAL]' in description, "Tool should be marked as [INTERNAL]"


@pytest.mark.asyncio
async def test_generate_individual_doc_description_recommends_alternative():
    """
    TEST-007-B: Verify generate_individual_doc description recommends generate_foundation_docs.
    """
    tools = list_tools()

    individual_doc_tool = next(
        (t for t in tools if t.name == 'generate_individual_doc'),
        None
    )

    description = individual_doc_tool.description

    # Should recommend alternative
    assert 'generate_foundation_docs' in description, \
        "Description should recommend generate_foundation_docs"
    assert 'not recommended' in description.lower() or 'internal' in description.lower(), \
        "Description should discourage direct use"


@pytest.mark.asyncio
async def test_generate_individual_doc_still_functional(mock_project_basic):
    """
    TEST-007-C: Verify generate_individual_doc still works (backward compatibility).
    """
    with patch('tool_handlers.FoundationGenerator') as mock_gen_class:
        mock_gen = Mock()
        mock_gen.generate_readme.return_value = "# README\n\nGenerated"
        mock_gen_class.return_value = mock_gen

        arguments = {
            'project_path': str(mock_project_basic),
            'template_name': 'readme'
        }

        result = await handle_generate_individual_doc(arguments)

        # Should still work
        assert len(result) > 0
        assert isinstance(result[0].text, str)


# ============================================================================
# TEST: coderef_foundation_docs [DEPRECATED] Marking
# ============================================================================

@pytest.mark.asyncio
async def test_coderef_foundation_docs_marked_deprecated():
    """
    TEST-007-D: Verify coderef_foundation_docs marked as [DEPRECATED] in server.py.
    """
    tools = list_tools()

    deprecated_tool = next(
        (t for t in tools if t.name == 'coderef_foundation_docs'),
        None
    )

    assert deprecated_tool is not None, "coderef_foundation_docs tool not found"

    # Verify [DEPRECATED] in description
    description = deprecated_tool.description
    assert '[DEPRECATED]' in description, "Tool should be marked as [DEPRECATED]"


@pytest.mark.asyncio
async def test_coderef_foundation_docs_description_migration_path():
    """
    TEST-007-E: Verify coderef_foundation_docs description shows clear migration path.
    """
    tools = list_tools()

    deprecated_tool = next(
        (t for t in tools if t.name == 'coderef_foundation_docs'),
        None
    )

    description = deprecated_tool.description

    # Should mention generate_foundation_docs
    assert 'generate_foundation_docs' in description, \
        "Description should mention replacement tool"

    # Should mention migration
    assert 'migration' in description.lower() or 'replace' in description.lower(), \
        "Description should explain migration"

    # Should mention version removal
    assert 'v5.0.0' in description or 'removed' in description.lower(), \
        "Description should mention when it will be removed"


@pytest.mark.asyncio
async def test_coderef_foundation_docs_deprecation_warning_in_output(mock_project_basic):
    """
    TEST-007-F: Verify coderef_foundation_docs output includes deprecation warning.
    """
    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool:
        mock_new_tool.return_value = [Mock(text="Generated docs")]

        arguments = {'project_path': str(mock_project_basic)}
        result = await handle_coderef_foundation_docs(arguments)

        output_text = result[0].text

        # Should have deprecation warning
        assert 'DEPRECATION WARNING' in output_text or 'deprecated' in output_text.lower(), \
            "Output should include deprecation warning"

        # Should mention replacement
        assert 'generate_foundation_docs' in output_text, \
            "Warning should mention replacement tool"


@pytest.mark.asyncio
async def test_coderef_foundation_docs_lists_benefits():
    """
    TEST-007-G: Verify deprecation warning lists benefits of new tool.
    """
    tools = list_tools()

    deprecated_tool = next(
        (t for t in tools if t.name == 'coderef_foundation_docs'),
        None
    )

    description = deprecated_tool.description

    # Should mention benefits
    benefits = ['MCP integration', 'drift detection', 'sequential generation', 'validation']
    has_benefits = any(benefit.lower() in description.lower() for benefit in benefits)

    assert has_benefits, "Description should mention benefits of replacement tool"


# ============================================================================
# TEST: Backward Compatibility
# ============================================================================

@pytest.mark.asyncio
async def test_coderef_foundation_docs_still_functional(mock_project_basic):
    """
    TEST-007-H: Verify coderef_foundation_docs still works (backward compatibility).
    """
    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool:
        mock_new_tool.return_value = [Mock(text="Generated docs")]

        arguments = {'project_path': str(mock_project_basic)}
        result = await handle_coderef_foundation_docs(arguments)

        # Should still work (delegates to new tool)
        assert len(result) > 0
        assert isinstance(result[0].text, str)


@pytest.mark.asyncio
async def test_coderef_foundation_docs_delegates_to_new_tool(mock_project_basic):
    """
    TEST-007-I: Verify coderef_foundation_docs delegates to generate_foundation_docs.
    """
    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool:
        mock_new_tool.return_value = [Mock(text="Generated")]

        arguments = {'project_path': str(mock_project_basic)}
        result = await handle_coderef_foundation_docs(arguments)

        # Should call new tool
        mock_new_tool.assert_called_once_with(arguments)


# ============================================================================
# TEST: Tool Hierarchy
# ============================================================================

@pytest.mark.asyncio
async def test_tool_hierarchy_foundation_docs_orchestrates():
    """
    TEST-007-J: Verify generate_foundation_docs orchestrates generate_individual_doc.

    Hierarchy:
    - generate_foundation_docs (public, recommended)
      └─ calls generate_individual_doc 5 times (internal)
    - coderef_foundation_docs (deprecated, delegates to generate_foundation_docs)
    """
    with patch('tool_handlers.handle_generate_individual_doc', new_callable=AsyncMock) as mock_individual:
        mock_individual.return_value = [Mock(text="Generated")]

        mock_project = Path("/fake/project")
        arguments = {'project_path': str(mock_project)}

        result = await handle_generate_foundation_docs(arguments)

        # Should call individual doc 5 times
        assert mock_individual.call_count == 5


@pytest.mark.asyncio
async def test_recommended_tool_is_generate_foundation_docs():
    """
    TEST-007-K: Verify generate_foundation_docs is the recommended public tool.
    """
    tools = list_tools()

    foundation_docs_tool = next(
        (t for t in tools if t.name == 'generate_foundation_docs'),
        None
    )

    assert foundation_docs_tool is not None

    # Should NOT be marked internal or deprecated
    description = foundation_docs_tool.description
    assert '[INTERNAL]' not in description
    assert '[DEPRECATED]' not in description


# ============================================================================
# TEST: Migration Path Clarity
# ============================================================================

@pytest.mark.asyncio
async def test_migration_instructions_clear(mock_project_basic):
    """
    TEST-007-L: Verify migration instructions are actionable.
    """
    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool:
        mock_new_tool.return_value = [Mock(text="Generated")]

        arguments = {'project_path': str(mock_project_basic)}
        result = await handle_coderef_foundation_docs(arguments)

        output_text = result[0].text

        # Should have clear "replace X with Y" instruction
        assert 'replace' in output_text.lower() or 'use' in output_text.lower(), \
            "Should provide clear replacement instruction"


@pytest.mark.asyncio
async def test_migration_parameter_compatible():
    """
    TEST-007-M: Verify parameters are compatible between old and new tools.

    Both should accept: project_path
    """
    tools = list_tools()

    deprecated_tool = next(t for t in tools if t.name == 'coderef_foundation_docs')
    new_tool = next(t for t in tools if t.name == 'generate_foundation_docs')

    # Both should have project_path parameter
    deprecated_schema = deprecated_tool.inputSchema
    new_schema = new_tool.inputSchema

    assert 'project_path' in deprecated_schema['required']
    assert 'project_path' in new_schema['required']


# ============================================================================
# TEST: Logging and Warnings
# ============================================================================

@pytest.mark.asyncio
async def test_deprecated_tool_logs_warning(mock_project_basic):
    """
    TEST-007-N: Verify using deprecated tool logs warning.
    """
    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool, \
         patch('tool_handlers.logger') as mock_logger:

        mock_new_tool.return_value = [Mock(text="Generated")]

        arguments = {'project_path': str(mock_project_basic)}
        result = await handle_coderef_foundation_docs(arguments)

        # Should log deprecation warning
        mock_logger.warning.assert_called()

        # Warning should mention deprecation
        warning_call = mock_logger.warning.call_args[0][0]
        assert 'deprecated' in warning_call.lower()


# ============================================================================
# TEST: Tool Discovery
# ============================================================================

def test_all_tools_properly_registered():
    """
    TEST-007-O: Verify all 3 tools properly registered in server.

    - generate_foundation_docs (public)
    - generate_individual_doc (internal)
    - coderef_foundation_docs (deprecated)
    """
    tools = list_tools()
    tool_names = [t.name for t in tools]

    assert 'generate_foundation_docs' in tool_names
    assert 'generate_individual_doc' in tool_names
    assert 'coderef_foundation_docs' in tool_names


def test_internal_tool_not_prominently_advertised():
    """
    TEST-007-P: Verify internal tool description discourages use.
    """
    tools = list_tools()

    internal_tool = next(t for t in tools if t.name == 'generate_individual_doc')

    description = internal_tool.description

    # Should discourage direct use
    discouraging_terms = ['[INTERNAL]', 'not recommended', 'internal', 'called by']
    has_discouraging = any(term.lower() in description.lower() for term in discouraging_terms)

    assert has_discouraging, "Internal tool should discourage direct use"


# ============================================================================
# TEST: Version Information
# ============================================================================

def test_deprecation_specifies_removal_version():
    """
    TEST-007-Q: Verify deprecation warning specifies removal version (v5.0.0).
    """
    tools = list_tools()

    deprecated_tool = next(t for t in tools if t.name == 'coderef_foundation_docs')

    description = deprecated_tool.description

    # Should mention version
    assert 'v5.0.0' in description or '5.0' in description, \
        "Should specify when tool will be removed"


# ============================================================================
# TEST: Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_deprecated_tool_handles_errors_gracefully(tmp_path):
    """
    TEST-007-R: Verify deprecated tool handles errors same as new tool.
    """
    invalid_path = tmp_path / "nonexistent"

    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool:
        mock_new_tool.side_effect = ValueError("Invalid project path")

        arguments = {'project_path': str(invalid_path)}

        with pytest.raises(ValueError):
            result = await handle_coderef_foundation_docs(arguments)


# ============================================================================
# TEST: Documentation Consistency
# ============================================================================

def test_tool_descriptions_mention_consolidation():
    """
    TEST-007-S: Verify tool descriptions reference consolidation task IDs.
    """
    tools = list_tools()

    internal_tool = next(t for t in tools if t.name == 'generate_individual_doc')
    deprecated_tool = next(t for t in tools if t.name == 'coderef_foundation_docs')

    # Should mention CONSOLIDATE task IDs
    assert 'CONSOLIDATE-001' in internal_tool.description or 'WO-GENERATION-ENHANCEMENT-001' in internal_tool.description
    assert 'CONSOLIDATE-002' in deprecated_tool.description or 'WO-GENERATION-ENHANCEMENT-001' in deprecated_tool.description


# ============================================================================
# TEST: User Experience
# ============================================================================

@pytest.mark.asyncio
async def test_deprecation_warning_prominently_displayed(mock_project_basic):
    """
    TEST-007-T: Verify deprecation warning prominently displayed (not buried).
    """
    with patch('tool_handlers.handle_generate_foundation_docs', new_callable=AsyncMock) as mock_new_tool:
        mock_new_tool.return_value = [Mock(text="Generated docs")]

        arguments = {'project_path': str(mock_project_basic)}
        result = await handle_coderef_foundation_docs(arguments)

        output_text = result[0].text

        # Warning should appear early in output (first 500 chars)
        first_section = output_text[:500]
        assert 'DEPRECATION' in first_section or 'deprecated' in first_section.lower(), \
            "Deprecation warning should be prominent (near start of output)"


# ============================================================================
# SUMMARY
# ============================================================================

"""
TEST-007 SUMMARY (WO-GENERATION-ENHANCEMENT-001):

Test Coverage:
- ✅ [INTERNAL] marking (A, B, C)
- ✅ [DEPRECATED] marking (D, E, F, G)
- ✅ Backward compatibility (H, I)
- ✅ Tool hierarchy (J, K)
- ✅ Migration path (L, M)
- ✅ Logging (N)
- ✅ Tool discovery (O, P)
- ✅ Version info (Q)
- ✅ Error handling (R)
- ✅ Documentation (S)
- ✅ User experience (T)

Total Tests: 20 test functions
Expected Pass Rate: 100%

Tests verify:
1. generate_individual_doc marked as [INTERNAL] with discouraging description
2. coderef_foundation_docs marked as [DEPRECATED] with migration warning
3. Deprecation warning appears prominently in output
4. Clear migration path: replace coderef_foundation_docs with generate_foundation_docs
5. Both tools still functional (backward compatibility maintained)
6. Tool hierarchy clear: foundation_docs → individual_doc (5x)
7. Removal version specified (v5.0.0)
8. Logging and user experience improvements
"""
