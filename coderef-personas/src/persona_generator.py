"""
System prompt generation and persona metadata creation.

Implements template-based persona generation from user inputs:
- Template rendering with {{placeholder}} substitution
- System prompt generation using templates
- Metadata generation (version, timestamps, created_by)
- Complete PersonaDefinition creation

Added in custom persona feature (WO-CREATE-CUSTOM-PERSONA-001).
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .models import CustomPersonaInput, PersonaDefinition, PersonaBehavior


class TemplateRenderer:
    """Simple template renderer supporting {{placeholders}} and conditional sections."""

    @staticmethod
    def render(template: str, context: Dict[str, Any]) -> str:
        """
        Render template with context.

        Supports:
        - {{variable}} - Simple variable substitution
        - {{#section}}...{{/section}} - Conditional section (show if truthy)
        - {{^section}}...{{/section}} - Inverted section (show if falsy)

        Args:
            template: Template string with {{placeholders}}
            context: Dictionary of values to substitute

        Returns:
            Rendered template string
        """
        result = template

        # Handle conditional sections first ({{#field}}...{{/field}})
        result = TemplateRenderer._render_conditionals(result, context, inverted=False)

        # Handle inverted sections ({{^field}}...{{/field}})
        result = TemplateRenderer._render_conditionals(result, context, inverted=True)

        # Handle simple variable substitution ({{variable}})
        result = TemplateRenderer._render_variables(result, context)

        return result

    @staticmethod
    def _render_conditionals(template: str, context: Dict[str, Any], inverted: bool = False) -> str:
        """Render conditional sections."""
        pattern = r'\{\{([#^])(\w+)\}\}(.*?)\{\{/\2\}\}'
        prefix = '^' if inverted else '#'

        def replace_section(match):
            section_type = match.group(1)
            field_name = match.group(2)
            content = match.group(3)

            # Only process sections matching the current inverted state
            if section_type != prefix:
                return match.group(0)

            field_value = context.get(field_name)

            # Determine if section should be shown
            if inverted:
                # Show if field is falsy (None, empty, False)
                show = not field_value
            else:
                # Show if field is truthy
                show = bool(field_value)

            return content if show else ''

        # Use DOTALL flag to match across newlines
        return re.sub(pattern, replace_section, template, flags=re.DOTALL)

    @staticmethod
    def _render_variables(template: str, context: Dict[str, Any]) -> str:
        """Render simple variable substitutions."""
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, f'{{{{var_name}}}}'))

        return re.sub(r'\{\{(\w+)\}\}', replace_var, template)


class PersonaGenerator:
    """Generate complete persona definitions from user inputs."""

    def __init__(self, template_path: Optional[Path] = None):
        """
        Initialize generator.

        Args:
            template_path: Path to system prompt template (default: templates/persona_template.txt)
        """
        self.template_path = template_path or Path(__file__).parent.parent / "templates" / "persona_template.txt"

        # Load template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()

    def generate_system_prompt(self, persona_input: CustomPersonaInput) -> str:
        """
        Generate system prompt from template and user inputs.

        Args:
            persona_input: Validated CustomPersonaInput

        Returns:
            Complete system prompt string
        """
        # Prepare context for template rendering
        context = self._prepare_template_context(persona_input)

        # Render template
        system_prompt = TemplateRenderer.render(self.template, context)

        return system_prompt.strip()

    def _prepare_template_context(self, persona_input: CustomPersonaInput) -> Dict[str, Any]:
        """Prepare context dictionary for template rendering."""
        context = {
            'name': persona_input.name,
            'description': persona_input.description,
            'communication_style': persona_input.communication_style,
        }

        # Format lists as markdown bullet points
        context['expertise_list'] = self._format_list(persona_input.expertise)
        context['use_cases_list'] = self._format_list(persona_input.use_cases)

        # Optional fields
        if persona_input.problem_solving:
            context['problem_solving'] = persona_input.problem_solving

        if persona_input.tool_usage:
            context['tool_usage'] = persona_input.tool_usage

        if persona_input.specializations:
            context['specializations'] = True  # For conditional
            context['specializations_list'] = self._format_list(persona_input.specializations)

        if persona_input.key_principles:
            context['key_principles'] = True  # For conditional
            context['key_principles_list'] = self._format_list(persona_input.key_principles)

        if persona_input.example_responses:
            context['example_responses'] = True  # For conditional
            context['example_responses_formatted'] = self._format_examples(persona_input.example_responses)

        return context

    def _format_list(self, items: list) -> str:
        """Format list as markdown bullet points."""
        return '\n'.join(f'- {item}' for item in items)

    def _format_examples(self, examples: Dict[str, str]) -> str:
        """Format example responses as Q&A pairs."""
        formatted = []
        for question, answer in examples.items():
            formatted.append(f"**Q: {question}**\n\nA: {answer}\n")
        return '\n'.join(formatted)

    def generate_metadata(self, persona_input: CustomPersonaInput) -> Dict[str, Any]:
        """
        Generate metadata for persona definition.

        Args:
            persona_input: CustomPersonaInput

        Returns:
            Metadata dictionary with timestamps, version, etc.
        """
        now = datetime.now(timezone.utc).isoformat()

        return {
            'created_at': now,
            'updated_at': now,
            'created_by': 'create_custom_persona',
            'custom_persona': True,
            'source': 'user-generated'
        }

    def generate_persona_definition(self, persona_input: CustomPersonaInput, version: str = '1.0.0') -> PersonaDefinition:
        """
        Generate complete PersonaDefinition from user inputs.

        Args:
            persona_input: Validated CustomPersonaInput
            version: Persona version (default: "1.0.0")

        Returns:
            Complete PersonaDefinition ready to save
        """
        # Generate system prompt
        system_prompt = self.generate_system_prompt(persona_input)

        # Create behavior object
        behavior = PersonaBehavior(
            communication_style=persona_input.communication_style,
            problem_solving=persona_input.problem_solving or "Expert problem-solving approach tailored to the domain",
            tool_usage=persona_input.tool_usage or "Uses available tools effectively to assist with domain-specific tasks"
        )

        # Generate timestamps
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        # Create PersonaDefinition
        persona_definition = PersonaDefinition(
            name=persona_input.name,
            version=version,
            parent=None,
            description=persona_input.description,
            system_prompt=system_prompt,
            expertise=persona_input.expertise,
            use_cases=persona_input.use_cases,
            behavior=behavior,
            specializations=persona_input.specializations,
            example_responses=persona_input.example_responses,
            key_principles=persona_input.key_principles,
            created_at=now,
            updated_at=now
        )

        return persona_definition

    def save_persona(self, persona_definition: PersonaDefinition, output_dir: Optional[Path] = None) -> Path:
        """
        Save persona definition to JSON file.

        Args:
            persona_definition: PersonaDefinition to save
            output_dir: Directory to save to (default: personas/custom/)

        Returns:
            Path to saved file
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "personas" / "custom"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save to {name}.json
        output_file = output_dir / f"{persona_definition.name}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(persona_definition.model_dump(), f, indent=2, ensure_ascii=False)

        return output_file


def generate_persona(persona_input: CustomPersonaInput, version: str = '1.0.0', save: bool = True) -> tuple[PersonaDefinition, Optional[Path]]:
    """
    Convenience function to generate and optionally save a persona.

    Args:
        persona_input: CustomPersonaInput
        version: Persona version
        save: Whether to save to file

    Returns:
        Tuple of (PersonaDefinition, path_to_saved_file or None)
    """
    generator = PersonaGenerator()
    persona_definition = generator.generate_persona_definition(persona_input, version)

    saved_path = None
    if save:
        saved_path = generator.save_persona(persona_definition)

    return persona_definition, saved_path
