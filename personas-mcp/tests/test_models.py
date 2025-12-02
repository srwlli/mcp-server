"""
Unit tests for CustomPersonaInput model.

Tests Pydantic schema validation for custom persona creation.
"""

import pytest
from pydantic import ValidationError
from src.models import CustomPersonaInput


def test_valid_custom_persona_input():
    """Test that valid inputs pass validation."""
    valid_input = {
        "name": "test-expert",
        "description": "A test expert for unit testing purposes with comprehensive knowledge",
        "expertise": [
            "Unit testing best practices",
            "Test-driven development",
            "Mocking and fixtures"
        ],
        "use_cases": [
            "Writing comprehensive test suites",
            "Debugging failing tests",
            "Setting up CI/CD pipelines"
        ],
        "communication_style": "Clear, technical, and example-driven with emphasis on best practices"
    }

    persona = CustomPersonaInput(**valid_input)
    assert persona.name == "test-expert"
    assert len(persona.expertise) == 3
    assert len(persona.use_cases) == 3


def test_invalid_name_format():
    """Test that invalid name formats are rejected."""
    invalid_names = [
        "Test Expert",  # spaces
        "test_Expert",  # uppercase
        "test@expert",  # special chars
        "te",  # too short
        "a" * 51  # too long
    ]

    for invalid_name in invalid_names:
        with pytest.raises(ValidationError):
            CustomPersonaInput(
                name=invalid_name,
                description="A test expert for validation testing purposes",
                expertise=["Testing", "Validation", "Quality"],
                use_cases=["Test 1", "Test 2", "Test 3"],
                communication_style="Professional and clear communication style"
            )


def test_missing_required_fields():
    """Test that missing required fields are rejected."""
    # Missing name
    with pytest.raises(ValidationError):
        CustomPersonaInput(
            description="Test description",
            expertise=["A", "B", "C"],
            use_cases=["1", "2", "3"],
            communication_style="Test style"
        )

    # Missing expertise
    with pytest.raises(ValidationError):
        CustomPersonaInput(
            name="test-expert",
            description="Test description for validation testing purposes",
            use_cases=["1", "2", "3"],
            communication_style="Professional communication style"
        )


def test_expertise_constraints():
    """Test expertise list constraints."""
    base_input = {
        "name": "test-expert",
        "description": "A test expert for constraint validation testing purposes",
        "use_cases": ["Test 1", "Test 2", "Test 3"],
        "communication_style": "Clear professional communication style"
    }

    # Too few expertise items (< 3)
    with pytest.raises(ValidationError):
        CustomPersonaInput(**{**base_input, "expertise": ["Only", "Two"]})

    # Too many expertise items (> 10)
    with pytest.raises(ValidationError):
        CustomPersonaInput(**{**base_input, "expertise": [f"Expertise {i}" for i in range(11)]})

    # Valid range (3-10)
    valid = CustomPersonaInput(**{**base_input, "expertise": ["A", "B", "C", "D", "E"]})
    assert len(valid.expertise) == 5


def test_optional_fields():
    """Test that optional fields work correctly."""
    persona = CustomPersonaInput(
        name="test-expert",
        description="A comprehensive test expert for optional fields validation",
        expertise=["A", "B", "C"],
        use_cases=["1", "2", "3"],
        communication_style="Professional and detailed communication style",
        problem_solving="Systematic approach",
        tool_usage="Uses testing frameworks",
        specializations=["Unit tests", "Integration tests"],
        key_principles=["Quality first", "Test coverage"],
        example_responses={"Q1": "Answer 1"}
    )

    assert persona.problem_solving == "Systematic approach"
    assert len(persona.specializations) == 2
    assert len(persona.key_principles) == 2
    assert "Q1" in persona.example_responses


def test_string_length_constraints():
    """Test string length constraints."""
    base_input = {
        "name": "test-expert",
        "expertise": ["A", "B", "C"],
        "use_cases": ["1", "2", "3"],
        "communication_style": "Professional communication"
    }

    # Description too short (< 20)
    with pytest.raises(ValidationError):
        CustomPersonaInput(**{**base_input, "description": "Too short"})

    # Description too long (> 200)
    with pytest.raises(ValidationError):
        CustomPersonaInput(**{**base_input, "description": "A" * 201})

    # Valid length (20-200)
    valid = CustomPersonaInput(**{**base_input, "description": "A" * 50})
    assert len(valid.description) == 50
