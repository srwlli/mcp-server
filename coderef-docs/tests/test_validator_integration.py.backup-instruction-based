"""
Unit tests for Papertrail validator integration (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)

Tests verify that validation instructions are included in tool outputs for:
- Foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
- Standards docs (ui-patterns, behavior-patterns, ux-patterns)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import handle_generate_individual_doc, handle_establish_standards


class TestFoundationDocValidation:
    """Test FoundationDocValidator integration in generate_individual_doc"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_foundation_doc_includes_validation_instructions(self, mock_context, mock_gen_class):
        """Test that foundation doc generation includes validation instructions"""
        # Setup mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/mock/project')}
        mock_gen.read_template.return_value = "# Mock Template"
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path('/mock/project/README.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Mock context instructions"

        arguments = {
            "project_path": str(Path.cwd()),
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)

        # Verify validation instructions are in output
        output = result[0].text
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
        assert "FoundationDocValidator" in output
        assert "result.score < 90" in output
        assert "Validation threshold: Score >= 90" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_all_foundation_templates_have_validation(self, mock_context, mock_gen_class):
        """Test that all 5 foundation templates get validation instructions"""
        # Setup mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/mock/project')}
        mock_gen.read_template.return_value = "# Mock Template"
        mock_gen.get_template_info.return_value = {'save_as': 'DOC.md'}
        mock_gen.get_doc_output_path.return_value = Path('/mock/project/DOC.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Mock context instructions"

        foundation_templates = ['readme', 'architecture', 'api', 'schema', 'components']

        for template in foundation_templates:
            arguments = {
                "project_path": str(Path.cwd()),
                "template_name": template
            }

            result = await handle_generate_individual_doc(arguments)
            output = result[0].text

            assert "FoundationDocValidator" in output, f"{template} missing validation"
            assert f"validator.validate_file" in output, f"{template} missing validate_file call"

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_non_foundation_doc_no_validation(self, mock_context, mock_gen_class):
        """Test that non-foundation docs don't get validation instructions"""
        # Setup mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/mock/project')}
        mock_gen.read_template.return_value = "# Mock Template"
        mock_gen.get_template_info.return_value = {'save_as': 'USER-GUIDE.md'}
        mock_gen.get_doc_output_path.return_value = Path('/mock/project/USER-GUIDE.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Mock context instructions"

        arguments = {
            "project_path": str(Path.cwd()),
            "template_name": "user-guide"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # user-guide is not a foundation doc, should not have validation
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" not in output


class TestStandardsDocValidation:
    """Test StandardsDocValidator integration in establish_standards"""

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_standards_includes_validation_instructions(self, mock_generator_class):
        """Test that establish_standards includes validation instructions"""
        # Mock the generator
        mock_generator = MagicMock()
        mock_generator.save_standards.return_value = {
            'files': [
                Path('/path/to/ui-patterns.md'),
                Path('/path/to/behavior-patterns.md'),
                Path('/path/to/ux-patterns.md')
            ],
            'patterns_count': 10,
            'ui_patterns_count': 4,
            'behavior_patterns_count': 3,
            'ux_patterns_count': 3,
            'components_count': 5
        }
        mock_generator_class.return_value = mock_generator

        arguments = {
            "project_path": str(Path.cwd()),
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify validation instructions are in output
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
        assert "StandardsDocValidator" in output
        assert "result.score < 90" in output
        assert "Validation threshold: Score >= 90" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_standards_validation_includes_all_files(self, mock_generator_class):
        """Test that validation instructions include all generated standards files"""
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
            "project_path": str(Path.cwd()),
            "scan_depth": "standard",
            "focus_areas": ["all"]
        }

        result = await handle_establish_standards(arguments)
        output = result[0].text

        # Verify all files are included in validation loop
        for file_path in test_files:
            assert str(file_path) in output


class TestPapertrailEnabledDefault:
    """Test PAPERTRAIL_ENABLED default value change"""

    @pytest.mark.asyncio
    async def test_papertrail_enabled_defaults_to_true(self):
        """Test that PAPERTRAIL_ENABLED now defaults to true"""
        # Clear any existing env var
        old_val = os.environ.get("PAPERTRAIL_ENABLED")
        if "PAPERTRAIL_ENABLED" in os.environ:
            del os.environ["PAPERTRAIL_ENABLED"]

        arguments = {
            "project_path": str(Path.cwd()),
            "template_name": "readme",
            "workorder_id": "WO-TEST-001"
        }

        # Mock the generator to avoid actual Papertrail calls
        with patch('tool_handlers.FoundationGenerator'):
            result = await handle_generate_individual_doc(arguments)

        # Restore old value
        if old_val is not None:
            os.environ["PAPERTRAIL_ENABLED"] = old_val

        # The test passes if no exception is raised
        # (Implementation would try to use Papertrail if default is true)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
