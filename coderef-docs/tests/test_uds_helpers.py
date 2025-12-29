"""
Unit tests for UDS helper functions.

Tests for WO-UDS-INTEGRATION-001 Phase 4.
"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from uds_helpers import generate_uds_header, generate_uds_footer, get_server_version


class TestGetServerVersion:
    """Test get_server_version() function."""

    def test_returns_string(self):
        """Should return a string."""
        version = get_server_version()
        assert isinstance(version, str)

    def test_format_valid(self):
        """Should return string in format 'coderef-docs v<version>' or 'unknown'."""
        version = get_server_version()
        assert version.startswith("coderef-docs v") or version == "unknown"

    def test_version_pattern(self):
        """If version found, should match X.Y.Z pattern."""
        version = get_server_version()
        if version != "unknown":
            # Extract version number
            version_num = version.replace("coderef-docs v", "")
            parts = version_num.split(".")
            assert len(parts) == 3
            for part in parts:
                assert part.isdigit()


class TestGenerateUdsHeader:
    """Test generate_uds_header() function."""

    def test_basic_header_generation(self):
        """Should generate valid YAML header with required fields."""
        header = generate_uds_header(
            title="Test Plan",
            workorder_id="WO-TEST-001",
            feature_name="test-feature",
            status="DRAFT"
        )

        assert isinstance(header, str)
        assert header.startswith("---")
        assert header.endswith("---")
        assert "title: Test Plan" in header
        assert "workorder_id: WO-TEST-001" in header
        assert "feature_id: test-feature" in header
        assert "status: DRAFT" in header

    def test_includes_timestamp(self):
        """Should include ISO 8601 timestamp."""
        header = generate_uds_header(
            title="Test",
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        assert "timestamp:" in header
        # Check format YYYY-MM-DDTHH:MM:SSZ
        import re
        timestamp_match = re.search(r'timestamp: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', header)
        assert timestamp_match is not None

    def test_includes_server_version(self):
        """Should include server version."""
        header = generate_uds_header(
            title="Test",
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        assert "generated_by:" in header
        assert "coderef-docs" in header

    def test_includes_doc_version(self):
        """Should include document version."""
        header = generate_uds_header(
            title="Test",
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT",
            doc_version="2.0"
        )

        assert "version: 2.0" in header

    def test_default_doc_version(self):
        """Should use default doc_version if not provided."""
        header = generate_uds_header(
            title="Test",
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        assert "version: 1.0" in header

    def test_status_values(self):
        """Should handle different status values."""
        statuses = ["DRAFT", "IN_REVIEW", "APPROVED", "ARCHIVED"]

        for status in statuses:
            header = generate_uds_header(
                title="Test",
                workorder_id="WO-TEST-001",
                feature_name="test",
                status=status
            )
            assert f"status: {status}" in header


class TestGenerateUdsFooter:
    """Test generate_uds_footer() function."""

    def test_basic_footer_generation(self):
        """Should generate valid YAML footer with required fields."""
        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test-feature",
            status="DRAFT"
        )

        assert isinstance(footer, str)
        assert footer.startswith("---")
        assert footer.endswith("---")
        assert "Workorder: WO-TEST-001" in footer
        assert "Feature: test-feature" in footer
        assert "Status: DRAFT" in footer

    def test_includes_ai_assistance_flag(self):
        """Should always set AI Assistance to true."""
        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        assert "AI Assistance: true" in footer

    def test_includes_last_updated(self):
        """Should include last updated date."""
        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        assert "Last Updated:" in footer
        # Check format YYYY-MM-DD
        import re
        date_match = re.search(r'Last Updated: (\d{4}-\d{2}-\d{2})', footer)
        assert date_match is not None

    def test_calculates_next_review_date(self):
        """Should calculate next review date correctly."""
        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT",
            review_days=30
        )

        assert "Next Review:" in footer

        # Extract review date
        import re
        review_match = re.search(r'Next Review: (\d{4}-\d{2}-\d{2})', footer)
        assert review_match is not None

        review_date_str = review_match.group(1)
        review_date = datetime.strptime(review_date_str, "%Y-%m-%d")

        # Should be approximately 30 days from now
        expected_date = datetime.utcnow() + timedelta(days=30)
        diff = abs((review_date - expected_date).days)
        assert diff <= 1  # Allow 1 day tolerance for test timing

    def test_custom_review_days(self):
        """Should handle custom review_days parameter."""
        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT",
            review_days=7
        )

        import re
        review_match = re.search(r'Next Review: (\d{4}-\d{2}-\d{2})', footer)
        review_date = datetime.strptime(review_match.group(1), "%Y-%m-%d")

        expected_date = datetime.utcnow() + timedelta(days=7)
        diff = abs((review_date - expected_date).days)
        assert diff <= 1

    def test_includes_server_version(self):
        """Should include server version in Generated by field."""
        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        assert "Generated by:" in footer
        assert "coderef-docs" in footer


class TestUdsIntegration:
    """Integration tests for UDS header + footer together."""

    def test_header_and_footer_compatible(self):
        """Header and footer should have compatible field formats."""
        header = generate_uds_header(
            title="Test Plan",
            workorder_id="WO-TEST-001",
            feature_name="test-feature",
            status="DRAFT"
        )

        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test-feature",
            status="DRAFT"
        )

        # Both should have valid YAML delimiters
        assert header.startswith("---") and header.endswith("---")
        assert footer.startswith("---") and footer.endswith("---")

        # Both should reference same workorder and feature
        assert "WO-TEST-001" in header and "WO-TEST-001" in footer
        assert "test-feature" in header and "test-feature" in footer

    def test_wrapped_markdown_document(self):
        """Should be able to wrap markdown content with UDS."""
        header = generate_uds_header(
            title="Implementation Plan",
            workorder_id="WO-EXAMPLE-001",
            feature_name="example-feature",
            status="IN_REVIEW"
        )

        footer = generate_uds_footer(
            workorder_id="WO-EXAMPLE-001",
            feature_name="example-feature",
            status="IN_REVIEW"
        )

        content = "# Implementation Plan\n\nThis is the plan content."

        full_doc = f"{header}\n\n{content}\n\n{footer}"

        # Check structure
        assert full_doc.startswith("---")
        assert full_doc.endswith("---")
        assert "# Implementation Plan" in full_doc
        assert "This is the plan content" in full_doc
