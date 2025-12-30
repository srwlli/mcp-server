"""Tests for Papertrail practical use cases.

Verifies the 5 key use cases work as claimed:
1. Add traceability to docs
2. Validate documentation quality
3. Generate new docs with UDS
4. Test UDS compliance
5. Build custom doc generators
"""

import os
import pytest
import tempfile
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
    PAPERTRAIL_AVAILABLE = True
except ImportError:
    PAPERTRAIL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PAPERTRAIL_AVAILABLE,
    reason="Papertrail not installed"
)


class TestUseCase1AddTraceability:
    """Use Case 1: Add Traceability to Your Docs

    Add UDS headers to all your markdown files to link them to workorders.
    """

    def test_add_uds_to_existing_markdown(self) -> None:
        """Test adding UDS header to existing markdown file."""
        # Existing markdown content
        existing_content = """# My Project

## Overview
This is my project documentation.

## Features
- Feature A
- Feature B
"""

        # Create UDS header linking to workorder
        header = UDSHeader(
            workorder_id="WO-DOCS-UPDATE-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="traceability-test",
            timestamp="2025-12-29T20:00:00Z",
            title="My Project",
            version="1.0.0",
            status=DocumentStatus.PUBLISHED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="MyOrg",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-DOCS-UPDATE-001",
            feature_id="traceability-test",
            last_updated="2025-12-29",
        )

        # Inject UDS
        engine = create_template_engine()
        traced_doc = engine.inject_uds(existing_content, header, footer)

        # Verify traceability links
        assert "workorder_id: WO-DOCS-UPDATE-001" in traced_doc
        assert "feature_id: traceability-test" in traced_doc
        assert "# My Project" in traced_doc  # Original content preserved
        assert "Feature A" in traced_doc  # Original content preserved

    def test_bulk_add_traceability_to_multiple_docs(self) -> None:
        """Test adding traceability to multiple markdown files."""
        docs = [
            ("README.md", "# README\n\nProject readme."),
            ("ARCHITECTURE.md", "# Architecture\n\nSystem design."),
            ("API.md", "# API Reference\n\nAPI docs."),
        ]

        traced_docs = []

        for filename, content in docs:
            header = UDSHeader(
                workorder_id="WO-BULK-TRACE-001",
                generated_by="coderef-docs v2.0.0",
                feature_id=f"trace-{filename}",
                timestamp="2025-12-29T20:00:00Z",
                title=filename,
                version="1.0.0",
                status=DocumentStatus.PUBLISHED,
            )

            footer = UDSFooter(
                copyright_year=2025,
                organization="MyOrg",
                generated_by="coderef-docs v2.0.0",
                workorder_id="WO-BULK-TRACE-001",
                feature_id=f"trace-{filename}",
                last_updated="2025-12-29",
            )

            engine = create_template_engine()
            traced_doc = engine.inject_uds(content, header, footer)
            traced_docs.append((filename, traced_doc))

        # Verify all docs now have traceability
        assert len(traced_docs) == 3
        for filename, doc in traced_docs:
            assert "workorder_id: WO-BULK-TRACE-001" in doc
            assert f"trace-{filename}" in doc


class TestUseCase2ValidateQuality:
    """Use Case 2: Validate Documentation Quality

    Run health checks to find low-quality docs that need updates.
    """

    def test_health_check_identifies_low_quality_docs(self) -> None:
        """Test health scoring identifies docs that need improvement."""
        # Low-quality doc (minimal content)
        low_quality = """---
workorder_id: WO-TEST-001
---

# Title

Short content.
"""

        # High-quality doc (comprehensive content)
        high_quality = """---
workorder_id: WO-TEST-002
generated_by: coderef-docs v2.0.0
feature_id: comprehensive-doc
timestamp: 2025-12-29T20:00:00Z
title: Comprehensive Documentation
version: 2.0.0
status: published
---

# Comprehensive Documentation

## Introduction
Detailed introduction explaining the purpose and scope.

## Architecture
Complete architectural overview with diagrams and explanations.

## API Reference
Full API documentation with examples.

## Getting Started
Step-by-step guide for new users.

## Advanced Topics
In-depth coverage of advanced features.

## Examples
Multiple real-world examples.

## Troubleshooting
Common issues and solutions.

---
Copyright © 2025 MyOrg
Generated by coderef-docs v2.0.0
Workorder: WO-TEST-002
---
"""

        low_health = calculate_health(low_quality)
        high_health = calculate_health(high_quality)

        # Low-quality doc should score lower
        assert low_health["score"] < high_health["score"]
        assert low_health["grade"] != "A"
        assert high_health["score"] >= 70

    def test_batch_health_check_for_quality_audit(self) -> None:
        """Test running health checks on multiple docs to find issues."""
        docs = {
            "good_doc.md": """---
workorder_id: WO-GOOD-001
---
# Good Doc
## Section 1
Content here.
## Section 2
More content.
## Section 3
Even more content.
---
Copyright © 2025
---
""",
            "bad_doc.md": "# Bad\nNo metadata.",
            "medium_doc.md": """---
workorder_id: WO-MED-001
---
# Medium
Some content.
---
Copyright © 2025
---
"""
        }

        health_scores = {}
        for name, content in docs.items():
            health = calculate_health(content)
            health_scores[name] = health["score"]

        # Identify docs needing improvement (score < 70)
        needs_improvement = [
            name for name, score in health_scores.items() if score < 70
        ]

        assert "bad_doc.md" in needs_improvement
        assert "good_doc.md" not in needs_improvement


class TestUseCase3GenerateNewDocs:
    """Use Case 3: Generate New Docs with UDS

    Create new documentation with built-in workorder tracking.
    """

    def test_generate_readme_with_uds(self) -> None:
        """Test generating README.md with built-in UDS tracking."""
        template = """# {{ project_name }}

{{ description }}

## Installation
```bash
{{ install_command }}
```

## Usage
{{ usage }}

## License
{{ license }}
"""

        context = {
            "project_name": "My Awesome Project",
            "description": "A great project that does awesome things.",
            "install_command": "pip install my-project",
            "usage": "Run `my-project start` to begin.",
            "license": "MIT License",
        }

        header = UDSHeader(
            workorder_id="WO-README-GEN-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="readme-generation",
            timestamp="2025-12-29T20:00:00Z",
            title="My Awesome Project",
            version="1.0.0",
            status=DocumentStatus.PUBLISHED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="MyOrg",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-README-GEN-001",
            feature_id="readme-generation",
            last_updated="2025-12-29",
        )

        engine = create_template_engine()
        rendered = engine.render(template, context)
        final_readme = engine.inject_uds(rendered, header, footer)

        # Verify README has both content and UDS
        assert "# My Awesome Project" in final_readme
        assert "pip install my-project" in final_readme
        assert "workorder_id: WO-README-GEN-001" in final_readme
        assert "feature_id: readme-generation" in final_readme

    def test_generate_api_docs_with_uds(self) -> None:
        """Test generating API documentation with UDS tracking."""
        template = """# {{ api_name }} API Reference

## Endpoints

{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

{{ endpoint.description }}

**Request:**
```json
{{ endpoint.request_example }}
```

**Response:**
```json
{{ endpoint.response_example }}
```

{% endfor %}
"""

        context = {
            "api_name": "MyAPI",
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/api/users",
                    "description": "Get all users",
                    "request_example": "{}",
                    "response_example": '{"users": []}',
                },
                {
                    "method": "POST",
                    "path": "/api/users",
                    "description": "Create new user",
                    "request_example": '{"name": "John"}',
                    "response_example": '{"id": 1, "name": "John"}',
                },
            ],
        }

        header = UDSHeader(
            workorder_id="WO-API-DOCS-001",
            generated_by="coderef-docs v2.0.0",
            feature_id="api-docs-generation",
            timestamp="2025-12-29T20:00:00Z",
            title="MyAPI API Reference",
            version="2.0.0",
            status=DocumentStatus.PUBLISHED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="MyOrg",
            generated_by="coderef-docs v2.0.0",
            workorder_id="WO-API-DOCS-001",
            feature_id="api-docs-generation",
            last_updated="2025-12-29",
        )

        engine = create_template_engine()
        rendered = engine.render(template, context)
        final_api_docs = engine.inject_uds(rendered, header, footer)

        # Verify API docs have endpoints and UDS
        assert "GET /api/users" in final_api_docs
        assert "POST /api/users" in final_api_docs
        assert "workorder_id: WO-API-DOCS-001" in final_api_docs


class TestUseCase4TestCompliance:
    """Use Case 4: Test UDS Compliance

    Validate that all your docs meet UDS standards before archiving.
    """

    def test_validate_doc_before_archiving(self) -> None:
        """Test validating document UDS compliance before archiving."""
        # Document ready for archiving
        compliant_doc = """---
workorder_id: WO-ARCHIVE-001
generated_by: coderef-docs v2.0.0
feature_id: archive-test
timestamp: 2025-12-29T20:00:00Z
title: Archived Document
version: 1.0.0
status: published
---

# Archived Document

Complete documentation content.

---
Copyright © 2025 MyOrg
Generated by coderef-docs v2.0.0
Workorder: WO-ARCHIVE-001
---
"""

        # Validate before archiving
        validation = validate_uds(compliant_doc)

        assert validation["valid"] is True
        assert validation["errors"] == []

        # Only archive if validation passes
        if validation["valid"]:
            # Safe to archive
            assert "workorder_id: WO-ARCHIVE-001" in compliant_doc

    def test_reject_non_compliant_docs_from_archiving(self) -> None:
        """Test rejecting docs that don't meet UDS standards."""
        # Document missing UDS metadata
        non_compliant_doc = """# Some Document

No UDS metadata at all.
"""

        validation = validate_uds(non_compliant_doc)

        # Should fail validation
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0

        # Do NOT archive if validation fails
        if not validation["valid"]:
            # Document needs UDS metadata before archiving
            assert True  # Test passes if we catch non-compliance

    def test_bulk_compliance_check(self) -> None:
        """Test batch validation of multiple docs for compliance."""
        docs = {
            "compliant1.md": """---
workorder_id: WO-001
---
# Doc 1
Content.
---
Copyright © 2025
---
""",
            "compliant2.md": """---
workorder_id: WO-002
---
# Doc 2
Content.
---
Copyright © 2025
---
""",
            "non_compliant.md": "# Bad Doc\nNo metadata.",
        }

        compliance_results = {}
        for name, content in docs.items():
            validation = validate_uds(content)
            compliance_results[name] = validation["valid"]

        # Identify non-compliant docs
        non_compliant = [
            name for name, valid in compliance_results.items() if not valid
        ]

        assert "non_compliant.md" in non_compliant
        assert "compliant1.md" not in non_compliant
        assert "compliant2.md" not in non_compliant


class TestUseCase5CustomDocGenerators:
    """Use Case 5: Build Custom Doc Generators

    Use Papertrail as a library to build your own doc generation tools.
    """

    def test_custom_generator_for_architecture_docs(self) -> None:
        """Test building custom architecture doc generator."""
        class ArchitectureDocGenerator:
            def __init__(self):
                self.engine = create_template_engine()
                self.template = """# {{ title }} Architecture

## System Overview
{{ overview }}

## Components
{% for component in components %}
### {{ component.name }}
{{ component.description }}

**Responsibilities:**
{% for resp in component.responsibilities %}
- {{ resp }}
{% endfor %}
{% endfor %}

## Data Flow
{{ data_flow }}
"""

            def generate(self, workorder_id, context):
                # Render template
                rendered = self.engine.render(self.template, context)

                # Add UDS
                header = UDSHeader(
                    workorder_id=workorder_id,
                    generated_by="custom-arch-generator v1.0.0",
                    feature_id=context.get("feature_id", "arch"),
                    timestamp="2025-12-29T20:00:00Z",
                    title=context["title"],
                    version="1.0.0",
                    status=DocumentStatus.PUBLISHED,
                )

                footer = UDSFooter(
                    copyright_year=2025,
                    organization="MyOrg",
                    generated_by="custom-arch-generator v1.0.0",
                    workorder_id=workorder_id,
                    feature_id=context.get("feature_id", "arch"),
                    last_updated="2025-12-29",
                )

                return self.engine.inject_uds(rendered, header, footer)

        # Use custom generator
        generator = ArchitectureDocGenerator()

        context = {
            "title": "MyApp",
            "overview": "Microservices architecture",
            "components": [
                {
                    "name": "API Gateway",
                    "description": "Entry point for all requests",
                    "responsibilities": ["Routing", "Auth", "Rate limiting"],
                },
                {
                    "name": "User Service",
                    "description": "Manages user data",
                    "responsibilities": ["CRUD operations", "Validation"],
                },
            ],
            "data_flow": "Client → API Gateway → Services → Database",
        }

        doc = generator.generate("WO-ARCH-001", context)

        # Verify custom generator works
        assert "# MyApp Architecture" in doc
        assert "API Gateway" in doc
        assert "User Service" in doc
        assert "workorder_id: WO-ARCH-001" in doc

    def test_custom_generator_with_file_output(self, tmp_path: Path) -> None:
        """Test custom generator that writes to files."""
        class READMEGenerator:
            def __init__(self):
                self.engine = create_template_engine()

            def generate_and_save(self, project_name, output_path, workorder_id):
                template = "# {{ name }}\n\nGenerated README for {{ name }}."
                rendered = self.engine.render(template, {"name": project_name})

                header = UDSHeader(
                    workorder_id=workorder_id,
                    generated_by="readme-generator v1.0.0",
                    feature_id="readme",
                    timestamp="2025-12-29T20:00:00Z",
                    title=project_name,
                    version="1.0.0",
                    status=DocumentStatus.PUBLISHED,
                )

                footer = UDSFooter(
                    copyright_year=2025,
                    organization="MyOrg",
                    generated_by="readme-generator v1.0.0",
                    workorder_id=workorder_id,
                    feature_id="readme",
                    last_updated="2025-12-29",
                )

                final_doc = self.engine.inject_uds(rendered, header, footer)

                # Write to file
                output_path.write_text(final_doc)
                return output_path

        generator = READMEGenerator()
        output_file = tmp_path / "README.md"

        result_path = generator.generate_and_save(
            "MyProject",
            output_file,
            "WO-README-001"
        )

        assert result_path.exists()
        content = result_path.read_text()
        assert "# MyProject" in content
        assert "workorder_id: WO-README-001" in content


class TestRealWorldScenarios:
    """Test real-world integration scenarios."""

    def test_complete_documentation_pipeline(self, tmp_path: Path) -> None:
        """Test complete pipeline: generate → validate → score → archive."""
        # 1. Generate doc
        engine = create_template_engine()
        template = "# {{ title }}\n\n{{ content }}"
        rendered = engine.render(template, {
            "title": "Pipeline Test",
            "content": "Complete documentation content."
        })

        header = UDSHeader(
            workorder_id="WO-PIPELINE-001",
            generated_by="pipeline-test v1.0.0",
            feature_id="pipeline",
            timestamp="2025-12-29T20:00:00Z",
            title="Pipeline Test",
            version="1.0.0",
            status=DocumentStatus.PUBLISHED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="pipeline-test v1.0.0",
            workorder_id="WO-PIPELINE-001",
            feature_id="pipeline",
            last_updated="2025-12-29",
        )

        doc = engine.inject_uds(rendered, header, footer)

        # 2. Validate
        validation = validate_uds(doc)
        assert validation["valid"] is True

        # 3. Score
        health = calculate_health(doc)
        assert health["score"] > 0

        # 4. Archive (if passes)
        if validation["valid"] and health["score"] >= 70:
            archive_path = tmp_path / "archived" / "pipeline-test.md"
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(doc)
            assert archive_path.exists()
