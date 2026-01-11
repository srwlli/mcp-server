"""
Tests for direct validation integration (WO-CODEREF-DOCS-DIRECT-VALIDATION-001).

Verifies that:
1. Foundation docs include direct validation instructions in output
2. Standards docs include direct validation instructions in output
3. Instruction-based validation remains intact (no breaking changes)
4. Both validation patterns coexist without conflicts
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import (
    handle_generate_individual_doc,
    handle_establish_standards,
)


class TestFoundationDocDirectValidation:
    """Test direct validation integration for foundation docs"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_foundation_doc_includes_direct_validation_instructions(
        self, mock_context, mock_gen_class
    ):
        """
        Test that foundation doc generation includes direct validation instructions.

        Verifies WO-CODEREF-DOCS-DIRECT-VALIDATION-001 implementation for README.
        """
        # Setup mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock Template"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Mock context"

        arguments = {
            "project_path": "/test",
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # Verify direct validation block present
        assert "DIRECT VALIDATION (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)" in output
        assert "from utils.validation_helpers import write_validation_metadata_to_frontmatter" in output
        assert "write_validation_metadata_to_frontmatter(file_path, validation_result)" in output
        assert "This writes validation_score, validation_errors, validation_warnings to frontmatter _uds section" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_all_foundation_templates_have_direct_validation(
        self, mock_context, mock_gen_class
    ):
        """
        Test that all 5 foundation templates include direct validation instructions.

        Tests: readme, architecture, api, schema, components
        """
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock"
        mock_gen.get_template_info.return_value = {'save_as': 'DOC.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/DOC.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context"

        foundation_templates = ['readme', 'architecture', 'api', 'schema', 'components']

        for template in foundation_templates:
            arguments = {
                "project_path": "/test",
                "template_name": template
            }

            result = await handle_generate_individual_doc(arguments)
            output = result[0].text

            # Each template must have direct validation
            assert "DIRECT VALIDATION (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)" in output, \
                f"{template} missing direct validation"
            assert "write_validation_metadata_to_frontmatter" in output, \
                f"{template} missing helper import"


class TestStandardsDocDirectValidation:
    """Test direct validation integration for standards docs"""

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_standards_includes_direct_validation_instructions(
        self, mock_generator_class
    ):
        """
        Test that standards generation includes direct validation instructions.

        Verifies WO-CODEREF-DOCS-DIRECT-VALIDATION-001 implementation for standards docs.
        """
        # Mock standards generator
        mock_generator = MagicMock()
        mock_generator.save_standards.return_value = {
            'files': [
                Path('/test/coderef/standards/ui-patterns.md'),
                Path('/test/coderef/standards/behavior-patterns.md'),
                Path('/test/coderef/standards/ux-patterns.md')
            ],
            'patterns_count': 15,
            'ui_patterns_count': 6,
            'behavior_patterns_count': 5,
            'ux_patterns_count': 4,
            'components_count': 10
        }
        mock_generator_class.return_value = mock_generator

        arguments = {
            "project_path": "/test",
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify direct validation block present
        assert "DIRECT VALIDATION (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)" in output
        assert "from utils.validation_helpers import write_validation_metadata_to_frontmatter" in output
        assert "write_validation_metadata_to_frontmatter(file_path, validation_result)" in output
        assert "This writes validation_score, validation_errors, validation_warnings to frontmatter _uds section" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_standards_validation_includes_all_files(
        self, mock_generator_class
    ):
        """
        Test that direct validation instructions include all 3 standards files.
        """
        mock_generator = MagicMock()
        test_files = [
            Path('/test/ui-patterns.md'),
            Path('/test/behavior-patterns.md'),
            Path('/test/ux-patterns.md')
        ]
        mock_generator.save_standards.return_value = {
            'files': test_files,
            'patterns_count': 10,
            'ui_patterns_count': 4,
            'behavior_patterns_count': 3,
            'ux_patterns_count': 3,
            'components_count': 5
        }
        mock_generator_class.return_value = mock_generator

        arguments = {
            "project_path": "/test",
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify all 3 files included in direct validation loop
        for file_path in test_files:
            assert str(file_path) in output


class TestInstructionBasedValidationIntact:
    """Test that instruction-based validation remains unchanged (no breaking changes)"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock'))
    @patch('tool_handlers.get_context_instructions')
    async def test_instruction_based_validation_still_outputs(
        self, mock_context, mock_gen_class
    ):
        """
        Test that instruction-based validation code still appears in tool output.

        Verifies WO-UDS-COMPLIANCE-CODEREF-DOCS-001 implementation remains intact.
        """
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context"

        arguments = {
            "project_path": "/test",
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # Verify instruction-based validation still present
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
        assert "from papertrail.validators.foundation import FoundationDocValidator" in output
        assert "result = validator.validate_file" in output
        assert "if result.score < 90:" in output
        assert "Validation threshold: Score >= 90" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_standards_instruction_based_validation_intact(
        self, mock_generator_class
    ):
        """
        Test that standards instruction-based validation remains intact.
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

        arguments = {
            "project_path": "/test",
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify instruction-based validation present
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
        assert "from papertrail.validators.standards import StandardsDocValidator" in output


class TestBothPatternsCoexist:
    """Test that both validation patterns (instruction-based + direct) coexist"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock'))
    @patch('tool_handlers.get_context_instructions')
    async def test_both_patterns_coexist_foundation_docs(
        self, mock_context, mock_gen_class
    ):
        """
        Test that both validation patterns appear in foundation doc output.

        Verifies:
        - Instruction-based validation (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)
        - Direct validation (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)
        - Both blocks present without conflicts
        """
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context"

        arguments = {
            "project_path": "/test",
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # Verify both patterns present
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output, \
            "Instruction-based validation missing"
        assert "DIRECT VALIDATION (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)" in output, \
            "Direct validation missing"

        # Verify key elements of each pattern
        # Pattern 1 (instruction-based): user transparency
        assert "After saving the document, validate it using FoundationDocValidator" in output
        assert "result = validator.validate_file" in output

        # Pattern 2 (direct): machine-readable metadata
        assert "write validation metadata to frontmatter _uds section" in output
        assert "write_validation_metadata_to_frontmatter(file_path, validation_result)" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_both_patterns_coexist_standards_docs(
        self, mock_generator_class
    ):
        """
        Test that both validation patterns appear in standards doc output.
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

        arguments = {
            "project_path": "/test",
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify both patterns present
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output, \
            "Instruction-based validation missing"
        assert "DIRECT VALIDATION (WO-CODEREF-DOCS-DIRECT-VALIDATION-001)" in output, \
            "Direct validation missing"

        # Verify key elements
        assert "Validate all standards documents using StandardsDocValidator" in output
        assert "write validation metadata to frontmatter _uds section for all standards files" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
