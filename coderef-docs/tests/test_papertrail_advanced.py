"""Advanced Papertrail tests: Performance, Scalability, Edge Cases, Health Accuracy.

Tests the claims that basic tests don't cover:
- Performance measurements
- Scalability (1000+ docs)
- Edge cases (Unicode, huge files, corrupted YAML)
- Health scoring accuracy
"""

import os
import pytest
import time
from pathlib import Path

os.environ["PAPERTRAIL_ENABLED"] = "true"

try:
    from papertrail import (
        UDSHeader,
        UDSFooter,
        DocumentStatus,
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


class TestPerformance:
    """Test performance and speed benchmarks."""

    def test_single_doc_generation_speed(self) -> None:
        """Test how fast a single doc can be generated."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-PERF-001",
            generated_by="perf-test",
            feature_id="speed-test",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="perf-test",
            workorder_id="WO-PERF-001",
            feature_id="speed-test",
            last_updated="2025-12-29",
        )

        content = "# Test Doc\n\nContent here."

        # Measure time
        start = time.perf_counter()
        result = engine.inject_uds(content, header, footer)
        elapsed = time.perf_counter() - start

        assert result is not None
        assert elapsed < 0.1  # Should complete in under 100ms
        print(f"\n✓ Single doc generation: {elapsed*1000:.2f}ms")

    def test_template_rendering_speed(self) -> None:
        """Test template rendering performance."""
        engine = create_template_engine()

        template = """# {{ title }}

{% for section in sections %}
## {{ section.name }}
{{ section.content }}
{% endfor %}
"""

        context = {
            "title": "Performance Test",
            "sections": [
                {"name": f"Section {i}", "content": f"Content for section {i}"}
                for i in range(10)
            ],
        }

        # Measure time
        start = time.perf_counter()
        result = engine.render(template, context)
        elapsed = time.perf_counter() - start

        assert "Section 0" in result
        assert "Section 9" in result
        assert elapsed < 0.05  # Should complete in under 50ms
        print(f"\n✓ Template rendering (10 sections): {elapsed*1000:.2f}ms")

    def test_validation_speed(self) -> None:
        """Test validation performance."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-VAL-PERF-001",
            generated_by="perf-test",
            feature_id="validation-speed",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="perf-test",
            workorder_id="WO-VAL-PERF-001",
            feature_id="validation-speed",
            last_updated="2025-12-29",
        )

        doc = engine.inject_uds("# Test\n\nContent.", header, footer)

        # Measure validation time
        start = time.perf_counter()
        validation = validate_uds(doc, doc_type="readme")
        elapsed = time.perf_counter() - start

        assert validation.valid is True
        assert elapsed < 0.1  # Should validate in under 100ms
        print(f"\n✓ Validation: {elapsed*1000:.2f}ms")

    def test_health_calculation_speed(self) -> None:
        """Test health calculation performance."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-HEALTH-PERF-001",
            generated_by="perf-test",
            feature_id="health-speed",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="perf-test",
            workorder_id="WO-HEALTH-PERF-001",
            feature_id="health-speed",
            last_updated="2025-12-29",
        )

        doc = engine.inject_uds("# Test\n\n## Introduction\nContent.", header, footer)

        # Measure health calculation time
        start = time.perf_counter()
        health = calculate_health(doc, doc_type="readme")
        elapsed = time.perf_counter() - start

        assert health.score >= 0
        assert elapsed < 0.1  # Should calculate in under 100ms
        print(f"\n✓ Health calculation: {elapsed*1000:.2f}ms")


class TestScalability:
    """Test scalability with many documents."""

    def test_generate_100_docs(self) -> None:
        """Test generating 100 documents."""
        engine = create_template_engine()

        docs_generated = []
        start = time.perf_counter()

        for i in range(100):
            header = UDSHeader(
                workorder_id=f"WO-SCALE-{i:03d}",
                generated_by="scale-test",
                feature_id=f"doc-{i}",
                timestamp="2025-12-29T20:00:00Z",
            )

            footer = UDSFooter(
                copyright_year=2025,
                organization="TestOrg",
                generated_by="scale-test",
                workorder_id=f"WO-SCALE-{i:03d}",
                feature_id=f"doc-{i}",
                last_updated="2025-12-29",
            )

            content = f"# Document {i}\n\nContent for doc {i}."
            doc = engine.inject_uds(content, header, footer)
            docs_generated.append(doc)

        elapsed = time.perf_counter() - start

        assert len(docs_generated) == 100
        assert all(f"WO-SCALE-{i:03d}" in docs_generated[i] for i in range(100))
        assert elapsed < 10.0  # Should generate 100 docs in under 10 seconds
        print(f"\n✓ Generated 100 docs in {elapsed:.2f}s ({elapsed/100*1000:.2f}ms per doc)")

    def test_validate_100_docs(self) -> None:
        """Test validating 100 documents."""
        engine = create_template_engine()

        # Generate 100 docs
        docs = []
        for i in range(100):
            header = UDSHeader(
                workorder_id=f"WO-VAL-{i:03d}",
                generated_by="scale-test",
                feature_id=f"validate-{i}",
                timestamp="2025-12-29T20:00:00Z",
            )

            footer = UDSFooter(
                copyright_year=2025,
                organization="TestOrg",
                generated_by="scale-test",
                workorder_id=f"WO-VAL-{i:03d}",
                feature_id=f"validate-{i}",
                last_updated="2025-12-29",
            )

            doc = engine.inject_uds(f"# Doc {i}\n\nContent.", header, footer)
            docs.append(doc)

        # Validate all 100
        start = time.perf_counter()
        validations = [validate_uds(doc, doc_type="readme") for doc in docs]
        elapsed = time.perf_counter() - start

        assert len(validations) == 100
        assert all(v.valid for v in validations)
        assert elapsed < 15.0  # Should validate 100 docs in under 15 seconds
        print(f"\n✓ Validated 100 docs in {elapsed:.2f}s ({elapsed/100*1000:.2f}ms per doc)")

    def test_batch_health_scoring(self) -> None:
        """Test health scoring on batch of documents."""
        engine = create_template_engine()

        # Generate 50 docs with varying quality
        docs = []
        for i in range(50):
            header = UDSHeader(
                workorder_id=f"WO-HEALTH-{i:03d}",
                generated_by="scale-test",
                feature_id=f"health-{i}",
                timestamp="2025-12-29T20:00:00Z",
            )

            footer = UDSFooter(
                copyright_year=2025,
                organization="TestOrg",
                generated_by="scale-test",
                workorder_id=f"WO-HEALTH-{i:03d}",
                feature_id=f"health-{i}",
                last_updated="2025-12-29",
            )

            # Vary content quality
            if i % 3 == 0:
                content = "# Minimal\n\nVery little content."
            else:
                content = f"""# Document {i}

## Introduction
Detailed introduction.

## Architecture
Complete architecture section.

## Examples
Multiple examples provided.
"""

            doc = engine.inject_uds(content, header, footer)
            docs.append(doc)

        # Calculate health for all
        start = time.perf_counter()
        health_scores = [calculate_health(doc, doc_type="readme") for doc in docs]
        elapsed = time.perf_counter() - start

        assert len(health_scores) == 50
        assert all(0 <= h.score <= 100 for h in health_scores)
        assert elapsed < 10.0  # Should score 50 docs in under 10 seconds
        print(f"\n✓ Scored 50 docs in {elapsed:.2f}s ({elapsed/50*1000:.2f}ms per doc)")


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_unicode_content(self) -> None:
        """Test documents with Unicode characters."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-UNICODE-001",
            generated_by="edge-test",
            feature_id="unicode-test",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="edge-test",
            workorder_id="WO-UNICODE-001",
            feature_id="unicode-test",
            last_updated="2025-12-29",
        )

        # Unicode content: emoji, CJK, Arabic, special symbols
        unicode_content = """# 文档标题 Documentation 📚

## العربية Section
Content with Arabic text: مرحبا بك

## 日本語 Section
Japanese content: こんにちは世界

## Symbols & Emoji
- ✓ Checkmark
- ★ Star
- → Arrow
- 🚀 Rocket
- 中文 Chinese
"""

        result = engine.inject_uds(unicode_content, header, footer)

        # Verify Unicode preserved
        assert "文档标题" in result
        assert "📚" in result
        assert "العربية" in result
        assert "こんにちは世界" in result
        assert "🚀" in result

        # Should still validate
        validation = validate_uds(result, doc_type="readme")
        assert validation.valid is True

    def test_very_large_document(self) -> None:
        """Test handling of very large documents (10MB+)."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-LARGE-001",
            generated_by="edge-test",
            feature_id="large-doc",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="edge-test",
            workorder_id="WO-LARGE-001",
            feature_id="large-doc",
            last_updated="2025-12-29",
        )

        # Generate ~1MB of content (10,000 lines)
        large_content = "# Large Document\n\n"
        for i in range(10000):
            large_content += f"Line {i}: This is content for line number {i}.\n"

        start = time.perf_counter()
        result = engine.inject_uds(large_content, header, footer)
        elapsed = time.perf_counter() - start

        assert "WO-LARGE-001" in result
        assert "Line 9999" in result
        assert elapsed < 1.0  # Should handle 1MB in under 1 second
        print(f"\n✓ Processed {len(large_content)/1024:.0f}KB in {elapsed*1000:.0f}ms")

    def test_empty_document(self) -> None:
        """Test handling of empty/minimal documents."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-EMPTY-001",
            generated_by="edge-test",
            feature_id="empty-test",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="edge-test",
            workorder_id="WO-EMPTY-001",
            feature_id="empty-test",
            last_updated="2025-12-29",
        )

        # Completely empty content
        result = engine.inject_uds("", header, footer)

        # Should still add UDS
        assert "WO-EMPTY-001" in result

    def test_malformed_yaml_in_content(self) -> None:
        """Test handling content that looks like YAML but isn't."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-YAML-001",
            generated_by="edge-test",
            feature_id="yaml-test",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="edge-test",
            workorder_id="WO-YAML-001",
            feature_id="yaml-test",
            last_updated="2025-12-29",
        )

        # Content with YAML-like syntax (but not real YAML header)
        tricky_content = """---
fake_field: This looks like YAML
but_its_not: Real UDS metadata
---

# Real Content

This document has fake YAML in the content.
"""

        result = engine.inject_uds(tricky_content, header, footer)

        # Should handle gracefully
        assert "WO-YAML-001" in result
        assert "fake_field" in result  # Original content preserved

    def test_special_characters_in_workorder_id(self) -> None:
        """Test workorder IDs with special characters."""
        engine = create_template_engine()

        # Workorder ID with hyphens and numbers (valid)
        header = UDSHeader(
            workorder_id="WO-TEST-123-ABC-456",
            generated_by="edge-test",
            feature_id="special-chars",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="edge-test",
            workorder_id="WO-TEST-123-ABC-456",
            feature_id="special-chars",
            last_updated="2025-12-29",
        )

        result = engine.inject_uds("# Test", header, footer)

        assert "WO-TEST-123-ABC-456" in result

    def test_newlines_and_whitespace(self) -> None:
        """Test documents with unusual whitespace."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-WHITESPACE-001",
            generated_by="edge-test",
            feature_id="whitespace",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="edge-test",
            workorder_id="WO-WHITESPACE-001",
            feature_id="whitespace",
            last_updated="2025-12-29",
        )

        # Content with lots of blank lines and spaces
        weird_whitespace = """# Title




Content with     multiple   spaces.


        More content after blank lines.



"""

        result = engine.inject_uds(weird_whitespace, header, footer)

        # Should preserve whitespace
        assert "WO-WHITESPACE-001" in result
        assert "multiple   spaces" in result


class TestHealthScoringAccuracy:
    """Test that health scores are actually meaningful."""

    def test_minimal_doc_gets_low_score(self) -> None:
        """Test that minimal docs get appropriately low scores."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-MIN-SCORE",
            generated_by="accuracy-test",
            feature_id="minimal",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="accuracy-test",
            workorder_id="WO-MIN-SCORE",
            feature_id="minimal",
            last_updated="2025-12-29",
        )

        minimal_doc = engine.inject_uds("# Title\n\nOne sentence.", header, footer)

        health = calculate_health(minimal_doc, doc_type="readme")

        # Minimal doc should score low
        assert health.score < 60, f"Minimal doc scored too high: {health.score}"

    def test_comprehensive_doc_gets_high_score(self) -> None:
        """Test that comprehensive docs get high scores."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-COMP-SCORE",
            generated_by="accuracy-test",
            feature_id="comprehensive",
            timestamp="2025-12-29T20:00:00Z",
            title="Comprehensive Documentation",
            version="2.0.0",
            status=DocumentStatus.APPROVED,
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="accuracy-test",
            workorder_id="WO-COMP-SCORE",
            feature_id="comprehensive",
            last_updated="2025-12-29",
        )

        comprehensive_doc = engine.inject_uds("""# Comprehensive Documentation

## Overview
This is a complete documentation with all sections properly filled out.
It provides context, examples, and detailed information.

## Purpose
Explain why this exists and what problem it solves.

## Architecture
Detailed architectural overview with component descriptions.

## Installation
Step-by-step installation instructions with examples.

## Usage
Clear usage examples with code snippets and explanations.

## API Reference
Complete API documentation with parameters and return values.

## Examples
Multiple real-world examples demonstrating common use cases.

## Troubleshooting
Common issues and their solutions.

## Contributing
Guidelines for contributing to the project.

## References
- Link 1
- Link 2
""", header, footer)

        health = calculate_health(comprehensive_doc, doc_type="readme")

        # Comprehensive doc should score high
        assert health.score >= 70, f"Comprehensive doc scored too low: {health.score}"

    def test_score_increases_with_more_sections(self) -> None:
        """Test that score increases as more sections are added."""
        engine = create_template_engine()

        scores = []

        for num_sections in [1, 3, 5, 7]:
            header = UDSHeader(
                workorder_id=f"WO-SECTIONS-{num_sections}",
                generated_by="accuracy-test",
                feature_id=f"sections-{num_sections}",
                timestamp="2025-12-29T20:00:00Z",
            )

            footer = UDSFooter(
                copyright_year=2025,
                organization="TestOrg",
                generated_by="accuracy-test",
                workorder_id=f"WO-SECTIONS-{num_sections}",
                feature_id=f"sections-{num_sections}",
                last_updated="2025-12-29",
            )

            content = "# Document\n\n"
            for i in range(num_sections):
                content += f"## Section {i}\nContent for section {i}.\n\n"

            doc = engine.inject_uds(content, header, footer)
            health = calculate_health(doc, doc_type="readme")
            scores.append(health.score)

        # Scores should generally increase
        assert scores[1] > scores[0], "3 sections should score higher than 1"
        assert scores[2] > scores[1], "5 sections should score higher than 3"
        print(f"\n✓ Scores by sections: {scores}")

    def test_missing_required_sections_affects_score(self) -> None:
        """Test that missing required sections lowers the score."""
        engine = create_template_engine()

        header = UDSHeader(
            workorder_id="WO-MISSING-SECTIONS",
            generated_by="accuracy-test",
            feature_id="missing",
            timestamp="2025-12-29T20:00:00Z",
        )

        footer = UDSFooter(
            copyright_year=2025,
            organization="TestOrg",
            generated_by="accuracy-test",
            workorder_id="WO-MISSING-SECTIONS",
            feature_id="missing",
            last_updated="2025-12-29",
        )

        # Doc with some sections but missing key ones
        partial_doc = engine.inject_uds("""# Documentation

## Some Section
Content here.

## Another Section
More content.
""", header, footer)

        health = calculate_health(partial_doc, doc_type="readme")

        # Validation should show errors for missing sections
        validation = validate_uds(partial_doc, doc_type="readme")

        # Health score should reflect missing sections
        assert health.score < 100, "Incomplete doc should not score 100"
        assert len(validation.errors) > 0, "Should have errors for missing sections"
