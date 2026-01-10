"""
Base UDS Validator

Base class for all document-specific validators in the UDS system.
Extends the original UDSValidator with category-specific validation logic.
"""

from pathlib import Path
from typing import Optional, Union
import re
import yaml
from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError

from ..validator import UDSValidator, ValidationResult, ValidationError, ValidationSeverity


class BaseUDSValidator(UDSValidator):
    """
    Base class for all UDS validators

    Provides common functionality:
    - YAML frontmatter extraction
    - JSON Schema validation
    - Base UDS field validation (agent, date, task)
    - Score calculation

    Subclasses should override:
    - schema_name: Name of JSON schema file in schemas/documentation/
    - doc_category: Category name (foundation, workorder, system, etc.)
    - validate_specific(): Category-specific validation logic
    """

    schema_name: Optional[str] = None
    doc_category: str = "unknown"

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize validator with schemas directory

        Args:
            schemas_dir: Path to schemas directory (default: package schemas/documentation/)
        """
        if schemas_dir is None:
            # Default to schemas/documentation/ for UDS schemas
            schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "documentation"

        self.schemas_dir = schemas_dir
        self.schema = None

        if self.schema_name:
            self._load_schema()

    def _load_schema(self):
        """Load JSON schema for this validator"""
        schema_path = self.schemas_dir / self.schema_name
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        import json
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a markdown file against UDS schema

        Args:
            file_path: Path to markdown file

        Returns:
            ValidationResult with errors, warnings, and score
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"File not found: {file_path}"
                )],
                warnings=[],
                score=0
            )

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.validate_content(content, file_path)

    def validate_content(self, content: str, file_path: Optional[Path] = None) -> ValidationResult:
        """
        Validate document content against UDS schema

        Args:
            content: Document content (markdown with YAML frontmatter)
            file_path: Optional path for context

        Returns:
            ValidationResult with errors, warnings, and score
        """
        errors = []
        warnings = []

        # Extract YAML frontmatter
        frontmatter = self._extract_frontmatter(content)

        if frontmatter is None:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.CRITICAL,
                    message="Missing or invalid YAML frontmatter (must start with --- and end with ---)"
                )],
                warnings=[],
                score=0
            )

        # Validate against JSON schema if loaded
        if self.schema:
            schema_errors = self._validate_against_schema(frontmatter)
            errors.extend(schema_errors)

        # Category-specific validation
        specific_errors, specific_warnings = self.validate_specific(frontmatter, content, file_path)
        errors.extend(specific_errors)
        warnings.extend(specific_warnings)

        # Calculate score
        score = self._calculate_score(errors, warnings)

        # Valid if no CRITICAL errors
        valid = not any(e.severity == ValidationSeverity.CRITICAL for e in errors)

        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            score=score
        )

    def _extract_frontmatter(self, content: str) -> Optional[dict]:
        """Extract YAML frontmatter from markdown"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter if isinstance(frontmatter, dict) else None
        except yaml.YAMLError:
            return None

    def _validate_against_schema(self, frontmatter: dict) -> list[ValidationError]:
        """Validate frontmatter against JSON schema"""
        errors = []

        try:
            validator = Draft7Validator(self.schema)
            for error in validator.iter_errors(frontmatter):
                # Convert JSON schema error to ValidationError
                severity = ValidationSeverity.CRITICAL if error.validator in ['required', 'type'] else ValidationSeverity.MAJOR

                errors.append(ValidationError(
                    severity=severity,
                    message=error.message,
                    field='.'.join(str(p) for p in error.path) if error.path else None
                ))
        except Exception as e:
            errors.append(ValidationError(
                severity=ValidationSeverity.CRITICAL,
                message=f"Schema validation error: {str(e)}"
            ))

        return errors

    def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
        """
        Category-specific validation logic

        Override this in subclasses to add custom validation.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        return ([], [])

    def _calculate_score(self, errors: list[ValidationError], warnings: list[str]) -> int:
        """
        Calculate validation score (0-100)

        Scoring:
        - Start with 100
        - Deduct 50 for each CRITICAL error
        - Deduct 20 for each MAJOR error
        - Deduct 10 for each MINOR error
        - Deduct 5 for each WARNING
        - Deduct 2 for each warning message
        """
        score = 100

        for error in errors:
            if error.severity == ValidationSeverity.CRITICAL:
                score -= 50
            elif error.severity == ValidationSeverity.MAJOR:
                score -= 20
            elif error.severity == ValidationSeverity.MINOR:
                score -= 10
            elif error.severity == ValidationSeverity.WARNING:
                score -= 5

        score -= len(warnings) * 2

        return max(0, min(100, score))
