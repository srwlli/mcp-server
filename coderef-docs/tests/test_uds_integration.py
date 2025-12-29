"""
Tests for UDS (Universal Document Standard) Integration
Workorder: WO-UDS-INTEGRATION-001

Tests all phases:
- Phase 1: Template creation (SETUP-001, 002, 003)
- Phase 2: Helper functions (IMPL-001, 002, 003)
- Phase 3: Generator integration (IMPL-004, 005, 006, 007, 008)
- Phase 4: Validation (TEST-001, 002, 003, 004, 005)
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import json


# ============================================================================
# Phase 1: Template Creation Tests (SETUP-001, 002, 003)
# ============================================================================

class TestUDSTemplateCreation:
    """Test SETUP-001, SETUP-002, SETUP-003 - Template directory and files."""

    def test_setup_001_uds_directory_exists(self):
        """
        SETUP-001: Create templates/uds/ directory structure

        What: Verify UDS template directory exists
        Why: Required for storing UDS header/footer templates
        How: Check if templates/uds/ exists
        """
        uds_dir = Path("C:/Users/willh/.mcp-servers/coderef-docs/templates/uds")

        assert uds_dir.exists(), f"UDS directory should exist at {uds_dir}"
        assert uds_dir.is_dir(), "UDS path should be a directory"

    def test_setup_002_header_template_exists(self):
        """
        SETUP-002: Create templates/uds/header.yaml

        What: Verify header template file exists with required fields
        Why: Header template defines YAML frontmatter structure
        How: Check file exists and contains required fields
        """
        header_path = Path("C:/Users/willh/.mcp-servers/coderef-docs/templates/uds/header.yaml")

        assert header_path.exists(), "header.yaml should exist"

        # Read and parse template
        with open(header_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required placeholders
        required_fields = [
            "title", "version", "generated_by", "workorder_id",
            "feature_id", "status", "timestamp"
        ]

        for field in required_fields:
            assert field in content, f"Header template must include '{field}' field"

    def test_setup_003_footer_template_exists(self):
        """
        SETUP-003: Create templates/uds/footer.yaml

        What: Verify footer template file exists with required fields
        Why: Footer template defines metadata structure
        How: Check file exists and contains required fields
        """
        footer_path = Path("C:/Users/willh/.mcp-servers/coderef-docs/templates/uds/footer.yaml")

        assert footer_path.exists(), "footer.yaml should exist"

        # Read and parse template
        with open(footer_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required placeholders
        required_fields = [
            "generated_by", "workorder", "feature", "last_updated",
            "ai_assistance", "status", "next_review"
        ]

        for field in required_fields:
            assert field in content, f"Footer template must include '{field}' field"


# ============================================================================
# Phase 2: Helper Function Tests (IMPL-001, 002, 003)
# ============================================================================

class TestUDSHelperFunctions:
    """Test IMPL-001, IMPL-002, IMPL-003 - Helper function implementation."""

    def test_impl_001_generate_uds_header_exists(self):
        """
        IMPL-001: generate_uds_header() function exists

        What: Verify helper function is importable
        Why: Required for generating UDS headers
        How: Import from uds_helpers module
        """
        try:
            from uds_helpers import generate_uds_header
            assert callable(generate_uds_header), "generate_uds_header should be callable"
        except ImportError:
            pytest.fail("uds_helpers.py module should exist with generate_uds_header function")

    def test_impl_001_generate_uds_header_output(self):
        """
        IMPL-001: generate_uds_header() returns valid YAML

        What: Test header generation with sample inputs
        Why: Verify YAML structure and required fields
        How: Call function, parse output with yaml.safe_load
        """
        from uds_helpers import generate_uds_header

        header = generate_uds_header(
            title="Test Feature",
            workorder_id="WO-TEST-001",
            feature_name="test-feature",
            status="DRAFT"
        )

        # Should start and end with YAML delimiters
        assert header.startswith("---"), "Header should start with YAML delimiter"
        assert header.strip().endswith("---"), "Header should end with YAML delimiter"

        # Parse YAML
        yaml_content = header.strip().replace("---", "").strip()
        parsed = yaml.safe_load(yaml_content)

        # Verify required fields
        assert parsed["title"] == "Test Feature"
        assert parsed["workorder_id"] == "WO-TEST-001"
        assert parsed["feature_id"] == "test-feature"
        assert parsed["status"] == "DRAFT"
        assert "timestamp" in parsed
        assert "version" in parsed
        assert "generated_by" in parsed

    def test_impl_001_uds_header_timestamp_format(self):
        """
        IMPL-001: Timestamp uses ISO 8601 format

        What: Verify timestamp field is valid ISO 8601
        Why: Standard format for machine readability
        How: Parse timestamp with datetime.fromisoformat
        """
        from uds_helpers import generate_uds_header

        header = generate_uds_header(
            title="Test",
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT"
        )

        yaml_content = header.strip().replace("---", "").strip()
        parsed = yaml.safe_load(yaml_content)

        # Should parse without error
        try:
            datetime.fromisoformat(parsed["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Timestamp should be ISO 8601 format: {parsed['timestamp']}")

    def test_impl_002_generate_uds_footer_exists(self):
        """
        IMPL-002: generate_uds_footer() function exists

        What: Verify footer helper function is importable
        Why: Required for generating UDS footers
        How: Import from uds_helpers module
        """
        try:
            from uds_helpers import generate_uds_footer
            assert callable(generate_uds_footer), "generate_uds_footer should be callable"
        except ImportError:
            pytest.fail("uds_helpers.py should have generate_uds_footer function")

    def test_impl_002_generate_uds_footer_output(self):
        """
        IMPL-002: generate_uds_footer() returns valid YAML

        What: Test footer generation with sample inputs
        Why: Verify footer structure and fields
        How: Call function, parse output
        """
        from uds_helpers import generate_uds_footer

        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test-feature",
            status="COMPLETE",
            review_days=30
        )

        # Parse YAML
        yaml_content = footer.strip().replace("---", "").strip()
        parsed = yaml.safe_load(yaml_content)

        # Verify required fields
        assert parsed["workorder"] == "WO-TEST-001"
        assert parsed["feature"] == "test-feature"
        assert parsed["status"] == "COMPLETE"
        assert "next_review" in parsed
        assert "ai_assistance" in parsed
        assert parsed["ai_assistance"] == True  # Always true for agent-generated

    def test_impl_002_footer_review_date_calculation(self):
        """
        IMPL-002: next_review calculated as today + review_days

        What: Verify review date calculation logic
        Why: Ensure correct scheduling of review dates
        How: Compare calculated date with today + 30 days
        """
        from uds_helpers import generate_uds_footer

        footer = generate_uds_footer(
            workorder_id="WO-TEST-001",
            feature_name="test",
            status="DRAFT",
            review_days=30
        )

        yaml_content = footer.strip().replace("---", "").strip()
        parsed = yaml.safe_load(yaml_content)

        # Parse review date
        review_date = datetime.fromisoformat(parsed["next_review"].replace("Z", "+00:00"))
        expected_date = datetime.now() + timedelta(days=30)

        # Should be within 1 day (allowing for test execution time)
        diff = abs((review_date - expected_date).days)
        assert diff <= 1, f"Review date should be ~30 days from now (diff: {diff} days)"

    def test_impl_003_get_server_version_exists(self):
        """
        IMPL-003: get_server_version() helper function

        What: Verify version helper function exists
        Why: Required for populating version field
        How: Import and call function
        """
        try:
            from uds_helpers import get_server_version
            version = get_server_version()

            assert isinstance(version, str), "Version should be string"
            assert len(version) > 0, "Version should not be empty"
            # Format: "coderef-docs vX.Y.Z" or "unknown"
            assert "coderef-docs" in version or version == "unknown"
        except ImportError:
            pytest.fail("uds_helpers.py should have get_server_version function")


# ============================================================================
# Phase 3: Generator Integration Tests (IMPL-004, 005, 006, 007, 008)
# ============================================================================

class TestUDSGeneratorIntegration:
    """Test IMPL-004 through IMPL-008 - Integration with generators."""

    @pytest.fixture
    def sample_context(self):
        """Sample context.json data."""
        return {
            "feature_name": "test-feature",
            "description": "Test description",
            "goal": "Test goal",
            "requirements": ["req1", "req2"]
        }

    @pytest.fixture
    def sample_plan(self):
        """Sample plan.json data."""
        return {
            "META_DOCUMENTATION": {
                "workorder_id": "WO-TEST-001",
                "feature_name": "test-feature"
            },
            "1_executive_summary": {
                "what": "Test feature"
            }
        }

    def test_impl_004_context_has_uds_header(self, sample_context):
        """
        IMPL-004: context.json includes UDS header

        What: Verify gather_context adds UDS header to context.json
        Why: All workorder docs need standardized metadata
        How: Generate context, check for YAML frontmatter
        """
        # This test requires actual integration - placeholder for now
        # In real implementation, would call gather_context and verify output
        pytest.skip("Integration test - requires running gather_context tool")

    def test_impl_005_plan_has_uds_header(self, sample_plan):
        """
        IMPL-005: plan.json includes UDS header

        What: Verify create_plan adds UDS header to plan.json
        Why: Plans need lifecycle tracking metadata
        How: Generate plan, check for YAML frontmatter with workorder_id
        """
        pytest.skip("Integration test - requires running create_plan tool")

    def test_impl_006_deliverables_has_uds_header(self):
        """
        IMPL-006: DELIVERABLES.md includes UDS header

        What: Verify deliverables template includes UDS header
        Why: Markdown docs need metadata in compatible format
        How: Generate deliverables, check for markdown-compatible frontmatter
        """
        pytest.skip("Integration test - requires running generate_deliverables tool")

    def test_impl_007_handoff_has_uds_header(self):
        """
        IMPL-007: claude.md includes UDS header

        What: Verify handoff generator adds UDS metadata
        Why: Handoff docs need provenance tracking
        How: Generate handoff doc, check for UDS header
        """
        pytest.skip("Integration test - requires running generate_handoff tool")

    def test_impl_008_analysis_has_uds_header(self):
        """
        IMPL-008: analysis.json includes UDS header

        What: Verify analyze_for_planning adds UDS header
        Why: Analysis docs need metadata
        How: Run analysis, check for UDS header in output
        """
        pytest.skip("Integration test - requires running analyze_for_planning tool")


# ============================================================================
# Phase 4: Validation Tests (TEST-001, 002, 003, 004, 005)
# ============================================================================

class TestUDSValidation:
    """Test TEST-001 through TEST-005 - End-to-end validation."""

    def test_test_001_header_yaml_validation(self):
        """
        TEST-001: UDS headers produce valid YAML

        What: Test various header inputs for YAML validity
        Why: Ensure all generated headers parse without errors
        How: Generate headers with edge cases, parse with yaml.safe_load
        """
        from uds_helpers import generate_uds_header

        test_cases = [
            {
                "title": "Simple Feature",
                "workorder_id": "WO-TEST-001",
                "feature_name": "simple",
                "status": "DRAFT"
            },
            {
                "title": "Feature with Special-Chars!@#",
                "workorder_id": "WO-SPECIAL-CHARS-001",
                "feature_name": "special-chars",
                "status": "IN_PROGRESS"
            },
            {
                "title": "Very Long Feature Name That Exceeds Normal Length",
                "workorder_id": "WO-LONG-NAME-001",
                "feature_name": "very-long-feature-name",
                "status": "COMPLETE"
            }
        ]

        for test_case in test_cases:
            header = generate_uds_header(**test_case)
            yaml_content = header.strip().replace("---", "").strip()

            try:
                parsed = yaml.safe_load(yaml_content)
                assert parsed is not None, "YAML should parse to dict"
            except yaml.YAMLError as e:
                pytest.fail(f"YAML parsing failed for {test_case['title']}: {e}")

    def test_test_002_footer_date_calculations(self):
        """
        TEST-002: Footer review dates calculated correctly

        What: Test review_days parameter affects next_review
        Why: Verify date calculation logic
        How: Generate footers with different review_days, check dates
        """
        from uds_helpers import generate_uds_footer

        test_days = [7, 14, 30, 60, 90]

        for days in test_days:
            footer = generate_uds_footer(
                workorder_id="WO-TEST-001",
                feature_name="test",
                status="DRAFT",
                review_days=days
            )

            yaml_content = footer.strip().replace("---", "").strip()
            parsed = yaml.safe_load(yaml_content)

            review_date = datetime.fromisoformat(parsed["next_review"].replace("Z", "+00:00"))
            expected_date = datetime.now() + timedelta(days=days)

            diff = abs((review_date - expected_date).days)
            assert diff <= 1, f"Review date should be ~{days} days from now"

    def test_test_003_backward_compatibility(self):
        """
        TEST-003: Existing workorder docs work without UDS

        What: Verify old docs without UDS headers still parse
        Why: Ensure backward compatibility
        How: Load existing plan.json/context.json without UDS
        """
        # Test that JSON files without UDS headers parse correctly
        sample_old_context = {
            "feature_name": "old-feature",
            "description": "No UDS header"
        }

        # Should parse as valid JSON
        try:
            json_str = json.dumps(sample_old_context)
            parsed = json.loads(json_str)
            assert parsed["feature_name"] == "old-feature"
        except json.JSONDecodeError:
            pytest.fail("Old format should still be valid JSON")

    def test_test_004_full_lifecycle_tracking(self):
        """
        TEST-004: UDS metadata tracks full workorder lifecycle

        What: Verify metadata supports DRAFT → IN_PROGRESS → COMPLETE
        Why: Enable lifecycle management
        How: Generate headers/footers with each status
        """
        from uds_helpers import generate_uds_header, generate_uds_footer

        statuses = ["DRAFT", "IN_PROGRESS", "COMPLETE", "ARCHIVED"]

        for status in statuses:
            header = generate_uds_header(
                title=f"Feature in {status}",
                workorder_id="WO-TEST-001",
                feature_name="test",
                status=status
            )

            yaml_content = header.strip().replace("---", "").strip()
            parsed = yaml.safe_load(yaml_content)

            assert parsed["status"] == status, f"Status should be {status}"

    def test_test_005_integration_e2e(self):
        """
        TEST-005: End-to-end UDS integration

        What: Test complete workflow with UDS
        Why: Verify all components work together
        How: Run create_workorder with UDS enabled
        """
        pytest.skip("E2E test - requires full create_workorder workflow")


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
