"""
Infrastructure Document Validator

Validates infrastructure documentation (deployment, CI/CD, monitoring) against UDS schema.
Infrastructure docs describe system setup, deployment, and operations.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class InfrastructureDocValidator(BaseUDSValidator):
    """
    Validator for infrastructure documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - Infrastructure fields (infra_type, environment, platform)
    - Recommended sections for infrastructure docs
    """

    schema_name = "infrastructure-doc-frontmatter-schema.json"
    doc_category = "infrastructure"

    # Recommended sections for infrastructure docs
    INFRASTRUCTURE_SECTIONS = [
        "Prerequisites",
        "Setup",
        "Configuration",
        "Deployment",
        "Verification",
        "Troubleshooting"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        Infrastructure-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check for recommended infrastructure sections
        missing_sections = self._check_infrastructure_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended infrastructure sections: {', '.join(missing_sections)}"
            )

        # Check prerequisites are specified
        prerequisites = frontmatter.get('prerequisites')
        if not prerequisites:
            warnings.append(
                "Consider specifying 'prerequisites' field for infrastructure docs"
            )

        # Check platform is specified for deployment docs
        infra_type = frontmatter.get('infra_type')
        platform = frontmatter.get('platform')
        if infra_type == 'deployment' and not platform:
            warnings.append(
                "Deployment docs should specify 'platform' field (e.g., AWS, Azure, Docker)"
            )

        return (errors, warnings)

    def _check_infrastructure_sections(self, content: str) -> list[str]:
        """Check for recommended infrastructure documentation sections."""
        missing = []
        for section in self.INFRASTRUCTURE_SECTIONS:
            if f"# {section}" not in content and f"## {section}" not in content:
                missing.append(section)
        return missing
