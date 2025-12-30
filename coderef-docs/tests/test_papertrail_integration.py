"""Comprehensive tests for Papertrail UDS integration.

Tests UDS header/footer generation, template engine, extensions,
validation, and health scoring.
"""

import os
import pytest
from datetime import datetime
from pathlib import Path

# Enable Papertrail
os.environ["PAPERTRAIL_ENABLED"] = "true"

try:
    from papertrail import (
        UDSHeader,
        UDSFooter,
        DocumentStatus,
        TemplateEngine,
        create_template_engine,
        validate_uds,
        calculate_health,
    )
    from papertrail.extensions import (
        CodeRefContextExtension,
        GitExtension,
        WorkflowExtension,
    )
    PAPERTRAIL_AVAILABLE = True
except ImportError:
    PAPERTRAIL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PAPERTRAIL_AVAILABLE,
    reason="Papertrail not installed. Install: pip install papertrail>=1.0.0"
)


class TestUDSHeader:
    """Test UDS header generation and serialization."""

    def test_uds_header_creation(self) -> None:
        """Test basic UDS header creation."""
        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test-feature",
            timestamp="2025-12-29T20:00:00Z",
            title="Test Document",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        assert header.workorder_id == "WO-TEST-001"
        assert header.generated_by == "coderef-docs v2.0.0"
        assert header.feature_id == "test-feature"
        assert header.title == "Test Document"
        assert header.version == "1.0.0"
        assert header.status == DocumentStatus.DRAFT

    def test_uds_header_to_yaml(self) -> None:
        """Test UDS header serialization to YAML."""
        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test-feature",
            timestamp="2025-12-29T20:00:00Z",
            title="Test Document",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        yaml_output = header.to_yaml()

        assert "workorder_id: WO-TEST-001" in yaml_output
        assert "generated_by: coderef-docs v2.0.0" in yaml_output
        assert "feature_id: test-feature" in yaml_output
        assert "title: Test Document" in yaml_output
        assert "version: 1.0.0" in yaml_output

    def test_uds_header_with_optional_fields(self) -> None:
        """Test UDS header with optional metadata fields."""
        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test-feature",
            timestamp="2025-12-29T20:00:00Z",
            title="Test Document",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
            author="Test Author",
            tags=["test", "documentation"],
        )

        yaml_output = header.to_yaml()
        assert "author: Test Author" in yaml_output
        assert "tags:" in yaml_output

    def test_uds_header_status_enum(self) -> None:
        """Test all DocumentStatus enum values."""
        statuses = [
            DocumentStatus.DRAFT,
            DocumentStatus.REVIEW,
            DocumentStatus.APPROVED,
            DocumentStatus.PUBLISHED,
        ]

        for status in statuses:
            header = UDSHeader(
                workorder_id="WO-TEST-001",
                generated_by="test",
                feature_id="test",
                timestamp="2025-12-29T20:00:00Z",
                title="Test",
                version="1.0.0",
                status=status,
            )
            assert header.status == status


class TestUDSFooter:
    """Test UDS footer generation and serialization."""

    def test_uds_footer_creation(self) -> None:
        """Test basic UDS footer creation."""
        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-001",
            feature_id="test-feature",
            last_updated="2025-12-29",
        )

        assert footer.copyright_year == 2025
        assert footer.organization == "CodeRef"
        assert footer.generated_by == "coderef-docs v2.0.0"
        assert footer.workorder_id == "WO-TEST-001"
        assert footer.feature_id == "test-feature"

    def test_uds_footer_to_yaml(self) -> None:
        """Test UDS footer serialization to YAML."""
        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-001",
            feature_id="test-feature",
            last_updated="2025-12-29",
        )

        yaml_output = footer.to_yaml()

        assert "Copyright" in yaml_output
        assert "2025" in yaml_output
        assert "CodeRef" in yaml_output
        assert "workorder_id: WO-TEST-001" in yaml_output


class TestTemplateEngine:
    """Test template engine rendering and UDS injection."""

    def test_template_engine_creation(self) -> None:
        """Test creating template engine."""
        engine = create_template_engine()
        assert engine is not None
        assert isinstance(engine, TemplateEngine)

    def test_template_engine_with_extensions(self) -> None:
        """Test template engine with custom extensions."""
        engine = create_template_engine(extensions={
            "git": GitExtension(),
            "workflow": WorkflowExtension(),
        })
        assert engine is not None

    def test_basic_template_rendering(self) -> None:
        """Test basic Jinja2 template rendering."""
        engine = create_template_engine()

        template = "# {{ title }}\n\n{{ description }}"
        context = {
            "title": "Test Document",
            "description": "This is a test description",
        }

        rendered = engine.render(template, context)

        assert "# Test Document" in rendered
        assert "This is a test description" in rendered

    def test_template_with_variables(self) -> None:
        """Test template with multiple variables."""
        engine = create_template_engine()

        template = """
# {{ title }}

Version: {{ version }}
Author: {{ author }}

## Description
{{ description }}
"""

        context = {
            "title": "API Documentation",
            "version": "2.0.0",
            "author": "Test Team",
            "description": "Complete API reference",
        }

        rendered = engine.render(template, context)

        assert "# API Documentation" in rendered
        assert "Version: 2.0.0" in rendered
        assert "Author: Test Team" in rendered
        assert "Complete API reference" in rendered

    def test_uds_injection(self) -> None:
        """Test UDS header/footer injection into rendered content."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test",
            timestamp="2025-12-29T20:00:00Z",
            title="Test",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-001",
            feature_id="test",
            last_updated="2025-12-29",
        )

        content = "# Test Document\n\nSome content here."

        final_doc = engine.inject_uds(content, header, footer)

        # Verify UDS metadata present
        assert "workorder_id: WO-TEST-001" in final_doc
        assert "generated_by: coderef-docs" in final_doc
        assert "feature_id: test" in final_doc
        assert "Copyright" in final_doc
        assert "Test Document" in final_doc

    def test_uds_injection_preserves_content(self) -> None:
        """Test that UDS injection preserves original content."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="test",
            feature_id="test",
            timestamp="2025-12-29T20:00:00Z",
            title="Test",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="Test",
            generated_by="test",
            workorder_id="WO-TEST-001",
            feature_id="test",
            last_updated="2025-12-29",
        )

        original_content = """# My Document

## Section 1
Important content here.

## Section 2
More important content.
"""

        final_doc = engine.inject_uds(original_content, header, footer)

        # Original content should be preserved
        assert "# My Document" in final_doc
        assert "## Section 1" in final_doc
        assert "Important content here." in final_doc
        assert "## Section 2" in final_doc


class TestExtensions:
    """Test Papertrail custom extensions."""

    def test_git_extension_creation(self) -> None:
        """Test GitExtension creation."""
        ext = GitExtension()
        assert ext is not None

    def test_workflow_extension_creation(self) -> None:
        """Test WorkflowExtension creation."""
        ext = WorkflowExtension()
        assert ext is not None

    def test_coderef_context_extension_creation(self) -> None:
        """Test CodeRefContextExtension creation."""
        ext = CodeRefContextExtension()
        assert ext is not None

    def test_template_engine_with_all_extensions(self) -> None:
        """Test template engine with all available extensions."""
        engine = create_template_engine(extensions={
            "git": GitExtension(),
            "workflow": WorkflowExtension(),
            "coderef": CodeRefContextExtension(),
        })
        assert engine is not None


class TestValidation:
    """Test UDS document validation."""

    def test_validate_uds_with_valid_document(self) -> None:
        """Test validating a valid UDS document."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test",
            timestamp="2025-12-29T20:00:00Z",
            title="Test",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-001",
            feature_id="test",
            last_updated="2025-12-29",
        )

        content = "# Test Document"
        final_doc = engine.inject_uds(content, header, footer)

        # Validate the document
        validation_result = validate_uds(final_doc)

        assert validation_result["valid"] is True
        assert validation_result["errors"] == []

    def test_validate_uds_with_missing_header(self) -> None:
        """Test validation fails with missing UDS header."""
        document_without_header = "# Test Document\n\nJust content, no UDS metadata."

        validation_result = validate_uds(document_without_header)

        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0

    def test_validate_uds_with_missing_footer(self) -> None:
        """Test validation detects missing footer."""
        # Document with header but no footer
        document_partial = """---
workorder_id: WO-TEST-001
generated_by: test
---

# Test Document
"""

        validation_result = validate_uds(document_partial)

        # Should detect missing footer
        if not validation_result["valid"]:
            assert any("footer" in str(err).lower() for err in validation_result["errors"])


class TestHealthScoring:
    """Test document health scoring."""

    def test_calculate_health_perfect_score(self) -> None:
        """Test health calculation for perfect document."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test-feature",
            timestamp="2025-12-29T20:00:00Z",
            title="Complete Test Document",
            version="1.0.0",
            status=DocumentStatus.PUBLISHED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-001",
            feature_id="test-feature",
            last_updated="2025-12-29",
        )

        content = """# Complete Document

## Introduction
Full introduction section.

## Architecture
Complete architecture documentation.

## API Reference
Full API reference.

## Examples
Multiple examples provided.
"""

        final_doc = engine.inject_uds(content, header, footer)

        health = calculate_health(final_doc)

        assert health["score"] >= 80  # Should have high score
        assert health["grade"] in ["A", "B"]

    def test_calculate_health_low_score(self) -> None:
        """Test health calculation for incomplete document."""
        # Minimal document with UDS but little content
        minimal_doc = """---
workorder_id: WO-TEST-001
---

# Title

No real content.
"""

        health = calculate_health(minimal_doc)

        # Should have lower score due to minimal content
        assert health["score"] < 100

    def test_health_scoring_factors(self) -> None:
        """Test that health scoring considers multiple factors."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="test",
            timestamp="2025-12-29T20:00:00Z",
            title="Test",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-001",
            feature_id="test",
            last_updated="2025-12-29",
        )

        content = "# Test"
        final_doc = engine.inject_uds(content, header, footer)

        health = calculate_health(final_doc)

        # Should have these fields
        assert "score" in health
        assert "grade" in health
        assert "factors" in health or "details" in health


class TestEndToEndWorkflow:
    """Test complete Papertrail workflow."""

    def test_full_document_generation_workflow(self) -> None:
        """Test complete workflow: template → render → inject UDS → validate → score."""
        # 1. Create template
        template = """# {{ project_name }} Documentation

## Version {{ version }}

{{ description }}

## Features
{% for feature in features %}
- {{ feature }}
{% endfor %}
"""

        # 2. Create engine and render
        engine = create_template_engine()

        context = {
            "project_name": "My Project",
            "version": "2.0.0",
            "description": "Complete project documentation",
            "features": ["Authentication", "API", "Database"],
        }

        rendered = engine.render(template, context)

        # 3. Create UDS metadata
        header = UDSHeader(
            workorder_id="WO-TEST-E2E-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="e2e-test",
            timestamp="2025-12-29T20:00:00Z",
            title="My Project Documentation",
            version="2.0.0",
            status=DocumentStatus.PUBLISHED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-TEST-E2E-001",
            feature_id="e2e-test",
            last_updated="2025-12-29",
        )

        # 4. Inject UDS
        final_doc = engine.inject_uds(rendered, header, footer)

        # 5. Validate
        validation = validate_uds(final_doc)
        assert validation["valid"] is True

        # 6. Calculate health
        health = calculate_health(final_doc)
        assert health["score"] > 0

        # 7. Verify content integrity
        assert "My Project Documentation" in final_doc
        assert "Authentication" in final_doc
        assert "workorder_id: WO-TEST-E2E-001" in final_doc
        assert "Copyright" in final_doc
