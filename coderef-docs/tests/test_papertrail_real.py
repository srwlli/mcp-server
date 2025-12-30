"""REAL Papertrail tests based on actual API.

These tests use the actual Papertrail API as it exists,
not assumptions. All tests verified to pass.
"""

import os
import pytest
from pathlib import Path

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
    reason="Papertrail not installed"
)


class TestRealUDSHeader:
    """Test UDS header with ACTUAL API."""

    def test_create_header_minimal(self) -> None:
        """Test creating header with required fields only."""
        header = UDSHeader(
            workorder_id="WO-TEST-001",
            generated_by="test-suite v1.0.0",
            feature_id="test-feature",
            timestamp="2025-12-29T20:00:00Z",
        )

        assert header.workorder_id == "WO-TEST-001"
        assert header.generated_by == "test-suite v1.0.0"
        assert header.feature_id == "test-feature"
        assert header.timestamp == "2025-12-29T20:00:00Z"

    def test_create_header_with_optional_fields(self) -> None:
        """Test creating header with optional fields."""
        header = UDSHeader(
            workorder_id="WO-TEST-002",
            generated_by="test-suite v1.0.0",
            feature_id="test-feature",
            timestamp="2025-12-29T20:00:00Z",
            title="Test Document",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        assert header.title == "Test Document"
        assert header.version == "1.0.0"
        assert header.status == DocumentStatus.DRAFT

    def test_header_to_yaml(self) -> None:
        """Test header YAML serialization."""
        header = UDSHeader(
            workorder_id="WO-TEST-003",
            generated_by="test-suite v1.0.0",
            feature_id="test-yaml",
            timestamp="2025-12-29T20:00:00Z",
            title="YAML Test",
            version="1.0.0",
        )

        yaml = header.to_yaml()

        # Verify YAML contains key fields
        assert "workorder_id:" in yaml
        assert "WO-TEST-003" in yaml
        assert "generated_by:" in yaml
        assert "feature_id:" in yaml
        assert "test-yaml" in yaml

    def test_all_document_statuses(self) -> None:
        """Test all real DocumentStatus values."""
        statuses = [
            DocumentStatus.DRAFT,
            DocumentStatus.REVIEW,
            DocumentStatus.APPROVED,
            DocumentStatus.DEPRECATED,
        ]

        for status in statuses:
            header = UDSHeader(
                workorder_id="WO-STATUS-TEST",
                generated_by="test-suite",
                feature_id="status-test",
                timestamp="2025-12-29T20:00:00Z",
                status=status,
            )
            assert header.status == status


class TestRealUDSFooter:
    """Test UDS footer with ACTUAL API."""

    def test_create_footer_minimal(self) -> None:
        """Test creating footer with required fields."""
        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-FOOTER-001",
            feature_id="footer-test",
            last_updated="2025-12-29",
        )

        assert footer.copyright_year == 2025
        assert footer.organization == "TestOrg"
        assert footer.workorder_id == "WO-FOOTER-001"
        assert footer.feature_id == "footer-test"

    def test_footer_with_ai_assistance(self) -> None:
        """Test footer with ai_assistance flag."""
        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-FOOTER-002",
            feature_id="ai-test",
            last_updated="2025-12-29",
            ai_assistance=True,
        )

        assert footer.ai_assistance is True

    def test_footer_with_contributors(self) -> None:
        """Test footer with contributors list."""
        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-FOOTER-003",
            feature_id="contrib-test",
            last_updated="2025-12-29",
            contributors=["Alice", "Bob", "Charlie"],
        )

        assert footer.contributors == ["Alice", "Bob", "Charlie"]

    def test_footer_to_yaml(self) -> None:
        """Test footer YAML serialization."""
        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-YAML-FOOTER",
            feature_id="yaml-test",
            last_updated="2025-12-29",
        )

        yaml = footer.to_yaml()

        # Verify YAML contains key elements
        assert "Copyright" in yaml
        assert "2025" in yaml
        assert "TestOrg" in yaml
        assert "WO-YAML-FOOTER" in yaml


class TestRealTemplateEngine:
    """Test template engine with ACTUAL API."""

    def test_create_engine_basic(self) -> None:
        """Test creating basic template engine."""
        engine = create_template_engine()
        assert engine is not None
        assert isinstance(engine, TemplateEngine)

    def test_create_engine_with_extensions(self) -> None:
        """Test creating engine with extensions."""
        engine = create_template_engine(extensions={
            "git": GitExtension(),
            "workflow": WorkflowExtension(),
            "coderef": CodeRefContextExtension(),
        })
        assert engine is not None

    def test_render_simple_template(self) -> None:
        """Test rendering a simple Jinja2 template."""
        engine = create_template_engine()

        template = "# {{ title }}\n\n{{ content }}"
        context = {
            "title": "My Document",
            "content": "This is the content.",
        }

        rendered = engine.render(template, context)

        assert "# My Document" in rendered
        assert "This is the content." in rendered

    def test_render_with_loops(self) -> None:
        """Test rendering template with Jinja2 loops."""
        engine = create_template_engine()

        template = """# Features

{% for feature in features %}
- {{ feature }}
{% endfor %}
"""

        context = {
            "features": ["Auth", "API", "Database"],
        }

        rendered = engine.render(template, context)

        assert "- Auth" in rendered
        assert "- API" in rendered
        assert "- Database" in rendered


class TestRealUDSInjection:
    """Test UDS injection with ACTUAL API."""

    def test_inject_uds_basic(self) -> None:
        """Test basic UDS injection."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-INJECT-001",
            generated_by="test-suite v1.0.0",
            feature_id="inject-test",
            timestamp="2025-12-29T20:00:00Z",
            title="Injection Test",
            version="1.0.0",
            status=DocumentStatus.DRAFT,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-INJECT-001",
            feature_id="inject-test",
            last_updated="2025-12-29",
        )

        content = "# Test Document\n\nSome content here."

        result = engine.inject_uds(content, header, footer)

        # Verify UDS metadata is present
        assert "WO-INJECT-001" in result
        assert "inject-test" in result
        assert "Test Document" in result  # Original content preserved

    def test_inject_preserves_markdown(self) -> None:
        """Test that UDS injection preserves markdown structure."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-PRESERVE-001",
            generated_by="test-suite",
            feature_id="preserve-test",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite",
            workorder_id="WO-PRESERVE-001",
            feature_id="preserve-test",
            last_updated="2025-12-29",
        )

        original = """# My Project

## Section 1
Content for section 1.

## Section 2
Content for section 2.

- List item 1
- List item 2
"""

        result = engine.inject_uds(original, header, footer)

        # All original content should be present
        assert "# My Project" in result
        assert "## Section 1" in result
        assert "## Section 2" in result
        assert "- List item 1" in result


class TestRealValidation:
    """Test validation with ACTUAL API (requires doc_type)."""

    def test_validate_complete_document(self) -> None:
        """Test validating a complete UDS document."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-VALID-001",
            generated_by="test-suite v1.0.0",
            feature_id="validation-test",
            timestamp="2025-12-29T20:00:00Z",
            title="Valid Document",
            version="1.0.0",
            status=DocumentStatus.APPROVED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-VALID-001",
            feature_id="validation-test",
            last_updated="2025-12-29",
        )

        content = "# Valid Document\n\nComplete documentation."
        doc = engine.inject_uds(content, header, footer)

        # Validate with doc_type (required parameter)
        validation = validate_uds(doc, doc_type="readme")

        # Document is valid (may have warnings, but no critical errors)
        assert validation.valid is True

    def test_validate_missing_metadata(self) -> None:
        """Test validation catches missing UDS metadata."""
        doc_without_uds = "# Just Content\n\nNo UDS metadata."

        validation = validate_uds(doc_without_uds, doc_type="readme")

        # Should fail validation
        assert validation.valid is False
        assert len(validation.errors) > 0


class TestRealHealthScoring:
    """Test health scoring with ACTUAL API (requires doc_type)."""

    def test_calculate_health_good_doc(self) -> None:
        """Test health calculation for well-formed document."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-HEALTH-001",
            generated_by="test-suite v1.0.0",
            feature_id="health-test",
            timestamp="2025-12-29T20:00:00Z",
            title="Healthy Document",
            version="1.0.0",
            status=DocumentStatus.APPROVED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-HEALTH-001",
            feature_id="health-test",
            last_updated="2025-12-29",
        )

        content = """# Healthy Document

## Introduction
Complete introduction with context.

## Architecture
Detailed architecture section.

## Examples
Multiple examples provided.
"""

        doc = engine.inject_uds(content, header, footer)

        # Calculate health with doc_type (required parameter)
        health = calculate_health(doc, doc_type="readme")

        assert health.score >= 0
        assert health.score <= 100
        # Note: health object has score, not grade

    def test_calculate_health_minimal_doc(self) -> None:
        """Test health calculation for minimal document."""
        doc = """---
workorder_id: WO-MIN-001
---

# Title

Minimal content.
"""

        health = calculate_health(doc, doc_type="readme")

        # Should return valid health score
        assert 0 <= health.score <= 100


class TestRealEndToEnd:
    """Test complete real-world workflows."""

    def test_full_workflow_template_to_validated_doc(self) -> None:
        """Test: template → render → inject UDS → validate → score."""
        # 1. Create template
        template = """# {{ project_name }}

## Overview
{{ description }}

## Features
{% for feature in features %}
- {{ feature }}
{% endfor %}
"""

        # 2. Render template
        engine = create_template_engine()
        context = {
            "project_name": "MyProject",
            "description": "A great project",
            "features": ["Auth", "API", "Tests"],
        }

        rendered = engine.render(template, context)
        assert "MyProject" in rendered

        # 3. Create UDS metadata
        header = UDSHeader(
            workorder_id="WO-E2E-001",
            generated_by="test-suite v1.0.0",
            feature_id="e2e-test",
            timestamp="2025-12-29T20:00:00Z",
            title="MyProject",
            version="1.0.0",
            status=DocumentStatus.APPROVED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-E2E-001",
            feature_id="e2e-test",
            last_updated="2025-12-29",
        )

        # 4. Inject UDS
        final_doc = engine.inject_uds(rendered, header, footer)
        assert "WO-E2E-001" in final_doc

        # 5. Validate
        validation = validate_uds(final_doc, doc_type="readme")
        assert validation.valid is True

        # 6. Calculate health
        health = calculate_health(final_doc, doc_type="readme")
        assert health.score > 0

    def test_add_traceability_to_existing_doc(self) -> None:
        """Real use case: Add UDS to existing markdown."""
        existing_doc = """# Existing Documentation

This documentation was written without UDS.

## Features
- Feature A
- Feature B
"""

        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-TRACE-001",
            generated_by="test-suite v1.0.0",
            feature_id="add-traceability",
            timestamp="2025-12-29T20:00:00Z",
            title="Existing Documentation",
            version="2.0.0",
            status=DocumentStatus.REVIEW,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="test-suite v1.0.0",
            workorder_id="WO-TRACE-001",
            feature_id="add-traceability",
            last_updated="2025-12-29",
        )

        # Add UDS to existing doc
        traced_doc = engine.inject_uds(existing_doc, header, footer)

        # Verify original content preserved
        assert "Existing Documentation" in traced_doc
        assert "Feature A" in traced_doc

        # Verify traceability added
        assert "WO-TRACE-001" in traced_doc
        assert "add-traceability" in traced_doc

        # Verify it validates
        validation = validate_uds(traced_doc, doc_type="readme")
        assert validation.valid is True


class TestRealExtensions:
    """Test real Papertrail extensions."""

    def test_git_extension(self) -> None:
        """Test GitExtension creation."""
        ext = GitExtension()
        assert ext is not None

    def test_workflow_extension(self) -> None:
        """Test WorkflowExtension creation."""
        ext = WorkflowExtension()
        assert ext is not None

    def test_coderef_extension(self) -> None:
        """Test CodeRefContextExtension creation."""
        ext = CodeRefContextExtension()
        assert ext is not None

    def test_engine_with_all_extensions(self) -> None:
        """Test engine with all extensions loaded."""
        engine = create_template_engine(extensions={
            "git": GitExtension(),
            "workflow": WorkflowExtension(),
            "coderef": CodeRefContextExtension(),
        })

        assert engine is not None

        # Can still render templates
        rendered = engine.render("# {{ title }}", {"title": "Test"})
        assert "# Test" in rendered
