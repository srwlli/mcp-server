"""
System Document Validator

Validates system documentation (CLAUDE.md, SESSION-INDEX.md, etc.) against UDS schema.
System docs describe codebase architecture, session management, and project history.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class SystemDocValidator(BaseUDSValidator):
    """
    Validator for system documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - System fields (project, version, status)
    - Recommended sections for system docs
    """

    schema_name = "system-doc-frontmatter-schema.json"
    doc_category = "system"

    # Recommended sections for system docs
    SYSTEM_SECTIONS = [
        "Quick Summary",
        "Architecture",
        "File Structure",
        "Design Decisions",
        "Integration",
        "Use Cases"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        System-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check for recommended system sections
        missing_sections = self._check_system_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended system sections: {', '.join(missing_sections)}"
            )

        # Validate status enum (additional check beyond schema)
        status = frontmatter.get('status')
        if status and status not in ['Production', 'Development', 'Deprecated', 'Archived']:
            errors.append(
                ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"Invalid status '{status}'. Must be one of: Production, Development, Deprecated, Archived"
                )
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

        return (errors, warnings)

    def _check_system_sections(self, content: str) -> list[str]:
        """Check for recommended system documentation sections."""
        missing = []
        for section in self.SYSTEM_SECTIONS:
            # Look for markdown headers with the section name
            if f"# {section}" not in content and f"## {section}" not in content:
                missing.append(section)
        return missing
