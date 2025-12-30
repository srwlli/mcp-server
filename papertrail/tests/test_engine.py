"""
Unit tests for template engine
"""

import pytest
from pathlib import Path
import tempfile

from papertrail.engine import TemplateEngine, create_template_engine
from papertrail.uds import UDSHeader, UDSFooter, DocumentStatus


class TestTemplateEngine:
    """Test template engine functionality"""

    def test_create_engine(self):
        """Test creating template engine"""
        engine = TemplateEngine()
        assert engine is not None

    def test_render_simple_template(self):
        """Test rendering simple template with variables"""
        engine = TemplateEngine()

        template = "# {{ title }}\n\nContent: {{ content }}"
        result = engine.render(template, {
            "title": "Test Document",
            "content": "This is test content"
        })

        assert "# Test Document" in result
        assert "Content: This is test content" in result

    def test_render_with_conditionals(self):
        """Test template with conditionals"""
        engine = TemplateEngine()

        template = """
# {{ title }}

{% if show_intro %}
## Introduction
This is the intro section.
{% endif %}

{% if not skip_conclusion %}
## Conclusion
Final notes.
{% endif %}
"""

        # With intro, with conclusion
        result1 = engine.render(template, {
            "title": "Doc",
            "show_intro": True,
            "skip_conclusion": False
        })
        assert "## Introduction" in result1
        assert "## Conclusion" in result1

        # No intro, no conclusion
        result2 = engine.render(template, {
            "title": "Doc",
            "show_intro": False,
            "skip_conclusion": True
        })
        assert "## Introduction" not in result2
        assert "## Conclusion" not in result2

    def test_render_with_loops(self):
        """Test template with loops"""
        engine = TemplateEngine()

        template = """
# Task List

{% for task in tasks %}
- {{ task.id }}: {{ task.title }}
{% endfor %}
"""

        result = engine.render(template, {
            "tasks": [
                {"id": "TASK-001", "title": "Setup"},
                {"id": "TASK-002", "title": "Implementation"},
                {"id": "TASK-003", "title": "Testing"}
            ]
        })

        assert "- TASK-001: Setup" in result
        assert "- TASK-002: Implementation" in result
        assert "- TASK-003: Testing" in result

    def test_inject_uds_header_only(self):
        """Test injecting UDS header only"""
        engine = TemplateEngine()

        header = UDSHeader(
            workorder_id="WO-TEST-DOCS-001",
            generated_by="papertrail v1.0.0",
            feature_id="test",
            timestamp="2025-12-29T10:00:00Z"
        )

        content = "# Test Document\n\nContent here."

        result = engine.inject_uds(content, header)

        assert "workorder_id: WO-TEST-DOCS-001" in result
        assert "# Test Document" in result

    def test_inject_uds_with_footer(self):
        """Test injecting both UDS header and footer"""
        engine = TemplateEngine()

        header = UDSHeader(
            workorder_id="WO-TEST-DOCS-001",
            generated_by="papertrail v1.0.0",
            feature_id="test",
            timestamp="2025-12-29T10:00:00Z"
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="CodeRef",
            generated_by="papertrail v1.0.0",
            workorder_id="WO-TEST-DOCS-001",
            feature_id="test",
            last_updated="2025-12-29"
        )

        content = "# Test Document"

        result = engine.inject_uds(content, header, footer)

        assert "workorder_id: WO-TEST-DOCS-001" in result
        assert "# Test Document" in result
        assert "Copyright © 2025 | CodeRef" in result

    def test_render_with_uds(self):
        """Test rendering template and injecting UDS in one step"""
        engine = TemplateEngine()

        template = "# {{ title }}\n\n{{ content }}"

        header = UDSHeader(
            workorder_id="WO-TEST-DOCS-001",
            generated_by="papertrail v1.0.0",
            feature_id="test",
            timestamp="2025-12-29T10:00:00Z"
        )

        result = engine.render_with_uds(
            template,
            {"title": "My Doc", "content": "Test content"},
            header
        )

        assert "---" in result  # YAML header delimiters
        assert "workorder_id: WO-TEST-DOCS-001" in result
        assert "# My Doc" in result
        assert "Test content" in result

    def test_render_file_with_template_dir(self):
        """Test rendering template from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)

            # Create a test template file
            template_file = template_dir / "test.md"
            template_file.write_text("# {{ title }}\n\nBy {{ author }}")

            engine = TemplateEngine(template_dir=template_dir)

            result = engine.render_file("test.md", {
                "title": "Test Doc",
                "author": "Agent1"
            })

            assert "# Test Doc" in result
            assert "By Agent1" in result

    def test_template_inheritance(self):
        """Test template inheritance with extends"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)

            # Create base template
            base = template_dir / "base.md"
            base.write_text("""# {{ title }}

{% block content %}
Default content
{% endblock %}

---
Footer""")

            # Create child template
            child = template_dir / "child.md"
            child.write_text("""{% extends 'base.md' %}

{% block content %}
Custom content for child template
{% endblock %}""")

            engine = TemplateEngine(template_dir=template_dir)

            result = engine.render_file("child.md", {"title": "Test"})

            assert "# Test" in result
            assert "Custom content for child template" in result
            assert "Default content" not in result
            assert "Footer" in result

    def test_template_include(self):
        """Test template includes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)

            # Create included partial
            partial = template_dir / "header.md"
            partial.write_text("Generated by: {{ generator }}")

            # Create main template
            main = template_dir / "main.md"
            main.write_text("""# {{ title }}

{% include 'header.md' %}

Content here.""")

            engine = TemplateEngine(template_dir=template_dir)

            result = engine.render_file("main.md", {
                "title": "Doc",
                "generator": "Papertrail"
            })

            assert "# Doc" in result
            assert "Generated by: Papertrail" in result


class TestTemplateEngineWithExtensions:
    """Test template engine with CodeRef extensions"""

    def test_register_extension(self):
        """Test registering extension"""
        engine = TemplateEngine()

        class MockExtension:
            def method(self):
                return "test"

        ext = MockExtension()
        engine.register_extension("mock", ext)

        assert "mock" in engine.extensions
        assert engine.extensions["mock"] == ext

    def test_render_with_extension(self):
        """Test rendering template that uses extension"""
        engine = TemplateEngine()

        class MockExtension:
            def get_data(self):
                return {"value": 42}

        engine.register_extension("mock", MockExtension())

        template = """
Data: {{ mock.get_data().value }}
"""

        result = engine.render(template, {})
        assert "Data: 42" in result

    def test_create_engine_with_extensions(self):
        """Test convenience function to create engine with extensions"""
        class Ext1:
            def method1(self):
                return "ext1"

        class Ext2:
            def method2(self):
                return "ext2"

        engine = create_template_engine(extensions={
            "ext1": Ext1(),
            "ext2": Ext2()
        })

        assert "ext1" in engine.extensions
        assert "ext2" in engine.extensions
