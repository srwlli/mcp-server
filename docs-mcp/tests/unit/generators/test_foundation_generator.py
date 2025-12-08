"""
Unit tests for FoundationGenerator.

Tests the foundation documentation generator including:
- Template reading and validation
- Workflow generation
- Generation plan creation
- Document output path handling
- Security features (path traversal prevention)

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from generators.foundation_generator import FoundationGenerator
from generators.base_generator import BaseGenerator


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestFoundationGeneratorInit:
    """Tests for FoundationGenerator initialization."""

    def test_init_with_valid_templates_dir(self, project_root):
        """Test initialization with valid templates directory."""
        templates_dir = project_root / "templates" / "power"
        generator = FoundationGenerator(templates_dir)

        assert generator.templates_dir == templates_dir

    def test_init_inherits_from_base_generator(self, project_root):
        """Test that FoundationGenerator inherits from BaseGenerator."""
        templates_dir = project_root / "templates" / "power"
        generator = FoundationGenerator(templates_dir)

        assert isinstance(generator, BaseGenerator)

    def test_foundation_templates_constant(self, project_root):
        """Test FOUNDATION_TEMPLATES class constant."""
        templates_dir = project_root / "templates" / "power"
        generator = FoundationGenerator(templates_dir)

        expected = ['readme', 'architecture', 'api', 'components', 'schema']
        assert generator.FOUNDATION_TEMPLATES == expected
        assert len(generator.FOUNDATION_TEMPLATES) == 5


# ============================================================================
# BASE GENERATOR INHERITED METHODS TESTS
# ============================================================================

class TestSanitizeTemplateName:
    """Tests for _sanitize_template_name method."""

    def test_valid_template_name(self, foundation_generator):
        """Test sanitization of valid template names."""
        assert foundation_generator._sanitize_template_name('readme') == 'readme'
        assert foundation_generator._sanitize_template_name('my-guide') == 'my-guide'
        assert foundation_generator._sanitize_template_name('test_name') == 'test_name'

    def test_invalid_template_name_path_traversal(self, foundation_generator):
        """Test rejection of path traversal attempts."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('../../../etc/passwd')

    def test_invalid_template_name_empty(self, foundation_generator):
        """Test rejection of empty template name."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('')

    def test_invalid_template_name_special_chars(self, foundation_generator):
        """Test rejection of special characters."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('template.txt')

        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('template/name')


class TestReadTemplate:
    """Tests for read_template method."""

    def test_read_existing_template(self, foundation_generator):
        """Test reading an existing template file."""
        content = foundation_generator.read_template('readme')

        assert content is not None
        assert len(content) > 0
        assert 'framework:' in content.lower() or 'purpose:' in content.lower()

    def test_read_nonexistent_template(self, foundation_generator):
        """Test reading a non-existent template."""
        with pytest.raises(FileNotFoundError, match="Template 'nonexistent' not found"):
            foundation_generator.read_template('nonexistent')

    def test_read_template_path_traversal_blocked(self, foundation_generator):
        """Test that path traversal is blocked when reading templates."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator.read_template('../../secrets')


class TestValidateProjectPath:
    """Tests for validate_project_path method."""

    def test_validate_existing_directory(self, foundation_generator, mock_project):
        """Test validation of existing directory."""
        result = foundation_generator.validate_project_path(str(mock_project))

        assert result == mock_project.resolve()
        assert result.is_dir()

    def test_validate_nonexistent_path(self, foundation_generator, tmp_path):
        """Test validation of non-existent path."""
        nonexistent = tmp_path / "does_not_exist"

        with pytest.raises(ValueError, match="does not exist"):
            foundation_generator.validate_project_path(str(nonexistent))

    def test_validate_file_not_directory(self, foundation_generator, tmp_path):
        """Test validation rejects files."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")

        with pytest.raises(ValueError, match="not a directory"):
            foundation_generator.validate_project_path(str(test_file))


class TestCreateOutputDirectory:
    """Tests for create_output_directory method."""

    def test_create_new_output_directory(self, foundation_generator, tmp_path):
        """Test creation of new output directory."""
        result = foundation_generator.create_output_directory(tmp_path)

        assert result.exists()
        assert result.is_dir()
        assert "coderef" in str(result) or "foundation-docs" in str(result)

    def test_create_output_directory_custom_subdir(self, foundation_generator, tmp_path):
        """Test creation with custom subdirectory."""
        result = foundation_generator.create_output_directory(tmp_path, "custom/subdir")

        assert result.exists()
        assert result.is_dir()
        assert result == tmp_path / "custom" / "subdir"

    def test_create_output_directory_already_exists(self, foundation_generator, tmp_path):
        """Test that existing directory is returned without error."""
        existing_dir = tmp_path / "coderef" / "foundation-docs"
        existing_dir.mkdir(parents=True)

        result = foundation_generator.create_output_directory(tmp_path)

        assert result.exists()


class TestGetTemplateInfo:
    """Tests for get_template_info method."""

    def test_get_template_info_readme(self, foundation_generator):
        """Test getting metadata for readme template."""
        info = foundation_generator.get_template_info('readme')

        assert isinstance(info, dict)
        # Should have at least save_as or purpose
        assert 'save_as' in info or 'purpose' in info

    def test_get_template_info_returns_dict(self, foundation_generator):
        """Test that get_template_info returns dictionary."""
        info = foundation_generator.get_template_info('architecture')

        assert isinstance(info, dict)


class TestGetDocOutputPath:
    """Tests for get_doc_output_path method."""

    def test_readme_goes_to_project_root(self, foundation_generator, mock_project):
        """Test that README.md is saved to project root."""
        result = foundation_generator.get_doc_output_path(mock_project, 'readme')

        assert result.parent == mock_project
        assert 'README' in str(result).upper()

    def test_my_guide_goes_to_project_root(self, foundation_generator, mock_project):
        """Test that my-guide.md is saved to project root."""
        result = foundation_generator.get_doc_output_path(mock_project, 'my-guide')

        assert result.parent == mock_project

    def test_other_docs_go_to_foundation_docs(self, foundation_generator, mock_project):
        """Test that other docs go to foundation-docs directory."""
        result = foundation_generator.get_doc_output_path(mock_project, 'architecture')

        assert 'foundation-docs' in str(result).lower() or 'coderef' in str(result).lower()

    def test_output_path_creates_directory(self, foundation_generator, tmp_path):
        """Test that output path creates necessary directories."""
        project = tmp_path / "test_project"
        project.mkdir()

        result = foundation_generator.get_doc_output_path(project, 'api')

        # Directory should be created
        assert result.parent.exists()


class TestSaveDocument:
    """Tests for save_document method."""

    def test_save_document_creates_file(self, foundation_generator, tmp_path):
        """Test saving a document creates the file."""
        content = "# Test Document\n\nThis is test content."

        result = foundation_generator.save_document(content, tmp_path, "test.md")

        assert Path(result).exists()
        assert Path(result).read_text() == content

    def test_save_document_returns_absolute_path(self, foundation_generator, tmp_path):
        """Test that save_document returns absolute path."""
        result = foundation_generator.save_document("content", tmp_path, "test.md")

        assert Path(result).is_absolute()

    def test_save_document_overwrites_existing(self, foundation_generator, tmp_path):
        """Test that saving overwrites existing file."""
        file_path = tmp_path / "existing.md"
        file_path.write_text("old content")

        foundation_generator.save_document("new content", tmp_path, "existing.md")

        assert file_path.read_text() == "new content"


class TestPrepareGeneration:
    """Tests for prepare_generation method."""

    def test_prepare_generation_returns_paths(self, foundation_generator, mock_project):
        """Test that prepare_generation returns paths dictionary."""
        result = foundation_generator.prepare_generation(str(mock_project))

        assert 'project_path' in result
        assert 'output_dir' in result
        assert result['project_path'].exists()
        assert result['output_dir'].exists()

    def test_prepare_generation_invalid_path(self, foundation_generator, tmp_path):
        """Test prepare_generation with invalid path."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(ValueError):
            foundation_generator.prepare_generation(str(nonexistent))


# ============================================================================
# FOUNDATION GENERATOR SPECIFIC METHODS TESTS
# ============================================================================

class TestGetWorkflowInfo:
    """Tests for get_workflow_info method."""

    def test_get_workflow_info_returns_list(self, foundation_generator):
        """Test that get_workflow_info returns a list."""
        result = foundation_generator.get_workflow_info()

        assert isinstance(result, list)

    def test_get_workflow_info_count(self, foundation_generator):
        """Test that workflow has 5 templates."""
        result = foundation_generator.get_workflow_info()

        assert len(result) == 5

    def test_get_workflow_info_template_names(self, foundation_generator):
        """Test that workflow contains expected template names."""
        result = foundation_generator.get_workflow_info()

        template_names = [item.get('template_name') for item in result]

        assert 'readme' in template_names
        assert 'architecture' in template_names
        assert 'api' in template_names
        assert 'components' in template_names
        assert 'schema' in template_names

    def test_get_workflow_info_structure(self, foundation_generator):
        """Test workflow item structure."""
        result = foundation_generator.get_workflow_info()

        for item in result:
            assert 'template_name' in item
            # Should either have metadata or error
            assert 'error' in item or any(
                key in item for key in ['save_as', 'purpose', 'framework']
            )

    def test_get_workflow_info_handles_missing_template(self, tmp_path):
        """Test workflow info handles missing templates gracefully."""
        # Create generator with empty templates dir
        empty_templates = tmp_path / "empty_templates"
        empty_templates.mkdir()

        generator = FoundationGenerator(empty_templates)
        result = generator.get_workflow_info()

        # Should still return 5 items, but with errors
        assert len(result) == 5
        for item in result:
            assert 'error' in item


class TestGetGenerationPlan:
    """Tests for get_generation_plan method."""

    def test_get_generation_plan_returns_string(self, foundation_generator, mock_project):
        """Test that generation plan returns a string."""
        result = foundation_generator.get_generation_plan(str(mock_project))

        assert isinstance(result, str)

    def test_get_generation_plan_contains_header(self, foundation_generator, mock_project):
        """Test that plan contains header."""
        result = foundation_generator.get_generation_plan(str(mock_project))

        assert "Foundation Documentation Generation Plan" in result

    def test_get_generation_plan_contains_project_path(self, foundation_generator, mock_project):
        """Test that plan contains project path."""
        result = foundation_generator.get_generation_plan(str(mock_project))

        assert "Project:" in result

    def test_get_generation_plan_contains_document_count(self, foundation_generator, mock_project):
        """Test that plan contains document count."""
        result = foundation_generator.get_generation_plan(str(mock_project))

        assert "5" in result or "Documents to generate" in result

    def test_get_generation_plan_contains_template_names(self, foundation_generator, mock_project):
        """Test that plan lists template names."""
        result = foundation_generator.get_generation_plan(str(mock_project))

        # Should contain at least some template references
        assert any(name.upper() in result.upper() for name in ['readme', 'api', 'architecture'])

    def test_get_generation_plan_invalid_path(self, foundation_generator, tmp_path):
        """Test generation plan with invalid path returns error message."""
        nonexistent = tmp_path / "nonexistent"

        result = foundation_generator.get_generation_plan(str(nonexistent))

        assert "Error" in result

    def test_get_generation_plan_generation_order(self, foundation_generator, mock_project):
        """Test that plan mentions generation order."""
        result = foundation_generator.get_generation_plan(str(mock_project))

        assert "Generation Order" in result or "order" in result.lower()


class TestGetTemplatesForGeneration:
    """Tests for get_templates_for_generation method."""

    def test_get_templates_returns_list(self, foundation_generator):
        """Test that get_templates_for_generation returns a list."""
        result = foundation_generator.get_templates_for_generation()

        assert isinstance(result, list)

    def test_get_templates_count(self, foundation_generator):
        """Test that 5 templates are returned."""
        result = foundation_generator.get_templates_for_generation()

        assert len(result) == 5

    def test_get_templates_structure(self, foundation_generator):
        """Test template item structure."""
        result = foundation_generator.get_templates_for_generation()

        for item in result:
            assert 'template_name' in item
            assert 'template_content' in item
            assert 'status' in item

    def test_get_templates_success_status(self, foundation_generator):
        """Test that successful templates have 'success' status."""
        result = foundation_generator.get_templates_for_generation()

        success_count = sum(1 for item in result if item['status'] == 'success')

        # Should have at least some successful templates
        assert success_count > 0

    def test_get_templates_content_not_empty(self, foundation_generator):
        """Test that successful templates have non-empty content."""
        result = foundation_generator.get_templates_for_generation()

        for item in result:
            if item['status'] == 'success':
                assert len(item['template_content']) > 0

    def test_get_templates_handles_missing_files(self, tmp_path):
        """Test handling of missing template files."""
        # Create generator with empty templates dir
        empty_templates = tmp_path / "empty_templates"
        empty_templates.mkdir()

        generator = FoundationGenerator(empty_templates)
        result = generator.get_templates_for_generation()

        # Should return 5 items with error status
        assert len(result) == 5
        for item in result:
            assert item['status'] == 'error'
            assert 'error' in item
            assert item['template_content'] == ''


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFoundationGeneratorIntegration:
    """Integration tests for FoundationGenerator."""

    def test_full_workflow(self, foundation_generator, mock_project):
        """Test complete workflow from preparation to template retrieval."""
        # Step 1: Prepare generation
        paths = foundation_generator.prepare_generation(str(mock_project))
        assert paths['project_path'].exists()
        assert paths['output_dir'].exists()

        # Step 2: Get workflow info
        workflow = foundation_generator.get_workflow_info()
        assert len(workflow) == 5

        # Step 3: Get generation plan
        plan = foundation_generator.get_generation_plan(str(mock_project))
        assert "Foundation Documentation Generation Plan" in plan

        # Step 4: Get templates
        templates = foundation_generator.get_templates_for_generation()
        assert len(templates) == 5

    def test_output_paths_for_all_templates(self, foundation_generator, mock_project):
        """Test output paths for all foundation templates."""
        root_templates = ['readme']  # my-guide is not in foundation templates
        foundation_templates = ['architecture', 'api', 'components', 'schema']

        for template_name in root_templates:
            path = foundation_generator.get_doc_output_path(mock_project, template_name)
            assert path.parent == mock_project, f"{template_name} should be in root"

        for template_name in foundation_templates:
            path = foundation_generator.get_doc_output_path(mock_project, template_name)
            assert 'foundation-docs' in str(path).lower() or 'coderef' in str(path).lower(), \
                f"{template_name} should be in foundation-docs"

    def test_save_and_read_document_cycle(self, foundation_generator, tmp_path):
        """Test saving and reading a document."""
        test_content = "# Test\n\nContent with special chars: éàü"

        saved_path = foundation_generator.save_document(
            test_content,
            tmp_path,
            "test_doc.md"
        )

        # Read back and verify
        read_content = Path(saved_path).read_text(encoding='utf-8')
        assert read_content == test_content


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestFoundationGeneratorEdgeCases:
    """Edge case tests for FoundationGenerator."""

    def test_unicode_content_handling(self, foundation_generator, tmp_path):
        """Test handling of Unicode content in documents."""
        unicode_content = "# 日本語テスト\n\n中文内容\n\n한글 텍스트"

        saved_path = foundation_generator.save_document(
            unicode_content,
            tmp_path,
            "unicode_test.md"
        )

        read_content = Path(saved_path).read_text(encoding='utf-8')
        assert read_content == unicode_content

    def test_empty_template_content(self, tmp_path):
        """Test handling of empty template file."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        # Create empty template file
        (templates_dir / "empty.txt").write_text("")

        generator = FoundationGenerator(templates_dir)
        content = generator.read_template('empty')

        assert content == ''

    def test_large_template_content(self, tmp_path):
        """Test handling of large template content."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        # Create large template (100KB)
        large_content = "x" * 100000
        (templates_dir / "large.txt").write_text(large_content)

        generator = FoundationGenerator(templates_dir)
        content = generator.read_template('large')

        assert len(content) == 100000

    def test_special_characters_in_content(self, foundation_generator, tmp_path):
        """Test special characters are preserved in documents."""
        special_content = "Code: `const x = () => { return 'test'; }`\n\n> Quote\n\n- List item"

        saved_path = foundation_generator.save_document(
            special_content,
            tmp_path,
            "special.md"
        )

        read_content = Path(saved_path).read_text()
        assert "`const x = () => { return 'test'; }`" in read_content
        assert "> Quote" in read_content


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestFoundationGeneratorSecurity:
    """Security tests for FoundationGenerator."""

    def test_path_traversal_in_template_name(self, foundation_generator):
        """Test path traversal prevention in template names."""
        malicious_names = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32',
            'template/../../../secret',
            '/etc/passwd',
            'C:\\Windows\\System32',
        ]

        for name in malicious_names:
            with pytest.raises(ValueError, match="Invalid template name"):
                foundation_generator.read_template(name)

    def test_null_byte_injection(self, foundation_generator):
        """Test null byte injection prevention."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('template\x00.txt')

    def test_template_name_with_dots(self, foundation_generator):
        """Test template name with dots is rejected."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('template.txt')

    def test_template_name_with_slashes(self, foundation_generator):
        """Test template name with slashes is rejected."""
        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('dir/template')

        with pytest.raises(ValueError, match="Invalid template name"):
            foundation_generator._sanitize_template_name('dir\\template')


# ============================================================================
# PERFORMANCE TESTS (marked for selective running)
# ============================================================================

@pytest.mark.slow
class TestFoundationGeneratorPerformance:
    """Performance tests for FoundationGenerator."""

    def test_workflow_info_performance(self, foundation_generator):
        """Test that get_workflow_info completes quickly."""
        import time

        start = time.time()
        for _ in range(10):
            foundation_generator.get_workflow_info()
        duration = time.time() - start

        # Should complete 10 iterations in under 1 second
        assert duration < 1.0

    def test_template_reading_performance(self, foundation_generator):
        """Test that template reading is fast."""
        import time

        start = time.time()
        for _ in range(50):
            foundation_generator.read_template('readme')
        duration = time.time() - start

        # Should complete 50 reads in under 1 second
        assert duration < 1.0

    def test_generation_plan_performance(self, foundation_generator, mock_project):
        """Test that generation plan creation is fast."""
        import time

        start = time.time()
        for _ in range(10):
            foundation_generator.get_generation_plan(str(mock_project))
        duration = time.time() - start

        # Should complete 10 iterations in under 2 seconds
        assert duration < 2.0
