"""
Integration tests for complete custom persona creation workflow.

Tests end-to-end persona creation from input to saved file.
"""

import pytest
import json
from pathlib import Path
from src.models import CustomPersonaInput
from src.validators import PersonaValidator
from src.persona_generator import PersonaGenerator, generate_persona


@pytest.fixture
def complete_persona_input():
    """Complete valid persona input for integration testing."""
    return {
        "name": "integration-test",
        "description": "An integration test expert for validating complete persona creation workflows",
        "expertise": [
            "End-to-end testing",
            "Integration patterns",
            "Workflow validation",
            "System testing",
            "Acceptance testing"
        ],
        "use_cases": [
            "Testing complete user workflows",
            "Validating system integration",
            "Ensuring feature completeness",
            "Verifying cross-component interactions",
            "Catching integration bugs"
        ],
        "communication_style": "Systematic and thorough with emphasis on complete workflow coverage",
        "problem_solving": "Tests from end-to-end to ensure all components work together",
        "tool_usage": "Uses integration testing frameworks and monitoring tools",
        "specializations": ["API integration", "Database integration"],
        "key_principles": ["Test realistic scenarios", "Cover happy and sad paths"],
        "example_responses": {
            "What is integration testing?": "Testing how components work together in a complete system"
        }
    }


def test_complete_persona_creation_workflow(complete_persona_input, tmp_path):
    """Test complete workflow: input → validation → generation → save."""
    # Step 1: Create CustomPersonaInput
    persona_input = CustomPersonaInput(**complete_persona_input)
    assert persona_input.name == "integration-test"

    # Step 2: Validate
    validator = PersonaValidator()
    passed, results = validator.validate_all(persona_input.model_dump())

    assert passed, f"Validation failed: {[r.errors for r in results.values() if r.errors]}"
    assert all(result.passed for result in results.values())

    # Step 3: Generate persona
    generator = PersonaGenerator()
    persona_def = generator.generate_persona_definition(persona_input)

    assert persona_def.name == "integration-test"
    assert len(persona_def.system_prompt) > 100
    assert persona_def.version == "1.0.0"

    # Step 4: Save to file
    saved_path = generator.save_persona(persona_def, output_dir=tmp_path)

    assert saved_path.exists()
    assert saved_path.name == "integration-test.json"

    # Step 5: Verify saved content
    with open(saved_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)

    assert saved_data['name'] == "integration-test"
    assert saved_data['description'] == complete_persona_input['description']
    assert len(saved_data['expertise']) == 5
    assert 'system_prompt' in saved_data
    assert 'behavior' in saved_data


def test_invalid_input_rejected_early():
    """Test that invalid inputs are rejected before generation."""
    invalid_input = {
        "name": "Invalid Name",  # Spaces not allowed
        "description": "Test",  # Too short
        "expertise": ["A", "B"],  # Too few
        "use_cases": ["1"],  # Too few
        "communication_style": "Short"  # Too short
    }

    # Should fail at Pydantic validation
    with pytest.raises(Exception):  # ValidationError
        persona_input = CustomPersonaInput(**invalid_input)


def test_duplicate_name_caught_in_validation():
    """Test that duplicate names are caught during validation."""
    # Use a name that exists in base personas
    duplicate_input = {
        "name": "docs-expert",  # Exists in base/
        "description": "A duplicate documentation expert for validation testing",
        "expertise": ["Docs", "Writing", "Standards"],
        "use_cases": ["Writing docs", "Maintaining guides", "Creating standards"],
        "communication_style": "Professional and clear documentation style"
    }

    persona_input = CustomPersonaInput(**duplicate_input)

    validator = PersonaValidator()
    passed, results = validator.validate_all(persona_input.model_dump())

    # Should fail semantic validation due to duplicate name
    assert not passed or not results['semantic'].passed


def test_generated_persona_can_be_loaded(complete_persona_input, tmp_path):
    """Test that generated personas can be loaded back as PersonaDefinition."""
    from src.models import PersonaDefinition

    # Generate and save
    persona_def, saved_path = generate_persona(
        CustomPersonaInput(**complete_persona_input),
        version="1.0.0",
        save=True
    )

    # Load back from file
    with open(saved_path, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)

    # Should be able to reconstruct PersonaDefinition
    loaded_persona = PersonaDefinition(**loaded_data)

    assert loaded_persona.name == persona_def.name
    assert loaded_persona.description == persona_def.description
    assert len(loaded_persona.expertise) == len(persona_def.expertise)


def test_minimal_valid_persona():
    """Test that minimal valid input (required fields only) works."""
    minimal_input = {
        "name": "minimal-test",
        "description": "A minimal test persona with only required fields for workflow testing",
        "expertise": ["Testing", "Validation", "Workflows"],
        "use_cases": ["Basic testing", "Simple validation", "Workflow checks"],
        "communication_style": "Clear and concise communication style"
    }

    # Should complete full workflow
    persona_def, saved_path = generate_persona(
        CustomPersonaInput(**minimal_input),
        save=False  # Don't save to disk
    )

    assert persona_def.name == "minimal-test"
    assert persona_def.specializations is None
    assert persona_def.key_principles is None
    assert persona_def.example_responses is None


def test_maximal_valid_persona():
    """Test that maximal valid input (all fields) works."""
    maximal_input = {
        "name": "maximal-test",
        "description": "A maximal test persona with all optional fields populated for comprehensive testing",
        "expertise": [f"Expertise {i}" for i in range(1, 11)],  # 10 items (max)
        "use_cases": [f"Use case {i}" for i in range(1, 11)],  # 10 items (max)
        "communication_style": "Extremely detailed and comprehensive communication style with examples",
        "problem_solving": "Highly systematic problem-solving approach with multiple strategies",
        "tool_usage": "Uses all available tools with expert-level proficiency and best practices",
        "specializations": [f"Specialization {i}" for i in range(1, 6)],  # 5 items (max)
        "key_principles": [f"Principle {i}" for i in range(1, 11)],  # 10 items (max)
        "example_responses": {
            f"Question {i}": f"Answer {i}" for i in range(1, 4)  # 3 items (max)
        }
    }

    # Should complete full workflow
    persona_def, saved_path = generate_persona(
        CustomPersonaInput(**maximal_input),
        save=False
    )

    assert persona_def.name == "maximal-test"
    assert len(persona_def.expertise) == 10
    assert len(persona_def.use_cases) == 10
    assert len(persona_def.specializations) == 5
    assert len(persona_def.key_principles) == 10
    assert len(persona_def.example_responses) == 3


def test_system_prompt_quality(complete_persona_input):
    """Test that generated system prompts are high quality."""
    persona_def, _ = generate_persona(
        CustomPersonaInput(**complete_persona_input),
        save=False
    )

    system_prompt = persona_def.system_prompt

    # Check for key sections
    assert "Your Identity" in system_prompt or "expert" in system_prompt.lower()
    assert complete_persona_input['name'] in system_prompt
    assert complete_persona_input['description'] in system_prompt

    # Check that expertise is included
    for exp in complete_persona_input['expertise']:
        assert exp in system_prompt

    # Check that use cases are included
    for uc in complete_persona_input['use_cases']:
        assert uc in system_prompt

    # Check reasonable length
    assert len(system_prompt) > 500, "System prompt should be comprehensive"
