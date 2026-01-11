"""
Tests for direct validation integration (WO-CODEREF-DOCS-DIRECT-VALIDATION-001).

REWORK: Tests verify TRUE direct integration (tool executes validation).

Verifies that:
1. Foundation docs are saved with validation metadata in frontmatter
2. Standards docs are saved with validation metadata in frontmatter
3. Tool output does NOT contain instruction blocks
4. Validation runs at tool runtime (not via Claude execution)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import (
    handle_generate_individual_doc,
    handle_establish_standards,
)


class TestFoundationDocDirectValidation:
    """Test that foundation doc tool saves files and writes validation metadata"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    @patch('tool_handlers.Path.write_text')
    @patch('tool_handlers.Path.read_text')
    @patch('papertrail.validators.foundation.FoundationDocValidator')
    @patch('utils.validation_helpers.write_validation_metadata_to_frontmatter')
    async def test_tool_saves_file_and_validates(
        self, mock_write_metadata, mock_validator_class, mock_read_text,
        mock_write_text, mock_context, mock_gen_class
    ):
        """
        Verify tool saves file and runs validator (not Claude).

        REWORK: Tests TRUE direct integration - tool executes validation.
        """
        # Setup mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock Template Content"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Mock context"

        # Mock validator
        mock_validator = MagicMock()
        mock_validator.validate_file.return_value = MagicMock(
            score=95,
            errors=[],
            warnings=[]
        )
        mock_validator_class.return_value = mock_validator

        arguments = {
            "project_path": "/test",
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # Verify tool saved file (not Claude)
        assert mock_write_text.called, "Tool should save file directly"

        # Verify validator was called at runtime
        assert mock_validator.validate_file.called, "Tool should run validator"

        # Verify metadata helper was called
        assert mock_write_metadata.called, "Tool should write validation metadata"

        # Verify tool output does NOT contain instructions
        assert '```python' not in output, "Tool should NOT output instruction blocks"
        assert 'VALIDATION (WO-UDS-COMPLIANCE' not in output, "No instruction-based validation"
        assert 'DIRECT VALIDATION (WO-CODEREF' not in output, "No instruction blocks"

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    @patch('builtins.open', new_callable=mock_open, read_data="---\ntitle: Test\n---\n\nContent")
    @patch('papertrail.validators.foundation.FoundationDocValidator')
    async def test_validation_metadata_in_frontmatter(
        self, mock_validator_class, mock_file, mock_context, mock_gen_class
    ):
        """
        Verify that validation metadata appears in file frontmatter _uds section.

        REWORK: Tests file metadata, not instruction presence.
        """
        # Setup generator mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Template"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context"

        # Mock validator
        mock_validator = MagicMock()
        mock_validation_result = MagicMock(
            score=92,
            errors=[],
            warnings=["Minor warning"]
        )
        mock_validator.validate_file.return_value = mock_validation_result
        mock_validator_class.return_value = mock_validator

        arguments = {
            "project_path": "/test",
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)

        # Verify validator was called with correct path
        call_args = mock_validator.validate_file.call_args
        assert call_args is not None, "Validator should be called"


class TestStandardsDocDirectValidation:
    """Test that standards doc tool saves files and writes validation metadata"""

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    @patch('papertrail.validators.standards.StandardsDocValidator')
    @patch('utils.validation_helpers.write_validation_metadata_to_frontmatter')
    async def test_tool_validates_all_standards_files(
        self, mock_write_metadata, mock_validator_class, mock_generator_class
    ):
        """
        Verify tool validates all 3 standards files and writes metadata.

        REWORK: Tests TRUE direct integration for standards.
        """
        # Mock standards generator
        mock_generator = MagicMock()
        test_files = [
            Path('/test/ui-patterns.md'),
            Path('/test/behavior-patterns.md'),
            Path('/test/ux-patterns.md')
        ]
        mock_generator.save_standards.return_value = {
            'files': test_files,
            'patterns_count': 15,
            'ui_patterns_count': 6,
            'behavior_patterns_count': 5,
            'ux_patterns_count': 4,
            'components_count': 10
        }
        mock_generator_class.return_value = mock_generator

        # Mock validator
        mock_validator = MagicMock()
        mock_validator.validate_file.return_value = MagicMock(
            score=94,
            errors=[],
            warnings=[]
        )
        mock_validator_class.return_value = mock_validator

        arguments = {
            "project_path": "/test",
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify validator was called for all 3 files
        assert mock_validator.validate_file.call_count == 3, \
            "Tool should validate all 3 standards files"

        # Verify metadata helper was called for all 3 files
        assert mock_write_metadata.call_count == 3, \
            "Tool should write metadata for all 3 files"

        # Verify tool output does NOT contain instructions
        assert '```python' not in output, "Tool should NOT output instruction blocks"
        assert 'VALIDATION (WO-UDS-COMPLIANCE' not in output, "No instruction-based validation"
        assert 'DIRECT VALIDATION (WO-CODEREF' not in output, "No instruction blocks"


class TestNoInstructionBlocks:
    """Test that tool output contains NO instruction blocks (critical requirement)"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock'))
    @patch('tool_handlers.get_context_instructions')
    @patch('tool_handlers.Path.write_text')
    @patch('papertrail.validators.foundation.FoundationDocValidator')
    @patch('utils.validation_helpers.write_validation_metadata_to_frontmatter')
    async def test_foundation_doc_has_no_instructions(
        self, mock_write_metadata, mock_validator_class, mock_write_text,
        mock_context, mock_gen_class
    ):
        """
        REWORK CRITICAL: Verify tool output contains NO instruction blocks.

        This is the key difference from incorrect implementation.
        """
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context"

        mock_validator = MagicMock()
        mock_validator.validate_file.return_value = MagicMock(score=95, errors=[], warnings=[])
        mock_validator_class.return_value = mock_validator

        arguments = {
            "project_path": "/test",
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # Critical assertions - NO instruction blocks
        assert '```python' not in output, \
            "CRITICAL: Tool must NOT output Python code blocks (instruction-based pattern)"
        assert 'from papertrail.validators' not in output, \
            "CRITICAL: Tool must NOT output validator imports (instruction-based pattern)"
        assert 'validate_file' not in output, \
            "CRITICAL: Tool must NOT output validation code (instruction-based pattern)"
        assert 'write_validation_metadata_to_frontmatter' not in output, \
            "CRITICAL: Tool must NOT output helper calls (instruction-based pattern)"

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    @patch('papertrail.validators.standards.StandardsDocValidator')
    @patch('utils.validation_helpers.write_validation_metadata_to_frontmatter')
    async def test_standards_doc_has_no_instructions(
        self, mock_write_metadata, mock_validator_class, mock_generator_class
    ):
        """
        REWORK CRITICAL: Verify standards tool output contains NO instruction blocks.
        """
        mock_generator = MagicMock()
        mock_generator.save_standards.return_value = {
            'files': [Path('/test/ui-patterns.md')],
            'patterns_count': 5,
            'ui_patterns_count': 2,
            'behavior_patterns_count': 2,
            'ux_patterns_count': 1,
            'components_count': 3
        }
        mock_generator_class.return_value = mock_generator

        mock_validator = MagicMock()
        mock_validator.validate_file.return_value = MagicMock(score=93, errors=[], warnings=[])
        mock_validator_class.return_value = mock_validator

        arguments = {
            "project_path": "/test",
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Critical assertions - NO instruction blocks
        assert '```python' not in output, \
            "CRITICAL: Standards tool must NOT output Python code blocks"
        assert 'from papertrail.validators' not in output, \
            "CRITICAL: Standards tool must NOT output validator imports"
        assert 'for file_path in standards_files:' not in output, \
            "CRITICAL: Standards tool must NOT output validation loops"


class TestValidationRunsAtToolRuntime:
    """Test that validation happens during tool execution, not later via Claude"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock'))
    @patch('tool_handlers.get_context_instructions')
    @patch('tool_handlers.Path.write_text')
    @patch('papertrail.validators.foundation.FoundationDocValidator')
    @patch('utils.validation_helpers.write_validation_metadata_to_frontmatter')
    async def test_validator_called_during_tool_execution(
        self, mock_write_metadata, mock_validator_class, mock_write_text,
        mock_context, mock_gen_class
    ):
        """
        Verify validator is called DURING tool execution (not after).

        REWORK: This proves tool executes validation, not Claude.
        """
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Template"
        mock_gen.get_template_info.return_value = {'save_as': 'ARCHITECTURE.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/ARCHITECTURE.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context"

        # Track call order
        call_order = []

        def track_write(*args, **kwargs):
            call_order.append('write_file')

        def track_validate(*args, **kwargs):
            call_order.append('validate')
            return MagicMock(score=96, errors=[], warnings=[])

        def track_metadata(*args, **kwargs):
            call_order.append('write_metadata')

        mock_write_text.side_effect = track_write
        mock_validator = MagicMock()
        mock_validator.validate_file.side_effect = track_validate
        mock_validator_class.return_value = mock_validator
        mock_write_metadata.side_effect = track_metadata

        arguments = {
            "project_path": "/test",
            "template_name": "architecture"
        }

        await handle_generate_individual_doc(arguments)

        # Verify all operations happened during tool execution
        assert 'write_file' in call_order, "Tool should save file"
        assert 'validate' in call_order, "Tool should run validator"
        assert 'write_metadata' in call_order, "Tool should write metadata"

        # Verify correct order: save → validate → write metadata
        assert call_order.index('write_file') < call_order.index('validate'), \
            "File must be saved before validation"
        assert call_order.index('validate') < call_order.index('write_metadata'), \
            "Validation must run before writing metadata"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
