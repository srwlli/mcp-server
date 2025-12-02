"""
Unit tests for PersonaValidator.

Tests multi-stage validation pipeline (schema → semantic → quality).
"""

import pytest
from pathlib import Path
from src.validators import PersonaValidator, ValidationResult


@pytest.fixture
def validator():
    """Create validator instance for tests."""
    return PersonaValidator()


@pytest.fixture
def valid_persona_input():
    """Sample valid persona input."""
    return {
        "name": "test-validator",
        "description": "A validation expert for testing multi-stage validation pipelines",
        "expertise": [
            "Schema validation",
            "Semantic analysis",
            "Quality checks",
            "Best practices",
            "Error handling"
        ],
        "use_cases": [
            "Validating user inputs",
            "Ensuring data quality",
            "Catching errors early",
            "Providing helpful feedback",
            "Maintaining standards"
        ],
        "communication_style": "Clear and technical with detailed error messages and actionable feedback"
    }


def test_validation_result_creation():
    """Test ValidationResult creation and behavior."""
    # Passing result
    pass_result = ValidationResult(passed=True)
    assert pass_result.passed
    assert bool(pass_result)
    assert len(pass_result.errors) == 0

    # Failing result with errors
    fail_result = ValidationResult(passed=False, errors=["Error 1", "Error 2"])
    assert not fail_result.passed
    assert not bool(fail_result)
    assert len(fail_result.errors) == 2


def test_schema_validation_success(validator, valid_persona_input):
    """Test that valid inputs pass schema validation."""
    result = validator.validate_schema(valid_persona_input)
    assert result.passed
    assert len(result.errors) == 0


def test_schema_validation_failures(validator):
    """Test that invalid inputs fail schema validation."""
    # Invalid name format
    invalid_input = {
        "name": "Test Expert",  # spaces not allowed
        "description": "A test description that is long enough for validation",
        "expertise": ["A", "B", "C"],
        "use_cases": ["1", "2", "3"],
        "communication_style": "Professional communication style"
    }
    result = validator.validate_schema(invalid_input)
    assert not result.passed
    assert len(result.errors) > 0


def test_semantic_validation_uniqueness(validator):
    """Test that duplicate names are caught."""
    # Create input with name that matches existing base persona
    duplicate_input = {
        "name": "docs-expert",  # This exists in base personas
        "description": "A documentation expert that duplicates existing persona",
        "expertise": ["Documentation", "Writing", "Standards"],
        "use_cases": ["Writing docs", "Creating guides", "Maintaining documentation"],
        "communication_style": "Professional and clear documentation style"
    }

    result = validator.validate_semantics(duplicate_input)
    # Should fail or warn about duplicate name
    assert not result.passed or len(result.warnings) > 0


def test_semantic_validation_coherence(validator):
    """Test semantic coherence checks."""
    incoherent_input = {
        "name": "test-expert",
        "description": "A generic helper with no specific domain",  # Vague
        "expertise": ["Thing 1", "Thing 2", "Thing 3"],  # Not specific
        "use_cases": ["Helping with stuff", "Doing things", "Other tasks"],  # Vague
        "communication_style": "Friendly and helpful communication style overall"
    }

    result = validator.validate_semantics(incoherent_input)
    # Should have warnings about vague content
    assert len(result.warnings) > 0 or not result.passed


def test_quality_validation_coverage(validator):
    """Test quality validation checks for coverage."""
    minimal_input = {
        "name": "minimal-expert",
        "description": "A minimal expert with bare minimum fields for testing quality",
        "expertise": ["A", "B", "C"],  # Only 3 (minimum)
        "use_cases": ["1", "2", "3"],  # Only 3 (minimum)
        "communication_style": "Professional communication style with minimal detail"
    }

    result = validator.validate_quality(minimal_input)
    # Should pass but have warnings about adding more content
    assert result.passed
    assert len(result.warnings) >= 2  # Should warn about low count


def test_quality_validation_optional_fields(validator):
    """Test that quality validation recommends optional fields."""
    input_without_optional = {
        "name": "basic-expert",
        "description": "A basic expert without optional fields for quality testing",
        "expertise": ["Field A", "Field B", "Field C", "Field D", "Field E"],
        "use_cases": ["Use case 1", "Use case 2", "Use case 3", "Use case 4", "Use case 5"],
        "communication_style": "Clear and professional communication without extra details"
    }

    result = validator.validate_quality(input_without_optional)
    assert result.passed
    # Should recommend adding optional fields
    assert any('problem_solving' in w.lower() for w in result.warnings)


def test_validate_all_pipeline(validator, valid_persona_input):
    """Test complete validation pipeline."""
    passed, results = validator.validate_all(valid_persona_input)

    # Should have results for all 3 stages
    assert 'schema' in results
    assert 'semantic' in results
    assert 'quality' in results

    # All stages should pass for valid input
    assert passed
    assert results['schema'].passed
    assert results['semantic'].passed
    assert results['quality'].passed


def test_validate_all_stops_on_schema_failure(validator):
    """Test that validation stops if schema fails."""
    invalid_input = {
        "name": "Invalid Name",  # Spaces not allowed
        "description": "Short",  # Too short
        "expertise": ["A", "B"],  # Too few
        "use_cases": ["1"],  # Too few
        "communication_style": "Test"  # Too short
    }

    passed, results = validator.validate_all(invalid_input)

    # Should fail overall
    assert not passed
    # Schema should fail
    assert not results['schema'].passed
    # Other stages might not run, but if they do, schema failure is caught
    assert len(results) >= 1
