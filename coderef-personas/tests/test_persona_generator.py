"""
Unit tests for PersonaGenerator.

Tests template rendering, system prompt generation, and persona creation.
"""

import pytest
import json
from pathlib import Path
from src.persona_generator import PersonaGenerator, TemplateRenderer
from src.models import CustomPersonaInput


@pytest.fixture
def sample_input():
    """Sample CustomPersonaInput for testing."""
    return CustomPersonaInput(
        name="test-generator",
        description="A test persona for generator testing purposes with comprehensive features",
        expertise=["Expertise 1", "Expertise 2", "Expertise 3"],
        use_cases=["Use case 1", "Use case 2", "Use case 3"],
        communication_style="Professional and clear communication style with examples"
    )


@pytest.fixture
def generator():
    """Create PersonaGenerator instance."""
    return PersonaGenerator()


def test_template_renderer_simple_variables():
    """Test simple variable substitution."""
    template = "Hello {{name}}, you are {{role}}."
    context = {"name": "Alice", "role": "Developer"}

    result = TemplateRenderer.render(template, context)
    assert result == "Hello Alice, you are Developer."


def test_template_renderer_conditional_sections():
    """Test conditional sections {{#field}}...{{/field}}."""
    template = "Base content\n{{#optional}}Optional content: {{value}}{{/optional}}"

    # With optional field
    context_with = {"optional": True, "value": "Present"}
    result_with = TemplateRenderer.render(template, context_with)
    assert "Optional content: Present" in result_with

    # Without optional field
    context_without = {"optional": False, "value": "Hidden"}
    result_without = TemplateRenderer.render(template, context_without)
    assert "Optional content" not in result_without


def test_template_renderer_inverted_sections():
    """Test inverted sections {{^field}}...{{/field}}."""
    template = "{{^missing}}This shows when missing is falsy{{/missing}}"

    # When field is falsy
    context_falsy = {"missing": None}
    result_falsy = TemplateRenderer.render(template, context_falsy)
    assert "This shows when missing is falsy" in result_falsy

    # When field is truthy
    context_truthy = {"missing": "present"}
    result_truthy = TemplateRenderer.render(template, context_truthy)
    assert "This shows when missing is falsy" not in result_truthy


def test_persona_generator_system_prompt_generation(generator, sample_input):
    """Test system prompt generation from template."""
    system_prompt = generator.generate_system_prompt(sample_input)

    # Check that key content is present
    assert sample_input.name in system_prompt
    assert sample_input.description in system_prompt
    assert sample_input.expertise[0] in system_prompt
    assert sample_input.use_cases[0] in system_prompt
    assert sample_input.communication_style in system_prompt


def test_persona_generator_template_context(generator, sample_input):
    """Test template context preparation."""
    context = generator._prepare_template_context(sample_input)

    assert context['name'] == sample_input.name
    assert context['description'] == sample_input.description
    assert 'expertise_list' in context
    assert 'use_cases_list' in context
    assert '- Expertise 1' in context['expertise_list']


def test_persona_generator_format_list(generator):
    """Test list formatting as markdown bullets."""
    items = ["Item A", "Item B", "Item C"]
    formatted = generator._format_list(items)

    assert "- Item A" in formatted
    assert "- Item B" in formatted
    assert "- Item C" in formatted


def test_persona_generator_format_examples(generator):
    """Test example responses formatting."""
    examples = {
        "What is testing?": "Testing is the process of verifying software quality",
        "Why test?": "To catch bugs early and ensure reliability"
    }
    formatted = generator._format_examples(examples)

    assert "Q: What is testing?" in formatted
    assert "A: Testing is the process" in formatted


def test_persona_generator_generate_metadata(generator, sample_input):
    """Test metadata generation."""
    metadata = generator.generate_metadata(sample_input)

    assert 'created_at' in metadata
    assert 'updated_at' in metadata
    assert 'created_by' in metadata
    assert metadata['created_by'] == 'create_custom_persona'
    assert metadata['custom_persona'] is True


def test_persona_generator_generate_persona_definition(generator, sample_input):
    """Test complete PersonaDefinition generation."""
    persona_def = generator.generate_persona_definition(sample_input, version="1.0.0")

    # Check basic fields
    assert persona_def.name == sample_input.name
    assert persona_def.version == "1.0.0"
    assert persona_def.description == sample_input.description
    assert len(persona_def.expertise) == len(sample_input.expertise)
    assert len(persona_def.use_cases) == len(sample_input.use_cases)

    # Check system prompt was generated
    assert len(persona_def.system_prompt) > 0
    assert sample_input.name in persona_def.system_prompt

    # Check behavior
    assert persona_def.behavior.communication_style == sample_input.communication_style


def test_persona_generator_save_persona(generator, sample_input, tmp_path):
    """Test persona saving to file."""
    persona_def = generator.generate_persona_definition(sample_input)

    # Save to temporary directory
    saved_path = generator.save_persona(persona_def, output_dir=tmp_path)

    # Check file exists
    assert saved_path.exists()
    assert saved_path.name == f"{sample_input.name}.json"

    # Check file content
    with open(saved_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)

    assert saved_data['name'] == sample_input.name
    assert saved_data['version'] == persona_def.version
    assert 'system_prompt' in saved_data


def test_persona_generator_with_optional_fields(generator):
    """Test persona generation with optional fields populated."""
    full_input = CustomPersonaInput(
        name="full-test",
        description="A fully populated test persona for comprehensive testing of all fields",
        expertise=["A", "B", "C", "D", "E"],
        use_cases=["1", "2", "3", "4", "5"],
        communication_style="Detailed and comprehensive communication style",
        problem_solving="Systematic and methodical problem-solving approach",
        tool_usage="Uses testing frameworks and automation tools effectively",
        specializations=["Unit testing", "Integration testing"],
        key_principles=["Quality first", "Test coverage matters"],
        example_responses={"Q1": "Answer 1", "Q2": "Answer 2"}
    )

    persona_def = generator.generate_persona_definition(full_input)

    assert persona_def.specializations is not None
    assert len(persona_def.specializations) == 2
    assert persona_def.key_principles is not None
    assert persona_def.example_responses is not None
    assert persona_def.behavior.problem_solving == full_input.problem_solving
