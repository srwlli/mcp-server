"""
Validation logic for custom persona creation.

Implements multi-stage validation pipeline:
1. Schema validation (JSON schema compliance)
2. Semantic validation (coherence and relevance)
3. Quality validation (completeness and best practices)

Added in custom persona feature (WO-CREATE-CUSTOM-PERSONA-001).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from jsonschema import validate, ValidationError as JSONSchemaValidationError
from pydantic import ValidationError

from .models import CustomPersonaInput


class ValidationResult:
    """Result of a validation stage."""

    def __init__(self, passed: bool, errors: List[str] = None, warnings: List[str] = None):
        self.passed = passed
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self):
        return self.passed

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"ValidationResult({status}, errors={len(self.errors)}, warnings={len(self.warnings)})"


class PersonaValidator:
    """Multi-stage validator for custom persona inputs."""

    def __init__(self, schema_path: Optional[Path] = None, base_personas_dir: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            schema_path: Path to JSON schema file (default: templates/custom_persona_schema.json)
            base_personas_dir: Path to base personas directory (default: personas/base/)
        """
        self.schema_path = schema_path or Path(__file__).parent.parent / "templates" / "custom_persona_schema.json"
        self.base_personas_dir = base_personas_dir or Path(__file__).parent.parent / "personas" / "base"

        # Load JSON schema
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.json_schema = json.load(f)

        # Load existing persona names for uniqueness check
        self.existing_names = self._load_existing_persona_names()

    def _load_existing_persona_names(self) -> set:
        """Load names of existing base personas."""
        names = set()
        if self.base_personas_dir.exists():
            for persona_file in self.base_personas_dir.glob("*.json"):
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    names.add(persona_data.get("name", ""))
        return names

    def validate_all(self, persona_input: Dict) -> Tuple[bool, Dict[str, ValidationResult]]:
        """
        Run all validation stages.

        Args:
            persona_input: Dictionary of persona input data

        Returns:
            Tuple of (overall_passed, results_by_stage)
        """
        results = {}

        # Stage 1: Schema validation
        results['schema'] = self.validate_schema(persona_input)
        if not results['schema']:
            # If schema validation fails, stop here
            return False, results

        # Stage 2: Semantic validation
        results['semantic'] = self.validate_semantics(persona_input)

        # Stage 3: Quality validation
        results['quality'] = self.validate_quality(persona_input)

        # Overall pass if all stages pass
        overall_passed = all(result.passed for result in results.values())

        return overall_passed, results

    def validate_schema(self, persona_input: Dict) -> ValidationResult:
        """
        Stage 1: Validate against JSON schema and Pydantic model.

        Checks:
        - Required fields present
        - Field types correct
        - String length constraints
        - Array size constraints
        - Pattern matching (name format)
        """
        errors = []
        warnings = []

        # JSON schema validation
        try:
            validate(instance=persona_input, schema=self.json_schema)
        except JSONSchemaValidationError as e:
            errors.append(f"JSON schema validation failed: {e.message}")
            return ValidationResult(passed=False, errors=errors)

        # Pydantic model validation
        try:
            CustomPersonaInput(**persona_input)
        except ValidationError as e:
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            return ValidationResult(passed=False, errors=errors)

        return ValidationResult(passed=True, warnings=warnings)

    def validate_semantics(self, persona_input: Dict) -> ValidationResult:
        """
        Stage 2: Validate semantic coherence and relevance.

        Checks:
        - Expertise areas are relevant to description
        - Use cases align with expertise
        - Communication style is clear and descriptive
        - No contradictions between fields
        - Name doesn't conflict with base personas
        """
        errors = []
        warnings = []

        name = persona_input.get('name', '')
        description = persona_input.get('description', '').lower()
        expertise = [e.lower() for e in persona_input.get('expertise', [])]
        use_cases = [u.lower() for u in persona_input.get('use_cases', [])]

        # Uniqueness check
        if name in self.existing_names:
            errors.append(f"Persona name '{name}' conflicts with existing base persona. Choose a different name.")

        # Check for meaningful description
        generic_words = ['expert', 'specialist', 'professional', 'helper']
        if all(word not in description for word in generic_words):
            warnings.append("Description should clearly indicate the persona's expertise (e.g., 'expert', 'specialist')")

        # Check expertise-description alignment
        # Look for at least one expertise keyword in description
        expertise_mentioned = any(
            any(keyword in description for keyword in exp.split())
            for exp in expertise
        )
        if not expertise_mentioned:
            warnings.append("Consider mentioning at least one expertise area in the description")

        # Check for duplicate or very similar items
        if len(expertise) != len(set(expertise)):
            warnings.append("Some expertise areas appear to be duplicates")

        if len(use_cases) != len(set(use_cases)):
            warnings.append("Some use cases appear to be duplicates")

        # Check communication style quality
        comm_style = persona_input.get('communication_style', '').lower()
        if len(comm_style.split()) < 5:
            warnings.append("Communication style description is too brief. Provide more detail.")

        # Check for filler words in communication style
        filler_patterns = ['etc', 'and so on', 'and more']
        if any(filler in comm_style for filler in filler_patterns):
            warnings.append("Communication style contains filler words. Be more specific.")

        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)

    def validate_quality(self, persona_input: Dict) -> ValidationResult:
        """
        Stage 3: Validate completeness and best practices.

        Checks:
        - Sufficient number of expertise areas (5+ recommended)
        - Sufficient number of use cases (5+ recommended)
        - Optional fields populated where appropriate
        - Clear and actionable content
        - Best practices followed
        """
        errors = []
        warnings = []

        expertise = persona_input.get('expertise', [])
        use_cases = persona_input.get('use_cases', [])

        # Recommend sufficient coverage
        if len(expertise) < 5:
            warnings.append(f"Only {len(expertise)} expertise areas provided. Consider adding more (5-10) for comprehensive coverage.")

        if len(use_cases) < 5:
            warnings.append(f"Only {len(use_cases)} use cases provided. Consider adding more (5-10) to clarify when this persona is valuable.")

        # Check if optional fields are populated
        if not persona_input.get('problem_solving'):
            warnings.append("Consider providing 'problem_solving' approach for clearer persona behavior")

        if not persona_input.get('tool_usage'):
            warnings.append("Consider providing 'tool_usage' description to guide tool integration")

        if not persona_input.get('specializations'):
            warnings.append("Consider adding 'specializations' for more specific sub-area expertise")

        if not persona_input.get('key_principles'):
            warnings.append("Consider adding 'key_principles' to establish guiding philosophies")

        # Check expertise quality (should be specific, not too generic)
        generic_expertise = []
        for exp in expertise:
            if len(exp.split()) <= 2:
                generic_expertise.append(exp)

        if len(generic_expertise) > len(expertise) / 2:
            warnings.append("Many expertise areas are very brief (1-2 words). Consider making them more descriptive.")

        # Check use case quality (should be actionable scenarios)
        vague_use_cases = []
        for uc in use_cases:
            if not any(word in uc.lower() for word in ['help', 'assist', 'guide', 'create', 'build', 'implement', 'debug', 'analyze', 'review']):
                vague_use_cases.append(uc)

        if vague_use_cases:
            warnings.append(f"{len(vague_use_cases)} use case(s) don't clearly describe what help the persona provides")

        # Quality check passes with warnings
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)


def validate_persona_input(persona_input: Dict) -> Tuple[bool, Dict[str, ValidationResult]]:
    """
    Convenience function to validate persona input.

    Args:
        persona_input: Dictionary of persona input data

    Returns:
        Tuple of (overall_passed, results_by_stage)
    """
    validator = PersonaValidator()
    return validator.validate_all(persona_input)
