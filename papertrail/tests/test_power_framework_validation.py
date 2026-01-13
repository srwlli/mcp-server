"""
Tests for POWER Framework Section Validation

Tests that foundation doc validators enforce required sections
for README, ARCHITECTURE, API, SCHEMA, and COMPONENTS documents.
"""

import pytest
from pathlib import Path
from papertrail.validators.foundation import FoundationDocValidator
from papertrail.validator import ValidationSeverity


class TestPOWERFrameworkValidation:
    """Test POWER framework section validation for foundation docs"""

    @pytest.fixture
    def validator(self):
        """Create FoundationDocValidator instance"""
        return FoundationDocValidator()

    def test_readme_with_all_sections_passes(self, validator):
        """Test that compliant README with all 5 POWER sections scores 100/100"""
        # Use our test fixture
        fixture_path = Path(__file__).parent / "fixtures" / "compliant_readme.md"

        result = validator.validate_file(fixture_path)

        # Should pass validation
        assert result.valid == True, f"Expected valid=True, got {result.valid}. Errors: {result.errors}"
        assert result.score >= 98, f"Expected score >= 98, got {result.score}"

        # Should have no MAJOR errors for missing sections
        major_section_errors = [
            e for e in result.errors
            if e.severity == ValidationSeverity.MAJOR and "Missing required" in e.message
        ]
        assert len(major_section_errors) == 0, f"Found unexpected section errors: {major_section_errors}"

    def test_readme_missing_examples_fails(self, validator):
        """Test that README missing Examples section gets MAJOR error and score <= 80"""
        fixture_path = Path(__file__).parent / "fixtures" / "missing_examples_readme.md"

        result = validator.validate_file(fixture_path)

        # Should have MAJOR error for missing Examples section
        examples_errors = [
            e for e in result.errors
            if e.severity == ValidationSeverity.MAJOR and "Examples" in e.message
        ]
        assert len(examples_errors) > 0, "Expected MAJOR error for missing Examples section"

        # Score should be reduced by 20 points (MAJOR error)
        assert result.score <= 80, f"Expected score <= 80 for missing section, got {result.score}"

    def test_readme_sections_enforced(self, validator):
        """Test that README requires all 5 POWER framework sections"""
        # Get schema and check required sections for README
        schema = validator.schema

        # Schema should have required_sections defined
        assert 'properties' in schema
        assert 'required_sections' in schema['properties']

        required_sections_prop = schema['properties']['required_sections']
        readme_sections = required_sections_prop.get('properties', {}).get('readme', {}).get('default', [])

        # README should require these 5 sections
        expected_sections = ["Purpose", "Overview", "What/Why/When", "Examples", "References"]
        assert set(readme_sections) == set(expected_sections), \
            f"Expected sections {expected_sections}, got {readme_sections}"

    def test_architecture_sections_enforced(self, validator):
        """Test that ARCHITECTURE doc requires specific sections"""
        schema = validator.schema
        required_sections_prop = schema['properties']['required_sections']
        arch_sections = required_sections_prop.get('properties', {}).get('architecture', {}).get('default', [])

        # ARCHITECTURE should require these sections
        expected_sections = ["System Overview", "Key Components", "Design Decisions", "Integration Points"]
        assert set(arch_sections) == set(expected_sections), \
            f"Expected sections {expected_sections}, got {arch_sections}"

    def test_api_sections_enforced(self, validator):
        """Test that API doc requires specific sections"""
        schema = validator.schema
        required_sections_prop = schema['properties']['required_sections']
        api_sections = required_sections_prop.get('properties', {}).get('api', {}).get('default', [])

        # API should require these sections
        expected_sections = ["Endpoints", "Authentication", "Request/Response Examples", "Error Codes"]
        assert set(api_sections) == set(expected_sections), \
            f"Expected sections {expected_sections}, got {api_sections}"

    def test_schema_sections_enforced(self, validator):
        """Test that SCHEMA doc requires specific sections"""
        schema = validator.schema
        required_sections_prop = schema['properties']['required_sections']
        schema_sections = required_sections_prop.get('properties', {}).get('schema', {}).get('default', [])

        # SCHEMA should require these sections
        expected_sections = ["Data Models", "Field Descriptions", "Validation Rules", "Relationships"]
        assert set(schema_sections) == set(expected_sections), \
            f"Expected sections {expected_sections}, got {schema_sections}"

    def test_components_sections_enforced(self, validator):
        """Test that COMPONENTS doc requires specific sections"""
        schema = validator.schema
        required_sections_prop = schema['properties']['required_sections']
        comp_sections = required_sections_prop.get('properties', {}).get('components', {}).get('default', [])

        # COMPONENTS should require these sections
        expected_sections = ["Component Catalog", "Props/Parameters", "Usage Examples", "Dependencies"]
        assert set(comp_sections) == set(expected_sections), \
            f"Expected sections {expected_sections}, got {comp_sections}"

    def test_section_validation_case_insensitive(self, validator, tmp_path):
        """Test that section validation is case-insensitive"""
        # Create a test doc with lowercase section headers
        test_content = """---
agent: Test Agent
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test
doc_type: readme
---

# Test README

## purpose

This is the purpose section (lowercase).

## OVERVIEW

This is the overview section (uppercase).

## What/Why/When

This is what/why/when.

## examples

This is examples (lowercase).

## References

This is references.
"""
        test_file = tmp_path / "test_case_insensitive.md"
        test_file.write_text(test_content)

        result = validator.validate_file(test_file)

        # Should pass - case insensitive matching
        section_errors = [
            e for e in result.errors
            if "Missing required" in e.message
        ]
        assert len(section_errors) == 0, \
            f"Expected no section errors with case-insensitive matching, got: {section_errors}"

    def test_section_validation_multiple_heading_levels(self, validator, tmp_path):
        """Test that section validation accepts both # and ## headings"""
        test_content = """---
agent: Test Agent
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test
doc_type: readme
---

# Purpose

Level 1 heading.

## Overview

Level 2 heading.

### What/Why/When

Level 3 heading.

## Examples

Level 2 heading.

# References

Level 1 heading.
"""
        test_file = tmp_path / "test_heading_levels.md"
        test_file.write_text(test_content)

        result = validator.validate_file(test_file)

        # Should pass - any heading level
        section_errors = [
            e for e in result.errors
            if "Missing required" in e.message
        ]
        assert len(section_errors) == 0, \
            f"Expected no section errors with different heading levels, got: {section_errors}"
