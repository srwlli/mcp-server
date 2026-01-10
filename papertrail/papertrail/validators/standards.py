"""
Standards Document Validator

Validates standards documentation (global-documentation-standards.md, resource-sheet-standards.md, etc.) against UDS schema.
Standards docs define policies, conventions, and enforcement rules.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class StandardsDocValidator(BaseUDSValidator):
    """
    Validator for standards documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - Standards fields (scope, version, enforcement)
    - Recommended sections for standards docs
    """

    schema_name = "standards-doc-frontmatter-schema.json"
    doc_category = "standards"

    # Recommended sections for standards docs
    STANDARDS_SECTIONS = [
        "Overview",
        "Standards",
        "Validation",
        "Enforcement",
        "Exceptions"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        Standards-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check for recommended standards sections
        missing_sections = self._check_standards_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended standards sections: {', '.join(missing_sections)}"
            )

        # Check version format (semver)
        version = frontmatter.get('version')
        if version:
            import re
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                errors.append(
                    ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message=f"Invalid version '{version}'. Must be semver format (e.g., 1.0.0)",
                        field='version'
                    )
                )

        # Check scope is meaningful
        scope = frontmatter.get('scope')
        if scope and len(scope.strip()) < 10:
            warnings.append(
                "Scope field is very short. Consider providing more detail about what these standards apply to."
            )

        # Check enforcement is specified
        enforcement = frontmatter.get('enforcement')
        if enforcement and len(enforcement.strip()) < 5:
            warnings.append(
                "Enforcement field is very short. Specify how standards are enforced (e.g., 'Automated validators', 'Manual review')."
            )

        return (errors, warnings)

    def _check_standards_sections(self, content: str) -> list[str]:
        """Check for recommended standards documentation sections."""
        missing = []
        for section in self.STANDARDS_SECTIONS:
            # Look for markdown headers with the section name
            if f"# {section}" not in content and f"## {section}" not in content:
                missing.append(section)
        return missing
