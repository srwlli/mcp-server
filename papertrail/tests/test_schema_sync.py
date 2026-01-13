"""
Tests for Schema Synchronization Tool

Tests that SchemaSyncTool correctly validates schema completeness,
generates reports, and detects drift.
"""

import pytest
from pathlib import Path
from papertrail.tools.sync_schemas import SchemaSyncTool


class TestSchemaSyncTool:
    """Test schema synchronization tool"""

    @pytest.fixture
    def tool(self):
        """Create SchemaSyncTool instance"""
        return SchemaSyncTool()

    def test_load_foundation_schema(self, tool):
        """Test loading foundation-doc-frontmatter-schema.json"""
        schema = tool.load_schema("foundation-doc-frontmatter-schema.json")

        # Should load successfully
        assert schema is not None
        assert isinstance(schema, dict)

        # Should have required fields (may be in allOf)
        assert "allOf" in schema or "properties" in schema

    def test_get_doc_types_foundation_schema(self, tool):
        """Test extracting doc_type enum from foundation schema"""
        schema = tool.load_schema("foundation-doc-frontmatter-schema.json")
        doc_types = tool.get_doc_types(schema)

        # Foundation schema should have 5 doc types
        expected_doc_types = ["readme", "architecture", "api", "schema", "components"]
        assert set(doc_types) == set(expected_doc_types)

    def test_get_required_sections_foundation_schema(self, tool):
        """Test extracting required_sections from foundation schema"""
        schema = tool.load_schema("foundation-doc-frontmatter-schema.json")
        required_sections = tool.get_required_sections(schema)

        # README should have 5 POWER framework sections
        assert "readme" in required_sections
        readme_sections = required_sections["readme"]
        assert len(readme_sections) == 5
        assert "Purpose" in readme_sections
        assert "Overview" in readme_sections
        assert "What/Why/When" in readme_sections
        assert "Examples" in readme_sections
        assert "References" in readme_sections

        # API should have 4 sections
        assert "api" in required_sections
        api_sections = required_sections["api"]
        assert len(api_sections) == 4
        assert "Endpoints" in api_sections
        assert "Authentication" in api_sections

        # COMPONENTS should have 4 sections
        assert "components" in required_sections
        comp_sections = required_sections["components"]
        assert len(comp_sections) == 4
        assert "Component Catalog" in comp_sections
        assert "Props/Parameters" in comp_sections

    def test_validate_schema_completeness_foundation(self, tool):
        """Test that foundation schema is complete"""
        is_complete, issues = tool.validate_schema_completeness(
            "foundation-doc-frontmatter-schema.json"
        )

        # Foundation schema should be complete
        assert is_complete == True, f"Schema incomplete with issues: {issues}"
        assert len(issues) == 0

    def test_generate_schema_report_foundation(self, tool):
        """Test generating report for foundation schema"""
        report = tool.generate_schema_report("foundation-doc-frontmatter-schema.json")

        # Report should be non-empty markdown
        assert len(report) > 0
        assert "# Schema Report" in report
        assert "foundation-doc-frontmatter-schema.json" in report

        # Should show completeness
        assert "**Complete:** Yes" in report

        # Should list doc types
        assert "readme" in report
        assert "api" in report
        assert "components" in report

        # Should show checkmarks for complete types
        assert "✅" in report

    def test_list_all_schemas(self, tool):
        """Test listing all schemas in directory"""
        schemas = tool.list_all_schemas()

        # Should find schemas
        assert len(schemas) > 0

        # Foundation schema should be present
        assert "foundation-doc-frontmatter-schema.json" in schemas

        # Base schema should be present
        assert "base-frontmatter-schema.json" in schemas

    def test_validate_all_schemas(self, tool):
        """Test validating all schemas"""
        report = tool.validate_all_schemas()

        # Report should be non-empty
        assert len(report) > 0
        assert "# All Schemas Validation Report" in report

        # Should show total count
        assert "**Total Schemas:**" in report

        # Should show completeness stats
        assert "**Complete:**" in report

    def test_schema_not_found_error(self, tool):
        """Test error handling when schema doesn't exist"""
        with pytest.raises(FileNotFoundError):
            tool.load_schema("nonexistent-schema.json")

    def test_get_doc_types_empty_for_base_schema(self, tool):
        """Test that base schema doesn't define doc_type enum"""
        schema = tool.load_schema("base-frontmatter-schema.json")
        doc_types = tool.get_doc_types(schema)

        # Base schema shouldn't have doc_type field
        assert len(doc_types) == 0

    def test_get_required_sections_empty_for_base_schema(self, tool):
        """Test that base schema doesn't have required_sections"""
        schema = tool.load_schema("base-frontmatter-schema.json")
        required_sections = tool.get_required_sections(schema)

        # Base schema shouldn't have required_sections
        assert len(required_sections) == 0

    def test_validate_base_schema_has_issues(self, tool):
        """Test that base schema validation reports it doesn't have doc_type"""
        is_complete, issues = tool.validate_schema_completeness(
            "base-frontmatter-schema.json"
        )

        # Base schema should have issues (no doc_type enum)
        assert is_complete == False
        assert len(issues) > 0
        assert any("doc_type" in issue.lower() for issue in issues)

    def test_compare_schemas_identical(self, tool):
        """Test comparing foundation schema with itself (should be identical)"""
        report = tool.compare_schemas(
            "foundation-doc-frontmatter-schema.json",
            "foundation-doc-frontmatter-schema.json"
        )

        # Should show all doc types as identical
        assert "✅" in report
        assert "Identical" in report

        # Should not show differences
        assert "❌" not in report or "Different sections" not in report

    def test_schema_report_includes_section_counts(self, tool):
        """Test that schema report includes section counts per doc_type"""
        report = tool.generate_schema_report("foundation-doc-frontmatter-schema.json")

        # Should show section counts
        # README has 5 sections
        assert "5 required sections" in report

        # API, SCHEMA, ARCHITECTURE, COMPONENTS each have 4 sections
        assert "4 required sections" in report

    def test_validate_all_schemas_includes_foundation(self, tool):
        """Test that batch validation includes foundation schema"""
        report = tool.validate_all_schemas()

        # Foundation schema should be in report
        assert "foundation-doc-frontmatter-schema.json" in report

        # Should show checkmark (complete)
        lines = report.split("\n")
        foundation_line = next(
            (line for line in lines if "foundation-doc-frontmatter-schema.json" in line),
            None
        )
        assert foundation_line is not None
        assert "✅" in foundation_line

    def test_tool_initialization_with_custom_dir(self, tmp_path):
        """Test initializing tool with custom schemas directory"""
        # Create a temporary schemas directory
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        # Should initialize without errors
        tool = SchemaSyncTool(schemas_dir=schemas_dir)
        assert tool.schemas_dir == schemas_dir

    def test_tool_initialization_invalid_dir(self):
        """Test error when initializing with non-existent directory"""
        with pytest.raises(FileNotFoundError):
            SchemaSyncTool(schemas_dir=Path("/nonexistent/directory"))

    def test_doc_type_sections_architecture(self, tool):
        """Test that architecture doc type has correct required sections"""
        schema = tool.load_schema("foundation-doc-frontmatter-schema.json")
        required_sections = tool.get_required_sections(schema)

        assert "architecture" in required_sections
        arch_sections = required_sections["architecture"]
        assert len(arch_sections) == 4
        assert "System Overview" in arch_sections
        assert "Key Components" in arch_sections
        assert "Design Decisions" in arch_sections
        assert "Integration Points" in arch_sections

    def test_doc_type_sections_schema(self, tool):
        """Test that schema doc type has correct required sections"""
        schema = tool.load_schema("foundation-doc-frontmatter-schema.json")
        required_sections = tool.get_required_sections(schema)

        assert "schema" in required_sections
        schema_sections = required_sections["schema"]
        assert len(schema_sections) == 4
        assert "Data Models" in schema_sections
        assert "Field Descriptions" in schema_sections
        assert "Validation Rules" in schema_sections
        assert "Relationships" in schema_sections
