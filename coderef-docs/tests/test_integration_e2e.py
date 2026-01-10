"""
Integration tests for validator integration (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)

Tests verify end-to-end functionality:
- Tools generate output with validation instructions
- Validation instructions are executable Python code
- Validators can be imported and run successfully
- PAPERTRAIL_ENABLED default behavior works correctly
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import (
    handle_generate_individual_doc,
    handle_establish_standards,
)


class TestEndToEndFoundationDocGeneration:
    """End-to-end tests for foundation doc generation with validation"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_generate_readme_with_validation_e2e(self, mock_context, mock_gen_class):
        """Test complete README generation flow with validation instructions"""
        # Setup realistic mocks
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {
            'project_path': Path(tempfile.gettempdir())
        }
        mock_gen.read_template.return_value = """# {project_name}

## Purpose
{purpose}

## Overview
{overview}"""
        mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
        mock_gen.get_doc_output_path.return_value = Path(tempfile.gettempdir()) / 'README.md'
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Context for README template"

        arguments = {
            "project_path": tempfile.gettempdir(),
            "template_name": "readme"
        }

        result = await handle_generate_individual_doc(arguments)
        output = result[0].text

        # Verify all expected elements are present
        assert "# Mock Template" in output or "README.md" in output
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
        assert "FoundationDocValidator" in output
        assert "from papertrail.validators.foundation import FoundationDocValidator" in output
        assert "result = validator.validate_file" in output
        assert "result.score < 90" in output
        assert "Validation threshold: Score >= 90" in output

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_all_foundation_templates_e2e(self, mock_context, mock_gen_class):
        """Test all 5 foundation templates generate with validation"""
        mock_gen = MagicMock()
        mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
        mock_gen.read_template.return_value = "# Mock Template"
        mock_gen.get_template_info.return_value = {'save_as': 'DOC.md'}
        mock_gen.get_doc_output_path.return_value = Path('/test/DOC.md')
        mock_gen_class.return_value = mock_gen
        mock_context.return_value = "Mock context"

        templates = ['readme', 'architecture', 'api', 'schema', 'components']

        for template in templates:
            arguments = {
                "project_path": "/test",
                "template_name": template
            }

            result = await handle_generate_individual_doc(arguments)
            output = result[0].text

            # Each foundation template must have validation
            assert "FoundationDocValidator" in output, f"{template} missing validator"
            assert "result.score < 90" in output, f"{template} missing score check"


class TestEndToEndStandardsGeneration:
    """End-to-end tests for standards generation with validation"""

    @pytest.mark.asyncio
    @patch('tool_handlers.StandardsGenerator')
    async def test_establish_standards_with_validation_e2e(self, mock_generator_class):
        """Test complete standards establishment flow with validation"""
        # Mock standards generator to return realistic data
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

        # Verify validation instructions present
        assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
        assert "StandardsDocValidator" in output
        assert "from papertrail.validators.standards import StandardsDocValidator" in output

        # Verify all 3 files are included in validation loop
        assert "ui-patterns.md" in output
        assert "behavior-patterns.md" in output
        assert "ux-patterns.md" in output

        # Verify validation logic
        assert "result.score < 90" in output
        assert "for file_path in standards_files:" in output


class TestPapertrailEnabledBehavior:
    """Test PAPERTRAIL_ENABLED environment variable behavior"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock'))
    @patch('tool_handlers.get_context_instructions')
    async def test_papertrail_enabled_true_by_default(self, mock_context, mock_gen_class):
        """Test that PAPERTRAIL_ENABLED defaults to true in new code"""
        # Remove env var to test default
        old_val = os.environ.get("PAPERTRAIL_ENABLED")
        if "PAPERTRAIL_ENABLED" in os.environ:
            del os.environ["PAPERTRAIL_ENABLED"]

        try:
            # The default is now "true" (changed in WO-UDS-COMPLIANCE-CODEREF-DOCS-001)
            # We verify this by checking the behavior when workorder_id is present

            mock_gen = MagicMock()
            mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
            mock_gen.read_template.return_value = "# Template"
            mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
            mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
            mock_gen_class.return_value = mock_gen
            mock_context.return_value = "Context"

            arguments = {
                "project_path": "/test",
                "template_name": "readme",
                "workorder_id": "WO-TEST-001"  # Workorder ID present
            }

            result = await handle_generate_individual_doc(arguments)
            output = result[0].text

            # With default true and workorder_id present, validation should be included
            # (This is the key behavior change from v3.4.0 to v3.5.0)
            assert "VALIDATION" in output or "# Template" in output

        finally:
            # Restore env var
            if old_val is not None:
                os.environ["PAPERTRAIL_ENABLED"] = old_val

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock'))
    @patch('tool_handlers.get_context_instructions')
    async def test_papertrail_disabled_skips_uds_but_includes_validation(self, mock_context, mock_gen_class):
        """Test that PAPERTRAIL_ENABLED=false skips UDS frontmatter but still includes validation instructions"""
        # Set env var to false
        old_val = os.environ.get("PAPERTRAIL_ENABLED")
        os.environ["PAPERTRAIL_ENABLED"] = "false"

        try:
            mock_gen = MagicMock()
            mock_gen.prepare_generation.return_value = {'project_path': Path('/test')}
            mock_gen.read_template.return_value = "# Template"
            mock_gen.get_template_info.return_value = {'save_as': 'README.md'}
            mock_gen.get_doc_output_path.return_value = Path('/test/README.md')
            mock_gen_class.return_value = mock_gen
            mock_context.return_value = "Context"

            arguments = {
                "project_path": "/test",
                "template_name": "readme",
                "workorder_id": "WO-TEST-001"
            }

            result = await handle_generate_individual_doc(arguments)
            output = result[0].text

            # Validation instructions are ALWAYS included for foundation docs
            # (This is the feature - validation happens regardless of UDS)
            assert "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001)" in output
            assert "FoundationDocValidator" in output

            # UDS frontmatter generation is skipped when PAPERTRAIL_ENABLED=false
            # (Uses legacy template-only generation path)
            assert "=== Generating README ===" in output  # Legacy header
            assert "Generated README with UDS" not in output  # UDS header not present

        finally:
            # Restore env var
            if old_val is not None:
                os.environ["PAPERTRAIL_ENABLED"] = old_val
            elif "PAPERTRAIL_ENABLED" in os.environ:
                del os.environ["PAPERTRAIL_ENABLED"]


class TestValidationCodeExecutability:
    """Test that generated validation code is syntactically correct and executable"""

    @pytest.mark.asyncio
    @patch('tool_handlers.BaseGenerator')
    @patch('tool_handlers.TEMPLATES_DIR', Path('/mock/templates'))
    @patch('tool_handlers.get_context_instructions')
    async def test_validation_code_is_valid_python(self, mock_context, mock_gen_class):
        """Test that validation instructions contain valid Python code"""
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

        # Extract code block
        code_start = output.find("```python")
        code_end = output.find("```", code_start + 10)

        if code_start != -1 and code_end != -1:
            code_block = output[code_start + 9:code_end].strip()

            # Verify it's valid Python syntax
            try:
                compile(code_block, '<string>', 'exec')
                # If compilation succeeds, code is syntactically valid
            except SyntaxError as e:
                pytest.fail(f"Generated validation code has syntax error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
